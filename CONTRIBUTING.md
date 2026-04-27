# Contributing

Thanks for considering a contribution. This repo prefers small, focused PRs over big rewrites.

## Quick Guide

1. **Fork + branch** , `git checkout -b your-feature`
2. **Match the tone** , direct, no AI slop, no "as an AI assistant" / "I'd be happy to" / "let's dive in" / "in conclusion" boilerplate. The skills themselves enforce this; PRs should too.
3. **Test in a real session** , if you add a new skill or modify an existing one, run a real Claude Code session to validate. Document what worked and what didn't.
4. **Open PR** , describe the change, link any session transcript or test artifact, note breaking changes (if any).

## Preferred Contribution Areas

| Area | Why it matters |
|---|---|
| **Cross-platform hook** | Current `mythos-sync.py` is Windows-tested. macOS/Linux variant needed. |
| **New domain modes** | Data engineering, DevOps incident response, content writing, technical interview prep , anything with multi-step structure. |
| **Generic versions** | Some skills lightly reference Obsidian-style vault conventions (such as a `(C)` prefix). Cleaner generic versions broaden adoption. |
| **Case studies** | Anonymized real-session walkthroughs in `examples/` , show scaffolding in action with both successes and limit-encounters. |
| **Translations** | Skills are bilingual-friendly (Turkish + English). Translations welcome. |
| **Bug fixes** | Inconsistent cross-links, formatting drift, broken sync hook scenarios. |

## What We're Not Looking For

- "Make the AI do anything" magic features (capability honesty is the core value)
- Bot evasion / unauthorized security testing tooling (ethically gray, out of scope)
- Generic AI hype rewrites without test backing
- Bulk auto-generated content (slop)

## Skill Format Convention

Every skill is a Markdown file with:
- YAML frontmatter (`type: skill | guideline`, `tags`, `related` cross-links)
- H1 title
- Block quote (>) one-line summary
- Sectioned content (Philosophy, Flow, Anti-Pattern, Quick Checklist)
- 200-300 lines target

Cross-references use Obsidian-style `[[wikilink]]` format. They render fine on GitHub as-is and resolve correctly in vault tools.

## Versioning

- v0.x , patterns evolving, breaking changes allowed
- v1.0 , when production-stability is claimed (multiple users, multiple sessions, no critical issues for a quarter)

## Code of Conduct

Be direct. Be honest about limitations. Don't oversell. If you find a flaw in the scaffolding, say so , the goal is patterns that work, not patterns that look good.
