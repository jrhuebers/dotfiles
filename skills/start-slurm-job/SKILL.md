---
name: start-slurm-job
description: "Use when submitting or monitoring Slurm batch jobs."
version: 1.1.0
author: huebers (imported from Codex; updated with walltime defaults)
platforms: [linux, macos]
---

# Start Slurm Job

## When to Use

Use whenever you create or submit a Slurm batch job (sbatch, GPU jobs, test jobs, or jobs launched on behalf of another task), especially when the user wants confirmation that a job started successfully. Also use when diagnosing why a submitted job is stuck, pending, or failed.

Use this workflow for every newly submitted Slurm batch job. Treat the submission as incomplete until the start ping arrives (job picked up) or the job's terminal state has been observed.

## Walltime: default to 7 days

- **Default `--time=7-00:00:00`** unless the user explicitly requests a shorter walltime or the workload has a hard internal bound (e.g. a known epoch budget).
- A short `--time` is NOT how you schedule a "short" job. **The job releases its allocation and exits on its own the moment the command finishes** — Slurm frees the nodes automatically when the workload completes, so a long limit costs nothing.
- A too-short limit only risks the scheduler killing a healthy long-running workload with `TIMEOUT`, and short limits can hurt queue position (jobs needing to start soon and finish soon compete worse than flexible 7-day windows).
- Short limits are fine for genuinely bounded smoke tests, but never the default.

## Fleet GPU cap (operator-confirmed 2026-08-14)

The fleet may run at most **15 concurrent GPU jobs** total across all agents
(was 8; raised twice, 8→10→15 — 15 is the authoritative number,
operator-confirmed). coconut and durian count toward the limit. (apple and
banana were retired 2026-08-19 and no longer count.) Before
submitting a NEW GPU job, count current GPU jobs (`squeue -u huebers -t
RUNNING,PENDING` with a GPU partition/gres); if at/above the cap, join an
existing allocation (`srun --jobid=... --overlap`) or wait instead of
pushing the count over. The cap applies to NEW submissions.

## Single agent per job (operator rule 2026-08-16)

**Never join a Slurm job that is already utilized by another agent. One
agent per job — period.** Before joining an allocation (coconut/durian/
mission-control or any running job), check its steps first
(`squeue --steps --job <id>`): if another agent's workload is running
inside (a non-`.batch`/`.extern` step owned by someone else), do NOT join —
pick a different allocation or submit a new job (subject to the GPU cap).
Sharing a job between agents creates unresolvable conflicts: step-limit
burn, GPU contention, and cross-agent interference in the same cgroup.
Each agent's work gets its own allocation (a single GPU job counts once
against the cap, not per agent).

## Persistent joinable allocations (coconut / durian / mission-control)

Some allocations exist to be JOINED, not to run a workload. Pre-provision them
so routine work never waits on the scheduler during traffic spikes.

Operator retired apple and banana 2026-08-19 (both cancelled; watchdog
NAMES now coconut+durian only). apple/banana details below are historical
for quick re-enablement if the operator revives them.

- **apple & banana** (RETIRED): persistent single-GPU allocations (GPU1, 1x A100-80GB
  (SXM4), `--cpus-per-task=8 --mem=64G --time=7-00:00:00`, holder process
  `exec sleep infinity`). When the queue is saturated and new jobs would sit
  PENDING for hours, join one instead — no wait.
- **coconut & durian**: persistent single-GPU allocations, same shape as
  apple/banana but `--time=14-00:00:00` (14d): GPU1, 1x A100-**40GB** (SXM4),
  `--cpus-per-task=8 --mem=64G`, holder `exec sleep infinity`. IMPORTANT:
  their cards are A100-40GB, NOT the 80GB of apple/banana — size GPU memory
  accordingly. coconut landed on ml2ran01, durian on ml2ran05 (job 53685).
  Add `--gres=gpu:nvidia_a100_sxm4_80gb:1` or a node constraint on
  resubmission if 80GB is required.
  All are maintained by the cron watchdog
  (`~/.hermes/scripts/maintain_apple_banana.py`, every 4h): missing or <12h
  left -> resubmitted automatically. Walltimes are per-name in the script
  (`TIMES` dict: apple/banana 7d, coconut/durian 14d). Verify the cron job is
  enabled (`cronjob list` — it has been found disabled/completed before;
  re-enable with a recurring schedule).
