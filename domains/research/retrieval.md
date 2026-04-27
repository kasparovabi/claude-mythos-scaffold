---
type: skill
tags:
  - system/skill
  - mythos
  - research
  - retrieval
  - rag
related:
  - "[mode](./mode.md)"
  - "[tool-stack](../../core/tool-stack.md)"
  - "[context-priming](../../core/context-priming.md)"
  - "[memory](../../core/memory.md)"
---

# Mythos Research Retrieval

> Multi-source retrieval protocol across local notes, memory layers, academic databases, web, and social.
> Source authority ordering, Adaptive RAG, citation skeleton construction.

---

## Philosophy

1. **Source-aware retrieval beats volume.** Five quality sources outrank fifty SEO-spam results. Authority filtering is the first cut.
2. **Local first.** Local knowledge and memory layers are zero-cost and instant. Web comes second. This order is context budget discipline.
3. **Adaptive RAG.** Classify the question type first, then pick the retrieval path. A naive "one pipeline fits all" approach is expensive and noisy.
4. **Citation skeleton first.** Build the citation anchor structure before retrieval ends, mapping which claim goes to which source slot. The synthesis phase starts from this skeleton.

---

## Source Tiers

### Tier 1: Local Authority (zero-cost, instant)

| Source | What | Trigger |
|---|---|---|
| Local knowledge index | Distilled local concepts | Start of every research session |
| Concept or entity notes | Specific concept depth | Drilled from the index |
| Memory query (L0+L1) | Prior session insight | Task domain known (~170 tok) |
| Memory drawer expand | Verbatim conversation snippet | "Have we discussed this?" hit, drill in |
| Session history archive | Raw conversation fallback | When memory layer is empty |
| Quick capture and journal notes | Personal context | Background priming |

### Tier 2: Canonical External (low-cost, high-trust)

| Source | What | Tool |
|---|---|---|
| Official documentation | Anthropic docs, MDN, language docs, RFC, IETF | WebFetch direct URL |
| Academic preprint | arXiv, SSRN, OSF | WebFetch + arXiv API where available |
| Peer-reviewed | Google Scholar, Semantic Scholar API | WebSearch + WebFetch DOI |
| Standards body | W3C, ISO, IEEE, NIST | WebFetch direct |
| Government or regulator | EU, SEC, FDA, EBA portals | WebFetch direct |

### Tier 3: Curated Secondary (medium trust)

| Source | What | Tool |
|---|---|---|
| Quality technical blog | Engineering blogs (Stripe, Cloudflare, GitHub, Vercel), Substacks | WebFetch |
| White paper | Bain, McKinsey, Gartner, Forrester | WebFetch (paywall risk) |
| Industry analyst | Stratechery, Benedict Evans, a16z research | WebFetch |
| GitHub repo + README | Project source of truth | WebFetch + gh CLI |

### Tier 4: Forum and Community (low to medium trust, signal-rich)

| Source | What | Tool |
|---|---|---|
| StackOverflow | Accepted answer, score above 50 | WebSearch site:stackoverflow.com |
| Reddit (specific subs) | r/MachineLearning, r/programming, r/cscareerquestions | WebSearch site:reddit.com |
| HN comments | Sergeant-style technical depth | WebFetch HN thread |
| Discord or Slack archive | Project-specific community | Usually unindexed, skip |
| GitHub issue or discussion | Maintainer and power-user signal | gh CLI or WebFetch |

### Tier 5: Social and Real-Time (noisy, signal extraction needed)

| Source | What | Tool |
|---|---|---|
| Twitter/X | Author quality is critical, low-trust default | No Twitter API, use WebSearch |
| LinkedIn posts | Executive narrative, marketing-heavy | WebSearch site:linkedin.com |
| News (Reuters, AP, FT, NYT) | Breaking events, recency | WebSearch with news domain filter |

### Tier 6: Deep Research Tools (heavy, dedicated)

| Tool | What for |
|---|---|
| **NotebookLM** (`mcp__notebooklm`) | Multi-document synthesis, podcast or mind-map output |
| **Firecrawl** (`mcp__firecrawl_crawl`) | Site-wide deep extraction |
| **Firecrawl** (`firecrawl_extract`) | Structured schema from a URL |
| **Elicit, Consensus, Scite** | Academic AI agents (external, optional API) |

---

## Adaptive RAG: Question Classification

