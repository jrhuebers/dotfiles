---
name: computational-research
description: Use for computational experiments and research workloads on the shared Slurm cluster.
---

You are on a shared research cluster. The login/access node is a small VMware
VM with 2 vCPUs, about 8 GiB RAM, and 2 GiB swap; it is not a compute
allocation. See `~/admin-docs/login-node-resource-guidance.md` and
`~/admin-docs-map.md` for local guidance.

**Never run computations directly on the login node with `bash`.** This rule
also applies to quick experiments, smoke tests, builds, data processing, and
prescreen runs. Run all such work through the Pi Slurm tools:

1. Submit with `slurm_submit`.
2. Inspect jobs and results with `slurm_jobs`.

If Slurm submission is unavailable, do not fall back to running the workload on
the login node; report the blocker instead. `bash` is limited to file
inspection/editing, Git, read-only scheduler queries, and preparing or
submitting jobs. Do not run Python, Lean, R, Julia, MATLAB, benchmarks, or
similar workloads there.

Request suitable resources, preserve job IDs and output paths, and record the
job and its result in a Markdown research log.
