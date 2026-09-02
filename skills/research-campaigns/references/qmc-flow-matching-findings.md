# QMC / Flow-Matching Transport — domain findings (diffusion-qmc project)

Condensed results from the diffusion-qmc campaign (wave 5-9, 2026-08-12/13).
Targets: 30D paper GMM (4 modes, full-rank), manifold-30D (2D structure +
noise in 28 dims), spectral-30D (centered Gaussian, diag cov j^-1.5).
Protocol: scrambled Sobol, logit base, complex integrand + second-moment
integrand, 10 eval replicates, N up to 8192. All RMSE@max-N unless noted.

## The oracle ceiling (Klebanov–Sullivan exact mixture transport)

Closed-form ODE transport for GMM targets (Theorem 5.1 of arXiv:2308.10081):
rho_t mixture with A_j,t = tA_j + (1-t)I, velocity
v_t(x) = sum_j w_j rho_j,t (a_j + (A_j-I) A_j,t^{-1}(x - t a_j)) / sum_j w_j rho_j,t.
Implemented as `src/diffusion_qmc/oracle_transport.py` (MixtureTransport,
RK4; logistic base via quantile coupling Phi^{-1}(sigmoid(x))).
Used as the *achievable-error ceiling* for every learned map.

- 2D paper GMM: oracle-QMC slope -0.97, 3.76e-5 @8192 (≈ direct RQMC).
- 30D paper GMM, complex: oracle-QMC slope **-0.50** (1.3e-3 @8192) — the
  complex integrand's effective dimension caps EVERY method, learned or
  exact. The 30D ceiling is integrand-side, not map-side.
- 30D paper GMM, second-moment: oracle slope -0.97 (1.8e-3) — the QMC rate
  IS available on low-eff-dim integrands; learned maps were 200x off.
- spectral-30D: oracle complex slope -1.15 (8.75e-5 @512), second -0.87.
- manifold-2D: oracle 3.5e-6 (slope -1.2).

## Moment correction (the strongest lever; novel)

Evaluation-time affine renormalization of the flow pushforward:
x' = diag(sigma_p/sigma_q)(x - mu_q) + mu_p, using the target's analytic
first two moments (CAREFUL: use marginal variance incl. mean^2 contribution
= diag(cov) + mean^2, not just diag(cov) — using cov-only destroyed the
second moment). Needs no retraining, is measure-preserving, and directly
attacks the QMC-exposed variance bias. Results:
- 30D paper, second-moment: baseline FM-QMC 3.7e-1 -> 2.4e-2, slope -0.96.
- OT-30D second: 4.7e-1 -> 2.1e-2 (slope -0.96) — stacks across flows.
- spectral: baseline complex 3.19e-3 -> 3.13e-4 (10x); OT 1.71e-3 ->
  1.15e-4 (15x) — corrected OT within 1.3x of oracle (8.75e-5).
- Complex integrand roughly unchanged or slightly worse (it is ~linear in
  the sum; the correction targets variance, not location).

## What worked per 30D target (complex integrand, FM-QMC)

| target | winner | value | runner-up |
|---|---|---|---|
| 30D paper GMM | baseline / PCA-OT / structured | ~2.1e-3, slope -0.5..-0.6 | oracle 1.3e-3 caps all |
| manifold-30D | monotone-PC | 2.7e-4 (slope -0.70) | baseline 3.8e-4 |
| spectral-30D | OT-CFM | 1.7e-3 | +moment corr 1.15e-4 |

- OT-CFM beats baseline only on spectral (the low-eff-dim target); on the
  30D paper GMM it loses (3.7e-3 vs 2.1e-3).
- monotone/rank couplings win ONLY on the manifold target (2D structure):
  monotone-PC 2.7e-4 vs baseline 3.8e-4. Every other 30D intervention
  (monotone-k2 5.1e-3, moment-reg 5.1e-3, lip-pen-smooth 5.2e-3) is worse
  than plain CFM on manifold-30D.
- StructuredMap (Liu-style KL transport): optimal QMC rate in 2D (S-QMC
  slope -1.03), best 30D map (2.0e-3, slope -0.61, within 1.6x of oracle)
  but reverse-KL collapses on anisotropic targets (correlation -0.81 vs
  target 0 on thin 2D GMM; fails on power-law spectral).

## PCA-frame training (Sobol dimension ordering) — interaction, not lever

Train in the target's PCA basis (top PC = coord 1 aligns with Sobol dim 1,
the best-equidistributed dimension), unrotate at eval. Implementation:
compute V from 50k target samples (SVD of centered), rotate x1 in the
training loop, save rotation_matrix + target_mean in checkpoint, unrotate
in eval drivers (full_eval_driver + evaluate_structured).

