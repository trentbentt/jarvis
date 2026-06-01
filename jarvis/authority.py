"""
Authority gate + durable trust ledger — the §9.5 three-tier authority model.

Two collaborators:

  AuthorityLedger  — owns ~/.local/state/jarvis/authority.json. Holds the
                     N=12 trust counters per action and the one-shot per-run
                     approvals the operator grants from the CLI. This file is
                     SEPARATE from state.json by design: state.json is
                     non-doctrine (§0.1 rule 5), pruned/rehydrated on cold-start;
                     an action with 11 clean runs must NOT silently reset to 0
                     on a daemon restart, so the counters own their own store
                     with atomic-replace write discipline (mirrors
                     state.py:save_to_disk).

  AuthorityGate    — classifies each ProposedAction into a tier (§9.5.2) and
                     dispatches it: Tier 1 acts silently, Tier 2 acts + logs,
                     Tier 3 surfaces a PendingAsk and waits for operator
                     approval. Records every outcome back to the ledger and,
                     after N=12 clean runs, proposes a promotion ask (never
                     self-promotes — promotion is always a Tier 3 ask).

Doctrine: master_summary §9.5 / §9.5.2 (authority model + N=12 lifecycle),
§12.6 (decision-engine flow).
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .actions import ACTIONS
from .schema import (
    ActionLifecycleState,
    ActionRecord,
    ActionTier,
    PendingAsk,
    ProposedAction,
)

logger = logging.getLogger(__name__)

AUTHORITY_PATH = Path(os.environ.get(
    "JARVIS_AUTHORITY_PATH",
    Path.home() / ".local/state/jarvis/authority.json",
))

PROMOTION_THRESHOLD = 12   # §9.5.2 Item 7 — uniform across all actions
_FLAP_THRESHOLD = 3        # mirrors process.py: >= this restarts/24h = flapping


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Seed registry: one cold-start ledger row per registered action. Built from
# ACTIONS so the ledger stays in lockstep with the action contract metadata.
ACTION_REGISTRY: Dict[str, dict] = {
    aid: dict(
        description=a.description,
        current_tier=a.default_tier,
        target_tier=a.target_tier,
    )
    for aid, a in ACTIONS.items()
}


class AuthorityLedger:
    """Durable N=12 counters + one-shot run approvals. Survives daemon restart
    by design — NOT in state.json."""

    def __init__(self) -> None:
        self.records: Dict[str, ActionRecord] = {}
        self.approved_runs: set[str] = set()

    # ── Persistence ───────────────────────────────────────────────────────────
    def load(self) -> None:
        """Hydrate from authority.json, then seed any missing rows from
        ACTION_REGISTRY (cold-start). Idempotent — safe to call every tick to
        pick up CLI mutations (promote/demote/approve)."""
        data: dict = {}
        seeded = not AUTHORITY_PATH.exists()   # missing file → will materialize below
        if AUTHORITY_PATH.exists():
            try:
                data = json.loads(AUTHORITY_PATH.read_text())
            except Exception as exc:
                logger.error("[authority] failed to parse %s: %s — reseeding",
                             AUTHORITY_PATH, exc)
                data = {}
                seeded = True

        records: Dict[str, ActionRecord] = {}
        for aid, raw in (data.get("actions") or {}).items():
            try:
                records[aid] = ActionRecord.model_validate(raw)
            except Exception as exc:
                logger.error("[authority] dropping unparseable row %s: %s", aid, exc)

        # Seed/hydrate cold-start rows for any registered action missing a row.
        for aid, seed in ACTION_REGISTRY.items():
            if aid not in records:
                logger.info("[authority] seeding cold-start row: %s", aid)
                records[aid] = ActionRecord(
                    action_id=aid,
                    description=seed["description"],
                    current_tier=seed["current_tier"],
                    target_tier=seed["target_tier"],
                    state=ActionLifecycleState.COLD_START,
                )
                seeded = True

        self.records = records
        self.approved_runs = set(data.get("approved_runs") or [])

        # Materialize the durable file the moment we seed (first load / new
        # action / corrupt file) so authority.json exists from daemon start and
        # survives an ungraceful kill. Steady-state ticks re-read an existing
        # file → no seeding → no write.
        if seeded:
            self.save()

    def save(self) -> None:
        AUTHORITY_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "actions": {aid: r.model_dump(mode="json") for aid, r in self.records.items()},
            "approved_runs": sorted(self.approved_runs),
            "saved_at": _utcnow().isoformat(),
        }
        tmp = AUTHORITY_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, default=str))
        tmp.replace(AUTHORITY_PATH)

    # ── Accessors ───────────────────────────────────────────────────────────
    def get(self, action_id: str) -> Optional[ActionRecord]:
        return self.records.get(action_id)

    def records_list(self) -> List[ActionRecord]:
        return list(self.records.values())

    # ── Trust-counter mutations ─────────────────────────────────────────────
    def record(self, action_id: str, outcome: str) -> None:
        """Record an action outcome. ok → clean streak++; failed → streak reset
        (but no demotion — a failed restart isn't operator regret); regretted →
        demote to Tier 3 + reset (operator pressed the regret button)."""
        row = self.records.get(action_id)
        if row is None:
            logger.error("[authority] record() for unknown action %s", action_id)
            return
        row.total_runs += 1
        row.last_fired = _utcnow()
        row.last_outcome = outcome
        if outcome == "ok":
            row.clean_run_count += 1
        elif outcome == "regretted":
            row.current_tier = ActionTier.TIER_3
            row.state = ActionLifecycleState.DEMOTED
            row.clean_run_count = 0
            row.demotion_reason = "operator regret (recorded outcome)"
        else:  # "failed" — breaks the clean streak, no tier change
            row.clean_run_count = 0
        self.save()

    def approve_run(self, action_id: str) -> None:
        """Operator grants a one-shot approval for the next Tier-3 run."""
        if action_id in self.records:
            self.approved_runs.add(action_id)
            self.save()

    def consume_run_approval(self, action_id: str) -> bool:
        """Atomically consume a standing run approval. True if one was present."""
        if action_id in self.approved_runs:
            self.approved_runs.discard(action_id)
            self.save()
            return True
        return False

    def promote(self, action_id: str) -> bool:
        """Operator approves an ELIGIBLE action's promotion → move to target
        tier (capped). Resets the clean-run streak for the new tier. Returns
        True if a promotion happened."""
        row = self.records.get(action_id)
        if row is None:
            return False
        if row.state != ActionLifecycleState.ELIGIBLE:
            return False
        if row.current_tier <= row.target_tier:
            # already at/above cap (lower int = higher authority); nothing to do
            return False
        row.current_tier = row.target_tier
        row.state = ActionLifecycleState.PROMOTED
        row.clean_run_count = 0
        row.demotion_reason = None
        self.save()
        return True

    def demote(self, action_id: str, reason: str) -> bool:
        """Operator regret: reset to Tier 3, zero the streak, drop any pending
        run approval."""
        row = self.records.get(action_id)
        if row is None:
            return False
        row.current_tier = ActionTier.TIER_3
        row.state = ActionLifecycleState.DEMOTED
        row.clean_run_count = 0
        row.demotion_reason = reason
        self.approved_runs.discard(action_id)
        self.save()
        return True


class AuthorityGate:
    """Classifies and dispatches proposed actions; records outcomes; proposes
    promotions at N=12. Holds the standing PendingAsk set in memory; the engine
    publishes it to the decisions domain each tick."""

    def __init__(self, store, ledger: AuthorityLedger) -> None:
        self.store = store
        self.ledger = ledger
        self.pending: Dict[str, PendingAsk] = {}   # dedup_key → standing ask
        # Off-thread action execution: a long subprocess must never freeze the
        # decision loop. Workers run the action only; emit + ledger record are
        # finalized on the engine thread via collect_finished().
        self._exec_lock = threading.Lock()
        self._in_flight: Dict[str, bool] = {}      # dedup_key → currently executing
        self._finished: List[tuple] = []           # (proposed, emit_kind, outcome) to finalize

    # ── Classification ──────────────────────────────────────────────────────
    def classify(self, proposed: ProposedAction) -> ActionTier:
        """Current tier comes from the ledger. Flapping guard forces Tier 3:
        even a promoted action will not auto-fire against a tier that is
        restart-looping — surface it to the operator instead."""
        row = self.ledger.get(proposed.action_id)
        tier = row.current_tier if row else ActionTier.TIER_3
        if self._is_flapping(proposed):
            return ActionTier.TIER_3
        return tier

    def _is_flapping(self, proposed: ProposedAction) -> bool:
        tid = proposed.params.get("tier")
        if not tid:
            return False
        try:
            snap = self.store.snapshot()
            t = snap.tiers.get(tid)
            return bool(t and t.runtime.restart_count_24h >= _FLAP_THRESHOLD)
        except Exception:
            return False

    # ── Dispatch ──────────────────────────────────────────────────────────────
    def dispatch(self, proposed: ProposedAction) -> None:
        tier = self.classify(proposed)
        if tier == ActionTier.TIER_1:
            self._spawn_exec(proposed, emit_kind="silent")
        elif tier == ActionTier.TIER_2:
            self._spawn_exec(proposed, emit_kind="tier2")
        else:  # TIER_3 — surface and ask, unless the operator pre-approved
            if self.ledger.consume_run_approval(proposed.action_id):
                self.pending.pop(proposed.dedup_key, None)
                self._spawn_exec(proposed, emit_kind="approved")
            else:
                self.pending[proposed.dedup_key] = PendingAsk(
                    action_id=proposed.action_id,
                    params=proposed.params,
                    rationale=proposed.rationale,
                    proposed_at=proposed.proposed_at,
                    tier=ActionTier.TIER_3,
                    kind="run",
                    blocking=True,
                )

    def process_pending_approvals(self) -> set[str]:
        """Called every engine tick (even on cooldown). Executes any standing
        run-ask the operator approved between ticks, and clears promotion asks
        the operator has acted on. Returns the set of dedup_keys handled this
        tick so the engine can arm their cooldown and skip same-tick re-asking
        off a not-yet-refreshed snapshot. Keyed by dedup_key; ledger lookups use
        ask.action_id (trust is per action, not per tier)."""
        executed: set[str] = set()
        for key, ask in list(self.pending.items()):
            if ask.kind == "run":
                if self.ledger.consume_run_approval(ask.action_id):
                    proposed = ProposedAction(
                        action_id=ask.action_id, trigger="operator_approval",
                        params=ask.params, dedup_key=key,
                        rationale=ask.rationale, proposed_at=ask.proposed_at,
                    )
                    self._execute_approved(proposed)
                    executed.add(key)
            elif ask.kind == "promotion":
                row = self.ledger.get(ask.action_id)
                if row and row.state == ActionLifecycleState.PROMOTED:
                    del self.pending[key]   # operator approved the promotion
                    self.store.emit(
                        type="action", severity="info",
                        detail=f"{ask.action_id} promoted to Tier {int(row.current_tier)}",
                        action_id=ask.action_id,
                    )
        return executed

    def prune_stale_runs(self, active_dedup_keys: set[str]) -> None:
        """Drop run-asks whose triggering condition no longer holds (the tier
        recovered — via this engine's restart or on its own). Promotion asks are
        not condition-driven and are never pruned here. Keyed by dedup_key so a
        still-crashed t3 cannot keep a recovered t5's ask alive (or vice-versa)."""
        for key, ask in list(self.pending.items()):
            if ask.kind == "run" and key not in active_dedup_keys:
                logger.info("[authority] pruning stale run-ask %s (condition cleared)", key)
                del self.pending[key]

    def _execute_approved(self, proposed: ProposedAction) -> None:
        # Clear the standing run ask, then run OFF the engine thread — the
        # subprocess can take minutes. collect_finished() finalizes (emit +
        # record_outcome) back on the engine thread when the worker returns.
        self.pending.pop(proposed.dedup_key, None)
        self._spawn_exec(proposed, emit_kind="approved")

    # ── Off-thread execution ────────────────────────────────────────────────
    def _spawn_exec(self, proposed: ProposedAction, emit_kind: str) -> None:
        """Run an action on a short-lived worker thread so a multi-minute
        subprocess never freezes the decision loop. The worker ONLY runs the
        action; emit + ledger record happen on the engine thread via
        collect_finished(), keeping ledger access single-threaded."""
        key = proposed.dedup_key
        with self._exec_lock:
            if key in self._in_flight:
                return                            # already running — never double-run
            self._in_flight[key] = True

        def _worker() -> None:
            outcome = self._act(proposed)
            with self._exec_lock:
                self._in_flight.pop(key, None)
                self._finished.append((proposed, emit_kind, outcome))

        threading.Thread(target=_worker, name=f"action-{key}", daemon=True).start()

    def collect_finished(self) -> None:
        """Finalize actions that finished executing off-thread: emit the
        tier-appropriate event and record the outcome. MUST run on the engine
        thread (it touches the ledger). Called once at the top of each tick."""
        with self._exec_lock:
            done = self._finished
            self._finished = []
        for proposed, emit_kind, outcome in done:
            if emit_kind == "tier2":
                self.store.emit(
                    type="action", severity="info",
                    tier=proposed.params.get("tier"),
                    detail=f"{proposed.rationale} (Tier 2 autonomous-with-log)",
                    action_id=proposed.action_id, outcome=outcome,
                )
            elif emit_kind == "approved":
                self.store.emit(
                    type="action", severity="info",
                    tier=proposed.params.get("tier"),
                    detail=f"{proposed.rationale} (operator-approved Tier 3 run)",
                    action_id=proposed.action_id, outcome=outcome,
                )
            # emit_kind == "silent" (Tier 1): autonomous, no event by design
            self.record_outcome(proposed.action_id, outcome)

    def is_in_flight(self, dedup_key: str) -> bool:
        with self._exec_lock:
            return dedup_key in self._in_flight

    def _act(self, proposed: ProposedAction) -> str:
        action = ACTIONS.get(proposed.action_id)
        if action is None:
            logger.error("[authority] no executor for %s", proposed.action_id)
            return "failed"
        if not action.matches(proposed.params):
            logger.error("[authority] params %r rejected by %s.matches()",
                         proposed.params, proposed.action_id)
            return "failed"
        return action.execute(proposed.params)

    # ── Outcome recording + promotion ladder ───────────────────────────────────
    def record_outcome(self, action_id: str, outcome: str) -> None:
        self.ledger.record(action_id, outcome)
        if outcome == "ok":
            self._maybe_propose_promotion(action_id)

    def _maybe_propose_promotion(self, action_id: str) -> None:
        """After N=12 clean runs below the target tier, surface a promotion ask.
        The engine NEVER self-promotes — the operator approves via the CLI."""
        row = self.ledger.get(action_id)
        if row is None:
            return
        can_climb = row.current_tier > row.target_tier   # lower int = higher authority
        if (can_climb
                and row.clean_run_count >= PROMOTION_THRESHOLD
                and row.state != ActionLifecycleState.ELIGIBLE):
            row.state = ActionLifecycleState.ELIGIBLE
            self.ledger.save()
            self.pending[f"{action_id}:promotion"] = PendingAsk(
                action_id=action_id, params={},
                rationale=(f"{action_id}: {row.clean_run_count} clean runs at "
                           f"Tier {int(row.current_tier)} — propose promotion to "
                           f"Tier {int(row.target_tier)}"),
                proposed_at=_utcnow(),
                tier=row.current_tier, kind="promotion", blocking=True,
            )
            self.store.emit(
                type="action_promotion_eligible", severity="info",
                detail=(f"{action_id} eligible for promotion to Tier "
                        f"{int(row.target_tier)} after {row.clean_run_count} clean runs"),
                action_id=action_id,
            )

    def demote(self, action_id: str, reason: str) -> bool:
        ok = self.ledger.demote(action_id, reason)
        if ok:
            # pending is keyed by dedup_key; drop every ask for this action
            # (run asks for any tier + the promotion ask).
            for k in [k for k, a in self.pending.items() if a.action_id == action_id]:
                self.pending.pop(k, None)
            self.store.emit(
                type="action_demoted", severity="warning",
                detail=f"{action_id} demoted to Tier 3: {reason}",
                action_id=action_id,
            )
        return ok

    def pending_asks(self) -> List[PendingAsk]:
        return list(self.pending.values())
