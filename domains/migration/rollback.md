---
type: skill
tags: [system/skill, mythos, migration, rollback, recovery]
related:
  - "[mode](./mode.md)"
  - "[execute](./execute.md)"
  - "[failure-recovery](../../core/failure-recovery.md)"
---

# Mythos Migration Rollback

> Rollback is not failure. Deployment safety means the rollback path stays available at all times.

## Philosophy

- **Rollback is not failure.** A migration that can be rolled back is a safe migration. A migration without a rollback path is a risky bet. Treating rollback as failure kills motivation, pushes the team into force-forward decisions, and makes incidents worse. Rollback is a tool, not a verdict on success.
- **Forward-only deployments are dangerous.** Without a rollback in place, production incidents turn into hours of downtime. Migrations that start with a "forward only" mindset produce panic decisions on the first serious incident. The rollback path is insurance: you may never use it, but you must own it.
- **Partial migration recovery is mandatory.** Sitting in a mid-state poisons production. If an incident hits at Phase 5 of 10 while Phase 6 is half done, you carry both operational and mental load. The recovery pattern must be known in advance.
- **Documentation is a rollback prerequisite.** Without decision records (`migration/DECISIONS.md`), atomic commits, and rollback drill notes, a rollback cannot be debugged. If you cannot tell which commit changed what, or which data shape lived in which phase, the rollback becomes its own migration.

## Rollback Triggers

| Trigger | Threshold | Decision |
|---|---|---|
| Test fail spike | >10% over baseline | Automatic rollback (CI block) |
| Performance regression | p95 latency >20% | Automatic rollback |
| Production incident | 5xx spike, error rate >1% | Immediate rollback |
| Scope creep | Phase planned vs actual >50% deviation | Manual decision |
| Resource exhaust | Team capacity, deadline hit | Manual decision |
| Stakeholder cancel | Business priority shift | Manual decision |

Automatic triggers do not wait for human judgment. CI or monitoring kicks the rollback off, then the team moves to postmortem. Manual triggers need stakeholder approval and usually fall under "abort migration."

## Rollback Strategies

### 3.1 Git Revert (atomic commit)

- **Mechanism:** Per-commit revert. This is where atomic commit discipline pays off.
- **Use case:** A single migration commit caused the incident, the rest are stable.
- **Duration:** Minutes.
- **Risk:** Low if commits are atomic. Adjacent commits may surface conflicts.
- **Command:**
  ```
  git revert <sha>
  git push origin main
  # CI/CD redeploy fires
  ```
- **After:** Incident root cause analysis, plan a forward fix.
- **Prerequisite:** Migration commits must be atomic. A commit that mixes schema, code, and config cannot be reverted cleanly.

### 3.2 Feature Flag Toggle (runtime)

- **Mechanism:** Runtime kill switch. LaunchDarkly, Unleash, or a custom env-driven boolean flag.
- **Use case:** The new framework path is live but causing incidents; flip the flag and traffic returns to the old path instantly.
- **Duration:** Seconds.
- **Risk:** Very low. No code changes, no deploy, only flag state changes.
- **Prerequisite:** The new and old paths must coexist during migration (dual-path). This is critical for the Strangler Fig pattern. Both implementations stay in the codebase, the toggle decides which one runs.
- **Scenario:** `if (featureFlag.useNewAuthService) { newAuth() } else { legacyAuth() }`. On incident, set the flag to false and legacy takes over.

### 3.3 Env Var Toggle (deployment)

- **Mechanism:** Behavior controlled via an environment variable.
- **Use case:** No feature flag platform, but runtime config (env vars) is available.
- **Duration:** Minutes (config update plus restart).
- **Risk:** Low. Deploy is required but the code does not change.
- **Example:**
  ```
  MIGRATION_PHASE=v1   # old path
  MIGRATION_PHASE=v2   # new path
  ```
  The app reads the env var on startup and runs the matching code path.
- **Limit:** A restart implies some downtime, however small. Hot-reload setups minimize it.

### 3.4 Database Migration Reverse

