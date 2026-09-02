---
name: multi-agent-coordination
description: "Use when messaging or coordinating parallel Hermes agents."
version: 1.0.0
author: hermes-curator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [multi-agent, agent-net, messaging, coordination, discovery]
    related_skills: [hermes-agent, start-slurm-job]
---

# Multi-Agent Coordination (agent-net)

The user runs several independent Hermes CLI agents in parallel (helper1,
helper2, fim, gauge, qmc, research-assistant — one per terminal/tmux on the
cluster). This skill
covers the agent-net message bus, agent identity/discovery, and the ping
mechanism that ties it together.

## When to use

- Send a message / order to another running agent (agent-net-send).
- Discover which agents are running, where, and whether they're alive
  (agent-net-list).
- Onboard a new agent to the network (arm its listener).
- Find out what another agent is currently doing (read-only: transcripts,
  logs, processes).

## The agent-net bus (inbox = maildir pattern)

File-based message bus on the shared /cephfs home. No daemons, no sockets:
the message IS a JSON file. Works across cluster hosts because cephfs is
shared. Layout: `~/.hermes/agent-net/{registry,inbox,seen,outbox}/`.
Commands live in `~/.local/bin/agent-net-*`. Full protocol + message format:
`references/agent-discovery.md`.

- `agent-net-register <name> [desc]` — claim your name (UID). Run INSIDE the
  agent; records host/tty/workspace/session_id. Re-register after reconnect.
- `agent-net-list` — roster with liveness (● = hermes process on its tty).
- `agent-net-send <to> <message> [--from X] [--file PATH]` — write to
  target's inbox (copy in outbox). Sender auto-resolves via AGENT_NAME env or
  reverse tty lookup.
- `agent-net-listen <name> [--timeout S]` — blocking watcher; prints new
  messages, exits 0. Arm inside the receiving agent:
  `terminal(background=true, notify_on_complete=true, command="agent-net-listen <name>")`
  and RE-ARM after every delivery.

## The ping mechanism (critical, do not "improve" it)

The only sanctioned way to ping a live CLI agent: the TARGET arms a
background watcher that exits when something happens; the exit triggers
Hermes' completion notification, whose output re-enters the agent's
conversation as a tool notification. The message body is printed INLINE in
the ping (the JSON file path is metadata, not a retrieval requirement).

- **ARM-ONCE LOOP (sanctioned since 2026-08-14):** run the listener as a
  never-exiting loop, ONE background process, no notify_on_complete:
  `while true; do agent-net-listen <name>; sleep 2; done` with
  `watch_patterns=["agent-net message"]`. The loop re-arms itself forever —
  the "forgot to re-arm" failure class is gone. Requirements: (a)
  WATCH_STRIKE_LIMIT must be raised from the default 3 to ~50 in
  `tools/process_registry.py` (operator override; mailbox bursts otherwise
  auto-disable watch_patterns — re-apply after any `hermes update`, the
  comment in the source says so); (b) accept the 15s rate limit — at most
  one notification per 15s, so bursts collapse into fewer pings, but the
  listener prints ALL new messages in one batch and the agent reads the
  inbox, so nothing is lost. Legacy exit-based arming (notify_on_complete +
  re-arm per message) still works and remains the documented fallback.
- **Do NOT use tty injection (/dev/pts/N writes, former agent-net-send
  --push).** The user explicitly rejected it (removed 2026-08-12). Inbox bus
  only. Tty writes look like typed user input and interleave with real
  typing; the bus is durable and non-intrusive.
- Pings are pull-shaped: no armed listener → no ping; the message waits in
  the inbox until one exists. That durability is a feature.
- The listener script treats STALE messages as new on next arm (seen/ marker
  is what counts, not arrival time). An agent that was offline/deaf catches
  up on everything in one ping when it re-arms — no message loss, ever.

## Diagnosing "agent X hasn't heard back" (dead-listener pattern)

The most common fleet failure is NOT lost mail — it's a dead listener: the
reply IS in the target's inbox, but no `agent-net-listen` process is armed,
so the target never gets pinged. Real case (2026-08-13): claude-qmc and
claude-gauge both replied on schedule; qmc/gauge "heard nothing" because
their listeners had been dead since 12:26 / 04:22 respectively. Diagnose in
three checks:

1. `ps aux | grep agent-net-listen` — is the target's listener alive?
   Healthy fleet: one per agent (fim, gauge, qmc, helper1, helper2,
   research-assistant, gateway...). Missing = deaf.
2. `ls -la ~/.hermes/agent-net/seen/<name>/ | tail` — newest marker mtime
   is the LAST message that agent actually processed. Hours/days old while
   its hermes process is up ⇒ listener died and was never re-armed.