Classify every research question **before** picking a retrieval pipeline.

| Class | Example | Retrieval pipeline | Cost |
|---|---|---|---|
| **Single-fact lookup** | "How many tokens in the GPT-4o context window?" | Tier 2 (canonical doc), single fetch | Low |
| **Single-domain query** | "What is the JWT algorithm confusion attack?" | Tier 2 + 3 (RFC + blog explainer) | Low to medium |
| **Multi-hop synthesis** | "WebAssembly module load times in 2026 across runtimes, weaknesses?" | Tiers 1-5 in parallel + synthesis | Medium to high |
| **Temporal or current** | "What did OpenAI release in March 2026?" | Tier 5 (news) + Tier 2 (official blog) | Low |
| **Comparative** | "LangGraph vs CrewAI vs AutoGen, production scaling comparison" | Tiers 2-4 per framework + synthesis | Medium to high |
| **Personal or historical** | "How did we plan this project six months ago?" | Tier 1 (memory + local index) | Very low |
| **Vague scope** | "What is being studied in AI safety?" | Threshold test first, narrow scope, then Tiers 2-3 | Medium |

---

## Retrieval Flow (4 Phases)

### Phase 1: Scope Definition
```
Task parse:
- Question class (per the table above)
- Domain (tech / academic / market / policy / personal)
- Recency window (6 months / 2 years / historical OK?)
- Output format (from research output spec)
- Citation density target (1 ref/100w / 1 ref/200w / executive selective)
```

Output: `research/scope.md` (4-6 line brief).

### Phase 2: Local Sweep (zero-cost)
In parallel:
- Local knowledge index query
- Memory query L0+L1 (~170 tok)
- Session history archive: filtered grep (last N days, domain)
- Project rule files relevant to the domain

Output: `research/local-context.md`. What we already know, what is missing.

### Phase 3: External Retrieval (parallel batch)
Pipeline picks based on question class. Use parallel sub-agents or multi-tool calls in a single message:

```
WebSearch query 1 (canonical angle)
WebSearch query 2 (controversy or critique angle)
WebSearch query 3 (recency angle, "X 2026")
WebFetch top 3-5 canonical URLs (Tier 2)
WebFetch 2-3 secondary blogs or whitepapers (Tier 3)
Firecrawl 1 site deep crawl (only if multi-page extraction is needed)
```

Output: `research/raw/sources.jsonl`. Each line:
```json
{"id":"src_001","url":"...","tier":2,"title":"...","author":"...","date":"2026-04-08","trust_score":0.9,"recency_in_window":true,"raw_content_path":"research/raw/src_001.md"}
```

### Phase 4: Citation Skeleton
Do not jump to synthesis before retrieval ends. Build the skeleton first:

```markdown
# Research Skeleton: <topic>

## Claim slots

### Claim 1: <topic.subarea1>
- Source candidates: [src_002, src_005, src_011]
- Evidence type: empirical / theoretical / observational
- Confidence init: medium

### Claim 2: <topic.subarea2>
- Source candidates: [src_003, src_007]
- Contradiction risk: high (src_003 vs src_007)
...

## Gaps (sub-areas with no source)
- Subarea X: no source found, additional search needed?
- Subarea Y: only low-trust sources (Tier 5), retry Tiers 2-3
```

Output: `research/skeleton.md`. The synthesis phase starts from this file.

---

## Source Authority Score

Score every source automatically (`research/sources-rank.md`):

```
trust_score = (
    0.4 * tier_score (Tier 1 = 1.0, Tier 5 = 0.3)
    + 0.2 * recency_score (inside window = 1.0, outside = 0.3 to 0.7)
    + 0.2 * author_score (institution / expert / anonymous)
    + 0.1 * citation_count (normalized when available)
    + 0.1 * cross_reference_count (how many other sources cite this one)
)
```

Sources scoring below 0.5 are flagged "low confidence" and noted explicitly when used in output.

---

## Tool Cascade Recipes

### Recipe: Academic literature review
```
1. Local index query, find existing concept notes
2. WebSearch "topic 2026 systematic review" + "topic survey paper"
3. arXiv search via WebFetch (https://arxiv.org/search/?query=...)
4. Google Scholar via WebSearch + WebFetch DOI
5. Top 5 papers, WebFetch full text (PDF parse: abstract + intro + conclusion)
6. Backward citation: top 10 from references of those top 5
7. Forward citation: which newer papers cite the top 5 (Semantic Scholar API)
```

