# Distillation curation

How mined working patterns become directives in `core/fable-distilled.md`. The
mining step (watching real Fable/Mythos sessions and extracting candidate
behaviors) happens elsewhere and privately. This document covers only the
curation gate that stands between raw candidates and the public repo.

## Boundary

- **Input** (private, never committed): `~/.claude/mythos/distill/candidates.md`,
  a running list of mined episodes. Each candidate is a short observed behavior
  plus the transcript excerpt it came from.
- **Output** (public): edits to `core/fable-distilled.md`, sections 1-4
  (decomposition, verification, next-action, explicit triggers).
- Candidate files and their source transcripts stay out of the repo. Nothing
  under `~/.claude/mythos/distill/` or any run transcript is ever copied into a
  tracked file. Directives are rewritten from scratch as general imperatives;
  transcript text, file paths, and session-specific detail never appear verbatim.

## Cadence

Manual, roughly monthly, or whenever candidates accumulate past a handful.
There is no automation and no schedule hook; curation is a deliberate reading
pass, not a pipeline.

## Curation session template

1. **Read the candidates.** Open `~/.claude/mythos/distill/candidates.md`. For
   each entry decide: does this generalize beyond the session it came from, to
   any Opus-class model on any task?
2. **Accept or reject, one line each.**
   - Accept: a behavior that would improve an unseen task and can be stated as a
     single imperative ("verify at the altitude the user consumes").
   - Reject: session-specific, tool-specific, already covered, or too vague to
     act on. Record the candidate with a one-word reason (`duplicate`,
     `specific`, `vague`, `covered`, `wrong`).
3. **Merge accepted patterns as directives.** Fold each into the right section
   of `core/fable-distilled.md` as a single imperative bullet. Prefer editing an
   existing bullet over adding a near-duplicate. Match the file's voice:
   second-person imperative, concrete, no hedging. Never paste the source text.
4. **Dedupe.** After merging, reread the touched section. Collapse bullets that
   now say the same thing. The file earns its keep by being short.
5. **Changelog.** Add a dated entry noting what changed and why (one or two
   lines). Keep rejected candidates listed with their one-word reason so the
   same episode is not relitigated next month.
6. **Regression check.** Run the eval harness to confirm the edit did not make
   behavior worse:

   ```
   eval/mythos-eval run
   eval/mythos-eval report
   ```

   Compare mythos-arm metrics against the previous report. A directive that
   raises `premature_qs` or drops `verif_before_done` is a regression; revert or
   reword it.

## What never enters the public repo

- `candidates.md` and any mined episode file.
- Raw run transcripts (`run.jsonl`, `run.err`) and copied workdirs under
  `~/.claude/mythos/eval-data/`.
- Personal paths, names, or any content lifted verbatim from a session.
