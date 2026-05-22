# Jarvis Authority Spec (Decision 5 — Draft)

**Date:** 2026-05-19 (draft); 2026-05-21 (Items 1-3 revise pass)
**Status:** DRAFT — Decision 5 walkthrough Items 1-3 banked; Items 4-8 pending operator confirmation
**Scope:** Jarvis + financial pipeline action surface (per Decision 6)
**Operator confirmation required on:** quota cascade thresholds, sleep window bounds, bypass severity ladder, Pro tier estimation, promotion threshold (N), cold-start rule

---

## Three Action Tiers

Each Jarvis-initiated action belongs to exactly one tier. Tier determines whether Jarvis asks, logs, or stays silent.

### Tier 1 — Autonomous-immediate

Jarvis acts without asking, without surfacing. Standard telemetry only.

**Criteria for inclusion:**

- Reversible
- Has run successfully ≥ 10 times without correction
- Does not change user-visible state
- Costs no money
- Burns < 100 MiB VRAM

**Confirmed actions:**

- Rotate internal Jarvis logs (state.json, daemon.log)
- Compact state.json snapshots
- Clear tmpfs caches owned by Jarvis
- Reconnect a Tailscale node that flapped (`tailscale up` after detected disconnect)
- Restart Jarvis writer thread if deadlock detected (defensive — should never fire under v0.2; revisit on daemon version bump)
- Prune Jarvis event ring buffer beyond retention
- Garbage-collect stale `_tier_last_pid` entries for tiers no longer enabled

### Tier 2 — Autonomous-with-log

Jarvis acts and writes a `jarvis-q events` entry the operator can audit.

**Criteria for inclusion:**

- Reversible or low-cost-to-reverse
- Operator might want to know post-hoc
- Action correct in ≥ 99% of cases
- No money, no user-visible blocking change
- Burns < 1 GB VRAM

**Confirmed actions (driven by Phase 2 listeners):**

| Trigger (listener · signal) | Action | Notes |
|---|---|---|
| process.py · T3/T4/T5 dataplane tier crashed (PID gone, was active) | `tmux kill-window inference:<window>` + `inference-up` idempotent guards | tier_health confirms post-restart |
| process.py · T2/T6 burst tier crashed (PID gone, was active) | `t2-up` / `t6-up` (when T6 tooling ships) | tier_health confirms post-restart |
| process.py · T1 crashed (PID gone, was active) | Escalate to Tier 3 — never silent restart | T1 is the Jarvis reasoning brain; the manager doesn't silently restart its own brain |
| process.py · tier flapping (`restart_count_24h ≥ 3`) | Stop restart loop, demote action to Tier 3 surface | Don't keep restarting broken things |
| vram.py · active burst tier (T2 or T6) idle > N min | Call tier down-script (`t2-down` / `t6-down`) | N = 30 min default; reclaims VRAM |
| quota.py · LiteLLM tier-1 walled (429) | Escalate to tier-2 provider per Decision 4 cascade | Reversible; cross-provider behavior governed by Quota Cascade Policy below |
| cron.py · git repo size > threshold | Schedule `git gc` for next idle window | Reversible |

**Latency-band routing cascade (replaces VRAM-threshold framing for workload routing):**

Each workload is assigned a class with two latency markers — *peak* (ideal target) and *minimum acceptable* (degradation floor). Jarvis monitors observed latency per class and responds along this cascade:

- In-band → no action; current substrate continues serving.
- Approaching minimum (within ~20% of min) → Jarvis considers substrate alternatives, does not yet act.
- Below minimum → escalate per Decision 4 cascade: substrate re-allocation first, API as second lever within the workload's authorized budget.
- Way below minimum (2× past min) → Tier 3 surface; operator decision needed.

VRAM, CPU, and RAM thresholds are secondary diagnostics under this framing — used by Jarvis to predict and explain latency drift, not as standalone triggers. **Pause is not in the toolkit:** Jarvis re-routes work, never blocks it.

**Initial workload class slots (framework only — peak/minimum values deferred to measurement data; Scope B):**

