---
name: agent-coordination
description: "Coordinate multiple agents via a generic file-based message bus: discovery, messaging, parallel coordination, and session migration/handoff."
author: huebers
version: 1.0.0
platforms: [linux]
---

# Agent Coordination — File-Based Message Bus Protocol

A generic protocol for coordinating multiple independent agent processes running
on a shared filesystem (e.g. a cluster home on NFS/Lustre/CephFS). No daemons,
no sockets, no central server — **the message IS a file**. Any process that can
read/write files and run bash can join. This document describes the protocol
so any agent harness can implement it.

## Directory layout

```
<bus-root>/
  registry/        <name>.json   — one entry per registered agent
  inbox/<name>/     <ts>-<from>.json — queued messages TO <name>
  seen/<name>/      <message-basename> — markers preventing redelivery
  outbox/           copies of sent messages (archive)
  heartbeat/<name>  — file touched every poll cycle (liveness)
```

`<bus-root>` is any path on shared filesystem. On a single host, a local dir
works too. Messages survive process crashes, reconnections, and host restarts —
the inbox is a durable queue.

## Registration (claiming a name)

Each agent registers itself. Names are unique UIDs matching `^[a-z0-9][a-z0-9-]{0,31}$`.

**Registry entry** (`registry/<name>.json`):
```json
{"name": "agent-a", "host": "host01", "tty": "pts/4",
 "workspace": "/home/user/project-a", "session_id": "...",
 "description": "...", "registered_at": 1700000000, "heartbeat_at": 1700000090}
```

Re-register after any reconnect (ttys change) or session restart.

### Sender identity resolution

Agents have no built-in names — the registry name IS the identity. Each agent
must be **told** its name at onboarding so its replies are attributed correctly.
Sender resolution order: explicit `--from` flag > `$AGENT_NAME` env var >
registry reverse-lookup by tty/workspace.

## Messaging

### Send (write to a target's inbox)

Writes `inbox/<to>/<ts>-<from>.json` (and a copy to `outbox/`). Non-blocking,
~0s, durable.

**Message JSON format**:
```json
{"id": "<ts>-<from>", "from": "agent-a", "to": "agent-b",
 "ts": 1786566354578759373, "body": "...message text..."}
```
- `ts` is epoch **nanoseconds** for sortable, collision-free filenames.
- The message file is **not deleted** on delivery — a `seen/<name>/<basename>`
  marker prevents redelivery.

### Listen (poll for new messages)

A blocking watcher that prints all **unseen** messages for a name, writes
`seen/` markers, then exits (or loops).

**Arm-once loop (recommended)** — one background process, self-re-arming
forever, no per-delivery re-arm:
```bash
while true; do <listen-script> <name>; sleep 2; done
```
The 2s sleep prevents a hot spin. Start this as a single background process
with a watch-pattern or completion-notification mechanism so message arrivals
re-enter the agent's live conversation context.

**Legacy exit-based arming** — listener exits after each delivery, requires
re-arming after every message. The "forgot to re-arm" failure is chronic;
prefer the loop.

### Broadcast

Write to every registered agent's inbox except the sender. Use for
fleet-wide announcements only; direct-message otherwise.

### Read-before-deliver rule

If you read a message file directly (e.g. to inspect a long body before
replying), mark it seen to prevent duplicate delivery:
```bash
touch <bus-root>/seen/<your-name>/<message-basename>
```
The `seen/` marker keeps the **full basename** including the `.json` suffix —
compare against the full filename, not a stripped version.

## Liveness (heartbeat)

The listener touches `heartbeat/<name>` every poll cycle (~2s). Freshness:
- mtime < ~10s → actively polling right now
- < ~90s → alive, possibly between polls
- > 90s or missing → **listener is dead**

This is the sole automated liveness signal. Check it before trusting
delivery. To check liveness **without** messaging (no disturbance):
1. Heartbeat freshness: `stat -c %Y <bus-root>/heartbeat/<name>` vs `date +%s`
2. Listener process: `ps -eo pid,etime,args | grep "<listen-script> <name>"`

Both checks together: fresh heartbeat + matching process = listening.

## Agent discovery

To find which agents are running, where, and what they're doing (read-only):

