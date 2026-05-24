# Jarvis & v19 Handoff — 2026-05-24

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

v19 doctrine: **4 of 6 cardinals closed** (Decisions 1, 4, 5, 6). Decisions 2 (Hermes) and 3 (T6) remain open — each prerequisite-blocked, not stuck on a walkthrough. Jarvis substrate Phase 1 (vram.py, tier_health.py) live; Phase 2 listeners (process.py, quota.py, cron.py) specced, unbuilt. Path B dual-session topology live since 2026-05-21. Standard mode baseline at 66% per Rebalance Change 1 (Change 2 patched, measurement pending next natural T1 restart). Authority model (Decision 5) ratified 2026-05-24 — three-tier autonomous-immediate / autonomous-with-log / surface-and-ask, N=12 promotion threshold, strict cold-start, Quota Cascade Policy with fullest-peer rotation. See `Session 2026-05-24` section below for the closure details.

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
| 2 | Hermes Pattern B adoption (parallel to n8n, Curator narrow-scope, memory disabled, routed cloud initially) | OPEN — blocked on v18 Hermes brainstorm docs (audit §A7 flags these may not exist as discrete artifacts) |
| 3 | T6 defaults: Qwen3.6-35B-A3B UD-Q4_K_XL, 25% expert offload, 64K context | OPEN; model not downloaded |
| 4 | Cascade restructured into structural classes: workflow-tier-zero (Pro) / peer rotation (DeepSeek V4 Flash ↔ Kimi K2.6) / emergency rung (Anthropic direct, vestigial). Cowork retired. | CLOSED 2026-05-19; amended 2026-05-24 (class reframe + Haiku 4.5 deprecation) — see DECISIONS_v19.md |
| 5 | Jarvis authority levels (immediate / with-log / surface-and-ask). N=12 uniform promotion threshold, strict cold-start (no override at introduction; material behavior change re-enters Tier 3), Quota Cascade Policy. | CLOSED 2026-05-24 — see DECISIONS_v19.md, AUTHORITY_SPEC_v19.md |
| 6 | v19 scope: Jarvis + Financial = phase-level; Nexus = design only; 2nd Brain = deferred | CLOSED 2026-05-19 — see DECISIONS_v19.md |

Operator preferences expressed in v18 thread:
- Financial intensive work routes to API (money-on-line discipline)
- News pipeline once-daily is light load
- Two Claude Pro accounts for building/design
- T6 is overflow valve when Pro walls, NDA-tagged work, or quality-needed local coding
- Jarvis is **manager first**, voice assistant a distant second

## Standard Mode Rebalance — Change 1 Executed; Change 2 Patched (Measurement Deferred)

Target: baseline ≤ 80% (≤ 19.6 GB) to leave headroom for T6 and active workloads.

Proposed:
- T1: 36K → 24K context, frees ~1 GB (assumes Decision 1 — T1 becomes Hermes/Jarvis host, not OpenCode harness)
- T2: drop from always-on to burst-only, frees 6.8 GB (assumes Decision 4 — synthesis goes to cloud)
- T4: optionally reduce -np 4 → -np 2, frees ~1 GB
- Result: baseline ~14-15 GB / 60% — plenty of room for T6 expert-offload burst

Change 1 (T2 → burst-only) executed and live-validated 2026-05-20: t2-down baseline 66.1% measured via jarvis-q vram, idempotent, Jarvis catches transitions inside 5s polling. Change 2 (T1 ctx 36K → 24K) gated on cold-cycle test of inference-up patch. Change 3 (T4 -np 4 → 2) deferred per REBALANCE_v19.md.

## Path B — Dual-Session Topology (2026-05-21)

Operational change to the tmux session topology. Promoted live on 2026-05-21
and validated end-to-end via cold cycle test. The system now runs across
**two tmux sessions** instead of one. The split mirrors v19 doctrine's
control-plane / dataplane distinction structurally rather than via
maintenance discipline.

### Partition

| Session | Lifetime | Windows | Notes |
| --- | --- | --- | --- |
| `control` | long-lived; survives `inference-down` | bootstrap, jarvis, validation-gate, lora-dispatcher, litellm, t1-interactive | T1 is the Jarvis-facing reasoning brain per Decision 1; LiteLLM routes to cloud during burst-down; vg/ld/jarvis are services, not tiers. |
| `inference` | dataplane; cycle-safe | bootstrap, t3-content, t4-phi4, t5-small (+ t2-pipeline burst when up, t6-coder burst when deployed) | `tmux kill-session -t inference` is now semantically safe — only dataplane dies. |

### Why this exists

Pre-Path-B, `inference-down` ran `tmux kill-session -t inference` which
took T1, LiteLLM, validation-gate, lora-dispatcher, and jarvis with it
every time the dataplane needed to cycle. The teardown script then ran a
straggler-kill prompt that offered to `sudo kill -9` the very services
it had just (correctly) destroyed. The defensive design was: an operator
would notice T1's PID in the list and decline. That depended on operator
attention at the moment of cycle.

