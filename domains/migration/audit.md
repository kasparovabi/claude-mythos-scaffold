---
type: skill
tags: [system/skill, mythos, migration, audit, footprint]
related:
  - ./mode.md
  - ./plan.md
  - ../../core/tool-stack.md
  - ../../core/context-priming.md
---

# Mythos Migration Audit

> Before migration starts, the footprint must be exact and the breaking change matrix must be complete.

## Philosophy

- **Audit first, plan second.** Building a plan without audit data is guessing. Codebase scale, breaking change density, hidden coupling: without these three, any plan is paper. No measurement, no risk awareness; the risk is still there, just invisible. See [mode](./mode.md): the migration sub-mode does not start without an audit.
- **Quantitative over qualitative.** "Big codebase" is not information. 47K LOC, 312 files, 89 dependencies is information. A numeric metric is comparable, feeds plan effort estimates, and lets you measure delta against a post-migration baseline. The adjective "complex" is banned: write cyclomatic complexity, in-degree, coupling score as numbers.
- **Hidden coupling is critical.** Static analysis cannot catch singleton state, dynamic require, runtime reflection, DI containers, or build-time codegen. AST scans see the public API surface but not the inner mechanism. Most migration blowups come from hidden coupling: "everything compiled, tests passed, prod died."
- **Environment baseline.** "Did the migration improve or regress things?" can only be answered if a pre-snapshot exists. Build time, test pass rate, lint warning count, bundle size, runtime p50/p95: freeze them before migration starts, write them to JSON, use them as the reference point through plan, execute, and rollback.

## Phase 1: Codebase Footprint

### 1.1 Quantitative metrics (programmatic)

The numeric backbone of the audit. All metrics are saved under `audit/footprint.json`.

- **File count + LOC.** `cloc --json --out=audit/cloc.json src/` or `tokei --output=json src/`. Output: file count, code lines, comment lines, blank lines per language. Baseline for migration effort estimation.
- **Dependency tree depth + node count.**
  - Node.js: `npm ls --all --json > audit/deps-tree.json`
  - Python: `pipdeptree --json > audit/deps-tree.json`
  - Go: `go mod graph > audit/deps-graph.txt`
  - Dead deps: `depcheck` (Node), `pip-autoremove` (Python). Dead dependencies can be excluded from migration scope.
- **Cyclomatic complexity per file.**
  - JS/TS: `eslint --rule complexity:error` or `escomplex`
  - Python: `radon cc -j src/ > audit/complexity.json`
  - Files with complexity > 15 go into the manual fix queue.
- **Test coverage baseline.**
  - Jest: `jest --coverage --coverageReporters=json-summary`
  - Pytest: `pytest --cov=src --cov-report=json:audit/coverage.json`
  - Go: `go test -coverprofile=audit/cover.out ./...`
  - Low-coverage modules are blind shots during migration.
- **Build time.** `time npm run build` or `time make build`. Run 5 times sequentially, take mean and variance. A single snapshot is not enough (cache and filesystem state move it).
- **Bundle size.**
  - Webpack: `webpack-bundle-analyzer --mode=json`
  - Vite/Rollup: `source-map-explorer dist/**/*.js --json`
  - Python wheel: `wheel size`. Bundle size should shrink, or at least not grow, after migration.
- **Runtime metrics (if available).** Pull from production observability: p50/p95 latency, error rate, memory baseline. If absent, capture a load-test snapshot (`k6`, `wrk`, `locust`).

### 1.2 Framework / library version inventory

- **Direct deps**: `package.json`, `requirements.txt`, `go.mod`, `Gemfile`, `Cargo.toml`. Explicitly declared dependencies.
- **Transitive deps**:
  - `npm ls --all > audit/deps-all.txt`
  - `pip list --format=freeze > audit/deps-all.txt`
  - `go list -m all > audit/deps-all.txt`
  - Transitive count is typically 10 to 50x the direct count; at least a few of the migration blowups will come from this set.
- **Pin gaps**: `>=`, `^`, `~` prefix means drift risk. Tighten pins with `npm-check`, `pip-tools compile`. The audit report lists every unpinned dependency explicitly.
- **Outdated check**:
  - `npm outdated --json > audit/outdated.json`
  - `pip list --outdated --format=json > audit/outdated.json`
  - `go list -u -m all > audit/outdated.txt`
  - Stale versions raise the risk of incompatibility with the target framework.

