---
name: slurm-live-monitoring
description: "Use when building live per-job Slurm resource dashboards."
version: 1.0.0
author: hermes-curator
platforms: [linux]
---

# Slurm Live Monitoring

Use for any task needing live per-job resource metrics on Slurm: dashboards like the user's `allocation-dashboard`, answering "what's running and how busy", or debugging a slow job. Validated on Lamarr (Slurm 25.11, cgroup v2).

## Data sources

| Need | Source | Notes |
|---|---|---|
| Job list/state | `squeue -u <user> -h -o "%i %j %T %M %l %R %b %C"` | **%l = TIME LIMIT, %L = TIME LEFT** — easy to mix up; %b = TRES (has "gpu" if job has GPUs); %C = allocated CPUs; **%M/%l are MM:SS for durations < 1h** — parse 2-part times or fresh jobs crash |
| Per-job GPU util/mem/temp | **PERSISTENT join step** (current design): one long-lived `srun --jobid=<jid> --overlap --cpu-bind=none --ntasks=1 python3 ~/.local/bin/alloc-probe-persist.py` per job, sampling every REFRESH_S and streaming one JSON line per sample to stdout; dashboard reads the stream. Transient per-refresh joins (`srun ... nvidia-smi` per cycle) work but **burn a Slurm step per call** — see the MaxStepCount pitfall; they silently blinded the live dashboard after ~2.3 days. Include uuid to identify the physical card |
| Per-job CPU + RAM | job cgroup v2: `/sys/fs/cgroup/system.slice/slurmstepd.scope/job_<jid>/` → `cpu.stat` (usage_usec), `memory.current`, `memory.max` | readable from inside the join; memory.max = job's --mem limit |
| Steps inside an allocation | `scontrol show step <jid>` | see parsing notes below |
| Pending job's target node | `scontrol show job <jid> -o` → `SchedNodeList=` | |
| sstat / sacct | **EMPTY on Lamarr** (no jobacct_gather configured) | do not rely on it |

## Cgroup device restriction — the key insight
A join into a GPU job sees ONLY that job's own physical GPU (nvidia-smi lists exactly one card; verify identity via UUID — two different jobs' joins return different UUIDs). A join into a CPU-only job sees NO GPUs ("No devices found"). Consequence: **per-job joins are the only way to read a job's GPU stats**; there is no node-wide nvidia-smi view from inside any allocation.

## MaxStepCount — transient joins exhaust the step budget (2026-08-15)

Every `srun --jobid=<jid> --overlap` creates a NEW STEP on that job. Slurm
caps steps per job via `MaxStepCount` (stock default **40000**; check
`scontrol show config | grep MaxStepCount` — it is NOT cluster-specific, it is
stock Slurm). A dashboard that spawns a transient join every 5s burns
17,280 steps/job/day → **~2.3 days to exhaust the budget**. Symptoms:
- `srun: error: Unable to create step for job <jid>: Step limit reached for this job`
- The dashboard silently stops showing GPU/CPU/RAM for those jobs (its probes
  fail), while `squeue --steps` still lists the real user steps.
- `scontrol update JobId=<jid> MaxSteps=...` → "Update of this parameter is
  not supported" on a RUNNING job. Cannot be raised mid-job; only a
  resubmission (fresh job = fresh step counter) recovers the job.

FIX — the persistent-join design (current dashboard): spawn ONE long-lived
step per job (`alloc-probe-persist.py` above) at dashboard startup; it loops
internally sampling + printing JSON every REFRESH_S. Cost: exactly 1 step per
job per dashboard lifetime (plus 1 per dashboard restart — negligible).
Verified: probe step aged 0:17→0:39 over 3 refresh cycles with ZERO new steps
created; old design would have added 3.

Robustness details that matter:
- **Instant-death backoff**: a probe whose srun exits within ~10s of spawn
  (job at step limit, node down) must NOT be respawned every refresh — record
  a spawn timestamp and back off ~5 min. Without this, the dashboard hammers
  step-limited jobs with a failed srun every cycle.
- **Probe cleanup on exit**: `stop_all_probes()` must run in BOTH the
  `finally:` block AND the SIGTERM takeover handler (see terminal pitfall
  below). Verified: SIGTERM on the dashboard removed all 4 probe steps; a
  killed srun client terminates its remote step (client death propagates).
  kill -9 on the dashboard orphans the probe steps until the job ends —
  recovery: `pkill -f alloc-probe-persist`.
- **Non-blocking read**: drain each probe's stdout with `select.select([p.stdout],[],[],0)` + `os.read`, keep the partial tail line per job in a buffer, parse complete JSON lines, return the last sample. Never block the refresh on the probe stream.

