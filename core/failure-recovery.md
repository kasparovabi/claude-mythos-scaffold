---
type: skill
tags:
  - system/skill
  - mythos
  - failure-recovery
  - ralph-loop
related:
  - [mode](./mode.md)
  - [agent-loop](./agent-loop.md)
  - [verification](./verification.md)
  - [memory](./memory.md)
---

# Mythos Failure Recovery

> What to do when things break, how to escape when you get stuck.
> The flip side of Mythos's "iterate" behavior. The Ralph Loop pattern.

---

## Philosophy

1. **Failure is feedback, not the end.** A failed verify is a signal for the next round. Log it, analyze it, iterate.
2. **Change the pattern, do not retry.** If the same approach failed twice, a third attempt rarely succeeds. Try a new angle.
3. **Avoid destructive actions.** Recovery panic makes things worse. `rm -rf`, `git reset --hard`, force-push usually do harm.
4. **Persistence is not stubbornness.** Persistence does not mean refusing to stop after 10 turns. The exit point must be clear.

---

## Failure Classification

Classify the error first, then choose the strategy:

| Class | Symptom | Recovery approach |
|---|---|---|
| **Code error (compile/runtime)** | Build broken, exception thrown, lint fail | Read the error message and stack trace, then fix |
| **Tool error** | Permission denied, missing path, invalid syntax, timeout | You are using the tool wrong. Find an alternative or fix |
| **Logic error** | Test passes but behavior is wrong | List your assumptions, verify each one with a test |
| **Knowledge gap** | You do not know, do not remember, post-cutoff | WebSearch + WebFetch + cross-validate |
| **Env error** | Network, disk, env var, dependency missing | Check the environment, then install or configure |
| **Stuck** | The loop spins, no progress | Change the pattern, hand fresh context to a sub-agent |

**First question:** "Which class is this?" Wrong classification leads to wrong recovery and deeper stuck.

---

## Class-Based Recovery Strategy

### Code error
```
1. Read the entire error message, including the stack trace
2. Open the file:line of the first frame (Read)
3. Read 30 lines of context around it
4. Form a hypothesis: which assumption is wrong?
5. Write a minimal repro (a test or a CLI command)
6. Try the fix, then verify
7. Still failing? Write 2 or 3 different hypotheses, test them in order
```

### Tool error
```
1. Error type:
   - Permission: check settings.json, ask the user
   - Missing path: confirm with Glob that it actually exists
   - Syntax: check tool docs or help
   - Timeout: try background mode, or pick another tool
2. Is there an alternative tool?
   - Bash failed: try PowerShell?
   - Glob found nothing: try Grep?
   - WebSearch insufficient: try Firecrawl?
3. Still no luck: ask the user, "I need this tool, will you grant it?"
```

### Logic error
```
1. Write the expected behavior vs the actual behavior plainly
2. Assumption list:
   - "Input arrives in format X"
   - "Calling Y returns Z"
   - "This function is idempotent"
3. Verify each assumption with a test or Read
4. Find the wrong assumption, then fix it
5. Add a test (regression guard)
```

### Knowledge gap
```
1. WebSearch (1 to 3 parallel queries from different angles)
2. WebFetch from a canonical source (vendor docs, GitHub repo, arxiv, accepted SO answer)
3. Cross-validate: do two sources agree?
4. Still uncertain: ask the user, "I researched this, I found X but I am not sure. Do you know?"
```

### Env error
```
1. Env var or config missing: `printenv`, read the relevant .env
2. Dependency: `npm ls X`, `pip show X`, `go list -m all | grep X`
3. Network: ping, curl test
4. Disk: `df -h` (Windows: Get-PSDrive)
5. Fix, then tell the user, "I installed/added X. OK?"
```

### Stuck
Detail below in the Ralph Loop section.

---

## Ralph Loop Pattern

Inspired by Ralph Wiggum: the "iterate without giving up" pattern.

### Skeleton
```
while not verifyCompletion():
    state = read_current_state()         # git diff, progress log, last output
    diff = intent - actual                # what was the goal vs what happened
    next_step = plan_correction(diff)    # correction plan
    execute(next_step)
    verify()
    log_learning(state, action, result)  # append to the progress note
```

### State reading
At the start of every turn:
- `git diff` (if it is a git repo): see the latest change
- `progress.txt` or a dated run log file: what happened in earlier turns
- The last tool output: summarized, not verbose

### Diff detection
```
Intent: "Tests pass, build is clean"
Actual: "Tests 2/5 fail, build passes"
Diff: Logic error in 2 tests
Action: Switch to logic error recovery
```

### Learning log
At the end of each turn, add 1 to 3 lines to the progress note:
```
[2026-04-26 14:30] Turn 4: pytest 2 fail (test_auth_login, test_token_refresh).
                          Cause: token TTL calculation wrong. Fix: timezone-aware datetime.
                          Result: 5/5 pass. Build still green.
```