- **Mechanism:** Forward plus backward migration script. Alembic (`upgrade()` / `downgrade()`), Flyway (`U__` files), Liquibase rollback tags.
- **Use case:** A schema change must be undone.
- **Duration:** Minutes to hours, depending on data volume, index rebuilds, and lock contention.
- **Risk:** MEDIUM to HIGH. Data loss risk turns this critical.
- **Prerequisite:** The backward script must be tested. The forward then backward then forward loop must run cleanly in a test environment. Skip the drill and the rollback fails roughly half the time.
- **Important:** Some schema changes are not reversible:
  - Column drop (data is gone)
  - Type narrowing (NVARCHAR(500) to NVARCHAR(50), data truncation)
  - Constraint stricter (NULL to NOT NULL, existing NULLs fail)

  In these cases, a backward script accepts data loss. Mark these commits as "irreversible" during the migration plan phase.

## Partial Migration Recovery

**Scenario:** Phase 5 of 10 done, Phase 6 incident, you need to recover but Phases 1 through 5 are running fine in production.

**Approaches:**

- **Forward-fix (recommended):** Fix the Phase 6 root cause and continue forward. Update Phase 6 commits, redeploy. Going back is usually riskier because it means undoing Phases 1 through 5 too.
- **Phase 6 partial revert:** Revert only Phase 6 commits, Phases 1 through 5 stay live. Requires atomic commit discipline. Locate the Phase 6 commit range with `git log`, revert it, leave the earlier phases alone.
- **Full rollback to Phase 0:** Revert all migration commits. Only justified during scope creep or business cancellation. Rare scenario, since it discards the work that is already running.

**Decision matrix:**

| Situation | Decision |
|---|---|
| Incident severity LOW + production stable | Forward-fix (patch Phase 6, keep going) |
| Incident severity HIGH + Phase 6 isolated | Phase 6 revert (Phases 1 through 5 stay) |
| Business cancel + Phase 1 to 5 deprecated path | Full rollback (rare, plan carefully) |
| Phase 6 depends on Phase 1 to 5 + incident HIGH | Forward-fix is mandatory (revert would also break Phases 1 to 5) |

## Rollback Decision Tree

```
Incident detected
     |
     v
Severity classification
+- Critical (5xx >5%, downtime)
|    -> Feature flag off (seconds)
|    -> fix forward in shadow environment
|
+- High (perf regression, 20% latency)
|    -> Git revert last commit
|    -> deploy and monitor
|
+- Medium (test fail spike, 10%)
|    -> CI block (never reached production)
|    -> fix forward in branch
|
+- Low (single test, edge case)
     -> Continue migration
     -> fix in next commit
```

The decision must land within 5 minutes. When severity is unclear, escalate one level. False positives are acceptable, false negatives (underestimating an incident) burn production.

## Rollback Drill (Pre-Migration Test)

This step is critical. During the planning phase, the rollback path must be **tested manually**. Skipping the drill raises migration risk dramatically.

**Drill protocol:**

1. **Set up a test environment** that mirrors production with realistic data shapes.
2. **Apply forward.** Run the new migration script and move the system to the new state.
3. **Verify forward.** Confirm the new state loaded successfully.
4. **Execute rollback.** Use the backward script, the feature flag toggle, or git revert.
5. **Verify rollback.** Did the system return fully to the original state? Is data integrity intact?
6. **Forward again.** Re-apply forward to confirm idempotency.
7. **Drill log.** Record results in `migration/ROLLBACK_DRILL.md`.

**Which rollback methods need a drill:**

- Database migration: REQUIRED (forward then backward then forward loop).
- Feature flag: REQUIRED (flag on, off, on, verify dual-path coexistence).
- Git revert: STRONGLY RECOMMENDED (does the commit-level revert produce merge conflicts).
- Env var toggle: RECOMMENDED (verify the config switch and restart sequence).

If the drill is skipped, flag it as a red flag during the planning phase. Run the drill before going to production.

## Communication Protocol

Communication flow during rollback:

1. **Detect.** Monitoring alarm fires, on-call is notified within 5 minutes.
2. **Decide.** Pick a rollback strategy within 15 minutes. Severity and scope analysis.
3. **Execute.** Run the rollback. Duration depends on the strategy (seconds to hours).
4. **Verify.** Have monitoring metrics returned to baseline? Check error rate, latency, success rate.
5. **Communicate.** Notify stakeholders (Slack, email). If user-facing downtime occurred, update the status page.
6. **Postmortem.** Run a blameless postmortem within 24 to 48 hours. Root cause, prevention, learnings.

