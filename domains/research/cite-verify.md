---
type: skill
tags: [system/skill, mythos, research, cite-verify, hallucination-check]
related: ["[mode](./mode.md)", "[synthesis](./synthesis.md)", "[output](./output.md)", "[verification](../../core/verification.md)"]
---

# Mythos Research Cite-Verify

> Citation atom verification. After synthesis, every claim gets traced back to its source for a reality check. Treat hallucination as the bad-faith default; every citation is suspect until proven.

## Philosophy

- **Citations must be verifiable.** If a claim cannot be traced back to a source, it is a hypothesis, not a claim. No excerpt match means no source.
- **Hallucination is the bad-faith default.** Do not trust LLM-generated citations on first sight. Real paper, real author, real year, real excerpt. All four must hold. Three out of four means the citation is rotten.
- **Multi-tier validation.** A single check is not enough: title search, DOI fetch, author cross-check, citation graph, and sub-agent peer review. A crack in any tier means the claim gets revised.
- **Agent-as-peer-reviewer (Feynman 2026 pattern).** The AI agent verifies its own citations. Hand a draft and a claim list to an independent sub-agent in fresh context, then ask it to return per-claim answers to "is the source real, does the excerpt match?" This is cross-review, not self-review.

## Verification Flow (4 Phases)

### Phase 1: Per-Claim Source Re-Check

Physically return to the source text for every claim. Break the paraphrase chain that builds up during synthesis and go back to the original.

- Isolate the claim: "X is Z because of Y [Source A]"
- Re-fetch Source A (fresh, not cached)
- Compare the excerpt against the exact wording in the source
- If paraphrased, run a semantic equivalence test. Is the meaning preserved, exaggerated, or inverted?
- If the source mentions it in multiple places, gather them all. Contradictions mean the claim is ambiguous.

| Re-check Status | Meaning | Action |
|---|---|---|
| Exact match | Excerpt is verbatim | Pass |
| Semantic match | Meaning preserved, wording different | Pass (add paraphrase note) |
| Weak match | Theme is similar, claim is strengthened | Weaken the claim |
| Mismatch | Source does not support the claim | Remove the claim |
| Source unreachable | Source cannot be fetched | Mark claim as "unverified" |

### Phase 2: Hallucination Scan

Sweep for fabrication patterns systematically. Apply this phase to the entire citation list at once, not claim-by-claim.

- Resolve every DOI through doi.org/{DOI}. A 404 means vapor.
- Fetch every arXiv ID through arxiv.org/abs/{ID}. A 404 means vapor.
- Cross-check the author + year + title combination on Google Scholar or Semantic Scholar.
- Match every quote against the full text of the source. Missing means fabrication.
- Two different author attributions for the same paper means a composite suspect.
- For paywalled papers, stay within the abstract. Anything beyond is paywall guessing.

### Phase 3: Forward and Backward Citation Chain

Feynman pattern: cross-validate using the citation graph around the source. A single paper can lie. A citation graph has a hard time lying.

- **Backward chain:** pull the papers the source cites (its references). Is the basis of the claim in that list?
- **Forward chain:** pull the papers that cite the source. Do later works repeat the claim, refute it, or qualify it?
- A retraction or correction in the forward chain critically weakens the claim.
- Anomalously low citation count (years passed, 0 to 3 cites) means the claim is niche, not consensus.

### Phase 4: Sub-Agent Peer Review

Hand a draft and a claim list to an independent general-purpose agent in fresh context. The agent returns independent verification per claim. This is cross-review, not self-review. The verdict is free of the original agent's context bias.

- Give the sub-agent only the draft and the claim list. Do not include the intermediate arguments from synthesis.
- Standardize the questions per claim: "Is the source real, does the excerpt match, is there an alternative source?"
- After the sub-agent returns, log every discrepancy. The sub-agent may be wrong, but every discrepancy is a red flag.
- If the sub-agent and the original agent disagree, adjudicate with a third agent or a manual call.

## Hallucination Pattern Taxonomy

| Pattern | Description | Detection |
|---|---|---|
| Fake DOI | DOI format is valid but points to a different paper | doi.org resolver + title cross-check |
| Author misattribution | Paper is real, author is wrong (co-author confusion) | Semantic Scholar author list match |
| Year drift | Paper is real, year is off by 1 to 2 | Publication metadata fetch |
| Quote fabrication | Excerpt does not appear in the source | Phrase match within full text |
| Composite citation | Stitched from two papers, belongs to neither | Isolate which paper the excerpt is in |
| Vapor citation | No source exists, fully fabricated | No trace on DOI, arXiv, or Scholar |
| Paywall guessing | Citing beyond the abstract on a paywalled paper | Flag any claim beyond abstract content |
| Title drift | Paper is real, title is reformulated incorrectly | Exact title search + fuzzy match |
| Phantom edition | Year or edition is invented (e.g. "3rd edition 2024" when 2nd is current) | Publisher metadata check |

## Tool Stack (Cite-Verify)

| Tool | Use | Limit |
|---|---|---|
| WebSearch | Title + author + year re-search | Search engine bias, top 10 results |
| WebFetch | Direct DOI/arXiv URL fetch + abstract/full-text match | Paywall, robots.txt, JS-render gaps |
| Semantic Scholar API | Forward/backward citation graph, author disambiguation | Rate limits, CS-biased coverage |
| Google Scholar | Citation count, alternative year/edition detection | Hard to automate, manual queries |
| Crossref API | Authoritative DOI metadata lookup | Only papers with DOIs |
| arXiv API | Preprint version + revision history | arXiv scope only |
| OpenAlex | Open scholarly graph, citation network | New API, edge case gaps |

