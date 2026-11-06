# HPC Dashboard

HPC Dashboard is maintained in the standalone [jrhuebers/hpc-dashboard](https://github.com/jrhuebers/hpc-dashboard) repository, not in dotfiles. Its commands are `hpc-dashboard` and `hpcd`; the former `sj` / `slurmjobs` commands are retired. It is **required on every HPC cluster** as part of the cluster profile, not an optional tool. Install it once per independent user environment; hosts sharing the same home and compatible Python environment can share that installation. Do not install it for personal-device profiles. Currently only the Slurm backend is implemented; RunAI-only clusters should still have the commands installed, but dashboard operation there must wait for RunAI support.

## Install

Use Python 3.10+ and uv on a POSIX cluster host. Slurm clients are needed for current dashboard operation, not for installing the package or verifying `--help`. The standalone repository's [README](https://github.com/jrhuebers/hpc-dashboard#readme) is the authoritative usage, telemetry lifecycle, migration, and test guide.

```sh
git clone https://github.com/jrhuebers/hpc-dashboard.git ~/hpc-dashboard
uv tool install --editable ~/hpc-dashboard
uv tool update-shell
hpcd --help
```

Source lives in `~/hpc-dashboard/`; uv installs the `hpc-dashboard` and `hpcd` entry points into its user-local tool bin directory, normally `~/.local/bin`. Alternatively, the README documents direct checkout symlinks for a system Python that already has Rich. Inspect existing launcher destinations first; do not overwrite unrelated commands or mix installation methods.

## Verify and update

Verify installation on every cluster:

```sh
command -v hpc-dashboard hpcd
hpc-dashboard --help
hpcd --help
```

On Slurm clusters, additionally verify a read-only snapshot:

```sh
hpcd --me --no-watch --no-usage --no-color --timeout 2
```

Update the editable checkout with `git -C ~/hpc-dashboard pull --ff-only`.

`--no-usage` is important for read-only verification: normal invocations start/reuse persistent telemetry steps in your running allocations. Restart dashboards after updating. Existing telemetry state and old collector names are recognized without resetting step budgets; follow the standalone migration guide rather than moving or deleting live cache files.

## Remove

```sh
uv tool uninstall hpc-dashboard
```

For direct-symlink installations, remove only `~/.local/bin/hpcd` and `~/.local/bin/hpc-dashboard` instead. Retain the source while collectors are active; no system services or scheduler configuration changes are involved.
