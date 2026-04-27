# References & Acknowledgments

This scaffold synthesizes patterns from active open-source projects, research papers, and blog posts (2023 to 2026). Each pattern listed below either directly inspired this skill set or shaped a specific skill file. Listed alphabetically within categories.

This is independent work. **Not endorsed by, affiliated with, or representative of** any cited project, author, or organization.

## AI Memory Systems

### MemPalace

* **Authors:** Milla Jovovich + Ben Sigman, 2026
* **Repo:** https://github.com/MemPalace/mempalace
* **Site:** https://mempalace.tech
* **Used in:** `core/memory.md`
* **Patterns adopted:** AAAK 30x compression format, hierarchical loci memory (wings/rooms/halls/drawers), 170-token startup, semantic search via ChromaDB
* **Benchmark referenced:** 96.6 percent R@5 on LongMemEval

### claude-mem

* **Author:** thedotmack
* **Repo:** https://github.com/thedotmack/claude-mem
* **Site:** https://claude-mem.ai
* **Used in:** `core/memory.md` (alternative path mentioned)
* **Patterns adopted:** progressive disclosure (Search, then Timeline, then Get Observations), SQLite FTS5 search, ~10x token savings via compression

### memory-palace (jeffpierce)

* **Repo:** https://github.com/jeffpierce/memory-palace
* **Patterns observed:** persistent agent memory via MCP, knowledge graph integration

## Agent Patterns & Frameworks

### Ralph Loop

* **Coined by:** Geoffrey Huntley (named after Ralph Wiggum, persistent confused but undeterred)
* **Reference site:** https://asdlc.io/patterns/ralph-loop/
* **Repo (one implementation):** https://github.com/snarktank/ralph
* **Used in:** `core/failure-recovery.md`, `domains/migration/execute.md`
* **Pattern adopted:** verification-driven autonomous iteration (verify, fail, feedback, iterate); each iteration fresh context, memory persists via git history, progress notes, AGENTS.md learnings

### Self-Refine

* **Authors:** Madaan et al., 2023
* **Paper:** https://arxiv.org/abs/2303.17651
* **Site:** https://selfrefine.info/
* **Used in:** `core/agent-loop.md`, `domains/research/output.md`
* **Pattern adopted:** iterative output refinement (generate, critique, refine), score-based threshold, ~20 percent improvement over single-shot

### Reflexion

* **Authors:** Shinn et al., 2023
* **Paper:** https://arxiv.org/abs/2303.11366
* **Used in:** `core/agent-loop.md`
* **Pattern adopted:** episodic self-critique with memory, 4-question post-action reflection (what / target / gap / next)

### ReAct (Reasoning + Acting)

* **Authors:** Yao et al., 2022
* **Paper:** https://arxiv.org/abs/2210.03629
* **Used in:** `core/agent-loop.md`
* **Pattern adopted:** think-act-observe loop for exploratory tasks where flow is uncertain

### Plan-and-Execute

* **Origin:** LangChain agent architecture, 2023
* **Reference:** https://blog.langchain.dev/planning-agents/
* **Used in:** `core/agent-loop.md` (default pattern), throughout migration domain
* **Pattern adopted:** upfront planning plus sequential execution, replan on failure

### Adaptive RAG

* **Authors:** Jeong et al., 2024
* **Paper:** https://arxiv.org/abs/2403.14403
* **Used in:** `core/context-priming.md`, `domains/research/retrieval.md`
* **Pattern adopted:** query-complexity classifier routes each question to appropriate retrieval pipeline (lookup, multi-hop, synthesis)

### Agentic RAG (survey)

* **Authors:** Singh et al., 2025
* **Paper:** https://arxiv.org/abs/2501.09136
* **Repo:** https://github.com/asinghcsu/AgenticRAG-Survey
* **Used in:** `core/context-priming.md`, `domains/research/retrieval.md`
* **Pattern adopted:** planning, reflection, tool use over retrieval, multi-agent collaboration

### LangGraph deepagents

* **Reference:** https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents
* **Used in:** `domains/migration/execute.md`
* **Pattern adopted:** durable execution, checkpointing, stop, resume, retry across process boundaries

## Citation Verification

### Feynman AI Research Agent

* **Reference:** https://virtualuncle.com/feynman-ai-research-agent-2026/
* **Used in:** `domains/research/cite-verify.md`
* **Pattern adopted:** AI agent verifies its own citations via independent re-search, forward and backward citation chain traversal

### PaperOrchestra (Google Research)

