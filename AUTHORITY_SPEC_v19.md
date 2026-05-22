# Jarvis Authority Spec (Decision 5 — Draft)

**Date:** 2026-05-19 (draft); 2026-05-21 (Items 1-5 revise passes)
**Status:** DRAFT — Decision 5 walkthrough Items 1-5 banked; Items 6-8 pending operator confirmation
**Scope:** Jarvis + financial pipeline action surface (per Decision 6)
**Operator confirmation required on:** quota cascade thresholds, bypass severity ladder thresholds, Pro tier estimation, promotion threshold (N), cold-start rule

---

## Hard Constraints

Lines that do not move under any combination of resource pressure, operator absence, or scheduling priority. The cascades and policies below operate within these constraints, not against them.

- **Jarvis never shuts off.** Jarvis is load-bearing for system boot and recovery — nothing else in the stack can bring tiers back if the daemon dies. Killing Jarvis is structurally forbidden, not just discouraged. Maximum degradation is conditional self-offload to RAM/CPU per the Substrate Pressure Cascade below.
- **Jarvis identity never routes to API.** The daemon, T1 reasoning brain, listeners, and state store stay monarch-local under all pressure conditions. Two reasons: (a) routing the coordination layer to cloud exposes the entire system's credentials, dispatch decisions, and telemetry to an external surface; (b) Jarvis is high-traffic by design and monthly prepaid budgets would drain in days at cloud rates. Workloads route to API per the cascade below — the coordinator does not.
- **Pause is not in the toolkit.** Under VRAM, latency, or quota pressure, Jarvis re-routes work — never blocks it. The Substrate Pressure Cascade, latency-band routing cascade (Tier 2), and Quota Cascade Policy together cover the response surface without resorting to pause-the-workload.
- **T1 restart is Tier 3, never silent.** T1 is the Jarvis reasoning brain. The manager does not silently restart its own brain. Operator confirmation gates any T1 restart action.

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

## Overnight Workload Window

Doctrinal time window during which pipelines are scheduled, the Substrate Pressure Cascade Layer 2 (self-offload) is permitted, and voice/push notifications are quieted unless severity ladder bypass applies.

**Window (weekday baseline):** 23:00–07:00 America/New_York

The window assumes a Monday–Friday 9-5 operator schedule. Weekend variability is acknowledged and deferred — once the post-9-5 weekend pattern stabilizes, a `weekend_window` doctrine will be specced separately.

**What the window controls:**

- **Scheduling preference.** Pipelines marked overnight-eligible (news ingestion at 05:15 / 05:30 / 06:00; financial Phase A pre-market when wired) target this window. Bound by cron.py listener (Phase 2 / not yet built).
- **Substrate Pressure Cascade Layer 2 gating.** Conditional self-offload of Jarvis to RAM/CPU is permitted only within this window — see Substrate Pressure Cascade below.
- **Notification channel.** Voice TTS and push notifications quieted within the window unless an event clears the bypass severity ladder. Visual notifications still render to `jarvis-q events`.
- **Action tiers unchanged.** The window is a notification and substrate doctrine, not an authority gate. Tier 1/2/3 classification of actions does not change inside or outside the window.

**Working-hours notification policy:** outside the overnight window — including weekday 9-5 working hours when the operator is away — voice/push notifications fire normally. Operator needs awareness of pipeline state, workflow failures, and outcome events ("trade completed profit = x", "workflow shutdown") when not at the keyboard.

**Notification Interrupt Conditions (bypass severity ladder):**

Events that interrupt the operator regardless of window state (audio/push allowed inside window for these classes).

| Event class | Threshold | Rationale |
|---|---|---|
| GPU thermal | temp > 85°C sustained 60s | Hardware damage risk; 3090 throttle at 93°C — 85°C/60s gives operator-in-loop time before thermal throttling kicks in |
| Security | fail2ban escalation, SSH breach attempt | Compromise risk; broad framing intentional — operator uses multiple IPs / VPNs, narrower triggers would false-negative |
| Spend burst | > $5 in < 5 min on any single provider | Runaway agent / budget bleed; prepaid keys and provider-side budget caps make this a "something is wrong" signal, not a routine event |
| RAM exhaustion | RAM free < 500 MiB | Kernel OOM-killer territory; threatens Jarvis daemon survival (Hard Constraints) — cascade cannot help |
| VRAM cascade exhausted | VRAM free < 500 MiB AND Quota Cascade in Tier 3 surface | Substrate Pressure Cascade ran out of moves; operator decision required |
| Power *(deferred)* | UPS event / power loss | Not yet wired — no UPS monitoring listener in Phase 2 / v19. Row preserved as doctrine debt; threshold and trigger to be specified when monitoring infrastructure exists. |

Thresholds ratified 2026-05-21 walkthrough Item 5. Power row carried as deferred entry pending listener implementation.

**Queued items batch-surface at window end:** Jarvis emits a morning brief at window end (07:00 default) listing all Tier 2 events from overnight and any Tier 3 items held for surface.

---

## Substrate Pressure Cascade

Jarvis's response to observed VRAM pressure is a **continuous intensity band**, not a sequential layer ladder. Three response kinds — eviction, self-offload, API routing — blend with scaling intensity as pressure rises across the band. Intensity recalibrates automatically as pressure eases. **Pause is not in the toolkit** — Jarvis re-routes work, never blocks it (see Hard Constraints).

