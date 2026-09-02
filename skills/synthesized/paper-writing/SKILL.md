---
name: paper-writing
description: "Write, revise, and submit scientific papers for NeurIPS/ICML/ICLR. LaTeX conventions, claims rigor, review workflow, and submission checklists."
author: huebers
license: MIT
---

# Scientific Paper Writing

## When to Use

Any session that drafts, revises, or prepares a scientific paper for submission: designing experiments, writing sections, integrating reviewer feedback, auditing citations, restructuring for page limits, or running the submission checklist. Load before editing main.tex.

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions. Produce something concrete to react to, then iterate.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically. Mark unverifiable citations as `[CITATION NEEDED]`.
3. **Paper is a story, not a collection of experiments.** Every paper needs one clear contribution stated in a single sentence. If you cannot, the paper is not ready.
4. **Experiments serve claims.** Every experiment must explicitly state which claim it supports. Never run experiments that do not connect to the narrative.
5. **Commit early, commit often.** Every completed experiment batch and draft update gets committed with descriptive messages.

## Claims and Rigor Guidelines

These are hard rules — violating them invites reviewer rejection.

- **No RMSE sample-efficiency claims without controlled evidence.** Do not claim a method is "more sample-efficient" from RMSE curves alone unless the sample budget, seed set, and baseline are controlled. RMSE-vs-epochs is not sample efficiency.
- **Coordinate diagnostics are not general claims.** A diagnostic on a specific coordinate system (phase/holonomy statistics, angular quantities) is a measurement under that convention, not a universal property. Scope it: "in the architectures and benchmarks we study." Never make an unqualified universal claim.
- **Test synthetic axis-ordering confounds before real-world generalization.** Synthetic sweep plots (K-sweeps, depth sweeps) must exclude sibling variants sharing the name prefix, or a confounding run plots as a spurious dip. Load filters must pin the EXACT config (stack_layers, seeds, era suffix), not just the model name. Generalization claims require clean synthetic axes first.
- **Honest calibration.** Drop noise-dominated residual claims rather than defending them; say the STRONGER true thing instead. State limitations prominently.
- **Measure what you assert.** A headline row labeled "curved" with never-measured curvature is a reviewer invitation. If a claim requires a measurement, the measurement must exist.
- **Audit the statistics, not just the prose.** A reported quantity whose scale contradicts its inputs (e.g., mean phase 0.016 rad vs "mean holonomy" 3.47 rad — impossible for a sum of three small phases) means the computation is wrong, not that the result is surprising. Audit the statistic before believing the claim.
- **Report angle statistics in principal values** (-pi, pi] with flat-fractions, never raw mod-2-pi sums (Python `%` wraps negative sums to near-2pi, inflating a mean by ~100x). State the convention explicitly when numbers appear.
- **Sweep ALL claim sites when a claim is retracted**, not just the section that changed.

## LaTeX Conventions

- **Compiler: tectonic.** `~/.local/bin/tectonic -X compile main.tex`. Style quirks (undefined macros, missing companion .tex files) surface as XeTeX "halted on potentially-recoverable error" — grep the .sty for `DeclareOption` before guessing.
- **NO em-dashes.** Never `---` in the paper. Use `--` (en-dash) for ranges/dashes. Sweep `grep -c "---"` before committing; every new patch must not reintroduce one.
- **docs/ directory.** Keep paper LaTeX source, figures, and compiled PDFs under a `docs/` (or `paper/`) directory in the repo. Results trees are version-controlled — "every result is a committed run" is literal. A table cell that cannot trace to a run dir is a submission blocker; cite exact run dirs in captions for rows that matter.
- **Appendix after references.** `\bibliography` BEFORE `\appendix`. Appendix sections numbered A/B/C with `\label{app:...}`.
- **Plain-text anchors in patches.** On .tex files, use plain-text anchors for find-and-replace; backslash-heavy anchors are rejected by the escape-drift guard. When a new_string contains LaTeX commands, verify the file got the single-backslash form.