* **Reference:** https://research.google/blog/improving-the-academic-workflow-introducing-two-ai-agents-for-better-figures-and-peer-review/ and https://www.marktechpost.com/2026/04/08/google-ai-research-introduces-paperorchestra-a-multi-agent-framework-for-automated-ai-research-paper-writing/
* **Used in:** `domains/research/synthesis.md`, `domains/research/cite-verify.md`
* **Pattern adopted:** multi-agent specialization with parallel execution, 52 to 88 percent quality improvement over single-agent baselines, average 45 to 48 citations per paper matching human authors
* **Note:** PaperOrchestra is Google's framework; this scaffold borrows the structural pattern, not the implementation.

### Elicit / Consensus / Scite.ai

* **Reference (Elicit):** https://elicit.com/
* **Used in:** `domains/research/retrieval.md` (mentioned as Tier 6 deep research tool)
* **Pattern observed:** sentence-level citation grounding, structured claim-evidence binding

## Codebase Migration Research

### Environment-in-the-Loop

* **Authors:** Various, 2026 (ReCode workshop)
* **Paper:** https://arxiv.org/abs/2602.09944
* **Conference:** https://conf.researchr.org/details/recode26/recode-2026-papers/5/Environment-in-the-Loop-Rethinking-Code-Migration-with-LLM-based-Agents
* **Used in:** `domains/migration/audit.md`
* **Pattern adopted:** environment integration is essential, static analysis alone insufficient; runtime feedback, build environment baseline.

### LLM Agents for Automated Dependency Upgrades

* **Authors:** Tawosi et al. (IBM Research), 2025
* **Paper:** https://arxiv.org/abs/2510.03480
* **Used in:** `domains/migration/mode.md`, `domains/migration/audit.md`
* **Pattern adopted:** multi-agent architecture (Summary Agent, Control Agent, Code Agent), 71.4 percent precision baseline cited

### Aviator: Java to TypeScript Migration

* **Reference:** https://www.aviator.co/blog/llm-agents-for-code-migration-a-real-world-case-study/
* **Used in:** `domains/migration/mode.md` (case study)
* **Pattern adopted:** real-world LLM-aided migration patterns

### Doctolib (Production Case Study)

* **Reference:** Cited via "Enterprise AI Agents 2026: Mid-Year Report", https://www.ampcome.com/post/enterprise-ai-agents-2026-mid-year-report
* **Used in:** `domains/migration/mode.md` (case study)
* **Result cited:** 40 percent faster shipping, hours instead of weeks for legacy testing infrastructure replacement

## Claude / Anthropic Sources

### Claude Mythos Preview

* **Reference:** https://red.anthropic.com/2026/mythos-preview/
* **Project Glasswing:** https://www.anthropic.com/glasswing
* **Used in:** Inspired the entire scaffold (capability ceiling discussion in `core/mode.md`)
* **Note:** This scaffold is **not** Claude Mythos Preview, nor a clone, nor endorsed by Anthropic. It is a third-party attempt to approximate observed behaviors via prompt, tool, and scaffold layering.

### Claude Code Skills Documentation

* **Reference:** https://code.claude.com/docs/en/skills, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
* **Used in:** Skill format conventions (frontmatter, structure)

### Claude Code Sub-Agents

* **Reference:** https://code.claude.com/docs/en/sub-agents
* **Used in:** `core/decomposition.md` (hub-and-spoke pattern, self-contained briefing rule)

## Other Active Projects (Pattern Influence)

### Anthropic Skills Repository

* **Repo:** https://github.com/anthropics/skills
* **Used in:** SKILL.md format reference (loose adoption; vault skills use slightly different conventions)

### Superpowers (multi-agent methodology)

* **Reference:** https://github.com/obra/superpowers (40K+ GitHub stars)
* **Pattern observed:** multi-agent battle-tested workflows

## Research Reports & Industry Surveys

* **Enterprise AI Agents 2026 Mid-Year Report:** https://www.ampcome.com/post/enterprise-ai-agents-2026-mid-year-report (production deployment statistics, scaling challenges)
* **Stack Overflow developer pain points 2026:** https://earezki.com/ai-news/2026-04-21-what-1000-developer-posts-told-me-about-the-biggest-pain-points-right-now/ (informed which pain points to address)
* **Long-Horizon Task Mirage:** https://arxiv.org/abs/2604.11978 (limits of long-horizon agent reliability)

## Vault & Knowledge Management

### Karpathy LLM Wiki

* **Reference:** Andrej Karpathy gist on LLM-curated wikis
* **Used in:** Author's private vault integration pattern (mentioned in `core/memory.md`'s vault and wiki coexistence section); the published scaffold references the pattern conceptually

### Obsidian

* **Reference:** https://obsidian.md
* **Used in:** Skill files use Obsidian-style `[[wikilink]]` format. Renders as plain text on GitHub (acceptable), resolves correctly in Obsidian-based vaults.

## How to Add a Reference

If you find your project influenced this scaffold and isn't credited, open a PR or issue. Format above; alphabetical within category.
