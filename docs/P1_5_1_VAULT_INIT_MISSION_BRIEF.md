# P1.5-1 Mission Brief — Vault Initialization

**For:** Claude Code session executing Phase 1.5 Step 1  
**Doctrine source:** `MEMORY_ARCHITECTURE_v20.md §7.6, §12.1` + `master_summary_v20.md §16.6`  
**All sub-decisions locked:** 2026-05-27 design session  
**Prereqs before this mission runs:** see § Pre-mission checklist below

---

## Purpose

Initialize `~/vault/` as the canonical Truth layer (L6) for the monarch memory architecture.
Migrate doctrine docs from `~/projects/jarvis/` to vault. Update all self-referential path
pointers in CLAUDE.md and `§0.2`. Leave jarvis repo with a clean tombstone record.

This is Phase 1.5 Step 1 in the locked sequence. Every downstream memory layer
(pgvector, Codebase-Memory, Hermes, EverMemOS) either reads from or seeds from the vault.
Nothing else in Phase 1.5 can start until this exits clean.

---

## Pre-mission checklist (operator does these before Claude Code runs)

- [ ] **Create empty private GitHub repo** named `vault` (or `monarch-vault`) under the
      operator's GitHub account. No README, no license, no .gitignore — Claude Code
      populates all of these.
- [ ] **Have the repo SSH remote URL ready** — e.g. `git@github.com:<user>/vault.git`
- [ ] **Review and edit the operator.md draft** — Claude Code will draft this (see § Step 3);
      operator confirms before the init commit fires. Do not skip this review — operator.md
      is Truth-layer content; agent-proposed edits are always Tier 3 under
      `MEMORY_ARCHITECTURE_v20.md §9`.

---

## Exit criteria

Per `MEMORY_ARCHITECTURE_v20.md §12.1`:

- `~/vault/` exists, git-initialized, remote set, initial commit pushed
- Initial commit contains: all migrated doctrine, `operator.md`, `README.md`,
  `skills/` (kepano/obsidian-skills), `projects/`, `archive/`, `.gitignore`
- `~/projects/jarvis/` has deletion commits for the three canonical-root docs and
  the seven archive docs; CLAUDE.md Pointers table updated to vault paths
- `master_summary_v20.md §0.2` doc-set table updated: paths now point to `~/vault/`
- `kepano/obsidian-skills` content committed to `~/vault/skills/` as plain files

---

## Vault directory structure to create

```
~/vault/
├── .gitignore                          ← see § .gitignore spec below
├── README.md                           ← vault entry point (brief; see § Step 2)
├── operator.md                         ← operator identity (see § Step 3)
├── final_master_summary.md             ← migrated from ~/projects/jarvis/master_summary_v20.md
├── final_memory_architecture.md        ← migrated from ~/projects/jarvis/MEMORY_ARCHITECTURE_v20.md
├── final_handoff.md                    ← migrated from ~/projects/jarvis/HANDOFF_v19.md
├── skills/                             ← kepano/obsidian-skills content (plain files)
├── projects/                           ← empty at init; populated organically per stack build
└── archive/
    ├── AUTHORITY_SPEC_v19.md
    ├── DECISIONS_v19.md
    ├── REBALANCE_v19.md
    ├── INFRASTRUCTURE_BIBLE_v19.md
    ├── JARVIS_PHASE2_SPEC.md
    ├── master_summary_v19.md
    └── BIBLE_AUDIT_findings.md         ← drift tracker sunsets at P1.5-1; §16.1 is canonical
```

**`projects/` is empty at init.** No placeholder files. Populated organically when each
stack's build begins. news-pipeline is farthest along and will be first to populate here.

---

## .gitignore spec

```gitignore
# OS and editor artifacts
.DS_Store
Thumbs.db
*.tmp
*.swp
*~

# Obsidian workspace state (machine-specific, not doctrine)
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# Credential safety net — these should never be in vault, but if they appear:
*.env
*.key
*.pem
*secret*
*credential*
*password*
*api_key*
*token*

# Reserved private subdirectories (pre-excluded before any sensitive content lands)
# NDA and financial-edge content will eventually need local-only subdirs
private/
nda/
sensitive/
trading-edge/
```

---

## File migration table

All source files confirmed present on disk (`ls ~/projects/jarvis/` verified 2026-05-27).

### Canonical-root docs — MOVE and RENAME