Path B removes the need for defense by removing the failure mode. Control-
plane services live in a separate session whose lifetime is decoupled
from the dataplane's.

### What changed

**Operator scripts (not in repo, edited in parallel):**

- `~/bin/inference-up` — dual-session aware. Creates `control` session
  if missing (idempotent). Per-service `already_up` port-check guards
  skip launches for control-plane services already running. Smoke
  tests still run unconditionally. Zombie-check rewritten to filter
  control-session survivors as expected (via parent-walk PID→session
  resolution); only non-control GPU processes abort the bringup.
- `~/bin/inference-down` — kills only `inference` session. Surviving
  GPU processes are inspected and reported with tmux affiliation, not
  killed. No force-kill prompt under any flag.
- `~/bin/t2-up`, `~/bin/t2-down` — unchanged. Both already used
  `TMUX_SESSION="inference"` as a variable; T2 is dataplane.

**Repo file (commit `9858a6a`):**

- `deploy.sh` — Jarvis daemon window now created in `${CONTROL_SESSION}`
  instead of `inference`.

### Validation evidence (2026-05-21 04:14–04:21 EDT)

- `tmux move-window` verified safe for a VRAM-resident llama-server. T1
  retained its 12 GB VRAM allocation, stayed bound on :8080, and passed
  a coherence test (`OK`) immediately after the move and again after a
  full dataplane cycle.
- Jarvis daemon writer thread maintained its documented 10s cadence
  through the session reassignment (mtime advanced 04:15:21 → 04:15:31).
