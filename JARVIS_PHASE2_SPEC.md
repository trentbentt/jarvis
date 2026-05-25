# Jarvis Phase 2 Listener Build Spec

**Date:** 2026-05-19
**Status:** Build spec — listeners not yet implemented
**Substrate:** Jarvis v0.2 (snapshot-on-read, queue-on-write, single writer thread)
**Scope:** process.py · quota.py · cron.py

---

## Architecture Conformance

Every Phase 2 listener must:

1. Inherit from `jarvis.listeners.base.BaseListener`
2. Define `name` (str), `interval_sec` (float), and `poll(self) -> None`
3. Build an update function in `poll()` and queue it via `StateStore.apply(fn)` — never hold the model lock directly
4. Emit events via `StateStore.emit()` — separate ring buffer, no lock contention
5. Wrap every subprocess call with a hard timeout (≤ 3s for fast probes, ≤ 5s for slow probes)
6. Emit events only on state transitions, never every poll (v0.1 spam lesson)
7. Never block on I/O without timeout — listener thread starvation is the prior failure mode

---

## process.py — Per-tier process monitoring

**Interval:** 30s
**Priority:** Build first (highest decision-engine value, smallest scope, reuses vram.py patterns)

**Schema additions to `TierRuntime`:**

| Field | Type | Notes |
|---|---|---|
| `pid` | `Optional[int]` | Current PID; None if tier not running |
| `rss_mb` | `int` | Resident set size in MiB |
| `cpu_pct` | `float` | Rolling-window CPU% (computed across polls) |
| `uptime_s` | `int` | Seconds since current PID started |
| `restart_count_24h` | `int` | Rolling 24h restart counter |
| `last_restart_ts` | `Optional[datetime]` | Wall-clock of most recent restart |

**Poll loop:**

1. For each tier where `config.enabled = True`:
   - Find PID by scanning processes with matching `--port` arg (reuse `_port_from_cmdline()` pattern from vram.py — promote to a shared util in `jarvis/listeners/util.py`)
   - Read `/proc/{pid}/status` for `VmRSS`
   - Read `/proc/{pid}/stat` for `starttime` (uptime) and cumulative CPU time
   - Compute CPU% as delta from previous poll
2. Detect restarts: compare current PID against `self._tier_last_pid[tier_id]`
3. If PID changed and prior PID was not None → restart event

**Restart event emission (state-transition rule):**

- `tier_restart` severity=info if restart_count_24h ≤ 2
- `tier_restart_flapping` severity=warning if restart_count_24h ≥ 3 in 24h window
- Rolling window cleanup: prune `_restart_history` entries older than 24h on each poll

**Internal state:**

```
self._tier_last_pid: dict[str, Optional[int]]   # tier_id → last seen PID
self._cpu_last_sample: dict[int, tuple[float, float]]  # pid → (cpu_time, wall_time)
self._restart_history: dict[str, list[datetime]]  # tier_id → timestamps
```

**Edge cases:**

- Self-monitoring: exclude Jarvis daemon process by PID (`os.getpid()` at startup, store in `self._self_pid`)
- T3 / T5 (CPU-only tiers): no GPU PID in nvidia-smi, so port-based PID discovery is mandatory — do not rely on vram.py's pid_to_tier map
- Transient absence during restart: require 2 consecutive polls with PID=None before flagging tier as stopped
- /proc race conditions: wrap reads in try/except FileNotFoundError, treat as transient

**CLI surfacing:**

`jarvis-q tiers` row gains four columns: `rss`, `cpu%`, `up`, `restarts/24h` (color-coded yellow if ≥3, red if ≥5).

---

## quota.py — LiteLLM spend & token tracking

**Interval:** 60s
**Priority:** Build second (gates Decision 5 authority spec for routing decisions)

**Schema gap CLOSED 2026-05-19:**

~~Two CloudQuota entries added to `_build_initial_model()` to match Decision 4's 5-tier routing chain:~~

**Section DEPRECATED 2026-05-24.** Original instructions specified adding `haiku_4_5` and `anthropic_api_direct` CloudQuota entries. Both are stale:

- **Haiku 4.5 deprecated** (DECISIONS_v19.md 2026-05-24 amendment): pricing parity with DeepSeek V4 Flash at lower capability; removed from cascade entirely. Do not add a `haiku_4_5` entry.
- **Anthropic API direct vestigial** (DECISIONS_v19.md 2026-05-24 amendment): emergency rung is doctrine-forward but not yet wired (operator-confirmed). Add `anthropic_api_direct` only when operational need materializes, not preemptively.

