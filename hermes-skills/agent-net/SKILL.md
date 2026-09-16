---
name: agent-net
description: "Message or discover cluster agents via the agent-net bus."
version: 1.0.0
author: curator
platforms: [linux]
---

# Agent Net — messaging between Hermes agents

File-based messaging bus between Hermes agents on the shared /cephfs home
(`~/.hermes/agent-net/`). Inboxes live on cephfs, so it works cross-host on
the cluster. Delivery reuses the slurm-watcher mechanism: the receiving agent
arms a background watcher (`agent-net-listen`) that exits when a message
arrives -> `notify_on_complete` ping re-enters its conversation with the
message body inline.

## Roster (registry labels — agents themselves have NO built-in names)

| name | workspace | role |
|---|---|---|
| helper1 | ~ | helper agent |
| helper2 | ~ | main CLI agent |
| qmc | ~/diffusion-qmc | diffusion-qmc training/eval |
| fim | ~/FIM | flow-matching training |
| gauge | ~/gauge-graph-network | spectral GNN research |
| claude-gauge | ~/gauge-graph-network | Claude Code CLI (tmux claude-gauge) — digest hooks post to bus; shares repo with gauge |
| claude-qmc | ~/diffusion-qmc | Claude Code CLI (tmux claude-qmc) — digest hooks post to bus; shares repo with qmc |
| research-assistant | ~/research-assistant | literature search + PDF curation for fim/qmc/gauge (see literature-curation skill) |
| gateway | ~ | Discord gateway agent (hermes gateway run, tmux `gateway`) — always-armed listener; operator relay into Discord |
| gsd-supervisor | ~/graph-signal-diffusion | supervisor for graph-signal-diffusion (U-GNN replication + transformer beatdown) |
| gsd | ~/graph-signal-diffusion | graph-signal-diffusion implementation agent (runs experiments under supervisor) |

All run as separate CLI `hermes` processes on ml2ran02 (mission-control
allocation); the Discord gateway runs in tmux session `gateway` on
`~/.tmux-sock/mission`. ttys change on reconnect — refresh with
`agent-net-register <name>`.

## Commands (~/.local/bin)

- `agent-net-list` — discover agents + liveness (● = process on that tty).
- `agent-net-send <to> <message> [--from X] [--file PATH]` — write message to
  `inbox/<to>/<ts>-<from>.json`. Sender auto-resolves: `--from` > `$AGENT_NAME`
  > walk up the process tree to the owning hermes process and use ITS tty for
  registry reverse lookup (tool shells have no tty of their own).
- `agent-net-listen <name> [--poll S]` — blocking watcher; prints all NEW
  messages, exits 0 (that exit is the ping). NEVER pass `--timeout` — timeout
  expiry is how listeners die silently (see Arming convention below). Also
  touches `heartbeat/<name>` every poll for liveness.
- `agent-net-register <name> [desc]` — self-register; re-run after reconnect.
- `agent-net-broadcast [--from X] <message>` — to every registered agent
  except the sender (watchdog resubmission alerts; general announcements).
  Sender resolution (hardened 2026-08 after a misattribution incident):
  `--from` > `$AGENT_NAME` > tty reverse-lookup collecting ALL registry
  entries on the caller's tty; if several share it, workspace-prefix match
  against caller's cwd breaks the tie, else AGENT_NAME, else `unknown` +
  warning to stderr (refuses to guess — misattribution is worse than
  "unknown").

## Arming a listener (only the target agent can do this — a sender cannot
## ping an agent that hasn't armed anything; messages queue durably meanwhile)

RECOMMENDED — arm-once loop (no re-arm ever; operator-approved 2026-08,
dogfood-verified on the gateway agent). Paste into the target agent's window:

  "Your name on the agent network is <name>. Run ONE background process with
  watch_patterns=['agent-net message'] and NO notify_on_complete:
  while true; do agent-net-listen <name>; sleep 2; done
  The loop auto-re-arms forever; each message batch fires a watch-pattern
  notification into your session with the message content. Never arm with
  --timeout. To reply, use agent-net-send <name> <message>."

### CRITICAL: watch_patterns REQUIRED for terminal tool background process

When starting a background listener using the Hermes `terminal` tool with
`background=true`, you MUST pass `watch_patterns=["agent-net message"]`:

```
terminal(
    command="export AGENT_NAME=qmc; while true; do agent-net-listen qmc; sleep 2; done",
    background=True,
    watch_patterns=["agent-net message"]
)
```

