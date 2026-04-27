---
type: guideline
tags:
  - system/guideline
  - mythos
  - research
  - synthesis
related:
  - ../../core/mode.md
  - ./retrieval.md
  - ./synthesis.md
  - ./cite-verify.md
  - ./output.md
  - ../../core/memory.md
---

# Mythos Research

> Long-horizon multi-source research synthesis sub-mode of Mythos.
> Systematic scaffold for academic literature review, market intelligence, technical decision support, and policy review.

---

## Philosophy

1. **Synthesis is not summarization.** A summary shortens a source paragraph; synthesis builds the relationship **between** sources: contradiction, complement, gap, novel insight. Synthesis is the characteristic strength of Mythos research.
2. **Citation is the atom.** Every claim is sourced. An unsourced sentence is a hypothesis and is marked as one. This is the antidote to hallucination.
3. **Multi-hop beats single-hop.** "X claims Y" is not enough. "X claims Y, Z refutes it, W finds the middle ground" is synthesis. Multi-hop reasoning is the core contribution of research mode.
4. **Iteration multiplies quality.** Self-Refine pattern: draft, critique, revise. Multi-agent benchmarks show 52 to 88 percent quality lift from iterative passes.

---

## Activation Threshold

When does research sub-mode activate?

| Situation | Active |
|---|---|
| Multi-source synthesis required (3 or more sources) | yes |
| Citation quality is critical (academic, policy, journalism) | yes |
| Contradiction detection is valuable (literature review) | yes |
| Single-source one-shot lookup (wiki query) | no, overkill |
| Quick summary of a current event (news tracking) | no, web search is enough |
| Personal opinion writing (no sources required) | no, internal-comms style is better |
| Learning a concept inside one codebase | no, an explore agent is enough |

**Net threshold:** 3 or more sources, citation required, contradiction or gap detection valuable, then research mode applies.

---

## Research Types

| Type | Characteristic | Typical sources | Output |
|---|---|---|---|
| **Academic** | Peer-reviewed, methodology critique, citation chain | arXiv, Scholar, journal databases | Literature review, gap analysis, draft paper |
| **Market intelligence** | Competitive intel, trend, financial signal | Public filings, industry reports, Bloomberg, professional networks | Market brief, competitor matrix, executive summary |
| **Technical decision support** | Codebase plus docs plus community Q and A plus RFC | GitHub, official docs, Stack Overflow, public discussion archives | Technical brief, architecture comparison, decision record |
| **Policy and regulatory** | Legal text, regulator stance, expert commentary | Government portals, law firm white papers, news | Policy brief, compliance gap, position paper |
| **Personal knowledge** | Local notes plus prior session memory plus external | Internal knowledge base, conversation history, web | Insight note, weekly synthesis, decision support |

The type determines source authority, citation format, and output template.

---

## Skill Set Map

```
research/
├── mode.md         <- entry point (this file)
├── retrieval.md    <- multi-source retrieval
├── synthesis.md    <- claim mapping, contradiction tree
├── cite-verify.md  <- per-claim source verification
└── output.md       <- format adaptation (academic, blog, brief)
```

**Typical flow:**

```
priming -> retrieval -> synthesis -> cite-verify -> output
              ^           |              |
              +.... iter .+ <............+
                  (self-refine)
```

After every major step, run a Reflexion pass: what did I produce, what was I aiming for, what is the gap, what is the next round.

---

## Behavior Rules in Research Mode

### 1. Citation atom rule
Every factual claim ends with `[ref:N]` or an inline link. An unsourced sentence equals a hypothesis and gets a "Hypothesis:" prefix. This is not a reporting format; it is mandatory during drafting and cannot be added later.

### 2. Contradiction is visible
When you find a conflict, do not delete it. Source both sides: "Source A: ... ; Source B (conflict): ..." The user decides priority, or the methodology section explains the call.

### 3. Source authority order
Do not weigh sources equally. Order: peer-reviewed, canonical docs, institutional white papers, quality blogs, forums and social posts. When citing a low-authority source, mark it as "low confidence source".

### 4. Recency window
Domain dependent:
- Tech, AI, security: 6 to 12 months (everything moves fast)
- Foundational academic (math, theoretical physics): 5 to 10 years is fine
- Applied academic (CS, applied biology): 2 to 3 years
- Market intelligence: 3 to 6 months
- Policy: current legal year

A source outside the window is marked "historical reference".

### 5. Multi-hop reasoning is explicit
Write the chain "claim X, source Y, gap Z" so it is visible. Reader trust comes from the chain being legible.

### 6. Self-Refine, at least one pass
After draft, run a critique pass: 0 to 10 score, anything below 8 gets revised. Check citation density, claim balance, contradiction handling, output format match.

### 7. Output format adapts
Academic draft, blog post, executive brief, decision memo, slide deck. Format is set by the user or context. The same synthesis serializes differently into each.

---

## Composition: Typical 4-Hour Flow

