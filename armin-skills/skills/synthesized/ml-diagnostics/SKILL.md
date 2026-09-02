---
name: ml-diagnostics
description: "Diagnose ML training issues: noisy metric analysis, supervisor-feedback root-cause, CPU/GPU device divergence, and provenance-verified artifact packages."
version: 1.0.0
author: huebers
---

# ML Diagnostics

## When to Use

Use when (1) interpreting noisy loss/metric logs from TensorBoard, W&B, CSV/JSON, or cluster output — comparing runs, choosing checkpoints, diagnosing instability or overfitting; and (2) conducting model diagnostics, stability tests, or collapse investigations under iterative supervisor/audit feedback where root-cause claims may be rejected for methodology flaws.

## Analyzing Noisy Training Metrics

### Collect and validate the data
1. Identify the metric source and its sampling unit: batch, step, epoch, eval interval, or checkpoint.
2. Load the complete series for train, validation, and evaluation metrics. Preserve step/epoch numbers and timestamps.
3. Check ordering, duplicates, missing intervals, resumed-run boundaries, NaNs/Infs, metric resets, and LR/config changes.
4. Confirm metric direction (losses minimized; scores maximized). Don't compare metrics with different definitions without stating the limitation.
5. Report coverage and resolution — a short tail, sparse checkpoints, or only final values is insufficient for strong trend claims.

Prefer TensorBoard/W&B exports or structured logs over scraping console text.

### Summarize the trajectory
For each important metric, calculate or estimate:
- final value and best-so-far value with their steps
- mean, median, min, max, and spread over recent windows
- a robust smoothed curve (rolling median/mean or EMA) with the window stated
- recent slope across multiple windows, not just the last two points
- variability around the local trend (std, IQR, or MAD)
- whether the metric is still improving, plateaued, oscillating, drifting, or deteriorating

Choose windows relative to data density (e.g., compare last 5–10% of steps with an earlier 5–10% window). When points are autocorrelated, avoid treating every batch as an independent sample — use cautious language ("the recent window is consistently lower") rather than claiming statistical significance from raw point counts. Do not over-smooth away a short-lived divergence or sharp failure.

### Outlier detection
Identify spikes with robust statistics (MAD-based or IQR fences) rather than raw min/max. A single outlier should not dominate a trend claim. Flag abrupt changes tied to configuration events (LR schedule, batch-size change, resume point, data corruption) before attributing the pattern to model quality.

### Diagnose training behavior
Compare train and validation/evaluation curves on aligned steps or epochs:
- **Improving:** smoothed validation metric improves across several windows, not dominated by a single outlier.
- **Plateau:** recent windows overlap within observed noise; robust slope near zero.
- **Overfitting:** training improves while validation worsens or the gap grows persistently.
- **Instability:** large oscillations, repeated spikes, divergence, NaNs/Infs, or abrupt changes.
- **Under-training:** metrics still improving at the end with no plateau evidence — do not recommend stopping solely because the step budget ended.
- **Possible regression:** compare against the best checkpoint and prior runs, accounting for seed, data order, objective, and evaluation protocol.

### Compare runs fairly
Align runs by optimizer step, consumed examples, or epoch. Verify datasets, dimensions, objective, loss weighting, evaluation set, seed policy, and effective batch size match. Compare distributions over matched windows, not just the best number ever observed. State when a comparison is confounded.

### Make recommendations
Recommend actions only after connecting them to measured evidence. Do not recommend a hyperparameter change from one noisy point, one unusually good batch, or the final value alone. Separate evidence, interpretation, confidence, and proposed action. If logs do not support a reliable conclusion, say exactly what is missing and request the smallest additional artifact needed.

## Diagnosing Model Issues Under Supervisor Feedback

### Core principle: artifact-rigorous diagnostics
**Never substitute fresh instances for the actual trained/produced artifacts.**

| What you might do | What the audit expects |
|-------------------|------------------------|
| Instantiate fresh model for diagnosis | Load the ACTUAL trained checkpoint |
| Run a toy approximation of a sampler | Run the ACTUAL production reverse-SDE pipeline |
| Save summary statistics only | Save raw stage NPZ arrays for per-stage diagnostics |
| Assume checkpoint was saved | VERIFY the checkpoint file exists (it may not) |

Never claim to load a checkpoint without verifying it exists. Never diagnose with a fresh model — the trained weights matter. Never run a toy sampler when the real pipeline is available. Summary-only diagnostics are insufficient — save raw arrays.

### Supervisor/audit feedback patterns

| Feedback | Meaning | Action |
|----------|---------|--------|
| "verifier-only" / "not a producer" | You're verifying artifacts, not running the producer | Accept label, don't overclaim |
| "preserved unchanged" | Don't touch that path/family | Use a new directory |
| "root-cause rejected" | Your diagnosis method is flawed | Check for artifact substitution |
| "provenance gap" | Something expected is missing | Explicitly document the gap |

### Unit test vs runner integration
Checking imports/strings is NOT integration. A smoke test exercises a model forward pass in isolation; runner integration requires actually calling the production benchmark/dispatch function with full dispatch and seed control. Both are valid, but claiming runner integration requires calling the real function (or a shared dispatch used by it). Always set the seed (`seed_everything` / equivalent) before any model instantiation — without it, independent reruns produce different values. Never just print "PASS" — fail-closed with `sys.exit(1)` on error. Capture stdout/stderr to files.

### Metric comparison pitfall
When comparing a surrogate vs an authoritative metric, they must use the SAME formula. If formulas differ, the "mismatch" is methodological, not a real comparison. Always verify the metric computation method matches between compared artifacts.

