"""
Rule registry — pure functions over a SystemModel snapshot.

Each rule inspects the latest snapshot and returns at most one ProposedAction
(or None). Rules are PURE: no I/O, no mutation, no clock reads beyond stamping
proposed_at. The engine handles cooldown/dedup and routes proposals through the
authority gate — rules only answer "is there a condition worth acting on?".

P3.1 ships ONE rule (the seed). master_summary §12.6.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, List

from .schema import HealthStatus, ProposedAction, SystemModel, TierState

Rule = Callable[[SystemModel], List[ProposedAction]]

# Crash detection reconciled against disk (P3.1 execution):
#   • tier_health.py sets runtime.state = FAILED on an ACTIVE→unresponsive
#     transition. BUT it only clears FAILED via STOPPED→ACTIVE, so FAILED is
#     STICKY: a tier that crashed once and recovered stays state=FAILED while
#     health_status returns to OK. (Verified on disk: t3/t5 both sat at
#     state=failed / health_status=ok for ~15h while serving fine.)
#   • Therefore state alone is NOT a live crash signal — we AND it with the
#     live health_status==UNRESPONSIVE. Both are set together by tier_health on
#     a genuine crash; the sticky-but-healthy case (health_status==ok) is
#     correctly excluded, so we never spuriously bounce a healthy tier.
#   • process.py owns restart_count_24h; _FLAP_THRESHOLD mirrors its value.
# (The brief referenced runtime.last_pid, which does not exist — the schema
# field is runtime.pid, None during a crash, so it cannot discriminate
# incidents. The engine's cooldown handles "one incident counts once" instead.)
_CRASHED_STATE = TierState.FAILED
_DOWN_HEALTH = HealthStatus.UNRESPONSIVE
_FLAP_THRESHOLD = 3                      # >= this restarts/24h → flapping; don't auto-bounce
_SEED_TIERS = ("t3", "t5")               # zero-VRAM CPU dataplane tiers


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def crashed_cpu_tier(model: SystemModel) -> List[ProposedAction]:
    """Seed rule: a T3/T5 CPU dataplane tier is crashed RIGHT NOW (state FAILED
    AND health_status UNRESPONSIVE) and is not flapping (restart_count_24h < 3).
    Proposes an idempotent single-tier restart PER crashed tier — a simultaneous
    t3+t5 crash yields two proposals (distinct dedup_keys), so neither masks the
    other. The engine's per-dedup_key cooldown prevents re-proposing while a
    condition persists."""
    out: List[ProposedAction] = []
    for tid in _SEED_TIERS:
        t = model.tiers.get(tid)
        if t is None:
            continue
        rt = t.runtime
        if (rt.state == _CRASHED_STATE
                and rt.health_status == _DOWN_HEALTH
                and rt.restart_count_24h < _FLAP_THRESHOLD):
            out.append(ProposedAction(
                action_id="auto_restart_cpu_dataplane_tier",
                trigger=f"tier_health:tier_crashed:{tid}",
                params={"tier": tid},
                dedup_key=f"auto_restart_cpu_dataplane_tier:{tid}",
                rationale=f"{tid} crashed (state=failed); idempotent restart via t{tid[-1]}-up",
                proposed_at=_utcnow(),
            ))
    return out


RULES: List[Rule] = [crashed_cpu_tier]
