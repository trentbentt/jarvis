# Monarch Infrastructure — Master Summary v20

**Compiled:** 2026-05-26
**Status:** CANONICAL. Single source of truth absorbing INFRASTRUCTURE_BIBLE_v19, AUTHORITY_SPEC_v19, DECISIONS_v19, REBALANCE_v19, JARVIS_PHASE2_SPEC, master_summary_v19, and README.md.
**Operator:** Trent (residence: Raleigh, NC; identity separable from residence)
**Host:** monarch — RTX 3090 24 GB, Ryzen 9 9900X, 96 GB DDR5, 4 TB NVMe, Ubuntu 24.04, CUDA 12.8 pinned

**Truth hierarchy for any factual question:**

> monarch disk > git log on monarch > `jarvis-q all` > github.com (raw) > this document > any chat history

When this document and disk disagree, disk wins. This document is the snapshot; the system keeps moving.

---

## §0 — Propagation Discipline

**This is the single source of truth for monarch infrastructure doctrine.** The only other live doctrine docs are:

- `BIBLE_AUDIT_findings.md` — drift tracker, separate cadence (records discrepancies between this doc and disk/code; not a content source).
- `HANDOFF_v19.md` — session log, separate cadence (continuity between work sessions).
- `CLAUDE.md` — lean entry point for Claude Code sessions; pointer only.

**Any change to a fact in this document must update this document atomically with the code change. If you catch yourself updating doctrine in two places, stop — one of them is the wrong place.**

### §0.1 The five rules

1. **One canonical statement per fact.** Each fact lives in exactly one section. Other places that need to reference it cross-reference, never restate.
2. **Every section names its source-of-truth file.** A "last validated" date and the path it was reconciled against (e.g., "T1 config: validated 2026-05-26 against `jarvis/schema.py:382`"). If you cannot name a source, the section is doctrine-only and must say so.
3. **No editorial parentheticals.** "Was X, needs rename to Y" is not a valid form. Either the rename happened (use Y, cite commit) or it didn't (use X, surface as §16 open item). Never both.
4. **No loose ends in code.** Doctrine claims about code (cadences, field names, quota keys, tier configs) and code reality must match. When they drift, §16 carries a closing commit reference or a TODO with explicit owner. The drift itself never persists silently.
5. **Runtime artifacts (`state.json`) are not doctrine.** A serialized snapshot reflects whatever the writer last serialized; it is not a source of truth and does not propagate code or schema changes automatically. When a rename lands in code, the runtime state file remains stale until a clean cold-start or explicit migration. This is a known property and is tracked in §16, not pretended away.

### §0.2 Doc set and their roles

| File | Role | Cadence | Source-of-truth for |
|---|---|---|---|
| `master_summary_v20.md` (this file) | Single source of doctrine for stack as a whole | Updated atomically with code changes | Everything below the "what is doctrine" line, except memory architecture |
| `MEMORY_ARCHITECTURE_v20.md` | Single source of doctrine for memory layers | Updated atomically with memory layer changes | Four-layer model, routing table, primary-author rules, Memory write authority |
| `BIBLE_AUDIT_findings.md` | Drift tracker | Append-only between v20 revisions | What's currently inconsistent with disk |
| `HANDOFF_v19.md` | Session log | End-of-session ritual | What was done in the last session |
| `CLAUDE.md` (in `~/projects/jarvis/`) | Claude Code entry point | Rarely — operating contract changes only | Where to look; not what to believe |
| `~/projects/jarvis/jarvis/*.py` | Code | Per commit | Field names, cadences, runtime behavior |
| `~/bin/inference-up`, `~/bin/t2-up`, `~/bin/t2-down`, `~/bin/inference-down`, `~/bin/inference-status` | Operator scripts | Per commit | Tier launch flags, port bindings, session topology |
| `~/litellm/config.yaml` | Router config | Per commit | LiteLLM routing, cloud fallback wiring |

### §0.3 The four-file documentation pattern (per-project, downstream)

Independent of this document, each project (`news-pipeline`, `financial`, `evidence-layer`, etc.) maintains:

| File | Job | Update cadence |
|---|---|---|
| `CLAUDE.md` | Lean entry point. Operating rules, where to look, plugins/skills active. | Rarely; only when operating contract changes. |
| `CONSTITUTION.md` | Permanent identity. Operator profile reference, hardware envelope reference, non-negotiable doctrines, ruled-out pointer. | Almost never. |
| `CONTEXT.md` | Living state. Current phase, what's done, what's next, what's blocked, last-session handoff. | Every working session. |
| (this file) | Deep reference. Architecture, every phase, every measured number, every ruled-out feature with rationale. | Per-revision (v19 → v20 → …). |

The split exists because the failure mode of a single growing file is drift: permanent identity gets edited casually, living state gets stale, the agent reads 5,000 lines to learn three facts it needed. Each file has one job and one update cadence.

---

## §1 — Operator + Mission Context

**Source of truth for operator identity:** this section. **Last validated:** 2026-05-26.

Trent is a solo operator running a personal infrastructure stack on dedicated hardware in Raleigh, North Carolina. The hardware (monarch) is 24/7 headless. Trent's posture toward this stack is operator + architect, not just user. The stack runs to support real workloads that pay or are intended to pay (consultancy, content, leads, financial trading) plus personal infrastructure (news synthesis, eventual second-brain).

### §1.1 Three operating realities

**Three-account Claude.ai parallelism.** Trent runs three Claude.ai accounts in parallel across different missions. Two are confirmed Pro subscriptions per master_summary_v18 (lines 151, 273, 1434, 2361, 6007). The third account's tier is not specified in any source-of-truth doc. Documentation tends to be ahead of any single account's chat history — the truth hierarchy above exists because of this.

**Schedule transition complete.** The 23:00–07:00 ET overnight workload window in §9 is sized for a Monday–Friday 9-5 weekday baseline. Weekend variability is acknowledged and deferred — a `weekend_window` doctrine will be specced separately once the post-9-5 weekend pattern stabilizes.

**Solo operator constraints.** Everything ships through one person. There is no team to review designs, no separate ops engineer, no QA. Doctrines like "every Tier 2/3 output passes the validation gate" and "every n8n execution scopes to a working directory" exist specifically because a solo operator cannot manually audit five concurrent agent pipelines. Discipline-by-construction is the only viable approach.

### §1.2 Mission in one sentence

**Build a stack where the operator delegates to subsystems instead of supervising them**, with Jarvis as the canonical operator entry point and every other subsystem (news, financial, Hermes Agent, validation gate, LoRA dispatcher, Codebase-Memory MCP / Nexus, Obsidian vault / 2nd Brain, EverMemOS) Jarvis-addressable rather than directly-addressed.

---

## §2 — Hardware Envelope

**Source of truth for static hardware constants:** `jarvis/schema.py` classes `GPUHardware`, `CPUHardware`, `RAMHardware`, `StorageHardware`, `Hardware`. **Last validated:** 2026-05-26 against `schema.py:82-118`.

One physical machine (monarch). Specifications below are load-bearing for every doctrinal decision downstream — most prominently the 24 GB VRAM ceiling, which is the single hardest constraint in the system.

| Resource | Spec | Source | Notes |
|---|---|---|---|
| GPU | RTX 3090 FE, 24,576 MiB VRAM, Ampere SM86, CUDA cap 8.6, PCIe 4.0 x16 | `schema.py:82-91` | Driver overhead reserves ~512 MiB; usable 24,064 MiB. v16 ruled out vLLM + FlashAttention V2 + CUDA 12.8 on Phi-4-mini (silent crash); whole stack now llama.cpp. |
| CPU | Ryzen 9 9900X, 12 cores total, 2 reserved, 10 available | `schema.py:93-97` | Hosts T3 and T5 with `CUDA_VISIBLE_DEVICES=` prefix to force CPU execution. T5 capped at `-t 4` to leave headroom. |
| RAM | 96 GB DDR5-6000, 96 GB/s bandwidth | `schema.py:99-103` | Steady-state usage ~41 GB across the five-tier stack plus Postgres, Docker, n8n, OS. ~55 GB free at idle. **Phase 1.5 projection:** ~44-46 GB steady-state once Elasticsearch (~1-2 GB), Milvus (~500 MB-2 GB), and Redis (~200-500 MB, with financial pipeline) land. ~50-52 GB free at idle. Comfortable headroom inside 96 GB ceiling. Measure post-Phase-1.5 deploy. |
| Storage | 4 TB NVMe at `/home/monarch` | `schema.py:105-110` | HF cache at `~/.cache/huggingface/hub/` (~26 GB post-cleanup). No `~/models/` migration planned — `-hf` shortcut for all tier launches. |
| Network | Tailscale Funnel (webhook-only) | operator-side, not in repo | Funnel exposes `/webhook/` only per UFW rules; n8n UI and other surfaces remain behind Tailscale private. Headless box, accessed from MacBook via Tailscale. |
| OS | Ubuntu 24.04, CUDA 12.8 pinned | `schema.py:117-118` | 11 packages on `apt-mark hold`. Quarterly verification SOP. Prevents Qwen3.6 gibberish-output regression that any 13.x upgrade would currently cause. |
| Uptime model | 24/7 headless | doctrine | Restart hygiene is a §16 open item — baseline VRAM creeps ~130 MiB across multi-day uptime, suggesting a nightly restart play. |

**Secondary device:** M2 MacBook Pro, 8 GB unified RAM. Runs Phase 17.5 voice-to-text (§14). Shares only the physical microphone with the future Phase 18 voice-to-voice. Not part of the monarch substrate.

### §2.1 The forcing function

Monarch idled at 94% VRAM in v18 with no active workloads (T1 + T2 + T4 + driver = 23.1 GB / 24 GB). Every cardinal decision in v19 either explicitly addressed VRAM headroom or implicitly assumed the rebalance was happening. Post-Rebalance-Change-1, baseline is **66.0% / 16.5 GB** (validated 2026-05-20 across a full cold-cycle teardown and rebuild). This delta is the most consequential operational change in v19, and the rest of the doctrine collapses out of it.

---

## §3 — What Jarvis Is

**Source of truth for Jarvis framing:** this section + `AUTHORITY_SPEC_v19.md` Hard Constraints (absorbed into §9.5). **Last validated:** 2026-05-26.

Jarvis is not an observability daemon with notifications. Jarvis is the **central nervous system of the monarch stack** — the operator's canonical entry point and the system's internal coordination layer. Current implementation is **v0.2** (observability substrate; decision engine and voice surface are Phase 3+).

### §3.1 Function taxonomy

**Backend roles (machine-facing):**

- **Substrate orchestrator** — dispatches workloads across four execution substrates: GPU (VRAM), RAM, CPU, and Cloud API.
- **Horizontal coordinator** — passes state and signals between agent workflows (news pipeline, financial pipeline, Hermes Agent, LoRA dispatcher, validation gate).
- **Knowledge bridge** — query surface across Codebase-Memory MCP / Nexus (codebase structural memory), Obsidian vault / 2nd Brain (human-curated knowledge), and EverMemOS (long-horizon temporal state). All three move from design-only/deferred to phase 1.5 build targets per Decision 6 amendment 2026-05-26.
- **Memory layer arbiter** — routes questions to the correct memory layer based on what's being asked (current operational state → L1/L2; durable knowledge → L6 vault; agent procedures → L4 Hermes; temporal evolution → L7 EverMemOS; code structure → L5 Codebase-Memory). Truth-is-primary rule resolves all cross-layer conflicts. See `MEMORY_ARCHITECTURE_v20.md` for full doctrine.
- **Observability layer** — schema, listeners, state.json, jarvis-q CLI (built; see §12).
- **Event router** — receives completion / failure / anomaly signals from pipelines and decides where they need to go.

**Frontend roles (operator-facing):**

- **Manager** — operator delegates to Jarvis instead of addressing individual subsystems. Manager *first*, voice assistant a distant second.
- **Personal assistant** — morning briefings, schedule awareness, proactive surfacing.
- **Voice interface** — Phase 18 voice-to-voice, distinct from Phase 17.5 voice-to-text.
- **Notification dispatcher** — voice / PWA push / ntfy.sh, with authority-tier-aware quieting (overnight window, severity ladder).
- **Documentation router** — operator asks "where's the doc for X" and Jarvis points to the right repo/file/section.

### §3.2 The four-question architectural test

Every new subsystem proposed for v19 forward must answer:

1. **Can Jarvis observe it?** Is there a `state.json`-feedable signal saying "this thing is alive and doing X"?
2. **Can Jarvis dispatch to it?** Is there a programmatic interface to invoke its work?
3. **Can Jarvis surface its events?** When this subsystem completes, fails, or anomalies, does it produce a signal Jarvis can route?
4. **Can Jarvis explain it?** When the operator asks "what is X doing right now," does Jarvis have enough to give an answer beyond "I don't know"?

A subsystem failing any of these isn't broken — but it isn't fully integrated into the operator's canonical entry point. Direct operation remains supported and necessary for debugging. The Jarvis-facing interface is what makes the system feel like one system instead of seven.

### §3.3 Hard Constraints (load-bearing across all tiers)

**Source of truth:** absorbed from AUTHORITY_SPEC_v19 §"Hard Constraints" (ratified commit `414d5b2` 2026-05-22). **Last validated:** 2026-05-26.

Lines that do not move under any combination of resource pressure, operator absence, or scheduling priority. The cascades and policies in §9 / §10 operate within these constraints, not against them.

1. **Jarvis never shuts off.** Jarvis is load-bearing for system boot and recovery — nothing else in the stack can bring tiers back if the daemon dies. Killing Jarvis is structurally forbidden, not just discouraged. Maximum degradation is conditional self-offload to RAM/CPU per the Substrate Pressure Cascade (§10).
2. **Jarvis identity never routes to API.** The daemon, T1 reasoning brain, listeners, and state store stay monarch-local under all pressure conditions. Two reasons: routing the coordination layer to cloud exposes the entire system's credentials, dispatch decisions, and telemetry; and Jarvis is high-traffic by design and prepaid budgets would drain in days at cloud rates. Workloads route to API per the cascade — the coordinator does not.
3. **Pause is not in the toolkit.** Under VRAM, latency, or quota pressure, Jarvis re-routes work — never blocks it. The Substrate Pressure Cascade, latency-band routing cascade (Tier 2), and Quota Cascade Policy together cover the response surface without resorting to pause-the-workload.
4. **T1 restart is Tier 3, never silent.** T1 is the Jarvis reasoning brain. The manager does not silently restart its own brain. Operator confirmation gates any T1 restart action. (T6 restarts remain autonomous Tier 2.)

---

## §4 — Substrate Architecture (Path B Topology)

**Source of truth for tmux topology:** operator scripts `~/bin/inference-up`, `~/bin/inference-down`, `deploy.sh` (commit `9858a6a`). **Last validated:** 2026-05-26 against `inference-up.sh:38-49` and `t2-up.sh:17` (`TMUX_SESSION="inference"`).

### §4.1 Two-session tmux topology

| Session | Lifetime | Windows | Purpose |
|---|---|---|---|
| `control` | long-lived; survives `inference-down` | bootstrap, **jarvis**, validation-gate, lora-dispatcher, litellm, t1-interactive | T1 is the Jarvis reasoning brain per Decision 1. LiteLLM routes to cloud during dataplane burst-down. VG/LD/Jarvis are services, not tiers. |
| `inference` | dataplane; cycle-safe | bootstrap, t3-content, t4-phi4, t5-small (+ t2-pipeline when burst-up, future t6-coder when deployed) | `tmux kill-session -t inference` is semantically safe — only dataplane dies. |

