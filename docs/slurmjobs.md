# slurmjobs / sj

A read-only, indented Slurm queue viewer for cluster hosts with Python 3, Rich, and `squeue`. Your jobs appear first, followed by other users grouped by username. Section and username headers use white text on black backgrounds. There are no blank spacer lines within either section; a single blank line separates your jobs from the other-users section.

## Install

Source and tests live in `tools/slurmjobs/`. The installed commands are symlinks into the checkout, so updates take effect immediately. Do not replace unrelated existing commands; inspect any existing destination first.

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
sj --watch --interval 30
sj --compact
sj --no-color
sj --timeout 5
```

Each job shows its complete ID and name, state, optional submission `--comment`, partition and nodes, GPUs, total RAM, CPU count, and elapsed/limit wall time. Pending jobs also show their waiting reason. Names and comments wrap without ellipses; detail continuations align under their values. Resource amounts are allocations where reported for active jobs, otherwise requests, not measured utilization. GPU models appear when Slurm provides them; unspecified types and unknown representations are labeled explicitly.

Time uses `M:SS`, `H:MM:SS`, or `D-HH:MM:SS`; unlimited and unknown limits are explicit. Pending jobs show zero elapsed time. `--compact` combines resources and time. Piped output and `--no-color` disable colors; `NO_COLOR` is also honored.

A snapshot uses one bounded `squeue --json` call, without per-job queries. Clients rejecting JSON use a unit-separator text fallback, which has less GPU detail; multi-node GPU requests are labeled per node. Legacy names/comments containing embedded newlines or separator characters cannot be reliably parsed. Queue visibility matches normal `squeue` defaults.

Watch mode refreshes in the normal terminal screen every 10 seconds and exits with Ctrl-C. On query errors it preserves the previous queue and displays a warning. It requires a terminal and works best when the queue fits the viewport; larger queues can scroll on refresh. Use `--me`, `--compact`, or a single snapshot for large queues. There is no daemon or job-modification functionality.

## Verify

```sh
sj --help
sj --me --no-color
cd ~/dotfiles/tools/slurmjobs
python3 -m unittest -v test_slurmjobs
```

Tests use offline fixtures and mocked commands, so they do not submit or alter jobs. They cover comments, long names, user grouping, header colors, resources, arrays, suspension, unlimited limits, JSON and legacy parsing, and scheduler failures.

## Remove

```sh
rm ~/.local/bin/sj ~/.local/bin/slurmjobs
```

Retain repository source/tests. No shell aliases, system services, or scheduler changes need removal.
