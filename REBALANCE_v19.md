# v19 Standard Mode Rebalance Proposal

**Date:** 2026-05-19
**Status:** DRAFT — proposal, not committed
**Authority:** Decisions 1 and 4 (closed in `DECISIONS_v19.md`)
**Measurement source:** Jarvis v0.2 telemetry
**Goal:** Reduce idle VRAM baseline from 94% → ≤ 60% to enable T6 burst, LoRA loading, and active workload headroom

---

## Measured Current State

Source: `jarvis-q vram` at 2026-05-19 09:34 (resting baseline, zero active workloads)

| Tier | Model | Quant | Ctx | -np | VRAM |
|---|---|---|---|---|---|
| T1 | Qwen3.6-27B | UD-Q4_K_XL | 36K | 1 | 11,842 MiB |
| T2 | Qwen3.6-27B | UD-Q4_K_XL | 16K | 1 | 6,832 MiB |
| T3 | Qwen3.6-27B | UD-Q4_K_XL | 8K | 1 | 0 MiB (CPU) |
| T4 | Phi-4-mini | Q4_K_M | 16K | 4 | 4,174 MiB |
| T5 | Qwen3-1.7B | Q5_K_M | 8K | 1 | 0 MiB (CPU) |
| Driver | — | — | — | — | 512 MiB |
| **Total** | | | | | **23,102 MiB / 24,576 MiB (94.0%)** |
| **Free** | | | | | **1,016 MiB** |

**80% target line:** 19,661 MiB used / 4,915 MiB free
**Current deficit vs target:** 3,442 MiB over (+14.0pp)

Idle drift observed: 10 MiB used / 10 MiB free shift over ~30 min between two Jarvis snapshots. Suggests KV cache or per-session activation creep. Not concerning at this magnitude; longitudinal data will tell.

---

## Target State

| Metric | Value |
|---|---|
| Idle baseline | ≤ 14,500 MiB (~ 59%) |
| Free at idle | ≥ 10,000 MiB |
| T6 burst headroom | ≥ 17,000 MiB available when burst-eligible tiers are stopped |
| 80% ceiling | Never exceeded at idle, briefly OK during active workload spikes |

Two-thirds of the deficit closes from T2 alone. The rest is optional — measure first, cut only what's needed.

---

## Proposed Changes

### Change 1 — T2: always-on → burst-only

**Estimated savings:** 6,832 MiB (measured residency, near certain)
**Confidence:** High — full tier shutdown frees exact measured value
**Risk:** Low — assumes Decision 4 (synthesis → cloud) holds, which it does

**Current config (`~/bin/inference-up` T2 block):**
- Always started during stack bringup
- Port 8083, ctx 16K, Qwen3.6-27B
- Workload assumption (v18 era): continuous bounded summary work

**New role under v19 (Decisions 1 + 4):**
- News pipeline Stage 2 sector synthesis (validated local workload, daily-ish)
- Possibly: financial pipeline classification windows
- Manual operator invocation for specific tasks
- Everything heavier routes to DeepSeek V3 or Pro

**Burst lifecycle:**

```
~/bin/t2-up        # starts T2, waits for /health OK, returns
~/bin/t2-down      # gracefully stops T2 process
```

Cron jobs that need T2 wrap their work:

```
# Before news Stage 2:
~/bin/t2-up && ~/projects/news-pipeline/synthesis/synthesis_export.py && ~/bin/t2-down
```

**Idle auto-shutdown:** Jarvis vram.py (Phase 2 work) can fire `t2-down` after configurable idle timeout. Default proposal: 30 min idle. Authority Tier 2 (autonomous-with-log).

**Schema change:**

Add `burst_only: bool = False` to `TierConfig` in `schema.py`. Set T2's `burst_only=True` in `MONARCH_TIERS`. Update `inference-up` to skip burst-only tiers during standard bringup.

**Rollback:** flip `burst_only=False`, run `inference-up t2`.

---

### Change 2 — T1: ctx 36K → 24K

**Estimated savings:** ~1,000-3,000 MiB (range reflects uncertainty about Qwen3.6-27B KV cache scaling)
**Confidence:** Medium — direction is certain, magnitude unknown until measured
**Risk:** Low for the new T1 role; would be high under old role (OpenCode coding harness, retired by Decision 1)

**Current config:**
- ctx 36K, sized for OpenCode coding sessions
- Decision 1 reframes T1 as Hermes/Jarvis host: agentic glue, routing, light reasoning
- 24K is the smallest context that comfortably holds Hermes routing prompts + history + tool definitions

**New config:**
- ctx 24K, -np 1, same -ngl (unchanged), same model and quant
- One-number change in `inference-up`

**Measurement gate:** apply this change *after* Change 1 lands and Jarvis has 10 min of clean post-T2-shutdown data. Compare T1 VRAM before and after. Real number replaces the 1-3 GB estimate.

**Rollback:** restore `-c 36864` in `inference-up`, restart T1.

