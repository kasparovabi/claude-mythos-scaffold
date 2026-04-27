---
type: skill
tags: [system/skill, mythos, migration, execute, atomic-commits]
related: ["[mythos-migration-mode](./mode.md)", "[mythos-migration-plan](./plan.md)", "[mythos-migration-rollback](./rollback.md)", "[mythos-verification](../../core/verification.md)", "[mythos-agent-loop](../../core/agent-loop.md)"]
---

# Mythos Migration Execute

> Atomic commits + test gate + Reflexion per step + sub-agent parallelism.

## Philosophy

- **Atomic commit:** Every commit is standalone deployable. Mid-state never reaches production. Reverting a single commit must not break the whole migration. Isolation is sacred.
- **Test gate every step:** No advance to the next step without build green + unit green + integration green. "Fix it later" is forbidden. Accumulated fail risk grows exponentially.
- **Reflexion after every commit:** What was the goal, what happened, what is the gap, what comes next. Written down. The next commit starts by reading this reflexion.
- **Sub-agent parallelism for independent modules:** [decomposition](../../core/decomposition.md) pattern applied. Distribute independent modules to sub-agents, run in parallel, main agent coordinates. Coupled regions stay sequential.

---

## Atomic Commit Discipline

One commit equals one logical change. Codemod application **or** manual fix, never mixed in the same commit.

**Rules:**

- **Mid-state commit FORBIDDEN:** Half-done type fix is not pushed, half-done rename is not pushed. If you are stuck mid-change, keep it on the branch, do not push.
- **Commit message format:** `migration(<phase>): <module> <change-summary>`
  - Example: `migration(phase-2): auth/oauth codemod react-17 to react-18`
  - Example: `migration(phase-3): user-service manual fix Optional[T] return type`
- **Pre-commit check:** Test green + lint green + build green. If any of the three gates is closed, no commit.
- **Per-commit decision record:** One line in `migration-decisions.md`. What changed, why, which acceptance criterion was met.
- **Revert-friendly:** When a commit is reverted, later commits must not blow up. That is why commits are placed in dependency-aware order (the audit dependency graph guides this).

**Target state:** Average commit size small (50 to 200 LOC), every commit moves tests from green to green, history is bisect-friendly (`git bisect` can hunt regressions).

---

## Test Gate Protocol

```
pre-commit (local, fast):
  - lint (changed files only, eslint --cache)
  - type check (incremental, tsc --noEmit or mypy --incremental)
  - unit tests (changed module + direct dependents)
  - format check (prettier / black --check)

post-commit (CI, comprehensive):
  - full unit test suite (parallel, max workers)
  - integration tests
  - build (all artifacts, dev + prod)
  - bundle size diff (alarm if > 5 percent growth)
  - performance regression check (if baseline exists, k6/lighthouse/pytest-benchmark)
  - security scan (bandit / npm audit / trivy)

per-phase end (manual + automated):
  - e2e tests (playwright / cypress / selenium)
  - manual smoke test (critical user flows, audit "must not break" list)
  - production canary deploy (5 percent traffic, 24h observation)
  - rollback drill (was the rollback path tested)
```

**Rule:** CI red blocks merge through branch protection. Bypassing the pre-commit hook locally with `--no-verify` is forbidden (confirm explicit user request, otherwise stop).

---

## Sub-Agent Parallel Module Migration

**Decision matrix:**

- **Independent modules in audit (low cross-coupling, no shared util)** parallel sub-agents.
- **Overlapping modules (shared utility, transitive dependency)** sequential, main agent runs them.
- **Test infrastructure changes (test-helpers, fixtures)** sequential, in the first phase.

**Sub-agent brief template:**

```
Task: <module-path> migration to <target framework/version>

Context:
  - Breaking change matrix: <relevant subset, from audit>
  - Codemod script: <repo-path or inline>
  - Test command: <cmd, example: pnpm test packages/auth>
  - Acceptance: tests green + baseline metrics within +/- 5 percent
  - Dependencies: <which packages have not been migrated yet, watch out>

Output format: per-commit summary
  - Status: success | partial | blocked
  - Regression findings: <list>
  - Manual fixes applied: <what you did, why>
  - Decision record entry: <markdown line>

Limit: 4 hours or 5 turns. If you cannot fit, report + stop, escalate.
```

