---
type: guideline
tags: [system/guideline, mythos, migration, codebase-upgrade]
related:
  - "[mythos-mode](../../core/mode.md)"
  - "[mythos-migration-audit](./audit.md)"
  - "[mythos-migration-plan](./plan.md)"
  - "[mythos-migration-execute](./execute.md)"
  - "[mythos-migration-rollback](./rollback.md)"
---

# Mythos Migration

> Entry point for the codebase migration / framework upgrade Mythos sub-mode. Systematic scaffold for large migrations such as React 16 to 18, Vue 2 to 3, Python 2 to 3, and Java to TypeScript. Activates inside Mythos mode and brings discipline to dependency hell and breaking change chaos.

## Philosophy

- **Migration is not refactor.** Refactor preserves local behavior, touches a single module, stays reversible. Migration touches the whole codebase, ships breaking changes, alters the API surface, and rewrites the dependency graph. Walk into a migration with a refactor mindset and months later you find yourself nowhere near where you started.
- **Atomic commits are law.** Every commit is a standalone deployable state. A mid-state shipped to production puts whole weeks of migration at risk. If a commit contains a half-migrated module and broken tests, that commit already represents a broken main. The discipline: every commit reflects either fully the old system or fully the new system.
- **Rollback path always exists.** Three layers of escape: commit history (git revert), feature flag (runtime toggle), env toggle (deployment-level kill switch). Before migration starts, the question "by which mechanism do I roll back right now" must have three answers. One layer is not enough. If a feature flag bug stops the deploy itself, you need the env toggle.
- **Pick your priority strategy per module.** Two schools: high-risk first (start with the hardest module to surface bad surprises early), or low-risk pilot first (prove the pattern on something small, then move to the hard modules). You cannot pick without knowing the codebase: production-critical core, peripheral util, blast radius. Default to pilot first, then high-risk in the next wave.

## Threshold Test

| Situation | Active? |
|---|---|
| Framework major version upgrade (React 16 to 18, Vue 2 to 3, Angular to React, Python 2 to 3) | yes |
| Language migration (JS to TS, Python to Go, Ruby to Elixir, Java to Kotlin) | yes |
| Platform migration (monolith to microservice, REST to GraphQL, on-prem to cloud) | yes |
| Major dependency upgrade (Webpack 4 to 5, Babel 6 to 7, Django 3 to 5, Spring Boot 2 to 3) | yes |
| Database migration (Postgres 12 to 16, MySQL to Postgres) | yes |
| Single library swap (lodash to native, moment to dayjs) | no, overkill, normal refactor is enough |
| Code style refactor (rename, extract, inline) | no, overkill |
| Adding a feature inside one module | no, base Mythos mode is enough |
| One line bug fix | no, scaffold is unnecessary |

If you fall below the threshold, prefer base Mythos mode or direct execution. The migration sub-mode is heavy. Do not activate it for nothing.

## Migration Types

| Type | Typical Duration | Risk | Tool Stack | Strategy Bias |
|---|---|---|---|---|
| Framework upgrade (React 16 to 18) | 1 to 4 weeks | Medium | Codemod (jscodeshift), ESLint plugin, type checker | Incremental |
| Language migration (JS to TS) | 2 to 12 weeks | High | Type inference (ts-migrate), codemod, gradual `any` | Incremental |
| Platform (monolith to microservice) | 6 to 26 weeks | Very high | Strangler fig proxy, API gateway, event bus | Strangler fig |
| Dependency major (Webpack 4 to 5) | 1 to 3 weeks | Medium | Migration guide, plugin compat matrix | Big bang or incremental |
| Database (Postgres 12 to 16) | 1 to 8 weeks | Very high | Dual-write, replication, schema diff tools | Strangler fig |
| API contract (REST to GraphQL) | 4 to 16 weeks | High | Schema-first, codegen, dual-endpoint | Strangler fig |

The table is a default. Calibrate it for your codebase. If test coverage is low, push the risk up one tier. If a monorepo lets you parallelize execution, the duration drops.

