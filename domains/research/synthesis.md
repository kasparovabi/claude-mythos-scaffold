---
type: skill
tags:
  - system/skill
  - mythos
  - research
  - synthesis
  - claim-mapping
related:
  - [mode](./mode.md)
  - [retrieval](./retrieval.md)
  - [cite-verify](./cite-verify.md)
  - [agent-loop](../../core/agent-loop.md)
  - [decomposition](../../core/decomposition.md)
  - [failure-recovery](../../core/failure-recovery.md)
---

# Mythos Research Synthesis

> Multi-source claim mapping, contradiction tree, multi-hop reasoning protocol.
> Once retrieval is done, synthesis takes over with this skill.

---

## Philosophy

1. **Synthesis builds; summary shortens.** Summary is not synthesis. A summary compresses source content; synthesis discovers **relationships** across sources: supports, refutes, complements, gap.
2. **Claim atom rule.** Every synthesis sentence carries one or more claims; every claim binds to one or more source slots. Atomic binding equals traceable.
3. **Contradiction is signal.** When you find a clash, do not delete it and do not look away. Place it into a **structure**. Each reader can see the structure and form their own judgment.
4. **Multi-hop beats single-hop.** A one-sentence "X claims Y" synthesis is shallow. "X claims, Y adds nuance, Z refutes in a different context, the common ground is W" is multi-hop. This is where Mythos is strong.

---

## Flow (5 Phases)

```
Retrieval skeleton -----> Claim extraction -----> Claim graph -----> Contradiction tree -----> Multi-hop chain -----> Self-Refine
   (previous skill)                                                                                                       |
                                                                                                                          v
                                                                                                                cite-verify (next skill)
```

### Phase 1: Claim Extraction
For each source, pull 5 to 15 claims. Atomic, sourced, falsifiable.

**Claim format:**
```yaml
- id: c001
  text: "FrameworkX 4.2 production bundle is 28.4 KB gzipped for the counter benchmark"
  source: src_011
  evidence_excerpt: "dist/index.js  28,412 bytes gzipped (table 3, p. 12)"
  type: empirical  # empirical | theoretical | observational | normative
  confidence_init: 0.9  # raw read confidence, revised in cite-verify
  recency: 2026-03-14
```

**Extraction discipline:**
- A single claim from a single source often loses context. Add a context sentence.
- Subjective phrasing (for example "best", "leading") is not an atomic claim. Mark it as opinion.
- Prefer quantitative claims (numbers, ratios, dates). They are falsifiable.
- If the same claim shows up from two or more sources, write two separate entries and merge them later in the graph.

Output: `research/claims.yaml`, the full list of claims.

### Phase 2: Claim Graph
Edges between claims:

| Edge | Meaning | Example |
|---|---|---|
| `supports` | Claim B reinforces claim A (sources agree) | A: "FrameworkX bundle is 28 KB gzipped" -> B: "Independent benchmark measured 27.8 KB on the same build" |
| `refutes` | Claim B contradicts claim A | A: "SolidJS hydration is faster than React in 2026" -> B: "On the e-commerce SSR test, React 19 hydration finished 12 ms earlier" |
| `complements` | Same domain, different angle | A: "FrameworkX runtime is 4.5 KB" -> B: "FrameworkX uses 28% less heap on the TodoMVC stress test" |
| `prerequisite` | A must hold for B to be possible | A: "Compiler-only mode is enabled" -> B: "Reactive primitives compile away to direct DOM updates" |
| `clarifies` | A is general, B is the detail | A: "FrameworkX has small bundles" -> B: "Counter demo gzipped is 28.4 KB on v4.2" |
| `temporal` | A first, B after (time order) | A: "v4.0 shipped a runtime-heavy reactivity core" -> B: "v4.2 moved most of it to compile time" |

**Graph:**
```
research/graph.json
{
  "nodes": [{"id": "c001", "text": "..."}, ...],
  "edges": [
    {"from": "c001", "to": "c003", "type": "supports", "strength": 0.8},
    {"from": "c002", "to": "c005", "type": "refutes", "strength": 0.6}
  ]
}
```

