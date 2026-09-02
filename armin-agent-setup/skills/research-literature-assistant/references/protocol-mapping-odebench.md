# Worked example: apples-to-apples protocol mapping (FIM-ODE 1 ODEBench)

Session 2026-08-13. fim needed to judge whether their 5-seed ODEBench results
beat/compared to their own published paper (arXiv 2602.08733v2, ICML 2026,
"Foundation Inference Models for Ordinary Differential Equations", checkpoint
= models/base_model). The protocol doc produced: FIM/papers/notes/
odebench-apples-to-apples-protocol.md. This file is the condensed method.

## The paper's protocol (extracted from deep-read note)

- 61 systems = ODEBench's 63 minus 2 with d > 3; reference on fixed 512-pt grid.
- Corruption: multiplicative noise sigma in {0, 0.03, 0.05} x random
  subsampling rho in {0, 0.5} -> 6 configs; SINGLE corrupted context trajectory.
- Tasks: reconstruction (integrate inferred field from GT IC) and
  generalization (from NEW ICs — in ODEBench the 2 solutions per system are
  pairs; context = corrupted *other* solution).
- Metric: variance-weighted R2 (per-dim R2 weighted by SS_tot share), reported
  as % trajectories with R2 > 0.9 (gen also 0.8). Denominator 122 = 61 x 2.
- Integration: scipy.integrate.solve_ivp. Single run, no seeds reported.

## Codebase mapping (fim harness)

| Paper element | Codebase | Status |
|---|---|---|
| 61 systems (d<=3) | cli.py:180 dim > max_dim filter (max_dim=3) | exact |
| 6 configs rho x sigma | cli.py:1317-1322 loops [0.0,0.5] x [0.0,0.03,0.05] | exact |
| multiplicative noise | cli.py:210-221 min_sigma=max_sigma=sigma | exact |
| subsampling random | cli.py:216-218 min_ratio=max_ratio=rho | exact |
| single corrupted context | cli.py:345-355 | exact |
| recon GT IC | get_initial_conditions = traj[:,0,:] | exact |
| gen new ICs | cli.py:357-365 pair-swap | exact |
| variance-weighted R2 | stats.py R2VarianceWeighterStatCalculator | exact (same formula) |
| thresholds 0.9/0.8 | reporting.py THRESHOLDS_BY_TEST_TYPE | exact |
| per-trajectory denom | stats.py b*t rows | exact |

## The two deltas found

1. **Grid 200 vs 512**: cli.py:119 MAX_POINTS_ODE_BENCH=200; cli.py:199-201
   uniformly selects 200 of the 512 points (raw data IS 512). Truth and pred
   on same grid (consistent) but R2 values shift slightly AND corruption
   operates on the 200-grid -> at rho=0.5 the model sees 100 context pts vs
   the paper's 256. One-line fix: MAX_POINTS_ODE_BENCH = 512.
2. **Solver**: ivp_solver.py = Heun (improved Euler), step_per_dt=8
   (cli.py:564) vs paper's scipy solve_ivp (adaptive RK45, tolerances
   unspecified). Recommend keeping Heun/8 (deterministic; anchor matched).

## Anchor arithmetic (verification discipline)

- Peer's pooled summary md (r2_summary_seeds_0-1-2-3-4.md) vs paper's Table 1:
  recon |delta| ~1.3pt, gen ~1.6pt across 12 cells -> harnesses compatible.
- Per-dim denominators NOT in the r2.json (flat list of 122 R2 values per
  config). Verified arithmetically: dim=2 (0,0) 92.9% = 260/280 pooled; dim=3
  25.0% = 25/100 -> per-seed 46/56/20 trajectories (23/28/10 systems x 2 ICs),
  pooled 230/280/100, total 610 = 122 x 5. (My first draft guessed 220/260/130
  from a wrong 22/26/13 system split — fim corrected; arithmetic on the real
  summary proved it. LESSON: never guess per-dim splits; derive from data.)

## Takeaways for next time

- One CLI invocation often runs all configs (configs_per_batch=6 fuses them).
- Report BOTH pooled (610) and per-seed-122 for direct paper comparison.
- Thresholded % metrics hide boundary shifts: for an ablation fork (no-u),
  also report mean-R2-over-seeds.
- Verify subagent claims and peer corrections against raw artifacts (grep the
  tex; arithmetic on the summary files) before sending or patching.
