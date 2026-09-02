---
name: paper-writing
description: "Use when writing or revising a scientific paper."
version: 1.0.0
author: curator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [paper, latex, tectonic, reviews, submission]
    related_skills: [gauge-gnn-experiments, report-writing, arxiv-latex-sources]
---

# Scientific paper writing and review integration

## When to Use

Any session that drafts, revises, or prepares a scientific paper for
submission: integrating an external-reviewer round (opus/Sol/claude-gauge
reviews), fixing stale numbers or figures after a table edit, auditing
citations, restructuring for a page limit, or adding the mandatory
submission checklist. Load BEFORE editing main.tex — the verification
habits below have each caught a reviewer-visible error at least once.

Class-level workflow for drafting, revising, and shipping a LaTeX paper
(workshop/conference, e.g. NeurIPS-style) with an external-reviewer loop
(opus/Sol/claude-gauge-style reviews relayed by the user). Covers the
toolchain, the verification habits that keep reviewers from finding
carelessness, the user's style rules, and the venue/submission structure.
Session-specific detail for the gauge paper lives in
`references/gauge-paper.md`.

## The review-round loop (the core discipline)

1. Every review round: fix the numbers/figures/claims FIRST, then
   proofread, then recompile, then commit. Expect 2-4 rounds.
2. After ANY table/caption edit, run a STALE-NUMBER SWEEP over the whole
   paper: grep the prose for the old values (each changed table cell is a
   candidate) — the prose/tabular mismatch is the first thing a reviewer
   checks and usually signals a deeper claim problem. Seen live three
   times in one session: the ladder's old accs, a "0.10 apart" magnitude
   that became 0.05 after a row correction, and a fix-chain "1.55" that
   survived in the text after the table's max became 1.35.
3. Verify claims against the CODE, not just the tables: "the readout is a
   complex linear map" was false — the head is a real linear map on the
   realified features (a general real-linear map is a strict superset of
   the complex-linear A/-B/B/A form; it is covariant and MORE expressive,
   which STRENGTHENS the complexification decomposition). Grep the model
   code for every architectural claim the paper makes; correct the paper
   to match the code, and sweep the appendix for the same stale claim
   (the appendix repeated the wrong "complex linear head" — a fix in one
   section must propagate everywhere).
4. Figure/data verification after regeneration: PIL non-white fraction
   (empty-figure check), AND check the numbers the figure PLOTS against
   the table (a reviewer cross-checks the first thing in the caption).
   Panel-level: sweep panels must exclude sibling variants sharing the
   name prefix (the U(1)^k run plotted into the K-sweep as a spurious
   0.473 dip — `if "_u1k" in f: continue`), and load filters must pin the
   EXACT config (stack_layers, seeds, era suffix), not just the model
   name.
5. Dangling-ref audit after any structural move: compare `\label{}` and
   `\ref{}` key sets (strip prefixes, sort, `comm -13`); a missing label
   compiles silently as "Section 3--??". Re-verify after cutting
   subsections into the appendix (keep the labels working).
6. Re-read the FILE before re-patching after a failed patch (the
   "identical old/new" or stale-anchor failures); the same region twice =
   rewrite the enclosing block.

## User style rules (hard preferences — do not re-learn them)

- NO em-dashes: never `---` in the paper — use `--` (en-dash) for dashes.
  Sweep `grep -c "\-\-\-"` before committing; every new patch must not
  reintroduce one (the escape-drift guard in patch old_strings is
  separate — plain-text anchors only on .tex files).
- Scope qualifier everywhere: "in the architectures and benchmarks we
  study" (or the user's exact equivalent) — never an unqualified
  universal. Sweep ALL claim sites when a claim is retracted, not just
  the section that changed (architecture-family counts, residual claims).
- Abstract: ~150 words, findings WITHOUT numbers, one thesis structure
  (the thesis lives in the abstract OR a Section-1 box — exactly one
  place, never both).
