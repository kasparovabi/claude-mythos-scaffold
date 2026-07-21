---
type: guideline
tags:
  - system/guideline
  - mythos
  - agent-mode
related:
  - "[fable-distilled](./fable-distilled.md)"
  - "[decomposition](./decomposition.md)"
  - "[agent-loop](./agent-loop.md)"
  - "[verification](./verification.md)"
---

# Mythos mode

> A framework for pushing Claude toward behavior approaching Anthropic's Mythos-class models.
> Not a single file but a **mode**: a kernel plus demand-loaded skills used with discipline.
> The binding rules live in [fable-distilled](./fable-distilled.md); this file is the framing.

---

## What is Mythos?

On April 8, 2026, Anthropic opened `Claude Mythos Preview` as a gated research preview,
codename **Capybara**, distributed under Project Glasswing to critical partner organizations.

**Update (July 2026):** the Mythos line shipped publicly as **Claude Fable 5**
(`claude-fable-5`, priced well above Opus 4.8), with `claude-mythos-5` continuing under
Project Glasswing. Fable's own working patterns were distilled into the kernel
([fable-distilled](./fable-distilled.md)), first on 2026-07-06, revised 2026-07-21. The daily
executor this scaffold targets is **Opus 4.8**. If the session model is already Fable/Mythos
class, do not load the scaffold (see SKILL.md model gating).

Characteristics: strong autonomous reasoning over long horizons, subtle-failure detection,
multi-stage execution without losing focus. The most distinctive trait: iterating on a
problem instead of getting stuck.

Mythos = raw capability (weights) + agentic discipline (training-time).

---

## Closable vs not closable

| **Closable** (with scaffold) | **Not closable** (needs training) |
|---|---|
| Knowledge gap (cutoff): RAG, WebSearch, WebFetch | Raw reasoning depth |
| Action capacity: tool stack, MCP, sub-agent | Novel pattern recognition |
| Persistence and iteration: agent loop, hooks, mission file | Sample efficiency (no degradation at iter 50) |
| Domain context: priming, repo retrieval | "Seeing" connections nobody else has spotted |
| Verification discipline: headless tests, smoke runs | Autonomous multi-stage execution (training taught) |
| Failure recovery: Ralph loop, retry strategy | Encoded "do not give up" behavior (imitated, not 1:1) |

**Honest expectation:** this mode delivers roughly **40 to 60 percent** of Mythos, higher on
narrow tasks (code authoring, repo discovery, doc extraction, test running), much lower on
novel pattern discovery. The v2 eval harness (`eval/`) exists to replace this estimate with
measured deltas.

---

## When the mode is active

1. **Explicit:** user says "mythos mode", `/mythos-mode`, or "work at Mythos level".
2. **Implicit:** the threshold test fails: "Can I finish this in one context window, with one
   tool call, without getting stuck?"
3. **Recovery:** started in another mode and got stuck; the scaffold is needed to continue.

Skill loading is tiered: the kernel always, everything else on the kernel's load-map
triggers. Domain submodes layer on top: [research](../domains/research/mode.md) (multi-source
synthesis, citation discipline), [migration](../domains/migration/mode.md) (audit, plan,
execute, rollback), [memory](./memory.md) (cross-session recall).

---

## When the mode is overhead

- One-line fixes, knowledge questions, five-minute work: direct execution, no scaffold.
- User asked for speed: minimum overhead, but still no finishing without verify.
- Plan mode already active: research and design are happening there; trust the plan.

Heuristic: if the Mythos overhead exceeds the gain on this task, skip it.

---

## Operating template

```
1. Parse the task: deliverable, acceptance criterion, scope
2. Mission file: goal, done-condition, PLAN (via /mythos-mode)
3. Priming: repo and prior context, web verify if needed
4. Decomposition: PLAN items, sub-agent decisions with explicit models
5. Agent loop: plan-and-execute, reflexion after each major step
6. Verification: headless checks, output reading, evidence
7. (failure case): failure-recovery, pattern change
8. Compact report: done, verified, remaining
```

The order is not flexible. Skip a step deliberately, never out of laziness.

---

## Boundary of honesty

This framework is *not* Mythos. It is an **approach** to Mythos. Where it falls short, say
so: "this task needs Mythos-level raw capability; I can simulate with the scaffold but not
match it," then name the single question that deserves a Fable/Mythos session and continue
with the rest (see the kernel's escalation section).

No slop. Mythos mode is not "I can do everything." It is discipline plus honesty.

---

*Last update: 2026-07-21 (v2: rules moved into the kernel; mission file added).*