## Paper Structure and Sections

### Abstract (~150 words)
- Findings WITHOUT numbers. One thesis structure.
- The thesis lives in the abstract OR a Section-1 box — exactly one place, never both.
- Delete the first sentence if it could prepend any paper. Start with your specific contribution.

### Introduction
- Front-load contribution bullets. Do not exceed ~1.5 pages; split background into Related Work.
- State the single contribution in one sentence early.

### Related Work
- Group by methodology, not paper-by-paper. "One line of work uses X's assumption [refs] whereas we use Y's because..." — not "Smith et al. introduced X. Jones et al. introduced Y."
- Cite papers the corpus has actually downloaded; NEVER drop a needed citation — request it first.

### Methods
- Pseudocode, all hyperparameters, architectural details sufficient for reproduction.
- Theory papers: Preliminaries -> Main Results (theorems) -> Proof Sketches -> Full Proofs (appendix). State theorems formally with all assumptions explicit. Provide intuition before formal proof.

### Experiments
- Each experiment states which claim it supports: "This experiment tests whether [specific claim]..."
- Error bars (specify SD or SE), confidence intervals, pairwise tests, effect sizes.
- Baselines: naive, strong, ablation, compute-matched. Strong baselines separate accepted from rejected.

### Conclusion
- Single-sentence takeaway. Limitations stated prominently.

### Figures and Tables
- **Figures**: Vector graphics (PDF). Colorblind-safe palettes (Okabe-Ito or Paul Tol). Self-contained captions (reader understands without main text). No title inside the figure — the caption serves this.
- **Tables**: `booktabs` package. Bold best value per metric. Include direction symbols (up/down arrow). Consistent decimal precision.
- After regeneration: PIL non-white fraction check (empty-figure detection), AND verify the numbers the figure plots against the table (reviewers cross-check this first).
- A reviewer citing "Figure 2" may mean a different source figure than the script fig2 — diagnose broken-figure complaints against the compiled page.

## Citation Practices

**Never generate BibTeX from memory. Always fetch programmatically.**

Per-citation process (mandatory):
1. SEARCH — query Semantic Scholar / arXiv / CrossRef with specific keywords.
2. VERIFY — confirm paper exists in 2+ sources.
3. RETRIEVE — get BibTeX via DOI content negotiation.
4. VALIDATE — confirm the cited claim actually appears in the paper.
5. ADD — add verified BibTeX to bibliography.

If any step fails: mark `[CITATION NEEDED]`, inform co-authors.

- **Citation audit**: every bib entry surnames + count checked against the arXiv API. Corpus metadata is NOT ground truth (fabricated first names, wrong IDs happen); rebuild author lists from API data. Skip no-arXiv entries explicitly. Whitelist API typos with a comment.
- **Bib must contain ONLY entries the text cites** — run the used-vs-had comm check.
- **Dangling-ref audit** after any structural move: compare `\label{}` and `\ref{}` key sets (strip prefixes, sort, `comm -13`); a missing label compiles silently as "Section 3--??".

## Co-Author Conventions

Most papers have 3-10 authors. Establish workflows early:

- **Section ownership**: Assign each section to one primary author. Others comment but do not edit directly. Prevents merge conflicts and style inconsistency.
- **Shared workspace**: Overleaf (live collab) or git+LaTeX with `.gitignore` for aux files. Overleaf+Git sync combines both.
- **Agree on conventions BEFORE writing**:
  - `\method{}` macro for consistent method naming.
  - Citation style: `\citet{}` vs `\citep{}` usage.
  - Math notation: lowercase bold for vectors, uppercase bold for matrices.
  - British vs American spelling.
  - Figure style (colors, fonts, sizes) before creating figures.
- **Internal review rounds** throughout, not just at the end. Designate one person for the final formatting pass.

## NeurIPS / ICML / ICLR Submission Workflow

### Venue Requirements

