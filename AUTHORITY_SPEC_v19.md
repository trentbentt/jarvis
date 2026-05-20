# Jarvis Authority Spec (Decision 5 — Draft)

**Date:** 2026-05-19
**Status:** DRAFT — Decision 5 not yet closed
**Scope:** Jarvis + financial pipeline action surface (per Decision 6)
**Operator confirmation required on:** action lists per tier, sleep window bounds, bypass severity ladder, Pro tier estimation

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
- Restart Jarvis writer thread if deadlock detected (defensive — should never fire under v0.2)
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
| process.py · tier crashed (PID gone, was active) | Restart tier via `inference-up <tier>` | Idempotent; tier_health confirms |
| process.py · tier flapping (restart_count_24h ≥ 3) | Stop restart loop, demote to Tier 3 surface | Don't keep restarting broken things |
| vram.py · burst-only T2 idle > N min | Stop T2 (free 6.8 GB) | N = 30 min default |
| quota.py · DeepSeek V4 Flash spend > 80% monthly | Route subsequent batch calls to Haiku 4.5 | Reversible, free escalation |
| quota.py · LiteLLM tier 1 walled (429) | Escalate to tier 2 provider per Decision 4 cascade | Reversible |
| vram.py · OOM imminent (free < 500 MiB) | Pause lowest-priority active workload | Workload priority TBD |
| cron.py · git repo size > threshold | Schedule `git gc` for next idle window | Reversible |

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
| quota.py · all cheap providers walled | Route to Anthropic API direct | Money-on-line discipline |
| process.py · tier flapping (5+ in 24h) | Pause cron jobs that target tier | User-visible workflow change |
| Retire model from local storage | Delete HF cache entry | Irreversible (re-download cost) |
| Any action in sleep window not meeting bypass | Hold and surface at 07:00 | Voice/notification policy |

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

- [ ] Tier 1 action list (no surprises)
- [ ] Tier 2 action list (especially routing escalations and tier restart policy)
- [ ] Tier 3 action list (especially money-on-line trigger conditions)
- [ ] Sleep window bounds (23:00–07:00 ET assumed)
- [ ] Bypass severity ladder thresholds
- [ ] Pro tier estimation (~250 msg/5h Pro Max vs ~50 msg/5h standard)
- [ ] Promotion threshold N (default 10)
- [ ] Cold-start rule (everything starts Tier 3)