| Source path | Vault path | Notes |
|---|---|---|
| `~/projects/jarvis/master_summary_v20.md` | `~/vault/final_master_summary.md` | §0.2 self-reference updated before deletion |
| `~/projects/jarvis/MEMORY_ARCHITECTURE_v20.md` | `~/vault/final_memory_architecture.md` | |
| `~/projects/jarvis/HANDOFF_v19.md` | `~/vault/final_handoff.md` | Session log lives in vault repo going forward |

### Archive docs — MOVE (no rename)

| Source path | Vault path |
|---|---|
| `~/projects/jarvis/AUTHORITY_SPEC_v19.md` | `~/vault/archive/AUTHORITY_SPEC_v19.md` |
| `~/projects/jarvis/DECISIONS_v19.md` | `~/vault/archive/DECISIONS_v19.md` |
| `~/projects/jarvis/REBALANCE_v19.md` | `~/vault/archive/REBALANCE_v19.md` |
| `~/projects/jarvis/INFRASTRUCTURE_BIBLE_v19.md` | `~/vault/archive/INFRASTRUCTURE_BIBLE_v19.md` |
| `~/projects/jarvis/JARVIS_PHASE2_SPEC.md` | `~/vault/archive/JARVIS_PHASE2_SPEC.md` |
| `~/projects/jarvis/master_summary_v19.md` | `~/vault/archive/master_summary_v19.md` |
| `~/projects/jarvis/BIBLE_AUDIT_findings.md` | `~/vault/archive/BIBLE_AUDIT_findings.md` |

### Stays in jarvis repo (not migrated)

`README.md` — gets rewritten per §16.5 C2; not a vault target  
All `*.py`, `deploy.sh`, `requirements.txt`, `bin/` — code; not doctrine  
All `*.backup` untracked files — scratch; not committed to either repo

---

## Execution sequence

### Step 1 — Vault git init

```bash
# Run from monarch@monarch-...
mkdir -p ~/vault/{archive,projects,skills}
cd ~/vault
git init
git remote add origin <SSH_REMOTE_URL>   # operator supplies this from pre-mission checklist
```

### Step 2 — Write vault README.md

Lean entry point — 15-20 lines max. Content:

```markdown
# monarch vault

Operator knowledge base and doctrine store for the monarch inference stack.

## What lives here

- `final_master_summary.md` — single source of doctrine for the stack
- `final_memory_architecture.md` — memory layer architecture doctrine
- `final_handoff.md` — active session log
- `operator.md` — operator identity and preferences (Truth; L6)
- `skills/` — Hermes skill library (kepano/obsidian-skills + promoted skills)
- `projects/` — per-stack documentation; populated as each stack activates
- `archive/` — superseded v19 docs; preserved for historical reference

## Truth hierarchy

monarch disk > git log > jarvis-q all > docs > chat history

## Access

Operator edits directly on monarch or via SSH/Tailscale from MacBook.
Agent access (Hermes) via kepano/obsidian-skills in skills/.
```

### Step 3 — Draft operator.md, present to operator for review

Draft by synthesizing from these exact sections of the pre-migration doctrine docs:

- **Identity + mission:** `final_master_summary.md §1` (Operator + Mission Context)
  and `§1.1` (Three operating realities) and `§1.2` (Mission in one sentence)
- **Hardware envelope:** `final_master_summary.md §2` (the forcing-function table)
- **Decision posture:** `final_master_summary.md §9` cardinals summary
  (one line per cardinal — closed status + one-sentence essence)
- **Working pattern:** `final_handoff.md` — operator quirks / lessons banked sections

Suggested `operator.md` structure:
```
# operator.md — Trent

## Identity
## Mission
## Hardware (monarch)
## Operating posture (from cardinals)
## Working pattern
## Open queue pointer
```

**STOP after drafting.** Present the draft to the operator. Do not commit until the
operator explicitly approves. This is a Truth-layer file — operator confirmation is
required before it enters git history per `MEMORY_ARCHITECTURE_v20.md §9`.

### Step 4 — Write .gitignore

Paste the spec from § .gitignore spec above verbatim.

### Step 5 — Install kepano/obsidian-skills into ~/vault/skills/

```bash
# Clone to temp, copy content into vault/skills/, discard the clone's .git
cd /tmp
git clone https://github.com/kepano/obsidian-skills.git kepano-skills-tmp
cp -r kepano-skills-tmp/. ~/vault/skills/
rm -rf kepano-skills-tmp
```

Plain files in vault — no submodule. Skills are versioned alongside vault doctrine.

