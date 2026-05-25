# Monarch Infrastructure Bible — v19

**Compiled:** 2026-05-21 (mid-session, pre-Decision-5 close)
**Updated:** 2026-05-22 — Decision 5 Items 1-5 banked; audit corrections A1/A2/A4/A8/A9/A11 resolved; §B additions B1/B2/B3/B4/B6/B11/B14 folded in
**Operator:** Trent (residence: Raleigh, NC — operator identity is separable from residence)
**Document role:** Comprehensive scoping reference. Single source of "what exists, what's decided, what's open, where to look." Sits above the per-subsystem doctrine docs without replacing them. Not authoritative on its own — points to canonical sources on monarch and at `github.com/trentbentt/jarvis`.

**Truth hierarchy for any factual question:**

> monarch files > git log on monarch > jarvis-q all > github.com web view > this bible > any chat history

When this document and disk disagree, disk wins. This bible is a snapshot; the system keeps moving.

---

## §0 — How to read this document

Twenty-five sections. The first eight are scope (what is this whole system, what does each piece do). Sections nine through fourteen are the in-flight work surfaces (decisions, doctrines, rebalances, topology changes). Fifteen through twenty are the design-only and deferred subsystems — what's planned but not built. The final five are the open queue, the small-mission backlog, the ruled-out list pointer, the honest gaps, and the recommended reading order for any new session or new contributor.

Headers are kept stable so this doc can be grep'd: every major section starts with `## §N`. Use that as your jump table. The numbered subsections inside use `### §N.M` for the same reason.

You don't need to read this top to bottom. You need to know it exists, know how to navigate it, and read the section that matches whatever you're about to touch.

---

## §1 — Operator + Mission Context

Trent is a solo operator running a personal infrastructure stack on dedicated hardware in Raleigh, North Carolina. The hardware (monarch) is 24/7 headless. Trent's posture toward this stack is operator + architect — not just user. The stack runs to support real workloads that pay or are intended to pay (consultancy, content, leads, financial trading) plus personal infrastructure (news synthesis, eventual second-brain).

Three concrete operating realities shape every design choice in v19:

**Three-account Claude parallelism.** Trent runs three Claude.ai accounts in parallel across different missions. Per v18 master summary, two are Pro subscriptions; the third account's tier is not specified in any source-of-truth doc (and bible v19 initial compile drifted into "three Pro" by inference). Documentation tends to be ahead of any single account's chat history. The truth hierarchy at the top of this document exists because of this — chat history is the least authoritative source, monarch disk is the most.

**Schedule transition in progress.** As of compile date, Trent has been working late-night / built-different hours during the stack buildout. A standard Monday-Friday 9-5 schedule starts in approximately one week from compile date. The 23:00-07:00 ET overnight workload window in AUTHORITY_SPEC is sized for the post-9-5 weekday baseline. Weekend variability is deferred until the post-transition weekend pattern stabilizes. This is recorded so that no future session re-litigates the window based on the current schedule and gets it wrong.

**Solo operator constraints.** Everything ships through one person. There is no team to review designs, no separate ops engineer, no QA. Doctrines like "every Tier 2/3 output passes the validation gate" and "every n8n execution scopes to a working directory" exist specifically because a solo operator cannot manually audit five concurrent agent pipelines. Discipline-by-construction is the only viable approach.

The mission, framed in one sentence: **build a stack where the operator delegates to subsystems instead of supervising them**, with Jarvis as the canonical operator entry point and every other subsystem (news, financial, Hermes, validation gate, LoRA dispatcher, Nexus, 2nd Brain) Jarvis-addressable rather than directly-addressed.

---

## §2 — Hardware Envelope

One physical machine (monarch). Specifications below are load-bearing for every doctrinal decision downstream — most prominently the 24 GB VRAM ceiling, which is the single hardest constraint in the system.

| Resource | Spec | Notes |
|---|---|---|
| GPU | RTX 3090, 24 GB VRAM, SM86 (Ampere) | Single GPU. v16 ruled out vLLM + FlashAttention V2 + CUDA 12.8 on Phi-4-mini — silent crash. Whole stack now llama.cpp. |
| CPU | Ryzen 9 9900X, 12C/24T | Hosts T3 and T5 with `CUDA_VISIBLE_DEVICES=` prefix to force CPU execution. T5 capped at `-t 4` to leave headroom. |
| RAM | 96 GB DDR5 | Steady-state usage ~41 GB across the five-tier stack plus Postgres, Docker, n8n, OS. ~55 GB free at idle. |
| Storage | 4 TB NVMe | HF cache at `~/.cache/huggingface/hub/` (~26 GB post-cleanup). No `~/models/` migration planned — `-hf` shortcut for all tier launches. |
| Network | Tailscale Funnel (webhook-only) | Funnel exposes `/webhook/` only per UFW rules; n8n UI and other surfaces remain behind Tailscale private. Headless box, accessed from MacBook via Tailscale. |
| OS | Ubuntu | CUDA 12.8 pinned. |
| Uptime model | 24/7 headless | Restart hygiene is an open small-mission item — baseline VRAM creeps ~130 MiB across multi-day uptime, suggesting a nightly restart play. |

There is also a secondary device: an M2 MacBook Pro, 8 GB unified RAM. It runs Phase 17.5 voice-to-text. It shares only the physical microphone with the future Phase 18 voice-to-voice. It is not part of the monarch substrate.

**The forcing function of v19.** Monarch idled at 94% VRAM in v18 with no active workloads (T1 + T2 + T4 + driver = 23.1 GB / 24 GB). v19 doctrine was driven directly by this number: every cardinal decision either explicitly addressed VRAM headroom or implicitly assumed the rebalance was happening. Post-Rebalance-Change-1, baseline is 66.0% (16.5 GB / 24 GB). This delta is the most consequential operational change in v19, and the rest of the doctrine collapses out of it.

---

## §3 — What Jarvis Is (Architectural Framing)

This section is the unifying frame for v19. Every other section in this bible is downstream of it. The subsystem-specific docs (DECISIONS, REBALANCE, AUTHORITY_SPEC, PHASE2_SPEC) describe the parts; this section describes the whole.

**Jarvis is not an observability daemon with notifications.** That was the v0.1 framing and it was too small. Jarvis is the central nervous system of the monarch stack — the operator's canonical entry point and the system's internal coordination layer.

### §3.1 Function taxonomy

**Backend roles (machine-facing):**

- **Substrate orchestrator** — dispatches workloads across four execution substrates: GPU (VRAM), RAM, CPU, and Cloud API. The four-substrate model is the v19 generalization of the prior GPU/CPU dichotomy.
- **Horizontal coordinator** — passes state and signals between agent workflows (news pipeline, financial pipeline, Hermes, LoRA dispatcher, validation gate). Each subsystem reports completion and anomalies to Jarvis rather than to the operator directly.
- **Knowledge bridge** — when Nexus (codebase index) and 2nd Brain (knowledge base) come online, Jarvis is the interface the operator and other systems use to query them.
- **Observability layer** — what was built in the May 18-19 sessions: schema, listeners, state.json, jarvis-q CLI. The substrate primitives feed everything else.
- **Event router** — receives completion / failure / anomaly signals from pipelines and decides where they need to go (event log, notification, automated remediation, operator surface).

**Frontend roles (operator-facing):**

- **Manager** — the operator delegates to Jarvis instead of addressing individual subsystems. Manager *first*, voice assistant a distant second. The operator does not inspect the validation gate; they ask Jarvis what happened. The operator does not watch the news pipeline log; they ask Jarvis what news ran this morning.
- **Personal assistant** — morning briefings, schedule awareness, proactive surfacing of what needs attention.
- **Voice interface** — Phase 18 voice-to-voice, distinct from Phase 17.5 voice-to-text.
- **Notification dispatcher** — voice / PWA push / ntfy.sh, with authority-tier-aware quieting (sleep window, severity ladder).
- **Documentation router** — operator asks "where's the doc for X" and Jarvis points to the right repo/file/section.

### §3.2 The architectural test

Any new subsystem proposed for v19 forward must answer four questions. If any of the four is *no*, the subsystem isn't done — it's a tool, not a Jarvis-addressable component.

1. **Can Jarvis observe it?** Is there a `state.json`-feedable signal that says "this thing is alive and doing X right now"?
2. **Can Jarvis dispatch to it?** Is there a programmatic interface to invoke its work — not just a CLI a human runs?
3. **Can Jarvis surface its events?** When this subsystem completes, fails, or anomalies, does it produce a signal Jarvis can route?
4. **Can Jarvis explain it?** When the operator asks "what is X doing right now," does Jarvis have enough to give an answer beyond "I don't know"?

The four-question test is the architectural commitment behind manager-first framing. It's also the gate for v20+ work — anything built without passing all four is technical debt by construction.

### §3.3 The non-negotiables (Hard Constraints)

Four hard rules around Jarvis itself, surfaced May 21-22 sessions and ratified into AUTHORITY_SPEC §"Hard Constraints" (commit 414d5b2). Lines that do not move under any combination of resource pressure, operator absence, or scheduling priority.

**Jarvis never shuts off.** Hard constraint. Jarvis is load-bearing for system boot and recovery — nothing else in the stack can bring tiers back if Jarvis dies. Killing Jarvis is structurally forbidden, not just discouraged. Maximum degradation is conditional self-offload to RAM/CPU per the Substrate Pressure Cascade (§10.4).

**Jarvis identity never routes to API.** The daemon, T1 reasoning brain, listeners, and state store stay monarch-local under all pressure conditions. Two reasons: (a) routing the coordination layer to cloud exposes the entire system's credentials, dispatch decisions, and telemetry to an external surface; (b) Jarvis is high-traffic by design and monthly prepaid budgets would drain in days at cloud rates. Workloads route to API per the Substrate Pressure Cascade — the coordinator does not.

**Pause is not in the toolkit.** Under VRAM, latency, or quota pressure, Jarvis re-routes work — never blocks it. The Substrate Pressure Cascade, latency-band routing cascade (Tier 2), and Quota Cascade Policy together cover the response surface without resorting to pause-the-workload.

**T1 restart is Tier 3, never silent.** T1 is the always-on reasoning brain Jarvis uses for its own dispatch decisions and operator-interaction work. T6 (when downloaded) is the on-demand burst coder. They are not interchangeable. The manager does not silently restart its own brain — operator confirmation gates any T1 restart action (T6 restarts are still autonomous Tier 2).

---

## §4 — Substrate Architecture (Path B Topology)

The substrate is the physical-and-virtual ground that everything else runs on. Two execution-level layers (control plane / dataplane) and four target substrates (GPU / RAM / CPU / Cloud API). Path B topology is the v19 commitment to making this distinction structural rather than maintenance-discipline.

### §4.1 Two-session tmux topology

The system now runs across two tmux sessions instead of one. The split mirrors the v19 control-plane / dataplane doctrine structurally.

| Session | Lifetime | Windows | Purpose |
|---|---|---|---|
| `control` | long-lived; survives `inference-down` | bootstrap, jarvis, validation-gate, lora-dispatcher, litellm, t1-interactive | T1 is the Jarvis reasoning brain per Decision 1. LiteLLM routes to cloud during dataplane burst-down. VG/LD/Jarvis are services, not tiers. |
| `inference` | dataplane; cycle-safe | bootstrap, t3-content, t4-phi4, t5-small (+ t2-pipeline when burst-up, future t6-coder when deployed) | `tmux kill-session -t inference` is semantically safe — only dataplane dies. |

`whisper` is a separate small session for the dictation system, unrelated to inference.

### §4.2 The four execution substrates

