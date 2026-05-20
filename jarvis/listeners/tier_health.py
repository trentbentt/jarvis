"""
Tier Health Listener v0.2

Polls every service endpoint every 15s via HTTP.
Queues update functions via StateStore.apply() — never holds the model lock.
"""

from __future__ import annotations

import logging
import socket
import time
from datetime import datetime, timezone
from typing import Optional

import urllib.request
import urllib.error

from .base import BaseListener
from ..schema import ComponentHealth, HealthStatus, TierState
from ..state import StateStore

logger = logging.getLogger(__name__)

_HEALTH_PATHS: dict[str, str] = {
    "llama-server-t1":   "/health",
    "llama-server-t2":   "/health",
    "llama-server-t3":   "/health",
    "llama-server-t4":   "/health",
    "llama-server-t5":   "/health",
    "litellm":           "/health/liveliness",
    "validation-gate":   "/health",
    "lora-dispatcher":   "/health",
    "n8n":               "/healthz",
}

_TCP_ONLY = {"postgres"}


def _http_check(port: int, path: str, timeout: float = 3.0) -> tuple[bool, int]:
    url = f"http://127.0.0.1:{port}{path}"
    start = time.monotonic()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout):
            ms = int((time.monotonic() - start) * 1000)
            return True, ms
    except urllib.error.HTTPError as e:
        if e.code == 404 and path != "/v1/models":
            return _http_check(port, "/v1/models", timeout)
        ms = int((time.monotonic() - start) * 1000)
        return False, ms
    except Exception:
        ms = int((time.monotonic() - start) * 1000)
        return False, ms


def _tcp_check(port: int, timeout: float = 2.0) -> tuple[bool, int]:
    start = time.monotonic()
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            ms = int((time.monotonic() - start) * 1000)
            return True, ms
    except Exception:
        ms = int((time.monotonic() - start) * 1000)
        return False, ms


_TIER_TO_COMPONENT = {
    "t1": "llama-server-t1",
    "t2": "llama-server-t2",
    "t3": "llama-server-t3",
    "t4": "llama-server-t4",
    "t5": "llama-server-t5",
}


class TierHealthListener(BaseListener):
    name = "tier_health"
    interval_sec = 15.0

    def poll(self) -> None:
        now = datetime.now(timezone.utc)
        store = StateStore.get()

        snap = store.snapshot()
        components_to_check = list(snap.health.components)

        updated_components: list[ComponentHealth] = []
        for comp in components_to_check:
            if comp.port is None:
                updated_components.append(comp)
                continue

            if comp.name in _TCP_ONLY:
                healthy, ms = _tcp_check(comp.port)
            else:
                path = _HEALTH_PATHS.get(comp.name, "/health")
                healthy, ms = _http_check(comp.port, path)

            new_status = HealthStatus.OK if healthy else HealthStatus.UNRESPONSIVE
            new_comp = ComponentHealth(
                name=comp.name,
                port=comp.port,
                status=new_status,
                last_check=now,
                last_seen_healthy=now if healthy else comp.last_seen_healthy,
                response_ms=ms if healthy else None,
                detail=None if healthy else f"no response on :{comp.port}",
            )
            updated_components.append(new_comp)

        health_map = {c.name: c for c in updated_components}
        transitions: list[tuple[str, str, str]] = []
        for tier_id, comp_name in _TIER_TO_COMPONENT.items():
            comp = health_map.get(comp_name)
            old_tier = snap.tiers.get(tier_id)
            if comp is None or old_tier is None:
                continue
            old_state = old_tier.runtime.state
            if comp.status == HealthStatus.OK and old_state == TierState.STOPPED:
                transitions.append((tier_id, "stopped_to_active",
                                    f"{tier_id} transitioned stopped -> active"))
            elif comp.status == HealthStatus.UNRESPONSIVE and old_state == TierState.ACTIVE:
                transitions.append((tier_id, "active_to_failed",
                                    f"{tier_id} unresponsive on :{old_tier.config.port}"))

        def update(model):
            model.health.components = updated_components
            model.health.last_full_sweep = now

            map_local = {c.name: c for c in updated_components}
            for tier_id, comp_name in _TIER_TO_COMPONENT.items():
                if tier_id not in model.tiers:
                    continue
                tier = model.tiers[tier_id]
                comp = map_local.get(comp_name)
                if comp is None:
                    continue

                if comp.status == HealthStatus.OK:
                    tier.runtime.health_status = HealthStatus.OK
                    tier.runtime.last_health_check = now
                    if tier.runtime.state == TierState.STOPPED:
                        tier.runtime.state = TierState.ACTIVE
                else:
                    tier.runtime.health_status = HealthStatus.UNRESPONSIVE
                    tier.runtime.last_health_check = now
                    if tier.runtime.state == TierState.ACTIVE:
                        tier.runtime.state = TierState.FAILED

        store.apply(update)

        for tier_id, kind, detail in transitions:
            if kind == "stopped_to_active":
                store.emit(
                    type="tier_state_change", tier=tier_id, detail=detail,
                )
            elif kind == "active_to_failed":
                store.emit(
                    type="tier_health_failed",
                    severity="warning",
                    tier=tier_id,
                    detail=detail,
                )

        for comp in updated_components:
            if comp.status == HealthStatus.UNRESPONSIVE:
                logger.warning("[tier_health] %s unresponsive on :%s",
                               comp.name, comp.port)