- **Hurts plain CFM**: 30D paper 6.67e-3 vs 2.12e-3; manifold 2.52e-3 vs
  3.81e-4; spectral 2.33e-3 vs 3.19e-3 (spectral the only mild win).
  Mechanism: CFM freely entangles coordinates — rotating target samples
  does NOT make output coord 1 a function of input coord 1; unrotation
  spreads the PC score back across coordinates. Even on the PC-score
  integrand (the aligned case) PCA is worse (structured: plateau 1.28e-1
  vs non-PCA 3.40e-2).
- **Force multiplier for OT-CFM**: PCA-OT beats plain OT everywhere (30D
  paper 3.65e-3 -> 2.11e-3, best CFM slope -0.57; manifold 1.84e-3;
  spectral 1.71e-3 -> 1.27e-3). The minibatch OT plan already aligns map
  coordinates with target variance, so the rotation compounds it.

## Regularizers — the aux-weight-scale lesson, twice

- Lipschitz/Jacobian penalties (lip_pen) DO work in 2D at weight 0.1
  (FM-QMC 4.0e-4, slope -0.70, tightest sigma_max 1.68) but NOT in 30D:
  weight 0.001 (earlier screening) is 1000x too weak to matter; weight 0.1
  over-regularizes (manifold FM-QMC 5.24e-3 vs baseline 3.81e-4).
- Strain/vorticity decomposition (Tao & Choi 2605.06680): penalty
  alpha*||S||^2 + beta*||Omega||^2 with S=(J+J^T)/2, Omega=(J-J^T)/2,
  estimated via ||S||^2 = (||J||^2_F + tr(J^2))/2, tr(J^2) = E[(J^T z).(J z)]
  (VJP times JVP). alpha > beta; start beta=0; weight ~10-20% of FM loss.
  This is the decomposed version of lip_pen — the literature-grounded fix
  for the 30D plateau (strain -> exponential map-error amplification ->
  rough IS integrand -> Owen boundary growth fails -> RQMC rate degrades).

## Hutchinson double-backprop penalties — numerics & memory

- The penalty gradient through the Hutchinson estimator is unstable:
  uncapped and hard-capped variants NaN at steps 70-96k. A hard cap bounds
  the LOSS VALUE but not the GRADIENT (clamp passes gradient below cap).
  Robust fix: **smooth variant log1p(penalty)** — gradient magnitude
  bounded by 1/(1+x) <= 1, cannot produce inf/NaN; trained stably to 96k.
- Double-backprop (VJP + JVP with create_graph) blows GPU memory at batch
  256 (OOM even on 80GB). Fix: compute the penalty on a SUBSAMPLE of x_t
  (penalty_batch=64) — it is a Hutchinson estimate, the batch only affects
  estimate quality. Also use interval=100 not 10 (regularizer, not main
  loss) and probes=1.
- NaN'd final checkpoint: check for NaN tensors in checkpoint.pt before
  evaluating; the final checkpoint can be poisoned (54/55 tensors NaN)
  while periodic checkpoints (checkpoint-step-75000.pt) are clean.
  Swap the clean checkpoint into checkpoint.pt (backup the NaN one as
  checkpoint.pt.nan) and evaluate that.

## Real data (HEPMASS 21D, MINIBOONE 43D)

Empirical/bootstrap target (no density => no ISQMC; FM-MC/FM-QMC only).
QMC ≈ MC for both baseline and monotone couplings (slopes ~-0.2): no
low-discrepancy advantage on real-world targets; monotone doesn't transfer.
Future route to real-data FM-ISQMC: energy-weighted FM (2509.03726) trains
a CNF from an unnormalized/surrogate density (one energy eval per
trajectory) -> exact ICoV log-density -> tractable change-of-variable
weights. Caveats: exact w.r.t. the MODELED target (surrogate error = bias);
use EXACT divergence for weight computation (Hutchinson-trace densities are
noisy); weight clipping (97.5-99.9th pct) is the key hyperparameter.

## Inference-time dimension reordering (integrand PCA) — NEGATIVE

"PCA for the integrand" at inference = estimate per-coordinate base
importance I_j = E[(d h/d x0_j)^2] (finite differences THROUGH the ODE —
autograd breaks on the ODE chain), then reorder base coords so the best
Sobol dims drive the important ones. CRITICAL constraint: an orthogonal
rotation of base points is distribution-preserving only for a
ROTATION-INVARIANT base (Gaussian); the logistic base admits only
PERMUTATIONS/reflections. Results with scrambled Sobol:
- spectral-OT 1.71e-3 vs 1.71e-3 (permutation near-identity — map already
  coordinate-aligned), 30D baseline 2.12 vs 2.14e-3, PCA-30d-OT 5.85 vs
  5.85e-3. No gain anywhere.
