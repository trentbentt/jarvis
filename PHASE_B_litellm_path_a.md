# Phase B — LiteLLM Path A live wiring (gated)

Companion to `jarvis/listeners/quota.py`. Phase A (the listener + schema + CLI)
is built and runs **dormant** until this runbook is executed. Per
`master_summary §12.4` (Path A, ratified 2026-05-24) and the P2-2 design walk
(2026-05-29).

## Why this is gated, not done

1. **Cloud routing is DISABLED** in `~/litellm/config.yaml` — every cloud
   fallback chain is commented out and only `deepseek-v4-flash` is defined (no
   active route to it). Until cloud lanes are restored, `spend_logs` would hold
   only local **$0** rows, so wiring the DB now adds LiteLLM's ~12–15
   `LiteLLM_*` tables + a LiteLLM restart for **zero quota data**.
2. **DB superuser creds required.** `POSTGRES_PASSWORD` in
   `~/.config/inference/api_keys.env` does not authenticate as
   `postgres`/`monarch`/`litellm` on either instance. The one-time DDL needs a
   superuser connection the build agent does not hold.

**Target instance decision (operator, 2026-05-29): `monarch-postgres:5433`**
(not the 5432 news-pipeline instance). Diverges from the doctrine rationale,
which predates 5433's existence; chosen for cleaner separation from
news-pipeline data.

## Steps (run when cloud lanes are restored AND creds are available)

### 1. One-time DDL on monarch-postgres:5433 (as a superuser)

```sql
CREATE ROLE litellm_user LOGIN PASSWORD '<choose-strong-password>';
CREATE DATABASE litellm_logs OWNER litellm_user;
```

### 2. Add the DB URL to api_keys.env (separate from any shared DATABASE_URL)

```bash
# ~/.config/inference/api_keys.env
LITELLM_DB_URL=postgresql://litellm_user:<password>@127.0.0.1:5433/litellm_logs
```

`quota.py` reads `LITELLM_DB_URL`. LiteLLM itself reads `database_url` from its
config (step 3) — keep the two pointed at the same DB.

### 3. Enable spend logging in ~/litellm/config.yaml

Under `general_settings:` (currently `# database_url: DISABLED`):

```yaml
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/LITELLM_DB_URL
  store_prompts_in_spend_logs: false   # cost/token metadata only — no prompt content
```

`store_prompts_in_spend_logs: false` is deliberate: cost tracking needs only
metadata (provider/model/tokens/cost/timestamp); prompt content adds
privacy/NDA surface for no benefit. Reversible; un-collecting is not.

### 4. Restart LiteLLM, let it migrate, confirm tables land in litellm_logs

LiteLLM auto-creates its `LiteLLM_*` tables on first start with a DB. Verify
they are in `litellm_logs` (not the news-pipeline DB).

### 5. Restart the Jarvis daemon

```bash
cd ~/projects/jarvis && ./deploy.sh
```

`quota.py` exits dormant on the next 60s poll once `LITELLM_DB_URL` resolves
and the spend table exists. It self-resolves the table name + timestamp column
(`LiteLLM_SpendLogs.startTime` vs doctrine `spend_logs.start_time`).

## Known limitation carried into Phase B

`walls_in_window` (429 count) is **not** in `spend_logs` — LiteLLM does not
record HTTP status there. `quota.py` leaves it at 0 and does not fire
`rate_limit_hit`. If 429 tracking is needed, introspect `LiteLLM_ErrorLogs` (or
the proxy logs) at Phase B and extend `quota.py._query` accordingly.

## Verify after wiring

```bash
jarvis-q quotas          # deepseek_v4_flash / kimi_k2_6 show spend + last_call
jarvis-q events 50       # quota_approaching / quota_exceeded on threshold crossings
psql "$LITELLM_DB_URL" -c '\dt'   # LiteLLM_* tables present in litellm_logs only
```