Visualization is optional (mermaid or graphviz, handled in the output skill). For synthesis itself, the JSON is enough.

### Phase 3: Contradiction Tree
Isolate and group the refute edges:

```markdown
## Contradiction T1: FrameworkX vs React 19 hydration time on SSR

- A: src_002 (FrameworkX core team blog) "FrameworkX hydrates the e-commerce demo in 38 ms, 22% faster than React 19"
- B: src_005 (independent benchmark, web.dev 2026-02) "On the same hardware profile, React 19 hydration finished in 41 ms vs FrameworkX 53 ms"
- C: src_009 (production report from a mid-size e-commerce team) "Hydration variance is high under real network conditions; both frameworks land within 10 ms of each other"

**Resolution candidates:**
1. Test surface split: the core team benchmark uses a static product list, the independent test uses a hydrated cart with live pricing. Different hydration cost.
2. Temporal: FrameworkX 4.1 (used by src_002) shipped before the React 19 hydration patch. src_005 tests the post-patch React build.
3. Methodology: src_002 is a lab synthetic test, src_005 is closer to production with throttled CPU.

**Reader judgment:** every resolution is sourced. Explain the methodology section. Do not pretend there is a single right answer.
```

Output: `research/contradictions.md`. Each contradiction tree gets its own section.

### Phase 4: Multi-Hop Reasoning Chain
Instead of a single-sentence claim, build a chain:

```
Single-hop (shallow):
  "FrameworkX bundles got smaller in 2026."

Multi-hop (synthesis):
  "FrameworkX 4.2 (src_011) cut its runtime to 4.5 KB by moving reactive primitives
  to compile time, which the core team measured as a 22% hydration win on the
  static product demo (src_002, 2026-01). The independent web.dev benchmark
  (src_005, 2026-02) puts the same scenario at parity with React 19 once the cart
  is hydrated under throttled CPU. A production report (src_009): under real
  network variance, the hydration gap drops below noise floor. The bundle-size
  delta (FrameworkX 28 KB vs React 45 KB gzipped) holds across all three sources;
  the runtime hydration delta is workload dependent. Conclusion: bundle is the
  durable axis to compare on, hydration is not."
```

**Multi-hop discipline:**
- Every hop announces itself at the start of the sentence (X claims, Y is a different angle, Z gives context).
- A typical chain is 3 to 5 hops. Two is shallow, seven plus loses the reader.
- Source IDs go inline or as a paragraph-end ref list.
- The final synthesis sentence adds value: it names the gap or the novel angle.

Output: `research/synthesis.md`. Multi-hop paragraphs under section headings.

### Phase 5: Self-Refine (at least one pass)
After the draft synthesis, run a critique pass. Score your own output 0 to 10:

| Criterion | Score (0-10) | Threshold |
|---|---|---|
| Claim density (no unsourced sentence) | | 8 |
| Contradiction visibility | | 8 |
| Multi-hop depth (avg hop count >= 3) | | 7 |
| Recency window respected | | 9 |
| Authority balance (no Tier 5 only claims) | | 8 |
| Reading flow (transitions, narrative) | | 7 |
| Novel insight (not a summary, adds value) | | 6 |
| AI slop check (generic, vague phrasing) | | 9 |

Any criterion under threshold gets a revision. Minimum 1 revision pass, maximum 3.

---

## Sub-Agent Delegation (Synthesis-Specific)

| Sub-agent | When | Brief |
|---|---|---|
| **General-purpose** | 50+ claims in the synthesis, parallel graph build | "From sources src_007, src_008, src_009 extract claims. Output YAML with claim, source, excerpt, type, confidence." |
| **Code-reviewer** | Technical synthesis where code excerpts arrive as claims | "Is this code excerpt claim consistent: <claim text> against source <code>?" |
| **Plan agent** | Synthesis output planning (structure depends on output format) | "From these 47 claims and 8 contradictions, draft an 800 word executive brief." |

Detail: [decomposition](../../core/decomposition.md)

Only the **synthesis summary** from the sub-agent comes back to the main context. Verbose claim YAMLs stay inside the sub-agent context, get written to disk, and the main agent receives a JSON summary.

---

## Bias Control (Synthesis-Specific)

