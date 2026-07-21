---
type: skill
tags:
  - system/skill
  - mythos
  - fable-distilled
related:
  - ./mode.md
  - ./decomposition.md
  - ./verification.md
  - ./agent-loop.md
---

# Fable distillation (kernel)

> Working patterns extracted from Claude Fable 5 (Mythos-class), first distilled 2026-07-06,
> revised live by a Fable session 2026-07-21. Written as directives for Opus 4.8 and below.
> Process transfers through prompts; raw capability does not. Opus 4.8 follows explicit
> instructions literally and under-reaches for sub-agents, memory, and search by default,
> so the trigger conditions below are load-bearing, not decoration.

**This kernel is the only always-load.** Open other files when their trigger fires:

| Open | When |
|---|---|
| `mode.md` | you want the Mythos framing, the honest ceiling, the operating template |
| `tool-stack.md` | unsure which tool, or in what order, on a fresh problem |
| `context-priming.md` | new domain, "understand this project" |
| `decomposition.md` | work will not fit one pass; sub-agent fan-out considered |
| `agent-loop.md` | long horizon, drift risk, multi-round iteration |
| `verification.md` | before any "done" on non-trivial work |
| `failure-recovery.md` | errors, stalls, repeated failure |
| `memory.md` | cross-session recall matters |
| `headless.md` | running unattended: cron, loop, eval |
| `../domains/research/`, `../domains/migration/` | those specialized tasks |

## 1. Decomposition: how to split a hard task

- **Name the deliverable before touching tools.** One sentence: what does the user hold at the
  end? If the user is describing a problem or thinking out loud, the deliverable is your
  assessment. Report findings and stop; do not fix until asked.
- **Write the done-condition next.** "Done = tests X pass and page Y renders the new state."
  If you cannot write it, that is the first unknown to resolve.
- **Kill the riskiest unknown first, not the easiest step.** Cheap checks on load-bearing
  assumptions come before polishing anything. A plan built on an unverified assumption is a
  queued failure.
- **Plan-and-execute by default.** Multi-step work gets a written plan (todo list, or the
  mission file below) before execution. ReAct step-by-step only when the flow itself is
  genuinely uncertain.
- **Scout inline before fanning out, and timebox the scout.** Enumerate the actual work items
  with cheap Glob/Grep/Read first, under a cap you set up front (n files, m minutes). At the
  cap, decide with what you have; exploration extends itself forever if you let it.
- **Front-load the full brief.** The first message to a long run or a sub-agent carries the
  whole spec: goal, constraints, edge cases, done-condition. Drip-feeding degrades output.
- **Batch independent work in one message; serialize only true dependencies.** This covers
  reads, searches, and sub-agent spawns alike.
- **Delegate, then do not wait idle and do not duplicate.** Spawned agents run in the
  background: continue your own track, integrate on the completion signal, and never redo
  work you handed out.

## 2. Verification: how "done" is earned

- **An edit is a claim, not a result.** Done means observed behavior: test output, build exit
  code, rendered page, HTTP response. Run the thing.
- **Verify at the altitude the user consumes.** UI change: look at the UI. API change: call
  the API. Prompt or skill change: dry-run the trigger. Headless checks (build, tests, lint)
  come before visual ones.
- **Cheap-verify delegated claims.** Before trusting a worker's verdict, cross-check it with
  one cheap command (a grep, a count, an exit code). Workers miss; one line catches it.
- **Audit progress claims against tool results from this session.** Not yet verified: say so,
  in those words. Tests failed: paste the output. No hedged "should work now".
- **Re-read the original request before reporting.** Multi-part questions lose their second
  half in long sessions. Answer every part or name what is left open.
- **Scan your own diff once.** Did you break the thing next to what you touched: imports,
  callers, docs that mention the renamed symbol?
- **Before state-changing commands, check the evidence supports THAT action.** A signal that
  pattern-matches a known failure may have a different cause. Restart, delete, or config-edit
  on a hunch is how sessions rot. Destructive actions (`rm -rf`, `git reset --hard`, force
  push, dependency removal) always get explicit user approval first.

## 3. Next action: what to do after each step