- Why: Owen-scrambled Sobol gives comparable equidistribution across ALL
  dimensions, so the early-dimension advantage that dimension-ordering
  exploits is weak (the classical big active-subspace gains use
  UNSCRAMBLED Sobol). The full rotation version needs a Gaussian base
  (retrain with Phi^-1(u) instead of logit(u)) — not worth it given the
  permutation signal is zero.

## Strain-regularized OT results (Tao & Choi 2605.06680)

alpha*||S||^2 + beta*||Omega||^2 (alpha=1, beta=0, weight 0.2, smooth
log1p, interval=100, probes=1, penalty_batch=64) on spectral-30D:
- complex FM-ISQMC 5.4e-4 -> 3.7e-4 (1.5x, slope -0.52) — improves exactly
  the importance-weighted channel the theory predicts (strain roughens
  pi o tau |det J_tau|)
- FM-QMC unchanged (1.71 -> 1.68e-3); second-moment FM-QMC slightly worse
  (1.4e-2 -> 2.7e-2, mild over-regularization)
- stable (no NaN) where full-Frobenius lip_pen was not; paper suggests
  time-dependent alpha(t) at endpoints as follow-up.

## Rate theory for the exact IS weights (Du & He 2511.10599)

Our FM-ISQMC weights omega_tau = pi_1 o tau |det J_tau| / q_0 are exactly
the RQMC-SNIS IS integrand. Composed growth rate:
    M_{g o tau} = M_g C_tau + d M_tau
- map derivative growth (strain) M_tau costs d*M_tau — dimension-proportional
  penalty: at 30D, M_tau = 0.1 drags the rate exponent from 1 toward 0.6.
  This is the QUANTIFIED plateau mechanism our strain experiments target.
- composing K map layers multiplies C_tau by lambda_max^K — deep NF
  proposals are structurally rate-hostile; a single well-trained shallow FM
  map is the better QMC proposal.
- self-normalization is asymptotically free (numerator/denominator rates add).
Complementary sufficient conditions: Owen boundary growth of the composition
(2608.11055 / Zeng & Chen) vs quadratic-exponential growth of the factors
(this paper). KR-map diagnostic (2511.04579): triangular-map roughness =
conditional density ratio dT_i/dx_i = f(x_i|x_1:i-1)/g(T_i|T_1:i-1), blows
up where conditional target densities -> 0 — thin targets are structurally
doomed for triangular families (explains the manifold-2D structured-map
collapse a priori); KL-penalty (lambda) knob is the smoothing lever.

## Uncertainty reporting (Owen 2501.00150)

For scrambled-net RQMC: Student's t on R independent replicates
(mu_hat +/- t^0.975_{R-1} s/sqrt(R)); R >= 10 (all failures in Owen's study
at R=5). Avoid percentile bootstrap, BCa, bootstrap-t (undercover for nets).
Report R in every table cell. This justifies the campaign's R=10 protocol.

## Related-work note

The FM-QMC reference (Zeng & Chen 2601.01072) and the Diffusion-QMC
competitor (Chen & Yu 2608.11055) are the SAME group (J. Chen in both; the
latter reuses propositions verbatim). Frame them together in related work.

## Other operational notes

- Evaluation wall-time is dominated by ISQMC (Hutchinson log-prob): ~45
  min on GPU for 30D. Run evals on a free joinable allocation, not CPU.
- The 6-estimator eval is `scripts/full_eval_driver.py` (reads a list file
  of run dirs); `batch_diagnose.py`/`cli/diagnose.py` only runs quick
  diagnostics — check eval dirs exist before trusting job completion.
- train_structured.py saves config WITHOUT a `model` key (layers/hidden at
  top level); eval drivers must branch on `"model" in config`.
- Double-logit footgun: `EulerTransport.__call__(u)` applies logit(u)
  internally — feed raw Sobol u, never `transport(logit(u))` (RMSE
  inflates ~400x silently). Use `from_base(x0)` only when x0 is already
  logistic-distributed.
- StructuredMap PCA-frame training needs the KL evaluated at rotated-back
  points (x_orig = x @ V + mean); log-det unchanged (|det V| = 1); store
  rotation_matrix + target_mean in the checkpoint and unrotate in eval.
