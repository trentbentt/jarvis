# v19 Cardinal Decisions — Doctrine Close

**Date:** 2026-05-19
**Closes:** Decisions 1, 4, 6 (of 6)
**Status:** Decisions 2, 3, 5 remain open

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

- **Decision 2 — Hermes adoption shape.** Pattern B parallel to n8n, Curator scope narrow or off, memory writes disabled, routed via DeepSeek V4 Flash initially. Needs its own session.
- **Decision 3 — T6 operational defaults.** Qwen3.6-35B-A3B UD-Q4_K_XL, ~25% expert offload, 64K context, three named modes (comfort / conservative / aggressive). Blocked on 21 GB model download + spin-up tooling. Requires rebalance to land first.
- **Decision 5 — Jarvis authority levels.** Three tiers (autonomous-immediate / autonomous-with-log / surface-and-ask), sleeping-window voice rules. Substrate ready (v0.2). Needs its own session.

## Note on Rebalance Headroom

Projected post-rebalance baseline: ~14-15 GB / 60%. That leaves ~9 GB free at idle — more headroom than T6 expert-offload strictly needs.

Pre-decide whether the slack stays as T6 burst capacity, or gets reclaimed for one of:

- T1 context restored to 36K (or extended past it)
- T4 `-np` raised to 6 or 8
- Whisper preloaded for voice dictation (Phase 17.5)
- Reserved for a second concurrent T6 burst session

Don't let this become unspoken. Decide before T6 spin-up tooling lands.