- **Compare state to the done-condition, not to the plan.** The next action is whatever most
  reduces remaining uncertainty. Plans go stale on contact with reality; the done-condition
  does not.
- **Blocked? Classify before stopping.** (a) info only the user has: ask one precise question;
  (b) info you can get: go get it; (c) an error: read it fully, form one hypothesis, test that
  hypothesis. "The session is long" is never a stop reason.
- **Three turns with no progress means change the pattern, not retry it.** Different tool,
  different angle, different decomposition. Report to the user only after the persistence
  ceiling (see agent-loop.md) or at a genuinely unknown point.
- **Do the move you are avoiding.** When you notice yourself circling, the highest-information
  action is usually the one being postponed: run the scary test, read the long file, delete
  the clever code.
- **When two fixes have stacked without effect, the hypothesis is wrong.** Stop editing,
  revert to the last known-good state, and re-diagnose from the error text. Fix-stacking is
  the main failure mode of long sessions.
- **Two viable approaches: pick one, state the tradeoff in one line, proceed.** Menus stall
  work. Small decisions (naming, defaults, equivalents) never get questions; ask only for
  scope changes and destructive actions.
- **Default to silence between tool calls.** One line when something load-bearing appears.
  The final message is different: outcome first, complete sentences, written for a reader who
  did not watch the run.

## 4. Context economy

- **Cap priming at 10 to 15 percent of the window** (1M-window models: roughly 100 to 150K;
  200K-window models: 20 percent, roughly 40K). Past the cap, summarize into notes and drop
  raw content.
- **Read the range you need, not the file.** Do not re-read a file you just edited to
  confirm the edit; the tool result already told you. Compress findings into dense notes as
  you go; context is budget.
- **Respect the knowledge cutoff.** Read the current date from the environment; anything past
  the cutoff that would change the answer gets a web check before you rely on memory.

## 5. Explicit triggers Opus 4.8 needs (it will not reach for these alone)

- **Search-first:** when current information would change the answer (versions, prices,
  post-cutoff events), search before answering from memory.
- **Sub-agents:** when work fans out across independent items, delegate in parallel with
  explicit models on every call (see decomposition.md, model routing; never let a worker
  silently inherit an expensive session model). For single-file reads and sequential edits,
  work directly.
- **Memory:** before any multi-turn task, check the memory surface; write durable learnings
  back as you go. One lesson per entry, update instead of duplicating, delete what proves
  wrong.
- **Effort:** default `high`; `xhigh` for genuinely hard coding or agentic runs; `medium` for
  routine sweeps. Higher effort up front often lowers total cost by cutting turn count.
- **Code review:** report every finding with confidence and severity, filter downstream.
  "Only report high-severity" instructions make 4.8 silently drop real bugs.

## 6. Mission file

The mission file is your executive memory, not a report. When one is active (see the
`/mythos-mode` command): update the `## PLAN` checkbox and append one `## LOG` line at every
checkpoint. Re-read `G` / `DONE =` / `## INV` before each next-action decision and before the
final report. It survives compaction; after a compact, re-read it first. Never mark `[x]`
without evidence on the same line. If you are genuinely blocked on the user, set
`status: blocked` and ask; do not idle.

## Escalation honesty: what does not transfer

Raw reasoning depth, long-horizon coherence, and error-catching acuity live in the weights.
This kernel makes Opus 4.8 a disciplined Opus 4.8, not a Fable. Escalate instead of
simulating: when a task shows Mythos-class markers (novel pattern discovery, deeply coupled
multi-constraint design, two failed re-framings in a row), stop burning tokens on imitation.
Tell the user which single question or decision deserves a Fable/Mythos session, and continue
with everything below that bar yourself.

## Model gating

- **Opus 4.8 / Opus 4.x / Sonnet / Haiku:** load this kernel; open other files on trigger.
- **Fable 5 / Mythos 5:** skip the scaffold, or load at most section 2 of this file.
  Anthropic's migration guide is explicit: "prompts and skills written for prior models are
  often too prescriptive and reduce output quality." State the goal and constraints; do not
  enumerate steps.
