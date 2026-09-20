---
name: computational-research
description: Use when conducting computational experiments, simulations, benchmarks, data processing, builds, or prescreen runs for scientific research on the shared Slurm cluster.
---

# Computational research on the cluster

You are working on a shared research cluster. The current login/access node is a
small VMware guest with 2 vCPUs and about 8 GiB RAM (with 2 GiB swap). It is a
shared access node, not a compute allocation. Do not infer compute-node
resources from the login node.

Read the local operational guidance before planning substantial work:

- `~/admin-docs/login-node-resource-guidance.md`
- `~/admin-docs-map.md`

## Absolute execution rule

**Never run computational work directly on the login node with the `bash` tool.**
Always run it inside a Slurm job, including tiny, quick, or exploratory work.
There are no exceptions for prescreen runs.

Computational work includes, at minimum:

- experiments, simulations, training, inference, and evaluation;
- data loading, preprocessing, conversion, and analysis scripts;
- Lean/mathlib builds, compilation, tests, benchmarks, and linters;
- smoke tests, one-off scripts, timing tests, and resource prescreens.

Do not use `bash` to run Python, Lean, R, Julia, MATLAB, compiled programs,
training commands, or similar workloads on the login node. A command being
short or expected to use little CPU does not make it a login-node computation.

The `bash` tool may be used for lightweight file inspection and editing,
version-control operations, read-only scheduler/resource queries, preparing job
scripts, and submitting or inspecting Slurm jobs. The workload itself must
execute on the allocated compute node.

## Required Slurm workflow

Use the Pi Slurm tools for every computation:

1. Submit with `slurm_submit`.
2. Use `slurm_jobs` to inspect tracked jobs and their terminal results.
3. Use `slurm_cancel` only when the job is obsolete, invalid, wedged, or the
   user explicitly asks for cancellation.

If the Slurm tools are unavailable or submission fails, do **not** fall back to
running the workload with `bash` on the login node. Report the blocker and ask
for an approved alternative.

Request only the resources needed for the job. For example, a CPU prescreen
should use the CPU partition with a small CPU and memory request; a GPU
experiment should request an appropriate GPU explicitly. Put stdout/stderr and
intermediate artifacts in a deliberate, persistent path. Include the Slurm job
ID in research notes and preserve enough logging to reproduce the result.

The currently observed cluster limits are:

- `cpu` partition: maximum 4 days;
- `gpu` partition: maximum 3 days;
- the current user association allows up to 7 days per job, but the partition
  limits are stricter for ordinary jobs.

Verify live limits with read-only Slurm queries when they matter; cluster policy
can change.

## Research hygiene

Before submission, make the command, working directory, inputs, outputs,
resource request, and random seeds explicit. Prefer a small Slurm prescreen to
guesswork about memory, runtime, or hardware. Record the job ID, requested
resources, actual result, and relevant log paths in a Markdown research log.

Do not overload the login node with parallel Pi sessions, builds, or analysis.
Idle SSH/tmux infrastructure is acceptable, but it does not authorize running
research workloads locally.