**Hub-and-spoke topology:**

- **Main agent:** Phase coordinator. Reads audit, distributes work to sub-agents, serializes conflicts, runs per-phase acceptance check.
- **Sub-agents:** Module workers. One module, focused. Verbose log lives in the sub-agent context, only a summary returns to the main agent.
- **Conflict handling:** When two sub-agents try to change the same shared util, the main agent serializes them. The second waits for the first commit. The main agent watches the commit log.
- **Sub-agent output format:** Maximum 30 line summary. Verbose logs stay in the sub-agent transcript so the main agent context is not polluted.

**Parallelism payoff:** 5 independent modules with 5 sub-agents equals 5x throughput. 25 hours single-agent becomes 5 hours. Migration adaptation of the [decomposition](../../core/decomposition.md) pattern.

---

## Reflexion Pattern (Per Commit)

After every commit, answer 4 questions and save the result to memory (progress note or MemPalace):

1. **What did I do?** (one sentence: "Applied auth/oauth codemod, did 3 manual fixes: Optional[T] return type, async generator type, deprecated callback")
2. **What was the goal?** (acceptance criteria reminder: "All unit tests green, bundle size delta below 5 percent, no behavioral change in OAuth flow")
3. **What is the gap?** ("Tests green but bundle size grew 3 percent, runtime perf benchmark down 2 percent, acceptable. No behavioral change detected.")
4. **What is next?** ("Next commit: user-service module, same codemod plus similar manual fix expected. Risk: shared validation util, main agent should handle instead of sub-agent.")

Saved to memory and read at the start of the next commit. [context-priming](../../core/context-priming.md) pattern.

**Why Reflexion matters:** Pattern recognition. After 5 commits "manual fix type X" repeats, so extend the codemod and gain automation. Skip Reflexion and the pattern stays invisible.

---

## Stuck Detection

Migration adaptation of the Mythos [failure-recovery](../../core/failure-recovery.md) pattern:

- **3+ consecutive test fails on the same module** change pattern. Codemod is insufficient, switch to manual triage. Or skip the module, return to audit, revise the dependency graph.
- **Same codemod ran twice, residual error remains** manual investigation. Codemod might be silently failing (AST match miss). Read the diff, add the missing transformation manually.
- **Sub-agent fresh context** clear assumptions from the previous context. Re-brief the sub-agent with "what has been done so far: <summary>" and reset the starting state.
- **Stuck more than 5 hours** escalation. Pause the phase, revise the audit, change strategy if needed (incremental to parallel-tree, or vice versa). Report to the user: what was tried, what failed, which decision is pending.
- **Sub-agent reports "blocked"** main-agent options: (a) re-brief the sub-agent, (b) try a different sub-agent, (c) move the module to sequential, (d) return to audit.

**Rule:** No progress for 3 turns means change pattern. Do not drop "what should I do" before turn 10. Mythos mode detail.

---

## Codemod Plus Manual Fix Flow

Per-module standard flow:

```
1. Apply codemod
   - jscodeshift -t transform.js packages/auth/
   - or 2to3 -w src/auth/
   - or ts-migrate migrate packages/auth/

2. Build + unit test
   - Build green move to step 3
   - Build red move to step 3a (lint error or syntax error, check the diff)

3. Produce test fail list, triage each:
   a. Codemod miss extend the codemod script, the fix will propagate to other modules.
   b. Manual fix one-off code change, append to audit decision record.
   c. Behavioral change update the test. BUT silent regression risk:
      - Make sure the test update is not masking the behavior.
      - Record "behavioral change accepted" in the audit.
      - Request QA review, do not auto-pass.

4. Lint + format
   - eslint --fix on changed files
   - prettier --write on changed files
   - Re-run tests, on green move to step 5.

5. Atomic commit
   - Commit message format: migration(<phase>): <module> <summary>
   - Append a line to the decision record.

6. Reflexion (4 questions)
   - Save to memory, becomes start context for the next commit.
```

