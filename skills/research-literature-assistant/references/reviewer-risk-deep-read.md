# Reviewer-risk deep-reads + state-doc status discipline (2026-08-14 session)

Two additions to the research-literature-assistant workflow, distilled from the
gauge-supervisor deep-read queue and the GESC audit arc.

## 1. Reviewer-risk deep-reads (manuscript-anchored)

When a peer is writing a paper and an external review (Sol/Opus pattern in
SKILL.md) flags specific claims as attackable, run deep-reads ANCHORED ON THE
RISKS instead of generic reads. Worked example: gauge's priority queue
(Platonov 2302.11640 / Loukas 1907.03199 / DiGiovanni 2302.02941, then
CycleNet 2311.14333 / Torres-Hugas 2604.19682).

Prompt structure per paper:
- State the EXACT reviewer objection and the specific claim it threatens
  (e.g. "§4 rests on Wisconsin/Texas/Chameleon with ±0.03 stds — Platonov
  shows duplicate-node leakage"; "a K=3 one-layer covariant tower cannot
  close a 12-hop loop").
- Ask for a VERDICT, not a summary: does the theory LICENSE the peer's
  conclusion, EXPLAIN IT AWAY (making it an artifact), or neither?
  (Loukas + DiGiovanni both did two of three simultaneously: they license
  the necessity half of the architectural claim AND explain away the oracle
  ceiling, but do NOT cover the binding residual — which is the project's
  actual contribution. That split is the value.)
- Tell the subagent to read the peer's OWN manuscript sections + references.bib
  and anchor the note there. This produced two real catches:
  - gauge already cited Platonov (main.tex L343) but with one throwaway
    clause — the letter of the reviewer's "not citing" was wrong, the
    substance stood.
  - a LITERALLY TRUNCATED related-work sentence at main.tex:567 (the literal
    `[truncated]` in the file, verified with od) and a bib entry (CycleNet)
    absent at the point of use — both became action items for the manuscript.
- Note sections: house style + explicit "Reviewer-risk implications for
  <project>" section listing concrete mitigations (which clean dataset to
  add, which column to demote, which claim to reframe, which theorem numbers
  to cite). Subagents verified their own numeric claims (walk counts, ring
  sensitivities recomputed exactly) — require that.
- Subagents may patch the peer's papers/README.md (deep-read status line,
  author-list fixes — one fixed a missing 5th author) — that is curation
  space; they must NOT touch the manuscript itself.
- Deliver ONE consolidated digest per batch mapping each note to the review
  risk it resolves, plus the action items for the manuscript. The supervisor
  relays to the peer; keep supervisor messages short (truncation observed).

## 2. Stats-bug audit for peer reproduction numbers (mod-2π lesson)

Peer reproduction/verification numbers are self-reports and can carry STATS
BUGS. GESC case: gauge's patched harness reported mean |holonomy| 1.98-4.59
rad (which initially looked like task-driven curvature — a "counterexample"
to the collapse thesis). It was an artifact of `h = sum % 2π` wrapping
NEGATIVE sums to near-2π (a -0.1 rad sum became 6.18). Corrected to principal
values: mean triangle holonomy 0.0321 rad, flat-fraction 1.0 — the transport
is FLAT. The counterexample dissolved.

Rules:
- Report holonomy/angle statistics in PRINCIPAL VALUES with a flat-fraction
  (frac of cycles with |hol| > threshold), never raw mod-2π sums.
- When a peer's angle/holonomy number looks anomalously large, suspect the
  wrap before believing it; ask for the principal-value version.
- A reproduction can fail NUMERICALLY on one dataset while reproducing on
  others (Chameleon's headline 65.0: non-finite grads from epoch 0) — record
  both sides; "reproduces on X, diverges on Y" is the honest note.
- Update the paper note's ⚠️ REPRODUCTION UPDATE addendum to the final audited
  state (broken-by-default released path vs patched paper mode), with dates.

## 3. State-doc status discipline (PROPOSED vs APPROVED)

- Record proposed mitigations/experiments as PROPOSED, never as done:
  gauge-supervisor explicitly asked that Amazon-ratings be recorded as
  "proposed mitigation, not yet approved or completed" until the operator
  approved it. Flip the marker only when the peer/operator confirms.
- Keep state docs OPEN-ENDED: don't write "experiment freeze" / "closed"
  markers unless the operator says so. A freeze can be superseded mid-course
  (happened same day: freeze superseded, Amazon-ratings proceeds, mechanistic
  inquiry continues) — a stale frozen marker misleads every reader.
- When the operator changes direction, record the supersede with date +
  attribution and remove the stale marker in the same edit.
