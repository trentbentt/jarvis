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

import json
import subprocess

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
    "embed-nomic":       "/health",
}

_TCP_ONLY = {"postgres", "monarch-postgres"}

# CLI-probed components: stdio MCP servers and other non-network services.
# Probe = run command; exit 0 + last stdout line parses as JSON = healthy.
_CLI_PROBE: dict[str, list[str]] = {
    "codebase-memory": ["/home/monarch/.local/bin/codebase-memory-mcp", "cli", "list_projects"],
}

# Companion paths whose newest-file mtime is reported as informational detail
# (e.g. last_index_activity for codebase-memory). NOT a healthy/unhealthy gate.
_MTIME_FILES: dict[str, str] = {
    "codebase-memory": "/home/monarch/.cache/codebase-memory-mcp/",
}

# Marker file written by ~/bin/t2-down on clean teardown, removed by ~/bin/t2-up.
# When a burst_only tier is unresponsive AND this marker exists, the listener
# reports IDLE (clean offload) instead of UNRESPONSIVE (unexpected failure).
T2_IDLE_MARKER = "/home/monarch/.local/state/inference/t2_idle_marker"


def _is_burst_idle(comp_name: str, snap) -> bool:
    """Return True if the component is mapped to a burst_only tier AND the
    idle marker file exists on disk. Caller has already established the
    component is unresponsive."""
    import os
    tier_id = None
    for tid, cname in _TIER_TO_COMPONENT.items():
        if cname == comp_name:
            tier_id = tid
            break
    if tier_id is None:
        return False
    tier = snap.tiers.get(tier_id)
    if tier is None or not tier.config.burst_only:
        return False
    return os.path.exists(T2_IDLE_MARKER)



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


def _cli_check(cmd: list[str], timeout: float = 5.0) -> tuple[bool, int]:
    """Run a CLI command; exit 0 + last stdout line parses as JSON = healthy."""
    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        ms = int((time.monotonic() - start) * 1000)
        if proc.returncode != 0:
            return False, ms
        for line in reversed(proc.stdout.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                return True, ms
            except ValueError:
                return False, ms
        return False, ms
    except Exception:
        ms = int((time.monotonic() - start) * 1000)
        return False, ms


def _newest_mtime(path: str) -> Optional[datetime]:
    """Return UTC mtime of newest entry under `path`. None if missing/empty."""
    import os
    try:
        if os.path.isfile(path):
            return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
        if not os.path.isdir(path):
            return None
        newest = 0.0
        for entry in os.listdir(path):
            m = os.path.getmtime(os.path.join(path, entry))
            if m > newest:
                newest = m
        if newest == 0.0:
            return None
        return datetime.fromtimestamp(newest, tz=timezone.utc)
    except Exception:
        return None


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
            if comp.name in _CLI_PROBE:
                healthy, ms = _cli_check(_CLI_PROBE[comp.name])
            elif comp.port is None:
                updated_components.append(comp)
                continue
            elif comp.name in _TCP_ONLY:
                healthy, ms = _tcp_check(comp.port)
            else:
                path = _HEALTH_PATHS.get(comp.name, "/health")
                healthy, ms = _http_check(comp.port, path)

            if healthy:
                new_status = HealthStatus.OK
                new_detail = None
                if comp.name in _MTIME_FILES:
                    mtime = _newest_mtime(_MTIME_FILES[comp.name])
                    if mtime is not None:
                        age_s = int((now - mtime).total_seconds())
                        new_detail = f"last_index_activity {age_s}s ago"
            elif _is_burst_idle(comp.name, snap):
                new_status = HealthStatus.IDLE
                new_detail = "deepseek fallback active (clean idle)"
            else:
                new_status = HealthStatus.UNRESPONSIVE
                new_detail = f"no response on :{comp.port}"
            new_comp = ComponentHealth(
                name=comp.name,
                port=comp.port,
                status=new_status,
                last_check=now,
                last_seen_healthy=now if healthy else comp.last_seen_healthy,
                response_ms=ms if healthy else None,
                detail=new_detail,
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
            elif comp.status == HealthStatus.IDLE and old_state == TierState.ACTIVE:
                transitions.append((tier_id, "active_to_idle",
                                    f"{tier_id} entered burst-idle; deepseek fallback active"))
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
                elif comp.status == HealthStatus.IDLE:
                    tier.runtime.health_status = HealthStatus.IDLE
                    tier.runtime.last_health_check = now
                    if tier.runtime.state == TierState.ACTIVE:
                        tier.runtime.state = TierState.STOPPED
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
            elif kind == "active_to_idle":
                store.emit(
                    type="tier_burst_idle_entered",
                    tier=tier_id,
                    detail=detail,
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
            elif comp.status == HealthStatus.IDLE:
                logger.info("[tier_health] %s burst-idle on :%s (deepseek fallback)",
                            comp.name, comp.port)
