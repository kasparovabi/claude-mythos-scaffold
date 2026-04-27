---
type: skill
tags: [system/skill, mythos, research, output, format]
related:
  - "[mythos-research-mode](./mode.md)"
  - "[mythos-research-synthesis](./synthesis.md)"
  - "[mythos-research-cite-verify](./cite-verify.md)"
  - "[mythos-agent-loop](../../core/agent-loop.md)"
---

# Mythos Research Output

> Synthesis substrate stays fixed; output format flexes to the audience.

Protocol for deriving an academic draft, executive brief, blog post, decision memo, slide deck, and wiki page from the same `claims.yaml + graph.json + synthesis.md` layer. Audience function = format selection. Refine passes are also format-specific.

## Philosophy

- **Format is an audience function.** An executive brief is wasted on an academic; an 8000-word paper is wasted on a CEO. Reader profile to format mapping is mandatory and not swappable.
- **Synthesis substrate is fixed.** Claims, evidence graph, base synthesis stay constant. Only the output serialization differs: one body of knowledge, plural presentations. Do not re-research, re-format.
- **Self-Refine tunes per format.** Academic gets 3 passes (draft, peer-mimic critique, polish). Blog gets 1 pass (flow check). Executive gets 2 passes (clarity, brevity). Pass count tracks the format's tolerance for error.
- **Citation density is format-bound.** Academic peer-review demands 1 to 2 refs per 100 words. Executive takes a selective top-5 that supports decisions. Blog uses selective narrative-supporting refs. Cramming the same 50 references into every format breaks the format.

## Format Templates (6 detailed)

### 2.1 Academic Draft (3000 to 8000 words)

| Field | Rule |
|------|-------|
| Section structure | Abstract / Introduction / Related Work / Methodology / Results / Discussion / Conclusion / References |
| Citation | 1 to 2 refs per 100 words, BibTeX format, DOI preferred |
| Self-Refine | 3 passes minimum |
| Audience | Peer reviewer, methodology critic, replication-seeking reader |

**Methodology section required content:**
- Synthesis approach (claim extraction, contradiction detection)
- Cite-verify pass documentation (claim count, verified count, false-positive rate)
- Limitations explicit (sample, time window, source bias)

**Self-Refine 3 passes:**
1. **First draft.** Serialize synthesis.md into sections.
2. **Peer-review-mimic critique.** Attack with a "Reviewer 2" persona: is the methodology sound, is a hypothesis being passed off as fact, are the gaps closed?
3. **Polish.** Clean jargon, unify citation format, write the abstract last.

**Anti-pattern:** Jargon abuse (gratuitous Latin), framing a hypothesis as fact, claiming a "novel contribution" and then citing the same finding in related work.

### 2.2 Long-Form Blog (1500 to 4000 words)

| Field | Rule |
|------|-------|
| Section structure | Hook + Thesis + Evidence (3 to 5 angles) + Counter-arg + Conclusion + Further Reading |
| Citation | 1 ref per 200 words, inline link primary, footnote secondary |
| Self-Refine | 1 pass |
| Audience | Technical reader, casual deep-dive reader |

**Narrative arc rules:**
- The hook must be concrete (anecdote, number, paradox). Flat openings like "X is important" are banned.
- Thesis is 1 to 2 sentences and forms the spine of the post.
- Evidence is 3 to 5 angles. Story beats exhaustive coverage.
- Counter-arg signals honesty and is not optional.

**Self-Refine 1 pass:**
- Does the hook still pull, does the flow stutter, does the final paragraph close on the thesis?
- One pass only. Do not stretch this to 3 academic-style passes.

**Anti-pattern:** Academic-tone leak ("In this article we will explore"), citation overload (a ref on every sentence), missing counter-argument.

### 2.3 Executive Brief (500 to 1500 words)

| Field | Rule |
|------|-------|
| Section structure | TLDR (3 sentences) + 3 Key Insights (bullets) + Recommendation + Risk + Source list |
| Citation | Selective top-5, link only, no inline footnotes |
| Self-Refine | 2 passes (clarity + brevity) |
| Audience | C-suite, decision maker, time-poor reader |

**TLDR rule:** The first 3 sentences must kill the rest of the paper. The reader should be able to decide without reading anything else.