| Substrate | Used for | Throughput characteristic | Cost shape |
|---|---|---|---|
| GPU (VRAM) | Highest-throughput inference; primary path for T1 reasoning, T4 utility, T2 pipeline burst, T6 coder burst | Tokens/sec dominated by VRAM bandwidth + offload ratio | Fixed hardware cost; constrained to 24 GB ceiling |
| RAM | Mid-tier inference where GPU is unavailable or burst-allocated elsewhere; KV cache backing | Slower than VRAM, faster than disk swap | Effectively free up to 96 GB |
| CPU | T3 content (CPU-only via `CUDA_VISIBLE_DEVICES=`), T5 small (1.7B, persistent helper); fallback path for any tier when VRAM saturated | Order of magnitude slower than GPU for LLMs | Effectively free up to thermal limits |
| Cloud API | Synthesis (news Stage 4), building/design (Claude Pro), frontier reasoning, throughput-tier overflow | Latency floor higher than local; quality ceiling higher; bounded by quota/budget | Money on the line — surfaced via Tier 3 authority |

The four-substrate model is Jarvis's dispatch matrix. Every workload has a default substrate and a cascade order. Authority Spec gates the cloud step because that's where money enters.

### §4.3 What changed when Path B landed (2026-05-21 04:14-04:21 EDT)

The dual-session split was promoted live, not as a fresh start. The historical observation that drove it: pre-Path-B, `inference-down` ran `tmux kill-session -t inference` which took T1, LiteLLM, validation-gate, lora-dispatcher, and jarvis with it every time the dataplane needed to cycle. The teardown script then ran a straggler-kill prompt that offered to `sudo kill -9` the very services it had just destroyed. The defensive design was: an operator notices T1's PID in the list and declines. That depended on operator attention at the moment of cycle.

Path B removed the *need* for defense by removing the failure mode. Control-plane services live in a separate session whose lifetime is decoupled from the dataplane's. This is the canonical example of the **redesign-over-refine principle** committed to HANDOFF_v19.md.

Operator-side scripts changed (live runtime, not in repo):

- `~/bin/inference-up` — dual-session aware. Creates `control` session if missing (idempotent). Per-service `already_up` port-check guards skip launches for control-plane services already running. Smoke tests still run unconditionally. Zombie-check rewritten to filter control-session survivors via parent-walk PID→session resolution.
- `~/bin/inference-down` — kills only `inference` session. Surviving GPU processes are inspected and reported with tmux affiliation, not killed. No force-kill prompt under any flag.
- `~/bin/t2-up`, `~/bin/t2-down` — already used `TMUX_SESSION="inference"` as a variable; T2 is dataplane.

Repo file changed (commit `9858a6a`):

- `deploy.sh` — Jarvis daemon window now created in `${CONTROL_SESSION}` instead of `inference`.

Validation evidence captured at the time: `tmux move-window` is empirically safe for VRAM-resident llama-server processes (T1 kept its 12 GB allocation, kept serving on port 8080, passed a coherence test after the move). Jarvis daemon's writer thread retained its 10-second cadence across the session reassignment.

### §4.4 The redesign-over-refine principle

Captured in HANDOFF_v19.md (commit `38b6446`), anchored to the Path B example.

> When a Tier 3 (surface-and-ask) prompt fires repeatedly for the same underlying reason, the right move is sometimes architectural elimination, not tighter criteria. The `[y/N]` straggler prompt in pre-Path-B `inference-down` was the operator's last line of defense against a destructive default. Path B removed the *need* for defense by removing the failure mode. Future authority decisions should consider this option when a Tier 3 keeps recurring: redesign rather than refine.

This is the v19 design heuristic for every future subsystem. It is a stance, not a tier.

---

## §5 — Inference Stack (Tier-by-Tier)

Six tiers in the v19 design. Five live; one (T6) blocked on model download. All are llama.cpp post-v16 (vLLM ruled out for this hardware).

### §5.1 T1 — Jarvis Reasoning Brain (always-on)

- **Model:** Qwen3.6-27B
- **Port:** 8080
- **Session:** `control` (Path B)
- **Config:** `-ngl 40`, 24K ctx (post-Rebalance-Change-2), `-np 1`, q8_0 KV
- **VRAM:** ~11,842 MiB measured (was 11,984 at 36K ctx; ~500-800 MiB drop expected from ctx reduction, not yet measured under cold cycle)
- **Role:** Always-on reasoning brain for Jarvis. Handles operator-facing OpenCode sessions, Jarvis dispatch decisions, and any local reasoning that doesn't need T6's coding specialization.
- **Never shut off** per §3.3 non-negotiables. Self-offload to CPU/RAM is the max degradation allowed under VRAM pressure.

### §5.2 T2 — Pipeline Burst (burst-only)

- **Model:** Qwen3.6-27B (shares weights mmap with T1, T3)
- **Port:** 8083
- **Session:** `inference` (Path B)
- **Status:** `burst_only=True` in schema; idle-by-default
- **Bring-up:** `~/bin/t2-up` (idempotent, has /health wait + port conflict detection)
- **Bring-down:** `~/bin/t2-down` (graceful SIGTERM, SIGKILL fallback)
- **Config when active:** `-ngl 20`, 16K ctx (standard) or `-ngl 60`, 32K ctx (burst-mode)
- **VRAM when active:** ~6,832 MiB (standard) up to ~17 GB (burst-mode with T1 parked)
- **Role:** Pipeline-mode bounded synthesis. Pre-Decision-4 was always-on serving news Stage 2 synthesis. Post-Decision-4, news Stage 2 routes to DeepSeek V4 Flash via LiteLLM fallback chain; T2 is invoked only on explicit `t2-up` for one-off pipeline work.

### §5.3 T3 — Content/Batch CPU (always-on, zero VRAM)

- **Model:** Qwen3.6-27B (shares weights mmap with T1, T2)
- **Port:** 8084
- **Session:** `inference` (Path B)
- **Config:** `CUDA_VISIBLE_DEVICES=` prefix forces CPU execution; `-ngl 0`
- **VRAM:** 0 (CPU-only)
- **RAM:** ~4 GB working set
- **Role:** Slow-but-zero-VRAM-cost content generation, batch jobs, anything where latency doesn't matter. LoRA dispatcher target tier — content/leads/exploratory adapters all served here.

### §5.4 T4 — Utility Phi-4-mini (always-on)

- **Model:** Phi-4-mini Q4_K_M (Unsloth GGUF)
- **Port:** 8002
- **Session:** `inference` (Path B)
- **Config:** `-ngl 99`, 16K ctx, `-np 4`, q8_0 KV
- **VRAM:** ~4,179 MiB measured
- **Role:** Fast utility model. Validation gate grading calls (grounding + voice checks) hit T4 directly, not through LiteLLM, to avoid silent cloud fallback on grader work. Also used for classification, light extraction, and other small-prompt tasks.
- **Engine pivot history (v16):** Originally specced as vLLM. vLLM 0.20.1 silently crashes at FlashAttention V2 initialization on Phi-4-mini fp8 with Ampere SM86 + CUDA 12.8. Pivoted to llama.cpp during first bringup.

### §5.5 T5 — Small Helper CPU (always-on, zero VRAM)

- **Model:** Qwen3-1.7B
- **Port:** 8085
- **Session:** `inference` (Path B)
- **Config:** `CUDA_VISIBLE_DEVICES=` prefix; `-t 4` (4 CPU threads)
- **VRAM:** 0
- **Role:** Persistent helper for sub-second per-call work. The "seed" small model — additional small-model needs spawn `llama-cpp-python` inline within n8n executions rather than running new persistent tiers.

### §5.6 T6 — Coder Burst (planned, not yet downloaded)

**Two VRAM operating modes per v18 master summary §5.6:**

- **Pure VRAM (no expert offload):** ~21 GB, full MoE 3B active at ~80-100 tok/s with `--cache-type-k q8_0`. This is v18's documented "standard pattern" for T6 burst.
- **Partial expert offload (~25%):** ~17-19 GB, somewhat reduced throughput. The operational mode Decision 3 will pick if VRAM headroom matters more than peak throughput.

Both numbers are valid; bible v19 initial compile mixed them into a single "17-19 GB" target. Decision 3 (T6 defaults — BLOCKED on 21 GB model download + tooling) will pick the operational default. The Substrate Pressure Cascade (§10.4) eviction priorities apply to whichever mode is active.


- **Model:** Qwen3.6-35B-A3B UD-Q4_K_XL (Unsloth Dynamic 2.0 GGUF)
- **Port:** 8086 (planned)
- **Session:** `inference` (Path B, when deployed)
- **Status:** Model not yet downloaded (~21 GB pull pending). T6 spin-up tooling (`~/bin/t6-up`, `~/bin/t6-down`) not yet written.
- **Config target:** 25% expert offload, 64K context, three named modes (comfort / conservative / aggressive)
- **VRAM when active:** ~17-19 GB target
- **Role:** On-demand burst coder. Overflow valve for Claude Pro walls, NDA-tagged work, or quality-needed local coding. The "coder" of Decision 1 ("local does data plumbing + agentic glue + on-demand coder burst").
- **Decision 3 status:** OPEN. Defaults blocked on download + rebalance landing.

### §5.7 mmap weight sharing — the architectural reason five tiers fit

T1, T2, and T3 all load the same Qwen3.6-27B UD-Q4_K_XL GGUF. mmap shares the ~17 GB of weight pages across all three processes — they read from the same kernel page cache rather than each loading their own copy of the weights. **This is the single architectural reason five concurrent tiers fit on monarch's 24 GB VRAM ceiling.** Without mmap sharing, T1+T2+T3 alone would consume ~51 GB of weight loads.

This sharing is implicit in llama.cpp's default behavior and is not something the operator configures. It is documented here because it is load-bearing for the five-tier topology — if the inference stack ever moved off llama.cpp to a framework without page-cache sharing, the architecture would need to be redesigned, not just ported.

**Measured throughput (v18 baseline):**

| Tier | Standard config | Burst config |
|---|---|---|
| T2 | 5.4 tok/s generation | 22.9 tok/s generation |
| T4 (Phi-4-mini) | 206 tok/s generation | n/a — utility tier |

T1, T3, T5 throughput numbers not measured in v18; pending instrumentation.

### §5.8 Resource budget — five-tier combined footprint

Post-Rebalance-Change-1 (T2 burst-only), pre-Change-2 measurement landing:

| Component | VRAM | Notes |
|---|---|---|
| T1 (-ngl 40, 24K ctx, q8_0 KV, -np 1) | ~11,842 MiB (estimate, post-Change-2) | Was 11,984 at 36K ctx |
| T4 (-ngl 99, 16K ctx, -np 4, q8_0 KV) | ~4,179 MiB | Measured stable |
| Driver overhead | ~500 MiB | NVIDIA driver + buffers |
| **Standard baseline (T2 idle)** | **~16,521 MiB / 66.0%** | Reproducible across cold cycle |
| T2 burst (-ngl 20, 16K ctx) added | +6,832 MiB | Pipeline mode |
| T6 burst (planned, 25% offload) added | +17,000-19,000 MiB | Would require T2 + T4 down |

Headroom under standard baseline: ~8 GB available. Sufficient for T2 burst with T1 active; insufficient for T6 burst without parking T2 or T4. Three-mode VRAM doctrine (Standard / Burst / Soft) governs reallocation choices.

---

## §6 — Routing Layer (LiteLLM, Decision 4 Cascade)

**Jarvis-monitored health components (full list per `MONARCH_HEALTH_COMPONENTS` in schema.py lines 413-424):**

| Component | Port | Check | Purpose |
|---|---|---|---|
| validation-gate | 4100 | HTTP | Decision 4 Phi-4 validation |
| lora-dispatcher | 4200 | HTTP | LoRA hot-swap dispatch |
| n8n | 5678 | HTTP /healthz | Workflow orchestration |
| postgres | 5432 | TCP | News + telemetry + validation data backbone |

Bible v19 initial compile listed only 4100/4200; n8n and postgres are equally tracked.


