# Bible Audit — Findings from the Full Read

**Audit performed:** 2026-05-21, after operator's push to verify coverage.
**Read against:** Full GitHub repo (19 files, 2,873 lines, never previously accessed); all 5 session PDFs in full; master_summary_v18.md in full; 5_20_26_session2.md in full.

---

## §A — Verifiable failures: things the bible got wrong

These are corrections, not "additional context." If you trust the bible without these patches, you'll trust wrong numbers or claims.

### A1. GitHub repo is PUBLIC, not private — ✅ FOLDED into bible §17.4 (2026-05-22)

- HANDOFF_v19.md line 156-era describes the repo as `(private)`.
- Bible §17.4 said `(private)` by inheritance.
- Actual API response: `"private": false`.
- The doctrine doc itself is drifted on this; bible inherited the drift.

### A2. Three accounts ≠ three Pro accounts — ✅ FOLDED into bible §1 (2026-05-22)

- Bible §1: "Three-account Claude Pro parallelism."
- What operator actually said in bootstrap: "I run three Claude accounts in parallel."
- Pro composition not specified. v18 master summary consistently says "two Claude Pro subscriptions" (lines 151, 273, 1434, 2361, 6007).
- The third account could be free, Workspace, or different. The bible inferred Pro, which is not in evidence.

### A3. CLAUDE.md is materially stale, not "slightly stale"

I described it in bible §17.2 as "slightly stale, v0.1 era." Actual read reveals at least 6 substantive drift items:

| Claim in CLAUDE.md | Actual reality |
|---|---|
| "Current version: v0.1" | v0.2 substrate live (per HANDOFF, repo README, daemon.py) |
| "writes state.json every 30s" (line 12) | Writes every 10s per daemon.py `PERSIST_INTERVAL_SEC = 10` |
| "tmux attach -t inference" (line 33) | Should be `control` per Path B |
| "every 30s by daemon" (line 45) | Wrong, see above |
| T1 context 36K (table line 55) | Schema is 24K (Rebalance Change 2 patched in `c0f7ea7`) |
| References `inference-burst-up/down` (line 90) | These are v16-era scripts. Replaced by t2-up/t2-down |

Tier D3 (CLAUDE.md update) is more urgent than bible portrayed.

### A4. OOM thresholds in vram.py are 2000/500, not 1500/500 — ⚠️ SUPERSEDED 2026-05-22 (commit f0675da reframed cascade as continuous intensity band; discrete thresholds no longer applicable. vram.py still uses 2000/500 in code which now functions as observation guideposts within the band; bible §10.4 updated)

- Bible §3.3 / §9.5 / §12 stated the two-band rule as: "free < 1500 MiB → Tier 2 preemptive burst-tier shutdown; free < 500 MiB → Tier 3 escalation."
- Actual code in `jarvis/listeners/vram.py` lines 23-24:
  - `_OOM_ELEVATED_THRESHOLD_MB = 2000`
  - `_OOM_IMMINENT_THRESHOLD_MB = 500`
- The 1500 number was a *proposed* revision during the Decision 5 walkthrough — not yet implemented in the listener. Bible conflated proposal with code reality.

### A5. State.json schema_version is "0.1.0"

