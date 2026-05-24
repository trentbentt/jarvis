# Workstation Infrastructure Setup — Master Summary v19 (INTERIM)

**Last Updated:** May 22, 2026 (post-Decision-5-Item-5)
**Status header:** **INTERIM REVISION.** This document supersedes v18 as the reg-blueprint of record but is itself transitional — final v19 ratification waits on Decisions 2, 3, 5 closing and Rebalance Changes 2-3 landing per `INFRASTRUCTURE_BIBLE_v19.md` §22.4. Sections marked **[v19 update]** capture the substantive changes since v18; all other content is preserved from v18 because it remains factually correct.
**Document role:** This is the `reg-blueprint.md` of the documentation set (CLAUDE.md → CONSTITUTION.md → CONTEXT.md → reg-blueprint). It is the deep reference. CLAUDE.md is the lean entry point; CONTEXT.md is living state; claude-mem captures granular session observations automatically.

**v19 truth-hierarchy update:** Since v18, a separate doctrine layer has emerged on monarch (`~/projects/jarvis/`) and in `github.com/trentbentt/jarvis` (public). Truth hierarchy for everything authority/Jarvis-related is now: monarch disk > git log on monarch > github raw > this reg-blueprint > chat history. Treat the doctrine docs (`AUTHORITY_SPEC_v19.md`, `HANDOFF_v19.md`, `DECISIONS_v19.md`, `INFRASTRUCTURE_BIBLE_v19.md`, `BIBLE_AUDIT_findings.md`, `README.md`) as canonical for the live system; this reg-blueprint is the deep build reference, not the live operating manual.

**v18 status preserved:** Core infrastructure COMPLETE. File system migration COMPLETE. All three critical risk items RESOLVED and verified on disk (May 14, 2026). News pipeline Phase 1 (schema + ingestion) and Phase 2 (automated ingestion via cron) COMPLETE — 2,362+ articles flowing across 9 sectors. **Phase 3 architecture pivoted (v18): n8n synthesis retired → hybrid T2+Cowork; Stage 2 (local T2 sector synthesis) deployed and validated May 17, 2026; Stages 3-5 next.** **Five-tier inference stack VALIDATED in first live bringup May 16, 2026** — all 8 services UP, end-to-end LiteLLM routing verified, T4 pivoted from vLLM to llama.cpp during bringup (see v16 changelog). **Three-mode VRAM reallocation doctrine (Standard/Burst/Soft) introduced in v16** with `inference-burst-up` / `inference-burst-down` interim scripts validated end-to-end (T2 measured 4.2× speedup in burst mode). Jarvis Phase 18 scope expanded to include GPU layer policy supervisor. qwen-coder-deep retired from automated use (manual on-demand only). LoRAs still untrained. **v18 (May 17, 2026) — MacBook voice-to-text input for agent harnesses LIVE.** Hands-free dictation system (wake word "Okay Comrade" → Whisper STT → paste/submit, end word "You May Begin") fully functional on M2 MacBook Pro 8GB. Drives OpenCode / Claude Code / Claude Pro browser sessions hands-free. Pivoted from Porcupine to OpenWakeWord during bringup after Picovoice Console signup blocked on company-email requirement. **This subsystem is a sister voice system to Phase 18 Jarvis, not a prerequisite or input layer for it.** Jarvis is voice-to-voice for system observation; Phase 17.5 is voice-to-text for agent input. They share only the physical mic. **Next major build target: Phase 18 Jarvis** (unchanged scope — supervisor responsibility + voice-to-voice loop). **v17 folds in the offload-then-hotswap methodology clarification** — the three-mode doctrine is now named, the sequential-not-concurrent scheduling rule is explicit, and the Jarvis operator-negotiation flow is specified to implementation granularity. The v16→v17 addendum is superseded by this revision and should not be referenced separately.

---

## Current State — May 16, 2026 (post-bringup)

| Component | State | Notes |
|---|---|---|
| Hardware (monarch) | ✅ Live, 24/7 headless | RTX 3090, 96 GB DDR5, 4 TB NVMe |
| n8n + Postgres | ✅ Running | Restart policy `always`; 79 tables initialized |
| n8n encryption key | ✅ Verified May 14, 2026 | In 1Password, n8n volume, and `api_keys.env`; compose references `${N8N_ENCRYPTION_KEY}` |
| Tailscale Funnel | ✅ Verified May 14, 2026 | `/ → proxy http://127.0.0.1:5678/webhook/` — UI not publicly reachable. apt-mark hold still needed (W2.3) |
| Postgres backup cron | ✅ Verified May 14, 2026 | Fired at 02:00; backup confirmed. Restore drill passed — 79 tables restored clean |
| CUDA 12.8 pinning | ✅ Applied May 16, 2026 | 11 packages on `apt-mark hold`. Quarterly verification SOP in Phase 2. Prevents the Qwen3.6 gibberish-output regression that any 13.x upgrade would cause until 13.3+ is proven. |
| Inference stack — five-tier architecture | ✅ Live, first bringup May 16, 2026 | All 8 services UP. Standard config VRAM 22901/24576 MiB (1675 free). T1 reconfigured this session to np=1 / 36K ctx (architectural prep for Jarvis supervisor). T4 pivoted from vLLM to llama.cpp during bringup. All v15.1 corrections applied and validated. End-to-end LiteLLM routing through T2 and T4 confirmed coherent. |
| Burst-mode infrastructure | ✅ Validated end-to-end May 16, 2026 | `~/bin/inference-burst-up` / `inference-burst-down` written and round-tripped cleanly. Burst T2 measured at 22.9 tok/s gen (4.2× standard's 5.4) with 3036 MiB free VRAM during burst. Cycle time ~21s up+down. Interim implementation; superseded by Jarvis Phase 18 supervisor when built. |
| qwen-coder-deep | ⚠️ Retired from automation | Manual on-demand only (NDA-tagged work). Reasoning recorded in Appendix A. |
| File system | ✅ Verified May 14, 2026 | All 6/6 CONSTITUTIONs genuine (64–135 lines): financial 135, consultancy 83, content 89, design 80, exploratory-coding 76, leads 64 |
| News pipeline | ⚠️ Phase 3 — Stage 2 VALIDATED, Stages 3-5 next | Phase 1 (schema+ingestion) ✅ May 15. Phase 2 (cron automation) ✅ May 15. **Phase 3 architecture pivoted: n8n synthesis RETIRED → hybrid T2+Cowork (see §What Changed in v18).** Stage 2 (local T2 sector synthesis via `synthesis_export.py`) smoke-tested and validated May 17 — two full 9-sector runs (direct + `news-synth` wrapper), 9/9 ok, 0 errors, ~5-6 min wall time, output quality verified. 2,362+ articles in news_unified across 9 sectors. Stages 3-5 (Drive sync + Cowork compilation + brief pickup) not yet built. |
| Financial pipeline | ⬜ Design only | Paper trading not started; circuit-breaker not built. Phase A timing must account for measured T2 throughput (~44 min in burst, ~3.5 hr standard) — see §Phase 9 burst doctrine. |
| LoRA training | ⬜ Planned | All 5 LoRAs planned, none trained. v14 sequence: validation gate baseline → 1 week telemetry → first LoRA training. Each LoRA estimated to cost 200-500 MiB of T1 headroom; current Standard-mode headroom 1675 MiB allows ~3 simultaneous adapters before tightening. |
| Nexus (codebase index) | ⬜ Aspirational | Design conversation queued as next major item after 24h soak. |
| 2nd brain (knowledge base) | ⬜ Aspirational | Design conversation queued after nexus. |
| Jarvis daemon (v0.2) | ✅ LIVE since v19 cycle | **[v19 update]** Jarvis daemon v0.2 shipped. `~/projects/jarvis/` on monarch; `github.com/trentbentt/jarvis` public, 14 commits as of 2026-05-22 head `f0675da`. Writer thread, state.json, event ring buffer backing `jarvis-q events`. Hard Constraints ratified (Jarvis never shuts off; identity never routes to API; pause not in toolkit; T1 restart is Tier 3, never silent). Voice-to-voice surface (Phase 18) and PWA (Phase 19) are still planned but reserved ports `4300` / `4400` / `3000` are doctrinally locked. |
| Jarvis Phase 2 listeners | 🟡 2 of 5 live | **[v19 update]** `vram.py` (5s cadence — per-tier PID attribution, VRAM consumption, 80% baseline target, OOM thresholds) and `tier_health.py` (15s cadence — HTTP /health probes per tier; states OK / DEGRADED / UNRESPONSIVE / IDLE-for-burst-only) are LIVE and feeding state.json every 10s. The reusable `_port_from_cmdline()` PID resolution pattern lives in `vram.py` and is reused downstream. Spec-only: `process.py` (per-tier `rss_mb`/`cpu_pct`/`uptime_s`/`restart_count_24h`; drives the Tier 2 'restart on crash' action — ~2-3 hr estimate, no prereqs), `quota.py` (LiteLLM log parsing for spend / token / rate-limit proximity; ~3-4 hr including Path A wiring; logging-path closed 2026-05-24 — Path A ratified, `store_prompts_in_spend_logs=false`; quota.py doctrine-unblocked), `cron.py` (reconciles scheduled jobs vs actual runs; ~2-3 hr; easiest to defer). |
| AUTHORITY_SPEC_v19 | 🟡 Items 1-5 of 8 ratified | **[v19 update]** Decision 5 walkthrough across 2026-05-21 → 2026-05-22 banked Items 1-5 in commits `50692bd` / `414d5b2` / `f0675da`: Tier 1/2/3 action lists, Hard Constraints section, Overnight Workload Window (weekday 23:00-07:00 ET), Substrate Pressure Cascade (continuous intensity band 2.5 GB → 500 MiB free VRAM), bypass severity ladder (Notification Interrupt Conditions). Items 6-8 + Quota Cascade Policy threshold ratification (20%/10% prepaid model) remain open. |
| INFRASTRUCTURE_BIBLE_v19 | ✅ Live (1,158 lines) | **[v19 update]** Meta-reference compiled 2026-05-21, updated 2026-05-22 with Decision 5 commit refs and 9 folded audit corrections (B1/B2/B3/B4/B6/B11/B14 + A1/A2). New: §1 Raleigh residence (was Charlotte — audit §F1 records inheritance from session user-context drift), §3.3 Hard Constraints, §5.7 mmap weight sharing as the architectural reason 5 tiers fit on a 24 GB card, §10.4 continuous-intensity-band cascade (replaces the v18 three-mode sequential cascade ASCII diagram). |
| BIBLE_AUDIT_findings | ✅ Tracker mode | **[v19 update]** Tracker, not content source. 9 FOLDED markers (corrections integrated into bible), 3 RESOLVED markers (Decision 5 commits closed), 1 SUPERSEDED marker (continuous-intensity-band makes the discrete A4 OOM thresholds N/A). §F1-F3 audit-of-the-audit entries. |
| Rebalance v19 (94% → 66%) | 🟡 Change 1 executed | **[v19 update]** Monarch idled at 94% VRAM in v18 with no active workloads (T1 + T2 + T4 + driver = 23.1 GB / 24 GB). Rebalance Change 1 executed; post-Change-1 baseline is 66.0% (16.5 GB / 24 GB). Change 2 patched but measurement not landed (pending next natural T1 restart). Change 3 drafted, not executed. The 94→66 delta is the most consequential operational change in v19 and the forcing function behind every cardinal Decision. |
| News-pipeline-evidence (sister project) | 🟡 Phase 1 live, gate live | **[v19 update]** Sister project to the Jarvis fabric. `github.com/trentbentt/news-pipeline-evidence` (public, head `4728b23`). Monarch working tree at `~/projects/evidence-layer/`. Five invariants (I1-I5) and verdict precedence (REJECTED > QUARANTINED > HEDGED > VERIFIED) implemented at the data-structure level — `Ledger.record()` itself calls `grounding_postcheck` and raises on violation. Old `~/projects/news-pipeline/` still runs 06:00 cron — subscribers see that brief, not the evidence-layer output yet. Eleven-step build sequence locked; Phases 1-6 done, Phase 5 signal-class architecture drafted. |
| Jarvis (Phase 18 voice-to-voice) | ⬜ Design complete, scope expanded in v16, deferred behind Phase 2 listeners | Voice-to-voice assistant for system observation + GPU layer policy supervisor (see §Phase 18). **[v19 update]** Phase 18 voice surface deferred behind the Phase 2 listener layer. The supervisor logic that v17/v18 specced as the Phase 18 burst-mode supervisor has been generalized in AUTHORITY_SPEC into the Substrate Pressure Cascade plus the latency-band routing cascade — those doctrines now own the role. Phase 18 voice surface remains the next operator-touch surface but is no longer the next major build target; the listeners are. |
| MacBook voice-to-text input (Phase 17.5) | ✅ Live May 17, 2026 | Wake word "Okay Comrade" + end word "You May Begin" via OpenWakeWord. mlx-whisper-large-v3-turbo for STT. Hammerspoon for paste/submit into focused agent window (OpenCode / Claude Code / Claude Pro browser). Runs entirely on M2 MacBook 8GB, no monarch dependency. Distinct subsystem from Phase 18 Jarvis — shares only the physical mic. |
| Command Center PWA (Phase 19) | ⬜ Design complete | Build sequenced after Jarvis. |

---

## Documentation Set & Memory Strategy

This project uses a four-file documentation pattern plus an automatic memory plugin. The split exists because the failure mode of a single growing file is drift: permanent identity gets edited casually, living state gets stale, and the agent reads 5,000 lines to learn three facts it needed. Each file has one job and one update cadence.

| File | Job | Update cadence | Who reads it |
|---|---|---|---|
| `CLAUDE.md` | Lean entry point. Operating rules, where to look, what plugins/skills are active. | Rarely — only when the operating contract changes. | Claude Code, every session start (auto-loaded). |
| `CONSTITUTION.md` | Permanent identity. Operator profile, hardware envelope, non-negotiable doctrines, the ruled-out list pointer. | Almost never — changes here are architectural decisions. | Claude Code when it needs to know *why*; humans onboarding. |
| `CONTEXT.md` | Living state. Current phase, what's done, what's next, what's blocked, last-session handoff. | Every working session (end-of-session ritual). | Claude Code at session start to know where things stand. |
| `reg-blueprint.md` (this file, `master_summary_v19.md`) | Deep reference. Full architecture, every phase, every measured number, every ruled-out feature with rationale. | Per-revision (v16 → v17 → v18 → v19 → …), when a phase completes or a doctrine is added. | Claude Code on demand when implementing a specific phase; never read top-to-bottom in normal work. |
| `INFRASTRUCTURE_BIBLE_v19.md` | **[v19 update]** Live operating manual. The meta-reference describing the system as it currently is. Captures live doctrine, open queue, cardinals, decisions ledger, calibration lessons. | Updated when a session commits new doctrine to monarch. | Any agent or operator at session start. Read this before the reg-blueprint when orienting on live state. |
| `AUTHORITY_SPEC_v19.md` | **[v19 update]** Canonical source for what Jarvis may do autonomously. Tier 1/2/3 action lists, Hard Constraints, Substrate Pressure Cascade, Overnight Workload Window, Quota Cascade Policy, bypass severity ladder. | Per-walkthrough revision (Items 1-5 banked 2026-05-22). | Phase 2 listener implementations; any session designing Jarvis behavior. |
| `HANDOFF_v19.md` | **[v19 update]** Session-to-session continuity. Cardinals, open queue, Path B dual-session topology, "redesign over refine" principle. | End-of-session ritual. | First read of any new session. |
| `DECISIONS_v19.md` | **[v19 update]** Ledger of closed + in-flight decisions with rationale. | When a decision opens, progresses, or closes. | Sessions revisiting why a doctrine exists. |
| `BIBLE_AUDIT_findings.md` | **[v19 update]** Tracker of bible drift and corrections. §A self-contradictions, §B additions, §F audit-of-the-audit. Resolved/folded items annotated inline. | When new drift is surfaced or a fix lands. | Any session about to make a substantive bible edit. |
| `README.md` (in `~/projects/jarvis/`) | **[v19 update]** Operator entry point + doc index for the jarvis repo. | When the repo doc set changes. | First read for an operator opening the jarvis repo cold. |

**Read order:** CLAUDE.md is the only always-loaded file. It points to CONSTITUTION.md (read when the agent needs the *why* behind a constraint), CONTEXT.md (read at session start for *where we are*), and this reg-blueprint (read the relevant section when *implementing* that phase). The reg-blueprint is deliberately huge and deliberately not always-loaded — that is the point of the split.

**[v19 update] Refined read order for the live system:** For anything authority/Jarvis-related (Phase 2 listeners, daemon behavior, cascade response, notification policy), read in this order: `README.md` (jarvis repo entry point) → `HANDOFF_v19.md` (cardinals + current state) → `INFRASTRUCTURE_BIBLE_v19.md` (meta-reference) → `AUTHORITY_SPEC_v19.md` (the section relevant to the work). This reg-blueprint is the build reference; the v19 docs are the live operating manual. Truth hierarchy: monarch disk > git on monarch > github raw > this reg-blueprint > chat history.

**Memory plugin pairing.** The documentation set is the *human-curated, deliberate* layer. The [`claude-mem`](https://github.com/thedotmack/claude-mem) plugin is the *automatic, granular* layer. claude-mem hooks Claude Code's session lifecycle (SessionStart, PostToolUse, Stop, UserPromptSubmit, SessionEnd), compresses every tool use and decision into observations in a local SQLite store, and injects relevant context at the start of the next session — no manual tagging. The two layers are complementary, not redundant:

- **claude-mem answers:** "What did we actually do last Tuesday? Which files did we touch fixing the LiteLLM health-check bug? What approach did we try and abandon?" — granular, automatic, searchable, never curated.
- **CONTEXT.md answers:** "What phase are we in, what's the next deliverable, what's blocked, what should the next session start with?" — coarse, deliberate, the operator's own framing.
- **CONSTITUTION.md / reg-blueprint answer:** "What are the rules, the hardware limits, the doctrines, the things we already ruled out and why?" — stable, authoritative.

The end-of-session ritual is: update `CONTEXT.md` with the coarse state delta (this is the deliberate handoff), let claude-mem capture the granular trace automatically (this is the safety net for everything you didn't think to write down), and bump the reg-blueprint only when a phase completes or a doctrine changes. Wrap secrets in `<private>` tags so claude-mem's edge processing excludes them from the store — relevant here because NDA-tagged work (qwen-coder-deep) and API keys flow through this project.

**Operational note:** claude-mem can also auto-generate folder-level CLAUDE.md content from its observation DB while preserving manually written sections. Keep the hand-written CLAUDE.md content above a clearly marked boundary so the two never fight; treat any auto-generated block as advisory, not canonical. CONSTITUTION.md and this reg-blueprint are always hand-curated and never auto-generated.

---

## What Changed in v19

v18 closed with the five-tier substrate live, the news pipeline ingesting, the burst-mode interim scripts validated, and Phase 17.5 (MacBook voice-to-text) operational. The v19 cycle (2026-05-19 through 2026-05-22) ran four substantive doctrine sessions and three substrate changes. The forcing function was a single number: monarch idling at **94% VRAM** with no active workloads. Every cardinal Decision in v19 either explicitly addresses that number or implicitly assumes the rebalance is happening.

**Specific changes from v18:**

- **The 94% → 66% VRAM rebalance.** v18-era monarch idled at 23.1 GB / 24 GB even with nothing actively running (T1 + T2 + T4 + driver). Post-Rebalance Change 1, baseline is 66.0% (16.5 GB / 24 GB) — saved ~6.8 GB versus a deficit of 3.4 GB, and now sitting comfortably under the 80% target. Change 2 patched, measurement landing on next natural T1 restart. Change 3 drafted. The delta is what made every other v19 decision possible (T6 burst becomes physically feasible; the Substrate Pressure Cascade has room to operate; the multi-account parallelism stops competing with idle headroom).

- **Jarvis daemon v0.2 SHIPPED.** v18 had Jarvis as design-only with a planned Phase 18 build target. v19 closed that gap: `~/projects/jarvis/` on monarch and `github.com/trentbentt/jarvis` (public, 14 commits, head `f0675da` as of 2026-05-22). Writer thread, state.json, event ring buffer, `jarvis-q` CLI. The daemon is load-bearing for boot and recovery — Hard Constraint #1 (Jarvis never shuts off) is structural, not aspirational. Phase 18 voice surface and Phase 19 PWA remain planned with reserved ports (4300 / 4400 / 3000).

- **AUTHORITY_SPEC_v19 — Decision 5 walkthrough through Item 5.** A canonical source for what Jarvis may do autonomously now exists on monarch and github. Items 1-5 banked across three commits (`50692bd` / `414d5b2` / `f0675da`):
  - **Hard Constraints section** at the top — four lines that do not move: (1) Jarvis never shuts off; (2) Jarvis identity never routes to API (workloads route, the coordinator does not); (3) Pause is not in the toolkit (Jarvis re-routes work, never blocks it); (4) T1 restart is Tier 3, never silent. These were repeated across cascade descriptions; hoisting them removes ambiguity downstream.
  - **Tier 1 / Tier 2 / Tier 3 action lists** ratified with restructures. Tier 2 split tier-crash actions by tier class (T3/T4/T5 dataplane vs T2/T6 burst vs T1→Tier 3 escalation); added latency-band routing cascade. Tier 3 added T1 restart, latency cascade failed; Quota Cascade Policy supersedes the prior "all cheap walled → Anthropic" row.
  - **Overnight Workload Window** (weekday 23:00-07:00 ET; weekend deferred until post-9-5-transition pattern stabilizes). Controls scheduling preference, Substrate Pressure Cascade Layer 2 self-offload availability, and voice/push notification quieting. Bypass severity ladder fires regardless.
  - **Substrate Pressure Cascade — continuous intensity band 2.5 GB → 500 MiB free VRAM.** This is a meaningful reframe of the v18 doctrine. v18's three-mode VRAM doctrine (Standard / Burst / Soft) described workflows; v19's cascade describes a stateless response function from current VRAM free to current blended-intensity response across three response kinds (evict burst tiers → conditional self-offload → route workloads to API). The 2.5 / 1.5 / 0.75 / 0.5 GB markers are intensity guideposts, not discrete trigger thresholds. Switchover at next natural workload checkpoint (token-stream end / batch-item / message-turn end) avoids re-issue/dedup. The v18 three-mode operational language survives as the human-readable expression of cascade states; the doctrine layer underneath is now stateless and continuous.
  - **Bypass Severity Ladder** ratified (Notification Interrupt Conditions). GPU thermal 85°C/60s; security (left broad — operator uses multiple IPs / VPNs); spend burst $5/5min; RAM exhaustion < 500 MiB (kernel-OOM territory, threatens daemon survival); VRAM cascade exhausted (< 500 MiB AND Quota Cascade in Tier 3 surface — cascade has run out of moves); Power deferred (no UPS listener yet).
  - **Quota Cascade Policy (prepaid model)** — Each provider key carries a manually-loaded prepaid balance. Once spent, key unavailable until operator reloads. No auto-recharge, no monthly reset, no overage. 20% / 10% thresholds drive Tier 2 (route to next-cheaper rung) and Tier 3 (surface to operator) — explicit numeric ratification of these thresholds is the last outstanding Decision 5 item.

- **Items 6-8 still pending.** Item 6 — Pro tier estimation. v18 assumed ~250 msg/5h Pro Max vs ~50 msg/5h standard; Anthropic support docs (verified 2026-05-22) give the actual numbers: standard Pro ~45 msg/5h; Max 5x ~225 msg/5h; Max 20x ~900 msg/5h. Plus a weekly cap layer; plus peak-hours acceleration (5am-11am PT weekday burns ~1.5-2× faster — multiplier not published). v19 spec needs to choose single-axis vs two-axis (session+weekly) vs three-factor (peak-aware) estimate model. Item 7 — promotion threshold N=10 ratification. Item 8 — cold-start rule confirmation.

- **Schema rename: `sleeping_window_*` → `overnight_window_*`** (commit `414d5b2`). Defaults harmonized 22:30 → 23:00, 06:00 → 07:00 to match AUTHORITY_SPEC. `OperatorState.SLEEPING` enum kept (forward-looking surface for the Presence Axis); `voice_during_sleeping` kept (state-based gate, separable from window).

- **Operator residence: Raleigh, NC** (not Charlotte). Bible audit §F1 records that the initial bible compile inherited "Charlotte" from a session user-context location guess (Claude infrastructure surfaces approximate operator location to itself; that surfaced value was Charlotte, likely from VPN endpoint or ISP geolocation noise). Operator identity is separable from residence.

- **News-pipeline-evidence as a sister project.** `github.com/trentbentt/news-pipeline-evidence` (public, head `4728b23` as of 2026-05-22). Monarch working tree at `~/projects/evidence-layer/`. Distinct from the v18 news pipeline (`~/projects/news-pipeline/`, still runs 06:00 cron). The evidence layer's thesis: truth-bearing work (selection, attribution, corroboration) happens in a deterministic verification gate keyed on the *claim*, not the article. Five invariants enforced at the data-structure level (`Ledger.record()` raises on ungrounded text). Verdict precedence REJECTED > QUARANTINED > HEDGED > VERIFIED. The product property is provable by code reading rather than test running. Phases 1-6 done. Eleven-step build sequence locked. Subscribers still see the old pipeline; cutover happens when the evidence layer is signal-class-complete.

- **Three-account Claude.ai parallelism (correction).** v18 inferred "three Pro accounts"; bible audit A2 corrected to "two Pro confirmed; third account's tier not specified in any source-of-truth doc." Documentation tends to be ahead of any single account's chat history — this is the operational reason the truth hierarchy treats chat history as least-authoritative.

- **Doctrine layer separation.** v18 was the single deep reference. v19 introduces a layered doctrine: `README.md` (entry point) → `HANDOFF_v19.md` (cardinals + state) → `INFRASTRUCTURE_BIBLE_v19.md` (meta-reference) → `AUTHORITY_SPEC_v19.md` + `DECISIONS_v19.md` (canonical authority + decision ledger) → this reg-blueprint (deep build reference). The reg-blueprint stops being the live operating manual; it becomes the deep build reference. The bible is now the live manual.

- **Burst-mode interim scripts implicitly superseded by Substrate Pressure Cascade doctrine.** v16's `inference-burst-up` / `inference-burst-down` scripts remain validated and runnable, but the doctrine they were placeholders for has shipped at the spec level (not yet at the listener level). When `vram.py` and `process.py` Phase 2 listeners ship, the cron entries that drive burst-mode get removed and the cascade owns the substrate response. Until then, the scripts remain the working surface. This is the cleanest expression of the v19 forcing function: doctrine ratified before listeners are built means listeners ship against locked semantics.

- **Path B dual-session topology adopted.** HANDOFF_v19 specifies a dual-session pattern (control session + worker session) as the v19 working topology. Captured in commit `f4a7835`. "Redesign over refine" principle (commit `38b6446`) — when a design surface is structurally wrong, the v19 cycle rebuilt it rather than patching. The Substrate Pressure Cascade reframe is the canonical example: v18's three-mode framing was workflow-correct but doctrine-wrong; v19 rebuilt the framing rather than patching it.

- **Open audit items carried.** A3 (CLAUDE.md materially stale — Tier D backlog), A5 (state.json schema_version "0.1.0" — small mission), A6 (quota schema key `deepseek_v3` rename), A7 (v18 Hermes brainstorm document may not exist as a discrete artifact — Decision 2 prerequisite question), A10 (N=10 distinction surfaces in Item 7 ratification), A12 (SystemModel 9-domains vs 8 — cosmetic), A13 (HANDOFF intra-doc drift — Tier D). Plus B8/B10 (7-doc rubric as discipline, deserves its own ratification), B13 (session_start/checkpoint/wrap rituals).

---

### §V19A — Path B dual-session topology (architectural detail)

The substrate now runs across two tmux sessions instead of one. The split mirrors the v19 control-plane / dataplane doctrine **structurally** rather than as a maintenance discipline. Bible v19 §4 is canonical.

**Session map:**

| Session | Lifetime | Windows | Purpose |
|---|---|---|---|
| `control` | Long-lived; survives `inference-down` | `bootstrap`, `jarvis`, `validation-gate`, `lora-dispatcher`, `litellm`, `t1-interactive` | T1 is the Jarvis reasoning brain per Decision 1. LiteLLM routes to cloud during dataplane burst-down. VG/LD/Jarvis are services, not tiers. |
| `inference` | Dataplane; cycle-safe | `bootstrap`, `t3-content`, `t4-phi4`, `t5-small` (+ `t2-pipeline` when burst-up, future `t6-coder` when deployed) | `tmux kill-session -t inference` is now semantically safe — only dataplane dies. |

A separate `whisper` session runs the dictation system (Phase 17.5); unrelated to inference.

**The four execution substrates** (Jarvis's dispatch matrix):

| Substrate | Used for | Throughput | Cost shape |
|---|---|---|---|
| GPU (VRAM) | Highest-throughput inference: T1 reasoning, T4 utility, T2 pipeline burst, T6 coder burst | Tokens/sec dominated by VRAM bandwidth + offload ratio | Fixed hardware cost; bounded by 24 GB ceiling |
| RAM | Mid-tier inference where GPU is unavailable or burst-allocated; KV cache backing | Slower than VRAM, faster than disk swap | Effectively free up to 96 GB |
| CPU | T3 content (CPU-only via `CUDA_VISIBLE_DEVICES=`), T5 small (1.7B persistent); fallback when VRAM saturated | Order-of-magnitude slower than GPU for LLMs | Effectively free up to thermal limits |
| Cloud API | News Stage 4 synthesis, building/design (Claude Pro), frontier reasoning, throughput-tier overflow | Higher latency floor; higher quality ceiling; bounded by quota/budget | Money on the line — surfaced via Tier 3 authority |

Every workload has a default substrate and a cascade order. Authority Spec gates the cloud step because that's where money enters.

**What changed when Path B landed (2026-05-21 04:14-04:21 EDT):**

The dual-session split was promoted live, not as a fresh start. The historical observation that drove it: pre-Path-B, `inference-down` ran `tmux kill-session -t inference` which took T1, LiteLLM, validation-gate, lora-dispatcher, and Jarvis with it every time the dataplane needed to cycle. The teardown script then ran a straggler-kill prompt that offered to `sudo kill -9` the very services it had just destroyed. The defensive design assumed: an operator notices T1's PID in the list and declines. That depended on operator attention at the moment of cycle.

Path B removed the *need* for defense by removing the failure mode. Control-plane services live in a separate session whose lifetime is decoupled from the dataplane's. This is the canonical example of the **redesign-over-refine principle** (HANDOFF_v19, commit `38b6446`):

> When a Tier 3 (surface-and-ask) prompt fires repeatedly for the same underlying reason, the right move is sometimes architectural elimination, not tighter criteria. The `[y/N]` straggler prompt in pre-Path-B `inference-down` was the operator's last line of defense against a destructive default. Path B removed the need for defense by removing the failure mode. Future authority decisions should consider this option when a Tier 3 keeps recurring: redesign rather than refine.

**Operator-side script changes (live runtime, not all yet in repo):**

- `~/bin/inference-up` — dual-session aware. Creates `control` session if missing (idempotent). Per-service `already_up` port-check guards skip launches for control-plane services already running. Smoke tests still run unconditionally. Zombie-check rewritten to filter control-session survivors via parent-walk PID→session resolution.
- `~/bin/inference-down` — kills only `inference` session. Surviving GPU processes are inspected and reported with tmux affiliation, **not killed**. No force-kill prompt under any flag.
- `~/bin/t2-up`, `~/bin/t2-down` — already used `TMUX_SESSION="inference"` as a variable. T2 is dataplane.

**Repo file changed (commit `9858a6a`):**

- `deploy.sh` — Jarvis daemon window now created in `${CONTROL_SESSION}` instead of `inference`.

**Validation evidence captured at the time:** `tmux move-window` is empirically safe for VRAM-resident llama-server processes (T1 kept its 12 GB allocation, kept serving on port 8080, passed a coherence test after the move). Jarvis daemon's writer thread retained its 10-second cadence across the session reassignment.

---

### §V19B — The Six Cardinal Decisions framework

v19 organizes around six numbered architectural decisions. Three closed, two in flight, one blocked. The reg-blueprint should carry the framework at minimum because future sessions will reference Decisions by number.

**Decision 1 — Architectural reframe (CLOSED 2026-05-19).**
*Statement:* Local does **data plumbing + agentic glue + on-demand coder burst**. Cloud carries **synthesis + building/design + frontier reasoning**.
*Forcing function:* The 94% VRAM baseline. There is no headroom for the alternative. Confirming this collapsed approximately 10 other open decisions (closed Path 1/2/3, retired three high-stakes LoRAs, retired Cowork as a synthesis stage, confirmed Decision 4 cascade).
*Implications still propagating:* T1 is the Jarvis reasoning brain, not the OpenCode harness host. T2 is burst-only, not always-on (per Rebalance Change 1). The three high-stakes LoRAs (consultancy, design, exploratory-coding) are likely deferred indefinitely. Synthesis defaults to cloud — news Stage 2 routes through DeepSeek V4 Flash by default with T2 burst available on operator-triggered exception.

**Decision 2 — Hermes adoption shape (OPEN).**
*What's pending:* Pattern B parallel to n8n, Curator scoped narrowly or disabled, memory writes disabled, routed via DeepSeek V4 Flash initially.
*What's missing:* The v18-era Hermes brainstorm documents haven't been pasted into a fresh chat. Decision 2 cannot be closed cold without them — risk of confident speculation overriding actual prior thinking.
*Why it matters:* If Phase 2 Jarvis listeners coexist with Hermes agents, the boundary between "Jarvis observes" and "Hermes acts" matters. Hermes is the v18 candidate for agent automation; if adopted, it parallels n8n on workflow execution but exposes a different agent surface (memory + Curator). Pattern B is the "run it alongside n8n, don't migrate" choice. Curator-narrow is the "don't let it talk to the rest of memory" choice. Both are doctrinal stances.
*Next action:* Surface the v18 Hermes brainstorm docs (audit A7 flags they may not exist as discrete artifacts) and walk Decision 2 in a dedicated session.

**Decision 3 — T6 operational defaults (BLOCKED).**
*Statement (proposed, not closed):* Qwen3.6-35B-A3B UD-Q4_K_XL, 25% expert offload, 64K context, three named modes (comfort / conservative / aggressive).
*Blocked on:* (1) Model not downloaded (~21 GB pull required); (2) Spin-up tooling not written (`~/bin/t6-up`, `~/bin/t6-down` don't exist); (3) Rebalance Change 2 measurement not landed — need to confirm post-Change-2 baseline is comfortable enough to absorb T6 burst (~17-19 GB partial offload, or ~21 GB pure-VRAM mode) under one of the three modes.
*Mode shapes:* Comfort mode parks T1 and runs T6 burst-up under tight VRAM constraints. Conservative mode requires T2 + T4 down. Aggressive mode pushes expert offload higher with quality tradeoffs.

**Decision 4 — Cloud routing chain (CLOSED 2026-05-19).**
*Statement:* **Pro (×2) → DeepSeek V4 Flash → Kimi K2.6 → Haiku 4.5 → Anthropic API direct.** Cowork retired. The two-Pro head of the cascade reflects the three-account parallelism (two Pro confirmed; third account's tier not specified). This is the cascade composition; the Quota Cascade Policy (Decision 5 Items 1-3) governs the autonomous depth Jarvis walks before surfacing.
*Status:* Mostly a doc formalization. Stage 4 news migration to DeepSeek had already executed; Decision 4 wrote down the cascade order.
*Open small missions related to Decision 4:* Throughput-tier model ambiguity (used in leads and financial opencode.jsonc but not explicitly placed in cascade); no Moonshot/Kimi key (Tier 3 of cascade is theoretical until key acquired); Decision 4 doesn't address quota saturation across two Pro accounts — specced as "DeepSeek V4 Flash" but `quota.py` listener needs to track Pro usage to make this decidable.

**Decision 5 — Jarvis authority model (IN PROGRESS — Items 1-5 banked, 6-8 + Quota thresholds pending).** See What-Changed-v19 bullets above for the per-Item walkthrough state and commit refs.

**Decision 6 — Nexus / 2nd Brain scope (CLOSED).**
*Statement:* Nexus 17.1 (codebase index) is **design-only in v19**. 2nd Brain 17.2 is **deferred** — no design conversation queued.
*Why:* The v18 vision of nexus + 2nd brain as v19 deliverables collided with Decision 1's reframe (local stops doing synthesis-class work). Both remain in the roadmap; neither blocks v19 close.

---

### §V19C — Rebalance Change 1 execution detail

`REBALANCE_v19.md` is canonical. The reg-blueprint carries the artifact-level detail because the reg-blueprint is where build-history specifics belong.

**Change 1 — T2 to burst-only (EXECUTED 2026-05-19/20).**

- *Schema:* `TierConfig.burst_only: bool = False` field added to `jarvis/schema.py`; T2 marked `True`.
- *Bringup script:* `~/bin/inference-up` patched with `SKIP_BURST_ONLY_TIERS="t2"` constant. T2 skipped during standard bringup.
- *Operator tooling:* `~/bin/t2-up` and `~/bin/t2-down` written, idempotent, dry-run verified.
- *LiteLLM:* `qwen3.6-pipeline` → `deepseek-v4-flash` fallback wired and tested end-to-end. When T2 is down (which is the default state under Change 1), pipeline calls fall through to cloud rather than failing.
- *Measured baseline post-Change-1:* **66.0% / 16.5 GB**. Validated 2026-05-20 across cold-cycle teardown and rebuild. Reproducible.
- *Saved vs 94% baseline:* ~6,832 MiB. Larger than the original deficit (3,442 MiB). Even without further changes, baseline is comfortably under the 80% target.

**Change 2 — T1 ctx 36K → 24K (PATCHED 2026-05-21, measurement deferred).**

- *Schema:* `~/projects/jarvis/jarvis/schema.py` MONARCH_TIERS T1 `context_size`: 36864 → 24576.
- *Script:* `~/bin/inference-up` T1 launch line `--ctx-size`: 36864 → 24576.
- Both files patched and committed (`c0f7ea7`).
- *Measurement deferred to next natural T1 restart.* T1 is in the `control` session and survived the Path B cold cycle by design — the schema-level patch will land on next reboot or explicit control-session kill.
- *Expected effect:* ~500-800 MiB drop in T1 VRAM (KV cache scales with ctx size). Projected baseline ~63-64% / 15.5-16.0 GB.

**Change 3 — T4 `-np 4` → `-np 2` (PROPOSED, NOT EXECUTED).**

- *Status:* Drafted, pending Change-2 measurement.
- *Rationale:* T4 with `-np 4` supports four concurrent slots; `-np 2` supports two. Validation-gate grader calls are sequential per request — concurrency 4 is over-provisioned for current load.
- *Estimated savings:* ~1 GB.
- *Honest call from the v19 cycle:* likely unnecessary. Post-Change-1 + Change-2, baseline is ~63%. T6 burst at ~17-19 GB would put total at ~32-34 GB if T6 stacked on full baseline — which it doesn't, because T6 burst requires T2 already down and may require T1 parked depending on mode. The slack isn't load-bearing. Change 3 is optional.

**What Rebalance unlocks (Decision 1 doctrine actionable):**

- 8 GB of free VRAM at idle for burst windows.
- T6 burst becomes physically possible (vs. "would OOM under standard mode" in v18).
- Phase 2 listeners measure against a stable baseline, not a shifting one.
- "Comfort / conservative / aggressive" modes from Decision 3 become real choices instead of "T6 cannot run."

---

### §V19D — Reading order + audit-of-the-audit pointers

**Bible §22 (Recommended Reading Order) — the canonical orientation sequence for any new session approaching v19 doctrine:**

1. `README.md` (jarvis repo entry point) — what the repo is and where to look
2. `HANDOFF_v19.md` — cardinals + current state + open queue
3. `INFRASTRUCTURE_BIBLE_v19.md` — the meta-reference describing the system as it is
4. `AUTHORITY_SPEC_v19.md` — the section relevant to the work
5. `DECISIONS_v19.md` — ledger of why specific doctrines exist
6. `BIBLE_AUDIT_findings.md` — when about to make a substantive bible edit
7. *This reg-blueprint* — when implementing a specific phase, never top-to-bottom

The reg-blueprint is **the deep build reference, not the live operating manual**. Bible v19 §23 ("What This Document Is Not") makes the inverse statement: the bible is the live operating manual, not the deep build reference. The two documents are paired; neither replaces the other.

**Bible audit §F — the audit-of-the-audit:**

- *§F1* — Records the Charlotte → Raleigh drift: the initial bible compile (2026-05-21) inherited "Charlotte" as the operator's residence from a session user-context location guess. Claude infrastructure surfaces an approximate location to itself; the surfaced value was Charlotte, likely from VPN endpoint or ISP geolocation noise. Operator is Raleigh, NC. Identity is separable from residence.
- *§F2* — Records the audit's transition from content source to tracker. Substantive corrections are folded into the bible; the audit retains §A (self-contradictions), §B (additions), §F (audit-of-the-audit) with resolved/folded items annotated inline.
- *§F3* — Sets the audit's go-forward usage discipline: surface drift before making changes, fold corrections inline, mark resolved items rather than deleting them so the bible audit reads as a trail rather than a checklist.

The reg-blueprint cross-references these because future v19 sessions should know the audit is a tracker, not a content source — when looking at a bible claim that feels off, check the audit first to see whether it's already known drift.

---

## What Changed in v16

v15 closed with the five-tier stack code-complete but unproven on hardware. v16 captures the first live bringup (May 16, 2026), the corrections discovered during it (originally tracked in `master_summary_v15.1_corrections.md`, now folded in), the architectural reconfiguration of T1 to support a future Jarvis supervisor pattern, the **three-mode VRAM reallocation doctrine** that replaces v15's implicit one-allocation-fits-all assumption, and the burst-mode interim scripts that were validated end-to-end at the close of the session. The v15.1 corrections document is superseded by this revision and should not be referenced separately.

**Specific changes from v15:**

- **Phase 9 — First bringup completed.** All 5 tiers + LiteLLM + validation gate + LoRA dispatcher came up clean on May 16, 2026. End-to-end LiteLLM routing through T2 and T4 returned coherent output. Measured baselines captured: T2 5.4 tok/s gen at standard config, T4 206 tok/s gen, T2 burst 22.9 tok/s gen.
- **Phase 9 — T4 engine pivot vLLM → llama.cpp.** vLLM 0.20.1 silently crashes at FlashAttention V2 initialization on Phi-4-mini fp8 with the Ampere SM86 + CUDA 12.8 combination. Reproduced across four launch variants. Pivoted to llama.cpp serving `unsloth/Phi-4-mini-instruct-GGUF:Q4_K_M` with full GPU offload + q8_0 KV cache. Removes vLLM from the stack entirely; all five tiers now llama.cpp.
- **Phase 9 — T1 reconfigured to np=1, 36K ctx.** Single-slot allocation; clears the operational path for parking/unparking T1 cleanly under burst-mode and the future Jarvis supervisor. 36K chosen over 48K because llama.cpp compute scratch scales with `n_ctx_seq`; the extra 12K context cost an additional 240 MiB without proportional utility.
- **Phase 9 — Three-mode VRAM reallocation doctrine — offload-then-hotswap methodology (NEW, named in v17). [v19 update: doctrine reframed as the continuous-intensity-band Substrate Pressure Cascade in AUTHORITY_SPEC_v19. The Standard / Burst / Soft mode language survives as operational shorthand for cascade states; the underlying doctrine is now stateless and continuous over 2.5 GB → 500 MiB free VRAM. Read AUTHORITY_SPEC_v19 §"Substrate Pressure Cascade" for canonical doctrine.]** The system's default response to a resource conflict is a clean hotswap (30s–3min transition), not permanent shrinkage or degraded-concurrent operation. The methodology: temporarily reallocate to run at peak efficiency, complete the workload, reallocate back. Standard (interactive default, T1 full residence, T2 lean) / Burst (T1 parked, T2 promoted to -ngl 60 for time-windowed pipelines, sequential not concurrent) / Soft (T1 preserved because the operator is actively using it, auto-fallback to offload or cloud). Replaces v15's single-allocation assumption. Quality of output is non-negotiable; allocation is negotiable. Permanent shrinkage to dodge a 30-second swap pays a GIGO tax 24/7 to avoid a one-time cost — never the right trade. Context size and weight determine output quality; starving either to avoid a swap produces garbage at slow speed.
- **Phase 9 — Burst-mode interim scripts.** `~/bin/inference-burst-up <pipeline-name>` and `~/bin/inference-burst-down` written, validated end-to-end May 16. Throwaway implementation; deprecated when Jarvis Phase 18 ships.
- **Phase 9 — VRAM ceilings calibrated to measured reality.** v15's estimates were ~1.2 GB low. Updated to measured.
- **Phase 9 — Multiple v15 spec corrections applied.** T1 layer count 40-of-64 (was 40-of-62); `--language-model-only` flag does not exist → `--no-mmproj`; T3/T5 require `CUDA_VISIBLE_DEVICES=` prefix to actually be CPU-only (recovers 1.7 GB); T4 KV cache must be q8_0 (saves 942 MiB); T5 model repo is `unsloth/Qwen3-1.7B-GGUF:Q5_K_M` (not bartowski); smoke tests must pass `chat_template_kwargs: {enable_thinking: false}` for Qwen3 reasoning-default models; `wait_for_port` and `inference-status` must use `/health/liveliness` for LiteLLM port 4000.
- **Phase 2 — CUDA 12.8 pinning operationalized.** 11 packages on `apt-mark hold`. Quarterly verification SOP added. Prevents the Qwen3.6 gibberish-output regression that any 13.x upgrade would currently cause.
- **Phase 18 — Jarvis scope expanded.** Jarvis now owns time-of-day GPU layer policy in addition to its v15 voice/notification responsibilities. Supervisor loop, failure-mode catalog, and recursive-dependency resolution (T4 fallback for Jarvis's own reasoning during T1-parked bursts) documented. Build sequencing unchanged — Jarvis is still the next major build target after 24h soak.
- **Phase 9 — `fail()` behavior flagged as outstanding.** v15's `fail()` does `tmux kill-session -t inference`, destroying healthy upstream tiers on any downstream tier's failure. During bringup debugging this cost multiple full rebuilds. Patch is one line (script-exit only, leave tmux intact) but not yet applied. Listed in Open Items.
- **Phase 9 — LiteLLM smoke test flagged as outstanding.** End-to-end routing test accepts empty `content` field silently because it only checks JSON parse, not field population. Cosmetic — production calls have enough max_tokens to be unaffected — but logged.
- **Open Items updated.** First bringup ✅. Burst-mode validation ✅. CUDA pinning ✅. T1 reconfig ✅. New items: T1/T3/T5 generation-speed benchmarks (not captured this session); cloud API key acquisition (DeepSeek V4 Flash/Pro, Kimi K2.6 — required to uncomment LiteLLM fallback chains); fail() patch; LiteLLM smoke-test fix.
- **Appendix A — One ruled-out entry added:** vLLM for Phi-4-mini fp8 on Ampere SM86 + CUDA 12.8 (silently crashes at FlashAttention V2 init).

## What Changed in v18

v17 closed with the three-mode doctrine clarified and Phase 18 Jarvis specified to implementation granularity. v18 captures the May 17, 2026 build session that produced an unplanned but durable subsystem: a fully functional hands-free **voice-to-text input method for agent harnesses** on the M2 MacBook (wake word → STT → paste/submit into the focused window). This is documented as **Phase 17.5** and is positioned as a **sister voice subsystem to Phase 18 Jarvis, not a prerequisite or input layer for it**. The two systems share the wake-word listening pattern but diverge entirely at the output: Jarvis is voice-to-voice (audio out to the operator's ears, monarch-resident, surfaces system observation), while Phase 17.5 is voice-to-text (paste keystroke into agent input fields, MacBook-resident, drives OpenCode / Claude Code / Claude Pro browser sessions). They share no runtime state and have no build-order dependency on each other.

**Specific changes from v17:**

- **Phase 17.5 (NEW) — MacBook Voice-to-Text Input for Agent Harnesses, LIVE on M2 MacBook Pro 8GB.** Full end-to-end pipeline: OpenWakeWord wake/end models → sounddevice capture → Silero VAD → mlx-whisper-large-v3-turbo STT → Hammerspoon paste+submit. Runs entirely on the MacBook, no monarch dependency. Wake word "Okay Comrade", end word "You May Begin". Auto-submit when front app is in the allowlist (browsers + terminals + Claude desktop). Daemon under launchd, JLab Go Air Pop ANC double-tap fallback for noisy/silent moments. **Purpose: hands-free interaction with the agent harnesses Trent codes against (OpenCode, Claude Code, Claude Pro browser tabs) — not a system control surface.** The dictated text is consumed by the agent in the focused window, the same way typed input would be. Phase 17.5 has no opinion about what the agent does with it.
- **Phase 17.5 — Explicit non-overlap with Jarvis.** Jarvis is voice-to-voice for system observation and supervisor responsibilities (Phase 18). Phase 17.5 is voice-to-text for agent interaction (Phase 17.5). The shared resource is the MacBook microphone, which both systems will listen to if both are running. The wake words must be distinct ("Okay Comrade" for Phase 17.5; Jarvis's wake word is TBD but will not collide). The intent classifiers are independent. Sharing a single mic listener at runtime is a future optimization, not a current requirement — both can run side-by-side on M2 hardware. See §17.5.0 boundary-of-responsibility statement.
- **Phase 17.5 — Wake word engine pivot: Porcupine → OpenWakeWord.** Picovoice Console signup blocked on company-email requirement during the build session. Pivoted to OpenWakeWord (`openwakeword` Python package, `.onnx` models trained on Outspoken at €1/model). No runtime API key required. Both engines are conceptually equivalent at the architecture level; the swap was lateral, not a downgrade. Captured in §17.5.2 (engine selection rationale) and Appendix A (Porcupine ruled out for new builds).
- **Phase 17.5 — Whisper model selection: large-v3-turbo, not large-v3.** Initial design used `large-v3` for accuracy on the noisy HFP earbud signal. First bringup on 8GB unified RAM showed heavy swap pressure (76M+ swapouts pre-load) — `large-v3` would consume ~2GB unified RAM resident. Pivoted to `whisper-large-v3-turbo` (~800MB RAM, ~1.5GB disk). For short-burst dictation the accuracy delta is imperceptible. When monarch is online and SSH-streaming becomes viable, the model can upgrade back to large-v3 served from monarch's 96GB RAM, but **this is independent of Jarvis** — it's just where Whisper inference runs. See §17.5.6 future architecture.
- **Phase 17.5 — Hammerspoon `hs.ipc.cliInstall()` regression on current build.** `cliInstall()` returns `false` on the shipped Hammerspoon version (May 2026); manual symlink works but the IPC handshake fails. The daemon falls back to `pbcopy + osascript keystroke` for delivery, which requires Accessibility permission for `Terminal` (or whichever shell launches osascript). This is fully functional and well-tested; the `hs` CLI path is a "nice to have" that buys the front-app allowlist gate, which the osascript path skips. Logged in §17.5.7 as an outstanding minor item.
- **Phase 17.5 — Five tuning passes captured.** (1) Audio scaling — OWW expects int16-range float32, not [-1, 1] float32; the model returned scores of 0.003 instead of 0.98 before scaling was added. (2) VAD frame size — Silero requires 512-sample frames, OWW requires 1280; the inner loop splits OWW chunks into VAD sub-chunks. (3) Retrigger cooldown — wake events were re-firing during the transcription window; cooldown set immediately at `start_recording` entry, not at delivery. (4) Threshold raised 0.55 → 0.75 to reject music false-fires. (5) Model `.reset()` after each take to clear OWW's sliding-window state. Captured in §17.5.5 (Build hardening lessons).
- **Phase 17.5 — Hardware fallback resilience.** Capture device is now re-resolved at every `start_recording()` call (was: resolved once at daemon startup). Three-layer fallback chain: JLab → MacBook → system default. JLab battery death or disconnect mid-session is recovered transparently with no daemon restart. Concurrent MacBook-mic access by the wake listener and capture stream is permitted by macOS (verified May 17, 2026). The four existing wake-retrigger protections are device-independent and apply equally on the fallback path. Battery drain on the JLabs is modestly increased (~10-15% on a heavy-dictation day); this is documented but not large enough to plan around. Captured in §17.5.4 (Daemon design) and the new §17.5.7 (Hardware fallback resilience).
- **Phase 18 — No scope change.** Jarvis is unchanged. The supervisor responsibilities, voice-to-voice loop, operator-negotiation flows, and recursive-dependency resolution all remain as specified in v17. The §Phase 18 section gets a single new paragraph at the top noting that Phase 17.5 exists as a sister system and they share only the physical mic. No code, no design, no build-order changes.
- **Appendix A — One ruled-out entry added:** Porcupine wake-word engine for new builds (May 2026 Picovoice Console requires company email for signup; non-blocking for existing AccessKey holders, but a hard barrier for new accounts and unsuitable as a default recommendation in this stack).

---

### v18 — News Pipeline Phase 3: architecture pivot + Stage 2 validation (May 17, 2026)

v18 also captures a second, independent build thread from May 17: the news pipeline Phase 3 architecture was finalized (a pivot away from the n8n synthesis design that earlier versions carried) and Stage 2 was deployed and smoke-tested to validation on monarch. This is unrelated to Phase 17.5 — different machine, different subsystem, same date.

- **Phase 3 — n8n synthesis architecture RETIRED, replaced by hybrid T2+Cowork.** The original plan (n8n HTTP-node workflows calling LiteLLM for Stream A / Stream B / final assembly) was never built and is now formally ruled out. The replacement is a five-stage hybrid: Stage 1 cron ingestion (existing) → Stage 2 local T2 sector synthesis via `synthesis_export.py` (9 sequential per-sector calls through LiteLLM `qwen3.6-pipeline`) → Stage 3 rclone sync to Google Drive → Stage 4 Cowork (Sonnet 4.6) stream compilation + final assembly → Stage 5 brief pickup + ntfy. Rationale: cross-sector/cross-stream reasoning quality on Qwen3.6-27B is materially weaker than Sonnet 4.6 for institutional synthesis; T2 burst capacity should stay free for financial/Jarvis work; Pro weekly Sonnet budget has ~95% headroom and news consumes ~1-2%. Sector synthesis (bounded summarization, T2's weakness least exposed) stays local; compilation/assembly (high reasoning load) goes to Sonnet via Cowork. Three-tier (T2+Haiku+Sonnet) was evaluated and rejected — Haiku's reasoning load is medium-high not low, the quality hit on the brief's analytical core isn't worth the ~3× saving on a 3-call stage.

- **Phase 3 — Stage 2 deployed and validated on monarch May 17, 2026.** `synthesis/synthesis_export.py` smoke-tested per the HANDOFF protocol. Two full 9-sector runs (direct invocation + `~/bin/news-synth` cron-equivalent wrapper), both 9/9 sectors ok, 0 errors, ~315-346s wall time (within the ~6 min target). 65 articles consumed per run; Postgres `used_in_brief` counts match `SECTOR_TOPN` exactly. Output quality verified: Variant A and Variant B both structurally correct, source attribution faithful, numeric figures spot-checked verbatim against source excerpts (geopolitics Ebola "246 cases and 80 deaths" confirmed against source — no hallucination), low-volume sectors (quantum, quant) correctly emit terse Variant B Signal Status rather than padding. Reproducible across both runs.

- **Phase 3 — Two implementation facts that are now load-bearing (not transient debugging).** (1) `synthesis_export.py` self-loads `~/.config/inference/api_keys.env` via `os.environ.setdefault` at startup (after imports, before config). Required because neither venv activation nor cron inherits shell-sourced environment — without this the script gets HTTP 401 (empty `LITELLM_MASTER_KEY`) and an empty FRED snapshot. Verified working through the wrapper, which is the cron path. (2) The LiteLLM payload must include `chat_template_kwargs: {"enable_thinking": false}`. On this llama.cpp build (b9172), Qwen3.6 with thinking enabled returns the entire chain-of-thought in `message.reasoning_content` with `message.content` empty — producing 0-char output files. The `/no-think` prompt-string convention does **not** work on this build; it must be the request kwarg. This corroborates the v16 spec-correction note that Qwen3 reasoning-default models need `enable_thinking: false` in smoke tests — it applies to production synthesis calls too, not just smoke tests.

- **Phase 3 — Out-of-scope but necessary infrastructure change.** `~/bin/inference-up` aborted on a VRAM budget gate (measured 12054 MiB vs a hardcoded 12000 MiB ceiling after Tier 1 — a 0.4% overage attributable to baseline driver/OS VRAM drift). This was a hard blocker: the stack would not start, so no synthesis was possible. The gate was raised 12000 → 12500 (one `sed`). Flagged for operator review — confirm 12500 is the right ceiling or replace the hardcoded gate with tolerance-based logic. No other inference-stack code was touched. This is recorded because the HANDOFF explicitly scoped the session away from inference code; the change was made only because it was an absolute prerequisite, and it is surfaced rather than buried.

- **Phase 3 — Findings flagged for operator, not fixed.** (a) `~/projects/news-pipeline/` is **not under git** — `synthesis_export.py` was edited in place multiple times this session with no version control or rollback path. Strong recommendation: `git init` + initial commit before any further edits. (b) `synthesis_export.py --dry-run` writes `manifest.json` despite the HANDOFF stating it should not — cosmetic, no functional impact, left as-is to stay within session scope. (c) The on-monarch `CONTEXT.md` "Active Phase Detail" and "Key Decisions Log" still describe the old n8n synthesis path and were intentionally left for operator reconciliation against this revision — updating them is a doctrine/narrative call, not session state.

- **Process note — circular-debugging recovery.** Stage 2's `reasoning_content` problem was initially approached with successive output-string post-processing patches (reasoning fallback → `/no-think` append → `##`-strip → regex heading-finder). This was a symptom-chasing loop; the operator called the halt, a conversation review confirmed the loop, and the root cause was correctly relocated to the inference request layer (`enable_thinking: false`), after which all the string-surgery patches were reverted. Recorded as a methodology data point: when fixes stack on fixes for the same symptom, stop and re-locate the layer.

- **Appendix A — ruled-out entries added (news pipeline):** (1) n8n HTTP-node synthesis workflows (Stream A / Stream B / final assembly) — superseded by hybrid T2+Cowork before any were built. (2) Cron-scheduled burst window *for news synthesis specifically* — T2 standard mode is sufficient for bounded sector synthesis; burst is not required for this pipeline (may still be used by other workloads). (3) Haiku 4.5 as the stream-compilation tier — reasoning load too high for the quality contract. (4) Three-tier model split (T2 + Haiku + Sonnet) for news synthesis — Haiku tier adds complexity without quality benefit; two-tier (T2 + Sonnet) is cleaner. (5) `/no-think` prompt-string convention for thinking suppression on llama.cpp b9172 — does not work; must use `chat_template_kwargs`.

## What Changed in v17

v16 closed with the three-mode VRAM doctrine introduced and the burst scripts validated, but the *methodology* was implicit and the Jarvis negotiation flow was under-specified for a builder. v17 folds in the offload-then-hotswap clarification conversation (May 16, 2026): the doctrine is named, the scheduling philosophy is made explicit, and the operator-negotiation paths are specified to the granularity Phase 18 needs to be built correctly. No architecture changed — this is a precision pass on intent.

**Specific changes from v16:**

- **Three-mode doctrine reframed as "offload-then-hotswap."** The methodology now has an explicit name capturing the actual execution pattern: temporarily reallocate to run at peak efficiency, complete the work, reallocate back. The default response to a resource conflict is a clean 30s–3min hotswap, never permanent shrinkage or degraded-concurrent operation. Captured in §What Changed in v16 (Phase 9 line) and §Three-Mode VRAM Doctrine core principle.
- **Sequential pipeline scheduling rationale made explicit.** News-then-financial sequential in burst mode is the *designed* pattern, not an edge case. Concrete math added: ~55 min sequential burst vs ~3.5+ hr concurrent standard at lower quality. Captured in §Three-Mode Doctrine, §Mode 2 behavior, and a new §18.0 "Pipeline scheduling philosophy" subsection.
- **Jarvis operator-negotiation flow specified to implementation granularity.** The three operator response paths are now named and distinguished: yield-to-Claude-Code, yield-by-stepping-back, and no-response/can't-yield (automatic offload fallback). Auto-fallback is the *designed* behavior when the operator is unavailable, not a failure mode. 5-minute hard timeout, priority-ordered fallback chain (cloud → soft offload → defer). Captured in §Mode 3 status block, §Phase 18 supervisor loop step 3, §Phase 18 failure-mode catalog (two new rows).
- **Context-cutoff rationale captured.** The doctrine originates from a real constraint: large-context, high-quality inputs require full VRAM allocation; serving them under co-resident standard allocation produces garbage at slow speed. GIGO applies at the allocation layer, not just the prompt layer. The swap cost is always cheaper than hours of degraded output.
- **Documentation set formalized.** The lean CLAUDE.md / CONTEXT.md / CONSTITUTION.md / reg-blueprint pattern (this document) is now explicitly the canonical structure, paired with the claude-mem plugin for automatic session-observation capture. See §Documentation Set & Memory Strategy.
- **Appendix A — no new ruled-out entries.** v17 is a precision pass; architecture unchanged.

## What Changed in v15

v14 completed the five-tier always-on inference architecture, the validation gate, and the LoRA dispatcher. v15 adds the two operator-facing layers that close the loop between the running system and the person running it: **Jarvis** (always-on voice orchestration manager) and the **Command Center PWA** (unified glass-panel dashboard with push notifications and deep links). Both are read-oriented — they surface what the system is doing, not direct control surfaces. All control remains in the actual tools (n8n, OpenCode, tmux, Claude Code).

**Specific changes from v14:**

- **Phase 18 — Jarvis added.** Always-listening voice manager: openWakeWord daemon on MacBook (launchd), faster-whisper STT on monarch CPU, Chatterbox TTS, T1 Qwen3.6-27B as the reasoning engine. FastAPI service on port 4300. Reads morning briefings, surfaces telemetry anomalies, answers system-state questions. WebSocket notification bus for Command Center real-time push.
- **Phase 19 — Command Center PWA added.** React PWA on port 3000, Tailscale-only. Connects to a new read-only data API (FastAPI, port 4400) rather than directly to Postgres. Full connection surface documented. ntfy.sh push to mobile. Deep links to n8n, SSH, and OpenCode serve. N8N_SECURE_COOKIE flip gated on this going live.
- **Read-only data API added (port 4400).** Thin FastAPI service proxying Postgres reads + n8n API + inference-status into clean JSON endpoints for the PWA. No writes, no side effects.
- **Port assignments updated.** Three new ports: 4300 (Jarvis), 4400 (Read API), 3000 (PWA).
- **UFW rules updated.** Three new tailscale0 rules for the three new Tailscale-accessible services.
- **SOP table updated.** Jarvis service, Read API, PWA static server, MacBook daemon management.
- **Remaining Items updated.** N8N_SECURE_COOKIE item now references the PWA go-live as its trigger. React PWA item updated to reflect Phase 19 design.
- **Open Items updated.** v15 build sequence for Phase 18 and Phase 19 items added.
- **Appendix A — no new ruled-out entries.** Architecture is additive.

## What Changed in v14

v13 settled the LoRA-on-Qwen3.6 architecture question (llama-server, not vLLM) but kept the inference stack at a single interactive serving tier plus an on-demand "deep-think" tier. That topology assumes serial workflows — one OpenCode session at a time, with batch and pipeline work either competing for the same VRAM block or running while the operator is asleep. It cannot accommodate concurrent always-on pipelines without saturating Tier 1 or triggering takedown-and-rebringup cycles.

v14 rebuilds Phase 9 around the observation that **VRAM is zero-sum but RAM is abundant on monarch (96 GB)**, and that llama.cpp's `-ngl` argument plus Linux page-cache mmap sharing make it possible to run three Qwen3.6-27B instances at different GPU-layer ratios off the same underlying GGUF file. Combined with vLLM Phi-4-mini and a CPU small-model seed, this produces a five-tier always-on architecture where every concurrent workflow has a home, and LiteLLM fallback chains route overflow to cloud.

Two associated decisions follow from the five-tier shift:

1. **qwen-coder-deep retired from automated use.** At 3-5 tok/s under MoE expert offload, the achievable nightly token budget (~70-86k in 8 hours) cannot scale to a growing codebase's refactor needs without producing accumulating half-finished work. With two Claude Pro subscriptions in the daytime workflow, the "more brain right now" niche is filled by Claude Pro. Preserved as a manual on-demand capability for NDA-tagged work only. No cron touches it.
2. **A discipline layer becomes non-optional once five concurrent pipelines write to disk 24/7.** Validation gate (FastAPI, port 4100) and LoRA dispatcher (FastAPI, port 4200) added as the substrate for drift detection, per-workflow telemetry, and adapter management.

**Specific changes from v13:**

- **Current State block updated.** Inference stack row now reflects code-complete five-tier architecture awaiting first bringup. qwen-coder-deep, nexus, and 2nd brain rows added.
- **§Open Risk Items — Risk Item 5 resolved.** v13's LoRA-on-Qwen3.6 architecture conflict is fully resolved by v14's llama-server-based five-tier design. Marked ✅.
- **Model Stack §15 rationale updated.** Reflects three-tier Qwen3.6-27B deployment with mmap weight sharing.
- **Phase 9 — Inference Architecture rewritten end-to-end.** Three-engine table replaced by Five-tier table. Port assignments expanded. Tier 1 / T2 / T3 / T4 / T5 sections written. LoRA Management section with two patterns (session-wrapper for T1, dispatcher for T3). Validation Gate section added. LoRA Dispatcher section added. LiteLLM config expanded. VRAM and RAM budget tables updated. Startup script replaced by `~/bin/inference-up` with VRAM ceilings. Verification Checkpoints expanded to per-tier. Failure Modes expanded. qwen-coder-deep status reclassified.
- **Phase 9 — Five v12 broken quotes corrected** (originally addressed by v13, re-corrected for five-tier in v14).
- **Phase 10 — OpenCode config note added.** Session wrappers manage T1 adapter state.
- **Phase 16 — Discipline Layer added** (new phase). Validation gate integration, per-workflow working directories, telemetry-driven drift detection, git-gated agent commits (planned).
- **Phase 17 — Aspirational Knowledge Systems added** (new phase). Documents nexus (codebase index) and 2nd brain (knowledge base) as deferred design items with explicit "design before build, build before maintain" sequencing. **§17.4 Continual Improvement** added: improvement-ledger service (buildable now — thin disposition/outcome + abandoned-approach capture, leaderboard as SQL view), multi-dimensional retrieval weighting as a nexus/2nd-brain design parameter, deliberate outcome-based retraining as a design conversation.
- **Appendix A — Six new ruled-out entries.** vLLM multi-LoRA on Qwen3.6 (carried from v13); overnight automated refactoring via qwen-coder-deep; multi-mode inference switching; per-request multi-LoRA on T1 via punica-style serving; closed-loop automated LoRA retraining on validation-passed outputs; single-scalar self-reinforcing knowledge weighting.
- **Operational deliverables shipped.** `~/bin/inference-up` (VRAM-gated five-tier bringup), `~/bin/inference-down` (clean shutdown), `~/bin/inference-status` (health snapshot), `~/services/validation-gate/` (FastAPI service, three checks, telemetry), `~/services/lora-dispatcher/` (FastAPI service, workflow-scoped adapter swap).

## What Changed in v13

v12 had a load-bearing architectural contradiction: the inference stack documented vLLM multi-LoRA hot-swap on Qwen3.6-27B, which is a Qwen3-Next hybrid architecture (interleaved Gated DeltaNet linear-attention + softmax attention + native MTP head). vLLM's `SupportsLoRA` mixin is not implemented for this topology. Additionally, the doc simultaneously recommended `UD-Q4_K_XL` (GGUF-only, llama.cpp) and vLLM serving — incompatible ecosystems. v13 resolved this by committing to Path C: llama.cpp serving for Qwen3.6-27B with session-level LoRA swap via `/lora-adapters` endpoint. vLLM retained for Phi-4-mini only.

**Specific changes from v12 (all applied in this v14 doc):**

- **Architecture decision recorded:** LoRA-bearing primary model moved from vLLM to llama.cpp. vLLM scope reduced to Phi-4-mini utility classifier only.
- **§Open Risk Items updated** — Risk Item 5 introduced (LoRA-on-Qwen3.6 conflict) and resolved.
- **§15 "Why Qwen3.6-27B" rationale corrected** — vLLM multi-LoRA bullet replaced with llama.cpp session-level adapter swap.
- **Phase 9 — Three-Engine Architecture table rewritten** — vLLM #1 role collapsed; llama-server promoted to primary GPU engine.
- **Phase 9 — vLLM Deployment #1 block replaced** with llama-server invocation for Qwen3.6-27B.
- **Phase 9 — LoRA management section added** — `/lora-adapters` endpoint swap pattern, session wrapper scripts per stack.
- **Phase 9 — LiteLLM config updated** — `qwen3.6-*` entries point to port 8080 (llama-server), not port 8000 (vLLM).
- **Phase 9 — VRAM budget, startup order, checkpoints, failure modes all updated** for llama-server context.
- **Phase 10 — OpenCode config note added** — adapter state set by session wrapper, not model name.
- **§Port Assignments — Port 8000 retired**, port 8080 added for llama-server.
- **Appendix A — Ruled-out entry added**: "vLLM for Qwen3-Next hybrid LoRA serving."
- **Five v12 quotes corrected** in their original locations.

> **Note on the v13→v14 transition.** v13 was published as a corrections block applied to v12. v14 supersedes it entirely — every v13 correction is incorporated below, plus the additional v14 changes. There is no longer a separate v13 corrections document to maintain. If you find yourself referencing `master_summary_v13_corrections.md`, treat it as historical context only.

## What Changed in v12

v11 completed the Error Audit (documentation corrections only). v12 documents the first live build session of the news pipeline (May 15, 2026). All changes reflect actual deployed state on monarch.

- **Current State block updated.** News pipeline row advanced from ⬜ Architecture only → ⚠️ Phase 3 in progress.
- **Phase 15 open items updated.** news_unified ingestion pipeline, daily_stream_outputs table, and deploy infrastructure marked complete. Phase 3 remaining items updated.
- **Project Portfolio updated.** News pipeline status updated from "Architecture complete, n8n build pending" to "Phase 1+2 complete, Phase 3 in progress."
- **News pipeline build — Phase 1 complete (May 15, 2026):**
  - `sql/001_schema.sql` deployed — 5 tables: news_sources, news_unified, daily_stream_outputs, news_pipeline_runs, cross_sector_signals. All indexes confirmed.
  - `sql/002_sources_seed.sql` deployed — 48 sources across 9 sectors seeded in news_sources.
  - `ingestion/fetch_worker.py` built and tested — universal fetcher: rss, newsapi, fmp, finnhub, alphavantage, github_api (HN Algolia + HF models API), fred, sec_edgar. Deduplicates by URL.
  - All credentials live: newsapi ✅, finnhub ✅, alphavantage ✅, fred ✅. FMP disabled (free tier restriction).
  - Dead RSS sources switched to NewsAPI: anthropic_blog, openai_blog, meta_ai_blog.
  - 2,362+ articles in news_unified across all 9 sectors.
  - Postgres exposed to host on localhost:5432 (`127.0.0.1:5432:5432` in docker-compose.yml).
- **News pipeline build — Phase 2 complete (May 15, 2026):**
  - `~/bin/news-ingest` wrapper script — sources api_keys.env, runs fetch_worker --all.
  - Crontab updated: `*/30 * * * * /home/monarch/bin/news-ingest` (alongside existing pg-backup cron).
  - n8n ingestion workflow (01_ingestion.json) abandoned — executeCommand node unavailable in current n8n image; cron + host script is strictly better for host-side scheduled tasks (no Docker/host boundary issues).
  - `~/n8n/.env` created — POSTGRES_PASSWORD and N8N_ENCRYPTION_KEY auto-loaded on every `docker compose up`, preventing env-less restart issue.
  - n8n updated to latest image.
- **Architecture decision recorded:** n8n is used for synthesis only (HTTP Request nodes to LLM API + Postgres read/write). Ingestion is cron. This is the correct tool split and is now the canonical pattern.
- **Context system deployed to monarch:** CONSTITUTION.md, CONTEXT.md, ref-blueprint.md, AGENTS.md/CLAUDE.md symlinks, .opencode/ directory, pipeline-builder agent, Plan.md, Changelog.md all live at `~/projects/news-pipeline/`.

## What Changed in v11

v10 completed the News Pipeline architecture documentation. v11 applies the Error Audit (May 14, 2026) — no new features. All changes are documentation corrections.

- **Current State block added.** Single canonical status table replaces the contradictory header claim vs Risk Summary table (E1, E2, E3).
- **Risk Summary table corrected.** R1–R3 status updated from ❌ to ⚠️ (resolved per v9 changelog; disk verification still needed per W1.2).
- **Phase 11 / Phase 12 contradiction resolved (E5, E6, E7).** Phase 11 superseded note prepended. Migration script updated to operate on CONSTITUTION.md. Symlink convention updated to match Phase 12. AGENTS.md skeleton relabeled as CONSTITUTION.md template.
- **Duplicate Open Items table removed (E8).** Lines 1669–1675 (second copy) deleted.
- **Phase 5 compose updated (E4, E9).** `POSTGRES_PASSWORD` and `DB_POSTGRESDB_PASSWORD` updated to env var references. `N8N_ENCRYPTION_KEY` added to n8n service block. Env file load instruction added.
- **LiteLLM config fixed (E13, E14, E15, E16).** `throughput-tier` promoted to `model_group_alias` in `router_settings`. `routing_strategy: simple-shuffle` documented with explicit caveat. `--served-model-name` flags added to both vLLM launch commands. `database_url` isolation note added.
- **Checkpoint 13 updated (E5/E7 residual).** Checks CONSTITUTION.md and both symlinks instead of AGENTS.md only.
- **Tailscale pin note added (E11).** `apt-mark hold tailscale` and monthly SOP check added to Phase 14.
- **Pro alias definitions added (E17, E18).** Concrete `claude-personal` / `claude-client` alias definitions added to Phase 14.
- **Appendix A — Ruled-Out Features Log added (E22).** All scattered "why not" rationales consolidated into a single permanent appendix.

## What Changed in v10

v9 completed Phase 14 (operational tooling and security hardening). v10 documents the News Pipeline as a standalone system and establishes its future integration surface with the rest of the stack. New material:

- **§Phase 15 — News Pipeline added.** Full hierarchical synthesis architecture documented: dual-stream (Stream A: AI/Tech; Stream B: Political/Financial), per-sector synthesis, stream compilation, final assembly. 12 daily API calls, ~29K tokens/day, ~3–4 min wall time. Postgres storage schema for compiled blocks included.
- **§Pipeline Inference Strategy added (Phase 9 appendix).** Critical architectural principle: pipelines optimize for accuracy, not speed. Real context windows documented (262K native / 1M YaRN for both Qwen3.6-27B and 35B-A3B). `--max-model-len` identified as a KV cache budget cap that silently discards ~230K tokens of context at default settings — not a model capability limit. Full KV cache VRAM math, memory tier strategy (VRAM → RAM → NVMe), interactive vs pipeline mode operational pattern, and the two-layer fast ingestion / slow synthesis design documented. Applies to all pipelines (news, financial, leads).
- **Future integration surface defined.** Three planned crossover points captured (not yet built): (1) Stream A AI intelligence feeds AI infrastructure decisions and model stack maintenance; (2) Stream B Finance + Geopolitics feeds long-term portfolio hedging and position sizing in the financial pipeline; (3) Cross-sector signals from Stream B compilation feed directly into financial pipeline data sourcing for trading algorithms. These are flagged as `⬜ Planned` — no wiring built yet.
- **Project Portfolio updated.** News Pipeline added as an active personal infrastructure project.
- **Financial stack updated.** Future news feed integration noted in the financial stack's data-sourcing and analysis substacks.

## What Changed in v9

v8 integrated the ground-truth discovery session and upgraded the context system design. v9 completes Phase 14 (operational tooling and security hardening). New material:

- **n8n encryption key secured.** Key extracted from running Docker volume and saved to 1Password Private vault. `N8N_ENCRYPTION_KEY` added to `docker-compose.yml` so future rebuilds preserve credentials.
- **Tailscale Funnel restricted to webhook-only.** Funnel now exposes `/webhook/` only; n8n UI is behind Tailscale. Resolves the critical public exposure risk (Risk Item #2).
- **Postgres backup cron implemented.** Nightly pg_dump at 2am, 7-day retention, log at `~/backups/postgres/backup.log`. Resolves Risk Item #3.
- **`~/bin/` operational scripts.** `inference-up` (startup orchestration) and `pg-backup` (nightly backup) added to PATH. `monarch-startup.service` systemd unit enabled for boot-time orchestration.
- **File system migration completed.** All 6 stacks scaffolded with CONSTITUTION/CONTEXT files. Financial pipeline directories migrated. API keys centralised at `~/.config/inference/api_keys.env`. CONTENTGEN scripts migrated. free-data-sourcing skill extracted from ZIP.

## What Changed in v8

v7 specified the file system architecture on paper. v8 integrates the ground-truth discovery session (actual Desktop inventory on monarch) and upgrades the context system design. New material:

- **§0 Business Identity added.** Taolen Logic / Trent M. Dunkak / tyrent.ai — business context now lives in the doc so every stack's CONSTITUTION.md can reference the canonical identity without drift.
- **CONSTITUTION + CONTEXT dual-file pattern replaces flat AGENTS.md.** Adopted from the Context_soln system already built and in use. CONSTITUTION.md = permanent anchor (read every session, never updated casually). CONTEXT.md = living state (updated by checkpoint compression and `/wrap`). This is a strict improvement over a single flat AGENTS.md.
- **`/wrap` command and checkpoint compression documented** as the session-end protocol for Claude Code. OpenCode equivalent documented separately (no `claude_mem` — CONSTITUTION/CONTEXT only).
- **7-document rubric system documented** as the standard for all pipeline builds across stacks — sourced from financial-pipeline/CLAUDE.md which already implements it.
- **Migration plan updated to match ground truth.** Source directories are on `~/Desktop/` not `~/projects/`. Actual directory names mapped. `free-data-sourcing.skill` is a ZIP package — requires `unzip`, not `cp`.
- **CONTENTGEN Python scripts inventoried** — 10 scripts across two directories, migrating to `~/projects/content/.opencode/substacks/youtube-ambient/`.
- **`claude_mem` caveat added** — this is Claude Code-specific. OpenCode sessions use CONSTITUTION/CONTEXT only without the mechanical capture layer.

## What Changed in v7

v6 finalized the deployment architecture (three-engine multi-host) and harness layer (OpenCode + Claude Code dual-Pro + Qwen Code CLI + n8n+LiteLLM). v7 adds the file system architecture that organizes how project context, skills, agents, and commands are structured across the six stacks. New material:

- **Phase 11 — File System Architecture.** Three-tier skill hierarchy (global / stack / substack), AGENTS.md as canonical with CLAUDE.md symlinked, promote-up convention for cross-stack skill reuse with lineage tracking, per-stack project layout, migration plan from existing CLAUDE.md/SKILL.md investments.
- **Cowork deprecated.** `~/financial-cowork/` retired; financial pipeline work moves to `~/projects/financial/` with the standard `.opencode/` layout. API keys migrate from `~/financial-cowork/.env` to `~/.config/inference/api_keys.env` (chmod 600).
- **Project scope clarified.** Six stacks (consultancy, exploratory-coding, design, content, leads, financial) are the file system scope. micro-saas and eeg-pipeline are out of scope for this iteration.

## What Changed in v6

v5 finalized the model stack and harness selection (OpenCode for local agentic, Claude Code for cloud premium). v6 added the deployment architecture: three-engine multi-host serving, LiteLLM routing, harness layer integration patterns, vLLM vs LiteLLM clarification, VRAM fragmentation gotcha with startup-order mitigation, expanded SOP with engine commands.

## What Changed in v5

The v4 model stack was written before Qwen 3.6 (April 16/22, 2026) and Qwen3-Coder-Next (April 8, 2026). Several v4 assumptions had aged out — DeepSeek R2 became cloud-only, Llama 4 Scout was outclassed by Qwen3.6-35B-A3B, and Qwen3 32B was superseded by Qwen3.6-27B (dense, smaller, better, native vision). 96GB DDR5 properly accounted for via MoE expert offload, unlocking Qwen3-Coder-Next 80B-A3B locally. CUDA 13.2 gibberish bug documented. Two Claude Pro subscriptions integrated as cloud fill tier.

See [§14](#full-planned-stack-reference) for the revised stack, [§15](#model-stack-may-2026) for selection rationale, [§16](#phase-9--inference-architecture--multi-host-deployment) for deployment architecture, [§17](#phase-10--harness-layer) for harness layer, and [§18](#phase-11--file-system-architecture) for file system architecture (NEW v7).

---

## Table of Contents
0. [Business Identity — Taolen Logic](#business-identity)
0a. [Documentation Set & Memory Strategy](#documentation-set--memory-strategy)
1. [Hardware Specs](#hardware-specs)
2. [Network Address Book](#network-address-book)
3. [Phase 1 — Linux Security](#phase-1--linux-security)
4. [Phase 2 — NVIDIA Drivers + CUDA](#phase-2--nvidia-drivers--cuda)
5. [Phase 3 — Tailscale](#phase-3--tailscale)
6. [Phase 4 — Docker + NVIDIA Container Toolkit](#phase-4--docker--nvidia-container-toolkit)
7. [Phase 5 — n8n + Postgres](#phase-5--n8n--postgres)
8. [Phase 6 — UFW Firewall](#phase-6--ufw-firewall)
9. [Phase 7 — Inference Stack (installed components)](#phase-7--inference-stack)
10. [Phase 8 — File Transfers](#phase-8--file-transfers)
11. [Standard Operating Procedure](#standard-operating-procedure)
12. [Remaining Items](#remaining-items)
13. [Open Risk Items & Architecture Decisions](#open-risk-items--architecture-decisions)
14. [Full Planned Stack Reference](#full-planned-stack-reference)
15. [Model Stack May 2026 — Selection Rationale](#model-stack-may-2026)
16. [Phase 9 — Inference Architecture & Multi-Host Deployment](#phase-9--inference-architecture--multi-host-deployment)
16a. [Phase 9 — Pipeline Inference Strategy (Accuracy vs Speed)](#phase-9--pipeline-inference-strategy-accuracy-vs-speed)
17. [Phase 10 — Harness Layer](#phase-10--harness-layer)
18. [Phase 11 — File System Architecture](#phase-11--file-system-architecture)
19. [Phase 12 — Context System (CONSTITUTION + CONTEXT)](#phase-12--context-system)
20. [Phase 13 — Migration Execution](#phase-13--migration-execution)
21. [Phase 15 — News Pipeline](#phase-15--news-pipeline)
22. [Phase 16 — Discipline Layer](#phase-16--discipline-layer)
23. [Phase 17 — Aspirational Knowledge Systems](#phase-17--aspirational-knowledge-systems)
23a. [Phase 17.5 — MacBook Voice-to-Text Input for Agent Harnesses](#phase-175--macbook-voice-to-text-input-for-agent-harnesses)
23b. [Phase 18 — Jarvis](#phase-18--jarvis)
23c. [Phase 19 — Command Center PWA](#phase-19--command-center-pwa)
24. [Open Items — v14](#open-items--v14)
25. [Appendix A — Ruled-Out Features Log](#appendix-a--ruled-out-features-log)

---

## Business Identity

| Field | Value |
|---|---|
| Business Name | Taolen Logic |
| Founder | Trent M. Dunkak |
| Location | Raleigh, NC — remote-first delivery, US-wide |
| Stage | Pre-revenue. Hardware live. Pipelines in build. |
| Social handles | tyrent.ai (Instagram + TikTok) |
| LinkedIn | Personal LinkedIn active. Dedicated business LinkedIn not yet created. |
| Business entity | Not yet formed (LLC pending) |

### Business Model
AI workflow automation consultancy for US small businesses. Path: freelance one-time builds → larger deals → SaaS template platform.

**Services:** Custom agentic workflow builds (data entry, lead qualification, onboarding, CRM, documentation, chatbots, pre-sales briefings) + SOPs + client team training + optimization retainer.

**Pricing:** $3,000–$4,000 build / $400/mo retainer first 6 months / $800/mo renewal. Build timeline: 2–4 days active + 1 week client stress test + reoptimization pass.

**Target verticals (first priority):** Salons, gyms, clinics, contractors, restaurants — any small business running manual versions of automatable workflows.

### Core Rule — Client Deployment
**All client-facing intelligence runs through Claude API. Always. No exceptions.**
Local stack = internal ops only. Local models are never deployed into client environments.

### Active Pipelines
| Pipeline | Status |
|---|---|
| TheCoolBreezeVibe (ambient YouTube) | Live. ~10 videos. YPP pending. |
| AI Education — tyrent.ai (inbound) | Instagram created, algorithm primed, no posts yet |
| Automated Outreach (outbound) | Architecture defined, not yet built |

### Open Business Items
| Item | Status |
|---|---|
| LLC formation | ❌ Not yet |
| Brand assets (logo, colors) | ❌ Not yet |
| Business website | ❌ Not yet |
| Beehiiv setup | ❌ Not yet |
| Tally/Typeform audit form | ❌ Not yet |
| Secondary domain (cold email) | ❌ Not yet purchased |
| Domain warming | ❌ Not yet started |
| Dedicated business LinkedIn | ❌ Not yet |

---

## Hardware Specs

| Component | Detail |
|---|---|
| Motherboard | ASRock B650I Lightning WiFi |
| GPU | NVIDIA GeForce RTX 3090 Founders Edition (24GB VRAM / 24576 MiB) |
| CPU | AMD Ryzen 9 9900X |
| RAM | 96GB DDR5 |
| Storage | 4TB NVMe |
| PSU | Cooler Master V850 SFX |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.17.0-23-generic |
| Hostname | monarch-B650I-Lightning-WiFi |
| Primary User | `monarch` (sudo) |
| GPU Idle Temp | 31°C |
| GPU Power Cap | 350W |
| GPU VRAM (llama-cpp detected) | 24117 MiB |
| Warranty | 1-year Allstate (GPU) |

### ⚠️ Critical Hardware Issue — RESOLVED
The RTX 3090 FE caused boot failures for 3 consecutive days. Root cause: a single daisy-chained PSU cable was feeding both 8-pin connectors on the 12-pin adapter. The RTX 3090 FE **requires two completely separate PCIe cables from two completely separate PSU ports** — one 8-pin connector used per cable, with the second head on each cable hanging loose and unused.

Fixing this resolved all boot hangs immediately. The GPU was professionally stress-tested and had thermal pads replaced by the seller prior to purchase. Covered by a 1-year Allstate warranty.

> **Lesson:** Never daisy-chain PCIe power on a high-draw GPU. The V850 SFX has separate modular ports — always use them independently.

The machine now runs **24/7 headless** — no monitor required. All access is via SSH over Tailscale from MacBook.

---

## Network Address Book

| Resource | Address |
|---|---|
| Local IP (home network only) | `192.168.12.170` |
| Tailscale IP (works from anywhere) | `100.101.244.6` |
| Tailscale IPv6 | `fd7a:115c:a1e0::f738:f406` |
| MacBook Tailscale IP | `192.168.12.224:41641` (direct interface) |
| SSH | `ssh monarch@100.101.244.6` |
| n8n (internal via Tailscale) | `http://100.101.244.6:5678` |
| n8n (public webhook via Funnel) | `https://monarch-b650i-lightning-wifi.tail89cb86.ts.net` |

**Active NIC:** `wlp8s0` (WiFi). Ethernet port `enp9s0` has no carrier and is inactive.

---

## Phase 1 — Linux Security
**Status: ✅ COMPLETE**

### User Setup
- Named user `monarch` created during Ubuntu install
- Confirmed in `sudo` group via `groups monarch`
- All operations run as `monarch`, never as root

### SSH Key Authentication
| Detail | Value |
|---|---|
| Key Type | ed25519 |
| Storage | 1Password — **Private vault** (NOT Shared ALL vault — agent ignores shared vaults) |
| Public Key | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBEJtdt10bcZs1KJ+Fo4uvHrXt3Z1IwJVmwwx5ee15uO` |
| Authorized Keys Path | `~/.ssh/authorized_keys` |
| Permissions | `authorized_keys` → chmod 600 / `.ssh` dir → chmod 700 |
| Password Auth | Disabled (`PasswordAuthentication no` in `/etc/ssh/sshd_config`) |

**1Password SSH Agent setup on MacBook:**
- 1Password SSH agent enabled via Settings → Developer
- MacBook `~/.ssh/config` written automatically by 1Password "Edit Automatically" option:
```
Host *
    IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
```
- SSH service restarted after `sshd_config` changes

### Fail2ban
- Installed via `sudo apt install fail2ban`
- Enabled and started via systemctl
- Config at `/etc/fail2ban/jail.local`:
```ini
[sshd]
enabled = true
port = ssh
maxretry = 3
bantime = 1h
findtime = 10m
```
> **Note:** The machine was receiving brute-force SSH attempts within 2 hours of first boot. Fail2ban is non-negotiable.

### Unattended Security Updates
- Installed via `sudo apt install unattended-upgrades`
- Enabled via `sudo dpkg-reconfigure -plow unattended-upgrades` → selected Yes
- Runs automatically in background — security patches apply without manual intervention

### Secure Boot
- **Secure Boot is OFF** — required for proprietary NVIDIA drivers to load kernel modules (nvidia.ko, nvidia-modeset.ko, etc.)
- This is expected and intentional — do not re-enable

---

## Phase 2 — NVIDIA Drivers + CUDA
**Status: ✅ COMPLETE**

### Driver Installation
| Detail | Value |
|---|---|
| Driver Package | `nvidia-driver-595` (proprietary, non-open) |
| Driver Version | 595.58.03 |
| CUDA Runtime Version (nvidia-smi) | 13.2 |
| Removed Package | `nvidia-driver-595-open` (was previously installed, removed) |

DKMS built all required kernel modules on install:
- `nvidia.ko`
- `nvidia-modeset.ko`
- `nvidia-drm.ko`
- `nvidia-uvm.ko`
- `nvidia-peermem.ko`

Reboot was required after install. First successful GPU boot confirmed after the PCIe cable fix.

### nvidia-smi Confirmed Output
```
Driver Version: 595.58.03
CUDA Version: 13.2
GPU: NVIDIA GeForce RTX 3090
VRAM: 24576 MiB
Temp (idle): 31°C
Power Cap: 350W
Running Processes: None (clean)
```

### CUDA Toolkit
| Detail | Value |
|---|---|
| Package | `cuda-toolkit-12-8` |
| nvcc Version | CUDA 12.8, V12.8.93 |
| Repo Method | NVIDIA CUDA keyring: `cuda-keyring_1.1-1_all.deb` |

Environment variables added to `~/.bashrc`:
```bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```
Verified with `nvcc --version` → CUDA 12.8, V12.8.93.

> **Note:** nvidia-smi reports CUDA 13.2 (max supported by the driver). nvcc reports CUDA 12.8 (the installed toolkit). This discrepancy is normal — use 12.8 for all toolkit-dependent builds.

### ⚠️ CUDA 13.2 Gibberish Bug — KNOWN ISSUE
A confirmed bug in CUDA 13.2 produces gibberish outputs on several GGUF quants — notably Qwen3.6 and IQ3_S/IQ3_XXS/IQ2_M variants. This is a CUDA runtime bug, not a model or llama.cpp bug. Reference: `unslothai/unsloth#4849`.

**Mitigation:**
- Local builds compiled against CUDA 12.8 toolkit (`nvcc -V` = 12.8.93) link to the 12.8 runtime libraries and are unaffected.
- Pre-built binaries that link against CUDA 13.2 (some Docker images, some HF deployment containers) ARE affected.
- Unsloth provides pre-compiled CUDA 13.0 llama.cpp binaries at `unslothai/llama.cpp` releases (b8811+) that work on CUDA 13.2 systems via backwards compatibility.
- Unsloth Studio compiles against CUDA 13.0 and is a safe fallback.

**Required smoke test before deploying Qwen3.6:**
```bash
# After llama.cpp build, run a sanity prompt and confirm coherent output
./llama.cpp/build/bin/llama-cli -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  --jinja -ngl 99 -c 8192 -p "What is 2+2? Answer in one word." -n 32
# If output is gibberish or repeated tokens, your llama.cpp linked against 13.2 runtime — rebuild.
```

**Verify your Python inference venv is not on the broken 13.2 runtime:**
```bash
source ~/venv/inference/bin/activate
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA runtime (PyTorch): {torch.version.cuda}')
print(f'cuDNN: {torch.backends.cudnn.version()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'CUDA available: {torch.cuda.is_available()}')
"
# If CUDA runtime reports 12.x → safe.
# If it reports 13.2 → force-reinstall the cu128 wheel:
#   pip install --force-reinstall --index-url https://download.pytorch.org/whl/cu128 torch torchvision torchaudio
```

**Driver vs runtime vs toolkit — what to keep pinned:**
- Driver stays at 595.58.03 — supports up to CUDA 13.2 max, but that's a ceiling, not what's used.
- Toolkit stays at `cuda-toolkit-12-8` (nvcc 12.8.93). Do NOT install `cuda-toolkit-13-2`.
- Docker base images: pin `nvidia/cuda:12.8.x` tags explicitly. Never use `latest` — it will silently shift to 13.2 and break Qwen3.6 deployments.
- Pip wheels: any `vllm` / `torch` upgrade requires re-running the verify command above.

NVIDIA is reportedly fixing this in CUDA 13.3.

### CUDA 12.8 Pinning — APPLIED May 16, 2026

The advisory language above is necessary but not sufficient. A single stray `apt upgrade` could pull CUDA 13.x and silently break every Qwen3.6 inference call. Pinned the toolkit and all dependent libraries with `apt-mark hold`:

```bash
sudo apt-mark hold \
  cuda-toolkit-12-8 cuda-12-8 cuda-runtime-12-8 \
  cuda-cudart-12-8 cuda-cudart-dev-12-8 libcudart12 \
  libcublas-12-8 cuda-libraries-12-8 cuda-libraries-dev-12-8 \
  cuda-nvcc-12-8 cuda-compiler-12-8
```

Verify holds:
```bash
apt-mark showhold | grep cuda
# Expect at least 11 cuda-* lines
```

### Quarterly Verification SOP (add to operator calendar)

```bash
# 1. Holds still in effect
apt-mark showhold | grep -c cuda    # expect ≥ 11

# 2. llama.cpp still linked to 12.x runtime
ldd ~/llama.cpp/build/bin/llama-server | grep -E "cudart|cublas"
# Expect: libcudart.so.12, libcublas.so.12

# 3. nvcc still 12.8
nvcc --version | grep release
# Expect: release 12.8

# 4. Functional smoke test (the same Qwen3.6 coherence check from above)
~/llama.cpp/build/bin/llama-cli -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  --jinja -ngl 99 -c 8192 -p "What is 2+2? Answer in one word." -n 32
# Expect: "4" or similar. Gibberish = CUDA flipped despite holds — investigate.
```

### Unpinning Procedure (only when 13.3+ is widely available and proven)

Before any `apt-mark unhold`, verify llama.cpp + Python venv torch still link to a 12.x runtime. If anything flips to 13.x, rebuild against the new toolkit AND smoke-test Qwen3.6 output BEFORE committing.

---

## Phase 3 — Tailscale
**Status: ✅ COMPLETE**

### Installation
- Workstation: installed via official script → `curl -fsSL https://tailscale.com/install.sh | sh`
- MacBook: installed via Homebrew
- Both authenticated to the same Tailscale account
- Both devices confirmed visible in Tailscale admin panel

### Operator Config (avoid sudo requirement)
```bash
sudo tailscale set --operator=$USER
```
This allows `monarch` to run `tailscale` commands without sudo.

### MacBook Settings
- Launch at Login: enabled
- Direct interface: `192.168.12.224:41641`

### Tailscale Funnel ✅
Funnel exposes n8n to the public internet with HTTPS — used for webhooks from external services.

```bash
tailscale funnel --bg 5678
```

| Detail | Value |
|---|---|
| Public HTTPS URL | `https://monarch-b650i-lightning-wifi.tail89cb86.ts.net` |
| Proxies to | `http://127.0.0.1:5678` (n8n) |
| Persistence | Survives reboots (background flag) |
| UFW changes needed | None — Tailscale handles its own interface |
| Disable command | `tailscale funnel --https=443 off` |

> Funnel was enabled via the Tailscale admin console browser prompt — required a one-time toggle in the admin panel before the CLI command would accept it.

---

## Phase 4 — Docker + NVIDIA Container Toolkit
**Status: ✅ COMPLETE**

### Docker Engine
| Detail | Value |
|---|---|
| Package | `docker.io` |
| Docker Compose Version | v5.1.3 (plugin) |
| Official Docker repo | Added for Compose plugin |

`monarch` added to docker group (no sudo required for docker commands):
```bash
sudo usermod -aG docker monarch
```
(Requires logout/login or new shell to take effect.)

### NVIDIA Container Toolkit
| Detail | Value |
|---|---|
| Package | `nvidia-container-toolkit 1.19.0-1` |
| Repo method | Added via GPG keyring |
| Runtime config | `sudo nvidia-ctk runtime configure --runtime=docker` |
| Config file | `/etc/docker/daemon.json` |

Docker was restarted after runtime config was written.

### GPU Smoke Test — ✅ PASSED
```bash
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu24.04 nvidia-smi
```
Result: RTX 3090 visible inside container, 24576 MiB VRAM, no running processes (clean state confirmed).

---

## Phase 5 — n8n + Postgres
**Status: ✅ COMPLETE**

### Docker Compose File
**Location:** `~/n8n/docker-compose.yml`

> **Env file:** Secrets are sourced from `~/.config/inference/api_keys.env` (chmod 600). Load with `set -a; source ~/.config/inference/api_keys.env; set +a` before running `docker compose up -d`, or add to `~/.bashrc`.

```yaml
services:
  postgres:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_HOST=0.0.0.0
      - N8N_SECURE_COOKIE=false
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

volumes:
  postgres_data:
  n8n_data:
```

> ✅ **W2.1 — POSTGRES_PASSWORD rotated May 14, 2026.** Generated via `openssl rand -base64 32`, stored in `~/.config/inference/api_keys.env`. Postgres role password updated via `ALTER USER`. n8n healthy confirmed via `/healthz`. Old hardcoded `n8npassword` gone from compose.  
> ✅ **W1.1 — N8N_ENCRYPTION_KEY verified May 14, 2026.** Present in `~/n8n/docker-compose.yml`; backed up in 1Password Private vault.

### Status Details
| Detail | Value |
|---|---|
| Running Containers | `n8n-postgres-1`, `n8n-n8n-1` |
| Postgres Tables | 79 (full n8n schema initialized — confirmed) |
| Postgres Image | postgres:16 |
| n8n Image | n8nio/n8n (latest) |
| Restart Policy | `always` (both containers — survive reboots) |
| Internal Access | `http://100.101.244.6:5678` |
| Public Webhook Access | `https://monarch-b650i-lightning-wifi.tail89cb86.ts.net` |
| License | Free license key activated |
| Named Volumes | `postgres_data`, `n8n_data` |

### ⚠️ Technical Debt — N8N_SECURE_COOKIE
`N8N_SECURE_COOKIE=false` is set as a **temporary workaround**. This must be flipped to `true` once HTTPS is properly configured end-to-end with the React PWA. Leaving it as false is acceptable during development but must not remain in production.

---

## Phase 6 — UFW Firewall
**Status: ✅ COMPLETE**

### Policy
- Default incoming: **deny**
- Default outgoing: **allow**
- Default routed: **deny**

### Rules Applied
```bash
sudo ufw allow in on tailscale0 to any port 22    # SSH via Tailscale (primary)
sudo ufw allow in on tailscale0 to any port 5678  # n8n via Tailscale only
sudo ufw allow in on wlp8s0 to any port 22        # SSH via local WiFi (emergency fallback)
```

### Final UFW Status
```
Status: active
Default: deny (incoming), allow (outgoing), deny (routed)

To                         Action      From
--                         ------      ----
22 on tailscale0           ALLOW IN    Anywhere
5678 on tailscale0         ALLOW IN    Anywhere
22 on wlp8s0               ALLOW IN    Anywhere
22 (v6) on tailscale0      ALLOW IN    Anywhere (v6)
5678 (v6) on tailscale0    ALLOW IN    Anywhere (v6)
22 (v6) on wlp8s0          ALLOW IN    Anywhere (v6)
```

### Key Security Notes
- n8n (port 5678) is **only accessible via Tailscale** — not exposed to open internet directly
- Tailscale Funnel (public HTTPS) is handled by Tailscale's own infrastructure and does not require a UFW rule
- SSH via local WiFi (`wlp8s0`) is retained as an emergency fallback only — primary SSH access is always over Tailscale
- SSH confirmed working over Tailscale after UFW was enabled

---

## Phase 7 — Inference Stack
**Status: ⚠️ PARTIALLY COMPLETE — Blocked on file transfers (no models on machine yet)**

### Python Virtual Environment
| Detail | Value |
|---|---|
| Location | `~/venv/inference` |
| Python Version | 3.12 |
| Activate Command | `source ~/venv/inference/bin/activate` |

### vLLM
- Installed via `pip install vllm`
- CUDA confirmed: `torch.cuda.is_available() = True`
- GPU confirmed: NVIDIA GeForce RTX 3090
- **Status:** Installed and validated. Awaiting models.

### llama-cpp-python
| Detail | Value |
|---|---|
| Version | 0.3.22 |
| Install Command | `CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python` |
| GPU Offload | Confirmed: `llama_supports_gpu_offload() = True` |
| VRAM Detected | 24117 MiB |

- **Status:** Installed and validated. Awaiting models.
- **Role:** CPU/embedded utility model server (Phi-4-mini, Llama 3.2 3B, Qwen3 0.6B). Python library, not a server process.

### llama.cpp (separate from llama-cpp-python)
| Detail | Value |
|---|---|
| Build Method | `cmake llama.cpp -B llama.cpp/build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DLLAMA_CURL=ON` |
| CUDA Linkage | Compiled against CUDA 12.8 toolkit (avoids 13.2 runtime bug) |
| Server Binary | `~/llama.cpp/build/bin/llama-server` |
| CLI Binary | `~/llama.cpp/build/bin/llama-cli` |

- **Status:** Build sequence documented in Phase 9. Build completion + smoke test pending.
- **Role:** Server process for MoE-offload large models (Qwen3-Coder-Next 80B-A3B). Required because vLLM does not natively support the `-ot` expert-offload-to-CPU pattern that makes the 80B model fit on 24+96GB hardware.

### LiteLLM
- Installed via `pip install litellm`
- Import confirmed working
- **Status:** Installed. Router config not yet written — pending model availability.

### tmux
- Installed via `sudo apt install tmux`
- Primary session name: `inference`
- Attach command: `tmux attach -t inference`
- All long-running inference processes should live inside this session

### What's Missing
1. **No models on the machine yet** — rsync file transfers are still in progress (models live in `~/projects/`)
2. **LiteLLM router config** — unified API endpoint config pointing at vLLM backends, to be written once models load successfully
3. **End-to-end vLLM model test** — smoke test a single model load, VRAM allocation, and a sample completion

### Planned Full Inference Architecture (not yet deployed)
| Component | Role |
|---|---|
| vLLM | Primary inference engine (multi-LoRA, PagedAttention) |
| LiteLLM | Router — unified API endpoint across all vLLM backends |
| llama-cpp-python | Tiny/lightweight agent models (CPU or partial GPU offload) |
| Ray | Multi-host inference if/when scale requires it |
| Unsloth QLoRA | Fine-tuning pipeline |
| W&B | Fine-tuning tracking |
| LLaMA-Factory | Fine-tuning orchestration |

---

## Phase 8 — File Transfers
**Status: ⚠️ IN PROGRESS**

### Transfer Commands (run from MacBook terminal)
```bash
# html-guides
rsync -az --progress '/Users/trentdunkak/Desktop/html guides/' monarch@100.101.244.6:~/html-guides/

# projects
rsync -az --progress /Users/trentdunkak/Desktop/projects/ monarch@100.101.244.6:~/projects/
```

### Details
| Detail | Value |
|---|---|
| Transfer Method | rsync over Tailscale |
| Total Files | ~130,000 across both directories |
| html-guides Destination | `~/html-guides/` |
| projects Destination | `~/projects/` |
| Previous html-guides Transfer | Wiped and restarted clean (`rm -rf ~/html\ guides` before re-run) |
| Resumable | Yes — re-run the same rsync command if dropped, it will pick up where it left off |

### macOS rsync Compatibility Note
macOS ships a very old version of rsync. `--info=progress2` is **not supported**. Use `--progress` only.

---

## Standard Operating Procedure

| Task | Command |
|---|---|
| SSH into workstation | `ssh monarch@100.101.244.6` |
| Attach to inference tmux session | `tmux attach -t inference` |
| Create new tmux session | `tmux new -s <name>` |
| List tmux sessions | `tmux ls` |
| Start n8n stack | `cd ~/n8n && docker compose up -d` |
| Stop n8n stack | `cd ~/n8n && docker compose down` |
| Check running containers | `docker ps` |
| Check container logs | `docker logs n8n-n8n-1` or `docker logs n8n-postgres-1` |
| Activate inference venv | `source ~/venv/inference/bin/activate` |
| Check GPU status | `nvidia-smi` |
| Resume file transfer (html-guides) | `rsync -az --progress '/Users/trentdunkak/Desktop/html guides/' monarch@100.101.244.6:~/html-guides/` |
| Resume file transfer (projects) | `rsync -az --progress /Users/trentdunkak/Desktop/projects/ monarch@100.101.244.6:~/projects/` |
| Disable Tailscale Funnel | `tailscale funnel --https=443 off` |
| Re-enable Tailscale Funnel | `tailscale funnel --bg 5678` |
| **Start inference stack (vLLM #1+#2 + LiteLLM)** | `~/bin/inference-up` |
| **Stop inference stack** | `~/bin/inference-down` |
| **Bring up Qwen3-Coder-Next deep-think (llama.cpp)** | `~/bin/qwen-coder-deep-up` |
| **Tear down Qwen3-Coder-Next** | `~/bin/qwen-coder-deep-down` |
| **Verify CUDA runtime safety (Phase 2)** | `python -c "import torch; print(f'CUDA: {torch.version.cuda}')"` — must report 12.x |
| **Verify LiteLLM end-to-end (Checkpoint 4)** | `curl http://127.0.0.1:4000/v1/chat/completions -H "Authorization: Bearer $LITELLM_MASTER_KEY" -H "Content-Type: application/json" -d '{"model":"qwen3.6-consultancy","messages":[{"role":"user","content":"OK?"}],"max_tokens":5}'` |
| **Tail vLLM #1 logs** | `tmux capture-pane -t inference:vllm1 -p \| tail -50` |
| **Tail LiteLLM logs** | `tmux capture-pane -t inference:litellm -p \| tail -50` |
| **Launch Claude Code (personal, Pro #1)** | `claude-personal` |
| **Launch Claude Code (client, Pro #2)** | `claude-client` |
| **Launch OpenCode interactive against local model** | `opencode --model litellm/qwen3.6-exploratory` |
| **Launch Qwen Code CLI (deep-think, requires llama.cpp up)** | `qwen-code` |
| **Start Jarvis service (monarch)** | `tmux new-window -t inference -n jarvis 'cd ~/services/jarvis && source ~/venv/inference/bin/activate && python app.py'` |
| **Start Read-only API (monarch)** | `tmux new-window -t inference -n read-api 'cd ~/services/read-api && source ~/venv/inference/bin/activate && python app.py'` |
| **Start Command Center PWA (monarch)** | `tmux new-window -t inference -n pwa 'npx serve ~/projects/command-center/dist -p 3000 -s'` |
| **Check MacBook wake-word daemon** | `launchctl list \| grep jarvis` (run on MacBook) |
| **Restart MacBook wake-word daemon** | `launchctl kickstart -k gui/$(id -u)/com.taolen.jarvis-listener` (run on MacBook) |
| **Tail Jarvis logs** | `tmux capture-pane -t inference:jarvis -p \| tail -50` |
| **Access Command Center** | `http://100.101.244.6:3000` (Tailscale only) |
| **Monthly — Postgres restore drill** | `~/bin/restore-drill` — verify output shows PASS and 79 tables |
| **Monthly — Tailscale Funnel scope check** | `curl -I https://monarch-b650i-lightning-wifi.tail89cb86.ts.net/` — root must return 404, not 200 |

> **All workstation commands are run via SSH from MacBook terminal. The machine runs 24/7 headless — no monitor required.**

---

## Remaining Items

| # | Item | Blocked By | Priority |
|---|---|---|---|
| 1 | File transfer completion (html-guides + projects) | rsync in progress | 🔴 High — everything else unblocks from this |
| 2 | End-to-end vLLM model test | File transfers | 🔴 High |
| 3 | LiteLLM router config | vLLM model test | 🔴 High |
| 4 | `N8N_SECURE_COOKIE=false` → `true` | Command Center PWA go-live (Phase 19) — see §19.5 for Option A vs B | 🟡 Medium |
| 5 | Command Center PWA build + deploy (Tailscale, port 3000) — design complete (Phase 19) | Read-only data API (port 4400) live | 🟡 Medium |
| 6 | Fine-tuning environment test (Unsloth QLoRA) | Models + projects on machine | 🟡 Medium |
| 7 | Ray multi-host config | Not yet needed | 🟢 Low |

---

## Open Risk Items & Architecture Decisions

This section captures items that need answers, decisions, or follow-up work before the workstation is genuinely production-ready. Grouped by severity. None of these block the current development workflow, but several represent real risk if left unaddressed.

### 🔴 Critical — Real Risk if Unaddressed

#### 1. n8n Encryption Key Backup
n8n auto-generates an encryption key on first run that encrypts all stored credentials in Postgres. **If this key is lost, every credential in n8n becomes unrecoverable** — even with the `postgres_data` volume intact.

| Detail | Value |
|---|---|
| Key Location | `n8n_data` volume → `/home/node/.n8n/config` |
| Retrieval | `docker exec n8n-n8n-1 cat /home/node/.n8n/config` |
| Backup Target | 1Password (alongside SSH ed25519 key) |

**Action:** Export the key and store in 1Password Private vault before adding any credentials to n8n workflows.

**Status:** ❌ Not yet backed up.

---

#### 2. Public Funnel Exposure of n8n
The Tailscale Funnel URL `https://monarch-b650i-lightning-wifi.tail89cb86.ts.net` proxies straight to the n8n login screen. Anyone on the public internet who guesses or discovers this hostname can hit the n8n login page and brute-force it. n8n's built-in basic auth is **not currently enabled** in the docker-compose file.

**Two viable strategies:**

| Option | Approach |
|---|---|
| A. Webhook-only Funnel | Restrict Funnel to only expose webhook paths (`/webhook/*`), leaving the n8n UI behind Tailscale-only |
| B. Basic Auth in front | Enable `N8N_BASIC_AUTH_ACTIVE=true` + `N8N_BASIC_AUTH_USER` + `N8N_BASIC_AUTH_PASSWORD` env vars in compose |

Option A is more secure (smaller attack surface). Option B is simpler but means a basic-auth password is the only thing between the public internet and full n8n access.

**Decision needed:** Which approach? **Status:** ❌ Currently fully exposed with no auth layer beyond n8n's own login.

---

#### 3. Postgres Backup Strategy
The `postgres_data` Docker volume holds every n8n workflow, execution history, encrypted credential, and (eventually) every pipeline result. **No backup plan currently exists.** Volume corruption, accidental `docker compose down -v`, or disk failure would wipe everything.

**Minimum viable backup:**
```bash
# Nightly cron — dump to ~/backups/ with date stamp
0 3 * * * docker exec n8n-postgres-1 pg_dump -U n8n n8n | gzip > ~/backups/n8n-$(date +\%Y\%m\%d).sql.gz
```

**Better:** rotate to external storage (rsync to MacBook, push to S3/B2, etc.).

**Status:** ❌ Not implemented.

---

### 🟡 Architecture Decisions Not Yet Documented

#### 4. Model Storage Location
Model weights are large (Qwen3 32B at FP16 ≈ 60GB; even AWQ 4-bit ≈ 18GB). Currently models are presumed to land somewhere in `~/projects/` via rsync, but this conflates code and weights.

**Recommended:** Dedicated `~/models/` path with subdirs per model family. Affects:
- vLLM `--model` paths
- Disk-usage monitoring later
- Backup scope decisions (probably skip — re-downloadable from HF)

**Decision needed:** `~/models/` separate path, or live inside `~/projects/<subdir>/`? **Status:** ❌ Undecided.

---

#### 5. VRAM + RAM Math for May 2026 Stack
The 24GB RTX 3090 + 96GB DDR5 give a combined ~115–120GB working envelope when MoE expert offload is used. The table below was originally v12's; v14 rewrites it to reflect the five-tier always-on architecture (see Phase 9 — Five-Tier Architecture).

**v14 five-tier VRAM accounting (the production layout):**

| Tier | Engine | Model | `-ngl` | Ctx | VRAM (alone) | Notes |
|---|---|---|---|---|---|---|
| **T1 interactive** | llama-server | Qwen3.6-27B UD-Q4_K_XL | 40 of 64 | 36K | **~12 GB measured** | LoRA-capable, `-np 1` (v16), measured baseline pending |
| **T2 pipeline** | llama-server | Qwen3.6-27B UD-Q4_K_XL | 20 of 64 | 16K | **~6.7 GB measured** | No LoRA (base synthesis), **5.4 tok/s measured** (22.9 in burst-mode) |
| **T3 content/batch** | llama-server | Qwen3.6-27B UD-Q4_K_XL | 0 (CPU) | 8K | **~0.5 GB** | CPU execution, LoRA via dispatcher, 3-8 tok/s |
| **T4 utility** | llama.cpp (v16: pivoted) | Phi-4-mini Q4_K_M GGUF | 99 | 16K | **~4.2 GB measured** | **206 tok/s gen** measured, -np 4 parallel slots, q8_0 KV |
| **T5 small seed** | llama-server | Qwen3-1.7B Q5_K_M | 0 (CPU) | 8K | **~0 GB** (RAM only) | Classifier seed, CPU only |
| **All five together** | — | — | — | — | **~19.9 GB** | ~4.1 GB VRAM free for KV spikes |

> **mmap weight sharing (load-bearing).** T1, T2, and T3 all load the *same* `Qwen3.6-27B UD-Q4_K_XL` GGUF file. Because llama-server uses `mmap` by default, the Linux page cache shares the ~17 GB of weight pages across all three processes — physical RAM cost for weights is paid once, not three times. This is the single architectural reason five concurrent tiers fit on monarch.

**v14 RAM accounting (newly explicit):**

| Consumer | RAM | Notes |
|---|---|---|
| Qwen3.6-27B mmap'd weights | ~17 GB | Shared across T1, T2, T3 — paid once |
| T1 KV cache + activations | ~3 GB | 32K ctx, q8_0 KV, -np 2 |
| T2 KV cache + activations | ~3 GB | 16K ctx, plus 42 CPU-resident layers' activation buffers |
| T3 KV cache + activations | ~4 GB | 8K ctx, all 64 layers on CPU |
| T4 llama.cpp Phi-4-mini | ~0.5 GB | Q4_K_M GGUF, full GPU offload (v16: pivoted from vLLM) |
| T5 Qwen3-1.7B Q5_K_M | ~2 GB | Full weights on CPU |
| Postgres + Docker + n8n + OS | ~12 GB | Phase 5 baseline |
| **Five-tier baseline total** | **~43 GB** | Leaves ~53 GB free on a 96 GB box |

**Per-model footprints (carried forward from v12 for reference):**

| Model | Q4 footprint | Fits where? | Speed expectation |
|---|---|---|---|
| Qwen3.6-27B (dense) | ~16.8 GB | See five-tier table above | T1: 30-40, T2: 12-18, T3: 3-8 tok/s |
| Qwen3.6-35B-A3B (MoE) | ~21 GB | Pure VRAM — not in five-tier baseline | Full speed (MoE 3B active, ~80–100 tok/s with `--cache-type-k q8_0`); deferred until needed |
| Qwen3-Coder-30B-A3B | ~17–18 GB | Pure VRAM | Full speed |
| GLM-4.7-Flash (30B-A3B) | ~22 GB | Pure VRAM | Full speed |
| Qwen3-Coder-Next 80B-A3B | ~46 GB total (Q4_K_XL) | Manual on-demand only (NDA-tagged work) | ~3–5 tok/s under MoE expert offload — too slow for routine use; see Appendix A |
| Gemma 4 12B / 26B-MoE / 31B-dense | 7–22 GB | Not in current stack | Full speed |
| Phi-4-mini, Llama 3.2 3B, Qwen3 0.6B/1.7B | 1–4 GB each | T4 (Phi-4) on GPU, T5 (Qwen3-1.7B) on CPU; others spawnable inline | 30–80 tok/s on CPU |
| GLM-4.7 full (~358B MoE) | ~135 GB UD-Q2_K_XL | Won't fit | API only |
| DeepSeek V4 Flash (284B-A13B) | ~158 GB | Won't fit | API only — primary cloud fallback |
| Kimi K2.6 (1T) | ~240 GB at 1.8-bit | Won't fit | API only — 1M context fallback |

**Key architectural decisions this enables:**

1. **mmap weight sharing across three Qwen3.6-27B instances.** Same GGUF file → same inode → Linux page cache shares the weight pages. Three concurrent llama-server processes for ~17 GB total RAM weight cost, not 51 GB. This is what makes five concurrent tiers feasible on 24 GB VRAM and 96 GB RAM.

2. **Session-level LoRA swap on T1 via llama.cpp `/lora-adapters` endpoint** — replaces v12's broken vLLM multi-LoRA pattern. T3 uses a wrapper service (LoRA dispatcher) on top of the same endpoint pattern, scoped to one adapter per n8n execution.

3. **MoE offload pattern for 80B-class** (Qwen3-Coder-Next) preserved as a manual on-demand capability. v14 retires it from automated use — see Appendix A entry.

4. **Co-resident utility workers.** T4 (Phi-4-mini on GPU via llama.cpp [v16: pivoted from vLLM], measured 206 tok/s gen for high-frequency classifier calls) + T5 (Qwen3-1.7B on CPU, persistent classifier seed). Additional small CPU workers can be spawned per-n8n-execution as needed.

**Decision now resolved (v14):** v12 settled on AWQ + vLLM multi-LoRA — v13 corrected this to llama.cpp + UD-Q4_K_XL after the audit found vLLM doesn't support LoRA on Qwen3-Next hybrid architecture. v14 builds on v13 by deploying three Qwen3.6-27B instances at different `-ngl` ratios with mmap weight sharing, plus vLLM Phi-4-mini + a CPU small-model seed, producing five always-on tiers. **Status:** ✅ Architecture finalized and operational deliverables shipped (see Phase 9).

---

#### 6. LiteLLM Configuration
LiteLLM is installed and the v14 router config is written. Documented in full in Phase 9 — LiteLLM Config.

**Resolved (v14):**
- Bind port: 4000 (Tailscale-accessible at `0.0.0.0:4000` — the only port external clients hit).
- n8n routing: Docker bridge network reaches LiteLLM via Tailscale IP `100.101.244.6:4000` or `host.docker.internal:4000`.
- Auth: master key sourced from `~/.config/inference/api_keys.env` (`LITELLM_MASTER_KEY`).
- Routing rules: explicit per-tier (qwen3.6-consultancy/design/exploratory → T1:8080; qwen3.6-pipeline → T2:8083; qwen3.6-content → T3:8084; phi4-mini → T4:8002; qwen3-small → T5:8085). Fallback chains route overflow to DeepSeek V4 Flash / Pro / Kimi K2.6.

**Status:** ✅ Config complete; pending first inference-up run on monarch for end-to-end validation.

---

### 🟢 Operational Items Not Yet Addressed

#### 7. UPS / Power Protection
The workstation runs 24/7 with a 3090 pulling up to 350W. A power blip during a Postgres write can corrupt the database. No UPS currently in place.

**Recommended:** APC/CyberPower 1000VA+ unit + `nut` (Network UPS Tools) for graceful shutdown on power loss.

**Status:** ❌ No UPS.

---

#### 8. Monitoring & Observability
No system in place to track GPU temps, VRAM usage, disk space, or container health over time. Currently running blind — only ad-hoc `nvidia-smi` and `docker ps`.

**Tiered options:**

| Tier | Tools | Effort |
|---|---|---|
| Quick | `nvtop`, `btop`, `ctop` | Minutes |
| Mid | `glances` + web UI | An hour |
| Full | Prometheus + Grafana + nvidia-dcgm-exporter + cadvisor | A day |

**Decision needed:** Which tier, and when? **Status:** ❌ Nothing deployed.

---

#### 9. Swap Configuration
With 96GB RAM, swap is rarely hit, but if a vLLM model load OOMs the behavior matters. Default Ubuntu 24.04 swap is typically a small swapfile or none.

**Action:** Run `swapon --show` and `free -h` to verify. Recommended: 8-16GB swapfile minimum.

**Status:** ❌ Not verified.

---

#### 10. Disk Space Tracking
4TB NVMe sounds vast until: 130k project files + 5-10 model weights (each 15-60GB) + Docker volumes + container images + n8n execution history accumulate.

**Recommended:** `ncdu` for ad-hoc inventory; longer-term, disk-space metrics in monitoring stack.

**Status:** ⚪ Punt for now — revisit when first model weights land.

---

### ⚪ Items to Confirm or Correct

| # | Item | Current Doc Says | Action Needed |
|---|---|---|---|
| 11 | CPU brand | "AMD Ryzen 9 9900X" | Confirm — no Intel 9900X exists currently, so almost certainly correct, but verify |
| 12 | File transfer status | "in progress" | If rsyncs are done, flip to ✅ and unblock Phase 7 inference test |
| 13 | Docker group activation | `monarch` added to docker group | Verify with `groups monarch` after logout/login or `newgrp docker` — confirm `docker ps` works without sudo |
| 14 | UFW persistence | Active | Verify `sudo systemctl is-enabled ufw` returns `enabled` — UFW must start on boot |

---

### Risk Item Summary Table

| # | Item | Severity | Status |
|---|---|---|---|
| 1 | n8n encryption key backup | 🔴 Critical | ✅ Verified May 14, 2026 — key in 1Password, volume, and api_keys.env; compose uses ${N8N_ENCRYPTION_KEY} |
| 2 | Public Funnel exposure of n8n | 🔴 Critical | ✅ Verified May 14, 2026 |
| 3 | Postgres backup strategy | 🔴 Critical | ✅ Verified May 14, 2026 |
| 4 | Model storage location decision | 🟡 Architecture | ⚠️ Convention adopted (`~/models/` via `-hf` cache; LoRAs at `~/loras/`) — pending first model download to monarch to verify |
| 5 | VRAM math + quantization strategy | 🟡 Architecture | ✅ v14 — five-tier architecture with mmap weight sharing finalized |
| 6 | LiteLLM router config decisions | 🟡 Architecture | ✅ v14 — config written, pending first inference-up run |
| 7 | UPS / power protection | 🟢 Operational | ❌ |
| 8 | Monitoring & observability | 🟢 Operational | ⚠️ Foundation laid via validation gate + LoRA dispatcher telemetry (Postgres-backed); standalone GPU/system monitoring still ❌ |
| 9 | Swap verification | 🟢 Operational | ❌ |
| 10 | Disk space tracking | 🟢 Operational | ⚪ Punt |
| 11 | CPU brand confirmation | ⚪ Verify | ⏳ |
| 12 | File transfer status update | ⚪ Verify | ⏳ |
| 13 | Docker group activation verify | ⚪ Verify | ⏳ |
| 14 | UFW boot persistence verify | ⚪ Verify | ⏳ |

---

## Full Planned Stack Reference

Included here as a reference for the complete intended architecture — items below that are not yet deployed are noted.

### Agent Stacks (6 total) — May 2026 revised

Each stack lists the local primary (GPU-resident or RAM-offload), local supporting workers (CPU or co-resident), and the cloud fill tier (which Claude Pro account, or which API).

| Stack | Local Primary | Local Supporting | Cloud Fill |
|---|---|---|---|
| Consultancy | Qwen3.6-27B + qwen3.6-consultancy LoRA | Gemma 4 12B (utility), Phi-4-mini (classify) | Claude Pro #2 — client deliverables |
| Exploratory Coding | Qwen3-Coder-30B-A3B (fast tier) + Qwen3-Coder-Next 80B-A3B (deep-think tier, MoE offload) | Qwen3.6-27B as second opinion | Claude Pro #1 — architecture, multi-file refactors |
| Design | Qwen3.6-27B + qwen3.6-design LoRA (vision support) | Gemma 4 12B | Claude Pro #2 — client copy, brand voice |
| Content | Qwen3.6-35B-A3B + content LoRA (speed tier) | Phi-4-mini, Qwen3 1.7B | Claude Pro #1 — weekly batch QA, brand-voice synthesis |
| Leads | Qwen3.6-35B-A3B + leads LoRA | Phi-4-mini (filter), Qwen3 0.6B (triage) | Rare — leads work shouldn't burn Claude tokens |
| Financial | Qwen3.6-35B-A3B (orchestrator) + Qwen3-Coder-30B-A3B (notebooks) | Phi-4-mini, Llama 3.2 3B (parallel sub-tasks); MiroFish + OASIS unchanged | DeepSeek V4 Flash API (cheap reasoning + 1M ctx); Claude Pro #1 only for sanity checks |

**LoRA targets (revised):** `qwen3.6-consultancy`, `qwen3.6-design`, `qwen3.6-exploratory-coding` (all on Qwen3.6-27B dense), `qwen3.6-content`, `qwen3.6-leads` (both on Qwen3.6-35B-A3B). MoE bases generally produce noisier LoRA gradients than dense bases — content/leads accept this for the speed gain; the three high-value LoRAs target dense Qwen3.6-27B.

**Two-Pro split rationale:** Pro #1 powers Claude Code for personal/exploratory work and gates personal financial pipeline experiments. Pro #2 is reserved for client-facing consultancy deliverables — keeps client context isolated from personal experiments and prevents cross-contamination of context windows.

### Harness Layer — finalized

The harness is the agentic loop wrapping the model: how it parses tool calls, manages context, dispatches subagents, and integrates with workflows. Different tiers need different harnesses — model strength and use context dictate the right shape.

| Tier | Harness | Triggered by | Models | Role |
|---|---|---|---|---|
| Cloud premium | Claude Code | Manual (terminal) | Claude Opus 4.7 (Pro #1 personal / Pro #2 client) | High-stakes reasoning, client deliverables, multi-file refactors, "I'm stuck" |
| Local agentic interactive | OpenCode TUI | Manual (terminal) | Qwen3.6-27B + LoRAs, Qwen3-Coder-30B-A3B | Sit-down delegation to local models with full agentic loop |
| Local agentic headless | OpenCode `serve` HTTP API | n8n webhooks, scheduled triggers, Tailscale Funnel | Same as interactive, routed via LiteLLM | Triggered/repeatable agentic workflows |
| Local deep-think specialist | Qwen Code CLI | Manual (terminal) for hard problems | Qwen3-Coder-Next 80B-A3B (MoE offload via llama.cpp) | "Ask the slow expert" — privacy-first hard problem solving |
| Local lightweight | n8n + LiteLLM direct API | n8n triggers, schedules, Funnel webhooks | Qwen3.6-35B-A3B, Phi-4-mini, Llama 3.2 3B | Non-agentic structured generation (classify, score, summarize, extract) |

**Why OpenCode for local agentic.** OpenCode is the closest 1:1 to Claude Code in design philosophy. AGENTS.md as project context (now a Linux Foundation AAIF standard alongside MCP), `.opencode/skills/` with progressive-disclosure Markdown skills, `.opencode/agents/` for primary and subagents as Markdown files with frontmatter, `.opencode/commands/` for slash commands with bash injection (`!command`) and file include (`@filename`) syntax, `opencode.jsonc` for provider/permission config. Bash tool with allow/ask/deny permission scoping. Sub-agent dispatch via Task tool with hidden agents for programmatic-only invocation. Headless `--format json` mode and `opencode serve` HTTP API for n8n integration.

**Why not Cline.** VS Code extension with per-action approval gates is optimized for developers writing code by hand. The use case here is delegation to local models with reviewable artifacts at the end, not granular hand-on-the-wheel control.

**Why not Goose for primary.** Goose has an unresolved tool-calling bug with Qwen3-Coder via Ollama where >5-6 tools causes XML-fallback rather than proper JSON tool calls. Reference: `block/goose#6883`. Pairing Goose with Claude Pro avoids this, but if Claude is the model, Claude Code is the better-fitting harness anyway. Goose remains viable for ACP-bridged workflows (Zed, JetBrains) if those become relevant later.

**File system implication.** AGENTS.md and CLAUDE.md can be the same file via symlink, and skills/agents/commands directories can serve both Claude Code and OpenCode. This means one set of project context investment runs against either harness depending on which model is addressing the task.

### Content Tools

| Category | Tools |
|---|---|
| Image | Nano Banana Pro + Flux 1.1 Pro / Replicate |
| Video | Higgsfield Soul + Diffuse, Veo 3.1, Kling 3.0, WAN 2.6 (self-hosted) |
| Voice | Chatterbox (self-hosted) + Fish Audio S1 |
| Music | Udio |
| Lip-sync | Pika 2.0 |
| Editing | HeyGen, Descript, Opus Clip |
| Cut (removed) | MusicGen (CC-BY-NC-4.0 incompatible with monetized YouTube), Suno v4 |

### Consultancy Tools (client-facing, deploy into client environments — never Trent's hardware)

| Tool | Purpose |
|---|---|
| Manus AI | General AI automation |
| Apify | Web scraping + data pipelines |
| Chatbase | Client chatbot deployment |
| v0 | Rapid UI prototyping |
| Softr | No-code client portals |

### Inference Infrastructure (full target state)

| Component | Detail |
|---|---|
| vLLM | Multi-LoRA, PagedAttention — primary inference engine |
| LiteLLM | Router — unified API endpoint |
| llama-cpp-python | Tiny/lightweight agents (CPU or partial GPU) |
| Ray | Multi-host scaling (future) |
| Unsloth QLoRA | Fine-tuning |
| W&B | Fine-tuning experiment tracking |
| LLaMA-Factory | Fine-tuning orchestration |

### Orchestration + Automation

| Component | Detail |
|---|---|
| n8n | Workflow engine (running, 79 tables initialized) |
| Postgres 16 | Central data store for n8n + all pipeline telemetry |
| **Jarvis** | **Always-on voice manager: wake-word on MacBook (launchd), STT/TTS/reasoning on monarch (port 4300). Morning briefings, anomaly surfacing, system-state queries.** |
| **Command Center PWA** | **React PWA on port 3000 (Tailscale-only). Unified dashboard, real-time notifications via Jarvis WebSocket, deep links to all tools.** |
| **Read-only data API** | **FastAPI on port 4400 (Tailscale). PWA's only data source — proxies Postgres telemetry, n8n API, and inference-status. No write path.** |
| Tailscale Funnel | Public HTTPS webhook exposure for n8n (`/webhook/` only) |
| ntfy.sh | Push notifications to mobile — routed through Jarvis `/notify` |
| Nodera | Emergency mobile n8n editing only (rare) |

### Project Portfolio

| Project | Type | Status |
|---|---|---|
| AI Consulting | Primary income | Active — infrastructure scaling |
| Instagram | Lead-gen + affiliate hub | Active |
| Financial Pipeline | Personal (Bayesian + Monte Carlo → n8n auto-trade post paper-test) | In development |
| Baseball Pipeline | Personal (MiroFish stress testing) | In development |
| YouTube Ambience | Passive income (~5min/video, largely automated) | Active |
| News Pipeline | Personal infrastructure (daily intelligence brief via hierarchical LLM synthesis) | Phase 1+2 complete. Phase 3 pivoted to hybrid T2+Cowork; Stage 2 (local T2 sector synthesis) validated May 17, 2026; Stages 3-5 (Drive sync + Cowork compilation + pickup) next. |

---

## Model Stack May 2026 — Selection Rationale

This section captures *why* the v5 stack looks the way it does, so future revisions can argue against it from the same baseline.

### What's runnable on 24 GB VRAM + 96 GB DDR5

The hardware envelope is roughly 115–120 GB combined working memory. Three runnability tiers result:

1. **Pure-VRAM tier (sub-24 GB Q4):** Qwen3.6-27B dense, Qwen3.6-35B-A3B, Qwen3-Coder-30B-A3B, GLM-4.7-Flash, Gemma 4 (up to 26B-MoE). All run at full GPU speed.
2. **MoE-offload tier (40–90 GB total Q4):** Qwen3-Coder-Next 80B-A3B (~46 GB), Qwen3.5-122B-A10B (~60–70 GB). Active path on GPU, experts in RAM. Speed degradation is bounded because only ~3B params are touched per token.
3. **Out of reach (160 GB+):** DeepSeek V4 Flash, GLM-4.7 full, Kimi K2.6, DeepSeek V4 Pro. API-only.

### Why Qwen3.6-27B is the spine of three stacks

- **Dense architecture** = cleaner LoRA training gradients than MoE. Three independent LoRAs (consultancy/design/exploratory) trained on the same base produce reliable role separation.
- **Native vision** = Design stack handles client mood-boards, screenshot review, and multimodal client briefs without a separate vision model. Use `--no-mmproj` at serve time to save ~0.9 GB VRAM unless vision is explicitly needed. *(v16 correction: v15 said `--language-model-only`; that flag does not exist in llama.cpp.)*
- **llama.cpp session-level LoRA swap on Tier 1, dispatcher-managed swap on Tier 3.** v12 originally proposed vLLM multi-LoRA hot-swap; v13 corrected this because Qwen3.6 is Qwen3-Next hybrid (Gated DeltaNet + softmax + MTP head) and vLLM's `SupportsLoRA` mixin does not cover this architecture. llama.cpp handles GGUF natively and provides a `/lora-adapters` REST endpoint for adapter swap. v14 deploys the same GGUF across three concurrent llama-server tiers (T1 interactive, T2 pipeline, T3 batch) with mmap weight sharing — ~17 GB of weight pages paid once across all three.
- **Three deployment tiers off one model file (v14):**
  - **T1 interactive** (port 8080, `-ngl 40` of 64, 36K ctx, `-np 1` in v16, ~12 GB VRAM measured) — session-level LoRA swap via session wrappers; OpenCode-facing.
  - **T2 pipeline** (port 8083, `-ngl 20`, 16K ctx, ~5.5 GB VRAM) — no LoRA; base-model synthesis for background pipelines.
  - **T3 content/batch** (port 8084, `-ngl 0` CPU-only, 8K ctx, ~0.5 GB VRAM) — LoRA via dispatcher (port 4200); content-marketing and leads-icp adapters.
- **April 22, 2026 release benchmarks** = Qwen3.6-27B beats the previous-gen Qwen3.5-397B-A17B flagship on SWE-bench Verified (77.2% vs 76.2%) and Terminal-Bench 2.0 (59.3% vs 52.5%) at a fraction of the VRAM. The "27B beats 397B" result is the headline shift of 2026 Q2.

### Why Qwen3-Coder-Next 80B-A3B is the manual on-demand tier (v14 reclassified)

> **v14 status change.** v12 originally positioned this model as an automated on-demand "deep-think" tier; v14 retires it from automated use after honest analysis of its 3-5 tok/s throughput under MoE expert offload. See Appendix A — Ruled-Out Features for the full rationale. The model is preserved as a manual on-demand capability for NDA-tagged work where the code cannot leave monarch.

- 80B total / 3B active MoE = parameter breadth without dense compute cost.
- ~58.7% SWE-Bench Verified (third-party); within striking distance of Claude Sonnet 4.6 (62.4%) on the same benchmark.
- 256K native context, extendable to 1M via YaRN.
- Purpose-trained for Cline/Aider/Claude Code-style scaffolds with long-horizon tool use.
- Fits 24+96 envelope at Q4 with MoE expert offload — the first frontier-class agentic coding model that's locally runnable on this class of hardware.
- **Trade-off that pushed it to manual on-demand status:** measured 3-5 tok/s under expert offload on monarch is too slow for routine interactive use AND insufficient for overnight batch workloads on a growing codebase (achievable nightly budget ~70-86k tokens in 8 hours; refactor passes touch 20+ files at 2-4k tokens each, leading to accumulating half-finished work).
- **What replaces it in v14:** interactive heavy code work goes to Claude Pro tabs (zero-second latency, faster, two subscriptions in operator's workflow); cloud overnight batch goes to DeepSeek V4 Pro via LiteLLM; local-only NDA work stays on this manual invocation.

### Why Qwen3.6-35B-A3B is the throughput tier

- MoE 3B active = 80–100 tok/s achievable with `--cache-type-k q8_0` and flash attention.
- Native 1M-token context (KV cache will balloon — keep this for batch jobs, not interactive chat).
- Better choice than dense 27B for content/leads/financial-orchestration where throughput matters more than reasoning depth.
- Caveat: LoRA training on MoE bases is harder (router confusion, expert collapse risks). Content + Leads LoRAs accept this; the three high-stakes LoRAs target dense 27B instead.

### Cloud fill — when to reach for Claude vs DeepSeek API vs not at all

| Trigger | Use |
|---|---|
| Architectural decisions, multi-file refactors, "I'm stuck" on complex code | Claude Pro #1 (Claude Code) |
| Client deliverables, polished consultancy outputs, brand-voice copy | Claude Pro #2 |
| Cheap agentic reasoning, 1M-context backtests, bulk financial analysis | DeepSeek V4 Flash API |
| Long-horizon agent swarms, big-context document analysis | Kimi K2.6 API ($0.60/M input — cheaper than Claude for these workloads) |
| Routine content generation, lead filtering, classification | Local only — no cloud needed |

The two-Pro split keeps client work and personal experiments in separate accounts so context windows don't cross-contaminate, and so personal token burn doesn't risk client-deliverable rate limits.

### Operational notes specific to the May 2026 stack

**Qwen3.6 requires llama.cpp directly, not Ollama.** Qwen3.6 ships with a separate `mmproj-F16.gguf` vision projector file. Ollama's blob format doesn't include this, so Qwen3.6 GGUFs do not currently run in Ollama. Use llama.cpp (built from source against CUDA 12.8) or Unsloth Studio. This is a real workflow change from v4 — any prior `ollama run` patterns for Qwen3-class models will need to be migrated to `llama-server` invocations.

**Recommended llama.cpp invocation for Qwen3.6-27B (server mode):**
```bash
./llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  --mmproj unsloth/Qwen3.6-27B-GGUF/mmproj-F16.gguf \
  --jinja \
  --flash-attn on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -ngl 99 \
  --ctx-size 32768 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --host 0.0.0.0 --port 8080
```

**Recommended llama.cpp invocation for Qwen3-Coder-Next 80B-A3B (MoE offload):**
```bash
./llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen3-Coder-Next-GGUF:UD-Q4_K_XL \
  --jinja \
  --flash-attn on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -ngl 99 \
  -ot ".ffn_.*_exps.=CPU" \
  --ctx-size 65536 \
  --temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05 \
  --host 0.0.0.0 --port 8081
```

**vLLM multi-LoRA serving for Qwen3.6-27B + 3 LoRAs:**
```bash
vllm serve unsloth/Qwen3.6-27B \
  --served-model-name qwen3.6-27b \
  --enable-lora \
  --max-loras 4 \
  --max-lora-rank 32 \
  --lora-modules \
    qwen3.6-consultancy=/home/monarch/loras/qwen3.6-consultancy \
    qwen3.6-design=/home/monarch/loras/qwen3.6-design \
    qwen3.6-exploratory=/home/monarch/loras/qwen3.6-exploratory \
  --port 8000
```
LiteLLM router then dispatches `model: qwen3.6-consultancy` / `qwen3.6-design` / `qwen3.6-exploratory` per request; vLLM applies the named adapter at inference time on the shared base.

### What's deliberately NOT in this stack

- **DeepSeek R2 / V4 Pro / V4 Flash local** — too large for 24+96 envelope. Use DeepSeek API instead.
- **Kimi K2.6 local** — 1T MoE, ~240 GB minimum even at 1.8-bit, would yield ~1 tok/s. Use Moonshot API.
- **GLM-4.7 full local** — needs 128 GB RAM minimum for 2-bit quant. Borderline on 96 GB; not worth the engineering vs running GLM-4.7-Flash locally and GLM-4.7 full via API.
- **Llama 4 Scout** — outclassed by Qwen3.6 at the same footprint.
- **Original Qwen3 32B / Qwen3-Coder 32B** — superseded by Qwen3.6-27B and Qwen3-Coder-30B-A3B/80B-A3B. Don't pin these.

### Open questions for v6

1. **Fine-tuning compute scheduling.** Unsloth QLoRA on Qwen3.6-27B fits the 96 GB envelope but contends with inference for VRAM during training. Decision: train overnight with inference paused, or partition GPU memory and accept slower training? — pending first training run benchmark.
2. **OpenCode SKILL.md / AGENTS.md migration scope.** Existing CLAUDE.md/SKILL.md infrastructure across micro-saas, financial-pipeline, eeg-pipeline, leads, and youtube-pipeline projects needs symlink strategy decided: single AGENTS.md as source-of-truth with CLAUDE.md symlink, or maintain dual files? Pending file-system architecture session.
3. **GLM-4.7-Flash as alternative to Qwen3.6-35B-A3B for throughput tier.** Both fit 24 GB Q4. GLM has better reasoning benchmarks; Qwen has bigger native context and Unsloth Dynamic 2.0 quants. Bake-off worth running once models land.
4. **OpenCode subagent → vLLM LoRA mapping.** Each OpenCode subagent declares a model. The mapping from subagent name → LiteLLM-routed LoRA needs convention (e.g., `model: "litellm/qwen3.6-consultancy"` vs explicit URL). Resolve when first OpenCode config ships.

---

## Phase 9 — Inference Architecture & Multi-Host Deployment

> **v14 architecture.** v12 specified a three-engine model (vLLM, llama.cpp, llama-cpp-python) wired to a single interactive serving role. v13 corrected the LoRA-on-Qwen3.6 architecture to llama.cpp. v14 deploys five concurrent always-on tiers (three of them llama-server instances sharing the same mmap'd GGUF) plus discipline-layer services (validation gate, LoRA dispatcher). Reading order: five-tier overview → port assignments → per-tier configs → LoRA management → validation gate → LoRA dispatcher → LiteLLM config → VRAM/RAM budget → bringup → verification → failure modes → qwen-coder-deep status.

### Five-Tier Architecture — what each tier owns

Engines (llama-server, vLLM, llama-cpp-python) are now implementation details of tiers, not first-class abstractions. The five tiers partition workloads along latency / quality / specialisation axes and run concurrently.

| Tier | Purpose | Engine | Model | Memory pattern | Owns |
|---|---|---|---|---|---|
| **T1 interactive** | OpenCode sessions (consultancy/design/exploratory) | llama-server | Qwen3.6-27B UD-Q4_K_XL | 11 GB VRAM, mmap-shared weights | Latency-critical interactive work, session-level LoRA swap, vision capability (load mmproj on demand) |
| **T2 pipeline** | Background synthesis (news, financial, leads) | llama-server | Qwen3.6-27B UD-Q4_K_XL (base) | 5.5 GB VRAM + GPU/CPU split, mmap-shared | Always-on synthesis at moderate context. No LoRA. Base-model intelligence. |
| **T3 content/batch** | Batch content generation, LoRA work | llama-server | Qwen3.6-27B UD-Q4_K_XL + adapters | 0.5 GB VRAM, all CPU, mmap-shared | LoRA-bearing batch jobs. Dispatcher-managed adapter state. Slow tolerated. |
| **T4 utility** | Fast classification, validation grading | llama.cpp | Phi-4-mini Q4_K_M GGUF | 4.2 GB VRAM (measured), GPU-resident | High-frequency small-output calls. -np 4 parallel slots. Validation gate's direct dependency. v16: pivoted from vLLM. |
| **T5 small seed** | In-process classifier worker | llama-server | Qwen3-1.7B Q5_K_M | 0 VRAM, ~2 GB RAM | CPU triage, routing, schema-validation. Additional CPU workers spawned per n8n execution as needed. |

**mmap weight sharing (load-bearing).** T1, T2, and T3 all load the *same* GGUF file. Linux page cache shares the ~17 GB of weight pages across all three llama-server processes. Each pays only for its own KV cache + per-instance activation buffers. **This is the single architectural reason the five tiers fit on monarch.** If the three Qwen3.6 tiers were given different file paths, the RAM cost would triple and the architecture would not fit.

**llama-cpp-python role (carried forward from v12, scope narrowed).** Used as a *library* inside Python scripts and n8n nodes for short-lived classifier work. The persistent role goes to T5 (Qwen3-1.7B always-on); llama-cpp-python is for additional workers spawned per-execution.

**Tier selection guidance — "which tier does this workload belong on?":**

| If the workload is… | Use… |
|---|---|
| Interactive, latency matters, human at keyboard | T1 (or escalate to Claude Pro) |
| Background synthesis, can wait minutes | T2 |
| Heavy batch with brand voice or domain LoRA, can run overnight | T3 |
| Classification or routing, sub-second target | T4 |
| Lightweight schema/format check, very high volume | T5 |
| Anything above with >16K ctx | LiteLLM fallback → DeepSeek V4 Flash |
| Heavy interactive code work | Claude Pro tab, not local |
| NDA code work, locally only, can wait hours | qwen-coder-deep manually (see end of Phase 9) |

**vLLM and LiteLLM clarification (frequent confusion point):** vLLM is the inference engine for T4 only — it loads weights, manages KV cache, runs forward passes on the GPU. LiteLLM is the routing proxy — it sits in front of all tier endpoints and presents a unified OpenAI-compatible interface. They are complements, not alternatives.

### Port Assignments

| Service | Port | Bind | Status | Notes |
|---|---|---|---|---|
| **T1 — llama-server Qwen3.6-27B interactive + LoRA** | 8080 | 127.0.0.1 | always-on | Specialist OpenCode sessions, session-wrapper LoRA swap |
| **T2 — llama-server Qwen3.6-27B pipeline synthesis** | 8083 | 127.0.0.1 | always-on | NEW in v14. News synthesis, financial Phase A/C, leads triage |
| **T3 — llama-server Qwen3.6-27B content/batch (CPU)** | 8084 | 127.0.0.1 | always-on | NEW in v14. Content/marketing/leads-ICP LoRA work via dispatcher |
| **T4 — llama-server Phi-4-mini** | 8002 | 127.0.0.1 | always-on | Utility classifier, validation grader. v16: pivoted from vLLM (which silently crashes at FlashAttention V2 init on Ampere+CUDA 12.8) to llama.cpp serving Phi-4-mini Q4_K_M GGUF. 206 tok/s gen measured. |
| **T5 — llama-server Qwen3-1.7B (CPU seed)** | 8085 | 127.0.0.1 | always-on | NEW in v14. Lightweight classifier worker |
| llama-server Qwen3-Coder-Next 80B-A3B | 8081 | 127.0.0.1 | **manual on-demand** | v14 RECLASSIFIED. NDA-tagged work only |
| LiteLLM router | 4000 | 0.0.0.0 (Tailscale) | always-on | The only port external clients hit |
| **Validation gate** | 4100 | 127.0.0.1 | always-on | NEW in v14. Schema/grounding/voice gating |
| **LoRA dispatcher (Tier 3)** | 4200 | 127.0.0.1 | always-on | NEW in v14. Workflow-scoped adapter swap |
| **Jarvis orchestration service** | 4300 | 0.0.0.0 (Tailscale) | always-on | NEW in v15. MacBook wake-word daemon posts audio here. WebSocket notification bus for PWA. |
| **Read-only data API** | 4400 | 0.0.0.0 (Tailscale) | always-on | NEW in v15. PWA's only data source. No writes, no side effects. |
| **Command Center PWA** | 3000 | 0.0.0.0 (Tailscale) | always-on | NEW in v15. Static React build, nginx or `serve`. Tailscale-only — no Funnel. |
| n8n | 5678 | 0.0.0.0 | always-on | Phase 5, unchanged |
| Postgres | 5432 | Docker network | always-on | Phase 5, unchanged |

> **Port 8000 is retired** (v12's vLLM #1 port). **Port 8081 (qwen-coder-deep) is no longer automated** — see the new Appendix A entry.

**UFW rules** for these new services (Tailscale interface only — none of these inference ports should be reachable from public internet directly):
```bash
sudo ufw allow in on tailscale0 to any port 4000  # LiteLLM
sudo ufw allow in on tailscale0 to any port 4300  # Jarvis (MacBook daemon + PWA WebSocket)
sudo ufw allow in on tailscale0 to any port 4400  # Read-only data API (PWA data source)
sudo ufw allow in on tailscale0 to any port 3000  # Command Center PWA (static serve)
# Ports 8080, 8083, 8084, 8002, 8085, 4100, 4200 stay loopback-only — only LiteLLM forwards externally
```

### Tier 1 (Interactive): llama-server Qwen3.6-27B + LoRA

**Recommended base model:** `unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL` (Unsloth Dynamic 2.0 — near-lossless on Qwen3.6-27B; third-party benchmarks: 60.9% Aider Polyglot vs 61.8% BF16 full).

```bash
# T1 — Interactive (port 8080, -ngl 40 of 64, 36K ctx, -np 1)  [v16: was np 2/32K in v15]
~/llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  --no-mmproj --jinja --flash-attn on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -ngl 40 --ctx-size 36864 -np 1 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --host 127.0.0.1 --port 8080
```

**`--no-mmproj`** skips the integrated MoonViT BF16 vision tower (~0.9 GB VRAM saved). v15 doc specified `--language-model-only` for this; that flag does not exist in llama.cpp builds 9172+. The correct flag is `--no-mmproj`. Add `--mmproj ~/models/qwen3.6-27b/mmproj-F16.gguf` and remove this flag when Design stack vision tasks are active.

**`-ngl 40` vs v13's `-ngl 99`.** v13's all-layers-on-GPU allocation made T1 the sole VRAM consumer at ~17 GB. v14 caps T1 at 40 of 64 layers so T2 + T3 + T4 fit in the same 24 GB envelope. The 24 CPU-resident layers cost ~1.5 GB RAM; tok/s drops from 30-50 to 30-40 (below interactive noise floor). T1 generation speed not yet benchmarked end-to-end — flagged in Open Items.

**`-np 1` vs v15's `-np 2`.** v15 ran two parallel slots so a pipeline call landing on T1 would queue rather than reject. In practice, Trent has two Claude Pro lanes for heavy concurrent work; T1 serves at most one OpenCode session at a time. Dropping to single-slot also clears the operational path for Jarvis's Phase 18 supervisor to park/unpark T1 cleanly during pipeline burst windows.

**`--ctx-size 36864` (36K) vs the obvious "more is better" choice.** llama.cpp compute scratch buffers scale with `n_ctx_seq` (the longest single-sequence the model handles). v15's 32K-with-np-2 had `n_ctx_seq=16K`. Naïvely keeping 32K at np=1 would have been a wash; bumping to 48K-with-np-1 cost an extra 240 MiB scratch without proportional utility. 36K is the sweet spot: 2.25× the previous per-slot context capacity, same VRAM footprint as v15 within margin of error.

**VRAM at startup (no-mmproj, 36K ctx, q8_0 KV, -ngl 40, np=1) — MEASURED May 16, 2026:**
- Weights (40 of 64 layers on GPU): ~7 GB
- KV cache (36K, q8_0, single slot): ~2.4 GB
- Compute scratch buffers (sized for 36K): ~2.0 GB
- Overhead: ~0.5 GB
- **Total: 11984 MiB (measured)**

### Tier 2 (Pipeline Synthesis): llama-server Qwen3.6-27B base [NEW]

```bash
# T2 — Pipeline synthesis (port 8083, -ngl 20 of 64, 16K ctx, base model only)
~/llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  --no-mmproj --jinja --flash-attn on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -ngl 20 --ctx-size 16384 \
  --temp 0.3 --top-p 0.9 --top-k 20 \
  --host 127.0.0.1 --port 8083
```

**Purpose.** Always-on background synthesis. News pipeline (06:25), financial Phase A pre-market synthesis (09:00), financial Phase C EOD synthesis (16:30), leads triage synthesis, and any "read a lot of stuff and write a coherent summary" workload routes here via LiteLLM's `qwen3.6-pipeline` model entry.

**Why no LoRA on T2.** Synthesis is base-model intelligence at modest context. Persona specialisation (the consultancy/design/exploratory LoRAs targeting T1) does not help "summarise these 12 articles into a market brief." T2 is intentionally base-model.

**VRAM accounting.** Weights live in the mmap'd page cache shared with T1 and T3. T2 pays only KV cache (~0.8 GB at 16K, q8_0) plus activation buffers for the 20 GPU layers (~0.5 GB) and the 44 CPU layers (~2 GB RAM, not VRAM). **Total VRAM measured May 16, 2026: 6752 MiB.**

**Speed — MEASURED May 16, 2026.** **5.4 tok/s gen, 20.6 tok/s prompt eval** — meaningfully below v15's 12-18 tok/s projection. llama.cpp logs `fused Gated Delta Net (chunked) not supported, set to disabled` at startup; Qwen3.6's hybrid attention architecture falls back to a slower path under partial offload. Repeated benchmarks across three runs returned 5.38-5.42 tok/s. This drives the three-mode reallocation doctrine (§ Three-Mode VRAM Doctrine below) — standard T2 is functional but not viable for time-windowed pipelines without a burst.

**At burst-mode (-ngl 60, 32K ctx) — MEASURED May 16, 2026:** 22.9 tok/s gen, 112.4 tok/s prompt eval. 4.2× standard. See `inference-burst-up` script details below.

**Context overflow strategy.** When a synthesis job needs >16K ctx (rare — most daily synthesis fits in 8-12K), LiteLLM's fallback chain routes that specific call to `deepseek-v4-flash` (~$0.004 per call). v14 does NOT implement dynamic context resizing of T2 — the VRAM juggling adds failure surface that the cloud route avoids for pennies.

### Tier 3 (Content/Batch CPU): llama-server Qwen3.6-27B + LoRA via dispatcher [NEW]

```bash
# T3 — Content/batch (port 8084, -ngl 0 = pure CPU, 8K ctx)
# v16: CUDA_VISIBLE_DEVICES= prefix is REQUIRED — see note below
CUDA_VISIBLE_DEVICES= ~/llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  --no-mmproj --jinja \
  -ngl 0 --ctx-size 8192 -t $(nproc) \
  --temp 0.7 --top-p 0.95 --top-k 20 \
  --host 127.0.0.1 --port 8084
```

**v16 critical correction: `CUDA_VISIBLE_DEVICES=` prefix.** llama.cpp's CUDA build initializes cuBLAS workspace + KV scratch buffers on the GPU regardless of `-ngl 0`. Measured cost without the prefix: 1759 MiB just on T3 startup. Hiding the GPU from the process zeroes that contribution. The same prefix is required on T5.

**Purpose.** Always-on batch generation with LoRA. Content generation in the Taolen Logic brand voice (`content-marketing` LoRA), lead-scoring triage (`leads-icp` LoRA), and any scheduled/queued workload that benefits from a domain-specialised adapter and tolerates 3-8 tok/s.

**VRAM accounting (v16).** 0 MiB GPU contribution with `CUDA_VISIBLE_DEVICES=`. All weight execution runs on CPU using the same mmap'd page-cache weights as T1 and T2.

**RAM accounting.** ~4 GB for KV cache + activations + the LoRA adapter (which lives in RAM alongside the base weights). T3 is the most RAM-heavy of the three Qwen3.6 tiers because all 64 layers' activations are CPU-resident.

**Why CPU is acceptable here.** Batch work runs while the operator is doing something else. A 1K-token LinkedIn post at 5 tok/s = 200 seconds; a batch of 20 = ~70 minutes; running 9 PM to 10:10 PM is fine. If the workload needs to be faster, it should be queued earlier or routed to `deepseek-v4-flash` via LiteLLM.

**LoRA management on T3 is dispatcher-controlled.** n8n workflows do NOT POST directly to `http://127.0.0.1:8084/lora-adapters`. They POST to `http://127.0.0.1:4200/dispatch` with `required_adapter` and `workflow_id`; the dispatcher handles swap-then-forward. See "LoRA Dispatcher Service" below.

**Failure mode unique to T3.** If `htop` shows T3 saturating all CPU cores during heavy batch, T2's CPU layers (the 44-of-64 non-GPU layers) will slow down too. Don't run T2-heavy synthesis (e.g., a 12K-token EOD financial brief) concurrently with a T3-heavy content batch. Telemetry makes this observable; the daily morning review surfaces it if it becomes a pattern.

### Tier 4 (Phi-4-mini Utility) — llama.cpp [PIVOTED in v16 from vLLM]

```bash
# T4 — Utility classifier (port 8002, llama.cpp, Q4_K_M, full GPU offload)
~/llama.cpp/build/bin/llama-server \
  -hf unsloth/Phi-4-mini-instruct-GGUF:Q4_K_M \
  --jinja --flash-attn on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -ngl 99 --ctx-size 16384 -np 4 \
  --temp 0.3 --top-p 0.9 \
  --host 127.0.0.1 --port 8002
```

**v16 critical change: pivoted from vLLM to llama.cpp.** v15 specified vLLM 0.20.1 serving `microsoft/Phi-4-mini-instruct` at fp8. In live bringup May 16, 2026, vLLM 0.20.1 + Phi-4-mini-instruct fp8 on RTX 3090 (Ampere SM86) + CUDA 12.8 **silently crashes at FlashAttention V2 initialization** with no traceback. Reproduced across four launch variants:
- default (0.12 gpu-memory-utilization, 16K ctx)
- bumped to 0.18 gpu-memory-utilization
- with `--enforce-eager` (disables torch.compile + CUDA graphs)
- with `--max-model-len 4096` (avoids LongRoPE warning)

All four crashed identically with `Using FlashAttention version 2` as the last log line. Switched to llama.cpp with the Q4_K_M GGUF. Measured: **206 tok/s gen, 537 tok/s prompt eval, 4179 MiB VRAM**. Exceeds vLLM's design intent throughput. Removes vLLM from the stack entirely; all five tiers are now llama.cpp.

**`-np 4` parallel slots** support concurrent classifier calls (validation gate + intraday financial classifier + news triage can hit T4 simultaneously without serializing).

**`--cache-type-k q8_0 --cache-type-v q8_0`** halves KV cost vs f16 default. Critical: f16 KV at 16K × np 4 cost ~3.2 GB, blowing the budget. q8_0 brings it to ~1.6 GB. Imperceptible quality impact on classifier workloads.

T4 is the direct dependency of the validation gate (which calls Phi-4 for the grounding and voice graders). It also serves Phase B intraday financial classification, news article triage, and any "fast, cheap, structured" call. The 4 parallel slots handle concurrent bursts cleanly.

> ⚠️ **LiteLLM contract.** The model alias `phi4-mini` in the LiteLLM config points to `http://127.0.0.1:8002`. With llama.cpp, the actual model name is reported as `local`; LiteLLM's `model` field translates this. Verify: `curl http://127.0.0.1:8002/v1/models` returns a model entry.

> **vLLM is officially out of the stack.** Appendix A entry added in v16. Do not re-introduce vLLM for any tier unless and until the FlashAttention V2 Ampere/CUDA-12.8 bug is confirmed fixed and reproducibly tested.

### Tier 5 (Small-Model Seed): llama-server Qwen3-1.7B CPU [NEW]

```bash
# T5 — CPU classifier seed (port 8085)
# v16: CUDA_VISIBLE_DEVICES= prefix required to actually be CPU-only
# v16: model repo corrected to unsloth/Qwen3-1.7B-GGUF (v15 said bartowski; that repo does not exist)
CUDA_VISIBLE_DEVICES= ~/llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen3-1.7B-GGUF:Q5_K_M \
  --jinja -ngl 0 --ctx-size 8192 -t 4 \
  --host 127.0.0.1 --port 8085
```

**Purpose.** A persistent, always-available CPU classifier worker. n8n nodes that need "tag this email as ICP / not ICP," "is this article actually about lighting," "extract the company name from this paragraph," "is this JSON valid against the schema" route here. Sub-second per call on CPU. Zero VRAM cost.

**Why dedicate a tier to it.** v12's plan was to have small-model workers live "inside Python scripts" via llama-cpp-python. In practice this means every n8n execution reloads the model from disk. T5 is persistent — load once, serve forever, sub-second per call.

**`-t 4` (4 CPU threads).** Caps T5's CPU footprint at 4 cores so it doesn't compete with T2/T3 during heavy work. Ryzen 9 9900X has 12 cores; T2 and T3 share the remaining 8 by default.

**Spawning additional CPU workers.** When a single n8n execution needs a different small model (e.g., Llama 3.2 3B for a specific classification format), spawn `llama-cpp-python` inline within the n8n execution rather than running a persistent tier. T5 is the *seed*, not the complete small-model swarm.

### Three-Mode VRAM Reallocation Doctrine [NEW in v16]

This section defines the strategic framework for VRAM allocation across operating modes. It replaces v15's implicit assumption that one allocation works for all workloads.

#### Core principle

**Quality of output is non-negotiable. Allocation is negotiable.**

The methodology is **offload-then-hotswap**: temporarily reallocate VRAM to run at peak efficiency, complete the work, reallocate back. The swap cost is 30 seconds to 3 minutes (a single tier kill + relaunch). The alternative — permanently shrinking allocations so all tiers coexist at reduced capacity — pays a GIGO tax continuously: small context windows, poor latency, and underweight inference produce results that take hours longer and are lower quality. The math never favors the permanent shrink.

The methodology originates from a real constraint: large-context, high-quality pipeline inputs require large context windows and full GPU offload. Trying to serve a financial or news synthesis pipeline under standard T2 (5.4 tok/s, 16K ctx) with T1 also resident produces slow, context-starved output. A 3-minute hotswap into burst mode (22.9 tok/s, 32K ctx) runs the same workload in 44 minutes instead of 3.5 hours — at higher quality because the full context fits. Garbage in, garbage out applies at the allocation layer just as much as at the prompt layer.

**Sequential, not concurrent.** Running the news pipeline and then the financial pipeline sequentially in burst mode will be faster in aggregate than running both concurrently with T1 up in standard mode. This is the designed pattern. Do not attempt to run multiple pipelines concurrently to "save time" — the degraded allocation cancels any parallelism gain.

#### Mode 1 — Standard / Interactive

**When:** Default operating state. Trent at keyboard, OpenCode possibly active, no scheduled pipeline running.

**Allocation (measured May 16, 2026):**
- T1 full residence: -ngl 40, 36K ctx, np=1 → **11984 MiB**
- T2 lean: -ngl 20, 16K ctx → **6752 MiB**
- T3 CPU only (CUDA_VISIBLE_DEVICES=) → **0 MiB**
- T4: -ngl 99, 16K ctx, np=4, q8_0 KV → **4179 MiB**
- T5 CPU only (CUDA_VISIBLE_DEVICES=) → **0 MiB**
- **Total: 22901 MiB. Headroom: 1675 MiB.**

**Speed (measured):**
- T1 interactive: not yet benchmarked (Open Item)
- T2 pipeline: 5.4 tok/s gen, 20.6 tok/s prompt eval
- T3 batch CPU: not yet benchmarked
- T4 utility: 206 tok/s gen, 537 tok/s prompt eval
- T5 small seed: not yet benchmarked

**Behavior:** Interactive queries hit T1 fast. Pipeline calls land on T2 at slow throughput — acceptable when there is no time window.

#### Mode 2 — Burst / Pipeline window

**When:** Scheduled pipeline event arrives AND T1 is idle (no active session in last 5 min).

**Allocation (measured May 16, 2026 — end-to-end burst test):**
- T1 PARKED (window killed via `tmux kill-window`) → **0 MiB**
- T2 promoted: -ngl 60, 32K ctx, q8_0 KV → **~16 GB resident (T2 alone)**
- T3 CPU only → 0 MiB
- T4 unchanged → 4179 MiB
- T5 CPU only → 0 MiB
- **Total: 21540 MiB. Headroom during burst: 3036 MiB.**

**Speed (measured):** **22.9 tok/s gen, 112.4 tok/s prompt eval** — 4.2× standard T2 gen, 5.4× standard prompt eval. Repeated across 3 runs, all within 0.2 tok/s of each other. Below the theoretical -ngl 99 ceiling (~30 tok/s on this card) because the Gated DeltaNet fallback path persists even at near-full offload; this is the realistic ceiling on a 3090 for this model with T4 staying up.

**Behavior:** Pipeline completes much faster. Sequential — news pipeline finishes before financial Phase A starts; they do NOT overlap. This is by design: sequential burst is faster in aggregate than concurrent standard (see §18.0 Pipeline scheduling philosophy for the math). T1 unavailable during the burst window (intentional — T1 is parked to fund the burst). Cycle time measured: ~10s burst-up + ~11s burst-down = ~21s total transition overhead.

**Practical pipeline math at burst mode (measured numbers):**

| Workload | Standard wall time | Burst wall time |
|---|---|---|
| Financial Phase A (12 calls × 13K tokens) | ~3.5 hours | ~44 minutes |
| News pipeline (typical 8-10 source synthesis batch) | ~25-40 min | ~6-10 min |

**Trigger:** Cron initially (interim scripts below). Jarvis Phase 18 supervisor when built.

#### Mode 3 — Soft fallback

**When:** Scheduled pipeline event arrives AND T1 is active (operator is using OpenCode and has not yielded T1).

**Design intent allocation:**
- T1 unchanged (full residence preserved) → 11984 MiB
- T2 moderately promoted: -ngl 30, 24K ctx → estimated ~10 GB
- T3/T5 CPU → 0 MiB
- T4 unchanged → 4179 MiB
- **Total estimated: ~26 GB. EXCEEDS the 24576 MiB cap.**

**Status:** Mode 3 is design only. The arithmetic above shows the obvious problem: with T1 fully resident, T2 has no headroom to promote meaningfully.

**Mode 3 is not a failure mode — it is the designed automatic fallback when the operator is actively using T1 and cannot or does not yield.** Jarvis detects T1 activity, notifies the operator, and responds based on the operator's answer:

- **Path A — Operator yields (switches to Claude Code or steps back from T1):** Jarvis proceeds with full burst mode (Mode 2). Clean hotswap, pipeline runs at peak efficiency.
- **Path B — Operator declines or does not respond within 5 min:** Jarvis automatically resorts to the best available fallback in priority order:
  1. **Cloud route** — pipeline runs via LiteLLM cloud chain (DeepSeek V4 Flash). Requires API key (Open Item). Preferred when available because quality is maintained.
  2. **Heavy offload on T2** — pipeline runs slower under T2 standard config with T1 still resident. Latency degrades but pipeline completes without disrupting interactive work.
  3. **Deferral** — pipeline waits for next viable T1-idle window; logs the deferral and surfaces to PWA.
- **Path C — Operator is unavailable (no MacBook session, no PWA response):** Jarvis auto-falls through the same priority order as Path B with no negotiation delay.

The critical design intent: **the operator never needs to babysit the system.** If they are busy with T1 when a pipeline fires, the system handles it gracefully. If they happen to notice Jarvis's notification and can yield, the pipeline gets peak performance. If not, the pipeline runs at reduced performance or defers — and the operator finds out via PWA.

Jarvis Phase 18 will arbitrate among these based on pipeline criticality (financial Phase A: cloud fallback preferred; news synthesis: deferral acceptable).

#### Implementation — Interim Scripts (validated May 16, 2026)

Until Jarvis Phase 18 ships, Mode 2 is implemented as two shell scripts:

**`~/bin/inference-burst-up <pipeline-name>`** — parks T1, relaunches T2 in burst config.

```bash
#!/usr/bin/env bash
# inference-burst-up — interim profile switch for time-windowed pipeline bursts.
# Parks T1, relaunches T2 with -ngl 60 for fast generation.
# Will be superseded by Jarvis supervisor when Phase 18 lands.
set -euo pipefail

PIPELINE="${1:-unnamed}"
LLAMA_BIN="${LLAMA_BIN:-$HOME/llama.cpp/build/bin/llama-server}"
MODEL_QWEN36="${MODEL_QWEN36:-unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL}"
LOG_DIR="${LOG_DIR:-$HOME/.local/state/inference}"
BURST_LOG="$LOG_DIR/burst.log"
STATE_FILE="$LOG_DIR/burst.state"

log() { echo "[$(date -Is)] burst-up($PIPELINE) $*" | tee -a "$BURST_LOG"; }

# Refuse double-burst
if [ -f "$STATE_FILE" ]; then
  log "REFUSE: burst already active ($(cat $STATE_FILE)). Run inference-burst-down first."
  exit 1
fi

# Refuse if no inference session
if ! tmux has-session -t inference 2>/dev/null; then
  log "FAIL: no inference tmux session — bring stack up first with inference-up"
  exit 1
fi

# v16 interim: T1 activity check is a placeholder. Jarvis Phase 18 will own this signal.
log "starting burst (T1 activity check: SKIPPED in interim mode — Jarvis will own this)"

log "parking T1 (kill window t1-interactive)"
tmux kill-window -t inference:t1-interactive 2>/dev/null || true
sleep 3

log "killing standard T2 (kill window t2-pipeline)"
tmux kill-window -t inference:t2-pipeline 2>/dev/null || true
sleep 3

log "launching burst T2 (-ngl 60, 32K ctx)"
tmux new-window -t inference -n t2-pipeline \
  "$LLAMA_BIN \
    -hf $MODEL_QWEN36 \
    --no-mmproj --jinja --flash-attn on \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    -ngl 60 --ctx-size 32768 \
    --temp 0.3 --top-p 0.9 --top-k 20 \
    --host 127.0.0.1 --port 8083 \
    2>&1 | tee $LOG_DIR/t2-pipeline.log"

# Wait for T2 burst to come up
for i in {1..60}; do
  if curl -sf "http://127.0.0.1:8083/health" >/dev/null 2>&1; then
    log "burst T2 healthy after ${i}s"
    break
  fi
  sleep 2
  if [ "$i" -eq 60 ]; then
    log "FAIL: burst T2 did not bind in 120s — rolling back"
    "$HOME/bin/inference-burst-down" || true
    exit 1
  fi
done

echo "$PIPELINE $(date -Is)" > "$STATE_FILE"
log "burst-up complete — T2 in pipeline-burst mode for $PIPELINE"
```

**`~/bin/inference-burst-down`** — restores standard T1 + T2.

```bash
#!/usr/bin/env bash
# inference-burst-down — restore standard T1/T2 config after a burst window.
set -euo pipefail

LLAMA_BIN="${LLAMA_BIN:-$HOME/llama.cpp/build/bin/llama-server}"
MODEL_QWEN36="${MODEL_QWEN36:-unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL}"
LOG_DIR="${LOG_DIR:-$HOME/.local/state/inference}"
BURST_LOG="$LOG_DIR/burst.log"
STATE_FILE="$LOG_DIR/burst.state"

log() { echo "[$(date -Is)] burst-down $*" | tee -a "$BURST_LOG"; }

if [ ! -f "$STATE_FILE" ]; then
  log "WARN: no burst state file — proceeding anyway with restore"
fi

log "killing burst T2"
tmux kill-window -t inference:t2-pipeline 2>/dev/null || true
sleep 3

log "launching standard T2 (-ngl 20, 16K ctx)"
tmux new-window -t inference -n t2-pipeline \
  "$LLAMA_BIN \
    -hf $MODEL_QWEN36 \
    --no-mmproj --jinja --flash-attn on \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    -ngl 20 --ctx-size 16384 \
    --temp 0.3 --top-p 0.9 --top-k 20 \
    --host 127.0.0.1 --port 8083 \
    2>&1 | tee $LOG_DIR/t2-pipeline.log"

for i in {1..60}; do
  if curl -sf "http://127.0.0.1:8083/health" >/dev/null 2>&1; then
    log "standard T2 healthy after ${i}s"; break
  fi
  sleep 2
done

log "launching T1 (-ngl 40, 36K ctx, np 1)"
tmux new-window -t inference -n t1-interactive \
  "$LLAMA_BIN \
    -hf $MODEL_QWEN36 \
    --no-mmproj --jinja --flash-attn on \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    -ngl 40 --ctx-size 36864 -np 1 \
    --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
    --host 127.0.0.1 --port 8080 \
    2>&1 | tee $LOG_DIR/t1-interactive.log"

for i in {1..90}; do
  if curl -sf "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    log "T1 healthy after ${i}s"; break
  fi
  sleep 2
done

rm -f "$STATE_FILE"
log "burst-down complete — standard config restored"
```

**Cron schedule (NOT yet installed — pending production decision):**

```cron
# News pipeline burst window (initial schedule — adjust based on data acquisition timing)
55 5 * * * /home/monarch/bin/inference-burst-up news-pipeline
0 8 * * * /home/monarch/bin/inference-burst-down

# Financial Phase A burst (weekdays only, ahead of market open; activates when paper trading begins)
# 25 8 * * 1-5 /home/monarch/bin/inference-burst-up financial-phase-a
# 30 9 * * 1-5 /home/monarch/bin/inference-burst-down

# Financial Phase C burst (EOD synthesis; activates when paper trading begins)
# 25 16 * * 1-5 /home/monarch/bin/inference-burst-up financial-phase-c
# 0 18 * * 1-5 /home/monarch/bin/inference-burst-down
```

Financial entries stay commented until paper trading begins and the actual workload timing is empirically observed. News entry stays commented until 24h soak passes and burst cycle is operationally trusted.

**Pre-burst checklist (operator responsibility until Jarvis owns it):**
1. OpenCode is not connected (it'll fail when T1 dies)
2. No other Trent-initiated workflow needs T1
3. `~/.local/state/inference/burst.state` does not exist (no stale burst)

If burst-up half-completes and burst-down also fails, full rebuild always works:
```bash
inference-down
rm -f ~/.local/state/inference/burst.state
inference-up
```

### LoRA Management (two patterns in v14)

#### Pattern 1 — Session-wrapper LoRA swap on Tier 1 (interactive)

llama-server's `/lora-adapters` REST endpoint swaps adapters at runtime without restart. T1's adapter state is owned by the human operator's choice of session wrapper.

**Wrapper scripts — `~/bin/session-<stack>`:**

```bash
# ~/bin/session-consultancy
#!/bin/bash
echo "→ Setting consultancy LoRA..."
curl -s -X POST http://127.0.0.1:8080/lora-adapters \
  -H "Content-Type: application/json" \
  -d '[{"id": 0, "path": "/home/monarch/loras/qwen3.6-consultancy.gguf", "scale": 1.0}]' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('LoRA active:', [a.get('path','').split('/')[-1] for a in d])"
echo "→ Starting OpenCode (consultancy stack)..."
cd ~/projects/consultancy
opencode
```

Mirror this for `session-design` and `session-exploratory`. Adapter swap latency: ~50 ms (a single POST). The session wrapper waits for confirmation before launching OpenCode.

To clear all adapters (use base model only — same as the "pipeline mode" pattern):
```bash
curl -s -X POST http://127.0.0.1:8080/lora-adapters \
  -H "Content-Type: application/json" -d '[]'
```

> **LoRA files don't exist yet.** All five LoRAs are planned, none trained. These scripts are the operational pattern for when they're ready. Until LoRAs are trained, omit the swap call and run base model only — base Qwen3.6-27B UD-Q4_K_XL is a strong general model.

#### Pattern 2 — Dispatcher-managed LoRA swap on Tier 3 (batch)

n8n batch workflows POST to `http://127.0.0.1:4200/dispatch` with `workflow_id`, `required_adapter`, and the OpenAI-format chat completion `request`. The dispatcher serialises swaps under an asyncio lock, drains T3 before swapping, and forwards the request. See "LoRA Dispatcher Service" below for the full contract.

**Workflow boundary = one n8n execution.** Each execution declares one `workflow_id`; all dispatches in that execution use the same `required_adapter`. n8n workflows batch by adapter when planning work (all `content-marketing` jobs in one execution, all `leads-icp` jobs in another). The dispatcher swaps maybe 2-3 times per day total in steady state.

#### Pattern not adopted: per-request multi-LoRA serving on T1

vLLM's punica-style per-request multi-adapter pattern is not available on llama.cpp. Documented in Appendix A's ruled-out entry. For the solo-operator session pattern, session-swap on T1 is functionally equivalent (you don't have three OpenCode sessions running in parallel needing three different adapters in the same instant).

### Validation Gate Service (NEW in v14)

A FastAPI service on port 4100 that sits between Tier 2/3 outputs and downstream consumers. **Every Tier 2/3 output goes through the gate before delivery.** Not optional once the five-tier architecture is live — the volume of agent outputs is too high to audit by hand.

#### Three checks

1. **Schema (deterministic).** Length bounds, JSON shape (optional `jsonschema` validation), required-section heading checks, forbidden-phrase scan. Runs locally in the FastAPI process. ~1 ms.
2. **Grounding (Phi-4-mini call).** Asks Phi-4-mini to identify entities in the OUTPUT that are NOT supported by the SOURCE context. Returns a fraction (grounded entities / total entities). Thresholds: pass at ≥0.90, warn at ≥0.75, fail below.
3. **Voice (Phi-4-mini call).** Scores OUTPUT against a brand voice profile (YAML in `brand_voices/`) on weighted dimensions, scans for forbidden phrases, checks required elements. Returns a normalised 0.0-1.0 score. Thresholds: pass at ≥0.70, warn at ≥0.50, fail below.

#### Verdict synthesis

| Verdict | Action | n8n behaviour |
|---|---|---|
| `pass` | `accept` | Deliver downstream |
| `warn` | `accept` | Deliver, surface in morning review |
| `fail` | `retry_cloud` | Re-run prompt via LiteLLM `deepseek-v4-flash`. If second fail: `surface_for_review` |

#### Critical design: gate calls Phi-4 directly, NOT via LiteLLM

If the validation gate routed grader calls through LiteLLM, the fallback chains would silently redirect grader calls to DeepSeek when Tier 4 is busy — meaning every grader call would cost per-token. Direct connection to T4 means a grader call **fails loudly** when T4 is down, which is the correct behaviour: validation should not silently fall back to cloud.

#### Telemetry

Every `/validate` call writes one row to `validation_telemetry` (Postgres if `DATABASE_URL` is set, SQLite at `~/.local/state/validation-gate/telemetry.db` otherwise). Columns: telemetry_id, timestamp, workflow_id, source_model, output_length, verdict, suggested_action, schema_pass, grounding_score, voice_score, duration_ms.

Two endpoints back drift detection:
- `/telemetry/recent?limit=N` — last N verdicts (also displayed by `inference-status`)
- `/telemetry/summary?hours=N` — aggregate stats by `source_model` over N hours

What to watch:
- **Voice score trending down** for a `source_model` over time = the LoRA is drifting (or training data is stale)
- **Grounding score trending down** = the model is hallucinating more (often source context truncation upstream)
- **retry_cloud rate climbing** = local model regressing or thresholds too strict

#### Brand voice profile

`brand_voices/<name>.yaml`:

```yaml
name: <profile name>
description: <natural-language voice description>
dimensions:
  - name: <dimension>
    weight: <relative weight>
    description: <what scoring this dimension means>
forbidden: [<phrases that flag the output>]
required: [<qualities Phi-4 verifies>]
examples:
  good: [<exemplar good outputs>]
  bad: [<exemplar bad outputs>]
```

`taolen-logic.yaml` ships as the seed profile (technically precise, direct, confident-but-honest, structural clarity). Edit a profile then `curl -X POST http://127.0.0.1:4100/voice/reload`.

#### Integration with n8n workflows

Build once as an n8n sub-workflow; reuse from every Tier 2/3 pipeline:

```
[generate via litellm/qwen3.6-pipeline]
        ↓
[POST http://127.0.0.1:4100/validate
   body: {source_context, output, expected, brand_voice, workflow_id, source_model}]
        ↓
[Switch node on $json.suggested_action]
   ├─ accept           → deliver downstream
   ├─ retry_cloud      → re-prompt via litellm/deepseek-v4-flash → re-validate
   └─ surface_review   → write to morning-review queue, Slack alert
```

### LoRA Dispatcher Service (NEW in v14)

A FastAPI service on port 4200 that owns Tier 3's adapter state and serves `/dispatch` — swap-if-needed then forward, in one call.

#### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service liveness + Tier 3 reachability |
| `/current` | GET | What adapter is loaded on Tier 3 right now |
| `/dispatch` | POST | The main contract: swap-if-needed → forward request |
| `/telemetry/recent?limit=N` | GET | Last N swap+dispatch records |
| `/telemetry/adapter_stats?hours=N` | GET | Aggregate by adapter over N hours |
| `/registry/reload` | POST | Re-read `adapters.yaml` from disk |

#### `/dispatch` contract

Request:
```json
{
  "workflow_id":     "content-linkedin-batch-20260515-2200",
  "required_adapter": "content-marketing",
  "request": { /* OpenAI-format chat completion body */ }
}
```

Response:
```json
{
  "telemetry_id": "9d2c...",
  "completion":   { /* full OpenAI-format chat completion response */ },
  "swap": {
    "swap_needed":       true,
    "previous_adapter":  "base",
    "requested_path":    "/home/monarch/loras/qwen3.6-content-marketing.gguf",
    "drain_ms":          12,
    "swap_ms":           48,
    "dispatch_ms":       18374,
    "total_ms":          18434
  }
}
```

#### Internal pattern

1. Acquire asyncio swap-lock (serialises swaps across concurrent dispatch calls)
2. Read current adapter on T3
3. If `required_adapter` matches current → release lock, forward immediately
4. Otherwise: drain T3 (`/slots` poll until idle, max 60s) → POST `/lora-adapters` → confirm → release lock → forward
5. Write one telemetry row regardless of outcome

The lock guarantees that concurrent dispatches with DIFFERENT adapters serialise their swaps. Concurrent dispatches with the SAME adapter as currently loaded skip the lock-protected work and run in parallel against T3.

#### Adapter registry

`~/services/lora-dispatcher/adapters.yaml`:

```yaml
adapters:
  base:
    path: null   # null = clear adapters, use base Qwen3.6-27B
  content-marketing:
    path: /home/monarch/loras/qwen3.6-content-marketing.gguf
  leads-icp:
    path: /home/monarch/loras/qwen3.6-leads-icp.gguf

defaults:
  drain_timeout_seconds: 60
  fallback_to_base_on_unknown: false
  dispatch_timeout_seconds: 600
```

Edit the YAML then `curl -X POST http://127.0.0.1:4200/registry/reload`.

#### Failure modes (specific to the dispatcher)

- **Drain timeout (503).** T3 had an in-flight request that didn't finish within `drain_timeout_seconds`. Indicates adapter mixing within an execution — anti-pattern.
- **Adapter swap failed (502).** llama-server's `/lora-adapters` POST returned non-2xx. Often: corrupt LoRA file or non-existent path.
- **Dispatch failed (502).** T3 didn't respond. Often: T3 is sick — check `inference-status`.
- **Unknown adapter (404).** Registry doesn't contain `required_adapter`. Fix the workflow name or add to `adapters.yaml`.

#### What to watch in telemetry

- **High average drain_ms for an adapter** = n8n is mixing adapters within executions. Fix the batching.
- **Adapter used heavily** = candidate for further training.
- **Adapter never used** = candidate for retirement.
- **High failure rate on a specific adapter** = file integrity issue or training pathology.

### LiteLLM Router Configuration

`~/litellm/config.yaml` (v14 — expanded for five-tier):

```yaml
model_list:
  # ─── T1 — Interactive (port 8080) ───
  - model_name: qwen3.6-consultancy
    litellm_params:
      model: openai/qwen3.6-consultancy
      api_base: http://127.0.0.1:8080/v1
      api_key: "EMPTY"
  - model_name: qwen3.6-design
    litellm_params:
      model: openai/qwen3.6-design
      api_base: http://127.0.0.1:8080/v1
      api_key: "EMPTY"
  - model_name: qwen3.6-exploratory
    litellm_params:
      model: openai/qwen3.6-exploratory
      api_base: http://127.0.0.1:8080/v1
      api_key: "EMPTY"

  # ─── T2 — Pipeline synthesis (port 8083) — NEW in v14 ───
  - model_name: qwen3.6-pipeline
    litellm_params:
      model: openai/qwen3.6-pipeline
      api_base: http://127.0.0.1:8083/v1
      api_key: "EMPTY"
      timeout: 600
      stream_timeout: 600

  # ─── T3 — Content/batch (port 8084) — NEW in v14 ───
  # Note: n8n batch jobs should call the LoRA dispatcher (:4200/dispatch),
  # NOT this LiteLLM route, because LiteLLM cannot manage the adapter swap.
  # This route exists so ad-hoc calls (manual prompts, eval runs) can still
  # hit T3 directly with whatever adapter is currently loaded.
  - model_name: qwen3.6-content
    litellm_params:
      model: openai/qwen3.6-content
      api_base: http://127.0.0.1:8084/v1
      api_key: "EMPTY"
      timeout: 1200
      stream_timeout: 1200

  # ─── T4 — Phi-4-mini utility (port 8002) ───
  - model_name: phi4-mini
    litellm_params:
      model: openai/phi4-mini
      api_base: http://127.0.0.1:8002/v1
      api_key: "EMPTY"

  # ─── T5 — CPU small-model seed (port 8085) — NEW in v14 ───
  - model_name: qwen3-small
    litellm_params:
      model: openai/qwen3-small
      api_base: http://127.0.0.1:8085/v1
      api_key: "EMPTY"

  # ─── Manual on-demand: qwen-coder-deep (port 8081) ───
  # Only reachable when manually brought up. LiteLLM fallback hides the
  # absence from callers under normal (always-on five-tier) operation.
  - model_name: qwen-coder-deep
    litellm_params:
      model: openai/qwen3-coder-next
      api_base: http://127.0.0.1:8081/v1
      api_key: "EMPTY"
      timeout: 1800
      stream_timeout: 1800

  # ─── Cloud fallback tier ───
  - model_name: deepseek-v4-flash
    litellm_params:
      model: deepseek/deepseek-v4-flash
      api_key: os.environ/DEEPSEEK_API_KEY
  - model_name: deepseek-v4-pro
    litellm_params:
      model: deepseek/deepseek-v4-pro
      api_key: os.environ/DEEPSEEK_API_KEY
  - model_name: kimi-k2.6
    litellm_params:
      model: moonshot/kimi-k2-6
      api_key: os.environ/MOONSHOT_API_KEY

# ─── Fallback chains — every local tier has a cloud release valve ───
litellm_settings:
  fallbacks:
    - qwen3.6-pipeline:    ["deepseek-v4-flash"]
    - qwen3.6-content:     ["deepseek-v4-flash"]
    - qwen3.6-consultancy: ["qwen3.6-pipeline", "deepseek-v4-flash"]
    - qwen3.6-design:      ["qwen3.6-pipeline", "deepseek-v4-flash"]
    - qwen3.6-exploratory: ["qwen3.6-pipeline", "deepseek-v4-flash"]
    - qwen-coder-deep:     ["deepseek-v4-pro", "deepseek-v4-flash"]
    - phi4-mini:           []   # no fallback — validation gate depends on direct connection
    - throughput-tier:     ["deepseek-v4-flash", "kimi-k2.6"]

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  # database_url: DISABLED — see v11 note on LiteLLM DB isolation

router_settings:
  model_group_alias:
    throughput-tier: ["qwen3.6-content", "deepseek-v4-flash", "kimi-k2.6"]
  routing_strategy: simple-shuffle
  num_retries: 2
  request_timeout: 120
```

> **`phi4-mini` has empty fallback by design.** The validation gate calls Phi-4 directly (not via LiteLLM) to prevent silent cloud routing on grader calls. The empty fallback here is belt-and-braces — any other consumer of `phi4-mini` via LiteLLM also stays local.

> **`qwen-coder-deep` fallback assumes manual on-demand tier may not be up.** Routes hitting `qwen-coder-deep` silently fall through to `deepseek-v4-pro` if port 8081 is unreachable. Callers don't need to know whether the operator brought it up manually.

**Note on Claude Code:** Pro #1 and Pro #2 access Claude via Claude Code's built-in subscription auth, NOT via LiteLLM. Adding Claude as an API model in LiteLLM would bill against an API account separately from Pro subscriptions. Keep Claude Code on a separate path.

### Resource Budget — Five-Tier Combined Footprint

**VRAM (24 GB total) — five tiers always-on:**

| Process | VRAM allocation | Notes |
|---|---|---|
| T1 llama-server interactive (-ngl 40, 36K ctx, q8_0 KV, -np 1) | **~12.0 GB measured** | v16: np=1 + 36K ctx (was np=2 + 32K in v15) |
| T2 llama-server pipeline (-ngl 20, 16K ctx) | **~6.7 GB measured** | mmap-shared weights with T1, T3. 5.4 tok/s gen measured. |
| T3 llama-server content/batch (-ngl 0, CUDA_VISIBLE_DEVICES=) | **0 GB measured** | CPU execution. v16: env-var prefix zeroes GPU contribution. |
| T4 llama-server Phi-4-mini Q4_K_M (-ngl 99, -np 4, q8_0 KV) | **~4.2 GB measured** | **v16: pivoted from vLLM** to llama.cpp |
| T5 llama-server Qwen3-1.7B CPU (CUDA_VISIBLE_DEVICES=) | **0 GB measured** | RAM only. v16: env-var prefix zeroes GPU contribution. |
| **Total (five tiers, Standard mode)** | **22.9 GB measured** | **~1.7 GB headroom** under 24576 MiB cap |
| Burst mode (T1 parked, T2 -ngl 60 / 32K ctx) | **21.5 GB measured** | **~3.0 GB headroom**. Time-windowed (see Three-Mode Doctrine in Phase 9). |
| qwen-coder-deep (manual, additional) | +5 GB | **Would OOM under Standard mode** — see manual mitigation below |

**Mitigation for manual qwen-coder-deep sessions:** Before bringing it up, take down T3 (`tmux kill-window -t inference:t3-content`) — note T3 now contributes 0 VRAM under v16 with the CUDA_VISIBLE_DEVICES= prefix, so the savings are RAM (~4 GB) and CPU cores only. To free GPU VRAM for qwen-coder-deep, take down T2 (~6.7 GB) or run `inference-burst-up` first to park T1 (~12 GB freed, but then qwen-coder-deep contends with the burst T2 — pick one).

**RAM (96 GB total):**

| Consumer | RAM | Notes |
|---|---|---|
| Qwen3.6-27B mmap'd weights | ~17 GB | Shared across T1, T2, T3 |
| T1 KV cache + activations | ~3 GB | v16: 36K ctx, single slot |
| T2 KV cache + activations | ~3 GB | Includes 44-CPU-layer working set |
| T3 KV cache + activations | ~4 GB | All 64 layers on CPU |
| T4 llama.cpp Phi-4-mini | ~0.5 GB | v16: pivoted from vLLM, GGUF mmap'd |
| T5 Qwen3-1.7B | ~2 GB | Full weights on CPU |
| Postgres + Docker + n8n + OS | ~12 GB | Phase 5 baseline |
| **Five-tier baseline total** | **~41 GB** | **~55 GB free** (measured May 16: 17.4 GB used, 76.7 GB available) |
| qwen-coder-deep (manual, additional) | +41 GB | Tight but fits with T3 down |

**CPU (9900X 12C/24T):** T1/T2/T3 share CPU when their respective non-GPU layers execute. T5 capped at 4 threads. Normal operation load average under 8-10.

### Bringup — `~/bin/inference-up` with VRAM Ceilings

v13's `inference-up` was a simple sequential startup. v14 replaces it with a script that enforces VRAM ceilings between every tier and aborts on any failure. Operational deliverable: `inference-stack/bin/inference-up` (shipped in v14).

Key behaviours:

1. Refuses to start if GPU isn't clean (zombie process holding memory)
2. Brings up tiers in order: T1 → T2 → T3 → T4 → T5 → LiteLLM → validation gate → LoRA dispatcher
3. Reads `nvidia-smi` after each tier startup, asserts cumulative VRAM under documented ceiling
4. Runs coherence smoke test against each Qwen3.6 tier — catches CUDA 13.2 gibberish failure mode per-instance
5. Refuses to proceed past any failure; kills the entire tmux session on abort

**VRAM ceilings (configurable at top of script):**

| After tier | Ceiling (MiB) |
|---|---|
| T1 interactive | 12 000 |
| T2 pipeline | 17 500 |
| T3 content/batch | 18 000 |
| T4 Phi-4-mini | 21 500 |
| Hard cap (any reading) | 23 000 |

Companion scripts:
- `~/bin/inference-down` — clean shutdown with VRAM drain check and optional force-kill prompt
- `~/bin/inference-status` — health snapshot of every port, current VRAM/RAM, current LoRA state on T1 and T3, recent validation verdicts, recent LoRA swaps

> **Startup order rationale:** T1 claims its ~11 GB VRAM block first (largest dedicated allocation). T2 and T3 reuse the mmap'd weights — they cold-start in seconds. T4 (vLLM) sizes `--gpu-memory-utilization` against the *remaining* VRAM after T1-T3, so it must come after them.

### Verification Checkpoints

Per-tier checkpoints replace v13's pair. Run in order after first deployment or major change.

**Checkpoint 1a — T1 (port 8080) responds coherently:**
```bash
curl -s http://127.0.0.1:8080/health
# Expect: {"status":"ok"}
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.6","messages":[{"role":"user","content":"What is 2+2? Answer in one word."}],"max_tokens":10}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
# Expect: "4" or "Four". Gibberish → CUDA 13.2 issue (rebuild llama.cpp).
curl -s http://127.0.0.1:8080/lora-adapters
# Expect: [] (no adapter loaded at base startup)
```

**Checkpoint 1b — T2 (port 8083) responds coherently.** Same shape as 1a, on port 8083.

**Checkpoint 1c — T3 (port 8084) responds coherently.** Same shape as 1a, on port 8084. Slower response (CPU); use a minimal prompt ("Reply with only: OK").

**Checkpoint 1d — T4 llama.cpp Phi-4-mini (port 8002):** [v16: pivoted from vLLM]
```bash
curl -s http://127.0.0.1:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local","messages":[{"role":"user","content":"Reply with just OK"}],"max_tokens":10}'
# Expect: response with content "OK" — measured 206 tok/s gen, ~2s end-to-end
```

**Checkpoint 1e — T5 (port 8085).** Same shape as 1a, on port 8085.

**Checkpoint 2 — Validation gate (port 4100):**
```bash
curl -s http://127.0.0.1:4100/health
# Expect: {"status":"ok","service":"validation-gate"}

# Round-trip test (skips voice check if profile not yet installed)
curl -s -X POST http://127.0.0.1:4100/validate \
  -H "Content-Type: application/json" \
  -d '{
    "source_context": "",
    "output": "test output for the gate",
    "expected": {"min_length": 5},
    "brand_voice": null,
    "workflow_id": "smoke-test",
    "source_model": "smoke-test"
  }'
# Expect: a verdict with checks.schema.passed = true
```

**Checkpoint 3 — LoRA dispatcher (port 4200):**
```bash
curl -s http://127.0.0.1:4200/health
# Expect: {"status":"ok","service":"lora-dispatcher","tier3_reachable":true,...}

# Round-trip test (base adapter only — works even without LoRAs installed)
curl -s -X POST http://127.0.0.1:4200/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "smoke-test",
    "required_adapter": "base",
    "request": {"model":"local","messages":[{"role":"user","content":"Reply with only: OK"}],"max_tokens":5,"temperature":0}
  }'
# Expect: completion.choices[0].message.content contains "OK"
```

**Checkpoint 4 — VRAM budget is sane (all five tiers running):**
```bash
nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader
# Expect: 19500-21500 MiB used, 3000-5000 MiB free, 24576 MiB total
# If used > 22000 MiB: T2 or T3 -ngl may need adjustment. Take down, fix, retry.
```

**Checkpoint 5 — LiteLLM routes to T2 (the new always-on synthesis tier):**
```bash
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.6-pipeline","messages":[{"role":"user","content":"What is 2+2?"}],"max_tokens":20}'
# Expect: "4" or similar. Verifies LiteLLM → T2 routing.
```

**Checkpoint 6 — LiteLLM routes to cloud:**
```bash
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"What is 2+2?"}],"max_tokens":20}'
# Expect: "4". Verifies cloud fallback path.
```

**Checkpoint 7 — qwen-coder-deep manual on-demand fallback:**
```bash
# With qwen-coder-deep down (default state in v14), LiteLLM should fall back to deepseek-v4-pro:
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-coder-deep","messages":[{"role":"user","content":"What is 2+2?"}],"max_tokens":20}'
# Expect: response served by deepseek-v4-pro (cloud)
```

**Checkpoint 8 — n8n can hit LiteLLM:**
```bash
docker exec n8n-n8n-1 curl http://host.docker.internal:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
# Or use 100.101.244.6:4000 (Tailscale IP)
# Expect: model list including all v14 model_name entries
```

### Failure Modes — What to do when verification fails

**Checkpoint 1a-1c fails: llama-server OOM at startup.**
- Confirm GPU is clean before retry: `nvidia-smi`, kill any zombie PIDs.
- If T1 OOMs: `-ngl 40` may need to drop to 36 on this specific GPU.
- If T2 OOMs after T1 succeeded: T2's `-ngl 20` may need to drop to 16. Or reduce T1's `-ngl` from 40 to 36.
- If T3 OOMs: should not happen — T3 is CPU-only. Likely cause: corrupt GGUF download. Verify sha256 against HF `x-linked-etag`.

**Checkpoint 1a-1c fails: Response is gibberish or repeating tokens.**
- This is the CUDA 13.2 llama.cpp build issue, not PyTorch/vLLM.
- Verify llama.cpp's CUDA linkage:
  ```bash
  ldd ~/llama.cpp/build/bin/llama-server | grep libcuda
  # Should show: /usr/local/cuda-12.8/lib64/libcudart.so.12
  # If cuda-13: rebuild from source pinned to CUDA 12.8 nvcc:
  rm -rf ~/llama.cpp/build
  cmake ~/llama.cpp -B ~/llama.cpp/build \
    -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.8/bin/nvcc \
    -DGGML_CUDA=ON -DLLAMA_CURL=ON
  cmake --build ~/llama.cpp/build --config Release -j --target llama-server
  ```

**Checkpoint 1a fails: MTP head issues / low draft acceptance.**
- If using speculative decoding and draft acceptance is 0%: `mtp.fc.weight` loader bug in some Qwen3.6 GGUF variants. Switch to `Lorbus/Qwen3.6-27B-int4-AutoRound` GGUF if available, or disable speculative decoding (`--draft-max 0`).

**Checkpoint 1d fails: vLLM Phi-4-mini startup error.**
- Phi-4-mini chat_template issues in some vLLM versions — pass `--chat-template` explicitly.
- If memory error: T1 or T2 over-allocating. Lower their `-ngl` first.

**Checkpoint 4 fails: VRAM > 22 GB after all five tiers up.**
- Reduce T1 `--ctx-size` from 32768 → 16384 (saves ~0.8 GB KV).
- Or reduce T4 `--gpu-memory-utilization` from 0.12 → 0.10.

**Checkpoint 5 fails: LiteLLM returns 404 / "model not found".**
- `model_name` in request must exactly match `model_name` in config.yaml. Case-sensitive.
- Restart LiteLLM after config changes: `tmux send-keys -t inference:litellm C-c` then re-run.
- Check logs: `tmux capture-pane -t inference:litellm -p | tail -50`.

**Checkpoint 5 fails: 500 / connection refused to upstream tier.**
- The tier may have died silently. Check `tmux capture-pane -t inference:<tier> -p | tail -30`.
- Common cause: KV cache overflow. Restart the affected tier.

**Checkpoint 6 fails: cloud API auth error.**
- Confirm `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY` are set in LiteLLM's env.
- Source from `~/.config/inference/api_keys.env` (chmod 600) before starting LiteLLM.

**Checkpoint 8 fails: n8n can't reach LiteLLM.**
- Default Docker network doesn't expose host services. Either:
  - (a) Use `100.101.244.6:4000` (Tailscale IP) inside n8n workflows. UFW allows tailscale0:4000.
  - (b) Add `extra_hosts: ["host.docker.internal:host-gateway"]` to n8n's docker-compose.yml.
- Recommend (a) — uses existing Tailscale plumbing.

**New v14 failure modes:**

**mmap weight sharing failed silently — RAM usage tripled.** Symptom: `free -m` shows ~52 GB used after T3 starts instead of expected ~43 GB. Cause: one tier loading the GGUF without mmap (`--no-mmap` flag, or page cache evicted under memory pressure). Fix: confirm `--no-mmap` is not in any tier's invocation; file path must be identical across all three Qwen3.6 tiers.

**Validation gate cannot reach Phi-4 (T4).** Gate returns `grader call failed`. Does NOT fall back to cloud by design — if T4 is sick, the gate goes down. Mitigation: bring T4 back up; gate self-recovers on next `/validate` call.

**LoRA dispatcher drain timeout.** T3 had a long-running in-flight request. The 503 returned to n8n is the correct signal — retry or batch differently. Investigate if it happens >once per day: an n8n workflow is probably mixing adapters within one execution.

**Telemetry DB unreachable.** Both validation gate and LoRA dispatcher write telemetry but neither fails the request if the write fails. They log the error and proceed. Check Postgres health if `inference-status` shows no recent verdicts/swaps despite traffic.

**General fallback when something is mysteriously broken:**
1. `inference-down` — clean shutdown with VRAM drain check.
2. Confirm GPU clean: `nvidia-smi` shows no compute processes.
3. `inference-up` — VRAM-gated bringup will abort early if anything's wrong.
4. Check Phase 2 CUDA verification block.
5. Last resort: full reboot.

### qwen-coder-deep Status (RECLASSIFIED in v14)

> **v14 status change.** Reclassified from "on-demand deep-think tier" to "manual on-demand for NDA-tagged work only." No automated use, no cron, no scheduled mode switching. Full rationale in Appendix A.

**Why retired from automation:**

1. **Speed makes overnight refactoring structurally bad.** Measured 3-5 tok/s under MoE expert offload. Achievable nightly token budget (~70-86k in 8 hours) does not scale with codebase growth. A real refactor pass touches 20+ files; budget exhaustion produces accumulating half-finished refactors, worse than not running at all.
2. **Two Claude Pro subscriptions occupy the "more brain right now" niche.** Interactive heavy code work is faster, higher-quality, and zero-second latency on Pro tab #2 versus a 4-minute takedown-and-bringup cycle on monarch.
3. **DeepSeek V4 Pro fills the overnight-cloud niche.** Scheduled cloud-batch at ~$2-8/night provides orders of magnitude more throughput than 70k local tokens.

**Preserved as a manual on-demand capability** for cases where:
- Code is genuinely NDA-restricted and cannot leave monarch
- Operator can afford to take down T3 (and optionally T2) for the duration
- Runtime fits in a daytime window the operator is awake to monitor

**Manual invocation (v13 Phase 9 block, preserved verbatim):**

```bash
# ~/bin/qwen-coder-deep-up
#!/bin/bash
tmux new-session -d -s qwen-coder-deep \
  '~/llama.cpp/build/bin/llama-server \
    -hf unsloth/Qwen3-Coder-Next-GGUF:UD-Q4_K_XL \
    --jinja \
    --flash-attn on \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    -ngl 99 \
    -ot ".ffn_.*_exps.=CPU" \
    --ctx-size 65536 \
    --temp 0.7 --top-p 0.8 --top-k 20 --repeat-penalty 1.05 \
    --host 127.0.0.1 --port 8081'

# ~/bin/qwen-coder-deep-down
#!/bin/bash
tmux kill-session -t qwen-coder-deep
```

**Pre-flight before manual bringup:**
```bash
# Take down T3 to free ~0.5 GB VRAM + ~4 GB RAM (and the CPU cores it was using)
tmux send-keys -t inference:t3-content C-c
# Optionally take down T2 for more headroom
tmux send-keys -t inference:t2-pipeline C-c
# Then bring up qwen-coder-deep
qwen-coder-deep-up
```

**LiteLLM behaviour:** When qwen-coder-deep is up on port 8081, routes hitting the `qwen-coder-deep` model name reach it directly. When down, fallback chain (`deepseek-v4-pro`, `deepseek-v4-flash`) handles those routes silently. n8n workflows don't need to know which mode is active.



---

## Phase 9 — Pipeline Inference Strategy (Accuracy vs Speed)

*Added v10. This section governs how inference resources are allocated for pipeline tasks vs interactive tasks — a fundamentally different set of trade-offs.*

---

### The Core Principle

Interactive sessions (agentic coding, consultancy work, quick lookups) optimize for latency. **Data pipelines do not.** A news synthesis call that takes 90 seconds instead of 5 seconds is irrelevant when it runs at 6:25 AM unattended. A financial analysis that takes 4 minutes instead of 30 seconds is irrelevant when it runs nightly. What matters for pipelines is that the model has the full context it needs to be correct.

**Two-tier design rule:**
- **Ingestion tier (fast):** Small/fast models classify, filter, score, and route incoming data. Speed matters here — this is the firehose layer. Phi-4-mini, Qwen3 1.7B, Llama 3.2 3B.
- **Synthesis tier (accurate):** Full-size models with maximum context do the actual reasoning — summarization, cross-document analysis, signal identification, strategy conclusions. Latency is irrelevant. Qwen3.6-27B, Qwen3.6-35B-A3B, Qwen3-Coder-Next 80B-A3B.

This means the synthesis tier gets dedicated resources, not a leftover slice after the interactive stack is served.

---

### Real Context Windows — Qwen3.6 Series

Both flagship local models have the same context spec:

| Model | Native context | YaRN extended | vLLM default cap risk |
|---|---|---|---|
| Qwen3.6-27B | **262,144 tokens** | ~1,010,000 tokens | `--max-model-len` silently truncates |
| Qwen3.6-35B-A3B | **262,144 tokens** | ~1,010,000 tokens | same |
| Qwen3-Coder-Next 80B-A3B | 256,000 tokens | ~1,000,000 via YaRN | MoE offload, llama.cpp, -c flag |

**`--max-model-len` is a KV cache budget cap, not a model capability statement.** Setting `--max-model-len 32768` doesn't reflect the model — it saves VRAM by refusing to allocate the KV cache beyond 32K tokens. For synthesis pipelines that need to process full daily article batches, financial reports, or multi-day news blocks, this silently destroys the accuracy you're building the pipeline for.

---

### KV Cache VRAM Math — What Each Context Budget Costs

For Qwen3.6-27B at FP16 KV cache (vLLM default), approximate VRAM cost for the KV cache alone:

| `--max-model-len` | KV cache VRAM (approx) | Use case |
|---|---|---|
| 8,192 (8K) | ~0.5 GB | Trivial — routing, classification |
| 32,768 (32K) | ~2 GB | Fast interactive — loses most context |
| 65,536 (64K) | ~4 GB | Documents, short reports |
| 131,072 (128K) | ~8 GB | Multi-document synthesis, daily news blocks |
| 262,144 (256K) | ~16 GB | Full native context — leaves ~8 GB for weights slice on 3090 |

At 262K, the KV cache alone (~16 GB) + model weights on GPU means you cannot run a second model simultaneously. **This is fine for pipeline jobs — they run on a schedule, not interactively.** The interactive stack runs at reduced context; pipeline runs get dedicated full-context sessions.

**With quantized KV cache** (`--kv-cache-dtype fp8` or `int8`), memory roughly halves:
- 128K context → ~4 GB KV cache
- 256K context → ~8 GB KV cache — leaves room to share VRAM with a smaller resident model

---

### Memory Tier Strategy for Pipeline Synthesis

The 24GB VRAM + 96GB DDR5 + 4TB NVMe is not just a "VRAM first, spill to RAM" story — it's a deliberate tiering strategy based on what each job needs.

```
┌─────────────────────────────────────────────────────────┐
│ VRAM (24 GB)                                            │
│  Attention layers + active compute path                 │
│  KV cache for current context window                    │
│  Fast: hot-swap LoRAs, real-time interactive sessions   │
├─────────────────────────────────────────────────────────┤
│ DDR5 RAM (96 GB)                                        │
│  MoE expert layers (ffn_*_exps offloaded via llama.cpp) │
│  Larger model weight slices not fitting on GPU          │
│  Extended KV cache overflow (future: llama.cpp --cache-type-k q8_0)  │
│  Intermediate pipeline results / in-memory Postgres     │
├─────────────────────────────────────────────────────────┤
│ NVMe (4 TB)                                             │
│  Model weights (mmap — pages in as needed)              │
│  Postgres WAL + table data                              │
│  Pipeline outputs, compiled stream blocks               │
│  llama.cpp memory-mapped weights (fast random access)   │
└─────────────────────────────────────────────────────────┘
```

**For pipeline synthesis tasks, the right model is Qwen3.6-27B or 35B-A3B running via llama.cpp (not vLLM) with:**
- Model weights memory-mapped from NVMe (`--mmap` — default in llama.cpp)
- All layers that fit on VRAM loaded to GPU (`-ngl 99` or tune down for 35B-A3B)
- KV cache allocated in RAM for the extended context (`--cache-type-k q8_0` halves KV memory)
- No interactive stack competing for the same resources

This configuration can sustain 128K–256K context windows on the 3090 + 96GB DDR5 at reduced token/s — acceptable for a pipeline that runs while you sleep.

---

### Pipeline Mode vs Interactive Mode — Operational Pattern

Two runtime configurations. You don't run both simultaneously for synthesis jobs.

**Interactive mode** (default daytime config):
- vLLM #1: Qwen3.6-27B, `--max-model-len 32768`, `--enable-lora`, 3 LoRAs hot
- vLLM #2: Phi-4-mini, `--max-model-len 8192`
- LiteLLM routing all stacks
- Fast, responsive, loses most of the context window

**Pipeline mode** (scheduled, off-hours):
```bash
# Stop interactive stack to free VRAM
inference-down

# Launch pipeline model via llama.cpp with full context budget
llama-server \
  -hf Qwen/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
  -ngl 99 \
  -c 131072 \                          # 128K context — tune up/down based on job
  --cache-type-k q8_0 \               # halve KV cache VRAM cost
  --host 127.0.0.1 --port 8082 \
  -np 1 &                              # single parallel slot — pipeline is sequential

# n8n pipeline workflow hits http://127.0.0.1:8082/v1/chat/completions
# On completion, pipeline-down and inference-up
```

Or for jobs needing the full 256K native window (weekly synthesis, full-corpus analysis):
```bash
# 256K at q8_0 KV cache is ~8 GB KV + ~17 GB weights = ~25 GB — tight but possible
llama-server -hf Qwen/Qwen3.6-27B-GGUF:UD-Q4_K_XL -ngl 99 -c 262144 --cache-type-k q8_0 ...
# If OOM: reduce -ngl to offload some layers to RAM, or use 35B-A3B MoE (smaller active path)
```

**n8n orchestration for mode switching:**
```
[Trigger: 06:25 AM]
    → HTTP Request: POST /inference/pipeline-mode-on  (custom n8n webhook → script)
    → [all synthesis nodes run against llama-server:8082]
    → HTTP Request: POST /inference/pipeline-mode-off
    → [inference-up restores interactive stack]
```

The `~/bin/inference-up` and a new `~/bin/pipeline-mode` script handle the switch. Add to `~/bin/`:
```bash
#!/bin/bash
# pipeline-mode [on|off]
# on: stops interactive stack, starts llama-server with full context
# off: stops llama-server, starts interactive stack
```

---

### Fast Ingestion / Slow Synthesis — The Two-Layer Pipeline Pattern

The principle: **separate the data arrival rate from the synthesis quality.**

```
                    ┌─────────────────────────────────────┐
Incoming articles   │  INGESTION TIER (always-on, fast)   │
RSS / webhooks  ──► │  Phi-4-mini or Qwen3 1.7B           │
                    │  Tasks: classify, filter, score,     │
                    │  deduplicate, route to sector table  │
                    │  Latency target: <2s per article     │
                    └──────────────┬──────────────────────┘
                                   │ writes to news_unified (Postgres)
                                   ▼
                    ┌─────────────────────────────────────┐
Scheduled trigger   │  SYNTHESIS TIER (scheduled, slow)   │
06:25 AM daily  ──► │  Qwen3.6-27B at 128K–256K context   │
                    │  Tasks: sector synthesis, stream     │
                    │  compilation, cross-signal ID,       │
                    │  final brief assembly                │
                    │  Latency target: irrelevant          │
                    └──────────────┬──────────────────────┘
                                   │ writes to daily_stream_outputs
                                   ▼
                    ┌─────────────────────────────────────┐
Sunday 22:00    ──► │  RESTRUCTURING TIER (weekly, deep)  │
                    │  Qwen3.6-27B or 80B-A3B at 256K+    │
                    │  Tasks: Crossing Watch, Sector       │
                    │  Momentum, strategy conclusions,     │
                    │  update financial macro_signals      │
                    │  Latency target: irrelevant          │
                    └─────────────────────────────────────┘
```

**This pattern generalizes to all pipelines:**

| Pipeline | Ingestion tier (fast) | Synthesis tier (accurate) | Restructure cadence |
|---|---|---|---|
| News | Phi-4-mini classify/route | Qwen3.6-27B at 128K | Weekly: Crossing Watch |
| Financial | Minute-frame price feed + fast signal scoring (see below) | Qwen3.6-35B-A3B at 128K+ | End-of-day + weekly |
| Leads | Qwen3 0.6B triage | Qwen3.6-35B-A3B at 64K | Weekly: ICP drift, sequence QA |

The restructuring tier is where strategic conclusions are drawn — regime shifts, hedge adjustments, sector momentum reversals. These conclusions then become inputs to the ingestion and synthesis tiers in the next cycle (e.g., updated regime flag changes how incoming articles are scored).

---

### Financial Pipeline — Intraday Cycle in Detail

The financial pipeline has a more precisely defined cycle than the generic pattern above. Three distinct operational phases per trading day:

**Phase A — Pre-market strategy formation (before open)**

Runs against the full database. Qwen3.6-35B-A3B at maximum feasible context reads: overnight news signals from `macro_signals`, current regime classification, historical performance on similar setups, FRED snapshot, relevant sector moves from the morning brief. Output: a single named strategy for the day — specific stock(s), direction, entry/exit parameters, position size based on confidence and regime. This strategy is written to a `daily_strategy` record in Postgres before market open.

```
Pre-market run:
  Input: full database context (~128K token synthesis job)
  Output: daily_strategy record {stock, direction, entry, exit, size, confidence, regime_tag}
  Model: Qwen3.6-35B-A3B, pipeline mode, slow is fine
  Trigger: ~09:00 AM (before 09:30 open)
```

**Phase B — Intraday execution support (market open → close)**

The strategy is already formed. The ingestion tier's only job is to feed real-time price data to evaluate whether the strategy's conditions are being met — not to re-derive the strategy.

```
Intraday ingestion:
  Input: single stock price feed, 1-minute candles
  Model: small/fast — Llama 3.2 3B or even direct rule-based logic
  Tasks: compare current price to strategy parameters, score confidence
         that conditions still hold, flag if stop/target hit
  Latency target: <500ms per evaluation cycle
  Output: execution signal (hold / scale / exit) written to Postgres
```

The key design point: **the intraday model is not re-analyzing the world every minute**. It is asking a narrow question — "given the strategy we formed pre-market, does this price action still support it?" That question is fast, small, and doesn't require a large model.

**Phase C — End-of-day re-evaluation**

After close, the full synthesis tier runs again. This is not optional — it is the learning loop.

```
End-of-day synthesis:
  Input: today's strategy record, actual intraday execution log, open vs close,
         P&L result, any signals that fired during the day, macro_signals for today
  Model: Qwen3.6-35B-A3B at 128K+ context, pipeline mode
  Tasks: score the strategy's accuracy (was the pre-market read correct?),
         identify what worked vs what didn't, update success rate metrics,
         flag any regime or parameter drift for the weekly restructure
  Output: daily_strategy_result record written to Postgres
  Trigger: ~04:30 PM (after market close)
```

Over time the `daily_strategy_result` table becomes the primary training signal for improving the pre-market strategy formation. A run of failures on a specific setup type triggers a restructuring pass.

---

### ⚠️ Exception Handling — Fast-Moving Exogenous Signals

*This is a distinct design problem. It is not yet solved. Documented here as a known gap.*

**The problem:** The pre-market strategy assumes the conditions that existed at formation time persist through the trading day. Some events break that assumption catastrophically mid-session — not gradually, but in seconds:

- Trump Truth Social post (tariff announcement, trade deal, Fed comment)
- Geopolitical event (military escalation, sanctions, energy supply shock)
- Corporate event (surprise earnings, FDA decision, CEO departure, acquisition announcement)
- Fed official statement outside scheduled meetings

The intraday ingestion tier as designed above cannot handle these. It is asking "does price action still support the strategy?" — but if the strategy's underlying thesis just evaporated, the right answer is "exit immediately," not "price action is still within parameters."

**The gap:** There is currently no circuit-breaker layer between the Market Movers / news feed and the intraday execution logic. The news pipeline produces these signals (Stream B: Market Movers × Finance, Geopolitics × Finance) but the financial pipeline has no mechanism to receive them in real time during trading hours and act on them.

**Design direction (not yet built):**

```
Proposed circuit-breaker layer:

[Market Movers feed — continuous poll]
    │
    ▼
Fast classifier (Phi-4-mini or rule-based):
  "Does this event have potential to materially affect [today's stock/sector]?"
  Latency target: <3 seconds from post detection
    │
    ├── No → discard
    │
    └── Yes → ESCALATE
              │
              ▼
         Deeper analysis call (Qwen3.6-35B-A3B, ~30–60s, full context):
           Input: the event + today's strategy record + current position
           Output: HOLD / REDUCE / EXIT + confidence + reasoning
           Written to: circuit_breaker_events table
              │
              ▼
         Human alert (ntfy.sh push notification) + optional auto-action
         depending on confidence threshold and position size
```

**Key design constraints when this is built:**
- The escalation path must complete faster than the market can move on the signal. For Trump Truth Social posts on tariffs, the market moves in under 60 seconds from post detection. The classifier must fire in <3s. The deeper analysis is for position management, not initial reaction — by the time the 30-60s call completes, the first wave has already moved price.
- Initial reaction (first 30s): exit or reduce based on classifier output alone
- Sustained position management (30s–5min): use the deeper analysis output
- This is a risk management system, not a trading signal system — its job is to prevent losses, not generate alpha

**This is flagged as a separate architecture problem** to be designed when the base financial pipeline is stable and paper-trading. It requires its own design session.

---

### Open Items — Pipeline Inference Strategy

| Item | Status |
|---|---|
| `~/bin/pipeline-mode` script | ⬜ Write when inference stack is built |
| n8n mode-switch webhook pattern | ⬜ Design when first pipeline workflow is built |
| KV cache dtype benchmark (fp16 vs q8_0 vs q4_0 on 3090) | ⬜ Benchmark on first llama.cpp load |
| Confirm 128K context fits on 3090 with q8_0 KV cache | ⬜ Verify — math says yes, test to confirm |
| Confirm 256K context fits (tight — ~25 GB total) | ⬜ May need -ngl tuning to offload some layers |
| Circuit-breaker layer design (fast exogenous signals) | ⬜ Separate design session — after base financial pipeline stable |

---

## Phase 10 — Harness Layer

The harness is the agentic loop wrapping the inference engine: how it parses tool calls, manages context, dispatches subagents, and integrates with workflows. Different tiers need different harnesses depending on model strength and use context.

### Harness Tier Map (finalized in v6)

| Tier | Harness | Triggered by | Models | Role |
|---|---|---|---|---|
| Cloud premium | Claude Code | Manual (terminal) | Claude Opus 4.7 (Pro #1 personal / Pro #2 client) | High-stakes reasoning, client deliverables, multi-file refactors |
| Local agentic interactive | OpenCode TUI | Manual (terminal) | Qwen3.6-27B + LoRAs via LiteLLM | Sit-down delegation to local models |
| Local agentic headless | OpenCode `serve` HTTP | n8n webhooks, scheduled triggers, Funnel | Same models, same LiteLLM routing | Triggered/repeatable agentic workflows |
| Local deep-think specialist | Qwen Code CLI | Manual (terminal) for hard problems | Qwen3-Coder-Next 80B-A3B via llama.cpp | Privacy-first hard problem solving |
| Local lightweight | n8n + LiteLLM direct API | n8n triggers, schedules, Funnel webhooks | Qwen3.6-35B-A3B (cloud), Phi-4-mini, Llama 3.2 3B | Non-agentic structured generation |

### OpenCode Deployment

**Install (one-line):**
```bash
curl -fsSL https://opencode.ai/install | bash
# or via npm: npm install -g @opencode/cli
```

**Global config — `~/.config/opencode/opencode.jsonc`:**
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "providers": {
    "litellm": {
      "name": "Local LiteLLM Router",
      "type": "openai",
      "options": {
        "baseURL": "http://127.0.0.1:4000/v1",
        "apiKey": "${LITELLM_MASTER_KEY}"
      },
      "models": {
        "qwen3.6-consultancy": { "name": "Qwen3.6-27B Consultancy LoRA" },
        "qwen3.6-design":      { "name": "Qwen3.6-27B Design LoRA" },
        "qwen3.6-exploratory": { "name": "Qwen3.6-27B Exploratory Coding LoRA" },
        "phi4-mini":           { "name": "Phi-4-mini Utility" },
        "qwen-coder-deep":     { "name": "Qwen3-Coder-Next Deep Think" },
        "deepseek-v4-flash":   { "name": "DeepSeek V4 Flash (cloud)" },
        "kimi-k2.6":           { "name": "Kimi K2.6 (cloud, 1M ctx)" }
      }
    }
  },
  "model": "litellm/qwen3.6-exploratory",
  "small_model": "litellm/phi4-mini",
  "default_agent": "build",
  "permissions": {
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status": "allow",
      "git diff": "allow",
      "ls *": "allow",
      "cat *": "allow",
      "rm -rf *": "deny",
      "sudo *": "deny"
    }
  },
  "instructions": [
    "AGENTS.md",
    ".opencode/AGENTS.md"
  ]
}
```

**Per-project config — `<project>/.opencode/opencode.jsonc`:** overrides global where needed (model selection per project, project-specific MCP servers, project-specific permissions).

**Per-project context file — `<project>/AGENTS.md`:** the canonical project instructions file. CLAUDE.md should be a symlink to this so Claude Code and OpenCode read the same source-of-truth.
```bash
# In each project directory:
ln -s AGENTS.md CLAUDE.md
```

**Subagent definitions — `<project>/.opencode/agents/*.md`:**
```markdown
---
name: financial-backtest-runner
mode: subagent
hidden: true
model: litellm/deepseek-v4-flash
permissions:
  bash:
    "python *": allow
    "rm *": deny
---
You are a backtesting subagent. Given a strategy specification, generate the backtest code, execute it, and return summary statistics. Always validate input data shape before running. Never modify files outside /home/monarch/financial-pipeline/backtests/.
```

**Headless mode for n8n integration:**
```bash
# Single-shot prompt with JSON output
opencode run -p "Summarize this transcript: ..." --format json

# HTTP API server (better for n8n — avoids cold-start)
OPENCODE_SERVER_PASSWORD=$LITELLM_MASTER_KEY opencode serve --port 8090 --host 127.0.0.1
# Then n8n hits http://100.101.244.6:8090 with HTTP request nodes
```

### Qwen Code CLI Deployment

For the deep-think tier specifically (Qwen3-Coder-Next 80B-A3B via llama.cpp).

**Install:**
```bash
npm install -g @qwen/qwen-code
```

**Config — `~/.qwen/config.json`:**
```json
{
  "providers": {
    "local": {
      "type": "openai",
      "baseURL": "http://127.0.0.1:8081/v1",
      "apiKey": "EMPTY",
      "model": "qwen3-coder-next"
    }
  },
  "defaultProvider": "local"
}
```

**Workflow:** Bring up llama.cpp first (`qwen-coder-deep-up`), wait ~60s, then `qwen-code` for an interactive session. Tear down llama.cpp when done.

### Claude Code via Pro Authentication

Claude Code is already in use on Pro #1. Pro #2 setup:

```bash
# Pro #1 — already authenticated, used for personal/exploratory work
claude /login
# (existing session)

# Pro #2 — for client-facing consultancy work, use a separate user profile
mkdir -p ~/.claude-client
CLAUDE_CONFIG_DIR=~/.claude-client claude /login
# Authenticate with Pro #2 account

# Run Pro #2 by exporting CLAUDE_CONFIG_DIR before launching:
export CLAUDE_CONFIG_DIR=~/.claude-client
claude
```

Recommend wrapping in shell aliases:
```bash
# ~/.bashrc
# Pro #1 — personal/exploratory work. Uses default ~/.claude config dir.
alias claude-personal='CLAUDE_CONFIG_DIR=~/.claude-personal claude'
# Pro #2 — client-facing consultancy work only. Never route client work through claude-personal.
alias claude-client='CLAUDE_CONFIG_DIR=~/.claude-client claude'
```

> ✅ **W2.4 — Pro isolation verified May 14, 2026.**
> - `claude-personal` → `trent.dunkak@gmail.com` (Pro #1 — personal/exploratory)
> - `claude-client` → `tdunkak@gmail.com` (Pro #2 — client-facing only)
> - Aliases live in `~/.bashrc`. Checkpoint 12b passed.

### File System Convention — AGENTS.md / CLAUDE.md Migration

The AGENTS.md format is now an LF AAIF standard alongside MCP and Goose. It supports both Claude Code (via CLAUDE.md symlink) and OpenCode (native). One source of truth, two harnesses.

Per-project structure:
```
~/projects/<stack>/
├── AGENTS.md              # CANONICAL project context (symlinked to CLAUDE.md)
├── CLAUDE.md              # → AGENTS.md (symlink)
├── .opencode/
│   ├── opencode.jsonc     # OpenCode config (provider, model defaults, permissions)
│   ├── agents/            # subagent definitions (.md with frontmatter)
│   ├── skills/            # capability packages (progressive disclosure)
│   ├── commands/          # slash commands (.md files with bash !injection)
│   └── plugins/           # custom TS extensions if needed
└── .claude/
    ├── skills/            # → ../.opencode/skills (symlink — share skills)
    └── commands/          # Claude Code-specific commands if needed
```

Skill files are portable between Claude Code and OpenCode without modification — both support the `SKILL.md` progressive-disclosure pattern.

### Verification Checkpoints — Harness Layer

**Checkpoint 8 — OpenCode connects to LiteLLM:**
```bash
opencode models
# Expect: list of all models defined in opencode.jsonc, sourced from LiteLLM /v1/models
```

**Checkpoint 9 — OpenCode interactive session against local model:**
```bash
opencode --model litellm/qwen3.6-exploratory
# > "Read AGENTS.md and summarize this project in 3 sentences"
# Expect: coherent response that references actual AGENTS.md content
```

**Checkpoint 10 — OpenCode subagent dispatch:**
```bash
# In an OpenCode session with subagents defined:
# > "@financial-backtest-runner Run a quick mean-reversion backtest on AAPL"
# Expect: subagent invocation, with the subagent's system prompt visible in the trace
```

**Checkpoint 11 — OpenCode headless mode for n8n:**
```bash
opencode run -p "Classify this lead as cold/warm/hot: [text]" --format json --model litellm/phi4-mini
# Expect: clean JSON response, no ANSI codes, exits 0
```

**Checkpoint 12 — Claude Code Pro auth split:**
```bash
claude-personal /login    # confirms Pro #1
claude-client /login      # confirms Pro #2 (separate config dir)
```

### Failure Modes — Harness Layer

**Checkpoint 8 fails: OpenCode reports "no models found".**
- LiteLLM not running, or master key mismatch. Verify `curl http://127.0.0.1:4000/v1/models -H "Authorization: Bearer $LITELLM_MASTER_KEY"` works first (Checkpoint 4).
- If LiteLLM works but OpenCode fails: check `~/.config/opencode/opencode.jsonc` for typos in `baseURL` or env var expansion of `${LITELLM_MASTER_KEY}`.

**Checkpoint 9 fails: OpenCode session "model timeout" or "connection error".**
- The selected model's vLLM process may not be up. Check `tmux capture-pane -t inference:vllm1 -p | tail -20`.
- Increase OpenCode's request timeout in `opencode.jsonc`: `"options": { "timeout": 120000 }` (ms).

**Checkpoint 10 fails: subagent silently doesn't dispatch.**
- Subagent file must have YAML frontmatter (the `---` delimited block) with `name`, `mode: subagent`, and `model`. Missing fields silently fail.
- Subagent must be discoverable — check `.opencode/agents/<name>.md` is in the project directory or `~/.config/opencode/agents/<name>.md` for global.

**Checkpoint 11 fails: headless run produces ANSI escape codes in output.**
- Use `--quiet` (or `-q`) flag in addition to `--format json` to suppress spinner.
- For n8n shell-execution nodes, ensure `TERM=dumb` or `NO_COLOR=1` in env.

**Checkpoint 12 fails: Pro #2 login leaks into Pro #1 session.**
- Confirm `CLAUDE_CONFIG_DIR` is set BEFORE launching `claude`. After launch, the session is locked to whichever config dir was visible at startup.
- If credentials cross-contaminated: delete `~/.claude-client/credentials.json` and re-login.

### What's Still Pending After Phase 9 + 10

| Item | Blocked by | Priority |
|---|---|---|
| First end-to-end Checkpoint 1 (vLLM startup with real model) | Model file transfers (Phase 8) | 🔴 High |
| LoRA adapter files (qwen3.6-consultancy/design/exploratory) | LoRA training pipeline | 🔴 High |
| OpenCode skills migration from existing CLAUDE.md/SKILL.md across micro-saas, financial-pipeline, eeg-pipeline, leads, youtube-pipeline | File system architecture session (next) | 🟡 Medium |
| n8n workflow templates that hit LiteLLM | OpenCode `serve` smoke test | 🟡 Medium |
| Qwen Code CLI smoke test | llama.cpp build + first model load | 🟡 Medium |
| Claude Code Pro #2 separate config | One-time setup | 🟢 Low — 5 minutes when ready |

---

## Phase 11 — File System Architecture

> ⚠️ **Partially superseded by Phase 12 (v8).** CONSTITUTION.md is now the canonical source of truth. Both CLAUDE.md and AGENTS.md are symlinks to it. The skeleton below has been relabeled as the CONSTITUTION.md per-stack template. The migration script has been updated to operate on CONSTITUTION.md. If Phase 11 and Phase 12 appear to contradict each other, Phase 12 wins.

This section defines how project context, skills, agents, and commands are organized across the six stacks. It's the foundation that turns the harness + inference layers into productive work — without these files in place, OpenCode and Claude Code have no project context to operate against.

### Core Principles

1. **CONSTITUTION.md is canonical.** CLAUDE.md and AGENTS.md are both symlinks to CONSTITUTION.md (see Phase 12). CONSTITUTION.md is the LF AAIF standard anchor. Both harnesses read it transparently via their respective symlinks. One source of truth, multiple harnesses. *(Note: earlier versions of this section stated "AGENTS.md is canonical" — that was superseded in v8 when the CONSTITUTION/CONTEXT dual-file pattern was adopted.)*
2. **Three-tier skill hierarchy.** Global (`~/.opencode/skills/`) for capabilities every stack uses. Stack-isolated (`~/projects/<stack>/.opencode/skills/`) for stack-specific work. Substack-isolated (`~/projects/<stack>/.opencode/skills/<substack>/`) for sub-domain specialization. Two-level cap — anything deeper means the substack should be promoted to a peer.
3. **Promote-up at the 2+ stack threshold.** When a skill developed in one stack becomes useful in a second, it graduates to global. Each stack's `.opencode/skills/README.md` records promotion lineage so the history is preserved.
4. **Bottom-up skill resolution.** OpenCode resolves skills in order: substack → stack → global. Most specific wins. This means a stack can override a global skill with a stack-specific version without modifying the global.
5. **Six stacks only.** consultancy, exploratory-coding, design, content, leads, financial. Other projects (micro-saas, eeg-pipeline, ad-hoc work) live at `~/projects/<name>/` with the same internal layout but are out of scope for this iteration.

### Top-Level Directory Layout

```
~/
├── .config/
│   ├── opencode/
│   │   └── opencode.jsonc                # global OpenCode config
│   ├── claude-code/                      # global Claude Code config
│   └── inference/
│       └── api_keys.env                  # all API keys (chmod 600)
│
├── .opencode/                            # global skills/agents/commands
│   ├── skills/
│   │   ├── web-search-with-citations/
│   │   ├── markdown-document-creation/
│   │   ├── api-key-management/
│   │   ├── git-commit-conventions/
│   │   ├── litellm-routing/
│   │   ├── n8n-webhook-handling/
│   │   ├── error-tracing-python/
│   │   ├── tmux-session-management/
│   │   └── README.md                     # global skills index
│   ├── agents/
│   │   ├── researcher.md                 # general research subagent
│   │   ├── code-reviewer.md              # general code review subagent
│   │   └── README.md
│   └── commands/
│       ├── plan.md                       # /plan slash command
│       ├── review.md                     # /review slash command
│       └── README.md
│
├── projects/
│   ├── consultancy/                      ← stack
│   ├── exploratory-coding/               ← stack
│   ├── design/                           ← stack
│   ├── content/                          ← stack
│   ├── leads/                            ← stack
│   ├── financial/                        ← stack (replaces ~/financial-cowork/)
│   ├── _archive/                         ← retired projects
│   └── _shared-data/                     ← cross-stack data not specific to any stack
│       ├── client-context/               ← consultancy-only client info (gitignored)
│       └── reference-corpora/            ← shared training/eval data
│
├── loras/                                ← LoRA adapter weights
│   ├── qwen3.6-consultancy/
│   ├── qwen3.6-design/
│   ├── qwen3.6-exploratory/
│   ├── qwen3.6-content/                  # on Qwen3.6-35B-A3B base when trained
│   └── qwen3.6-leads/                    # on Qwen3.6-35B-A3B base when trained
│
├── venv/inference/                       ← Phase 7
├── llama.cpp/                            ← Phase 7
├── n8n/                                  ← Phase 5 (docker-compose lives here)
├── litellm/
│   └── config.yaml                       ← Phase 9
├── bin/                                  ← shell scripts (inference-up, etc.)
└── html-guides/                          ← reference HTML guides (transferred)
```

### Per-Stack Project Layout (uniform across all six)

```
~/projects/<stack>/
├── AGENTS.md                             ← CANONICAL project context
├── CLAUDE.md                             → AGENTS.md (symlink)
├── .opencode/
│   ├── opencode.jsonc                    ← stack-specific config (model defaults, permissions, MCP)
│   ├── skills/                           ← stack-isolated skills
│   │   ├── README.md                     ← skills index + promotion lineage
│   │   ├── <stack-specific-skill-1>/
│   │   │   └── SKILL.md
│   │   ├── <substack-1>/                 ← substack directory
│   │   │   ├── README.md
│   │   │   ├── <substack-skill-1>/
│   │   │   │   └── SKILL.md
│   │   │   └── <substack-skill-2>/
│   │   │       └── SKILL.md
│   │   └── <substack-2>/
│   │       └── ...
│   ├── agents/                           ← stack-specific subagents
│   │   ├── README.md
│   │   ├── <agent-1>.md
│   │   └── <agent-2>.md
│   ├── commands/                         ← stack-specific slash commands
│   │   ├── README.md
│   │   ├── <command-1>.md
│   │   └── <command-2>.md
│   └── plugins/                          ← TS plugins (rare, only if needed)
├── .claude/                              ← Claude Code-specific overrides (mostly empty)
│   └── skills/                           → ../.opencode/skills (symlink, share skills)
├── data/                                 ← stack data (gitignored if sensitive)
├── outputs/                              ← stack deliverables
├── scripts/                              ← stack-specific Python/bash scripts
├── .env                                  ← stack-scoped env vars (chmod 600)
└── .gitignore
```

### Symlink Convention

Every stack creates two symlinks at setup time. CONSTITUTION.md is the source of truth; both harness-specific names point to it:

```bash
cd ~/projects/<stack>
ln -s CONSTITUTION.md CLAUDE.md     # CONSTITUTION → Claude Code alias
ln -s CONSTITUTION.md AGENTS.md     # CONSTITUTION → OpenCode/AAIF alias
mkdir -p .claude
ln -s ../.opencode/skills .claude/skills  # share skills between Claude Code and OpenCode
```

The `.claude/skills` symlink means any skill you write once is accessible to both harnesses. Same for global skills — Claude Code reads `~/.claude/skills` if it exists, OpenCode reads `~/.opencode/skills`. Symlink one to the other or duplicate both as links to a single source.

### CONSTITUTION.md Skeleton (per-stack template)

> This is the template for each stack's CONSTITUTION.md — the permanent anchor document. 300–500 words. Anti-goals and non-negotiables must be explicit. CLAUDE.md and AGENTS.md are both symlinks to this file.

```markdown
# <Stack Name> — Project Context

## Purpose
<One paragraph: what this stack does, who it serves, what success looks like>

## Active Workflows
- <workflow 1 name>: <one-line description>
- <workflow 2 name>: <one-line description>

## Models & Routing
- Primary local model: <e.g., litellm/qwen3.6-consultancy>
- Cloud fill: <e.g., Claude Pro #2 for client deliverables, DeepSeek V4 Flash for bulk reasoning>
- Forbidden routes: <e.g., "Never route client work through Pro #1">

## Skill Inventory
### Stack-isolated
- <skill 1>: <purpose>
### Substacks
- <substack 1>: <purpose>
  - <substack skill A>: <purpose>

## Agent Inventory
- <agent 1>: <when to invoke>

## Commands
- /<command 1>: <what it does>

## File Locations
- Inputs: <where data comes from>
- Outputs: <where deliverables go>
- Sensitive data: <what's gitignored, what's encrypted>

## Conventions
- <convention 1>: <e.g., "All deliverables timestamp-prefixed YYYY-MM-DD">
- <convention 2>: <e.g., "Client work uses Pro #2 only">

## Known Limitations
- <limitation 1>: <e.g., "Local model has no knowledge of post-Jan 2026 markets — use DeepSeek for current data">
- <limitation 2>: <e.g., "LoRA was trained on 2024-2025 data; sanity-check brand-voice consistency on first use">

## Pending / Open Questions
- <item 1>
- <item 2>
```

### Per-Stack Architecture

#### Consultancy

**Purpose:** Client-facing AI consulting deliverables. Audit reports, AI readiness assessments, implementation roadmaps, training materials.

**Substacks:**
- `client-deliverables/` — templated outputs (audit report, readiness assessment, roadmap)
- `methodology/` — your consultancy methodology codified as skills (intake process, gap analysis, ROI calc)
- `industry-knowledge/` — vertical-specific skills (small business AI, mid-market integration patterns)

**Models & Routing:**
- Primary local: `litellm/qwen3.6-consultancy` (Qwen3.6-27B + consultancy LoRA) for drafting and routine work
- Cloud fill: Claude Pro #2 ONLY for client-facing deliverables (never Pro #1)
- Forbidden: routing client data through DeepSeek/Kimi without explicit client approval; routing client work through Pro #1

**Sample agents:**
- `client-intake-summarizer.md` — given a client intake form, produce structured summary + initial gap analysis
- `deliverable-quality-reviewer.md` — read a draft deliverable, flag issues against your methodology checklist
- `methodology-codifier.md` — when you describe a new pattern, generate a skill file capturing it

**Sample commands:**
- `/intake <client-name>` — runs intake skill against `data/clients/<client-name>/intake.md`
- `/draft-readiness-assessment <client-name>` — generates first draft using methodology skills
- `/review-for-client <file>` — runs deliverable-quality-reviewer agent

**Sensitive data handling:** All client data lives in `~/projects/_shared-data/client-context/<client-name>/` (gitignored, chmod 700). Stack scripts reference by relative path. Never commit client identifiers, contracts, or intake content.

**LoRA training data source:** Anonymized past consulting deliverables, methodology documents, your own client communications (with PII scrubbed). Should be 200-500 high-quality examples.

#### Exploratory Coding

**Purpose:** Personal R&D coding work, technical experiments, debugging deep-dives, infrastructure exploration. Not client-facing.

**Substacks:**
- `infrastructure/` — workstation maintenance, deployment automation, monitoring
- `pipelines/` — n8n workflow development, LiteLLM config evolution, OpenCode skill authoring
- `experiments/` — short-lived spike code that may not survive

**Models & Routing:**
- Primary local: `litellm/qwen3.6-exploratory` (Qwen3.6-27B + exploratory LoRA) for routine code work
- Deep-think tier: `litellm/qwen-coder-deep` (Qwen3-Coder-Next 80B-A3B via llama.cpp, on-demand) for hard problems
- Cloud fill: Claude Pro #1 (Claude Code) for architectural decisions, multi-file refactors, "I'm stuck"
- DeepSeek V4 Flash for bulk reasoning where privacy doesn't matter

**Sample agents:**
- `infrastructure-changes-reviewer.md` — before applying any change to inference stack, verify against §16 verification checkpoints
- `error-trace-analyzer.md` — given a Python traceback, identify root cause and suggest fix
- `n8n-workflow-builder.md` — given a workflow spec, generate the JSON workflow definition

**Sample commands:**
- `/verify-stack` — runs Phase 9 verification checkpoints sequentially, reports which fail
- `/new-skill <name>` — scaffolds a new global or stack skill with SKILL.md template
- `/spike <description>` — creates a new experiment under `experiments/<date>-<slug>/`

**Forbidden:** Never use Claude Pro #2 from within this stack — that account is reserved for client work. If you accidentally launch it, exit immediately.

**LoRA training data source:** Your own past exploratory code, debugging logs, infrastructure documentation (this master_summary itself is high-signal training data), Python scripts you've written. 300-800 examples.

#### Design

**Purpose:** Visual asset generation for client work and personal content. Image prompts, video prompts, brand-voice copy, social asset templates.

**Substacks:**
- `image-generation/` — Nano Banana Pro / Flux 1.1 Pro / Replicate prompts and pipelines
- `video-generation/` — Higgsfield / Veo 3.1 / Kling 3.0 / WAN 2.6 self-hosted
- `voice-and-music/` — Chatterbox + Fish Audio S1 + Udio
- `brand-systems/` — visual identity, color systems, typography references

**Models & Routing:**
- Primary local: `litellm/qwen3.6-design` (Qwen3.6-27B + design LoRA, leverages native vision for screenshot review)
- Cloud fill: Claude Pro #2 for client copy and brand voice, Pro #1 for personal content
- Tools (not models): Nano Banana Pro, Flux, Higgsfield, Veo, Kling, WAN, Chatterbox, Fish, Udio, Pika 2.0

**Sample agents:**
- `prompt-craftsperson.md` — given a desired output description, generate detailed image/video prompts in the format the target tool expects
- `brand-voice-checker.md` — given draft copy, assess against brand voice rules and flag deviations
- `asset-pipeline-runner.md` — given a content brief, orchestrate full image+video+voice pipeline

**Sample commands:**
- `/prompt-image <description>` — generates Nano Banana Pro prompt
- `/prompt-video <description>` — generates Veo or Kling prompt depending on style
- `/brand-check <file>` — runs brand-voice-checker

**Substack: image-generation specific skills:**
- `nano-banana-pro-prompt-format/SKILL.md`
- `flux-1.1-pro-prompt-format/SKILL.md`
- `80s-penthouse-aesthetic/SKILL.md` (your established style for ambient content)

**LoRA training data source:** Your own past prompts (with outputs as evaluation data), brand-voice documents, your established style anchors (Patrick Nagel + Syd Mead style references). 200-400 examples.

#### Content

**Purpose:** Personal content generation pipeline — Instagram, YouTube ambient, blog drafts, affiliate content. Bulk generation tier where throughput matters more than per-piece quality.

**Substacks:**
- `instagram/` — carousel pipeline, caption generation, hashtag strategy
- `youtube-ambient/` — fantasy study vibes / dark academia content (formerly `youtube-pipeline`)
- `blog-drafts/` — long-form drafts, affiliate content
- `audience-capture/` — off-platform email/newsletter content (Instagram-algo hedge)

**Models & Routing:**
- Primary local: `litellm/qwen3.6-content` (Qwen3.6-35B-A3B + content LoRA, MoE for speed)
- Cloud fill: Claude Pro #1 for weekly batch QA pass and brand-voice synthesis (rare — high-leverage moments only)
- Utility tier: Phi-4-mini for trend classification, Qwen3 1.7B for hashtag generation

**Sample agents:**
- `instagram-carousel-drafter.md` — given a topic, produce 5-slide carousel + caption
- `weekly-content-batch-reviewer.md` — read all week's drafts, flag any that diverge from house style
- `youtube-prompt-generator.md` — given a session theme, produce Nano Banana Pro prompt for thumbnail + ambient style guide

**Sample commands:**
- `/draft-carousel <topic>` — runs instagram-carousel-drafter
- `/batch-review` — weekly QA pass over `outputs/<current-week>/`
- `/youtube-session <theme>` — generates full session brief

**Substack: instagram specific skills:**
- `carousel-format-rules/SKILL.md`
- `caption-hook-patterns/SKILL.md`
- `affiliate-disclosure-format/SKILL.md`

**LoRA training data source:** Your past Instagram captions, YouTube descriptions, blog drafts. 500-1000 examples (this is the highest-volume LoRA — more data is fine because the throughput tier benefits from broad coverage).

#### Leads

**Purpose:** Lead generation pipeline. ICP qualification, outreach sequence generation, lead enrichment, response classification. Almost entirely automated — minimal manual touch.

**Substacks:**
- `icp-qualification/` — Ideal Customer Profile filters, scoring rubrics
- `outreach/` — message sequences, follow-up cadences, A/B variants
- `enrichment/` — public-data scraping (LinkedIn, company sites) + Postgres ingestion
- `response-handling/` — classify replies as interested/not-interested/auto-reply/spam

**Models & Routing:**
- Primary local: `litellm/qwen3.6-leads` (Qwen3.6-35B-A3B + leads LoRA)
- Utility tier: Phi-4-mini (filter/classify), Qwen3 0.6B (triage)
- Cloud fill: rare — leads work shouldn't burn Claude tokens. Emergency only: Pro #1 for tricky response handling.

**Sample agents:**
- `icp-scorer.md` — given lead data, return score 0-100 with reasoning
- `outreach-message-drafter.md` — given lead + sequence stage, produce personalized message variant
- `response-classifier.md` — given inbound reply, return category + suggested next action

**Sample commands:**
- `/score-leads <file>` — batch ICP scoring of CSV
- `/draft-sequence <icp-segment>` — generates 5-message sequence for a segment
- `/triage-replies` — runs response-classifier over latest n8n-fetched inbound batch

**Forbidden:** Never store full LinkedIn profile data unencrypted at rest; respect rate limits; no impersonation in outreach.

**LoRA training data source:** Your past outreach messages (with conversion outcomes as eval signal), ICP rubric documents, response classification examples. 300-500 examples.

#### Financial

**Purpose:** Personal financial pipeline. Bayesian/Monte Carlo analysis, portfolio decisions, paper-trading toward auto-trade, baseball analytics (MiroFish), market regime detection. Personal, not for sale.

**Substacks:**
- `data-sourcing/` — SEC EDGAR, FRED, FMP, Finnhub, Alpha Vantage integrations (replaces `~/financial-cowork/`)
- `analysis/` — Bayesian inference, Monte Carlo simulations, regime detection logic
- `backtesting/` — strategy testing infrastructure, performance metrics
- `prediction-markets/` — MiroFish (Kalshi prediction market simulation)
- `morning-briefs/` — daily summary generation pipeline
- `news-signals/` ⬜ *Planned* — ingestion point for cross-sector signals from the News Pipeline (Stream B compilations → position sizing inputs; Stream A AI signals → infrastructure decision feed)

**Models & Routing:**
- Primary local orchestrator: `litellm/qwen3.6-content` (Qwen3.6-35B-A3B, reuses content LoRA for speed) — note this stack does NOT have its own LoRA
- Notebook/code generation: `litellm/qwen3.6-exploratory` (reuses exploratory LoRA)
- Cloud fill: DeepSeek V4 Flash API for cheap heavy reasoning + 1M-context backtests
- Sanity checks: Claude Pro #1 (rare — only when an analysis result feels suspicious)

**Sample agents:**
- `morning-brief-generator.md` — pulls overnight market data, runs analysis pipeline, produces daily summary
- `backtest-runner.md` — given strategy spec, generates code, executes, returns stats
- `regime-classifier.md` — given current market data, classify regime + confidence

**Sample commands:**
- `/morning-brief` — runs full morning pipeline (n8n-triggered nightly via cron, or manual)
- `/backtest <strategy-name>` — runs backtest-runner against `analysis/strategies/<strategy-name>/`
- `/regime-check` — current regime classification with reasoning

**Cowork migration:** `~/financial-cowork/` is deprecated. Migration steps:
```bash
# Move data
mv ~/financial-cowork/data ~/projects/financial/data
mv ~/financial-cowork/notebooks ~/projects/financial/scripts/legacy-notebooks
# Migrate API keys to consolidated location
cat ~/financial-cowork/.env >> ~/.config/inference/api_keys.env
chmod 600 ~/.config/inference/api_keys.env
# Validate keys are present
grep -E "^(FMP_API_KEY|FINNHUB_API_KEY|ALPHAVANTAGE_API_KEY)=" ~/.config/inference/api_keys.env
# After verification: rm -rf ~/financial-cowork
```

**No dedicated LoRA:** Financial reuses content LoRA for orchestration prose and exploratory LoRA for code generation. Reason: financial domain is too dynamic for a LoRA to stay current; better to lean on retrieval (skills + recent data) than baked-in priors. Revisit if a specific financial sub-domain stabilizes enough to merit a dedicated LoRA.

### Global Skills Inventory (initial)

These belong at `~/.opencode/skills/`:

| Skill | Used by | Purpose |
|---|---|---|
| web-search-with-citations | all stacks | Search web with proper citation formatting |
| markdown-document-creation | all stacks | Standardized MD output formatting |
| api-key-management | all stacks | Reference patterns for `~/.config/inference/api_keys.env` |
| git-commit-conventions | exploratory-coding, content, leads | Commit message format, branching |
| litellm-routing | all stacks | How to address models via LiteLLM, fallback chains |
| n8n-webhook-handling | leads, financial, content | Standard webhook patterns |
| error-tracing-python | exploratory-coding, financial | Python traceback analysis |
| tmux-session-management | exploratory-coding | Session conventions for inference stack |

Each global skill lives at `~/.opencode/skills/<skill-name>/SKILL.md` with progressive disclosure — short top-level description, expandable detail, examples.

### Promote-Up Convention

When a skill in one stack becomes useful in a second:

1. **First use** — skill lives in originating stack: `~/projects/<stack-A>/.opencode/skills/<skill-name>/SKILL.md`
2. **Second stack discovers need** — that stack's owner adds an entry to the second stack's `skills/README.md` noting "consider promoting `<skill-name>` from `<stack-A>`"
3. **Promotion** — when ready: move the skill to `~/.opencode/skills/<skill-name>/`, leave a stub `<stack-A>/.opencode/skills/_promoted/<skill-name>.md` pointing to the new location, update the `<stack-A>/.opencode/skills/README.md` to note "→ promoted to global on YYYY-MM-DD"
4. **Provenance preserved** — the global skill's `SKILL.md` includes a `lineage:` field in frontmatter showing which stack it originated from

This means at any point you can answer "where did this skill come from, and which stacks depend on it?" by reading the global skill's lineage and the stacks' `_promoted/` directories.

### Migration Plan from Existing Files

Your existing CLAUDE.md/SKILL.md infrastructure across `financial-pipeline`, `leads`, and `youtube-pipeline` projects needs to migrate. Plan:

| Existing | New location | Notes |
|---|---|---|
| `~/projects/financial-pipeline/CLAUDE.md` | `~/projects/financial/AGENTS.md` (rename + symlink CLAUDE.md → AGENTS.md) | Rename project directory |
| `~/projects/financial-pipeline/SKILL.md` and any skills/ | `~/projects/financial/.opencode/skills/` | Restructure with substacks |
| `~/financial-cowork/` | `~/projects/financial/data/` + scripts | See Cowork migration block above |
| `~/projects/leads/CLAUDE.md` | `~/projects/leads/AGENTS.md` (symlink) | No rename needed |
| `~/projects/leads/SKILL.md` | `~/projects/leads/.opencode/skills/` | Restructure |
| `~/projects/youtube-pipeline/CLAUDE.md` | `~/projects/content/AGENTS.md` (symlink) — youtube-pipeline becomes a substack of content | Rename project, content stack absorbs it |
| `~/projects/youtube-pipeline/SKILL.md` | `~/projects/content/.opencode/skills/youtube-ambient/` | Becomes the youtube-ambient substack |
| Existing global skills (premium-frontend, free-data-sourcing, skill-creator, web-artifacts-builder) | `~/.opencode/skills/<name>/` | Move as-is; OpenCode SKILL.md format is compatible with Claude Code's |
| `~/projects/micro-saas/` | unchanged, out of scope | Independent project, keeps current structure |
| `~/projects/eeg-pipeline/` | unchanged, out of scope | Independent project, keeps current structure |

**Migration script template:**
```bash
#!/bin/bash
# ~/bin/migrate-stack
# Usage: migrate-stack <old-name> <new-name>
set -e
OLD=$1
NEW=$2
cd ~/projects
[ -d "$OLD" ] || { echo "$OLD not found"; exit 1; }
[ -d "$NEW" ] && { echo "$NEW already exists, aborting"; exit 1; }
mv "$OLD" "$NEW"
cd "$NEW"
# Phase 12 model: CONSTITUTION.md is canonical. CLAUDE.md and AGENTS.md are both symlinks.
# If an old flat CLAUDE.md exists (Phase 11 era), rename it to CONSTITUTION.md.
if [ -f CLAUDE.md ] && [ ! -L CLAUDE.md ]; then
  mv CLAUDE.md CONSTITUTION.md
fi
# If an old flat AGENTS.md exists (Phase 11 era), absorb or remove it.
if [ -f AGENTS.md ] && [ ! -L AGENTS.md ]; then
  echo "WARNING: standalone AGENTS.md found — review and merge into CONSTITUTION.md manually"
fi
# Create canonical symlinks (Phase 12)
[ -L CLAUDE.md ] || ln -s CONSTITUTION.md CLAUDE.md
[ -L AGENTS.md ] || ln -s CONSTITUTION.md AGENTS.md
# Create .opencode/ skeleton
mkdir -p .opencode/{skills,agents,commands,plugins}
mkdir -p .claude
[ -L .claude/skills ] || ln -s ../.opencode/skills .claude/skills
# Move existing SKILL.md if present
[ -f SKILL.md ] && mv SKILL.md .opencode/skills/legacy-skill.md
echo "Migrated $OLD → $NEW. Verify CONSTITUTION.md content (300-500 words, anti-goals explicit)."
```

### Verification Checkpoints — File System Layer

Run after migration is complete.

**Checkpoint 13 — All six stacks exist with canonical structure:**
```bash
for stack in consultancy exploratory-coding design content leads financial; do
  echo "=== $stack ==="
  test -f ~/projects/$stack/CONSTITUTION.md && echo "  ✓ CONSTITUTION.md" || echo "  ✗ CONSTITUTION.md MISSING"
  test -L ~/projects/$stack/CLAUDE.md && echo "  ✓ CLAUDE.md → CONSTITUTION.md" || echo "  ✗ CLAUDE.md symlink broken"
  test -L ~/projects/$stack/AGENTS.md && echo "  ✓ AGENTS.md → CONSTITUTION.md" || echo "  ✗ AGENTS.md symlink broken"
  test -f ~/projects/$stack/.opencode/opencode.jsonc && echo "  ✓ opencode.jsonc" || echo "  ✗ opencode.jsonc MISSING"
  test -d ~/projects/$stack/.opencode/skills && echo "  ✓ skills/" || echo "  ✗ skills/ MISSING"
  test -L ~/projects/$stack/.claude/skills && echo "  ✓ .claude/skills symlink" || echo "  ✗ .claude/skills symlink broken"
done
```

**Checkpoint 14 — Symlink integrity (no broken links):**
```bash
find ~/projects -maxdepth 4 -type l ! -exec test -e {} \; -print
# Expect: empty output. Any output = broken symlink.
```

**Checkpoint 15 — OpenCode discovers stack context:**
```bash
cd ~/projects/consultancy
opencode --model litellm/qwen3.6-consultancy
# > "Read AGENTS.md and tell me what this project is for"
# Expect: response that references actual AGENTS.md content
```

**Checkpoint 16 — Claude Code reads same context via symlink:**
```bash
cd ~/projects/consultancy
claude-client
# > "Read CLAUDE.md and tell me what this project is for"
# Expect: same response as Checkpoint 15 (proves canonical/symlink works)
```

**Checkpoint 17 — Global skills accessible from a stack:**
```bash
cd ~/projects/leads
opencode --model litellm/qwen3.6-leads
# > "Use the web-search-with-citations skill to find current LinkedIn API rate limits"
# Expect: skill is discovered and invoked despite living at ~/.opencode/skills/, not in this project
```

**Checkpoint 18 — Substack skill resolution:**
```bash
cd ~/projects/design
opencode --model litellm/qwen3.6-design
# > "Use the nano-banana-pro-prompt-format skill to generate a prompt for an 80s penthouse interior"
# Expect: skill resolves from .opencode/skills/image-generation/nano-banana-pro-prompt-format/
```

**Checkpoint 19 — Sensitive data isolation:**
```bash
ls -la ~/projects/_shared-data/client-context 2>/dev/null && stat -c "%a" ~/projects/_shared-data/client-context
# Expect: 700 permissions
ls -la ~/.config/inference/api_keys.env && stat -c "%a" ~/.config/inference/api_keys.env
# Expect: 600 permissions
git -C ~/projects/consultancy status --ignored | grep -q "_shared-data" && echo "✓ client data gitignored" || echo "✗ CLIENT DATA NOT GITIGNORED"
```

### Failure Modes — File System Layer

**Checkpoint 13 fails: AGENTS.md missing in a stack.**
- Run `~/bin/migrate-stack <old> <new>` if migration was incomplete.
- For new stacks (no migration source): copy the AGENTS.md skeleton from this document and fill in for the stack.
- For exploratory-coding (no prior project): skeleton-only start is fine; AGENTS.md grows as you use the stack.

**Checkpoint 13 fails: CLAUDE.md symlink broken.**
- `cd ~/projects/<stack> && rm -f CLAUDE.md && ln -s AGENTS.md CLAUDE.md`
- If symlink kept reverting: check whether some script (perhaps an old Claude Code init) is recreating CLAUDE.md as a real file.

**Checkpoint 14 fails: broken symlinks reported.**
- Common cause: project directory was renamed but symlinks pointed at old path.
- Fix: `find ~/projects -type l ! -exec test -e {} \; -delete` to remove broken links, then recreate per the standard layout.

**Checkpoint 15 fails: OpenCode doesn't read AGENTS.md.**
- Confirm `opencode.jsonc` has `"instructions": ["AGENTS.md"]` (global config or per-project).
- Confirm `cd` was into the project directory before launching OpenCode (it reads project context relative to cwd).
- Restart OpenCode session after any config change.

**Checkpoint 16 fails: Claude Code can't read CLAUDE.md.**
- If symlink: confirm `cat ~/projects/<stack>/CLAUDE.md` works from shell. If shell can read it, Claude Code can too.
- If response references wrong content: you may have a stale AGENTS.md from migration. Compare to what Checkpoint 15 returned.

**Checkpoint 17 fails: global skill not discovered.**
- Confirm `~/.opencode/skills/web-search-with-citations/SKILL.md` exists.
- Confirm OpenCode's global config has `"instructions": [..., "~/.opencode/skills/index.md"]` or skill discovery is enabled by default.
- Try invoking by full path: "Use the skill at ~/.opencode/skills/web-search-with-citations/".

**Checkpoint 18 fails: substack skill not resolved.**
- Skill resolution is bottom-up. If invoked from stack root, OpenCode may need the path: "Use the image-generation/nano-banana-pro-prompt-format skill".
- Add a `skills/index.md` per stack listing all skills with paths so the model can discover them by name without remembering the substack hierarchy.

**Checkpoint 19 fails: client data not gitignored or wrong permissions.**
- Add `_shared-data/client-context/` to `~/projects/consultancy/.gitignore` (and any other stack that touches client data).
- Run `chmod -R 700 ~/projects/_shared-data/client-context` and `chmod 600 ~/.config/inference/api_keys.env`.
- Audit recent git commits: `cd ~/projects/consultancy && git log --all --diff-filter=A -- 'client*' '*intake*'` — if any client data was committed, force-rewrite history before pushing anywhere remote.

### Setup Sequence — From Scratch

For each stack, the setup sequence is:

```bash
# 1. Create directory structure
cd ~/projects
mkdir -p <stack>/.opencode/{skills,agents,commands,plugins}
mkdir -p <stack>/.claude
mkdir -p <stack>/{data,outputs,scripts}

# 2. Create canonical context files
cd <stack>
touch AGENTS.md  # fill from skeleton
ln -s AGENTS.md CLAUDE.md
ln -s ../.opencode/skills .claude/skills

# 3. Create stack-scoped configs
cat > .opencode/opencode.jsonc <<EOF
{
  "$schema": "https://opencode.ai/config.json",
  "model": "litellm/qwen3.6-<stack>",
  "small_model": "litellm/phi4-mini",
  "instructions": ["AGENTS.md"]
}
EOF

# 4. Create skills/agents/commands READMEs (empty indices)
echo "# <Stack> Skills Index" > .opencode/skills/README.md
echo "# <Stack> Agents Index" > .opencode/agents/README.md
echo "# <Stack> Commands Index" > .opencode/commands/README.md

# 5. Create .gitignore
cat > .gitignore <<EOF
.env
data/sensitive/
_shared-data/client-context/
*.key
*.pem
__pycache__/
.venv/
EOF

# 6. Initial git commit (optional but recommended)
git init && git add -A && git commit -m "Initial scaffold for <stack>"
```

A `~/bin/scaffold-stack <stack-name>` script encapsulating these steps is worth writing once and using for any future scaffolding.

### What's Still Pending After Phase 11

| Item | Blocked by | Priority |
|---|---|---|
| First migration run (financial-pipeline → financial, including Cowork retirement) | None — can proceed now | 🔴 High |
| Per-stack AGENTS.md content authored from skeletons | Migration | 🔴 High |
| Migration of existing skills into new substack hierarchy | Migration | 🔴 High |
| Initial global skills moved into `~/.opencode/skills/` | Migration | 🟡 Medium |
| Sample agents and commands populated per stack | AGENTS.md content | 🟡 Medium |
| Original deliverable: per-stack guide synthesizing harness + LoRA + file-system | Phase 11 complete (this section) | 🟢 Now unblocked |
| LoRA training data assembly per stack | Per-stack AGENTS.md content (defines what success looks like) | 🟡 Medium — depends on first deliverable |

---

## Phase 12 — Context System

### Design Philosophy
Sourced from `~/Desktop/Context_soln/context-system-setup-claude-code.md` — a context persistence system built and tested in April 2026. Adopted as the standard for all six stacks.

**The core principle:** Lean mandatory load, precise positional state, on-demand reference. Every session starts fast because Claude only reads what it must read, not everything.

### Two-File Architecture (replaces flat AGENTS.md)

Every project directory has two canonical context files:

**CONSTITUTION.md** — The permanent anchor.
- Read at every session start. Always. No exceptions.
- Never updated casually — only when the project fundamentally changes direction.
- Contains: what this project is fundamentally building, core approach, non-negotiable constraints, architectural decisions that do not change, anti-goals, quality bar, how Claude operates here.
- Target length: 300–500 words. Short enough to read instantly, dense enough to actually orient.

**CONTEXT.md** — The living state document.
- Read at every session start after CONSTITUTION.md.
- Updated by checkpoint compression during sessions and by `/wrap` at session end.
- Contains: active phase, current state (what's built and working), current blockers, key decisions log, terminology, last session summary, checkpoint log, next starting point.
- The "Next Starting Point" field is the most important — written so Claude can begin immediately without clarifying questions.

**The distinction:** CONSTITUTION answers "what are we building and why." CONTEXT answers "where are we right now and what's next."

### Symlink Convention (unchanged from v7)
```bash
# CONSTITUTION.md is the source of truth
# CONTEXT.md is the mutable layer
# CLAUDE.md symlinks to CONSTITUTION.md for Claude Code compatibility
# AGENTS.md symlinks to CONSTITUTION.md for OpenCode compatibility
ln -s CONSTITUTION.md CLAUDE.md
ln -s CONSTITUTION.md AGENTS.md
```

### Session Start Protocol (Claude Code)
Defined in CLAUDE.md addition block. Mandatory order:
1. Read CONSTITUTION.md in full
2. Read CONTEXT.md in full
3. Check claude_mem for cached reference docs (Claude Code only)
4. Phase-activate: read the current phase's reference doc in full; all others via claude_mem summaries only

### Checkpoint Compression (mid-session)
At every natural phase completion boundary — not session end:
- Write compressed summary of what was completed
- Append to CONTEXT.md under "Checkpoint Log"
- Update "Current State" and "Active Phase" fields
- Confirm: "Checkpoint written to CONTEXT.md"

**Do not wait until session end to checkpoint.** Capture while context is clean.

### `/wrap` Command (session end, Claude Code)
User types `/wrap`. Claude executes:
1. Review full session
2. Write comprehensive CONTEXT.md update (completed, decisions, state, blockers, updated phase, next starting point)
3. Present as proposed update: `FIELD / UPDATE` format
4. Awaits: ACCEPT (writes to disk), EDIT, or REJECT

### Recovery Patch (abrupt session end, Claude Code)
At session start, Claude checks whether CONTEXT.md "Last Updated" matches most recent claude_mem timestamp. If gap detected: queries claude_mem for missed observations, proposes recovery patch in same `/wrap` format.

### `claude_mem` Caveat — Claude Code Only
`claude_mem` is Claude Code's built-in mechanical session capture. It supplements CONSTITUTION/CONTEXT with automatic observation logging. **OpenCode does not have claude_mem.** For OpenCode sessions: CONSTITUTION.md + CONTEXT.md are the complete context system. No recovery patch available — the `/wrap` discipline is the only safety net. Implication: always run `/wrap` before closing an OpenCode session; no automatic fallback exists.

### 80% Context Warning
At approximately 80% context utilization: stop at logical boundary, run checkpoint compression, notify user. Do not produce `/wrap` summaries above 90% utilization — quality degrades significantly.

### Model Routing (Claude Code)
| Task Type | Model |
|---|---|
| Complex architectural decisions | Opus — flag to user before switching |
| Deep analysis, probability systems, financial modeling | Opus |
| Active building, code generation, debugging | Sonnet (default) |
| Checkpoint compression, `/wrap` summaries | Sonnet |

Never switch models automatically — flag and let user decide.

### 7-Document Rubric System
Every new pipeline or tool built in any stack follows this rubric. Sourced from financial-pipeline/CLAUDE.md where it is fully implemented. Missing docs surface as a checkpoint at session start and before new builds — not a hard block, but user must explicitly choose how to proceed.

| # | Doc | Purpose |
|---|---|---|
| 1 | `PRD.md` | Purpose, boundary, success metrics |
| 2 | `AppFlow_&_Design.md` | Data flow, interaction, output design |
| 3 | `Architecture_&_Backend.md` | Stack, folder structure, data model, env vars |
| 4 | `AIRules_&_Quality.md` | Coding standards, data quality gates |
| 5 | `Plan.md` | Phased execution roadmap with granular checklists |
| 6 | `Security_Checklist.md` | API key hygiene, data protection |
| 7 | `Changelog.md` | Decision log — what changed, why, what was ruled out |

The Changelog.md "Ruled-Out Features Log" is permanent — never delete entries. Check it before adding any new module or data source to prevent re-proposing already-rejected ideas.

### OpenCode Config Addition (`opencode.jsonc`)
```jsonc
{
  "instructions": ["CONSTITUTION.md", "CONTEXT.md"],
  "model": "litellm/<stack-model>",
  "small_model": "litellm/phi4-mini"
}
```
Both files load at every session start. No phase-activation logic in OpenCode (that's Claude Code-specific). All reference docs must be explicitly invoked via slash commands or agent instructions.

---

## Phase 13 — Migration Execution

### Ground Truth (from May 13 inventory session)

**Actual source locations on monarch:**
```
~/Desktop/
├── ClaudeSkills/          ← empty scaffold
├── CONTENTGEN/            ← Content stack — 10 Python scripts + assets
│   └── python_scripts/    ← pipeline variants (pipeline.py, shorts, steam, dark_academia, etc.)
├── Context_soln/          ← CONSTITUTION/CONTEXT templates + 3 workflow contexts
│   ├── ClientWF_ExplorativeCode/  CONSTITUTION.md + CONTEXT.md
│   ├── ContentGen_LeadGen/        CONSTITUTION.md + CONTEXT.md
│   └── FinancialAnalysis_RWTrading/ CONSTITUTION.md + CONTEXT.md
├── ExpCode/               ← empty scaffold
├── Headquarters/          ← empty scaffold
├── html-guides/           ← transferred from MacBook
├── LeadGen/               ← empty scaffold
├── plan/                  ← planning docs (review before archiving)
├── projects/
│   ├── financial-pipeline/ ← REAL WORK — CLAUDE.md, .env, skill ZIP, folder structure
│   ├── leads/              ← leads-CLAUDE.md, .claude/settings.json
│   ├── micro-saas/         ← out of scope
│   ├── micro-saa/          ← out of scope
│   └── [others]
├── WebDesign/             ← empty scaffold
└── Workflows/             ← empty scaffold
```

**Target location:** `~/projects/` (to be created)

### Migration Source → Target Mapping

| Source | Target | Type | Notes |
|---|---|---|---|
| `~/Desktop/projects/financial-pipeline/` | `~/projects/financial/` | Migrate | Real work — backup first |
| `~/Desktop/projects/leads/` | `~/projects/leads/` | Migrate | Minimal content |
| `~/Desktop/CONTENTGEN/python_scripts/` | `~/projects/content/scripts/youtube-ambient/` | Migrate | 10 Python scripts |
| `~/Desktop/Context_soln/FinancialAnalysis_RWTrading/` | `~/projects/financial/` | Merge | CONSTITUTION.md + CONTEXT.md content |
| `~/Desktop/Context_soln/ContentGen_LeadGen/` | `~/projects/content/` + `~/projects/leads/` | Split | Separate CONSTITUTION/CONTEXT per stack |
| `~/Desktop/Context_soln/ClientWF_ExplorativeCode/` | `~/projects/consultancy/` + `~/projects/exploratory-coding/` | Split | Separate CONSTITUTION/CONTEXT per stack |
| `~/Desktop/Headquarters/` | `~/projects/consultancy/` | Scaffold | Empty — start fresh |
| `~/Desktop/ExpCode/` | `~/projects/exploratory-coding/` | Scaffold | Empty — start fresh |
| `~/Desktop/WebDesign/` | `~/projects/design/` | Scaffold | Empty — start fresh |
| `~/Desktop/ClaudeSkills/` | `~/.opencode/skills/` | Review + migrate | Check contents first |
| `~/Desktop/html-guides/` | `~/projects/content/reference/html-guides/` | Move | Reference material |

### Special Handling — `free-data-sourcing.skill`

The `~/Desktop/projects/financial-pipeline/free-data-sourcing.skill` is a **ZIP package** (confirmed by `PK` magic bytes), not a plain text file. Migration requires:

```bash
# Create target skills directory
mkdir -p ~/projects/financial/.opencode/skills/

# Unzip the skill package into skills directory
unzip ~/Desktop/projects/financial-pipeline/free-data-sourcing.skill \
  -d ~/projects/financial/.opencode/skills/

# Verify extraction
ls ~/projects/financial/.opencode/skills/free-data-sourcing/
# Expect: SKILL.md (at minimum)
```

After verifying the skill works in the financial stack, evaluate whether it qualifies for promotion to `~/.opencode/skills/` (global). Given it's used in both financial and leads stacks, it meets the 2+ stack threshold for promote-up.

### Special Handling — `.env` Key Migration

Financial pipeline `.env` contains 8 keys (all free tier):
```
FMP_API_KEY, FINNHUB_API_KEY, ALPHAVANTAGE_API_KEY, EIA_API_KEY,
NEWSAPI_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
```

Migration path:
```bash
# Create secure config directory
mkdir -p ~/.config/inference
touch ~/.config/inference/api_keys.env
chmod 600 ~/.config/inference/api_keys.env

# Append financial keys with section header
echo "# Financial Pipeline — Data APIs" >> ~/.config/inference/api_keys.env
grep -v '^#' ~/Desktop/projects/financial-pipeline/.env >> ~/.config/inference/api_keys.env

# Verify permissions
stat -c "%a" ~/.config/inference/api_keys.env
# Expect: 600
```

The migrated `~/projects/financial/.env` should source from the central file:
```bash
# ~/projects/financial/.env
source ~/.config/inference/api_keys.env
```

### Migration Sequence (ordered by blast radius)

**Step 1 — Create target structure (zero risk)**
```bash
mkdir -p ~/projects/{consultancy,exploratory-coding,design,content,leads,financial}
mkdir -p ~/projects/{consultancy,exploratory-coding,design,content,leads,financial}/.opencode/{skills,agents,commands,plugins}
mkdir -p ~/projects/{consultancy,exploratory-coding,design,content,leads,financial}/.claude
echo "Target structure created"
find ~/projects -maxdepth 2 -type d | sort
```

**Step 2 — Migrate financial-pipeline (backup first)**
```bash
# Backup
tar -czf ~/financial-pipeline-backup-$(date +%Y%m%d).tar.gz ~/Desktop/projects/financial-pipeline/
echo "Backup created: ~/financial-pipeline-backup-$(date +%Y%m%d).tar.gz"

# Copy real work (preserve originals on Desktop until verification)
cp -r ~/Desktop/projects/financial-pipeline/pipelines ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/ingestion ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/processing ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/analysis ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/visualization ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/lib ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/configs ~/projects/financial/
cp -r ~/Desktop/projects/financial-pipeline/output ~/projects/financial/
cp ~/Desktop/projects/financial-pipeline/.gitignore ~/projects/financial/

# Migrate skill (ZIP extraction)
unzip ~/Desktop/projects/financial-pipeline/free-data-sourcing.skill \
  -d ~/projects/financial/.opencode/skills/

echo "Financial pipeline migrated. Verify before removing Desktop source."
```

**Step 3 — Create CONSTITUTION.md and CONTEXT.md for financial stack**

Source content from:
- `~/Desktop/Context_soln/FinancialAnalysis_RWTrading/CONSTITUTION.md` → `~/projects/financial/CONSTITUTION.md`
- `~/Desktop/Context_soln/FinancialAnalysis_RWTrading/CONTEXT.md` → `~/projects/financial/CONTEXT.md`
- Merge `~/Desktop/projects/financial-pipeline/CLAUDE.md` content → into CONSTITUTION.md (session protocol, rubric system, hard rules, architecture)

```bash
cp ~/Desktop/Context_soln/FinancialAnalysis_RWTrading/CONSTITUTION.md ~/projects/financial/CONSTITUTION.md
cp ~/Desktop/Context_soln/FinancialAnalysis_RWTrading/CONTEXT.md ~/projects/financial/CONTEXT.md
# Then manually merge financial-pipeline/CLAUDE.md content into CONSTITUTION.md
# (session start protocol, rubric system, data architecture, hard rules)
```

**Step 4 — Create symlinks**
```bash
cd ~/projects/financial
ln -s CONSTITUTION.md CLAUDE.md
ln -s CONSTITUTION.md AGENTS.md
ln -s ../.opencode/skills .claude/skills
echo "Symlinks created"
ls -la ~/projects/financial/
```

**Step 5 — Migrate leads**
```bash
cp ~/Desktop/projects/leads/leads-CLAUDE.md ~/projects/leads/CONSTITUTION.md
cp ~/Desktop/Context_soln/ContentGen_LeadGen/CONSTITUTION.md ~/projects/leads/CONSTITUTION-ref.md
cp ~/Desktop/Context_soln/ContentGen_LeadGen/CONTEXT.md ~/projects/leads/CONTEXT.md
# Manually merge leads-CLAUDE.md content + ContentGen CONSTITUTION leads section
# into ~/projects/leads/CONSTITUTION.md
cd ~/projects/leads
ln -s CONSTITUTION.md CLAUDE.md
ln -s CONSTITUTION.md AGENTS.md
```

**Step 6 — Migrate CONTENTGEN scripts to content stack**
```bash
mkdir -p ~/projects/content/scripts/youtube-ambient
cp ~/Desktop/CONTENTGEN/python_scripts/*.py ~/projects/content/scripts/youtube-ambient/
cp ~/Desktop/CONTENTGEN/pipeline-2.py ~/projects/content/scripts/youtube-ambient/
echo "CONTENTGEN scripts migrated"
ls ~/projects/content/scripts/youtube-ambient/
```

**Step 7 — Scaffold fresh stacks (no migration source)**
```bash
# These were empty on Desktop — scaffold from template only
for stack in consultancy exploratory-coding design content; do
  touch ~/projects/$stack/CONSTITUTION.md
  touch ~/projects/$stack/CONTEXT.md
  ln -s CONSTITUTION.md ~/projects/$stack/CLAUDE.md
  ln -s CONSTITUTION.md ~/projects/$stack/AGENTS.md
  ln -s ../.opencode/skills ~/projects/$stack/.claude/skills 2>/dev/null || true
  # Create opencode.jsonc
  cat > ~/projects/$stack/.opencode/opencode.jsonc <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "instructions": ["CONSTITUTION.md", "CONTEXT.md"],
  "model": "litellm/qwen3.6-${stack//-/}",
  "small_model": "litellm/phi4-mini"
}
EOF
done
echo "Fresh stacks scaffolded"
```

**Step 8 — Context_soln content → remaining stacks**
```bash
# Consultancy gets ClientWF CONSTITUTION content
cp ~/Desktop/Context_soln/ClientWF_ExplorativeCode/CONSTITUTION.md \
  ~/projects/consultancy/CONSTITUTION-ref.md
cp ~/Desktop/Context_soln/ClientWF_ExplorativeCode/CONTEXT.md \
  ~/projects/consultancy/CONTEXT.md
# Manually extract consultancy-relevant content from ClientWF CONSTITUTION

# Exploratory coding similarly
cp ~/Desktop/Context_soln/ClientWF_ExplorativeCode/CONSTITUTION.md \
  ~/projects/exploratory-coding/CONSTITUTION-ref.md
```

**Step 9 — API key migration**
```bash
mkdir -p ~/.config/inference
touch ~/.config/inference/api_keys.env
chmod 600 ~/.config/inference/api_keys.env
echo "# Financial Pipeline — Data APIs (migrated $(date))" >> ~/.config/inference/api_keys.env
grep -v '^#' ~/Desktop/projects/financial-pipeline/.env | \
  grep -v '^$' >> ~/.config/inference/api_keys.env
stat -c "%a" ~/.config/inference/api_keys.env
# Expect: 600
```

**Step 10 — Verify**
Run Checkpoints 13–19 from Phase 11 against the migrated structure.

### Post-Migration Cleanup (only after verification passes)
```bash
# Archive Desktop scaffold directories (don't delete yet)
mkdir -p ~/Desktop/_migrated
mv ~/Desktop/ExpCode ~/Desktop/Headquarters ~/Desktop/WebDesign \
   ~/Desktop/ClaudeSkills ~/Desktop/Workflows ~/Desktop/_migrated/

# Keep ~/Desktop/projects/financial-pipeline/ and ~/Desktop/CONTENTGEN/ 
# until verified working in new location (30-day retention)
echo "Cleanup complete. Original sources retained in ~/Desktop/projects/ for 30 days."
```

### Leads Stack — Note on Paid Tools
`~/Desktop/projects/leads/leads-CLAUDE.md` references apollo, zoominfo, and common-room as plugins. These are **paid tools not currently active** — they appear to be aspirational/planned integrations. The ref-blueprint specifies free-only scraping (Google Maps API, Instagram, Facebook scrapers). Do not treat apollo/zoominfo/common-room as current infrastructure. They can remain as documented future options in the leads CONSTITUTION.md under "Planned Integrations."

### Migration Status Tracker

| Stack | Scaffold | CONSTITUTION | CONTEXT | Skills | Symlinks | Verified |
|---|---|---|---|---|---|---|
| financial | ⬜ | ⬜ | ⬜ | ⬜ (ZIP) | ⬜ | ⬜ |
| leads | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| content | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| consultancy | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| exploratory-coding | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| design | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

Update this table as migration steps complete.

---

## Phase 14 — Operational Tooling & Security Hardening

*Completed May 14, 2026*

### n8n Encryption Key — Secured

- Key extracted from running Docker volume: `docker exec n8n-n8n-1 cat /home/node/.n8n/config`
- Saved to 1Password Private vault as `monarch — n8n Encryption Key`
- Added to `~/n8n/docker-compose.yml` under `N8N_ENCRYPTION_KEY=` so future container rebuilds use the same key
- **Recovery procedure:** If n8n container is ever rebuilt, ensure `N8N_ENCRYPTION_KEY` is set in docker-compose.yml before starting. Without it, all stored credentials (API keys, SMTP, Postgres passwords) are permanently unrecoverable.

### Tailscale Funnel — Webhook-Only

**Before:** `/ → proxy http://127.0.0.1:5678` (entire n8n exposed publicly)

**After:** `/ → proxy http://127.0.0.1:5678/webhook/` (webhook handler only)

```bash
# Current configuration (Tailscale v1.96.4)
tailscale funnel --bg http://127.0.0.1:5678/webhook/
```

- n8n UI now accessible only via Tailscale: `http://100.101.244.6:5678`
- `/webhook-test/` intentionally not exposed — only needed during active development when already on Tailscale. Use internal address: `http://100.101.244.6:5678/webhook-test/...`
- Public hostname unchanged: `https://monarch-b650i-lightning-wifi.tail89cb86.ts.net`
- **Note:** Tailscale v1.96.4 supports only one funnel target at a time. Path-based multi-rule syntax from older docs does not work on this version.

> ✅ **W2.3 — Tailscale pinned May 14, 2026.** `sudo apt-mark hold tailscale` confirmed. Monthly SOP check: `curl -I https://monarch-b650i-lightning-wifi.tail89cb86.ts.net/` should return 404 on root.

### Postgres Backup Cron

```bash
# Script: ~/bin/pg-backup
# Schedule: nightly at 2am
# Retention: 7 days
# Log: ~/backups/postgres/backup.log
0 2 * * * /home/monarch/bin/pg-backup >> /home/monarch/backups/postgres/backup.log 2>&1
```

Backup procedure:
```bash
docker exec n8n-postgres-1 pg_dump -U n8n n8n | gzip > ~/backups/postgres/n8n_YYYYMMDD_HHMMSS.sql.gz
```

To restore from backup:
```bash
gunzip -c ~/backups/postgres/n8n_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i n8n-postgres-1 psql -U n8n n8n
```

### ~/bin/ Operational Scripts

```
~/bin/
├── inference-up      # Startup orchestration — sources api_keys.env, starts n8n + Tailscale
├── pg-backup         # Postgres backup — run by cron nightly at 2am
├── restore-drill     # Monthly restore verification — spins up throwaway container, verifies 79 tables, tears down
└── qwen-coder-deep-up / qwen-coder-deep-down  # On-demand llama.cpp deep-think (Phase 9)
```

`~/bin/` added to PATH in `~/.bashrc`. Active after next login or `source ~/.bashrc`.

**inference-up current state (verified May 14, 2026):**
```bash
#!/bin/bash
# Taolen Logic — Monarch Startup Script
# Run after boot to bring up inference stack and funnel
echo "[$(date)] Starting inference stack..."
# Load secrets — must happen before any service that needs them
set -a
source ~/.config/inference/api_keys.env
set +a
echo "✓ Environment loaded"
# n8n + Postgres — bring up if not already running
cd ~/n8n && docker compose up -d
echo "✓ n8n + Postgres started"
# Tailscale Funnel — webhook-only public exposure
tailscale funnel --bg http://127.0.0.1:5678/webhook/
echo "✓ Tailscale Funnel started"
# TODO: vLLM #1 (Qwen3.6-27B + LoRAs) — add when model is loaded
# TODO: vLLM #2 (Phi-4-mini) — add when model is loaded
# TODO: LiteLLM proxy — add when config is written
echo "[$(date)] Startup complete."
```

⚠️ **Status: Partial.** Secrets loading, n8n + Postgres, and Tailscale Funnel are live and tested. vLLM and LiteLLM start commands are still TODO — populate as inference stack is built out in Phase 9.

### monarch-startup.service (systemd)

```ini
[Unit]
Description=Monarch Inference Stack Startup
After=network-online.target tailscaled.service docker.service
Wants=network-online.target

[Service]
Type=oneshot
User=monarch
ExecStart=/home/monarch/bin/inference-up
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Status: **enabled** — runs `inference-up` on every boot after network, Tailscale, and Docker are ready.

### File System Migration — Completed

| Stack | CONSTITUTION | CONTEXT | Skills | Symlinks |
|---|---|---|---|---|
| financial | ✅ 135 lines | ✅ | ✅ free-data-sourcing extracted | ✅ |
| leads | ✅ 64 lines | ✅ | ⬜ | ✅ |
| content | ✅ 89 lines | ✅ | ✅ 10 Python scripts migrated | ✅ |
| consultancy | ✅ 83 lines | ✅ | ⬜ | ✅ |
| exploratory-coding | ✅ 76 lines | ✅ | ⬜ | ✅ |
| design | ✅ 80 lines | ✅ | ⬜ | ✅ |

**Financial pipeline directories migrated:** pipelines/, ingestion/, processing/, analysis/, visualization/, lib/, configs/, output/

**API keys centralised:** `~/.config/inference/api_keys.env` (chmod 600)
Keys present: FMP_API_KEY, FINNHUB_API_KEY, ALPHAVANTAGE_API_KEY, EIA_API_KEY, NEWSAPI_API_KEY
Keys missing (were commented in original): REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT — add manually when available.

**CONTENTGEN scripts migrated:** 10 Python scripts to `~/projects/content/scripts/youtube-ambient/`
(mux.py, normalize_audio.py, pipeline.py, pipeline_1.py, pipeline1.py, pipeline-2.py, pipeline_dark_academia.py, pipeline_steam.py, pipeline_steam_1.py, shorts_pipeline.py)

**free-data-sourcing skill:** Extracted from ZIP to `~/projects/financial/.opencode/skills/free-data-sourcing/SKILL.md`. Candidate for promotion to global skills (~/.opencode/skills/) — meets 2+ stack threshold (financial + leads).

### Open Items Remaining

| Item | Status |
|---|---|
| Reddit API keys | ⬜ Add to ~/.config/inference/api_keys.env manually |
| free-data-sourcing promote to global | ⬜ After verifying it works in financial stack |
| All 6 CONSTITUTION files | ✅ Verified May 14, 2026 — all genuine (64–135 lines) |
| Inference stack (Phase 9) | ⬜ vLLM, llama.cpp, LiteLLM — next major work item |
| OpenCode installation | ⬜ Required before local agentic sessions |

---

## Phase 15 — News Pipeline

*Phase 1 (schema + ingestion) COMPLETE May 15, 2026 | Phase 2 (automated ingestion) COMPLETE May 15, 2026 | Phase 3 ARCHITECTURE PIVOTED to hybrid T2+Cowork — Stage 2 VALIDATED May 17, 2026, Stages 3-5 next | Stack connections: ⬜ Planned (not yet wired)*

---

### Overview

The News Pipeline produces a daily intelligence brief via hierarchical LLM synthesis. Raw articles are pulled from Postgres (`news_unified`), synthesized per-sector in parallel, compiled into two topical streams, then assembled into a final document with cross-stream signals and action items.

**It is currently a standalone system.** Future integration with the financial pipeline and AI infrastructure decisions is planned and documented in §Future Integration Surface below — but no wiring is built yet.

**Daily stats:**
| Metric | Value |
|---|---|
| n8n trigger | 06:25 AM daily |
| Total API calls | 12 |
| Estimated tokens/day | ~28,950 |
| Wall time (parallel) | ~3–4 minutes |
| Output | Daily Brief (markdown) + compiled blocks in Postgres |

---

### Architecture — Dual-Stream Hierarchical Synthesis

```
news_unified (Postgres)
│
├── STREAM A ─── AI / Technology
│   ├── AI/Tech synthesis call
│   ├── China AI synthesis call
│   └── Research/GitHub synthesis call
│             └── Stream A compilation call ──────────────┐
│                                                          │
└── STREAM B ─── Political / Financial                    │
    ├── Finance synthesis call                            │
    ├── Quant synthesis call                              │
    ├── Geopolitics synthesis call                        │
    ├── US Legislative synthesis call                     │
    ├── Quantum synthesis call                            │
    └── Market Movers synthesis call                      │
              └── Stream B compilation call ──────────────┤
                                                          │
                                            Final Assembly call
                                            (+ FRED + system status)
                                                          │
                                                    Daily Brief
```

**Why two streams:** Stream A (AI/Tech) and Stream B (Political/Financial) require fundamentally different synthesis logic — different "What It Means" frames, different signal types, and different time sensitivity. Keeping them separate means each stream's compilation prompt is purpose-built. Cross-stream relationships (AI × Finance, AI × Geopolitics) are surfaced exclusively in the final assembly step.

| | Stream A | Stream B |
|---|---|---|
| "What It Means" frame | Model capability, architecture implications, competitive landscape, local stack impact | Market risk, regulatory exposure, portfolio signal, consulting opportunity |
| Signal types | Releases, benchmarks, GitHub velocity, research papers | Price moves, legislation, executive actions, geopolitical events |
| Time sensitivity | Hours to days | Minutes to hours |

---

### Stream A — AI / Technology

#### Sectors

| Sector | Sources | Top-N pulled |
|---|---|---|
| AI/Tech Core | Anthropic, OpenAI, DeepMind, Meta AI, HuggingFace, Axios Generate, HackerNews filtered | top-8 |
| China AI | DeepSeek, Qwen, Moonshot/Kimi, ZhipuAI, 01.AI, Baichuan | top-8 |
| Research / GitHub | Papers with Code, GitHub Org Release Monitor, GitHub Star Velocity, Subquadratic | top-8 |

China AI is a separate sector (not folded into AI/Tech Core) because developments there carry different implications for the local model stack — a Qwen update is an infrastructure decision trigger, not just a competitor note.

Research/GitHub surfaces pre-commercial signal: what becomes mainstream in 30–90 days.

#### n8n Flow
```
[Trigger 06:25 AM]
    │
    ├── Postgres query: AI/Tech top-8
    ├── Postgres query: China AI top-8
    └── Postgres query: Research/GitHub top-8
         │
         ├── AI/Tech synthesis call      ─┐
         ├── China AI synthesis call      ├── parallel
         └── Research/GitHub synth call  ─┘
                    │
              Stream A compilation call
                    │
             stream_a_block.json (→ stored in daily_stream_outputs)
```

#### Stream A Compilation Logic

```
Input: three sector blocks (AI/Tech, China AI, Research/GitHub)

Tasks:
1. Identify any Chinese AI development that directly impacts the local model stack
   (Qwen updates, DeepSeek releases, architecture advances from Research sector)
2. Identify any research-to-commercial pipeline signals
   (GitHub star spike or paper that will become a lab announcement within weeks)
3. Flag any competitive capability shift between US labs and Chinese labs
4. Write the compiled AI section: sector blocks in order, followed by
   a single "AI Landscape Note" paragraph (2-3 sentences max) only if a
   cross-sector pattern within Stream A is present. Omit if no pattern.
```

---

### Stream B — Political / Financial

#### Sectors

| Sector | Sources | Top-N pulled |
|---|---|---|
| Finance / Markets | Reuters Markets, FT, FMP, Finnhub, AlphaVantage, NewsAPI, FRED | top-8 |
| Quant | Virtu, Jane Street, Two Sigma/DE Shaw (via Reuters filter), Chinese quant funds | top-6 |
| Geopolitics | BBC World, Al Jazeera, CFR, AP, Axios World, Politico EU, EU Commission | top-8 |
| US Legislative | GovTrack, ProPublica Congress, White House, Federal Register, Politico RSS, AP Politics | top-8 |
| Quantum Computing | Google Quantum, IBM Quantum, IonQ, Rigetti | top-5 |
| Market Movers | Trump Truth Social/Reuters fallback, Elon Musk, Buffett 13F, Ackman, Dalio | top-6 |

#### n8n Flow
```
[Trigger 06:25 AM — parallel with Stream A]
    │
    ├── Postgres query: Finance top-8
    ├── Postgres query: Quant top-6
    ├── Postgres query: Geopolitics top-8
    ├── Postgres query: US Legislative top-8
    ├── Postgres query: Quantum top-5
    └── Postgres query: Market Movers top-6
         │
         ├── Finance synthesis call       ─┐
         ├── Quant synthesis call          │
         ├── Geopolitics synthesis call    ├── parallel
         ├── US Legislative synth call     │
         ├── Quantum synthesis call        │
         └── Market Movers synth call     ─┘
                    │
              Stream B compilation call
                    │
             stream_b_block.json (→ stored in daily_stream_outputs)
```

#### Stream B Compilation Logic

```
Input: six sector blocks (Finance, Quant, Geopolitics, US Legislative, Quantum, Market Movers)

Tasks:
1. Check Market Movers against Finance and Geopolitics:
   - Did any Market Mover statement appear within 2 hours of a Finance or Geopolitics move?
   - If yes: flag as potential causal pair. Note in compilation.
2. Check US Legislative against Finance:
   - Any bill, executive order, or regulatory filing that directly affects a sector
     covered in Finance (banking, semiconductors, energy, trade)?
3. Check Geopolitics against Finance:
   - Trade policy, sanctions, tariffs, or diplomatic events with market implications?
4. Write the compiled Political/Financial section: sector blocks in order, followed by
   a "Cross-Sector Signals" subsection only if causal pairs were identified.
   This subsection feeds the weekly Crossing Watch — write in the same format.

Cross-Sector Signal format:
  **[Sector A] × [Sector B]:** {what happened} | {causal link confidence: high/medium/speculative}
```

---

### Final Assembly Call

Receives `stream_a_block.json` + `stream_b_block.json` + FRED snapshot + system status.

```
Input: Stream A block, Stream B block, FRED data, system status

Tasks:
1. Write the document header (date, source count, system status one-liner)
2. Insert Stream A section
3. Insert Stream B section
4. Write the "Cross-Stream Signals" block — the ONLY place AI × Finance or
   AI × Geopolitics crossings are identified. Look for:
   - Any AI development (Stream A) that has a regulatory response in Stream B
   - Any geopolitical move (Stream B) that directly affects AI lab operations (Stream A)
   - Any financial move (Stream B) driven by AI capability news (Stream A)
5. Extract action items from both streams (time-sensitive items only).
6. Append FRED macro snapshot at bottom of Finance section (not a separate section).
```

**Token budget (final assembly):**

| Component | ~Tokens |
|---|---|
| Stream A block | ~1,200 |
| Stream B block | ~2,800 |
| FRED + system status | ~150 |
| System prompt | ~200 |
| Output | ~600 |
| **Total** | **~4,950** |

---

### Full Token Budget Summary

| Step | Calls | ~Tokens Each | Total | Parallel? |
|---|---|---|---|---|
| Stream A: sector synthesis | 3 | ~1,700 | ~5,100 | ✅ Yes |
| Stream B: sector synthesis | 6 | ~1,700 | ~10,200 | ✅ Yes |
| Stream A: compilation | 1 | ~3,200 | ~3,200 | — |
| Stream B: compilation | 1 | ~5,500 | ~5,500 | ✅ (with Stream A compile) |
| Final assembly | 1 | ~4,950 | ~4,950 | — |
| **Daily total** | **12 calls** | — | **~28,950** | — |

Wall time: ~3–4 minutes across two parallel sector-synthesis waves, two parallel compilation calls, one final assembly.

---

### Sector Synthesis Prompt Variants

Not all sectors use the same prompt template. Two variants handle different signal types:

**Variant A — Event-based sectors** (Finance, Geopolitics, US Legislative, Market Movers, AI/Tech, China AI):
Standard raw→meaning format. Facts first, then implications. Tone: institutional, direct.

**Variant B — Low-volume, high-signal sectors** (Quantum, Quant, Research/GitHub):
```
Modified prompt: "This sector produces low daily volume. If fewer than 3 qualifying
articles were found, write a brief 'Signal Status' note explaining the quiet period
rather than forcing a What It Means section from thin material. A quiet week in Quantum
is meaningful information — do not pad it."
```

This prevents the model from generating plausible-sounding but thin synthesis on low-volume days. Silence is signal.

---

### Postgres Storage Schema

Compiled blocks are stored in Postgres — not just passed between n8n nodes. This enables the weekly synthesis to query them reliably and provides an audit trail.

```sql
CREATE TABLE IF NOT EXISTS daily_stream_outputs (
    id              SERIAL PRIMARY KEY,
    output_date     DATE NOT NULL,
    stream          TEXT NOT NULL,       -- 'A' or 'B'
    sector          TEXT,                -- NULL for compiled/assembly outputs
    stage           TEXT NOT NULL,       -- 'sector_synthesis' | 'compilation' | 'assembly'
    content         TEXT NOT NULL,       -- the markdown block
    token_count     INTEGER,
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON daily_stream_outputs (output_date, stream, stage);
```

Weekly synthesis query (reads last 7 days of compiled blocks):
```sql
-- Stream A compiled blocks for past 7 days
SELECT output_date, content
FROM daily_stream_outputs
WHERE stream = 'A'
  AND stage = 'compilation'
  AND output_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY output_date ASC;
```

---

### Weekly Synthesis — How the Hierarchy Carries Forward

The weekly document reads already-compiled stream blocks — not raw articles — keeping token costs flat regardless of source volume.

```
[Trigger Sunday 22:00]
    │
    ├── Read 7 × stream_a_block (daily AI sections from daily_stream_outputs)
    │        └── Weekly Stream A synthesis call → weekly_ai_section
    │
    ├── Read 7 × stream_b_block (daily Pol/Fin sections)
    │        └── Weekly Stream B synthesis call → weekly_polyfin_section
    │
    ├── Read sector_state.json (pre-computed velocity metrics)
    │
    └── Weekly Final Assembly call
            Input: weekly_ai_section + weekly_polyfin_section
                   + sector_state.json + last week's Crossing Watch
            Output: full weekly document including Sector Momentum + Crossing Watch
```

**The Crossing Watch** accumulates:
- Cross-sector signals flagged in 7 × Stream B daily compilations
- Cross-stream signals flagged in 7 × daily final assemblies
- New patterns identified by the weekly assembly looking across all of the above

The weekly assembly doesn't start from scratch — it inherits already-flagged signals from the daily pipeline and decides which ones have developed into confirmed crossings over the week.

---

### Future Integration Surface

**Status: ⬜ Planned — none of the below is built yet. The news pipeline runs standalone until explicitly connected.**

Three integration points are anticipated. Each will require explicit wiring work when the time comes.

---

#### Integration 1 — AI Infrastructure Maintenance (Stream A → AI stack)

**What it means:** The news pipeline's Stream A already tracks Qwen, DeepSeek, and lab announcements that directly affect the local model stack. Today those insights stay inside the daily brief. The planned integration surfaces them as structured signals that can trigger stack review tasks.

**Future wiring pattern:**
- Stream A compilation call already flags Chinese AI developments that "directly impact your local model stack" (see compilation logic above)
- Planned: a post-compilation n8n step that parses these flags and creates structured records in a `stack_signals` table
- Planned: a weekly review task (OpenCode or manual) that reads `stack_signals` and produces a list of model stack decisions to evaluate (upgrade Qwen, re-benchmark, adjust LoRA training data, etc.)
- Long-term: Stream A signals feed the financial stack's AI infrastructure cost model (model API pricing changes, new open-weight models that could replace paid API calls)

**Connection point in this document:** §Financial stack → `data-sourcing/` substack + AI infrastructure decisions in §Phase 9.

---

#### Integration 2 — Financial Hedging (Stream B → Financial Pipeline)

**What it means:** Stream B produces daily cross-sector signals at geopolitics × finance, legislative × finance, and market-mover × finance intersections. These are exactly the macro inputs that should influence long-term position sizing and hedging decisions in the financial pipeline — not individual trade signals, but regime-level context.

**Future wiring pattern:**
- Stream B compilation already writes Cross-Sector Signals in a structured format: `[Sector A] × [Sector B]: {event} | {confidence: high/medium/speculative}`
- Planned: a post-compilation step that writes high/medium-confidence signals to a `macro_signals` Postgres table (same DB as financial pipeline)
- Planned: financial pipeline's Monte Carlo and regime-detection logic reads `macro_signals` as an input factor alongside FRED data
- Planned: weekly brief surfaces "macro regime shift candidates" — signals that have appeared in 3+ of the past 7 daily briefs at medium/high confidence

**Connection point in this document:** §Financial stack → `analysis/` substack, specifically Monte Carlo and regime detection. Also feeds the `morning-briefs/` substack context block.

---

#### Integration 3 — Trading Algorithm Data Feed (Stream B → Financial Pipeline data sourcing)

**What it means:** Trading algorithms — especially mean-reversion and momentum strategies — benefit from knowing when unusual macro context is active (active tariff escalation, imminent Fed language shift, Market Mover post correlated with price move). The news pipeline already does this correlation work in the Stream B compilation. The trading layer currently has no awareness of this context.

**Future wiring pattern:**
- Planned: Stream B compilation's `Market Movers × Finance` and `Geopolitics × Finance` causal pairs are written to a `news_trade_signals` table at the moment they're identified (same Postgres instance, accessible by n8n financial workflow)
- Planned: financial pipeline's n8n workflows can query `news_trade_signals` for the current day before executing or sizing a trade
- High-confidence causal pairs could be treated as temporary regime flags (e.g., "tariff escalation active → reduce position size on export-exposed names")
- Speculative pairs are logged but don't affect execution — they feed the weekly hedging review

**Connection point in this document:** §Financial stack → `data-sourcing/` substack, specifically the n8n ingestion nodes. Also connects to backtesting infrastructure — historical `news_trade_signals` records become an input feature for strategy development.

---

### Open Items — News Pipeline

| Item | Status |
|---|---|
| `news_unified` Postgres table — article ingestion pipeline | ✅ Complete May 15, 2026 — 2,362+ articles across 9 sectors |
| `daily_stream_outputs` table created in Postgres | ✅ Complete May 15, 2026 |
| `cross_sector_signals`, `news_pipeline_runs` tables | ✅ Complete May 15, 2026 |
| fetch_worker.py — universal ingestion worker | ✅ Complete May 15, 2026 — 42 active sources, 0 errors |
| Automated ingestion (cron) | ✅ Complete May 15, 2026 — `*/30 * * * *` via ~/bin/news-ingest |
| Context system on monarch (CONSTITUTION/CONTEXT/ref-blueprint) | ✅ Complete May 15, 2026 |
| ~~n8n workflows: Stream A / Stream B / Final assembly~~ | ❌ RETIRED — never built; superseded by hybrid T2+Cowork (see §What Changed in v18) |
| Synthesis prompt files (synthesis/prompts/) | ✅ Complete — 5 files in use by Stage 2 (sector_variant_a/b, stream_a/b_compilation, final_assembly) |
| Stage 2: `synthesis_export.py` local T2 sector synthesis | ✅ Validated May 17, 2026 — two full 9-sector runs, 9/9 ok, quality verified |
| Stage 2: `~/bin/news-synth` cron wrapper | ✅ Tested May 17, 2026 — cron-equivalent path, self-loads env |
| Stage 3: rclone install + Google Drive sync of outputs/pending/ | ⬜ NEXT UP — separate session per HANDOFF |
| Stage 4: Cowork scheduled routine (Sonnet 4.6 compilation + final assembly) | ⬜ After Stage 3 |
| Stage 5: brief pickup + ntfy notification (interim until Jarvis Phase 18) | ⬜ After Stage 4 |
| Cron install for news-synth (`15 5 * * *` or per schedule) | ⬜ Deferred — operator validates one manual end-to-end run first |
| `git init` on ~/projects/news-pipeline | ⬜ RECOMMENDED before further edits — project has no version control |
| `~/bin/inference-up` VRAM gate (12000→12500 applied) | ⚠️ Operator review — confirm ceiling or move to tolerance-based logic |
| LiteLLM routing for news synthesis (`qwen3.6-pipeline` → T2) | ✅ Working — validated end-to-end May 17, 2026 |
| Weekly synthesis workflow | ⬜ Phase 5 — after 7 daily compiled blocks exist |
| FRED snapshot integration | ✅ FRED key active, fred_macro source fetching 7 series |
| Integration 1: stack_signals table + review task | ⬜ Planned, after news pipeline Phase 3 live |
| Integration 2: macro_signals table + financial pipeline input | ⬜ Planned, after news pipeline Phase 3 live |
| Integration 3: news_trade_signals table + trading algorithm input | ⬜ Planned, after Integrations 1+2 validated |


---

## Phase 16 — Discipline Layer

*Added v14. The five-tier always-on architecture produces enough agent output, across enough concurrent workflows, that without a discipline layer the operator drowns in agent-generated noise within a quarter. v14 adds three pillars of discipline, with a fourth planned.*

---

### 16.1 Validation Gate Integration

**Every Tier 2/3 generation passes through the validation gate before downstream delivery.** The gate (FastAPI on port 4100) runs three checks in sequence — schema, grounding, and voice — and returns a verdict that n8n workflows act on. Full technical specification and n8n integration pattern documented in Phase 9 (Validation Gate Service section).

**This is not optional once the five-tier architecture is live.** At five concurrent pipelines, each producing multiple outputs per day, manual quality review is not a viable audit strategy. The gate is the audit strategy.

**Calibration note.** Default thresholds (`VOICE_PASS_THRESHOLD = 0.70`, `GROUNDING_PASS_THRESHOLD = 0.90`) are conservative starting points. Real calibration requires at least one week of live traffic through the gate — adjust only after the first-pipeline telemetry shows baseline distribution. Do not tune thresholds to reduce the `retry_cloud` rate artificially; tune to ensure `fail` verdicts represent real failures.

---

### 16.2 Per-Workflow Working Directories

Every n8n execution and every agent session writes to a scoped working directory:

```
/var/agents/<tier>/<workflow_id>/<timestamp>/
```

No agent writes outside its scope. Drift is visible via `find` for unexpected paths. Cross-execution contamination is detectable at a glance.

**Current status: not yet enforced by the harness in v14.** This is an open item — the harness change (or n8n node template) that sets CWD and refuses writes outside the scoped path is planned but not implemented. It becomes more important once nexus exists, because nexus indexes these paths and unexpected writes show up as anomalies.

---

### 16.3 Telemetry-Driven Drift Detection

Validation gate writes to `validation_telemetry`. LoRA dispatcher writes to `lora_swap_telemetry`. Both back the same Postgres instance (when `DATABASE_URL` is set across both services) — joinable on `workflow_id`. A single cross-table query answers: "for workflow X, how long did the adapter swap take, and did the resulting output pass validation?"

**What to watch for in the telemetry:**

| Signal | Meaning | Response |
|---|---|---|
| Voice score trending down for a `source_model` | LoRA is drifting; training data may be stale | Queue a LoRA re-evaluation, consider retraining |
| Grounding score trending down | Model is hallucinating; source context may be truncated upstream | Audit context window usage in the failing workflow |
| `retry_cloud` rate climbing | Local model regressing OR thresholds are miscalibrated | Check raw scores; if scores are flat, thresholds need recalibration |
| Drain time (`drain_ms`) persistently high for a workflow | That workflow mixes adapters within one n8n execution | Refactor the workflow to batch by adapter |
| n_swaps climbing day-over-day | More workflows are running with different adapters | Expected growth; only a problem if drain_ms is also climbing |

**Daily morning report (planned, foundation laid).** SQL against both telemetry tables, plus LiteLLM logs, generates a digest at `~/morning-review/YYYY-MM-DD.md`. Not yet built — the cron skeleton for this depends on the morning digest job, which is deferred until both telemetry tables have ≥7 days of real traffic data to query meaningfully.

**Weekly drift eval (aspirational).** A fixed prompt set (~5 prompts per tier) runs weekly, scored via the same validation gate, diffed week-over-week. Voice score drop above threshold triggers a "consider retraining this LoRA" alert in the morning report. Not yet built — requires a stable LoRA baseline (at least one trained LoRA with ≥4 weeks of telemetry) to produce a meaningful week-over-week diff.

---

### 16.4 Git-Gated Agent Commits (Planned, Not Implemented)

For agents that propose code changes: branch-per-agent-task, validation gate on the final output before merge, human or automated approval gate before the branch is pushed to main. This complements the per-workflow working directory pattern — the working directory is the staging area; the git gate is the egress control.

Not in scope for v14. Flagged as an open design item before nexus build begins, because nexus will index these branches and the two systems need a shared convention for what a "branch created by an agent" looks like vs. one created by the operator.

---

## Phase 17 — Aspirational Knowledge Systems

*Added v14. Two knowledge-system layers were referenced in master_summary v1-v11 but did not survive into v12+ and have not yet been built. v14 documents them formally as deferred design items, with explicit "design before build, build before maintain" sequencing.*

---

### 17.1 Nexus (Codebase Index)

**What it is.** A coherent, indexed, searchable view of every code project the operator actively works on. Not a generic code search tool — a purpose-built index of Taolen Logic's active codebase, awareness of what exists, what's stale, and what references something that no longer exists.

**Intended capability surface:**

- Walk `~/projects/`, parse source files, embed at function or file level, write to Postgres + pgvector
- Surface cross-project dependencies ("this n8n export calls a Python script that was refactored last week")
- Identify dead imports, stale references, TODO/FIXME markers older than 30 days
- Feed the weekly loose-ends scan (which becomes a query against nexus, not a standalone scanner)
- Feed the morning digest ("what changed in the codebase since yesterday")

**Open design questions before build begins:**

| Question | Options | Decision needed |
|---|---|---|
| Scope | All projects explicitly enumerated vs. convention-based discovery (e.g., anything in `~/projects/`) | Explicit enum is safer initially — reduces noise from transient test dirs |
| Indexing unit | File-level, function-level, commit-level | File-level first; function-level as a Phase 2 enhancement |
| Substrate | Postgres + pgvector + filesystem walker (matches existing stack) vs. external tool | Postgres + pgvector: zero new infrastructure, joinable to existing telemetry |
| Query interface | CLI, HTTP API, OpenCode MCP integration, n8n nodes | CLI first; HTTP API to unlock n8n and MCP integration |
| Index behavior | Read-only (never writes to the projects) vs. active (can open issues, create notes) | Read-only initially — reduces risk surface substantially |

**Build sequence.** Design conversation first (resolve the above questions). Build after design is complete. Maintenance jobs (nightly nexus-update, weekly loose-ends scan) are built last, as queries on top of the index — not as standalone scanners. Building maintenance for a system that hasn't been designed is the trap that produced the doomed overnight-refactor architecture.

**Status:** ⬜ Design conversation queued as the next major design item after the five-tier soak test completes.

---

### 17.2 2nd Brain (Knowledge Base)

**What it is.** Personal knowledge management. Ingests the operator's accumulated knowledge artifacts — chat transcripts, session outputs, n8n execution results, hand-written notes, completed deliverables — cross-links them, deduplicates, and surfaces relevant material into active sessions and morning reviews.

**Intended capability surface:**

- Ingest Claude Pro chat exports, OpenCode session transcripts, aimux logs, n8n execution outputs
- Cross-link: "this conversation about the financial pipeline architecture is related to these three documents in the design stack"
- Surface into morning digest: "you asked about this topic three times last month; here's what you concluded each time"
- Feed the 2nd brain's content into CONSTITUTION.md updates at session end (the `/wrap` pattern extended to a knowledge graph)

**Open design questions before build begins:**

| Question | Options | Decision needed |
|---|---|---|
| Source material catalog | Claude Pro chat exports (how?), aimux logs (format, location), n8n outputs (which tables?), markdown notes (existing vault?) | Enumerate actual sources on monarch before designing the ingestion pipeline |
| Retrieval surface | Semantic search (ad-hoc), weekly digests (automated), active surfacing into interactive sessions (MCP), daily morning briefs | All of the above — but build in priority order |
| Integration with Claude Pro | Stay separate, integrate via custom MCP server, use Claude Projects as substrate | MCP is the right interface; Claude Projects may be substrate or competitor |
| Existing substrate | Obsidian vault, structured notes directory, both, neither | Ground-truth discovery needed before deciding |

**Relationship to nexus.** Nexus indexes code; 2nd brain indexes knowledge. They share substrate (Postgres + pgvector) and are queryable together, but serve different retrieval patterns. Morning digest queries both: "what's new in the codebase" (nexus) + "what decisions did you make recently that are relevant to today's work" (2nd brain). Design nexus first — the schema decisions made there constrain what 2nd brain's schema can look like if they're to be jointly queryable.

**Status:** ⬜ Design conversation queued after nexus is operational.

---

### 17.3 Maintenance Jobs That Depend on These Systems

Once nexus and 2nd brain exist, the following become small queries on top of them rather than standalone systems. **None of these should be built before their data substrates exist.**

| Job | Substrate required | Description |
|---|---|---|
| **Nightly nexus-update** | Nexus | Ingest the day's new code changes (git diffs, new files) into the codebase index |
| **Weekly loose-ends scan** | Nexus | Query for stale references, dead imports, broken paths — output to morning review |
| **Daily morning digest** | Both | Query both systems for "what's new, what needs attention" — write to `~/morning-review/` |
| **2nd brain ingestion** | 2nd brain | Ingest new chat transcripts, session outputs, n8n results from the previous day |

Building maintenance jobs before their substrates exist produces maintenance jobs for systems that don't work yet. The correct sequence is: design → build → only then maintain.

---

### 17.4 Continual Improvement

*The requirement: agents should get smarter as they keep running a workflow. The honest decomposition: this is three mechanisms on three timescales, and only one of them is dangerous.*

#### The three mechanisms

| Mechanism | Timescale | Risk | Status |
|---|---|---|---|
| **Context accumulation** — learnings land in CONTEXT.md via `/wrap`, eventually in 2nd brain | Within / across sessions | Low (retrieval engineering, no weight change) | Already designed (Phase 12, Phase 17.2) |
| **Retrieval growth** — agent queries nexus / 2nd brain for "how did I handle this before" | Across sessions, fast | None (no weight change) | Already designed (Phase 17.1, 17.2) |
| **Weight updates** — periodically fine-tune a LoRA on accumulated examples | Across sessions, slow | **High — closed-loop self-training degrades invisibly** | See ruled-out + design item below |

Most of the felt "the agent is smarter now" comes from the first two mechanisms, which are cheap and safe. The third is the only thing that is literally self-training, and a naive closed loop on it fails three ways: model collapse (training on own outputs reinforces existing errors), Goodhart on the validation gate (the gate becomes a training target and stops measuring quality), and distilling Phi-4's noise (the gate grades with a small noisy model; a loop trained on its approvals imitates a weaker model's taste). A closed loop is ruled out (Appendix A). Deliberate, human-reviewed retraining on **outcome** data is the design item.

#### The improvement ledger (buildable now)

The signal that makes real improvement possible is not more model-graded signal — it is **outcome** signal, which nothing currently captures. The validation gate records "this looked good." It does not record whether the operator shipped it as-is, edited it, or discarded it; whether the scored lead converted; whether the content performed.

v14 specifies an **improvement-ledger** service: a thin, single-concern FastAPI service, sibling to the validation gate (4100) and LoRA dispatcher (4200), writing to the same Postgres instance (joinable on `workflow_id`). It is buildable now, independent of nexus, and this independence is the decisive point — the data it captures is irrecoverable if not captured at the moment of the workflow. A schema deferred can be redesigned later; an unobserved outcome is lost permanently.

**Scope is deliberately narrow — capture and record, NOT ranking.** The ledger is the system-of-record for three things:

1. **Operator disposition + outcome** — for each gated output: `accepted` / `edited` / `discarded`, the edit delta where applicable, and the downstream business outcome where it exists (lead converted, content performed, deliverable shipped unchanged).
2. **Abandoned approaches** — when an approach to a workflow is tried and dropped: what was attempted, under what conditions, why it failed, and a **mandatory re-open condition**. An abandoned-approach record without a re-open condition is a bug, not a record — this is Appendix A's discipline generalized and machine-maintained.
3. **Approach leaderboard** — a SQL view over the ledger's own tables: for each workflow, which approach currently has the best measured outcome. This view *is* the "don't re-try what we already tried" guarantee — a leaderboard that records every approach and its outcome makes re-attempting a known dead-end visible by construction.

**The ledger does not own retrieval weighting.** When nexus and 2nd brain are built, *they* read the ledger and apply weighting at retrieval time. This keeps weighting co-located with the corpus it weighs, and makes the seam one-directional: the ledger writes facts; the knowledge systems read facts and decide how to weigh them.

#### Multi-dimensional weighting (nexus / 2nd brain design parameter)

When the knowledge systems consume the ledger, retrieved information must not be ranked on a single "quality" scalar. A single scalar conflates four independent axes and recreates the rich-get-richer collapse inside the retrieval layer:

| Axis | What it measures | Why separate |
|---|---|---|
| **Grade** | Validation scores + operator disposition + downstream outcome | The quality signal — but only meaningful with the outcome anchor below |
| **Recency** | How long ago — **must decay** | Without decay, a once-high-confidence conclusion is cited forever, including after it goes stale (the authority self-reinforcement failure) |
| **Authority** | CONSTITUTION-level fact vs. synthesized conclusion vs. raw artifact | Different *kinds* of thing; must not compete on one axis |
| **Polarity** | Positive exemplar vs. dead-end vs. neutral record | The crux of the requirement — see below |

**Negative knowledge is a first-class, separately-queried class — not low-ranked positives.** Down-weighting failures *buries* them, and a buried dead-end is one the agent rediscovers. Positive knowledge is retrieved by "best prior work on this, ranked by grade." Negative knowledge is retrieved by a *different* query: "before proposing X, has anything resembling X been tried, and what happened" — a coverage lookup, not a ranked-best search. Same store, two retrieval paths.

**Two anti-collapse requirements on the weighting model:**

- **Decay is mandatory.** Weight must fall with time, and a meaningful component of weight must come from *external outcome signal* (did it work when reused) rather than purely *internal grade at creation*. Without an external anchor the loop eats itself — this is the closed-loop failure relocated into retrieval.
- **Every machine-recorded dead-end carries a re-open condition.** A dead-end treated as a permanent prohibition makes the system refuse approaches that became viable after the model, data, or tooling changed. The re-open condition is the anti-ossification mechanism, mandatory by construction.

**Start deterministic and legible.** Recency decay, a discrete authority tier, the polarity tag, and a coarse grade band. A learned cross-encoder re-ranker is a re-open-when-the-simple-version-is-proven-insufficient item, not a v1 — a four-dimensional learned ranker is its own tuning project and, at solo-operator query volume, the trap.

#### Status and sequence

- **Improvement-ledger service: buildable now.** Recommended as the concrete next build after the five-tier soak test, ahead of nexus, so disposition/outcome capture begins the day the validation gate goes live.
- **Multi-dimensional weighting + dead-end retrieval: nexus / 2nd brain design parameters.** Not buildable until those substrates exist; the ledger is designed to be consumed by them, not to rank on its own.
- **Deliberate retraining: design conversation, blocked on nexus.** Human-reviewed dataset built from *outcomes*, retrained on a deliberate cadence (quarterly, not a cron), with the validation gate kept strictly as an independent evaluator that is never a training target.

---

## Phase 17.5 — MacBook Voice-to-Text Input for Agent Harnesses

*Added v18 (May 17, 2026). Phase 17.5 is the hands-free voice-to-text input method for agent interaction. It is what lets the operator dictate prompts into OpenCode, Claude Code, and Claude Pro browser tabs without typing — while at the desk, across the room, mid-workout, or away from the keyboard for any other reason. It is **not** a system control surface and **not** a Jarvis component. It runs entirely on the M2 MacBook Pro (8GB unified RAM), has no monarch dependency, and shares no runtime state with the inference stack. Built and shipped live May 17, 2026 in a single session.*

The phase is numbered 17.5 because it bridges Phase 17 (aspirational knowledge systems, design-only) and Phase 18 (Jarvis, build-target). The dictation system was a tangential, unplanned build — triggered by the operator's actual workflow need to interact with agent sessions without typing — but the result is a durable, in-production subsystem that deserves first-class documentation.

---

### 17.5.0 Boundary of responsibility — what Phase 17.5 is and is not

**What Phase 17.5 does:**
- Listens for a wake word on the MacBook microphone (always on, ~1% CPU).
- On wake-word detection, opens the capture mic (built-in or JLab earbuds) and records.
- Detects an end word OR trailing silence, and stops the take.
- Transcribes the recording via local Whisper.
- Pastes the transcript into the focused window, and on end-word stops also presses Return to submit (front-app gated allowlist).
- Provides a fallback double-tap-earbud trigger for noisy/silent moments where speaking the wake word is impractical.

**What Phase 17.5 does not do:**
- It does not speak back. There is no TTS layer. Output is text into the focused window, nothing else.
- It does not observe system state, route to inference tiers, surface notifications, or supervise GPU policy. **Those are Jarvis responsibilities (Phase 18) and are not in scope here.**
- It does not interact with monarch. The MacBook is the entire stack.
- It does not know or care what window is focused or what the agent in that window does with the text. The agent (OpenCode, Claude Code, a Claude Pro tab) consumes the dictation the same way it would consume typed input.

**Sister-system relationship with Phase 18 Jarvis:** Both are voice subsystems on the MacBook. They share one physical resource: the MacBook microphone. They share no runtime state, no daemon, no models, no socket, no Python process. Wake words must be distinct (Phase 17.5 uses "Okay Comrade"; Jarvis's wake word is TBD and will not collide). Both can run side-by-side; running both is not currently required but is the long-term steady state. **There is no build-order dependency in either direction.** Jarvis was not waiting on Phase 17.5, and Phase 17.5 does not anticipate Jarvis.

---

### 17.5.1 Architecture

```
"Okay Comrade"  ─► OpenWakeWord (always-on, MacBook mic, <1% CPU)  ─┐
                                                                    │
Double-tap right earbud  ─► NEXT key ─► Hammerspoon ─socket─►       ├─► START take
(fallback for noisy/silent moments)                                 │   (earbud mic
echo -n toggle | nc -U /tmp/dictation.sock  ────────────────────────┘    opens now)
                                                                    │
                                                                    ▼
                      Silero VAD + end-word OpenWakeWord watch stream
                                                                    │
                            say end word ("You May Begin")  ────────┤
                            OR ~2.5s silence (no end word)          ▼
                            OR ~12s silence runaway-guard      STOP ► mlx-whisper-large-v3-turbo
                                                                    │
                            wake/auto-stop ◄──────────────────────┤────► socket
                            take: daemon calls                      │      caller
                            `hs -c dictationDeliver(...)` (or       │      gets
                            osascript fallback)                     ▼      TEXT:
                                        Hammerspoon (or osascript) pastes
                                        at cursor, optionally presses Return
                                        (preserves prior clipboard)
```

**Components and their roles:**

| Component | Role | Location |
|---|---|---|
| OpenWakeWord (`openwakeword` Python package) | Wake-word and end-word detection | `~/.dictation/venv/` |
| Outspoken-trained `.onnx` models | The actual wake/end classifiers | `~/.dictation/wake.onnx`, `~/.dictation/end.onnx` |
| Silero VAD (via `silero-vad` + `torch`) | Silence detection for auto-stop | `~/.dictation/venv/` |
| mlx-whisper-large-v3-turbo | Local STT inference on Apple Silicon | `~/.cache/huggingface/hub/` (~1.5GB) |
| `dictation_daemon.py` | The orchestrator — owns the mic, models, socket, lifecycle | `~/.dictation/dictation_daemon.py` |
| `launchd` agent | Keeps the daemon running | `~/Library/LaunchAgents/com.trent.dictation.plist` |
| Hammerspoon `init.lua` | Earbud media-key handling + paste/submit callback | `~/.hammerspoon/init.lua` |
| osascript fallback | Paste path when `hs` CLI is unavailable | `pbcopy` + `tell System Events` |

---

### 17.5.2 Engine selection — Porcupine ruled out, OpenWakeWord adopted

**The original design called for Picovoice Porcupine** for wake-word detection. Porcupine is the standard production choice for this role: well-documented, low CPU, mature SDK, supports macOS arm64 natively. The plan was to train "Comrade" and a separate end word on Picovoice Console, download the `.ppn` files, and integrate via the `pvporcupine` Python SDK.

**This blocked at signup.** The Picovoice Console signup page (May 2026) presents a single "Sign up" form requiring a company email. The "Free Plan" documentation states personal email is acceptable, but the UI does not surface a personal-email path or a GitHub/Google OAuth alternative on the form Trent landed on. GitHub OAuth attempts returned "unable to sign in, go back to sign up." This is plausibly a misconfigured A/B test or a recent UI change, but it is a hard barrier for a new account in this build window.

**OpenWakeWord (Apache 2.0, MIT-License-equivalent) is the chosen substitute.** It is a Tensorflow/ONNX-based wake-word engine, originally developed by David Scripka, designed for exactly this on-device use case. The classifier architecture is similar to Porcupine's: a small neural net runs on a sliding window of audio frames and emits a per-frame score 0–1. The substitution is lateral, not a downgrade.

**Custom wake words are trained via Outspoken.cloud** (€1 per model, ~45 minute training time, downloadable as `.onnx`). Outspoken is the most practical option for an English wake word; LiveKit's wakeword trainer is also viable and free but takes hours of local compute.

**Why this matters as documented architecture, not just a runtime choice:** Porcupine is what every tutorial and most production builds default to. Documenting the substitution prevents a future re-evaluation from re-defaulting to Porcupine and re-hitting the same signup wall. See Appendix A.

**Trained models in production:**
- `wake.onnx` — "Okay Comrade" — peak score 0.98+ on real speech, peak ~0.10 on background music
- `end.onnx` — "You May Begin" — peak score 0.98+ on real speech (trained as the third attempt — see §17.5.5 for the failed "Send it" experiment)

---

### 17.5.3 Whisper model selection — large-v3-turbo on M2 8GB

**Initial design called for `whisper-large-v3`** (~3GB disk, ~2GB unified RAM resident). This is the most robust model for the noisy 8–16kHz HFP signal an earbud mic produces. On a workstation-class machine it would be the default choice.

**The M2 MacBook has 8GB unified RAM.** First-bringup memory_pressure check showed:
- Pages free: 3,603 (out of 524,288 = 0.7%)
- Compressed memory: 206,244 pages in use
- Lifetime swapouts: 76,385,102
- System-wide memory free percentage: 29%

The base workload (Conda env, browser, IDE) was already pressing the machine into compression and swap. Loading large-v3 resident would push it into sustained swap during dictation, which means slow transcription, sluggish foreground apps, and accelerated SSD wear.

**Pivoted to `mlx-community/whisper-large-v3-turbo`.** ~800MB unified RAM, ~1.5GB disk. The accuracy delta on short, well-articulated speech (which is what dictation produces) is imperceptible. The original architecture document noted large-v3 was chosen "for the earbud HFP signal" — turbo handles HFP fine; the original concern was over-stated for this use case.

**Future architecture: when monarch is available over Tailscale and a low-latency RPC path exists,** Whisper inference can move to monarch (96GB RAM, RTX 3090) and the MacBook becomes a thin client. At that point large-v3 (or whisper-v4 if released) becomes feasible. This is a deferred optimization, not a current need — turbo on-device is sufficient.

**Repository correction:** the initial daemon used `mlx-community/whisper-large-v3` as the repo string. This 404s as of May 2026 — the MLX community repo was renamed. Correct string is `mlx-community/whisper-large-v3-turbo`.

---

### 17.5.4 Daemon design

The daemon (`~/.dictation/dictation_daemon.py`) is a single Python process with several responsibilities. Design principles:

**Three independent trigger paths converge on one start_recording entry point:**
1. **Wake word** — `wake_word_loop` thread, always-on MacBook mic, fires `start_recording(deliver=True)` when score crosses threshold.
2. **Unix socket toggle** — `/tmp/dictation.sock`, called by Hammerspoon on earbud double-tap, calls `toggle()` which routes to start or stop.
3. **Manual toggle** — `echo -n toggle | nc -U /tmp/dictation.sock`, for headless testing.

**Recording stops on whichever fires first:**
- End-word detection (OpenWakeWord on the capture stream, scored every 1280-sample frame)
- Trailing silence (Silero VAD, 2.5s with no end word configured, 12s as a runaway-guard when an end word is configured)
- Maximum take duration (120s hard cap)
- Manual cancel (`echo -n cancel | nc -U /tmp/dictation.sock`)

**Two delivery paths:**
- **Preferred:** `hs -c 'dictationDeliver(base64-decoded-text, submit_bool)'` — calls Hammerspoon's CLI which does the paste with clipboard preservation and front-app allowlist gating for the Return key.
- **Fallback:** `pbcopy` + `osascript -e 'tell application "System Events" to keystroke "v" using command down'` — used when the `hs` CLI is unavailable. No front-app gating; the Return-on-end-word feature is silently skipped.

**Dual-mic design with live fallback:** The wake-word listener always uses the MacBook mic (set by `WAKE_MIC_DEVICE = "MacBook"`). This keeps the Bluetooth A2DP link to the JLabs intact during the ~99% of the time the operator is not actively dictating, preserving music quality. The capture mic for the actual take is the earbuds (`RECORD_MIC_DEVICE = "JLab"`), opened only for the duration of the take, which forces a brief A2DP→HFP switch (audible ~1s click in the earbuds). **Capture device is re-resolved at every `start_recording()` call, not at daemon startup** — earbuds may have disconnected between takes (battery died, walked out of range, deliberately powered off), and the daemon must adapt without restart. The fallback chain on each take is: `JLab` → `MacBook` → system default. Each fallback level is logged so the operator knows which mic is active for a given take (e.g. `JLab unavailable, falling back to MacBook mic [1]`). Concurrent open of the same physical mic by the wake listener and the capture stream is permitted by macOS — verified May 17, 2026 — so MacBook-mic fallback does not require suspending the wake listener.

**Battery considerations.** Running this system increases JLab earbud drain modestly. Two effects: (a) each take forces a brief A2DP→HFP profile switch, which is high-radio-activity for ~1-2 seconds; (b) for the duration of the take, the earbuds are in HFP (bidirectional 16kHz call mode) which consumes roughly 1.3-1.5× the radio power of A2DP music playback. Net effect on a heavy-dictation day is approximately 10-15% faster drain — indistinguishable on a light day, not large enough to plan around. When the earbuds die mid-session, the live-fallback chain above takes over automatically and the operator can keep dictating from the MacBook mic without intervention. Capture quality drops (MacBook mic is farther from the mouth) but the wake-word and end-word detection remain accurate at desk-distance.

**Wake-word retrigger cooldown:** When a take ends, OpenWakeWord's sliding 1.3-second classification window still contains audio from the end of the take — including the spoken end word, which itself partially matches the wake-word phonemes. Without protection, this re-fires the wake word multiple times immediately after delivery. The mitigation is two-part:
1. `_wake_cooldown_until` is set to `time.monotonic() + 600.0` at `start_recording` entry (blocking wake during the entire take), then reduced to `+ 8.0` at `stop_and_transcribe` entry (covering transcription + tail-of-speech window).
2. Both OWW models (`wake_oww`, `end_oww`) have their internal state reset via `.reset()` at the end of every take, clearing the sliding window's audio history.

These two mitigations together produce clean single-fire behavior even with music playing in the earbuds.

**Filler-word stripping:** `STRIP_FILLERS = True` removes whole-token "um", "uh", "erm", "er" disfluencies (and their pluralized forms) from the transcript before delivery, cleaning up the comma-and-space residue. Won't touch "umbrella" or "uh-huh." A user-extendable `EXTRA_FILLERS` list exists but is empty by default — adding "like" or "so" causes false positives in technical prompts where those words are content.

---

### 17.5.5 Build hardening — five lessons captured during bringup

These are not theoretical concerns. Each one is a concrete bug found and fixed during the May 17, 2026 build session. They are documented here so a future rebuild does not rediscover them.

**1. Audio scaling.** OpenWakeWord's input convention is **int16-range float32** (i.e. values in roughly ±32,768), not the standard float32 audio range of ±1.0. Sounddevice returns ±1.0 float32. Without scaling by 32768, every score is ~0.001 and nothing ever fires. Diagnostic: train a known-good model, run a 30-second mic test with `score = max(model.predict(audio).values())`, and look for scores above 0.1 when speaking the wake phrase. If they never appear, this is the bug.

**2. Silero VAD frame-size mismatch.** Silero requires **exactly 512 samples per frame at 16kHz** (or 256 at 8kHz). OpenWakeWord requires 1280-sample frames. The auto-stop monitor processes audio in OWW-sized chunks for end-word detection, so the inner loop must split each 1280-sample chunk into 512-sample sub-chunks for VAD scoring. Without this, every VAD frame raises an exception and silence detection is broken.

**3. Wake-word retrigger storm.** See §17.5.4 above. Symptom: the log shows the wake word firing 3–5 times in 2 seconds immediately after a take completes. The fix is the two-part cooldown described above. A naive cooldown set at delivery time is too late — the wake re-fires during the transcription window before delivery.

**4. Threshold tuning for music-aware operation.** The original threshold of 0.55 produced false-fires when music played in the earbuds (real wake words scored 0.98; music alone hit 0.10–0.20 sustained, with occasional spikes above 0.55). Raising to 0.75 cleanly separated signal from noise — real wake words still hit 0.98 reliably, music never crossed 0.75. The same threshold works for the end-word model.

**5. OpenWakeWord model state reset between takes.** OWW's classifier maintains an internal sliding window of embedded audio features (16 embeddings × 80ms = 1.28s of context). After a take ends, that window still contains residual audio from the end of the take. Without `.reset()`, the very first frame of the new wake-listen period scores against a window pre-populated with phonemes that partially match the wake phrase. Calling `model.reset()` on both wake and end OWW models at the end of every take clears this state.

**Failed experiment worth recording — short end-word phrases.** "Send it" was the operator's preferred end word semantically. Trained on Outspoken, downloaded, integrated. **It produced a max score of 0.003 across a 30-second test recording with the operator saying "Send it" ~20 times.** The model is technically valid (loads cleanly, produces output, matches the OWW architecture) but trained dud. Hypothesized cause: at ~0.4 seconds of spoken audio, "Send it" is too short for OpenWakeWord's 1.3-second classification window — too much of the window is silence/context relative to the phrase. Outspoken's synthetic training data may not have captured enough variation. **Retraining once might fix it.** The practical resolution was to switch to a longer phrase ("You May Begin", 3 syllables, ~0.9 seconds), which trained cleanly and scored 0.98+. **Lesson: when training an OpenWakeWord model, target ≥3 syllables / ≥0.7 seconds of spoken phrase.**

---

### 17.5.6 File inventory and lifecycle

```
~/.dictation/
├── dictation_daemon.py       # The orchestrator (~600 lines)
├── wake.onnx                 # "Okay Comrade" OWW classifier
├── end.onnx                  # "You May Begin" OWW classifier
├── wake.okay-comrade.bak     # Backup of working wake model
├── end.dismissed-comrade.bak # Backup of original end model
├── venv/                     # Python virtualenv
│   └── lib/python3.13/site-packages/
│       ├── openwakeword/
│       ├── silero_vad/
│       ├── mlx_whisper/
│       └── sounddevice/
└── daemon.log                # Rolling log

~/.hammerspoon/
├── init.lua                  # Media-key handler + dictationDeliver()
├── probe.lua                 # Diagnostic for confirming JLab button codes
└── init.lua.backup.<unixts>  # Pre-install backup

~/Library/LaunchAgents/
└── com.trent.dictation.plist # launchd config

~/.cache/huggingface/hub/
└── models--mlx-community--whisper-large-v3-turbo/  # ~1.5GB
```

**Operational commands:**

```bash
# Restart the daemon (after config change)
launchctl unload ~/Library/LaunchAgents/com.trent.dictation.plist
launchctl load   ~/Library/LaunchAgents/com.trent.dictation.plist

# Watch logs
tail -f ~/.dictation/daemon.log

# Disable temporarily
launchctl unload ~/Library/LaunchAgents/com.trent.dictation.plist

# Headless test (without speaking — useful for verifying paste path)
echo -n toggle | nc -U /tmp/dictation.sock   # start
echo -n toggle | nc -U /tmp/dictation.sock   # stop+transcribe+return
echo -n cancel | nc -U /tmp/dictation.sock   # abort

# Status
echo -n status | nc -U /tmp/dictation.sock   # IDLE | RECORDING
```

**Future architecture (deferred):** when monarch is online and a low-latency RPC path exists, the daemon's `mlx_whisper.transcribe()` call becomes a remote call to monarch. The MacBook keeps the wake/end listeners (mic must stay local) and the paste path (focused window is local), but Whisper inference moves to monarch where large-v3 or larger is feasible. The split point in the code is a single function — `stop_and_transcribe()` — so the swap is mechanical when the time comes. **This is not a Jarvis dependency.** It's just where Whisper runs.

---

### 17.5.7 Hardware fallback resilience

The system is designed to degrade gracefully through three layers of hardware availability. The operator should never need to restart the daemon, replug an earbud, or change a configuration to recover from a hardware change mid-session. **Validated live May 17, 2026.**

#### Layer 1 — Earbuds available (preferred)

- Wake listener: MacBook built-in mic
- Capture stream: JLab Go Air Pop ANC, opened only during a take
- Feedback sounds: played to JLabs via A2DP
- Music: continues uninterrupted on A2DP, briefly drops to HFP call quality during a take, returns to A2DP after

This is the standard operating mode and accounts for the vast majority of takes.

#### Layer 2 — Earbuds dead or disconnected (automatic fallback)

When the JLabs power off (battery exhaustion is the expected trigger), disconnect (walked out of Bluetooth range), or are deliberately turned off:

- Wake listener: MacBook built-in mic (unchanged — never used the JLabs)
- Capture stream: **automatically resolves to MacBook built-in mic** on the next `start_recording()` call
- Feedback sounds: played to MacBook speakers (the active audio output after JLab disconnect)
- Music: stops when JLabs disconnect (this is macOS behavior, unrelated to the daemon)
- Log entry: `JLab unavailable, falling back to MacBook mic [N]` where N is the resolved device index

The operator may notice three things: (a) the spoken wake word may need to be a touch louder if the MacBook is more than 6-8 feet away; (b) the feedback Tink/Pop/Funk sounds come from the laptop instead of the earbuds; (c) accuracy on dictation drops slightly because the MacBook mic array is farther from the mouth and picks up more room noise. None of these prevents the system from working — they are quality-of-life differences, not failures.

**No restart, no reconfiguration, no manual intervention required.** Put the JLabs on the charger, swap to different earbuds, or just keep using the MacBook mic — the daemon handles all three transparently because the device is re-resolved on every take.

#### Layer 3 — All Bluetooth/external audio failed (last-ditch fallback)

If the MacBook mic also fails to open (extremely unlikely — would require macOS audio system failure or revoked Microphone permission mid-session), the daemon attempts `sounddevice.InputStream(device=None)` which uses whatever macOS reports as the current default input. If that also fails, the take is cancelled cleanly with a Funk sound and an `ERROR:` socket response — the daemon does not crash, hang, or leave the lock held. The wake listener continues running on its existing stream so future takes can succeed when audio returns.

#### What is NOT auto-recovered

- **Microphone permission revoked at the OS level.** If the operator goes into System Settings → Privacy & Security → Microphone and toggles Python off mid-session, the daemon's audio streams begin returning silent buffers. The fix is to re-grant the permission and restart the daemon. There is no in-process way to detect or recover from this; macOS does not signal it.
- **Hammerspoon quit.** If Hammerspoon is killed, the daemon's `hs` CLI calls fail and it falls back to `osascript` paste. If `osascript` is also denied Accessibility permission (or Hammerspoon is what was granted), delivery fails. The transcript still completes and is logged in `~/.dictation/daemon.log` — it just doesn't paste.
- **launchd daemon itself crashing.** The launchd config sets `KeepAlive` with `Crashed = true` and `ThrottleInterval = 10`, so a crashed daemon is restarted within 10 seconds. A daemon that exits cleanly (e.g. `launchctl unload`) stays down — this is correct behavior.

#### Concurrent mic access verified

A failure mode that was *anticipated but proved non-issue*: when the wake listener and the capture stream both target the MacBook mic during fallback mode, would macOS allow two simultaneous opens of the same input device? **Yes** — tested with two concurrent `sd.InputStream` instances both opening device index 1 (the MacBook Pro Microphone), both started, both delivering audio to their respective callbacks without error. No suspension of the wake listener is needed during fallback capture. The four existing wake-retrigger protections (`self.recording` check, cooldown, threshold, model.reset) are device-independent and apply equally on the fallback path.

---

### 17.5.8 Outstanding items

These are non-blocking known issues. They are listed here so they get fixed in a future maintenance window rather than being rediscovered.

| Item | Description | Resolution |
|---|---|---|
| Hammerspoon `hs.ipc.cliInstall()` returns false | Current Hammerspoon version (May 2026) has a regression where `cliInstall` reports the install path as a boolean instead of a string. Daemon falls back to `osascript` paste, which works fully. The "nice-to-have" cost of the fallback is losing the front-app allowlist gate on the auto-submit Return — submit currently fires regardless of focused app. | Wait for Hammerspoon upstream fix, or patch the IPC bootstrap manually. Not urgent. |
| End word lands in the transcript on fast speech | If "You May Begin" is spoken too quickly after the last content word, `END_TRIM_SECONDS = 1.0` is insufficient to trim it cleanly. Whisper sees the end-word audio and transcribes it. | Raise `END_TRIM_SECONDS` to 1.4 if this becomes annoying. Currently fine. |
| No probe of JLab button codes confirmed | The Hammerspoon `init.lua` assumes double-tap-right → NEXT, triple-tap-right → PREVIOUS. The `probe.lua` diagnostic ships with the install but Trent has not yet run it. | Optional — wake word is the primary trigger and works fine. The earbud-button fallback is theoretical until probed. |
| MacBook microphone permission was not granted to launchd-spawned Python | macOS does not show the mic-permission prompt for processes launched via launchd. Resolution required running the daemon once foregrounded from Terminal to trigger the prompt, then launchd inherits the grant. Documented here because it will reproduce on a clean install. | Document in any rebuild SOP: "Run daemon foreground once to trigger mic prompt, then launchd-load." |
| Outspoken training "Send it" produced a dud model | See §17.5.5. Short phrases under ~0.7 seconds may train unreliably. | Document in any future end-word selection: target ≥3 syllables. |

---

## Phase 18 — Jarvis

> **[v19 update — read this first]** The Jarvis daemon shipped in v19 as v0.2 (`~/projects/jarvis/` on monarch; public on github). What follows below is the v15-v18 design content, **preserved as the historical build record**. **Live governance is `AUTHORITY_SPEC_v19.md`** — Tier 1/2/3 action lists, Hard Constraints, Substrate Pressure Cascade, Overnight Workload Window, Quota Cascade Policy. The "GPU Layer Policy Supervisor" role specified below (§18.0) has been generalized in v19 into two doctrines: the Substrate Pressure Cascade (response to observed VRAM pressure) and the latency-band routing cascade (Tier 2 response to workload latency drift). The voice surface and the PWA remain planned. Reserved ports are doctrinally locked: Jarvis voice surface `4300`, Read API `4400`, Command Center PWA `3000`. Read the v19 doctrine docs before treating any specific number, threshold, or behavior described below as live.
>
> *The v18 design below is correct as a description of how the operator and a previous designer-mode session framed the build. v19 doctrine refined the framing without invalidating the build sequence — when Phase 2 listeners ship (`process.py`, `vram.py`, `quota.py`, `cron.py`), they translate the cascade doctrine into runtime behavior. The v18 burst-up/burst-down shell scripts remain the working surface until the listeners land.*

*Added v15. Jarvis is the operator's always-on voice manager. It listens for a wake word on the MacBook, routes voice queries through the inference stack, and proactively surfaces system state — morning briefings, pipeline anomalies, agent completion events — so the operator doesn't have to watch the system. It runs on T1 (Qwen3.6-27B) at zero additional VRAM cost and is architecturally a sibling service to the validation gate (4100) and LoRA dispatcher (4200).*

**v18 note — Phase 17.5 is a sister system, not a prerequisite.** Phase 17.5 (MacBook Voice-to-Text Input for Agent Harnesses) shipped May 17, 2026, and it shares the wake-word listening pattern with Jarvis. They are not the same system and have no build-order dependency. **Phase 17.5 is voice-to-text** (transcribed audio → paste keystroke into the focused agent window) — its consumers are OpenCode, Claude Code, and Claude Pro browser tabs. **Jarvis is voice-to-voice** (audio query → reasoning on T1 → TTS response to the operator's ears) — its consumers are the operator's working memory and the notification bus. The only shared physical resource is the MacBook microphone, and both systems will run side-by-side once Jarvis ships. Wake words must be distinct (Phase 17.5 uses "Okay Comrade"; Jarvis's wake word is TBD and will not collide). Sharing a single mic listener at runtime is a possible future optimization; it is not required for either system to function. **Jarvis's design and scope in this section is unchanged from v17.**

**v16 scope expansion: Jarvis owns time-of-day GPU layer policy.** Per the Three-Mode VRAM Doctrine introduced in Phase 9, the system reallocates between Standard / Burst / Soft modes based on workload. Jarvis is the right home for this supervisor logic because it already has the notification bus, schedule awareness, T1 access-pattern visibility, and operator-facing channel needed to make and announce these transitions. The interim shell scripts (`inference-burst-up` / `inference-burst-down`) are throwaway implementations of what Jarvis will subsume.

---

### 18.0 GPU Layer Policy Supervisor [NEW in v16]

#### Why Jarvis owns this responsibility

The v15 design principle says Jarvis is "read-oriented — surfaces what the system is doing, not a direct control surface." That principle was about not exposing arbitrary infrastructure control to voice commands ("Hey Jarvis, rebalance VRAM" is bad). It does not preclude internal autonomic behavior that Jarvis announces. The distinction:

- ❌ Operator commands Jarvis → Jarvis controls infra (violates principle)
- ✅ Jarvis observes infra signals → Jarvis reallocates autonomously → Jarvis tells operator what it did

VRAM reallocation is the first concrete case for the second pattern. Jarvis already has:
- The notification bus carrying cron and workflow events
- LiteLLM access log visibility (the T1 activity signal)
- An operator-facing channel (PWA push + voice) for negotiation when needed
- Built-in awareness of T4 as a fallback for its own reasoning during T1-parked windows

A separate supervisor daemon would replicate all of this. Jarvis is the natural home.

#### Supervisor loop

```
On scheduled pipeline event (cron-emitted, bus-delivered):
  1. Check T1 active-session signal (LiteLLM access log, last 5 min)
  2. If T1 idle:
     a. Announce on bus: "Parking T1 for <pipeline> burst (~N min)"
     b. Switch Jarvis's own reasoning model from qwen3.6-consultancy → phi4-mini
     c. Kill T1 tmux window
     d. Relaunch T2 with -ngl 60 + 32K ctx (burst-mode launch — see Phase 9 scripts)
     e. Run the pipeline to completion
     f. Restore T2 standard config (-ngl 20, 16K ctx)
     g. Relaunch T1 standard config (-ngl 40, 36K ctx, np=1)
     h. Switch Jarvis reasoning back to qwen3.6-consultancy
     i. Announce: "Restored interactive tier"
  3. If T1 active during scheduled window:
     a. Push notification to operator (PWA + voice):
        "<pipeline> scheduled now. T1 is active — can you yield?
         Options: switch to Claude Code, step back, or I'll run at reduced performance."
     b. Wait up to 5 min for operator response:
        - Operator confirms yield (switches to Claude Code or signals ready):
          proceed as in step 2 (full burst mode)
        - Operator declines: proceed to step 3c
        - No response within 5 min: proceed to step 3c automatically
     c. Auto-fallback (operator busy, absent, or declined). Priority order:
        1. Cloud route via LiteLLM (DeepSeek V4 Flash) — announce: "Routing <pipeline> to cloud"
        2. Heavy offload on T2 with T1 resident (Mode 3 soft) — announce: "Running <pipeline> at reduced speed"
        3. Deferral to next T1-idle window — announce: "Deferred <pipeline>, ETA: <time>"
     d. Announce final routing decision to PWA regardless of path taken.
     e. Log: pipeline name, T1 activity signal at trigger time, operator response (if any),
        fallback path taken, wall-clock outcome.
```

#### Recursive dependency: Jarvis using T1 while parking T1

Jarvis's default reasoning engine is T1 (`qwen3.6-consultancy` via LiteLLM). When Jarvis parks T1 for a burst window, it cannot use T1 for its own reasoning during that window. Resolution: Jarvis maintains a `current_reasoning_model` config field that it sets to `phi4-mini` BEFORE issuing the T1 kill, and restores AFTER T1 is verified healthy on restore. T4 at 206 tok/s gen is more than adequate for Jarvis's intent classification, state-query, and short-response workload. Deep reasoning calls during the window get deferred (logged as "pending — T1 burst window") or routed to cloud.

Implementation note for Claude Code: this is a single-field swap, not an architectural refactor. The model name flows through the same LiteLLM call path Jarvis already uses.

#### Failure-mode catalog

| Failure | Detection | Response |
|---|---|---|
| T1 active when burst window opens | LiteLLM access log shows recent T1 hits | Notify operator, defer or cloud-route |
| Operator does not respond to yield request within 5 min | 5-min timer expires with no PWA/voice acknowledgment | Auto-proceed to fallback priority chain (cloud → soft offload → defer); log operator-unavailable |
| Operator is mid-active-work and yield would disrupt them | Operator declines via PWA | Respect the decline; proceed to fallback chain; never force-park T1 if the operator is actively using it |
| Burst T2 launch fails (OOM, etc.) | `wait_for_port 8083 120` times out | Roll back via inference-burst-down, announce failure, fall pipeline through to cloud |
| Pipeline runs longer than expected | Burst wall clock > 1.5× window | Auto-extend burst by 50% once, then enforce shutdown if pipeline still running |
| Multiple pipelines collide in one window | Cron registry check at burst-up | Serialize: first scheduled wins, second deferred |
| Jarvis itself crashes mid-burst | Watchdog on Jarvis health | systemd unit restarts Jarvis; burst state file ensures it knows it was mid-burst on restart |
| Operator manually attaches OpenCode mid-burst | OpenCode connect attempt rejected by T1 (down) | PWA surfaces friendly error explaining why T1 unavailable + ETA to restore |

#### Build sequencing

Implement as part of Phase 18 Jarvis build, not as standalone earlier. The interim is the cron-driven shell scripts described in Phase 9. Those scripts are validated end-to-end as of May 16, 2026, and can be installed in crontab any time the operator wants to start using burst-mode in production. When Jarvis ships, the cron entries are removed and the supervisor loop takes over.

#### Pipeline scheduling philosophy [NEW in v17]

**Sequential burst beats concurrent standard.** The designed scheduling pattern for multi-pipeline days (e.g., news synthesis followed by financial Phase A pre-market) is:

1. T1-idle window detected or operator yields T1
2. Burst-up → run news pipeline to completion
3. Burst-down → brief pause (optional, ~21s)
4. Burst-up → run financial Phase A to completion
5. Burst-down → T1 restored for interactive work

This sequential burst approach completes both pipelines faster in aggregate than running them concurrently with T1 up in standard mode. The math: news (~6–10 min burst) + financial (~44 min burst) + two transition cycles (~42s) ≈ **55 minutes total**. Running both under standard T2 with T1 resident: news (~25–40 min) + financial (~3.5 hr) concurrently ≈ **3.5+ hours, at lower quality due to constrained context and slow throughput.**

Do not schedule overlapping burst windows. The cron registry check at burst-up enforces this (first scheduled wins, second defers), but the underlying principle is architectural: sequential is the design, not a limitation.

**Jarvis schedule awareness is load-bearing.** Jarvis must know the pipeline schedule to give the operator advance notice when burst windows are approaching. "Financial pipeline in 5 min, are you done with T1?" requires Jarvis to have schedule visibility, not just reactivity. Phase 18 build must include: reading the pipeline cron registry at startup, surfacing upcoming windows in the morning briefing, and proactively notifying 5–10 min before each window opens.

---

### 18.1 Architecture Overview

Jarvis is three things composed together:

```
┌─────────────────────────────────────────────────────────────────┐
│  MacBook (always-on daemon via launchd)                         │
│                                                                 │
│  openWakeWord listener → detects "Hey Jarvis"                   │
│      │                                                          │
│      └── records audio until 1.5s silence                      │
│          → POST audio to http://100.101.244.6:4300/listen       │
│          ← receives TTS audio bytes from Chatterbox             │
│          → plays audio locally (sounddevice)                    │
└─────────────────────────────────────────────────────────────────┘
                            │ Tailscale
┌─────────────────────────────────────────────────────────────────┐
│  monarch — Jarvis FastAPI service (port 4300)                   │
│                                                                 │
│  /listen   ← audio bytes → faster-whisper STT (CPU)            │
│                → text → T1 via LiteLLM (port 4000)             │
│                → response text → Chatterbox TTS                 │
│                → audio bytes back to MacBook client             │
│                                                                 │
│  /briefing ← cron 06:30 → queries Postgres daily_stream_outputs│
│                → synthesis call to T1                           │
│                → TTS → plays on MacBook + pushes card to PWA   │
│                                                                 │
│  /notify   ← internal: other services POST anomaly events here  │
│                → routes to PWA WebSocket + ntfy.sh              │
│                                                                 │
│  /ws       ← WebSocket: Command Center PWA holds this open      │
│                → real-time notification cards pushed here        │
│                                                                 │
│  /health   ← inference-up checks this at startup               │
└─────────────────────────────────────────────────────────────────┘
```

**Why T1 and not a dedicated model slot.** Jarvis queries are conversational and low-frequency — morning briefing (~1/day), anomaly summaries (~0-5/day), ad-hoc questions (<10/day). These fit comfortably within T1's `-np 2` parallel slots without competing meaningfully with OpenCode sessions. A dedicated model slot would cost VRAM the budget doesn't have. T1 is the right home.

**Why CPU Whisper.** faster-whisper medium runs at roughly 1-2 seconds transcription latency on the 9900X (12 cores). That's the correct trade-off: VRAM is the binding constraint on this machine, and the STT latency floor is already set by wake-word detection + audio recording, not by Whisper. GPU Whisper would add ~1-2 GB VRAM pressure for no perceptible latency improvement.

---

### 18.2 MacBook Component — Always-Listening Daemon

**Stack:**
- `openWakeWord` — wake-word detection (MIT license, CPU-only, <1% CPU at idle)
- `sounddevice` — audio capture + playback
- `requests` — HTTP to Jarvis endpoint over Tailscale
- `launchd` — macOS service manager for always-on restart behavior

**Install on MacBook:**
```bash
pip3 install openwakeword sounddevice requests numpy
# openWakeWord ships pre-trained models including "hey_jarvis" variants
# or train a custom "Hey Jarvis" model with ~20-30 positive samples via openWakeWord's training API
```

**Listener script — `~/bin/jarvis-listener.py` (MacBook):**
```python
import numpy as np
import sounddevice as sd
import requests
import io
import time
from openwakeword.model import Model

JARVIS_ENDPOINT = "http://100.101.244.6:4300/listen"
WAKE_WORD_MODEL  = "hey_jarvis"   # or path to custom .tflite model
SAMPLE_RATE      = 16000
SILENCE_SECONDS  = 1.5
CHUNK_FRAMES     = 1280           # openWakeWord expects 80ms chunks at 16kHz

oww = Model(wakeword_models=[WAKE_WORD_MODEL], inference_framework="tflite")

def record_until_silence(stream, silence_s=SILENCE_SECONDS, threshold=0.01):
    """Record audio until silence_s seconds of silence detected."""
    frames = []
    silence_chunks = int(silence_s * SAMPLE_RATE / CHUNK_FRAMES)
    silent_count = 0
    while True:
        chunk, _ = stream.read(CHUNK_FRAMES)
        frames.append(chunk.copy())
        rms = np.sqrt(np.mean(chunk**2))
        if rms < threshold:
            silent_count += 1
        else:
            silent_count = 0
        if silent_count >= silence_chunks:
            break
    return np.concatenate(frames, axis=0)

def play_audio_bytes(audio_bytes: bytes):
    """Play WAV bytes returned from Chatterbox."""
    import wave, io
    with wave.open(io.BytesIO(audio_bytes)) as wf:
        data = wf.readframes(wf.getnframes())
        arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(arr, samplerate=wf.getframerate(), blocking=True)

def main():
    print("Jarvis listener active.")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.float32,
                        blocksize=CHUNK_FRAMES) as stream:
        while True:
            chunk, _ = stream.read(CHUNK_FRAMES)
            oww.predict(chunk)
            scores = oww.prediction_buffer.get(WAKE_WORD_MODEL, [0])
            if scores and scores[-1] > 0.5:
                oww.reset()
                audio = record_until_silence(stream)
                # Send to Jarvis
                wav_io = io.BytesIO()
                import wave
                with wave.open(wav_io, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes((audio * 32768).astype(np.int16).tobytes())
                try:
                    r = requests.post(JARVIS_ENDPOINT,
                                      files={"audio": ("query.wav", wav_io.getvalue(), "audio/wav")},
                                      timeout=30)
                    if r.status_code == 200:
                        play_audio_bytes(r.content)
                except Exception as e:
                    print(f"Jarvis request failed: {e}")

if __name__ == "__main__":
    main()
```

**launchd plist — `~/Library/LaunchAgents/com.taolen.jarvis-listener.plist` (MacBook):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.taolen.jarvis-listener</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/trentdunkak/bin/jarvis-listener.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/trentdunkak/Library/Logs/jarvis-listener.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/trentdunkak/Library/Logs/jarvis-listener.log</string>
</dict>
</plist>
```

**Load the daemon:**
```bash
launchctl load ~/Library/LaunchAgents/com.taolen.jarvis-listener.plist
# Verify it's running:
launchctl list | grep jarvis
# Expect: a PID in the first column
```

**macOS microphone permission:** macOS requires explicit microphone permission for terminal applications. On first launch, grant access via System Settings → Privacy & Security → Microphone. The launchd daemon inherits this permission once granted.

---

### 18.3 Jarvis Service (monarch, port 4300)

**Location:** `~/services/jarvis/`

**Install dependencies:**
```bash
source ~/venv/inference/bin/activate
pip install fastapi uvicorn faster-whisper websockets httpx --break-system-packages
# Chatterbox is already self-hosted — Jarvis calls its API, doesn't install it inline
```

**`~/services/jarvis/app.py`:**

```python
import asyncio, io, wave, os
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
import httpx
from faster_whisper import WhisperModel

app = FastAPI()

# ── Models ──────────────────────────────────────────────────────────────────
whisper = WhisperModel("medium", device="cpu", compute_type="int8")

LITELLM_BASE    = "http://127.0.0.1:4000/v1"
LITELLM_KEY     = os.environ["LITELLM_MASTER_KEY"]
CHATTERBOX_URL  = "http://127.0.0.1:8888/tts"   # adjust to actual Chatterbox port
DB_URL          = os.environ.get("DATABASE_URL")  # Postgres connection string

JARVIS_SYSTEM = """
You are Jarvis, the voice manager for Trent's local AI infrastructure at Taolen Logic.
You have deep knowledge of the five-tier inference stack, all running pipelines, and
the six active project stacks (consultancy, exploratory-coding, design, content, leads,
financial). You speak in concise, direct sentences — you are briefing someone who is
busy, not writing a report. When surfacing anomalies, name the specific service,
the specific metric, and the specific number. When asked about something you don't have
current data for, say so plainly. Never fabricate system state.
"""

# ── WebSocket connection manager ─────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self.connections.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.connections:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ── STT → T1 → TTS pipeline ──────────────────────────────────────────────────
async def transcribe(audio_bytes: bytes) -> str:
    segments, _ = whisper.transcribe(io.BytesIO(audio_bytes), language="en")
    return " ".join(s.text for s in segments).strip()

async def reason(text: str, context: str = "") -> str:
    prompt = f"{context}\n\nUser: {text}" if context else text
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{LITELLM_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {LITELLM_KEY}"},
            json={"model": "qwen3.6-consultancy",
                  "messages": [{"role": "system", "content": JARVIS_SYSTEM},
                                {"role": "user",   "content": prompt}],
                  "max_tokens": 300, "temperature": 0.4})
    return r.json()["choices"][0]["message"]["content"]

async def synthesize(text: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(CHATTERBOX_URL, json={"text": text})
    return r.content   # WAV bytes

# ── Endpoints ────────────────────────────────────────────────────────────────
@app.post("/listen")
async def listen(audio: UploadFile = File(...)):
    raw = await audio.read()
    transcript = await transcribe(raw)
    context = await build_status_context()
    response_text = await reason(transcript, context)
    tts_audio = await synthesize(response_text)
    # Also push as a notification card to PWA
    await manager.broadcast({"type": "voice_exchange",
                              "query": transcript,
                              "response": response_text})
    return Response(content=tts_audio, media_type="audio/wav")

@app.get("/briefing")
async def briefing():
    """Generate morning briefing from last 24h of compiled stream outputs."""
    import asyncpg
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT stream, stage, content FROM daily_stream_outputs
        WHERE output_date = CURRENT_DATE AND stage IN ('compilation','assembly')
        ORDER BY stream, stage
    """)
    await conn.close()
    combined = "\n\n".join(r["content"] for r in rows)
    briefing_prompt = f"""
    Produce a spoken morning briefing from the following compiled intelligence.
    Target length: 90-120 seconds spoken (roughly 220-280 words).
    Open with the date and one sentence on the most significant overnight development.
    Cover AI/Tech, then Political/Financial, then any cross-stream signals.
    Close with any pipeline anomalies from the validation telemetry if present.
    Be specific: names, numbers, tickers. No filler phrases.

    SOURCE BLOCKS:
    {combined}
    """
    text = await reason(briefing_prompt)
    audio = await synthesize(text)
    await manager.broadcast({"type": "briefing", "text": text})
    return Response(content=audio, media_type="audio/wav")

@app.post("/notify")
async def notify(event: dict):
    """
    Internal endpoint — other services POST anomaly events here.
    Jarvis routes them to the PWA WebSocket and ntfy.sh.
    Expected payload: {severity, service, message, detail}
    """
    await manager.broadcast({"type": "notification", **event})
    # ntfy.sh push
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post("https://ntfy.sh/YOUR_NTFY_TOPIC",
            headers={"Title": f"[{event.get('severity','INFO')}] {event.get('service','')}",
                     "Priority": "high" if event.get("severity") == "ERROR" else "default"},
            content=event.get("message", ""))
    return {"status": "routed"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()   # keep alive — client sends pings
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "jarvis",
            "pwa_clients": len(manager.connections)}

# ── Status context builder ────────────────────────────────────────────────────
async def build_status_context() -> str:
    """Query telemetry tables to give T1 current system state as context."""
    try:
        import asyncpg
        conn = await asyncpg.connect(DB_URL)
        val = await conn.fetch("""
            SELECT source_model, verdict, COUNT(*) as n
            FROM validation_telemetry
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY source_model, verdict
        """)
        swaps = await conn.fetch("""
            SELECT requested_adapter, COUNT(*) as n, AVG(drain_ms) as avg_drain
            FROM lora_swap_telemetry
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY requested_adapter
        """)
        await conn.close()
        val_str = "\n".join(f"  {r['source_model']} {r['verdict']}: {r['n']}" for r in val)
        swap_str = "\n".join(f"  {r['requested_adapter']}: {r['n']} swaps, avg drain {r['avg_drain']:.0f}ms"
                             for r in swaps)
        return f"LAST 24H VALIDATION:\n{val_str}\nLORA SWAPS:\n{swap_str}"
    except Exception as e:
        return f"(telemetry unavailable: {e})"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4300)
```

---

### 18.4 Morning Briefing — Cron Integration

Add to crontab after news pipeline synthesis completes:

```bash
# Crontab additions (monarch)
# Morning briefing via Jarvis — 06:30 (5 min after news pipeline trigger, 3-4 min synthesis)
30 6 * * * curl -s http://127.0.0.1:4300/briefing > /dev/null 2>&1
```

The briefing endpoint queries `daily_stream_outputs` for today's compiled blocks, calls T1 for synthesis, plays TTS via the MacBook wake-word client's audio channel, and simultaneously pushes a briefing card to the PWA WebSocket. The operator wakes up and it plays; if they're already at their desk it's queued and available via the PWA's Jarvis panel.

---

### 18.5 Anomaly Notification Pattern — Other Services → Jarvis

Services that currently write to Postgres telemetry (validation gate, LoRA dispatcher) can also POST to Jarvis `/notify` when a threshold is crossed. Add this to the validation gate's verdict handler:

```python
# In validation-gate/app.py — add after writing telemetry row
if verdict == "fail":
    import httpx
    with httpx.Client(timeout=5) as client:
        client.post("http://127.0.0.1:4300/notify", json={
            "severity":  "WARN",
            "service":   "validation-gate",
            "message":   f"Output failed validation — {workflow_id}",
            "detail":    f"grounding={grounding_score:.2f} voice={voice_score:.2f}"
        })
```

Mirror the pattern in the LoRA dispatcher for drain timeouts and adapter swap failures. Jarvis becomes the single notification egress point — everything routes through it to both the PWA and ntfy.sh.

---

### 18.6 What Jarvis Knows — Data Sources by Capability

| Capability | Data source | Status |
|---|---|---|
| Morning intelligence briefing | `daily_stream_outputs` (Postgres) | ✅ Available once news pipeline Phase 3 live |
| Validation gate status | `validation_telemetry` (Postgres) | ✅ Available once gate is live |
| LoRA adapter state | `lora_swap_telemetry` (Postgres) | ✅ Available once dispatcher is live |
| Inference tier health | `inference-status` output (parsed) | ✅ Available now |
| n8n workflow status | n8n REST API (port 5678 via Tailscale) | ✅ Available now |
| Improvement ledger summaries | `improvement_ledger` (Postgres) | ⬜ When ledger service is built |
| Codebase change summaries | Nexus index (Postgres + pgvector) | ⬜ When nexus is built |
| Decision history | 2nd brain (Postgres + pgvector) | ⬜ When 2nd brain is built |

Jarvis is designed to grow with the knowledge systems. Each new data source that comes online (improvement ledger → nexus → 2nd brain) is a new table query added to `build_status_context()` and a new capability Jarvis can speak to. No architectural changes needed — it's additive.

---

### 18.7 Verification Checkpoints — Jarvis

**Checkpoint J1 — MacBook daemon is running:**
```bash
# On MacBook
launchctl list | grep jarvis
# Expect: PID in first column, 0 exit status in second
tail -f ~/Library/Logs/jarvis-listener.log
# Expect: "Jarvis listener active." and no Python errors
```

**Checkpoint J2 — Wake-word detection fires:**
```bash
# Say "Hey Jarvis" near MacBook microphone
# Expect: log line "Wake word detected" and a POST to port 4300
# If no detection: check microphone permissions in System Settings → Privacy → Microphone
```

**Checkpoint J3 — Jarvis service health (monarch):**
```bash
curl -s http://100.101.244.6:4300/health
# Expect: {"status":"ok","service":"jarvis","pwa_clients":0}
```

**Checkpoint J4 — STT round-trip:**
```bash
# Speak: "Hey Jarvis, what time is it?"
# Expect: Chatterbox audio plays back on MacBook within ~4-6 seconds
# Latency breakdown: wake-word 0s | recording 1.5s | Tailscale RTT <5ms |
#   Whisper medium CPU 1-2s | T1 inference 1-3s | TTS 0.5-1s | playback
```

**Checkpoint J5 — Morning briefing endpoint:**
```bash
curl -s http://127.0.0.1:4300/briefing -o /tmp/briefing.wav
# Expect: WAV file, non-zero size
# If 500: daily_stream_outputs may not have today's compiled blocks yet
#   (run news pipeline first, or test against yesterday's date by temporarily patching the query)
```

**Checkpoint J6 — Notify endpoint routes to PWA:**
```bash
curl -s -X POST http://127.0.0.1:4300/notify \
  -H "Content-Type: application/json" \
  -d '{"severity":"INFO","service":"test","message":"Jarvis notification test","detail":"smoke test"}'
# Expect: {"status":"routed"}
# Expect: notification card appears in Command Center Jarvis panel (if PWA is open)
# Expect: ntfy.sh notification received on mobile (if ntfy.sh topic is configured)
```

---

### 18.8 Failure Modes — Jarvis

**Checkpoint J2 fails: wake word not detecting.**
- macOS microphone permission not granted to the Python process. Fix in System Settings → Privacy & Security → Microphone.
- openWakeWord model not downloaded. Run `python -c "from openwakeword.model import Model; m = Model(wakeword_models=['hey_jarvis'])"` once to trigger download.
- If using a custom `.tflite` model: confirm the path in the listener script matches the actual file location.

**Checkpoint J4 fails: audio plays but is garbled.**
- Chatterbox port mismatch. Confirm `CHATTERBOX_URL` in `app.py` matches the actual Chatterbox serve port.
- Confirm `play_audio_bytes` sample rate matches Chatterbox's output (Chatterbox defaults to 22050 Hz — adjust `wf.setframerate` in the listener if needed).

**Checkpoint J4: latency > 15 seconds.**
- T1 is likely busy with an OpenCode session. Jarvis uses the second parallel slot (`-np 2`) but if both are occupied, the query queues. Acceptable for low-frequency use. If it becomes chronic: add a `model: qwen3.6-pipeline` fallback in the Jarvis reasoning call to overflow to T2 when T1 is saturated.

**Checkpoint J5 fails: `daily_stream_outputs` empty.**
- News pipeline Phase 3 is not yet live. Interim: Jarvis briefing falls back to a system-status-only brief (validation telemetry + inference health). Patch `build_status_context()` to handle the empty-table case gracefully.

**MacBook daemon dies silently.**
- launchd's `KeepAlive: true` restarts it automatically. Check `~/Library/Logs/jarvis-listener.log` for the restart reason.
- If it's crashing on import: the Python environment on MacBook may be missing a dependency. Run `pip3 install openwakeword sounddevice requests numpy` again.

---

## Phase 19 — Command Center PWA

*Added v15. The Command Center is the operator's unified glass panel — a React PWA served on port 3000 over Tailscale that surfaces what every part of the system is doing in one place. It is read-oriented: it shows state, pushes notifications, and deep-links to where action is needed. It does not control workflows, edit n8n, or interact with the inference tiers directly. All control remains in the actual tools.*

---

### 19.1 Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│  Command Center PWA (port 3000, Tailscale-only)                    │
│  React SPA, built to ~/projects/command-center/dist/               │
│  Served: nginx or `npx serve -s -p 3000`                          │
│                                                                    │
│  Data reads ──► Read-only API (port 4400)                         │
│                 ├── validation_telemetry (Postgres)                │
│                 ├── lora_swap_telemetry (Postgres)                 │
│                 ├── daily_stream_outputs (Postgres)                │
│                 ├── n8n API proxy (port 5678)                      │
│                 └── inference-status (bin/inference-status output) │
│                                                                    │
│  Real-time ────► Jarvis WebSocket (port 4300/ws)                  │
│                  notifications, briefing cards, anomaly events      │
│                                                                    │
│  Mobile push ──► ntfy.sh (routed through Jarvis /notify)          │
│                                                                    │
│  Deep links ───► n8n editor  http://100.101.244.6:5678            │
│                  SSH terminal (Tailscale SSH URL)                   │
│                  OpenCode serve (port 8090 when running)           │
│                  LiteLLM admin UI (port 4000/ui if enabled)        │
└────────────────────────────────────────────────────────────────────┘
```

**What it is NOT:**
- Not a control plane. It cannot trigger n8n workflows, modify config files, restart services, or interact with models.
- Not a chat interface. Jarvis handles voice interaction. The PWA surfaces Jarvis's output as cards, not a chat window.
- Not a public endpoint. Tailscale-only, no Funnel. `N8N_SECURE_COOKIE` flips to `true` when this goes live.

---

### 19.2 Read-Only Data API (port 4400)

The PWA never queries Postgres directly from the browser. All data flows through this thin FastAPI service, which enforces read-only access, handles CORS for the PWA origin, and presents a clean JSON API regardless of what's happening in the underlying services.

**Location:** `~/services/read-api/`

**Install:**
```bash
source ~/venv/inference/bin/activate
pip install fastapi uvicorn asyncpg httpx --break-system-packages
```

**`~/services/read-api/app.py`:**

```python
import os, json, subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg, httpx

app = FastAPI()

# Allow PWA origin (port 3000 on same Tailscale IP)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://100.101.244.6:3000"],
    allow_methods=["GET"],
    allow_headers=["*"])

DB_URL   = os.environ["DATABASE_URL"]
N8N_URL  = "http://127.0.0.1:5678"
N8N_KEY  = os.environ.get("N8N_API_KEY", "")   # set in api_keys.env if n8n API auth is enabled

# ── Validation telemetry ──────────────────────────────────────────────────────
@app.get("/telemetry/validation")
async def validation_summary(hours: int = 24):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT source_model,
               COUNT(*) FILTER (WHERE verdict='pass')  as pass_n,
               COUNT(*) FILTER (WHERE verdict='warn')  as warn_n,
               COUNT(*) FILTER (WHERE verdict='fail')  as fail_n,
               AVG(voice_score)      as avg_voice,
               AVG(grounding_score)  as avg_grounding,
               AVG(duration_ms)      as avg_ms
        FROM validation_telemetry
        WHERE timestamp > NOW() - INTERVAL '%s hours'
        GROUP BY source_model
        ORDER BY source_model
    """ % hours)
    await conn.close()
    return [dict(r) for r in rows]

@app.get("/telemetry/validation/recent")
async def validation_recent(limit: int = 50):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT telemetry_id, timestamp, workflow_id, source_model,
               verdict, suggested_action, voice_score, grounding_score, duration_ms
        FROM validation_telemetry
        ORDER BY timestamp DESC LIMIT $1
    """, limit)
    await conn.close()
    return [dict(r) for r in rows]

# ── LoRA telemetry ────────────────────────────────────────────────────────────
@app.get("/telemetry/lora")
async def lora_summary(hours: int = 24):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT requested_adapter,
               COUNT(*)          as n_swaps,
               AVG(drain_ms)     as avg_drain_ms,
               AVG(swap_ms)      as avg_swap_ms,
               COUNT(*) FILTER (WHERE status='error') as n_errors
        FROM lora_swap_telemetry
        WHERE created_at > NOW() - INTERVAL '%s hours'
        GROUP BY requested_adapter
    """ % hours)
    await conn.close()
    return [dict(r) for r in rows]

# ── News intelligence ─────────────────────────────────────────────────────────
@app.get("/news/latest")
async def news_latest():
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT output_date, stream, stage, content, generated_at
        FROM daily_stream_outputs
        WHERE output_date = CURRENT_DATE
        ORDER BY stream, stage
    """)
    await conn.close()
    return [dict(r) for r in rows]

@app.get("/news/history")
async def news_history(days: int = 7):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT output_date, stream, stage, token_count, generated_at
        FROM daily_stream_outputs
        WHERE output_date >= CURRENT_DATE - INTERVAL '%s days'
          AND stage IN ('compilation','assembly')
        ORDER BY output_date DESC, stream, stage
    """ % days)
    await conn.close()
    return [dict(r) for r in rows]

# ── n8n workflow proxy ────────────────────────────────────────────────────────
@app.get("/workflows")
async def workflows():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{N8N_URL}/api/v1/workflows",
                             headers={"X-N8N-API-KEY": N8N_KEY} if N8N_KEY else {})
    return r.json()

@app.get("/workflows/executions")
async def executions(limit: int = 20):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{N8N_URL}/api/v1/executions?limit={limit}",
                             headers={"X-N8N-API-KEY": N8N_KEY} if N8N_KEY else {})
    return r.json()

# ── Inference status ──────────────────────────────────────────────────────────
@app.get("/inference/status")
async def inference_status():
    """Run inference-status script and return parsed output."""
    result = subprocess.run(["~/bin/inference-status"], shell=True,
                            capture_output=True, text=True, timeout=10)
    # inference-status writes key metrics to stdout as JSON when called with --json flag
    # Until that flag is implemented, return raw text
    return {"raw": result.stdout, "exit_code": result.returncode}

# ── Pipeline runs ─────────────────────────────────────────────────────────────
@app.get("/pipelines/runs")
async def pipeline_runs(limit: int = 30):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch("""
        SELECT * FROM news_pipeline_runs
        ORDER BY started_at DESC LIMIT $1
    """, limit)
    await conn.close()
    return [dict(r) for r in rows]

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "read-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4400)
```

> **Read-only guarantee.** This service has no POST/PUT/DELETE endpoints and no write path to Postgres. The `asyncpg.connect()` call can be further hardened by using a read-only Postgres role: `CREATE ROLE dashboard_ro LOGIN PASSWORD '...' IN ROLE pg_read_all_data;` — point `DATABASE_URL` for this service at that role.

---

### 19.3 PWA Panel Layout

The Command Center is a single-page React app with a persistent left navigation and five panels. Each panel pulls from the Read API; the Jarvis panel additionally holds the WebSocket connection.

| Panel | Key data shown | Primary API routes |
|---|---|---|
| **Dashboard** | VRAM gauge, tier status (T1-T5 + gate + dispatcher), n8n container health, active Tailscale connection | `/inference/status`, `/health` checks on all services |
| **Intelligence** | Today's Stream A + B compiled blocks as readable cards, 7-day history strip | `/news/latest`, `/news/history` |
| **Pipelines** | n8n workflow list, last 20 executions with status badges, validation pass-rate sparklines per workflow | `/workflows`, `/workflows/executions`, `/telemetry/validation` |
| **System** | Validation telemetry table (last 50 verdicts), LoRA adapter usage charts, voice/grounding score trends | `/telemetry/validation/recent`, `/telemetry/lora` |
| **Jarvis** | Real-time notification stream (WebSocket cards), morning briefing text when available, notification history | Jarvis WebSocket `ws://100.101.244.6:4300/ws` |

**Notification cards** (surfaced in Jarvis panel and as banner overlays on all panels):

| Card type | Triggered by | Visual treatment |
|---|---|---|
| `briefing` | Morning cron via Jarvis `/briefing` | Full-width blue card, text expandable |
| `notification` severity=ERROR | Validation fail, dispatcher drain timeout | Red banner, persists until dismissed |
| `notification` severity=WARN | Validation warn, swap error | Yellow card, auto-dismisses after 60s |
| `notification` severity=INFO | Pipeline complete, n8n run success | Grey card, auto-dismisses after 10s |
| `voice_exchange` | Any Jarvis voice query | Compact card: query → response |

---

### 19.4 Deep Links

Deep links open in a new tab. They are always Tailscale-internal URLs — they only work when the device is on Tailscale.

| Target | URL | Notes |
|---|---|---|
| n8n editor | `http://100.101.244.6:5678` | Opens n8n workflow list |
| n8n specific execution | `http://100.101.244.6:5678/workflow/{id}/executions/{exec_id}` | Linked from Pipeline panel execution rows |
| Monarch SSH | `ssh://monarch@100.101.244.6` | Opens terminal SSH if OS has handler registered; otherwise show copy-to-clipboard |
| OpenCode serve | `http://100.101.244.6:8090` | Only linked when `/health` on 8090 returns 200 |
| LiteLLM admin | `http://100.101.244.6:4000/ui` | Only linked if LiteLLM UI is enabled |

---

### 19.5 N8N_SECURE_COOKIE — Flip Trigger

From Phase 5 tech debt:

> `N8N_SECURE_COOKIE=false` must be flipped to `true` once HTTPS is properly configured end-to-end with the React PWA.

**The trigger is the PWA going live on port 3000 over Tailscale.** The PWA itself is served over plain HTTP on the Tailscale network — this is acceptable because Tailscale traffic is already encrypted at the network layer (WireGuard). What `N8N_SECURE_COOKIE=true` requires is that the n8n session cookie is only sent over HTTPS. Since n8n is accessed via `http://100.101.244.6:5678` (internal Tailscale, not HTTPS), flipping this requires one of:

- **Option A (recommended):** Configure n8n behind a local nginx reverse proxy with a self-signed cert, and access n8n at `https://` via that proxy. The PWA deep link and Tailscale Funnel both use the HTTPS URL.
- **Option B:** Keep `N8N_SECURE_COOKIE=false` and document it as an accepted risk for a Tailscale-only deployment (Tailscale WireGuard encryption provides the equivalent transport security). Mark the tech debt item as a deliberate decision, not an oversight.

**Recommended: Option B for now, Option A when the n8n proxy is worth the engineering.** Add this decision to Appendix A as an accepted architectural trade-off, not a ruled-out feature.

---

### 19.6 Build and Deploy

**Build:**
```bash
cd ~/projects/command-center
npm install
npm run build
# Output: ~/projects/command-center/dist/
```

**Serve (static, Tailscale-only):**
```bash
# Via npx serve (simplest)
npx serve dist -p 3000 -s

# Via nginx (if already installed — more robust for 24/7)
# /etc/nginx/sites-available/command-center:
# server {
#   listen 3000;
#   root /home/monarch/projects/command-center/dist;
#   index index.html;
#   location / { try_files $uri /index.html; }
# }
```

**Environment config for the React build (`~/projects/command-center/.env`):**
```env
VITE_API_BASE=http://100.101.244.6:4400
VITE_JARVIS_WS=ws://100.101.244.6:4300/ws
VITE_N8N_URL=http://100.101.244.6:5678
```

---

### 19.7 Verification Checkpoints — Command Center

**Checkpoint P1 — Read API health:**
```bash
curl -s http://100.101.244.6:4400/health
# Expect: {"status":"ok","service":"read-api"}
```

**Checkpoint P2 — Read API returns validation data:**
```bash
curl -s http://100.101.244.6:4400/telemetry/validation | python3 -m json.tool
# Expect: JSON array (may be empty if gate has no traffic yet — that's fine)
```

**Checkpoint P3 — Read API proxies n8n:**
```bash
curl -s http://100.101.244.6:4400/workflows | python3 -m json.tool
# Expect: JSON with n8n workflow list
```

**Checkpoint P4 — PWA loads:**
```bash
# From MacBook browser
open http://100.101.244.6:3000
# Expect: Command Center loads, Dashboard panel shows tier status
```

**Checkpoint P5 — PWA WebSocket connects to Jarvis:**
```bash
# Open Jarvis panel in PWA — connection indicator should show green
# Send a test notification:
curl -s -X POST http://127.0.0.1:4300/notify \
  -H "Content-Type: application/json" \
  -d '{"severity":"INFO","service":"test","message":"PWA WebSocket test"}'
# Expect: notification card appears in Jarvis panel within 1 second
```

**Checkpoint P6 — Mobile push (ntfy.sh):**
```bash
# Ensure ntfy.sh app is installed on phone and subscribed to your topic
curl -s -X POST http://127.0.0.1:4300/notify \
  -H "Content-Type: application/json" \
  -d '{"severity":"WARN","service":"test","message":"ntfy.sh mobile test"}'
# Expect: push notification arrives on phone within 5 seconds
```

---

### 19.8 Failure Modes — Command Center

**Checkpoint P1 fails: Read API connection refused.**
- Service not running. Start it: `tmux new-window -t inference -n read-api 'cd ~/services/read-api && python app.py'`
- UFW rule missing. Verify: `sudo ufw status | grep 4400`

**Checkpoint P3 fails: n8n proxy returns 401.**
- n8n API key not set or incorrect. Generate one in n8n → Settings → API Keys. Set `N8N_API_KEY` in `api_keys.env`.

**Checkpoint P4 fails: PWA loads but panels show no data.**
- CORS error. Open browser devtools → Console. If CORS errors appear: confirm `allow_origins` in read-api `app.py` matches the exact origin the PWA is served from (including port).
- `VITE_API_BASE` in `.env` doesn't match the actual Read API URL. Rebuild the PWA after fixing.

**Checkpoint P5 fails: WebSocket connects but no notification cards appear.**
- Jarvis `/notify` is routing to the WebSocket but the PWA is rendering the wrong message type. Check that `event.type` in the card renderer matches the payload's `type` field.

**PWA is accessible from public internet.**
- Funnel is not configured for port 3000 — this is correct. Verify: `curl -I https://monarch-b650i-lightning-wifi.tail89cb86.ts.net:3000` should timeout or refuse. If it doesn't, the Funnel config has a stray rule — run `tailscale funnel status` and remove it.

---

## Open Items — v19

**[v19 update]** Organized to mirror `INFRASTRUCTURE_BIBLE_v19.md` §18's Tier A through E priority structure. Every row from the prior v19 Open Items section is preserved below, reorganized by tier.

### Tier A — Validation work (small, closes gaps)

| # | Item | Status | Blocked by | Time |
|---|---|---|---|---|
| A1 | Rebalance Change 2 measurement | 🟡 Patched, measurement deferred | Next natural T1 restart (reboot or explicit control session kill); T1 context 36K → 24K committed in `c0f7ea7`. Needed to confirm post-Change-2 baseline absorbs T6 burst (~17-19 GB or ~21 GB depending on mode). | 5 min observation |
| A2 | AUTHORITY_SPEC Items 6-8 + Quota Cascade thresholds | ⏳ Pending | Walkthrough + threshold ratification (see Tier B-D5 below) | 30 min after walkthrough |
| A3 | Decision 4 cascade composition formalization | ⏳ Small mission | Throughput-tier model ambiguity used in leads/financial `opencode.jsonc` but not explicitly placed in cascade; Moonshot/Kimi key not acquired (Tier 3 of cascade theoretical); two-Pro saturation handling needs `quota.py` to make decidable. | 30 min docs + ongoing |
| A4 | `inference-up` cosmetic items | ⏳ Trivial | Baseline VRAM warning, LiteLLM "→ Tier 2" comment | 5 min |
| A5 | HANDOFF_v19.md date stamp refresh | ⏳ Trivial | — | 2 min |

### Tier B — Decisions still open

| # | Decision | Status | Blocked on |
|---|---|---|---|
| B-D2 | Decision 2 — Hermes adoption shape | ⏳ Blocked on prereq | v18 Hermes brainstorm documents may not exist as discrete artifacts (audit A7). Reconstruct from session histories, hunt earlier sessions, or close as "framing-only" — decision pending. |
| B-D3 | Decision 3 — T6 operational defaults | 🔴 Blocked | 21 GB T6 model download outstanding; `~/bin/t6-up` / `~/bin/t6-down` tooling not built; Rebalance Change 2 measurement (A1) not landed. Will pick between pure-VRAM (~21 GB) and partial-expert-offload (~17-19 GB) modes when unblocked. |
| B-D5.6 | Decision 5 Item 6 — Pro tier estimation | ⏳ Pending | Choose estimate model: single-axis (msg/5h sliding window per tier) vs two-axis (session + weekly cap tracked separately) vs three-factor (peak-hours acceleration multiplier). Anthropic support doc actual values: Pro ~45 msg/5h; Max 5x ~225 msg/5h; Max 20x ~900 msg/5h. Plus a weekly cap. Plus 5am-11am PT weekday burns ~1.5-2× faster (multiplier not published). Lean: two-axis. |
| B-D5.7 | Decision 5 Item 7 — Promotion threshold N | ⏳ Pending | Default N=10 (successful Tier 3 surfaces without operator regret → promote to Tier 2). Already written into spec inclusion criteria; Item 7 ratifies as policy. |
| B-D5.8 | Decision 5 Item 8 — Cold-start rule | ⏳ Pending | "All new actions begin in Tier 3" — operator confirm or revise. |
| B-D5.Q | Decision 5 Quota Cascade thresholds | ⏳ Pending | Numeric ratification of the 20% / 10% prepaid thresholds. Partner-derived from operator constraint "once the budget is hit, it's hit." Explicit operator confirmation of these specific numbers needed before Decision 5 formally closes. |

### Tier C — Phase 2 build work

| # | Item | Status | Prereq | Time |
|---|---|---|---|---|
| C0 | `vram.py` listener | ✅ LIVE | — | Built; runs 5s cadence; per-tier PID attribution, VRAM consumption, OOM thresholds; reusable `_port_from_cmdline()` pattern. |
| C0' | `tier_health.py` listener | ✅ LIVE | — | Built; runs 15s cadence; HTTP /health probes; states OK / DEGRADED / UNRESPONSIVE / IDLE (for burst-only). |
| C1 | `process.py` listener | ⏳ Spec-only | None (reuses `vram.py` patterns) | 2-3 hr. Drives the Tier 2 "restart on crash" autonomous action; tracks `rss_mb`, `cpu_pct`, `uptime_s`, `restart_count_24h`. Extends existing `tiers` domain — no new schema domain needed. |
| C2 | LiteLLM logging path decision | ✅ CLOSED 2026-05-24 | — | Path A ratified: separate `litellm_logs` DB on existing postgres instance, `store_prompts_in_spend_logs=false`. Implementation specifics deferred to Claude Code build-time (folded into C3 quota.py task). See PHASE2_SPEC §quota.py for the ratification block. |
| C3 | `quota.py` listener | ⏳ Spec-only | C2 + schema updates for `haiku_4_5` + `anthropic_api_direct` | 3-4 hr. Parses LiteLLM logs for spend / token / rate-limit proximity / cost-per-task. Hard limitation: Claude Pro doesn't expose quota via API — Pro usage walls are session-based and opaque; `quota.py` can only *estimate* Pro by counting requests/tokens. Estimate is "good enough to warn at 80% projected" but not authoritative. |
| C4 | `cron.py` listener | ⏳ Spec-only | None | 2-3 hr. Reconciles scheduled jobs vs actual runs. Detects missed runs, overlap collisions, resource pressure ("financial pipeline fires in 8 min, currently at 89% VRAM, T6 burst won't fit"). Easiest of the three to defer — mostly observability. |

### Tier D — Documentation cleanup

| # | Item | Where | Time |
|---|---|---|---|
| D1 | `ref-blueprint §Phase 15` rewrite | news-pipeline repo | 30 min |
| D2 | Per-stack `CONTEXT.md` updates | Six project repos | 1-2 hr total |
| D3 | Jarvis `CLAUDE.md` v0.2 update | jarvis repo | 30 min |
| D4 | `master_summary_v18.md` → `_v19.md` stable | Wherever master_summary lives | 2-4 hr (LAST — gated on Items 6-8 + Quota thresholds + Rebalance Changes 2-3) |

### Tier E — Larger workstreams

| # | Workstream | Status |
|---|---|---|
| E1 | Financial pipeline strategy doc + phase-level design | `FINANCIAL_STRATEGY_v19.md` proposed; answer the open §8.2 strategy questions in bible v19 first |
| E2 | Hermes / Pattern B implementation | After Decision 2 (B-D2) |
| E3 | T6 spin-up tooling | After Decision 3 (B-D3) + model download + Rebalance Change 2 measurement (A1) |
| E4 | Nexus 17.1 design phase | Per Decision 6, design-only in v19 |
| E5 | LoRA training (content + leads only; three high-stakes likely deferred per Decision 1) | Validation gate live + ≥1 week telemetry baseline |
| E6 | Improvement ledger service | Validation gate live |
| E7 | 2nd Brain 17.2 design | After Nexus operational |
| E8 | News-pipeline-evidence — complete 11-step build sequence | Phases 1-6 done; Phase 5 signal-class architecture drafted. See `news-pipeline-evidence-bible_v4.md` §10. |
| E9 | News-pipeline-evidence — cutover from old `~/projects/news-pipeline/` | When evidence layer is signal-class-complete; subscribers still see v18-era brief until then. |
| E10 | News-pipeline-evidence — LoRA's structurally-safe home (reasoning adjudicator, downgrade-only: VERIFIED → HEDGED, never reverse) | Designed; awaiting build slot. |

---

## Open Items — v16

Items completed during the May 16, 2026 bringup are marked ✅. New items introduced by the v16 changes are flagged **NEW v16**.

| Item | Status | Blocked by |
|---|---|---|
| Build llama.cpp from source against CUDA 12.8 (required for all five Qwen3.6 tiers) | ✅ Complete | — |
| Verify `-ngl` partial-offload produces coherent output on T2 (port 8083) and T3 (port 8084) | ✅ Complete (May 16, 2026) | — |
| Verify mmap weight sharing works across T1+T2+T3 (`free -m` should NOT show 3 × ~17 GB) | ✅ Complete — RAM at 17 GB used post-bringup, not 51 GB | — |
| Confirm Phi-4-mini coexists with T1+T2+T3 in VRAM budget | ✅ Complete — via llama.cpp pivot (vLLM crashed silently) | — |
| Confirm T5 small-model seed coexists with T1-T4 without RAM pressure | ✅ Complete | — |
| **CUDA 12.8 apt-mark hold** | ✅ Complete (May 16, 2026) **NEW v16** | — |
| **T1 reconfigure to np=1 + extended ctx** | ✅ Complete (May 16, 2026) **NEW v16** | — |
| **inference-burst-up / inference-burst-down scripts written and validated end-to-end** | ✅ Complete (May 16, 2026) **NEW v16** | — |
| **Patch `fail()` in inference-up to NOT tmux kill-session** | ⬜ **NEW v16** — one-line fix, defer until convenient | — |
| **Fix LiteLLM smoke-test routing-test to require non-empty content field** | ⬜ **NEW v16** — cosmetic, production calls unaffected | — |
| **Benchmark T1 generation speed end-to-end** | ⬜ **NEW v16** — left ungathered May 16 | T1 healthy |
| **Benchmark T3 generation speed end-to-end** | ⬜ **NEW v16** — left ungathered May 16 | T3 healthy |
| **Benchmark T5 generation speed end-to-end** | ⬜ **NEW v16** — left ungathered May 16 | T5 healthy |
| 24-hour soak test: five-tier standard mode under realistic n8n traffic | ⬜ **TOP PRIORITY** | First bringup ✅; just leave it running |
| **Backup n8n encryption key to second location** | 🔴 **HIGH RISK if unaddressed** | — |
| **Set up pg_dump cron + offsite copy** | 🔴 **HIGH RISK if unaddressed** | — |
| **Decide on Tailscale Funnel auth for n8n** (gate behind Tailscale-private OR add basic auth) | 🔴 **HIGH RISK if unaddressed** | — |
| **Cloud API key acquisition (DeepSeek V4 Flash/Pro, Kimi K2.6)** | ⬜ **NEW v16** — required for Mode 3 cloud fallback and LiteLLM overflow chains | — |
| **Uncomment LiteLLM cloud fallback chains** | ⬜ **NEW v16** | Cloud API keys acquired |
| Write `~/bin/session-consultancy`, `session-design`, `session-exploratory` (LoRA session wrappers, T1) | ⬜ Carried over | LoRAs trained |
| Train first LoRA (recommend: `content-marketing`) against the validation gate baseline | ⬜ Carried over | Validation gate baseline + ≥1 week telemetry |
| Build n8n sub-workflow that calls validation gate, switches on `suggested_action`, retries via DeepSeek V4 Flash on `fail` | ⬜ Carried over | Validation gate live + cloud keys |
| Calibrate `VOICE_PASS_THRESHOLD` and `GROUNDING_PASS_THRESHOLD` based on real workflow data | ⬜ Carried over | ≥1 week of validation gate telemetry |
| Wire first pipeline (news) through validation gate end-to-end | ⬜ Carried over | n8n sub-workflow built |
| **Install news pipeline burst cron entry** (`55 5 * * *` and `0 8 * * *`) | ⬜ **NEW v16** — defer until soak passes and burst trusted | 24h soak ✅ |
| Wire remaining pipelines through validation gate after first-pipeline thresholds are calibrated | ⬜ Carried over | First-pipeline calibration complete |
| Enforce per-workflow working directory discipline in n8n harness | ⬜ Carried over | Discipline layer foundation (Phase 16.2) |
| Implement git-gated agent commit pattern | ⬜ Carried over | Working-directory discipline live |
| Build daily morning report | ⬜ Carried over | Telemetry tables active with ≥7 days of data |
| Build weekly drift eval suite | ⬜ Carried over | ≥1 trained LoRA + 4 weeks baseline telemetry |
| **Begin nexus design conversation** | ⬜ Next major design item | Five-tier soak test complete |
| Build improvement-ledger service | ⬜ Carried over | Validation gate live |
| Wire operator disposition + downstream outcome capture into n8n workflows | ⬜ Carried over | Improvement-ledger service live |
| **Begin retrain/weighting design conversation** | ⬜ Design item | Nexus design conversation underway + ≥4 weeks improvement-ledger data |
| Build nexus after design specification | ⬜ Carried over | Nexus design specification |
| **Begin 2nd brain design conversation** | ⬜ After nexus | Nexus operational |
| Build 2nd brain after design specification | ⬜ Carried over | 2nd brain design specification |
| Build maintenance jobs (nightly nexus-update, weekly loose-ends scan, daily morning digest) | ⬜ Carried over | Both knowledge systems operational |
| Install openWakeWord on MacBook + train or download hey_jarvis wake-word model | ⬜ Carried over | — |
| Write and load MacBook launchd plist for jarvis-listener | ⬜ Carried over | openWakeWord install |
| Build `~/services/jarvis/` FastAPI service — **including v16 supervisor scope** | ⬜ Carried over (scope expanded v16) | faster-whisper + Chatterbox confirmed running |
| **Migrate Jarvis supervisor logic from burst-up/burst-down shell scripts into Jarvis FastAPI** | ⬜ **NEW v16** | Jarvis service base built |
| Confirm Chatterbox port and test TTS round-trip | ⬜ Carried over | Chatterbox self-hosted deployment |
| Wire validation gate and LoRA dispatcher to POST anomaly events to Jarvis `/notify` | ⬜ Carried over | Jarvis service live |
| Build `~/services/read-api/` FastAPI service | ⬜ Carried over | — |
| Create Postgres read-only role `dashboard_ro` and point Read API at it | ⬜ Carried over | Read API service built |
| Scaffold `~/projects/command-center/` React app | ⬜ Carried over | — |
| Build Dashboard panel (tier status + VRAM gauge + **burst-mode indicator** [NEW v16]) | ⬜ Carried over (scope expanded v16) | Read API `/inference/status` returns JSON |
| Build Intelligence panel (news briefing cards) | ⬜ Carried over | News pipeline Phase 3 live |
| Build Pipelines panel (n8n executions + validation sparklines) | ⬜ Carried over | Read API `/workflows/executions` confirmed |
| Build System panel (telemetry tables + score trend charts) | ⬜ Carried over | Validation gate live with traffic |
| Build Jarvis panel (WebSocket cards + notification history) | ⬜ Carried over | Jarvis service + WebSocket confirmed |
| Configure ntfy.sh topic + install app on phone | ⬜ Carried over | — |
| Decide N8N_SECURE_COOKIE flip (Option A: nginx proxy, Option B: accept trade-off) | ⬜ Carried over | PWA go-live |
| Add `inference-up` bringup steps for Jarvis (4300), Read API (4400), PWA (3000) | ⬜ Carried over | Services built |
| Add `~/bin/inference-up` VRAM ceiling check after Jarvis start (should be 0 VRAM — CPU-only) | ⬜ Carried over | inference-up updated |

---

## Recommended Build Order — Phase 18 + 19

The open items table above lists all tasks; this section sequences them into the fastest path to a working system. Dependencies are real — skipping the order produces dead ends.

**Stage 1 — Read API (no dependencies, start here)**

Build `~/services/read-api/` first. It has zero external dependencies beyond Postgres and n8n already running, and it gives you a testable data layer immediately — even with empty telemetry tables the workflow and n8n endpoints work. This also validates the Tailscale UFW rule for port 4400 before anything else needs it.

```
Build read-api service → confirm Checkpoints P1, P2, P3 → create dashboard_ro Postgres role
```

**Stage 2 — Command Center scaffold + Dashboard panel**

Scaffold the React PWA and build the Dashboard panel against the live Read API. The Dashboard only needs `/inference/status` and health checks — it works before any telemetry exists. This gets the glass panel on screen early and validates the port 3000 UFW rule and CORS config before the more complex panels are built.

```
Scaffold command-center → configure .env → build Dashboard panel → confirm Checkpoints P4
```

**Stage 3 — Chatterbox confirmation + Jarvis service**

Before building Jarvis, confirm Chatterbox is running and its port. Then build `~/services/jarvis/`. Test the `/listen` endpoint via a direct HTTP POST with a WAV file before touching the MacBook daemon — isolate the monarch-side pipeline first.

```
Confirm Chatterbox port → build jarvis service → test /listen via curl → confirm Checkpoints J3, J4
```

**Stage 4 — MacBook daemon**

Once Jarvis is responding on port 4300, install openWakeWord on the MacBook, write the listener script, load the launchd plist. This is the last step, not the first — the daemon is useless until the endpoint it calls is working.

```
Install openWakeWord → write jarvis-listener.py → load launchd plist → confirm Checkpoints J1, J2
```

**Stage 5 — Jarvis panel + WebSocket in PWA**

With Jarvis running and the WebSocket live, build the Jarvis panel in the Command Center. Confirm Checkpoint P5 (WebSocket cards appear). Wire ntfy.sh topic and confirm Checkpoint P6 (mobile push).

```
Build Jarvis panel → confirm P5 → configure ntfy.sh → confirm P6
```

**Stage 6 — Wire anomaly notifications + remaining PWA panels**

Wire the validation gate and LoRA dispatcher to POST to Jarvis `/notify` on threshold crossings. Then build the Intelligence, Pipelines, and System panels — these depend on the validation gate having real traffic and the news pipeline Phase 3 being live, so they are last.

```
Wire gate + dispatcher → confirm J6 → build Intelligence panel (needs news Phase 3) →
build Pipelines panel → build System panel (needs gate traffic)
```

**Stage 7 — Decide N8N_SECURE_COOKIE + update inference-up**

Once all services are stable, make the N8N_SECURE_COOKIE decision (Option A: nginx proxy, Option B: accepted trade-off) and add Jarvis, Read API, and PWA start commands to `~/bin/inference-up` so they come up automatically on boot.

```
N8N_SECURE_COOKIE decision → update inference-up → confirm services survive reboot
```

**Summary table:**

| Stage | What gets built | Unblocks |
|---|---|---|
| 1 | Read API (4400) | PWA data layer, all panels |
| 2 | PWA scaffold + Dashboard panel | Visual confirmation, CORS validation |
| 3 | Jarvis service (4300) | Voice interaction, WebSocket bus |
| 4 | MacBook daemon (launchd) | Always-on wake-word |
| 5 | Jarvis PWA panel + ntfy.sh | Real-time notifications, mobile push |
| 6 | Anomaly wiring + remaining panels | Full monitoring surface |
| 7 | inference-up update + cookie decision | Production-hardened boot sequence |

---

## Appendix A — Ruled-Out Features Log

This appendix is permanent and load-bearing. Scattered "why not" rationales from across the document are consolidated here. Before re-proposing anything on this list, cite the original rationale and explain specifically what has changed. Re-opening without a changed-circumstance argument wastes design time.

| Feature | Ruled Out Because | Re-open Condition |
|---|---|---|
| **MusicGen (local audio generation)** | CC-BY-NC-4.0 license — incompatible with monetized YouTube (TheCoolBreezeVibe). Any content generated with it could trigger copyright claims on monetized uploads. | License changes to a permissive commercial license. |
| **Suno v4 (AI music generation)** | Suno's Terms of Service prohibit commercial use without a paid Enterprise plan. Free/Pro tiers do not cover monetized YouTube. | Suno offers a viable commercial license at acceptable cost, or a self-hostable open-weight alternative with CC-BY or Apache 2.0 license emerges. |
| **Goose as primary harness** | Unresolved tool-calling regression with Qwen3-Coder via Ollama where >5–6 tools causes XML-fallback rather than proper JSON tool calls. Reference: `block/goose#6883`. Pairing Goose with Claude Pro avoids the bug, but if Claude is the model, Claude Code is the better-fitting harness anyway. | `block/goose#6883` is resolved and confirmed fixed in a released version; Qwen3-Coder tool calls tested to pass at 8+ tools without XML fallback. |
| **Cline as primary harness** | VS Code extension with per-action approval gates. Optimized for developers writing code by hand — approval granularity is counter to the delegation pattern this stack uses. Not compatible with headless n8n integration. | Cline ships a headless/server mode with delegation-style permission scoping. |
| **GLM-4.7 full local** | Minimum 128 GB RAM for 2-bit quantization. This machine has 96 GB. Borderline even if MoE offload math worked out; not worth engineering vs using GLM-4.7-Flash locally and full via API. | Monarch RAM upgraded to 192 GB+, or a quantization method achieves GLM-4.7 full at ≤80 GB RAM. |
| **DeepSeek V4 Flash local** | ~158 GB minimum at practical quantization. Exceeds the 96 GB RAM + 4 TB NVMe envelope for acceptable inference speed. Use DeepSeek API instead. | Hardware upgrade to 256 GB+ RAM, or a sub-50 GB quantization that maintains benchmark parity is published. |
| **Kimi K2.6 local** | 1T MoE architecture, ~240 GB minimum even at 1.8-bit quantization, yielding ~1 tok/s on this hardware. Not viable. Use Moonshot API. | Hardware dramatically exceeds current specs, or a Kimi K2.6 distillate is published that fits the envelope. |
| **Flat AGENTS.md as canonical (Phase 11 model)** | Deprecated in v8 when the CONSTITUTION/CONTEXT dual-file pattern was adopted. Flat AGENTS.md mixes permanent identity (should never change casually) with living state (should update every session) — causes drift. CONSTITUTION.md is now canonical; AGENTS.md and CLAUDE.md are both symlinks. | N/A — architectural improvement. CONSTITUTION/CONTEXT is strictly better. Do not revert. |
| **Cowork as project harness** | `~/financial-cowork/` retired in v7. Cowork's collaboration model doesn't map to a solo operator with a local GPU stack. Financial pipeline moved to `~/projects/financial/` with standard `.opencode/` layout. | N/A — deprecated. |
| **vLLM multi-LoRA hot-swap on Qwen3.6-27B** | Qwen3.6-27B is a Qwen3-Next hybrid architecture (Gated DeltaNet linear-attention + Gated softmax attention + native MTP head). vLLM's `SupportsLoRA` mixin is implemented only for standard dense/MoE softmax architectures. Open issues: vLLM #18120, #40005. No production multi-LoRA recipe for any Qwen3-Next family model exists in vLLM main, nightly, or vLLM Recipes as of May 2026. Additionally, the UD-Q4_K_XL GGUF quant recommended for quality reasons is incompatible with vLLM's quantization stack (AWQ/GPTQ/FP8 only). These two constraints together — hybrid architecture + GGUF format — make vLLM wrong for this role. llama.cpp with `/lora-adapters` endpoint swap is the correct substitute. *(Ruled out v13.)* | vLLM ships stable `SupportsLoRA` for Qwen3-Next hybrid topology AND an official Qwen3.6 multi-LoRA recipe appears in vLLM Recipes/docs. Then re-evaluate whether PagedAttention concurrency gains justify switching back from llama.cpp. |
| **Overnight automated refactoring via qwen-coder-deep** | Qwen3-Coder-Next 80B-A3B under MoE expert offload runs at 3-5 tok/s. Nightly token budget (~70-86k in 8 hours) does not scale with codebase growth — a real refactor pass on a growing project touches 20+ files, and budget exhaustion produces accumulating half-finished refactors. With two Claude Pro subscriptions in the operator's daytime workflow, the "more brain right now" niche is filled by interactive Claude Pro (zero-second latency, no tier juggling, no half-finished overnight artifacts). For overnight cloud-batch work, DeepSeek V4 Pro provides orders of magnitude more throughput at ~$2-8/night versus 70k local tokens that arrive half-done. *(Ruled out v14.)* | Tokens-per-second on local 80B-class MoE models reaches >20 tok/s on the same hardware (e.g., a future inference engine optimization or hardware refresh), AND the operator's interactive workflow stops including Claude Pro tabs as the heavy-code fallback. Both conditions, not either. |
| **Multi-mode inference switching (overnight-deep, pipeline-heavy, standard)** | A mode-switch architecture was considered (cron-driven takedown of T1+T3 to free VRAM/RAM for qwen-coder-deep overnight, separate "pipeline-heavy" mode with parallel T2 instances). Rejected because: (a) the overnight use case it served is itself ruled out (see above), (b) LiteLLM fallback chains handle pipeline bursts cleanly without takedown, (c) mode-switching adds takedown-failure surface area that can leave the stack in a degraded state into the operator's morning sessions. The five-tier "standard" mode runs 24/7; bursty workloads spill to cloud via LiteLLM. *(Ruled out v14.)* | The overnight refactor use case is reopened (see above), OR a workload appears that genuinely needs >2 parallel T2 instances to meet SLA (none currently exists). |
| **Per-request multi-LoRA serving on Tier 1 (vLLM punica-style)** | llama.cpp's `/lora-adapters` endpoint serves one active adapter at a time per llama-server process. Per-request multi-adapter serving (where two simultaneous requests can use different adapters in parallel) requires vLLM's punica kernel, which does not support the Qwen3-Next hybrid architecture (see the vLLM ruled-out entry above). For the solo-operator session pattern — one OpenCode session at a time, with the operator choosing which adapter to load via session wrapper — session-swap on T1 is functionally equivalent. Building per-request multi-LoRA would either require switching the base model away from Qwen3.6 (giving up the coding benchmarks) or running multiple T1 instances (no VRAM budget). *(Ruled out v14.)* | The operator's workflow pattern changes to require concurrent specialist sessions (e.g., two OpenCode sessions running in parallel with different LoRAs), AND vLLM ships `SupportsLoRA` for Qwen3-Next hybrid, AND VRAM budget permits dual T1 instances (which it does not on a single 3090). |
| **Closed-loop automated LoRA retraining on validation-passed outputs** | Collecting gate-passing outputs as positive examples and periodically fine-tuning the LoRA on them is a closed loop with no external ground truth. It degrades, and degrades invisibly because the gate that is gamed is also the drift detector. Three named failure modes: (a) model collapse — training on own outputs reinforces existing subtle errors, converging toward "more confidently whatever I already was" not toward good; (b) Goodhart — once "passes the gate" is the training target, the model learns to produce gate-passing outputs, and voice/grounding scores stop measuring quality; (c) Phi-4 noise distillation — the gate grades with Phi-4-mini, so a loop trained on its approvals mathematically distills a weaker model's preferences into a stronger model. *(Ruled out v14.)* | An external ground-truth signal (operator disposition + downstream business outcome, captured by the improvement-ledger) is in the loop AND retraining is human-reviewed and runs on a deliberate cadence (quarterly, not a cron) AND the validation gate is kept strictly as an independent evaluator that is never a training target. All conditions, not any. |
| **Single-scalar self-reinforcing knowledge weighting** | Ranking retrieved nexus/2nd-brain information on one "quality" scalar conflates grade, recency, authority, and polarity. It recreates the closed-loop collapse inside the retrieval layer: high-weight info is retrieved more → reused → re-synthesized → inherits the weight, so a once-high-confidence conclusion is cited forever including after it goes stale. It also buries failures (a buried dead-end is rediscovered), when failed approaches have high value *as* failures and must be a separately-queried class. *(Ruled out v14.)* | The weighting model has mandatory time decay AND a meaningful weight component from external outcome signal (not purely internal grade at creation) AND negative knowledge is a first-class separately-queried class with mandatory per-record re-open conditions. All conditions, not any. |
| **vLLM 0.20.1 for Phi-4-mini fp8 serving on Ampere SM86 + CUDA 12.8** | Silently crashes at FlashAttention V2 initialization with no traceback. Reproduced May 16, 2026 across four launch variants (default 0.12 gpu-mem-util / bumped to 0.18 / `--enforce-eager` / `--max-model-len 4096`). Last log line is always `Using FlashAttention version 2` then process dies. llama.cpp serving the same model at Q4_K_M GGUF on the same hardware delivers 206 tok/s gen — substantially better than the vLLM design intent. The entire stack is now uniform llama.cpp; vLLM is removed from the architecture. *(Ruled out v16.)* | vLLM ships a verified fix for the FlashAttention V2 Ampere+CUDA-12.8 crash AND reproducible benchmarks demonstrate vLLM throughput materially exceeds llama.cpp on the same model at the same quant on the same hardware. Both conditions, not either. Until then, do not re-introduce vLLM. |
| **Picovoice Porcupine for new wake-word builds (May 2026)** | Picovoice Console signup (the only path to obtain an AccessKey for the free tier) requires a company email and offers no working personal-email fallback in the current UI. GitHub OAuth attempts returned "unable to sign in, go back to sign up." This is a hard barrier for a new account in this build window. Existing AccessKey holders are unaffected; this rules Porcupine out only as a *default recommendation for fresh installs* on this stack. OpenWakeWord (Apache-2.0, models trained via Outspoken at €1/model, no API key) is the lateral substitute and is in production as of Phase 17.5. *(Ruled out v18.)* | Picovoice Console signup accepts personal email or GitHub OAuth for new accounts on the Free Plan, verified end-to-end. Then re-evaluate whether Porcupine's commercial maturity is worth swapping back from OpenWakeWord. Even then, the swap is lateral, not an upgrade. |

