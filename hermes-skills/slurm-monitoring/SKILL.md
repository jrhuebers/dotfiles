---
name: slurm-monitoring
description: "Use when checking GPU/queue availability on a Slurm cluster."
version: 1.0.0
author: hermes-curator
license: MIT
platforms: [linux]
metadata:
  tags: [hpc, slurm, gpu, monitoring, dashboard]
  related_skills: [start-slurm-job]
---

# Slurm Cluster Monitoring

## When to Use

Use when the user asks how many GPUs are free, what the queue/pending pressure
looks like, which allocations are running what, or wants a live resource
dashboard. Complements the job-submission workflow (start-slurm-job skill).

## Counting free GPUs (authoritative recipe)

- `sinfo -N -o "%n %G %e %t"` — **`%e` is FREE MEMORY, not free GPUs**. It
  shows node state (mix/alloc/idle) but never per-GPU availability. Don't use
  it for GPU counts.
- Authoritative per-node count comes from AllocTRES:

```bash
scontrol show nodes | awk '/^NodeName=/{split($1,a,"="); node=a[2]} /AllocTRES=/{n=$0; sub(/.*gres\/gpu=/, "", n); sub(/,.*/, "", n); print node, n"/8"}'
```

  free per node = 8 - alloc (adjust total per `Gres=` line).
- Cross-check with the per-job view (only RUNNING jobs actually hold GPUs):

```bash
scontrol show jobs | awk '/JobId=/{jid=$1; st=""} /JobState=/{st=$0} /AllocTRES=/{if (st ~ /RUNNING/ && match($0, /gres\/gpu=[0-9]+/)) {v=substr($0, RSTART+9, RLENGTH-9)+0; s+=v}} END {print s}'
```

  The two numbers (per-node sum, per-job sum) must match; if they disagree a
  parsing error crept in.

### Counting pitfalls (all hit in practice)

- `scontrol show jobs` prints `ReqTRES=`, `AllocTRES=` AND `TRES_PER_NODE=`
  lines. Matching bare `/TRES=/` triple-counts. Match `/AllocTRES=/` only.
- `TRES_PER_NODE=` also starts with "TRES" — same trap.
- `squeue -o "%b"` prints TRES_PER_NODE abbreviated as `gres/gpu` with no
  `=N` — useless for summing.
- PENDING jobs have TRES too: a sum over all active jobs (196 jobs, 215 GPUs)
  wildly exceeds capacity. Restrict to JobState=RUNNING.

## squeue format-code gotchas

- `%l` (lowercase) = TIME LIMIT (total). `%L` (uppercase) = TIME LEFT
  (remaining). A "limit" column built on `%L` silently shows remaining time —
  verify with `%l` when displaying elapsed/limit pairs.
- `%T` is INVALID in step-format strings (`squeue --steps -o "%T"` errors with
  "Invalid job step format specification"). Use `scontrol show step <jobid>`
  for step state instead.

## Per-allocation GPU reads (srun join + cgroup restriction)

To read the GPU of a specific allocation (e.g. a joinable allocation like
apple/banana/coconut) from the login node:

```bash
srun --jobid=<id> --overlap --cpu-bind=none --ntasks=1 nvidia-smi \
  --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu,uuid \
  --format=csv,noheader,nounits
```

- `--cpu-bind=none` avoids "CPU binding outside of job step allocation".
- Cgroup device restriction: the step sees ONLY the allocation's own physical
  GPU — `nvidia-smi -L` shows a single remapped "GPU 0" and
  `CUDA_VISIBLE_DEVICES` is empty. Verified: two 1-GPU allocations on the same
  node each see a different card (different UUIDs). Include `uuid` in the
  query to identify the physical card.
- Therefore query PER ALLOCATION, not per node — a node-level dedupe shows
  only one allocation's card. Parallelize the srun probes
  (ThreadPoolExecutor) or the refresh cycle takes 3x as long.
- Each probe appears transiently as a step named "nvidia-smi" in the target
  allocation — filter it out of step listings.

## OOM-killed but the node has free RAM? Check the JOB cgroup, not the node

Symptom: a heavy single-process tool (e.g. marker-pdf, ~11GB RSS model stack)
dies with exit 137 / "Killed" while `free -g` shows hundreds of GB free.
The limit is NOT the node — it is the job-level cgroup. On this cluster:

- A slurm JOB's cgroup (`/sys/fs/cgroup/system.slice/slurmstepd.scope/job_<id>/`)
  carries `memory.max` (e.g. 17179869184 = 16GB) even when the per-task cgroup
  shows `max`/unlimited. Diagnose in order:
  1. `cat /proc/self/cgroup` → your task cgroup path, walk one level UP to the job.
  2. `cat .../job_<id>/memory.max` and `memory.events` — `oom_kill` counter > 0 proves the kill.
  3. `cat .../job_<id>/memory.current` — how full the shared budget is.
- **Steps are SHARED across users**: other users' jobs running in the same
  step (visible via `ps -eo pid,rss,comm --sort=-rss` as their python/torch
  processes) consume the same 16GB. `free` and `ulimit -a` look fine the
  whole time. Always check `memory.current` before launching a memory-heavy
  job into a shared/joined step, and prefer the 64GB joinable allocations
  (apple/banana) for anything needing >~8GB RSS.
- A process killed this way can silently degrade results: a wrapper with a
  fallback chain may emit low-quality output without failing (see
  ocr-and-documents skill — `pdf2md` prints `marker failed, falling back...`
  to stderr; check it when extraction quality matters).

## Steps (jobs) running inside an allocation

`scontrol show step <jobid>` blocks: `StepId=` line also carries
`StartTime=` on the SAME line; continuation lines carry `State=` and a
mid-line `Name=` token (`Nodes=1 CPUs=8 Tasks=1 Name=python Network=(null)`)
— scan tokens for `Name=`, don't expect it at line start. `Name=` gives the
executable only, not full args. `.batch` = the allocation's holder script,
`.extern` = slurm extern, numbered steps = joined user commands.

## Persistent-allocation watchdog cron gotcha (Hermes cronjob)

A watchdog created with `repeat=1` runs ONCE, then silently completes
(state=completed, enabled=false) — allocations stop being maintained with no
alert. `cronjob update <id> repeat=0` makes it run forever. After
creating/updating, confirm `cronjob list` shows enabled=true,
state=scheduled, repeat=forever. `no_agent=true` + a script that prints only
when it acts keeps recurring runs silent when healthy.

## Detecting stuck orphaned processes in an allocation

Not all work in an allocation is tracked as Slurm steps. A manually launched
`bash -c "python scripts/benchmark.py"` process runs in the job's cgroup but
is invisible to `squeue --steps -j <id>` — it shows only `.batch`/`.extern`
plus any `srun`-launched steps. Symptoms of stuck orphaned processes:

- `ps aux` shows python processes at 99.9% CPU, STAT=Rl (running)
- `nvidia-smi` shows 0% GPU utilization (GPU idle despite "running" work)
- Log files not written to in 1-4 days (check `stat -c %y <log>`)
- The process is in a tight CPU loop but making no forward progress

Diagnostic recipe (run from login node into the allocation):

```bash
# Check for non-Slurm python processes in the allocation's cgroup
srun --jobid=<id> --overlap --cpu-bind=none --mem=2G bash -c '
  echo "=== Slurm steps ==="; scontrol show step <id> 2>/dev/null | grep StepId
  echo "=== Python processes ==="; ps -eo pid,etime,stat,%cpu,%mem,args | grep python | grep -v grep
  echo "=== GPU ==="; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
  echo "=== Recent log writes ==="; ls -lt /path/to/logs/*.log 2>/dev/null | head -5
'
```

If processes are stuck (high CPU, zero GPU, stale logs): kill them with
`kill -9 <pid>` via srun, then scancel the job if the allocation is no
longer needed. Stuck processes on face-basis computation (chameleon dataset,
~29K faces) were found this way — 5 processes burning 5 CPUs for days with
zero GPU use and no log output.

## Live dashboard

`~/.local/bin/allocation-dashboard` — 5s-refresh tmux dashboard for the
apple/banana/coconut persistent allocations: state, node, time left, steps
inside each, and the allocation's own GPU util/mem/UUID. flock-guarded
(single instance), parallel probes. Launch: `tmux new-window -n alloc
allocation-dashboard`. Pattern generalizes to any set of named allocations.

## Overlap note

start-slurm-job (user-owned, not curator-managed) documents the
apple/banana/coconut system itself (creation commands, join syntax, watchdog
script, mission-control sshd). This skill carries the monitoring recipes that
grew out of that system. If start-slurm-job is ever adopted
(`hermes curator adopt start-slurm-job`), fold the monitoring section there
or cross-link deliberately.
