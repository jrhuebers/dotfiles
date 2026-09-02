---
name: training-run-analysis
description: "Use when analyzing ML training runs and noisy metric logs."
version: 1.0.0
author: huebers (imported from Codex)
platforms: [linux, macos]
---

# Training Run Analysis

## When to Use

Use when interpreting loss curves and noisy metric logs from TensorBoard, W&B, CSV/JSON files, plain logs, or Slurm output — comparing runs, choosing checkpoints, diagnosing instability or overfitting, or recommending next training steps.

Analyze the trajectory of a run before making recommendations. Treat the final logged value as one observation, not as a sufficient summary of training quality.

## Collect and validate the data

1. Identify the metric source and its sampling unit: batch, optimizer step, epoch, evaluation interval, or checkpoint.
2. Load the complete available series for train, validation, and evaluation metrics. Preserve step/epoch numbers and timestamps when present.
3. Check ordering, duplicate points, missing intervals, resumed-run boundaries, NaNs/Infs, metric resets, and changes in learning rate or configuration.
4. Confirm metric direction. Losses are usually minimized; accuracy and other scores may be maximized. Do not compare metrics with different definitions or normalizations without stating the limitation.
5. Report the coverage and resolution of the data. A short tail, sparse checkpoints, or only final values is insufficient for strong trend claims.

Use read-only parsing and existing run artifacts where possible. Prefer TensorBoard/W&B exports or structured logs over scraping console text; fall back to log parsing when necessary.

## Summarize the trajectory

For each important metric, calculate or estimate:

- final value and best-so-far value with their steps
- mean, median, minimum, maximum, and spread over recent windows
- a robust smoothed curve, such as a rolling median or mean, with the window stated
- recent slope or change across multiple windows, not just the last two points
- variability around the local trend, using standard deviation, IQR, or MAD as appropriate
- whether the metric is still improving, plateaued, oscillating, drifting, or deteriorating

Choose windows relative to the data density. For example, compare the last 5–10% of steps with an earlier 5–10% window, while also examining shorter and longer windows when the run is highly nonstationary. Do not over-smooth away a short-lived divergence or sharp failure.

When points are autocorrelated, avoid treating every batch as an independent sample. Use cautious language such as "the recent window is consistently lower" rather than claiming statistical significance from raw point counts.

## Diagnose training behavior

Compare train and validation/evaluation curves on aligned steps or epochs.

- **Improving:** smoothed validation metric improves across several windows and is not dominated by a single outlier.
- **Plateau:** recent windows overlap within observed noise and robust slope is near zero.
- **Overfitting:** training continues improving while validation/evaluation worsens or its gap grows persistently.
- **Instability:** large oscillations, repeated spikes, divergence, NaNs/Infs, or abrupt changes tied to a configuration event.
- **Under-training:** metrics are still improving at the end with no evidence of a plateau; do not recommend stopping solely because the configured step budget ended.
- **Possible regression:** compare against the best checkpoint and prior run, accounting for seed, data order, objective, and evaluation protocol.

Check learning-rate schedules, gradient accumulation, batch-size changes, resume points, data corruption/noise settings, and checkpoint cadence before attributing a pattern to model quality.

## Make recommendations

Recommend actions only after connecting them to measured evidence. Examples:

- Continue training when validation/evaluation is still improving across robust windows.
- Select the best validation checkpoint when the final checkpoint is worse and the gap is persistent.
- Reduce learning rate or investigate optimization when the smoothed curve oscillates without progress.
- Stop or early-stop when validation has plateaued or deteriorated for a sustained patience window.
- Inspect data, numerics, and resource logs when loss spikes, becomes non-finite, or changes abruptly.
- Run multiple seeds or longer evaluation when the apparent difference is comparable to run-to-run noise.

Do not recommend a hyperparameter change from one noisy point, one unusually good batch, or the final value alone. Separate evidence, interpretation, confidence, and proposed action.

## Compare runs fairly

Align runs by optimizer step, consumed examples, or epoch—whichever represents comparable training progress. Verify that datasets, dimensions, objective, loss weighting, evaluation set, seed policy, and effective batch size match. Compare distributions over matched windows, not just the best number ever observed. State when a comparison is confounded.

## Report format

Return a concise evidence-based report containing:

- data sources, metric definitions, and coverage
- best and final values with corresponding steps
- recent-window summary and smoothing choice
- train/validation/evaluation relationship
- diagnosis with confidence and caveats
- recommended next action, including what evidence would change it

If the available logs do not support a reliable conclusion, say exactly what is missing and request the smallest additional artifact needed.
