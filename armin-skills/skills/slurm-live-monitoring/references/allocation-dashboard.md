# allocation-dashboard — build notes & pitfalls

Reference for ~/.local/bin/allocation-dashboard (huebers, Lamarr). Live 5s-refresh
tmux dashboard, COMPACT layout (user preference, 2026-08-12): three sections —
'persistent allocations' (apple/banana/coconut/durian), 'gpu jobs', 'cpu-only
jobs' (CPU-only jobs go in their own section). Per job exactly two lines: header
(id, name, node, elapsed/limit, time left) and ONE metrics line (CPU busy/RAM
and GPU util/mem/temp on the same line — fmt_combined). Hidden for compactness:
.extern and .batch holder steps (only real joined steps shown) and the old
'GPU (allocation's card)' label. Interactive since 2026-08-14: alt screen
(no tmux-scrollback spill), LIVE VIEWPORT scroll (2026-08-15 — see SKILL.md
"Interactive dashboard" section; the earlier frame-history scrollback was
removed after the user clarified they want to scroll WITHIN the live frame,
not page through old frames). flock at
/tmp/allocation-dashboard.lock serializes instances — since 2026-08-14 a new
launch KILLS the old one and takes over (reads lock-file PID + pgrep, SIGTERM,
waits for flock release, writes own PID; prints "took over dashboard from
previous instance"). `ALLOC_DASH_NO_LOCK=1` still bypasses the lock for
testing.

## Architecture (persistent-join since 2026-08-15)
- Every refresh: `squeue -u huebers -o "%i %j %T %M %l %R %b %C"` (7 fields via
  split(None, 7)) → jobs dict. PENDING jobs: show yellow + SchedNodeList from
  `scontrol show job <jid> -o`.
- ONE long-lived probe step per RUNNING job, spawned once at startup:
  `srun --jobid=<jid> --overlap --cpu-bind=none --ntasks=1 python3
  ~/.local/bin/alloc-probe-persist.py` (the old per-refresh transient
  `srun ... bash -c` joins burned a Slurm step every 5s and exhausted
  MaxStepCount after ~2.3 days — see SKILL.md MaxStepCount section).
- `alloc-probe-persist.py` loops internally every REFRESH_S, emitting one JSON
  line per sample: {jid, ts, usage_usec (from cgroup cpu.stat), mem_cur/mem_max
  (memory.current/max), gpus: [{idx, util, memu, memt, temp, uuid}] via
  nvidia-smi (only when ALLOC_DASH_WANT_GPU=1 — CPU jobs skip it)}.
- Dashboard reads each probe's stdout NON-BLOCKING: select.select + os.read,
  keep partial tail line in a per-job buffer, parse complete JSON lines, return
  the last sample. ensure_probe() tracks spawn time; a probe that dies within
  10s of spawn (step limit / node down) gets a 5-min backoff — never hammer
  failed sruns every refresh. stop_all_probes() runs on exit AND in the
  SIGTERM handler (client kill propagates to the remote step — verified).
- CPU busy = (usage_now − usage_prev) / wall_delta / 1e6 across refreshes; first
  sample shows "CPU sampling…". memory.current/max in bytes → humanize.

## Pitfalls hit while building (all verified)
- squeue %M/%l use MM:SS for durations < 1h (e.g. "4:30") — parse_duration must
  handle 2-part times or ANY fresh job crashes the whole dashboard with
  "ValueError: not enough values to unpack (expected 3, got 2)". This is the
  exact crash helper1 reported over agent-net (2026-08-12); UNLIMITED/empty
  also need guards.
- squeue %L = time LEFT, %l = time LIMIT. Using %L made the "limit" column show
  remaining time and double-subtracted in the "left" calculation.
- cpu.stat usage_usec is SPACE-separated ("usage_usec 61664012837"), not
  "usage_usec=..." — an "=" parser silently yields None for every job.
- cgroup.procs at the job level is empty (processes are in step_*/user/task_*);
  a find-based PID enumeration is needed if you ever go the ps route — the
  usage_usec delta approach avoids it entirely.
- sstat returns headers only (no data) — no jobacct_gather on this cluster.
- nvidia-smi through a GPU job join shows ONE card (the job's own, cgroup
  restricted; UUID differs per job). Through a CPU-only job join: "No devices
  found". Per-job joins are mandatory; no node-wide view exists.
- scontrol show step: StartTime is on the StepId= line; Name= sits mid-line
  ("... Tasks=1 Name=python ..."). .batch = holder, .extern = slurm extern.
- The dashboard's own probe shows up transiently as a step named `nvidia-smi`
  or `bash` — filter both from step listings.
- Joining a job that ends mid-probe → srun error → show "unavailable" line.

## Verification recipe
- Functions are importable without the lock: SourceFileLoader on the script,
  then d.get_jobs(), d.ensure_probe(jid, has_gpu) + d.read_probe(jid),
  d.fmt_resources(jid, job, res), d.render_view(out, view_off). The old
  transient `probe()` function was REMOVED 2026-08-15 (persistent-join
  rework) — do not call it.
- Two samples ~2-3s apart confirm the CPU-rate path ("sampling…" → number).
- Full-frame test: `ALLOC_DASH_NO_LOCK=1 timeout 13 ~/.local/bin/allocation-dashboard | head -50`