- **mission-control**: CPU allocation (8 CPUs, **32GB**, 14d, holder process
  `exec sleep infinity`; 16GB proved too tight once the dashboard/gateway/webui
  stack moved in — recreate with 32GB). SSH access into the allocation (compute-node port 22
  is NOT reachable, not
  even via the login node — this cluster only exposes sshd-in-job on custom
  ports): a user-space sshd step in the allocation on port 25000, held in tmux
  session `mission-sshd`:
  `/usr/sbin/sshd -D -p 25000 -h ~/.ssh/ssh_host_ed25519_key -o PidFile=~/.ssh/sshd-mission.pid -o UsePAM=no -o PasswordAuthentication=no -o StrictModes=no -o GSSAPIAuthentication=no -o LogLevel=QUIET -E ~/sshd-mission.log`
  (host key generated once with `ssh-keygen -t ed25519 -f ~/.ssh/ssh_host_ed25519_key -N ""`).
  Mac side: `Host mission-control mc` -> HostName ml2ran02s0 (public alias of the node), ProxyJump gwkilab, Port 25000.
  (User renamed the old `mission` alias to `mission-control`; `mc` is a shorthand alias. The Slurm job is also named mission-control.)
  If `ssh mission` suddenly fails while the allocation is RUNNING: the job was almost certainly
  resubmitted, which killed tmux+sshd. Restart exactly:
  `mkdir -p ~/.tmux-sock && tmux -S ~/.tmux-sock/mission new-session -d -s mission-sshd '/usr/sbin/sshd -D -p 25000 -h ~/.ssh/ssh_host_ed25519_key -o PidFile=~/.ssh/sshd-mission.pid -o UsePAM=no -o PasswordAuthentication=no -o StrictModes=no -o GSSAPIAuthentication=no -o LogLevel=QUIET -E ~/sshd-mission.log'`
  Verify: `ss -tln | grep 25000`.
  Self-test gotcha: `ssh -p 25000 localhost` FROM inside the allocation gives Permission denied —
  the node's own ~/.ssh/id_ed25519 is not in authorized_keys. Expected; don't chase it. Check the
  client's real key is in authorized_keys (comments are meaningful, e.g. jhuebers@mp-macbook-40).
- tmux on this cluster: /tmp is not writable for the default socket, so always
  use an explicit socket path: `tmux -S ~/.tmux-sock/mission new-session -d -s <name> '<cmd>'`.
- `--cpu-bind=none` on the srun avoids the inherited-CPU-binding failure
  (`CPU binding outside of job step allocation`) when launching a step into
  another job's allocation; harmless from a login shell.

Create (apple/banana shape):

```bash
sbatch --parsable --job-name=apple --partition=GPU1 --gres=gpu:1 \
  --cpus-per-task=8 --mem=64G --time=7-00:00:00 \
  --output=/cephfs/users/huebers/slurm-logs/apple-%j.out \
  --error=/cephfs/users/huebers/slurm-logs/apple-%j.err \
  --wrap='exec sleep infinity'
```

Join (no new allocation needed):

```bash
srun --jobid=<apple-jobid> --overlap --chdir=/explicit/workdir <command>
```

