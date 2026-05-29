"""
Cron Listener v0.2

Schedule reconciliation. Polls cron sources every 60s, computes upcoming runs,
and surfaces drift: missed runs, near-collisions, and stale entries (target
script gone). Observability-only — emits events, takes no action.

Spec: master_summary §12.4 ("cron.py — schedule reconciliation").

── Design notes (P2-3 design walk, 2026-05-29) ────────────────────────────────
- Log path is DERIVED from each crontab line's `>> <path>` redirect, not a
  hardcoded JOB_LOG_MAP — the crontab is self-describing, so this stays correct
  as jobs change.
- Cron runs in system-LOCAL tz (America/New_York here); Jarvis stores UTC.
  Next/prev runs are computed with croniter on a local-aware base, then
  converted to UTC.
- Missed-run signal: the most-recent scheduled occurrence is "missed" if it was
  due more than GRACE ago AND the job's log mtime predates it (log not touched
  at/after the scheduled time). Heuristic; jobs with no derivable log are
  skipped (can't tell).
- Scope: user crontab + /etc/cron.d. systemd timers (OS housekeeping) are out
  of scope. VRAM-collision forecasting is deferred (doctrine optional).
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from croniter import croniter

from .base import BaseListener
from ..schema import Collision, CronJob, MissedRun, ScheduledRun
from ..state import StateStore

logger = logging.getLogger(__name__)

_GRACE = timedelta(minutes=15)          # time allowed for a due job to run + write its log
_UPCOMING_WINDOW = timedelta(minutes=60)
_COLLISION_GAP = timedelta(minutes=5)
_CRON_D_DIR = "/etc/cron.d"


def _run(cmd: List[str], timeout: float = 3.0) -> Optional[str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _local_now() -> datetime:
    """System-local timezone-aware now (the frame cron schedules run in)."""
    return datetime.now().astimezone()


def _extract_log(cmd: str) -> Optional[str]:
    m = re.search(r">>?\s*(\S+)", cmd)
    if not m:
        return None
    path = os.path.expanduser(m.group(1))
    # /dev/null (and other /dev sinks) are not real logs — using their mtime
    # would yield false "missed run" flags.
    if path == "/dev/null" or path.startswith("/dev/"):
        return None
    return path


def _strip_redirects(cmd: str) -> str:
    # Drop everything from the first redirect operator onward.
    return re.split(r"\s*\d?>>?", cmd, maxsplit=1)[0].strip()


def _target_script(cmd: str) -> str:
    toks = _strip_redirects(cmd).split()
    return toks[0] if toks else cmd


def _parse_line(line: str, has_user: bool) -> Optional[Tuple[str, str]]:
    """Return (schedule_expr, command) or None for blanks/comments/env-assigns."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", line):   # env assignment (SHELL=, PATH=, MAILTO=)
        return None
    if line.startswith("@"):
        parts = line.split(None, 2 if has_user else 1)
        if has_user and len(parts) >= 3:
            return parts[0], parts[2]
        if not has_user and len(parts) >= 2:
            return parts[0], parts[1]
        return None
    n = 6 if has_user else 5
    parts = line.split(None, n)
    if len(parts) < n + 1:
        return None
    schedule = " ".join(parts[:5])
    command = parts[n]
    return schedule, command


def _mtime_utc(path: str) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    except (FileNotFoundError, PermissionError, OSError):
        return None