- Interactive coding (OpenCode → T1)
- Batch synthesis (news pipeline → T2 or cloud cascade)
- Cron-scheduled jobs (daily/weekly → T3 / T4)
- Real-time voice (Phase 18, future — flagged as needing its own class; values not defined in v19)

### Tier 3 — Surface-and-ask

Jarvis notifies, waits for explicit confirmation before acting.

**Criteria for inclusion:**

- Costs money (any cloud API call at non-trivial rate)
- Burns significant VRAM (T6 spin-up ≈ 17-19 GB)
- Affects user-visible workflow (paused/killed jobs, deferred runs)
- Has never run autonomously before (new action type — surface first N times)
- Triggers in NDA-tagged context
- Operator explicitly demoted from Tier 1 or 2 after regret

**Confirmed actions:**

| Trigger | Action | Why Tier 3 |
|---|---|---|
| Pro walled during interactive session | Spin up T6 | VRAM impact, fan noise, real footprint |
| process.py · T1 crashed or unresponsive | Restart T1 with operator confirmation | Jarvis reasoning brain restart is high-impact; the manager doesn't restart its own brain silently |
| Latency cascade failed (workload still ≥ 2× past min after substrate + API attempts exhausted) | Surface for operator decision | Jarvis ran out of autonomous moves |
| process.py · tier flapping (5+ restarts in 24h) | Pause cron jobs that target the tier | User-visible workflow change |
| Retire model from local storage | Delete HF cache entry | Irreversible (re-download cost) |
| Any action in sleep window not meeting bypass | Hold and surface at 07:00 | Voice / notification policy |

Cross-provider quota cascade behavior — including the "all cheap providers walled" case — is governed by the Quota Cascade Policy below, not by a Tier 3 trigger row.

---

## Quota Cascade Policy (Prepaid Model)

Each provider key in the Decision 4 cloud cascade carries a manually-loaded prepaid balance. Once a key's loaded balance is spent, that key is unavailable until the operator manually reloads it. There is no auto-recharge, overage billing, or monthly reset. Jarvis treats remaining balance as a hard floor, not a soft monthly target.

This policy supersedes two earlier entries from the 5/19 draft: the "DeepSeek > 80% monthly spend" Tier 2 row and the "all cheap providers walled → Anthropic direct" Tier 3 row. Both are subsumed below.

**Cascade behavior per provider:**

| Remaining balance | Trigger | Tier | Action |
|---|---|---|---|
| ≥ 20% | normal operation | — | Continue serving from current provider |
| < 20% (80% consumed) | listener signal | Tier 2 | Route subsequent calls to next-cheaper cascade rung; log in `jarvis-q events` |
| < 10% (90% consumed) OR provider walled (429 / out-of-credit response) | listener signal | Tier 3 | Surface to operator. Do NOT auto-cascade further. Operator decides: reload current key, accept the cascade down to the next prepaid rung, or pause the workload. |

**Why earlier Tier 3 escalation than a monthly-billing default would suggest:** under prepaid manual reload, 10% remaining is a small absolute runway. A single large synthesis call landing at 95% consumed can push the next listener sweep past 99%. Tier 3 at 90% consumed gives the operator-in-loop time to decide before the runway disappears.

**Why no auto-cascade past Tier 3 to Anthropic API direct:** the cascade has finite depth under prepaid model. Pro walls but doesn't die; DeepSeek, Haiku, and Anthropic direct each have independent prepaid balances that exhaust independently. Unbounded auto-cascade worst case is "Pro walls, DeepSeek drains, Haiku drains, Anthropic direct drains" in a single bad day if a pipeline misbehaves. Operator-in-loop at each rung is the only thing between predictable cost and three prepaid balances burned overnight.

**Pending explicit confirmation:** the 20% / 10% threshold values were derived during the 5/21 walkthrough in response to the operator's "once the budget is hit, it's hit" constraint. Operator did not explicitly confirm these specific numeric values before the walkthrough was interrupted by the Item 4 redirect. Values to be ratified or revised when Decision 5 closes (or as part of approving this revise commit).

---

## Sleep Window Rules

Sleep window controls **notification channel**, not whether action happens.

**Window:** 23:00–07:00 America/New_York
OPERATOR TO CONFIRM bounds and timezone (Raleigh = ET, confirmed).