### Memory persistence
For long-running work, keep a per-run log file (a dated markdown file in your notes or repo):

```markdown
---
type: mythos-run
status: in-progress
started: 2026-04-26
---

# Run: <task>

## Intent
<one sentence goal>

## Turn log

[14:00] Turn 1: ...
[14:15] Turn 2: ...
```

Mark `status: done` when finished. The log becomes a reference for future runs.

---

## Persistence Limits

Endless iteration is forbidden. Exit points:

| Signal | Action |
|---|---|
| 10 turns | Stop, give the user a compact report |
| 30 minutes wall clock | Same |
| 200K token consumption (about 20% of a 1M window) | Same |
| Same error 5+ turns in a row | Pattern fault, manual input needed |
| Destructive action required (rm, reset --hard) | User approval required first |
| User feedback needed (ambiguous spec) | Ask |

**Compact report template:**
```
What I have tried so far:
1. <approach A> -> <result + reason>
2. <approach B> -> <result + reason>
3. <approach C> -> <result + reason>

Current state: <state>
My hypothesis: <likely cause>

Options:
A. <option>
B. <option>
C. Skip this, move to other work

Which one should I try?
```

---

## Pattern Change

Same approach failing twice does not mean attempt three. It means approach three.

| Old approach | New approach |
|---|---|
| Retry with the same tool | Switch to an alternative tool |
| Same sub-agent | Different sub-agent type, or the main agent |
| Same plan | Re-decompose with a different breakdown |
| Same hypothesis | Write 2 alternative hypotheses, test both |
| Looking at one file | Cross-cutting view, including the callers |
| Trusting memory | WebSearch plus verification |

**Anti-pattern:** "I will try one more time, maybe it works now." It will not. Change the pattern.

---

## Avoiding Destructive Actions

Recovery tempts you toward panic moves. Do not take them:

| Do not | Instead |
|---|---|
| `rm -rf node_modules && npm install` | What is the cause? Maybe a single package, maybe the lockfile |
| `git reset --hard HEAD~5` | Keep the branch, switch to a new branch, layer the fix on top |
| `git push --force` | Is there an alternative to force-push? Or get approval |
| `kubectl delete pod -A` | Just the affected pod, or scale 0 then scale 1 |
| `DROP TABLE x` | Migrate down, or rename and recreate |
| `--no-verify` | Why did the hook fail? Fix that |
| Deleting half-finished Edits to "clean up" | Use Read to see actual state first, then decide |

**Rule:** Any irreversible action requires user approval. "This action cannot be undone. I plan to do X. Approve?"

---

## Recovery Memory (Two-Layer)

Two layers of failure log, working together:

### Layer 1: Agent diary (automatic, verbatim)
If you have a memory store wired up (see [memory](./memory.md)):
```
diary-add \
  --wing Project-X \
  --room failure-recovery \
  --content "Pattern: <description>. Cause: <root>. Fix: <solution>. Verify: <evidence>."
```

In a future session, the same pattern surfaces in a low-cost L1 query and you skip straight to the resolution.

### Layer 2: Curated wiki (optional, distilled)
Recurring patterns get distilled into your vault's failure log file:

```markdown
---
type: failure-log
---

# Mythos Failure Log

## Pattern: TypeScript build fail with strict mode + JSX
- First seen: 2026-03-12
- Typical cause: tsconfig has jsx: "preserve" but runtime needs it compiled
- Fix: tsconfig.json jsx: "react-jsx"
- Recurrence: 3 times

## Pattern: pytest collects 0 tests
- Cause: missing __init__.py or wrong pytest.ini
- Fix: check conftest.py
- Recurrence: 2 times
```

**Flow:** Diary captures verbatim. After 3+ recurrences, distill into the wiki. Without an automatic diary, lean fully on the wiki layer (less automation, more manual curation).

---

## Anti-Pattern: Recovery Mistakes

- **Retrying the same approach.** Change the pattern, do not retry.
- **Hiding the failure.** Do not say "build passed" when it did not. Report the fail.
- **Ignoring the persistence limit.** Turn 20, one hour deep, same problem.
- **Performing destructive actions silently.** Ask, ask, ask.
- **Filling a knowledge gap with a guess.** Do not invent. Search.
- **Failing to brief a sub-agent on the failure.** Add "X was tried and failed, do not retry" to the briefing.

---

## Quick Checklist

When you hit a failure:
1. Which class? (code / tool / logic / knowledge / env / stuck)
2. What is the strategy for that class?
3. Has the same approach been tried 2+ times? Change the pattern.
4. Am I close to the persistence limit?
5. Is a destructive action involved? Ask first.
6. Did I log the learning?
7. If delegating, did I pass the failure context to the sub-agent?

When recovery completes, return to the main loop: [agent-loop](./agent-loop.md)
For verify retest: [verification](./verification.md)
