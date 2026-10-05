# slurmjobs / sj

An indented Slurm queue viewer for cluster hosts with Python 3, Rich, and `squeue`. Normal operation is read-only; opt-in `--usage` starts persistent telemetry steps in your own running allocations. Your jobs appear first, followed by other users grouped by username. Section and username headers use white text on black backgrounds; detail labels and empty-state text use darker grey (`#707070`). There are no blank spacer lines within either section; a single blank line separates your jobs from the other-users section.

## Install

Source and tests live in `tools/slurmjobs/` (`slurmjobs.py`, sibling `telemetry.py`, and their test modules). The installed commands are symlinks into the checkout, so updates take effect immediately. Do not replace unrelated existing commands; inspect any existing destination first.

```sh
python3 -c 'import rich'
command -v squeue
mkdir -p ~/.local/bin
chmod +x ~/dotfiles/tools/slurmjobs/slurmjobs.py
ln -s ~/dotfiles/tools/slurmjobs/slurmjobs.py ~/.local/bin/slurmjobs
ln -s slurmjobs ~/.local/bin/sj
```

Keep `~/.local/bin` on PATH. If Rich is absent, use an isolated user-local environment rather than changing system Python:

```sh
python3 -m venv ~/.local/share/slurmjobs-venv
~/.local/share/slurmjobs-venv/bin/python -m pip install rich
```

In that case replace the `slurmjobs` source symlink with a small executable launcher invoking `~/.local/share/slurmjobs-venv/bin/python ~/dotfiles/tools/slurmjobs/slurmjobs.py "$@"`; the `sj` symlink can remain. This tool is intended for Slurm cluster access hosts, not personal systems without Slurm.

## Usage

```sh
slurmjobs
sj --me
sj --watch
sj --me --watch --usage
sj --watch --interval 30
sj --compact
sj --no-color
sj --timeout 5
```

Each job shows its complete ID and name, state, optional submission `--comment`, partition and nodes, GPUs, total RAM, CPU count, and elapsed/limit wall time. Pending jobs also show their waiting reason. Names and comments wrap without ellipses; detail continuations align under their values. Resource amounts are allocations where reported for active jobs, otherwise requests, not measured utilization. GPU models appear when Slurm provides them; unspecified types and unknown representations are labeled explicitly.

Time uses `M:SS`, `H:MM:SS`, or `D-HH:MM:SS`; unlimited and unknown limits are explicit. Pending jobs show zero elapsed time. `--compact` combines resources and time. Piped output and `--no-color` disable colors; `NO_COLOR` is also honored.

A snapshot uses one bounded `squeue --json` call, without per-job queries. Clients rejecting JSON use a unit-separator text fallback, which has less GPU detail; multi-node GPU requests are labeled per node. Legacy names/comments containing embedded newlines or separator characters cannot be reliably parsed. Queue visibility matches normal `squeue` defaults.

Watch mode refreshes the display in the normal terminal screen every second and exits with `q`, Escape, or Ctrl-C. Interactive input temporarily uses cbreak mode with echo disabled; the previous terminal settings are restored on normal exit and handled errors. Arrow/function-key escape sequences are ignored. With redirected stdin, only Ctrl-C is available; no alternate screen is used. Queue queries remain limited to once every 10 seconds; elapsed times advance locally between queries. `--interval` controls display refresh, not accounting frequency. On query errors it preserves the previous queue and displays a warning. It requires a terminal and works best when the queue fits the viewport; larger queues can scroll on refresh. Use `--me`, `--compact`, or a single snapshot for large queues.

## Persistent utilization collectors

`sj --usage` starts or reuses a named `sj-telemetry` step in each of your running jobs; it never monitors other users' allocations or starts a new allocation. One detached supervisor owns each step, so closing `sj` or its terminal does not stop the collector. Concurrent dashboard invocations share readings and launch locks. Pending jobs have no collector. Sampling is once per second, and readings are published atomically in a user-private shared-home cache rather than an unbounded log.

CPU readings come from changes in job-level cgroup CPU time, expressed as busy cores and percentage of allocated CPUs. RAM is job-level cgroup-charged memory, which includes cache and collector overhead; it is not process RSS. If cgroup counters are inaccessible, a batched `sstat --allsteps` query supplies slower CPU/RSS fallback readings, at most every 10 seconds. Multi-node cgroup readings must be complete before a job-wide total is shown. Watch mode retains the last successful reading for each node and metric across transient shared-filesystem reads, failed GPU queries, or collector warm-up. Retained values remain visible with an explicit stale/unconfirmed marker and the age of the underlying measurement; they are never silently presented as current or converted to zero. A measurement is unavailable only if no valid value has been seen. Retention is in-memory for that dashboard instance and ends when the job leaves its running-job list.

GPU readings require `nvidia-smi` on the compute nodes. GPU percentage and VRAM occupancy describe allocated devices, not per-process GPU compute usage; sharing a device can include another workload's activity. Slurm step GPU UUIDs are used directly; numeric GRES IDs require GPU UUID verification against same-user processes in the exact job cgroup, avoiding assumptions about GRES/index ordering. Thus an idle allocation with no GPU context may show unavailable until ownership can be verified. Totals describe the verified devices; node coverage is displayed, and unverified devices are not guessed. The collector does not change Slurm accounting configuration or require root.

Collector launches use an overlapping step with one lightweight task per node. A persistent collector consumes one step ID, not one per refresh. Failed launches can also consume step IDs; launch locking, startup timeouts, backoff, and a bounded restart budget prevent unbounded step creation. Collector work is charged to the existing job, and the job's end terminates its step. This feature requires a shared cache location and Slurm configurations permitting overlapping steps. Collectors re-exec themselves when their source changes, preserving the same Slurm step rather than consuming another step ID.

After confirmed job completion, the detached supervisor waits one hour locally (without retaining a Slurm step) and removes expired samples and metadata. Subsequent `sj --usage` invocations also reclaim expired files if the supervisor was lost. Tiny lock files/directories remain deliberately to avoid lock-inode races. No system cleanup service is installed. The supervisor survives closing `sj`, but termination of its launch host or originating allocation can still kill it; later invocations reattach/recover where possible. Do not remove launch-state files for a running job: they preserve duplicate-launch protection and the two-start restart budget.

## Verify

```sh
sj --help
sj --me --no-color
cd ~/dotfiles/tools/slurmjobs
python3 -m unittest -v test_slurmjobs test_telemetry
```

Tests use offline fixtures and mocked commands, so they do not submit or alter jobs. They cover rendering, queue-query caching, JSON/legacy parsing, scheduler failures, telemetry parsing, cache lifecycle, and collector launch safeguards.

## Remove

```sh
rm ~/.local/bin/sj ~/.local/bin/slurmjobs
```

Retain repository source/tests. Existing collectors are independent of the command symlinks and continue until their allocations end; retain `telemetry.py` until then. Expired samples/metadata are cleaned automatically, while tiny lock tombstones remain. No shell aliases, system services, or scheduler configuration changes need removal.
