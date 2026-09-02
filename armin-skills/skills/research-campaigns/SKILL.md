---
name: research-campaigns
description: "Autonomous research campaigns on HPC: slurm batches, logs."
version: 1.0.0
---

# Research Campaigns (autonomous scientific experimentation)

## When to Use

Use when the user asks you to autonomously "do research", "test ideas", "figure
out what works", or run experiments comparing methods — especially on an HPC
cluster with slurm and a git repo containing an experiment codebase. The class
is: hypothesis -> controlled experiment batch -> diagnostics -> research log ->
iterate, without pestering the user.

Also load `slurm-job-watch` (job submission/monitoring) and
`training-run-analysis` (metric interpretation) alongside this skill.

## Workflow

1. **Survey first**: README, configs, tests, existing run dirs (they encode
   prior work and conventions), GPU/partition availability (`squeue -p <part>`
   counts running vs pending), registry/heartbeat conventions.
2. **Write the research log BEFORE running**: `documentation/research_log.md`
   (or similar) with the hypothesis, the success metric, the matched budget, and
   the theory. Commit it. The log is the deliverable the user reads.
3. **Controlled experiments**: baseline + variants at IDENTICAL budget (steps,
   batch size, seed, model size unless the variant is architectural). One knob
   per variant. Name runs `w1-<method>` etc. so batches are greppable.
4. **Batch launcher script** (per wave): one bash function that sbatch's a job
   per variant with `--parsable` to capture job IDs. Keep total concurrent jobs
   within the user's limit (ask or infer; this user: 8). Prefer explicit
   `--output=slurm-logs/<name>-%j.out`.
5. **Monitor via per-run log FILES, not slurm .out** — see pitfalls.
6. **Diagnostics beyond the headline metric**: measure WHY (map regularity,
   discrepancy, curvature, gradient norms). A diagnose script per model dir that
   saves summary.yaml makes batch comparison trivial.
7. **Update the research log after each wave** with a results table and
   findings; commit code + log together.
8. **Iterate**: winners -> longer runs, higher dimensions, new benchmarks
   (incl. low-intrinsic-dimensionality cases).

## User preferences (this user — embed, don't re-ask)