## Sub-Agent Peer Review Pattern

Hand the independent general-purpose agent this brief in fresh context:

```
Task: Verify the citations in the research draft below.

Input:
- draft.md (full text)
- claims.json (per claim: id, statement, source ref, excerpt)

Return per claim:
{
  "claim_id": "C-007",
  "source_real": true/false,
  "excerpt_match": "exact" | "semantic" | "weak" | "none",
  "doi_resolves": true/false,
  "author_correct": true/false,
  "year_correct": true/false,
  "alternative_source": "<DOI or null>",
  "confidence": 0.0-1.0,
  "notes": "<discrepancy detail>"
}

Rules:
- The sub-agent runs its own web search and fetch. Do not trust the draft.
- For excerpt match, fetch the original source text.
- If a discrepancy is found, explain why.
- For citations you cannot verify, return confidence 0.0. Do not guess.
```

The defining feature: the sub-agent **never sees the synthesis process**. Only the draft and the claim list. This keeps the original agent's paraphrase bias from leaking into the sub-agent.

## Confidence Scoring (Post-Verify)

Every claim gets a final confidence after cite-verify. Confidence measures the verification level of the citation, not the quality of the claim.

| Confidence | Meaning | Action |
|---|---|---|
| 1.0 | Source verified, exact excerpt, author/year correct, within recency window | Claim stays as is |
| 0.7 | Source exists, semantic excerpt match, author/year correct | Claim stays, add "paraphrase" note |
| 0.4 | Source exists but year is off by 1 to 2 or co-author confusion | Mark "weak citation" or seek an alternative source |
| 0.2 | Source exists but excerpt mismatch, only theme overlaps | Rewrite with "Hypothesis" prefix |
| 0.0 | No source found, paper not located, or vapor citation | Remove claim or include as "unsourced hypothesis" |

Claims with confidence below 0.4 cannot reach final output with their citation intact. Either remove, rewrite with a hypothesis prefix, or replace with an alternative source.

## Cite-Verify Audit Report Format

Every research output ships with `research/citation-audit.md`. Template:

```markdown
# Citation Audit, <Research Topic>

**Date:** YYYY-MM-DD
**Total claims:** N
**Verified (1.0):** A
**Semantic (0.7):** B
**Weak (0.4):** C
**Hypothesis (0.2):** D
**Removed (0.0):** E

## Per-Claim Audit

### C-001
- **Statement:** "X is Y because Z"
- **Source ref:** Smith et al. 2024, DOI 10.xxx/yyy
- **Verification status:** verified | semantic | weak | hypothesis | removed
- **Confidence:** 1.0
- **Excerpt match:** exact
- **DOI resolves:** yes
- **Author correct:** yes
- **Year correct:** yes
- **Alternative source:** none
- **Sub-agent verdict:** match (confidence 1.0)
- **Notes:** none

### C-002
...

## Hallucination Findings

- **Vapor citations:** [list]
- **Year drifts:** [list]
- **Quote fabrications:** [list]
- **Composite citations:** [list]

## Methodology Notes

- Tools used: WebFetch, Semantic Scholar API, sub-agent peer review
- Sub-agent model: <model name>
- Adjudication needed: <claim ids>
```

The audit report is a mandatory artifact. It ships with the output. Do not lose it.

## Anti-Patterns: Cite-Verify Mistakes

- **Random sample only.** Saying "I checked 1 of 10 citations, the rest are probably fine" opens the door to hallucination. Every claim gets re-checked. A sample is not enough.
- **"Looks plausible" pass.** Plausibility is not verification. Either the citation exists and the source actually says it, or it does not.
- **Skipping sub-agent peer review.** Self-review is biased. Parallel verification by a sub-agent in fresh context is mandatory. "No time" is not a valid excuse.
- **Loose excerpt matching.** Semantic equivalence can be tested, but "probably saying the same thing" does not pass. Keep the matching protocol explicit.
- **Treating hallucination as normal in low-trust sources.** If a blog post hallucinated, do not keep citing it. Even tier-3 sources need real citations.
- **Confidence inflation.** Do not give a sketchy citation 0.7 to avoid 0.4. In borderline cases, round confidence down.
- **Treating the audit report as optional.** No `citation-audit.md` means cite-verify did not happen.

## Quick Checklist

**Setup (before phase 0):**
- [ ] Final draft from synthesis is ready
- [ ] Every claim is tagged with a claim-id
- [ ] Each claim is bound to a source ref
- [ ] Citation list is deduplicated
- [ ] Fresh sub-agent context is ready for peer review

**During the run:**
- [ ] Phase 1 ran on every claim (full sweep, not sample)
- [ ] Phase 2 hallucination scan ran across the whole citation list
- [ ] Phase 3 citation graph ran at least on tier-1 sources
- [ ] Sub-agent peer review returned and discrepancies are logged
- [ ] Claims below 0.4 confidence are revised or removed
- [ ] `citation-audit.md` is produced
- [ ] Every citation in the final draft maps to a claim_id in the audit report

Related: [mode](./mode.md), [synthesis](./synthesis.md), [output](./output.md), [verification](../../core/verification.md)
