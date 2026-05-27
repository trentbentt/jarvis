# Monarch Memory Architecture — v20

**Compiled:** 2026-05-26
**Status:** CANONICAL. Single source of truth for monarch's memory architecture across all seven physical layers and four conceptual layers (Truth / Index / Memory / Arbiter).
**Operator:** Trent (residence: Raleigh, NC; identity separable from residence)
**Pairs with:** `master_summary_v20.md` (overall stack doctrine)

**Truth hierarchy for any factual question:** as established in `master_summary_v20.md` §0 and §15.3 — monarch disk > git log on monarch > `jarvis-q all` > github.com (raw) > this document > any chat history. This document is the snapshot; the system keeps moving.

---

## §0 — Propagation Discipline

The five rules from `master_summary_v20.md` §0.1 apply to this document without restatement. One canonical statement per fact. Every section names its source-of-truth file. No editorial parentheticals. No loose ends in code. Runtime artifacts are not doctrine.

**Atomic-update discipline.** Any memory layer change to code lands atomically with the corresponding patch to this document. If memory architecture is being updated in two places, one of them is the wrong place.

---

## §1 — What This Document Is

**Source of truth for:** the four-layer memory architecture model, the Truth-is-primary conflict-resolution rule, the routing table mapping operator/agent questions to memory layers, the primary-author table per content type, per-layer operational doctrine, Hermes Agent's memory-architecture-specific interactions, authority gating for memory writes, per-layer failure modes and recovery patterns, and the Phase 1.5 build sequence rationale.

**Last validated:** 2026-05-26 against master_summary_v20.md §3.1, §9.2 (Decision 2 closure), §9.6 (Decision 6 amendment), §13 (Hermes Agent operational detail), §18 (Memory Architecture pointer).

**Not source of truth for:** Hermes Agent artifact identification and Pattern B partitioning vs n8n (that lives in master_summary_v20.md §13). Decision 5 authority model framework (lives in master_summary_v20.md §9.5). Phase 1.5 build queue status (lives in master_summary_v20.md §16.6 Tier E). Hardware envelope (master_summary_v20.md §2). RAM budget projections (master_summary_v20.md §2).

This document covers memory architecture. master_summary_v20.md covers everything else.

---

## §2 — Why Memory Architecture Is Doctrine-Grade

Memory failures in agentic work surface as financial loss, not as quality regressions. A trade thesis built on stale state in EverMemOS, an agent procedure diverging from its vault note, code knowledge going stale between L3 semantic search and L5 structural graph — these break things that the operator pays for in real money, not in retries.

**Build-it-right principle locked 2026-05-26.** The original v19 framing treated Nexus and 2nd Brain as deferred work because the cost calculus assumed "we can stand them up when we need them." Under build-it-right, that math inverts: the cost of not having them is paid in agent decisions made on incomplete world state, and those costs compound silently until something concrete fails. Decision 6 amendment 2026-05-26 reflects this reversal.

**The seven-technology landscape collapses to four conceptual layers under the elegance test.** Postgres + Redis + repositories + vault are all Truth in different shapes. pgvector + Codebase-Memory MCP + Hermes session search are all Index in different shapes. Hermes Agent and EverMemOS are both Memory in different shapes (working vs long-horizon). Jarvis is the only Arbiter. Seven addressable components, four doctrinal roles, one conflict-resolution rule. That's the elegance test passing.

**Scope of the build-it-right principle.** Applies to memory architecture correctness — layer model, conflict-resolution rule, primary-author assignments, Truth-is-primary discipline. Does not extend to speculative content-scope features whose absence can be added as additive layers rather than rebuilds. NDA isolation is the canonical example: its absence at install does not compound silently into agentic memory failure, so deferring it is a YAGNI call rather than a build-it-right violation. (Clarification added 2026-05-26 from §15 Item 1 walk.)

**Vault hygiene principle.** The vault's value derives from being a high-quality documentation graph — not from comprehensive capture. Folders, templates, or capture conventions that lower friction at the cost of accumulating unprocessed or low-quality content are rejected. Garbage-in produces garbage-out in agent retrieval: low-quality vault content gets embedded by L3, surfaced by L4 retrieval, and treated as Truth by downstream agents — silently degrading every layer above. Four PARA-style additions were evaluated and rejected at install (inbox, templates, journal, people); the rejection is recorded here so it isn't relitigated. (Principle added 2026-05-26 from §15 Item 1 walk.)

---

## §3 — The Four Layers

The architecture is defined by *what each layer owns* and *who writes to it*, not by which tool implements it. Each layer has a fundamentally different write discipline. Mixing write disciplines is what creates conflict zones. Keeping them separated is what makes the system feel designed rather than assembled.

### §3.1 Truth

**Definition.** Authoritative state. The actual facts of the world as monarch knows them.

**Members:**
- Repositories on disk (code; canonical: `~/projects/*/`)
- Postgres (structured data; news corpus, telemetry, validation, financial data, n8n state)
- Obsidian vault (human-curated knowledge; doctrine, project docs, architectural decisions, research notes)
- Redis (live operational state; sub-10ms tick data, position state — joins Phase 1.5 step 6 with financial pipeline)

**Write discipline.** Written by operators and pipelines. Never written by agents directly without authority gating per §9. Each Truth member has a single primary-author per content type (§6).

**Read discipline.** All other layers read from Truth and may cache or derive views. Truth never reads from other layers.

### §3.2 Index

**Definition.** Derived views over Truth, optimized for retrieval at agentic speed.

**Members:**
- pgvector extension on existing Postgres (semantic similarity search over vault notes, code chunks, news corpus)
- Codebase-Memory MCP / Nexus (Tree-Sitter AST knowledge graph; structural code queries: call graphs, import chains, impact analysis)
- Hermes Agent session search (SQLite FTS5; full-text keyword search over conversation history)

**Write discipline.** Written by re-indexers reacting to Truth changes. pgvector indexes refresh on vault note commits and news ingestion. Codebase-Memory's file watcher triggers re-index on repository changes. Hermes session search appends per conversation turn.

**Read discipline.** Index members are consulted by agents (via tool calls) and by Jarvis (when routing questions per §5). Index never modifies Truth; an Index miss surfaces to the agent as "not found in this view," never as a Truth update.

### §3.3 Memory

**Definition.** Agent and world models built from Truth over time. The system's interpretation of what it has observed.

**Members:**
- Hermes Agent — working memory layer: `MEMORY.md` (~2,200 char cap), `USER.md` (~1,375 char cap), `SOUL.md` (agent identity), `~/.hermes/skills/` (reusable procedures), session SQLite at `~/.hermes/state.db`
- EverMemOS — long-horizon temporal memory: MemCells (atomic episodes), MemScenes (thematic clusters), User Profile (continuously evolving), Foresight signals (time-bounded forward inferences)

**Write discipline.** Written by agents based on observation. Memory→Memory writes (agent updating its own MEMORY.md, EverMemOS consolidating MemCells into MemScenes) are inherently low-stakes and run under Decision 5 N=12 promotion after strict cold-start (§9). Memory→Truth writes (an agent proposing to update a vault note or Postgres row) are **always Tier 3** under Decision 5 — operator confirmation required.

**Read discipline.** Memory layers read from Truth and Index freely. Memory layers may also read from each other (Hermes can query EverMemOS for long-horizon context; EverMemOS treats Hermes session SQLite as one of its conversation sources).

### §3.4 Arbiter

**Definition.** Routes questions to the right layer. Observes every layer's health. Writes nothing.

**Member:** Jarvis (single member; see master_summary_v20.md §3.1 for full role taxonomy).

**Write discipline.** None. The Arbiter never writes to any memory layer. Routing decisions and observation events are logged to Jarvis's own `state.json` and event ring buffer, which are not memory layers in this taxonomy — they are operational telemetry for Jarvis itself.

**Read discipline.** Arbiter reads health signals from every layer (§10), and reads from layers as part of routing decisions (e.g., "is this question best answered by L4 or L6"). The Arbiter has no authoritative knowledge of its own; it is purely a router and observer.

---

## §4 — The Single Conflict-Resolution Rule

**Truth is primary. Everything else is derived.**

This is the only rule needed to resolve every cross-layer conflict that can arise in the architecture. Applied consistently, it eliminates the entire class of "two layers both claim to know the current state of X" problems.

### §4.1 The four worked examples

**Operator preferences.**
- Truth: Obsidian vault, file `<vault>/operator.md`
- Derived (Memory): Hermes `USER.md` auto-syncs from vault; EverMemOS User Profile is seeded from vault
- On conflict: vault wins. Hermes `USER.md` is regenerated; EverMemOS profile is reseeded.

