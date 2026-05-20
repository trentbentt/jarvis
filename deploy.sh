#!/usr/bin/env bash
# deploy.sh — install Jarvis v0.1 on monarch
# Run from the directory containing this file (~/projects/jarvis/)
#
# What it does:
#   1. Verifies prerequisites (venv, nvidia-smi)
#   2. Installs pydantic into the inference venv (already present via litellm)
#   3. Creates state/log directories
#   4. Installs jarvis-q symlink into ~/bin/
#   5. Adds a 'jarvis' window to the inference tmux session
#   6. Verifies the daemon starts and produces a state file

set -euo pipefail

JARVIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$HOME/venv/inference}"
STATE_DIR="$HOME/.local/state/jarvis"
BIN_DIR="$HOME/bin"

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
blue()   { printf '\033[36m%s\033[0m\n' "$*"; }

blue "═══ Jarvis v0.1 deploy ═══"
blue "Jarvis dir : $JARVIS_DIR"
blue "Venv       : $VENV"

# ─── Prerequisites ────────────────────────────────────────────────────────────
if [ ! -f "$VENV/bin/activate" ]; then
  red "Inference venv not found at $VENV"
  red "Run inference-up first or set VENV=/path/to/your/venv"
  exit 1
fi

if ! command -v nvidia-smi &>/dev/null; then
  red "nvidia-smi not found — VRAM listener will not work"
  exit 1
fi

green "Prerequisites OK"

# ─── Directories ──────────────────────────────────────────────────────────────
mkdir -p "$STATE_DIR" "$BIN_DIR"
green "Directories: $STATE_DIR  $BIN_DIR"

# ─── Python dependencies ──────────────────────────────────────────────────────
# pydantic is almost certainly already installed via litellm, but ensure it.
source "$VENV/bin/activate"
python3 -c "import pydantic; assert int(pydantic.__version__.split('.')[0]) >= 2, 'Need pydantic>=2'" \
  && green "pydantic >= 2 ✓" \
  || {
    yellow "Installing pydantic >= 2…"
    pip install "pydantic>=2.0.0" --quiet
  }

# ─── jarvis-q symlink ─────────────────────────────────────────────────────────
chmod +x "$JARVIS_DIR/bin/jarvis-q"
ln -sf "$JARVIS_DIR/bin/jarvis-q" "$BIN_DIR/jarvis-q"
green "Installed: ~/bin/jarvis-q → $JARVIS_DIR/bin/jarvis-q"

# ─── Verify the package imports cleanly ───────────────────────────────────────
python3 -c "
import sys; sys.path.insert(0, '$JARVIS_DIR')
from jarvis.schema import SystemModel
from jarvis.state import StateStore
from jarvis.listeners import VRAMListener, TierHealthListener
print('Package imports OK')
" || { red "Import check failed — check the output above"; exit 1; }
green "Package imports ✓"

# ─── Start daemon in inference tmux session ───────────────────────────────────
if tmux has-session -t inference 2>/dev/null; then
  # Kill any existing jarvis window first
  tmux kill-window -t inference:jarvis 2>/dev/null || true
  sleep 1

  tmux new-window -t inference -n jarvis \
    "source $VENV/bin/activate && \
     cd $JARVIS_DIR && \
     JARVIS_STATE_PATH=$STATE_DIR/state.json \
     JARVIS_LOG_PATH=$STATE_DIR/daemon.log \
     python3 daemon.py 2>&1 | tee $STATE_DIR/daemon.log"

  green "Daemon window created: tmux attach -t inference → jarvis"

  # Wait up to 45s for the state file to appear
  yellow "Waiting for first state write (up to 45s)…"
  for i in $(seq 1 45); do
    if [ -f "$STATE_DIR/state.json" ]; then
      green "State file written after ${i}s ✓"
      break
    fi
    sleep 1
    if [ "$i" -eq 45 ]; then
      red "State file not written in 45s — check: tmux attach -t inference → jarvis window"
      exit 1
    fi
  done

  # Quick sanity check
  source "$VENV/bin/activate"
  python3 "$JARVIS_DIR/bin/jarvis-q" health 2>/dev/null || yellow "(jarvis-q health returned non-zero — first run may have unknown states)"

else
  yellow "No 'inference' tmux session found."
  yellow "Start the daemon manually after running inference-up:"
  echo ""
  echo "  tmux attach -t inference"
  echo "  # Open a new window: Ctrl+B c"
  echo "  source ~/venv/inference/bin/activate"
  echo "  cd ~/projects/jarvis && python3 daemon.py"
fi

# ─── Done ─────────────────────────────────────────────────────────────────────
echo ""
green "═══ Deploy complete ═══"
echo ""
echo "  Query:   jarvis-q all"
echo "  VRAM:    jarvis-q vram"
echo "  Health:  jarvis-q health"
echo "  Events:  jarvis-q events"
echo "  Daemon:  tmux attach -t inference → jarvis window"
echo "  Logs:    tail -f $STATE_DIR/daemon.log"
