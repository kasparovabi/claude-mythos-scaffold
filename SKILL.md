---
name: mythos-scaffold
description: Activate Mythos scaffold. Fable-distilled working patterns (decomposition, verification, next-action decision) plus a discipline framework (mode, tool-stack, context-priming, decomposition, agent-loop, verification, failure-recovery) and domain modes (research, migration) that push Opus-class and smaller models toward Mythos/Fable-grade agentic behavior. Use when starting complex multi-step work, long-horizon research, codebase migration, or tasks that benefit from systematic persistence and verification. Do NOT fully load on Fable 5 / Mythos 5; over-scaffolding degrades Mythos-class models.
---

# Mythos Scaffold

Pattern-based agentic discipline framework. Brings Plan-and-Execute, Reflexion, Self-Refine, and Ralph Loop into structured protocols, anchored by working patterns distilled from Claude Fable 5 itself on 2026-07-06, during the 2-7 July free window.

**Honest expectation:** the scaffold transfers process discipline, not capability. It makes Opus 4.8 a disciplined Opus 4.8. Raw reasoning depth, long-horizon coherence, and novel pattern recognition live in the weights and cannot be patched in via prompts.

## Model gating (check first)

| Session model | What to load |
|---|---|
| Opus 4.8 / Opus 4.x / Sonnet / Haiku | Tiered activation below |
| Fable 5 / Mythos 5 | Nothing, or at most `core/fable-distilled.md` section 2 (verification). State goal and constraints; do not enumerate steps. Per Anthropic's migration guide, prior-model scaffolding reduces Fable-class output quality. |

## Tiered activation

Always load (cheap, covers most sessions):

1. **Distilled patterns:** [`core/fable-distilled.md`](./core/fable-distilled.md)
2. **Mode rules:** [`core/mode.md`](./core/mode.md)

Load on trigger only, not preemptively:

| File | Open when |
|---|---|
| [`core/tool-stack.md`](./core/tool-stack.md) | Unsure which tool, or in what order, on a fresh problem |
| [`core/context-priming.md`](./core/context-priming.md) | New domain, "understand this project" |
| [`core/decomposition.md`](./core/decomposition.md) | Task will not fit one pass; sub-agent fan-out considered |
| [`core/agent-loop.md`](./core/agent-loop.md) | Long horizon, drift risk, multi-round iteration |
| [`core/verification.md`](./core/verification.md) | Before any "done" on non-trivial work |
| [`core/failure-recovery.md`](./core/failure-recovery.md) | Errors, stalls, repeated failure |
| [`core/memory.md`](./core/memory.md) | Cross-session recall matters (MemPalace / wiki) |

## Domain Modes

For specialized tasks, also load the relevant domain bundle:

- **Long-horizon research synthesis:** [`domains/research/`](./domains/research/)
  - `mode.md` -> `retrieval.md` (6-tier source hierarchy) -> `synthesis.md` (claim graph, contradiction tree) -> `cite-verify.md` (hallucination check) -> `output.md` (academic, blog, brief, slide, wiki)
- **Codebase migration / framework upgrade:** [`domains/migration/`](./domains/migration/)
  - `mode.md` -> `audit.md` (footprint, breaking change matrix) -> `plan.md` (phasing, calibrated time estimates) -> `execute.md` (atomic commits, sub-agent parallel) -> `rollback.md` (4 strategies + drill protocol)

## Slash Command

The `/mythos-mode <task>` command (installed at `~/.claude/commands/mythos-mode.md`) runs a full Mythos pass on a single task. Use it when the task is well-defined and you want the scaffold to drive end-to-end.

## When to Use

- Multi-step tasks where the model might stall, drift, or miss verification
- Long-horizon research across many sources (research domain)
- Framework or codebase migrations needing audit plus phased rollout (migration domain)
- Debugging cycles where naive retry fails (failure-recovery / Ralph Loop)
- Tasks where sub-agent parallelism helps (decomposition, with explicit model routing)

## When NOT to Use

- Single tool call, single answer questions: overhead not worth it
- Tasks already covered by a more specific skill
- Sessions running on Fable 5 / Mythos 5 (see model gating above)

## Changelog

- **2026-07-06:** `core/fable-distilled.md` added (patterns written by Fable 5 about its own decomposition, verification, and next-action habits). Read-all-8 activation replaced with tiered loading. Model gating added. Stale Opus 4.7 / hardcoded date references fixed. Sub-agent model routing added to decomposition.
- **2026-04-27:** initial 6-skill framework plus research and migration domains.

## Source

https://github.com/kasparovabi/claude-mythos-scaffold (MIT, by kasparovabi). Inspired by Claude Mythos Preview behaviors, not affiliated with Anthropic.