**Stable procedures (skills).**
- Truth: `~/.hermes/skills/<skill-name>/SKILL.md` (the executable form)
- Derived: Vault may carry a pointer note ("how to run X — see Hermes skill `run-x`")
- On conflict: skill file wins. Vault pointer is corrected to match.

**Code knowledge.**
- Truth: Repository file on disk
- Derived (Index): pgvector chunk embeddings; Codebase-Memory AST graph
- Derived (Memory): Hermes skill that references a specific function
- On conflict: repository wins. pgvector re-embeds. Codebase-Memory re-indexes via file watcher. Hermes skill referencing a renamed function is flagged (§11.4) and either updated by operator-explicit edit or deprecated.

**Current vs historical state.**
- Truth (current): Postgres row, Redis key
- Memory (historical): EverMemOS MemScene representing "what's true about this engagement now" as of last consolidation
- On conflict: Truth wins for "what is true now." EverMemOS is not consulted for current-state queries. EverMemOS is consulted for "how did we get here" and "what trajectory was the state on."

### §4.2 The test for any future addition

When a new memory tool or technology is proposed, the test is:

1. **Does it write to Truth?** If yes, it must replace or extend an existing Truth member with explicit doctrine. If no, proceed.
2. **Does it write derived state?** If yes, it joins Index or Memory based on whether the writes are reactive (Index) or interpretive (Memory).
3. **Does it route or arbitrate?** If yes, it extends Jarvis, not a peer layer. There is one Arbiter.
4. **Does it claim to know current state independently?** If yes, the proposal is rejected — that's a Truth duplication and the source of conflict.

Most proposals will fail one of these tests. That's the architecture working as intended.

---

## §5 — Routing Table

The Arbiter's job concretely. When the operator or an agent asks a question, Jarvis routes it to the layer that owns the answer. This table is the most-referenced page in the document.

### §5.1 Operator-facing questions

| Question shape | Routes to | Notes |
|---|---|---|
| "What's my preference for X?" | L6 vault (Truth) | L4 USER.md is fast-path cache; vault is canonical |
| "What did we discuss last week about X?" | L4 Hermes session search | FTS5 keyword search |
| "How do I do X?" (stable procedure) | L4 Hermes skill | `~/.hermes/skills/` |
| "How do I do X?" (project-specific / exploratory) | L6 vault | Project notes |
| "What does function X do / who calls it?" | L5 Codebase-Memory MCP | AST graph query |
| "Find code similar to X" | L3 pgvector over repo embeddings | Semantic |
| "What's the current state of trade X?" | L1 Redis | Sub-10ms |
| "What does the news corpus say about X?" | L3 pgvector over news embeddings | Semantic |
| "How has client engagement X evolved over months?" | L7 EverMemOS | Temporal trajectory |
| "What's the Foresight on macro regime X?" | L7 EverMemOS | Time-bounded inference |
| "What do we know about person/entity X?" | L7 EverMemOS profile (if person) OR L6 vault (if project/domain) | Disambiguation by content type |
| "Where's the doc for X?" | L6 vault | Documentation router role per master_summary_v20.md §3.1 |

### §5.2 Agent-facing tool calls

Agents (Hermes Agent primarily) issue tool calls that route directly to layers without Jarvis arbitration. The routing here is configuration, not runtime decision:

| Tool / capability | Layer | Endpoint |
|---|---|---|
| Vault read/write | L6 | kepano/obsidian-skills (filesystem access) |
| Code semantic search | L3 | pgvector via Postgres connection |
| Code structural query | L5 | Codebase-Memory MCP (`mcp://codebase-memory`) |
| Session history | L4 | Hermes built-in session search |
| Skill load | L4 | Hermes built-in skill discovery |
| Operator preferences | L4 read → L6 if uncached | Hermes USER.md fallback to vault |
| Current trading state | L1 | Redis client (when financial pipeline lands) |
| Historical engagement state | L7 | EverMemOS API |

### §5.3 Multi-layer queries — composition pattern

Some operator questions require composing across layers. The pattern:

**"What's the current state and trajectory of trade X?"**
1. Query L1 Redis for current state
2. Query L7 EverMemOS for trajectory
3. Compose answer with L1 result authoritative for "now" and L7 contextualizing "how we got here"
4. Never trust L7 alone for current state — even if it's recent

**"What does the codebase say about pattern X, and what have we written about why we use it?"**
1. Query L3 pgvector + L5 Codebase-Memory for code
2. Query L6 vault for architectural decision notes
3. Compose with vault explaining intent and code showing implementation

**"Has this kind of task come up before, and what did we do?"**
1. Query L4 Hermes session search for past instances
2. Query L4 Hermes skills for stable procedures
3. Query L6 vault for project notes if exploratory
4. L4 owns "what we did" history; L6 owns the structured record

The composition pattern is operator/agent-side, not Jarvis-side. Jarvis routes the individual sub-queries; the agent or operator composes the answer.

---

## §6 — Primary-Author Table

Per content type, exactly one layer owns writes. This is the conflict-prevention spec — applied consistently, the four conflict zones from the design conversation (operator preferences, stable procedures, code knowledge, current vs historical state) cannot produce contradictions.

| Content type | Primary author | Read-replicas (derived) | Authority gating for writes |
|---|---|---|---|
| Operator identity / preferences | L6 vault — `<vault>/operator.md` | L4 USER.md (auto-sync), L7 user profile (seeded) | Operator-direct edit (Tier 0 — outside Jarvis authority surface) |
| Architectural decisions (e.g., this doc) | L6 vault | None | Operator-direct edit; agents propose via Tier 3 |
| Project doctrine (CONSTITUTION.md, CONTEXT.md) | L6 vault | None | Operator-direct edit; agents propose via Tier 3 |
| Stable reusable procedures | L4 Hermes skill (`~/.hermes/skills/`) | L6 vault pointer notes; Hermes drafts at `~/.hermes/skill-drafts/` per §8.4 | Operator approval (Tier 3) of Hermes-drafted candidates via `approve-draft` OR operator-direct promotion via `promote-skill`; Curator-the-grader disabled |
| Exploratory / project-specific procedures | L6 vault note | None | Operator-direct edit |
| Code | Repository file on disk | L3 pgvector embeddings; L5 Codebase-Memory AST nodes | Operator-direct via git; agents commit via authority-gated PRs |
| News corpus | L2 Postgres (`news_unified`, etc.) | L3 pgvector embeddings | Pipeline-write (n8n cron); agents read-only |
| Validation telemetry | L2 Postgres (`validation_telemetry`) | None | Validation gate writes; agents read-only |
| Live trading state | L1 Redis | Snapshotted into L2 Postgres periodically | Trading pipeline writes; agents read-only |
| Hermes working memory (MEMORY.md, USER.md) | L4 (Hermes itself) | None | Memory→Memory autonomous after Decision 5 promotion; cold-start Tier 3 |
| Hermes session history | L4 (Hermes SQLite) | None | Append-only by Hermes; no gating needed |
| EverMemOS MemCells / MemScenes | L7 (EverMemOS itself) | None | Memory→Memory autonomous; cold-start Tier 3 |
| EverMemOS profile updates | L7 with vault seed | L4 USER.md may pull subset | Memory→Memory autonomous; cold-start Tier 3 |
| Long-horizon engagement state | L7 EverMemOS | None | Memory→Memory autonomous |
| Foresight signals (temporal predictions) | L7 EverMemOS | None | Memory→Memory autonomous; consumed by trading pipeline read-only |

**Rule:** if a layer is not listed as primary author for a content type, it does not write that content type. Period. Read-replicas refresh from primary author; they never source-of-truth themselves.

---

## §7 — Per-Layer Operational Detail

For each of the seven physical members (L1 Redis through L7 EverMemOS), the on-disk location, access pattern, Jarvis observation surface, and failure-mode preview. Full failure mode and recovery doctrine in §11.

### §7.1 L1 — Redis (Truth: hot operational)

**Status.** Not built. Joins Phase 1.5 step 6 with the financial pipeline.

**On-disk location.** TBD at build time. Likely Docker container alongside existing Postgres + n8n.

**Access pattern.** Sub-10ms reads via `redis-cli` or client library. Primary consumer is the financial pipeline's tick data ingestion and live position state.

**Jarvis observation.** `redis-cli ping` for liveness; `INFO memory` and `INFO clients` for activity signals. Add as health component in `MONARCH_HEALTH_COMPONENTS` per Phase 2 listener work.

**Authority concern.** None. Pure operational store. Writes come from trading pipeline; agents are read-only.

