---
type: skill
tags:
  - system/skill
  - mythos
  - migration
  - plan
  - phasing
related:
  - [mode](./mode.md)
  - [audit](./audit.md)
  - [execute](./execute.md)
  - [decomposition](../../core/decomposition.md)
  - [agent-loop](../../core/agent-loop.md)
---

# Mythos Migration Plan

> Turn the audit's quantitative output into a phased plan with acceptance criteria and a rollback path.

## Philosophy

- **The plan is a derivative of the audit.** No audit means the plan is a guess; no guess survives the first incident, so the migration becomes cowboy work. Start with the [audit](./audit.md) output: footprint, breaking change matrix, risk score. The plan ingests those three inputs and slices them into phases. A plan written without audit data is a wishlist dressed up with optimistic numbers.
- **Per-phase deliverable plus acceptance criteria.** "Phase 2 is roughly done" is not acceptable. Every phase declares a measurable output: "X module migrated, Y tests green, Z performance metric within +/-5%". Subjective phrases ("seems to work", "mostly there") stay out of the plan; "done" must be binary.
- **A rollback path lives in every phase.** One-way migrations are dangerous. Each phase defines a way back: feature flag off, env var revert, git tag checkout, traffic split rollback. Production incidents do not wait for ad-hoc fixes; the rollback hook has to be ready in advance.
- **Time estimate is calibrated.** A raw guess ("about three weeks") has to be validated against the audit baseline. Formula: base_hours_per_kloc * kloc * complexity_multiplier * (2 - test_coverage). Add a 50% variance buffer and 30% overhead. Calibrated estimates land within 20%; raw guesses miss by 200%.

## Strategy Selection (from the audit)

The audit output carries the signals you need to choose a strategy. Decision matrix:

| Audit signal | Strategy | Rationale |
|---|---|---|
| Codebase < 50K LOC plus tight timeline | **Big Bang** | On a small codebase the parallel maintenance overhead exceeds the incremental gain |
| 50K to 500K LOC plus agile team | **Incremental (module by module)** | Module-scoped phases, parallel sub-agents, learning curve compounds across phases |
| > 500K LOC plus critical production | **Strangler Fig** | Side-by-side systems, gradual traffic cutover, zero downtime |
| High coupling plus low test coverage | **Strangler (dual run, gradual cutover)** | When coupling cannot be tested, the old system stays alongside as a reference |

**Audit risk score distribution is the deciding factor.** If 30% or more modules are high-risk (> 0.7), Big Bang is forbidden; incremental or strangler is mandatory. When high-risk module density is high, work piles up in the final phase, so split that phase into 2 or 3.

## Phase Decomposition

Phase skeleton for the incremental strategy. Every phase carries deliverable, acceptance, and rollback.

### Phase 0: Setup (1 to 2 days)

- **Branch strategy:** long-running migration branch (rebase-heavy) versus main plus feature flags. From the audit, team size > 3 picks feature flags; < 3 picks the long-running branch.
- **CI/CD pipeline extension:** parallel test path. Old and new framework tests run in the same pipeline as parallel jobs. The migration branch carries a `test:migration` task.
- **Codemod scripts ready:** breaking change matrix from the audit becomes ast-grep, jscodeshift, or custom Python AST scripts. Codemods automate 60% to 80%; the rest is manual fix.
- **Rollback hooks:** env var (`MIGRATION_PHASE=2`), feature flag (`new_framework_enabled`), git tag at every phase end (`migration-phase-2-complete`).

**Acceptance:** branch, pipeline, codemod, and rollback hook in place; tests runnable.

### Phase 1: Pilot Module (3 to 7 days, low-risk module)

- **Module choice:** a module with `risk_score < 0.3` and `test_coverage > 0.7`. Examples: utility functions, helpers, leaf-level components. The pilot module is a learning ground; picking high-risk here means damage before the migration habits are formed.
- **Codemod, manual fix, test, review, merge.**
- **Run behind a feature flag in production:** new code is written but traffic still hits the old code. Open `new_framework_enabled=true` to 1% of traffic and observe.
- **Acceptance:** pilot module migrated, CI green, flag on/off works, 24 hours stable at 1% production traffic.

### Phase 2 to N: Module Migration (1 to 3 days per module)

- **Per-module risk-ascending order:** low risk to high risk. Sort by audit risk score; start at the bottom.
- **Sub-agents in parallel:** see [decomposition](../../core/decomposition.md). Independent modules go to parallel agents (typically 4 to 8). Dependent modules stay sequential.
- **Per-module workflow:**
  1. Apply codemod
  2. Pass tests (red to green)
  3. Manual fix (areas the codemod missed)
  4. Review (sub-agent and main agent cross-check)
  5. Merge to migration branch