**Visual requirement:** At least 1 table, 1 to 2 charts or diagrams. A wall-of-text executive brief is a read-fail.

**Self-Refine 2 passes:**
1. **Clarity.** Does each bullet support one decision, is there jargon?
2. **Brevity.** Are we over the 1500-word ceiling, which section can be cut?

**Anti-pattern:** Detail dumping (serving a shortened academic draft as a brief), hedging language ("might", "could be", "potentially"). The executive expects certainty.

### 2.4 Decision Memo (800 to 2000 words)

| Field | Rule |
|------|-------|
| Section structure | Problem statement + Options (2 to 4 with tradeoffs) + Recommendation + Risks + Implementation outline |
| Citation | Position-supporting + opposing refs (balanced) |
| Self-Refine | 2 passes |
| Audience | Internal team, executive sponsor |

**Balanced citation rule:** Do not list only sources that back the recommended option. The **rejected** options must also carry their own supporting sources. Otherwise the memo reads as sham analysis.

**Options matrix is mandatory:**

| Option | Cost | Speed | Risk | Reversibility |
|--------|------|-------|------|---------------|
| A | ... | ... | ... | ... |
| B | ... | ... | ... | ... |

**Self-Refine 2 passes:**
1. **Recommendation defensible?** Can "why A and not B" be answered in one short sentence?
2. **Equal treatment.** Did each option get the same depth, or did A get 200 words while B got 30?

**Anti-pattern:** Pre-determined recommendation (sham options), missing implementation outline (no bridge between decision and execution).

### 2.5 Slide Deck (8 to 20 slides)

| Field | Rule |
|------|-------|
| Slide structure | Title + Agenda + Context (2 to 3) + Key Insights (3 to 5) + Recommendation + Q&A buffer |
| Citation | 1 ref per slide footer, top-source only |
| Visual hierarchy | 1 idea per slide, max 3 bullets |
| Self-Refine | 1 pass (story flow check) |
| Audience | Presentation, mixed (live + handout) |

**Visual hierarchy rules:**
- One main idea per slide. If a second idea creeps in, that is a new slide.
- Max 3 bullets, each under 7 words.
- Citation in the footer, in small type, never in the slide body.

**Q&A buffer:** The final slide repeats the main message; the next 2 to 3 slides are back-up data prepared for likely questions.

**Anti-pattern:** Text-wall slide, 7-bullet death (every slide carrying 7 bullets), paragraph in the title slide, skipping the recommendation slide.

### 2.6 Wiki Page (80 to 150 lines, vault convention)

| Field | Rule |
|------|-------|
| Section structure | Summary + Key Claims + Relations + Log |
| Citation | Inline `[[wikilink]]` to vault page, or `[[Source - X.md]]` |
| Tone | Self-curated, future-self readability |
| Self-Refine | 1 pass (cross-link density) |
| Audience | My future sessions, teammate vault users |

**Wiki-specific rules:**
- `(C)` prefix in the filename
- Frontmatter: `type`, `tags`, `related`, `created`, `updated`
- At least 4 cross-links (`[[...]]`). Orphan pages break the wiki.
- Log section: who updated, when (vault convention)

**Anti-pattern:** Temporal-only content ("This week X happened" goes stale in 3 months), thin detail (page lingers as a stub), missing cross-links (the graph stops feeding).

## Format Conversion Flow

`synthesis.md` is the shared source. Each format serializes separately:

```
synthesis.md (shared)
   |
   +-> academic.md       : full + methodology + bib
   |
   +-> blog.md           : narrative-flatten + selective ref
   |
   +-> executive.md      : top-5 ref + 3-bullet TLDR
   |
   +-> decision-memo.md  : option matrix + position rec
   |
   +-> slides.md         : graph nodes to slide hierarchy
   |
   +-> wiki.md           : condense + cross-link
```

**Conversion steps:**
1. `synthesis.md` claims pass through an audience filter
2. Citation density sharpens to the format rule
3. Section template gets filled
4. Self-Refine pass (format-specific count)
5. Tool renders the final (Pandoc, reveal.js, Obsidian)

## Self-Refine Score Card (Format-specific)

Threshold is **8/10**. Anything below triggers another pass.

