---
type: guideline
tags:
  - system/guideline
  - mythos
  - memory
  - mempalace
related:
  - [mode](./mode.md)
  - [context-priming](./context-priming.md)
  - [failure-recovery](./failure-recovery.md)
---

# Mythos Memory

> Protocol for integrating prior session knowledge into Mythos priming.
> MemPalace AAAK format, bridging into a curated knowledge wiki.

---

## Philosophy

1. **Two knowledge gaps**: post-cutoff world knowledge (WebSearch) AND your own prior session knowledge (MemPalace). Mythos primes both. Neither replaces the other.
2. **170 token startup, on-demand expand**: priming needs only MemPalace L0+L1; real detail arrives as you descend into drawers. Natural fit with the Mythos context budget discipline.
3. **Verbatim > summary**: MemPalace stores original content (drawer); summaries live in user-curated wiki pages. A faulty summary is not a source. Wiki distillation stays manual and reviewed.
4. **AAAK = LLM-native, not human-illegible**: structured English shorthand, `~30x compression`, no fine-tuning required. Any LLM (Claude/GPT/Llama) parses it natively.

---

## Architectural Position

```
+---------------------------------------------------------+
|                  Mythos mode priming                    |
+---------------------------------------------------------+
            |                    |                    |
            v                    v                    v
   +----------------+   +-----------------+   +------------------+
   |  Wiki layer    |   |   MemPalace     |   |  WebSearch /     |
   |  (curated)     |   |   (verbatim)    |   |  WebFetch        |
   |                |   |                 |   |                  |
   | knowledge/     |   | $MEMPALACE_HOME |   | current world    |
   | curated pages  |   | wings/rooms/    |   | post-cutoff      |
   | human-reviewed |   | drawers (AAAK)  |   | + canonical doc  |
   +----------------+   +-----------------+   +------------------+
            |                    |                    |
            +------------+-------+-----------+--------+
                         v
               +----------------------+
               |  Claude main context |
               |  (1M Opus 4.7)       |
               +----------------------+
```

| Layer | What | Size | Latency | Source of truth? |
|---|---|---|---|---|
| Wiki | Distilled, cross-linked, curated | ~80 lines/page | Instant (Read) | Human-reviewed |
| MemPalace | Verbatim conversation history | 170 tok startup, drawer expand | <100ms semantic query | Original |
| Web | Current world | Variable | Network bound | External |

---

## MemPalace Setup

**One time, on the user's machine:**

```bash
# Use any Python venv
pip install mempalace  # if a PyPI release exists
# or
git clone https://github.com/MemPalace/mempalace ~/.mempalace
cd ~/.mempalace && pip install -r requirements.txt
```

Dependencies: ChromaDB + PyYAML. Local storage under `$MEMPALACE_HOME` (default `~/.mempalace/data/`). Zero API calls.

MCP register (Claude Code):
```json
{
  "mcpServers": {
    "mempalace": {
      "command": "python",
      "args": ["-m", "mempalace.mcp_server"],
      "env": {"MEMPALACE_HOME": "${MEMPALACE_HOME:-~/.mempalace/data}"}
    }
  }
}
```

29 MCP tools become available: palace ops, knowledge graph, agent diary, drawer mgmt, cross-wing nav.

---

## Initial Ingest (one-time)

Map your session history archive into a MemPalace wing structure. Wing names are arbitrary and reflect your domains; do not copy the example below verbatim.

```
$MEMPALACE_HOME/
+-- Wings/
|   +-- User-You/             (personal persona, profile)
|   +-- Project-Alpha/        (active project)
|   +-- Project-Beta/         (active project)
|   +-- Project-Gamma/        (active project)
|   +-- Project-Mythos/       (this scaffold's own evolution)
|   +-- Domain-AI-Tools/      (Claude Code, MCP, agent stacks)
+-- Rooms/                     (cross-wing topic clusters)
+-- Halls/                     (entity bridges)
```

Ingest command:
```bash
mempalace ingest \
  --source "<path-to-session-history-archive>" \
  --wing-strategy folder-as-wing \
  --temporal-window all \
  --aaak-compress
```

Expected output: ~500K words of source -> ~17K tokens verbatim AAAK + index.

---

## Mythos Priming Hierarchy (updated)

Coordinate with [context-priming](./context-priming.md). New ordering:

| Order | Source | Cost | Trigger |
|---|---|---|---|
| 1 | Project root context file (e.g. `CLAUDE.md`) | Read 1 file | Every session |
| 2 | Active project file | Read 1 file | Task domain known |
| 3 | Cross-project rules | Read N files | Stable conventions |
| 4 | Active mythos skill files | Read N files | Mode activation |
| 5 | **MemPalace L0+L1 query** (170 tok) | <100ms | Task domain known |
| 6 | Wiki index page | Read 1 file | Concept/entity lookup |
| 7 | Relevant curated wiki pages | Read N files | Followed from index |
| 8 | **MemPalace drawer expand** (verbatim) | <100ms x N | "Did I decide this before?" |
| 9 | Raw session history fallback | Read N MB | MemPalace absent or deep search |
| 10 | WebSearch / WebFetch | Network | Post-cutoff, external |