**Hour 0 to 1: Priming and retrieval**
- Parse the task, define scope, choose recency window
- Local knowledge base plus prior session memory query
- 3 to 5 parallel web searches (different angles)
- Fetch canonical sources (top 5 to 10)
- Deep crawl when needed (1 to 2 sites)
- Output: `research/raw/sources.jsonl` (one source per line), `research/sources-rank.md` (authority and recency rank)

**Hour 1 to 2: Synthesis**
- Claim extraction per source (5 to 15 claims each)
- Claim graph: support, refute, complement edges
- Contradiction tree with conflict points marked
- Multi-hop reasoning chains written out
- Output: `research/synthesis.md` (claim graph), `research/contradictions.md`

**Hour 2 to 3: Cite-verify**
- Re-check the source for every claim
- Hallucination scan (the agent verifies its own citations)
- Cross-validate with parallel sub-agents revisiting sources
- Output: `research/citation-audit.md` (claim, source ID, verification status, alternate source)

**Hour 3 to 4: Output and self-refine**
- Serialize per format (academic, blog, brief)
- Self-Refine 1 to 2 passes, score threshold 8
- Final review: citation density, narrative flow, executive summary
- Output: `research/output-<format>.md` (final draft)

---

## Composition with Core Mythos Skills

| Core skill | Research use |
|---|---|
| [context-priming](../../core/context-priming.md) | Knowledge base plus memory plus web priming, recency window, source authority init |
| [tool-stack](../../core/tool-stack.md) | Tier selection across web search, fetch, deep crawl, scholarly APIs |
| [decomposition](../../core/decomposition.md) | Per-source sub-agent analysis (parallel), per-claim cite-verify sub-agent |
| [agent-loop](../../core/agent-loop.md) | Self-Refine at least one pass, Reflexion after every major step |
| [verification](../../core/verification.md) | Citation audit, hallucination check, contradiction tree consistency |
| [failure-recovery](../../core/failure-recovery.md) | Source unavailable, paywall, contradicting majority: change pattern |
| [memory](../../core/memory.md) | Prior research session query, post-research distillation back to notes |

---

## Output Types (Format Variants)

| Format | Length | Citation density | Audience |
|---|---|---|---|
| Academic draft | 3000 to 8000 words | 1 to 2 refs per 100 words | Peer review, methodology critic |
| Long-form blog | 1500 to 4000 words | 1 ref per 200 words | Technical reader |
| Executive brief | 500 to 1500 words | Selective top-5 refs | Decision maker |
| Decision memo | 800 to 2000 words | Position-supporting refs | Internal team |
| Slide deck | 8 to 20 slides | 1 ref per slide | Presentation |
| Internal wiki page | 80 to 150 lines | Inline links | Self or team future-self |

See [output](./output.md) for detailed templates and checklists per format.

---

## Honest Capability Boundary

**Can do:**
- Multi-source retrieval and synthesis (a domain where Mythos is strong)
- Citation discipline and hallucination minimization
- Contradiction detection and multi-hop reasoning
- Format adaptation (academic to blog to brief)
- Iterative refinement (self-critique, sub-agent peer review)

**Cannot or limited:**
- Novel research discovery (generating new hypotheses; raw reasoning ceiling, needs Mythos Preview tier)
- Primary data collection (interviews, surveys, lab experiments; human work)
- Domain-specific deep expertise (radiologist, lawyer, chemist level judgment; consultant work)
- Real-time live event tracking (live feeds, breaking news; needs continuous polling)

**Estimated effectiveness:** Multi-source literature review at 70 to 85 percent quality vs human baseline (citation density and accuracy). Novel insight generation at 20 to 40 percent (new angles from extended literature, but no breakthroughs). Format polish at 85 to 95 percent (Mythos is strong here).

---

## Anti-Patterns

- **Cherry-picking**: only sources that back the thesis. Contradiction tree is mandatory.
- **Citation inflation**: irrelevant sources padded in, density faked. Every ref must do work.
- **Hallucinated citation**: invented DOI, paper that does not exist. Cite-verify pass is mandatory.
- **Single-source synthesis**: under 3 sources is lookup, not research. The activation threshold catches this.
- **Recency ignored**: presenting an old source as current. Always flag the window.
- **Format mismatch**: executive brief to academic audience or the reverse. Audience first.

---

## Quick Checklist

Start of a research session:
1. Threshold passed (3 or more sources, citation needed, synthesis goal)?
2. Research type identified (academic, market, technical, policy, personal)?
3. Recency window decided?
4. Output format chosen?
5. Source authority order planned?

In flow:
1. Citation atom on every sentence?
2. Contradictions visible?
3. Multi-hop chain explicit?
4. Reflexion after each major step?
5. Self-Refine at least one pass done?

Detail: [retrieval](./retrieval.md), [synthesis](./synthesis.md), [cite-verify](./cite-verify.md), [output](./output.md)
