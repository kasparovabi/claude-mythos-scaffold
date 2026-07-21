# Claude Mythos Scaffold

> Pattern-based scaffold for systematic AI agent work, with honest capability boundaries.
> Inspired by observed Claude Mythos Preview behaviors (Anthropic, April 2026). Not affiliated with Anthropic.

A Claude Code skill set that brings agentic discipline (Plan-and-Execute, Reflexion, Self-Refine, Ralph Loop) into structured, reusable protocols. Since v0.3 the discipline is not only prose: a persistent mission file externalizes task state, Stop/SessionStart hooks enforce persistence at the harness level, named sub-agents carry explicit model routing, and a small eval harness measures the scaffold instead of trusting it.

## Why This Exists

Claude Mythos Preview demonstrated agentic behaviors (problem persistence, multi-step iteration, verification-driven correction) that scaffold patterns can partially reproduce in Opus-class and smaller models (Opus 4.8, Sonnet 5, Haiku 4.5). This repo packages those patterns as opt-in skills. The kernel, `core/fable-distilled.md`, carries working patterns written by Claude Fable 5 (the GA'd Mythos-class model) about its own decomposition, verification, and next-action habits: first captured 2026-07-06, revised live by a Fable session 2026-07-21.

**Honest expectation:** the scaffold transfers process discipline, not capability. It makes Opus 4.8 a disciplined Opus 4.8, not a Fable. Raw reasoning depth, novel pattern recognition, and sample efficiency cannot be patched in via prompts; those are weights. Do not fully load it on Fable 5 / Mythos 5: over-scaffolding degrades Mythos-class output.

**What you get:** a compact always-load kernel, demand-loaded protocols for tool selection, priming, decomposition, verification and failure recovery, a mission-file lifecycle with enforcement hooks, four worker agent definitions, a headless profile for unattended runs, an eval harness, and two domain modes (research synthesis, codebase migration).

## Repository Layout

```
claude-mythos-scaffold/
├── SKILL.md                       Skill entry: model gating + kernel activation
├── INTEGRATION.md                 Route-don't-duplicate table (neighbor skills)
├── core/
│   ├── fable-distilled.md         The kernel: Fable 5 patterns + binding rules (read first)
│   ├── mode.md                    Framing, honest ceiling, operating template
│   ├── tool-stack.md              Cascade selection, parallel/sequential
│   ├── context-priming.md         Adaptive RAG, source hierarchy
│   ├── decomposition.md           Sub-agent delegation, model routing
│   ├── agent-loop.md              Plan-Execute, Reflexion, Self-Refine
│   ├── verification.md            Headless verify, output reading
│   ├── failure-recovery.md        Ralph Loop, persistence threshold
│   ├── memory.md                  Cross-session memory integration
│   └── headless.md                Preamble for unattended runs (cron, loops, eval)
├── agents/                        Worker definitions (install into ~/.claude/agents/)
│   ├── mythos-scout.md            haiku: mechanical bulk, references only
│   ├── mythos-builder.md          sonnet: scoped light implementation
│   ├── mythos-heavy.md            opus: hard multi-file work
│   └── mythos-verifier.md         sonnet: adversarial verification, never edits
├── hooks/
│   ├── mythos-stop.py             Stop hook: blocks premature stops (bounded nudges)
│   ├── mythos-session.py          SessionStart hook: mission survives compaction
│   ├── autoskill-mythos-rule.snippet  Optional prompt-router rule (documented)
│   ├── install.sh                 Copies hooks, prints settings JSON
│   └── README.md                  Contract, registration, kill-switch
├── eval/
│   ├── mythos-eval                Runner: bare vs scaffold arms, headless
│   ├── tools/metrics.py           Objective metrics from stream-json transcripts
│   ├── tasks/T1-persistence/      Planted-obstacle fixture + check.sh
│   ├── tasks/T2-verification/     Tempting-wrong-fix fixture + check.sh
│   └── distill/CURATION.md        Distillation curation procedure (manual)
├── domains/
│   ├── research/                  mode, retrieval, synthesis, cite-verify, output
│   └── migration/                 mode, audit, plan, execute, rollback
└── commands/
    └── mythos-mode.md             /mythos-mode: mission lifecycle + full pass
```

Runtime state lives outside the repo: missions in `~/.claude/mythos/missions/`, the active-mission pointer in `~/.cache/mythos/active`, eval data in `~/.claude/mythos/eval-data/`.

## Quick Start

### Option A: Symlink into Claude Code (recommended)

macOS or Linux:

```bash
git clone https://github.com/kasparovabi/claude-mythos-scaffold ~/.claude/skills/mythos-scaffold
cd ~/.claude/skills/mythos-scaffold
ln -sf "$PWD/commands/mythos-mode.md" ~/.claude/commands/mythos-mode.md
mkdir -p ~/.claude/agents
for f in agents/mythos-*.md; do ln -sf "$PWD/$f" ~/.claude/agents/"$(basename "$f")"; done
bash hooks/install.sh   # optional: enforcement hooks; prints the settings.json entries
```

Symlinks keep the installed command and agents in lockstep with the repo. If your platform lacks symlink support, `cp` works identically (the command uses absolute paths, no macro resolution).

Then in any Claude Code session:

```
/mythos-mode <your task>
/mythos-mode resume | status | close
```

### Option B: Domain-only

Just need research synthesis or codebase migration? Copy the relevant `domains/<name>/` directory plus `core/` (the kernel is required).

### Option C: Vault integration (Obsidian-style)

If you maintain a knowledge vault, the skills support `[[wikilink]]` cross-references and integrate with MemPalace for verbatim conversation history. See `core/memory.md`.

## What's Tested vs Newer

**Production-tested** (used across multiple real Claude Code sessions):

* `core/mode.md`, `tool-stack.md`, `context-priming.md`, `decomposition.md`, `agent-loop.md`, `verification.md`, `failure-recovery.md`

**Newer (v0.3, self-tested + eval-smoked, real-world feedback expected):**

* `core/fable-distilled.md` kernel revision, mission-file lifecycle, `hooks/*`, `agents/*`, `core/headless.md`, `eval/*`
* `core/memory.md`, `domains/research/*`, `domains/migration/*`

## Acknowledgments

This scaffold is a synthesis of patterns from active open-source projects, research papers, and industry case studies. Full credit list with links: see [REFERENCES.md](./REFERENCES.md).

Highlights:

* [Claude Mythos Preview](https://red.anthropic.com/2026/mythos-preview/) (Anthropic, April 2026): the observed behaviors that motivated this scaffold
* [MemPalace](https://github.com/MemPalace/mempalace) (Jovovich + Sigman, 2026): AAAK compression, hierarchical loci memory, used in `core/memory.md`
* [claude-mem](https://github.com/thedotmack/claude-mem) (thedotmack): Claude Code-native memory plugin alternative
* [Ralph Loop](https://asdlc.io/patterns/ralph-loop/) (Geoffrey Huntley): persistence pattern, used in `core/failure-recovery.md`
* [Self-Refine](https://arxiv.org/abs/2303.17651) (Madaan et al.): iterative output refinement, used in `core/agent-loop.md`
* [Reflexion](https://arxiv.org/abs/2303.11366) (Shinn et al.): episodic self-critique
* [ReAct](https://arxiv.org/abs/2210.03629) (Yao et al.): think-act-observe loop
* [Adaptive RAG](https://arxiv.org/abs/2403.14403) (Jeong et al.): query-complexity routing, used in `domains/research/retrieval.md`
* [PaperOrchestra](https://research.google/blog/improving-the-academic-workflow-introducing-two-ai-agents-for-better-figures-and-peer-review/) (Google Research): multi-agent research synthesis
* [Environment-in-the-Loop](https://arxiv.org/abs/2602.09944) (ReCode 2026): code migration with environment integration
* [Aviator Java to TypeScript case study](https://www.aviator.co/blog/llm-agents-for-code-migration-a-real-world-case-study/), Doctolib production migration (2026 enterprise reports)

This repo is independent. **Not endorsed by Anthropic, MemPalace, or any cited project.** Patterns are credited; opinions and integration choices are mine.

## Contributing

PRs welcome, see `CONTRIBUTING.md`. Particular areas of interest:

* Real-world session case studies (anonymized) for an `examples/` directory
* More eval tasks (decomposition, orchestration axes) and cross-model baselines
* Generic versions of vault-specific references (some skills mention conventions like `(C)` prefix; these are opt-in)
* Additional domain modes (data engineering, devops incident response, content writing)

## License

MIT, see `LICENSE`.

## Anti-Goals (What This Is Not)

* "10x your AI agent" magic. Scaffolding helps consistency, not raw capability.
* Drop-in replacement for engineering judgment. The scaffold structures decisions; humans still make them.
* Production-stable v1.0. This is v0.3; patterns are sound, edge cases will surface.

If you're looking for those things, this repo will disappoint. If you're looking for systematic AI agent discipline with honest documentation, it's a starting point.