**Decision logic:**
- "Have we discussed this?" -> 5 (MemPalace L1 quick) -> 8 (drawer detail). Skip the raw archive.
- "What is this concept?" -> 6 -> 7 (curated wiki). MemPalace not needed if a wiki page exists.
- "How is project X going?" -> 2 (project file). Current state lives there.
- "What is pattern X?" -> 3 (rules) -> 6 -> 10 (web validation).

---

## Failure Recovery Memory (Mythos sub-mode)

Bridge with [failure-recovery](./failure-recovery.md).

When stuck, query the **MemPalace agent diary**:
```
mempalace query --wing Domain-AI-Tools --topic stuck-pattern --temporal "last 30 days"
```

If the same pattern was solved before -> drawer expand + adapt.
If first time -> after solving, write a diary entry:
```
mempalace diary-add \
  --wing Project-Mythos \
  --room failure-recovery \
  --content "Auth flow hypothesis confirmed: refresh token rotation requires server-side jti tracking. Fix: add Redis-backed jti store + 5s clock skew tolerance."
```

In the next session, the same problem surfaces this drawer in the 170 tok L0+L1 query -> instant resolution.

A wiki-side `MYTHOS-FAILURES.md` page is optional: human-curated summary on the wiki, verbatim diary on MemPalace.

---

## Wiki vs MemPalace: which is which

| Data type | Wiki | MemPalace |
|---|---|---|
| Distilled insight (human-reviewed) | yes | - |
| Verbatim conversation snippet | - | yes |
| Cross-linked concept tree | yes | - |
| Temporal "when was this said" | - | yes |
| Curated source list | yes | - |
| Failure pattern diary | - | yes |
| Stable canonical reference | yes | - |
| Recent decision log | - | yes |

**Flow:** verbatim sits in MemPalace -> the user distills via your vault's wiki ingest tooling -> wiki page becomes durable. The two systems do not duplicate the same data; one is operational, the other canonical.

---

## Sub-Agent Briefing with MemPalace

Bridge with [decomposition](./decomposition.md).

Sub-agents start with a fresh context. Inject prior-session summaries into the briefing:

```
Briefing (to sub-agent):
- Task: <one sentence>
- Context: <file paths, prior state>
- MemPalace prior context (L1 query):
  * "auth flow design 2026-04 sessions" -> 3 drawer hits
  * Key learnings: JWT HS256->RS256 migration, refresh token rotation pattern
- Acceptance criteria: <what comes back>
- Format: <table, code, prose>
```

The sub-agent can also call the MemPalace MCP tool from its own context to expand drawers when needed. In a hub-and-spoke topology, every spoke is memory-aware.

---

## AAAK Format: practical detail

AAAK = "Acronym + Abbreviation + Acceptable + Knowledge-dense" structured shorthand.

Example (human-readable conversation):
```
User: I want to design a GraphQL schema for a multi-tenant analytics dashboard.
Claude: Let me check the federation strategy. Common issue is N+1 across tenants.
```

AAAK form (~30x compression):
```
U:design GraphQL schema multi-tenant analytics dash
C:chk federation strat. common: N+1 across tenants
```

Any LLM (Claude/GPT/Llama) parses this shorthand natively without fine-tuning and does not lose context. 30x token savings, equal recall in semantic search.

**For ingest**: keep your raw session history archive as-is; MemPalace ingest applies AAAK compression automatically. Dual storage (raw + AAAK) costs ~5% extra for ~96% recall.

---

## Anti-patterns: memory mistakes

- **Using MemPalace as a wiki replacement**. The wiki is a separate layer for distilled insight. MemPalace is verbatim and raw.
- **Stopping at L0+L1 when it returns no result**. "No result" means L0+L1 failed; drawer expand is mandatory.
- **Diary entries without detail**. If you need to recall the failure pattern tomorrow, no detail = no recall.
- **Querying without ingest**. An empty MemPalace returns "no relevant memory", which the user reads as truth. Ingest is a pre-flight requirement.
- **Cross-platform paths**. `~/.mempalace/` is Unix style. Resolve via the `MEMPALACE_HOME` env var; on Windows it expands under `%USERPROFILE%`.

---

## Quick checklist

Is your Mythos mode memory-aware?
1. MemPalace MCP server installed and registered?
2. Initial ingest done (session history -> wings)?
3. L0+L1 query in the priming flow (170 tok)?
4. Diary query reflex when stuck?
5. Sub-agent briefings carry prior context?
6. Wiki vs MemPalace boundary clear (distilled vs verbatim)?

5 or more = memory-aware Mythos mode is active.

---

## Fallback when MemPalace is absent

Mythos still works without MemPalace:
- Priming orders 5 and 8 are skipped.
- Order 9 (raw session history archive) stays active. Slower but functional.
- Instead of diary entries, a wiki-side `MYTHOS-FAILURES.md` page (optional) carries the human-curated record.

So MemPalace is not required, but the upside is large. The skill set supports both modes.