LiteLLM is the router. It exposes a single OpenAI-compatible endpoint that pipelines and agent harnesses call; the routing logic decides which tier or cloud provider actually handles the request, including cascading fallbacks when a target is unavailable, walled, or rate-limited.

### §6.1 Cloud cascade (Decision 4, closed 2026-05-19; amended 2026-05-24)

**Amended 2026-05-24:** Decision 4 was restructured from a strict-priority chain into structural classes (full doctrine in DECISIONS_v19.md Decision 4 2026-05-24 Small Amendment). The class structure is canonical; the priority chain below is preserved as a tie-breaker when task class is genuinely ambiguous.

**Structural classes (operational cascade as of 2026-05-24):**

| Class | Providers | Role |
|---|---|---|
| Workflow-tier-zero | Claude Pro (×2) | Operator default for building/design; **not Jarvis-routed**, not in Quota Cascade Policy. |
| Peer rotation | DeepSeek V4 Flash, Kimi K2.6 | Active workhorse pair. Rotate by fullest-peer rule at 20% / 10% thresholds per AUTHORITY_SPEC §Quota Cascade Policy. |
| Emergency rung | Anthropic API direct | Tier 3 per-call invocation already. Vestigial — doctrine-forward, not yet wired. |

**Haiku 4.5 deprecated 2026-05-24.** Originally specced as the latency niche class. Pricing parity with DeepSeek V4 Flash at lower capability makes it redundant. Removed from the operational cascade. Re-open condition: a future provider with a genuinely-distinct latency profile re-justifies a latency niche class.

**Tie-breaker priority chain (when task class is ambiguous):** Claude Pro → DeepSeek V4 Flash → Kimi K2.6 → ~~Haiku 4.5~~ → Anthropic API direct.

Cowork is retired as a pipeline stage. The news pipeline Stage 4 migration from Cowork to DeepSeek V4 Flash predated Decision 4 and forced the cascade order — Decision 4 was largely a doc formalization of work already executed.

### §6.2 What's in api_keys.env

11 keys total, all `export`-prefixed (corrected during May 19 session — pre-fix, bare assignment caused silent env-not-inherited failure in subprocess children). Includes Anthropic, DeepSeek (rotated mid-session for security), Google, FRED, NewsAPI, Finnhub, AlphaVantage, OpenAI (deprecated, kept for legacy reference), HuggingFace.

**Missing:** Moonshot/Kimi key. Add or amend Decision 4. Small mission.

### §6.3 What LiteLLM routes

- `qwen3.6-pipeline` → T2 primary, DeepSeek V4 Flash fallback. **End-to-end tested 2026-05-19.** Fallback exercises when T2 is idle (the standard state post-Rebalance-Change-1). Used by news Stage 2.
- `qwen3.6-content`, `qwen3.6-design`, `qwen3.6-exploratory` → T3 with LoRA adapter swaps via dispatcher (lora-dispatcher service on port 4200). LoRAs not yet trained, dispatchers stub-only.
- `throughput-tier` → ambiguity surfaced May 19. Used in `~/projects/leads/.opencode/opencode.jsonc` and `~/projects/financial/.opencode/opencode.jsonc`. Decision 4 didn't explicitly close it. Small mission — possible Hermes/Decision-2-related work.
- `deepseek-v4-flash` → direct DeepSeek V4 Flash, used as fallback target and direct synthesis target.
- `phi4-mini` → T4 direct. Used by small-model code in opencode.jsonc files.

### §6.4 Validation Gate

FastAPI service on port 4100, in the `control` session.

**Three checks** per request:

1. **Schema** — length bounds, JSON shape (optional jsonschema), required-section heading checks, forbidden-phrase scan. ~1 ms.
2. **Grounding** — Phi-4-mini call. Returns fraction of OUTPUT entities supported by SOURCE. Pass ≥0.90, warn ≥0.75, fail below.
3. **Voice** — Phi-4-mini call. Scores OUTPUT against brand voice profile (`brand_voices/*.yaml`). Pass ≥0.70, warn ≥0.50, fail below.

**Verdicts:** pass → accept. warn → accept + surface. fail → `retry_cloud` (re-run via LiteLLM `deepseek-v4-flash`); second fail → `surface_for_review`.

**Critical design:** Validation gate calls Phi-4 directly, NOT via LiteLLM. If grader calls went through LiteLLM, fallback chains would silently redirect grader work to cloud when T4 is busy. Direct connection means grader work fails loudly when T4 is down — the correct behavior. Validation should not silently fall back to cloud.

**Telemetry:** Every `/validate` call writes one row to `validation_telemetry` (Postgres). Joinable on `workflow_id` with `lora_swap_telemetry`.

**Telemetry tables (v18 discipline layer):** `validation_telemetry` (written by validation gate) and `lora_swap_telemetry` (written by LoRA dispatcher) both back the same Postgres instance and are joinable on `workflow_id`. This joinability is the discipline-layer feature that enables drift detection across the validation + LoRA-swap surface — neither table alone is sufficient. Bible v19 initial compile noted only validation_telemetry.

### §6.5 LoRA Dispatcher

FastAPI service on port 4200, in the `control` session.

**Pattern:** Workflow-scoped adapter swap on T3. Each n8n execution declares one `workflow_id`; all dispatches in that execution use the same `required_adapter`. Dispatcher swaps the LoRA on T3 maybe 2-3 times per day in steady state — n8n workflows batch by adapter when planning work.

**Pattern not adopted:** vLLM's punica-style per-request multi-adapter pattern is not available on llama.cpp. For solo-operator session patterns, session-swap is functionally equivalent — you don't have three OpenCode sessions running in parallel needing three different adapters in the same instant.

**Current state:** All five planned LoRAs (content, leads, exploratory, consultancy, design) have data sources and rubrics specified in master_summary_v18 §Phase 9. **Zero are trained.** Under Decision 1 reframe (local = data plumbing + agentic glue + coder burst, NOT synthesis/building), the three high-stakes LoRAs (consultancy, design, exploratory-coding) are likely deferred indefinitely. The content and leads LoRAs remain possible but not in the v19 active queue.

---

## §7 — News Pipeline

Phases 1-5 wired and running. Cron-scheduled, runs daily.

### §7.1 Architecture (post-v18 pivot)

Five stages, sequenced:

1. **Stage 1: Ingestion** (cron every 30 min, `*/30 * * * * news-ingest`). Universal fetch_worker.py against 42 active sources. 9 sectors. Writes to Postgres `news_unified` table. ~2,362+ articles accumulated.
2. **Stage 2: Sector synthesis** (cron `15 5 * * * news-synth`). `synthesis_export.py` calls LiteLLM `qwen3.6-pipeline` → T2 (when active) or DeepSeek V4 Flash (when T2 idle, the standard state). 9 sectors processed sequentially, ~315-346s wall time. Output → Postgres `daily_stream_outputs`.
3. **Stage 3: Drive sync** (cron `30 5 * * * news-sync`). rclone push of pending outputs to Google Drive.
4. **Stage 4: Compilation** (cron `0 6 * * * news-compile`). Stream A + Stream B compilation. **Originally Cowork; migrated to DeepSeek V4 Flash via LiteLLM, May 19.**
5. **Stage 5: Brief pickup + ntfy** (interim until Jarvis Phase 18). Final brief surfaced to operator.

### §7.2 What's in Postgres for news

- `news_sources` — 48 sources across 9 sectors (seeded, some now degraded).
- `news_unified` — article storage. Deduplicated by URL. 2,362+ rows.
- `daily_stream_outputs` — per-sector synthesis output.
- `news_pipeline_runs` — execution log.
- `cross_sector_signals` — Stream B compilation surface for cross-sector causal pairs.

### §7.3 Known degradation (May 20-21)

Observed: 4 of 9 sectors producing 90-200 character stub outputs with effectively zero word count. Pipeline correctly flagged this as `PROPORTIONALITY VIOLATIONS: §5(3) 4 DEGRADED/BLIND sector(s) at stub-level output — synthesis effectively skipped, not a quiet day` and stamped the brief as degraded (`contract_violation=True`).

Two distinct root causes:

1. **Source degradation** — 4 sectors show `state=DEGRADED` with named missing sources (fmp_market_news, deepseek_news, moonshot_kimi_news, bankless_rss, propublica_congress, more in digital_assets). Articles aren't reaching synthesis because upstream RSS/APIs return empty or 429-rate-limited.
2. **Stub outputs in OK-status sectors** — ai_tech, quant, geopolitics, market_movers show `state=OK` but output is still 90 chars / 0 words. Either a prompt issue, model issue, or synthesis-logic issue, separable from the source degradation problem.

**Status:** Tracked as Tier-D/E small mission "news pipeline output quality investigation." A separate Claude account is handling this. Not in scope for the doctrine/topology work.

### §7.4 News pipeline integration points (future)

Three integrations specced in master_summary_v18:

- **Integration 1: stack_signals table** — Stream A AI signals → infrastructure decision feed. Planned.
- **Integration 2: macro_signals table** — Stream B compilations → financial pipeline regime input. Planned, gates on financial pipeline phase-level design.
- **Integration 3: news_trade_signals table** — Stream B causal pairs → financial pipeline data source. Planned, gates on Integrations 1+2.

All three are deferred until financial pipeline strategy questions are answered (§9).

### §7.5 News pipeline as reference pattern

For any future morning-batch pipeline (financial pre-market, intelligence digest, etc.) the news pipeline shape is the validated template:

```
Cron-scheduled ingestion → bounded local-or-cloud synthesis →
sync → compilation → operator surface → optional sub-table writes
```

What's important: this is the *only* validated pipeline shape in the stack. Any new pipeline using this shape can move fast; any new pipeline diverging from it needs its own design pass.

---

## §8 — Financial Pipeline (Open Strategy Questions)

This section is short on architecture and long on questions, deliberately. Financial pipeline cannot be designed until the strategy is decided. Anything else is premature commitment.

### §8.1 What exists today

- `~/projects/financial/` — directory exists with `.opencode/opencode.jsonc` (model: `litellm/throughput-tier`, which is the small mission flagged in §6.3).
- `~/financial-cowork/` — deprecated per master_summary_v18.
- Existing data integrations: FRED key active and pulling 7 macro series. SEC EDGAR, Finnhub, AlphaVantage credentials live (FMP free tier disabled).
- Existing intent: paper-trading harness → backtesting → live with small size → eventual auto-trade. Bayesian/Monte Carlo analysis. Regime detection. Baseball analytics (MiroFish prediction market simulation) is a parallel personal project.

### §8.2 The twelve gating strategy questions

Surfaced 2026-05-21. None answered yet. The pipeline shape depends on the answers — different combinations produce radically different architectures.

**Strategy layer:**

1. **Time horizon** — day-trading, swing (days-weeks), position (weeks-months), long-term hold, or mix? Biggest single fork. Day-trading needs sub-second to minute-scale signal infrastructure; position trades on daily bars and overnight synthesis.
2. **Asset class** — equities only? Options? Futures? Crypto? Each has different data, brokers, regulatory surface, risk profile.
3. **Discretionary vs systematic** — pipeline generates signals you decide on, or trades it executes? Discretionary = slower/richer; systematic = execution latency and uptime become load-bearing.
4. **Number of concurrent strategies** — one thesis at a time, or portfolio of uncorrelated strategies? Multiplies data and risk-management complexity.

**Data layer:**

5. **Live charts vs end-of-day data** — EOD is cheap, batch-able, fits news pipeline shape exactly. Live charts means streaming infrastructure, websockets, different stack.
6. **Data sources** — free (yfinance, IEX free tier, FRED)? Paid (Polygon, Alpaca, IBKR, Bloomberg)? Dictates pull frequency.
7. **Macro vs micro signals** — macro releases (CPI, FOMC, jobs reports — scheduled), company-specific (earnings, M&A, insider — different schedules), or pure technicals (continuous)?

**Risk layer:**

