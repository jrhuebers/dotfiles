# Slurm job log files: locations, tidying, safe moves

Operational notes from the 2026-08 home-root tidy (huebers cluster, Lamarr).

## Where logs land and why root gets littered

- sbatch/srun without explicit `--output`/`--error` drops `<jobname>-<jid>.out` /
  `<jobname>-<jid>.err` in the submission directory. When agents submit from
  home root, root accumulates these (41 files, ~40 MB, accumulated in days).
- Cluster convention (established 2026-08): ALL slurm stdout/stderr go to
  `~/slurm-logs/` via `--output=~/slurm-logs/<name>-%j.out
  --error=~/slurm-logs/<name>-%j.err`. The persistent allocations
  (apple/banana/coconut, maintained by the watchdog) already comply; legacy
  jobs (fim-*, llm-evolution-*, mission-control-*, mission-tunnel-*,
  vscode-tunnel-*, hello-loop-*) did not.
- The user-facing home dir doubles as the Mac GUI browsing surface, so root
  clutter has direct visibility cost.

## Moving logs of RUNNING jobs is safe

`mv ~/*.out ~/*.err ~/slurm-logs/` is safe even for jobs still running:
slurm's open file descriptors follow the old inodes, so writes continue to
the moved-away file and nothing breaks. Verified live with a running
mission-control holder job (moved its .out/.err while RUNNING; job
unaffected). No need to restart the job or touch launchers for the move
itself.

## Broadcast path changes to other agents

After moving files that other agents' tooling may reference, send an
agent-net broadcast naming the old vs new paths. On this cluster: fim, gauge,
qmc, research-assistant, helper2 all acked; nothing referenced home-root log
paths, and each agreed to use explicit `--output=~/slurm-logs/...` going
forward. (Comms rule: agent-to-agent notifications go via agent-net only.)

## Related

- start-slurm-job skill: prefer explicit output paths on every submission
  (`--output=/path/to/logs/slurm-%j.out`); `scontrol show job <jid>` reveals
  the effective StdOut when a path wasn't given.
- Service logs (gateway.log, hermes-dash.log, sshd-mission.log) are a
  SEPARATE category from slurm logs — same tidy problem, different fix
  (launcher scripts write them to root; left untouched by the 2026-08 tidy).