### 1.3 Test inventory

- **Test count + type.** Split unit / integration / e2e. Derive from folder layout and naming patterns (`*.test.ts`, `*_test.py`, `e2e/`). Table:
  ```
  Type        | Count | LOC   | Coverage
  unit        | 412   | 8.2K  | 78%
  integration | 67    | 3.1K  | 45%
  e2e         | 18    | 1.4K  | n/a
  ```
- **Per-module coverage map.** Parse `coverage.json` and produce a per-module table. Modules with coverage below 30% do not enter the first migration wave; add tests first.
- **Flaky test detection.** If CI history exists, pull retry rates from the last 30 days. Flaky tests mask migration regressions and produce false positives and negatives.
- **Mock ratio.** A mock-heavy suite goes green during migration but blows up at runtime. Heuristic: `grep -r "jest.mock\|MagicMock\|sinon.stub" tests/ | wc -l` divided by total test count. Ratio above 0.6 means high "mock illusion" risk.

## Phase 2: Breaking Change Matrix

The most critical audit output. The plan phase is built on top of this matrix.

### 2.1 Target framework changelog parse

- **Official migration guide.** React 18 to 19, Vue 3 to 3.4, Python 2 to 3, Django 4 to 5, Node 18 to 22: every framework has official docs. Read manually, extract the breaking change list to CSV.
- **Breaking change types**:
  - **Removed APIs**: hard fail.
  - **Signature changes**: argument or return type changed.
  - **Behavior changes**: same API, different behavior (the sneakiest).
  - **Default value changes**: opt-in / opt-out flipped.
  - **Deprecation**: warning now, removal later.
- **Codemod availability**:
  - `jscodeshift` ecosystem (React, Next.js, Vue codemods)
  - `2to3` (Python 2 to 3)
  - `ts-migrate` (Airbnb, JS to TS)
  - `gofix` / `gopls rename`
  - With a codemod, manual fix count drops; without one, effort multiplier is 5 to 10x.

### 2.2 Codebase x changelog cross-reference

For every breaking change, scan the codebase for usage:

- **Grep + AST hybrid**:
  - Fast scan: `rg "ReactDOM.render" --json > audit/usages-render.json`
  - Precise: `ts-morph` to find imports and call sites (filters false positives).
- **Affected files list**: full file path list per change_id.
- **Manual fix vs codemod-fixable split**:
  - Codemod-fixable: batch transform script.
  - Manual: review and rewrite queue.
- **High-impact threshold**: usage count above 100 means "high severity"; if no codemod exists, it gets its own phase in the migration plan.

### 2.3 Output: `audit/breaking-change-matrix.csv`

```csv
change_id,description,codemod_available,usage_count,affected_files,severity,fix_strategy
RC-001,ReactDOM.render removed,yes (jscodeshift),214,src/index.tsx;src/legacy/*,high,codemod batch
RC-002,Suspense behavior change,no,89,src/data/*,med,manual review
RC-003,defaultProps deprecated for FC,yes (custom regex),437,src/components/**,low,codemod batch
PY-001,async generator throw signature,no,12,src/streams/*,low,manual rewrite
```

The plan phase reads this CSV and derives phases and effort estimates from these rows.

## Phase 3: Hidden Coupling Detection

Connections that static analysis cannot see, the main source of migration blowups.

- **Singleton state.** Module-level globals (`let cache = {}`), mutable objects exported via `module.exports`, Python `_instance = None` patterns. State is shared if the module is imported twice; if migration changes the bundler, that import path can break.
- **Dynamic require/import.** `require(variableName)`, `import(dynamicPath)`, Python `importlib.import_module(name)`, `__import__`. Static analysis cannot follow these; what loads at runtime is unknown. Audit list: every dynamic import call site.
- **Reflection / metaprogramming.**
  - JS: `Object.defineProperty`, `Proxy`, `Reflect.*`
  - Python: `__getattr__`, `__getattribute__`, decorator factories, metaclasses
  - TS: decorators (legacy vs stage-3 differ)
  - These break silently if the migration target changes decorator semantics.
