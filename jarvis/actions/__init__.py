"""
Action registry. ACTIONS maps action_id → Action instance.

Exactly ONE action is registered (the seed). The ladder must be proven on it
end-to-end (cold-start → N=12 → promote) before a second action joins — see
P3.1 brief §0 decision 1.
"""

from .base import Action
from .restart_dataplane_tier import RestartCpuDataplaneTier

ACTIONS: dict[str, Action] = {
    a.action_id: a for a in (RestartCpuDataplaneTier(),)
}

__all__ = ["Action", "ACTIONS"]
