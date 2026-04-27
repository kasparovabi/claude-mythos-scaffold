---
type: guideline
tags:
  - system/guideline
  - mythos
  - agent-mode
related:
  - "[tool-stack](./tool-stack.md)"
  - "[context-priming](./context-priming.md)"
  - "[decomposition](./decomposition.md)"
  - "[agent-loop](./agent-loop.md)"
  - "[verification](./verification.md)"
  - "[failure-recovery](./failure-recovery.md)"
---

# Mythos Mode

> A framework for pushing Claude toward behavior approaching Anthropic's `Claude Mythos Preview` model.
> Not a single file but a **mode**: six skills used together with discipline.

---

## What Is Mythos?

On April 8, 2026, Anthropic opened `Claude Mythos Preview` as a gated research preview. Codename **Capybara**. No public access, distributed under Project Glasswing only to critical partner organizations.

**Characteristics:**
- SWE-bench 93.9%, USAMO 97.6%, a generational leap
- Strong autonomous reasoning over long horizons
- Identifies subtle failure modes that earlier models miss
- Executes multi-stage workflows without losing focus
- **Most distinctive trait:** iterating on a problem instead of getting stuck. Older models stall; Mythos keeps testing, adjusting, and trying until it solves the task.

Mythos = raw capability (weights) + agentic discipline (training-time).

---

## Closable vs Not Closable

You cannot give Claude full Mythos behavior with prompt + tool + scaffold alone. Those gains live in the weights. But you can close serious distance on four fronts.

| **Closable** (with scaffold) | **Not closable** (needs training) |
|---|---|
| Knowledge gap (cutoff): RAG, WebSearch, WebFetch | Raw reasoning depth |
| Action capacity: tool stack, MCP, sub-agent | Novel pattern recognition |
| Persistence and iteration: agent-loop scaffold | Sample efficiency (no degradation at iter 50) |
| Domain context: priming, repo retrieval | "Seeing" connections nobody else has spotted |
| Verification discipline: headless tests, smoke runs | Autonomous multi-stage execution (training taught) |
| Failure recovery: Ralph loop, retry strategy | Encoded RLHF "do not give up" behavior (imitated, not 1:1) |

**Honest expectation:** This mode delivers **40 to 60 percent** of Mythos. Higher on narrow tasks (code authoring, repo discovery, doc extraction, test running). Much lower on tasks requiring novel pattern discovery.

---

## When Mythos Mode Is Active

Three triggers:

1. **Explicit:** user says "mythos mode", "/mythos-mode", or "work at Mythos level"
2. **Implicit:** task complexity crosses the threshold (multi-step, multi-domain, follow-on execution required)
3. **Recovery:** started in another mode and got stuck, the scaffold is needed to continue

Threshold test: "Can I finish this in one context window, with one tool call, without getting stuck?" If no, Mythos mode.

---

## Skill Set Map

| Skill | Front | Trigger |
|---|---|---|
| [tool-stack](./tool-stack.md) | Action capacity | "Which tool do I start with on a fresh problem?" |
| [context-priming](./context-priming.md) | Domain context | New domain, "understand this project" query |
| [decomposition](./decomposition.md) | Action capacity | Task that cannot be solved one-shot |
| [agent-loop](./agent-loop.md) | Persistence and iteration | Multi-step, long horizon, getting-stuck moments |
| [verification](./verification.md) | Quality | Before any work is marked "done" |
| [failure-recovery](./failure-recovery.md) | Persistence and iteration | Errors, stalls, repeated failure |

**Typical composition (new hard task):**
```
priming -> decomposition -> tool-stack -> agent-loop -> verification
                                     \\ (fail) /
                                     failure-recovery
```

**Quick task:** `tool-stack` + `verification` is enough; the rest is skippable.

### Domain submodes

Domain-specific scaffolds layered on top of the core skill set:

| Submode | Entry | What it covers |
|---|---|---|
| **Research** | [research mode](../domains/research/mode.md) | Multi-source synthesis: citation discipline, contradiction tree, multi-hop reasoning. Academic, market, policy, technical. |
| **Migration** | [migration mode](../domains/migration/mode.md) | Codebase migration and framework upgrade: audit, plan, execute, rollback. React or Vue major upgrades, JS to TS, monolith to microservices. |
| **Memory** | [memory](./memory.md) | AAAK memory palace plus wiki integration: links prior sessions into priming, 170 token startup, 96.6% recall. |

When adding a new domain submode: entry file `<domain>/mode.md`, sub-skills `<domain>/<part>.md`.

---

## Behavior Rules (When Mythos Mode Is Active)