- **DI container.** Angular `@Injectable`, NestJS `@Module`, Python `dependency-injector`, Go `wire`. Every DI graph node is a potential migration risk node. Extract the DI graph (`madge`, `dependency-cruiser`, custom AST script).
- **Macros / build-time codegen.** Babel plugins, SWC plugins, Vite transforms, Sass mixins, Python decorators with `inspect.getsource`, Go `//go:generate`. Code produced in the build pipeline may not be compatible with the migration target.

### Tool stack (hidden coupling)

| Need | Tool |
|---------|------|
| TypeScript AST | `ts-morph` (programmatic refactor + analysis) |
| JS codemod | `jscodeshift`, `babel-plugin-transform-imports` |
| Python AST | `ast` (stdlib), `LibCST` (style-preserving) |
| Multi-language AST | `tree-sitter` (Rust core, multi-language bindings) |
| Dep graph | `dependency-cruiser` (JS), `madge` (JS), `pydeps` (Python), `gomod-graph` |
| Reflection scan | Custom regex + AST hybrid |

See [tool-stack](../../core/tool-stack.md) for the tool selection cascade.

## Phase 4: Module-Level Risk Scoring

A risk score between 0 and 1 per module. Above 0.7 is high-risk; these modules are scheduled either as the first wave (controlled) or the last wave (most stable) in the migration plan.

```
risk_score = (
    0.3 * size_score              # LOC normalized, log scale
  + 0.3 * test_coverage_inverse   # 1 - (coverage / 100)
  + 0.2 * external_api_exposure   # public-facing 1.0, internal 0.0
  + 0.2 * coupling_score          # (in-degree + out-degree) normalized
)
```

- **size_score**: `min(LOC / 5000, 1.0)`. Above 5K LOC is full risk.
- **test_coverage_inverse**: 0% coverage gives 1.0; 90% coverage gives 0.1.
- **external_api_exposure**: route handlers, public package exports, CLI entry points are 1.0; internal helpers are 0.0.
- **coupling_score**: in-degree plus out-degree from the dep graph, normalized by 5% of total module count.

Output: `audit/risk-scores.csv`, score and breakdown per module. The plan uses this score to sequence the migration.

## Phase 5: Environment Baseline

A frozen pre-migration snapshot. All three phases (plan, execute, rollback) read this file as reference.

- **Build time**: 5-run mean and standard deviation.
- **Test pass rate**: passed / total plus flake count (last 30 days CI).
- **Lint warning count**: `eslint --max-warnings=0` output, or `ruff check --statistics`.
- **Type check error count**: `tsc --noEmit` or `mypy --strict` output.
- **Bundle size**: production build, hashes included, raw and gzipped.
- **Runtime perf**: p50 / p95 / p99 for critical endpoints (at least 3).
- **Memory baseline**: idle and peak (from observability if available, otherwise a `process.memoryUsage()` snapshot).

Output: `audit/baseline.json`. The post-execute phase diffs against this file; regression detection comes from the delta.

```json
{
  "captured_at": "2026-04-27T10:00:00Z",
  "build": { "mean_seconds": 47.2, "std": 1.8 },
  "tests": { "total": 497, "passed": 491, "flaky": 4, "duration_seconds": 124 },
  "lint": { "warnings": 23, "errors": 0 },
  "typecheck": { "errors": 0 },
  "bundle": { "raw_bytes": 1842331, "gzip_bytes": 612447 },
  "runtime": {
    "endpoints": [
      { "path": "/api/users", "p50_ms": 42, "p95_ms": 118, "p99_ms": 240 }
    ]
  }
}
```

## Audit Report Format

`audit/report.md`: a one-page summary plus appendices, handed to the plan phase.

