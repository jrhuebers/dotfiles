---
name: slurm-ops
description: "Portable Slurm operations: submit jobs, check GPUs/queues, inspect allocations, build live dashboards. Use for any sbatch/squeue/srun/sacct/scontrol workflow on a Slurm cluster."
version: 1.0.0
author: huebers
platforms: [linux]
metadata:
  tags: [hpc, slurm, gpu, monitoring, sbatch, squeue]
---

# Slurm Ops

Portable Slurm cluster operations: job submission, resource counting,
allocation inspection, and live dashboards. All commands are standard
Slurm CLI (`sbatch`, `squeue`, `srun`, `scontrol`, `sacct`, `scancel`),
verified on Slurm 25.11 / cgroup v2.

## 1. Job submission

### Walltime: default 14 days

Default `--time=14-00:00:00` unless the user requests shorter or the workload
has a hard internal bound. A short `--time` is NOT how you schedule a "short"
job — the job releases its allocation the moment the command finishes, so a
long limit costs nothing. A too-short limit only risks `TIMEOUT` on healthy
long work and can hurt queue position. Short limits are fine for genuinely
bounded smoke tests, but never the default.

### sbatch essentials

1. Resolve partition, account, walltime (default 14d), GPU/CPU resources,
   workdir, command, output path. Preserve the user's requested resources.
2. Submit with `sbatch`, capture the job ID from `Submitted batch job <id>`.
3. **Always set an explicit output path**:
   `--output=~/slurm-logs/<name>-%j.out --error=~/slurm-logs/<name>-%j.err`.
   If none given, find the effective `StdOut` with `scontrol show job <jobid>`.
4. Use Bash explicitly for multi-command bodies. `sbatch --wrap` runs under
   `/bin/sh` on some clusters — bare `--wrap='set -euo pipefail; ...'` may
   fail. Prefer a `#!/usr/bin/env bash` script or `bash -lc` wrapping.
   `--wrap` does not accept script args — embed them in the string.
5. **Fine-grained progress logging is mandatory**: run python with `-u` (or
   `flush=True`); print a progress line every few minutes with cumulative
   work (`step 25000/100000`, `epoch 3/10`) + wall-clock timestamp + ETA when
   cheap. Bash: `echo "[$(date +%H:%M:%S)] phase ..."`.
6. Don't cancel pending/running/failed jobs unless the user asks.

### Patterns

Simple: `sbatch --job-name=myjob --partition=GPU1 --gres=gpu:1 \
--cpus-per-task=8 --mem=64G --time=14-00:00:00 --output=~/slurm-logs/%x-%j.out \
--error=~/slurm-logs/%x-%j.err --wrap='exec python -u train.py'`

Persistent holder: add `--wrap='exec sleep infinity'` to keep an allocation
alive for joining (see §5).

If a job quickly FAILs, inspect stderr — `Illegal option -o pipefail` means
the wrong shell ran (use bash explicitly).

## 2. Joining an allocation (srun --overlap)

```bash
srun --jobid=<id> --overlap --cpu-bind=none --chdir=/workdir <command>
```

- `--overlap` lets the step launch without claiming the job's resources.
- `--cpu-bind=none` is **required** — without it srun fails with `CPU binding
  outside of job step allocation`. `--exact` fails the same way.
- Read-only inspection: add `--gres=gpu:0 --mem=2G`. Note `--gres=gpu:0`
  means nvidia-smi shows "No devices found" — run nvidia-smi from within the
  job's own session or use `--gres=gpu:1` (may block if job holds all slots).

### One worker per allocation

Before joining, check `scontrol show step <id>`. If another worker's step
(non-`.batch`/`.extern`) is running inside, pick a different allocation.
Holder steps (`.batch`/`.extern`/`sleep infinity`) don't count.

### MaxStepCount: don't exhaust the step budget

Every `srun --overlap` creates a NEW step. Slurm caps steps per job
(`MaxStepCount`, stock default **40000**; `scontrol show config | grep
MaxStepCount`). A loop spawning a transient join every 5s burns ~17K
steps/day → exhausted in ~2.3 days. `MaxSteps` cannot be raised on a
RUNNING job — only resubmission recovers it. **Fix**: for repeated
sampling, spawn ONE long-lived step per job that loops internally rather
than a new srun per refresh.

## 3. Counting free GPUs

**Do NOT trust `sinfo -N -o "%n %G %e %t"`**: `%e` is FREE MEMORY, not free
GPUs; `%G` shows configured capacity, never what's free. Ground truth is
`scontrol show nodes` — compare configured `Gres=` vs `AllocTRES=` per node.

```bash
bash scripts/gpu_free.sh   # per-node used/free by GPU type + cluster total
```

### Counting traps (all hit in practice)

1. Per-node: sum `AllocTRES` `gres/gpu=N`; free = capacity − sum. Authoritative.
2. **Never sum `gres/gpu` across `scontrol show jobs` naively.** A bare
   `/TRES=/` match hits three lines: `ReqTRES` (PENDING → overcount, e.g.
   215), `AllocTRES` (correct), `TRES_PER_NODE` (double-count, e.g. 200).
   Only `AllocTRES=` with `JobState=RUNNING` counts.