**Stateless response:** Jarvis's response to pressure is a function of *current* observed VRAM free, not a function of past escalation state. There is no "exit cascade" logic — as VRAM free rises (because workloads moved, tiers freed, bursts finished), offload intensity drops to match the new pressure point.

### Intensity Band

| Free VRAM | Cascade state |
|---|---|
| > 2.5 GB | Normal operation — no cascade activity |
| 2.5 GB → 500 MiB | **Active band** — offload intensity scales with pressure (three response kinds blend) |
| < 500 MiB | API routing engaged (see "API switchover" below) |

The 2.5 GB / 1.5 GB / 750 MiB / 500 MiB markers are **intensity guideposts**, not discrete trigger thresholds. They describe how the cascade should *feel* across the band — by 1.5 GB free, T2 burst should typically be evicted; by 750 MiB, self-offload should be active when window-gated. The cascade is not implemented as a stack of `if VRAM < N` conditions; it is a continuous-pressure controller selecting the next-cheapest move.

**Percent-of-intensity assignment per response kind is Scope B framework, deferred to stress-testing data.** The spec records the band edges and the three response kinds; numeric calibration of the curve (how much evict vs how much self-offload at a given pressure point) waits for measurement.

### Response Kinds

The three kinds that blend across the intensity band:

**Evict burst and utility tiers.** Standard Tier 2 actions (autonomous-with-log). Priority order: T2 burst (~6.8 GB, call `t2-down`) → T6 burst (~17-19 GB when active, call `t6-down`) → T4 reductions within the tier's own operational range. T3 (CPU-only) and T5 (CPU-only) contribute zero VRAM and are not eviction targets.

**Conditional self-offload (Tier 3 non-blocking).** Jarvis offloads reasoning capacity from VRAM to RAM/CPU. Gated by two conditions:

- **Inside the Overnight Workload Window.** Self-offload during weekday working hours, when the operator is away but expects notifications and possible interactive use upon return, is the wrong move. Outside the window, self-offload is not in the cascade's available moves.
- **Operator does not veto within 120 seconds.** Self-offload fires as a Tier 3 non-blocking action: Jarvis surfaces ("VRAM pressure persists; offloading T1 to RAM in 120s unless you veto"), then default-proceeds at timeout.

Self-offload floor is Scope B framework, value pending measurement: T1 retains sufficient resource for operator-interactive queries and dispatch decisions. Below this floor, further offload is itself a failure mode.

**Route workloads to API.** Engages at the bottom of the intensity band (< 500 MiB free). Workloads route to cloud providers per the Decision 4 cascade, bounded by the Quota Cascade Policy.

### API Switchover

When API routing engages, the mechanism is **switch at next natural workload checkpoint** — token-stream end, batch-item boundary, message-turn end. In-flight GPU work runs to its next checkpoint, then the *next* unit of that workload routes to API. This avoids re-issue/dedup problems from hard-pulling in-flight work.

Under imminent-crash pressure (approaching the 500 MiB floor with no successful checkpoint switchover yet), checkpoint granularity may shorten or be bypassed. Exact escalation behavior is **deferred to implementation against measured failure modes** — Scope B framework only.

Once API is serving the routed workload, observed VRAM free rises and the cascade's intensity automatically recalibrates downward per the stateless-response principle above.

### Routing Constraints

- **Workloads route, the coordinator does not.** Per Hard Constraints, Jarvis identity (daemon, T1, listeners, state) never routes to API. Only workloads — news synthesis, financial analysis, coding bursts, etc. — are eligible for cloud routing.
- **Quota Cascade Policy gates routing depth.** If quota thresholds escalate to Tier 3 mid-cascade, Jarvis surfaces and stops.
- **All routes exhausted → notification interrupt.** If API routing is quota-capped, self-offload is unavailable (outside window) or already maxed, and evictions are exhausted, the cascade has run out of moves. Bypass severity ladder fires: operator notified regardless of window state. See "VRAM cascade exhausted" row in Notification Interrupt Conditions above.

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
- [x] Overnight Workload Window (weekday 23:00-07:00 ET; weekend deferred; Substrate Pressure Cascade gated by window; self-offload floor Scope B framework only) — banked 2026-05-21 walkthrough Item 4
- [x] Bypass severity ladder thresholds (GPU thermal / Security / Spend burst ratified; OOM scoped to RAM; VRAM cascade exhaustion added; Power deferred) — banked 2026-05-21 walkthrough Item 5
- [x] Substrate Pressure Cascade reframe (continuous intensity band 2.5 GB → 500 MiB free VRAM; three response kinds blend; stateless recalibration; checkpoint switchover) — banked 2026-05-21 walkthrough Item 5 (Item 4 refinement)
- [ ] Quota cascade policy thresholds (20% / 10% under prepaid model) — partner-derived from operator constraint; explicit numeric ratification pending
- [ ] Pro tier estimation (~250 msg/5h Pro Max vs ~50 msg/5h standard) (Item 6 — pending)
- [ ] Promotion threshold N (default 10) (Item 7 — pending)
- [ ] Cold-start rule (everything starts Tier 3) (Item 8 — pending)
