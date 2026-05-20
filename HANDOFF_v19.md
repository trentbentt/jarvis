# Jarvis & v19 Handoff — 2026-05-19

## Where We Are

Mid-transition from master_summary_v18 → v19. Building Jarvis (system manager + observability layer) as the foundation before locking v19 doctrine.

## Hard Facts on Disk

**Monarch baseline:** 94% VRAM utilization at idle, no active workloads.
T1 (11.8 GB) + T2 (6.8 GB) + T4 (4.2 GB) + driver (0.5 GB) = 23.1 GB / 24 GB.
This is the central forcing function for v19. Local cannot carry additional load without restructuring.

**Inference stack:** five tiers running per `~/bin/inference-up`. Live since May 17. `fail()` patch applied May 19 — tmux survives tier failures now.

**News pipeline:** Stages 1-5 wired and validated. Stage 4 migrated to DeepSeek V4 Flash. One full live cron-fired end-to-end run still outstanding. Lives in `~/projects/news-pipeline/` (git initialized).

**Model storage:** HF cache at `~/.cache/huggingface/hub/` (26 GB after cleanup of unused phi-4 transformers cache May 19). All tiers load via `-hf` shortcut. No `~/models/` migration planned.

**Qwen3.6-35B-A3B (for T6):** NOT yet downloaded. ~21 GB pull needed when T6 tooling lands.

## Jarvis v0.2 — Built & Running

**Location:** `~/projects/jarvis/`. Daemon runs as a window in the `inference` tmux session.

**Architecture:** Pydantic schema (8 domains), thread-safe state store with snapshot-on-read + queue-on-write + single writer thread, two listeners (VRAM 5s, tier_health 15s), JSON state at `~/.local/state/jarvis/state.json` written every 10s.

**v0.1 → v0.2 fix:** v0.1 had RLock contention deadlocks that froze listeners after a few minutes. v0.2 uses snapshot semantics and a writer queue — verified stable across soak.

**Query CLI:** `jarvis-q {vram,health,tiers,workloads,quotas,events,all,json}`.
The `vram` view shows the 80% baseline target on every query, flagging the current 94% as OVER by 3,432 MiB (+14pp).

**See:** `~/projects/jarvis/CLAUDE.md` (architecture), `~/projects/jarvis/daemon.py` (entry point).

## Six Cardinal Decisions — Status

These collectively unlock v19. Most are not yet formally written down.

| # | Decision | State |
|---|----------|-------|
| 1 | Architectural reframe: local = data plumbing + agentic glue + on-demand coder burst. Cloud = synthesis + building + frontier reasoning. | NOT FORMALLY CONFIRMED but operator instinct + 94% baseline math force it |
| 2 | Hermes Pattern B adoption (parallel to n8n, Curator narrow-scope, memory disabled, routed cloud initially) | OPEN |
| 3 | T6 defaults: Qwen3.6-35B-A3B UD-Q4_K_XL, 25% expert offload, 64K context | OPEN; model not downloaded |
| 4 | Cloud routing chain: Pro → DeepSeek V4 Flash → Kimi K2.6 → Haiku → Anthropic direct. Cowork retired. | PARTIALLY EXECUTED in news pipeline; doc-formalization needed |
| 5 | Jarvis authority levels (immediate / with-log / surface-and-ask) | OPEN |
| 6 | v19 scope: Jarvis + Financial = phase-level; Nexus = design only; 2nd Brain = deferred | OPEN |

Operator preferences expressed in v18 thread:
- Financial intensive work routes to API (money-on-line discipline)
- News pipeline once-daily is light load
- Two Claude Pro accounts for building/design
- T6 is overflow valve when Pro walls, NDA-tagged work, or quality-needed local coding
- Jarvis is **manager first**, voice assistant a distant second

## Standard Mode Rebalance — Sketched, Not Built

Target: baseline ≤ 80% (≤ 19.6 GB) to leave headroom for T6 and active workloads.

Proposed:
- T1: 36K → 24K context, frees ~1 GB (assumes Decision 1 — T1 becomes Hermes/Jarvis host, not OpenCode harness)
- T2: drop from always-on to burst-only, frees 6.8 GB (assumes Decision 4 — synthesis goes to cloud)
- T4: optionally reduce -np 4 → -np 2, frees ~1 GB
- Result: baseline ~14-15 GB / 60% — plenty of room for T6 expert-offload burst

Not committed. Requires Decisions 1 and 4 to lock first.

## Open Issues / Hygiene

- `ref-blueprint §Phase 15` body is stale (CONTEXT.md flags this)
- Per-stack CONTEXT.md files (six of them) reference pre-v19 doctrine
- LoRAs: zero trained. Three high-stakes LoRAs (consultancy/design/exploratory) likely deferred indefinitely under Decision 1 reframe.
- Phase 2 Jarvis listeners not built: process.py (PID/RAM/CPU per tier), quota.py (LiteLLM log parsing), cron.py (schedule reconciliation)
- Whisper models in HF cache: kept, used by Phase 17.5 voice dictation setup

## Files That Tell The Real Story (read these first in any new chat)

1. `~/projects/jarvis/HANDOFF_v19.md` — this file
2. `~/projects/jarvis/CLAUDE.md` — Jarvis architecture
3. `~/projects/news-pipeline/CONTEXT.md` — news pipeline real state
4. `~/projects/jarvis/jarvis/schema.py` — MONARCH_TIERS constants are the source of truth for tier config
5. Output of `jarvis-q all` — live system state

## Three Account Drift

Operator runs three Claude accounts on parallel missions. Documentation may be ahead of any one account's chat history. Always verify against:
- Real files on monarch (`cat`, `ls`, `git log`)
- `jarvis-q all` for live state
- Most recent master_summary.md (currently v18) over any old chat transcript

## Recommended Next Move for New Chat

The new chat should NOT re-litigate cardinals 1-6 by speculation. It should:
1. Run `jarvis-q all` to see live state
2. Read this handoff + Jarvis CLAUDE.md + news-pipeline CONTEXT.md
3. Ask operator which cardinal decision to formally close first

The 94% baseline is the data; cardinals 1 + 4 are the lowest-friction wins (already partially executed in practice).

---

Built across one long session: Step 1 hygiene → Jarvis v0.1 deploy → v0.1 deadlock discovered via telemetry → v0.2 rewrite with snapshot/queue → soak verified → 80% target view added → 5.5 GB phi-4 cache reclaimed.

The single most consequential finding: the hardware feels useless because v18 sized standard mode for the loading screen, not for use. Jarvis made this visible. v19 doctrine is mostly about giving each tier a job that matches the actual workload distribution.