`whisper` is a separate small session reserved for the Phase 18 voice-to-voice STT component (§14.3). Currently preparatory — session topology staked out, no inference process yet. Distinct from Phase 17.5 dictation, which is entirely MacBook-resident (§14.1) and does not touch monarch.

**The Jarvis daemon runs in the `control` session** (commit `9858a6a` moved it from `inference`). `HANDOFF_v19.md:114` "runs as a window in the inference tmux session" is stale; this is tracked as audit A13 (§16).

### §4.2 The four execution substrates

| Substrate | Used for | Throughput | Cost shape |
|---|---|---|---|
| GPU (VRAM) | Highest-throughput inference; T1 reasoning, T4 utility, T2/T6 burst | Tok/s dominated by VRAM bandwidth + offload ratio | Fixed; bounded by 24 GB ceiling |
| RAM | Mid-tier inference where GPU unavailable; KV cache backing | Slower than VRAM, faster than disk swap | Effectively free up to 96 GB |
| CPU | T3 content (CPU-only), T5 small helper; fallback when VRAM saturated | Order of magnitude slower than GPU for LLMs | Effectively free up to thermal limits |
| Cloud API | Synthesis (news Stage 4), building/design (Claude Pro), frontier reasoning, throughput overflow | Latency floor higher than local; quality ceiling higher; bounded by quota/budget | Money — surfaced via Tier 3 authority |

The four-substrate model is Jarvis's dispatch matrix. Every workload has a default substrate and a cascade order. Authority Spec (§9.5) gates the cloud step because that's where money enters.

### §4.3 What Path B fixed

Pre-Path-B, `inference-down` ran `tmux kill-session -t inference` which took T1, LiteLLM, validation-gate, lora-dispatcher, and Jarvis with it every time the dataplane needed to cycle. The teardown script then ran a straggler-kill prompt offering to `sudo kill -9` the very services it had just destroyed. The defensive design depended on operator attention at the moment of cycle.

Path B removed the *need* for defense by removing the failure mode. Control-plane services live in a separate session whose lifetime is decoupled from the dataplane's. This is the canonical example of the **redesign-over-refine principle** committed to HANDOFF_v19 (`38b6446`): when a Tier 3 prompt fires repeatedly for the same underlying reason, the right move is sometimes architectural elimination, not tighter criteria.

**Validation evidence (2026-05-21 04:14–04:21 EDT):**
- `tmux move-window` verified safe for a VRAM-resident llama-server. T1 retained its 12 GB VRAM allocation, stayed bound on :8080, passed a coherence test (`OK`) immediately after the move and again after a full dataplane cycle.
- Jarvis daemon writer thread maintained 10s cadence through the session reassignment (mtime 04:15:21 → 04:15:31).
- Full cold cycle: `inference-down` → 12,067 MiB VRAM (T1 + driver + Jarvis only, control intact) → `inference-up` exercised idempotent path (T1/LiteLLM/VG/LD all reported "already serving — skipping launch") → 16,247 MiB back to baseline.

**Operator-side script changes (not in repo):**
- `~/bin/inference-up` — dual-session aware. Creates `control` session if missing (idempotent). Per-service `already_up` port-check guards skip launches for control-plane services already running. Smoke tests still run unconditionally. Zombie-check filters control-session survivors via parent-walk PID→session resolution.
- `~/bin/inference-down` — kills only `inference` session. Surviving GPU processes inspected and reported with tmux affiliation, not killed. No force-kill prompt under any flag.
- `~/bin/t2-up`, `~/bin/t2-down` — already used `TMUX_SESSION="inference"` (T2 is dataplane).

**Repo file changed (commit `9858a6a`):** `deploy.sh` — Jarvis daemon window now created in `${CONTROL_SESSION}` instead of `inference`.

**Backups on disk (operator-side, ignored by git via `*.preB-backup` and `*.zombie-fix-backup` patterns):**
- `~/bin/inference-up.preB-backup`, `~/bin/inference-up.zombie-fix-backup`
- `~/bin/inference-down.preB-backup`
- `~/projects/jarvis/deploy.sh.preB-backup`

Rollback is one `mv` per file.

---

## §5 — Inference Stack (Tier-by-Tier)

**Source of truth for tier configuration:** `jarvis/schema.py` `MONARCH_TIERS` constant. **Last validated:** 2026-05-26 against `schema.py:378-411` and `inference-up.sh:225-303`.

Six tiers in the v19 design. Five live; one (T6) blocked on model download. All are llama.cpp post-v16 (vLLM ruled out for this hardware — see §17).

| Tier | Port | Model | Quant | `context_size` | `-np` | `cpu_only` | `burst_only` | Notes |
|---|---|---|---|---|---|---|---|---|
| T1 | 8080 | Qwen3.6-27B | UD-Q4_K_XL | 24576 | 1 | F | F | Always-on; Jarvis reasoning brain |
| T2 | 8083 | Qwen3.6-27B | UD-Q4_K_XL | 16384 | 1 | F | **T** | Burst-only post-Change-1; `~/bin/t2-up`/`t2-down` |
| T3 | 8084 | Qwen3.6-27B | UD-Q4_K_XL | 8192 | 1 | **T** | F | CPU-only via `CUDA_VISIBLE_DEVICES=` |
| T4 | 8002 | Phi-4-mini | Q4_K_M | 16384 | 4 | F | F | Always-on utility; q8_0 KV cache |
| T5 | 8085 | Qwen3-1.7B | Q5_K_M | 8192 | 1 | **T** | F | CPU-only seed |
| T6 | 8086 | Qwen3.6-35B-A3B | UD-Q4_K_XL | 65536 | 1 | F | F | `enabled=False`; 25% expert offload; model not yet downloaded |

Health endpoints (per `schema.py:413-424` `MONARCH_HEALTH_COMPONENTS`): llama-server-t1..t5 on each tier port, plus `litellm:4000`, `validation-gate:4100`, `lora-dispatcher:4200`, `n8n:5678` (HTTP), `postgres:5432` (TCP).

### §5.1 T1 — Jarvis Reasoning Brain (always-on)

- **Session:** `control` (Path B)
- **Launch:** `-ngl 40 --ctx-size 24576 -np 1` with q8_0 KV (`inference-up.sh:234`)
- **VRAM (measured):** ~11,842 MiB pre-Change-2 at 36K ctx; ~500-800 MiB drop expected at 24K, **measurement pending next natural T1 restart** (Rebalance Change 2; §11.2)
- **Role:** Always-on reasoning brain. Handles operator-facing OpenCode sessions, Jarvis dispatch decisions, and any local reasoning that doesn't need T6's coding specialization.
- **Never shut off** per §3.3. Self-offload to CPU/RAM is the max degradation under VRAM pressure (§10.3).

### §5.2 T2 — Pipeline Burst (burst-only)

- **Session:** `inference` (Path B)
- **Status:** `burst_only=True` in schema; idle-by-default
- **Bring-up:** `~/bin/t2-up` (idempotent, /health wait + port conflict detection; removes `t2_idle_marker` file)
- **Bring-down:** `~/bin/t2-down` (graceful SIGTERM, SIGKILL fallback; writes `t2_idle_marker` file at `/home/monarch/.local/state/inference/t2_idle_marker`)
- **Launch when active:** `-ngl 20 --ctx-size 16384` standard (`inference-up.sh:253`); `-ngl 60 --ctx-size 32768` burst mode
- **VRAM when active:** ~6,832 MiB standard; up to ~17 GB burst-mode with T1 parked
- **Role:** Pipeline-mode bounded synthesis. Post-Decision-4, news Stage 2 routes to DeepSeek V4 Flash via LiteLLM fallback chain by default; T2 is invoked only on explicit `t2-up` for one-off pipeline work.
- **IDLE marker pattern:** `tier_health.py:42` reads marker file presence; when burst tier is unresponsive AND marker exists, listener reports `IDLE` (clean offload) instead of `UNRESPONSIVE` (unexpected failure).

### §5.3 T3 — Content/Batch CPU (always-on, zero VRAM)

- **Session:** `inference` (Path B)
- **Launch:** `CUDA_VISIBLE_DEVICES=` prefix + `-ngl 0 --ctx-size 8192 -t $(nproc)` (`inference-up.sh:270`)
- **VRAM:** 0 (CPU-only). RAM working set ~4 GB.
- **Role:** Slow-but-zero-VRAM-cost content generation, batch jobs, anything where latency doesn't matter. LoRA dispatcher target tier — content/leads/exploratory adapters all served here.

### §5.4 T4 — Utility Phi-4-mini (always-on)

- **Session:** `inference` (Path B)
- **Launch:** `-ngl 99 --ctx-size 16384 -np 4` with q8_0 KV (`inference-up.sh:288`)
- **VRAM:** ~4,179 MiB measured
- **Role:** Fast utility model. Validation gate grading calls (grounding + voice checks) hit T4 directly, not through LiteLLM, to avoid silent cloud fallback on grader work. Also used for classification, light extraction, small-prompt tasks.
- **Engine pivot history (v16):** Originally specced as vLLM. vLLM 0.20.1 silently crashes at FlashAttention V2 initialization on Phi-4-mini fp8 with Ampere SM86 + CUDA 12.8. Pivoted to llama.cpp during first bringup. See §17 (Ruled-Out Pointer).

### §5.5 T5 — Small Helper CPU (always-on, zero VRAM)

- **Session:** `inference` (Path B)
- **Launch:** `CUDA_VISIBLE_DEVICES=` prefix + `--jinja -ngl 0 --ctx-size 8192 -t 4` (`inference-up.sh:302`)
- **VRAM:** 0
- **Role:** Persistent helper for sub-second per-call work. Additional small-model needs spawn `llama-cpp-python` inline within n8n executions rather than running new persistent tiers.

### §5.6 T6 — Coder Burst (planned, not yet downloaded)

- **Session:** `inference` (Path B, when deployed)
- **Status:** Model not yet downloaded (~21 GB pull pending). Spin-up tooling (`~/bin/t6-up`, `~/bin/t6-down`) not yet written.
- **Operating mode (D5 CLOSED 2026-05-26):** Single mode, 50-60% expert offload, targeting ~100 tok/s throughput with `--cache-type-k q8_0`. Actual VRAM footprint pending measurement at download time — projected range ~14-17 GB.
- **Role:** Reserve coder. Primary coding workloads route to Claude Pro ×2 (operator-driven, building/design) and Kimi K2.6 (peer rotation per Decision 4). T6 is the local backup for can't-wait missions, NDA-tagged work where cloud routing is disallowed, or low-level coding tasks where the spin-up cost is acceptable. The ~100 tok/s target reflects this — T6 is not optimized for raw throughput; it is the overflow valve when remote isn't an option.
- **Decision 3 status:** OPEN (§9.3). Spin-up tooling and downloaded model remain blockers; D5 closure resolves the operating-mode question.

### §5.7 mmap weight sharing — the architectural reason five tiers fit

T1, T2, and T3 all load the same Qwen3.6-27B UD-Q4_K_XL GGUF. mmap shares the ~17 GB of weight pages across all three processes — they read from the same kernel page cache rather than each loading their own copy. **This is the single architectural reason five concurrent tiers fit on monarch's 24 GB VRAM ceiling.** Without mmap sharing, T1+T2+T3 alone would consume ~51 GB of weight loads.

This sharing is implicit in llama.cpp's default behavior and is not something the operator configures. It is documented because it is load-bearing: if the inference stack ever moved off llama.cpp to a framework without page-cache sharing, the architecture would need to be redesigned, not just ported.

### §5.8 Measured throughput (v18 baseline)

| Tier | Standard config | Burst config |
|---|---|---|
| T2 | 5.4 tok/s generation | 22.9 tok/s generation (4.2× speedup) |
| T4 (Phi-4-mini) | 206 tok/s generation | n/a — utility tier |

T1, T3, T5 throughput numbers not measured; pending instrumentation.

### §5.9 Resource budget — five-tier combined footprint

**Source:** post-Rebalance-Change-1 measurements 2026-05-20 (§11.1). **Last validated:** 2026-05-26.

| Component | VRAM | Notes |
|---|---|---|
| T1 (-ngl 40, 24K ctx, q8_0 KV, -np 1) | ~11,342 MiB estimated post-Change-2; was 11,842 at 36K | Change 2 measurement pending |
| T4 (-ngl 99, 16K ctx, -np 4, q8_0 KV) | ~4,179 MiB | Measured stable |
| Driver overhead | ~512 MiB | NVIDIA driver + buffers |
| **Standard baseline (T2 idle)** | **~16,521 MiB / 66.0%** | Reproducible across cold cycle |
| T2 burst added (-ngl 20, 16K ctx) | +6,832 MiB | Pipeline mode |
| T6 burst added (planned, 25% offload) | +17,000–19,000 MiB | Would require T2 + T4 down |

Headroom under standard baseline: ~8 GB available. Sufficient for T2 burst with T1 active; insufficient for T6 burst without parking T2 or T4. Three-mode VRAM doctrine (§10) governs reallocation.

---

## §6 — Routing Layer

**Source of truth for routing config:** `~/litellm/config.yaml`. **Source of truth for cascade doctrine:** §9.4 (Decision 4) + §9.5 (Decision 5 Quota Cascade Policy). **Last validated:** 2026-05-26 against `litellm-config.yaml` and `schema.py:413-424`.

### §6.1 LiteLLM as the router

LiteLLM exposes a single OpenAI-compatible endpoint on `:4000` (in the `control` session). Pipelines and agent harnesses call this endpoint; the routing logic decides which tier or cloud provider handles the request, including cascading fallbacks when a target is unavailable, walled, or rate-limited.

**Jarvis-monitored health components (full list per `MONARCH_HEALTH_COMPONENTS` in `schema.py:413-424`):**

| Component | Port | Check | Purpose |
|---|---|---|---|
| llama-server-t1..t5 | 8080, 8083, 8084, 8002, 8085 | HTTP `/health` | Per-tier liveness |
| litellm | 4000 | HTTP `/health/liveliness` | Router |
| validation-gate | 4100 | HTTP `/health` | Decision 4 Phi-4 validation |
| lora-dispatcher | 4200 | HTTP `/health` | LoRA hot-swap dispatch |
| n8n | 5678 | HTTP `/healthz` | Workflow orchestration |
| postgres | 5432 | TCP | News + telemetry + validation data backbone |

### §6.2 Active routes in `litellm-config.yaml`

**Local model_list entries (active):**
- `qwen3.6-consultancy`, `qwen3.6-design`, `qwen3.6-exploratory` → T1 (port 8080); per-session LoRA selection via session wrapper, not by model name
- `qwen3.6-pipeline` → T2 (port 8083); `timeout: 600`
- `qwen3.6-content` → T3 (port 8084); `timeout: 1200`. n8n batch workflows should call `lora-dispatcher:4200/dispatch` instead, since LiteLLM cannot manage adapter swap.
- `phi4-mini` → T4 (port 8002)
- `qwen3-small` → T5 (port 8085)
- `qwen-coder-deep` → port 8081 (manual on-demand only; not in standard bringup)

