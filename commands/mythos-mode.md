---
description: Activate Mythos scaffold with skill set primed for a complex task.
---

# /mythos-mode  Activate Mythos Mode

## Skill Set Path Resolution

Before running the steps, resolve where the skill set lives:

- Skills live in the global Claude Code skills directory under `mythos/`. On Unix-like systems this is `~/.claude/skills/mythos/`. On other platforms use the equivalent location.
- Each skill file is named `mythos-<skill>.md` (mode, context-priming, decomposition, tool-stack, agent-loop, verification, failure-recovery).

In this document the notation `<MYTHOS>/<skill>.md` points at the resolved file inside that directory. `<MYTHOS>` always refers to the global skills directory containing this scaffold.

## Input
$ARGUMENTS

- If an argument is given, run that task in Mythos mode.
- If empty, ask "Mythos mode active. What is the task?" and start at step 1.

## Philosophy

Mythos mode means seeing the capability ceiling and using a scaffold to close what can be closed.

**Closable:** knowledge gap (RAG/web), action capacity (tool/MCP), persistence (loop), domain context (priming).
**Not closable:** raw reasoning depth, novel pattern recognition, sample efficiency.

Honest expectation: 40 to 60 percent of Mythos quality on narrow tasks. Far less on areas like CVE discovery or exploit dev.

## Steps

1. **Load mode and rules.**
   Read `<MYTHOS>/mode.md`.
   The seven behavior rules in that file (persistence, verify, context budget, cutoff, plan-execute, parallel, destructive-stop) are the law for this run.

2. **Threshold test.**
   Does this task actually deserve Mythos mode?
   - One-line fix, factual question, five-minute job: skip the mode, do it directly, report.
   - Multi-step, multi-domain, real risk of getting stuck: continue.

3. **Priming.**
   Follow `<MYTHOS>/context-priming.md`:
   - Read the active `CLAUDE.md` (in cwd) and any related project notes.
   - Scan a session history archive if one is maintained, and load relevant prior pages.
   - If the topic is past your knowledge cutoff, use WebSearch and WebFetch.
   - Context budget: stay under 15 percent of the 1M window.

4. **Decomposition.**
   Follow `<MYTHOS>/decomposition.md`:
   - Three-question decomposition test (single context, independence, verbosity).
   - Write a plan into TodoWrite.
   - Decide on sub-agents (Explore, Plan, Architect, Code-reviewer, Security, Build-error).
   - Independent parts go to parallel sub-agents.

5. **Tool stack.**
   Follow `<MYTHOS>/tool-stack.md`:
   - Cascade: cheap and fast first.
   - Independent searches go in one message as parallel tool calls.
   - Decide if MCP is needed (chrome, playwright, firecrawl, computer-use, dedicated).
   - No grep, find, or cat inside Bash. Use the dedicated tools.

6. **Agent loop.**
   Follow `<MYTHOS>/agent-loop.md`:
   - Plan-and-Execute by default. ReAct only when the flow is genuinely uncertain.
   - After each major step run Reflexion (four questions: what I did, what the goal was, the gap, next move).
   - Critical output (code, plan, report) gets at least one Self-Refine pass (target quality 8/10).
   - Stuck detection: three turns with no progress means change the pattern.
   - Persistence ceiling: 10 turns, 30 minutes, or 200K tokens (20 percent of Opus 1M).

7. **Verification.**
   Follow `<MYTHOS>/verification.md`:
   - Definition of done: verify passed, output read, state consistent.
   - Headless first (build, test, lint), visual after.
   - Output reading discipline: exit code is not enough, read stderr and warnings.
   - If the UI changed, run a Playwright or Chrome MCP smoke test.

8. **Failure recovery (if needed).**
   Follow `<MYTHOS>/failure-recovery.md`:
   - Classify the failure: code, tool, logic, knowledge, env, stuck.
   - Apply the class-specific strategy.
   - Ralph Loop: verify, fail, feedback, iterate.
   - Change the pattern instead of retrying the same path.
   - Avoid destructive actions, ask the user.

9. **Report.**
   When the task is done, give a compact report:
   ```
   Did: <one sentence>
   Verify: <which checks passed>
   Files: <changed or created files>
   Next: <if any>
   ```

   If the task failed at the persistence ceiling, stop and report:
   ```
   Tried:
   1. <approach A> -> <result and reason>
   2. <approach B> -> <result and reason>
   Current hypothesis: ...
   Options: A. ... B. ...
   Which should I try?
   ```

## Rules

- **Skip the mode when it is not warranted.** Mythos overhead on trivial work is pure loss.
- **Stay faithful to the skill set.** Steps 3 to 8 are detailed in the linked files. Do not bypass them with "my own way."
- **No completion without verify.** A TodoWrite item is not done until verify passes.
- **When stuck, change the pattern.** Retrying the same path is not persistence, it is inertia.
- **Never run destructive actions silently.** `rm -rf`, `git reset --hard`, force-push always need explicit user approval.
- **Report in the user's language.** Direct, no AI slop, no filler.
- **Be honest about the raw capability ceiling.** If the task needs reasoning depth the scaffold cannot reach, say "I can simulate it with the scaffold but it will not be enough."
