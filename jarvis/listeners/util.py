"""
Shared listener utilities.

Helpers used by more than one listener live here. Promoted out of vram.py
when process.py needed the same port→tier PID attribution (per
master_summary §12.4: "promote from vram.py to jarvis/listeners/util.py").
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def _port_from_cmdline(pid: int) -> Optional[int]:
    """Parse the --port argument from a process's /proc/{pid}/cmdline.

    Returns the port int if found, else None. Swallows FileNotFoundError /
    PermissionError so a vanished or inaccessible PID is simply "no port".
    """
    try:
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
        args = cmdline.decode("utf-8", errors="replace").split("\x00")
        for i, arg in enumerate(args):
            if arg in ("--port", "-port") and i + 1 < len(args):
                try:
                    return int(args[i + 1])
                except ValueError:
                    pass
            m = re.match(r"^--port=(\d+)$", arg)
            if m:
                return int(m.group(1))
    except (FileNotFoundError, PermissionError):
        pass
    return None
