# v19 Cardinal Decisions — Doctrine Close

**Date:** 2026-05-19 (initial close: Decisions 1, 4, 6); 2026-05-24 (Decision 5 close + Decision 4 small amendment)
**Closes:** Decisions 1, 4, 5, 6 (of 6)
**Status:** Decisions 2 and 3 remain open

---

## Decision 1 — Architectural Reframe

**Statement:**
Local (monarch) handles data plumbing, agentic glue, and on-demand coder burst. Cloud handles synthesis, building/design, and frontier reasoning.

**Forcing function:**
Monarch idle VRAM baseline measured at 94% (23.1 GB / 24 GB) under standard mode (Jarvis v0.2 telemetry, 2026-05-19). No headroom exists for synthesis workloads locally. The hardware cannot carry the alternative; this decision is now mathematically required, not preferential.

**Downstream consequences closed by this decision:**

- T1 reframed: OpenCode harness → Hermes/Jarvis host
- T2 reframed: always-on → burst-only
- Three high-stakes LoRAs (consultancy / design / exploratory) deferred indefinitely
- Path 1 / Path 2 / Path 3 alternatives closed
- Cowork retired as a pipeline stage (formalized in Decision 4)
- Six agent stacks restructured: synthesis-heavy components route to cloud; local retains plumbing, routing, light reasoning, and coder burst (T6)

**Status:** Closed 2026-05-19. Already executed in practice (news Stage 4 DeepSeek V4 Flash migration; financial intensive work routed to Anthropic API).

---

## Decision 4 — Cloud Routing Chain

**Statement:**
Cloud work is routed by task class to a defined provider tier. Cowork is retired as a pipeline stage.

**Routing by task class:**

| Task class | Primary | Overflow |
|---|---|---|
| Building / design (interactive, iterative) | Claude Pro (account A or B) | Kimi K2.6 → T6 local burst |
| Synthesis (batch, scheduled, news) | DeepSeek V4 Flash | Haiku 4.5 |
| Money-on-line (financial trades, NDA-tagged) | Anthropic API direct | — |
| Light / latency-sensitive | Haiku 4.5 | — |
| Local coder burst (NDA, quality-needed coding, Pro overflow) | T6 (monarch, Qwen3.6-35B-A3B) | — |

**Provider priority (when task class is ambiguous):**
Claude Pro → DeepSeek V4 Flash → Kimi K2.6 → Haiku 4.5 → Anthropic API direct.

**Retired:**
Cowork. No longer a pipeline stage. Existing references in stack CONTEXT.md files (consultancy / content / design / financial / leads / exploratory-coding) to be removed in the v19 doc pass.

**Discipline rules:**

- Two Claude Pro accounts are reserved for building/design. Do not burn Pro on synthesis that DeepSeek V4 Flash can handle for cents.
- Money-on-line work (live trading, NDA client work) routes to Anthropic API direct — never Pro, never DeepSeek, never Kimi.
- T6 is the overflow valve: triggered when Pro walls, NDA prohibits cloud, or quality demands local coding.

**Status:** Closed 2026-05-19. Partially executed (news Stage 4 on DeepSeek V4 Flash; financial intensive on API).

**2026-05-24 — Small Amendment: Structural Class Reframe**

The cascade is not a strict hierarchy. Providers organize into structural classes:

| Class | Providers | Role |
|---|---|---|
| Workflow-tier-zero | Claude Pro (×2) | Operator default for building/design; not Jarvis-routed |
| Peer rotation | DeepSeek V4 Flash, Kimi K2.6 | Active workhorse pair; rotate by fullest-peer rule (see Quota Cascade Policy in AUTHORITY_SPEC) |
| Emergency rung | Anthropic API direct | Tier 3 per-call invocation; not in rotation (vestigial — doctrine-forward, not yet wired) |