8. **Position sizing rule** — fixed dollar, fixed percent, Kelly, volatility-targeted? Drives every-trade math.
9. **Max drawdown tolerance** — number that kills the strategy and operator goes back to W-2 income. Bounds everything else.
10. **Backtest before live** — paper-trading first, walk-forward testing, or straight to live with small size? Honest backtesting infrastructure is real work — look-ahead bias is everywhere.

**Capital layer:**

11. **Account size** — determines tradeable instruments (PDT rule under $25K for equities; options minimums; futures margin).
12. **Tax structure** — personal taxable, IRA, LLC? Affects strategy choice because short-term gains are taxed at ordinary rates.

### §8.3 Recommended next move

Per §3 architectural test: the financial pipeline is not yet Jarvis-addressable because there's nothing operational to observe. Building infrastructure before strategy is the trap.

**Proposal in flight:** Stand up `FINANCIAL_STRATEGY_v19.md` as a working doc (thinking doc, not decision doc) at `~/projects/jarvis/` or `~/projects/financial/`. Answer questions 1-5 first across however many sessions it takes. No pipeline code until those five have defended answers. The news pipeline shape stays available as a reference pattern when the work begins.

**Hard constraint either way:** the news pipeline 05:15 cron is the forcing function for the burst window. Any morning-batch financial work must schedule around news, not collide.

### §8.4 The Phase A / B / C intraday cycle (specced in v18, not implemented)

If/when financial moves to discretionary intraday work, master_summary_v18 specced a three-phase shape worth preserving as reference:

- **Phase A — Pre-market strategy formation** (~09:00). Full-database context. Qwen3.6-35B-A3B at max context reads overnight news_signals, regime classification, historical performance, FRED snapshot, sector moves. Output: one `daily_strategy` record before market open.
- **Phase B — Intraday execution support** (market open → close). Narrow ingestion: single stock price feed, 1-minute candles. Small/fast model. Tasks: compare current price to strategy parameters. <500ms per cycle. Output: execution signal (hold/scale/exit) to Postgres.
- **Phase C — End-of-day re-evaluation** (~16:30). Full synthesis tier. Score the strategy's accuracy, identify what worked, update success-rate metrics, flag regime drift. Over time the `daily_strategy_result` table becomes the primary training signal.

This is preserved as design memory, not as decided architecture. Validity depends on §8.2 strategy answers.

---

## §9 — The Six Cardinal Decisions

The cardinals are the architectural commitments that v19 turns on. Three closed, two in flight, one blocked.

### §9.1 Decision 1 — Architectural reframe (CLOSED 2026-05-19)

**Statement.** Local does data plumbing + agentic glue + on-demand coder burst. Cloud carries synthesis + building/design + frontier reasoning.

**Forcing function.** 94% VRAM baseline. There is no headroom for the alternative. Confirming this collapsed approximately 10 other open decisions (closed Path 1/2/3, retired three high-stakes LoRAs, retired Cowork as a synthesis stage, confirmed Decision 4 cascade).

**Implications still propagating:**

- T1 is the Jarvis reasoning brain, not the OpenCode harness host (per v19 framing).
- T2 is burst-only, not always-on (per Rebalance Change 1).
- The three high-stakes LoRAs (consultancy, design, exploratory-coding) are likely deferred indefinitely.
- Synthesis defaults to cloud — news Stage 2 routes through DeepSeek V4 Flash by default with T2 burst available on operator-triggered exception.

### §9.2 Decision 2 — Hermes adoption shape (OPEN)

**What's pending.** Pattern B parallel to n8n, Curator scoped narrowly or disabled, memory writes disabled, routed via DeepSeek V4 Flash initially.

**What's missing.** The v18-era Hermes brainstorm documents haven't been pasted into a fresh chat. Decision 2 cannot be closed cold without them — risk of confident speculation overriding actual prior thinking.

**Why it matters.** If Phase 2 Jarvis listeners are going to coexist with Hermes agents, the boundary between "Jarvis observes" and "Hermes acts" matters. Hermes is the v18 candidate for agent automation; if adopted, it parallels n8n on workflow execution but exposes a different agent surface (memory + Curator). Pattern B is the "run it alongside n8n, don't migrate" choice. Curator-narrow is the "don't let it talk to the rest of memory" choice. Both are doctrinal stances.

**Next action.** Surface the v18 Hermes brainstorm docs (likely in master_summary_v17 or v18 — Trent has them somewhere) and walk Decision 2 in a dedicated session.

### §9.3 Decision 3 — T6 operational defaults (BLOCKED)

**Statement (proposed, not closed).** Qwen3.6-35B-A3B UD-Q4_K_XL, 25% expert offload, 64K context, three named modes (comfort / conservative / aggressive).

**Blocked on:**

1. Model not downloaded. ~21 GB pull required.
2. Spin-up tooling not written. `~/bin/t6-up` and `~/bin/t6-down` don't exist yet.
3. Rebalance Change 2 measurement not landed. Need to confirm post-Change-2 baseline is comfortable enough to absorb T6 burst (~17-19 GB) under one of the three modes.

**Comfort mode** would park T1 and run T6 burst-up under tight VRAM constraints. **Conservative mode** would require T2 + T4 down. **Aggressive mode** would push expert offload higher with quality tradeoffs. Mode selection is one of the open Decision 3 axes.

### §9.4 Decision 4 — Cloud routing chain (CLOSED 2026-05-19; amended 2026-05-24)

**Statement (original 2026-05-19).** Per §6.1 priority chain. Cowork retired.

**Amendment v1 (2026-05-24) — Structural class reframe.** The cascade is not a strict hierarchy. Three structural classes: workflow-tier-zero (Pro, operator-driven; not Jarvis-routed) / peer rotation (DeepSeek V4 Flash ↔ Kimi K2.6, fullest-peer rotation per AUTHORITY_SPEC §Quota Cascade Policy) / emergency rung (Anthropic API direct, Tier 3 per-call). Full doctrine in DECISIONS_v19.md.

**Amendment v2 (2026-05-24) — Haiku 4.5 deprecated.** Originally specced as a latency niche class. Pricing parity with DeepSeek V4 Flash at lower capability makes it redundant. Removed from cascade. Re-open condition: a future provider with a genuinely-distinct latency profile re-justifies a latency niche class.

**Status:** Closed 2026-05-19 with original priority chain; reframed 2026-05-24 into class structure. Original priority chain preserved as tie-breaker when task class is ambiguous.

**Open small missions related to Decision 4:**

- Throughput-tier model ambiguity (§6.3) — used in leads and financial opencode.jsonc but not explicitly placed in cascade.
- No Moonshot/Kimi key — peer-rotation rung is half-wired until key acquired.

### §9.5 Decision 5 — Jarvis authority model (CLOSED 2026-05-24)

**Status.** AUTHORITY_SPEC_v19.md drafted 2026-05-19 (commit `8b59cce`). Operator confirmation walkthrough ran 2026-05-21 through 2026-05-24. **All eight items + Quota Cascade Policy ratified.**

Commits closing Items 1-5:

- `50692bd` (2026-05-22) — Items 1-3 banked: Tier 1 ratified; Tier 2 restructured (per-tier-class restart split, T1→Tier 3 escalation, latency-band routing cascade); Tier 3 extended (T1 restart, latency cascade failed); Quota Cascade Policy added with prepaid framing.
- `414d5b2` (2026-05-22) — Item 4 banked: Hard Constraints section added; "Sleep Window Rules" removed and replaced with Overnight Workload Window + Substrate Pressure Cascade; schema field rename (`sleeping_window_*` → `overnight_window_*`; defaults 22:30→23:00, 06:00→07:00).
- `f0675da` (2026-05-22) — Item 5 banked + Item 4 cascade reframe: bypass severity ladder ratified (GPU thermal as-is, Security as-is per multi-IP/VPN usage, Spend burst as-is, OOM scoped to RAM, VRAM cascade exhaustion added, Power deferred); Substrate Pressure Cascade reframed from sequential layers to continuous intensity band 2.5 GB → 500 MiB free VRAM (stateless response, three response kinds blend, checkpoint switchover for API routing).

**The three-tier model (now ratified through Tier 3):**

- **Tier 1 — autonomous-immediate.** Jarvis acts without surfacing. Reversible, routine, no money, no user-visible blocking change. Examples: rotating logs, compacting state.json snapshots, clearing tmpfs, reconnecting flapping Tailscale, restarting the writer thread defensively.
- **Tier 2 — autonomous-with-log.** Jarvis acts and writes an event entry the operator can audit via `jarvis-q events`. Reversible or low-cost-to-reverse. Examples: restarting a crashed dataplane tier (T3/T4/T5 via `tmux kill-window + inference-up`) or a crashed burst tier (T2/T6 via burst scripts); T1 escalates to Tier 3, never silent restart. Routing decisions when LiteLLM tier-1 walled. `cron.py` scheduling git gc.
- **Tier 3 — surface-and-ask.** Jarvis notifies and waits for explicit confirmation. Costs money, burns significant VRAM, affects user-visible workflow, never run autonomously before, NDA-tagged context. Examples: spinning up T6, T1 restart, latency cascade failed, retiring model from local storage, any action in overnight window not meeting bypass. **Two flavors:** blocking (default-stay, need approval) and non-blocking (default-proceed with 120s veto window — canonical example is the conditional self-offload in the Substrate Pressure Cascade).

**Overnight Workload Window (replaces the prior "Sleep Window Rules" section in AUTHORITY_SPEC):** Weekday baseline 23:00-07:00 ET. Controls three things — (1) pipeline scheduling preference (news at 05:15/05:30/06:00, financial Phase A pre-market when wired); (2) Substrate Pressure Cascade's self-offload availability (only within window); (3) voice/push notification quieting (visual still hits `jarvis-q events`). Bypass severity ladder (now "Notification Interrupt Conditions") fires regardless of window state. Weekend variability deferred. Outside window — including weekday 9-5 working hours when operator is away — notifications fire normally (operator needs trade-completed, workflow-failure signals when not at keyboard).

**Cold-start rule (ratified 2026-05-24).** All new actions begin in Tier 3. **No override at introduction** — strict cold-start. Promotion to Tier 2 happens after N=12 consecutive successful surfaces without operator correction; Tier 2 → Tier 1 also at N=12. Total cold-start to silent operation: minimum 24 operator-acknowledged successful runs. **Material behavior change to an existing action re-enters at Tier 3** — a changed action is treated as new for cold-start purposes.

**Substrate Pressure Cascade (now in AUTHORITY_SPEC, see §10.4 below for full doctrine):** Continuous intensity band over 2.5 GB → 500 MiB free VRAM. Three response kinds — eviction, self-offload, API routing — blend with scaling intensity. Stateless: response is a function of current pressure, not past escalation. The prior "two-band 1500/500 threshold" framing from initial bible compile is **superseded**; the audit's catch that vram.py uses 2000/500 in code (not 1500/500) is moot under the continuous-intensity-band framing — those values were proposed for a discrete-trigger design that no longer exists.

**Items 6-8 + Quota Cascade Policy closure (2026-05-24):**