| Bias | Symptom | Counter-practice |
|---|---|---|
| **Confirmation bias** | The graph only contains claims that support the thesis | Check that `refutes` edge count >= 0.2 x `supports` edge count |
| **Cherry-picking** | Only one claim per source, the rest forgotten | Look at per-source claim count distribution. Is it lopsided? |
| **Recency bias** | Disproportionate weight on the newest source | Trust score recency factor balanced, not 2026-only |
| **Authority bias** | "Anthropic said it" treated as undeletable truth | Authority score exists, but a refute edge is allowed. Even peer-reviewed work can clash. |
| **Survivorship bias** | No failed implementations, only success cases | Actively hunt for negative results and failure post-mortems |
| **Anchoring** | The first source claim becomes the spine of the synthesis | Start the skeleton multi-source. Randomize order. |

After the synthesis pass, run a **bias self-audit**: a one-line evaluation against each of the 6 biases. Save it to `research/bias-audit.md`.

---

## Citation Graph (Feynman Pattern)

The Feynman AI 2026 approach: **the agent traverses the citation chain itself** (paper A cites B, B cites C, so A -> B -> C).

In synthesis this pattern becomes:
```
Forward citation: who cites source X afterwards? (new viewpoint, refute, validation)
Backward citation: who does source X cite? (foundational papers)
```

Tools:
- Semantic Scholar API (free), paper ID to forward and backward citations
- Google Scholar manual lookup
- arXiv direct paper reference parsing

Output: `research/citation-chain.md`. A citation map of the anchor sources, marking which claims are canonical and which are still controversial.

---

## Output Hooks (For the Output Skill)

When synthesis ends, three artifacts are ready, format-independent:

1. **`research/synthesis.md`** the full draft, sectioned, with multi-hop paragraphs
2. **`research/claims.yaml`** the atomic claim list (programmatic access)
3. **`research/graph.json`** the claim graph (visualization, navigation)

The output skill serializes these three into the target format:
- Academic draft: synthesis.md plus LaTeX BibTeX
- Blog post: synthesis.md flattened into narrative with inline links
- Executive brief: claims.yaml top-N selective plus a one-paragraph summary
- Slide deck: graph.json node titles plus key claims per slide

Detail: [output](./output.md)

---

## Mythos Pattern: Stuck, Change Pattern

If synthesis depth has not moved for 3 turns:
- **Re-criticize the sources.** Too many low-trust ones? Loop back to retrieval (extra Tier 2).
- **Claim formulation is too general.** Recheck atomicity, split into sub-claims.
- **Graph edges are thin.** Are you using `complements` and `clarifies`, or are you only working with supports and refutes (which keeps things shallow)?
- **Sub-agent peer review.** Spin up a fresh-context agent and have it critique the synthesis draft.

Detail: [failure-recovery](../../core/failure-recovery.md)

---

## Anti-Pattern: Synthesis Mistakes

- **List of summaries.** A separate paragraph per source, no links between them. That is neither summary nor synthesis.
- **"As X says, Y" chain.** A direct-quote shower with no synthesis contribution of your own.
- **Erasing contradictions.** "Ignore B because A is stronger." Methodology violation.
- **Multi-hop chain that ends at hop 2.** Depth is missing, the result is shallow.
- **Skipping the bias audit.** Without a confirmation bias self-check, you ship a cherry-picked synthesis.
- **Zero rounds of Self-Refine.** First draft is 7 out of 10, you ship to the user, quality drops.
- **Synthesis without quantitative claims.** "X is good in some cases, bad in others" is not falsifiable, not a claim.

---

## Quick Checklist

At synthesis start:
1. Is the retrieval skeleton ready (claim slots plus source candidates)?
2. Per-claim source assignment done?
3. Graph edge taxonomy chosen (default 6 types)?
4. Output format known (synthesis depth tunes to it)?

In progress:
1. Is claim atomicity holding in every sentence?
2. Is the contradiction tree visible?
3. Multi-hop average hop >= 3?
4. Bias audit passed all 6 items?
5. Self-Refine run at least once?

When synthesis is done: cite-verify pass: [cite-verify](./cite-verify.md)