### Recipe: Market and competitive intel
```
1. Local project state for the relevant project
2. WebSearch competitor name + "raised" / "launched" / "pricing 2026"
3. Crunchbase, Pitchbook free tier (when available)
4. Top 3 competitor official sites, WebFetch (pricing, features, blog)
5. Twitter and LinkedIn search: competitor founders + key product mentions
6. WebSearch recent (3 months) on Reuters, FT, or NewsAPI
7. Industry analyst WebFetch (Gartner or Forrester quadrant if available)
```

### Recipe: Technical decision support (e.g. framework comparison)
```
1. Local wiki + memory layer prior decisions
2. Per framework: official docs WebFetch, GitHub README, recent release notes
3. WebSearch "framework_A vs framework_B 2026 production"
4. HN search + GitHub issues (pain-point signal)
5. Reddit r/<lang> last 3 months
6. StackOverflow accepted answers (score-filtered)
7. Comparative blog post Tier 3 (Stripe, Vercel, GitHub eng blog)
```

### Recipe: Policy and regulatory
```
1. Official regulator portal (EU CELEX, SEC EDGAR, NIST)
2. Active law text (full text WebFetch)
3. Top 3 law firm white papers (interpretation)
4. Recent government press releases
5. Industry comment letters (regulator portal archive)
6. Academic legal review (SSRN, HeinOnline)
```

---

## Knowledge Cutoff Discipline (Research-Specific)

Cutoff: January 2026 (Opus 4.7).

For any source past the cutoff:
- WebSearch verification is mandatory
- "Memory says X exists" needs grep or fetch confirmation
- Source metadata carries a `cutoff_check: passed/failed` flag

For date-sensitive claims, stamp with **YYYY-MM-DD**. Use "released 2025-09-12" instead of "released in 2025".

Detail: [context-priming](../../core/context-priming.md) cutoff section.

---

## Context Budget (Retrieval Phase)

Opus 4.7 has a 1M window. Retrieval allocation:

| Slice | Target | If exceeded |
|---|---|---|
| Local sweep (local index + memory L0+L1) | 2 to 5 percent (~20-50K tok) | Filtered read, Grep for relevant paragraphs |
| External retrieval (raw content) | 20 to 30 percent (~200-300K tok) | Sub-agent delegate, verbose stays in sub, summary returns |
| Skeleton + index | 1 to 2 percent (~10-20K tok) | Compact structure |

Total retrieval lands at 25 to 35 percent, leaving 30 to 40 percent buffer for synthesis.

**Sub-agent delegation rules:**
- Source above 50K tokens, delegate fetch and extract to a sub-agent
- Sub-agent returns "key claims + cite" only, raw text stays in the sub
- Detail: [decomposition](../../core/decomposition.md)

---

## Knowledge Capture After Research

At the end of a research session, capture valuable findings into the local knowledge base:
- New concept, write a concept note if missing
- New entity (person, organization, tool), write an entity note
- Cross-reference: link the new note from related pages
- Append a one-line entry to the knowledge log: date, topic, links

The knowledge ingest workflow already runs this protocol. Pass the research output as the source document.

---

## Anti-Patterns: Retrieval Mistakes

- **Web first, local skip.** If distilled knowledge already exists locally, do not run ten web fetches.
- **Single-query reliance.** One WebSearch query, top 3 links, high bias. Run 3 to 5 parallel angles.
- **Ignoring the authority order.** Do not weigh a Reddit comment equal to a peer-reviewed paper.
- **Recency mismatch.** Do not present a 2018 paper as 2026 current state.
- **Skipping the skeleton.** Going straight to synthesis loses claim-source mapping.
- **Single-shot claim from a low-trust source.** A Twitter post is not evidence. Cross-verify.
- **Trusting memory.** "I remember this paper said..." Fetch and confirm.

---

## Quick Checklist

Start of retrieval:
1. Question class identified (Adaptive RAG)?
2. Recency window decided?
3. Local sweep done first (local index + memory)?
4. Source authority order planned?

During the run:
1. Trust score computed for every source?
2. Citation skeleton built before synthesis?
3. Cross-reference checked (does source X cite source Y)?
4. Web verification on for any post-cutoff claim?

When retrieval ends, the skeleton is in hand. Move to synthesis: [synthesis](./synthesis.md)