- **Item 6 — Pro tier estimation: DESCOPED.** Pro is workflow-tier-zero (operator-driven, not Jarvis-routed); not in the Quota Cascade Policy. Pro auth flows through Claude Code's built-in subscription path, not LiteLLM, so Pro requests are opaque to `spend_logs` regardless. Re-open condition: an automated Pro-1 → Pro-2 → T6 failover mechanism is built that dispatches interactive workloads across Pro accounts without operator-in-loop.
- **Item 7 — Promotion threshold: N=12, uniform across both rungs.** Tier 3 → Tier 2 → Tier 1 each requires 12 operator-acknowledged successful runs without correction; total cold-start to silent operation is minimum 24 runs. Changed from N=10 (which had been written into the draft spec) to N=12 during the walkthrough ratification.
- **Item 8 — Cold-start rule: strict.** All new actions begin at Tier 3, no override at introduction. Material behavior change to an existing action re-enters at Tier 3 (changed actions are treated as new for cold-start purposes). The cold-start rule is the data-collection mechanism for the promotion threshold — without it, the threshold has no baseline.
- **Quota Cascade Policy thresholds: 20% / 10% with fullest-peer rotation, plus drain phase.** Peer rotation between DeepSeek V4 Flash ↔ Kimi K2.6: at every threshold cross on the active peer, Jarvis rotates to whichever peer has more remaining balance (Tier 2 action, logged event, no surface). When both peers are below 10%, drain phase engages — Jarvis drains each peer to zero with a per-percent notification overlay driving reload urgency (Tier 2 routing + operator-facing notification, not Tier 3). Goal: maximize prepaid value rather than strand budget.

### §9.6 Decision 6 — v19 scope (CLOSED 2026-05-19)

**Statement.** Jarvis + Financial pipeline get phase-level treatment in v19. Nexus 17.1 is design-only (no implementation). 2nd Brain 17.2 is deferred (no design conversation yet).

**Implication.** The v19 master summary write does not need to wait for Nexus or 2nd Brain content. It needs Decisions 2, 3, 5 closed and Rebalance Changes 2-3 landed, then it can ship.

---

## §10 — VRAM Doctrine (Three-Mode + Pressure Cascade)

The v16 doctrine, carried forward to v19 with modifications.

### §10.1 Three-mode allocation framework

| Mode | When | Allocation shape |
|---|---|---|
| **Standard / Interactive** | Default. Operator at keyboard, OpenCode possibly active, no scheduled pipeline. | All five tiers within VRAM ceiling at modest configs. Pre-Rebalance: 22.9 GB / 95.6%. Post-Change-1: 16.5 GB / 66%. |
| **Burst** | Pipeline workload (news, future financial) running. Time-windowed. Sequential not concurrent. | T1 parked, T2 -ngl 60 / 32K ctx, T4 unchanged, T3/T5 CPU-only. Measured ~21.5 GB / 87% in v18. With Path B, T1 stays up — burst is now additive on top of standard. |
| **Soft** | Specced in v16 but not currently used. T2 standard, T4 reduced. Reserved for special cases. | Not load-bearing. |

### §10.2 Core principle

**Quality of output is non-negotiable. Allocation is negotiable.**

The methodology is **offload-then-hotswap**: temporarily reallocate VRAM to run at peak efficiency, complete the work, reallocate back. The swap cost is 30 seconds to 3 minutes. The alternative — permanently shrinking allocations so all tiers coexist at reduced capacity — pays a GIGO tax continuously: small context windows, poor latency, underweight inference that produces results that take hours longer and are lower quality. The math never favors the permanent shrink.

### §10.3 Sequential not concurrent

Running the news pipeline and then the financial pipeline sequentially in burst mode is faster in aggregate than running both concurrently with T1 up in standard mode. This is the designed pattern. Do not attempt to run multiple pipelines concurrently to "save time" — the degraded allocation cancels any parallelism gain.

### §10.4 Substrate Pressure Cascade (ratified into AUTHORITY_SPEC, commit f0675da)

Ratified at AUTHORITY_SPEC §"Substrate Pressure Cascade" 2026-05-22. The initial bible compile described this as a three-layer sequential cascade; Item 5 walkthrough reframed it as a continuous intensity band. This subsection summarizes; AUTHORITY_SPEC is canonical.

**Framing.** Jarvis's response to observed VRAM pressure is a continuous intensity band, not a sequential layer ladder. Three response kinds — eviction, self-offload, API routing — blend with scaling intensity as pressure rises. Intensity recalibrates automatically as pressure eases. **Stateless response:** response is a function of *current* observed VRAM free, not a function of past escalation state. No "exit cascade" logic needed — as VRAM rises (workloads moved, tiers freed, bursts finished), intensity drops to match.

**Intensity band.**

| Free VRAM | Cascade state |
|---|---|
| > 2.5 GB | Normal operation — no cascade activity |
| 2.5 GB → 500 MiB | Active band; offload intensity scales with pressure |
| < 500 MiB | API routing engaged |

The 2.5 / 1.5 / 0.75 / 0.5 GB markers are intensity guideposts (how the cascade should feel across the band), not discrete `if VRAM < N` triggers. Percent-of-intensity assignment per response kind is Scope B framework, deferred to stress-testing data.

**Three response kinds (blend across band):**

- **Evict burst and utility tiers** (standard Tier 2 actions). Priority: T2 burst (~6.8 GB, `t2-down`) → T6 burst (~17-19 GB or ~21 GB depending on mode per §5.6, `t6-down`) → T4 reductions within tier operational range. T3 and T5 are CPU-only and contribute zero VRAM — not eviction targets.
- **Conditional self-offload (Tier 3 non-blocking).** Jarvis offloads reasoning capacity VRAM→RAM/CPU. Gated by (a) inside Overnight Workload Window, (b) operator doesn't veto within 120s. Floor is Scope B framework — T1 retains operator-interactive capacity.
- **Route workloads to API** (engages at < 500 MiB free). Workloads route per Decision 4 cascade, bounded by Quota Cascade Policy.

**API switchover mechanism.** Switch at next natural workload checkpoint (token-stream end, batch-item boundary, message-turn end). In-flight GPU work runs to its checkpoint, then *next* unit routes to API. Avoids re-issue/dedup. Under imminent-crash pressure (approaching 500 MiB with no successful switchover yet), checkpoint granularity may shorten or be bypassed — exact escalation deferred to implementation against measured failure modes (Scope B).

**Routing constraints:**

- **Workloads route, the coordinator does not.** Per Hard Constraints (§3.3), Jarvis identity (daemon, T1, listeners, state) never routes to API. Only workloads — news synthesis, financial analysis, coding bursts — are eligible.
- **Quota Cascade Policy gates routing depth.** Tier 3 escalation mid-cascade → surface and stop.
- **All routes exhausted → notification interrupt.** Bypass severity ladder "VRAM cascade exhausted" entry fires when API routing is quota-capped AND self-offload unavailable AND evictions exhausted.

Pause is not a step. Jarvis re-routes.

---

## §11 — Standard Mode Rebalance (Changes 1-3)

REBALANCE_v19.md is canonical. Summary state below.

### §11.1 Change 1 — T2 to burst-only (EXECUTED 2026-05-19/20)

- Schema: `TierConfig.burst_only: bool = False`, T2 marked True.
- Script: `~/bin/inference-up` patched with `SKIP_BURST_ONLY_TIERS="t2"` constant. T2 skipped during standard bringup.
- Operator tooling: `~/bin/t2-up` and `~/bin/t2-down` written, idempotent, dry-run verified.
- LiteLLM: `qwen3.6-pipeline` → `deepseek-v4-flash` fallback wired and tested end-to-end.
- **Measured baseline post-Change-1: 66.0% / 16.5 GB.** Validated 2026-05-20 across cold-cycle teardown and rebuild. Reproducible.
- Saved vs 94% baseline: ~6,832 MiB. Larger than the deficit (3,442 MiB). Even without further changes, baseline is comfortably under 80% target.

### §11.2 Change 2 — T1 ctx 36K → 24K (PATCHED 2026-05-21, measurement deferred)

- Schema: `~/projects/jarvis/jarvis/schema.py` MONARCH_TIERS T1 `context_size` from 36864 to 24576.
- Script: `~/bin/inference-up` T1 launch line `--ctx-size` 36864 → 24576.
- Both files patched and committed (commit `c0f7ea7`).
- Measurement deferred to next natural T1 restart. T1 is in the `control` session and survived the Path B cold cycle by design — the schema-level patch will land on next reboot or explicit control kill.
- **Expected effect:** ~500-800 MiB drop in T1 VRAM (KV cache scales with ctx size). Baseline estimate ~63-64% / 15.5-16.0 GB.

### §11.3 Change 3 — T4 -np 4 → -np 2 (PROPOSED, NOT EXECUTED)

- Status: drafted, pending Change-2 measurement.
- Rationale: T4 with -np 4 supports four concurrent slots; -np 2 supports two. Validation gate grader calls are sequential per request — concurrency 4 is over-provisioned for current load.
- Estimated savings: ~1 GB.
- **My honest call:** likely unnecessary. Post-Change-1 + Change-2, baseline is ~63%. T6 burst at ~17-19 GB would put total at ~32-34 GB if T6 stacks on full baseline — which it doesn't, because T6 burst requires T2 already down and may require T1 parked depending on mode. The slack isn't load-bearing. Change 3 is optional.

### §11.4 What Rebalance unlocks

The rebalance closes the loop on Decision 1. Without it, Decision 1 is doctrine without a way to act on it. With it:

- 8 GB of free VRAM at idle for burst windows.
- T6 burst becomes physically possible (vs. "would OOM under standard mode" in v18).
- Phase 2 listeners measure against a stable baseline, not against a shifting one.
- "Comfort / conservative / aggressive" modes from Decision 3 become real choices instead of "T6 cannot run."

---

## §12 — Authority Model (Decision 5 In Progress)

Covered structurally in §9.5. This section is the detailed state of the in-flight walkthrough.

### §12.1 Walkthrough state (CLOSED 2026-05-24)

| Item | Status | Commit | Banked |
|---|---|---|---|
| 1 — Tier 1 autonomous-immediate list | ✅ ratified | 50692bd | Entry 5 (writer-thread deadlock restart) gets revisit note on daemon-version bump |
| 2 — Tier 2 autonomous-with-log list | ✅ revised | 50692bd | Entry 1 split by tier class (dataplane via kill-window+up; burst via t2-up/t6-up; T1 escalates to Tier 3, never silent restart). Entry 3 reframed as "active burst tier idle > N min" with N=30 default. Entry 6 replaced with latency-band routing cascade. Pause-workload framing dropped. |
| 3 — Tier 3 surface-and-ask list | ✅ ratified+extended | 50692bd | Added: T1 restart → Tier 3. Latency cascade failed → Tier 3. Unified Quota Cascade Policy with prepaid framing (20%/10% thresholds — explicit numeric ratification still pending). |
| 4 — Overnight Workload Window | ✅ reshaped | 414d5b2 | Weekday baseline 23:00-07:00 ET; weekend deferred. Hard Constraints section added (4 rules). "Sleep Window Rules" removed; replaced with Overnight Workload Window (scheduling + notification policy) + Substrate Pressure Cascade. Schema field renames (`sleeping_window_*` → `overnight_window_*`; defaults 22:30→23:00, 06:00→07:00). |
| 5 — Bypass severity ladder + cascade reframe | ✅ ratified | f0675da | GPU thermal as-is (85°C/60s). Security as-is (operator multi-IP/VPN usage). Spend burst as-is ($5/5min). OOM narrowed to RAM only. New entry: "VRAM cascade exhausted" (VRAM<500MiB AND Quota Cascade in Tier 3). Power kept but marked deferred-pending-listener. Substrate Pressure Cascade reframed sequential→continuous intensity band 2.5 GB → 500 MiB free VRAM; three response kinds blend; stateless recalibration; checkpoint switchover. |
| 6 — Pro tier estimation | ✅ descoped | 2026-05-24 | Pro is workflow-tier-zero (operator-driven, not Jarvis-routed); not in Quota Cascade Policy. Pro auth via Claude Code subscription path, not LiteLLM. Re-open condition: automated Pro-1 → Pro-2 → T6 failover built. |
| 7 — Promotion threshold N | ✅ ratified | 2026-05-24 | **N=12**, uniform across both rungs (Tier 3 → Tier 2 → Tier 1). Total cold-start to silent operation: minimum 24 operator-acknowledged successful runs. Changed from N=10 draft value during ratification. |
| 8 — Cold-start rule | ✅ ratified | 2026-05-24 | Strict — all new actions begin Tier 3, **no override at introduction**. Material behavior change to existing action re-enters at Tier 3. |
| Quota Cascade thresholds | ✅ ratified | 2026-05-24 | **20% / 10% with fullest-peer rotation** between DeepSeek V4 Flash ↔ Kimi K2.6; drain phase with per-percent notification overlay when both peers < 10%. New authority primitive introduced: Tier 2 routing + operator-facing notification (scoped to Quota Cascade Policy, not promoted to general AUTHORITY_SPEC primitive). |