## Skill Set Map

The migration sub-mode runs with four supporting skills, in order:

1. **[mythos-migration-audit](./audit.md)**. Footprint extraction. Which files, which imports, which patterns are affected. Breaking change matrix. Dependency graph. Risk score.
2. **[mythos-migration-plan](./plan.md)**. Per-module priority. Phase split. Atomic commit boundaries. Rollback points. Stakeholder timeline.
3. **[mythos-migration-execute](./execute.md)**. Atomic commit discipline. Test gate at every step. Sub-agent parallel module migration. Merge conflict management.
4. **[mythos-migration-rollback](./rollback.md)**. Safe abort. Partial recovery (half new, half old). Feature flag flip. Production hotfix protocol.

Order: audit, plan, execute, then rollback when needed. The reason to skip audit, "small migration," never holds up. A four hour minimum audit prevents week-scale losses every time.

## Behavior Rules

1. **Atomic commits.** Every commit is standalone deployable. Mid-state never reaches main. If a module is half-migrated, it stays on a branch and squash-merges when complete.
2. **Test gate at every step.** No next commit until build, unit, and integration tests are green. Lint comes last. Do not treat a formatting failure like a build failure.
3. **Per-module rollout.** One module live, observe, then the next. Do not migrate four modules in parallel. The debug surface explodes and root cause analysis collapses.
4. **Feature flag plus env toggle.** A runtime kill switch for every major change. Set up the `useNewAuth = process.env.MIGRATION_AUTH === 'v2'` pattern early. Free insurance.
5. **Documentation as you go.** A decision record for each major step. "Why this codemod, why this phase order, why this rollback point." Six weeks later you will not remember your own reasoning.
6. **Stakeholder communication.** Async update at the start and end of each phase. "Phase 2 starts. Impact: X. Observation window: Y. Rollback plan: Z." Silent migration means half-finished migration.
7. **Stuck detection.** Five plus test failures in the same module, or the same error pattern back to back, means change the pattern and spawn a sub-agent with fresh context. See [mythos-failure-recovery](../../core/failure-recovery.md).

## Migration Strategies

### Big Bang
- **Approach:** Upgrade the whole codebase in one go. Work on a branch, finish everything, ship one PR.
- **Risk:** High. One mistake blocks everything.
- **Duration:** Short (weeks).
- **Use when:** Small codebase (under 10K LoC), tight timeline, small team, low regression cost.
- **Typical victim:** The senior dev who said "I can finish in two days," now six weeks deep.

### Incremental (Phased)
- **Approach:** Module by module. Each phase ships to production, the next phase starts after.
- **Risk:** Medium. If a module breaks, only that module is affected.
- **Duration:** Long (months).
- **Use when:** Mid-size codebase (10K to 200K LoC), the team has review capacity, the business needs continuous shipping.
- **Default choice:** Start here when the codebase profile is unclear.

### Strangler Fig
- **Approach:** Stand up the new system alongside the old. Gradually shift traffic. The old system fades as traffic drops to zero.
- **Risk:** Low (rollback is always possible).
- **Duration:** Very long (months to years).
- **Use when:** Critical production, large codebase (200K plus LoC), zero-downtime requirement, high business risk.
- **Classic example:** Stripe Ruby monolith to Go services took four years.

## Real-World Case Studies

- **Doctolib.** Legacy testing infrastructure to a modern test stack. Goal: hours not weeks for the test cycle. 40% faster shipping (2026 enterprise migration report). Strategy: incremental, test platform renewed module by module.
- **Aviator.** Java to TypeScript migration. A multi-agent approach delivered 71% precision (arXiv 2510.03480, "AI-Assisted Codebase Migration at Scale"). Per-file agent spawn, type inference plus manual review combo. Human hours dropped to a quarter.
- **Stripe.** Ruby monolith to Go microservices. Strangler fig pattern, four years. New services behind an API gateway, the old monolith's traffic faded gradually. Reference case for zero-downtime migration.
- **Airbnb.** Java backend to React Native plus Kotlin. Two years incremental, then a reversal back from RN to Kotlin. Read this one as a failure case too. Migrations can run forward and they can run back.