**Note for P1.5-4 (Hermes install):** Hermes config must be wired to use `~/vault/skills/`
as an additional skills search path (alongside `~/.hermes/skills/` for promoted operator
skills). That wiring is P1.5-4's responsibility, not this step.

### Step 6 — Copy canonical-root docs to vault (with §0.2 self-reference update)

```bash
# Copy with new names
cp ~/projects/jarvis/master_summary_v20.md ~/vault/final_master_summary.md
cp ~/projects/jarvis/MEMORY_ARCHITECTURE_v20.md ~/vault/final_memory_architecture.md
cp ~/projects/jarvis/HANDOFF_v19.md ~/vault/final_handoff.md
```

**Immediately update `~/vault/final_master_summary.md §0.2` doc-set table** so the
file's first canonical version is already self-consistent:

In the §0.2 table, update the three canonical-root rows:

| Old path entry | New path entry |
|---|---|
| `master_summary_v20.md (this file)` | `~/vault/final_master_summary.md (this file)` |
| `MEMORY_ARCHITECTURE_v20.md` | `~/vault/final_memory_architecture.md` |
| `HANDOFF_v19.md` | `~/vault/final_handoff.md` |

Also update the `CLAUDE.md` row to: `~/projects/jarvis/CLAUDE.md`
(path was implicit before; now explicit to distinguish from vault location)

Use Python read-modify-write with assert-count-==1 per standard patch discipline.
Verify the three new path strings land and the three old strings are absent before
the vault initial commit fires.

### Step 7 — Copy archive docs to vault/archive/

```bash
for f in AUTHORITY_SPEC_v19.md DECISIONS_v19.md REBALANCE_v19.md \
          INFRASTRUCTURE_BIBLE_v19.md JARVIS_PHASE2_SPEC.md \
          master_summary_v19.md BIBLE_AUDIT_findings.md; do
    cp ~/projects/jarvis/$f ~/vault/archive/$f
done
```

### Step 8 — Vault initial commit and push

```bash
cd ~/vault
git add -A
git status   # review before commit; should show all vault files staged
git commit -m "vault: P1.5-1 initial commit — doctrine migration, operator.md, kepano/obsidian-skills

Initializes ~/vault/ as L6 Truth layer per MEMORY_ARCHITECTURE_v20.md §7.6 and §12.1.

Canonical-root docs migrated from ~/projects/jarvis/:
  master_summary_v20.md → final_master_summary.md (§0.2 self-reference updated)
  MEMORY_ARCHITECTURE_v20.md → final_memory_architecture.md
  HANDOFF_v19.md → final_handoff.md

Seven v19 docs migrated to archive/. BIBLE_AUDIT_findings.md drift tracker
sunsets here — §16.1 in final_master_summary.md is canonical going forward.

kepano/obsidian-skills installed as plain files in skills/ (no submodule).
P1.5-4 (Hermes install) wires Hermes config to ~/vault/skills/ as skills path.

operator.md seeded from §1 + §2 + §9 + HANDOFF operator profile sections;
operator-reviewed and approved before this commit."
git push -u origin master
```

### Step 9 — Update jarvis repo: CLAUDE.md Pointers table + delete migrated files

Three jarvis repo commits, in order:

**Jarvis commit 1 — CLAUDE.md path updates:**

In `~/projects/jarvis/CLAUDE.md` Pointers table, update vault-hosted doc references:

| Old entry | New entry |
|---|---|
| `` `master_summary_v20.md` `` | `` `~/vault/final_master_summary.md` `` |
| `` `MEMORY_ARCHITECTURE_v20.md` `` | `` `~/vault/final_memory_architecture.md` `` |
| `` `HANDOFF_v19.md` `` | `` `~/vault/final_handoff.md` `` |

Use Python read-modify-write with assert-count-==1 per patch discipline.

```bash
cd ~/projects/jarvis
git add CLAUDE.md
git commit -m "CLAUDE.md: update Pointers table to vault paths post-P1.5-1"
```

**Jarvis commit 2 — delete canonical-root docs:**

```bash
cd ~/projects/jarvis
git rm master_summary_v20.md MEMORY_ARCHITECTURE_v20.md HANDOFF_v19.md
git commit -m "doctrine: remove canonical-root docs migrated to ~/vault/ (P1.5-1)

These files now live at:
  ~/vault/final_master_summary.md
  ~/vault/final_memory_architecture.md
  ~/vault/final_handoff.md

Pre-migration git history preserved in this repo. Post-migration history
tracked in vault repo."
```

**Jarvis commit 3 — delete archive docs:**