### §7.2 L2 — Postgres (Truth: structured relational)

**Status.** Live since news pipeline Phase 1 (2026-05-15). Already health-monitored.

**On-disk location.** Docker container; data volume on `/home/monarch` NVMe.

**Access pattern.** SQL via psycopg2 / asyncpg / LiteLLM's connection pool. Backed by ~79 tables across news, n8n, validation, LoRA telemetry surfaces.

**Jarvis observation.** Already in `MONARCH_HEALTH_COMPONENTS` (TCP check on 5432). Row-count deltas and query latency as activity signals (deferred to `quota.py` / `process.py` extensions).

**Authority concern.** None for raw operational writes. Agent-proposed schema changes or row-level writes to authoritative tables (e.g., `validation_telemetry`) go through Tier 3 per Memory→Truth gating.

### §7.3 L3 — pgvector (Index: semantic)

**Status.** Not built. Phase 1.5 step 2 — one `CREATE EXTENSION vector;` against existing Postgres instance.

**On-disk location.** Extension lives inside Postgres; no separate process or storage.

**Access pattern.** SQL with `vector` column type and `<->` distance operator. Embeddings populated by re-indexers (vault watcher, news ingestion, code chunker).

**Embedding model selection.** TBD at build time. T5 (always-on CPU tier, zero VRAM) is the natural local embedding server for small-to-medium jobs; larger jobs route to cloud via LiteLLM. Decision deferred to Phase 1.5 step 2 implementation.

**Install scope (locked 2026-05-26 from §15 Item 3 walk).** Vault notes only at P1.5-2 install. Code chunks and news corpus are not embedded at install — each future corpus admitted to pgvector goes through the explicit expansion ritual below. This is the vault hygiene principle (§2) applied to the index layer: garbage embeddings degrade retrieval quality silently, and each corpus admitted imports its own quality profile.

**Index expansion ritual (locked 2026-05-26).** Each corpus admitted to pgvector after install requires four steps:

1. **Justification.** A concrete use case documented as a §16 open item in master_summary_v20.md: proposed corpus, primary consumer, expected retrieval pattern, why existing layers (L5 structural for code, raw Postgres queries for news) don't satisfy the need.
2. **Quality gate.** Filtering rules specified before any embedding (e.g., for code: exclude `node_modules/`, build artifacts, generated files; for news: exclude stub-level articles, exclude degraded sources per master_summary_v20.md §16.7 M11).
3. **Atomic landing.** Doctrine amendment patch to this §7.3 lands in the same commit as the indexer config change per master_summary_v20.md §0.1 rule 4.
4. **Post-deploy validation.** Retrieval quality spot-checked on representative queries before the expansion is declared complete. If retrieval quality drops on existing corpora due to the new content, expansion is rolled back.

**Jarvis observation.** Extension version query for liveness; index build time and retrieval latency as activity signals. Adds one row to `MONARCH_HEALTH_COMPONENTS` or piggybacks on existing Postgres check.

**Authority concern.** None. Index layer. Re-indexers react to Truth; embeddings never modify source content.

### §7.4 L4 — Hermes Agent (Memory: agent working memory)

**Status.** Not built. Phase 1.5 step 4. See §8 for full memory-architecture-specific detail.

**On-disk location.** `~/.hermes/` (state.db, skills/, memory.md, user.md, soul.md). Per-project `~/.opencode/skills/` for cross-agent discovery.

**Access pattern.** Hermes daemon process listening on its own OpenAI-compatible endpoint. Operator interacts via Hermes CLI; agents and tools interact via HTTP API. Jarvis dispatches work to Hermes via the same HTTP surface.

**Jarvis observation.** `hermes memory status` CLI command; SQLite file mtime on `~/.hermes/state.db`; HTTP `/health` on Hermes daemon port. Add as health component.

**Authority concern.** Significant — see §9. Memory→Memory writes (MEMORY.md, USER.md) under N=12 promotion; Memory→Truth writes (vault edits proposed by Hermes) always Tier 3; skill creation always Tier 3 (Curator disabled).

### §7.5 L5 — Codebase-Memory MCP / Nexus (Index: structural)

**Status.** Not built. Phase 1.5 step 3.

**On-disk location.** Single statically-linked C binary; SQLite database at TBD path (likely `~/.codebase-memory/<repo-name>.db` per repo, or unified DB with repo namespacing). File watcher monitors `~/projects/` for changes.

**Access pattern.** MCP server exposing 14 structural query tools (per arXiv 2603.27277). Agents consume via MCP protocol; Jarvis observes via health endpoint.

**Jarvis observation.** MCP `/health` endpoint; file watcher activity (re-index event rate). Add as health component.

**Authority concern.** None. Index layer. File watcher reacts to repo changes; the graph never modifies source code.

### §7.6 L6 — Obsidian vault / 2nd Brain (Truth: human-curated knowledge)

**Status.** Not built. Phase 1.5 step 1 — first step in the locked sequence because every downstream layer either reads from or seeds from the vault.

**On-disk location.** `~/vault/` on monarch's NVMe. Single monolithic vault — no per-project subdivision, no NDA-isolation pattern at install (deferred per §15 Item 1 closure 2026-05-26; subfolder + indexer-exclusion mechanic prescribed for future amendment if NDA-tagged content later requires vault isolation). Doctrine-first hierarchy with the master summary at vault root:

```
~/vault/
├── .gitignore                           # OS artifacts, credential safety net, reserved private subdirs
├── operator.md                          # L4 USER.md syncs from this exact path
├── README.md                            # vault entry point
├── final_master_summary.md              # root of the documentation graph
├── final_memory_architecture.md         # parallel doctrine doc for memory layers
├── final_handoff.md                     # active session log
├── skills/                              # kepano/obsidian-skills + operator-promoted skills (§8.4)
├── archive/                             # superseded; sunsets when superseded
│   ├── master_summary_v19.md
│   ├── INFRASTRUCTURE_BIBLE_v19.md
│   ├── AUTHORITY_SPEC_v19.md
│   ├── DECISIONS_v19.md
│   ├── REBALANCE_v19.md
│   ├── JARVIS_PHASE2_SPEC.md
│   └── BIBLE_AUDIT_findings.md          # sunsets at P1.5-1; §16.1 in final_master_summary.md is canonical going forward
└── projects/                            # per-subsystem documentation; populated organically
    ├── jarvis/
    ├── news-pipeline/
    ├── evidence-layer/
    ├── financial/
    └── ...
```

The `final_` prefix on the three canonical-root docs signals canonical-final status — no further version-suffix bumps, in-place updated via git commits. Archive-folder docs retain their version suffixes because they correspond to historical doctrine versions. No PARA-style additions at install (`inbox/`, `templates/`, `journal/`, `people/` evaluated and rejected per the vault hygiene principle in §2).

**Two-git-repo distinction (locked 2026-05-27).** The vault is a separate git repository from the monarch code repositories by deliberate design, not by convention. Code repositories (`~/projects/jarvis/` and future monolithic codebase subdirectories) are indexed by Codebase-Memory MCP — AST graph, symbol navigation, structural queries — and benefit from monolithic organization where cross-project symbol resolution works natively. The vault is indexed by pgvector (semantic, §7.3) and Obsidian backlinks (graph traversal), and benefits from isolation so vault-agent interactions (Hermes reads, operator edits via Obsidian UI or SSH) do not require code-repo write access or create merge-conflict surfaces with code tooling. The monolithic codebase principle applies to code repos only; the vault being a separate git repo is the correct architectural choice, not a default.

**Truth-singularity (multi-device, locked 2026-05-26 from §15 Item 7 walk).** Monarch is the sole Truth location for the vault. No multi-source replication; no MacBook-resident vault copy. MacBook accesses the vault remotely via SSH and/or Tailscale. Divergence vectors are zero by construction. Whether MacBook editing uses SSH-terminal only or also mounts `~/vault/` via Tailscale/SSHFS for native Obsidian UI is implementation-grade and decided at P1.5-1 build time — both implementations preserve the doctrine.

