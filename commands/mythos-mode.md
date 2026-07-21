---
description: Activate Mythos scaffold with a persistent mission file for a complex task.
argument-hint: <task> | resume | status | close
---

# /mythos-mode

Runs a task under the Mythos scaffold: kernel discipline, a persistent mission file, explicit
sub-agent routing, verification before "done". Skill files live at
`~/.claude/skills/mythos-scaffold/` (absolute paths below; on other platforms use the
equivalent location).

## Input

$ARGUMENTS

- `<task>`: run this task in Mythos mode (step 0 onward).
- `resume`: read the pointer `~/.cache/mythos/active` (if stale, glob
  `~/.claude/mythos/missions/` for the newest `status: open` mission matching the cwd),
  re-read the mission, continue from the first open PLAN item.
- `status`: print the active mission's goal, open/done counts, last LOG line. No work.
- `close`: set `status: done` in the active mission, append a final LOG line, remove the
  pointer file. No work.
- Empty: ask "Mythos mode active. What is the task?" and start at step 0 with the answer.

## Model gating

If the session model is already Mythos-class (Fable 5 / Mythos 5), skip the scaffold: state
goal and constraints, keep only the verify rule and the mission file if long-horizon, and let
the model work. Over-scaffolding degrades Mythos-class output.

## Steps

0. **Mission file.** Threshold first: one-line fix, factual question, five-minute job: skip
   the mode entirely, do it directly, report. Otherwise create the mission:
   - Slug: cwd basename, lowercased, non-alphanumerics to `-`. Path:
     `~/.claude/mythos/missions/<slug>--$(date +%Y%m%d-%H%M).md`.
   - Budget flag: read `~/.cache/wasteland/fable-share` (fields: EPOCH PCT FAB WEEK BUDGET).
     BUDGET>0 and (100*WEEK/BUDGET >= 90 or 200*FAB/BUDGET >= 90): `red`; >= 70: `yellow`;
     else `green`. File missing: `green`.
   - Write the file from the template below, write its absolute path as the single line of
     `~/.cache/mythos/active` (create the directory if needed).
   - The mission file is executive memory, and hooks read it: keep the frontmatter keys and
     checkbox markers exactly as in the template.

1. **Load the kernel.** Read `~/.claude/skills/mythos-scaffold/core/fable-distilled.md`.
   Its directives plus this command are the law for the run. Open other core files only on
   their kernel load-map triggers.

2. **Priming.** Only what the task needs: active `CLAUDE.md`, project notes, memory surface.
   Post-cutoff topics get WebSearch/WebFetch. Cap priming at 10 to 15 percent of the window.
   New domain: follow `core/context-priming.md`.

3. **Decomposition and workers.** Split by the kernel's rules; PLAN items go into the mission
   file (TodoWrite optional mirror). For fan-out, use the named agents with the model stated
   on every call, and follow the orchestration contract:
   - `mythos-scout` (haiku): mechanical bulk: search, count, inventory, bulk read.
   - `mythos-builder` (sonnet): scoped light implementation, single-area edits.
   - `mythos-heavy` (opus): hard code, multi-file features, subtle debugging, architecture.
   - `mythos-verifier` (sonnet): adversarial check of a claim or diff; it never edits.
   - Spec template per worker: `T:<job> IN:<paths/refs> OUT:<schema, list caps> KISIT:<limits>`.
     Full brief in the first message. Workers read files themselves; they return references
     (`path:line`) and verdicts, never file bodies. Output over ~40 lines goes to a scratch
     file; the return is the path plus a summary of at most 5 lines.
   - Independent workers launch in ONE message. Continue your own track while they run; never
     duplicate delegated work. Follow-ups to a live worker go via SendMessage, not a respawn.
   - Do not delegate jobs under ~5K tokens of reading/writing; do them directly.
   - Cheap-verify every worker verdict with one command before building on it.
   - Budget flag `yellow`: prefer sonnet workers, avoid opus fan-out. `red`: no fan-out,
     defer heavy work, tell the user.
   - Record planned calls under `## WORKERS` in the mission.

4. **Coding discipline.** If the task writes code: load the `guard-20` skill before the first
   edit and apply it while writing. Mid-iteration verification is typecheck + tests + build +
   smoke. `audit-20` runs only when the user declares the project final; never mid-loop.

5. **Agent loop.** Follow `core/agent-loop.md`: after each major step, one-line reflexion
   against `DONE =`; critical output gets one self-refine pass. Stuck = three no-progress
   turns: change the pattern (`core/failure-recovery.md`). Ceilings live in the mission
   frontmatter (default 10 turns / 30 min / 200K tokens); at a ceiling, stop and report
   honestly. Update `## PLAN` checkboxes with evidence and append one `## LOG` line at every
   checkpoint; after any compaction, re-read the mission first.

6. **Verification.** `core/verification.md`: headless checks before visual, output read fully,
   evidence for every claim. UI changed: browser smoke test. Record results under `## VERIFY`.

7. **Report and close.** Compact report in the user's language:
   ```
   Did: <one sentence>
   Verify: <which checks passed, with evidence>
   Files: <changed or created>
   Next: <if any>
   ```
   All PLAN items done: set `status: done`, final LOG line, remove
   `~/.cache/mythos/active`. Genuinely blocked on the user: set `status: blocked`, ask the
   one precise question. Failed at a ceiling: report approaches tried, current hypothesis,
   options, and leave the mission open for `resume`.

## Mission template

```markdown
---
mythos_mission: v1
id: <slug>--<yyyymmdd-hhmm>
project: <slug>
cwd: <absolute cwd>
status: open
model: <session model>
created: <ISO timestamp>
updated: <ISO timestamp>
turn: 0
ceil_turns: 10
ceil_min: 30
ceil_tok_k: 200
budget_flag: <green|yellow|red>
nudges: 0
last_open: -1
nudge_cap: 3
---

# G: <what the user holds at the end, one sentence>
DONE = <testable done-condition>

## INV
- <constraint that must never be violated>

## PLAN
- [ ] T1 <first task>
- [ ] T2 <second task>

## VERIFY
- method: <the check commands for this task>

## WORKERS
- <planned sub-agent calls, model explicit>

## STOP
- ask before: <destructive or scope-changing items>

## LOG
- [<hh:mm>] created
```

Markers: `[ ]` open, `[~]` in progress, `[x]` done with evidence on the same line, `[!]`
stuck. Hooks count `[ ]`, `[~]`, `[!]` as open.

## Rules

- **Stay faithful to the scaffold.** The kernel and the linked files are not decoration; do
  not bypass them with "my own way".
- **No completion without verify.** A PLAN item is not `[x]` until its evidence exists.
- **When stuck, change the pattern.** Retrying the same path is not persistence, it is
  inertia.
- **Never run destructive actions silently.** `rm -rf`, `git reset --hard`, force push,
  dependency removal: explicit user approval, every time.
- **Report in the user's language.** Direct, no filler.
- **Be honest about the ceiling.** If the task needs reasoning depth the scaffold cannot
  reach, say which single question deserves a Fable/Mythos session and continue with the rest.