```bash
cd ~/projects/jarvis
git rm AUTHORITY_SPEC_v19.md DECISIONS_v19.md REBALANCE_v19.md \
       INFRASTRUCTURE_BIBLE_v19.md JARVIS_PHASE2_SPEC.md \
       master_summary_v19.md BIBLE_AUDIT_findings.md
git commit -m "doctrine: remove v19 archive docs migrated to ~/vault/archive/ (P1.5-1)"
```

---

## Post-mission verification

Run all of these; each should pass before declaring P1.5-1 complete:

```bash
# 1. Vault structure
ls ~/vault/
ls ~/vault/archive/
ls ~/vault/skills/
ls ~/vault/projects/    # should be empty

# 2. Three canonical-root docs in vault
head -3 ~/vault/final_master_summary.md
head -3 ~/vault/final_memory_architecture.md
head -3 ~/vault/final_handoff.md

# 3. §0.2 self-reference updated
grep "final_master_summary" ~/vault/final_master_summary.md | head -3

# 4. operator.md present
wc -l ~/vault/operator.md

# 5. kepano/obsidian-skills landed
ls ~/vault/skills/

# 6. Vault git status clean, remote set, pushed
cd ~/vault && git status && git log --oneline | head -3 && git remote -v

# 7. Jarvis repo no longer has migrated docs
ls ~/projects/jarvis/master_summary_v20.md 2>&1   # should say "No such file or directory"
ls ~/projects/jarvis/HANDOFF_v19.md 2>&1           # same

# 8. CLAUDE.md updated
grep "final_master_summary\|final_memory_architecture\|final_handoff" \
     ~/projects/jarvis/CLAUDE.md

# 9. GitHub push confirmed
cd ~/vault && git log --oneline origin/master | head -3
```

---

## MEMORY_ARCHITECTURE amendment (ALREADY APPLIED in ca76498 -- DO NOT RE-APPLY)

**Target:** `~/vault/final_memory_architecture.md §7.6`  
**Where:** After the vault structure block, before the "Truth-singularity" paragraph  
**STATUS (2026-05-27):** This paragraph was ALREADY added to MEMORY_ARCHITECTURE_v20.md (which becomes final_memory_architecture.md at migration) section 7.6 in commit ca76498, BEFORE this mission runs. It travels with the file when the file migrates. Claude Code: do NOT re-apply -- it is already on disk. The blockquote below is the historical record only:

> **Two-git-repo distinction (locked 2026-05-27).** The vault is a separate git
> repository from the monarch code repositories by deliberate design. Code repositories
> (`~/projects/jarvis/` and future monolithic codebase subdirectories) are indexed by
> Codebase-Memory MCP — AST graph, symbol navigation, structural queries — and benefit
> from monolithic organization where cross-project symbol resolution works natively.
> The vault is indexed by pgvector (semantic search) and Obsidian backlinks (graph
> traversal), and benefits from isolation so that vault-agent interactions (Hermes reads,
> operator edits via Obsidian UI or SSH) do not require code-repo write access or create
> merge-conflict surfaces with code tooling. The monolithic codebase principle applies
> to code repos only. The vault being a separate git repo is the correct architectural
> choice, not a convention.

SUPERSEDED (2026-05-27): the amendment above already landed in ca76498. No anchor patch and no second vault commit are needed for this paragraph at P1.5-1. It migrates automatically as part of final_memory_architecture.md.

---

## Session log going forward

After P1.5-1, session-end commits go to the **vault repo**, not the jarvis repo.
`~/vault/final_handoff.md` is the append target. `cd ~/vault && git add final_handoff.md
&& git commit && git push` is the session-end pattern.

Code commits (listeners, schema, state.py etc.) continue to go to `~/projects/jarvis/`
or the future monolithic codebase repo.

---

## What this step does NOT do

- Does **not** install or configure Obsidian desktop app (implementation-grade;
  operator decides SSH-terminal-only vs Tailscale-mounted Obsidian UI at P1.5-1 build time)
- Does **not** enable pgvector — that is P1.5-2
- Does **not** configure Hermes skills path wiring — that is P1.5-4
- Does **not** migrate `README.md` from jarvis repo — that gets rewritten per §16.5 C2

---

## Pointer to next step

P1.5-2 — Enable pgvector extension on existing Postgres.  
Prereq: this step complete (vault exists so we can embed vault notes).  
Spec: `MEMORY_ARCHITECTURE_v20.md §12.2` + `§7.3` (vault-notes-only scope at install,
expansion ritual for code chunks and news corpus).