**What "voice off" means in window:**

- Audio TTS suppressed
- Push/mobile/desktop notification suppressed
- Visual notifications still render to `jarvis-q events`
- Action tiers 1/2/3 still apply unchanged — only notification channel quiet

**Bypass severity ladder (audio/push allowed in window):**

| Event class | Threshold | Rationale |
|---|---|---|
| GPU thermal | temp > 85°C sustained 60s | Hardware damage risk |
| Security | fail2ban escalation, SSH breach attempt | Compromise risk |
| Spend burst | > $5 in < 5 min on any single provider | Runaway agent / budget bleed |
| OOM imminent | free < 500 MiB | System-wide stability |
| Power | UPS event / power loss | If power monitoring later added |

OPERATOR TO CONFIRM thresholds.

**Queued items batch-surface at 07:00:** Jarvis emits a morning brief listing all Tier 2 events from overnight + any Tier 3 items that held.

---

## Presence Axis (Future Work — Not in v19)

Voice/notification rules may differ by operator presence state (solo / girlfriend present / on call / etc.). Flagged as open work, not specced in v19.

If specced later, would gate via a separate `model.operator.presence` field updated manually (or detected via macOS focus state / calendar status).

---

## Action Lifecycle

Actions are not static. Promotion and demotion follow operator behavior.

**Promotion (Tier 3 → 2 → 1):**

- An action fired with explicit confirmation N times (default 10) without correction is eligible for promotion
- Promotion is **proposed by Jarvis**, not automatic — surfaces as a Tier 3 ask: "I've done X 10 times without correction; promote to Tier 2?"
- Operator approves via reply (CLI: `jarvis-q authority promote <action_id>` — future tooling)

**Demotion (immediate, no threshold):**

- Any single instance where operator regrets the action triggers demotion to Tier 3
- CLI: `jarvis-q authority demote <action_id>` — future tooling
- Demotion is logged with reason if provided

**Cold-start rule:**

- All new actions begin in Tier 3
- No action ships in Tier 1 or Tier 2 without operator opt-in at spec time

---

## Integration with Phase 2 Listeners

The authority spec is implemented by the decision engine (Phase 3, not built). Listeners only observe; the engine reads state + applies authority rules.

| Listener | Drives | Tier |
|---|---|---|
| process.py | `tier_restart` (recoverable), `tier_flapping` (chronic) | T2 / T3 |
| quota.py | Cascade routing decisions, spend burst alerts | T2 / T3 |
| cron.py | Schedule conflicts, VRAM forecast collisions | T2 (reschedule) / T3 (pause) |
| vram.py | OOM pre-emption, burst-tier idle shutdown | T2 |

---

## Out of Scope for v19 Authority Spec

- Decision engine implementation (Phase 3)
- Natural-language formulations for Tier 3 prompts (UX work, post-v19)
- Voice persona / TTS choice (Phase 17.5, separate)
- Multi-operator handling (single-operator system)
- 2nd Brain or Nexus action surfaces (excluded by Decision 6)
- Hermes action surface (deferred until Decision 2 closes)

---

## Operator Confirmation Checklist

Before closing Decision 5, operator confirms:

- [x] Tier 1 action list (no surprises) — banked 2026-05-21 walkthrough Item 1
- [x] Tier 2 action list (routing escalations, tier restart policy, latency-band cascade) — banked 2026-05-21 walkthrough Item 2
- [x] Tier 3 action list (money-on-line, T1 restart, latency cascade failed) — banked 2026-05-21 walkthrough Item 3
- [ ] Quota cascade policy thresholds (20% / 10% under prepaid model) — partner-derived from operator constraint; explicit numeric ratification pending
- [ ] Sleep window bounds (Item 4 — pending)
- [ ] Bypass severity ladder thresholds (Item 5 — pending)
- [ ] Pro tier estimation (~250 msg/5h Pro Max vs ~50 msg/5h standard) (Item 6 — pending)
- [ ] Promotion threshold N (default 10) (Item 7 — pending)
- [ ] Cold-start rule (everything starts Tier 3) (Item 8 — pending)