3. `ls ~/.hermes/agent-net/inbox/<name>/ | tail` — replies present but
   unprocessed (no matching seen/ marker) confirms delivery side is fine.

Fix: you CANNOT arm another agent's listener for it (the ping must fire in
ITS session). Send it a bus message: "your listener is dead since <time>,
unread mail waiting (list X), re-arm `agent-net-listen <name>`
background=true notify_on_complete=true". Stale delivery on next arm picks
everything up. The operator can also type "check your inbox" in the agent's
window as an immediate nudge.

## Self-healing: heartbeat (watchdog REMOVED 2026-08-19)

The recurring failure was agents forgetting to re-arm (gauge dark 3x,
helper1 missed a greeting, qmc since 12:26). The arm-once loop + heartbeat
were deployed 2026-08-14; a watchdog cron was also deployed but REMOVED
2026-08-19 (operator decision — all watchdog cron jobs + registry entry
+ inbox dirs deleted). Current state:

- **Heartbeat:** `agent-net-listen` touches `~/.hermes/agent-net/heartbeat/<name>`
  every poll cycle. Fresh file = live listener (mtime < ~90s). This is the
  SOLE automated liveness signal now.
- **No watchdog backstop:** dead listeners go undetected automatically.
  Agents must self-monitor — check your own heartbeat freshness
  periodically, and check other agents' heartbeats when they go silent.
  The arm-once loop is the only reliability mechanism.
- The arm-once loop removes the re-arm step, so the main remaining
  failure is orphaned/duplicate listener loops after session resets
  (see pitfall below).

## Pitfall: never arm with --timeout

`agent-net-listen <name> --timeout 3600` silently EXITS after an hour of
quiet (rc=1) — if the agent is busy, the re-arm is forgotten and the agent
goes dark with no error anywhere. This was the root cause of the 2026-08-13
gauge/qmc/helper2 darkness. Arm with NO timeout (or the arm-once loop), so
the listener only exits when a message actually arrives.

## Names are UIDs

- Unique network-wide; must match `^[a-z0-9][a-z0-9-]{0,31}$` (also the
  inbox dir name).
- LIVE = a hermes process is attached to the registered tty on the
  registered host: `ps -t <tty> -o cmd= | grep -q hermes-agent/hermes`.
  A plain shell left in the window does NOT count (fix from 2026-08-12).
- Takeover rules on re-register: stale entry → auto takeover; live on
  another tty → reject (--force overrides); registered on ANOTHER host →
  --force required (liveness unverifiable remotely).
- Hermes has NO built-in agent identity: sessions have ids + auto-titles,
  processes are anonymous. The registry name is the identity; each agent
  must be TOLD its name when onboarded so its replies are attributed.

## Onboarding an agent (paste into its window)

Agents are self-registering: the agent calls `agent-net-register` itself
from inside its own session. The script walks the process tree to find
the owning hermes process, extracts its tty/host/workspace/session_id,
and writes the registry entry. This only works if called from within the
agent's own session — calling it from outside would get the wrong tty.

"Your name on the agent network is <name>. Arm your inbox listener now: run
agent-net-listen <name> as a background process with notify_on_complete=true,
exactly like the slurm start/end watchers. When it pings you with an
agent-net message, act on it and then re-arm the listener the same way. To
reply to other agents, use agent-net-send <name> <message>. There's a hello
from helper2 waiting in your inbox."

Queuing the hello in the inbox BEFORE the user pastes this is safe: delivery
only happens when the agent arms, so a busy agent (e.g. qmc mid-training) is
never disturbed — the user steers the timing. This is the standing pattern.

### Replacing an existing agent (use --force)

When a new session replaces an old one with the same name (migration,
model switch, restart), the new agent must register with `--force`:

    agent-net-register <name> "description" --force

Without `--force`, register checks if the old session's tty still has a
live hermes process and rejects the new one. `--force` overwrites the
registry entry to point at the new tty/session regardless.