```markdown
# Migration Audit Report: <project> @ <commit-sha>

## Executive Summary
Codebase: 47K LOC, 312 files, 89 deps (24 transitive stale).
Target: React 18 to 19. Breaking changes: 14 (8 codemod-fixable, 6 manual).
High-risk modules: 7. Estimated effort: 18 to 24 person-days. Strategy: incremental (3 waves).

## Footprint Metrics
[table: LOC, file count, complexity, coverage, build time, bundle size]

## Top 10 High-Risk Modules
[table: module, risk score, breakdown, primary risk factor]

## Breaking Change Matrix (summary)
[14 rows breakdown. Full CSV: audit/breaking-change-matrix.csv]

## Hidden Coupling Findings
[singleton, dynamic require, reflection, DI container, codegen: counts and examples]

## Environment Baseline
[baseline.json summary]

## Recommendation
Strategy: incremental (not strangler, public API surface is narrow).
Sequencing: low-risk modules first (warm-up), high-coupling middle wave, public API last.
Rollback: feature flag plus parallel deploy. Rollback gate: regression > 10% p95.
```

The strategy choice must come with reasoning:
- **Big Bang**: codebase under 10K LOC, breaking changes under 5, shallow dep graph.
- **Incremental**: most cases (waves of modules).
- **Strangler**: wide public API, old and new must run in parallel (e.g. monolith to microservice).

## Tool Stack (Audit-Specific)

| Tier | Purpose | Tool |
|--------|------|------|
| Built-in | File discovery | Glob, Grep, Read |
| LOC | Code metrics | `cloc`, `tokei` |
| Dep | Dependency tree | `npm ls`, `pipdeptree`, `go mod graph`, `depcheck` |
| Coverage | Test coverage | `jest --coverage`, `pytest --cov`, `go test -cover` |
| Complexity | Cyclomatic | `radon`, `eslint-plugin-complexity`, `lizard` |
| AST | Syntax scan | `ts-morph`, `jscodeshift`, Python `ast` / `LibCST`, `tree-sitter` |
| Graph | Module graph | `dependency-cruiser`, `madge`, `pydeps` |
| Bundle | Size analysis | `webpack-bundle-analyzer`, `source-map-explorer`, `vite-bundle-visualizer` |
| Outdated | Version drift | `npm outdated`, `pip list --outdated`, `go list -u -m all` |

See [tool-stack](../../core/tool-stack.md) for built-in preference and the escalation cascade.

## Anti-Patterns

- **Skipping audit.** Jumping straight to plan means a guess-based plan and a mid-migration surprise. The feeling of "I know this codebase" does not replace audit; if there are no numbers, there is no knowledge.
- **Quantitative only.** You measured LOC, coverage, and complexity but missed hidden coupling. Singleton state, dynamic require, reflection: these are the top blowup categories during migration and they do not show up in quantitative metrics.
- **Single-snapshot baseline.** You measured build time once at 38 seconds, then again at 52 seconds. Without variance, "is this regression or baseline noise?" cannot be answered. At least 5 runs and standard deviation are required.
- **Skipping the outdated check.** `package.json` was last touched 2 years ago, the transitive chain is 18 months behind. The migration target framework brings new dep requirements; without an outdated check, this hits as a surprise.
- **Planning manual fixes without checking codemod availability.** 437 occurrences planned as manual; later a `jscodeshift` codemod is found and effort drops 5x. The plan phase searches for codemods first, then queues the rest as manual.
- **Skipping test inventory.** Migration starts without a coverage map, low-coverage modules pass green, regression hits in prod. Low-coverage module = blind shot for migration.
- **Mock-heavy test illusion.** A suite with mock ratio above 0.6 passes during migration and breaks at runtime. The audit report writes the mock ratio explicitly and flags the integration test gap.

## Quick Checklist

**Before audit starts:**
- [ ] Target framework decided (target version pinned)?
- [ ] `audit/` folder created (and gitignored)?
- [ ] Quantitative tools installed (`cloc`, `radon`, `depcheck`, etc.)?
- [ ] CI history accessible (for flake detection)?
- [ ] Production observability metrics reachable (otherwise plan a load test)?

**At audit end:**
- [ ] `audit/footprint.json` filled (all quantitative metrics)?
- [ ] `audit/breaking-change-matrix.csv` filled (severity and fix_strategy included)?
- [ ] `audit/risk-scores.csv` produced (score 0 to 1 per module)?
- [ ] `audit/baseline.json` frozen (post-migration reference)?
- [ ] `audit/report.md` includes executive summary and recommendation?

See [context-priming](../../core/context-priming.md): audit outputs are handed to the plan phase as context. [plan](./plan.md) reads these five files as input.