**Migration pattern at P1.5-1 (locked 2026-05-27).** Doctrine docs MOVE from `~/projects/jarvis/` to vault root at vault init — they do not copy or symlink. Specifically: `master_summary_v20.md` → `~/vault/final_master_summary.md`; this document (`MEMORY_ARCHITECTURE_v20.md`) → `~/vault/final_memory_architecture.md`; `HANDOFF_v19.md` → `~/vault/final_handoff.md`. The seven v19 archive docs (AUTHORITY_SPEC, DECISIONS, REBALANCE, INFRASTRUCTURE_BIBLE, JARVIS_PHASE2_SPEC, master_summary_v19, BIBLE_AUDIT_findings) move to `~/vault/archive/`. After migration the vault is canonical; the jarvis repo retains pre-migration git history for these files but loses the working files themselves. CLAUDE.md in the jarvis repo updates its Pointers table to vault paths in the same P1.5-1 session. §0.2 of `final_master_summary.md` self-updates in the vault initial commit so the file's first canonical version is already self-consistent. Truth-singularity is preserved by deletion-from-jarvis-after-copy-to-vault — at no point do two files claim canonical status.

**Remote policy (locked 2026-05-27).** Vault is initialized with a private GitHub remote at P1.5-1 and pushed with the initial commit. The remote closes the `master_summary_v20.md` §16.8 gap #8 (no documented vault backup beyond Postgres cron). Initial vault content is doctrine docs (non-NDA, non-credential); pre-excluded private subfolders (`private/`, `nda/`, `sensitive/`, `trading-edge/`) carry forward future NDA isolation amendment per §15 Item 1. Credential patterns (`*.env`, `*.key`, `*secret*`, `*credential*`, etc.) are catchall-excluded in `.gitignore` as defense against accidental credential commits. MacBook clones the vault read-only via Tailscale when needed; primary access remains SSH/SSHFS to monarch per Truth-singularity. The vault repo and the jarvis repo are siblings — neither is a submodule of the other; both push independently.

**Access pattern.** Filesystem reads/writes by operator (directly on monarch or remotely via SSH/Tailscale). Agent access via kepano/obsidian-skills (filesystem-based skill set, native Hermes integration). Git history provides full audit trail. Git-versioned from initialization.

**Jarvis observation.** Vault directory mtime; `git log --oneline -n 20` for recent activity; commit rate as activity signal; orphan note detection (notes with no backlinks) as periodic check.

**Authority concern.** L6 is Truth — operator-authored. Agent-proposed vault edits via Hermes always Tier 3. Doctrine docs (this file, final_master_summary, final_handoff) migrate in at initialization as committed history.

### §7.7 L7 — EverMemOS (Memory: long-horizon temporal)

**Status.** Not built. Phase 1.5 step 5.

**On-disk location.** EverMemOS self-hosted deployment: Elasticsearch (BM25 keyword index), Milvus (vector index), relational DB for structured MemCells/MemScenes. Likely Docker containers alongside existing Postgres + n8n. Data volumes on `/home/monarch` NVMe.

**Access pattern.** EverMemOS REST API. Seeded at initialization from vault profile. MemCells form on conversation ingestion; MemScenes consolidate on cron cadence; Foresight signals emit on temporal-pattern detection.

**Jarvis observation.** Elasticsearch health endpoint; Milvus health endpoint; EverMemOS service health endpoint; MemCell creation rate, MemScene consolidation rate as activity signals.

**Authority concern.** Memory→Memory writes (MemCell creation, MemScene clustering, profile updates) autonomous under N=12 framework. Memory→Truth writes (EverMemOS proposing to update vault profile based on consolidated observations) always Tier 3.

---

## §8 — Hermes Agent in Depth

Hermes is the memory layer with the most surface area and the most authority interaction. v20 §13 carries the canonical artifact identification, Pattern B partitioning vs n8n, and operational integration. This section covers the memory-architecture-specific detail: how Hermes's internal memory components map to the four-layer model, how Truth→Memory sync flows work concretely, and how Hermes-internal operations (skill creation, Curator, external providers) interact with the architecture.

### §8.1 Hermes file-backed memory anatomy

| Hermes component | Path | Cap | Role in four-layer model | Primary author |
|---|---|---|---|---|
| `MEMORY.md` | `~/.hermes/MEMORY.md` | ~2,200 chars | L4 Memory (agent working memory) | Hermes (Memory→Memory) |
| `USER.md` | `~/.hermes/USER.md` | ~1,375 chars | L4 Memory (operator preferences cache) | Auto-sync from L6 vault |
| `SOUL.md` | `~/.hermes/SOUL.md` | ~1,000 chars (typical) | L4 Memory (agent identity / system prompt extension) | Operator-direct edit |
| `~/.hermes/skills/<name>/SKILL.md` | per-skill | None | L4 Truth (executable procedures) | Operator-explicit promotion |
| Session SQLite | `~/.hermes/state.db` | None (FTS5-indexed) | L4 Memory (conversation history) + L4 Index (session search) | Hermes append-only |
| External provider configs | `~/.hermes/providers/*.yaml` | None | Disabled at install | Per-provider doctrine decision required |

All caps are Hermes-enforced; exceeding them triggers aggressive prioritization (early memories may be overwritten). The caps are not the operator's enforcement burden — they are Hermes's design constraint reflecting the system-prompt injection model.

### §8.2 USER.md auto-sync from vault — the Truth→Memory data flow

The single most consequential data flow in the architecture: how operator identity in the vault propagates to Hermes's working memory without becoming a divergence vector.

**Pattern.**
- L6 vault file `<vault>/operator.md` is Truth for operator identity and preferences.
- L4 Hermes `USER.md` is a cache that gets regenerated from `<vault>/operator.md` whenever the vault file is modified.
- Sync is one-way: vault → Hermes. Hermes never writes back to vault without Tier 3 authority gating.

