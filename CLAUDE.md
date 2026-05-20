# Jarvis — CLAUDE.md

## What This Is

Jarvis is the resource manager and orchestration layer for the monarch inference stack. It maintains a continuously-updated model of system state (VRAM, tier health, workloads, cloud quotas, scheduled events) and will eventually make autonomous allocation decisions to prevent failures under contention.

**Current version: v0.1** — observability substrate only. Listeners collect data; no decisions are made yet. The decision engine and voice surface are Phase 2.

## Architecture

```
daemon.py           ← main process; starts listeners, writes state.json every 30s
jarvis/
  schema.py         ← Pydantic models for all 8 domains (the canonical truth)
  state.py          ← thread-safe singleton StateStore; load_from_disk() for CLI
  listeners/
    base.py         ← BaseListener: interval polling, error isolation per thread
    vram.py         ← 5s; nvidia-smi; attributes VRAM to tiers via PID→port→tier
    tier_health.py  ← 15s; HTTP /health polls all service endpoints
    # TODO Phase 2:
    # process.py   ← 10s; /proc for PID uptime, RAM resident, CPU%
    # quota.py     ← 60s; LiteLLM log parsing + Pro usage telemetry
    # cron.py      ← 5min; schedule reconciliation against crontab + Hermes
bin/
  jarvis-q          ← CLI; reads state.json; subcommands: vram/health/tiers/etc.
```

## Running

```bash
# The daemon runs as a window in the inference tmux session.
# deploy.sh creates it automatically.
tmux attach -t inference   # → jarvis window

# Query from anywhere on monarch:
jarvis-q all
jarvis-q vram
jarvis-q health
jarvis-q tiers
jarvis-q events 30
```

## State file

`~/.local/state/jarvis/state.json` — written every 30s by daemon. Atomic replace (writes .tmp then renames). The CLI reads this file directly; no live connection to the daemon needed.

## Monarch hardware constants (in schema.py)

RTX 3090 FE · 24576 MiB VRAM · Ryzen 9 9900X · 96 GB DDR5-6000 · 4TB NVMe · PCIe 4.0 x16 · CUDA 12.8 pinned (11 packages on apt-mark hold).

## Tier configuration (in schema.py — MONARCH_TIERS)

| Tier | Port | Model            | Context | np | Notes              |
|------|------|------------------|---------|----|-------------------|
| T1   | 8080 | Qwen3.6-27B Q4   | 36K     | 1  | Hermes/Jarvis host |
| T2   | 8083 | Qwen3.6-27B Q4   | 16K     | 1  | Bounded summaries  |
| T3   | 8084 | Qwen3.6-27B Q4   | 8K      | 1  | CPU-only           |
| T4   | 8002 | Phi-4-mini Q4    | 16K     | 4  | Fast classifier    |
| T5   | 8085 | Qwen3-1.7B Q5    | 8K      | 1  | CPU-only seed      |
| T6   | 8086 | Qwen3.6-35B-A3B  | 64K     | 1  | OFFLINE — on-demand coder burst |

T6 is `enabled=False` in MONARCH_TIERS. The listener treats it as OFFLINE until a coder-up script brings it live.

## Open items for Phase 2

- `listeners/process.py` — PID uptime, RAM resident, CPU% per tier
- `listeners/quota.py` — LiteLLM log parsing for API cost tracking; Pro usage telemetry
- `listeners/cron.py` — crontab + Hermes schedule reconciliation → `model.schedule`
- Postgres persistence for `events.log` and `workloads.completed`
- Decision engine (profile-based VRAM allocation)
- Voice surface (operator notification)

## Updating this file

Update CLAUDE.md whenever:
- A new listener is added
- The tier configuration changes (update MONARCH_TIERS in schema.py AND the table above)
- The state file path changes
- The project moves to a new phase

## What Jarvis is NOT (v0.1)

- Not a decision maker — it watches, does not act
- Not a voice assistant — notifications come later
- Not a replacement for inference-up/down — those scripts are unchanged
- Not Hermes — Hermes is the outbound agentic work layer; Jarvis manages resources

## Key files NOT in this repo

- `~/bin/inference-up` — five-tier bringup script (patched May 2026: fail() no longer kills tmux)
- `~/bin/inference-burst-up/down` — burst mode scripts  
- `~/litellm/config.yaml` — LiteLLM routing configuration
- `~/projects/news-pipeline/` — news pipeline (Stages 1-5, validated)