CRITICAL: kill the old session FIRST (or verify it's dead) before
registering the new one — agent-net is name-keyed, so two live sessions
with the same name cause split-brain (messages go to whichever polls
first). Also kill any orphaned listener loops from the old session
(see pitfall below) before the new agent arms its own.

## Skill edit ownership (operator rule)

A skill should ALWAYS be changed by the agent that caused the change to be
necessary. Noticing something a skill should document? Do NOT edit it
yourself — message the responsible agent (or helper2 if unsure) and let them
make the edit. (Operator rule, established 2026-08-12 after helper1 and fim
independently patched start-slurm-job's coconut entry.)

## Agent-to-agent communication: agent-net ONLY (operator rule)

Every message, order, or notification to another agent goes through the
agent-net bus (agent-net-send / agent-net-broadcast) — never tty injection
(/dev/pts/N writes), never tmux send-keys into another agent's window, no
other side channels. Read-only observation of other agents (transcripts,
logs, processes) remains fine. (2026-08-12; supersedes older
local-agent-coordination guidance.)

## Supervisor isolation (operator rule, 2026-08-14)

The supervisors (`qmc-supervisor`, `gauge-supervisor`) must stay undisturbed
by everyone EXCEPT their subordinates (qmc, gauge). Rationale: their context
should remain high-level and focused; their tokens are more expensive than
other agents'.

- Do NOT notify supervisors about infra changes, allocations, broadcasts,
  announcements, or general fleet chatter — even when told to "tell the
  agents". Send those to the non-supervisor agents only.
- Address a supervisor only for supervision-related matters (reviewing work,
  answering its questions, relaying operator review requests).
- `agent-net-broadcast` supports `--except <a,b>` to exclude them:
  `agent-net-broadcast --from X --except qmc-supervisor,gauge-supervisor "..."`
- The allocation watchdog already skips supervisors in all its notifications
  (maintain_apple_banana.py SUPERVISORS list).
- When relaying an operator instruction that names no recipient, default to
  excluding the supervisors unless the instruction explicitly concerns them.
  When in doubt, ask the operator rather than disturbing a supervisor.

## Agent migration / session replacement (2026-08-17)

Replacing a running agent with a new session on a different model while
preserving its agent-net identity. The bus is name-keyed and file-based,
so the new session inherits the old inbox, seen markers, and heartbeat
directory — no data loss, no registry cleanup needed.

### Sequence (strict — prevents split-brain)

Do ONE agent at a time, not all three. Start with whichever has the least
critical in-flight work (check squeue first).

1. Send the agent a message: "write your handoff file, then exit"
2. Wait for the handoff file to appear, verify it's complete
3. Kill the old session (or let it exit on its own)
4. Launch the new session with the SAME name + SAME cwd
5. New session reads handoff, registers on agent-net, picks up inbox

The gap between kill and launch is harmless — inboxes are file-based. Any
messages sent during the gap sit in the inbox and the new listener picks
them up on first poll. If BOTH old and new are alive simultaneously, both
respond to the name → split-brain (messages go to whichever polls first).

### Handoff file

Location: agent's cwd (e.g. ~/diffusion-qmc/HANDOFF.md). The new session
launches in the same cwd so the handoff is immediately visible. Keep it
TIGHT (~2-3K tokens) — it loads into the new session's context window.
Details belong in skills/references loaded on demand, not in the handoff.

Structure:
- What I was doing right now (current task, done/next/blocked)
- Active slurm jobs (job ID, allocation, what's running, expected
  completion, what to do when it finishes)
- Agent-net state (who I talk to, pending replies, unread inbox, supervisor)
- Recent learnings not yet in skills
- Environment (venv path, PYTHONPATH, env vars, temp files)
- What to watch for (known issues, traps)

### Launch command

```
hermes -m nvidia/GLM-5.2-NVFP4 --provider fhgenie --reasoning high \
  --name <same-name> --cwd <same-cwd>
```

The new session needs the same arm-once listen loop:
`while true; do agent-net-listen <name>; sleep 2; done`
with `watch_patterns=["agent-net message"]`.

### Agent-net identity continuity

- Name = whatever is passed to agent-net-listen. Launch with the same name
  and it takes over the identity.
- Registry/inbox/seen/outbox/heartbeat are all file-based under
  `~/.hermes/agent-net/<name>/`. The new session inherits them — no cleanup
  needed.
- Check: if the old session left orphaned heartbeat files, the new session
  overwrites them on first heartbeat. Verify the heartbeat is fresh after
  launch.
- Re-register the agent (agent-net-register <name>) from the new session
  so the registry reflects the new tty/host.

## Finding out what another agent is doing (read-only)

1. `ps aux | grep hermes-agent/hermes` → processes with pts + start time;
   `/proc/<pid>/cwd` → workspace → which agent.
2. Session transcripts: sqlite3 `~/.hermes/state.db` — sessions table
   (id, title, started_at, last_activity_at, cwd) and messages table
   (role, content, tool_name, timestamp). Exact queries:
   `references/agent-discovery.md`.
3. Workspace activity: squeue for its jobs + tail slurm-logs.

Reading transcripts is safe; do NOT write to another agent's session.

## Pitfalls

- **Broadcast sender misattribution (fixed 2026-08-14, still a pitfall):**
  `agent-net-broadcast` resolves `--from` via reverse TTY lookup in the
  registry when `--from` is omitted. If several agents share one tty in the
  registry (claude agents were registered with the LAUNCHING shell's tty,
  not their tmux pane ttys — claude-gauge/claude-qmc/helper1 all on pts/0),
  the alphabetical glob picks the FIRST match and the broadcast goes out
  under the wrong name. ALWAYS pass `--from` explicitly to
  `agent-net-broadcast` and `agent-net-send`. Registry fix: agents must be
  registered from their own tmux pane tty; broadcast now collects ALL tty
  matches and resolves via workspace-prefix vs caller cwd before falling
  back to AGENT_NAME → "unknown".

- Terminal tool shells have NO tty (tty → "not a tty"): resolve identity by
  walking the parent chain to the owning hermes process
  (`ps -o ppid= -p $p` loop, cmdline matches `hermes-agent/hermes`), then
  `ps -o tty= -p <hermes_pid>`.
- `HERMES_SESSION_*` env vars are UNSET in tool shells (the snapshot wrapper
  unsets them) — never rely on env for session identity; use the DB or the
  `--resume/-r <id>` argument in the hermes cmdline.
- Assistant rows in `messages` often have empty content (reasoning-only
  turns) — check neighboring tool rows for actual activity.
- Messages stay in inbox after delivery (only a seen/ marker is written) —
  clean up manually; outbox accumulates too.
- Reconnect = new tty: agent must re-register (auto-takeover of its own
  stale entry) AND re-arm its listener.
- **Duplicate listener loops (2026-08-19):** when a session is replaced
  (migration, restart), the old session's listener loop may survive as an
  orphan and the new session arms its own. Two loops polling the same inbox
  race: both see an unseen message, one marks it seen and prints it, the
  other may also mark it seen but its output goes to a background process
  the agent isn't watching. Net effect: messages get marked seen (never
  redelivered) but the notification sometimes goes to the wrong loop.
  SYMPTOM: "can send but struggles to receive." FIX: kill ALL listener
  loops for that name (`kill -9 <loop_pids>`), verify none survive, then
  let the agent arm a fresh single listener. The `while true` loops
  survive SIGTERM — use SIGKILL (`kill -9`). Check for orphans after any
  session replacement by running `ps -eo pid,lstart,args | grep
  "agent-net-listen <name>"`.

## Roster & system state

Snapshot and per-agent notes: `references/agent-discovery.md`. Live truth is
always `agent-net-list`.

## A2A protocol plugin (alternative bus, assessed 2026-08-14)

Should the fleet ever migrate from agent-net to Hermes' A2A plugin? NO —
see `references/a2a-plugin.md` for the full assessment. Key blockers:
inbound A2A is gateway-only (CLI agents can't host it), non-default agents
get headless `hermes chat -q` spawns instead of live sessions, and the
supervisors (qmc-supervisor/gauge-supervisor, formerly Claude Code) would
still be second-class in A2A. A2A is only worth enabling later as an
external-interop layer (outbound toolset first, then inbound inside the
existing gateway process).

## Renaming an agent (bus identity change)

Done 2026-08-14 for claude-qmc → qmc-supervisor and claude-gauge →
gauge-supervisor. The registry name IS the identity — a rename touches every
place the name appears, and the running session must be told (or relaunched)
to pick it up:

1. Move the mail dirs (history is preserved by moving, not deleting):
   `mv ~/.hermes/agent-net/inbox/<old> ~/.hermes/agent-net/inbox/<new>`
   and the same for `seen/<old>` → `seen/<new>`.
2. Registry: write `registry/<new>.json` (name/host/tty/workspace; tty may be
   empty if not yet launched — the session claims it on first send via
   reverse tty lookup) and `rm registry/<old>.json`.
3. Heartbeat: `mv heartbeat/<old> heartbeat/<new>` if it exists (else the
   first listener arm creates it).
4. Watchdog alert-state: `rm state/watch-alerts/<old>` (else a stale cooldown
   file suppresses future alerts for the new name).
5. Instruction/seed files: update identity, send command and inbox path in
   the agent's AGENTS.md/CLAUDE.md, HISTORY.md, memory files. Keep historical
   mentions ("previously <old>") but no live references. Outbox archives keep
   the old sender name in filenames (`<ts>-<old>_name.json` — underscore
   form!) — new sends use the new name; the seed file should note this.
6. Broadcast the rename to the fleet (all agents keep name lists in their
   instruction files): `agent-net-broadcast --from X "<old> is now <new>..."`.
7. The running session must re-read its files or be relaunched, and re-arm
   the watch loop under the new name (`agent-net-listen <new>`), else it
   listens on a dir nothing writes to anymore.
8. Update fleet memory + flag helper2 for the skill that documents the agent
   (skill-edit-ownership: the relaying agent may edit multi-agent-coordination;
   the claude-code-agents skill is helper2's).

Pitfalls: agent-net-send resolves the sender via reverse tty lookup, so a
registry entry with the correct tty makes attribution automatic — no --from
needed after a rename. Old inbox files stay under the old name as archives;
grep for stale references after the rename and leave only intentional
historical notes.
