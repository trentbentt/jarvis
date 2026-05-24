"""
Jarvis State Store v0.2

Architecture change from v0.1: no shared RLock contention.

Pattern:
  - Reads:  acquire lock briefly, deep-copy the model, release, return copy.
  - Writes: pushed as update functions onto a queue. Single writer thread.
  - Events: separate thread-safe ring buffer (collections.deque).
  - Persistence: snapshot pattern. Lock held only for the deep-copy.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Deque, Optional

from .schema import (
    ComponentHealth,
    Event,
    Health,
    HealthStatus,
    MONARCH_HEALTH_COMPONENTS,
    MONARCH_TIERS,
    Operator,
    Quotas,
    Resources,
    Schedule,
    SystemModel,
    Tier,
    TierRuntime,
    TierState,
    Workloads,
)

logger = logging.getLogger(__name__)

STATE_PATH = Path(os.environ.get(
    "JARVIS_STATE_PATH",
    Path.home() / ".local/state/jarvis/state.json"
))

_EVENT_BUFFER_MAX = 2000
_WRITE_QUEUE_MAX = 1000


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


UpdateFn = Callable[[SystemModel], None]


class StateStore:
    _instance: Optional["StateStore"] = None
    _instance_lock = threading.Lock()

    def __init__(self) -> None:
        self._model_lock = threading.Lock()
        self._model = self._build_initial_model()

        self._write_queue: "queue.Queue[Optional[UpdateFn]]" = queue.Queue(
            maxsize=_WRITE_QUEUE_MAX
        )
        self._writer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self._events_lock = threading.Lock()
        self._events: Deque[Event] = deque(maxlen=_EVENT_BUFFER_MAX)

    @classmethod
    def get(cls) -> "StateStore":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def start(self) -> None:
        if self._writer_thread is not None and self._writer_thread.is_alive():
            return
        self._stop_event.clear()
        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            name="state-writer",
            daemon=True,
        )
        self._writer_thread.start()
        logger.info("[state] writer thread started")

    def stop(self, timeout: float = 5.0) -> None:
        self._stop_event.set()
        try:
            self._write_queue.put_nowait(None)
        except queue.Full:
            pass
        if self._writer_thread is not None:
            self._writer_thread.join(timeout=timeout)
        logger.info("[state] writer thread stopped")

    def snapshot(self) -> SystemModel:
        with self._model_lock:
            return self._model.model_copy(deep=True)

    def apply(self, fn: UpdateFn, timeout: float = 1.0) -> bool:
        try:
            self._write_queue.put(fn, timeout=timeout)
            return True
        except queue.Full:
            logger.error("[state] write queue full")
            return False

    def emit(
        self,
        type: str,
        severity: str = "info",
        tier: Optional[str] = None,
        workload_id: Optional[str] = None,
        detail: Optional[str] = None,
        **data: Any,
    ) -> None:
        event = Event(
            event_id=str(uuid.uuid4())[:8],
            timestamp=_utcnow(),
            type=type,
            severity=severity,
            tier=tier,
            workload_id=workload_id,
            detail=detail,
            data=data,
        )
        with self._events_lock:
            self._events.append(event)

    def events_snapshot(self) -> list[Event]:
        with self._events_lock:
            return list(self._events)

    def save_to_disk(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

        model_copy = self.snapshot()
        events = self.events_snapshot()
        model_copy.events.log = events

        payload = model_copy.model_dump(mode="json")

        tmp = STATE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, default=str))
        tmp.replace(STATE_PATH)

    @classmethod
    def load_from_disk(cls) -> Optional[SystemModel]:
        if not STATE_PATH.exists():
            return None
        try:
            data = json.loads(STATE_PATH.read_text())
            return SystemModel.model_validate(data)
        except Exception as e:
            logger.error("Failed to parse state file: %s", e)
            return None

    def _writer_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                fn = self._write_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if fn is None:
                break

            start = _utcnow()
            try:
                with self._model_lock:
                    fn(self._model)
                    self._model.last_updated = _utcnow()
            except Exception as exc:
                logger.error("[state] update fn raised %s: %s",
                             type(exc).__name__, exc, exc_info=True)
            finally:
                elapsed = (_utcnow() - start).total_seconds()
                if elapsed > 0.5:
                    logger.warning("[state] slow update fn: %.2fs", elapsed)

    @staticmethod
    def _build_initial_model() -> SystemModel:
        tiers = {
            tid: Tier(
                config=cfg,
                runtime=TierRuntime(
                    state=TierState.OFFLINE if not cfg.enabled else TierState.STOPPED
                ),
            )
            for tid, cfg in MONARCH_TIERS.items()
        }

        health_components = [
            ComponentHealth(
                name=c["name"],
                port=c["port"],
                status=HealthStatus.UNKNOWN,
            )
            for c in MONARCH_HEALTH_COMPONENTS
        ]

        from .schema import CloudQuota, QuotaStatus
        quotas_dict = {
            "claude_pro_1": CloudQuota(
                name="claude_pro_1", provider="anthropic",
                period="weekly", status=QuotaStatus.OK,
            ),
            "claude_pro_2": CloudQuota(
                name="claude_pro_2", provider="anthropic",
                period="weekly", status=QuotaStatus.OK,
            ),
            "deepseek_v4_flash": CloudQuota(
                name="deepseek_v4_flash", provider="deepseek",
                period="monthly", budget_usd=20.0,
                used_usd=0.0, status=QuotaStatus.OK,
            ),
            "kimi_k2_6": CloudQuota(
                name="kimi_k2_6", provider="moonshot",
                period="monthly", budget_usd=10.0,
                used_usd=0.0, status=QuotaStatus.OK,
            ),
            "haiku_4_5": CloudQuota(
                name="haiku_4_5", provider="anthropic",
                period="monthly", budget_usd=15.0,
                used_usd=0.0, status=QuotaStatus.OK,
            ),
            "anthropic_api_direct": CloudQuota(
                name="anthropic_api_direct", provider="anthropic",
                period="monthly", budget_usd=None,
                used_usd=0.0, status=QuotaStatus.OK,
            ),
        }

        return SystemModel(
            tiers=tiers,
            workloads=Workloads(),
            schedule=Schedule(),
            quotas=Quotas(quotas=quotas_dict),
            resources=Resources(),
            operator=Operator(),
            health=Health(components=health_components),
            daemon_pid=os.getpid(),
        )
