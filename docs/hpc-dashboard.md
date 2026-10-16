# HPC Dashboard

HPC Dashboard is maintained in the standalone [jrhuebers/hpc-dashboard](https://github.com/jrhuebers/hpc-dashboard) repository, not in dotfiles. Its commands are `hpc-dashboard` and `hpcd`; the former `sj` / `slurmjobs` commands are retired. Currently it supports Slurm only, not RunAI. Install it only for the cluster profile.

## Install

Use Python 3.10+ and uv on a POSIX cluster host with Slurm clients. The standalone repository's [README](https://github.com/jrhuebers/hpc-dashboard#readme) is the authoritative usage, telemetry lifecycle, migration, and test guide.

```sh
git clone https://github.com/jrhuebers/hpc-dashboard.git ~/hpc-dashboard
uv tool install --editable ~/hpc-dashboard
uv tool update-shell
hpcd --help
```

Source lives in `~/hpc-dashboard/`; uv installs the `hpc-dashboard` and `hpcd` entry points into its user-local tool bin directory, normally `~/.local/bin`. Alternatively, the README documents direct checkout symlinks for a system Python that already has Rich. Inspect existing launcher destinations first; do not overwrite unrelated commands or mix installation methods.

## Verify and update

```sh
hpcd --me --no-watch --no-usage --no-color --timeout 2
git -C ~/hpc-dashboard pull --ff-only
```

`--no-usage` is important for read-only verification: normal invocations start/reuse persistent telemetry steps in your running allocations. Restart dashboards after updating. Existing telemetry state and old collector names are recognized without resetting step budgets; follow the standalone migration guide rather than moving or deleting live cache files.

## Remove

```sh
uv tool uninstall hpc-dashboard
```

For direct-symlink installations, remove only `~/.local/bin/hpcd` and `~/.local/bin/hpc-dashboard` instead. Retain the source while collectors are active; no system services or scheduler configuration changes are involved.