- **Multi-seed evaluation**: average over >= 3 training seeds x >= 8 eval
  replicates for any headline claim. Single-seed runs are fine for screening,
  but flag them as such. ("in my experience its important to average over
  multiple seeds for the evaluations")
- **File logging**: every training run dir gets a `.log` file (metrics,
  config, start/end), not just wandb. ("there should also be a .log file in
  every run dir")
- **CPU fallback**: if the GPU partition is saturated, run on the CPU
  partition with `OMP_NUM_THREADS=8` instead of queueing forever. 2D MLP
  training is often only 2-4x slower on CPU.
- **Benchmark coverage**: include low-intrinsic-dimensionality / manifold
  targets (support dimension < ambient dimension), not only full-dim support.
- **Autonomy**: user wants the agent to proceed without intervention; keep the
  research log current so the user can review asynchronously.

## Pitfalls (all hit and fixed in practice)

- **hydra `job_logging=disabled` silently kills your logger**: its dictConfig
  sets `disable_existing_loggers: true`, flagging existing loggers
  `disabled=True` so FileHandler writes vanish (file exists, 0 bytes). Fix:
  `logger.disabled = False` after attaching your handler.
- **hydra CLI override of a NEW key dies with "Could not override ... Key is
  not in struct"**: `loss.reg.penalty_cap=8` fails until the key exists in
  the baseline config. Fix: add the key to the baseline defaults first
  (`penalty_cap: null`) then override normally, or use the `+` prefix
  (`+loss.reg.penalty_cap=8`) to append. Adding to defaults is better —
  the key then shows in `--cfg job` and recipes can reference it.
- **`sbatch --wrap` cannot take script arguments** and nested quotes break it.
  Fix: write the arg list to a file and have the wrap run a driver script that
  reads it; or embed args in the wrap string, never `"$@"`.
- **Python stdout to a slurm .out file is block-buffered** — metrics appear
  minutes late or only at exit. Log to a file in the run dir instead.
- **Concurrent parallel jobs writing a shared YAML registry corrupt it**
  (read-modify-write race). Wrap writes in `fcntl.flock`.
- **`torch.linalg.svdvals` returns DESCENDING singular values** — index 0 is
  the max; swapping them yields condition numbers < 1 (impossible) that are
  easy to miss.
- **Aux-loss weight scale check**: log the raw regularizer value early. If
  weight x value < ~1% of the main loss, the run is effectively the baseline
  (e.g. weight 0.001 x penalty 2.8 = 0.003 vs loss 5.5 — negligible). Verify
  the term actually fires (log the loss key) before trusting the run.
- **GPU partitions can look idle on CPUs yet be saturated on GPU slots**
  (85 running / 20 pending while CPUs idle). Check `squeue -p` job counts
  before waiting.
- **CUDA/torch build — check before assuming incompatibility**: cluster
  drivers are upgraded periodically. As of 2026-08-20 drivers are 580.167.08
  (CUDA 13.0) and BOTH cu128 and cu130 torch wheels work. Previously
  (570.x / CUDA 12.8) the default cu130 wheel reported
  `torch.cuda.is_available() == False` ("NVIDIA driver too old"); that is no
  longer the case. The prebuilt `~/.venvs/torch-cu128` and `~/.local/bin/torch-gpu`
  wrapper remain a safe default. Before debugging "CUDA not available", run
  `nvidia-smi --query-gpu=driver_version --format=csv,noheader` to check the
  actual driver — the failure mode only persists on nodes that haven't been
  upgraded yet.
- **Verify kills actually landed** (hit twice): `scancel <id>` can silently
  miss when the job name matched by grep isn't a substring of the real name
  (job `fm-ot30d-b512` did NOT match grep `ot-b512` — the '30d' breaks it);
  and `srun --jobid=X --overlap bash -c 'pkill -f <pattern>'` can terminate
  the srun step while the python child SURVIVES as an orphan still holding
  the GPU (2 training processes shared one card, halving throughput).
  After any cancel/kill: `squeue -u <user>` for jobs AND
  `srun --jobid=<alloc> --overlap bash -c 'ps aux | grep <proc>'` on the
  allocation node to confirm the process is really gone.
- **Wait-loop launchers with stale run-dir names hang forever**: a
  `while ! ls models/<name>-*/checkpoint... ; do sleep 60; done` launcher
  that started BEFORE a rename/sed fix keeps polling the old name — kill
  and restart the launcher, don't wait for it.
- **Checkpoint poisoning on NaN**: the final checkpoint.pt can be NaN
  (54/55 tensors) while periodic checkpoints are clean — check
  `torch.isnan(v).any()` over the state_dict before evaluating; swap the
  last clean periodic checkpoint into place (backup the NaN one).
- **Log-parsing shapes drift between eval types**: GMM eval
  `evaluation/summary.yaml` nests under `complex`/`second` with N per
  method; `evaluation_real/summary.yaml` has no such nesting; oracle and
  structured evals use different method keys (oracle-MC, S-QMC). Grep the
  file's top-level keys before writing a parser, or access
  `s[methods[0]]['N']` defensively.
- **`python -m <module>` can exit 0 with ZERO output (silent no-op)**:
  hit with `uv run python -m diffusion_qmc.cli.evaluate_oracle`,
  `full_eval_driver.py`, `eval_dim_ordering` — command returns cleanly but
  nothing prints and nothing ran, looking like a hang/success. Workaround
  that always works: run the module's `main()` directly, e.g.
  `python -u -c "import sys; sys.argv=[...]; from <mod> import main; main()"`
  (or runpy.run_path for scripts). If a CLI is silent, suspect this before
  debugging the code.
- **Double-backprop Jacobian penalties (strain/lip_pen) OOM at batch 256
  even on 80GB**: the VJP+JVP with create_graph doubles memory. Compute
  the penalty on a subsample of the batch (`penalty_batch=64`) — it's a
  Hutchinson estimate, batch size only affects estimate quality. Also use
  `interval=100` (regularizer, not main loss) and `probes=1`; at
  interval=10 a 100k-step run takes ~6.5h instead of ~2h. Full detail in
  `references/qmc-flow-matching-findings.md` (smooth log1p variant for
  gradient stability).

## Support files

- `references/qmc-flow-matching-findings.md` — domain findings for the
  diffusion-qmc project (method inventory, what worked / failed, theory).
- `references/cuda-torch-compatibility.md` — driver history, torch wheel
  compatibility matrix, and verification commands for gwkilab GPU nodes.
