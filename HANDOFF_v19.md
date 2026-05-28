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

**Location:** `~/projects/jarvis/`. Daemon runs as a window in the `control` tmux session (Path B, since 2026-05-21).

**Architecture:** Pydantic schema (9 domains), thread-safe state store with snapshot-on-read + queue-on-write + single writer thread, two listeners (VRAM 5s, tier_health 15s), JSON state at `~/.local/state/jarvis/state.json` written every 10s.

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
- Projected result if all 3 changes execute: baseline ~14-15 GB / 60% (actual post-Change-1: 16.5 GB / 66%; see next paragraph for per-change status)

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

**Schema reality check (resolved 2026-05-24):** Provider name rows live in `jarvis/state.py::_build_initial_model()`, not `schema.py` (`schema.py` defines the `CloudQuota` Pydantic class only). Bible §13.2 corrected. The `deepseek_v3 → deepseek_v4_flash` rename landed in `state.py` lines 225-226. Audit A6 closed.

**New authority primitive introduced (scoped to Quota Cascade Policy):** Tier 2 action with a notification overlay. Routing action stays autonomous-with-log; operator-facing notification rides on top without converting to Tier 3. Not elevated to general AUTHORITY_SPEC primitive in this commit (re-open condition: a second action requires the same overlay shape).

**Follow-up status (all 3 closed):**

1. **C2 — CLOSED 2026-05-24 (Path A ratified).** Walked through in-session: rationale (LiteLLM auto-migration would pollute the shared news-pipeline postgres backing news + n8n + `validation_telemetry` + `lora_swap_telemetry`), Path A (separate `litellm_logs` DB on same postgres instance) ratified with `store_prompts_in_spend_logs=false` (cost/token metadata only — privacy/liability discipline against NDA-tagged work). Implementation specifics (postgres role, connection wiring, LiteLLM config edits) absorbed into the quota.py build task — Claude Code handles against monarch state. See PHASE2_SPEC §quota.py for the full ratification block.
2. **Provider-name-row location + rename — ✅ RESOLVED 2026-05-24.** `_build_initial_model()` located at `jarvis/state.py:195`. Four rows operationally present: `claude_pro_1`, `claude_pro_2`, `deepseek_v4_flash` (was `deepseek_v3`), `kimi_k2_6`. Bible §13.2 corrected. Audit A6 closed.
3. **Doc-cleanup — CLOSED 2026-05-24.** Three stale-doc items resolved this session (see two cleanup commits immediately preceding this one). Items as originally scoped: (a) DECISIONS_v19.md "Note on Rebalance Headroom" projects ~14-15 GB / 60% baseline; actual 16.5 GB / 66% per bible §11.1. (b) DECISIONS "What's Now Unblocked" treats Standard mode rebalance as future work; Change 1 executed, Change 2 patched. HANDOFF Standard Mode Rebalance section's "Result: baseline ~14-15 GB / 60%" line is a pre-execution projection (actual 16.5 GB / 66%). (c) JARVIS_PHASE2_SPEC.md broader sweep — one CloudQuota-instructions section already marked DEPRECATED 2026-05-24 in this session's cleanup commit, but other "5-tier" / haiku references remain elsewhere in the spec. `grep -n -i -E "5-tier|haiku" JARVIS_PHASE2_SPEC.md` surfaces them.

With (1) closed and (2) pending, `quota.py` needs only the schema-row work before it's fully unblocked for Claude Code. `process.py` is buildable today regardless (no further prereqs). Authority model is doctrine-complete — listener implementation work can begin whenever Claude Code picks it up.

**Session 2026-05-24 (evening) — Doctrine propagation sweep**

After today's morning cleanup commits (`385f893` / `e1dfddf` / `d7a8634` — Change-1 baseline refresh, PHASE2_SPEC sweep closure, HANDOFF §3 follow-up closure) and the Decision 5 close + Decision 4 amendments above, the doctrine layer (AUTHORITY_SPEC, DECISIONS) was ahead of the implementation-surface spec (PHASE2_SPEC) and the master_summary. The bible (INFRASTRUCTURE_BIBLE_v19.md) was discovered to be already-propagated on disk from an earlier session today — only PHASE2_SPEC, master_summary, and the audit doc needed touching. Evening sweep landed three commits:

1. **PHASE2_SPEC `quota.py` Pro-descope** (commit `efd495e`) — deleted the "Pro quota estimation (the hard part)" subsection that would have driven Claude Code to build Pro tracking that (a) shouldn't exist per Decision 5 Item 6 closure and (b) couldn't work anyway (Pro auth flows through Claude Code's subscription path, not LiteLLM; Pro requests don't appear in `spend_logs`). Replaced with a descope note pointing to AUTHORITY_SPEC §Quota Cascade Policy. Removed `pro_wall_imminent` from the event emission table.
2. **master_summary_v19** — nine edits: doc-set table AUTHORITY_SPEC row flipped to all-ratified; What-Changed-v19 Items 6-8 bullet rewritten with closure outcomes; open audit items list dropped A6 (closed in `b524bb0`) and A10 (resolved by today's N=12 ratification); §V19B Decision 4 + Decision 5 blocks updated; Tier A2 closed; Tier A3 two-Pro-saturation sub-item dropped; Tier B-D5.6/7/8/Q all flipped to ✅; Tier C3 quota.py prereq updated.
3. **BIBLE_AUDIT_findings** — A10 entry annotated ✅ RESOLVED 2026-05-24 with the note that today's ratification *changed* the value (N=10 → N=12), not merely confirmed it. §F2 Still-open list removed A10.

**Method note (two-strikes drift catch):** The originally-drafted heredoc planned five commits including a bible doctrine-propagation pass. First run aborted Commit 2 on assertion `FAIL 2h` — the bible §13.2 quota.py block on disk had already been edited beyond the project-knowledge upload used to build the heredoc. Diagnostic paste-from-disk revealed the disk had already been Path-A-ratified and A6-closed (per commits earlier today). Rebuilt with scoped 2h edits; re-run aborted on `FAIL 2a` — §6.1 was *also* already fully propagated. A second diagnostic paste against §6.1 / §9.4 / §9.5 / §12.1 showed the disk-actual bible had *all* of today's closure-propagation already in place from an earlier session. Commit 2 was dropped entirely as already-landed. **Lesson recorded: project-knowledge ≠ disk. Always paste-from-disk first when scripting edits against a doc that may have been touched in a parallel session today.** The asserts-with-mock-test pattern caught both drifts before any incorrect commit landed.

**Next-session orientation:** PHASE2_SPEC + bible + master_summary + audit doc now all reflect AUTHORITY_SPEC and DECISIONS truth. Single source of truth restored across the doctrine layer. Next-session reading order works as designed (README → HANDOFF → bible → AUTHORITY_SPEC → DECISIONS → audit) — no cross-doc drift to triage.

**Carried open items unchanged from prior sessions:**

- A1 — Rebalance Change 2 measurement (T1 ctx 36K → 24K patched, awaits next natural T1 restart).
- B1 / B-D2 — Decision 2 (Hermes), blocked on missing v18 brainstorm docs.
- B2 / B-D3 — Decision 3 (T6 defaults), blocked on 21 GB model download + `~/bin/t6-up` / `~/bin/t6-down` tooling + A1 measurement.

---

## Session 2026-05-26 — D1-D4 close + memory architecture design

Long working session. Two distinct workstreams: surgical doctrine-vs-code drift closure (D1-D4) plus the full memory architecture design conversation that reframes Decisions 2 and 6.

### Doctrine-vs-code drift closures (committed to disk)

Four small design items from v20 §16 walked and closed against actual code, not project-knowledge. Drift-catch pattern from 2026-05-24 evening sweep applied — every patch verified against disk with `grep` / `sed` / Python read-modify-write before commit.

1. **D2 — `Health.sweep_interval_sec` stripped.** Field at `schema.py:349` defined but never read; `tier_health.py:104` hardcodes 15.0s as a class attribute (the pattern all five listeners use). Strip per v20 NEW-v20-6 and §0 rule 4 (no loose ends in code). Pydantic v2 default `extra="ignore"` handles silent drop of the stale `sweep_interval_sec: 30` entry in existing state.json on next load. Single-line deletion + commit.

2. **D3 — `haiku_4_5` quota row pruned; `anthropic_api_direct` annotated as vestigial.** Decision 4 v2 deprecated Haiku 4.5 (pricing parity with DeepSeek V4 Flash at lower capability, redundant). The row at `state.py:_build_initial_model()` was kept as forward-compat hook through v19; v20 NEW-v20-7 asks for prune-or-keep. Pruned haiku_4_5 entirely (re-open condition is a new provider filling the latency niche, which will have a different model name anyway). Kept `anthropic_api_direct` with three-line inline comment marking it as vestigial — emergency rung for NDA / money-on-line work per Decision 4 v2, not yet wired through LiteLLM. Fresh-build cold-start now produces exactly 5 quota rows.

3. **D1 — Orphan quota key prune + missing-key hydrate on `load_from_disk()`.** `quotas.quotas` is `Dict[str,CloudQuota]`; Pydantic's `extra="ignore"` does not prune dict-value keys. Added an explicit prune+hydrate pass to `state.py::load_from_disk()` immediately after `model_validate(data)`: orphan keys (anything outside the canonical set) are deleted with an INFO log; missing canonical keys are hydrated from `_build_initial_model()` defaults. Caught and cleaned three live orphans in production state.json: `deepseek_v3` (renamed in `b524bb0` 2026-05-24 but never cleaned from runtime), `haiku_4_5` (just-pruned from code in D3 above), and the missing `deepseek_v4_flash` row (never written after the rename — primary peer-rotation provider had no quota tracking until this patch). Hydration step closed a live gap, not just a cosmetic drift.

4. **D4 — `schema_version` confirmed label-only.** Audit A5 asked what migration logic should do when it eventually lands. Walked three options (A: registry with no-op transforms, B: cleanup-only no versioning, C: strip the field entirely). Settled on Option B trimmed — `schema_version` stays as a human-readable label, no migration transforms are part of the design for this stack. Cold-cycle discipline (the existing operator practice) is the migration strategy. Added a three-line comment above the field in `schema.py` making this explicit so no future agent builds migration logic against it.

5. **NEW-v20-2 (`sleeping_window_*`) — confirmed self-healing, no action needed.** Verified on disk that `OperatorPreferences` loads `overnight_window_start=23:00` / `overnight_window_end=07:00` correctly from schema defaults despite stale `sleeping_window_start: "22:30"` / `sleeping_window_end: "06:00"` keys still present in state.json. Pydantic's field-level `extra="ignore"` handles this without code change.

Commits landed: D2 (single commit), D3 (single commit), D1+D4 (single combined commit). Backup files (`*.D2-backup`, `*.D3-backup`, `*.D1D4-backup`) sit on disk for rollback; ignored by git via existing `*-backup` patterns.

### Method note — interpreter discovery quirk worth banking

Validation steps initially failed with `ModuleNotFoundError: No module named 'pydantic'` because the system `python3` differs from the Jarvis runtime interpreter. The daemon launches via `deploy.sh` which sources `/home/monarch/venv/inference/` before invoking `python3 daemon.py`. The same `~/venv/inference/` venv hosts the inference stack (LiteLLM, llama-cpp-python) AND Jarvis. Naming is a misnomer — it's the shared monarch-stack venv, not inference-only. Banked for the A3 doc cleanup mission: `~/projects/jarvis/CLAUDE.md` should name `~/venv/inference/bin/python3` as the canonical interpreter for any session running tests, repls, or one-off validation, with a one-line note explaining the naming history.

### D7 — Decision 2 (Hermes) artifact question resolved

Pre-session sweep ran `grep -rni hermes ~/projects/` and `find ~ -name "*hermes*" -o -name "*HERMES*"`. Results: only INFRASTRUCTURE_BIBLE_v19.md references (all circular — "the brainstorm exists, needs to be pasted"), one news-pipeline SQL comment about Nous Hermes model family, and unrelated vllm/npm hits. **No v18 Hermes brainstorm artifact exists on monarch.** Audit A7 closes as confirmed absent — the proposed shape in v20 §9.2 (Pattern B, Curator narrow-scope, memory writes disabled, routed via DeepSeek V4 Flash) is the entire prior thinking.

What followed was the deeper conversation: the operator's actual reference was Nous Research's Hermes Agent (github.com/NousResearch/hermes-agent), a 134k-star MIT-licensed open-source agent framework that ships v0.3.0 with persistent memory, autonomous skill creation, multi-platform messaging gateway, MCP integration, OpenAI-compatible API endpoint, cron scheduler, and an Atropos RL training pipeline. This is a substantially different artifact than the bespoke "Hermes layer" the v18 brainstorm appeared to imagine — and it's a production system already solving most of the problems Nexus and 2nd Brain were designed for. Decision 2 doesn't close on the v19 framing; it reframes against the real artifact.

### Memory architecture design — full conversation, no doctrine landed yet

Worked through the full memory landscape with the operator. Surveyed and compared:

- **Hermes Agent memory** — file-backed (MEMORY.md, USER.md, SOUL.md) + SQLite session search (FTS5) + autonomous skill creation + 8 optional external provider plugins (Honcho, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory, OpenViking). Fully local by default. Token-capped at ~650 tokens always-in-context.
- **EverMemOS** (EverMind-AI, arXiv 2601.02163) — engram-inspired lifecycle (MemCell → MemScene → User Profile). SOTA on LoCoMo (93%) and LongMemEval. Hybrid retrieval (Elasticsearch BM25 + Milvus vectors + RRF + LLM-guided multi-round). Foresight signals carry explicit validity intervals. Heavy infrastructure (~2-4 GB additional RAM for Elasticsearch + Milvus).
- **Obsidian vault** — markdown filesystem + kepano/obsidian-skills (Steph Ango / Obsidian CEO's own skill set, native Hermes integration). Maximum operator auditability, full git versioning, NDA-safe.
- **Codebase-Memory MCP** (arXiv 2603.27277) — Tree-Sitter AST knowledge graph, 66 languages, single statically-linked C binary + SQLite. 14 structural query tools via MCP. 83% answer quality vs file-exploration agents at 10x fewer tokens.
- **Redis** — hot operational state for financial pipeline (sub-10ms tick data, position state). No question on this — it goes in when L1 lands with the financial pipeline.

Also surveyed but not adopted: Subquadratic SubQ (closed weights, cloud-only, recent prior-art skepticism around subquadratic architectures); TSTorch (Kulshrestha + Chong, student project, not publicly released).

**Operator principle locked in this session:** *build it right the first time, not "good enough until it breaks."* In agentic work, the cost of memory failure shows up in the operator's pocket — trade decisions on stale L7 state, agent procedures diverging from vault notes, code knowledge going stale across L3/L5. This rules out the original "defer EverMemOS until the financial pipeline forces it" framing. EverMemOS lands in phase 1 build, not as a future upgrade.

### Four-layer architecture (designed, not yet doctrine)

The seven-technology list collapses to four conceptual layers under the elegance test:

| Layer | Role | Members |
|---|---|---|
| **Truth** | Authoritative state. Written by operators and pipelines. | Repositories (code), Postgres (data), Obsidian vault (knowledge), Redis (live operational state) |
| **Index** | Derived views over Truth. Written by re-indexers. | pgvector (semantic), Codebase-Memory MCP (AST graph), Hermes session search (FTS5) |
| **Memory** | Agent and world models built from Truth over time. Written by agents. | Hermes (working memory, skills, preferences) + EverMemOS (long-horizon temporal state, Foresight) |
| **Arbiter** | Routes questions to the right layer. Observes everything. Writes nothing. | Jarvis |

**Single conflict-resolution rule: Truth is primary, everything else is derived.** Operator preferences = vault is Truth; Hermes USER.md auto-syncs from vault. Stable procedures = Hermes skill is Truth. Code = repository is Truth; L3 and L5 are derived. Current operational state = Postgres/Redis is Truth; EverMemOS never claims to know current state, only historical evolution.

Jarvis's role under this model is cleaner than the v20 framing: route questions to the right layer based on what's being asked (not which tool was queried first), observe each layer's health, surface anomalies. Memory→Memory autonomous writes are inherently low-stakes and don't gate under authority spec. Memory→Truth writes are gated under existing Decision 5 N=12 framework.

The v20 truth hierarchy (disk > git > jarvis-q > github > doc > chat) governs **current-state checks**. The Truth layer governs **durable knowledge home**. Different questions, both correct, no competition. The Obsidian vault is the eventual home for what master_summary represents; v20 was the consolidation step that made the doctrine vault-ready.

### Cardinal Decision amendments required (pending next session)

The four-layer architecture supersedes two closed Cardinals. Both need explicit amendment commits, not silent rewrites:

- **Decision 2 reframe.** Pattern B (parallel to n8n, do not migrate cron workflows), Curator scoped narrowly or disabled (operator-explicit skill promotion, no automatic), memory writes initially gated through validation gate (Memory→Truth gating), routed via DeepSeek V4 Flash initially (cost discipline) — all constraints transfer. Only the artifact changes: Nous Research's Hermes Agent replaces the bespoke "Hermes layer" framing. Audit A7 closes simultaneously.

- **Decision 6 scope amendment.** Nexus (codebase memory) and 2nd Brain (knowledge layer) move from "design-only / deferred" to phase 1.5 build targets. This is the largest doctrine change of the session and is driven explicitly by the build-it-right operator principle, not by new evidence about the original scope decision. The v19 framing was correct under cost-driven assumptions; it is no longer correct under quality-driven assumptions.

### Phase 1.5 build sequence (locked, awaits Claude Code)

1. **Vault initialization first.** Initialize Obsidian vault. Doctrine migrates in immediately: master_summary_v20, AUTHORITY_SPEC_v19, DECISIONS_v19, REBALANCE_v19, BIBLE_AUDIT_findings, HANDOFF_v19. This is the operator's existing "2nd Brain in scattered form" gaining a coherent home. Hermes (later in sequence) lands into a rich existing context rather than starting empty.
2. **pgvector enable.** One `CREATE EXTENSION vector;` against existing Postgres. Zero new infrastructure. Unblocks semantic search over vault + code + news corpus.
3. **Codebase-Memory MCP deploy.** Single C binary + SQLite, MCP-native, immediately consumable by Claude Code and (later) Hermes. File watcher handles incremental re-indexing.
4. **Hermes Agent adoption.** Install per `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`. Configure with Curator disabled, memory writes gated, kepano/obsidian-skills installed pointing at the vault from step 1.
5. **EverMemOS deploy.** Self-hosted with Elasticsearch + Milvus alongside existing Postgres. Seeded from vault profile. Begins MemCell formation on subsequent agent conversations.
6. **Redis** — joins with financial pipeline build (phase 2 or later).

### Numeric updates pending against v20

- **§2 RAM budget.** Steady-state climbs from ~41 GB to ~44-46 GB (Elasticsearch ~1-2 GB + Milvus ~500 MB-2 GB; Redis ~200-500 MB joins later). "~55 GB free at idle" claim drifts to ~50 GB free at idle. Comfortable headroom maintained inside 96 GB.
- **§11.5 headroom disposition.** D5 still answerable in next session; affects T6 burst-vs-T1-restore-vs-T4-up-vs-Whisper-preload-vs-second-T6 allocation of ~7.5-8.5 GB freed slack.
- **§16 audit closures.** D1, D2, D3, D4 close. NEW-v20-1, NEW-v20-2, NEW-v20-6, NEW-v20-7, A5, A7 all close with this session.

### New doctrine document pending

**`MEMORY_ARCHITECTURE_v20.md`** — single standalone doc paralleling AUTHORITY_SPEC's role. Contents: four-layer model with definitions, Truth-is-primary as single conflict-resolution rule, routing table (operator question → which layer), primary-author table per content type, Memory→Memory autonomous / Memory→Truth gated distinction, vault-as-identity-Truth, operator-explicit skill promotion (no N-uses counter), Jarvis observation surface per layer, build sequence.

### Carried open items into next session

- **D5** — §11.5 headroom disposition (answerable now, ~10-15 min conversation)
- **D6** — Decision 3 (T6 defaults) still blocked on 21 GB model download + R2 measurement + `~/bin/t6-up`/`~/bin/t6-down` tooling
- **R2 measurement** — T1 ctx 36K → 24K patched in `c0f7ea7` 2026-05-20; awaits next natural T1 restart for VRAM delta confirmation. Path B means T1 survives all dataplane cycles by design — fires on reboot or explicit control-session kill.
- **Cardinal Decision amendment commits** — D2 reframe + D6 scope expansion, landed atomically with `MEMORY_ARCHITECTURE_v20.md`
- **`MEMORY_ARCHITECTURE_v20.md`** — first writing task next session
- **Audit closures** in §16 — apply once doctrine doc lands
- **Phase 1.5 build** in Claude Code, in the locked order above

### Next-session orientation

Open with D5 headroom disposition (fast). Then write `MEMORY_ARCHITECTURE_v20.md` as a single doctrine doc. Land the D2 + D6 amendments to v20 atomically with it. Update §2 RAM budget and §16 audit closures. Then move to Claude Code for Phase 1.5 build execution starting with vault initialization. Total remaining design work: ~1-2 hours of focused doctrine-writing, no more substantive decisions.

The doctrine layer remains the single source of truth across files. The four-layer memory architecture is the natural completion of patterns v20 already established — not a graft. The Arbiter role was always Jarvis; the new doctrine just names the addressees.

---

## Session 2026-05-26 (evening) — D5 + D3 close; Phase 18 voice doctrine

### What happened

Picked up from the 2026-05-26 memory architecture session with D5 headroom
disposition as the only substantive doctrine decision still open per HANDOFF.
Worked through D5, caught a Hard Constraint conflict in D3's prior framing,
and closed both cardinals atomically. All six cardinals now carry a closed
status — though D2 and D6 each carry an amendment flag against the Phase 1.5
build (see cardinal status table below).

**Operator framings locked this session:**

- T6 targets 50-60% expert offload at ~100 tok/s. T6 is a reserve coder —
  primary coding routes to Claude Pro ×2 and Kimi K2.6; T6 is the local
  backup for can't-wait, NDA-tagged, or low-level missions where remote
  routing is unsuitable. Not optimized for throughput; optimized for
  availability.
- T1 context is uncapped. Allocated dynamically up to available VRAM.
  Cascade manages pressure by evicting burst tiers (T2 typically idle,
  T6 burst-only) before T1 is touched. Change 2's 24K patch lands as the
  post-restart starting point; runtime context is not statically capped.
  Hard Constraint #1 governs: T1 self-offloads to RAM/CPU only via
  Substrate Pressure Cascade (§10.3), never evicted by anything below as
  a first resort.
- Phase 18 `whisper` tmux session on monarch clarified: this is the Phase 18
  voice-to-voice STT component (preparatory), not Phase 17.5 dictation
  (MacBook-resident). Distinct subsystems sharing only the physical
  microphone.
- Phase 18 value proposition sharpened: conversational access to Jarvis's
  full codebase understanding (L5 Codebase-Memory MCP), doctrine (L6 vault),
  live system state (Phase 2 listeners), git history, and agent procedures
  (L4 Hermes skills) — operator doesn't need to be in the weeds of files.
  Maps to §3.2 architectural test question four ("Can Jarvis explain it?")
  and §3.1 documentation router role.

**D5 CLOSED.** §11.5, §5.6, §4.1, §14.3 patched atomically. Four anchors,
four patches, all landed cleanly. Phase 18 architecture block added with
STT/TTS halves, ChatterBox (Resemble AI, Apache 2.0) named as TTS candidate
(doctrinal placeholder, not hard commitment). Combined Phase 18 VRAM footprint
~1.5-3 GB burst-shaped; comfortable inside standard headroom.

**D3 CLOSED (commit 1ac1dad).** §9.3 rewritten from BLOCKED to CLOSED.
Original proposed statement (25% offload, three named modes —
comfort/conservative/aggressive) superseded by D5. The three-mode framing
depended on "parks T1" language which conflicted with Hard Constraint #1 —
caught at doctrine-vs-doctrine cross-reference walk, not at execution.
Execution items (model download, spin-up tooling, first-deploy VRAM
verification) moved to §16.6 E3; D3 doctrine is clean. §16.2 D3 row
checkmarked; §16.6 E3 row updated to drop D3 prereq.

**M19 banked.** Method note added to §16.7: when closing a cardinal that
affects tier allocation, walk Hard Constraints + Substrate Pressure Cascade
as a cross-reference check before drafting the closure statement. Doctrine
layer caught the D3 conflict; execution layer would have caught it later and
more expensively. `.gitignore` updated with `*.D3-close-backup` pattern.

### Session commit trail

Run `git log --oneline | head -6` to verify hashes. Three commits landed:
1. `master_summary_v20: close D5 + Phase 18 voice doctrine`
2. `master_summary_v20: close D3 (T6 defaults superseded by D5)` — `1ac1dad`
3. `doctrine: bank M19 method note (D3 closure lesson); .gitignore D3-close-backup`

### State of the six cardinals post-session

| # | Decision | Status |
|---|----------|--------|
| 1 | Architectural reframe | CLOSED 2026-05-19 |
| 2 | Hermes adoption shape | CLOSED 2026-05-26 — **amendment expected at P1.5-4 Hermes install** |
| 3 | T6 operational defaults | CLOSED 2026-05-26 |
| 4 | Cloud routing chain | CLOSED 2026-05-19; amended 2026-05-24 |
| 5 | Jarvis authority model | CLOSED 2026-05-24 |
| 6 | v19 scope | CLOSED 2026-05-19; amended 2026-05-26 — **second amendment expected at P1.5-1 vault init** |

All six cardinals carry a closed status for the first time in the v19/v20
lifecycle. D2 and D6 are flagged for amendment commits as Phase 1.5 build
surfaces doctrine gaps — this is expected and not a reopen in the cardinal
sense; it is the same pattern as Decision 4's two amendment commits.

**D2 amendment surface (P1.5-4 Hermes install):** MEMORY_ARCHITECTURE_v20.md
§15 items that require doctrinal choice rather than implementation choice:
USER.md auto-sync mechanism specifics (standalone watcher vs Codebase-Memory
file watcher piggyback vs Hermes cron skill), skill promotion ritual mechanics
(script vs operator-direct), Telegram/Signal gateway enablement decisions.
Any of these that resolve as doctrine land atomically with the install commit.

**D6 amendment surface (P1.5-1 vault init):** MEMORY_ARCHITECTURE_v20.md §15
items 1 (vault structure: single vs per-project, NDA isolation pattern) and 7
(multi-device sync: vault on monarch only vs MacBook sync). Both are
doctrine-grade calls that must land in v20 + MEMORY_ARCHITECTURE_v20.md
atomically with the vault initialization commit per §0.1 rule 4.

### Open items carried forward

- **R2 measurement** — T1 ctx 24K patch in code since `c0f7ea7`; VRAM delta
  pending next natural T1 restart. Path B means T1 survives dataplane cycles;
  fires on reboot or explicit control-session kill.
- **Doc cleanups** — C1 (CLAUDE.md rewrite per A3 + NEW-v20-4 + venv naming
  lesson from 2026-05-26 method note), C2 (README v20-aware), C3
  (ref-blueprint §Phase 15), C4 (six per-stack CONTEXT.md updates), C5
  (single-line fixes per A12/A13/NEW-v20-5). All low-effort; C1 highest
  priority since the venv misnomer catches Claude Code cold every session.
- **Phase 1.5 build** — vault init → pgvector → Codebase-Memory MCP →
  Hermes Agent → EverMemOS → Redis. All pending Claude Code execution.
  Locked order per MEMORY_ARCHITECTURE_v20.md §12.
- **Phase 2 listeners** — process.py (no prereqs, buildable today), quota.py
  (doctrine-unblocked since 2026-05-24), cron.py, memory.py (spec in
  MEMORY_ARCHITECTURE_v20.md §10.2).
- **E3** — T6 spin-up tooling + first-deploy VRAM verification. After model
  download (~21 GB). No doctrine blockers remaining.

### Recommended next-session opening

**If memory architecture build is the priority:** Open with the
MEMORY_ARCHITECTURE_v20.md §15 doctrine gap walk (~15-20 min) covering items
1 (vault structure), 3 (pgvector scope), 4 (skill promotion ritual), 7
(multi-device vault sync). These are fast decisions that must land in doctrine
before P1.5-1 vault init disk writes begin per §0.1 rule 4. Then move to
Claude Code for P1.5-1 execution. D6 amendment commit lands atomically with
vault init.

**If Phase 2 listener completeness is the priority:** process.py directly in
Claude Code. No prereqs, no doctrine gaps, ~2-3 hr mission. BaseListener
pattern established; reuses vram.py PID-resolution utilities; spec is
complete in master_summary_v20.md §12.4.

C1 (CLAUDE.md rewrite) is a 30-min standalone that pays for itself on the
first Claude Code session it prevents from hitting the venv-misnomer error.
Worth doing as a warm-up before either main thread.

### Backup files on disk (not in repo)

- `master_summary_v20.md.D5-backup`
- `master_summary_v20.md.D3-close-backup`
- `master_summary_v20.md.M19-backup`
- `HANDOFF_v19.md.session-20260526-evening-backup`

Safe to remove after next successful cold cycle confirms no regression.


---

Built across one long session: Step 1 hygiene → Jarvis v0.1 deploy → v0.1 deadlock discovered via telemetry → v0.2 rewrite with snapshot/queue → soak verified → 80% target view added → 5.5 GB phi-4 cache reclaimed.

The single most consequential finding: the hardware feels useless because v18 sized standard mode for the loading screen, not for use. Jarvis made this visible. v19 doctrine is mostly about giving each tier a job that matches the actual workload distribution.

---

## Session 2026-05-27 — §15 doctrine gap walk + doctrine bundle land

### What happened

Picked up the HANDOFF recommendation from the 2026-05-26 evening session: §15 doctrine gap walk on Items 1, 3, 4, 7 (all flagged as gating Phase 1.5 step 1 vault init and step 2 pgvector enable), followed by Thread C (C1 CLAUDE.md rewrite). Thread A (§15 walk + doctrine commits) completed in full. Thread C deferred to next session — doctrine bundle consumed the session.

### Doctrine bundle — five commits landed

| Commit | Hash | Scope |
|---|---|---|
| M1 | `34289bb` | `MEMORY_ARCHITECTURE_v20.md` §2: build-it-right scope clarification + vault hygiene principle |
| M2 | `f7f1030` | `MEMORY_ARCHITECTURE_v20.md` §7.3: pgvector install scope + expansion ritual; §7.6: vault structure rewrite |
| M3 | `90a07d9` | `MEMORY_ARCHITECTURE_v20.md` draft-state pattern + downstream consistency (§6, §8.4, §10.3, §11.4, §12.4) |
| M4 | `0467639` | `MEMORY_ARCHITECTURE_v20.md` §15 closures (Items 1, 3, 4, 7) + §12 downstream propagation (§12.1, §12.2) |
| S1 | `ec69ef3` | `master_summary_v20.md` D2 + D6 second amendment: vault structure doctrine resolved across §9.2, §9.6, §13.1, §13.5, §13.6 |

Net: 19 anchors across 2 files, ~125 insertions, ~25 deletions. `MEMORY_ARCHITECTURE_v20.md` §15 open items: 4 closed, 6 remain open (Items 2, 5, 6, 8, 9, 10).

### Doctrinal decisions made this session

**Build-it-right scope clarification (MEMORY_ARCHITECTURE_v20.md §2, M1).**
Build-it-right (locked 2026-05-26) applies to memory architecture correctness — the four-layer model, conflict-resolution rule, primary-author assignments, Truth-is-primary discipline. It does not extend to speculative content-scope features whose absence can be added as additive layers rather than rebuilds. NDA isolation is the canonical example. Deferring it is YAGNI discipline, not a build-it-right violation. This boundary was derived from operator push-back when the initial session framing treated Option D ("defer NDA, ship monolithic now") as conflicting with build-it-right.

**Vault hygiene principle (MEMORY_ARCHITECTURE_v20.md §2, M1).**
The vault's value derives from being a high-quality documentation graph, not from comprehensive capture. Garbage-in-garbage-out applies through the embedding layer: low-quality vault content gets embedded by L3, surfaced by L4 retrieval, and treated as Truth by downstream agents. Four PARA-style additions evaluated and rejected at install (inbox, templates, journal, people). Recorded in §2 so the rejection is not relitigated.

**Vault structure (MEMORY_ARCHITECTURE_v20.md §7.6, M2 + M4 — §15 Item 1 CLOSED).**
Decided in the prior session (2026-05-26 §15 walk), committed to doctrine this session. Single monolithic `~/vault/` on monarch's NVMe. Doctrine-first hierarchy: `final_master_summary.md`, `final_memory_architecture.md`, `final_handoff.md` at root; `archive/` for superseded versions; `projects/` for per-subsystem docs populated organically. `final_` prefix on canonical-root docs signals in-place updates via git, no version-suffix bumps. No PARA additions at install. NDA isolation deferred as future amendment (subfolder + indexer-exclusion mechanic recorded for amendment, not built at install).

**Truth-singularity for multi-device (MEMORY_ARCHITECTURE_v20.md §7.6, M2 + M4 — §15 Item 7 CLOSED).**
Decided in the prior session, committed this session. Monarch is the sole vault Truth location. No replication; no MacBook-resident vault copy. MacBook accesses remotely via SSH and/or Tailscale. Divergence vectors are zero by construction. Whether MacBook editing uses SSH-terminal only or Tailscale-mounted SSHFS for native Obsidian UI is implementation-grade, decided at P1.5-1 build time.

**pgvector install scope + expansion ritual (MEMORY_ARCHITECTURE_v20.md §7.3, M2 + M4 — §15 Item 3 CLOSED).**
Vault notes only at P1.5-2 install. Code chunks and news corpus not embedded at install. Each future corpus admission requires a four-step expansion ritual: justification (documented §16 open item), quality gate (filtering rules specified before embedding), atomic landing (doctrine amendment patch lands in same commit as indexer config), post-deploy validation (retrieval quality spot-checked; rollback if existing retrieval degrades). This is the vault hygiene principle applied to the index layer.

**Skill promotion mechanism — draft-state pattern (MEMORY_ARCHITECTURE_v20.md §8.4, M3 + M4 — §15 Item 4 CLOSED).**
Hermes's autonomous skill-creation hook is routed to a draft state (`~/.hermes/skill-drafts/<name>/SKILL.md`) rather than disabled. Curator-the-grader (autonomous consolidation, deprecation, quality alerts) remains disabled. Two promotion paths coexist: Hermes drafts → operator approves via `approve-draft`; operator directly promotes vault procedures via `promote-skill`. Both implemented as Hermes skill + bin script hybrid (bin script handles bootstrap and pre-Hermes fallback). Draft TTL: no auto-expiration; stale drafts (>30 days) surface as Tier 2 events via future `memory.py` listener. `jarvis-q skill-drafts` CLI subcommand surfaces pending drafts. Authority tiers: Hermes drafting is Tier 2 autonomous-with-log; `approve-draft` and `promote-skill` are Tier 3 operator-explicit; Curator-the-grader stays disabled until 30 days stable + 12 promoted skills + operator opt-in.

This is the Reading 2 framing from the §15 Item 4 walk: "Hermes drafts autonomously, operator approves." It distinguishes Curator-the-grader (stays off) from the skill-creation hook (routed to drafts, operator-gated at promotion to Truth). Decision 2's "Curator disabled" language is now precise: Curator-the-grader disabled; skill-creation hook is draft-state-routed.

**D6 second amendment surface (master_summary_v20.md §9.6, S1).**
§15 Items 1, 3, 4, 7 closures added as "Second amendment 2026-05-26 — Vault structure doctrine resolved" block in §9.6. Declares Phase 1.5 step 1 (vault init) doctrine-unblocked.

### Method notes banked (M20-series)

**M20 — cat-heredoc terminal-garbling over Tailscale SSH.**
Multi-anchor patch scripts piped via `cat > /tmp/XX-patch.py << 'SCRIPT_END'` produce garbled terminal echo at the heredoc terminator line when run over Tailscale SSH. The garbling is display-only — the file on disk is typically intact. Visual confirmation of the paste is unreliable. The correct verification pattern: `wc -l` (line count), `md5sum` (hash), `head -3` + `tail -3` (structural integrity), content-phrase `grep -c` (anchor presence), and `sed -n '<range>p'` spot-check on the relevant section. All five checks before `python3 /tmp/XX-patch.py`. Do not proceed on visual confidence alone.

**M21 — grep-vs-unicode-escape mismatch in script verification.**
When a patch script stores §, —, ✅ as `\u00a7`, `\u2014`, `\u2705` escape sequences (defensive practice for heredoc transit), grep targets for content-phrase verification must match the escape sequence literally, not the rendered glyph. `grep -c '§15'` returns 0 on a script that contains `\u00a715`. Better approach: `sed -n '<range>p'` directly on the relevant line range, or `grep -c 'u00a715'` without the backslash-u prefix depending on shell quoting. Discovered at S1 verification step when `grep -c 'CLOSED 2026-05-26 from §15 Item 4 walk'` returned 0 despite the content being present in the script as `\u00a715 Item 4 walk`.

**M22 — §13.4 ghost anchor / doc-structure confidence.**
A multi-hour doctrine session in the prior context confidently referenced "§13.4 authority table" in both a prose spec and a 20-anchor patch inventory. That section does not exist in `MEMORY_ARCHITECTURE_v20.md` — §13 is a 12-row cross-reference TOC with no subsections. The patch-script assert (`content.count(old) == 1`, count=0) caught the error before any disk write. The lesson: even a competent doctrine session will confidently reference doc structure that doesn't exist. Patch-script uniqueness asserts are the load-bearing safety net. The operator's review of the prose inventory is not sufficient. Verify anchor existence via `grep -nF` before writing a patch that targets it.

### State of §15 open items post-session

| Item | Status |
|---|---|
| 1 — Vault structure | ✅ CLOSED — see §7.6 |
| 2 — pgvector embedding model | Open — gated on T5 throughput measurement at P1.5-2 |
| 3 — pgvector install scope | ✅ CLOSED — vault only + expansion ritual, see §7.3 |
| 4 — Skill promotion ritual | ✅ CLOSED — draft-state pattern, see §8.4 |
| 5 — External provider re-enablement | Open — per-provider decision when first need surfaces |
| 6 — EverMemOS Foresight + trading pipeline | Open — when financial pipeline build starts |
| 7 — Multi-device vault sync | ✅ CLOSED — monarch sole Truth, SSH/Tailscale access, see §7.6 |
| 8 — Cross-layer event coordination | Open — deferred to first concrete need |
| 9 — Memory listener architecture | Open — at memory.py build time |
| 10 — Authority promotion granularity | Open — at first promotion attempt |

### Open items carried forward

- **C1 — CLAUDE.md rewrite.** Highest priority doc cleanup. Covers A3 + NEW-v20-4 + venv-naming lesson (M19 from 2026-05-26 session): `~/venv/inference/bin/python3` is the canonical interpreter for any session running tests or validation; the "inference" name is a misnomer for the shared monarch-stack venv. Catches Claude Code cold on first invocation every session. ~30 min standalone. Do this before any Phase 1.5 Claude Code work.
- **Phase 1.5 build — now doctrine-unblocked for steps 1 and 2.** Vault init (P1.5-1): `~/vault/` per §7.6 spec, `git init`, migrate doctrine docs, create `operator.md`, `README.md`. pgvector enable (P1.5-2): `CREATE EXTENSION vector;`, vault-notes-only initial embeddings. Both steps are ready for Claude Code with no further doctrine gaps.
- **Phase 1.5 build — steps 3-5.** Codebase-Memory MCP deploy (P1.5-3), Hermes Agent adoption (P1.5-4, with draft-state pattern per §8.4 as part of deploy config), EverMemOS deploy (P1.5-5). All locked in sequence per MEMORY_ARCHITECTURE_v20.md §12.
- **C2, C3, C4, C5** — remaining doc cleanups per prior session carry-forward. Lower priority than C1 and Phase 1.5 build.
- **Phase 2 listeners** — process.py (no prereqs), quota.py, cron.py, memory.py. Unchanged from prior session carry-forward.
- **R2 measurement** — T1 ctx 24K delta pending next natural T1 restart.
- **E3** — T6 spin-up tooling + first-deploy VRAM verification. After model download.
- **Backup hygiene** — `MEMORY_ARCHITECTURE_v20.md.{M1,M2,M3,M4}-backup` and `master_summary_v20.md.S1-backup` safe to remove after next successful cold cycle.

### Recommended next-session opening

**Run first:** `git log --oneline | head -7` to confirm five commits visible (ec69ef3 through 34289bb). `git status` to confirm clean working tree.

**Then C1 (CLAUDE.md rewrite, ~30 min):** Read the existing `~/projects/jarvis/CLAUDE.md`, rewrite per A3 + NEW-v20-4 + M19 venv-naming lesson. The `~/venv/inference/bin/python3` note must be prominent — it is the single most common Claude Code cold-start failure on this stack.

**Then Phase 1.5 step 1 in Claude Code:** `~/vault/` init per MEMORY_ARCHITECTURE_v20.md §7.6. Claude Code reads this HANDOFF + MEMORY_ARCHITECTURE_v20.md §7.6 + §12.1 as session context. No doctrine gaps remain for this step.

### Backup files on disk (not in repo)

- `MEMORY_ARCHITECTURE_v20.md.M1-backup`
- `MEMORY_ARCHITECTURE_v20.md.M2-backup`
- `MEMORY_ARCHITECTURE_v20.md.M3-backup`
- `MEMORY_ARCHITECTURE_v20.md.M4-backup`
- `master_summary_v20.md.S1-backup`

Safe to remove after next successful cold cycle confirms no regression.
---

## Session 2026-05-27 (continued) — C1 close + P1.5-1 design walk + hygiene closures

### What happened

Picked up from morning session's recommendation: C1 (CLAUDE.md rewrite) first, then Phase 1.5 step 1 (vault init) in Claude Code. C1 closed cleanly. Before handing off to Claude Code, operator surfaced the P1.5-1 design gaps that had been deferred at MEMORY_ARCHITECTURE §15 — running the design walk this session means Claude Code can execute against locked doctrine rather than locking doctrine during the build.

Three commits this session. Doctrine + hygiene + the C1 close from earlier in the day.

### Commits landed

| Commit | Hash | Scope |
|---|---|---|
| C1 | `13173f2` | `CLAUDE.md` full rewrite (A3) + `schema.py:355` docstring 30s -> 10s (NEW-v20-4) |
| P1.5-1 doctrine | `ca76498` | `MEMORY_ARCHITECTURE_v20.md` §7.6 vault structure amendments + §12 exit criteria + §15 items 11-13 |
| C5 hygiene | `8aa88c4` | A12, A13/A13b, NEW-v20-5 + §16 row flips across 4 files |

Net: 3 files patched in C1 (CLAUDE.md, schema.py + side-edit via Python), 1 file patched in ca76498 (MEMORY_ARCHITECTURE), 4 files patched in 8aa88c4 (schema.py, HANDOFF, master_summary, ~/bin/inference-up).

### C1 closure detail (commit 13173f2)

CLAUDE.md fully rewritten as lean-pointer entry point per master_summary_v20.md §0.2. Five drift sources resolved: v0.1 -> v0.2, 30s -> 10s persist, inference -> control session, T1 36K -> 24K, inference-burst-up/down -> t2-up/t2-down. M19 venv-naming lesson promoted to top of file: `~/venv/inference/bin/python3` is the canonical interpreter for the shared monarch-stack venv (name is a misnomer — hosts both inference tiers AND Jarvis). schema.py:355 SystemModel docstring also corrected (30s -> 10s) in the same bundle.

Pointers table replaces former duplication of hardware envelope, tier configuration, and listener spec — those live canonically in master_summary §2/§11/§12.4 with cross-references back from CLAUDE.md.

### P1.5-1 design walk — sub-decisions 1-10 locked

The mission brief for vault initialization had ten sub-decisions that needed resolution before Claude Code could execute. All ten closed this session.

**Sub-decision 1 — Migration mode: MOVE.** Doctrine docs move from `~/projects/jarvis/` to `~/vault/`. Not copy (truth-singularity violation), not symlink (anti-pattern, breaks portability). Jarvis repo loses the working files; pre-migration git history preserved in jarvis repo, post-migration history tracked in vault repo. Locked in MEMORY_ARCHITECTURE §7.6 "Migration pattern at P1.5-1" paragraph.

**Sub-decision 2 — Self-referential path updates.** Three commits at P1.5-1 in this order: (1) vault initial commit with §0.2 already pointing at vault paths (file's first canonical version is self-consistent), (2) jarvis CLAUDE.md Pointers table updates to vault paths, (3) jarvis deletes the migrated files.

**Sub-decision 3 — HANDOFF workflow post-vault.** Session-end commits go to vault repo going forward. The monolithic-codebase principle exposed a doctrine gap: code repos and doc vaults are indexed by different memory technologies (Codebase-Memory AST graph vs pgvector + Obsidian backlinks) and have fundamentally different write disciplines. Two-git-repo distinction is correct by design, not convention. Banked as new doctrine paragraph in §7.6.

**Sub-decision 4 — BIBLE_AUDIT sunsets at P1.5-1.** §16.1 in master_summary has absorbed the drift-tracking function. BIBLE_AUDIT migrates to `~/vault/archive/` at P1.5-1, not deferred. Confirmed completed projects use master_summary + HANDOFF; workflow builds use per-stack CONTEXT.md as drift tracker; no standalone audit doc needed going forward.

**Sub-decision 5 — operator.md initial content.** Claude Code drafts from master_summary §1 + §2 + §9 + HANDOFF operator-profile sections; operator reviews before the init commit fires. Tier 3 authority gating applies to all subsequent agent-proposed edits; initialization is a one-time seeded draft outside that authority surface.

**Sub-decision 6 — kepano/obsidian-skills target: `~/vault/skills/`.** Plain files, no submodule. Skills versioned alongside doctrine. Hermes config wiring (vault path as search path vs copy/symlink into `~/.hermes/skills/`) decided at P1.5-4 build time per §12.4.

**Sub-decision 7 — Remote policy: private GitHub at init.** Closes master_summary §16.8 gap #8 (no documented vault backup beyond Postgres cron). Initial vault content is non-NDA doctrine; pre-excluded private subfolders carry future NDA amendment. Operator creates empty repo before Claude Code runs P1.5-1.

**Sub-decision 8 — `projects/` empty at init.** Populated organically as each stack activates. Operator framing: "one stack at a time, news-pipeline farthest along." No placeholder subdirs.

**Sub-decision 9 — .gitignore: targeted private-repo protections.** OS artifacts, Obsidian workspace cache, credential safety net (`*.env`, `*.key`, `*secret*`, etc.), pre-reserved private subdirs (`private/`, `nda/`, `sensitive/`, `trading-edge/`).

**Sub-decision 10 — All seven archive files exist on disk.** Verified by `ls ~/projects/jarvis/`. BIBLE_AUDIT_findings.md also present and migrates to archive per sub-decision 4. README.md stays in jarvis repo for future C2 rewrite — not a vault target.

### Path A scope expansion — §15 items 11-13 surfaced

The session also surfaced three doctrine gaps that don't block P1.5-1 but block downstream Phase 1.5 steps. Documented as new §15 open items so they don't get forgotten:

- **Item 11** (vault file-watcher implementation) — resolution at P1.5-4 after Hermes capability surface is known. Default until decided: USER.md auto-sync on Hermes session-start refresh (not real-time mtime detection).
- **Item 12** (Hermes SQLite -> EverMemOS ingestion cadence) — resolution at P1.5-5. Default at deploy: batch-on-session-end with operator-acknowledgeable digest.
- **Item 13** (L7 EverMemOS profile-drift digest cadence) — resolution at P1.5-5 with initial cadence = daily digest; tighten to real-time alert on profile fields affecting financial pipeline once E1 goes live.

This is the build-it-right principle applied to its honest scope: memory architecture correctness is locked; downstream implementation choices are surfaced as open items rather than silently deferred.

### C5 hygiene closure (commit 8aa88c4)

Bundled four cosmetic fixes after design walk completed:

- A12 — schema.py docstring "Eight" -> "Nine" + missing `operator` row added (matched SystemModel:354-371).
- A13 — HANDOFF_v19.md:114 `inference` -> `control` session.
- A13b — caught same-class drift at HANDOFF_v19.md:116 during A12 verification (`8 domains` -> `9 domains`). Expanded A13 row to record.
- NEW-v20-5 — ~/bin/inference-up:282 T4 launch comment `4K ctx` -> `16K ctx` (matching actual `--ctx-size 16384` on :287). Also corrected the source-of-truth column in §16.1 — audit row said `.sh` extension; actual file has no extension.

§16 row flips: A3 + NEW-v20-4 -> RESOLVED 2026-05-27 (13173f2). A12 + A13 + NEW-v20-5 -> RESOLVED 2026-05-27 (8aa88c4). §16.5 C1 + C5 strikethrough.

Remaining §16.1 OPEN items: NEW-v20-3 only (self-heals on next T1 restart per §11.2, intentionally left open).

§16.5 doc cleanup queue now: C2 (README rewrite), C3 (ref-blueprint), C4 (per-stack CONTEXT.md updates). None gate Phase 1.5 step 1.

### Doctrine signal banked — build-it-right scope clarification

Operator push-back during sub-decision 1 ("D conflicts with build-it-right") exposed that the original build-it-right framing (locked 2026-05-26) didn't have a scope boundary. Read literally, it could be invoked to block any deferral on any feature. The clarification landed in MEMORY_ARCHITECTURE §2:

> **Scope of the build-it-right principle.** Applies to memory architecture correctness — the four-layer model, conflict-resolution rule, primary-author assignments, Truth-is-primary discipline. Does not extend to speculative content-scope features whose absence can be added as additive layers rather than rebuilds. NDA isolation is the canonical example: its absence at install does not compound silently into agentic memory failure, so deferring it is a YAGNI call rather than a build-it-right violation.

This is the exact pattern the project instructions encode: operator push-back becomes doctrine refinement. Build-it-right and YAGNI now sit next to each other with a clean boundary.

### Method notes banked

**M23 — Bundle != atomic.** Packing heredoc write + verification + commit into one paste means M20 garbling at the heredoc terminator eats every downstream phase. Split file-write from verification from commit into separate pastes. The verification paste should be the first thing run after a heredoc paste — if it runs, the heredoc closed correctly; if it doesn't run, M20 fired. This session split each commit into: (1) write script, (2) md5/structural verify, (3) backup + run + diff review, (4) commit. Four pastes per commit minimum.

**M24 — base64 transit for markdown content.** Heredoc paste of markdown over Tailscale corrupts unpredictably (M20 from prior sessions). For full-file or large-paragraph writes containing em-dashes, tree-drawing characters, §-glyphs, backticks, or arrows, encode the file content to base64 in the workspace, then decode on monarch. Alphabet is `A-Za-z0-9+/=` only — no terminal-escape-sensitive characters. md5 round-trip from workspace to monarch provides structural assertion that transit was clean. Used in this session for the P1.5-1 mission brief draft. Project instructions prescribe heredoc/sed/Python read-modify-write as defaults; base64 transit is the right escalation when markdown content over Tailscale is the failure surface.

**M25 — Audit rows can carry their own drift.** NEW-v20-5 row in §16.1 said `inference-up.sh:282` — file path with `.sh` extension and audit-line `:288`. Both wrong. Actual file is `~/bin/inference-up` (no extension), and line 287 is the `--ctx-size 16384` launch (not 288). The C5 patch corrected both the underlying file (4K -> 16K comment) AND the audit row's source-of-truth column. Lesson: when closing an audit row, verify the row's stated anchors as well as the underlying fix. Audit rows are doctrine too; they can drift from disk just like any other claim.

### Three pre-existing method notes still relevant

From prior sessions, still load-bearing this session:

- **M19** (2026-05-26): `~/venv/inference/bin/python3` is canonical interpreter despite misleading name. Used throughout this session for patch script execution.
- **M20** (2026-05-26): cat-heredoc + Tailscale + markdown content = terminal display garbling at heredoc terminator. Display unreliable; file content typically intact. md5/structural verify is the source of truth.
- **M22** (2026-05-26): §13.4 ghost — confident references to doc structure that doesn't exist. Patch-script asserts catch these; operator review of prose inventory doesn't.

### Carried open items into next session

- **Phase 1.5 step 1** — vault init in Claude Code. Doctrine-unblocked. Mission brief drafted this session covers all 10 sub-decisions, the operator.md sourcing spec, and the post-mission verification checklist. Next-session Claude Code reads MEMORY_ARCHITECTURE §7.6 + §12.1 + the mission brief and executes.
- **Phase 1.5 steps 2-5** — pgvector, Codebase-Memory MCP, Hermes Agent, EverMemOS. Sequential per §12. Items 11-13 surface as resolution-at-step doctrine decisions during 4 and 5.
- **§16.5 C2-C4** — README rewrite, ref-blueprint news-pipeline §Phase 15, per-stack CONTEXT.md updates. Operator framing: "one stack at a time, news-pipeline farthest along" — C3 (news-pipeline ref-blueprint) gets priority when news-pipeline workstream resumes; C4 batches as each stack activates rather than all at once.
- **§16.1 NEW-v20-3** — only remaining open audit row. Self-heals on next T1 restart.
- **R2 measurement** — T1 ctx 24K VRAM delta pending next natural T1 restart.
- **E3** — T6 spin-up tooling + first-deploy VRAM verification after model download.
- **Backup files on disk** — `CLAUDE.md.C1-backup`, `jarvis/schema.py.C1-backup`, `jarvis/schema.py.C5-backup`, `HANDOFF_v19.md.C5-backup`, `master_summary_v20.md.C5-backup`, `~/bin/inference-up.C5-backup`, `MEMORY_ARCHITECTURE_v20.md.C2-backup`. Safe to remove after next successful cold cycle confirms no regression.

### Recommended next-session opening

**Run first:** `git log --oneline | head -7` to confirm session commits (8aa88c4 -> ca76498 -> 13173f2 -> 3b0580c) and that working tree is clean.

**Then P1.5-1 in Claude Code.** Hand Claude Code the mission brief from this session plus MEMORY_ARCHITECTURE §7.6 + §12.1 as canonical doctrine for the build. Operator pre-creates the empty private GitHub repo before Claude Code starts. Claude Code drafts operator.md from the sources specified in sub-decision 5; operator reviews before the init commit fires. Post-mission verification checklist (in the mission brief) confirms all exit criteria before declaring P1.5-1 complete.

After P1.5-1 commits land: the doctrine docs on disk migrate to vault root. From that point forward, session-end HANDOFF commits go to `~/vault/final_handoff.md` in the vault repo. The transition itself is part of P1.5-1's deliverable per sub-decision 2.
