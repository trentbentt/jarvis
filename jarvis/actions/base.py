"""
Action contract — the executor interface the AuthorityGate classifies and runs.

An Action is a single, named autonomous behavior Jarvis may perform. The gate
reads the class-level metadata (default_tier, target_tier, reversible,
costs_money, vram_mb) to classify and bound each action; it never infers risk.
`execute()` performs the side effect and returns an outcome string the ledger
records ("ok" | "failed").

Doctrine: master_summary §12.6 (decision-engine flow) + §9.5 (three-tier
authority model). Adding an action is a deliberate decision — the seed
(restart_dataplane_tier) is the ONLY action until the N=12 ladder is proven.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..schema import ActionTier


class Action(ABC):
    """Subclass and set the metadata + implement matches()/execute().

    Metadata is class-level and read by AuthorityGate at classify time:
      action_id     — stable behavior id; key into ACTIONS and the ledger
      description    — human-readable, surfaced in jarvis-q
      default_tier   — cold-start authority tier (TIER_3 by doctrine §9.5.2)
      target_tier    — promotion cap; the ladder never climbs past this
      reversible     — does this action have a clean undo / is it self-healing
      costs_money    — gates anything touching paid cloud quotas (out of scope)
      vram_mb        — VRAM footprint; >0 actions are out of scope for the seed
    """

    action_id: str
    description: str
    default_tier: ActionTier
    target_tier: ActionTier
    reversible: bool
    costs_money: bool
    vram_mb: int

    @abstractmethod
    def matches(self, params: dict) -> bool:
        """Guard: are these params valid/in-scope for this action?"""
        ...

    @abstractmethod
    def execute(self, params: dict) -> str:
        """Perform the side effect. Return outcome: "ok" | "failed".

        Must not raise — catch internally and return "failed". The gate records
        whatever is returned; tier_health.py confirms real recovery on its next
        poll, so a returned "ok" is "dispatched cleanly", not "verified healthy".
        """
        ...