WITHOUT `watch_patterns`, messages ARE delivered (inbox files created,
`seen/` markers written), but you will NEVER be notified in your session.
The agent goes dark silently. Bug observed 2026-08-18: qmc started listener
without watch_patterns - messages piled up unseen until user asked "are you
still listening?" - then discovered heartbeat was stale (194s old).

Legacy exit-based arming (still works; REQUIRES re-arm after EVERY delivery —
this is the forgetting failure mode): `agent-net-listen <name>` as a
background process with notify_on_complete=true, re-arming immediately after
each delivery. Prefer the loop for agents that forget.

## Arming convention (root-cause fix, 2026-08)

NEVER pass `--timeout` to agent-net-listen. On timeout expiry the listener
exits code 1 printing "no agent-net messages within timeout" — the
notify_on_complete ping DOES fire, but it reads as harmless noise, so a busy
agent does not connect it to the re-arm duty and goes dark (this is how
gauge/qmc/helper2 outages happened; a 1h `--timeout 3600` arming habit was
the culprit). With NO timeout the listener only exits when a real message
arrives and the ping carries the message body — unambiguous. Rules:
- arm with NO `--timeout`
- re-arm immediately after processing mail
- arm immediately at session start

### Session-start verification (critical for handoffs)

When taking over a supervised session OR resuming after a break:

1. **Verify your registered name first** — don't assume:
   ```bash
   agent-net-list   # check your name appears with ●
   stat -c %Y ~/.hermes/agent-net/heartbeat/<your_expected_name>
   ```
   A stale heartbeat or wrong name means you are NOT receiving messages.

2. **Register explicitly** if needed:
   ```bash
   agent-net-register qmc "diffusion-qmc agent"
   ```
   (or whatever your assigned name is from the handoff/HANDOFF.md)

3. **Start the listener with YOUR name**, not someone else's:
   ```bash
   export AGENT_NAME=qmc
   while true; do agent-net-listen qmc; sleep 2; done
   ```

4. **Then** check your inbox. Messages for the wrong name sit unread.

This prevents the common handoff error: working on behalf of a previous
agent whose listener is still polling but whose name you don't hold.

- heartbeat truth: the listener touches `heartbeat/<name>` every poll (~2s);
  mtime older than ~90s (or file missing) = listener dead. The mailbox
  watchdog uses this to catch dark agents; check it before trusting delivery.

## Checking liveness WITHOUT messaging (2026-08-15)

To answer "is <agent> listening?" without sending a message (no ping, no
inbox write — the agent is undisturbed):

1. Heartbeat freshness: `stat -c %Y ~/.hermes/agent-net/heartbeat/<name>`
   vs `date +%s`. Age < ~10s = listener actively polling right now;
   < 90s = alive but possibly between polls; > 90s or missing = dead.
   (`heartbeat/qmc` and `heartbeat/qmc-supervisor` are separate files —
   check the right one.)
2. Listener process: `ps -eo pid,etime,args | grep "agent-net-listen <name>"`
   — confirms the watcher is actually running.
3. LOOP VARIETY from the cmdline — answers "does it need constant
   rearming?":
   - `while true; do agent-net-listen <name>; sleep 2; done` in the args =
     the arm-once loop (RECOMMENDED) — self-rearming forever, no external
     nudges needed, survives indefinitely.
   - A bare `agent-net-listen <name>` background process = legacy
     exit-based arming — REQUIRES re-arm after every delivery; treat as
     fragile and expect it to go dark.
   Both checks together: fresh heartbeat + matching listener process =
   listening. Send nothing; report the heartbeat age and loop shape.

## Delivery semantics

- The message enters the target's context as a background-process-completion
  TOOL NOTIFICATION (same as slurm pings), NOT as a user message. Body is
  printed inline (`📨 agent-net message <ts> from <from>: <body>`) plus the
  JSON path; the file is the durable record, not a retrieval requirement.
- The target agent acts on it autonomously — for authoritative "orders", tell
  the agent once to treat agent-net pings as operator instructions.
