# Claude Mythos Scaffold

> Pattern-based scaffold for systematic AI agent work, with honest capability boundaries.
> Inspired by observed Claude Mythos Preview behaviors (Anthropic, April 2026). Not affiliated with Anthropic.

A Claude Code skill set that brings agentic discipline (Plan-and-Execute, Reflexion, Self-Refine, Ralph Loop) into structured, reusable protocols. Real-world tested in production sessions; capability limits documented honestly.

## Why This Exists

Claude Mythos Preview demonstrated agentic behaviors (problem persistence, multi-step iteration, verification-driven correction) that scaffold patterns can partially reproduce in vanilla Claude (Sonnet 4.6, Opus 4.7). This repo packages those patterns as opt-in skills.

**Honest expectation:** scaffolding closes 40 to 60 percent of the gap. Raw reasoning depth, novel pattern recognition, and sample efficiency cannot be patched in via prompts; those are weights.

**What you get:** systematic protocols for tool selection, context priming, problem decomposition, verification loops, and failure recovery. Plus two domain modes: long-horizon research synthesis and codebase migration.

## Repository Layout

```
claude-mythos-scaffold/
├── core/                          Foundation skills (vault-agnostic)
│   ├── mode.md                    Entry point, mode rules
│   ├── tool-stack.md              Cascade selection, parallel/sequential
│   ├── context-priming.md         Adaptive RAG, source hierarchy
│   ├── decomposition.md           Sub-agent delegation, hub-and-spoke
│   ├── agent-loop.md              Plan-Execute, Reflexion, Self-Refine
│   ├── verification.md            Headless verify, output reading
│   ├── failure-recovery.md        Ralph Loop, persistence threshold
│   └── memory.md                  MemPalace integration, AAAK format
├── domains/
│   ├── research/                  Long-horizon multi-source synthesis
│   │   ├── mode.md
│   │   ├── retrieval.md           6-tier source hierarchy
│   │   ├── synthesis.md           Claim graph, contradiction tree
│   │   ├── cite-verify.md         Hallucination check, Feynman pattern
│   │   └── output.md              Academic / blog / brief / slide / wiki
│   └── migration/                 Codebase migration / framework upgrade
│       ├── mode.md
│       ├── audit.md               Footprint, breaking change matrix
│       ├── plan.md                Phasing, calibrated time estimates
│       ├── execute.md             Atomic commits, sub-agent parallel
│       └── rollback.md            4 strategies, drill protocol
├── commands/
│   └── mythos-mode.md             /mythos-mode slash command
├── hooks/
│   └── mythos-sync.py             PostToolUse hook, vault to global sync
└── examples/
    └── (real session walkthroughs, coming)
```

## Quick Start

### Option A: Drop into Claude Code

Copy core skills to your global Claude Code skills directory.

macOS or Linux:

```bash
mkdir -p ~/.claude/skills/mythos
cp core/* ~/.claude/skills/mythos/
cp commands/mythos-mode.md ~/.claude/commands/
```

Windows:

```powershell
mkdir -p $env:USERPROFILE\.claude\skills\mythos
Copy-Item core\* $env:USERPROFILE\.claude\skills\mythos\
Copy-Item commands\mythos-mode.md $env:USERPROFILE\.claude\commands\
```

Then in any Claude Code session:

```
/mythos-mode <your task>
```

### Option B: Domain-only

Just need research synthesis or codebase migration scaffold? Copy the relevant `domains/<name>/` directory plus `core/` (foundation skills are required).

### Option C: Vault integration (Obsidian-style)

If you maintain a knowledge vault, the skills support `[[wikilink]]` cross-references and integrate with MemPalace for verbatim conversation history. See `core/memory.md`.

## What's Tested vs Newer

**Production-tested** (used across multiple real Claude Code sessions):

* `core/mode.md`, `tool-stack.md`, `context-priming.md`, `decomposition.md`, `agent-loop.md`, `verification.md`, `failure-recovery.md`

**Newer (1 internal review pass):**

* `core/memory.md` (MemPalace integration)
* `domains/research/*` (5 skills)
* `domains/migration/*` (5 skills)

Real-world feedback expected; PRs welcome.

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

* Cross-platform sync hook (currently Windows-tested, Unix variant needed)
* Real-world session case studies (anonymized)
* Generic versions of vault-specific references (some skills mention conventions like `(C)` prefix; these are opt-in)
* Additional domain modes (data engineering, devops incident response, content writing)

## License

MIT, see `LICENSE`.

## Anti-Goals (What This Is Not)

* "10x your AI agent" magic. Scaffolding helps consistency, not raw capability.
* Drop-in replacement for engineering judgment. The scaffold structures decisions; humans still make them.
* Production-stable v1.0. This is v0.1; patterns are sound, edge cases will surface.

If you're looking for those things, this repo will disappoint. If you're looking for systematic AI agent discipline with honest documentation, it's a starting point.