## CPU rate
`usage_usec` is cumulative since job start: busy_cpus = (u_now − u_prev) / wall_delta / 1e6. First sample shows "sampling…" until the second refresh. Pitfalls:
- `cpu.stat` is **space-separated** ("usage_usec 123"), not key=value — parse with `split()[1]`.
- Job-level `cgroup.procs` is **EMPTY** (processes live in step_*/user/task_* sub-cgroups) — cannot enumerate job PIDs from the job cgroup directly.
- The probe's own tiny CPU time pollutes the job's usage_usec — negligible vs real workloads.

## Reading the numbers for a user (interpretation)
- `CPU x/y` = average busy cores over the last refresh window (delta of cgroup usage_usec / wall time), NOT a percentage. x ≈ y means the allocation is saturated; x slightly above y (e.g. 8.1/8) is normal — the job cgroup is not hard-capped, bursts overshoot briefly.
- A persistent "home-base" allocation (e.g. mission-control) showing full CPU is usually OTHER agents' joined work (`srun --jobid=<jid> --overlap`), not the resident stack (gateway/webui/sshd/CLI ≈ 1–2 cores). Attribute hot processes: `ps -eo pid,pcpu,comm --sort=-pcpu | head`, then `cat /proc/<pid>/cgroup` → `job_<jid>/step_N/...` shows whose work it is. Job-level `cgroup.procs` is EMPTY (see above), so node-wide ps + per-pid cgroup is the reliable attribution route.
- `RAM cur/limit` = memory.current, which INCLUDES reclaimable page cache. A job pinned at its cap (16.0G/16.0G) is not necessarily at risk: `grep -E "^anon |^file |^kernel " memory.stat` splits real committed memory (anon) from cache. Big rsync/IO (e.g. backing up a 17G model dir) inflates `file` hugely; OOM risk tracks anon, not current.

## Who spawned this step (attribution, 2026-08-15)

When a step is running inside an allocation and you need to know WHICH agent
launched it (and it is not in the dashboard because of step-limit blindness):

1. Step start time: `sacct -j <jid>.<step> --format=JobID,Start,State -P`
   (e.g. `52999.26931` → `2026-08-14T10:49:42`).
2. Find the spawner on the node: `ps -eo pid,lstart,args | grep "jobid=<jid>"`.
   The srun join processes show the full command they ran (`srun
   --jobid=52999 --overlap ... python scripts/benchmark.py dataset=cora ...`).
3. Walk up to the PARENT (`ps -o ppid= -p <pid>` → repeat): the launching
   shell is a `bash -lic` loop whose `cd /cephfs/users/huebers/<repo>` pins
   the agent — e.g. a loop `cd gauge-graph-network ... for tm in dfs bfs
   ...; do srun --jobid=52999 ...; done; echo CORA_TREES2_DONE` is the
   gauge agent's benchmark sweep.
4. Batch .out/.err empty does NOT mean "nothing running" — persistent
   `sleep infinity` allocations only log the wrapper; joined work may
   discard stdout (`>/dev/null 2>&1`), leaving only the sacct record.
   sacct Start + ps command line is the ground truth.

## scontrol show step parsing
- `StartTime=` sits ON the `StepId=` line, not on its own line.
- Executable is `Name=` mid-line (`Nodes=1 CPUs=8 Tasks=1 Name=python`), not line-start.
- `.batch` step = the batch holder (sleep infinity for persistent allocs); `.extern` = slurm extern; other steps = joined srun work.

## Implementation
The user's dashboard: `~/.local/bin/allocation-dashboard` — 5s refresh, tmux-friendly, flock-guarded (ALLOC_DASH_NO_LOCK=1 to test without disturbing the live instance). Probe design is the PERSISTENT join (one `alloc-probe-persist.py` step per RUNNING job, spawned via `ensure_probe` in the refresh loop, sampled via non-blocking `read_probe`) — NOT per-refresh transient sruns, which exhaust MaxStepCount (see pitfall above). The persistent probe step shows in step listings as `python3 alloc-probe-persist.py`; the age-based step filter (30s, below) keeps it visible since it persists.

Layout is a USER PREFERENCE — keep it compact (2026-08-12): three sections (persistent allocations / gpu jobs / cpu-only jobs), one metrics line per job (CPU+RAM+GPU together), and hide .extern/.batch steps plus the GPU label. Do not "improve" it back to the verbose multi-line layout. Details: `references/allocation-dashboard.md`.