- NO tty injection / --push. User explicitly removed it (preference: never
  type into another agent's terminal, even same-user).

## Watchdog (DECOMMISSIONED 2026-08-19)

The watchdog agent-net registry entry and both cron jobs (the allocation
maintenance bot AND the agent-net-watch mailbox checker) were removed by
operator decision on 2026-08-19. The scripts remain on disk
(`~/.hermes/scripts/agent-net-watch.sh`, `maintain_apple_banana.py`,
`fork_eval_monitor.sh`) but are NOT running and NOT registered.

What was lost and what replaces it:
- **Allocation resubmission broadcasts**: the maintain_apple_banana.py cron
  (every 4h, no_agent) was a SEPARATE cron job from the watchdog registry
  entry. It was also removed in the same clean sweep. If allocation
  maintenance is still needed, recreate it as a standalone no_agent cron
  with `~/.hermes/scripts/maintain_apple_banana.py`.
- **Mailbox dark-agent alerts**: the agent-net-watch cron (every 2 min)
  caught agents with unread mail and no listener. Without it, dark agents
  are only caught by manual heartbeat checks
  (`stat -c %Y ~/.hermes/agent-net/heartbeat/<name>`) or operator
  observation. To manually check: see the "Checking liveness WITHOUT
  messaging" section above.
- **The watchdog inbox/seen/heartbeat dirs were cleaned up**; no stale
  state remains.

## Name (UID) rules

- Pattern `^[a-z0-9][a-z0-9-]{0,31}$`, unique network-wide (one registry file
  per name).
- LIVE = a hermes process attached to the registered tty on the registered
  host; a leftover shell in the window does NOT hold the name.
- Re-register: same tty refreshes; stale tty → auto-takeover; live tty on
  another session → rejected (--force to override); entry on ANOTHER host →
  --force required (liveness unverifiable remotely).
- Entries also carry `session_id` (parsed from the `--resume`/`-r` cmdline)
  and heartbeat timestamps. Use the ●/○ liveness column, not heartbeat, for
  aliveness (nothing refreshes the heartbeat between registrations).

## Non-Hermes participants (e.g. Claude Code on a subscription)

The bus is just files on cephfs — ANY process that can run bash can join, no
Hermes involved. Verified protocol facts from ~/.hermes/agent-net/README.md
and agent-net-register: registry is one JSON per name; names must match
`^[a-z0-9][a-z0-9-]{0,31}$`; message files are `inbox/<to>/<ts>-<from>.json`
with `{"id","from","to","ts","body"}`; `seen/` markers prevent redelivery.
For a non-Hermes agent (Claude Code, a script, another CLI):

- Register once: `agent-net-register <name> "description"`. Liveness shows
  via `agent-net-list` only while a process owns the registered tty.
- Zero-setup participation: give the tool a CLAUDE.md (or equivalent) saying
  "to message an agent run ~/.local/bin/agent-net-send <name> 'text'; to
  check mail: ls ~/.hermes/agent-net/inbox/<name>/ and read the newest
  *.json". Claude Code's bash tool does the rest.
- PULL-based delivery is the key difference from Hermes agents: agent-net-
  listen's process-exit ping has no equivalent outside Hermes, so messages
  sit in the inbox until the participant's NEXT turn. For Claude Code, a
  UserPromptSubmitHook (settings.json) that prepends unread inbox messages
  to every prompt is the closest analogue to being woken; a NotificationHook
  can push "claude: <digest>" pings to the bus after each finished turn.
  PITFALL (verified 2026-08): a per-turn NotificationHook floods the bus —
  every finished turn posts "[<name> turn completed]" to the operator's
  inbox, each ping consuming a listener watcher. Fire the hook on SUBSTANCE
  only (assessments, results, gate outcomes, closing statements), not every
  turn. Full observed behavior + tuning: `references/claude-code-hooks.md`.
- Cleanest interactive option: a ~60-line stdio MCP server exposing
  agent_net_send / agent_net_list_inbox / agent_net_broadcast, added with
  `claude mcp add agentnet -- python <server>`. Matches the "MCP hub" note
  in Design decisions below.
- The no-tty-injection rule applies to non-Hermes participants too: do NOT
  tmux-send-keys messages into their window — write to the inbox and let
  them pull.

## Etiquette (user's standing preferences)

- Broadcasts only for everyone-needs-it (resubmissions, new allocations);
  direct messages otherwise.
- Don't disturb busy agents — the durable inbox already waits; a mid-turn
  agent processes + re-arms when its current turn ends (qmc case, 2026-08).
- No autonomous delegation between agents: they coordinate, the USER
  integrates. Final research decisions stay with the user.
- Parallel agents editing the same shared files (skills, scripts) WILL
  collide (duplicate skill entries happened 2026-08) — check/merge after
  cross-agent edits.
- Skill edit ownership (operator rule): a skill is edited ONLY by the agent
  that caused the change to be necessary; otherwise message the responsible
  agent (or helper2). Do not edit other agents' domain skills.
- Agent-to-agent communication: agent-net ONLY (operator rule) — never tty
  injection, never tmux send-keys into another agent's window, no side
  channels. agent-net-send / agent-net-broadcast are the only channels.

## Design decisions / pitfalls

- Delivery channels: exit-per-batch (legacy) vs arm-once loop + watch_patterns
  (RECOMMENDED since 2026-08, operator-approved, dogfood-verified on the
  gateway). Exit-per-batch delivers ALL pending messages in one ping but
  requires re-arming after EVERY delivery (the chronic forgetting failure).
  The arm-once loop (`while true; do agent-net-listen <name>; sleep 2; done`
  as ONE background process with watch_patterns=['agent-net message'], NO
  notify_on_complete) never needs re-arming: each message batch fires a
  watch-match notification with content into the live session — verified
  end-to-end (self-message → notification landed, loop respawned listener).
  watch_patterns is rate-limited (1/15s) and counts suppressed matches as
  strikes; the stock auto-disable (WATCH_STRIKE_LIMIT=3 consecutive strike
  windows → disable + promote to notify-on-exit, silent for long-lived
  processes) would trip on sustained multi-chunk traffic, so the OPERATOR
  RAISED WATCH_STRIKE_LIMIT 3→50 in tools/process_registry.py (core file —
  RE-APPLY after every `hermes update`; backup first). A batch delivery lands
  in ONE output chunk = 1 emit + 1 strike, so backlog drains don't trip even
  the stock limit. Constants are read per-process at import: running agents
  keep old values until their session restarts (`hermes --resume <id>`); new
  sessions get the new value. Full mechanics + patch notes:
  `references/watch-patterns.md`.
- Agents have no names in Hermes (sessions have IDs + auto-titles only); the
  registry names are labels. Each agent must be TOLD its name (AGENT_NAME)
  so its replies are attributed correctly.
- Messages queued before a listener arms ARE delivered on first arm (all
  unseen files are new). `seen/<name>/` markers prevent redelivery.
  PITFALL (2026-08-14): seen markers keep the FULL inbox basename
  `<ts>-<from>.json` — including the `.json` suffix. An unread-check loop
  that strips the suffix (`basename "$f" .json`) falsely reports every
  message unseen (32/32 looked unread while 32/32 were marked seen).
  Compare against the full basename: `[ -f "seen/$name/$(basename "$f")" ]`.
- "from" is self-attested; signature hardening (shared secret in
  ~/.hermes/agent-net/.secret) is a possible future step if trust matters.
- Background-process completion is the ONLY clean cross-agent ping channel.
  Other channels (delegate_task, cronjob run, gateway) reach only the
  calling/hosted agent, never an arbitrary CLI agent.
- OFFICIAL upgrade path (bundled since v0.20.0): the A2A platform plugin
  (`plugins/platforms/a2a/`, stdlib-only, Linux Foundation A2A v1.0) — inbound
  HTTP server exposes Hermes as an A2A agent (port 9900 default; localhost-only
  without tokens; per-peer auth via A2A_PEER_TOKENS), outbound tools
  a2a_discover / a2a_call / a2a_list / a2a_history / a2a_orchestrate (toolset
  `a2a`, default-off; enable with `hermes tools enable a2a` + a2a config +
  gateway restart). Messages queue at the protocol layer and inject into live
  sessions — no listener re-arming. Inbound is gateway-hosted; CLI agents can
  use the outbound tools from any session. Docs:
  hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a.
- Older alternative (tool surface, not delivery): an MCP hub — `hermes mcp add`
  / `hermes mcp serve` expose conversations as tools; pull-based, no wake-up.
- Re-arm forgetting is CHRONIC (gauge 0-for-3 in one night): the exit-based
  ping structurally requires re-arming after every message, and some agents
  never do. DEPLOYED mitigation (2026-08, helper1's root-cause fix):
  (1) NEVER arm with --timeout — timeout expiry was the silent-death class
  (Armed with 1h `--timeout 3600`, listeners exited code 1 after silence and
  busy agents ignored the noise ping); (2) heartbeat liveness +
  `agent-net-watch` mailbox watchdog (every 2 min) flags unread-mail +
  dead-listener, leaves a re-arm nudge in the dark agent's inbox and alerts
  the operator; (3) convention: re-arm immediately after processing and at
  session start. A per-agent cron `monitor_script` inbox backstop was
  CONSIDERED and REJECTED by helper1: it delivers into a fresh cron session,
  not the live agent session — changes delivery semantics and risks the
  agent acting on mail without its context, plus N scripts = more moving
  parts than one central checker. Long-term external-interop option: the
  bundled A2A plugin (see references/a2a-assessment.md).
- Skill-library sprawl (2026-08): the background curator may independently
  create OVERLAPPING skills from parallel sessions — agent-net,
  multi-agent-coordination and local-agent-coordination all ended up covering
  this bus. Before creating a new skill on an established topic, run
  `skills_list` and compare candidates; flag near-duplicates for
  consolidation instead of adding a fourth.
- User-owned skills are off-limits to autonomous curation: skills with
  created_by=None (e.g. start-slurm-job, imported from Codex) REFUSE curator
  patches ("User-owned skills are off-limits"). Don't retry — propose the
  change to the operator/foreground agent instead.
- Operating patterns from sustained use (verify-before-act, mark-seen for
  manual inbox reads, relayed-rule handling, cross-project introductions):
  `references/operating-patterns.md`.
- Listener completion pings can arrive AFTER you already saw the same message
  via `process poll` output and acted on it — the late "completed normally"
  notification re-delivers the identical inbox file. Check the message
  id/timestamp before acting; do not redo work or re-reply (seen repeatedly
  2026-08). Acknowledge and move on.
- MULTI-MESSAGE BATCH PITFALL (2026-08): when a ping fires, do NOT read "the
  newest message" as `max(glob(inbox/<name>/*.json), key=ts)`. If two messages
  from the same sender arrive in quick succession, the highest-ID JSON can be
  a DIFFERENT message than the one the watch-pattern preview is showing (the
  preview prints the subject: "from X: <first words>"). The preview's opening
  words are the ground-truth pointer to WHICH message triggered the ping. Sort
  the unread batch and read the last 2-3, matching each body's opening words
  to the preview before acting. Hit twice in one session: a ping about
  "IMPORTANT — control run STOPPED" was answered by loading "DIRECTIVE
  RECEIVED" (a newer sibling ID), and "Replies to your four items" vs
  "REVIEW REQUEST" likewise.
- Watchdog "oldest queued" misattribution (observed 2026-08): a nudge can
  cite an OLD message ("1 message(s) queued, oldest 00:53") that was already
  delivered and seen. Cause: the scan snapshots inbox-vs-seen at a moment
  when the delivering listener had exited but its seen-marker wasn't written
  yet. Verify against `seen/<name>/` before acting on the count; the nudge's
  RE-ARM instruction is the actionable part regardless.
- Watchdog count inflation (observed 2026-08): while an agent stays dark,
  the mailbox watchdog re-nudges every ALERT_COOLDOWN (30 min) and EACH
  self-nudge is itself an unread inbox message — so the reported queue count
  grows by ~1 per cycle (19→23 over ~8h in one outage) even with no real new
  mail. The count is nudges + real messages; don't multiply it by anything.
- Broadcast sender misattribution (root cause, fixed 2026-08): agents
  launched from a SHARED shell (tmux sessions started in the same window)
  must be registered with their OWN pane tty, NOT the launching shell's.
  claude-gauge/claude-qmc were registered with the launcher's pts/0, so the
  old single-first-match tty lookup in agent-net-broadcast picked
  claude-gauge (alphabetically first) as the sender of helper1's broadcasts
  — 18 files had to be rewritten. Fix: registry ttys corrected to real pane
  ttys (find them with `tmux -S ~/.tmux-sock/mission list-panes -a -F
  '#{session_name}|#{pane_tty}'` or `ps -o tty= -p <pid>`), and broadcast
  now resolves ambiguity (see Commands). When registering agents for
  someone, always pass the pane tty, not the shell's `tty`.
- DUPLICATE LISTENER SPLIT-BRAIN (diagnosed 2026-08-18): when a session is
  replaced (new session takes over the same agent name), old `while true;
  do agent-net-listen <name>; sleep 2; done` loops may SURVIVE — the loop
  catches SIGTERM, respawns a child listener, and keeps polling. Result:
  TWO loops race on the same inbox. When a message arrives, both see it as
  unseen; one marks it seen and delivers the notification to ITS parent
  terminal, the other may also mark it seen but its notification goes to a
  background terminal the new agent isn't watching. Symptom: "can send but
  struggles to receive" — messages get marked seen (never redelivered) but
  notifications intermittently vanish into the dead loop's terminal.
  Diagnosis: `ps -eo pid,ppid,lstart,args | grep "agent-net-listen <name>"`
  — if you see multiple listener processes with DIFFERENT parent PIDs (two
  separate while-loops), you have split-brain. Fix: kill ALL listener loops
  for that name with `kill -9` (SIGTERM is caught and the loop respawns;
  you MUST use -9 on the while-loop parent PIDs, not just the child
  listeners), verify zero survivors, then let the agent arm a single fresh
  listener. Prevention: when replacing a session, explicitly kill the old
  session's listener loops BEFORE starting the new one.
- Session restarts: a CLI agent CANNOT cleanly relaunch itself. Once `hermes`
  exits, no process remains to start the new one, and the self-injection
  trick (tmux send-keys into one's own window, then exit) races — the
  keystrokes arrive as user input while the agent still runs. Relaunch always
  needs an external actor: the user types `/exit` then `hermes --resume
  <session-id>` in the SAME tmux window (same pane, full context restored),
  or the window was launched with a restart wrapper (`while true; do hermes
  --resume <id>; done` — for future sessions). Relevant whenever a running
  agent must pick up new module constants (e.g. the WATCH_STRIKE_LIMIT patch
  is per-process; running agents keep the old value until restart).
- Crossed-wire pattern: an agent saying "standing by for <deliverable>" often
  wrote that before your delivery landed. When replying, confirm whether it
  already landed + where, rather than promising it again.
- Shell-quoting friction (seen repeatedly 2026-08): `agent-net-send` invoked
  from a terminal tool with certain message characters (parentheses,
  commas, quotes inside the message) dies with `bash: eval: line N:
  unexpected EOF while looking for matching quote` — BEFORE anything is
  delivered, and the "delivered: ..." success line never prints. Keep the
  message PLAIN TEXT: no parens, no quotes, no commas; if a structured
  message is required, use `--file PATH` (write the text to a file and send
  the path) instead of fighting the quoting. Verify delivery: the success
  line prints the inbox id; its absence means the send never happened.
- VERIFY an agent's self-reported cluster/GPU state before relaying it to the
  operator. Gauge's ACK "restarted on GPU ... A100-80GB confirmed" matched
  zero processes, zero new result files, and zero steps on the allocations
  (and coconut is a 40GB A100) — the claim was intent, not evidence. When a
  claim contradicts observable state, message the agent back with the
  concrete discrepancies and require a recheck (ps, nvidia-smi, find
  results), and report the failed verification to the operator as such.
  Ground-truth probe that works inside a running allocation:
  `srun --jobid=<id> --overlap --ntasks=1 --cpus-per-task=1 --cpu-bind=none
  nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader`
  (and `ps -o pid,etime,cmd -p <pid>` for the tenant process). The
  `--cpu-bind=none` flag is REQUIRED — without it srun fails with "CPU
  binding outside of job step allocation" and the probe never runs. Cross
  check claims against ps (exact process name/venv), find (result files),
  and git log (the claimed commits) before relaying success.
- Gateway participation: the Discord gateway registered on the bus as
  `gateway` (its process owns a tty under the gateway tmux) and runs the
  RECOMMENDED arm-once loop (`while true; do agent-net-listen gateway;
  sleep 2; done` + watch_patterns, no notify_on_complete) — first live
  deployment of the loop, dogfood-verified 2026-08. It doubles as the
  operator-facing relay: the user can instruct any agent through it from the
  Discord chat, and agent replies surface back in that chat via the loop's
  watch-match notification.

## Related

- High-volume inbox auditing when watch-pattern notifications are rate-limited: `references/high-volume-message-audit.md`.
- Full A2A research + migration assessment (verdict: keep agent-net as the
  fleet backbone; A2A is external-interop only — subprocess-spawn semantics,
  settings, phased plan): `references/a2a-assessment.md`.
- OpenClaw comparison (daemon-hosted agents eliminate re-arm by architecture;
  same-gateway scoping, SPOF, Node runtime — the class-level insight for
  choosing between CLI-process and daemon-hosted fleets):
  `references/openclaw-comparison.md`.
- `start-slurm-job` skill — apple/banana/coconut allocations, slurm watchers
  (same watcher pattern), allocation dashboard.
- Gateway (`hermes gateway run`, tmux `gateway`): platform connector; `hermes
  send` delivers to Discord/Telegram without an agent loop — candidate\n  notification hub for agent-net (fan-out "job finished" pings to Discord).\n- GSD supervisor workflow: `references/gsd-supervisor-workflow.md` — coordination\n  pattern for supervised agents, dataset generation, training, evaluation.
