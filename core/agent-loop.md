---
type: skill
tags:
  - system/skill
  - mythos
  - agent-loop
  - self-critique
related:
  - [mode](./mode.md)
  - [decomposition](./decomposition.md)
  - [verification](./verification.md)
  - [failure-recovery](./failure-recovery.md)
---

# Mythos Agent Loop

> Turn Mythos's most defining behavior into a protocol: iterate without giving up.
> Self-critique plus structured iteration.

---

## Philosophy

1. **Plan-and-Execute by default.** For most work, plan first, then execute. Use ReAct (think-act-observe) only when the flow is genuinely uncertain.
2. **Reflexion after every major step.** "What did I do, what was I aiming for, what's the gap, what's the next round?"
3. **Self-Refine on critical output.** Code, plans, reports: write first, critique, then revise.
4. **Stuck equals signal to change pattern.** Stop trying the same path. If three rounds yield no progress, change the approach.

---

## Loop Pattern Selection

| Pattern | When to use | Character |
|---|---|---|
| **Plan-and-Execute** | Flow is clear, steps are roughly independent, output is predictable | Plan first, then run. Most efficient for most work. |
| **ReAct** | Flow is uncertain (debugging, exploratory analysis) | Think then Act then Observe, one tool call per step. Slow but flexible. |
| **Reflexion** | Multi-attempt task where learning is required | Self-critique at the end of each round, push to memory, correct on the next round |
| **Self-Refine** | Improving the quality of a single output (code, report) | Generate then Critique then Refine, until the threshold is met |
| **Ralph Loop** | Verification exists, fail equals continue, pass equals stop | Verify-fail-iter, external signal as terminator |

**Decision matrix:**
- "Implement a new feature" goes to Plan-and-Execute plus Self-Refine (code quality)
- "Find this bug" goes to ReAct (flow is unknown)
- "Finish this PR, make tests pass" goes to Ralph Loop (with verify)
- "Write a complex report" goes to Plan-and-Execute plus Self-Refine (revise)
- "Design this system" goes to Plan-and-Execute plus Reflexion (weigh alternatives)

---

## Plan-and-Execute Detail

### Phase 1: Plan
Start with a TodoWrite list. Items should be:
- Imperative ("Write the auth middleware", "Add the test", "Run the build")
- Sequential by default if independence is unclear
- Each a clear step, even if a single tool call cannot finish it

### Phase 2: Execute
First TodoWrite item is `in_progress`, the rest stay `pending`. Run it. When it finishes, mark `completed` and promote the next to `in_progress`.

### Phase 3: Replan (when needed)
Signals that the plan must change:
- Could not perform a step (no tool, no permission)
- Performed a step but found something different, plan is stale
- User provided new information

Update the TodoWrite list (delete stale items, add new ones), revise explicitly. Do not drift silently.

---

## Reflexion Protocol

After each major step (a TodoWrite item completes), run a 4-question self-critique:

```
1. What did I do? One-sentence summary.
2. What was I aiming for? Acceptance criterion.
3. What's the gap? If any.
4. What's the next round? Correction or continue.
```

**Memory:** When handing off to a sub-agent, include this summary in the briefing. "Last round I tried X, got Y, now I will try Z."

**Progress log (optional):**
For long, multi-round work, keep an append-only progress log file:
```
[2026-04-26 14:23] Step 3: ran pytest, 2 tests fail. Error: AssertionError on user_id type.
[2026-04-26 14:25] Step 4: type fix, pytest passes.
```

This log is also used in the Ralph Loop. Detail: [failure-recovery](./failure-recovery.md)

---

## Self-Refine (Output Revision)

For critical output (code, plan, report, documentation), require at least one revision round:

### Phase 1: Generate
First version, clean pass. Before showing the user.

### Phase 2: Critique
Score your own output 0-10:
- **Code:** Is it correct, are edge cases covered, does it pass lint, is it idiomatic
- **Plan:** Are all steps present, are dependencies clear, is the acceptance criterion written
- **Report:** Does it answer the question, is there evidence, no AI slop

Threshold: **8/10**. Below that, revise.

### Phase 3: Refine
Address the critique and rewrite. One round may not be enough. 7/10 to revise to 9/10.

**Limit:** 3 revision rounds. If still not 8, hand the output to the user with the limit stated: "This direction Y is still weak, which of options X do you want?"

---

## Stuck Detection

"Stuck" means no progress, but the loop keeps running. Danger signals:

| Signal | Action |
|---|---|
| **Same error for 3 rounds** | Change the pattern. Do not retry with the same tool. |
| **Read the same file 5 plus times** | It's already in context, the fetch is wasteful |
| **TodoWrite item `in_progress` for 30 plus minutes** | Task is too broad, split it |
| **Sub-agent returned "fail" twice in a row** | Briefing is insufficient or task is impossible |
| **Waiting on user reply** | No automatic progress, do not make extra tool calls |

Detail recovery: [failure-recovery](./failure-recovery.md)

**Persistence limits:**
- 10 rounds (one round equals one TodoWrite item plus verify)
- 30 minutes wall clock
- 200K token consumption (20 percent of Opus 1M)

If any limit is crossed, **stop and give a compact report:**
```
Tried:
1. Approach X, failed at point Y (cause)
2. Approach Z, failed at point W (cause)

Current hypothesis: ...
Options:
A. ...
B. ...
Which should I try, or a different direction?
```

---

## Loop Skeleton (Typical Job)

```
1. Take the brief, parse the task
2. priming, load context (see context-priming)
3. decomposition, TodoWrite plus sub-agent decision (see decomposition)
4. Build the plan, an itemized list

5. while not done:
   5a. First pending item, mark in_progress
   5b. Tool calls, parallel where possible
   5c. Read tool output, observe
   5d. Reflexion 4-question pass
   5e. Verify, if testable (see verification)
   5f. Pass, mark completed, continue
   5g. Fail, route to failure-recovery
   5h. Stuck, change pattern or report to user

6. Self-Refine on critical output

7. Final verify, every item completed, build and tests pass

8. Compact report to the user: what was done, what was verified, what's left
```

---

## Sub-Agent Composition

Work delegated to a sub-agent runs **its own loop**. When delegating, add to the briefing:

```
- "Multi-step task, run your own loop"
- "Reflect after each major step"
- "If stuck, stop and report to the main agent"
- Persistence limit: max N rounds, max M minutes
```

The sub-agent's inner loop is invisible (lives in its own context). Only the final summary returns to the main agent.

---

## Anti-Patterns

- **Falling into ReAct without a plan.** Inefficient for multi-step work, wastes tokens.
- **Skipping Reflexion.** "I will fix it later" turns into not fixing it.
- **Showing code to the user without Self-Refine.** First pass is rarely 8/10.
- **Mistaking stuck for persistence.** Trying the same path 5 times is not persistence, it's inertia.
- **Plan changed but TodoWrite is stale.** Drift should not be silent. Revise explicitly.

---

## Quick Checklist

While in the loop, ask yourself:
1. Did I pick the right pattern (Plan-and-Execute, ReAct, Ralph)?
2. Is every major step in TodoWrite?
3. Am I reflecting, or running blind?
4. Did I run Self-Refine on critical output?
5. Am I close to stuck (3-round rule)?
6. Am I close to the persistence limit (10 rounds, 30 min, 20 percent token)?