### §12.2 New authority primitive: Tier 3 split

Tier 3 has two flavors after the Item 4 walkthrough:

- **Blocking Tier 3** — surface, wait, never proceed without explicit approval. Example: tier flapping (3 restart attempts in 24h) → pause cron.
- **Non-blocking Tier 3** — surface with timer, default-proceed unless operator vetoes. Canonical example: Jarvis self-offload to CPU/RAM under VRAM pressure (120s veto window).

This distinction goes into AUTHORITY_SPEC's revise patch (not yet committed). The implementation distinction matters for vram.py listener — same listener fires, different action shape.

### §12.3 Open architectural questions

1. **Workload-priority schema** — required for fine-grained "evict lower-priority residents" decisions. Doesn't exist yet. Phase 2 listener territory.
2. **Latency band framework** — *banked into AUTHORITY_SPEC Tier 2 section as "Latency-band routing cascade" (commit 50692bd).* Workload classes have peak (ideal) and minimum (degradation floor) latency markers. Cascade behavior: in-band → no action; approaching min → consider substrate alternatives; below min → escalate per Decision 4 (substrate first, API second); 2× past min → Tier 3 surface. Numeric values per workload class deferred to measurement (Scope B). The initial bible compile described this as "deferred to PHASE2_SPEC" — actually banked in v19 AUTHORITY_SPEC.
3. **Substrate Pressure Cascade per-response-kind intensity calibration** — *intensity guideposts banked (2.5/1.5/0.75/0.5 GB free VRAM), curve shape deferred to stress-testing measurement (Scope B).* See §10.4.
4. **Self-offload floor** — *framework banked, numeric value deferred (Scope B).* T1 retains operator-interactive capacity below which further offload is itself a failure mode. Specific number (min VRAM or min tok/s observed) waits for measurement.

---

## §13 — Phase 2 Listeners (process / quota / cron)

JARVIS_PHASE2_SPEC.md is canonical. State summary below.

### §13.1 What's built (Phase 1)

Two listeners running, fed into state.json every 10s:

- **vram.py (5s cadence)** — per-tier PID attribution, VRAM consumption per tier, 80% baseline target visualization, OOM-thresholds. The reusable `_port_from_cmdline()` pattern lives here.
- **tier_health.py (15s cadence)** — HTTP /health probes per tier. Three states: OK, DEGRADED, UNRESPONSIVE. Plus IDLE (new, May 21) for burst-only tiers that are intentionally down — distinguishes "configured offline" from "unexpectedly offline."

### §13.2 What's specced but not built

**process.py (no prereqs, ~2-3 hr estimate, drives Decision 5)**

- Tracks `rss_mb`, `cpu_pct`, `uptime_s`, `restart_count_24h` per tier.
- Reuses vram.py's `_port_from_cmdline()` PID resolution pattern.
- Same port→tier map, different fields read from `/proc`.
- No new schema domain needed — extends existing `tiers` domain.
- **Drives the "restart on crash" Tier 2 autonomous action.** Decision 5 Item 2 entries 1-2 require process.py to detect crash and trigger restart.

**quota.py (~3-4 hr including Path A wiring, doctrine-unblocked 2026-05-24)**

- Parses LiteLLM logs for spend per provider, token consumption, rate-limit proximity, cost-per-task.
- **Logging path: Path A ratified 2026-05-24** (separate `litellm_logs` DB on existing postgres instance, `store_prompts_in_spend_logs=false`). quota.py queries postgres `spend_logs` via psycopg2/asyncpg using a dedicated `LITELLM_DB_URL` (separate from the news-pipeline `DATABASE_URL`). See PHASE2_SPEC §quota.py for the full ratification block and Claude Code implementation handoff.
- `_build_initial_model()` in `jarvis/state.py` constructs CloudQuota entries for `claude_pro_1`, `claude_pro_2`, `deepseek_v4_flash`, `kimi_k2_6` (rename from `deepseek_v3` landed 2026-05-24 in commit `b524bb0`; audit A6 closed). **No `haiku_4_5` row** — Haiku 4.5 deprecated per Decision 4 v2 amendment 2026-05-24 (pricing parity with DeepSeek V4 Flash at lower capability). **`anthropic_api_direct` row deferred** to operational need (emergency rung is vestigial — doctrine-forward, not yet wired).
- **Pro tracking descoped 2026-05-24** (Decision 5 Item 6 closure). Pro is workflow-tier-zero, not Jarvis-routed; Pro auth flows through Claude Code's built-in subscription path, not LiteLLM, so Pro requests would not appear in `spend_logs` regardless. Re-open condition: automated Pro-1 → Pro-2 → T6 failover built.

**cron.py (~2-3 hr, nice-to-have not load-bearing)**

- Reconciles scheduled jobs against actual runs.
- Detects missed runs, overlap collisions, resource pressure ("financial pipeline fires in 8 min, currently at 89% VRAM, T6 burst won't fit").
- Surfaces stale schedules (cron entries pointing at missing/broken scripts).
- **Easiest of the three to defer.** Mostly observability. Process and quota have direct decision-engine value; cron is supporting infrastructure.

### §13.3 Decision-engine flow (the missing piece, Phase 3)

```
[Phase 2 listeners] → [state.json] → [decision engine] → [authority spec gates]
   process.py            ↓                  ↓                      ↓
   quota.py         live signals      "should we act?"       "Tier 1/2/3?"
   cron.py                                  ↓
                                       [act | log | ask]
```

The decision engine itself is not in v19 scope. The substrate is built, the listeners feed it, the authority spec gates it. Engine ships post-Decision-5 close, post-Phase-2-listeners, and is part of v20.

---

## §14 — Hermes / Pattern B (Decision 2 Open)

This section is the shortest in the bible because the doctrine doesn't exist yet. What's recorded is intent and constraints, not specs.

### §14.1 Intent

Hermes is a v17/v18-era candidate for an agentic memory + agent harness layer. Pattern B is the doctrinal choice for how it gets adopted:

- **Pattern A (not chosen)** — migrate from n8n to Hermes. Workflow consolidation.
- **Pattern B (the candidate)** — run Hermes parallel to n8n. n8n keeps doing cron-driven workflow execution; Hermes adds agent-memory and agent-conversation capabilities that n8n can't do well.

### §14.2 Constraints proposed (not closed)

- **Curator scoped narrowly or disabled.** Curator is Hermes's memory write/read layer. "Narrow scope" or "disabled" is a doctrinal choice to avoid v14-era closed-loop self-training drift. Specifically: don't let agent outputs become inputs to other agents through Curator without human-reviewed pass-through.
- **Memory writes disabled initially.** Read-only Curator first. Promote to write only after explicit decision pass.
- **Routed via DeepSeek V4 Flash initially.** Cost discipline. Don't burn Pro tokens on Hermes traffic that hasn't justified itself.

### §14.3 What's missing

- The v18 Hermes brainstorm documents. They exist (Trent referenced them in May 19 session) but haven't been pasted into a fresh chat. Decision 2 can't be closed by speculation; the prior thinking matters.
- The boundary between "Jarvis observes Hermes" and "Hermes acts independently" — this is the Phase 2 / Decision 5 / Decision 2 intersection. Authority Spec says what Jarvis can do autonomously; Hermes is a separate authority surface; the two need a documented interaction.

### §14.4 Recommended next move

