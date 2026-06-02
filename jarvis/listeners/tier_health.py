"""
Tier Health Listener v0.2

Polls every service endpoint every 15s via HTTP.
Queues update functions via StateStore.apply() — never holds the model lock.
"""

from __future__ import annotations

import logging
import os
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
    "hermes":            "/v1/models",
}

# Components that require Authorization: Bearer <token> for the health probe.
# Value is the env-var NAME holding the token — never the literal token.
# Read fresh on each call so key rotation doesn't require a daemon restart.
_BEARER_ENV: dict[str, str] = {
    "hermes": "API_SERVER_KEY",
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

# Marker file written by ~/bin/inference-down on clean dataplane teardown,
# removed by ~/bin/inference-up. When a cpu_only dataplane tier is unresponsive
# AND this marker exists, the listener reports STOPPED (clean teardown) instead
# of UNRESPONSIVE — so t3/t5 settle to STOPPED, not FAILED, on a dataplane
# cycle. Genuine crashes (no marker) still surface as UNRESPONSIVE -> FAILED.
DATAPLANE_IDLE_MARKER = "/home/monarch/.local/state/inference/dataplane_idle_marker"


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


def _is_dataplane_clean_stop(comp_name: str, snap) -> bool:
    """Return True if the component is mapped to a cpu_only dataplane tier AND
    the dataplane teardown marker exists on disk. Caller has already established
    the component is unresponsive."""
    import os
    tier_id = None
    for tid, cname in _TIER_TO_COMPONENT.items():
        if cname == comp_name:
            tier_id = tid
            break
    if tier_id is None:
        return False
    tier = snap.tiers.get(tier_id)
    if tier is None or not tier.config.cpu_only:
        return False
    return os.path.exists(DATAPLANE_IDLE_MARKER)


def _http_check(port: int, path: str, timeout: float = 3.0,
                bearer_env: Optional[str] = None) -> tuple[bool, int]:
    url = f"http://127.0.0.1:{port}{path}"
    start = time.monotonic()
    try:
        req = urllib.request.Request(url)
        if bearer_env:
            token = os.environ.get(bearer_env, "")
            if token:
                req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=timeout):
            ms = int((time.monotonic() - start) * 1000)
            return True, ms
    except urllib.error.HTTPError as e:
        if e.code == 404 and path != "/v1/models":
            return _http_check(port, "/v1/models", timeout, bearer_env)
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


# ─── EverCore (L7) composite probe ────────────────────────────────────────────
# EverCore is one logical service backed by 5 sub-services (docker substrate +
# uv-run API). The `evercore` health component is OK iff ALL sub-probes pass;
# its detail string always reports each sub-state (e.g. "es:ok milvus:ok ...")
# so a partial outage is visible in `jarvis-q health` / `jarvis-q evercore`.
# Redis is on :6380 (remapped from 6379, reserved for P1.5-6 L1 Redis).
_EVERCORE_SUBPROBES = [
    ("es",     "http", 19200, "/_cluster/health"),
    ("milvus", "http",  9091, "/healthz"),
    ("mongo",  "tcp",  27017, None),
    ("redis",  "tcp",   6380, None),
    ("api",    "http",  1995, "/health"),
]


def _evercore_check() -> tuple[bool, int, str]:
    """Composite probe: returns (all_healthy, total_ms, detail). Detail lists
    each sub-probe state regardless of overall result."""
    start = time.monotonic()
    parts: list[str] = []
    all_ok = True
    for label, kind, port, path in _EVERCORE_SUBPROBES:
        if kind == "http":
            ok, _ = _http_check(port, path)
        else:
            ok, _ = _tcp_check(port)
        parts.append(f"{label}:{'ok' if ok else 'DOWN'}")
        all_ok = all_ok and ok
    ms = int((time.monotonic() - start) * 1000)
    return all_ok, ms, " ".join(parts)


_TIER_TO_COMPONENT = {
    "t1": "llama-server-t1",
    "t2": "llama-server-t2",
    "t3": "llama-server-t3",
    "t4": "llama-server-t4",
    "t5": "llama-server-t5",
}


