# Jarvis & v19 Handoff — 2026-05-19

## What Jarvis Is (Architectural Framing)

*Added 2026-05-20. This section establishes the unifying frame for all v19
work. Subsystem-specific docs (DECISIONS, REBALANCE, AUTHORITY_SPEC,
PHASE2_SPEC) describe the parts; this section describes the whole.*

Jarvis is not an observability daemon with notifications. Jarvis is the
**central nervous system of the monarch stack** — the operator's canonical
entry point and the system's internal coordination layer.

### What Jarvis does (function taxonomy)

**Frontend (operator-facing) roles:**

- **Manager** — the operator delegates to Jarvis instead of addressing
  individual subsystems. The operator doesn't inspect the validation
  gate; they ask Jarvis. The operator doesn't watch news pipeline logs;
  they ask Jarvis what happened with news this morning. *(Manager first,
  voice assistant a distant second.)*
- **Personal assistant** — morning briefings, schedule awareness,
  proactive surfacing of what needs attention.
- **Voice interface** — voice-to-voice (Phase 18), distinct from
  Phase 17.5's voice-to-text for agent harnesses.
- **Notification dispatcher** — voice / PWA push / ntfy.sh, with
  authority-tier-aware quieting (sleep window, severity ladder).
- **Documentation router** — operator asks "where's the doc for X" and
  Jarvis points to the right repo/file/section.

**Backend (machine-facing) roles:**

- **Substrate orchestrator** — dispatches workloads across four execution
  substrates based on latency, quality, and resource availability:
  GPU VRAM, system RAM (via CPU inference + expert offload),
  CPU compute, and cloud API. The same workload may land on different
  substrates on different days depending on current resource state.
- **Horizontal coordinator** — relays state and signals between agent
  workflows (news pipeline, financial pipeline, Hermes when adopted,
  LoRA dispatcher).
- **Knowledge bridge** — eventual interface to 2nd Brain (deferred per
  Decision 6) and Nexus (design-only per Decision 6) for "what do we
  know about X" queries.
- **Observability layer** — schema-driven state model, listener threads,
  event log. The IDLE-vs-UNRESPONSIVE work shipped 2026-05-20 lives here.
- **Event router** — receives completion/failure/anomaly signals from
  every pipeline and decides where they need to surface.

### The architectural test

Every subsystem built from v19 forward must answer four questions
about its relationship to Jarvis:

1. **Can Jarvis observe it?** (state, health, activity signals)
2. **Can Jarvis dispatch to it?** (start/stop/route work to it)
3. **Can Jarvis surface its events?** (completions, failures, anomalies)
4. **Can Jarvis explain it?** (point operator at docs, recent activity,
   relevant errors)

A subsystem failing any of these isn't broken — but it isn't fully
integrated into the operator's canonical entry point. Direct operation
of subsystems remains supported and necessary for debugging. The
Jarvis-facing interface is what makes the system feel like one system
instead of seven.

### How this reframes the open queue

Items in the bootstrap's Tier A–E aren't independent operational chores.
They're foundational substrate work the manager will rely on:

- Cold cycle validation → manager can trust burst-mode transitions
- Phase 2 listeners (process, quota, cron) → manager has full
  situational awareness
- Authority spec → operator's contract with the manager about
  autonomous action
- inference-down patch → substrate teardown safe for manager to invoke
- Rebalance Changes 2/3 → headroom for manager to allocate
- T6 spin-up tooling → another substrate the manager dispatches to

The v19 master summary, when written, should treat Jarvis as the
through-line. Subsystems compose around it.

The full Jarvis vision (substrate decision matrix, LoRA routing model,
knowledge-bridge interface design, documentation-router lookup model)
is deferred to a dedicated session producing `JARVIS_VISION_v19.md`.
This section is the seed of that vision, captured before drift loses it.

---

## Where We Are

Mid-transition from master_summary_v18 → v19. Building Jarvis (system manager + observability layer) as the foundation before locking v19 doctrine.

## Hard Facts on Disk

**Monarch baseline (historical — v18 era):** 94% VRAM utilization at idle, no active workloads.
T1 (11.8 GB) + T2 (6.8 GB) + T4 (4.2 GB) + driver (0.5 GB) = 23.1 GB / 24 GB.
This was the central forcing function for v19 doctrine — local cannot carry additional load without restructuring. Drove Decision 1 (architectural reframe) and Rebalance Change 1 (T2 burst-only).

**Monarch baseline (current — post-Rebalance Change 1):** 66.0% VRAM at idle, measured 2026-05-20 across a full cold-cycle teardown and rebuild.
T1 (11.8 GB) + T4 (4.2 GB) + driver (0.5 GB) = 16.5 GB / 24 GB.
T2 is `burst_only` per schema, brought up on-demand via `~/bin/t2-up`, idle-by-default with DeepSeek V4 Flash fallback for pipeline calls (status: IDLE in `jarvis-q health`). Reproducible across the cold cycle — the 94% → 66% delta is durable, not a transient observation.

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
| 1 | Architectural reframe: local = data plumbing + agentic glue + on-demand coder burst. Cloud = synthesis + building + frontier reasoning. | CLOSED 2026-05-19 — see DECISIONS_v19.md |
| 2 | Hermes Pattern B adoption (parallel to n8n, Curator narrow-scope, memory disabled, routed cloud initially) | OPEN |
| 3 | T6 defaults: Qwen3.6-35B-A3B UD-Q4_K_XL, 25% expert offload, 64K context | OPEN; model not downloaded |
| 4 | Cloud routing chain: Pro → DeepSeek V4 Flash → Kimi K2.6 → Haiku → Anthropic direct. Cowork retired. | CLOSED 2026-05-19 — see DECISIONS_v19.md |
| 5 | Jarvis authority levels (immediate / with-log / surface-and-ask) | OPEN |
| 6 | v19 scope: Jarvis + Financial = phase-level; Nexus = design only; 2nd Brain = deferred | CLOSED 2026-05-19 — see DECISIONS_v19.md |

Operator preferences expressed in v18 thread:
- Financial intensive work routes to API (money-on-line discipline)
- News pipeline once-daily is light load
- Two Claude Pro accounts for building/design
- T6 is overflow valve when Pro walls, NDA-tagged work, or quality-needed local coding
- Jarvis is **manager first**, voice assistant a distant second

## Standard Mode Rebalance — Change 1 Executed (Change 2 Pending)

Target: baseline ≤ 80% (≤ 19.6 GB) to leave headroom for T6 and active workloads.

Proposed:
- T1: 36K → 24K context, frees ~1 GB (assumes Decision 1 — T1 becomes Hermes/Jarvis host, not OpenCode harness)
- T2: drop from always-on to burst-only, frees 6.8 GB (assumes Decision 4 — synthesis goes to cloud)
- T4: optionally reduce -np 4 → -np 2, frees ~1 GB
- Result: baseline ~14-15 GB / 60% — plenty of room for T6 expert-offload burst

Change 1 (T2 → burst-only) executed and live-validated 2026-05-20: t2-down baseline 66.1% measured via jarvis-q vram, idempotent, Jarvis catches transitions inside 5s polling. Change 2 (T1 ctx 36K → 24K) gated on cold-cycle test of inference-up patch. Change 3 (T4 -np 4 → 2) deferred per REBALANCE_v19.md.

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
