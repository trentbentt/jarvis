# Jarvis — CLAUDE.md

Lean entry point for Claude Code sessions on the Jarvis repo. Operating rules,
where to look, what to read. **Not** the doctrine source — see Pointers below.

## Canonical interpreter (read this first)

The Jarvis daemon runs under `~/venv/inference/bin/python3`. This is the shared
monarch-stack venv hosting both inference tier llama-server processes AND
Jarvis itself. The name is a misnomer — it is not inference-only.

**For any test, repl, or one-off validation against Jarvis code, invoke this
interpreter explicitly.** Bare `python3` resolves to system Python and fails on
`import pydantic` (or any other Jarvis dependency).

```bash
# Run a one-off against Jarvis schema:
~/venv/inference/bin/python3 -c "from jarvis.schema import MONARCH_TIERS; print(len(MONARCH_TIERS))"

# Verify the daemon's interpreter matches the one you intend to use:
ps -fp $(pgrep -f daemon.py)
```

## What Jarvis is

The resource manager, orchestration layer, and operator-facing entry point for
the monarch stack. Maintains a continuously-updated model of system state
(VRAM, tier health, workloads, cloud quotas, scheduled events) and gates
autonomous action against the operator's authority spec.

**Current version: v0.2** (snapshot/queue rewrite; RLock contention deadlocks
fixed). Two listeners live (`vram.py`, `tier_health.py`); Phase 2 build queue:
`process.py`, `quota.py`, `cron.py` (per `master_summary_v20.md` §12.4),
`memory.py` (per `MEMORY_ARCHITECTURE_v20.md` §10.2).

## Repo layout

```
daemon.py             ← main process; starts listeners; writes state.json every 10s
deploy.sh             ← creates the `jarvis` window in the `control` tmux session
jarvis/
  schema.py           ← Pydantic models for all 9 domains; MONARCH_TIERS is the tier source-of-truth
  state.py            ← thread-safe StateStore (snapshot-on-read, queue-on-write, single writer thread)
  listeners/
    base.py           ← BaseListener: interval polling, error isolation per thread
    vram.py           ← 5s; nvidia-smi → tier attribution via PID → port → tier
    tier_health.py    ← 15s; HTTP /health polls all service endpoints
bin/
  jarvis-q            ← CLI; reads state.json; subcommands: vram/health/tiers/workloads/quotas/events/all/json
```

## tmux topology (Path B, since 2026-05-21)

Two sessions, not one:

| Session | Lifetime | Hosts |
|---|---|---|
| `control` | long-lived; survives `inference-down` | bootstrap, jarvis, validation-gate, lora-dispatcher, litellm, t1-interactive |
| `inference` | dataplane; cycle-safe | bootstrap, t3-content, t4-phi4, t5-small (+ t2/t6 when burst-up) |

The Jarvis daemon lives in the `control` session. `tmux attach -t control` →
jarvis window. Dataplane cycles via `inference-up` / `inference-down` no
longer affect Jarvis.

## Running and querying

```bash
# Attach to the daemon window:
tmux attach -t control   # → jarvis window

# Query from anywhere on monarch (no live daemon connection needed; CLI reads state.json):
jarvis-q all
jarvis-q vram
jarvis-q health
jarvis-q tiers
jarvis-q events 30
```

## State file

`~/.local/state/jarvis/state.json` — written every 10s by the daemon via
atomic replace (writes `.tmp` then renames). The CLI reads this file directly.

Runtime artifacts are not doctrine (`master_summary_v20.md` §0.1 rule 5).
Stale keys after a code-side rename are pruned and hydrated by
`load_from_disk()` per the D1 patch — see `master_summary_v20.md` §16.1
NEW-v20-1.

## Pointers (source-of-truth)

This file is the lean entry point, not the doctrine source. For anything substantive:

| Question | Read |
|---|---|
| Hardware envelope, tier configuration, doctrine, open queue, audit items | `~/vault/final_master_summary.md` |
| Memory layers, vault structure, Hermes / EverMemOS roles, primary-author table | `~/vault/final_memory_architecture.md` |
| Last session's work, commits, decisions, carry-forward | `~/vault/final_handoff.md` |
| Tier constants (the actual values) | `jarvis/schema.py::MONARCH_TIERS` |
| Live system state | `jarvis-q all` |

Truth hierarchy when these disagree: **monarch disk > git log > `jarvis-q all`
> github.com (raw) > docs > chat history.**

## What Jarvis is NOT

- Not a replacement for `~/bin/inference-up` / `~/bin/t2-up` — those scripts
  manage tier bringup; Jarvis observes and (eventually) routes.
- Not Hermes — Hermes Agent is the L4 agentic working memory + skill layer.
  Jarvis is the Arbiter. See `MEMORY_ARCHITECTURE_v20.md` §3 (four-layer
  model) and §8 (Hermes detail).
- Not 2nd Brain, not Nexus, not EverMemOS — Jarvis observes those layers; it
  does not own their content.

## Updating this file

CLAUDE.md is updated only when the **operating contract** changes —
interpreter path, tmux topology, CLI surface, state file location, or the
role pointers above. Tier configuration, listener cadences, hardware specs,
and doctrine claims live in their canonical source files; do not duplicate
them here.