The original "Provider priority" line (Claude Pro → DeepSeek V4 Flash → Kimi K2.6 → ~~Haiku 4.5~~ → Anthropic API direct; Haiku deprecated 2026-05-24) remains as a tie-breaker when task class is genuinely ambiguous. It is not the default routing rule — class-by-task remains the default. The reframe makes explicit what Decision 4 implied but did not state: Pro is the operator's workflow surface, not a Jarvis-routed cascade rung. Quota Cascade Policy in AUTHORITY_SPEC governs cascade dynamics within and between classes.

**Haiku 4.5 deprecation note (2026-05-24):** Originally specced as the latency niche class. Operator-confirmed deprecated: pricing parity with DeepSeek V4 Flash at lower capability makes Haiku redundant. Removed from cascade. Re-open condition: a future provider with a genuinely-distinct latency profile (substantially faster than DeepSeek peer round-trip) re-justifies a latency niche class.

---

## Decision 5 — Jarvis Authority Model

**Statement:**
Jarvis acts within a three-tier authority framework (autonomous-immediate / autonomous-with-log / surface-and-ask), bounded by four Hard Constraints, with promotion governed by empirical thresholds rather than design-time judgment. Full doctrine in `AUTHORITY_SPEC_v19.md`.

**Forcing function:**
Substrate Phase 1 listeners (vram.py, tier_health.py) ship telemetry; without an authority model, every observed event has ambiguous response shape. The 94% → 66% VRAM rebalance creates real action-eligibility (substrate pressure can actually be acted on); the authority model defines who acts and under what supervision.

**Walkthrough closure path:**

| Item | Closed | Commit |
|---|---|---|
| 1 — Tier 1 autonomous-immediate list | 2026-05-22 | 50692bd |
| 2 — Tier 2 autonomous-with-log list (per-tier-class restart; latency-band cascade) | 2026-05-22 | 50692bd |
| 3 — Tier 3 surface-and-ask list (T1 restart; latency cascade failed; Quota Cascade Policy) | 2026-05-22 | 50692bd |
| 4 — Overnight Workload Window + Hard Constraints | 2026-05-22 | 414d5b2 |
| 5 — Bypass severity ladder + Substrate Pressure Cascade reframe (continuous intensity band) | 2026-05-22 | f0675da |
| 6 — Pro tier estimation: **descoped** (Pro is workflow-tier-zero, not Jarvis-routed) | 2026-05-24 | *this commit* |
| 7 — Promotion threshold: **N=12**, uniform across both rungs (Tier 3 → Tier 2 → Tier 1) | 2026-05-24 | *this commit* |
| 8 — Cold-start rule: **all new actions begin at Tier 3**, no override at introduction; material behavior change re-enters at Tier 3 | 2026-05-24 | *this commit* |
| Quota Cascade Policy: **20% / 10%** peer rotation thresholds; fullest-peer rotation mechanic; drain phase with per-percent notification overlay | 2026-05-24 | *this commit* |

**Hard Constraints (load-bearing across all tiers):**

1. Jarvis never shuts off.
2. Jarvis identity never routes to API (workloads route, the coordinator does not).
3. Pause is not in the toolkit (Jarvis re-routes work, never blocks it).
4. T1 restart is Tier 3, never silent.

**Key doctrine moves from the walkthrough:**

- The **Substrate Pressure Cascade** is a continuous intensity band (2.5 GB → 500 MiB free VRAM), not a sequential layer ladder. Stateless response — intensity recalibrates with current pressure, not past escalation state. Three response kinds (eviction, conditional self-offload, API routing) blend across the band.
- The **promotion threshold N=12** is uniform across both rungs. An action's full path from cold-start to silent operation requires a minimum of 24 operator-acknowledged successful runs (12 at Tier 3 + 12 at Tier 2). The strict cold-start rule is the data-collection mechanism for the promotion threshold — without it, the threshold has no baseline. Operator framing for this rule: "human in the loop directing growth."
- The **Quota Cascade Policy** is peer rotation, not strict hierarchy. DeepSeek V4 Flash and Kimi K2.6 are peers; the fullest-peer rule rotates active routing at 20% and 10% remaining. Drain phase engages when both peers are below 10% — work continues, with a per-percent notification overlay driving reload urgency.
- The **Decision 4 cascade is reframed** into structural classes: workflow-tier-zero (Pro), peer rotation (DeepSeek / Kimi), emergency rung (Anthropic direct). Haiku 4.5 was originally specced as a latency niche class; deprecated the same day. See Decision 4's 2026-05-24 amendment above.

