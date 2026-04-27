---
type: skill
tags:
  - system/skill
  - mythos
  - verification
  - quality-gate
related:
  - ./mode.md
  - ./agent-loop.md
  - ./failure-recovery.md
---

# Mythos Verification

> Proof requirement before any work counts as "done".
> "I marked it" is not "I did it".

---

## Philosophy

1. **"Done" requires proof.** In TodoWrite, `completed` means verify passed. Otherwise it stays `in_progress`.
2. **Headless beats visual.** Build/test output before pixel-perfect inspection. Fast, deterministic, repeatable.
3. **Output reading discipline.** Exit code 0 is not enough. Read stderr, warnings, "PASS"/"FAIL" strings.
4. **Failures are never hidden.** If verify failed, say it explicitly and trigger [failure-recovery](./failure-recovery.md).

---

## Verification Taxonomy

Minimum verify by work type:

| Work type | Verify method | Tool |
|---|---|---|
| **Code writing** | Compile/build passes | `npm run build`, `tsc --noEmit`, `cargo check`, `go build` |
| **Logic/feature** | Tests pass | `pytest`, `npm test`, `go test`, `cargo test` |
| **Style** | Lint passes | `eslint`, `ruff`, `golangci-lint`, `clippy` |
| **Type safety** | Type check passes | `tsc --noEmit`, `mypy`, `pyright` |
| **Migration/SQL** | Forward migrate + rollback both pass | `alembic upgrade/downgrade`, `prisma migrate` |
| **Deploy** | Smoke endpoint hit | `curl /health`, status check |
| **UI change** | Renders in browser | Playwright/Chrome MCP screenshot + click |
| **File change** | Read-back diff | `git diff`, or Read |
| **Doc/markdown** | Render produces no errors | Markdown preview, or pandoc |
| **Config change** | Loader is invoked | App restart + smoke |

**Multiple categories:** If code and UI both changed, verify both. One alone is not enough.

---

## Headless Verification Priority

Even for UI changes, run headless first:

```
1. tsc / build       → does the code compile
2. unit test         → is the logic correct
3. integration test  → do components work together (if any)
4. lint              → is the style clean
5. (then) browser    → visual smoke check
```

**Why:** Headless is deterministic and fast. Browser tests take 30 seconds, build takes 5. If the build is broken, the browser shows a blank screen anyway.

**Exception:** Pure CSS/copy change goes straight to browser (no build needed). Logic-free work.

---

## Output Reading Discipline

Evaluate `Bash` output by reading the content, not just the exit code:

### Exit code 0, but actually successful?
```
WRONG: "Build succeeded" + exit 0, but log says "warning: 47 deprecations"
   Tell the user: "Build passed but there are 47 deprecation warnings"

WRONG: "Tests passed" + pytest says "1 passed, 3 skipped"
   Why skipped? Expected, or unintended?

WRONG: "npm install" + exit 0, but "X vulnerabilities (Y high)"
   Security report. Do not ignore.
```

### Exit code != 0, but is it really a bug?
```
WRONG: exit 1 + "command not found: prettier"
   Not a bug. Tool is missing. Install it.

WRONG: exit 2 + "no tests collected"
   Means there are no tests. Not success. Flag it.
```

**Pattern matching:**
- "PASS" / "OK" / passed marker / "passed" indicates success
- "FAIL" / "ERROR" / failed marker / "failed" indicates failure
- "WARNING" / "warn" needs to be noted before saying "done"
- "DEPRECATED" is a long-term issue, raise it as a warning

---

## End-to-End Smoke Test

For UI or user-facing changes, run the actual user scenario step by step.

### Web app smoke (Playwright/Chrome MCP)
```
1. browser_navigate <url>
2. browser_snapshot               → see the DOM (does the login form render)
3. browser_fill_form              → email/password
4. browser_click submit
5. browser_wait_for selector ".dashboard"
6. browser_console_messages       → any errors
7. browser_take_screenshot        → evidence
```

### CLI smoke
```
1. Install the tool (if needed)
2. --help / --version             → does it run
3. Minimal happy path             → expected output
4. Edge case                      → graceful failure
```

### API smoke
```
1. curl /health                              → 200 OK
2. curl POST <main endpoint> with valid body → 2xx
3. curl POST with invalid payload            → 4xx (graceful)
4. curl GET <protected> without auth         → 401
```

---

## When Verify Can Be Skipped

Verify is **not** mandatory in these cases:

| Situation | Why |
|---|---|
| Pure documentation change (.md) | Nothing to run. Markdown preview is optional. |
| Plan-only file | A plan is thought, not code. |
| User explicitly said "skip the test, move fast" | User decision (but say "I did not test this"). |
| Read-only work (exploration/analysis only) | Nothing changed, nothing to verify. |
| Single-line comment add | Trivial. Build still compiles (assuming the comment syntax is right). |

**Even then, say it:** "I skipped verify because X" so the user knows.

---

## Failure to Feedback

If verify failed:

1. **Read the output.** What is the real error, not just the exit code.
2. **Classify it.** Code error, tool error, logic error, environment error.
3. **Logging.** No `failed` mark in TodoWrite. It stays `in_progress`.
4. **Move to recovery.** See [failure-recovery](./failure-recovery.md).
5. **Do not hide it.** Never tell the user "build passed". Say "build failed, X is the error, I am retrying."

**"Tell the user done first, then fix it later" is an anti-pattern.** Do not do it.

---

## Definition of "Done"

To mark `completed` in TodoWrite:

```
[ ] Verify passed (the appropriate one from the taxonomy above)
[ ] Output was read; warnings/skipped were noted
[ ] User-visible output exists (file, deploy, response)
[ ] File state is consistent (no half-applied Edit, no broken imports)
[ ] Side effects are under control (tested, or explicitly noted as out of scope)
```

All five hold then `completed`. Otherwise stay in `in_progress` and recovery kicks in.

---

## Verify Cost vs Value

Not every task needs the same verify. Scale with the work:

| Work scale | Min verify |
|---|---|
| One-line fix | Compile + relevant test |
| Single-file change | Build + lint + relevant unit test |
| Multi-file feature | Build + full test suite + smoke |
| Cross-cutting refactor | Build + full test + integration + e2e smoke |
| Migration / DB schema | Forward + rollback + data integrity test |
| Deploy | Health endpoint + smoke + log inspection |

**Verify scales with scope.** Running the whole test suite for a one-liner is waste; running only compile for a big change is not enough.

---

## Anti-Pattern: Verify Skips

- **Trusting exit code 0 as "build passed"** without reading the log.
- **Asking "do the tests pass?" instead of running them yourself.**
- **Counting manual review as automated test.** "I read the code and it looks right" is not verify.
- **Approving a UI change without Playwright.** If the render is broken, you will not see it.
- **Testing migrations forward only.** If rollback is broken, you cannot recover in production.
- **Letting a verify failure go silent.** A user thinks the work is done when it is actually broken: trust loss.

---

## Quick Checklist

Before marking `completed`:
1. What is the work type? (code / UI / migration / doc...)
2. Which verify method fits?
3. Did I read the output? (warnings, skipped, deprecated included)
4. Does the end-to-end scenario work?
5. Are there side effects, and were they checked?

All five pass then completed.
Any one fails then in_progress + [failure-recovery](./failure-recovery.md).
