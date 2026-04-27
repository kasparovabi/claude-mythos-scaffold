---
type: skill
tags:
  - system/skill
  - mythos
  - tool-selection
related:
  - ./mode.md
  - ./decomposition.md
---

# Mythos Tool Stack

> Protocol for which tool to use, when, and in what order.
> The action-capacity leg of mythos mode.

---

## Philosophy

1. **Cascade rule:** Cheap and fast first, expensive and deep later. One Glob beats three Greps.
2. **Parallel by default:** Independent calls go in one message in parallel. Sequential only when there is a dependency.
3. **Right tool, right job:** Do not call grep/find/cat from Bash. A dedicated tool exists (Grep/Glob/Read).
4. **MCP is not a last resort, but it is also not a duplicate:** If a dedicated MCP exists, it comes before generic browser/computer-use.

---

## Tool Tiers

### Tier 1: File ops (fastest, mostly read-only)

| Tool | When | When not |
|---|---|---|
| **Read** | Path is known, you need the contents | Listing a folder (use Glob) |
| **Glob** | Name/extension pattern (`**/*.tsx`) | Content search (use Grep) |
| **Grep** | String/regex inside content | Pattern is in the filename (use Glob) |
| **Edit** | Exact replacement in an existing file | New file (use Write) |
| **Write** | New file or full rewrite | Small change (use Edit) |

**Cascade:** Glob to find, Read to open, Grep when content needs scanning, Edit to change.

### Tier 2: Action / Execution

| Tool | When |
|---|---|
| **Bash** | Running commands (git, npm, pytest, build, lint). For cross-platform, use forward slashes and `/dev/null` |
| **PowerShell** | Windows-specific tasks (HKLM, regedit, Get-Service). Most cases already covered by Bash |

**Banned inside Bash** (a dedicated tool exists):
- `find` becomes Glob
- `grep`/`rg` become Grep
- `cat`/`head`/`tail` become Read
- `sed`/`awk` become Edit
- `echo > file` becomes Write

### Tier 3: Discovery / Web

| Tool | When | Cost |
|---|---|---|
| **WebSearch** | Current events, finding canonical links, "X 2026" style queries | Low, fast |
| **WebFetch** | You need the contents of a specific URL, analyze a page | Medium |
| **mcp__firecrawl__firecrawl_scrape/crawl** | Multi-page deep crawl, structured extraction | High, slow |
| **mcp__Claude_in_Chrome__** | Authenticated web app, action inside the user's browser (DOM-aware click, form fill) | Medium |

**Cascade:** WebSearch (find link), WebFetch (canonical page), Firecrawl (when deep crawl is needed).

### Tier 4: Sub-agent Delegation

`Task` tool. Detail: [decomposition](./decomposition.md).

One-liners:
- **Explore**: codebase exploration, broad search (when 3+ Glob/Grep would be needed)
- **Plan / planner**: design, implementation strategy
- **Architect**: system-level decision
- **Code-reviewer / security-reviewer**: review of code that was written
- **Build-error-resolver**: build/test failure
- **General-purpose**: exploration with unclear type

### Tier 5: MCP (specialized tools)

Currently deferred (loaded via ToolSearch):

| MCP | For what | Tier |
|---|---|---|
| `computer-use` | Native desktop apps (Notes, Maps, Settings, third-party) | Read/click/full per app |
| `Claude_in_Chrome` | Web app navigation (browser tier "read", computer-use cannot click) | DOM-aware |
| `playwright` | E2E tests, headless browser in CI | Full |
| `firecrawl` | Web crawl, structured extraction | API-based |
| `notebooklm` | Research synthesis, document Q&A | API |
| `Composio` (slack, gmail, asana, linear, etc.) | API-backed app actions | Auth required |

**Decision:** If a dedicated MCP exists, use it (Slack work goes to slack-automation, Gmail work goes to gmail-automation). Otherwise Chrome, otherwise computer-use.

---

## Parallel vs Sequential Decision Matrix

