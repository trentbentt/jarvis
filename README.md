# Jarvis

Monarch system manager and observability daemon. Pydantic schema + queued-write state store + listener threads polling the inference stack. Built as the foundation layer for `master_summary v19` doctrine.

**Status:** v0.2 substrate live. Phase 2 listeners (process, quota, cron) not yet built.

## Quick start

```bash
cd ~/projects/jarvis
./deploy.sh                # one-time setup
jarvis-q all               # current system state
jarvis-q vram              # VRAM with 80% target line
jarvis-q events 20         # recent events
jarvis-q tiers             # per-tier config + state
```

## Documents (read in this order)

1. **`HANDOFF_v19.md`** — current operational state; start here in any new session
2. **`DECISIONS_v19.md`** — six cardinal decisions; Decisions 1, 4, 6 closed
3. **`REBALANCE_v19.md`** — standard-mode VRAM rebalance proposal
4. **`JARVIS_PHASE2_SPEC.md`** — process / quota / cron listener build specs
5. **`CLAUDE.md`** — architecture and code-level notes for future Claude sessions

## Architecture

- `jarvis/schema.py` — Pydantic schema (8 domains), `MONARCH_TIERS` constants are the source of truth for tier config
- `jarvis/state.py` — thread-safe state store: snapshot-on-read, queue-on-write, single writer thread
- `jarvis/listeners/vram.py` — nvidia-smi → per-tier attribution via PID→port mapping (5s poll)
- `jarvis/listeners/tier_health.py` — HTTP polling of every inference service endpoint (15s poll)
- `daemon.py` — entry point; persists state.json every 10s

State lives at `~/.local/state/jarvis/state.json`. Logs at `~/.local/state/jarvis/daemon.log`.

## Related operator-side files (not in this repo)

- `~/bin/inference-up` — brings up the inference stack; honors `burst_only` flag
- `~/bin/t2-up`, `~/bin/t2-down` — operator scripts for the burst-only T2 tier
- `~/litellm/config.yaml` — router config with restored DeepSeek V4 Flash fallback