| Venue | Page Limit | Special Requirements |
|-------|-----------|---------------------|
| NeurIPS | 9 (excl. refs/appendix) | Paper checklist (appendix, unnumbered), lay summary if accepted |
| ICML | 8 | Broader Impact Statement (after conclusion, does not count toward limit) |
| ICLR | 9 | LLM disclosure required, reciprocal reviewing agreement |
| ACL | 8 (long) / 4 (short) | Mandatory Limitations section, Responsible NLP checklist |
| AAAI | 7 | Strict style file — no modifications |
| COLM | 9 | Frame contribution for language model community |

### Page Split Strategy
- Main text: thesis spine, core method, key experiments.
- Appendix (after references): controls, external studies, diagnostics, ablation details, full proofs.
- Add main-text bridges pointing at moved sections.

### Mandatory NeurIPS Checklist (11 items)
claims, limitations, theory, reproducibility, data, code, compute, broader impacts, statistical significance, hyperparameters, experimental scope. Each: Yes/No/N-A + short justification + `\ref` target. Plain `\begin{enumerate}` (no `[leftmargin=*]` unless enumitem loaded).

**Verify each checklist claim against the body before submitting**: the proof exists, the counts match, the sections referenced exist. Checklist claims about the body must be literally true.

### Anonymization (Double-Blind)
- No author names/affiliations in PDF. No acknowledgments (add after acceptance).
- Self-citations in third person: "Smith et al. [1] showed..." not "We previously showed [1]..."
- Use Anonymous GitHub (https://anonymous.4open.science/) for code links.
- No "our previous work" phrasing. Check PDF metadata for author names.
- Common mistakes: git commit messages in supplementary code, watermarked figures, arXiv preprint before anonymity period.

### Pre-Compilation Validation
```bash
# Lint
chktex main.tex -q -n2 -n24 -n13 -n1

# Verify citations exist in .bib
# Verify all \includegraphics files exist on disk
# Check for duplicate \label definitions
```
Fix warnings before compiling. Parse `.log` for first error if compilation fails.

### Format Conversion (Resubmission)
Never copy LaTeX preambles between templates. Start fresh with target template, copy only content sections. When cutting pages: move proofs to appendix, condense related work, combine tables, use subfigures. After rejection: address reviewer concerns without referencing the previous submission (blind review).

### arXiv Strategy

| Situation | Recommendation |
|-----------|---------------|
| Double-blind venue (NeurIPS/ICML/ACL) | Post AFTER submission deadline |
| ICLR | arXiv before submission allowed; do not put author names in submission |
| Workshop | arXiv fine anytime |
| Scooping concern | Post immediately, accept anonymity tradeoff |

Categories (ML/AI): `cs.LG`, `cs.CL`, `cs.AI`, `cs.CV`, `cs.IR`. List primary + 1-2 cross-listed.

## Revision Under Reviewer Feedback

### The Review-Round Loop (Core Discipline)
1. Every review round: fix numbers/figures/claims FIRST, then proofread, then recompile, then commit. Expect 2-4 rounds.
2. **Stale-number sweep** after ANY table/caption edit: grep the prose for old values (each changed table cell is a candidate). Prose/tabular mismatch is the first thing a reviewer checks and usually signals a deeper claim problem.
3. **Verify claims against the CODE, not just tables.** Grep the model code for every architectural claim; correct the paper to match the code. Sweep the appendix for the same stale claim — a fix in one section must propagate everywhere.
4. **Re-read the FILE before re-patching** after a failed patch. The same region twice = rewrite the enclosing block.

### Simulated Review (Pre-Submission)
Generate N=3-5 independent reviews from different perspectives, defaulting to negative bias (LLMs have positivity bias in evaluation). Each reviewer evaluates: soundness, clarity, significance, originality. Then run a meta-review (area chair aggregation) to identify consensus strengths/weaknesses.

Optional passes:
- **Visual review** on compiled PDF: figure quality, layout, caption alignment, grayscale readability.
- **Claim verification**: extract every factual claim, trace to the specific result file, flag untraceable claims.

### Prioritizing Feedback

| Priority | Action |
|----------|--------|
| Critical (technical flaw, missing baseline) | Must fix. May require new experiments. |
| High (clarity, missing ablation) | Should fix this revision. |
| Medium (minor writing, extra experiments) | Fix if time allows. |
| Low (style preferences) | Note for future work. |

### Rebuttal Writing
Point-by-point format. For each concern:
```
> R1-W1: "The paper lacks comparison with Method X."
We thank the reviewer. We added a comparison with Method X in Table 3 (revised).
Our method outperforms X by 3.2pp (p<0.05).
```
- Address every concern — reviewers notice if you skip one.
- Lead with strongest responses. Be concise. Include new results if run during rebuttal period.
- Never defensive or dismissive. Thank for specific, actionable feedback.
- Use `latexdiff` for marked-up PDF showing changes.

### Camera-Ready (Post-Acceptance)
- De-anonymize: add author names, affiliations, emails.
- Add Acknowledgments (funding, compute grants, helpful reviewers).
- Add public code/data URL (real GitHub, not anonymous).
- Address mandatory revisions from meta-reviewer.
- Verify final PDF compiles cleanly. Check camera-ready page limit (may differ).

## Figure and Table Pitfalls

- Panel-level sweep plots must exclude sibling variants sharing the name prefix (glob `planted-cheb*_pn0_*` matched a `_u1k` dir — fix: `if "_u1k" in f: continue`).
- Load filters must pin the EXACT config (stack_layers, seeds, era suffix), not just the model name — a depth sweep wrong cell matched before the right one, plotting 0.61 while the table said 0.905.
- The "truncation marker" (e.g., "our tr...[truncated]") is the tool cutting the display, not content corruption — verify full context before "fixing" a sentence that is fine. Same for "Figure N is empty": check load logic first.
- Reviewers re-read the paper AFTER your fixes — the round delta must include figure/caption/number consistency, not just substantive edits.

## Reviewer Evaluation Criteria

| Criterion | What They Check |
|-----------|----------------|
| Quality | Technical soundness, well-supported claims, fair baselines |
| Clarity | Clear writing, reproducible by experts, consistent notation |
| Significance | Community impact, advances understanding |
| Originality | New insights (does not require new method) |

NeurIPS 6-point scale: 6 Strong Accept, 5 Accept, 4 Borderline Accept, 3 Borderline Reject, 2 Reject, 1 Strong Reject.

## Handling Negative/Null Results

| Situation | Action | Venue Fit |
|-----------|--------|-----------|
| Hypothesis wrong but WHY is informative | Frame paper around analysis of why | NeurIPS/ICML (if rigorous) |
| Method does not beat baselines but reveals something new | Reframe as understanding/analysis | ICLR, workshops |
| Clean negative result on popular claim | Write it up — field needs to know | NeurIPS D&B, TMLR, workshops |
| Results inconclusive, no clear story | Pivot — do not force a paper | — |

## Paper Types Beyond Empirical ML

- **Theory**: Preliminaries -> Main Results -> Proof Sketches -> Full Proofs (appendix). Contribution is a theorem/bound/impossibility result. Proof sketches convey the main idea in 0.5-1 page. `\begin{proof}...\end{proof}` environments. Number assumptions, reference in theorems.
- **Survey**: Taxonomy -> Detailed Coverage -> Open Problems. Must be comprehensive within scope. Clear organizational framework. Best: TMLR, JMLR, Foundations and Trends.
- **Benchmark**: Task Definition -> Dataset Construction -> Baseline Evaluation -> Analysis. Must fill a genuine evaluation gap, demonstrate it is challenging, demonstrate construct validity. Best: NeurIPS D&B, ACL resource papers.
- **Position**: Thesis -> Supporting Evidence -> Counterarguments -> Implications. Must engage seriously with counterarguments. Best: ICML position track, workshops, TMLR.