Headers carry job counts (2026-08-16): the user asked "in the headers can we print how many jobs we have". Fetch `get_jobs()` BEFORE building the header, then: top line `slurm dashboard — 11 jobs (11 running)` (running/pending/other breakdown appended in parens, only non-zero parts); `persistent allocations (found/len(NAMES))`; `gpu jobs (N)` / `cpu-only jobs (N)`. NAMES = [apple, banana, coconut, durian] — mission-control is deliberately NOT in the persistent section (it is the host job).

Step listing = AGGREGATED COUNTS, not per-step rows (2026-08-14): `scontrol show step` returns one step per joined task, all named `python` — listing each row repeated `RUNNING python` 3× per allocation and was useless. The user asked for counts: render `N step(s), M running` plus one grouped line per distinct (name, state) pair, e.g. `3 step(s), 3 running` / `3× RUNNING python`. Group with a dict keyed on (name, state) and sort.

Step-filter pitfall — name-based filtering hides REAL joins (2026-08-14 evening): the dashboard's own probe steps are named `bash`/`nvidia-smi` (it runs `srun ... bash -c script` every refresh), so an early filter excluded any step named "bash". But a real user joining with `srun --jobid=<id> --overlap bash` creates a PERSISTENT step with the same name — it was silently dropped, and a busy allocation rendered "0 step(s), 0 running" while its GPU ran at 100% (real case: durian job 53685.1279, a FIM python process). Slurm exposes no step command (`scontrol show step` has no Command= field; `squeue --steps` %o is empty), so you cannot distinguish by name/command. FIX — discriminate by AGE: probe steps are born-and-dead within the refresh cycle (seconds old at capture); real joins persist for minutes. Drop bash/nvidia-smi steps only when `start` is not None AND `now - start.timestamp() < 30`. Keep .extern/.batch plumbing filter as-is. Verified: 2347s-old bash step kept, extern/batch dropped, transient probes still hidden.

Deployment (2026-08-14): the live dashboard runs in its own tmux session `alloc-dash` on the mission socket (`tmux -S ~/.tmux-sock/mission new-session -d -s alloc-dash -x 200 -y 50 '~/.local/bin/allocation-dashboard'`) — it used to be a detached child of the batch step and could die with the pty. The dashboard is flock-guarded at `/tmp/allocation-dashboard.lock`, but since 2026-08-14 a NEW LAUNCH TAKES OVER: it reads the lock file's PID (plus pgrep fallback), SIGTERMs the old instance, waits for the flock to release (flock dies with the process), then acquires and writes its own PID. So re-running `allocation-dashboard` anywhere always wins — no "another instance is running" error, no manual kill needed; it prints "took over dashboard from previous instance (killed it)". `ALLOC_DASH_NO_LOCK=1` still skips locking entirely for testing. If the alloc-dash tmux session is missing (it can die with a killed instance), recreate it with the new-session command above. Syntax-check (`python3 -m py_compile`) and smoke-test (`ALLOC_DASH_NO_LOCK=1 timeout 8 ... | head`) before swapping.

Full build notes and pitfalls: `references/allocation-dashboard.md`
Job log locations, root-clutter tidy, and safe moves of RUNNING jobs' logs: `references/job-log-hygiene.md`
Adding a new persistent allocation (sbatch template, maintain-watchdog
registration, dashboard NAMES, fleet announcement — the apple/banana/coconut/
durian pattern): `references/persistent-allocations.md`

## Interactive dashboard: live viewport + alt screen (2026-08-15)

The dashboard is a live frame with a scrollable VIEWPORT — NOT a frame-history
pager. User correction (2026-08-15): "i dont want to be able to look at old
frames... i want to scroll up and down WITHIN that frame! and the frame should
update, even when we are scrolling." A frozen-frame scrollback (deque of past
frames, `» scrollback N/M` banner) was built once and REJECTED — do not
rebuild it. The accepted design:

- **Alternate screen buffer** (`ALT_ON=\x1b[?1049h`, `ALT_OFF=\x1b[?1049l`):
  entered at startup, released on exit AND in a SIGTERM handler (takeover kills
  with SIGTERM — without the handler the pane is left inside the alt screen).
  Result: refreshes replace the frame in place; tmux scrollback stays at the
  pane height instead of accumulating a frame every 5s (was 11,960 lines and
  growing). This is the standard fix for "keeps printing below what already
  existed".