Case studies are not a fetish. Filter every one through "how would this strategy actually run inside our codebase."

## Capability Boundary

### Can do
- Apply codemods (jscodeshift, ts-migrate, 2to3 wrappers) with sub-agents in parallel
- AST manipulation (parse, transform, emit), heuristic transforms beyond regex
- Atomic commit discipline (keeping every commit consistent through the test gate)
- Test gate enforcement (build, unit, integration ordering)
- Regression detection (snapshot diff, behavior diff, performance diff)
- Decision record generation (a why-what-how file for each major step)
- Migration audit (footprint plus breaking change matrix plus dependency graph)

### Cannot do
- Real-time observation of production traffic. That needs human eyes on a dashboard.
- Business logic nuance. The special rules that should not be migrated without talking to a domain expert.
- Undocumented hidden behavior. What is not written in the codebase but is happening in production. Surprise is unavoidable.
- Stakeholder politics. "This module is owned by that team, do not touch it without talking to them" type social nuance.
- Operational risk evaluation. DR plan, on-call rotation, incident response. Human decisions.
- Cost benefit analysis. "Is this migration worth it." Mythos gathers input. The call belongs to a human.

Mythos measures, prepares, executes. The decision still belongs to a human.

## Anti-Patterns

1. **Skipping the audit.** "Small migration, let us just start." Wrong every time. A four hour minimum audit prevents week-scale losses.
2. **Mid-state main.** Merging a half-migrated module into main. The next person cannot know the state and rollback becomes impossible.
3. **Skipping tests.** "The codemod ran, tests will sort themselves out." 71% precision means 29% slip. Tests are required at every step.
4. **Single rollback path.** Trusting only `git revert`. With a live bug in production, git revert plus rebuild plus redeploy takes 30 minutes. A feature flag toggle takes 30 seconds.
5. **Big bang on a monolith.** A 200K LoC monolith migrated on one branch over three months is an invitation to merge conflict hell.
6. **Scope creep.** "This is bad too, let me fix it while I am here." Refactor leaks into the migration and the atomic commit principle dies. Refactor goes in a separate PR.
7. **Documentation post-facto.** "I will write the docs after we finish." It does not get written. Write while you are deciding. You will not remember in six weeks.
8. **Stakeholder isolation.** Running the migration disconnected from the team. Someone in phase 3 saying "but I use this module like X" sets the calendar back a week.

## Quick Checklist

Before migration starts:

- [ ] Audit complete: footprint, breaking change matrix, dependency graph extracted ([mythos-migration-audit](./audit.md))
- [ ] Strategy chosen: big bang, incremental, or strangler fig, with a written rationale
- [ ] Per-module priority set: pilot first or high-risk first
- [ ] Atomic commit boundaries defined: each phase from where to where
- [ ] Rollback path is three layers deep: git, feature flag, env toggle
- [ ] Test gate is up: no progress without build plus unit plus integration green
- [ ] Stakeholder timeline communicated: which phase when, what the impact is
- [ ] Decision record template ready: filled in at each major step
- [ ] Stuck detection threshold set: how many failures trigger a pattern change
- [ ] Sub-agent parallelization strategy: which modules in parallel, which in series

Before every commit during migration:

- [ ] Is this commit standalone deployable?
- [ ] Is the test gate green?
- [ ] Is the decision record updated?
- [ ] Can I roll back from this point?

After migration:

- [ ] Are all modules on the new system?
- [ ] Are the old code paths removed?
- [ ] Are feature flags retired (when no longer needed)?
- [ ] Is the decision record archived?
- [ ] Is the postmortem written: what worked, what did not, what changes next time?

You cannot call the migration "done" until the list is complete. A half-finished migration comes back as technical debt with interest.