| Criterion | Academic | Blog | Executive | Decision | Slide | Wiki |
|--------|----------|------|-----------|----------|-------|------|
| Section template complete | + | + | + | + | + | + |
| Citation density correct | + | + | + | + | + | + |
| Audience match | + | + | + | + | + | + |
| Anti-pattern absent | + | + | + | + | + | + |
| Methodology explicit | + | x | x | x | x | x |
| Narrative hook | x | + | x | x | x | x |
| TLDR present | x | x | + | x | x | x |
| Options balanced | x | x | x | + | x | x |
| 1 idea per slide | x | x | x | x | + | x |
| Cross-link density | x | x | x | x | x | + |
| Brevity guard | x | x | + | x | + | x |
| Counter-arg / Risk | + | + | + | + | x | x |

## Multi-Format Output (One Synthesis, Multiple Formats)

One research effort, several audiences served.

**Typical combination:**
- 1 academic draft (peer / technical channel)
- 1 executive brief (sponsor / leadership)
- 1 blog post (public / technical reader)

**Effort arithmetic:**
- Synthesis substrate (claims + graph + base): 100% of the core work
- Academic serialize: +30%
- Executive serialize: +10%
- Blog serialize: +15%

Total extra cost: about 20 to 25% on top of the synthesis, output covers 3 audiences at once. If you write each format from scratch, effort triples and content drifts (claim selection gets redone every time).

**Consistency guard:** Every format references the same `claims.yaml`, so claim numbers stay stable (`C-12`, `C-23`, etc.). Academic `[C-12]` becomes blog `(claim 12)` becomes executive "finding 12". The source remains traceable.

## Tool Stack (Output)

| Tool | Use | Format |
|------|----------|--------|
| Pandoc | `pandoc synthesis.md -o paper.pdf --bibliography=refs.bib` | Academic PDF, DOCX |
| markdown to reveal.js | `pandoc -t revealjs slides.md -o deck.html` | Slide deck |
| Obsidian preview | Native vault render | Wiki page |
| MkDocs / Hugo | Static site generator | Blog |
| LaTeX (Overleaf) | Paper finalization | Academic camera-ready |
| Markdown export | Notion / Confluence import | Executive brief, decision memo |

**BibTeX workflow:**
```bash
pandoc paper.md -o paper.pdf \
  --bibliography=refs.bib \
  --citeproc \
  --csl=ieee.csl
```

## Anti-Pattern: Output Mistakes

1. **Format-audience mismatch.** Serving an academic draft to a CEO (no TLDR, methodology section reads as noise).
2. **Citation copy-paste.** Force-feeding all 50 references into every format. Executive takes 5, academic takes 50.
3. **Skipping Self-Refine.** "First draft is good enough." Fatal for academic and executive briefs.
4. **Single-format trap.** Writing only the academic version, then hearing the executive sponsor say "I could not read it".
5. **Hedging language leaking into the executive layer.** "Could potentially might be" leaves the executive unable to decide. Brief is dead on arrival.
6. **Slide text wall.** Treating slides as a handout, reading them aloud during the talk, audience checks out.
7. **Decision memo with sham options.** Listing 4 options, giving 3 of them a paragraph each and the 4th 5 paragraphs. Pre-determined recommendation, ethics problem.
8. **Orphan wiki page.** No cross-links, the page never connects to the graph, future-self never finds it.

## Quick Checklist

**Start (after synthesis is done):**
1. Who is the audience? (Peer reviewer / CEO / blog reader / team / my own future session)
2. Which format? (Match against the table above.)
3. Section template ready?
4. Citation rule clear (density + format)?
5. How many Self-Refine passes are required?

**Finalize (after the output is written):**
1. Score card above 8/10?
2. Anti-pattern list scanned?
3. Cross-format consistency held (claim numbers stable)?
4. Rendered with the tool (Pandoc / reveal.js / Obsidian preview)?
5. Can you pitch the output to its audience in one sentence? ("This paper proves X", "This brief supports decision Y")

---

**Cross-references:**
- [mythos-research-mode](./mode.md) , research scaffold root
- [mythos-research-synthesis](./synthesis.md) , source of claims, graph, and base synthesis
- [mythos-research-cite-verify](./cite-verify.md) , citation verification, mandatory pass before output
- [mythos-agent-loop](../../core/agent-loop.md) , general agent loop scaffold; output is one loop step
