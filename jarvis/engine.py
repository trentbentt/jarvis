"""
Decision engine — the §12.6 consumer that closes the loop the Phase 2 listeners
opened.

Runs as a daemon thread on its own 10s tick (decoupled from listener cadences —
it acts off StateStore snapshots, not live polls). Each tick:

  1. reload the authority ledger      (pick up CLI promote/demote/approve)
  2. process standing approvals        (execute Tier-3 asks the operator OK'd)
  3. snapshot system state             (read-only; never holds the model lock)
  4. evaluate pure-function rules       → ProposedAction | None
  5. dispatch through the authority gate (cooldown-deduped)
  6. publish the decisions domain       (the engine's ONLY write)

The engine is a pure CONSUMER of domain state. The one domain it writes is
`decisions` (pending asks + a read-only ledger projection), pushed via
store.apply — it never touches tier/resource/health state, preserving the v0.2
single-writer invariant. Mirrors BaseListener error-isolation: a tick that
raises is logged and the loop continues — the engine never dies.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Optional

from .authority import AuthorityGate, AuthorityLedger
from .rules import RULES
from .state import StateStore

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DecisionEngine:
    name = "engine"
    interval_sec = 10.0      # decoupled from listener cadences; acts off snapshots
    cooldown_sec = 60.0      # min seconds before re-proposing the same dedup_key

    def __init__(self) -> None:
        self.store = StateStore.get()
        self.ledger = AuthorityLedger()
        self.ledger.load()
        self.gate = AuthorityGate(self.store, self.ledger)
        self._seen: Dict[str, datetime] = {}   # dedup_key → last proposed
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ── Thread lifecycle (same shape as BaseListener) ──────────────────────────
    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._run, name=f"engine-{self.name}", daemon=True,
        )
        self._thread.start()
        logger.info("[%s] started (interval=%.0fs)", self.name, self.interval_sec)

    def stop(self) -> None:
        self._stop_event.set()
        try:
            self.ledger.save()       # flush trust counters on shutdown
        except Exception as exc:
            logger.error("[%s] ledger flush failed: %s", self.name, exc)

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ── Core tick ──────────────────────────────────────────────────────────────
    def tick(self) -> None:
        # 1. reload ledger so CLI mutations (promote/demote/approve) take effect
        self.ledger.load()
        # 2. execute any standing Tier-3 asks the operator approved between ticks
        executed = self.gate.process_pending_approvals()
        # 3. read-only snapshot
        snap = self.store.snapshot()
        # 4. evaluate rules → this tick's live proposals
        proposed_now = {}
        for rule in RULES:
            p = rule(snap)
            if p is not None:
                proposed_now[p.action_id] = p
        # 5. GC: drop standing run-asks whose condition has resolved (tier
        #    recovered). Without this, an ask raised before recovery lingers.
        self.gate.prune_stale_runs(set(proposed_now))
        # 6. dispatch live proposals (deduped + cooldown-gated)
        for action_id, proposed in proposed_now.items():
            if action_id in executed:
                # Just ran this tick; the snapshot may not reflect recovery yet
                # (tier_health lags). Arm cooldown and skip re-asking — prune
                # clears it once the condition clears.
                self._mark(proposed.dedup_key)
                continue
            if action_id in self.gate.pending:
                continue                              # already a standing ask
            if self._on_cooldown(proposed.dedup_key):
                continue
            self.gate.dispatch(proposed)
            self._mark(proposed.dedup_key)
        # 7. publish the decisions domain (the engine's only write)
        self._publish_decisions()

    def _on_cooldown(self, key: str) -> bool:
        last = self._seen.get(key)
        if last is None:
            return False
        return (_utcnow() - last).total_seconds() < self.cooldown_sec

    def _mark(self, key: str) -> None:
        self._seen[key] = _utcnow()

    def _publish_decisions(self) -> None:
        """Push pending asks + a read-only ledger projection onto the decisions
        domain via the single writer thread. Deep-copies so the published model
        never shares mutable rows with the live ledger."""
        asks = [a.model_copy(deep=True) for a in self.gate.pending_asks()]
        records = [r.model_copy(deep=True) for r in self.ledger.records_list()]
        now = _utcnow()

        def update(model) -> None:
            model.decisions.pending_asks = asks
            model.decisions.ledger = records
            model.decisions.last_tick = now

        self.store.apply(update)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.tick()
            except Exception as exc:
                logger.error("[%s] tick raised %s: %s",
                             self.name, type(exc).__name__, exc, exc_info=True)
            self._stop_event.wait(self.interval_sec)