- Honest calibration: drop noise-dominated residual claims rather than
  defending them; say the STRONGER true thing instead (e.g. "two
  parameterizations of the same function class, not geometry"); state
  limitations prominently; "measure what you assert" — a headline row
  labeled "curved" with never-measured curvature is a reviewer
  invitation (the full-basis Yang-Mills of the trained models is one
  number per row).
- When a reviewer says "your best row is asserted, not measured" — the
  measurement is the full-basis YM/spectrum of the TRAINED models, and
  the result can flip a conclusion (both "curved" rows were flat in
  content — the SU(2) win became a capacity null).
- Reviewers audit the STATISTICS, not just the prose: a reported quantity
  whose scale contradicts its inputs (mean |edge phase| 0.016 rad vs a
  "mean triangle holonomy" of 3.47 rad — impossible for a sum of three
  small phases) means the COMPUTATION is wrong, not that the result is
  surprising. Audit the statistic before believing the claim; angle
  statistics must be reported in principal values (-pi, pi] with
  flat-fractions, never raw mod-2-pi sums (Python's `%` wraps negative
  sums to near-2pi, inflating a mean by ~100x). The paper's own
  wrap-safe numbers (Re-based YM, remainder-based losses) are fine — but
  state the convention explicitly when external-harness numbers appear.

## Toolchain

- tectonic: `~/.local/bin/tectonic -X compile main.tex`. Style quirks
  (e.g. `\nofinal` undefined in the 2026 style, missing companion .tex
  files) surface as XeTeX "halted on potentially-recoverable error" —
  grep the .sty for `DeclareOption` before guessing.
- Citation audit (the `audit_bib.py` pattern): every bib entry's
  surnames + count against the arXiv API. Corpus metadata is NOT ground
  truth (fabricated first names, wrong IDs happen); rebuild author lists
  from API data; skip no-arXiv entries explicitly (the per-entry window
  regex grabs the next entry's ID); whitelist API typos with a comment.
  Governance: only cite papers the research-assistant corpus has
  downloaded; NEVER drop a needed citation — request the download first
  (name-without-key is a temporary state). Bib must contain ONLY entries
  the text cites — run the used-vs-had comm check.
- Commit discipline: the paper, its figures, and the results tree are
  version-controlled (results/ IS tracked in the gauge repo — the
  "every result is a committed run" claim is literal; a reviewer's
  number-trace forced it). A table cell that cannot trace to a run dir
  is a submission blocker; cite the exact run dirs in captions for the
  rows that matter.

## Venue structure (NeurReps 2026 Proceedings Track example)

- 9 pages of MAIN TEXT (references + appendices excluded; no need to
  fill them). Split by what sensibly belongs: the thesis spine in the
  main, the controls/external studies/diagnostics in the appendix (the
  GESC non-reproduction, the depth sweep, the group-extension probe, the
  ablation details). Add main-text bridges pointing at the moved
  sections.
- USER REQUIREMENT: the appendix comes AFTER the references
  (`\bibliography` BEFORE `\appendix`). Appendix sections are numbered
  A/B/C (`\section` inside `\appendix`) with `\label{app:...}`.
- Mandatory NeurIPS checklist (appended after the appendix, unnumbered,
  NOT counted toward the page limit): the 11 standard items (claims,
  limitations, theory, reproducibility, data, code, compute, broader
  impacts, statistical significance, hyperparameters, experimental
  scope) each answered Yes/No/N-A with a short justification + a section
  reference. `\begin{enumerate}[leftmargin=*]` requires enumitem — use
  plain `\begin{enumerate}` if the package is not loaded. Keep the
  answers honest and traceable (e.g. the data item must list only
  datasets that actually appear in the results — Squirrel/CiteSeer got
  removed when a reviewer noticed they were absent). The checklist's
  claims about the BODY must also be literally true: "Theorem 1's
  assumptions and proof are included" was false (no proof environment
  existed — the only occurrence was the checklist itself), and the
  experimental-scope item overstated the dataset count (\"six real-world\"
  vs the paper's actual four). Before submitting, verify each checklist
  claim against the body: the proof exists, the counts match, the
  sections referenced exist.
- Compiled-PDF float reordering: a reviewer citing "Figure 2" may mean a
  different source figure than the script's fig2 — diagnose
  broken-figure complaints against the compiled page, not the script
  numbering.

## Pitfalls

- The `\\`-vs-`\` escape drift in patch old_strings on .tex files: the
  guard rejects backslash-heavy anchors; use plain-text anchors; when a
  patch's new_string contains LaTeX commands, verify the file got the
  single-backslash form (a double-escaped `\\cite`/`\\ref` renders
  literally).
- Never `write_file` a long curated log (research_log.md) — if the file
  was modified since the last read, write_file REPLACES the whole file.
  Append via a temp file + `cat >>`, and restore accidents with
  `git checkout -- <file>` (it is committed).
- The read_file "truncation marker" (e.g. "our tr...[truncated]") is
  the TOOL cutting the display, not content corruption — verify by
  reading the line's full context before "fixing" a sentence that is
  fine. Same for "Figure N is empty": check the load logic first (era
  globs, config filters) before assuming the figure script is broken.
- Reviewers re-read the paper AFTER your fixes — the round's delta must
  include the figure/caption/number consistency, not just the
  substantive edits.
