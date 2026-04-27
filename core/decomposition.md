---
type: skill
tags:
  - system/skill
  - mythos
  - decomposition
  - sub-agents
related:
  - ./mode.md
  - ./tool-stack.md
  - ./agent-loop.md
---

# Mythos Decomposition

> Splitting large problems into manageable sub-problems plus deciding when to spawn sub-agents.
> The "context budget plus parallel work" front of Mythos mode.

---

## Philosophy

1. **One context = one brain.** Verbose work (codebase scans, log dumps) pollutes the main context and reasoning degrades. Wall it off in a sub-agent and pull back a summary.
2. **Decomposition = writing it down.** A split that never made it into TodoWrite is not actually split.
3. **Hub and spoke, not mesh.** The main agent coordinates; sub-agents are specialists. Sub-agents do not talk to each other; everything routes through the main agent.
4. **Briefing is everything.** A sub-agent is a fresh context, so the prompt must be self-contained. "Based on the research" is the main agent's job, not the sub-agent's.

---

## Decomposition Test

When a task arrives, start with these three questions:

```
Q1: Solvable in a single context window?
   - Yes -> do not split, just do it
   - No  -> go to Q2

Q2: Are the sub-parts independent?
   - Yes -> parallel sub-agents
   - No  -> sequential, or single agent multi-step

Q3: Will it produce verbose output (>50K tokens)?
   - Yes -> sub-agent is mandatory (prevent context pollution)
   - No  -> main agent can handle it, sub-agent optional
```

**Thresholds:**
- 5+ files to read: parallel reads bloat the main context, use an Explore agent
- 3+ different searches (Grep/WebSearch): Explore agent or a parallel batch
- Test/build runs with >5KB output: sub-agent or `run_in_background`

---

## TodoWrite Discipline

**Rule 1: Every major step goes into TodoWrite.** Split but not on the list = forgotten.

**Rule 2: Only one `in_progress` at a time.** Two parallel jobs = both pending, one delegated to a sub-agent, with the queue listed as pending.

**Rule 3: Mark complete the moment it is done.** Do not batch. Three tasks finished does not mean mark all three completed at once. Mark each one as soon as it lands.

**Rule 4: No completed without verification.** Detail: [verification](./verification.md)

**Rule 5: Delete stale tasks.** If the plan changed, do not leave the old task pending. Remove it.

**Format:**
```json
{
  "content": "Imperative form of the work to do",
  "activeForm": "Form for what is happening right now",
  "status": "pending|in_progress|completed"
}
```

---

## Sub-Agent Decision Matrix

Available agent types (global agents directory plus harness built ins):

| Agent | What for | Typical trigger |
|---|---|---|
| **Explore** | Broad codebase search, "where is X defined" | 3+ Glob/Grep calls expected |
| **Plan / planner** | Implementation strategy, design | Complex feature, multi step |
| **architect** | System design, scalability | Start of a new feature, refactor |
| **general-purpose** | Multi step work of unclear type | Hybrid research plus build |
| **code-reviewer** | Review of code just written | After every code edit |
| **build-error-resolver** | Build/test failures | Compile or lint breakage |
| **go-build-resolver** | Go build/vet/lint | Build error in a Go project |
| **go-reviewer** | Go idiomatic and concurrency review | Go code review |
| **python-reviewer** | PEP 8, type hints, idioms | Python code review |
| **database-reviewer** | SQL/Postgres, migrations | DB changes |
| **e2e-runner** | Playwright E2E | Critical user flow |
| **refactor-cleaner** | Dead code, duplicates | Cleanup pass |
| **doc-updater** | Codemap, docs refresh | After a new feature |
| **tdd-guide** | Test first methodology | New feature, bug fix |

**Selection rule:** pick the closest name match. Otherwise `general-purpose`. A specific agent always beats a generic one.

---

## Hub and Spoke Pattern

```
                +-----------------+
                |   Main Agent    |  <- coordinator
                |  (state, plan)  |
                +----+---+---+----+
                     |   |   |
        +------------+   |   +-------------+
        v                v                 v
   +---------+      +---------+      +---------+
   | Explore |      | Plan    |      | Code-   |
   | agent   |      | agent   |      | review  |
   +---------+      +---------+      +---------+
   (verbose         (design          (post write
    output)          output)           review)
```

**Flow:**
1. Main agent splits the task into pieces and writes them to TodoWrite
2. Independent pieces are dispatched to parallel sub-agents (multiple Task calls in one message)
3. Sub-agents run in **independent context** and never see the main conversation
4. Each sub-agent returns a **summary**: what I did, what I found, my decision
5. Main agent collects the summaries, synthesizes, and reports to the user

**Sub-agent output = summary only.** Verbose logs, file dumps, intermediate reasoning all stay inside the sub-agent context and never reach the main one.

---

## Briefing Quality

The prompt handed to a sub-agent has to be **self-contained**:

| Good briefing | Bad briefing |
|---|---|
| Full file paths (`/proj/src/auth.ts:42`) | "the auth file" |
| The complete error message | "there is an error" |
| Expected format / acceptance criteria | "take a look" |
| What **not** to do ("do not write code, only analyze") | Vague scope |
| What was already tried (no wasted time) | Undated prompt |
| Maximum report length ("under 200 words") | No limit |

**Forbidden:** "Based on the research..." or "from the previous findings..." The sub-agent never saw that conversation. Synthesis is the main agent's job.

**Template:**
```
Briefing:
- Task: <one sentence>
- Context: <file paths, prior state, constraints>
- Acceptance: <what to return>
- Format: <table, code, prose, etc.>
- Limit: <words / lines / time>
```

---

## Parallel Sub-Agent Rules

### Multiple `Task` calls in one message
Independent work goes in a single message with multiple Agent tool calls. The harness runs them in parallel.

```
Agent 1: Explore - "where is session management under src/auth/"
Agent 2: WebSearch - "JWT vs session 2026 best practices"
Agent 3: Read - package.json + tsconfig
```

### Forbidden
- **Conflicting writes.** Two agents writing the same file must run sequentially.
- **Shared state.** Sub-agents do not see each other's variables. Each one has a fresh context.
- **Sub-agent spawning sub-agent.** A Task agent cannot itself call Task. The work has to finish in its own context, or it returns to the main agent saying "this is also needed" (the only return channel is the final output).

### Background mode
`run_in_background: true` is for long running work (10+ minute test suites, deep crawls). A notification arrives when it finishes.

---

## Anti Pattern: Decomposition Mistakes

- **Starting work without writing it to TodoWrite.** A three step plan kept in your head gets forgotten in the middle.
- **Implying "you know the context" to a sub-agent.** It does not. Fresh.
- **Not opening a sub-agent for verbose output.** A 50K line log will burn the main context.
- **Opening a sub-agent for trivial work.** Overhead beats the win. An Explore agent for two file reads is a waste.
- **Doing in sequence what could be parallel.** Independent searches go in one message with multiple Task calls.

---

## Quick Checklist

When a new task arrives:
1. Did you run the decomposition test (Q1 to Q3)?
2. Are all major steps written into TodoWrite?
3. Independent pieces split into parallel sub-agents, or kept single shot?
4. Is the briefing self-contained (paths, error, criteria)?
5. Will verbose output stay inside the sub-agent?

Agent loop detail: [agent-loop](./agent-loop.md)
Verification: [verification](./verification.md)
Failure to recovery: [failure-recovery](./failure-recovery.md)