**Cloud model_list entries (active):**
- `deepseek-v4-flash` → `deepseek/deepseek-v4-flash`, key from `DEEPSEEK_API_KEY`

**Cloud model_list entries (commented out, pending key acquisition):**
- `deepseek-v4-pro`
- `kimi-k2.6` — **Moonshot key missing**; see §16

**Active fallback chains:**
- `qwen3.6-{consultancy,design,exploratory}: ["qwen3.6-pipeline"]` — T1 LoRA models fall through to T2 base if T1 unhealthy
- `qwen3.6-pipeline: ["deepseek-v4-flash"]` — T2 pipeline falls through to cloud
- `qwen3.6-content`, `phi4-mini`, `qwen3-small`, `qwen-coder-deep`: empty (failures surface immediately)

**Router group alias:** `throughput-tier: ["qwen3.6-content"]` (cloud-extended version commented pending Kimi key).

**LiteLLM postgres logging is currently DISABLED** in `general_settings` (`# database_url: DISABLED — LiteLLM internal DB isolation note (see v11)`). Decision 5 Item C2 ratified **Path A** 2026-05-24: separate `litellm_logs` DB on the existing postgres instance with `store_prompts_in_spend_logs=false`. Implementation deferred to `quota.py` build task (see §12.3); rationale in §16.

### §6.3 What goes through LiteLLM vs direct

- **Workloads → LiteLLM:** news Stage 2, pipeline burst calls, n8n workflow tier calls, throughput-tier batch work.
- **Direct (bypasses LiteLLM):** Validation gate grader calls hit T4 (`:8002`) directly. If grader calls went through LiteLLM, fallback chains would silently redirect grader work to cloud when T4 is busy. Direct connection means grader work fails loudly when T4 is down — the correct behavior.

### §6.4 api_keys.env composition

11 keys total in `~/.config/inference/api_keys.env`, all `export`-prefixed (corrected during May 19 session — pre-fix, bare assignment caused silent env-not-inherited failure in subprocess children). Provider coverage: Anthropic, DeepSeek (rotated mid-session for security), Google, FRED, NewsAPI, Finnhub, AlphaVantage, OpenAI (deprecated, kept for legacy reference), HuggingFace.

**Missing:** Moonshot/Kimi key. Tracked in §16.

### §6.5 Validation Gate

FastAPI service on port 4100, in the `control` session.

**Three checks per request:**

1. **Schema** — length bounds, JSON shape (optional jsonschema), required-section heading checks, forbidden-phrase scan. ~1 ms.
2. **Grounding** — Phi-4-mini call. Returns fraction of OUTPUT entities supported by SOURCE. Pass ≥0.90, warn ≥0.75, fail below.
3. **Voice** — Phi-4-mini call. Scores OUTPUT against brand voice profile (`brand_voices/*.yaml`). Pass ≥0.70, warn ≥0.50, fail below.

**Verdicts:** pass → accept. warn → accept + surface. fail → `retry_cloud` (re-run via LiteLLM `deepseek-v4-flash`); second fail → `surface_for_review`.

**Telemetry:** Every `/validate` call writes one row to `validation_telemetry` (Postgres). Joinable on `workflow_id` with `lora_swap_telemetry` (the discipline-layer feature that enables drift detection across the validation + LoRA-swap surface).

### §6.6 LoRA Dispatcher

FastAPI service on port 4200, in the `control` session.

**Pattern:** Workflow-scoped adapter swap on T3. Each n8n execution declares one `workflow_id`; all dispatches in that execution use the same `required_adapter`. Dispatcher swaps the LoRA on T3 maybe 2-3 times per day in steady state.

**Pattern not adopted:** vLLM's punica-style per-request multi-adapter pattern is not available on llama.cpp. For solo-operator session patterns, session-swap is functionally equivalent.

**Current state:** All five planned LoRAs (content, leads, exploratory, consultancy, design) have data sources and rubrics specified in master_summary_v18 §Phase 9. **Zero are trained.** Under Decision 1 reframe, the three high-stakes LoRAs (consultancy, design, exploratory-coding) are likely deferred indefinitely. Content and leads LoRAs remain possible but not in the active queue.

---

## §7 — News Pipeline

**Source of truth:** `~/projects/news-pipeline/CONTEXT.md` on monarch. **Last validated:** 2026-05-26 against bible §7 + master_summary_v19.

### §7.1 Current state (Phase 3 in progress)

- **Phase 1 (schema + ingestion):** COMPLETE 2026-05-15.
- **Phase 2 (cron automation):** COMPLETE 2026-05-15. 2,362+ articles flowing across 9 sectors.
- **Phase 3 (synthesis):** architecture pivoted from n8n synthesis to hybrid T2+Cowork. Stage 2 (local T2 sector synthesis via `synthesis_export.py`) deployed and validated 2026-05-17.
- **Stages 3–5:** rclone sync to Drive (Stage 3), Cowork (Sonnet 4.6) stream compilation + final assembly (Stage 4), brief pickup + ntfy (Stage 5). Not yet built.

### §7.2 Cron schedule

Four news crons (per crontab on monarch — `crontab -l` is canonical):
- Ingestion at 05:15
- Stage 2 synthesis at 05:30
- (Future Stage 3 sync) ~06:00
- Brief pickup at ~06:00–06:15

One full live cron-fired end-to-end run still outstanding as of compile date.

### §7.3 Architecture pivot rationale (v18)