---

## Tool Stack (Execute-Specific)

| Category | Tools |
|---|---|
| Codemod | jscodeshift, 2to3, ts-migrate, recast, Bowler (Python), Babel plugins |
| AST manipulation | ts-morph, Python `ast` module, recast, JavaCC, libcst (Python) |
| Test runner | jest, vitest, pytest, go test, mvn test, cargo test |
| Build | webpack, vite, esbuild, tsc, mvn, gradle, cargo build |
| Lint | eslint, ruff, golangci-lint, clippy, rubocop |
| Format | prettier, black, gofmt, rustfmt |
| CI | GitHub Actions, GitLab CI, CircleCI, Jenkins |
| Diff visualization | git diff, semgrep diff, difftastic |
| Bundle analysis | webpack-bundle-analyzer, rollup-plugin-visualizer, source-map-explorer |
| Perf benchmark | k6, lighthouse, pytest-benchmark, hyperfine |
| Sub-agent | Mythos Task tool (general-purpose), specialized: build-error-resolver, code-reviewer |
| Decision tracking | Markdown decision records, ADR (Architecture Decision Records) |

[tool-stack](../../core/tool-stack.md) is the general guide; this table is the execute-specific subset.

---

## Per-Phase Deliverable

Acceptance checklist at the end of each phase:

- [ ] All planned modules migrated (audit phase scope satisfied)
- [ ] All tests green (unit + integration + e2e)
- [ ] Baseline metrics within +/- 5 percent (build time, bundle size, runtime perf, memory)
- [ ] Decision records up to date (one line for every atomic commit)
- [ ] Stakeholder communication sent (summary report: what changed, what risks remain)
- [ ] Rollback path verified (manual rollback drill done, [rollback](./rollback.md) reference)
- [ ] Production canary deploy successful where applicable (5 percent traffic for 24h, error rate within 110 percent of baseline)
- [ ] Residual dependencies from the previous phase fully removed (no old package, no old path)

If any item is missing, the phase **does not close** and the next phase does not start.

---

## Anti-Patterns

- **Mid-state commit:** Pushing half-done type fixes or half-done renames. Keep it on the branch.
- **Test skip:** Committing a red test with "I will fix this later." No, fix it now or skip the commit.
- **Codemod success is not migration success:** Celebrating just because the codemod ran. Silent regression risk. Test gate plus manual smoke is required.
- **Sequential when parallel is possible:** Running independent modules one by one with a single agent. Skipping sub-agent parallelism wastes throughput.
- **Skipping Reflexion:** "Let me ship commits fast and think later." The commit log balloons, learning is lost, pattern recognition becomes impossible.
- **Skipping per-phase acceptance check:** "We finished this phase, on to the next." The phase does not close until the checklist is complete.
- **Manual fix without git history:** Applying a manual fix and forgetting the decision record. Three months later there is no answer to "why is this here?"
- **Ignoring performance regression:** Bundle size grew 8 percent, dismissed as "small." It will blow up at the phase-end acceptance check anyway.

---

## Quick Checklist

- [ ] Migration plan in hand, phase scope clear ([plan](./plan.md))
- [ ] Codemod script ready, dry-run done
- [ ] Test gate pipeline running (pre-commit + CI)
- [ ] Sub-agent decomposition decision made (parallel or sequential)
- [ ] Sub-agent brief template ready
- [ ] Decision record file open (`migration-decisions.md` or project-specific)
- [ ] Reflexion memory path defined (progress note or MemPalace path)
- [ ] Stuck detection thresholds known (3 fails, 5 hours, 10 turns)
- [ ] Per-phase deliverable checklist reviewed at phase start
- [ ] Rollback path tested ([rollback](./rollback.md))
- [ ] Verification skill recalled ([verification](../../core/verification.md))
- [ ] Agent loop pattern active ([agent-loop](../../core/agent-loop.md))