3. Cross-check per-node sum == per-job sum. Disagreement = wrong line matched.
4. awk off-by-one: `gres/gpu=` is 9 chars → `substr($0, RSTART+9, RLENGTH-9)`.
5. CPU-partition jobs on GPU nodes hold 0 GPUs. A node at 8/8 with few
   visible jobs = whole-node allocations by others. Trust AllocTRES.
6. PENDING/held jobs inflate request sums; only RUNNING `AllocTRES` counts.
7. Quote a GPU number only after two independent methods agree.

### Per-job GPU read (cgroup restriction)

```bash
srun --jobid=<id> --overlap --cpu-bind=none --ntasks=1 nvidia-smi \
  --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu,uuid \
  --format=csv,noheader,nounits
```

A join into a GPU job sees ONLY that job's own physical GPU (`nvidia-smi -L`
shows one remapped "GPU 0"; `CUDA_VISIBLE_DEVICES` empty; UUID identifies
the card). A join into a CPU-only job sees no GPUs. Query **per allocation,
not per node** — parallelize the probes or the refresh cycle takes 3× longer.
Each probe appears transiently as a step named "nvidia-smi" — filter from
listings.

## 4. Queue checking

```bash
squeue -o "%.10P %.8u %.8T %.10M %.6D %R"
```

Count PENDING jobs and read reasons (Priority / Resources / held). squeue
format gotchas:
- `%l` (lowercase) = TIME LIMIT; `%L` (uppercase) = TIME LEFT — easy to mix
  up. A "limit" column on `%L` silently shows remaining time.
- `%T` is invalid in step-format strings — use `scontrol show step` instead.
- `%M`/`%l` use MM:SS for durations < 1h — parse 2-part times or fresh jobs
  crash duration parsers. UNLIMITED/empty need guards.
- `%b` = TRES (has "gpu" if job has GPUs); `%C` = allocated CPUs.

## 5. Inspecting jobs and steps

### scontrol show job / step

`scontrol show job <jid>` → `JobState=`, `RunTime=`, `TimeLimit=`, `StdOut=`,
`SchedNodeList=` (PENDING target node).

`scontrol show step <jid>` — steps inside an allocation. Parsing:
- `StartTime=` is ON the `StepId=` line, not its own line.
- `Name=` is mid-line (`Tasks=1 Name=python`), not line-start.
- `.batch` = batch holder; `.extern` = slurm extern; numbered = joined work.
- No `Command=` field; `squeue --steps` `%o` is empty — can't distinguish
  steps by command, only by name/age.

### sacct

`sacct -j <jid> --format=JobID,Start,State,Elapsed,ExitCode -P` —
historical accounting, step attribution. `sstat`/`sacct` may return EMPTY
if no `jobacct_gather` plugin is configured — don't rely on them for live
metrics.

### Stuck orphaned processes

A manually launched `bash -c "python script.py"` runs in the job's cgroup
but is invisible to `squeue --steps`. Symptoms: python at 99.9% CPU (STAT=Rl),
0% GPU util, stale logs. Diagnose via srun join:

```bash
srun --jobid=<id> --overlap --cpu-bind=none --mem=2G bash -c '
  scontrol show step <id> 2>/dev/null | grep StepId
  ps -eo pid,etime,stat,%cpu,%mem,args | grep python | grep -v grep
  nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
  ls -lt /path/to/logs/*.log 2>/dev/null | head -5'
```

If stuck: `kill -9 <pid>` via srun, then `scancel <jid>` if no longer needed.

### OOM-killed but node has free RAM

The limit is the **job-level cgroup**, not the node:
1. `cat /proc/self/cgroup` → walk UP to `job_<id>/`.
2. `cat .../job_<id>/memory.max` (e.g. 16GB) and `memory.events` —
   `oom_kill` > 0 proves the kill.
3. `cat .../job_<id>/memory.current` — how full the budget is.

Steps can be SHARED across users — others' jobs consume the same memory
budget while `free`/`ulimit` look fine. Check `memory.current` before
launching memory-heavy work into a shared/joined step. `memory.current`
includes reclaimable page cache; `grep -E "^anon |^file " memory.stat`
splits real committed memory (anon) from cache — OOM risk tracks anon.

## 6. Job log hygiene

- Without explicit `--output`/`--error`, logs land in the submission dir.
  Always use `--output=~/slurm-logs/<name>-%j.out --error=~/slurm-logs/<name>-%j.err`.
- **Moving RUNNING jobs' logs is safe**: `mv` follows open inodes; Slurm's
  writes continue to the moved file. No restart needed.
- `scontrol show job <jid>` reveals the effective `StdOut` if none was given.

## 7. GRES naming

Slurm GRES type names use **hyphens** in the model suffix, not underscores:
`nvidia_a100-sxm4-40gb`, `nvidia_a100-sxm4-80gb`. The vendor prefix
underscore (`nvidia_`) is standard; the model suffix uses hyphens.