**Open:** if 24K turns out to be tight for Hermes routing prompts (Decision 2 work), consider 28K as a middle ground. Re-evaluate when Hermes ships.

---

### Change 3 — T4: -np 4 → -np 2 (OPTIONAL)

**Estimated savings:** ~1,000 MiB
**Confidence:** Medium
**Risk:** Validation gate throughput halves; classifier concurrency drops from 4 to 2

**Recommendation: defer.** Probable that Changes 1 and 2 land us comfortably under 60%. T4 at -np 4 is the validation gate's throughput buffer for the news pipeline + future financial classification. Cutting it risks creating a new bottleneck for a benefit we likely don't need.

**Trigger to revisit:** if post-Changes-1+2 measurement shows baseline > 70% (i.e., Change 2 only saves ~1 GB instead of ~3 GB) and T6 burst pressure becomes real.

**Rollback:** restore `-np 4` in `inference-up`, restart T4.

---

## Plan B Reserves (Not in This Proposal)

Available if Changes 1 + 2 underperform and Change 3 isn't enough:

- **KV cache quantization** on T1: `-ctk q8_0 -ctv q8_0` likely saves another ~30-40% of KV memory at minor quality cost. Already used on T4 per inference-up's `q8_0 KV` annotation.
- **T1 ctx 24K → 16K:** further reduction if Hermes routing turns out to fit in 16K
- **T3 retirement:** if its workload moves to T5 or cloud entirely

Don't reach for these unless measured data demands it.

---

## Execution Order

Each step gated by Jarvis measurement. Don't batch — measure between.

1. **Schema patch:** add `burst_only: bool` to `TierConfig`, set T2's flag, restart daemon, verify Jarvis still polls cleanly. ~15 min.
2. **Write `t2-up` / `t2-down` scripts.** Mirror the per-tier startup logic from `inference-up`. ~30 min.
3. **Update `inference-up`:** skip burst-only tiers in bringup loop. ~10 min.
4. **Update news pipeline cron** to wrap Stage 2 in `t2-up && ... && t2-down`. ~10 min.
5. **Bring stack down, bring back up** without T2. Measure idle. Expected: ~16,270 MiB used (66%).
6. **Soak 30 min.** Run `jarvis-q vram` periodically. Confirm idle stable, no T2 invocations breaking.
7. **Change 2: T1 ctx 36K → 24K.** One-number edit in `inference-up`. Restart T1. Measure delta.
8. **Soak 30 min.** Confirm Hermes-class routing prompts still fit (manual test against T1 directly with a representative prompt).
9. **Evaluate:** measured baseline vs target. If ≤ 60%, stop. If 60-70%, consider Change 3. If > 70%, revisit estimates and consider Plan B.
10. **Update on-monarch CONTEXT.md** (per stack) to reflect new T2 burst semantics, T1 reduced context.

Total active engineering time: ~2-3 hours. Plus soaks. Reversible at every step.

---

## Risk & Rollback Summary

| Change | Reversibility | Time to rollback | Worst case |
|---|---|---|---|
| T2 burst-only | Full | 60s (`t2-up`) | News Stage 2 fails if cron wrapper bugged — manual run unblocks |
| T1 ctx reduction | Full | 60s (edit + restart) | Hermes routing prompts truncated — observable, reversible |
| T4 -np reduction | Full | 60s | Validation gate queue backs up under load — observable |
| Schema `burst_only` field | Full | git revert | Jarvis daemon won't load old schema — restart |

---

## What This Unblocks

- **Decision 3 (T6 defaults)** — T6 burst (17-19 GB) now physically possible. Spin-up tooling can be specced against real headroom.
- **Decision 5 (Jarvis authority)** — Tier 2 action `auto-stop burst tier on idle` becomes a real action with measurable trigger.
- **LoRA training** — pauseable T1 makes RTX 3090 available for short training runs (if Decision 1 reframe ever revisits the deferred LoRAs).
- **Active workload headroom** — financial classification + news Stage 2 can run concurrently without pushing baseline over 80%.

## What This Does Not Address

- Standard mode vs burst mode distinction is now real in code, but full burst orchestration (T6 spin-up that pauses T1, etc.) is Decision 3 work, not rebalance work.
- T6 download (~21 GB) still required separately.
- The `~/bin/inference-up` `fail()` tmux preservation patch (May 19) interacts with burst tier startup — verify `t2-up` failure path doesn't kill the inference session.

---

## Open Confirmations Needed

- [ ] T2 burst trigger: cron-wrapped only, or also Jarvis-triggered for specific workloads?
- [ ] T2 idle auto-shutdown timeout: 30 min default, or longer/shorter?
- [ ] T1 ctx target: 24K firm, or willing to try 16K first?
- [ ] Change 3 (T4 -np cut): authorize as fallback, or strictly defer to Plan B?
- [ ] News pipeline Stage 2 cron schedule: still 06:25, or has it shifted?
- [ ] Financial pipeline T2 dependency: any classification workload that hits T2 outside news Stage 2?