**Communication templates:**

- **Internal alert:** "Rollback initiated for [migration X], severity [Y], ETA recovery [Z min]."
- **Stakeholder update:** "Production incident detected at [time], rolled back to stable state. Impact: [Y]. Forward-fix plan: [Z]."
- **User-facing (if downtime occurred):** Status page entry for unplanned maintenance, written at RFC 5424 syslog severity.

## Rollback Log Format

Every rollback event is recorded in `migration/ROLLBACK_LOG.md`:

```markdown
## Rollback: [YYYY-MM-DD HH:MM UTC]

**Trigger:** [test-fail / perf-regression / 5xx-spike / scope-creep / business-cancel]
**Strategy:** [git-revert / feature-flag / env-var / db-reverse / hybrid]
**Affected commits / phases:** [SHA range or Phase X-Y]
**Recovery duration:** [HH:MM]
**Root cause (preliminary):** [one sentence]
**Forward-fix plan:** [one sentence, or "full abort"]
**Postmortem reference:** [link, updated within 24 to 48 hours]
**Lessons learned:** [drill skipped / atomic commit missing / monitoring late]
```

This log serves two purposes: (1) raw input for the postmortem, (2) reference for future migrations facing similar choices.

## Postmortem Flow (Mythos failure-recovery cross)

Apply the Ralph Loop pattern, with details in [failure-recovery](../../core/failure-recovery.md):

1. **Read the state.** `git diff <pre-rollback>..<post-rollback>`, monitoring metrics, error logs, user reports.
2. **Intent vs reality gap.** What did the migration plan promise, what actually happened. Which assumption broke.
3. **Form hypotheses.** List root cause candidates. Code change, infra, data shape, dependency.
4. **Verify.** Log evidence, metric correlation, repro attempts. Test each hypothesis one by one.
5. **Forward plan.** Either forward-fix (most common) or full abort (rare). Write the plan into `migration/PLAN.md`.
6. **Learning log.** Diary entry, knowledge wiki distillation. Which pattern must not repeat, which drill should have run earlier.

Postmortems must stay **blameless**. Look for systemic failures, not individuals. Replace "drill was skipped" with "the system allowed the drill to be skipped."

## Anti-Patterns

- **Skipping the rollback drill.** No drill means roughly 50% rollback failure risk. "Looks like it works" burns production.
- **Breaking atomic commit discipline.** A single commit that bundles schema, code, config, tests, and docs erases the revert anchor and makes partial revert impossible.
- **Untested feature flag deploy.** The runtime kill switch does not actually work, flipping it off crashes the system. Test the flag toggle in a staging environment before the deploy.
- **Untested database backward script.** Forward works, backward fails. Risk of data corruption during a production rollback.
- **Treating rollback as failure.** Causes motivation loss, force-forward decisions, and worse incidents. Rollback is one tool, not a success metric.
- **Late communication.** Stakeholders learning post-incident undermines trust. Notify within 5 minutes of detection, send a recovery update within 30 minutes.
- **Skipping the postmortem.** "We fixed it, move on" loses the lessons. The same mistake returns three months later.
- **Indecision between forward-fix and revert.** Zigzagging (rolling back and pushing forward at the same time) leaves the system half-rolled-back and the team paralyzed. Decide within 15 minutes.

## Quick Checklist

- [ ] Rollback path documented for every phase (in `migration/PLAN.md`)
- [ ] Atomic commit discipline followed (one commit, one concern)
- [ ] Feature flag dual-path coexistence in place (Strangler Fig)
- [ ] Database backward script tested through forward then backward then forward
- [ ] Rollback drill executed, `ROLLBACK_DRILL.md` log exists
- [ ] Monitoring alarms wired to rollback trigger thresholds (test fail 10%, p95 20%, 5xx 1%)
- [ ] On-call rotation active, alert routing correct
- [ ] `ROLLBACK_LOG.md` template ready
- [ ] Postmortem flow defined for the team (24 to 48 hour window)
- [ ] Rollback commands written in the runbook (copy-paste ready)
- [ ] Stakeholder communication templates ready (internal alert, stakeholder update, user-facing)
- [ ] Severity classification table reviewed with the team