```bash
--gres=gpu:nvidia_a100-sxm4-80gb:1   # specific 80GB A100
--gres=gpu:1                          # any GPU
```

Verify types on a node: `scontrol show node <name>` → `Gres=` line, e.g.
`gpu:nvidia_a100-sxm4-40gb:8(S:1,3,5,7)`.

## 8. Allocation persistence

Long-lived joinable allocations (`sleep infinity` holders) let routine work
skip the scheduler queue during traffic spikes:

1. **Submit holder**: `sbatch --wrap='exec sleep infinity' --time=14-00:00:00`
   with a GPU partition and explicit log paths.
2. **Watchdog**: a cron job checks every ~4h and resubmits when missing or
   < 12h walltime left. Verify the cron is enabled — recurring schedules
   can be found disabled/completed. A `repeat=1` cron runs ONCE then silently
   completes; use indefinite repeat.
3. **Join, don't resubmit**: when the queue is saturated, `srun --jobid=<id>
   --overlap --cpu-bind=none <cmd>` instead of a new job.
4. **Single worker per allocation**: check `scontrol show step <id>` before
   joining; if another worker is active, pick a different allocation.

### GPU memory sizing

Persistent allocations may have different GPU memory sizes (e.g. 40GB vs
80GB A100s). Size GPU requests to the allocation's card, not the node's max.
If a specific tier is required, add `--gres=gpu:<type>:1` or a node constraint.

## 9. Live dashboard concepts

### Data sources

| Need | Source | Notes |
|---|---|---|
| Job list/state | `squeue -u <user> -o "%i %j %T %M %l %R %b %C"` | %l=limit, %L=left; %b=TRES; %C=CPUs |
| Per-job GPU | persistent join step (nvidia-smi via `srun --overlap`; include `uuid`) | one card per join (cgroup-restricted) |
| Per-job CPU+RAM | cgroup v2 `job_<jid>/`: `cpu.stat`, `memory.current`, `memory.max` | readable inside the join |
| Steps | `scontrol show step <jid>` | StartTime on StepId line; Name mid-line |
| Pending target | `scontrol show job <jid> -o` → `SchedNodeList=` | |
| Accounting | `sacct -j <jid> --format=... -P` | may be empty if no jobacct_gather |

### Persistent-join probe design

Spawn ONE long-lived step per RUNNING job at startup:
`srun --jobid=<jid> --overlap --cpu-bind=none --ntasks=1 python3 probe.py`.
The probe loops internally every REFRESH_S, emitting one JSON line per
sample (`{jid, ts, usage_usec, mem_cur, mem_max, gpus: [{idx, util, memu,
memt, temp, uuid}]}`). Cost: 1 step per job per session. This avoids the
MaxStepCount exhaustion from per-refresh transient sruns (~17K steps/day).

Robustness:
- **Instant-death backoff**: a probe exiting within ~10s (step limit, node
  down) must NOT respawn every refresh — back off ~5 min.
- **Cleanup**: stop probes in BOTH `finally` AND a SIGTERM handler; a
  killed srun client terminates its remote step.
- **Non-blocking read**: `select.select([p.stdout],[],[],0)` + `os.read`,
  buffer partial lines, parse complete JSON, return the last sample.

### CPU rate + RAM interpretation

`busy_cpus = (usage_now - usage_prev) / wall_delta / 1e6` (first sample:
"sampling…"). `cpu.stat` is space-separated (`usage_usec 123`), not
key=value. `cgroup.procs` at job level is EMPTY — use node-wide `ps` +
`/proc/<pid>/cgroup` for attribution. `memory.current` includes page cache;
`grep -E "^anon |^file " memory.stat` separates real memory from cache.

### Step listing + filtering

Render **aggregated counts** (`N step(s), M running`), not per-step rows —
all joined steps are named `python`. Filter probe steps by **age**, not
name: probe steps are seconds old; real joins persist for minutes. Drop
bash/nvidia-smi steps only when `now - start < 30s`. Name-based filtering
alone silently hides real joins (a user joining with `srun --overlap bash`
creates a persistent step named `bash`).

### Interactive viewport

- **Alt screen** (`\x1b[?1049h`/`\x1b[?1049l`): entered at startup, released
  on exit AND in SIGTERM handler. Refreshes replace the frame in place.
- **Live viewport**: build the full frame each refresh, render a window
  `out[view_off : view_off + rows - 2]`. Scroll moves within the live frame.
- **Terminal restore pitfall**: `os._exit` in signal handlers skips
  `finally` — restore termios explicitly in the handler, force
  `ECHO|ICANON|ISIG` on (don't trust a captured baseline that may be corrupt).
- **Subprocess stdin**: probe children inherit the dashboard's stdin and
  steal keypresses — use `stdin=subprocess.DEVNULL` on every probe subprocess.
- **Decouple input**: a daemon key-reader thread + `queue.Queue` so keys
  respond in ~0.1s while probes run at most once per REFRESH_S.
- Non-interactive runs skip alt screen + cbreak:
  `interactive = sys.stdin.isatty() and sys.stdout.isatty()`.