- Full cold cycle: `inference-down` → 12,067 MiB VRAM (T1 + driver +
  jarvis tracking only, control session intact) → `inference-up`
  exercised the idempotent path (T1/LiteLLM/VG/LD all reported "already
  serving — skipping launch") → 16,247 MiB (back to baseline).

### Implications for future work

- Phase 2 listeners (`process.py`, `quota.py`, `cron.py`) can rely on
  T1 + LiteLLM + jarvis being co-located in `control` and durable across
  dataplane cycles. No special handling for "is T1 currently up?" needed
  in those listeners.
- Decision 5 (Jarvis authority) — the `inference-down` rewrite removed
  an `[y/N]` prompt that asked operator confirmation for a destructive
  action. That kind of script-level safety question gets simpler under
  Path B because the dangerous case (killing the preserve list) is
  structurally impossible now.
- Rebalance Change 2 measurement (T1 at 24K context) — still deferred.
  T1 survives the cycle by design under Path B, so the schema/launch-
  line patch in `c0f7ea7` lands naturally on next T1 restart (reboot,
  explicit control-session kill, or operator-initiated T1 cycle).

### Backups on disk (operator-side, not in repo)

- `~/bin/inference-up.preB-backup` — pre-topology version
- `~/bin/inference-up.zombie-fix-backup` — Path B version before the
  zombie-check rewrite (intermediate, kept for diff reference)
- `~/bin/inference-down.preB-backup` — pre-Path-B teardown script
- `~/projects/jarvis/deploy.sh.preB-backup` — local backup; ignored by git

Rollback is one `mv` per file. Filtered from the repo via `.gitignore`
patterns `*.preB-backup` and `*.zombie-fix-backup`.

### Principle exposed

Path B is a worked example of a broader pattern: when a Tier 3
(surface-and-ask) prompt fires repeatedly for the same underlying
reason, the right move is sometimes architectural elimination, not
tighter criteria. The `[y/N]` straggler prompt in pre-Path-B
`inference-down` was the operator's last line of defense against a
destructive default. Path B removed the *need* for defense by removing
the failure mode. Future authority decisions should consider this
option when a Tier 3 keeps recurring: redesign rather than refine.

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

The new chat should NOT re-litigate closed cardinals. It should:
1. Run `jarvis-q all` to see live state
2. Read this handoff + Jarvis CLAUDE.md + news-pipeline CONTEXT.md
3. Read the `Session 2026-05-24` section below for the three open follow-ups (C2 spec-surface; provider-name-row location + rename; doc-cleanup)

Decisions 2 and 3 are the remaining open cardinals but both are prerequisite-blocked (Hermes brainstorm docs may not exist; T6 model not downloaded). The forward-momentum path is the three small follow-ups, then `process.py` (no prereqs, ~2-3 hr Claude Code mission), then `quota.py` (~3-4 hr after the follow-ups land).

## Session 2026-05-24 — Decision 5 Close + Decision 4 Amendments

**Doctrine ratified this session:**

- **Decision 5 closed.** Items 6/7/8 + Quota Cascade Policy banked. Strict cold-start (all new actions begin Tier 3, no override at introduction; material behavior change to an existing action re-enters Tier 3). N=12 uniform promotion threshold across both rungs — minimum 24 operator-acknowledged successful runs from cold-start to silent operation (12 at Tier 3 + 12 at Tier 2). Pro tier estimation descoped (Pro is workflow-tier-zero, not Jarvis-routed; re-open condition: automated Pro-1 → Pro-2 → T6 failover is built). Quota Cascade Policy with fullest-peer rotation between DeepSeek V4 Flash ↔ Kimi K2.6 at 20% / 10% remaining + drain phase per-percent notification overlay.
- **Decision 4 amended (v1):** cascade restructured into structural classes. Workflow-tier-zero (Pro, operator-driven) / peer rotation (DeepSeek / Kimi) / latency niche (Haiku) / emergency rung (Anthropic direct).
- **Decision 4 amended (v2):** Haiku 4.5 deprecated same day. Pricing parity with DeepSeek V4 Flash at lower capability makes it redundant. Latency niche class removed; operational cascade is now three classes. Re-open condition: a future provider with a genuinely-distinct latency profile re-justifies a latency niche class.

**Operational reality of the cloud cascade as of 2026-05-24:**

| Class | Providers | Wired? |
|---|---|---|
| Workflow-tier-zero | Claude Pro ×2 | N/A (operator-driven, not Jarvis-routed) |
| Peer rotation | DeepSeek V4 Flash, Kimi K2.6 | ✅ Wired |
| Emergency rung | Anthropic API direct | ⏳ Vestigial — doctrine-forward, not yet wired |

**Schema reality check (audit residue, not patched here):** `~/projects/jarvis/jarvis/schema.py` defines the `CloudQuota` Pydantic class but no provider name rows are hardcoded in `schema.py`. Bible §13.2 conflated the class definition with row data and is stale on this. Provider name rows live elsewhere (config / env / DB seed — to be located). The `deepseek_v3 → deepseek_v4_flash` rename happens wherever those rows actually live.

**New authority primitive introduced (scoped to Quota Cascade Policy):** Tier 2 action with a notification overlay. Routing action stays autonomous-with-log; operator-facing notification rides on top without converting to Tier 3. Not elevated to general AUTHORITY_SPEC primitive in this commit (re-open condition: a second action requires the same overlay shape).

**Three open follow-ups for next session:**

1. **C2 — LiteLLM logging path decision (~30 min, real walkthrough).** Spec already documents that LiteLLM postgres logging is DISABLED (`JARVIS_PHASE2_SPEC.md` line 111 area) and offers three options: Path A (separate `litellm_logs` postgres DB, structured queries via `spend_logs`, ~15 min one-time setup), Path B (JSON file log tailing, no DB risk, messier parse), Path C (defer until after process.py). Spec recommends A but does not ratify. **Decision required** before quota.py work begins. Earlier framing of this in-session as a ~5-min spec-surface task conflated "fact surfaced" with "decision made" — the determination is still open.
2. **Provider-name-row location + rename (~15 min).** PHASE2_SPEC §quota.py references a function `_build_initial_model()` as the location for CloudQuota row construction — file location not specified there. Find it: `grep -rn "_build_initial_model" ~/projects/jarvis/jarvis/`. Confirm what provider rows are present operationally (likely a subset of `deepseek_v3`, `kimi_k2_6`, `claude_pro_1`, `claude_pro_2`). Do the `deepseek_v3 → deepseek_v4_flash` rename in-place. Add bible §13.2 correction noting schema.py defines the class but not the row data.
3. **Doc-cleanup small commit (~15 min).** Three stale-doc items: (a) DECISIONS_v19.md "Note on Rebalance Headroom" projects ~14-15 GB / 60% baseline; actual 16.5 GB / 66% per bible §11.1. (b) DECISIONS "What's Now Unblocked" treats Standard mode rebalance as future work; Change 1 executed, Change 2 patched. HANDOFF Standard Mode Rebalance section's "Result: baseline ~14-15 GB / 60%" line is a pre-execution projection (actual 16.5 GB / 66%). (c) JARVIS_PHASE2_SPEC.md broader sweep — one CloudQuota-instructions section already marked DEPRECATED 2026-05-24 in this session's cleanup commit, but other "5-tier" / haiku references remain elsewhere in the spec. `grep -n -i -E "5-tier|haiku" JARVIS_PHASE2_SPEC.md` surfaces them.

After (1) and (2) land, `quota.py` is unblocked at doctrine + logging-path + schema-row level. `process.py` is buildable today regardless (no further prereqs). Authority model is doctrine-complete — listener implementation work can begin whenever Claude Code picks it up.

**Carried open items unchanged from prior sessions:**

- A1 — Rebalance Change 2 measurement (T1 ctx 36K → 24K patched, awaits next natural T1 restart).
- B1 / B-D2 — Decision 2 (Hermes), blocked on missing v18 brainstorm docs.
- B2 / B-D3 — Decision 3 (T6 defaults), blocked on 21 GB model download + `~/bin/t6-up` / `~/bin/t6-down` tooling + A1 measurement.

---

Built across one long session: Step 1 hygiene → Jarvis v0.1 deploy → v0.1 deadlock discovered via telemetry → v0.2 rewrite with snapshot/queue → soak verified → 80% target view added → 5.5 GB phi-4 cache reclaimed.

The single most consequential finding: the hardware feels useless because v18 sized standard mode for the loading screen, not for use. Jarvis made this visible. v19 doctrine is mostly about giving each tier a job that matches the actual workload distribution.