- Bible never mentioned schema versioning explicitly.
- `schema.py` line 360: `schema_version: str = "0.1.0"`.
- The "v0.2 substrate" name refers to the StateStore implementation pattern, not the schema version. They are different things.
- This is also why "schema migration not auto-handled" (small mission #4) matters — the schema_version field exists but no migration logic uses it.

### A6. Quota schema key is `deepseek_v3`, not `deepseek_v4_flash` — ✅ RESOLVED 2026-05-24 (renamed in `jarvis/state.py::_build_initial_model()` lines 225-226)

- Bible §13 noted this as "was V3, needs rename" but stated it as if it were a Phase 2 update item.
- Actual state in `state.py` line 225-228: the schema dict literally has `"deepseek_v3"` as the key.
- This is real drift between Decision 4 (closed on V4 Flash) and the schema. Bible should have flagged it as a small-mission tracked item, not buried in Phase 2 prereqs.

### A7. v18 master summary contains ZERO Hermes references

- Bible §14 stated "Decision 2 cannot be closed without v18-era Hermes brainstorm docs."
- `grep -ni hermes master_summary_v18.md` returns ZERO results.
- The "v18 Hermes brainstorm" is repeatedly referenced in chat as "needs to be pasted" — but the only mention of Hermes in any v18-tier document is in 5_18_26 line 16-17 where the prior-prior session is referenced as having raised Curator/Hermes concerns.
- 5_19_26 line 678 even explicitly says "with the v18 Hermes brainstorm pulled in **if it exists**."
- The Hermes brainstorm probably exists in chat-only context from a session before 5_18_26. It may not be in any standalone doc.
- Bible should have flagged: the prerequisite for Decision 2 may not be a document the operator can produce — it may need to be reconstructed from scratch.

### A8. The 120-second timer is a current-session proposal, not banked doctrine — ✅ RESOLVED 2026-05-22 (commit 414d5b2; 120s timer ratified in AUTHORITY_SPEC Substrate Pressure Cascade Layer 2 / self-offload)

- Bible §3.3 and §9.5 cited "120s timed-default-proceed veto window" as if part of the framework.
- The "120s" number appears nowhere in the project PDFs.
- It was proposed by the operator in *this current session* (the chat that compiled the bible).
- Bible properly attributed it as "in-flight walkthrough" — but the value itself isn't ratified yet.

### A9. Item 4 of Decision 5 walkthrough was NOT banked in 5_21_26_2 — ✅ RESOLVED 2026-05-22 (commit 414d5b2; Item 4 banked as Overnight Workload Window + Substrate Pressure Cascade)

- Bible §9.5 / §12.1: "Item 4 reshaped" status.
- Actual end-of-session state in 5_21_26_2.pdf: session ends mid-Item-4 with three options proposed (lock 23:00–07:00 now / defer / two-window) and the operator's response was a *correction* ("remember t1 is jarvis, t6 is the coder") followed by session end.
- Item 4 status is "discussion in progress" not "reshaped." The reshape happened in *this* current session in response to operator's "Jarvis offload" framing.

### A10. AUTHORITY_SPEC Tier 1 lists ≥10 successful runs as the promotion threshold

- Bible §9.5 said "N=10 proposed default, Item 7 pending."
- Actual AUTHORITY_SPEC_v19.md line 21: "Has run successfully ≥ 10 times without correction" is the criteria for Tier 1 inclusion.
- N=10 is already *written into the draft spec*, not pending. The pending item is "Operator confirms N=10" — which is checklist Item 7, the confirmation, not the value itself.

### A11. Sleep window in schema is 22:30–06:00, not 23:00–07:00 — ✅ RESOLVED 2026-05-22 (commit 414d5b2; schema fields renamed `sleeping_window_*` → `overnight_window_*` and defaults harmonized to 23:00 / 07:00 to match spec)

- Bible repeatedly cited "23:00–07:00 ET" from AUTHORITY_SPEC.
- `schema.py` lines 306-307: `sleeping_window_start: str = "22:30"`, `sleeping_window_end: str = "06:00"`.
- AUTHORITY_SPEC has the proposed 23:00–07:00 but the live schema (which the operator schema points to as "source of truth") has 22:30–06:00.
- Real drift between AUTHORITY_SPEC and schema.py. Bible didn't catch this.

### A12. SystemModel has 9 top-level domains, not 8

- Bible §10/§13 said "Pydantic schema (8 domains)."
- schema.py docstring claims 8 (lines 5-13).
- Actual `class SystemModel` (lines 354-371) has 9 fields: hardware, tiers, workloads, schedule, quotas, resources, operator, events, health.
- The docstring is wrong, and bible inherited it.

### A13. daemon.py creates listeners in `inference` session per docstring; deploy.sh creates in `control`

- Bible §13.1 said "Two listeners running, fed into state.json every 10s" — correct.
- But there's an inconsistency: HANDOFF_v19 line 114 says "Daemon runs as a window in the `inference` tmux session" (pre-Path-B framing), while deploy.sh and the Path B section explicitly put it in `control`.
- HANDOFF has drift within itself — top says inference, Path B section says control. Bible inherited the "control" version but didn't flag that the HANDOFF top section is now wrong.

---

## §B — What's missing entirely from the bible

These aren't corrections — they're things that existed in source and the bible never mentioned.

### B1. Postgres + n8n are tracked health components in Jarvis — ✅ FOLDED into bible §6 (2026-05-22)

- `MONARCH_HEALTH_COMPONENTS` in schema.py lines 413-424 includes:
  - n8n on port 5678 (HTTP /healthz)
  - postgres on port 5432 (TCP only)
- Bible §6 listed validation-gate (4100) and lora-dispatcher (4200) as services Jarvis monitors but omitted n8n and postgres.

### B2. Phase 18 Jarvis port is 4300; Read API is 4400; Command Center PWA is 3000 — ✅ FOLDED into bible §16.2 (2026-05-22)

- v18 master line 133-136 specifies these port assignments.
- Bible §16.2 / §18.5 mentioned Phase 18 and Command Center but omitted ports.
- This matters because Phase 2 listener work and any future Jarvis-API integration needs these port reservations.

### B3. Tailscale Funnel is webhook-restricted, not generally exposed — ✅ FOLDED into bible §2 (2026-05-22)

- v18 master lines 242, 386, 759: Tailscale Funnel exposes `/webhook/` ONLY. n8n UI is behind Tailscale (private). UFW rules enforce this.
- Bible §2 said "Tailscale Funnel exposed" — too loose. The Funnel is restricted by design for security.

### B4. mmap weight sharing is load-bearing for the five-tier architecture — ✅ FOLDED into bible §5.7 (2026-05-22)

- v18 master line 998: T1, T2, and T3 all load the same Qwen3.6-27B UD-Q4_K_XL GGUF. mmap shares the ~17 GB of weight pages across all three processes. **This is the single architectural reason five concurrent tiers fit on monarch.**
- Bible §5 listed T1/T2/T3 individually but never mentioned mmap weight sharing. This is a critical architectural fact.

### B5. Pre-existing burst-mode measured throughput numbers

- v18 master line 1603: Financial Phase A (12 calls × 13K tokens) takes ~3.5 hours standard, ~44 minutes burst. Burst is 4.2× speedup.
- v18 master line 1597: cycle time measured: ~10s burst-up + ~11s burst-down = ~21s total transition overhead.
- Bible §10 mentioned "three-mode VRAM doctrine" but didn't cite these throughput measurements.

### B6. T6 (Qwen3.6-35B-A3B MoE) — actual VRAM is 21 GB pure VRAM, not 17-19 GB with offload — ✅ FOLDED into bible §5.6 (2026-05-22)

- v18 master line 1018: Qwen3.6-35B-A3B at ~21 GB pure VRAM, full speed (MoE 3B active, ~80-100 tok/s with --cache-type-k q8_0).
- Bible §5.6 said "17-19 GB target with 25% expert offload."
- The 17-19 GB figure assumes expert offload reduces VRAM. The 21 GB figure is pure-VRAM no-offload, which v18 says is the standard pattern.
- Decision 3 picks the offload variant. Both numbers are valid for different operational modes; bible mixed them.

### B7. The "improvement ledger" is a buildable v20 item with specific outcome-tracking spec

- v18 master §17.4 documents this as buildable now and specifies that the signal is *outcome*, not model-graded.
- Bible §15.3 mentioned it but didn't surface that the spec is concrete enough to start building. The substrate (operator disposition + downstream outcome capture in n8n workflows) is what gates it, not the spec itself.

### B8. Specific data sources, integrations, and 7-doc rubric system

- v18 master enumerated:
  - 48 news sources seeded across 9 sectors
  - 5 stable Postgres tables for news
  - 7-doc rubric system (PRD, AppFlow_&_Design, Architecture_&_Backend, AIRules_&_Quality, Plan, Security_Checklist, Changelog) — every new pipeline/tool follows this
  - FRED snapshot integration: 7 macro series active
  - Three planned integrations: stack_signals, macro_signals, news_trade_signals
- Bible §7 covered news pipeline at high level but omitted the 7-doc rubric (which is a system-wide discipline rule) and the sector source counts.

### B9. v18 ruled-out list has more entries than bible §20 enumerated

The Appendix A entries I missed include:

- AWQ/GPTQ 4-bit baseline (replaced by UD-Q4_K_XL)
- Cron-scheduled burst window for news synthesis (T2 standard is sufficient for bounded sector synthesis)
- vLLM multi-LoRA hot-swap on Qwen3-Next hybrid architecture (vLLM's SupportsLoRA mixin not implemented for this topology)
- Overnight automated refactoring via qwen-coder-deep
- CUDA 13.2 (gibberish bug)
- DeepSeek R2 (became cloud-only)
- Llama 4 Scout (outclassed by Qwen3.6-35B-A3B)
- Qwen3 32B (superseded by Qwen3.6-27B)

The pointer-only treatment in §20 was lazy; many of these specifically affect v19 design choices.

### B10. 7-doc rubric is canonical discipline, not optional

v18 master Phase 12 documents this as the standard for every new pipeline or tool. Bible §17 covered the four-file documentation pattern (CLAUDE/CONSTITUTION/CONTEXT/reg-blueprint) but completely omitted the 7-doc rubric.

### B11. Validation gate writes to validation_telemetry; LoRA dispatcher writes to lora_swap_telemetry — ✅ FOLDED into bible §6.4 (2026-05-22)

- Both back the same Postgres instance and are joinable on `workflow_id`.
- v18 master describes this as a discipline-layer telemetry feature critical for drift detection.
- Bible §6.4 mentioned validation_telemetry but omitted lora_swap_telemetry and the join pattern.

### B12. _EVENT_BUFFER_MAX = 2000; _WRITE_QUEUE_MAX = 1000

- Specific numeric limits in state.py.
- Bible mentioned "event ring buffer" without numbers.

### B13. The 7 "session_start" / "checkpoint" / "/wrap" rituals

v18 §Documentation Set specifies precise rituals:
- Mandatory session start order: CONSTITUTION → CONTEXT → claude_mem → phase-activate
- Checkpoint compression at every phase completion (mid-session)
- `/wrap` command at session end (Claude Code only)
- Recovery patch on abrupt session end
- 80% context warning at logical boundary
- Model routing rules (Opus for architectural decisions, Sonnet for building)

Bible §17 listed the four files and claude-mem but omitted these operational discipline rules.

### B14. v18 measured tier throughput numbers — ✅ FOLDED into bible §5.7 (2026-05-22)

- T2 5.4 tok/s gen at standard config
- T4 206 tok/s gen
- T2 burst 22.9 tok/s gen

Bible §5 didn't include any measured tok/s numbers.

### B15. CUDA pin and apt-mark holds

- Hardware schema: `cuda_pinned_version: "12.8"`, `cuda_pin_packages: 11` (apt-mark hold count; verify quarterly).
- Bible §2 mentioned CUDA 12.8 pinned but didn't surface the quarterly verification cadence.

---

## §C — What the bible got RIGHT (with read-confirmation)

For the record, things the bible captured correctly per the full read:

- Six cardinal decisions and their close status (1, 4, 6 closed; 2, 3, 5 open)
- Path B dual-session topology partition (control + inference)
- Path B validation evidence (2026-05-21 04:14-04:21 timing, T1 retained 12 GB across move, writer thread 10s cadence)
- Rebalance Change 1 (T2 burst-only) executed and live-validated at 66.0-66.1%
- Rebalance Change 2 patched (commit c0f7ea7), measurement deferred to next T1 restart
- The redesign-over-refine principle anchored to Path B example
- The 80% baseline target line on every jarvis-q vram query
- The IDLE vs UNRESPONSIVE distinction for burst-only tiers (T2_IDLE_MARKER file pattern)
- The validation gate's direct-to-Phi-4 design (not via LiteLLM)
- Phase 17.5 wake word "Okay Comrade", mlx-whisper-large-v3-turbo, OpenWakeWord, Hammerspoon
- Picovoice ruled out for new builds (company email signup blocker May 2026)
- Five planned LoRAs: three high-stakes (consultancy/design/exploratory-coding on dense Qwen3.6-27B), two speed-tier (content/leads on MoE)
- Validation gate thresholds (VOICE 0.70, GROUNDING 0.90)
- Truth hierarchy ordering
- 12 financial pipeline strategy questions
- LiteLLM postgres logging is DISABLED (confirmed in PHASE2_SPEC)
- 6 quota entries in schema (claude_pro_1, claude_pro_2, deepseek_v4_flash, kimi_k2_6, haiku_4_5, anthropic_api_direct)
- All small-mission entries (29 of them)

The structural shape was correct; the specifics had drift.

---

## §D — Method failures I want to name

To be honest about how I got here:

1. **I never opened /mnt/project/ files with `view`.** All project content came via `project_knowledge_search` snippets, which sample fragments. Treating this as "reading" was wrong.
2. **I never accessed the GitHub repo until prompted to audit.** The repo description in HANDOFF was "private" so I assumed I couldn't reach it. Without testing, I missed that it's actually public.
3. **The post-compaction transcript summary said "Assistant has read" — I treated that as if I had read.** Compaction summaries are not equivalent to having the content in context. They are claims about prior context that may or may not have been accurate even then.
4. **I conflated proposed framings with banked doctrine.** Items 4-8 of the Decision 5 walkthrough are in various states of in-flight; I represented them in tabular form as if they had clean status fields.
5. **I deferred to inferred state over verified state.** "Three Claude accounts" → "three Pro accounts" is the canonical example. Reasonable inference, unsupported by chat evidence, and master_summary explicitly contradicts it.

---

## §E — What this means for the bible

The bible's structural shape (sections, cardinals, what Jarvis is, the four-question test, the open queue, the small-missions inventory) survives the audit. The narrative arc is right.

The specifics need a revision pass. Recommend:

1. **Inline corrections** for items A1-A13. Most are surgical edits.
2. **Additions** for items B1-B15 — these are real missing content.
3. **Recompiled honesty section** noting what's verified-against-source vs what's inferred.
4. **The Hermes-brainstorm gap** (A7) is the most consequential single finding because it means Decision 2 may not be closable the way the bible implied — the prerequisite document may not exist.

I can produce a revised v2 of the bible incorporating all of the above, or you can take the audit as a patch list and apply it yourself. Your call.


---

## §F — Audit-of-the-audit (2026-05-22)

### F1. "Charlotte, NC" residence drift was inherited from session user-context

- Bible §1 initial compile recorded operator residence as "Charlotte, North Carolina."
- Operator residence is Raleigh, NC.
- Source of the drift: an earlier session's user-context location guess (Claude infrastructure surfaces the operator's approximate location to itself; that surfaced value was Charlotte, likely from VPN endpoint or ISP geolocation noise) made it into doctrine without verification against the operator.
- The audit itself inherited this drift — the audit's §A entries reference "Raleigh = ET, confirmed" because AUTHORITY_SPEC said so, but the audit never flagged that the bible's Charlotte vs spec's Raleigh was the actual drift, not the inverse.
- **Operator clarification 2026-05-22:** "operator lives in raleigh his identity is not raleigh" — residence is Raleigh, identity is separable from residence (the operator does not want to be doctrinally collapsed into a city).
- ✅ Bible §1 patched 2026-05-22.

### F2. Session-status summary

**Resolved by 2026-05-22 commits or fold:**
- A1, A2, A4, A8, A9, A11 (see annotations above)
- B1, B2, B3, B4, B6, B11, B14 (folded into bible — see annotations above)

**Resolved 2026-05-24:**
- A6 (deepseek_v3 → deepseek_v4_flash renamed in state.py::_build_initial_model())

**Still open (carried forward to future sessions):**
- A3 (CLAUDE.md materially stale — Tier D backlog)
- A5 (state.json schema_version "0.1.0" — small mission #4)
- A7 (v18 Hermes brainstorm may not exist — Decision 2 prereq question)
- A10 (N=10 distinction — Item 7 ratification surfaces this)
- A12 (SystemModel 9 domains vs docstring 8 — cosmetic schema fix)
- A13 (HANDOFF intra-doc drift inference vs control session — Tier D backlog)

**Folded forward but flagged for separate ratification (discipline-additions, not factual drift):**
- B8 / B10 (7-doc rubric as canonical discipline) — deserves its own ratification decision before becoming bible doctrine
- B13 (session_start / checkpoint / wrap rituals) — operational discipline; deserves explicit operator confirmation

**Not folded (minor or covered elsewhere):**
- B5 (financial pipeline burst measurements — covered in §10.3 sequential framing)
- B7 (improvement ledger spec concrete enough to start) — touched in §15.3 already
- B9 (ruled-out list additions) — §20 is pointer-only by design
- B12 (event buffer / write queue numeric limits) — not load-bearing for any current decision
- B15 (CUDA pin quarterly cadence) — minor; deferred

### F3. Audit usage going forward

This audit file becomes a **tracker**, not a content source — the substantive corrections have been folded into the bible. Future sessions should:

1. Treat unresolved §A items as queue entries.
2. Re-run audit-style verification any time bible content gets significantly updated, against monarch disk + github raw.
3. Add new audit entries for any drift surfaced in future sessions (the F1 entry above is the template).