SINGLE-AGENT-PER-JOB RULE (operator, 2026-08-16): before joining a
persistent allocation, check `squeue --steps -j <jobid>` — if another
agent's step is already running inside it, pick a DIFFERENT allocation.
One working agent per allocation at a time; avoids step collisions and
mixed workloads. (The allocations are otherwise empty — holders are
`batch`/`extern`/`sleep infinity`, which don't count.)

Keeping them alive: a cron watchdog (`~/.hermes/scripts/maintain_apple_banana.py`,
every 4h) resubmits apple/banana when they are missing or have less than 12h of
walltime left, so there is always at least one joinable GPU allocation. Never
submit a NEW short job to do something an apple/banana join can do instantly.

GPU smoke test / env: node driver is CUDA 12.8 (driver 570.211.01) — the default
PyPI torch wheel (cu130) FAILS with "NVIDIA driver too old" /
`torch.cuda.is_available() == False`; use the cu128 build. Canonical solution:
prebuilt venv `~/.venvs/torch-cu128` (torch 2.11.0+cu128 + numpy), or the
wrapper `~/.local/bin/torch-gpu <script.py>` — works on ALL GPU nodes
(A100 40/80GB and B300 ml2rbn01). Ephemeral alternative:
`uv run --with torch --index-url https://download.pytorch.org/whl/cu128 -- python ...`
(env cached in ~/.cache/uv after first fetch, so joins reuse it instantly).

## Submission

1. Resolve the requested partition, account, walltime (default 7 days per above), GPU/CPU resources, working directory, command, and output path. Preserve the user's requested resources; do not silently increase them.
2. Submit with `sbatch` and capture the numeric job ID from `Submitted batch job <id>`.
3. Prefer an explicit output path when constructing the job, for example `--output=/path/to/logs/slurm-%j.out`. If no path was specified, determine the effective `StdOut` path with `scontrol show job <jobid>` and check the default `slurm-<jobid>.out` in the submission directory.
4. Use Bash explicitly for every multi-command job body. `sbatch --wrap` runs under `/bin/sh` on this cluster, so bare `--wrap='set -euo pipefail; ...'` fails before the workload starts. Prefer a small `#!/usr/bin/env bash` batch script, or wrap the body in `bash -lc` with correct quoting. Use bare `--wrap` only for a simple POSIX-compatible single command. Also remember `--wrap` does NOT accept script arguments — embed any args in the wrap string.
5. Report the job ID immediately, then arm the start/end watchers (see Ping-based monitoring below).
6. **Fine-grained progress logging is mandatory** in every submitted script (training/eval/whatever). The log must let you estimate rate + ETA within minutes of start: run python with `-u` (or `flush=True`) so lines land immediately; print a progress line at least every few minutes containing cumulative work done (e.g. `step 25000/100000`, `power 8/14`, `epoch 3/10`) plus a wall-clock timestamp, and an in-script ETA when cheap. Bash wrappers: `echo "[$(date +%H:%M:%S)] phase ..."` around phases. Everything goes to the slurm stdout (`--output`), which is what the 10-minute check reads (see Ping-based monitoring below).

For a multi-command inline submission, the essential shape is:

```bash
sbatch ... --wrap='exec bash -lc '\''set -euo pipefail
cd /explicit/workdir
# workload
'\'''
```

If the end ping reports a quick FAILED state, inspect the job's stderr — shell errors such as `Illegal option -o pipefail` mean the workload never began.

Do not cancel a pending, running, or failed job unless the user asks or the requested workflow explicitly requires cancellation.

## Ping-based monitoring (no polling)

Do NOT wait 20 seconds or watch output files. Instead, arm two background
watchers right after `sbatch` returns; you get pinged when the job is picked
up and again when it ends:

    terminal(background=true, notify_on_complete=true,
             command="~/.hermes/scripts/slurm_watch.sh <jobid> start")
    terminal(background=true, notify_on_complete=true,
             command="~/.hermes/scripts/slurm_watch.sh <jobid> end")

- `start` watcher exits (-> ping) as soon as the job is RUNNING, printing the node.
- `end` watcher exits (-> ping) when the job reaches a terminal state, printing state + exit code.
- A job that dies before pickup: the start watcher prints the terminal state instead.
- The watchers stay silent while the job is PENDING, so no false pings — report
  the pending reason from `squeue -j <jobid>` only if the user asks why it's stuck.

### 10-minute progress check (every submitted job)

Right after the start ping, arm a 10-minute watcher:

    terminal(background=true, notify_on_complete=true,
             command="sleep 600 && ~/.hermes/scripts/check_progress.sh <jobid> '<progress-regex>'")

When it pings (10 min after pickup), read its output: elapsed vs walltime limit,
log tail, and matched progress lines. Compute throughput (work units / elapsed)
and extrapolated total time. Escalate to better hardware when:

- estimated total > walltime limit (job would TIMEOUT unfinished), or
- the hardware class is wrong for the work (e.g. net training/eval on CPU that
  belongs on GPU) — CPU jobs that won't finish are the classic case.

Escalation procedure: submit the SAME command on better hardware (GPU partition
or a joinable allocation like apple/banana) with the same fine-grained logging,
cancel the unfit job, and report both job IDs + reasoning to the user. This
kill-and-resubmit is the standing preference for skill-submitted jobs
(user-directed); only jobs the user explicitly asked to keep running are exempt.

On the start ping: report the node. On the end ping: report state + exit code
and inspect the output file if it failed. If no ping arrives, the job is still
pending or running — nothing to report.

## Reporting

Always include:

- job ID
- partition and node, if known
- the start ping (node) and end ping (state + exit code) results
- concise output or the path to the full output
- failure reason and exit code when applicable

For commands that fail because the execution environment cannot reach Slurm, retry via the permitted elevated execution path rather than concluding that the job or cluster is unavailable.
