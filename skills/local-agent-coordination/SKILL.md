---
name: local-agent-coordination
description: "Use when finding or messaging local Hermes agent processes."
version: 1.0.0
author: hermes-curator
platforms: [linux]
---

# Local Agent Coordination

The user runs several independent `hermes` CLI agents in separate terminals (pts) on the same host — e.g. inside the mission-control slurm allocation on ml2ran02: a FIM agent, a qmc/diffusion-qmc agent, a gauge-GNN agent, plus gateway + dashboard in tmux on the mission socket. A session may need to find them, see what they're doing, or message them. There is NO first-class cross-agent tool: `delegate_task` only spawns this session's own subagents, and `hermes send` targets messaging platforms (Discord/Telegram), not local agents. Use the OS-level channels below.

## Discover which agent is which
- `ps aux | grep -E "hermes"` → pid + pts per process; `--resume <id>` shows the resumed session.
- Identify by working directory: `readlink /proc/<pid>/cwd` (e.g. ~/diffusion-qmc = qmc agent, ~/FIM, ~/gauge-graph-network).
- Find YOUR OWN process: walk the ppid chain up from `$$` (`ps -o pid=,ppid=,cmd= -p $p` in a loop).
- `hermes sessions list` → titles/workspace/last-active. Prefixes: bg_* = background sessions, cron_* = cron runs.

## Read what an agent is doing
- Transcript from the SQLite store:
  `sqlite3 ~/.hermes/state.db "SELECT datetime(timestamp,'unixepoch','localtime'), role, substr(replace(content,char(10),' '),1,160) FROM messages WHERE session_id='<id>' ORDER BY timestamp DESC LIMIT 12;"`
  Assistant content can be empty on reasoning-only turns; tool rows carry tool_name.
- Live state: its cwd, child processes, and log files (e.g. diffusion-qmc/slurm-logs/*.log mtime growing = actively training/monitoring).

## Message an agent (give it orders)

Use the agent-net bus (below) — tty injection (`printf ... > /dev/pts/N`) is
EXPLICITLY REJECTED by the user (2026-08-12, the former `--push` flag was
removed): it looks like typed user input, interleaves with real typing, and
is non-durable. The inbox bus is the only sanctioned channel.

## agent-net bus (preferred for async messaging)

There is an agent-to-agent message bus on the host (tools in ~/.local/bin/agent-net-*):

- `agent-net-list` — registry: NAME HOST TTY SESSION WS DESCRIPTION (this session's name is in the WS/description; e.g. gauge = gauge-graph-network agent, fim = FIM agent, qmc = diffusion-qmc agent, helper1/helper2 = user-named helpers).
- `agent-net-register <name> [description]` — join the bus (run once per agent).
- `agent-net-send <to> <message>` — deliver to another agent's inbox (prints a receipt id; ~0s, non-blocking).
- `agent-net-listen <name>` — BLOCKING: waits for the next message for <name>, prints it (plus the full JSON path under ~/.hermes/agent-net/inbox/<name>/), then exits.

Listener pattern (how to be reachable inside an agent session):
1. Arm: run `agent-net-listen <name>` with terminal background=true + notify_on_complete=true.
2. When the notification fires, the process output IS the message(s); act on them.
3. Reply with agent-net-send, then RE-ARM the listener the same way.
The listener exits after delivering, so re-arming after every ping keeps the inbox watched.

Notes: `agent-net-listen --help` does NOT work (it ignores args and blocks — use a short timeout if probing). Messages accumulate in the inbox while unarmed; the next listen delivers everything pending. Never send secrets over the bus.

agent-net-send quoting pitfall: the message is passed through the shell
`eval` — parentheses, unbalanced quotes, backticks, or `$` in the message
text abort with `unexpected EOF while looking for matching quote` (hit
twice in one session). Keep messages plain text: no parentheses where
possible, no inner quotes; if the message must carry punctuation, write it
to a file and pass `"$(cat msgfile)"` instead of typing it inline.

## tmux-hosted infrastructure

tmux sessions on the mission socket (`~/.tmux-sock/mission`: gateway,
hermes-dash, mission-sshd) are infrastructure surfaces: attach/capture to
inspect, but they are NOT a channel for agent-to-agent communication —
operator rule: agent-to-agent communication goes through agent-net ONLY
(no tmux send-keys into an agent's window). Same-host note: a tmux Unix
socket cannot be reached across hosts even when the socket file lives on
shared /cephfs; the agent session runs on ml2ran02, so tmux on gwkilab
(login node) is out of reach (ssh from compute node to gwkilab times out).