- **Live viewport, no history**: build the FULL frame every refresh; render a
  window of it (`out[view_off : view_off + rows - 2]`). `view_off` is clamped
  to `max(0, len(out) - (rows - 2))` each render. Scroll keys move the window
  WITHIN the current frame; the frame itself keeps rebuilding every REFRESH_S
  underneath, so content and timestamps update while scrolled. Footer shows the
  window position: `view 1-22/29` (only when the frame overflows).
- **Key mapping** (`read_key()` in tty.setcbreak, keeps ISIG so Ctrl+C works;
  parses arrows/PgUp/PgDn/Home/End escapes + vim j/k/b/space/g/G): ↑/k and
  ↓/j line-scroll; PgUp/PgDn page-scroll; g/G jump top/bottom; q quits.
  Apply via a pure `apply_key(key, view_off, maxoff, rows)` → int function
  (no state, trivially testable). Re-render immediately on each key in the
  sleep loop — do NOT break out of it, so multiple scrolls work within one
  frame and the next refresh still lands on schedule.
- No `fit_to_screen` trimming, no "N line(s) hidden" marker — the viewport
  replaces both (scroll reveals the hidden lines).
- **CRITICAL PITFALL — terminal left in `-echo` after exit (2026-08-15)**:
  the dashboard runs in `tty.setcbreak` (disables ECHO+ICANON). If any exit
  path skips the termios restore, the shell is left with echo OFF — the user
  types and letters don't appear (`stty -a` shows `isig -icanon iexten -echo`;
  `stty sane` heals it manually). Two compounding bugs:
  1. The SIGTERM takeover handler used `os._exit(0)` — which SKIPS the
     `finally:` block that restored termios. Any kill-by-takeover (the
     standard way the dashboard restarts!) left the pane mute.
  2. Even the `finally` restore was wrong: it restored the CAPTURED
     `old_attr`, but if a previous unclean exit had already poisoned the tty,
     the captured baseline was itself the broken `-echo` state — the "restore"
     re-applied brokenness forever.
  FIX — a `restore_term()` helper that FORCES `ECHO|ICANON|ISIG` back on
  (never restores the possibly-corrupt captured attrs), called from BOTH the
  `finally:` block AND the SIGTERM handler before `os._exit`. General rule
  for any cbreak TUI: `os._exit` in signal handlers skips `finally`; restore
  terminal state explicitly in the handler itself, and force the canonical
  bits rather than trusting a captured baseline that may already be corrupt.
- **CRITICAL PITFALL — subprocess children steal the pty stdin**: srun probe
  children inherit the dashboard's stdin (the shared pty). They consume
  buffered keypresses before read_key sees them — symptom: Ctrl+C works (SIGINT
  is tty-level) but q/arrows do nothing, and only the probe-running dashboard
  is affected (a pure key-loop test in the same pane works fine). Fix:
  `stdin=subprocess.DEVNULL` on EVERY subprocess.run in the probe path. Any
  interactive pty app that spawns children needs this.
- **Input must be decoupled from the probe cadence (key-reader thread)**:
  polling read_key only once per frame makes scroll/quit wait up to 5s — the
  user calls this "super unresponsive". Fix: a daemon `key_reader` thread
  blocks on the tty (read_key with a long timeout) and pushes actions onto a
  `queue.Queue(maxsize=32)`; the main loop drains it (a) right after
  rendering and (b) inside a fine-grained sleep loop
  `while time.time()-t0 < remaining: key_q.get(timeout=0.1)`), so keys
  respond in ~0.1s while srun probes still run at most once per REFRESH_S.
  In the LIVE-VIEWPORT design do NOT `break` the sleep loop after a scroll
  key — keep polling so multiple scrolls apply within one frame, and the
  next refresh lands on schedule (the older scrollback design broke out to
  refresh immediately; that is obsolete). Non-interactive path keeps a
  plain `time.sleep`. Verified: scroll engaged in <0.8s (incl. capture
  round-trip) with probe cadence unchanged.
- **Trailing-newline overflow**: writing banner+rule+body+footer with a
  trailing "\n" makes N+1 lines; in an N-row pane the banner scrolls off the
  top. Drop the final newline when the content fills the pane.
- Debug technique that isolated the stdin bug: copy the script, inject a
  `logd()` line before/after read_key writing to a file, run in the pane,
  drive keys via `tmux send-keys`, read the log. Faster than guessing.
- Non-interactive runs (pipes, tests) skip alt screen + cbreak: guard with
  `interactive = sys.stdin.isatty() and sys.stdout.isatty()`.
- Pane is 80x24; the alloc-dash tmux session was recreated with a shell first
  (`new-session -d -s alloc-dash` then send-keys the dashboard) so it survives
  dashboard restarts/takeovers instead of dying with the process.