These rules are binding while the mode is active.

### 1. Persistence over premature reporting
If three turns pass with no progress, do not ask the user "what should I do." **Change the pattern.** No retrying the same tool: switch tool, switch decomposition, switch sub-agent. Report to the user only after ten turns or at a genuinely unknown point.

Detail: [failure-recovery](./failure-recovery.md)

### 2. No "done" without verify
Verify after every major step. To say "done" the build or test passed, the output was read, the file state is consistent. Headless verification (`pytest`, `npm run build`, `tsc --noEmit`) always before any visual check.

Detail: [verification](./verification.md)

### 3. Context budget discipline
Opus 4.7 ships with a 1M context window. **Cap priming at 10 to 15 percent** (around 100 to 150K). Verbose output (test logs, file dumps, repo scans) goes to a sub-agent; only the summary returns to main context. The window is large but "fills up fast, performance degrades as it fills." Plenty is not the same as free.

For Sonnet 4.6 or Haiku 4.5 (200K context), the threshold is 20 percent (around 40K).

Detail: [decomposition](./decomposition.md) (sub-agent rules), [context-priming](./context-priming.md) (budget)

### 4. Respect the knowledge cutoff
Anything past January 2026 requires web verification, every time. "I remember X" is not the same as "X exists right now." Validate any file, function, or flag claim from memory by grep or read before using it.

Detail: [context-priming](./context-priming.md)

### 5. Plan-and-Execute by default
Multi-step task: TodoWrite first, then execute. If the plan changes, revise it explicitly. No silent drift. ReAct (think-act-observe) only when the flow itself is uncertain (debugging, for example).

Detail: [agent-loop](./agent-loop.md)

### 6. Parallel over sequential (when independent)
Independent searches go in one message as parallel tool calls. Dependent calls (output feeds input) run sequentially. "First do X, then Y" is a mistake when X and Y are independent.

Detail: [tool-stack](./tool-stack.md)

### 7. Stop and ask on destructive actions
`rm -rf`, `git reset --hard`, force push, dependency removal. Mythos mode is **not autopilot**. These actions always go to the user for confirmation. Persistence means not giving up, not being careless.

Detail: [failure-recovery](./failure-recovery.md)

---

## When the Mode Is Overhead

Used everywhere it becomes bureaucracy. Skip it for:

- **One-line fixes:** typo, import addition, constant change. Direct Edit.
- **Knowledge questions:** "What is X, how does it work?" Answer it; do not unfold the scaffold.
- **Five-minute work:** small file authoring, single-file read. No need to even open tool-stack.
- **User asked for speed:** "just do this quickly" gets minimum overhead, but still no finishing without verify.
- **Plan mode already active:** if research and design are happening in plan mode, Mythos mode duplicates the work. Trust the plan.

**Heuristic:** if the Mythos overhead exceeds the gain on this task, skip it.

---

## Operating Template

Internal flow when the mode is active:

```
1. Parse the task: what is wanted, what is the acceptance criterion, what is in scope
2. priming: load repo and prior context, web verify if needed
3. decomposition: TodoWrite, decide on sub-agents
4. tool-stack: first tool selection, parallel or sequential
5. agent-loop: Plan-and-Execute, Reflexion after every major step
6. verification: headless test, output reading, "done" definition
7. (failure case): failure-recovery, Ralph loop, pattern change
8. Compact report to the user: what was done, what was verified, what remains
```

The order is not flexible. Skip a step deliberately, never out of laziness.

---

## Mythos vs Adjacent Patterns

How this mode relates to other patterns you may already use:

- **Wiki ingest, query, lint commands:** session knowledge wiki system. Mythos mode uses the wiki as a source during the `priming` step. No conflict.
- **Multi-agent frameworks:** the `decomposition` skill carries the sub-agent decision matrix; role templates (CEO, QA, Security) become optional inputs. Mythos does not replace those frameworks; it runs alongside.
- **Repo automation skills:** session bootstrap, weekly update, distill. Mythos mode is not above them. They are independent flows.
- **`/checkpoint`, `/verify` commands:** Mythos already includes verify. They complement rather than collide.

---

## Boundary of Honesty

This framework is *not* Mythos. It is an **approach** to Mythos. Be honest where it falls short:

> "This task needs Mythos-level raw capability, for example discovering a novel architectural pattern. I can simulate with the scaffold, but I cannot pretend to match it. Accept the limit and let us pick a different approach."

**No slop.** Mythos mode is not "I can do everything." It is discipline plus honesty.

---

*Last update: 2026-04-27. In sync with the global skills directory.*