**Schema.py reality check (2026-05-24):** the file defines the `CloudQuota` Pydantic class but no provider name rows are hardcoded there. Provider rows live elsewhere — `_build_initial_model()` location TBD (see HANDOFF follow-up #2). The code block below shows the *original instructed shape* — preserved for historical reference, NOT to be executed as written. Wider sweep of "5-tier" / "haiku" / cascade-hierarchy references elsewhere in this spec ran 2026-05-24: no other references found outside this deprecated block.

Original instruction (historical, do not execute):

```
"haiku_4_5": CloudQuota(
    name="haiku_4_5", provider="anthropic",
    period="monthly", budget_usd=15.0,
    used_usd=0.0, status=QuotaStatus.OK,
),
"anthropic_api_direct": CloudQuota(
    name="anthropic_api_direct", provider="anthropic",
    period="monthly", budget_usd=None,  # money-on-line, no cap, track-only
    used_usd=0.0, status=QuotaStatus.OK,
),
```

OPERATOR TO REVISIT: haiku_4_5 budget cap ($15/mo is a placeholder — confirm against actual baseline after one week of usage).

**Schema additions to `CloudQuota`:**

| Field | Type | Notes |
|---|---|---|
| `tokens_in_today` | `int` | Input tokens, rolling 24h |
| `tokens_out_today` | `int` | Output tokens, rolling 24h |
| `spend_today_usd` | `float` | Spend, rolling 24h |
| `last_call_ts` | `Optional[datetime]` | Most recent successful call |
| `walls_in_window` | `int` | 429 / rate-limit responses in current period |

**Source resolution — LiteLLM postgres logging is DISABLED as of 2026-05-19.**

Confirmed by `grep -i database ~/litellm/config.yaml`:
```
# database_url: DISABLED — LiteLLM internal DB isolation note (see v11)
```

The "see v11" reference indicates this was an intentional disable, likely to keep LiteLLM from writing into the news-pipeline postgres and creating schema collisions. **Do not flip `database_url` back on without reading the v11 rationale first** — there is a real reason it was off.

Three viable paths, ordered by preference:

- **Path A: Give LiteLLM its own postgres database.** Create `litellm_logs` DB (separate from news-pipeline DB on the same postgres instance), set `database_url` to point at it, enable `store_prompts_in_spend_logs: true`. Clean schema isolation, structured queries, the original v11 concern doesn't apply. Adds ~15 min one-time setup before quota.py work begins.
- **Path B: Enable JSON file logging.** Add `json_logs: true` to config.yaml, tail `~/litellm/logs/*.jsonl`. No DB risk, messier parsing, structured-enough to be reliable. Lower setup cost than Path A but quota.py code is more complex.
- **Path C: Defer.** Build process.py and cron.py first; revisit quota.py logging path after Decision 5 is closer to lock so the logging effort is scoped against actual authority spec needs.

**RATIFIED 2026-05-24: Path A** — separate `litellm_logs` DB on the existing postgres instance, `store_prompts_in_spend_logs=false` (cost/token metadata only — no prompt content stored).

Rationale recovered from v19 architectural context (v11 audit detail not preserved verbatim): the news-pipeline postgres backs news data + n8n + `validation_telemetry` + `lora_swap_telemetry`, all with explicit per-table operator-managed schema discipline. LiteLLM's auto-migration of ~12-15 `LiteLLM_*` tables on startup would pollute this clean schema, complicate backups, and create operational coupling. Separate DB on the same instance preserves isolation while still enabling structured `spend_logs` queries from quota.py.

`store_prompts_in_spend_logs=false` chosen because cost tracking needs only metadata (provider, model, tokens, timestamp, cost) — prompt content adds a privacy/liability surface (especially against NDA-tagged work via Anthropic direct) for no gain in the cost-tracking use case. Reversible if a future need surfaces; un-collecting prompts is not.

**Implementation specifics deferred to Claude Code build-time** (against monarch postgres state):
- Postgres role (new dedicated `litellm_user` vs. reuse existing); recommended new role for clean isolation.
- Connection-string mechanics (`LITELLM_DB_URL` in `~/.config/inference/api_keys.env` is the established pattern, separate from the shared `DATABASE_URL`).
- LiteLLM config edits: uncomment `database_url`, add `store_prompts_in_spend_logs: false` under `general_settings`.
- One-time `CREATE DATABASE litellm_logs OWNER <role>;` migration.

Paths B (JSON file logs) and C (defer) are formally ruled out by this ratification.

**Path A spec (ratified 2026-05-24 — Claude Code implementation reference):**

```
SELECT model, SUM(spend), SUM(prompt_tokens), SUM(completion_tokens),
       MAX(start_time), COUNT(*) FILTER (WHERE response_status = 429)
FROM spend_logs
WHERE start_time > NOW() - INTERVAL '24 hours'
GROUP BY model;
```

Use a dedicated Jarvis postgres connection (doesn't exist yet — wire via `psycopg2` or `asyncpg`; add to requirements.txt).

**Pro quota — descoped 2026-05-24.**

Pro is workflow-tier-zero (DECISIONS_v19.md Decision 5 Item 6 closure 2026-05-24; AUTHORITY_SPEC §Quota Cascade Policy "Provider Classes"). Operator-driven, not Jarvis-routed; not in scope for quota.py. Pro auth flows through Claude Code's built-in subscription path, not via LiteLLM — Pro requests would not appear in `spend_logs` regardless. Re-open condition: an automated Pro-1 → Pro-2 → T6 failover mechanism is built.

For cascade routing (DeepSeek V4 Flash ↔ Kimi K2.6 peer rotation, 20% / 10% thresholds, drain phase per-percent notification overlay), AUTHORITY_SPEC §Quota Cascade Policy is canonical. quota.py implements that policy against the prepaid balances of the peer-rotation rung and the emergency rung (Anthropic API direct) when wired.

**Event emission rules:**

| Trigger | Event | Severity |
|---|---|---|
| Quota crosses 80% of budget | `quota_approaching` | warning |
| Quota crosses 100% of budget | `quota_exceeded` | critical |
| First 429 from any provider | `rate_limit_hit` | warning |
| New burst of spend (>$1/min sustained 5min) | `spend_burst` | warning |

State-transition rule applies: don't re-emit `quota_approaching` while staying above 80%.

**CLI surfacing:**

`jarvis-q quotas` shows: name · provider · period · used/budget · % consumed · walls · last_call. Color-code red at ≥100%, yellow at ≥80%.

---

## cron.py — Schedule reconciliation

**Interval:** 60s
**Priority:** Build last (observability-only, no load-bearing decision engine work)

**Schema additions to `Schedule`:**

| Field | Type | Notes |
|---|---|---|
| `cron_entries` | `list[CronJob]` | Parsed from `crontab -l` + `/etc/cron.d/` |
| `missed_runs_24h` | `list[MissedRun]` | Scheduled but no log entry within tolerance |
| `upcoming_60min` | `list[ScheduledRun]` | Next runs in next 60 min with VRAM forecast where known |
| `collisions` | `list[Collision]` | Pairs of jobs scheduled within 5 min of each other |
| `stale_entries` | `list[str]` | Cron entries whose target script doesn't exist |

**Poll loop:**

1. Parse user crontab (`crontab -l` for monarch) and system cron files (`/etc/cron.d/*`)
2. For each entry, compute next N runs using `croniter` library (add to requirements.txt)
3. Cross-reference recent runs against logs:
   - News pipeline: `~/projects/news-pipeline/logs/`
   - Each job has its own log location; build a `JOB_LOG_MAP` constant
4. Detect missed runs: scheduled time + tolerance (5 min) < now and no log entry within tolerance window → missed
5. Detect collisions: pairwise comparison of next-60-min upcoming runs
6. Detect stale entries: target script in cron line doesn't exist on disk

**Event emission:**

| Trigger | Event | Severity |
|---|---|---|
| Job missed scheduled run | `cron_missed_run` | warning |
| Two jobs scheduled within 5 min | `cron_collision_warning` | info |
| Job's target script no longer exists | `cron_stale_entry` | warning |
| Job scheduled in next 60 min with VRAM forecast > headroom | `cron_vram_collision_imminent` | warning |

**VRAM forecasting (optional, defer if complex):**

Maintain a per-job VRAM cost map: `{"news-synth": 6800, "financial-classify": 4200}`. When forecasting upcoming runs, sum projected VRAM cost against current free. This is the path that lets Jarvis say "T6 burst at 09:15 won't fit, headroom -2,400 MiB."

**CLI surfacing:**

`jarvis-q schedule` shows upcoming runs in next 60 min, missed runs in last 24h, collisions. Empty section if nothing to report.

---

## Build Order

1. **process.py** — 2-3 hr active work. Reuses vram.py patterns, smallest scope, immediate decision-engine value (tier restart detection drives Decision 5 Tier 2 actions). **Not blocked by any prereq.**
2. **LiteLLM logging path** — CLOSED 2026-05-24 (Path A ratified, `store_prompts_in_spend_logs=false`). Implementation specifics (postgres role creation, connection wiring, LiteLLM config edits) absorbed into quota.py task — Claude Code handles against monarch state.
3. **quota.py** — 3-4 hr active work. Implementation gated on step 2 + provider rows located/renamed (HANDOFF follow-up #2). (Earlier "schema gap fix already landed (May 19 — 6 quotas in place)" claim was found incorrect 2026-05-24: schema.py has the `CloudQuota` class but no provider rows hardcoded there.)
4. **cron.py** — 2-3 hr active work. Last because observability-only.

Total Phase 2: ~8 hours active work (LiteLLM logging-path prereq closed 2026-05-24 — Path A wiring absorbed into quota.py task), plus soak verification between each listener.

## Soak Discipline (v0.1 lesson)

After each listener lands:

1. Restart daemon, verify `ps -T -p $(pgrep -f daemon.py)` shows +1 thread per listener added
2. Wait 5 min, verify `Updated` timestamp in `jarvis-q` views advances on cadence
3. Verify no event spam (`jarvis-q events 50` shouldn't have repeating warnings)
4. Only then move to the next listener

The v0.1 deadlock was discovered only via soak. Phase 2 listeners add more threads contending on the same writer queue — soak is non-negotiable.

## Out of Scope for Phase 2

- Decision engine (Phase 3): the logic that reads state and decides whether to act per the authority spec
- Voice/TTS layer (Phase 17.5 work, separate)
- Per-tier latency tracking (Phase 3+)
- Multi-host monitoring (single-host system)
