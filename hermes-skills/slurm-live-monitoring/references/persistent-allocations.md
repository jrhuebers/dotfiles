# Adding a new persistent GPU allocation (apple/banana/coconut/durian pattern)

The fleet keeps long-lived joinable allocations (`sleep infinity` holder jobs)
that any agent can attach to with
`srun --jobid=<id> --overlap --cpu-bind=none <cmd>`. Adding one touches FOUR
places — the same list every time (verified 2026-08-14 with `durian`):

## 1. Submit the holder job (coconut/durian type = 40GB, 14d)

    sbatch --parsable --job-name=<name> --partition=GPU1 --gres=gpu:1 \
      --cpus-per-task=8 --mem=64G --time=14-00:00:00 \
      --output=/cephfs/users/huebers/slurm-logs/<name>-%j.out \
      --error=/cephfs/users/huebers/slurm-logs/<name>-%j.err \
      --wrap="exec sleep infinity"

80GB allocations (apple/banana) use --time=7-00:00:00. The job may sit
PENDING on (Priority) even with free GPUs — that is queue ordering, not
resource starvation; `squeue -j <id> -o "%.20R"` shows the reason.

## 2. Register it with the maintain watchdog

`~/.hermes/scripts/maintain_apple_banana.py` (cron `maintain apple/banana/
coconut allocations`, every 4h, no_agent) keeps them alive — resubmits when
missing or < 12h left. Add the name to:
- `NAMES = ["apple", "banana", "coconut", "durian"]`
- `TIMES = {..., "<name>": "14-00:00:00"}` (or 7d for 80GB)
- `GPU_SIZE = {..., "<name>": "40GB"}` (drives availability announcements)
- The `resubmit <name>` command and `help` text derive from NAMES
  automatically (they were hardcoded once — keep them dynamic).

Verify with: `python3 -c "import ast; ast.parse(open('...').read())"` then run
the script once — it must NOT resubmit the new alloc (it exists as PENDING),
proving the "missing" check sees it.

## 3. Add it to the dashboard

`~/.local/bin/allocation-dashboard`: add the name to its `NAMES` list so it
gets the persistent-allocations section treatment (step counts, GPU card,
time left). Restart the live instance — since 2026-08-14 a fresh launch
auto-takes-over (kills the old pid, waits for the flock, acquires), so just
run it in the `alloc-dash` tmux session (`tmux -S ~/.tmux-sock/mission
new-session -d -s alloc-dash ...` — recreate the session if it died with the
old instance). PENDING jobs render yellow with `-> sched for ?`
(SchedNodeList is null until scheduled — normal).

## 4. Announce + record

- Broadcast to the fleet — EXCLUDING the supervisors (operator rule,
  2026-08-14: supervisors undisturbed by infra chatter):
  `agent-net-broadcast --from helper1 --except qmc-supervisor,gauge-supervisor "INFRA: ..."`
  Include the join command and the job id in the message.
- Fleet memory: add the name to the joinable-allocs entry
  (e.g. "coconut/durian A100-40GB").
- GPU cap check: count `squeue -p GPU1 -t RUNNING,PENDING` — cap is 15.

## Watchdog notifications skip supervisors

`maintain_apple_banana.py` has `SUPERVISORS = ["qmc-supervisor",
"gauge-supervisor"]`; `_notify()` passes `--except ,`.join(SUPERVISORS) to
agent-net-broadcast, so resubmission announcements never reach the
supervisors. Keep this list in sync if supervisors are renamed/added.