## Provenance & Artifact Patterns

### Immutable artifact families
Produce supervisor-grade artifact packages with strict provenance:
- **Producer writes inside the artifact directory** — explicit `os.chdir()` so relative paths resolve correctly (avoid output-path closure where results land in the wrong place).
- **Atomic writes for JSON and NPZ** — temp file + `os.rename`; never leave a partial file on crash.
- **Never overwrite a prior family** — fail with `sys.exit(1)` if the output directory already exists. Rerunning must not destroy prior evidence.
- **Recursive validation** — all numeric fields, shapes, dtypes, finiteness (`allow_nan=False`).
- **Raw sample propagation** — propagate all raw keys through shared dispatch; don't silently drop `return_raw` data.
- **Shared dispatch must be CALLED** — dead code that is defined but never invoked does not count.
- **Induced failure test** — run with a failure-injection flag; preserve the exit=1 run.
- **Deterministic rerun** — run multiple times, compare hashes; record `rerun_match` boolean.
- **Capture all runs** — preserve stdout/stderr for normal, induced-failure, and rerun.

### Manifest contents
- Input hashes: all source files (not just main scripts — track all dependencies)
- Data hashes: train/test/adjacency/Laplacian or equivalent
- Baseline hashes: hash forbidden paths BEFORE execution, compare AFTER
- Output hashes: all stdout/stderr/NPZ/JSON files
- Run info: exit codes for all runs, `rerun_match` boolean
- Explicit cell/file → keys → shapes mapping

### JSON self-referential hash pitfall
A JSON file cannot contain its own hash — adding the hash field changes the file and invalidates the hash. Don't include a self-referential hash; use the NPZ hash to verify data, trust JSON for metadata.

### Selected-cell isolation
When a benchmark supports subset execution, guard ALL cells — not just the target subset. Verify via stdout that only selected cells ran. Derive `executed_cells` mechanically from returned results, not by hand. Watch for boolean-precedence bugs in summary filters (`and`/`or` mixing); use explicit membership checks.

### Fail-closed checks
- Required files missing → `FileNotFoundError` / `sys.exit(1)`.
- Validate per-seed (not globally): shape, finiteness, metric recomputation match.
- Slurm may show COMPLETED but a Python step is CANCELLED — check stderr/stdout for "CANCELLED" and treat as failure.

## CPU/GPU Paired Comparison & Divergence Detection

### Paired comparison methodology
When verifying device consistency, run BOTH CPU and GPU with IDENTICAL configuration (single source of truth for epochs, samples, seed). The supervisor rejects CPU/GPU comparisons when protocols differ ("protocol drift"). Use minimal config (epochs=1, samples=2) for the paired consistency check; report full GPU runs separately as standalone training results.

Pass config via environment variables or f-string interpolation — never hardcode mismatched values in producer vs wrapper. Slurm may pre-create the output directory before the script runs — check for actual artifacts, not just directory existence.

### Divergence localization
To isolate the first divergent operation between CPU and GPU:

1. **Production hooks:** Inject diagnostics directly into production functions (not wrapper scripts). Capture hashes/tensors at every key stage inside the real pipeline.
2. **State capture/replay:** Serialize exact CPU state (batch indices, inputs, noise, model `state_dict`, time, RNG) to a bundle; load that exact state on GPU for deterministic replay.
3. **Per-component analysis:** Compare each computation stage separately with tolerances:
   ```python
   def max_abs(a, b): return float((a - b).abs().max())
   def max_rel(a, b):
       diff = (a - b).abs()
       denom = (a.abs() + b.abs()).clamp_min(1e-8)
       return float((diff / denom).max())
   TOLERANCE = 1e-5
   ```
   Report per-component `max_abs`, `max_rel`, and pass/fail against tolerance.

Typical finding: core computations (mean, std, forward state, score) are identical within 1e-6, but a downstream operation (e.g., a sampler clamp) diverges due to device-specific saturation behavior. The root cause is often a single operation that behaves differently on GPU after initial saturation.

## GAD/VPSDE Endpoint Issues

### Model collapse root cause
A common collapse pattern: unnormalized training data + a fixed clamp range + a standard-normal prior → the model outputs a constant near the clamp boundary regardless of input.

Ablation to isolate:
- Raw + clamp → COLLAPSE to constant
- Raw, no clamp → EXPLODE (unbounded magnitudes)
- Standardized + clamp → HEALTHY (correct mean/std, diversity)
- Standardized, no clamp → UNSTABLE (large variance)

Fix: standardize training data before clamping. The clamp range must be calibrated to the standardized scale, not the raw scale.

### Common VPSDE endpoint bugs
- Creating layers inside `forward()` instead of registering them in `__init__` (e.g., `nn.Linear` constructed per call). Fix: register all layers in `__init__`, reference via `self.`.
- Missing imports of new model classes in the runner.
- SDE type mismatch (GASDE/VPSDE/VESDE) between training and evaluation — always pair the correct SDE object with the corresponding train/evaluate function.

## Key Pitfalls

- Never substitute fresh instances for the actual trained artifacts.
- Never claim to load a checkpoint without verifying it exists.
- Summary-only diagnostics are insufficient — save raw arrays per stage.
- Never overwrite a prior artifact family — create a fresh immutable directory.
- Atomic writes must cover NPZ too, not just JSON.
- All dependency hashes must be tracked, not just main files.
- A "CANCELLED" Python step must trigger failure even if the Slurm batch shows COMPLETED.
- Do not recommend changes from one noisy point or the final value alone — use robust windows.
- Paired CPU/GPU comparisons require identical config — protocol drift is rejected.