- **Acceptance per module:** tests green, baseline metrics within +/-5% (latency, memory, throughput), no new lint warnings, manual smoke test passes.

### Phase Final: High-Risk Modules plus Global Cleanup (3 to 7 days)

- **High-risk module migration:** singleton state, DI container, global config, framework-specific magic (decorators, metaclasses).
- **Global cleanup:** all old framework usage scrubbed from the code. `grep -r "OldFramework" src/` must come back empty.
- **Performance regression check:** audit baseline (latency, memory, build time, bundle size) versus current. If regression > 10%, the phase reopens.
- **Acceptance:** zero old framework usage, baseline metrics preserved, full test suite green, manual QA pass.

### Phase N+1: Stabilization (3 to 14 days)

- **Production observation:** real traffic, real users. Edge case bugs surface in this phase.
- **Edge case bug fix:** migration-rooted incidents take priority. Observability dashboard plus alerting rules in place.
- **Documentation update:** README, ADR, onboarding guide, internal wiki.
- **Acceptance:** 2 weeks production stable, no migration-rooted incidents, documentation up to date, team training complete.

## Strangler Fig Strategy (large codebase)

A dedicated strategy for large codebases plus critical production. Big Bang is unacceptable; incremental cannot finish in a single phase.

- **New system runs alongside:** separate service (microservice) or separate module (monorepo). The old system stays untouched while the new one is built next to it.
- **API gateway or proxy splits traffic:** all traffic to the old system, then 50/50 split, then all traffic to the new system. Per-endpoint granularity (`/api/users` new, `/api/orders` old).
- **Per-endpoint cutover, gradual:** cut endpoint by endpoint. Each endpoint goes pilot, 1%, 10%, 50%, 100% traffic.
- **Old system traffic hits zero, then code is removed:** once every endpoint has cut over, the old system is decommissioned. That moment is the migration completion.
- **Duration:** 6 months to 2 years typical. On large projects, 3+ years is possible.
- **Risk:** low (rollback is easy at every phase, dual run is a safety net).
- **Cost:** high (dual maintenance, doubled infrastructure, team capacity split).

## Sub-Agent Decomposition

Module-scoped parallel agent dispatch. The [decomposition](../../core/decomposition.md) pattern:

- **Independent modules equal parallel sub-agents.** 4 to 8 agents can migrate different modules at once.
- **Agent brief template:** module path, breaking change list, codemod script, test command, acceptance criteria. A thin brief leads the agent to the wrong scope.
- **Hub-and-spoke pattern:** the main agent coordinates (plan, review, merge); each sub-agent owns one module. The sub-agent runs its own audit, codemod, test, review loop and returns the result to the main agent.
- **Conflict handling:** if a shared utility module is being changed by two agents at the same time, serialize them. The dependency graph from the audit decides parallel versus sequential automatically.
- **Agent loop:** see [agent-loop](../../core/agent-loop.md). Every sub-agent runs verify, respond, action, observe. After three failed turns, the issue escalates to the main agent.

## Time Estimation Formula

Calibrated estimates land 3x to 5x closer than raw guesses.

```
module_time_hours = base_hours_per_kloc * kloc * complexity_multiplier * (2 - test_coverage)

base_hours_per_kloc:
  - codemod-friendly migration (rename, signature change): 2 to 4
  - manual-heavy migration (paradigm shift): 8 to 12
  - language migration (JS to TS, Py2 to Py3): 6 to 10

complexity_multiplier:
  - simple module (CRUD, helpers): 1.0
  - DI / metaprogramming / decorators: 1.5
  - performance-critical (hot path, real-time): 2.0
  - public API (backward compat required): 1.8
```

**Total formula:**

```
total_hours = sum(module_time) * 1.3 (overhead) * 1.5 (variance buffer)
total_days = total_hours / 6 (productive hours per day)
total_calendar_days = total_days * 1.4 (meetings, blockers, context switch)
```

**Example:** 30 modules at an average of 12 hours = 360 hours * 1.3 * 1.5 = 702 hours = 117 days = 164 calendar days, roughly 5.5 months. A raw "3 months" guess misses by 80%.

## Plan Output Format

The plan output lives at `plan/PLAN.md`, templated:

```markdown
# Migration Plan: <Project>

## Strategy
- Choice: Incremental
- Rationale: 200K LOC, 5-dev team, low test coverage. Strangler is risky, Big Bang is forbidden.

## Phases

### Phase 0: Setup (2 days)
- Modules: -
- Acceptance: branch, CI, codemod ready
- Rollback trigger: -

### Phase 1: Pilot (5 days)
- Modules: src/utils/format.ts, src/utils/date.ts
- Acceptance: green CI, flag-on prod 24h stable
- Rollback trigger: error rate > 2%

### Phase 2 to N: Module Migration (60 days)
- Modules: src/services/* (15 modules), src/components/* (12 modules)
- Acceptance: per-module tests green, baseline +/-5%
- Rollback trigger: performance regression > 10%

### Phase Final: High-Risk plus Cleanup (7 days)
- Modules: src/core/di-container.ts, src/core/event-bus.ts, global config
- Acceptance: zero old framework usage, baseline preserved
- Rollback trigger: critical incident

### Phase Stabilization (14 days)
- Modules: production observation
- Acceptance: 2 weeks stable, no migration incident

## Time
- Total: 88 days work plus buffer = 123 calendar days, roughly 4 months

## Risk Register (top 5)
1. DI container migration. Mitigation: Phase Final, dedicated review
2. Performance regression in hot path. Mitigation: per-module benchmark
3. Team capacity drop (vacation). Mitigation: 50% buffer
4. Codemod coverage falls short. Mitigation: Phase 1 pilot learning
5. Production incident. Mitigation: feature flag, rollback hook

## Stakeholder Communication
- Weekly status: phase progress, blockers, ETA
- Phase completion: announcement plus demo
- Incident: immediate Slack plus post-mortem within 24h
```

## Risk Mitigation per Phase

| Risk | Symptom | Mitigation |
|---|---|---|
| Test fail spike | 20%+ tests red mid-phase | Pause and analyze, review the codemod, narrow the scope |
| Performance regression | Latency or memory > baseline + 10% | Bisect commits, identify the offending change, redo the codemod |
| Production incident | Error rate spike, user reports | Feature flag off, immediate rollback, post-mortem |
| Scope creep | Phase 5 work bleeds into Phase 2 | Freeze scope, push back to a later phase, refuse "just a tiny addition" |
| Resource conflict | Sub-agents collide on the same file | Serialize sequentially, lower parallelism, refresh the dependency graph |

## Anti-Patterns

- **Starting without a plan (cowboy migration).** Skipping the plan because the audit is done means no phases, no acceptance, no rollback. Three weeks in, "where are we?" has no answer.
- **No per-phase acceptance criteria.** "This phase is roughly done" means there is no definition of done. Replace subjective wording with binary metrics.
- **No rollback path considered.** One-way migrations are dangerous. During a production incident, no way back means hours of downtime.
- **Time estimate without the audit.** A "three weeks" guess without the calibrated formula is wishful thinking. Audit baseline, complexity multiplier, and variance buffer are mandatory.
- **No stakeholder communication.** No weekly status, no phase completion announcement. A surprise prod incident burns trust and turns the migration into a political crisis.
- **Picking Big Bang on a large codebase.** A Big Bang attempt at 200K+ LOC runs three months, gets aborted, and burns six months. Stick to the strategy matrix.
- **Picking a high-risk pilot module.** Phase 1 is a learning ground. Starting with the DI container fractures team confidence before the codemod habits form. Risk score < 0.3 is mandatory.

## Quick Checklist

- [ ] Audit output present (footprint, breaking matrix, risk score)?
- [ ] Strategy choice matches the matrix (LOC, team, risk distribution)?
- [ ] Phase 0 setup defined (branch, CI, codemod, rollback hooks)?
- [ ] Pilot module risk_score < 0.3, test_coverage > 0.7?
- [ ] Per-phase acceptance criteria binary (not subjective)?
- [ ] Per-phase rollback trigger defined?
- [ ] Time estimate produced by the calibrated formula (overhead plus buffer)?
- [ ] Sub-agent decomposition fits the dependency graph?
- [ ] Risk register holds the top 5 risks plus mitigations?
- [ ] Stakeholder communication plan exists (weekly, phase, incident)?
- [ ] Strangler Fig considered (> 500K LOC plus critical production)?
- [ ] Phase Final separates high-risk modules from global cleanup?
- [ ] Stabilization phase at least 2 weeks?
- [ ] Plan output matches the `plan/PLAN.md` template?
- [ ] Anti-pattern list reviewed?