class CronListener(BaseListener):
    name = "cron"
    interval_sec = 60.0

    def __init__(self) -> None:
        super().__init__()
        self._last_missed: set[str] = set()
        self._last_stale: set[str] = set()
        self._last_collisions: set[frozenset] = set()

    def _gather_sources(self) -> List[Tuple[str, str, bool]]:
        """Return (raw_line, source_label, has_user) for every cron source line."""
        out: List[Tuple[str, str, bool]] = []
        crontab = _run(["crontab", "-l"])
        if crontab:
            for ln in crontab.splitlines():
                out.append((ln, "crontab", False))
        try:
            for fname in sorted(os.listdir(_CRON_D_DIR)):
                if fname.startswith(".") or fname == "placeholder":
                    continue
                fpath = os.path.join(_CRON_D_DIR, fname)
                try:
                    text = Path(fpath).read_text()
                except (PermissionError, OSError):
                    continue
                for ln in text.splitlines():
                    out.append((ln, f"/etc/cron.d/{fname}", True))
        except (FileNotFoundError, PermissionError, OSError):
            pass
        return out

    def poll(self) -> None:
        now_local = _local_now()
        now_utc = now_local.astimezone(timezone.utc)

        jobs: List[CronJob] = []
        missed: List[MissedRun] = []
        upcoming: List[ScheduledRun] = []
        stale: List[str] = []

        for raw, source, has_user in self._gather_sources():
            parsed = _parse_line(raw, has_user)
            if parsed is None:
                continue
            schedule, command = parsed
            if not croniter.is_valid(schedule):
                continue

            command = command.strip()
            target = _target_script(command)
            # Scope: monarch workload jobs target an absolute/home path. Shell
            # builtins and conditionals (test, [, command -v …) lead the system
            # /etc/cron.d housekeeping entries — same OS-housekeeping category as
            # systemd timers, which are out of scope. Skip non-path targets.
            if not (target.startswith("/") or target.startswith("~")):
                continue
            name = os.path.basename(target)
            log_path = _extract_log(command)
            clean_cmd = _strip_redirects(command)

            # next / prev run in local tz, stored as UTC
            try:
                nxt_local = croniter(schedule, now_local).get_next(datetime)
                prev_local = croniter(schedule, now_local).get_prev(datetime)
            except Exception:
                continue
            nxt_utc = nxt_local.astimezone(timezone.utc)

            jobs.append(CronJob(
                name=name, schedule=schedule, command=clean_cmd,
                log_path=log_path, source=source, next_run=nxt_utc,
            ))

            # upcoming within 60 min
            if nxt_utc - now_utc <= _UPCOMING_WINDOW:
                upcoming.append(ScheduledRun(name=name, next_run=nxt_utc))

            # stale: a path-like target that doesn't exist
            if (target.startswith("/") or target.startswith("~")) and not os.path.exists(target):
                stale.append(name)

            # missed: prev run due > GRACE ago and log not touched since
            if (now_local - prev_local) > _GRACE and log_path:
                lm = _mtime_utc(log_path)
                prev_utc = prev_local.astimezone(timezone.utc)
                if lm is not None and lm < prev_utc:
                    missed.append(MissedRun(
                        name=name, scheduled_for=prev_utc,
                        log_path=log_path, last_log_mtime=lm,
                    ))

        # collisions: upcoming pairs within 5 min
        collisions: List[Collision] = []
        su = sorted(upcoming, key=lambda r: r.next_run)
        for i in range(len(su)):
            for j in range(i + 1, len(su)):
                gap = su[j].next_run - su[i].next_run
                if gap <= _COLLISION_GAP:
                    collisions.append(Collision(
                        job_a=su[i].name, job_b=su[j].name,
                        run_a=su[i].next_run, run_b=su[j].next_run,
                        gap_sec=int(gap.total_seconds()),
                    ))
                else:
                    break  # sorted — no closer pair past this point

        def update(model):
            s = model.schedule
            s.cron_entries = jobs
            s.missed_runs_24h = missed
            s.upcoming_60min = sorted(upcoming, key=lambda r: r.next_run)
            s.collisions = collisions
            s.stale_entries = sorted(set(stale))
            s.cron_updated_at = now_utc

        StateStore.get().apply(update)
        self._emit_transitions(missed, stale, collisions)

    def _emit_transitions(self, missed, stale, collisions) -> None:
        store = StateStore.get()

        missed_names = {m.name for m in missed}
        for m in missed:
            if m.name not in self._last_missed:
                store.emit(
                    type="cron_missed_run", severity="warning",
                    detail=f"{m.name} missed scheduled run at "
                           f"{m.scheduled_for.isoformat()} (log stale)",
                )
                logger.warning("[cron] missed run: %s", m.name)
        self._last_missed = missed_names

        stale_set = set(stale)
        for name in stale_set:
            if name not in self._last_stale:
                store.emit(
                    type="cron_stale_entry", severity="warning",
                    detail=f"{name}: cron target script does not exist",
                )
                logger.warning("[cron] stale entry: %s", name)
        self._last_stale = stale_set

        coll_set = {frozenset((c.job_a, c.job_b)) for c in collisions}
        for c in collisions:
            pair = frozenset((c.job_a, c.job_b))
            if pair not in self._last_collisions:
                store.emit(
                    type="cron_collision_warning", severity="info",
                    detail=f"{c.job_a} and {c.job_b} run within {c.gap_sec}s "
                           f"(next 60 min)",
                )
        self._last_collisions = coll_set