def _next_tier_state(old_state: TierState, status: HealthStatus) -> TierState:
    """Single source of truth for the health-driven tier state machine, used by
    BOTH the applied mutation and the event-detection pass so they can never
    drift (the §597 gap: update() promoted FAILED→ACTIVE but the event table
    only watched STOPPED→ACTIVE). Returns the new state, or old_state if this
    probe result implies no transition.

      OK           → STOPPED/FAILED recover to ACTIVE
      IDLE         → ACTIVE drops to STOPPED (burst tier cleanly offloaded)
      STOPPED      → ACTIVE/FAILED settle to STOPPED (clean dataplane teardown)
      UNRESPONSIVE → only ACTIVE escalates to FAILED. A STOPPED tier reading
                     UNRESPONSIVE is left STOPPED on purpose: inference-up clears
                     the teardown marker at the START of bringup (inference-up:65)
                     and documents (lines 61-64) that cpu tiers read UNRESPONSIVE
                     while they warm — escalating that to FAILED would mislabel
                     every warm-up and spuriously arm the restart rule. The
                     warming/failed-to-start tier stays visible via
                     health_status=UNRESPONSIVE.
    """
    if status == HealthStatus.OK:
        if old_state in (TierState.STOPPED, TierState.FAILED):
            return TierState.ACTIVE
    elif status == HealthStatus.IDLE:
        if old_state == TierState.ACTIVE:
            return TierState.STOPPED
    elif status == HealthStatus.STOPPED:
        if old_state in (TierState.ACTIVE, TierState.FAILED):
            return TierState.STOPPED
    else:  # UNRESPONSIVE
        if old_state == TierState.ACTIVE:
            return TierState.FAILED
    return old_state


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
            detail_override = None
            if comp.name == "evercore":
                healthy, ms, detail_override = _evercore_check()
            elif comp.name in _CLI_PROBE:
                healthy, ms = _cli_check(_CLI_PROBE[comp.name])
            elif comp.port is None:
                updated_components.append(comp)
                continue
            elif comp.name in _TCP_ONLY:
                healthy, ms = _tcp_check(comp.port)
            else:
                path = _HEALTH_PATHS.get(comp.name, "/health")
                bearer_env = _BEARER_ENV.get(comp.name)
                healthy, ms = _http_check(comp.port, path, bearer_env=bearer_env)

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
            elif _is_dataplane_clean_stop(comp.name, snap):
                new_status = HealthStatus.STOPPED
                new_detail = "dataplane down (clean teardown)"
            else:
                new_status = HealthStatus.UNRESPONSIVE
                new_detail = f"no response on :{comp.port}"
            # Composite probes (evercore) always report per-sub-probe detail,
            # so a partial outage is visible even when overall status is OK/down.
            if detail_override is not None:
                new_detail = detail_override
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
        # Detect transitions from the SAME state machine update() applies below,
        # so every applied state change emits its event — no silent FAILED→ACTIVE
        # recovery or ACTIVE/FAILED→STOPPED teardown. Tuple: (tier, old, new, status).
        transitions: list[tuple[str, TierState, TierState, HealthStatus]] = []
        for tier_id, comp_name in _TIER_TO_COMPONENT.items():
            comp = health_map.get(comp_name)
            old_tier = snap.tiers.get(tier_id)
            if comp is None or old_tier is None:
                continue
            old_state = old_tier.runtime.state
            new_state = _next_tier_state(old_state, comp.status)
            if new_state != old_state:
                transitions.append((tier_id, old_state, new_state, comp.status))

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

                # comp.status is exactly the mapped health enum (OK/IDLE/STOPPED/
                # UNRESPONSIVE), so mirror it onto runtime and resolve the new
                # state through the shared machine — same logic the event-detection
                # pass used, so applied state and emitted events cannot diverge.
                tier.runtime.health_status = comp.status
                tier.runtime.last_health_check = now
                tier.runtime.state = _next_tier_state(tier.runtime.state, comp.status)

        store.apply(update)

        for tier_id, old_state, new_state, status in transitions:
            label = f"{tier_id} {old_state.value} -> {new_state.value}"
            if new_state == TierState.FAILED:
                store.emit(
                    type="tier_health_failed", severity="warning",
                    tier=tier_id,
                    detail=f"{label}: unresponsive",
                )
            elif new_state == TierState.ACTIVE:
                store.emit(
                    type="tier_state_change", tier=tier_id,
                    detail=f"{label} (recovered)",
                )
            elif status == HealthStatus.IDLE:
                store.emit(
                    type="tier_burst_idle_entered", tier=tier_id,
                    detail=f"{label}: burst-idle, deepseek fallback active",
                )
            else:  # status == HealthStatus.STOPPED → clean dataplane teardown
                store.emit(
                    type="tier_state_change", tier=tier_id,
                    detail=f"{label} (clean teardown)",
                )

        for comp in updated_components:
            if comp.status == HealthStatus.UNRESPONSIVE:
                logger.warning("[tier_health] %s unresponsive on :%s",
                               comp.name, comp.port)
            elif comp.status == HealthStatus.IDLE:
                logger.info("[tier_health] %s burst-idle on :%s (deepseek fallback)",
                            comp.name, comp.port)