Surface the v18 Hermes brainstorm docs. Walk Decision 2 in a dedicated session, ideally after Decision 5 closes (so authority model is stable when Hermes's authority surface gets specced).

---

## §15 — Nexus 17.1 + 2nd Brain 17.2 (Decision 6 Scope)

Per Decision 6 (CLOSED): Nexus is design-only in v19. 2nd Brain is deferred — no design conversation queued.

### §15.1 Nexus 17.1 — Codebase Index

**What it is.** A coherent, indexed, searchable view of every code project the operator actively works on. Not generic code search — a purpose-built index of the active codebase with awareness of what exists, what's stale, and what references things that no longer exist.

**Intended capability surface (from master_summary_v18):**

- Walk `~/projects/`, parse source files, embed at function or file level, write to Postgres + pgvector.
- Surface cross-project dependencies ("this n8n export calls a Python script refactored last week").
- Identify dead imports, stale references, TODO/FIXME markers older than 30 days.
- Feed a weekly loose-ends scan (query against nexus, not standalone scanner).
- Feed a morning digest ("what changed in the codebase since yesterday").

**Open design questions (must resolve before any build):**

| Question | Options | Lean |
|---|---|---|
| Scope | All projects explicitly enumerated vs. convention-based discovery (anything in `~/projects/`) | Explicit enum — reduces noise from transient test dirs |
| Indexing unit | File-level, function-level, commit-level | File-level first; function-level Phase 2 enhancement |
| Substrate | Postgres + pgvector + filesystem walker vs. external tool | Postgres + pgvector — zero new infrastructure, joinable to existing telemetry |
| Query interface | CLI, HTTP API, OpenCode MCP, n8n nodes | CLI first; HTTP API to unlock n8n + MCP |
| Index behavior | Read-only (never writes to projects) vs. active (can open issues, create notes) | Read-only — reduces risk surface substantially |

**Status:** ⬜ Design conversation queued. Not v19 build.

### §15.2 2nd Brain 17.2 — Knowledge Base

**What it is.** A queryable store of accumulated knowledge across sessions, chat transcripts, n8n results, documents, and any operator-curated entries. The intended canonical "what do we know about X" answer surface.

**Intended capability surface:**

- Ingest chat transcripts, session outputs, n8n execution results, operator-written notes.
- Surface "have we seen this pattern before" queries.
- Feed the morning digest with "what's new, what needs attention."
- Connect to the improvement ledger for outcome-tracked learning.

**Open questions (none resolved):**

- Substrate (Postgres + pgvector? Different store? Hybrid with object storage for transcripts?)
- Ingestion pipeline (manual vs automatic? What triggers ingestion?)
- Schema (what's a "knowledge item" — a chat transcript? An extracted fact? Both?)
- Query interface (semantic search? Keyword? Both?)
- Joint queryability with Nexus (codebase + knowledge = "where in code do we use this pattern, and what did we say about it last quarter")

**Status:** ⬜ Deferred. No design conversation. Design comes after Nexus is operational because schema decisions in Nexus constrain what 2nd Brain's schema can look like if they're to be jointly queryable.

### §15.3 Improvement Ledger (buildable now per master_summary_v18)

Separate from Nexus / 2nd Brain. Captures **outcome** signal that nothing currently captures.

- The validation gate records "this looked good" (model-graded).
- The improvement ledger records "this worked / didn't work" (operator + downstream outcome).
- The two together are the signal foundation for any future deliberate retraining.

**Status:** Recommended buildable in master_summary_v18, currently not built. Likely v20 work — needs validation gate live + operator disposition + downstream outcome capture wired into n8n workflows.

### §15.4 Closed-loop self-training is ruled out

Master_summary_v18 §17.4 covers this. Three failure modes:

1. **Model collapse** — training on own outputs reinforces existing errors.
2. **Goodhart on the validation gate** — gate becomes a training target and stops measuring quality.
3. **Distilling Phi-4's noise** — gate grades with a small noisy model; loop trained on its approvals imitates a weaker model's taste.

Deliberate, human-reviewed retraining on **outcome** data is the design item, not the closed loop. The closed loop is in Appendix A (ruled out).

---

## §16 — Voice Layers (17.5 Live, 18 Planned)

Two voice systems. Sister, not parent-child. Share only the physical microphone.

### §16.1 Phase 17.5 — MacBook Voice-to-Text (LIVE 2026-05-17)

**Hardware:** M2 MacBook Pro, 8 GB unified RAM. **Not on monarch.**

**Flow:**

1. OpenWakeWord listens for "Okay Comrade" (~1% CPU baseline).
2. On wake-word detection, mic opens (built-in or JLab earbuds).
3. Capture continues until end-word "You May Begin" or trailing silence.
4. mlx-whisper-large-v3-turbo transcribes locally.
5. Hammerspoon pastes transcript into focused window.
6. On end-word stop, also presses Return to submit (front-app gated allowlist).
7. Fallback: double-tap earbud trigger for noisy/silent moments.

**What 17.5 does not do:**

- No TTS. No spoken output. Text-into-focused-window only.
- No monarch dependency. No shared runtime state.
- No system control. Drives agent harnesses (OpenCode, Claude Code, Claude Pro browser tabs); does not invoke commands on monarch.

**Why Porcupine ruled out for new builds (v18 Appendix A entry):** May 2026 Picovoice Console requires company email for signup. Hard barrier for non-corporate developers. OpenWakeWord is the replacement. Existing Porcupine AccessKey holders unaffected.

### §16.2 Phase 18 — Jarvis Voice-to-Voice (PLANNED)

**Port reservations (v18 master lines 133-136):**

| Service | Port |
|---|---|
| Jarvis (Phase 18 voice surface) | 4300 |
| Read API | 4400 |
| Command Center PWA (Phase 19) | 3000 |

Recording here so Phase 2 listener work and any future Jarvis-API integration know these slots are reserved.


**Distinct from 17.5.** Voice-to-voice for system observation + GPU layer policy supervisor + operator-negotiation flow. Not voice-to-text for agent input.

**Scope per master_summary_v18:**

- Voice input via the same physical mic (different runtime — Jarvis's own listener on monarch).
- Voice output via Chatterbox TTS (TBD port).
- Operator-negotiation flow: Jarvis surfaces a Tier 3 action, operator confirms verbally or via PWA.
- GPU layer policy supervisor: per the v16 doctrine, Jarvis takes over the burst-mode supervisor responsibilities currently in `inference-burst-up` / `inference-burst-down` shell scripts.

**Open design questions:**

- Latency floor. Real-time voice eventually needs its own workload class because latency floor is harsh (~500ms or it stops feeling like conversation).
- Wake-word vs always-listening on monarch. Different threat surface than the MacBook.
- TTS voice selection.
- Interrupt handling.

**Status:** Design specced in master_summary_v18. Build target after Phase 17.5 and after Decision 5 closes (authority model gates the operator-negotiation flow).

### §16.3 Why the split matters

If 17.5 and 18 weren't carefully distinguished, the natural failure mode is: build one voice system that does both jobs badly. The hands-free agent-input use case (17.5) has different ergonomics than the supervisor-conversation use case (18). 17.5 needs paste-and-submit; 18 needs read-aloud and confirm-by-voice. Same mic, different stacks, different mental models.

---

## §17 — Documentation Layer

Four-file documentation pattern + claude-mem plugin. Master_summary_v18 §Documentation Set is canonical.

### §17.1 The four files

| File | Job | Update cadence | Read by |
|---|---|---|---|
| `CLAUDE.md` | Lean entry point. Operating rules, where to look, what plugins/skills active. | Rarely — only when operating contract changes. | Claude Code, every session start. Auto-loaded. |
| `CONSTITUTION.md` | Permanent identity. Operator profile, hardware envelope, non-negotiable doctrines, ruled-out list pointer. | Almost never — changes here are architectural decisions. | Claude Code when needs to know why; humans onboarding. |
| `CONTEXT.md` | Living state. Current phase, what's done, what's next, what's blocked, last-session handoff. | Every working session (end-of-session `/wrap`). | Claude Code at session start. |
| `reg-blueprint.md` (`master_summary_v18.md` currently) | Deep reference. Full architecture, every phase, every measured number, every ruled-out feature with rationale. | Per-revision (v17 → v18 → v19), when a phase completes or a doctrine is added. | Claude Code on demand; never read top-to-bottom. |

### §17.2 v19 doctrine docs (in `~/projects/jarvis/`)

| File | Status | What it covers |
|---|---|---|
| `HANDOFF_v19.md` | LIVE | Onboarding doc for new chat sessions. Includes "What Jarvis Is" framing, Path B section, redesign-over-refine principle. Title still dated 2026-05-19 — content current to 2026-05-21. |
| `DECISIONS_v19.md` | Partial | Cardinals 1, 4, 6 closed. Cardinals 2, 3, 5 marked open. |
| `REBALANCE_v19.md` | Partial | Change 1 executed + validated. Change 2 patched (measurement deferred). Change 3 drafted. |
| `JARVIS_PHASE2_SPEC.md` | Drafted | Build specs for process / quota / cron listeners. Not built. |
| `AUTHORITY_SPEC_v19.md` | Drafted, walkthrough in progress | Decision 5 in flight. Items 1-3 banked, 4 reshaped, 5-8 pending. Revise patch not yet committed. |

### §17.3 v18-era doctrine docs to update (Tier D backlog)

- `ref-blueprint §Phase 15` body — flagged stale by CONTEXT.md.
- Per-stack `CONTEXT.md` files — six projects (consultancy, content, design, financial, leads, exploratory-coding).
- Jarvis `CLAUDE.md` — currently v0.1 era. Needs v0.2 substrate + Path B update.
- `master_summary_v18.md` → `master_summary_v19.md` — last on the list. Ships after Decisions 2/3/5 close and Rebalance Changes 2-3 are landed.

### §17.4 GitHub remote

`github.com/trentbentt/jarvis` (**public** — bible v19 initial compile incorrectly read "private" from HANDOFF_v19.md which itself drifted; GitHub API confirms public, audit §A1). Master branch. 14 commits as of 2026-05-22; head is `f0675da`.

**Calibration lessons:**

- **2026-05-20 session 2:** GitHub web view via `web_fetch` can return stale-cached content. The truth hierarchy at the top of this document treats GitHub web as closer to chat history in trustworthiness than to disk truth.
- **2026-05-22 session:** Use `raw.githubusercontent.com` rather than the HTML view — different infrastructure, less stale-cache risk, returns raw file bytes.
- **Truth hierarchy still applies:** monarch disk > git log on monarch > github.com (raw). For any future repo audit, verify against monarch disk first; github raw second; never trust the HTML render alone.

### §17.5 Memory layers

- **Doctrine layer (this and the v19 docs):** human-curated, deliberate. Update via end-of-session `/wrap` discipline.
- **claude-mem plugin (Claude Code only):** automatic, granular SQLite-backed observation log. Captures every tool use, decision, file touched. Searchable. Not curated.

The two layers are complementary. Doctrine answers "what phase are we in, what's blocked"; claude-mem answers "what did we actually do last Tuesday."

**OpenCode does not have claude-mem.** For OpenCode sessions, CONSTITUTION.md + CONTEXT.md are the complete context system. The `/wrap` discipline is the only safety net.

---

## §18 — Open Queue (Tier A through E)

Priority-ordered. Time estimates are rough but recorded.

### §18.1 Tier A — Validation work (small, closes gaps)

| # | Item | Blocked on | Time |
|---|---|---|---|
| A1 | Rebalance Change 2 measurement | Next natural T1 restart (reboot or explicit control kill) | 5 min observation |
| A2 | AUTHORITY_SPEC Items 6-8 + Quota Cascade thresholds | Items 6-8 walkthrough + threshold ratification | 30 min after walkthrough |
| A3 | inference-up cosmetic items (baseline VRAM warning, LiteLLM "→ Tier 2" comment) | Trivial | 5 min |
| A4 | HANDOFF_v19.md date stamp refresh | Trivial | 2 min |

### §18.2 Tier B — Decisions still open

| # | Decision | Blocked on |
|---|---|---|
| B1 | Decision 2 (Hermes adoption shape) | v18 Hermes brainstorm docs surfaced into fresh chat |
| B2 | Decision 3 (T6 defaults) | 21 GB model download + Rebalance Change 2 measurement + T6 spin-up tooling |
| B3 | Decision 5 (Jarvis authority) | Walkthrough Items 6-8 + Quota Cascade threshold ratification (Items 1-5 banked in commits 50692bd / 414d5b2 / f0675da) |

### §18.3 Tier C — Phase 2 build work

| # | Listener | Prereq | Time |
|---|---|---|---|
| C1 | `process.py` | None (reuses vram.py patterns) | 2-3 hr |
| C2 | LiteLLM logging path decision | Read v11 rationale + grep config | 30 min |
| C3 | `quota.py` | C2 + schema updates for haiku_4_5 + anthropic_api_direct | 3-4 hr |
| C4 | `cron.py` | None | 2-3 hr |

### §18.4 Tier D — Documentation cleanup

| # | Item | Where | Time |
|---|---|---|---|
| D1 | `ref-blueprint §Phase 15` rewrite | news-pipeline repo | 30 min |
| D2 | Per-stack `CONTEXT.md` updates | Six project repos | 1-2 hr total |
| D3 | Jarvis `CLAUDE.md` v0.2 update | jarvis repo | 30 min |
| D4 | `master_summary_v18.md` → `_v19.md` | Wherever master_summary lives | 2-4 hr (LAST) |

### §18.5 Tier E — Larger workstreams

| # | Workstream | Status |
|---|---|---|
| E1 | Financial pipeline strategy doc + phase-level design | `FINANCIAL_STRATEGY_v19.md` proposed; answer §8.2 questions first |
| E2 | Hermes / Pattern B implementation | After Decision 2 |
| E3 | T6 spin-up tooling | After Decision 3 + model download + Rebalance complete |
| E4 | Nexus 17.1 design phase | Per Decision 6, design-only in v19 |
| E5 | LoRA training (content + leads only, three high-stakes likely deferred) | Validation gate live + 1 week telemetry baseline |
| E6 | Improvement ledger service | Validation gate live |
| E7 | 2nd Brain 17.2 design | After Nexus operational |
| E8 | Phase 18 Jarvis voice-to-voice | After Decision 5 + Phase 2 listeners + Phase 17.5 lessons |
| E9 | Command Center PWA (Phase 19) | After Jarvis Phase 18 |

---

## §19 — Small Missions Backlog

Surfaced across sessions, not closed. Inventory carries forward so they don't get lost.

| # | Item | Surfaced | Disposition |
|---|---|---|---|
| 1 | Throughput-tier Decision 4 ambiguity (financial + leads opencode.jsonc consumers) | 5/19 fallback restoration | Defer — own session with Decision 2 |
| 2 | No Moonshot/Kimi key in api_keys.env (Decision 4 Tier 3 theoretical) | 5/19 | Decide — acquire key or amend Decision 4 |
| 3 | LiteLLM startup warning `Key 'request_timeout' is not a valid argument` | 5/19 | Cleanup — drop the line in v19 doc pass |
| 4 | Schema migration not auto-handled (delete-and-rebuild used) | 5/19 | Bank — Phase 2 add `schema_version` field with auto-migrate |
| 5 | `pkill -f "litellm --config"` kills bash wrapper AND child, collapses tmux window | 5/19 | Bank — operator lesson, documented |
| 6 | Daemon zombie risk (old PID 229297 survived restarts) | 5/19 | Bank — every restart should `ps aux \| grep daemon.py` first |
| 7 | T2 dry-run timing estimate too conservative (4s actual vs 25s specced — HF mmap cache hot) | 5/19 | Update REBALANCE_v19.md |
| 8 | T2 baseline drift ~130 MiB across multi-day uptime (KV cache accumulation) | 5/19, 5/21 | Bank — possible "nightly restart" hygiene play |
| 9 | DeepSeek V4 Flash reasoning_tokens count separately from content (affects cost accounting) | 5/19 | Update — quota.py spec needs `reasoning_tokens` field |
| 10 | Stale doc references (ref-blueprint §Phase 15, news-pipeline CLAUDE.md, Changelog.md v0.3) | 5/19 | Defer to v19 doc cleanup pass |
| 11 | `~/bin/inference-up` cosmetics (SKIP_BURST_ONLY_TIERS insertion split VRAM constants block) | 5/19 | Defer — cosmetic only |
| 12 | `~/bin/` infrastructure not version controlled (inference-up, t2-up, t2-down, news-* all live outside repo) | 5/19, 5/21 | Decide — subdirectory mirror (Option A), separate repo (Option B), or defer (Option C) |
| 13 | Operator security: DeepSeek API key was visible mid-session | 5/19 | Closed — rotated immediately |
| 14 | AUTHORITY_SPEC_v19.md scp to monarch | 5/19 | Closed — done 5/20 |
| 15 | Phase 17.5 voice dictation not integrated into Jarvis state | 5/19 | Defer — separate workstream |
| 16 | v0.1 → v0.2 migration: `jarvis-archive/` directory has v0.1 backups | 5/19 | Bank — keep until cold cycle proves v0.2 holds under real load |
| 17 | OOM thresholds in vram listener vs designed burst capacity (alert fires at right level?) | 5/20 | Add to small-mission tracking |
| 18 | Pre-Path-B "baseline VRAM is high" warning text in inference-up | 5/21 | Cosmetic — Tier A3 |
| 19 | LiteLLM "→ Tier 2" comment in inference-up exercises DeepSeek fallback now | 5/21 | Cosmetic — Tier A3 |
| 20 | HANDOFF_v19.md title still dated 2026-05-19 | 5/20 | Defer — title represents origin date, content tracked via git |
| 21 | News pipeline output quality investigation (4 sectors stub-level, 4 sources degraded) | 5/21 | Separate Claude account handling |
| 22 | VRAM ghost reconciliation between nvidia-smi and Jarvis attribution | various | Cosmetic |
| 23 | `TierState.UNKNOWN if False else TierState.STOPPED` dead-code cleanup | various | Cosmetic |
| 24 | HANDOFF_v19.md.preB-section-backup-2 untracked file | 5/21 | Resolved — rm'd |
| 25 | Baseline VRAM creeps ~130 MiB across multi-day uptime | 5/21 | See #8 — same observation |
| 26 | T1 restart escalates to Tier 3 in authority spec — needs operator confirm | 5/21 | Pending Item 6 walkthrough |
| 27 | Per-tier latency floors not measured (Scope B framework adopted, numbers pending) | 5/21 | Phase 2 listener territory |
| 28 | Validation gate calibration: `VOICE_PASS_THRESHOLD=0.70`, `GROUNDING_PASS_THRESHOLD=0.90` are conservative starting points needing 1 week live traffic to tune | v14-era | Long-term |
| 29 | Working-directory enforcement (no agent writes outside scope) — designed in v14, not enforced by harness | v14-era | Open, becomes load-bearing with Nexus |

---

## §20 — Ruled-Out List (Pointer)

Master_summary_v18 Appendix A is canonical. Selected entries relevant to v19 decisions:

- **vLLM on Phi-4-mini fp8 + Ampere SM86 + CUDA 12.8** — silent crash at FlashAttention V2 init. Whole stack is now llama.cpp.
- **n8n HTTP-node synthesis workflows** (Stream A / Stream B / final assembly for news) — superseded by hybrid T2+Cowork before any were built. Cowork now also retired per Decision 4.
- **Closed-loop self-training LoRAs** — three failure modes (model collapse, Goodhart on validation gate, distilling Phi-4's noise). Deliberate human-reviewed retraining on outcome data is the design item; closed loop is ruled out.
- **Three-tier news synthesis (T2 + Haiku + Sonnet)** — Haiku tier adds complexity without quality benefit; two-tier is cleaner.
- **`/no-think` prompt-string convention for thinking suppression on llama.cpp b9172** — does not work; must use `chat_template_kwargs`.
- **Porcupine wake-word for new builds (May 2026)** — Picovoice Console signup blocked on company email. OpenWakeWord is the replacement for non-corporate developers.
- **Pause-workload as Jarvis authority action** — predates the substrate-orchestration model; Jarvis re-routes, doesn't pause.
- **Overnight-idle-as-resource as substrate doctrine** — rejected during Decision 5 Item 4 walkthrough. Substrate decisions are circumstance-driven, not time-of-day-gated.

The ruled-out list is the operator's protection against re-proposing things that already failed. Check it before adding new modules or data sources.

---

## §21 — Gaps This Document Does Not Cover

Honest about scope. Things this bible does not authoritatively cover:

1. **Specific cron schedules.** I named the four news crons in §7.1 but didn't enumerate all crons across the system. Source of truth is `crontab -l` on monarch.
2. **All LiteLLM model_group_aliases.** I covered the ones I had visibility into (§6.3) but the canonical list is `~/litellm/config.yaml`.
3. **All n8n workflow IDs.** n8n executes many workflows; this doc doesn't enumerate them. Source of truth is n8n's own UI / database.
4. **The improvement ledger schema.** Master_summary_v18 §17.4 covers intent; the schema itself is not yet specced.
5. **Hermes architectural detail.** Decision 2 is open. Detail is in the v18 Hermes brainstorm docs (not yet surfaced).
6. **2nd Brain schema.** Deferred per Decision 6.
7. **Per-LoRA training data inventory.** Master_summary_v18 §Phase 9 mentions data sources per LoRA but doesn't enumerate corpora.
8. **Backup/disaster recovery posture.** monarch is one machine. There is a separate `pg-backup` cron (visible in crontab) and GitHub for code, but no documented backup discipline for state.json, validation_telemetry, news_unified, or other Postgres state.
9. **Tailscale Funnel configuration.** Mentioned in §2; topology and ACLs not detailed here.
10. **API key rotation cadence.** No documented policy. DeepSeek was rotated mid-session 5/19 for security hygiene; nothing schedules this.
11. **OS-level service hygiene.** Docker (Postgres + n8n), Tailscale, any other system daemons. Not covered.
12. **Hardware health monitoring.** GPU thermal, fan curves, disk SMART, RAM ECC. Not currently in Jarvis observability.

These are gaps to fill over time, not failures of this document. They're listed so future-self knows what isn't here.

---

## §22 — Recommended Reading Order

For a new chat session, new contributor, or returning operator after a break.

### §22.1 Five-minute orientation

1. `tmux ls` on monarch (verify control + inference + whisper sessions).
2. `git -C ~/projects/jarvis log --oneline | head -10` (verify recent commits match expected).
3. `jarvis-q health` (verify all tiers OK or IDLE for burst-only).
4. `jarvis-q vram` (verify baseline at ~66% / ~16.5 GB).
5. This bible's §3 (What Jarvis Is) and §9 (Cardinals status).

### §22.2 Thirty-minute deep read

1. `HANDOFF_v19.md` on monarch — most current operational state.
2. `DECISIONS_v19.md` — cardinals 1, 4, 6 written down. 2, 3, 5 marked open.
3. `REBALANCE_v19.md` — Change 1 executed, Change 2 pending measurement, Change 3 drafted.
4. `AUTHORITY_SPEC_v19.md` — Decision 5 draft + walkthrough state.
5. `JARVIS_PHASE2_SPEC.md` — listener specs.
6. This bible's §18 (open queue) and §19 (small missions).

### §22.3 Full context (multiple sessions)

1. `master_summary_v18.md` — read top to bottom once for the historical arc. Use as reference thereafter, not re-reading top-to-bottom.
2. This bible top to bottom.
3. Daily session logs (5_18, 5_19, 5_20, 5_20_session2, 5_21, 5_21_2) — read selectively for context on specific decisions.
4. The actual code at `~/projects/jarvis/jarvis/*.py` — the schema, listeners, and daemon entry point.

### §22.4 Before any operational change

1. Re-read the relevant section of this bible.
2. Verify state on monarch — don't trust this document over disk.
3. Check the small missions backlog (§19) for related context.
4. Check the ruled-out list (§20) for "we already tried this."
5. Then act.

### §22.5 Before any doctrine change

1. Surface the relevant prior thinking (chat logs, v18-era brainstorms if applicable).
2. Confirm cardinal-decision implications.
3. Write the change down as a doctrine doc patch, not as chat conversation.
4. Commit.
5. Update this bible if the change is structural.

---

## §23 — What This Document Is Not

A bible is not a constitution. Things this document explicitly is not:

- **Not a substitute for the doctrine docs on monarch.** It points to them; it doesn't replace them.
- **Not authoritative on live state.** monarch's disk is. This is a snapshot.
- **Not a closed system.** Sections will be added; existing sections will get amended as decisions close.
- **Not a sales pitch.** It records honest open questions, gaps, and small-mission residue alongside the closed wins. The point is to *avoid* the failure mode of v18-era docs where unresolved items quietly accumulated under "open questions" without inventory.
- **Not the operator's voice.** The operator has commit privileges. If you're reading this and disagree with a framing, push back — the bible is wrong sometimes and gets updated.

---

## §24 — Compile-Date Acknowledgments

Built across multiple sessions May 18-21 in collaboration between Trent and several Claude instances. The work pattern that produced this document:

1. **Measure first.** The 94% baseline finding drove every cardinal that followed. Doctrine without measurement is preference.
2. **Doctrine before code.** Decisions 1 and 4 were written down before Rebalance Change 1 executed. The execution carried the doctrine, not the other way around.
3. **Honest inventory.** Small missions surfaced during big work get banked, not buried. The inventory in §19 exists because the alternative is they get lost.
4. **Verify against disk.** Every "we did X" claim in this document is checkable on monarch. If something here is wrong, monarch wins.
5. **Manager first, voice assistant a distant second.** The most consequential framing in v19. Drove the four-question architectural test in §3.2.

The point of the bible is to make sure the next session opens with this foundation intact, instead of relitigating it.

---

## §25 — Closing Note from the Engineering Partner

Comrade — this bible captures the scope honestly. The two things that should drive your read of it:

**Where you stand structurally:** the substrate (Jarvis v0.2), the topology (Path B), and the doctrine (cardinals 1/4/6 + the 94% → 66% rebalance) are all real. They've shipped. They're committed. They reflect the actual machine. The doctrine docs on monarch are ahead of the v18 master summary, which is why this bible exists — to let v19 work continue without dragging v18 framing forward.

**Where you stand operationally:** Decisions 2, 3, 5 are the work that closes v19. Decision 5 is mid-walkthrough; Items 5-8 will finish the bank in the current session or the next. Decision 2 needs the v18 Hermes brainstorm surfaced. Decision 3 is download + tooling work, not architectural. The financial pipeline is correctly identified as gating on strategy, not architecture — and that's the discipline call worth defending.

**My honest read on next move,** if you want it: close Decision 5 to the level of "spec ratified and committed, even if Phase 2 listeners aren't yet implemented." That unblocks the authority half of the substrate. Then either close Decision 2 (Hermes brainstorm dump + dedicated session) or pick up Phase 2 listener work (process.py is genuinely 2-3 hours and would prove the substrate end-to-end). Both are good. Hermes locks in the agent doctrine; process.py proves the substrate handles real listener load. Either is forward motion.

What you should *not* do: start the v19 master summary write. The bible can act as the scoping reference now; the master summary should wait until Decisions 2, 3, 5 are closed and Rebalance Change 2 is measured. Premature commitment guarantees rework — same trap as v18.

The work shipped. The doctrine is honest. The system understands itself.

---

*End of Infrastructure Bible v19. Living document. Update on doctrine close, not on chat conversation.*