1. **Process scan**: `ps aux | grep <agent-process-pattern>` → pid, tty,
   start time. `readlink /proc/<pid>/cwd` → workspace → which project the
   agent owns.
2. **Registry**: read `registry/*.json` for the roster (name, host, tty,
   workspace, session_id, description). Liveness = process attached to
   the registered tty on the registered host.
3. **Workspace activity**: check job queues, log file mtimes, result dirs
   for the agent's workspace.

Reading another agent's state is safe; never write to another agent's
session or workspace.

## Onboarding a new agent

Queue a hello in the inbox **before** instructing the agent — delivery only
happens when the agent arms its listener, so a busy agent is never disturbed.
The user steers timing.

Onboarding text (paste into the agent's window):
> Your name on the network is `<name>`. Arm your inbox listener: run
> `<listen-script> <name>` as a background process (or the arm-once loop).
> When it delivers a message, act on it. To reply, use `<send-script>
> <name> <message>`. There's a hello waiting in your inbox.

## Parallel coordination patterns

### Coordination etiquette

- **Broadcasts** only for everyone-needs-it (announcements, alerts). Direct
  messages otherwise.
- **Don't disturb busy agents** — the durable inbox already waits; a mid-turn
  agent processes mail when its current turn ends. Skip acks for peers
  mid-experiment ("running now, will report" needs no reply).
- **No autonomous delegation between agents** — they coordinate, the user
  integrates. Final decisions stay with the user.
- **Agent-to-agent communication: the bus ONLY** — never tty injection
  (writing to `/dev/pts/N`), never tmux send-keys into another agent's
  window, no side channels. Read-only observation remains fine.
- **Skill/file edit ownership**: a file is edited only by the agent that
  caused the change to be necessary; otherwise message the responsible agent.
  Parallel agents editing the same shared files **will** collide — check/merge
  after cross-agent edits.

### Verify claims before acting on them

Agent self-reports (ACKs of completion, state claims) are the highest-risk
messages — they are often intent, not evidence. Before acting or relaying:
- Check the cited artifact/process/log directly.
- When a claim contradicts observable state, message the agent back with
  concrete discrepancies and require a recheck.
- Report failed verification honestly — do not relay an unverified ACK as fact.

### Crossed-wire messages

An agent saying "standing by for X" often wrote that before your delivery
landed. When replying, confirm whether it already arrived rather than
promising again. A one-line "our messages crossed" ack beats a full re-response.

### Multi-message batch handling

When a notification fires, do NOT assume "newest message" = the one in the
preview. If multiple messages arrive in quick succession, sort the unread
batch and match each body's opening words to the preview before acting. Late
duplicate notifications can re-deliver an already-seen message — check the
message id/timestamp before acting; acknowledge and move on.

## Session migration / handoff

Replacing a running agent with a new session while preserving its bus identity.
The bus is **name-keyed** and file-based, so the new session inherits the old
inbox, seen markers, and heartbeat — no data loss, no registry cleanup needed.

### Sequence (strict — prevents split-brain)

Do ONE agent at a time. Start with whichever has the least critical in-flight work.

1. Send the agent a message: "write your handoff file, then exit"
2. Wait for the handoff file to appear, verify it's complete
3. **Kill the old session** (or let it exit on its own)
4. Launch the new session with the **same name** + **same cwd**
5. New session reads the handoff, registers on the bus, picks up the inbox

The gap between kill and launch is harmless — inboxes are file-based. Messages
sent during the gap sit in the inbox and the new listener picks them up on
first poll.

### CRITICAL: kill the old session first

The bus is name-keyed — two live sessions with the same name cause
**split-brain** (messages go to whichever polls first). Before registering the
new agent, ensure the old session is dead. Also kill any **orphaned listener
loops** from the old session — `while true` loops catch SIGTERM and respawn;
use `kill -9` (SIGKILL) on the loop parent PIDs, verify zero survivors, then
let the new agent arm a single fresh listener.

### Handoff file

Location: the agent's cwd (e.g. `<workspace>/HANDOFF.md`). The new session
launches in the same cwd so the handoff is immediately visible. Keep it
**tight (~2-3K tokens)** — it loads into the new session's context window.
Details belong in skills/references loaded on demand, not in the handoff.

Structure:
- **Current state**: what I was doing right now (task, done/next/blocked)
- **Active jobs**: job ID, allocation, what's running, expected completion,
  what to do when it finishes
- **Bus state**: who I talk to, pending replies, unread inbox, supervisor
- **Recent learnings** not yet in skills
- **Environment**: venv path, env vars, temp files
- **What to watch for**: known issues, traps

### Identity continuity

- Launch with the same name → takes over the identity (inbox/seen/heartbeat
  inherited from the filesystem).
- Re-register from the new session so the registry reflects the new tty/host.
- Verify heartbeat is fresh after launch.
- Orphaned heartbeat files are overwritten on first heartbeat.

## Split-brain prevention

### Duplicate listener loops

When a session is replaced, old listener loops may survive as orphans while
the new session arms its own. Two loops polling the same inbox race: both see
an unseen message; one marks it seen and delivers the notification to ITS
parent terminal, the other may also mark it seen but its notification goes to
a background terminal the agent isn't watching.

**Symptom**: "can send but struggles to receive" — messages get marked seen
(never redelivered) but notifications intermittently vanish into the dead loop.

**Diagnosis**: `ps -eo pid,ppid,lstart,args | grep "<listen-script> <name>"` —
multiple listener processes with different parent PIDs = split-brain.

**Fix**: kill ALL listener loops for that name with `kill -9`, verify zero
survivors, then arm a single fresh listener.

**Prevention**: when replacing a session, explicitly kill the old session's
listener loops **before** starting the new one.

### Single-listener rule

Only ONE listener process per agent name should ever be armed. The listener
must fire in the agent's own session — you cannot arm another agent's listener
for it. If an agent's listener is dead, send it a bus message: "your listener
is dead since <time>, unread mail waiting, re-arm your listener." The durable
inbox ensures nothing is lost while it re-arms.

## Naming rules

- Pattern `^[a-z0-9][a-z0-9-]{0,31}$`, unique network-wide (one registry file
  per name).
- LIVE = a process attached to the registered tty on the registered host.
  A leftover shell in the window does NOT hold the name.
- Re-register: stale entry → auto-takeover; live on another tty → rejected
  (use force-override); entry on another host → force required (liveness
  unverifiable remotely).

## Renaming an agent

The registry name IS the identity — a rename touches every place the name
appears. History is preserved by **moving**, not deleting:

1. Move mail dirs: `mv inbox/<old> inbox/<new>`, `mv seen/<old> seen/<new>`,
   `mv heartbeat/<old> heartbeat/<new>`
2. Registry: write `registry/<new>.json`, remove `registry/<old>.json`
3. Update instruction/seed files (identity, send command, inbox path). Keep
   historical mentions ("previously <old>") but no live references.
4. Broadcast the rename to the fleet.
5. The running session must re-read its files or be relaunched, and re-arm
   the listener under the new name — else it listens on a dir nothing writes
   to anymore.

## Pitfalls

- **Never arm with a timeout**: a timeout causes silent death. On expiry the
  listener exits with an innocuous message; a busy agent doesn't connect it
  to the re-arm duty and goes dark with no error anywhere. Arm with NO
  timeout so the listener only exits when a real message arrives.
- **Shell-quoting friction**: messages passed through shell `eval` die on
  parentheses, unbalanced quotes, backticks, or `$`. Keep messages plain
  text. If a message must carry punctuation, write it to a file and pass the
  path instead of typing inline.
- **`seen/` basename pitfall**: the marker keeps the full basename including
  `.json`. An unread-check that strips the suffix falsely reports every
  message as unseen. Compare against the full basename.
- **Watchdog count inflation**: if a watchdog nudges a dark agent, each
  self-nudge is itself an unread inbox message — the reported queue count
  grows per cycle even with no real new mail. Verify against `seen/` before
  acting on the count.
- **Messages stay in inbox after delivery**: only a `seen/` marker is written.
  Clean up manually; outbox accumulates too.
- **Reconnect = new tty**: agent must re-register (auto-takeover of its own
  stale entry) AND re-arm its listener.