**New authority primitive introduced (Quota Cascade Policy):** Tier 2 action with a notification overlay. The routing action (rotate / drain) remains autonomous-with-log; the operator-facing notification rides on top without converting it to Tier 3. Local primitive of the Quota Cascade Policy; not elevated to a general AUTHORITY_SPEC primitive in this commit (re-open condition: a second action requires the same overlay shape).

**Status:** Closed 2026-05-24. Full spec ratified; Phase 2 listener implementation (`process.py`, `quota.py`, `cron.py`) is downstream work, not blocked on further doctrine.

---

## Decision 6 — v19 Scope

**Statement:**
Two subsystems receive full phase-level treatment in v19. Two are reduced in scope or deferred.

| Subsystem | v19 treatment |
|---|---|
| Jarvis | Full phase-level. v0.2 built; Phase 2 listeners (process.py / quota.py / cron.py) pending; authority spec pending (Decision 5). |
| Financial pipeline | Full phase-level. Paper-trading harness, backtesting, `macro_signals` and `news_trade_signals` tables, position sizing, risk model. |
| Nexus 17.1 | Design-only. No implementation in v19. |
| 2nd Brain 17.2 | Deferred. No v19 work. |

**Implications for open decisions:**

- **Decision 2 (Hermes):** No memory-write story needed for 2nd Brain. Adoption is Pattern B parallel to n8n only. Curator scope decision is narrower as a result.
- **Decision 5 (Jarvis authority):** No Nexus action rules needed. Authority spec covers Jarvis + financial pipeline action surface only.

**Status:** Closed 2026-05-19.

---

## What's Now Unblocked

- **Standard mode rebalance.** Concrete engineering task with doctrine behind it: T2 → burst-only, T1 context 36K → 24K, T4 `-np` 4 → 2. Target baseline ≤ 60% (≤ 14.4 GB).
- **Stack CONTEXT.md pass.** Six files (consultancy / content / design / financial / leads / exploratory-coding) need updates: synthesis components route to cloud, Cowork references removed, LoRA references marked deferred.
- **Financial pipeline phase-level design.** Tier 3 work can begin.
- **v18 → v19 master summary.** Deferred until rebalance is executed and measured.

## What Remains Open

- **Decision 2 — Hermes adoption shape.** Pattern B parallel to n8n, Curator scope narrow or off, memory writes disabled, routed via DeepSeek V4 Flash initially. Blocked on v18 Hermes brainstorm docs being surfaced (bible audit §A7 flags these may not exist as discrete artifacts; reconstruct-from-scratch may be required).
- **Decision 3 — T6 operational defaults.** Qwen3.6-35B-A3B UD-Q4_K_XL, ~25% expert offload, 64K context, three named modes (comfort / conservative / aggressive). Blocked on 21 GB model download + spin-up tooling. Requires Rebalance Change 2 measurement to land first.

## Note on Rebalance Headroom

Projected post-rebalance baseline: ~14-15 GB / 60%. That leaves ~9 GB free at idle — more headroom than T6 expert-offload strictly needs.

Pre-decide whether the slack stays as T6 burst capacity, or gets reclaimed for one of:

- T1 context restored to 36K (or extended past it)
- T4 `-np` raised to 6 or 8
- Whisper preloaded for voice dictation (Phase 17.5)
- Reserved for a second concurrent T6 burst session

Don't let this become unspoken. Decide before T6 spin-up tooling lands.
