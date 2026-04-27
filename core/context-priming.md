---
type: skill
tags:
  - system/skill
  - mythos
  - rag
  - context-priming
related:
  - "[Mode](./mode.md)"
  - "[Tool Stack](./tool-stack.md)"
  - "[Memory](./memory.md)"
---

# Mythos Context Priming

> Which information must be loaded before the task starts. The Agentic RAG protocol.
> The "domain context" face of Mythos mode.

---

## Philosophy

1. **Priming = RAG for yourself.** Whatever you need to know at task start gets **loaded into context**. You do not guess.
2. **Less but correct.** Wrong priming is worse than empty priming, because it produces wrong assumptions. Empty context beats wrong context.
3. **Recency wins.** Information past the knowledge cutoff requires web verification.
4. **Local authority.** If the knowledge lives in your local sources, scan them before reaching for the web.

---

## Priming Hierarchy

Authority order top to bottom. Higher entries override lower ones.

| Rank | Source | Used for |
|---|---|---|
| 1 | Project root context file (e.g. `CLAUDE.md`) | User profile, tone, naming conventions, anti-patterns |
| 2 | Global rules (`~/.claude/rules/*.md`) | Cross-project rules: agents, security, testing, conventions |
| 3 | Active project notes | Current project status, last action, open questions |
| 4 | Skill files for the current task | Specific protocols when a relevant skill exists |
| 5 | **MemPalace L0+L1 query** (170 tok) | Prior insights from past sessions, when MemPalace is set up. See [Memory](./memory.md) |
| 6 | Knowledge index of your local notes | Distilled concept and entity pages |
| 7 | **MemPalace drawer expand** (verbatim) | "Did I make this decision before?" Drill into detail |
| 8 | Session history archive | Fallback when MemPalace is absent or you need a deeper search |
| 9 | Quick capture and life-area notes | Loose notes and ongoing area files |

**Conflict rule:** Higher rank overrides lower. If a project note disagrees with the project root context file, the root file wins.

---

## Question Classification (Adaptive RAG)

Classify each question first, then pick a retrieval strategy. **Naive RAG (scan everything for every question) is expensive and noisy.**

| Class | Example | Strategy |
|---|---|---|
| **Single-fact lookup** | "Where does config X live?" | Read the root context file, done |
| **Single-domain query** | "What is the M3 entry rule?" | Read the relevant project file plus memory |
| **Multi-hop** | "How do these two systems integrate?" | Multi-doc: both project files plus cross-links |
| **Temporal/current** | "When was version 4.7 released?" | WebSearch required (post-cutoff) |
| **Synthesis** | "What did I learn this week?" | Session history scan plus distill skill |
| **Vague** | "What do we know about topic X?" | Hit the knowledge index first, then targeted reads |

---

## Priming Flow

### Step 1: Top level (every task start)
```
- Read the root context file (~200 lines, fast)
- Glob the active project notes for the project list
- Read global rules if not already known
```

### Step 2: Task-domain reads (in parallel)
```
For "build error in service X":
- Read the relevant project notes
- Read related concept pages from the knowledge index
- Glob recent session history files for the same project (last 5)

For "agent system design":
- Read the agent-system project notes
- Read global agent rules
- Glob recent session history for the same project (last 5)
- Read the decomposition skill
```

### Step 3: Knowledge index sweep (when present)
```
- Read the vault's knowledge index
- If a relevant concept page exists, read it
- Follow cross-links one hop deep
```

### Step 4: Past sessions (optional)
```
- Glob the session history archive for the relevant project and recent dates
- Read the latest 2-3 files
- Note repeating patterns
```

---

## External Context (Web)

Post-cutoff information, canonical documentation, current state.

| Tool | When | Output |
|---|---|---|
| **WebSearch** | "X 2026 best practices", "Y release date" | Link list plus summary |
| **WebFetch** | Deep analysis of a known URL | Structured content |
| **Structured search** (e.g. `firecrawl_search`) | When WebSearch is too shallow | Structured results |
| **Site crawl** (e.g. `firecrawl_crawl`) | 10+ pages from one site at once | Whole-site content |
| **Schema extract** (e.g. `firecrawl_extract`) | Pull specific fields from a URL into a schema | Typed JSON |

**Cross-validation rule:** Important claims need 2 independent sources. Single-source claims get flagged as "claim" and surfaced to the user.

---

## Knowledge Cutoff Discipline

Cutoff: **January 2026.** Today: **2026-04-26.**

Anything after the cutoff requires verification:

| Information type | Behavior |
|---|---|
| New model, product, release | WebSearch required, "memory says X" is unreliable |
| Library/framework version | WebSearch plus the GitHub releases page |
| Person/organization status | WebSearch (who is doing what right now) |
| Stable concept (e.g. "transformer architecture") | Memory is enough, no verification needed |
| Local project state | `git log` or file read. Local files are authoritative |

**"Memory says X exists" is not the same as "X exists now":** A path, function name, or flag pulled from memory must be verified with grep or read before use. Memory is **a snapshot from then**, not current state.

---

## Context Budget

Opus 4.7 = **1M context window**. Wide, not infinite.

| Budget slice | Max share | Example |
|---|---|---|
| **System + tool definitions** | 5-10% | ~50-100K (automatic) |
| **User conversation** | 20-30% | Multi-turn |
| **Priming** | **10-15%** | ~100-150K. Hard ceiling |
| **Tool outputs (Read, Bash, Search)** | 30-40% | The body of the work |
| **Buffer / reasoning** | 15-20% | Whatever is left |

**If you blow past it:**
1. **Sub-agent delegate.** Verbose work (test logs, codebase scans) stays in the sub-agent context, only the summary returns.
2. **Strategic compact.** Use the `strategic-compact` skill as a manual checkpoint.
3. **Filtered priming.** Do not read whole files. Grep for the relevant section.

**On Sonnet/Haiku 4.x** the window is 200K, ceiling 20% (~40K). Priming has to be much tighter.

---

## Local Knowledge Integration

When your local note system has a wiki layer, integrate it:

- During priming, read the knowledge index. If a relevant concept page exists, load it.
- Valuable findings from web search feed back into the wiki (tagged as new findings) so future priming is faster.
- Concentrated learnings from session history may already have been distilled into knowledge pages. Check there.

Use your vault tooling to ingest, query, and lint the wiki layer.

---

## Anti-Patterns

- **Reading every local file for every task.** Noise and context waste.
- **Trusting memory without verifying.** Especially after the cutoff.
- **Taking user-supplied paths on faith.** If the path is wrong, the task fails. Always confirm the file exists.
- **Saying "it does not exist" without a web search.** Not in your local notes means "not in my notes," not "not in the world."
- **Skipping priming and guessing.** "Probably under src/" loses to a one-line Glob that gives you certainty.

---

## Quick Checklist

Before starting a task, ask yourself:
1. Which root context file and active project note apply here? Have I read them?
2. Do I need post-cutoff information? Then WebSearch.
3. Is there a similar past session or decision in my notes? Then Glob the session archive.
4. Does the knowledge index have a relevant concept page?
5. Is my context budget enough, or do I delegate to a sub-agent?

If you cannot pass all five, you are under-primed. You will produce a wrong answer, naturally.