**Mechanism.** Vault file watcher (could be a small standalone process, or piggyback on Codebase-Memory's file watcher which runs anyway, or implemented as a Hermes skill that fires on a cron) detects mtime change on `operator.md`, reads the vault file, transforms to the USER.md format (token-capped, structured), writes to `~/.hermes/USER.md`. Hermes picks up the new USER.md on next session start.

**Conflict resolution.** If Hermes has autonomously updated USER.md mid-session (autonomous Memory→Memory write) and the operator simultaneously edits `<vault>/operator.md`, the vault wins. Hermes's autonomous edits are reverted; the vault re-syncs cleanly. The operator can always overwrite the cache by editing Truth.

**What this does not include.** Bidirectional sync. Hermes writing learned preferences back to the vault. Both are explicitly out of scope — they are exactly the patterns that would create divergence. If Hermes observes a preference change worth promoting to vault, that's a Memory→Truth proposal under Tier 3 authority gating (§9), surfaced to the operator for explicit confirmation. The operator edits the vault. Sync flows down.

### §8.3 Skill promotion ritual — vault note → SKILL.md

Skills are Truth (executable procedures stored in `~/.hermes/skills/`). Vault notes are also Truth (human-readable documentation). The boundary between them is **stability and reusability**.

**A procedure is a vault note when:**
- It's exploratory or one-off
- It's project-specific
- It's still evolving
- It's documented primarily for human reading

**A procedure graduates to a Hermes skill when:**
- It's stable (operator has used it the same way multiple times)
- It's reusable across projects or contexts
- It's mechanical enough that an agent should be able to execute it from the documentation

**Promotion is operator-explicit only.** No N-uses counter. No autonomous promotion. The operator decides. The Curator (Hermes's built-in autonomous skill grader) is disabled at install precisely to prevent autonomous promotion.

**Ritual (deferred to Phase 1.5 step 4 build time):** A script or Hermes skill that takes a vault note path and produces a draft `SKILL.md` at the proper location, with frontmatter, structured format, and a pointer note added to the vault that says "this procedure promoted to Hermes skill `<name>` on `<date>`." The operator reviews the draft, commits it.

### §8.4 Curator disabled — what that means concretely

The Curator is Hermes's autonomous skill grading and library consolidation loop. By default (v0.12+), it runs on a cron cycle: reviews recently-created skills, grades them on quality criteria, consolidates similar skills, deprecates unused ones, and may autonomously promote conversation patterns into new skills.

**On monarch, Curator is disabled at install.** Concretely:

- The cron entry that runs the Curator loop is not enabled in Hermes config
- Hermes's autonomous skill creation hook (which fires after multi-step task completions) is **routed to the draft-state pattern below** (closure 2026-05-26 from §15 Item 4 walk) — operator approval required before promotion to Truth
- Curator-related notification channels (skill quality alerts, deprecation suggestions) are off

**Re-open conditions for enabling Curator:**

1. Memory architecture has run stably for at least 30 days of active operator use
2. At least 12 operator-explicitly-promoted skills exist in `~/.hermes/skills/` providing a baseline corpus
3. Operator has reviewed the Curator's quality criteria and explicitly opted in
4. The decision is logged as a new entry in master_summary_v20.md §16 with explicit rationale

Until those conditions are met, all skill creation flows through the draft-state pattern (operator-approval-gated) per §8.3 and the spec below. This is the operationalization of the "Curator narrow-scope or disabled" constraint from the original v18-era Hermes brainstorm framing, applied to the actual Nous Research artifact.

**Draft-state pattern (specified 2026-05-26 from §15 Item 4 walk).**

*Draft location.* `~/.hermes/skill-drafts/<name>/SKILL.md` — sibling to `~/.hermes/skills/`. Separate directory so drafts are unambiguously not Truth. Any agent reading `~/.hermes/skills/` sees only approved skills; drafts only surface via explicit review tooling. No frontmatter-based draft/approved distinction inside the same directory.

*Approval ritual.* `approve-draft <name>` — implemented as a Hermes skill (steady-state, conversational) and a bin script (bootstrap + pre-Hermes fallback) per the hybrid mechanism. Steps:

1. Validate draft passes basic structure check (frontmatter complete, body non-empty)
2. Move `~/.hermes/skill-drafts/<name>/` → `~/.hermes/skills/<name>/`
3. Update frontmatter: add `approved_by: operator`, `approved_date: <ts>`, remove draft-status flag
4. Commit the move in git as a single atomic operation
5. Optionally add vault pointer note: "skill `<name>` promoted from Hermes-drafted candidate on `<date>`"

*Two promotion paths coexist.* Both produce SKILL.md at `~/.hermes/skills/<name>/`:

- *Draft approval path* — Hermes autonomously drafted; operator approves via `approve-draft`
- *Operator-direct path* — operator notices a stable vault procedure worth promoting; runs `promote-skill <vault-path>` (Hermes skill + bin script hybrid) to generate SKILL.md from the vault note

Bin script handles bootstrap (first `~/.hermes/skills/approve-draft/SKILL.md` and `~/.hermes/skills/promote-skill/SKILL.md` are hand-written; thereafter Hermes-skill path is canonical) and pre-Hermes fallback.

*Draft TTL.* No auto-expiration — auto-deletion of Hermes-drafted work introduces a "Hermes deleted my draft before I could review it" failure mode worse than the graveyard problem. Instead: stale drafts (>30 days unreviewed, threshold tunable) surface as Tier 2 events via the future `memory.py` listener per §10.2. Operator decides per draft: approve, edit, or discard.

*Review surface.* New `jarvis-q skill-drafts` CLI subcommand (modeled on `jarvis-q quotas`): lists pending drafts with name, age, source-of-draft (which conversation Hermes synthesized from, captured in SKILL.md frontmatter), and one-line description.

*Authority gating for skill actions.* Operation-level tiers extending the §9.1 two-axis framing:

| Action | Authority tier | Rationale |
|---|---|---|
| Hermes drafts candidate to `~/.hermes/skill-drafts/<name>/` | Tier 2 — autonomous-with-log | Draft is candidate, not Truth; surfaces via `jarvis-q skill-drafts` |
| Operator runs `approve-draft <name>` | Tier 3 — operator-explicit | Promotes draft to Truth at `~/.hermes/skills/<name>/` |
| Operator runs `promote-skill <vault-path>` | Tier 3 — operator-explicit | Direct vault-procedure promotion bypassing draft state |
| Curator-the-grader autonomous consolidation/deprecation | Disabled | Per §8.4 re-open conditions (30 days + 12 promoted skills + opt-in) |

### §8.5 External memory providers — all disabled at install

Hermes Agent ships with optional integrations to external memory services: Honcho (dialectic user modeling), Mem0 (vector memory), Hindsight (knowledge graph), Holographic (local vector), RetainDB, ByteRover, Supermemory, OpenViking.

**All disabled at install on monarch.** The architecture already covers each use case through native layers:

| External provider | What it would provide | Why it's redundant on monarch |
|---|---|---|
| Honcho | Dialectic user modeling over months | L7 EverMemOS provides this with SOTA benchmarks (LoCoMo 93%) |
| Mem0 | Vector-indexed memory store | L3 pgvector covers this against existing Postgres |
| Hindsight | Knowledge graph | L5 Codebase-Memory provides this for code; L6 vault graph view for knowledge |
| Holographic | Local vector search | L3 pgvector, no separate service needed |
| RetainDB / ByteRover / Supermemory / OpenViking | Various memory backends | All overlap with existing layers without adding distinct value |

**Re-open condition per provider:** a specific operator need that the native layers genuinely cannot serve, documented as a new memory architecture decision in this document. Provider-by-provider, not en bloc.

### §8.6 Hermes session search vs vault search vs Codebase-Memory — when to use which

Three Index-layer search surfaces exist for an agent or operator to choose from. The choice matters because each is good at different things, and silently choosing the wrong one wastes tokens or returns wrong-shaped results.

| Search surface | Indexed content | Method | Best for |
|---|---|---|---|
| Hermes session search (FTS5) | Conversation history in `~/.hermes/state.db` | Keyword full-text | "What did we discuss / decide / do in a past session" |
| Vault search (filesystem + pgvector) | Markdown notes, doctrine, project docs | Keyword (`grep` / Obsidian search) + semantic (pgvector) | "What have we written / decided / documented about a topic" |
| Codebase-Memory MCP | AST graph of code | Structural (call graph, imports, etc.) + 14 query tools | "What does function X do / who calls it / what's the impact of changing it" |
| pgvector over code | Code chunks embedded | Semantic similarity | "Find code that looks conceptually similar to X" |

**Heuristic for agents (codified as a Hermes skill at build time):**

- Question contains a verb of *recall* (remember, discuss, decide, ask) → Hermes session search
- Question contains a verb of *documentation* (write, document, note, decide formally) → vault search
- Question contains a verb of *code structure* (call, import, depend on, refactor) → Codebase-Memory MCP
- Question contains a verb of *conceptual similarity* (similar to, like, resembles) → pgvector over relevant corpus

The skill encoding this heuristic is one of the first to land post-Hermes-install in Phase 1.5 step 4.

---

## §9 — Authority Gating for Memory Writes

Extension to Decision 5 (master_summary_v20.md §9.5). Memory operations introduce a new class of autonomous writes that need to land under the existing three-tier authority framework without creating a parallel authority surface.

### §9.1 The two-axis framing

Every memory write is classified along two axes:

**Axis 1 — Origin layer:** Memory (L4 Hermes, L7 EverMemOS) or Other (rare; e.g., Index re-indexer writing to its own state).

**Axis 2 — Target layer:** Memory (own layer's state), Index (derived view), or Truth (authoritative state).

The resulting matrix:

| Origin → Target | Authority tier | Examples |
|---|---|---|
| Memory → Memory (same layer) | Tier 1 after N=12 promotion; Tier 3 at cold-start | Hermes updating MEMORY.md, EverMemOS consolidating MemScenes |
| Memory → Memory (different layer) | Tier 2 | Hermes reading EverMemOS profile to update USER.md cache |
| Memory → Index | Tier 1 | Hermes appending session row to SQLite (which is also Index) |
| Memory → Truth | **Tier 3 always** | Hermes proposing vault edit; EverMemOS proposing operator.md update |
| Index → Index (re-index) | Tier 1 | pgvector re-embedding on vault commit |
| Index → Truth | **Tier 3 always** | (Rare; should not occur by design — Index doesn't write Truth) |
| Truth → Truth | Outside Jarvis authority surface | Operator git commit, n8n pipeline write to Postgres |

### §9.2 Strict cold-start applies

All new Memory→Memory autonomous actions enter at Tier 3 per Decision 5's strict cold-start rule. Material behavior change re-enters at Tier 3. This means at first Hermes install:

- Every autonomous MEMORY.md write surfaces to the operator for confirmation
- Every autonomous EverMemOS MemCell creation surfaces (high volume — gets batched into a periodic digest, not a per-write notification)
- Promotion to Tier 1 requires N=12 operator-acknowledged successful runs without correction

**Practical operator experience.** First two weeks of Hermes use carries a per-session "Hermes autonomous memory writes since last review" summary that the operator confirms or corrects. After 12 sessions clear, autonomous Memory→Memory writes proceed silently.

### §9.3 Tier 3 framing for Memory→Truth

Any agent-proposed write that would modify a Truth-layer artifact (vault file, Postgres row, repository file) is surfaced as a Tier 3 ask:

> Hermes observed pattern X across N sessions and proposes updating `<vault>/operator.md` with: <diff>. Approve / reject / edit / defer.

Operator response determines the write. There is no autonomous Memory→Truth path at any promotion level. Decision 5's N=12 framework promotes individual *Memory→Memory action types* (e.g., "Hermes appending to MEMORY.md after task completion"), not memory categories en bloc. Memory→Truth writes are categorically Tier 3 and do not promote.

### §9.4 Authority spec extension — does Decision 5 need amendment?

No. Decision 5's three-tier framework, N=12 promotion threshold, strict cold-start, and Tier 3 surface-and-ask are all compatible with the memory architecture as written. The architecture adds *new actors* (Hermes, EverMemOS) and *new write categories* (Memory→Memory, Memory→Truth) but they fit within the existing tiers without modification.

The one new authority primitive introduced in this document is the **Memory→Truth always-Tier-3 categorical rule** (§9.3). This is local to the memory architecture and does not elevate to a general AUTHORITY_SPEC primitive. Re-open condition for elevation: a second autonomous-write surface (beyond memory) requires the same categorical rule.

---

## §10 — Observation Surface

For each layer, what Jarvis observes. This becomes the Phase 2.5 memory listener spec (or however the listener surface gets split — single listener vs per-layer).

### §10.1 Per-layer health and activity signals

| Layer | Health signal | Activity signal | Anomaly signal | Cadence |
|---|---|---|---|---|
| L1 Redis | `PING` returns PONG | command rate, memory used, connected clients | OOM approaching, command latency spike | 30s |
| L2 Postgres | TCP 5432 + simple SELECT | row count deltas per critical table, query latency p99 | replication lag, lock contention | 30s (already monitored) |
| L3 pgvector | `SELECT extversion FROM pg_extension WHERE extname='vector'` | index build time, retrieval latency, embedding cache hit rate | embedding model unreachable, index corruption | 60s |
| L4 Hermes | HTTP `/health` on Hermes daemon; `state.db` file mtime within 30s | skill creation rate, memory write rate, external provider call rate | autonomous write surge, Curator unexpectedly active | 30s |
| L5 Codebase-Memory MCP | MCP `/health` | re-index events per minute, file watcher activity | watcher stalled, MCP daemon unresponsive | 60s |
| L6 Obsidian vault | Vault directory exists + writable; git status clean | commit rate, note count, recent edits | Uncommitted changes >24h, sync conflict, orphan note rate spike | 5min |
| L7 EverMemOS | Elasticsearch + Milvus + EverMemOS service health endpoints | MemCell creation rate, MemScene consolidation rate, profile update rate | Consolidation backlog, Elasticsearch index health degraded | 60s |

### §10.2 Memory listener implementation

Single listener `memory.py` (proposed name) joining the Phase 2 listener queue per master_summary_v20.md §12.4. Inherits `BaseListener`. Polls each layer at its cadence. Writes to `state.json` under a new `memory` domain (extending `SystemModel` with a `MemoryLayers` block).

**Schema additions:** `MemoryLayer` Pydantic model with fields for each layer's health signal, activity signal, last-update timestamp, anomaly flags. `MemoryLayers` block in `SystemModel` containing dict of MemoryLayer by layer name.

**Event emissions:** state-transition rule (consistent with vram.py and tier_health.py pattern). `memory_layer_unhealthy`, `memory_layer_recovered`, `memory_anomaly_detected` (typed by layer + anomaly).

**Build sequencing:** memory.py spec'd alongside process.py / quota.py / cron.py. Build order: process.py first (smallest scope, already buildable), then quota.py (already unblocked), then cron.py and memory.py in parallel.

### §10.3 jarvis-q surface

New CLI subcommands:

- `jarvis-q memory` — shows per-layer health and recent activity. Format mirrors `jarvis-q tiers` and `jarvis-q quotas`.
- `jarvis-q skill-drafts` — lists pending Hermes-drafted skill candidates with name, age, source-conversation, and one-line description per §8.4 draft-state pattern. Surfaces stale-draft accumulation as Tier 2 events via the `memory.py` listener.

---

## §11 — Failure Modes and Recovery

Memory architectures fail in specific, predictable ways that distinguish doctrine from architecture diagrams. For each layer, what failure looks like, how Jarvis surfaces it, and the recovery path.

### §11.1 L1 Redis failure modes

**OOM under sustained write pressure.** Redis runs out of memory mid-trading-session. Recovery: Jarvis surfaces as critical event; trading pipeline halts incoming writes; operator either expands Redis maxmemory or triggers eviction policy. No automatic recovery — trading state loss is unacceptable; operator-in-loop required.

**Connection pool exhaustion.** Too many concurrent connections from agents/pipelines. Recovery: connection pool sizing review; rate-limit pipeline writes; logged Tier 2 event.

**Persistence lag.** RDB or AOF persistence falls behind, risking data loss on crash. Recovery: Jarvis warns at lag > 60s; operator review.

### §11.2 L2 Postgres failure modes

Already covered by existing operational discipline. Quarterly backup drill (last successful 2026-05-14, 79 tables restored clean). Connection failures, query timeouts, replication lag — all standard Postgres ops. Jarvis observes via existing tier_health pattern.

### §11.3 L3 pgvector failure modes

**Embedding model unreachable.** T5 (if used as local embedding server) or cloud embedding endpoint fails. Recovery: re-indexer pauses; queues up pending embeddings; resumes when model available. Jarvis surfaces as Tier 2 warning at queue depth >100.

**Index corruption.** pgvector index inconsistency. Recovery: drop and rebuild index. Operator-explicit (Tier 3) because the rebuild blocks searches during the operation.

### §11.4 L4 Hermes failure modes

**SQLite lock contention.** Multiple Hermes processes attempting writes; SQLite single-writer model bottlenecks. Recovery: Hermes is single-daemon by design; if lock contention appears, investigate parallel Hermes processes (should not exist) and kill duplicates. Jarvis observes via mtime stall.

**Skill file referencing renamed code.** Code refactor renames `validate_grounding()` to `check_grounding()`; existing Hermes skill still calls the old name. Recovery: Codebase-Memory's file watcher catches the rename; emits a `code_renamed` event; Jarvis cross-references against skills in `~/.hermes/skills/` and surfaces affected skills as Tier 3 for operator review.

**Curator unexpectedly active.** Curator config has been disabled but somehow it's running (config drift, manual edit, version upgrade reset). Recovery: Jarvis observes via skill creation rate spike or Curator-specific events; surfaces as critical; operator disables and reviews any autonomously-created skills.

**External provider unexpectedly active.** Similar pattern to Curator. Surface as critical; operator review.

**Stale skill drafts accumulating.** Hermes-drafted skill candidates in `~/.hermes/skill-drafts/` linger without operator review per §8.4 draft-state pattern. Recovery: `memory.py` listener surfaces drafts older than 30 days (threshold tunable) as Tier 2 event with name, age, and one-line description; operator approves via `approve-draft`, edits the draft, or discards. No auto-deletion (preserves drafts against accidental loss while surfacing the graveyard risk).

**MEMORY.md / USER.md drift from vault.** Auto-sync mechanism fails or runs slow; Hermes USER.md no longer reflects vault `operator.md`. Recovery: Jarvis observes USER.md vs vault `operator.md` mtime divergence; surfaces as Tier 2; operator triggers re-sync.

### §11.5 L5 Codebase-Memory failure modes

**File watcher stalled.** OS-level inotify limits or process crash; new code commits not re-indexing. Recovery: Jarvis observes via `last_reindex_event` timestamp; restarts the watcher process as Tier 2 autonomous action after N=12 promotion (cold-start Tier 3).

**Graph database corruption.** SQLite store corrupted (rare). Recovery: full re-index from repos. Operator-explicit (Tier 3) because re-index takes time and blocks queries.

### §11.6 L6 Obsidian vault failure modes

**Git corruption.** Vault `.git/` corrupted by interrupted commit or disk failure. Recovery: standard git recovery (fsck, restore from remote if pushed, restore from backup if not). Jarvis observes via `git status` errors.

**Uncommitted changes lingering.** Operator made vault edits but didn't commit. Recovery: Jarvis warns at uncommitted-change-age >24h; surfaces as Tier 2 reminder.

**Sync conflict.** If vault is multi-device (e.g., synced to laptop), git merge conflict. Recovery: operator-resolved; no autonomous handling.

**Orphan note proliferation.** Notes accumulate without backlinks; semantic clutter degrades retrieval quality. Recovery: periodic vault hygiene pass (operator-driven); Jarvis surfaces orphan rate as info-level activity signal.

### §11.7 L7 EverMemOS failure modes

**Milvus crash.** Vector index service down. Recovery: EverMemOS degrades to keyword-only (Elasticsearch); Jarvis surfaces as critical; operator restarts Milvus container.

**Elasticsearch crash.** Keyword index down. Recovery: EverMemOS degrades to vector-only (Milvus); operator restarts.

**Consolidation backlog.** MemCells accumulate without MemScene consolidation runs. Recovery: Jarvis observes consolidation rate vs creation rate; surfaces as Tier 2 at backlog >24h.

**Profile drift from vault.** EverMemOS profile diverges from vault `operator.md` due to autonomous updates not yet reviewed. Recovery: periodic profile-vs-vault diff surfaced as Tier 3 digest for operator review.

### §11.8 Cascade failure

The most consequential failure mode is multiple layers failing simultaneously (e.g., Postgres OOM takes down L2, L3, and indirectly L7 since EverMemOS uses Postgres-adjacent storage). Recovery follows existing Substrate Pressure Cascade discipline (master_summary_v20.md §10) extended to memory layers: workloads route to API for synthesis-grade work when local memory is degraded; vault-direct access via filesystem remains available as the L6 fallback even when Index layers are down.

---

## §12 — Build Sequence with Rationale

The locked Phase 1.5 sequence per master_summary_v20.md §16.6 Tier E. Each step's prereqs, exit criteria, and rationale for ordering.

### §12.1 Step 1 — Vault initialization

**Why first.** Every downstream layer either reads from or seeds from the vault. Hermes USER.md syncs from vault `operator.md`; EverMemOS profile is seeded from vault; vault holds the doctrine that defines all other layer behavior. Vault must exist before any other memory layer can be configured correctly.

**Prereqs.** None. Initial vault content (doctrine docs) is already on disk in `~/projects/jarvis/` as `master_summary_v20.md`, this document, AUTHORITY_SPEC_v19.md, DECISIONS_v19.md, REBALANCE_v19.md, BIBLE_AUDIT_findings.md, HANDOFF_v19.md.

**Exit criteria.** `~/vault/` exists, git-initialized with private GitHub remote pushed (per §7.6 Remote policy), with initial commit containing migrated doctrine, an operator-reviewed `operator.md` identity file, `README.md`, `.gitignore`, and the full structure per §7.6 tree (`skills/`, `archive/`, empty `projects/`). `kepano/obsidian-skills` content cloned as plain files into `~/vault/skills/` (no submodule); Hermes config wiring of the skills path is deferred to P1.5-4 per §12.4.

**Vault structure resolved 2026-05-26.** See §7.6 and §15 Item 1: single monolithic `~/vault/` on monarch's NVMe; doctrine-first hierarchy with `final_master_summary.md`, `final_memory_architecture.md`, `final_handoff.md` at root; `projects/` for per-subsystem docs; `archive/` for superseded versions; no PARA additions; NDA isolation deferred as future amendment per build-it-right scope clarification (§2). Multi-device sync resolved per §15 Item 7: monarch is sole Truth, MacBook accesses remotely via SSH/Tailscale. Implementation-grade choices (SSH-terminal-only vs Tailscale-mounted Obsidian UI) deferred to P1.5-1 build time.

### §12.2 Step 2 — pgvector enable

**Why second.** Index layer over the vault and over future repo embeddings. Cheap to enable; unblocks semantic search for everything downstream.

**Prereqs.** Step 1 (vault exists so we can embed vault notes).

**Exit criteria.** `CREATE EXTENSION vector;` succeeds against existing Postgres. Embedding model selection ratified (likely T5 for small/medium, cloud for large). **Install scope per §7.3 and §15 Item 3 closure: vault notes only at install** — code chunks and news corpus require explicit expansion ritual (justification → quality gate → atomic landing → post-deploy validation) per §7.3. Initial embeddings populated for vault notes. `jarvis-q` or simple SQL query verifies vector search works end-to-end.

### §12.3 Step 3 — Codebase-Memory MCP deploy

**Why third.** Structural code memory layer. Independent of Hermes (any MCP-compatible agent can consume it, including Claude Code). Better to have working before Hermes lands so Hermes inherits a populated structural memory.

**Prereqs.** None hard; pgvector (Step 2) provides complementary semantic search but Codebase-Memory works standalone.

**Exit criteria.** Single-binary daemon running. File watcher configured against `~/projects/`. Initial AST graph indexed across all projects. MCP endpoint reachable. Claude Code can call structural query tools. Add as health component in `MONARCH_HEALTH_COMPONENTS`.

### §12.4 Step 4 — Hermes Agent adoption

**Why fourth.** Hermes lands into a populated Truth + Index context (vault doctrine, pgvector embeddings, Codebase-Memory graph). First session is rich from minute one. Curator disabled, default model DeepSeek V4 Flash via LiteLLM, kepano/obsidian-skills installed pointing at vault, external memory providers all off.

**Prereqs.** Steps 1-3.

**Exit criteria.** Hermes daemon running, accessible at its OpenAI-compatible endpoint, integrated into LiteLLM routing as a model alias or peer endpoint. `MEMORY.md`, `USER.md`, `SOUL.md` initialized. kepano/obsidian-skills installed at `~/vault/skills/` per P1.5-1 (§12.1); **Hermes skills-path wiring** decided at this step: either (a) Hermes config adds `~/vault/skills/` as an additional skills search path alongside `~/.hermes/skills/`, or (b) kepano content is copied/symlinked from `~/vault/skills/` into `~/.hermes/skills/`. Implementation choice depends on Hermes config surface at install time; per §15 Item 11 the file-watcher mechanism (a) standalone process, (b) Codebase-Memory piggyback, or (c) Hermes-skill-on-cron also resolves here. USER.md auto-sync from vault working. First operator-explicit skill promotion documented. Hermes added to `MONARCH_HEALTH_COMPONENTS`. Skill heuristic from §8.6 codified as initial Hermes skill. **Draft-state pattern per §8.4 deployed:** `~/.hermes/skill-drafts/` directory created; Hermes autonomous skill-creation hook configured to route to drafts not skills; `approve-draft` and `promote-skill` skills bootstrapped (initial hand-written SKILL.md files); `jarvis-q skill-drafts` CLI subcommand stubbed (full implementation lands with `memory.py` listener).

### §12.5 Step 5 — EverMemOS deploy

**Why fifth.** Long-horizon memory. Lands after Hermes so that Hermes session SQLite can be one of EverMemOS's conversation ingestion sources. Profile seeded from vault.

**Prereqs.** Steps 1-4 (vault for profile seed, Hermes for session ingestion).

**Exit criteria.** Elasticsearch + Milvus + EverMemOS service running. Profile seeded from vault `operator.md`. First MemCells forming from Hermes sessions. Foresight signal generation verified on synthetic input. Health components added.

### §12.6 Step 6 — Redis (joins with financial pipeline)

**Why last.** L1 Redis is hot operational state for the financial pipeline. Doesn't need to be built until the financial pipeline build starts. Listed in the sequence for completeness; activation gated on E1 (financial strategy doc + phase-level design per master_summary_v20.md §16.6).

**Prereqs.** Financial pipeline strategy ratified (12 open questions per §8 of master_summary_v20.md).

**Exit criteria.** Redis daemon running. Trading pipeline integration. Health component added. Snapshot-to-Postgres cadence ratified.

### §12.7 Sequencing rationale

Build by layer, not by tool. Truth first (vault initialization). Index second (pgvector, Codebase-Memory). Memory third (Hermes, EverMemOS). Operational Truth (Redis) last because it's gated on a separate doctrine workstream.

This is the *only* ordering where each layer lands into a populated upstream. Any other ordering has downstream layers landing empty and backfilling. Backfilling memory layers is exactly what creates the "agent learned something wrong before it learned the right thing" problem the architecture is designed to prevent.

---

## §13 — Cross-References to master_summary_v20.md

Where v20 owns adjacent doctrine. This document defers to v20 on all these surfaces; v20 defers to this document for everything in §3-§12 above.

| Topic | v20 section | Role |
|---|---|---|
| Arbiter role in Jarvis function taxonomy | §3.1 | Names Jarvis as memory layer arbiter |
| Decision 2 — Hermes adoption closed 2026-05-26 | §9.2 | Closure with artifact identification, constraint mapping |
| Decision 5 — Authority model framework | §9.5 | N=12 promotion, strict cold-start, three-tier framework |
| Decision 6 — Scope amendment for memory build | §9.6 | Nexus and 2nd Brain moved to phase 1.5 build targets |
| Hermes Agent operational detail | §13 | Artifact, Pattern B vs n8n, build integration |
| Phase 1.5 build queue status | §16.6 Tier E | P1.5-1 through P1.5-6 with prereqs |
| Audit closures (D1-D4 codings, A5/A7/NEW-v20-* memory items) | §16.1 | Track record |
| Memory Architecture pointer summary | §18 | Reader entry-point with four-layer table + Truth-is-primary rule |
| RAM budget projection | §2 | ~44-46 GB steady-state with ES + Milvus + Redis |
| Truth hierarchy (current-state checks) | §0, §15.3 | Operational truth hierarchy preserved; distinct from Truth layer here (§18.4 of v20) |

---

## §14 — Ruled-Out / Deferred for Memory Architecture

Specific to this surface, not duplicating master_summary_v20.md §17.

- **External Hermes memory providers en bloc** (Mem0, Honcho, Hindsight, Holographic, RetainDB, ByteRover, Supermemory, OpenViking). All disabled at install per §8.5. Re-open: per-provider operator-explicit decision documenting unmet need.
- **EverMemOS deferral framing** (the original "wait until financial pipeline forces it" framing). Explicitly rejected 2026-05-26 in favor of build-it-right principle. Banked here so it doesn't get re-proposed under cost pressure. Re-open: never; the build-it-right principle is doctrine.
- **Knowledge graphs as L6 or L7 substrate** (Neo4j, Memgraph, Kuzu). Over-engineered for solo operator. Obsidian's filesystem + wikilinks + pgvector provides 80% of the value at 5% of the complexity. Re-open: a use case that genuinely cannot be served by filesystem + semantic search + L5 structural graph.
- **Custom memory framework built from scratch.** Hermes Agent and EverMemOS solve these problems with mature production systems. Building bespoke memory would be exactly the "reinvent the wheel" anti-pattern. Re-open: never.
- **Curator enabled at install.** Per §8.4. Re-open: 30 days stable use + 12 promoted skills + operator opt-in.
- **Bidirectional vault sync from Hermes.** Per §8.2. Re-open: never; this is the core conflict-prevention pattern.
- **Skill promotion via N-uses counter.** Operator-explicit only. Re-open: never; the elegance test rejects the counter.
- **Subquadratic / SubQ local serving.** Closed weights, cloud-only, prior-art skepticism around subquadratic architectures. Watch but don't design around. Re-open: if open-weight subquadratic architecture matures with verified benchmark gains.
- **TSTorch as a training framework.** Student project, not publicly released. Re-open: if it open-sources and matures.

---

## §15 — Open Items (Doctrine Gaps)

Things this document does not yet authoritatively cover. Build-implementation detail belongs in master_summary_v20.md §16.6 Tier E (Phase 1.5 queue); this list is purely doctrine gaps. **Update 2026-05-26:** Items 1, 3, 4, 7 closed in this session's §15 walk and now carry resolution cross-references. Items 2, 5, 6, 8, 9, 10 remain open.

1. **Vault structure decision.** ✅ CLOSED 2026-05-26 from this session's §15 walk. Resolution per §7.6: single monolithic `~/vault/`, monarch-only Truth, doctrine-first hierarchy with `final_master_summary.md` at root, projects as children under `projects/`, no PARA additions, NDA isolation deferred as future amendment.

2. **pgvector embedding model decision.** T5 local vs cloud embeddings vs mixed. Resolution: at Phase 1.5 step 2 build time, after measurement of T5 throughput on embedding workloads.

3. **pgvector scope decision.** ✅ CLOSED 2026-05-26 from this session's §15 walk. Resolution per §7.3: vault notes only at install; code chunks and news corpus require explicit expansion ritual (4-step pattern: justification → quality gate → atomic landing → post-deploy validation).

4. **Skill promotion ritual mechanics.** ✅ CLOSED 2026-05-26 from this session's §15 walk. Resolution per §8.4: draft-state pattern. Hermes autonomously drafts skill candidates to `~/.hermes/skill-drafts/`; operator approves via `approve-draft` (Hermes skill + bin script hybrid); operator-direct promotion of vault notes via `promote-skill`. Curator-the-grader remains disabled.

5. **External provider re-enablement pattern.** If a provider does eventually justify re-enablement, what's the decision shape? Resolution: when first provider is proposed.

6. **EverMemOS Foresight signal consumption by trading pipeline.** Read-only consumption pattern, frequency, gating. Resolution: when financial pipeline build starts (E1 in master_summary_v20.md §16.6).

7. **Multi-device vault sync.** ✅ CLOSED 2026-05-26 from this session's §15 walk. Resolution per §7.6: monarch is the sole Truth location; no replication; MacBook accesses remotely via SSH/Tailscale. Truth-singularity preserved by construction. Implementation choice (SSH-terminal-only vs Tailscale-mounted filesystem for Obsidian UI) deferred to P1.5-1 build time.

8. **Cross-layer event coordination.** When Codebase-Memory detects a code rename, does it notify Hermes (so skills referencing the old name can be flagged)? Doctrine pattern needed if cross-layer event surfaces become load-bearing. Resolution: deferred to first concrete need.

9. **Memory listener architecture.** Single `memory.py` listener watching all layers, or per-layer listeners. Resolution: at memory.py build time, after process.py / quota.py / cron.py pattern is established.

10. **Authority promotion granularity.** Does N=12 promotion apply per Memory→Memory action type (Hermes MEMORY.md append, Hermes USER.md update, EverMemOS MemCell creation, EverMemOS MemScene consolidation as separate types) or per memory layer category? Resolution: at first promotion attempt.

11. **Vault file watcher implementation (surfaced 2026-05-27).** §8.2 names three options for the watcher process: (a) standalone process, (b) piggyback on Codebase-Memory's file watcher, (c) Hermes skill firing on cron. Resolution: at P1.5-4 Hermes install, after the Hermes file-watcher capability surface is known. Default until decided: USER.md auto-sync from vault operates on Hermes session-start refresh (Hermes reads `~/vault/operator.md` fresh each session) rather than real-time mtime detection — operator-edit-during-session changes apply on next session.

12. **Hermes session SQLite → EverMemOS ingestion cadence (surfaced 2026-05-27).** §7.7 says EverMemOS treats Hermes session SQLite as one of its conversation sources but doesn't specify cadence (real-time stream, batch on session-end, periodic cron). Resolution: at P1.5-5 EverMemOS deploy, after EverMemOS ingestion API surface and Hermes session lifecycle hooks are both known. Default at deploy: batch-on-session-end with operator-acknowledgeable digest, conservative enough not to lose state if Hermes session crashes mid-conversation.

13. **L7 EverMemOS profile-drift digest cadence (surfaced 2026-05-27).** §11.7 specifies that EverMemOS profile diverging from vault `operator.md` (due to autonomous L7 updates) surfaces as a Tier 3 digest for operator review — but cadence is unspecified. For high-stakes consumption (financial pipeline Foresight queries, multi-month engagement state), slow cadence means agents could read drifted profile state for days/weeks before operator catches it. Resolution: at P1.5-5 deploy with initial cadence = daily digest; tighten to real-time alert on profile fields known to affect financial pipeline once that consumer goes live (master_summary_v20.md §16.6 E1).

---

## §16 — Closing Note

Built in a focused doctrine session 2026-05-26 alongside the master_summary_v20.md update that closed Decision 2 and amended Decision 6. The architecture is the natural completion of patterns master_summary_v20.md already established — not a graft.

The consequential framings from the design conversation that produced this document:

1. **Build it right the first time, not "good enough until it breaks."** In agentic work, memory failure costs surface as financial loss. The cost of not having the right architecture is paid silently in agent decisions made on incomplete world state.

2. **Truth is primary; everything else is derived.** One rule. Applied consistently. Eliminates the entire class of cross-layer conflict before it can occur.

3. **Layers stack rather than compete.** Each layer has a fundamentally different write discipline. Mixing disciplines creates conflict zones; keeping them separated makes the system feel designed. Seven addressable components, four doctrinal roles, one conflict-resolution rule. That's the elegance test passing.

4. **Hermes Agent lands into a populated context.** Build by layer (Truth → Index → Memory), not by tool. Hermes inherits the world rather than starting empty. First session is rich from minute one.

5. **Memory→Memory autonomous, Memory→Truth gated.** Decision 5's authority framework extends to memory operations without modification. Agents can update their own models freely; proposing edits to authoritative state requires operator confirmation. The discipline scales as the system grows.

6. **Single doctrine doc, paralleling AUTHORITY_SPEC's role.** Memory architecture is doctrine-grade because its failure mode is financial. It gets its own document, its own update cadence, its own cross-references. This is that document.

The system understands itself. The doctrine is honest. The architecture is elegant rather than over-engineered. Phase 1.5 build can begin.

---

*End of MEMORY_ARCHITECTURE_v20. Living document. Update on doctrine close or memory layer code change — never on chat conversation alone.*