Original n8n HTTP-node synthesis workflows (Stream A / Stream B / final assembly) were never built and are ruled out (§17). Rationale: cross-sector/cross-stream reasoning quality on Qwen3.6-27B is materially weaker than Sonnet 4.6 for institutional synthesis; T2 burst capacity should stay free for financial/Jarvis work; Pro weekly Sonnet budget has ~95% headroom and news consumes ~1-2%. Sector synthesis (bounded summarization, T2's weakness least exposed) stays local; compilation/assembly (high reasoning load) goes to Sonnet via Cowork. Three-tier (T2+Haiku+Sonnet) was evaluated and rejected — Haiku's reasoning load is medium-high not low, the quality hit on the brief's analytical core isn't worth the ~3× saving on a 3-call stage.

### §7.4 Sister project: news-pipeline-evidence

`github.com/trentbentt/news-pipeline-evidence` (public). Monarch working tree at `~/projects/evidence-layer/`. Five invariants (I1-I5) and verdict precedence (REJECTED > QUARANTINED > HEDGED > VERIFIED) implemented at the data-structure level — `Ledger.record()` itself calls `grounding_postcheck` and raises on violation.

Old `~/projects/news-pipeline/` still runs the 06:00 cron — subscribers see that brief, not the evidence-layer output yet. Eleven-step build sequence locked; Phases 1-6 done, Phase 5 signal-class architecture drafted. Cutover scheduled when evidence layer is signal-class-complete.

---

## §8 — Financial Pipeline (Open Strategy Questions)

**Source of truth:** master_summary_v19 §V19E and `FINANCIAL_STRATEGY_v19.md` (proposed, not yet drafted). **Last validated:** 2026-05-26.

Status: design-only. Paper trading not started; circuit-breaker not built. Phase A timing must account for measured T2 throughput (~44 min in burst, ~3.5 hr standard).

Twelve open strategy questions blocking the phase-level design (catalogued in `INFRASTRUCTURE_BIBLE_v19.md` §8.2; carried into this document by reference, not duplicated). The pipeline is correctly identified as gating on strategy, not architecture — the architecture work cannot productively start until the strategy questions are answered.

Tier 1 work in §16 (E1).

---

## §9 — The Six Cardinal Decisions

**Source of truth for closed decisions:** this section. **Last validated:** 2026-05-26 against `DECISIONS_v19.md`, `AUTHORITY_SPEC_v19.md`, and the git log (commits `333884f` through `8c113ea`).

Four closed (1, 4, 5, 6), one open (2), one blocked (3).

### §9.1 Decision 1 — Architectural Reframe (CLOSED 2026-05-19)

**Statement.** Local does data plumbing + agentic glue + on-demand coder burst. Cloud carries synthesis + building/design + frontier reasoning.

**Forcing function.** 94% VRAM baseline. There is no headroom for the alternative. Confirming this collapsed ~10 other open decisions (closed Path 1/2/3, retired three high-stakes LoRAs, retired Cowork as a synthesis stage, confirmed Decision 4 cascade).

**Implications still propagating:**
- T1 is the Jarvis reasoning brain, not the OpenCode harness host.
- T2 is burst-only, not always-on (per Rebalance Change 1).
- The three high-stakes LoRAs (consultancy, design, exploratory-coding) are likely deferred indefinitely.
- Synthesis defaults to cloud — news Stage 2 routes through DeepSeek V4 Flash by default; T2 burst available on operator-triggered exception.

### §9.2 Decision 2 — Hermes Adoption Shape (CLOSED 2026-05-26)

**Statement.** Adopt Nous Research's Hermes Agent (github.com/NousResearch/hermes-agent, v0.3+, MIT, 134k stars) as the agent execution layer in phase 1.5. Pattern B parallel to n8n (no migration of cron workflows); Curator disabled (operator-explicit skill promotion only, no autonomous); Memory→Memory autonomous, Memory→Truth gated under existing Decision 5 N=12 framework; routed via DeepSeek V4 Flash initially (cost discipline).

**Artifact identification.** The v19 framing assumed a bespoke "Hermes layer" that didn't exist on disk. 2026-05-26 audit confirmed absence (audit A7 closes simultaneously): `grep -rni hermes ~/projects/` returns only circular references in INFRASTRUCTURE_BIBLE_v19.md and one news-pipeline SQL comment about the Nous Hermes *model family*. The actual artifact in scope is the Nous Research Hermes *Agent* — a production-mature agent framework with persistent memory, autonomous skill creation, 18-platform messaging gateway, MCP integration, OpenAI-compatible API endpoint, cron scheduler, and Atropos RL training pipeline. Different artifact, same constraints transfer.

**Constraint mapping to artifact.**
- **Pattern B parallel to n8n** → Hermes Agent exposes `/v1/chat/completions` + `/v1/responses` + `/api/jobs`. n8n keeps cron-driven data pipelines (news ingestion, financial data ETL); Hermes handles agent-loop work (research, synthesis, multi-step task execution). No workflow migration.
- **Curator disabled / scoped narrowly** → Hermes ships an autonomous skill grader and consolidation loop (the Curator). Disabled at install. Skill promotion is operator-explicit only — when a vault procedure is stable enough to graduate, the operator explicitly moves it to `~/.hermes/skills/`. No N-uses counter, no autonomous promotion.
- **Memory writes initially disabled** → reframed as Memory→Memory autonomous (Hermes can write to its own MEMORY.md, USER.md, session SQLite, skill files), Memory→Truth gated (Hermes proposing to update the Obsidian vault operator profile or any other Truth-layer artifact requires Tier 3 operator confirmation per Decision 5). Strict cold-start applies: new autonomous Hermes actions enter at Tier 3.
- **Routed via DeepSeek V4 Flash initially** → Hermes default model configuration points at LiteLLM endpoint, model alias `deepseek-v4-flash`. Existing fallback chains apply per §6.2.

**Build commitment.** Phase 1.5, step 4 in the locked sequence (vault init → pgvector → Codebase-Memory MCP → **Hermes Agent** → EverMemOS → Redis). Lands into pre-populated Truth and Index layers so first session has full doctrine context via kepano/obsidian-skills (Steph Ango's official Obsidian skill set, native Hermes integration).

**Memory architecture cross-reference.** Hermes Agent is the L4 (Memory: agent working memory) layer per `MEMORY_ARCHITECTURE_v20.md`. Truth-is-primary rule governs its relationship to L6 (Obsidian vault, operator-authored Truth). Hermes USER.md auto-syncs from a designated vault file; vault wins on conflict.

**Closure simultaneous with audit A7** (Hermes brainstorm absent from disk, confirmed 2026-05-26). §13 below carries the operational detail.

### §9.3 Decision 3 — T6 Operational Defaults (CLOSED 2026-05-26)

**Statement.** Qwen3.6-35B-A3B UD-Q4_K_XL, 64K context, single operating mode: 50-60% expert offload targeting ~100 tok/s throughput with `--cache-type-k q8_0`. Actual VRAM footprint pending measurement at download — projected ~14-17 GB range.

**Role (per Decision 1 + D5 §11.5).** Reserve coder. Primary coding workloads route to Claude Pro ×2 (operator-driven, building/design) and Kimi K2.6 (peer rotation per Decision 4). T6 is the local backup for can't-wait missions, NDA-tagged work where cloud routing is disallowed, or low-level coding tasks where the spin-up cost is acceptable. The ~100 tok/s target reflects this — T6 is not optimized for raw throughput; it is the overflow valve when remote isn't an option.

**Closure path.** The original proposed statement (25% offload, three named modes — comfort / conservative / aggressive) was superseded by D5 §11.5 close. The three-mode framing depended on "parks T1" language under tight VRAM, which conflicts with Hard Constraint #1 (T1 never evicted by anything below it as a first resort; T1 self-offload only via Substrate Pressure Cascade per §10.3). Single mode at 50-60% offload removes the need for mode-switching entirely — the cascade handles VRAM pressure dynamically per §10, evicting T2 (typically idle) and stepping T4 down before T1 is touched.

**Execution items (not doctrinal — tracked in §16.6 E3):**
1. Model not downloaded. ~21 GB pull required.
2. Spin-up tooling not written. `~/bin/t6-up` and `~/bin/t6-down` don't exist yet.
3. First-deploy verification: measured VRAM footprint vs ~14-17 GB projection; cascade arithmetic of §10.1 confirmed against actual numbers.

**Re-open conditions.** Measured T6 footprint at 50-60% offload meaningfully above ~17 GB (would force T4 step-down by default rather than as exception); ~100 tok/s target proves unmet at projected offload ratio (suggests offload ratio needs adjustment); operator preference shifts T6 from reserve to primary coder role (would re-justify higher-throughput tuning).

### §9.4 Decision 4 — Cloud Routing Chain (CLOSED 2026-05-19; amended 2026-05-24 v1 + v2)

**Statement (original 2026-05-19).** Cloud work is routed by task class. Cowork retired as a pipeline stage.

**Amendment v1 (2026-05-24, commit `ec243d6`) — Structural class reframe.** The cascade is not a strict hierarchy. Providers organize by structural class:

| Class | Providers | Cascade role |
|---|---|---|
| Workflow-tier-zero | Claude Pro (×2) | Operator default for building/design. **Not Jarvis-routed; not in Quota Cascade.** Pro auth flows through Claude Code's subscription path, not LiteLLM. |
| Peer rotation | DeepSeek V4 Flash, Kimi K2.6 | Active workhorse pair. Rotate by fullest-peer rule (Quota Cascade Policy, §9.5.4). |
| Emergency rung | Anthropic API direct | Tier 3 per-call invocation. Not in rotation. **Vestigial as of 2026-05-24** — doctrine-forward, not yet wired (operator-confirmed). |

**Amendment v2 (2026-05-24, commit `dd712e3`) — Haiku 4.5 deprecated.** Originally specced as the latency niche class. Pricing parity with DeepSeek V4 Flash at lower capability makes it redundant. Removed from cascade.

**Tie-breaker priority chain (when task class is genuinely ambiguous):** Claude Pro → DeepSeek V4 Flash → Kimi K2.6 → Anthropic API direct. Haiku struck.

**Discipline rules:**
- Two Claude Pro accounts reserved for building/design. Do not burn Pro on synthesis DeepSeek V4 Flash can handle for cents.
- Money-on-line work (live trading, NDA client work) routes to Anthropic API direct — never Pro, never DeepSeek, never Kimi.
- T6 is the overflow valve: triggered when Pro walls, NDA prohibits cloud, or quality demands local coding.

**Re-open conditions:**
- Haiku 4.5: a future provider with a genuinely-distinct latency profile (substantially faster than DeepSeek peer round-trip) re-justifies a latency niche class.
- Pro tier as Jarvis-routed: automated Pro-1 → Pro-2 → T6 failover mechanism is built (covered by Decision 5 Item 6 descope).

### §9.5 Decision 5 — Jarvis Authority Model (CLOSED 2026-05-24)

**Statement.** Jarvis acts within a three-tier authority framework (autonomous-immediate / autonomous-with-log / surface-and-ask), bounded by the four Hard Constraints (§3.3), with promotion governed by empirical thresholds.

**Closure path (all 8 items + Quota Cascade Policy ratified):**

| Item | Closed | Commit |
|---|---|---|
| 1 — Tier 1 autonomous-immediate list | 2026-05-22 | `50692bd` |
| 2 — Tier 2 autonomous-with-log list (per-tier-class restart; latency-band cascade) | 2026-05-22 | `50692bd` |
| 3 — Tier 3 surface-and-ask list (T1 restart; latency cascade failed; Quota Cascade Policy) | 2026-05-22 | `50692bd` |
| 4 — Overnight Workload Window + Hard Constraints | 2026-05-22 | `414d5b2` |
| 5 — Bypass severity ladder + Substrate Pressure Cascade reframe (continuous intensity band) | 2026-05-22 | `f0675da` |
| 6 — Pro tier estimation: **descoped** (Pro is workflow-tier-zero, not Jarvis-routed) | 2026-05-24 | `ec243d6` |
| 7 — Promotion threshold: **N=12**, uniform across both rungs | 2026-05-24 | `ec243d6` (later audit-close `8c113ea` 2026-05-25) |
| 8 — Cold-start rule: strict (no override at introduction; material behavior change re-enters at Tier 3) | 2026-05-24 | `ec243d6` |
| Quota Cascade Policy: 20% / 10% peer rotation; fullest-peer mechanic; drain phase with per-percent notification overlay | 2026-05-24 | `ec243d6` |

#### §9.5.1 The three tiers

**Tier 1 — autonomous-immediate.** Jarvis acts without surfacing. Standard telemetry only.

*Criteria:* reversible · has run successfully ≥ 12 times without correction · does not change user-visible state · costs no money · burns < 100 MiB VRAM.

*Confirmed actions:* rotate internal Jarvis logs (state.json, daemon.log) · compact state.json snapshots · clear tmpfs caches · reconnect flapping Tailscale · restart Jarvis writer thread if deadlock detected (defensive, should not fire under v0.2; revisit on daemon version bump) · prune Jarvis event ring buffer · garbage-collect stale `_tier_last_pid` entries.

**Tier 2 — autonomous-with-log.** Jarvis acts and writes a `jarvis-q events` entry.

*Criteria:* reversible or low-cost-to-reverse · operator might want to know post-hoc · action correct in ≥ 99% of cases · no money, no user-visible blocking change · burns < 1 GB VRAM.

*Confirmed actions (driven by Phase 2 listeners):*

| Trigger (listener · signal) | Action | Notes |
|---|---|---|
| `process.py` · T3/T4/T5 dataplane tier crashed | `tmux kill-window inference:<window>` + `inference-up` idempotent guards | tier_health confirms post-restart |
| `process.py` · T2/T6 burst tier crashed | `t2-up` / `t6-up` (when shipped) | tier_health confirms |
| `process.py` · T1 crashed | **Escalate to Tier 3** — never silent restart | Hard Constraint #4 |
| `process.py` · tier flapping (`restart_count_24h ≥ 3`) | Stop restart loop, demote action to Tier 3 surface | Don't keep restarting broken things |
| `vram.py` · active burst tier idle > 30 min | Call tier down-script (`t2-down` / `t6-down`) | Reclaims VRAM |
| `quota.py` · LiteLLM tier-1 walled (429) | Escalate to tier-2 provider per Decision 4 cascade | Cross-provider behavior governed by Quota Cascade Policy |
| `cron.py` · git repo size > threshold | Schedule `git gc` for next idle window | Reversible |

*Latency-band routing cascade (Tier 2 framing for workload routing):* each workload class has *peak* (ideal target) and *minimum acceptable* (degradation floor) latency markers. Jarvis monitors observed latency and responds along the cascade: in-band → no action; approaching minimum (within ~20%) → consider substrate alternatives; below minimum → escalate per Decision 4 (substrate first, API second); 2× past minimum → Tier 3 surface. VRAM/CPU/RAM thresholds are secondary diagnostics under this framing — used to predict and explain latency drift, not as standalone triggers. **Pause is not in the toolkit.**

Initial workload classes (peak/minimum values deferred to measurement, Scope B): interactive coding (OpenCode → T1) · batch synthesis (news → T2 or cloud cascade) · cron-scheduled jobs (T3 / T4) · real-time voice (Phase 18, future).

**Tier 3 — surface-and-ask.** Jarvis notifies and waits for explicit confirmation.

*Criteria:* costs money · burns significant VRAM (T6 spin-up ≈ 17-19 GB) · affects user-visible workflow · has never run autonomously before (cold-start) · triggers in NDA-tagged context · operator explicitly demoted after regret.

*Two flavors:*
- **Blocking Tier 3** — surface, wait, never proceed without explicit approval. Example: tier flapping (3 restart attempts in 24h) → pause cron.
- **Non-blocking Tier 3** — surface with timer, default-proceed unless operator vetoes. Canonical example: Jarvis self-offload to CPU/RAM under VRAM pressure (120s veto window, §10.3).

*Confirmed actions:*

| Trigger | Action | Why Tier 3 |
|---|---|---|
| Pro walled during interactive session | Spin up T6 | VRAM impact, fan noise, real footprint |
| `process.py` · T1 crashed | Restart T1 with operator confirmation | Hard Constraint #4 |
| Latency cascade failed (workload still ≥ 2× past min after substrate + API attempts exhausted) | Surface for operator decision | Jarvis ran out of autonomous moves |
| `process.py` · tier flapping (5+ restarts in 24h) | Pause cron jobs that target the tier | User-visible workflow change |
| Retire model from local storage | Delete HF cache entry | Irreversible (re-download cost) |
| Any action in overnight window not meeting bypass | Hold and surface at 07:00 | Voice/notification policy |

#### §9.5.2 Action Lifecycle — Cold-Start, Promotion, Demotion

**Cold-start (Item 8, strict).** All new actions begin in Tier 3. **No override at introduction.** Material behavior change to an existing action re-enters at Tier 3 — the changed version must re-prove itself.

**Promotion (Item 7, N=12 uniform).** Promotion threshold is N=12 uniform across both rungs. An action that has fired N=12 times at its current tier without operator correction is eligible for promotion one tier (3→2 or 2→1). Promotion is **proposed by Jarvis**, not automatic — surfaces as a Tier 3 ask: "I've done X 12 times without correction; promote one tier?" Success criterion is "no operator correction," not "no crash." A technically-successful run the operator later flagged as wrong does not count toward the threshold.

**Total cold-start to silent operation:** minimum 24 operator-acknowledged successful runs (12 at Tier 3 + 12 at Tier 2).

**Demotion (immediate).** Any single instance where operator regrets the action triggers demotion to Tier 3. Demotion is logged with reason if provided.

**Future CLI tooling:** `jarvis-q authority promote <action_id>` and `jarvis-q authority demote <action_id>` not yet built.

#### §9.5.3 Overnight Workload Window

**Window (weekday baseline):** 23:00–07:00 America/New_York. Weekend variability deferred.

**Source of truth for window values:** `schema.py:306-307` `OperatorPreferences.overnight_window_start: str = "23:00"`, `overnight_window_end: str = "07:00"`. Field rename from `sleeping_window_*` → `overnight_window_*` and value harmonization 22:30→23:00 / 06:00→07:00 landed in commit `414d5b2` 2026-05-22.

**What the window controls:**
- **Scheduling preference.** Pipelines marked overnight-eligible (news at 05:15 / 05:30 / 06:00; financial Phase A pre-market when wired) target this window. Bound by `cron.py` listener (§12.3, not yet built).
- **Substrate Pressure Cascade self-offload gating.** Conditional self-offload of Jarvis to RAM/CPU is permitted only within this window (§10.3).
- **Notification channel.** Voice TTS and push notifications quieted within the window unless severity ladder bypass applies. Visual notifications still render to `jarvis-q events`.
- **Action tiers unchanged.** The window is a notification and substrate doctrine, not an authority gate. Tier 1/2/3 classification does not change inside or outside the window.

**Working-hours notification policy.** Outside the overnight window — including weekday 9-5 working hours when the operator is away — voice/push notifications fire normally. Operator needs awareness of pipeline state, workflow failures, and outcome events when not at the keyboard.

**Notification Interrupt Conditions (bypass severity ladder).** Events interrupting the operator regardless of window state:

| Event class | Threshold | Rationale |
|---|---|---|
| GPU thermal | temp > 85°C sustained 60s | Hardware damage risk; 3090 throttle at 93°C — 85°C/60s gives operator-in-loop time before thermal throttling |
| Security | fail2ban escalation, SSH breach attempt | Compromise risk; broad framing intentional (operator uses multiple IPs/VPNs) |
| Spend burst | > $5 in < 5 min on any single provider | Runaway agent / budget bleed; prepaid keys + provider-side budget caps make this a "something is wrong" signal |
| RAM exhaustion | RAM free < 500 MiB | Kernel OOM-killer territory; threatens Jarvis daemon survival (Hard Constraint #1) |
| VRAM cascade exhausted | VRAM free < 500 MiB AND Quota Cascade in Tier 3 surface | Substrate Pressure Cascade ran out of moves; operator decision required |
| Power (deferred) | UPS event / power loss | Not yet wired — no UPS monitoring listener in v19. Row preserved as doctrine debt; threshold and trigger to be specified when monitoring exists. |

Queued items batch-surface at window end: Jarvis emits a morning brief at 07:00 default listing all Tier 2 events from overnight and any Tier 3 items held for surface.

#### §9.5.4 Quota Cascade Policy (prepaid model)

Each provider key in the Decision 4 cloud cascade carries a manually-loaded prepaid balance. Once a key's loaded balance is spent, that key is unavailable until the operator manually reloads. There is no auto-recharge, overage billing, or monthly reset. Jarvis treats remaining balance as a hard floor.

**Rotation behavior (peer tier):**

| Remaining balance on active peer | Tier | Action |
|---|---|---|
| ≥ 20% | — | Continue serving from active peer |
| < 20% | Tier 2 | **Rotate** active routing to the peer with more remaining balance. Logged event; no operator surface. |
| < 10% | Tier 2 | **Rotate again** — flip to whichever peer is fuller at the moment of rotation. Logged event; no operator surface. |
| Both peers < 10% | Tier 2 + notification overlay | Drain phase: continue serving from active peer until 0%; switch to other peer and drain to 0%. Per-percent operator notification overlay. |

**Rotation mechanic.** At every threshold cross on the active peer, Jarvis selects the peer with more remaining balance as the new active provider. "Fullest-peer wins" rather than strict alternation — handles the case where one peer was reloaded more recently than the other.

**Drain phase.** Once both peers are below 10%, no further rotation target exists. Jarvis drains the active key to zero, switches to the other peer, drains to zero. Work continues end-to-end; the policy's goal is to maximize prepaid value rather than strand budget. Stopping work to avoid spending balance is itself a cost — pause is not in the toolkit.

**Per-percent notification overlay (drain phase only).** Every whole-percent drop on the active key during drain phase fires an operator notification. Continuous-cadence reload reminder; channel obeys Overnight Workload Window unless severity ladder bypass applies. Work does not stop.

**New authority primitive introduced.** Tier 2 action with a notification overlay — the routing action remains autonomous-with-log; the operator-facing notification rides on top without converting to Tier 3. **Local primitive of the Quota Cascade Policy.** Not elevated to a general AUTHORITY_SPEC primitive (re-open condition: a second action requires the same overlay shape).

### §9.6 Decision 6 — v19 Scope (CLOSED 2026-05-19)

**Statement.** Two subsystems get full phase-level treatment in v19; two are reduced or deferred.

| Subsystem | v19 treatment |
|---|---|
| Jarvis | Full phase-level. v0.2 built; Phase 2 listeners pending; authority spec ratified. |
| Financial pipeline | Full phase-level. Paper-trading harness, backtesting, `macro_signals` and `news_trade_signals` tables, position sizing, risk model. |
| Nexus 17.1 | Design-only. No implementation in v19. |
| 2nd Brain 17.2 | Deferred. No v19 work. |

**Implications (under original 2026-05-19 close):**
- Decision 2 (Hermes): no memory-write story needed for 2nd Brain. Adoption is Pattern B parallel to n8n only. Curator scope decision is narrower as a result.
- Decision 5 (Jarvis authority): no Nexus action rules needed. Authority spec covers Jarvis + financial pipeline action surface only.

**Amendment 2026-05-26 — Scope expansion to memory architecture build.**

Nexus and 2nd Brain move from "design-only / deferred" to **phase 1.5 build targets**. The artifacts are now named: Nexus = Codebase-Memory MCP (Tree-Sitter AST knowledge graph, single C binary + SQLite, MCP-native; arXiv 2603.27277). 2nd Brain = Obsidian vault + kepano/obsidian-skills + pgvector over Postgres. EverMemOS (arXiv 2601.02163) joins as long-horizon temporal memory (L7 per `MEMORY_ARCHITECTURE_v20.md`).

**Driver.** Operator principle locked 2026-05-26: build it right the first time, not "good enough until it breaks." In agentic work the cost of memory failure surfaces as financial loss (trade decisions on stale state, agent procedures diverging from vault notes, code knowledge going stale across L3/L5). The original Decision 6 scope was correct under cost-driven assumptions; under quality-driven assumptions the math inverts.

**What changes:**
- Nexus → Codebase-Memory MCP deployed pointing at `~/projects/`, exposed via MCP to Hermes Agent and Claude Code. Phase 1.5 step 3.
- 2nd Brain → Obsidian vault initialized first thing in phase 1.5. Doctrine (this document, AUTHORITY_SPEC, DECISIONS, REBALANCE, BIBLE_AUDIT, HANDOFF) migrates in immediately. Phase 1.5 step 1.
- EverMemOS → self-hosted with Elasticsearch + Milvus alongside existing Postgres, seeded from vault profile. Phase 1.5 step 5.

**What does not change:**
- Decision 2's Pattern B framing still bounds Hermes (parallel to n8n, no cron migration).
- n8n keeps cron-driven data pipelines (news ingestion, financial data ETL).
- Decision 5's authority model still gates Memory→Truth writes from any memory layer.
- Decision 6 v19 closure (Jarvis + Financial = phase-level scope) remains in force for everything else; this amendment only expands Nexus and 2nd Brain treatment.

**Build sequence** locked: vault init (1) → pgvector enable (2) → Codebase-Memory MCP deploy (3) → Hermes Agent adoption (4) → EverMemOS deploy (5) → Redis with financial pipeline (6).

---

## §10 — VRAM Doctrine + Substrate Pressure Cascade

**Source of truth for cascade ratification:** `AUTHORITY_SPEC_v19.md` §"Substrate Pressure Cascade" (absorbed below; commit `f0675da` 2026-05-22). **Last validated:** 2026-05-26.

### §10.1 Three-mode allocation framework (operational shorthand)

| Mode | When | Allocation shape |
|---|---|---|
| **Standard / Interactive** | Default. Operator at keyboard, OpenCode possibly active, no scheduled pipeline. | All five tiers within VRAM ceiling at modest configs. Pre-Rebalance: 22.9 GB / 95.6%. Post-Change-1: 16.5 GB / 66%. |
| **Burst** | Pipeline workload (news, future financial) running. Time-windowed. Sequential not concurrent. | T1 parked, T2 `-ngl 60` / 32K ctx, T4 unchanged, T3/T5 CPU-only. Measured ~21.5 GB / 87% in v18. With Path B, T1 stays up — burst is additive on top of standard. |
| **Soft** | Specced in v16 but not currently used. T2 standard, T4 reduced. Reserved for special cases. | Not load-bearing. |

These names survive as operational shorthand. The underlying doctrine is now the **continuous intensity band** below; "Standard / Burst / Soft" describes cascade states, not discrete configuration modes.

### §10.2 Core principle: offload-then-hotswap

**Quality of output is non-negotiable. Allocation is negotiable.**

Temporarily reallocate VRAM to run at peak efficiency, complete the work, reallocate back. Swap cost: 30 seconds to 3 minutes. The alternative — permanently shrinking allocations so all tiers coexist at reduced capacity — pays a GIGO tax continuously: small context windows, poor latency, underweight inference producing results that take hours longer and are lower quality. The math never favors the permanent shrink.

**Sequential not concurrent.** Running the news pipeline and then the financial pipeline sequentially in burst mode is faster in aggregate than running both concurrently with T1 up in standard mode. The degraded allocation cancels any parallelism gain.

### §10.3 Substrate Pressure Cascade (continuous intensity band)

**Framing.** Jarvis's response to observed VRAM pressure is a **continuous intensity band**, not a sequential layer ladder. Three response kinds — eviction, conditional self-offload, API routing — blend with scaling intensity as pressure rises. Intensity recalibrates automatically as pressure eases. **Stateless response:** response is a function of *current* observed VRAM free, not past escalation state. No "exit cascade" logic — as VRAM rises (workloads moved, tiers freed, bursts finished), intensity drops to match.

**Intensity band.**

| Free VRAM | Cascade state |
|---|---|
| > 2.5 GB | Normal operation — no cascade activity |
| 2.5 GB → 500 MiB | Active band; offload intensity scales with pressure |
| < 500 MiB | API routing engaged |

The 2.5 / 1.5 / 0.75 / 0.5 GB markers are **intensity guideposts** (how the cascade should feel across the band), not discrete `if VRAM < N` triggers. The `vram.py` constants `_OOM_ELEVATED_THRESHOLD_MB = 2000` and `_OOM_IMMINENT_THRESHOLD_MB = 500` (`vram.py:23-24`) serve as event-emit boundaries within the band; they are not separate decision triggers under the continuous-intensity framing.

**Three response kinds (blend across band):**

**Evict burst and utility tiers** (standard Tier 2 actions). Priority: T2 burst (~6.8 GB, `t2-down`) → T6 burst (~17-19 GB or ~21 GB depending on mode per §5.6, `t6-down`) → T4 reductions within tier operational range. T3 and T5 are CPU-only and contribute zero VRAM — not eviction targets.

**Conditional self-offload (Tier 3 non-blocking).** Jarvis offloads reasoning capacity VRAM → RAM/CPU. Gated by:
- **Inside the Overnight Workload Window.** Self-offload during weekday working hours, when the operator is away but expects notifications and possible interactive use upon return, is the wrong move. Outside the window, self-offload is not in the cascade's available moves.
- **Operator does not veto within 120 seconds.** Self-offload fires as a Tier 3 non-blocking action: Jarvis surfaces ("VRAM pressure persists; offloading T1 to RAM in 120s unless you veto"), then default-proceeds at timeout.

Self-offload floor is Scope B framework: T1 retains operator-interactive capacity. Below this floor, further offload is itself a failure mode. Specific number deferred to measurement.

**Route workloads to API.** Engages at the bottom of the band (< 500 MiB free). Workloads route per Decision 4 cascade, bounded by Quota Cascade Policy (§9.5.4).

### §10.4 API switchover mechanism

Switch at next natural workload checkpoint — token-stream end, batch-item boundary, message-turn end. In-flight GPU work runs to its next checkpoint, then the *next* unit of that workload routes to API. Avoids re-issue/dedup problems from hard-pulling in-flight work.

Under imminent-crash pressure (approaching 500 MiB with no successful checkpoint switchover yet), checkpoint granularity may shorten or be bypassed. Exact escalation behavior deferred to implementation against measured failure modes (Scope B).

Once API is serving the routed workload, observed VRAM free rises and the cascade's intensity automatically recalibrates downward per the stateless-response principle.

### §10.5 Routing constraints

- **Workloads route, the coordinator does not.** Hard Constraint #2. Jarvis identity (daemon, T1, listeners, state) never routes to API.
- **Quota Cascade Policy gates routing depth.** If quota thresholds escalate to Tier 3 mid-cascade, Jarvis surfaces and stops.
- **All routes exhausted → notification interrupt.** "VRAM cascade exhausted" row in §9.5.3 fires when API routing is quota-capped, self-offload is unavailable (outside window) or maxed, and evictions are exhausted.

**Pause is not a step. Jarvis re-routes.**

---

## §11 — Standard Mode Rebalance (Changes 1–3)

**Source of truth:** this section. **Last validated:** 2026-05-26 against commits `c0f7ea7` (Change 2 patch) and `385f893` (baseline reference refresh).

### §11.1 Change 1 — T2 to burst-only (EXECUTED 2026-05-19/20)

- **Schema:** `TierConfig.burst_only: bool = False` (`schema.py:135`); T2 set to `burst_only=True` (`schema.py:388`).
- **Script:** `~/bin/inference-up` patched with `SKIP_BURST_ONLY_TIERS="t2"` (`inference-up.sh:63`). T2 skipped during standard bringup.
- **Operator tooling:** `~/bin/t2-up`, `~/bin/t2-down` written; idempotent; dry-run verified.
- **LiteLLM:** `qwen3.6-pipeline` → `deepseek-v4-flash` fallback wired and tested end-to-end (`litellm-config.yaml:117`).
- **Measured baseline post-Change-1:** **66.0% / 16.5 GB**, validated 2026-05-20 across cold-cycle teardown and rebuild. Reproducible. (Initial measurement read 66.1% on first cycle; refreshed to 66.0% in commit `385f893` 2026-05-24.)
- **Saved vs 94% baseline:** ~6,832 MiB. Larger than the deficit (3,442 MiB to hit 80% target). Even without further changes, baseline is comfortably under target.

### §11.2 Change 2 — T1 ctx 36K → 24K (PATCHED 2026-05-20, measurement pending)

- **Schema:** `MONARCH_TIERS["t1"].context_size` 36864 → 24576 (`schema.py:382`).
- **Script:** `inference-up.sh:234` `--ctx-size 24576`.
- **Commit:** `c0f7ea7` 2026-05-20 22:54 EDT.
- **Status:** patched in code; **measurement pending next natural T1 restart.** T1 is in the `control` session and survived the Path B cold cycle by design — the schema-level patch lands on next reboot or explicit control kill.
- **Expected effect:** ~500-800 MiB drop in T1 VRAM (KV cache scales with ctx size). Baseline estimate ~63-64% / 15.5-16.0 GB.
- **Runtime artifact note:** `state.json:43` currently shows `"context_size": 36864` — this is a stale serialization of the operator-preferences/tier-config block. The schema validation on load would silently use the schema default (24576) for any missing fields, but for existing values pydantic preserves the serialized value. Resolves on cold-cycle daemon restart that re-renders the tier configs.

### §11.3 Change 3 — T4 -np 4 → -np 2 (DRAFTED, NOT EXECUTED)

- **Status:** drafted, pending Change-2 measurement.
- **Rationale:** T4 with `-np 4` supports four concurrent slots; `-np 2` supports two. Validation gate grader calls are sequential per request — concurrency 4 is over-provisioned for current load.
- **Estimated savings:** ~1 GB.
- **Honest call:** likely unnecessary. Post-Change-1 + Change-2, baseline is ~63%. T6 burst at ~17-19 GB stacks on top of standard but doesn't combine with full baseline because T6 burst requires T2 down and may require T1 parked. Change 3 is optional.
- **Trigger to revisit:** if post-Changes-1+2 measurement shows baseline > 70% (i.e., Change 2 only saves ~1 GB instead of ~3 GB) and T6 burst pressure becomes real.

### §11.4 What the rebalance unlocks

- 8 GB of free VRAM at idle for burst windows.
- T6 burst becomes physically possible (vs. "would OOM under standard mode" in v18).
- Phase 2 listeners measure against a stable baseline, not a shifting one.
- "Comfort / conservative / aggressive" modes from Decision 3 become real choices instead of "T6 cannot run."

### §11.5 Headroom disposition decision (D5 CLOSED 2026-05-26)

Measured post-Change-1 baseline 16.5 GB / 66%. Change 2 will free another ~1 GB on measurement. Change 3 deferred. That leaves ~7.5–8.5 GB free at idle.

**Decision.** T1 context is allocated dynamically up to available VRAM — no static ceiling. The Substrate Pressure Cascade (§10.3) manages VRAM pressure by evicting burst tiers (T2 typically idle, T6 burst-only) before T1 is ever touched per Hard Constraint #1. T1 self-offload to RAM/CPU remains the maximum degradation under cascade depth, gated to the overnight window per §10.3. Change 2's 24K patch lands as the post-restart starting point; runtime context is not statically capped. T4 unchanged at `-np 4`. Whisper preload is not a standard-mode baseline item — it is Phase 18 STT infrastructure (§14.3), distinct from Phase 17.5 dictation (MacBook-resident).

**Phase 18 voice layer is the consumer for the headroom.** When voice-to-voice ships (§14.3), monarch hosts a Whisper STT instance (currently the `whisper` tmux session, preparatory) and a TTS counterpart (ChatterBox or equivalent open-source). Combined footprint ~1.5-3 GB VRAM when active, burst-shaped (operator-invoked conversation, not always-on). Comfortable inside the current headroom; does not change the standard baseline.

**T6 single operating mode** (§5.6 updated): 50-60% expert offload targeting ~100 tok/s. Reserve coder — primary coding routes to Claude Pro ×2 and Kimi K2.6; T6 is the local backup for can't-wait, NDA-tagged, or low-level coding missions where remote routing is unsuitable. Actual VRAM footprint pending model download and measurement. T6 burst still requires the cascade to evict T2 and may require T4 to step down depending on measured footprint — the three-mode arithmetic of §10.1 still applies.

**Phase 1.5 RAM-vs-VRAM clarification.** The phase 1.5 commitments per §9.6 amendment (Elasticsearch + Milvus + Redis) consume **RAM, not VRAM**. They do not compete for the ~7.5-8.5 GB VRAM headroom this section discusses. RAM projections handled in §2; remain inside 96 GB ceiling with ~50-52 GB free at idle.

**Re-open conditions.** A measured T6 footprint at 50-60% offload meaningfully different from the ~14-17 GB range projected here; Phase 18 voice layer measured VRAM substantially above 3 GB; introduction of any new always-on workload that would consume baseline headroom.

---

## §12 — Jarvis Substrate (Phase 1 Live, Phase 2 Spec)

**Source of truth for code:** `~/projects/jarvis/jarvis/`. **Last validated:** 2026-05-26 against `schema.py`, `state.py`, `vram.py`, `tier_health.py`, `base.py`.

### §12.1 v0.2 substrate architecture (live)

```
daemon.py           ← main process; starts listeners, persists state.json every 10s
jarvis/
  schema.py         ← Pydantic models — the canonical truth
  state.py          ← thread-safe singleton StateStore; load_from_disk() for CLI
  listeners/
    base.py         ← BaseListener: interval polling, error isolation per thread
    vram.py         ← 5s; nvidia-smi; attributes VRAM to tiers via PID→port→tier
    tier_health.py  ← 15s; HTTP /health polls all service endpoints
bin/
  jarvis-q          ← CLI; reads state.json; subcommands vram/health/tiers/etc.
```

**v0.1 → v0.2 fix:** v0.1 had RLock contention deadlocks that froze listeners after a few minutes. v0.2 uses snapshot semantics (read = lock briefly, deep-copy, release, return copy) and a writer queue (writes pushed as update functions onto a `queue.Queue`, single writer thread drains it). Events use a separate thread-safe ring buffer (`collections.deque`, max 2000). Verified stable across soak.

**StateStore class** (`state.py:62-256`):
- `apply(fn: UpdateFn)` — enqueue an update function for the writer thread (timeout 1.0s, queue max 1000)
- `snapshot()` — deep-copy of current model under brief lock
- `emit(type, severity, ...)` — append an Event to the ring buffer
- `save_to_disk()` — serialize snapshot + recent events to `~/.local/state/jarvis/state.json` via atomic tmp + rename
- `load_from_disk()` — class method, reads + validates state.json (returns None if missing or invalid)

**State file path** (`state.py:46-49`): `~/.local/state/jarvis/state.json` by default; override via env `JARVIS_STATE_PATH`.

**Schema_version** (`schema.py:360`): `"0.1.0"`. No migration logic uses this field yet (§16 small mission).

### §12.2 SystemModel domain layout

**Source:** `schema.py:354-371`. **Nine top-level domains** in the live SystemModel:

| Domain | Class | Purpose |
|---|---|---|
| `hardware` | `Hardware` | Static; calibrated once |
| `tiers` | `Dict[str, Tier]` | Live state per T1–T6 |
| `workloads` | `Workloads` | Active / pending / completed (7-day retention) |
| `schedule` | `Schedule` | 24h forward forecast |
| `quotas` | `Quotas` | Cloud API budgets and burn rates |
| `resources` | `Resources` | Live VRAM / RAM / CPU |
| `operator` | `Operator` | Presence state + preferences (overnight_window_*) |
| `events` | `Events` | Append-only rolling log (24h retention) |
| `health` | `Health` | Per-component health checks |

(The `schema.py:5-13` module docstring says "eight" — this is stale; `operator` was added later. Tracked as audit A12 in §16.)

### §12.3 Phase 1 listeners (live)

**`vram.py`** (`vram.py:92-184`, `interval_sec = 5.0`):
- Polls `nvidia-smi` for total VRAM (`memory.used`, `memory.free`) and per-process VRAM (`pid`, `used_gpu_memory`).
- Resolves PIDs to tiers via `_port_from_cmdline()` — reads `/proc/{pid}/cmdline`, extracts `--port` arg, maps via `PORT_TO_TIER` (`schema.py:427-434`).
- Writes `resources.vram.{used_mb, free_mb, used_by_tier, oom_risk, updated_at}` and `tier.resources.vram_used_mb` per tier.
- Emits `oom_risk_changed` event on state transitions only (state-transition rule; never on every poll).
- OOM thresholds: `_OOM_ELEVATED_THRESHOLD_MB = 2000`, `_OOM_IMMINENT_THRESHOLD_MB = 500` — guideposts within continuous-intensity band (§10.3).

**`tier_health.py`** (`tier_health.py:102-219`, `interval_sec = 15.0`):
- HTTP `/health` (or `/health/liveliness` for LiteLLM, `/healthz` for n8n) per `MONARCH_HEALTH_COMPONENTS`.
- Postgres uses TCP-only check (`_TCP_ONLY = {"postgres"}`).
- Falls back to `/v1/models` on 404.
- IDLE marker pattern (`tier_health.py:42`): file at `/home/monarch/.local/state/inference/t2_idle_marker` written by `t2-down`, removed by `t2-up`. When a `burst_only` tier is unresponsive AND marker exists, listener reports `IDLE` (clean offload) instead of `UNRESPONSIVE` (unexpected failure).
- Writes `health.components`, `health.last_full_sweep`, `tier.runtime.{state, health_status, last_health_check}`.
- Emits `tier_state_change`, `tier_burst_idle_entered`, `tier_health_failed` on transitions only.

**Daemon persist cadence:** state.json written every 10s by daemon (atomic tmp + rename via `state.py:147-158`). The daemon source file is not in this repo bundle; per audit A3, `daemon.py` sets `PERSIST_INTERVAL_SEC = 10`.

### §12.4 Phase 2 listeners (spec only, not built)

**Source of truth for Phase 2 cadences and field schemas:** this section (absorbed from `JARVIS_PHASE2_SPEC.md`). **Build constraints:** every Phase 2 listener inherits `BaseListener` (`base.py:18-59`), defines `name`, `interval_sec`, `poll()`, queues updates via `StateStore.apply()`, emits via `StateStore.emit()` on state transitions only, wraps subprocess calls with hard timeouts (≤ 3s fast probe, ≤ 5s slow probe).

**`process.py` — per-tier process monitoring.** Build first; reuses `vram.py` patterns; smallest scope.

- **Cadence:** 30s.
- **Schema additions to `TierRuntime`:** `pid: Optional[int]`, `rss_mb: int`, `cpu_pct: float`, `uptime_s: int`, `restart_count_24h: int`, `last_restart_ts: Optional[datetime]`.
- **Poll loop:** for each enabled tier, find PID via shared `_port_from_cmdline()` (promote from vram.py to `jarvis/listeners/util.py`), read `/proc/{pid}/status` for `VmRSS`, read `/proc/{pid}/stat` for `starttime` and CPU time; compute CPU% as delta from previous poll. Detect restarts by comparing current PID against `self._tier_last_pid[tier_id]`.
- **Restart event emission:** `tier_restart` (info) if `restart_count_24h ≤ 2`; `tier_restart_flapping` (warning) if `restart_count_24h ≥ 3`. Rolling 24h window cleanup on each poll.
- **Edge cases:** exclude Jarvis daemon by `os.getpid()`; T3/T5 no GPU PID in nvidia-smi (port-based PID discovery mandatory); require 2 consecutive polls with `PID=None` before flagging tier stopped; wrap `/proc` reads in try/except FileNotFoundError.
- **CLI surfacing:** `jarvis-q tiers` row gains `rss`, `cpu%`, `up`, `restarts/24h` columns (yellow ≥3, red ≥5).
- **Drives:** Tier 2 "restart on crash" autonomous actions per §9.5.1.

**`quota.py` — LiteLLM spend & token tracking.** Doctrine-unblocked 2026-05-24; build second.

- **Cadence:** 60s.
- **Logging path:** **Path A ratified 2026-05-24** — separate `litellm_logs` DB on existing postgres instance, `store_prompts_in_spend_logs=false` (cost/token metadata only).
- **Rationale (recovered):** the news-pipeline postgres backs news data + n8n + `validation_telemetry` + `lora_swap_telemetry`, all with explicit per-table operator-managed schema discipline. LiteLLM's auto-migration of ~12-15 `LiteLLM_*` tables on startup would pollute this clean schema, complicate backups, create operational coupling. Separate DB on same instance preserves isolation while enabling structured `spend_logs` queries.
- **`store_prompts_in_spend_logs=false`** because cost tracking needs only metadata (provider, model, tokens, timestamp, cost) — prompt content adds privacy/liability surface (especially against NDA-tagged work via Anthropic direct) for no cost-tracking benefit. Reversible if future need surfaces; un-collecting prompts is not.
- **Implementation specifics deferred to Claude Code build-time** (against monarch postgres state): new dedicated `litellm_user` role (recommended for clean isolation); `LITELLM_DB_URL` in `~/.config/inference/api_keys.env` (separate from shared `DATABASE_URL`); uncomment `database_url` in LiteLLM config and add `store_prompts_in_spend_logs: false` under `general_settings`; one-time `CREATE DATABASE litellm_logs OWNER <role>;`.
- **Schema additions to `CloudQuota`:** `tokens_in_today: int`, `tokens_out_today: int`, `spend_today_usd: float`, `last_call_ts: Optional[datetime]`, `walls_in_window: int`.
- **Reference query:**
  ```sql
  SELECT model, SUM(spend), SUM(prompt_tokens), SUM(completion_tokens),
         MAX(start_time), COUNT(*) FILTER (WHERE response_status = 429)
  FROM spend_logs
  WHERE start_time > NOW() - INTERVAL '24 hours'
  GROUP BY model;
  ```
- **Event emission:** `quota_approaching` (warning) at 80% budget; `quota_exceeded` (critical) at 100%; `rate_limit_hit` (warning) on first 429; `spend_burst` (warning) at >$1/min sustained 5min. State-transition rule applies.
- **CLI surfacing:** `jarvis-q quotas` shows name · provider · period · used/budget · % consumed · walls · last_call. Red ≥100%, yellow ≥80%.
- **Pro descoped** per Decision 5 Item 6. Pro is workflow-tier-zero; Pro auth flows through Claude Code's subscription path, not LiteLLM; Pro requests would not appear in `spend_logs` regardless. Re-open: automated Pro-1 → Pro-2 → T6 failover built.
- **Quota dict state:** `state.py:215-245` initializes 6 `CloudQuota` rows: `claude_pro_1`, `claude_pro_2`, `deepseek_v4_flash` (renamed from `deepseek_v3` in commit `b524bb0` 2026-05-24, audit A6 closed), `kimi_k2_6`, `haiku_4_5`, `anthropic_api_direct`. **The `haiku_4_5` and `anthropic_api_direct` rows remain in code as forward-compatibility hooks despite Decision 4 v2 deprecation/deferral.** Whether to prune them is a §16 open item.

**`cron.py` — schedule reconciliation.** Build last; observability-only.

- **Cadence:** 60s.
- **Schema additions to `Schedule`:** `cron_entries: list[CronJob]`, `missed_runs_24h: list[MissedRun]`, `upcoming_60min: list[ScheduledRun]`, `collisions: list[Collision]`, `stale_entries: list[str]`.
- **Poll loop:** parse `crontab -l` + `/etc/cron.d/`; compute next N runs with `croniter`; cross-reference against per-job log paths (`JOB_LOG_MAP` constant); detect missed runs (scheduled + tolerance < now AND no log entry within tolerance), collisions (next-60-min pairs within 5 min), stale entries (target script doesn't exist).
- **VRAM forecasting (optional, defer if complex):** per-job VRAM cost map; sum projected against current free. Enables "T6 burst at 09:15 won't fit, headroom −2,400 MiB."
- **Event emission:** `cron_missed_run` (warning), `cron_collision_warning` (info), `cron_stale_entry` (warning), `cron_vram_collision_imminent` (warning).
- **CLI surfacing:** `jarvis-q schedule` shows upcoming next 60 min, missed in last 24h, collisions.

### §12.5 Build order + soak discipline

1. **`process.py`** — 2-3 hr active work. No prereqs. **Currently buildable.**
2. **LiteLLM Path A wiring** — folded into `quota.py` build task.
3. **`quota.py`** — 3-4 hr active work. Doctrine-unblocked 2026-05-24.
4. **`cron.py`** — 2-3 hr active work. Last; mostly observability.

Total Phase 2: ~8 hours active work, plus soak verification between each listener.

**Soak discipline (v0.1 lesson).** After each listener lands: (1) restart daemon, verify `ps -T -p $(pgrep -f daemon.py)` shows +1 thread per listener added; (2) wait 5 min, verify `Updated` timestamp in `jarvis-q` views advances on cadence; (3) verify no event spam (`jarvis-q events 50` should not have repeating warnings); (4) only then move to the next listener.

### §12.6 Decision-engine flow (Phase 3, not in v19 scope)

```
[Phase 2 listeners] → [state.json] → [decision engine] → [authority spec gates]
   process.py            ↓                  ↓                      ↓
   quota.py         live signals      "should we act?"       "Tier 1/2/3?"
   cron.py                                  ↓
                                       [act | log | ask]
```

The decision engine itself is not in v19 scope. The substrate is built, the listeners feed it, the authority spec gates it. Engine ships post-Phase-2-listeners, part of v20+ work.

---

## §13 — Hermes Agent (Pattern B)

**Source of truth for doctrinal constraints:** §9.2 (CLOSED 2026-05-26). **Source of truth for memory layer interaction:** `MEMORY_ARCHITECTURE_v20.md`. **Last validated:** 2026-05-26.

### §13.1 Artifact

Nous Research Hermes Agent (`github.com/NousResearch/hermes-agent`), v0.3+, MIT-licensed, ~134k GitHub stars, active production use. Model-agnostic agent framework — works with any OpenAI-compatible endpoint (Claude, Qwen, DeepSeek, local llama.cpp tiers). Ships with:

- **File-backed memory.** `MEMORY.md` (~2,200 char hard cap) and `USER.md` (~1,375 char hard cap) injected into every system prompt. Plus `SOUL.md` for agent identity, plus session SQLite at `~/.hermes/state.db` with FTS5 full-text search.
- **Autonomous skill creation.** Hermes distills reusable `SKILL.md` documents after multi-step task completion. Skills live in `~/.hermes/skills/` and per-project under `~/.opencode/skills/` for cross-agent discovery. 166+ tracked skills in the public catalog (87 bundled + 79 optional via agentskills.io).
- **Curator** (autonomous skill grader and library consolidator). **Disabled on monarch deploy** per Decision 2 closure.
- **Cron scheduler with `/api/jobs` REST API.** Daily reports, nightly backups, weekly audits.
- **Messaging gateway** to 18 platforms (Telegram, Signal, Discord, Slack, WhatsApp, others). Operator-driven enablement.
- **MCP integration.** Native consumption of MCP servers including Codebase-Memory (§16.6 / Phase 1.5 step 3) and Obsidian via kepano/obsidian-skills.
- **OpenAI-compatible endpoint.** `/v1/chat/completions` and `/v1/responses` — plugs directly into existing LiteLLM router.
- **Atropos RL training pipeline.** Agent execution trajectories exported as RL training data. Not in scope for v20 build; documented as future use.

### §13.2 Pattern B partitioning (vs n8n)

| Layer | n8n owns | Hermes owns |
|---|---|---|
| Cron-driven data ETL | News ingestion (05:15), Stage 2 synthesis (05:30), financial data refresh, retention sweeps | None |
| Agent-loop reasoning | Validation gate dispatch, LoRA dispatcher invocation | Research, multi-step synthesis, exploratory analysis, consultancy work, content generation |
| Stateful agent memory | None — n8n is stateless between executions | All memory layers — Hermes is L4 per `MEMORY_ARCHITECTURE_v20.md` |
| Operator-facing messaging | ntfy.sh for system events | 18-platform messaging gateway for agent conversations |

No workflow migration. n8n continues exactly as today. Hermes joins as a peer service.

### §13.3 Memory architecture role

Hermes Agent is the **L4 (Memory: agent working memory)** layer per the four-layer architecture. Concrete contents:

- `MEMORY.md` — short-term agent context, autonomously maintained, token-capped
- `USER.md` — operator preferences cache, **auto-synced from `<vault>/operator.md`** (L6 is Truth)
- `~/.hermes/skills/` — stable reusable procedures (Truth for skills, primary-author = operator-explicit promotion from vault notes)
- `~/.hermes/state.db` — session conversation history, FTS5 searchable
- External providers (Honcho, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory, OpenViking) — all disabled at install; only enabled if a specific future need justifies one

### §13.4 Authority model interaction

All Hermes autonomous writes fall under existing Decision 5 N=12 framework:

| Write target | Authority tier | Rationale |
|---|---|---|
| `MEMORY.md`, `USER.md` (Memory→Memory) | Tier 1 once promoted from cold-start; Tier 3 initially per strict cold-start | Token-capped, reversible, Memory layer only |
| Session SQLite writes | Tier 1 | Append-only conversation log |
| Skill creation (`SKILL.md`) | **Tier 3 always** — operator-explicit promotion only; Curator disabled | Skill becomes Truth (executable procedure); promotion is doctrine-grade decision |
| Vault writes (Memory→Truth) | **Tier 3 always** | L6 vault is Truth; agent-proposed vault edits require operator confirmation |
| External provider sync | Disabled by default | Each provider re-enabled requires its own doctrine decision |

### §13.5 Build sequence

Phase 1.5 step 4, after vault initialization, pgvector enable, and Codebase-Memory MCP deploy. Adoption command and configuration specifics handled by Claude Code against monarch state at build time. Configuration constraints (Curator disabled, default model = DeepSeek V4 Flash via LiteLLM, kepano/obsidian-skills installed pointing at vault, external memory providers all off) baked into deploy script before first Hermes session starts.

### §13.6 Open items deferred to build

- Skill promotion ritual (operator command + commit pattern when promoting vault note → Hermes skill)
- Telegram / Signal gateway enablement decision per platform
- Atropos RL pipeline scope (future, not v20)

---

## §14 — Voice Layers

**Source of truth for Phase 17.5:** `~/projects/voice-dictation/` on MacBook (CLAUDE.md + CONTEXT.md). **Source of truth for Phase 18:** this section + master_summary_v19 §Phase 18 (carried by reference). **Last validated:** 2026-05-26.

### §14.1 Phase 17.5 — MacBook voice-to-text input (LIVE since 2026-05-17)

Hands-free dictation system: wake word "Okay Comrade" → mlx-whisper-large-v3-turbo STT → Hammerspoon paste/submit, end word "You May Begin". Fully functional on M2 MacBook Pro 8GB. Drives OpenCode / Claude Code / Claude Pro browser sessions hands-free.

**Architecture:** OpenWakeWord wake/end models → sounddevice capture → Silero VAD → mlx-whisper STT → Hammerspoon paste+submit. Auto-submit when front app is in allowlist (browsers + terminals + Claude desktop). Daemon under launchd, JLab Go Air Pop ANC double-tap fallback for noisy/silent moments.

**Engine pivot history (v18):** Originally Porcupine. Picovoice Console signup blocked on company-email requirement during the build session — GitHub OAuth attempts returned "unable to sign in, go back to sign up." Pivoted to OpenWakeWord (Apache-2.0, models trained via Outspoken at €1/model, no API key). Porcupine is ruled out for new builds in this build window (§17).

**Whisper model selection:** `whisper-large-v3-turbo`, not `large-v3`. First bringup on 8 GB unified RAM showed heavy swap pressure — `large-v3` would consume ~2 GB RAM resident. Turbo runs at ~800 MB RAM, ~1.5 GB disk. Accuracy delta imperceptible for short-burst dictation. When monarch is online and SSH-streaming becomes viable, the model can upgrade back to large-v3 served from monarch's 96 GB RAM (independent of Jarvis — just where Whisper inference runs).

**Five tuning lessons captured during bringup:**
1. Audio scaling — OWW expects int16-range float32, not [-1, 1] float32 (returned 0.003 instead of 0.98 before scaling added).
2. VAD frame size — Silero requires 512-sample frames, OWW requires 1280; inner loop splits OWW chunks into VAD sub-chunks.
3. Retrigger cooldown — set immediately at `start_recording` entry, not at delivery.
4. Wake threshold raised 0.55 → 0.75 to reject music false-fires.
5. Model `.reset()` after each take to clear OWW sliding-window state.

**Hardware fallback resilience:** capture device re-resolved at every `start_recording()` call. Three-layer fallback: JLab → MacBook → system default. JLab battery death or disconnect mid-session recovered transparently with no daemon restart.

**Hammerspoon `hs.ipc.cliInstall()` regression** on current Hammerspoon build: returns `false`. Manual symlink works but IPC handshake fails. Daemon falls back to `pbcopy + osascript keystroke` for delivery (requires Accessibility permission for Terminal). Fully functional; the `hs` CLI path is a "nice to have" that buys the front-app allowlist gate. Tracked as minor open item.

### §14.2 Explicit non-overlap with Phase 18 Jarvis

**This subsystem is a sister voice system to Phase 18 Jarvis, not a prerequisite or input layer for it.**

- **Jarvis is voice-to-voice for system observation.** Audio out to operator's ears, monarch-resident, surfaces system observation.
- **Phase 17.5 is voice-to-text for agent input.** Paste keystroke into agent input fields, MacBook-resident, drives OpenCode / Claude Code / Claude Pro browser sessions.

They share **only the physical microphone**. The wake words must be distinct ("Okay Comrade" is taken by Phase 17.5; Jarvis's wake word TBD but will not collide). Intent classifiers are independent. Sharing a single mic listener at runtime is a future optimization, not a current requirement — both can run side-by-side on M2 hardware.

### §14.3 Phase 18 — Jarvis voice-to-voice (DEFERRED behind Phase 2 listeners)

**Status:** design complete, build deferred. The supervisor responsibilities that v17/v18 specced as the Phase 18 burst-mode supervisor have been **generalized in §9.5 / §10.3 into the Substrate Pressure Cascade plus the latency-band routing cascade** — those doctrines now own the role. Phase 18 voice surface remains the next operator-touch surface but is no longer the next major build target; the Phase 2 listeners are.

**Architecture.** Two halves running on monarch when active:
- **STT (speech-to-text):** Whisper instance in the `whisper` tmux session on monarch (currently preparatory; see §4.1). GPU-accelerated, ~500 MB-1 GB VRAM when loaded.
- **TTS (text-to-speech):** Candidate is ChatterBox (Resemble AI, Apache 2.0, released April 2025) — emotion-controllable, natural prosody, CUDA-native, fits the RTX 3090 profile at ~1-2 GB VRAM. Alternative open-source TTS layers may displace this when Phase 18 build starts; ChatterBox is the doctrinal placeholder, not a hard commitment.

Combined footprint ~1.5-3 GB VRAM when active. Burst-shaped: operator-invoked conversation, not always-on inference. Comfortable inside current standard-mode headroom per D5 (§11.5).

**Value proposition.** Conversational access to Jarvis's full understanding of the codebase (L5 Codebase-Memory MCP), doctrine (L6 vault), live system state (Phase 1+2 listeners), git history, and agent procedures (L4 Hermes skills) — without the operator needing to jump into the weeds of files. Jarvis already holds the structural knowledge; the voice surface makes it conversationally accessible. Maps to the §3.2 architectural test question four ("Can Jarvis explain it?") and the §3.1 documentation router role.

**Build sequencing:** after Phase 2 listeners complete, after Decision 5 listener implementations land, after Phase 17.5 lessons inform the engineering plan. Phase 17.5 and Phase 18 share only the physical microphone — wake words and intent classifiers are independent per §14.2.

---

## §15 — Documentation Layer + Reading Order

**Source of truth:** §0.2 (doc set + roles). **Last validated:** 2026-05-26.

### §15.1 The v20 doctrine surface

Per §0, four documents carry live doctrine after v20:

1. **`master_summary_v20.md`** (this file) — single source of truth for the stack as a whole.
2. **`MEMORY_ARCHITECTURE_v20.md`** — single source of truth for the four-layer memory architecture (Truth / Index / Memory / Arbiter). Parallels AUTHORITY_SPEC's role in v19; cross-referenced from §3, §9.2, §9.6, §13 of this document.
3. **`BIBLE_AUDIT_findings.md`** — drift tracker; append-only between v20 revisions.
4. **`HANDOFF_v19.md`** — session log; end-of-session ritual.

Plus the lean per-project entry points (`CLAUDE.md`, `CONSTITUTION.md`, `CONTEXT.md` per §0.3) and the code/scripts/config files that are themselves source-of-truth for runtime behavior.

The following are **superseded by v20** and archived (not deleted) for historical reference:
- `INFRASTRUCTURE_BIBLE_v19.md`
- `AUTHORITY_SPEC_v19.md`
- `DECISIONS_v19.md`
- `REBALANCE_v19.md`
- `JARVIS_PHASE2_SPEC.md`
- `master_summary_v19.md`
- `README.md` (v19 jarvis repo README — replaced by a shorter README that points to v20)

### §15.2 Reading order (one canonical sequence with sub-orderings)

Different orientation purposes need different reading orders. Below is the consolidated list; pick the section that matches the purpose.

**§15.2.1 Five-minute orientation (returning operator, new session start):**

1. `tmux ls` on monarch — verify `control` + `inference` + `whisper` sessions.
2. `git -C ~/projects/jarvis log --oneline | head -10` — verify recent commits match expected.
3. `jarvis-q health` — verify all tiers OK or IDLE for burst-only.
4. `jarvis-q vram` — verify baseline ~66% / ~16.5 GB.
5. This document's §3 (What Jarvis Is) and §9 (Cardinals status).

**§15.2.2 Thirty-minute deep read (new contributor, returning after a break):**

1. `HANDOFF_v19.md` — most current operational state.
2. This document, top to bottom (skim §1–§4 if returning; read §9, §10, §16 in full).
3. `BIBLE_AUDIT_findings.md` — known drift, what's open, what's resolved.

**§15.2.3 Before any operational change:**

1. Re-read the relevant section of this document.
2. Verify state on monarch — don't trust this document over disk.
3. Check §16 (open items) for related context.
4. Check §17 (ruled-out pointer) for "we already tried this."
5. Then act.

**§15.2.4 Before any doctrine change:**

1. Surface the relevant prior thinking (chat logs, prior session brainstorms if applicable).
2. Confirm cardinal-decision implications (§9).
3. Write the change down as a patch to this document, not as chat conversation.
4. Commit the doctrine change and the code change atomically (§0.1 rule 4).
5. If the change supersedes a closed audit item, annotate in `BIBLE_AUDIT_findings.md` §F.

### §15.3 Truth hierarchy (carried forward from v19)

> monarch disk > git log on monarch > `jarvis-q all` > github.com (raw) > this document > any chat history

When this document and disk disagree, disk wins. This document is the snapshot; the system keeps moving.

**Calibration lessons (kept for forward sessions):**
- GitHub web view via `web_fetch` can return stale-cached content. Treat GitHub web as closer to chat history in trustworthiness than to disk truth.
- Use `raw.githubusercontent.com` rather than the HTML view — different infrastructure, less stale-cache risk, returns raw file bytes.
- For any future repo audit, verify against monarch disk first; github raw second; never trust the HTML render alone.

### §15.4 Memory layers

- **Doctrine layer (this document + audit + HANDOFF):** human-curated, deliberate. Update via end-of-session `/wrap` discipline.
- **claude-mem plugin (Claude Code only):** automatic, granular SQLite-backed observation log. Captures every tool use, decision, file touched. Searchable. Not curated.

The two layers are complementary. Doctrine answers "what phase are we in, what's blocked"; claude-mem answers "what did we actually do last Tuesday." **OpenCode does not have claude-mem.** For OpenCode sessions, CONSTITUTION.md + CONTEXT.md are the complete context system. The `/wrap` discipline is the only safety net.

---

## §16 — Consolidated Open Items

**This is the single open-queue source of truth.** Replaces the five scattered lists across v19: `INFRASTRUCTURE_BIBLE_v19.md` §18 (Tier A-E queue), `INFRASTRUCTURE_BIBLE_v19.md` §19 (small missions), `BIBLE_AUDIT_findings.md` §F2 ("still open"), `DECISIONS_v19.md` "What Remains Open", `master_summary_v19.md` "Open Items — v19". One table per purpose; every row has priority, source-of-truth file, and either a closing commit or an explicit owner.

### §16.1 Open audit items (drift between doctrine and code/runtime)

| ID | Item | Source-of-truth file | Status | Owner / next action |
|---|---|---|---|---|
| A3 | `CLAUDE.md` stale: claims "v0.1", "30s persist", `inference` session for daemon, T1 36K ctx, references retired `inference-burst-up/down` | `~/projects/jarvis/CLAUDE.md` | OPEN | Doc cleanup — single commit rewriting CLAUDE.md against current code (`schema.py`, `state.py`, `deploy.sh`). 30 min. |
| A5 | `schema_version = "0.1.0"` field exists in `SystemModel`; no migration logic uses it | `schema.py:360` | ✅ RESOLVED 2026-05-26 (D4) | Label-only doctrine ratified; cold-cycle is the migration strategy. Comment added in `schema.py` making this explicit. |
| A7 | v18 Hermes brainstorm may not exist as discrete artifacts | n/a (artifact-existence question) | ✅ RESOLVED 2026-05-26 | Confirmed absent on disk via `grep -rni hermes ~/projects/` and `find ~ -name '*hermes*'`. Decision 2 closed simultaneously against actual Nous Research Hermes Agent artifact (§9.2). |
| A12 | `SystemModel` docstring says 8 domains; actual class has 9 (`operator` added) | `schema.py:5-13` docstring vs `schema.py:354-371` class | OPEN | Cosmetic schema docstring fix. 5 min. |
| A13 | `HANDOFF_v19.md:114` says daemon runs in `inference` session; deploy.sh and Path B put it in `control` | `HANDOFF_v19.md:114` | OPEN | Doc cleanup; one-line edit in HANDOFF. 2 min. |
| **NEW-v20-1** | **`state.json` runtime stickiness — orphan `deepseek_v3` key persists alongside `deepseek_v4_flash` after rename** | `state.py:215-245` (code) vs `state.json:304` (runtime) | ✅ RESOLVED 2026-05-26 (D1) | Path (a) implemented: `load_from_disk()` now prunes orphan keys + hydrates missing canonical keys, with INFO-level logging. Live state.json cleaned of `deepseek_v3` and `haiku_4_5` orphans; missing `deepseek_v4_flash` hydrated. |
| **NEW-v20-2** | **`state.json` runtime stickiness — `sleeping_window_*` field names + values persist after `overnight_window_*` rename** | `schema.py:306-307` (code) vs `state.json:414-415` (runtime) | ✅ RESOLVED 2026-05-26 | Confirmed self-healing via Pydantic v2 `extra="ignore"` default — `OperatorPreferences` loads `overnight_window_*` correctly from schema defaults despite stale `sleeping_window_*` keys in state.json. No code change required. |
| **NEW-v20-3** | **`state.json` runtime stickiness — T1 `context_size: 36864` persists after Rebalance Change 2 patch** | `schema.py:382` (code, 24576) vs `state.json:43` (runtime, 36864) | OPEN — same root cause | Resolves naturally on next T1 restart per §11.2. The state.json runtime field is overwritten by the listeners that read live tier config; this is the only one of the three "runtime stickiness" cases that self-heals. |
| **NEW-v20-4** | **`schema.py:357` SystemModel docstring says state.json written "every 30s by the daemon"; actual is 10s** | `schema.py:357` vs `daemon.py PERSIST_INTERVAL_SEC = 10` (per audit A3) | OPEN | Same edit as A3. Group with CLAUDE.md cleanup. 1 min. |
| **NEW-v20-5** | **`inference-up.sh:282` inline comment says "T4 ... 4K ctx"; actual launch is 16K (`:288`)** | `inference-up.sh:282` vs `inference-up.sh:288` | OPEN | One-line comment fix. 1 min. |
| **NEW-v20-6** | **`Health.sweep_interval_sec: int = 30` field in `schema.py:349` is unused; `tier_health.py:104` hardcodes `15.0`** | `schema.py:349` vs `tier_health.py:104` | ✅ RESOLVED 2026-05-26 (D2) | Field stripped from `schema.py`. Listener class-attribute cadence is the canonical pattern (vram.py, tier_health.py, future process.py/quota.py/cron.py all follow). |

### §16.2 Open decisions

| # | Decision | Status | Blocked on |
|---|---|---|---|
| D2 | Hermes adoption shape | ✅ CLOSED 2026-05-26 | Reframed against Nous Research Hermes Agent artifact. Audit A7 closed simultaneously. See §9.2. |
| D3 | T6 operational defaults | ✅ CLOSED 2026-05-26 | Operating mode resolved by D5 §11.5 closure. Execution items (model download + spin-up tooling) moved to §16.6 E3. See §9.3. |

### §16.3 Rebalance state

| Change | Status | Source-of-truth |
|---|---|---|
| R1 — T2 burst-only | EXECUTED 2026-05-19/20; baseline 66.0% measured | `schema.py:388` `burst_only=True`; `inference-up.sh:63` `SKIP_BURST_ONLY_TIERS="t2"`; commit landed |
| R2 — T1 ctx 36K → 24K | PATCHED 2026-05-20 (commit `c0f7ea7`); **measurement pending next natural T1 restart** | `schema.py:382` `context_size=24576`; `inference-up.sh:234` `--ctx-size 24576` |
| R3 — T4 `-np 4 → -np 2` | DRAFTED, not executed; likely unnecessary post-R2 | §11.3 |

### §16.4 Phase 2 listeners (build queue)

| # | Listener | Status | Prereq | Time |
|---|---|---|---|---|
| L1 | `process.py` | spec-only (§12.4) | None | 2-3 hr |
| L2 | `quota.py` | spec-only (§12.4); LiteLLM Path A wiring absorbed | provider rows decision (open item NEW-v20-7 below) | 3-4 hr |
| L3 | `cron.py` | spec-only (§12.4) | None | 2-3 hr |

**NEW-v20-7 — Quota dict provider rows decision.** ✅ RESOLVED 2026-05-26 (D3). `haiku_4_5` pruned entirely (re-open condition: a new provider fills the latency niche, which will have a different model name). `anthropic_api_direct` kept with inline comment annotating it as vestigial — emergency rung for NDA / money-on-line work per Decision 4 v2, not yet wired through LiteLLM. Fresh-build cold-start now produces exactly 5 quota rows: `claude_pro_1`, `claude_pro_2`, `deepseek_v4_flash`, `kimi_k2_6`, `anthropic_api_direct`.

### §16.5 Documentation cleanup

| # | Item | Where | Time |
|---|---|---|---|
| C1 | `~/projects/jarvis/CLAUDE.md` rewrite per A3 + NEW-v20-4 | jarvis repo | 30 min |
| C2 | `~/projects/jarvis/README.md` v20-aware rewrite (replace doc-set table with pointer to §0.2; remove the v19-era doc-set list inherited from old `INFRASTRUCTURE_BIBLE_v19.md` §17.2) | jarvis repo | 15 min |
| C3 | `ref-blueprint §Phase 15` rewrite (flagged stale by CONTEXT.md, carried since v18) | news-pipeline repo | 30 min |
| C4 | Per-stack `CONTEXT.md` updates — six project repos (consultancy, content, design, financial, leads, exploratory-coding) | six project repos | 1-2 hr total |
| C5 | Single-line fixes per NEW-v20-5, A12, A13 | various | 10 min total |

### §16.6 Larger workstreams (Tier E)

| # | Workstream | Status |
|---|---|---|
| E1 | Financial pipeline strategy doc + phase-level design | `FINANCIAL_STRATEGY_v19.md` proposed; answer §8 strategy questions first |
| E2 | Hermes / Pattern B implementation | After D2 |
| E3 | T6 spin-up tooling + first-deploy VRAM verification | After model download (~21 GB). Doctrine complete per D3/D5 close 2026-05-26; first deploy verifies measured footprint vs ~14-17 GB projection and cascade arithmetic of §10.1. R2 measurement independent (T1 context savings) — not a T6 prereq. |
| E4 | Nexus 17.1 design phase | Per Decision 6, design-only in v19 |
| E5 | LoRA training (content + leads only; three high-stakes deferred per Decision 1) | Validation gate live + ≥1 week telemetry baseline |
| E6 | Improvement ledger service | Validation gate live |
| E7 | 2nd Brain 17.2 design | After Nexus operational |
| E8 | News-pipeline-evidence — complete 11-step build sequence | Phases 1-6 done; Phase 5 signal-class architecture drafted |
| E9 | News-pipeline-evidence — cutover from old `~/projects/news-pipeline/` | When evidence layer is signal-class-complete |
| E10 | News-pipeline-evidence — LoRA as reasoning adjudicator (downgrade-only: VERIFIED → HEDGED, never reverse) | Designed; awaiting build slot |
| E11 | Phase 18 Jarvis voice-to-voice | After Phase 2 listeners + decision engine |
| E12 | Command Center PWA (Phase 19) | After Jarvis Phase 18 |

**Phase 1.5 — Memory architecture build (NEW 2026-05-26, locked order):**

| # | Step | Status | Prereq |
|---|---|---|---|
| P1.5-1 | Initialize Obsidian vault; migrate doctrine (v20, AUTHORITY_SPEC, DECISIONS, REBALANCE, BIBLE_AUDIT, HANDOFF) | Pending Claude Code | `MEMORY_ARCHITECTURE_v20.md` doctrine doc written |
| P1.5-2 | Enable pgvector extension on existing Postgres | Pending Claude Code | P1.5-1 |
| P1.5-3 | Deploy Codebase-Memory MCP (single C binary + SQLite); point at `~/projects/`; expose via MCP | Pending Claude Code | P1.5-2 |
| P1.5-4 | Install Hermes Agent v0.3+ with Curator disabled, DeepSeek V4 Flash default, kepano/obsidian-skills, external memory providers off | Pending Claude Code | P1.5-3 |
| P1.5-5 | Deploy EverMemOS self-hosted (Elasticsearch + Milvus alongside Postgres); seed user profile from vault | Pending Claude Code | P1.5-4 |
| P1.5-6 | Redis for hot operational state (L1) | Pending — joins with financial pipeline | E1 (financial strategy doc) |

### §16.7 Small missions (operational residue, deferred but tracked)

| # | Item | Surfaced | Disposition |
|---|---|---|---|
| M1 | Throughput-tier Decision 4 ambiguity (financial + leads `opencode.jsonc` consumers) | 2026-05-19 | Defer — own session with D2 |
| M2 | No Moonshot/Kimi key in `api_keys.env` (peer-rotation rung half-wired) | 2026-05-19 | Decide — acquire key or amend Decision 4 cascade |
| M3 | LiteLLM startup warning `Key 'request_timeout' is not a valid argument` | 2026-05-19 | Cleanup — drop the line in next config edit |
| M4 | `pkill -f "litellm --config"` kills bash wrapper AND child, collapses tmux window | 2026-05-19 | Bank — operator lesson; use targeted SIGTERM patterns |
| M5 | Daemon zombie risk (old PID 229297 survived restarts) | 2026-05-19 | Bank — every restart should `ps aux \| grep daemon.py` first |
| M6 | T2 baseline VRAM drift ~130 MiB across multi-day uptime (KV cache accumulation) | 2026-05-19, 2026-05-21 | Bank — possible "nightly restart" hygiene play |
| M7 | DeepSeek V4 Flash `reasoning_tokens` count separately from content (affects cost accounting) | 2026-05-19 | Update — `quota.py` spec needs `reasoning_tokens` field |
| M8 | `~/bin/` infrastructure not version controlled (inference-up, t2-up, t2-down, news-* all live outside repo) | 2026-05-19, 2026-05-21 | Decide — subdirectory mirror, separate repo, or accept |
| M9 | Pre-Path-B "baseline VRAM is high" warning text in inference-up | 2026-05-21 | Cosmetic |
| M10 | LiteLLM "→ Tier 2" comment in inference-up exercises DeepSeek fallback now | 2026-05-21 | Cosmetic |
| M11 | News pipeline output quality investigation (4 sectors stub-level, 4 sources degraded) | 2026-05-21 | Separate Claude account handling |
| M12 | VRAM ghost reconciliation between nvidia-smi and Jarvis attribution | various | Cosmetic |
| M13 | `TierState.UNKNOWN if False else TierState.STOPPED` dead-code in `schema.py:138` | various | Cosmetic — strip the conditional |
| M14 | Per-tier latency floors not measured (Scope B framework adopted, numbers pending) | 2026-05-21 | Phase 2 listener territory |
| M15 | Validation gate calibration — `VOICE_PASS_THRESHOLD=0.70`, `GROUNDING_PASS_THRESHOLD=0.90` are conservative starting points needing 1 week live traffic to tune | v14-era | Long-term |
| M16 | Working-directory enforcement (no agent writes outside scope) — designed v14, not enforced by harness | v14-era | Open; becomes load-bearing with Nexus |
| M17 | Quarterly CUDA pin verification SOP | 2026-05-16 | Operational discipline; calendar reminder |
| M18 | n8n encryption key rotation cadence | n/a | Bank — no documented policy |
| M19 | D3's original "parks T1" / three-mode framing inadvertently conflicted with Hard Constraint #1 (T1 never evicted by anything below as first resort). Caught at doctrine-vs-doctrine cross-reference walk during D5 close, not at execution. | 2026-05-26 | Method note — when closing a cardinal that affects a tier's allocation, walk Hard Constraints + Substrate Pressure Cascade as a cross-reference check before drafting the closure statement. Doctrine layer caught it; execution layer would have caught it later and more expensively. |

### §16.8 Gaps this document does not authoritatively cover

Honest about scope. Things v20 does not source-of-truth:

1. **Specific cron schedules.** §7.2 names the news crons; canonical source is `crontab -l` on monarch.
2. **All LiteLLM model_group_aliases.** §6.2 covers the active ones; canonical source is `~/litellm/config.yaml`.
3. **All n8n workflow IDs.** Canonical source is n8n's database.
4. **The improvement ledger schema.** Intent in `master_summary_v18.md` §17.4 (legacy doc, archived); schema not yet specced.
5. **Hermes architectural detail.** Decision 2 open; detail blocked on A7.
6. **2nd Brain schema.** Deferred per Decision 6.
7. **Per-LoRA training data inventory.** master_summary_v18 §Phase 9 mentions sources; corpora not enumerated.
8. **Backup/disaster recovery posture.** Postgres backup cron exists (verified 2026-05-14, 79 tables restored clean in drill); GitHub for code. No documented discipline for `state.json`, `validation_telemetry`, `news_unified`, or other Postgres state beyond the existing backup cron.
9. **Tailscale Funnel configuration.** Topology and ACLs not detailed here.
10. **API key rotation cadence.** No documented policy. DeepSeek rotated mid-session 2026-05-19 for hygiene; nothing schedules this.
11. **OS-level service hygiene.** Docker (Postgres + n8n), Tailscale, other system daemons. Not covered.
12. **Hardware health monitoring.** GPU thermal, fan curves, disk SMART, RAM ECC. Not currently in Jarvis observability.

These are gaps to fill over time, not failures. They're listed so future-self knows what isn't here.

---

## §17 — Ruled-Out Pointer

**Source of truth:** `master_summary_v19.md` Appendix A (final document table, lines ~6260-6280). Carried forward by reference; not duplicated here.

Selected entries relevant to v19/v20 decisions:

- **vLLM on Phi-4-mini fp8 + Ampere SM86 + CUDA 12.8** — silent crash at FlashAttention V2 init. Whole stack is now llama.cpp.
- **n8n HTTP-node synthesis workflows** — superseded by hybrid T2+Cowork before any were built. Cowork now also retired per Decision 4.
- **Closed-loop self-training LoRAs** — three failure modes (model collapse, Goodhart on validation gate, distilling Phi-4 noise). Deliberate human-reviewed retraining on outcome data is the design; closed loop is ruled out.
- **Three-tier news synthesis (T2 + Haiku + Sonnet)** — Haiku tier adds complexity without quality benefit; two-tier is cleaner.
- **`/no-think` prompt-string convention for thinking suppression** on llama.cpp b9172 — does not work; must use `chat_template_kwargs`.
- **Porcupine wake-word for new builds (May 2026)** — Picovoice Console signup blocked on company email. OpenWakeWord is the replacement for non-corporate developers.
- **Pause-workload as Jarvis authority action** — predates substrate-orchestration model; Jarvis re-routes, doesn't pause.
- **Overnight-idle-as-resource as substrate doctrine** — rejected during Decision 5 Item 4 walkthrough. Substrate decisions are circumstance-driven, not time-of-day-gated.
- **Haiku 4.5 as latency niche cascade class** — pricing parity with DeepSeek V4 Flash at lower capability; redundant. Re-open: a future provider with a genuinely-distinct latency profile.
- **Multi-mode inference switching (overnight-deep, pipeline-heavy, standard)** — mode-switch architecture rejected v14 because the overnight use case it served was itself ruled out; LiteLLM fallback handles pipeline bursts; mode-switching adds takedown-failure surface area.
- **Per-request multi-LoRA serving on Tier 1 (vLLM punica-style)** — llama.cpp's `/lora-adapters` endpoint serves one active adapter per llama-server process; per-request multi-adapter requires vLLM's punica kernel which doesn't support Qwen3-Next hybrid architecture.

The ruled-out list is the operator's protection against re-proposing things that already failed. Check master_summary_v19 Appendix A before adding new modules or data sources.

---

## §18 — Memory Architecture (Pointer)

**Source of truth:** `MEMORY_ARCHITECTURE_v20.md`. **Last validated:** 2026-05-26.

The memory architecture is doctrine-grade and gets its own document, parallel to AUTHORITY_SPEC's role in v19. This section is a pointer with the minimum content needed to orient a reader and route them to the full doctrine.

### §18.1 Four layers

| Layer | Role | Members |
|---|---|---|
| **Truth** | Authoritative state. Written by operators and pipelines. | Repositories (code), Postgres (data), Obsidian vault (knowledge), Redis (live operational state when financial pipeline lands) |
| **Index** | Derived views over Truth. Written by re-indexers. | pgvector (semantic search), Codebase-Memory MCP (AST graph / Nexus), Hermes session search (FTS5) |
| **Memory** | Agent and world models built from Truth over time. Written by agents. | Hermes Agent (working memory, skills, preferences) + EverMemOS (long-horizon temporal state with Foresight signals) |
| **Arbiter** | Routes questions to the right layer. Observes everything. Writes nothing. | Jarvis (per §3.1 memory layer arbiter role) |

### §18.2 Single conflict-resolution rule

**Truth is primary; everything else is derived.**

Operator preferences → vault is Truth; Hermes USER.md and EverMemOS profile auto-sync from vault. Stable procedures → Hermes skill is Truth (executable form); vault may pointer-reference. Code → repository is Truth; Index layer (L3 + L5) and Memory layer (skills that reference code) are derived. Current operational state → Postgres/Redis is Truth; EverMemOS never claims current state, only historical evolution.

### §18.3 Authority gating

Memory→Memory writes (Hermes writing to its own `MEMORY.md`; EverMemOS consolidating MemCells into MemScenes) are inherently low-stakes and run autonomously per Decision 5 N=12 framework after promotion from strict cold-start.

Memory→Truth writes (any memory layer proposing an edit to a Truth-layer artifact — vault file, Postgres row, repository file) are **always Tier 3** under Decision 5 — operator confirmation required.

### §18.4 v20 truth hierarchy vs memory Truth layer

These are different doctrines answering different questions:

- v20 truth hierarchy (§0, §15.3): "What is true *right now* on this system?" → disk > git > jarvis-q > github > doc > chat. Governs current-state checks.
- Memory Truth layer (§18.1): "Where does our *durable knowledge* formally live?" → vault, repos, Postgres, Redis. Governs durable knowledge home.

Both correct, both serve different purposes, neither competes with the other. v20 truth hierarchy preserved verbatim.

### §18.5 Full doctrine

See `MEMORY_ARCHITECTURE_v20.md` for the complete framework: routing table per question type, primary-author per content type, observation surface per layer, build sequence rationale, conflict zone analysis, and cross-references to §3.1 (Arbiter role), §9.2 (Decision 2 / Hermes), §9.6 (Decision 6 amendment / Nexus + 2nd Brain build commitment), §13 (Hermes Agent operational detail).

---

## §19 — Closing Note

Built across multiple sessions May 18-26 in collaboration between Trent and several Claude instances. Work pattern that produced this document:

1. **Measure first.** The 94% baseline finding drove every cardinal that followed. Doctrine without measurement is preference.
2. **Doctrine before code.** Decisions 1 and 4 were written down before Rebalance Change 1 executed. The execution carried the doctrine, not the other way around.
3. **Honest inventory.** Small missions surfaced during big work get banked, not buried. §16 exists because the alternative is they get lost.
4. **Verify against disk.** Every "we did X" claim in this document is checkable on monarch. If something here is wrong, monarch wins.
5. **Manager first, voice assistant a distant second.** The most consequential framing in v19. Drove the four-question architectural test in §3.2.
6. **Propagation discipline (new in v20).** One canonical statement per fact; every doctrine claim cites its source; runtime artifacts are not doctrine; loose ends in code are §16 open items, never silent drift. The v19 → v20 consolidation was forced by the discovery that the same closed item (audit A6, deepseek rename) had to be propagated across five documents and was repeatedly half-completed — the closing commit updated some, never all.

The point of v20 is to make sure the next session opens with this foundation intact, instead of relitigating it. The point of §0 is to make sure v20 itself doesn't drift the way v19 did.

The work shipped. The doctrine is honest. The system understands itself.

---

*End of master_summary_v20. Living document. Update on doctrine close or code change — never on chat conversation alone.*
