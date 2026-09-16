# Gauge paper session detail (opus/sol/claude-gauge rounds, 2026-08)

Concrete review items from the final rounds of the gauge-graph-network
paper (`reports/paper/main.tex`, tectonic) — each is a worked example of a
pitfall in the SKILL.md body.

## Round-final fixes (what the reviewers actually caught)

- **Corollary stray fragment**: the Torres-Hugas cite insertion trapped the
  next sentence's opening ("The gauge choices") INSIDE a `\begin{corollary}`
  block — a mid-statement fragment in a formal statement. Symptom class:
  after any cite/sentence insertion, read the enclosing environment end to
  end.
- **"SU(2) wins" clause**: the §4 prose said "including the SU(2) wins on
  Texas and Chameleon" while Table 1's own caption called the row a
  capacity NULL (Wisconsin 0.889 below flat AND cx; Texas +0.008;
  Chameleon +0.001). The prose claimed a win the table contradicted two
  pages earlier — replaced with "the SU(2) row matches the flat/cx rows
  within noise".
- **fig4(d) data error**: the oracle-vs-K panel plotted the U(1)^k torus
  run (0.473 at K=16) into the monotone K-sweep (0.600@K3 -> 0.880@K16).
  The panel's glob `planted-cheb*_pn0_*` matched the `_u1k` dir (same
  prefix, trailing suffix). Fix: `if "_u1k" in f: continue`.
- **fig1 flat bar**: the ladder load filtered `hidden=64` only — the depth
  sweep's s4 cell (stack_layers=4, 0.608) matched before the s1
  (stack_layers=1, 0.905), so Figure 1 plotted 0.61 while Table 1 said
  0.905. Fix: `stack_layers=1` added to every ladder row's load suffix.
- **"complex linear head" was false**: the paper (both §2 AND the appendix)
  claimed the readout is complex-linear; the code's head is
  `nn.Linear((K+1)*g*hidden, hidden)` — a general REAL-linear map on the
  realified features. Corrected to "real-linear head on the realified
  features" + the explicit "what is complex" exposition: features and the
  propagation (the transport's block-diagonal rotation) are complex; ALL
  learned linear maps are real-linear on the realified representation (a
  strict superset of the A/-B/B/A complex-linear form, real biases).
  The fix STRENGTHENS the argument (a real-linear head is more able to
  see the rotation).
- **cx baseline construction made explicit**: `x -> z = f_R(x) + i*f_I(x)`
  via two independent linears (the code's `proj` + `proj_im`), then the
  complex spectral tower with identity transport. Sol's caveat: with
  identity transport the propagation is effectively real, so "complex
  representation capacity" means the doubled realified channel structure;
  the rotation adds nothing (flat == cx exactly on Wisconsin).
- **Checklist data item**: claimed "Cora/CiteSeer, Chameleon/Squirrel" —
  CiteSeer and Squirrel appear nowhere in the results. Trimmed to the
  datasets that actually appear. Every checklist claim must trace like a
  paper claim.
- **§7 "truncation" was a tool artifact**: the reviewer's "our tr...[truncated]"
  was the message/preview truncation, not paper corruption — verify the
  full line before "fixing".

## NeurIPS checklist shape (11 items, all answered with section refs)

claims / limitations / theory / reproducibility / data / code / compute /
broader impacts (N/A for fundamental research) / statistical significance
(>=3 seeds, 6 on small sets, stds reported) / hyperparameters /
experimental scope. Each: Yes/No/N-A + one justification + `\ref` targets.
Plain `\begin{enumerate}` (no `[leftmargin=*]` — enumitem not loaded).

## NeurReps split that worked

Main: intro + theory (flat == trivial, the corollary) + collapse + the
complexification decomposition + cycle-space supervision + the multi-cycle
core (receptive-field + recovery diagnosis) + related work + discussion.
Appendix (after the references): GESC non-reproduction (app:gesc), depth
sweep (app:depth), U(1)^k probe (app:groups), architecture details
(app:arch), tree-sensitivity (app:tree when the batch lands). Bridges:
"Two further negative controls --- depth and larger gauge groups --- are
detailed in the appendix."