| Situation | Decision |
|---|---|
| Reading 3 different files (contents are independent) | **Parallel**: 3 Reads in one message |
| Glob + WebSearch + Read CLAUDE.md (task-start priming) | **Parallel**: all independent |
| Build run + test run (build then test) | **Sequential**: tests do not run until build passes |
| Write a file then read-back to verify | **Sequential** (write must finish before read sees it). Edit/Write tracking exists, so often unnecessary |
| 5 parallel sub-agents (independent research) | **Parallel**: 5 Agent calls in one message |
| Sub-agent A output feeds sub-agent B input | **Sequential** (dependent) |

**Rule:** If you are thinking "first X, then Y" but X has no dependency on Y, run them in parallel.

---

## Mock vs Real Action Distinction

| Type | Tool examples | In plan mode | Auto-allowed |
|---|---|---|---|
| **Read-only** | Read, Glob, Grep, WebSearch, WebFetch, Bash (`ls`, `git status`) | Allowed | Yes |
| **Workspace mutate** | Edit, Write, Bash (`mkdir`, `git add`) | Forbidden | Depends on settings |
| **External mutate** | Bash (`git push`, API call), MCP (`gmail send`, `slack post`) | Forbidden | No (user approval) |
| **Destructive** | Bash (`rm -rf`, `git reset --hard`, `--force`) | Forbidden | Never silently |

**Rule:** In plan mode, only read-only and plan-file writing. Even in auto-mode, destructive actions stop and ask the user.

---

## Tool Chains (Recipes)

### Recipe: New codebase exploration
```
1. Glob "*.md" + Glob "package.json" + Read CLAUDE.md (parallel)
2. Read package.json, find entry point
3. Glob src/**/*.{ts,tsx,py,go}, see main files
4. Read 2-3 main files
5. (if deep dive needed) Explore agent for pattern discovery
```

### Recipe: Bug investigation
```
1. Read error log / stack trace (if user provided one)
2. Grep error message, first frame
3. Read that file (50 lines around it)
4. Grep call site, see who calls it
5. Read caller, form root-cause hypothesis
6. (if needed) Bash run minimal repro
```

### Recipe: New feature implementation
```
1. priming (read CLAUDE.md, related module) in parallel
2. TodoWrite for sub-steps
3. Plan agent for design (when complex)
4. Edit/Write for implementation
5. Bash test/build to verify
6. Code-reviewer agent for review
```

### Recipe: Knowledge question (post knowledge cutoff)
```
1. WebSearch (1-3 parallel queries, different angles)
2. WebFetch (canonical source: Anthropic docs, GitHub repo, arxiv)
3. Cross-validate (do 2 sources say the same thing)
4. Answer plus Sources
```

### Recipe: Web app smoke test
```
1. mcp__plugin_playwright_playwright__browser_navigate
2. browser_snapshot, see DOM
3. browser_click / browser_fill_form, mimic user flow
4. browser_console_messages, check for errors
5. browser_take_screenshot, visual evidence
```

---

## MCP Trigger Decision

| Task | Right tool |
|---|---|
| Send email | `gmail-automation` skill (auth required) or Gmail MCP |
| Slack message | `slack-automation` |
| GitHub issue/PR | Bash via `gh` CLI over GitHub MCP |
| Click in a web app (open in chrome) | `Claude_in_Chrome` |
| Native desktop app (Notes, Calendar) | `computer-use` |
| Headless E2E test | `playwright` MCP |
| Structured extraction from a web page | `firecrawl_extract` |
| Multi-page deep crawl | `firecrawl_crawl` |
| Document Q&A, podcast, mind map | `notebooklm` |

**Default:** First `gh` or native CLI, then MCP. When a CLI exists, prefer it over MCP.

---

## Anti-Pattern: Tool Waste

- **Searching the same thing with 3 tools:** if 1 Glob/Grep fails, jump to the Explore agent. Do not run "Glob+Grep+Bash find" in parallel for the same query.
- **Sub-agent opening another sub-agent:** a Task agent cannot spawn another Task. Work must finish in its own context.
- **WebFetch loop:** one URL fetched, contains 10 more URLs. Do not fetch each one separately, use firecrawl_crawl in one shot.
- **Imitating a dedicated tool inside Bash:** do not write `find . -name "*.tsx"`, Glob exists.
- **Calling MCP that is not loaded:** check the deferred MCP list. If absent, think of a generic alternative (build pipeline check via Bash, GraphQL endpoint hit via WebFetch, etc.).

Detail: when stuck, see [failure-recovery](./failure-recovery.md).
