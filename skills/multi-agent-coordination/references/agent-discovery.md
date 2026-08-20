# agent-net protocol & agent discovery recipes

Session-specific detail for the multi-agent-coordination skill.
Verified 2026-08-12 on Lamarr (gwkilab / ml2ran0x).

## agent-net message format

Message file: `~/.hermes/agent-net/inbox/<to>/<ts-nanos>-<from>.json`
(copy written to `outbox/`):

```json
{"id": "1786566354578759373-helper1", "from": "helper1", "to": "helper2",
 "ts": 1786566354578759373, "body": "..."}
```

- ts is epoch NANOSECONDS (`date +%s%N`).
- Delivery: listener touches `seen/<name>/<msgid>` then prints
  "📨 agent-net message <time> from <from>: <body>" + file path, exits 0.
  Message file is NOT deleted on delivery (seen marker prevents redelivery).
- Sender resolution order: `--from` > `$AGENT_NAME` > reverse lookup of the
  owning hermes process's tty in registry/.json.

## Registry entry (`registry/<name>.json`)

```json
{"name": "qmc", "host": "ml2ran02", "tty": "pts/4",
 "workspace": "/cephfs/users/huebers/diffusion-qmc",
 "session_id": "20260811_233834_8c4907",
 "description": "...", "registered_at": <s>, "heartbeat_at": <s>}
```

## Identifying running agents (process -> tty -> session)

1. `ps aux | grep hermes-agent/hermes` — one process per agent, each on a
   distinct pts; `ps -o pid,tty,etime,cmd -p <pid>` for details.
2. `/proc/<pid>/cwd` → workspace → which project the agent owns
   (diffusion-qmc → qmc, FIM → fim, gauge-graph-network → gauge).
3. Session id: if the process was started with `--resume <id>` / `-r <id>`,
   it's in the cmdline. Otherwise match by start time in the DB.
4. `agent-net-list` shows the resolved roster (name/host/tty/session/ws).

## state.db queries (SQLite, ~/.hermes/state.db)

`PRAGMA table_info(sessions)` columns include: id, source, session_key,
display_name, model, parent_session_id, started_at, ended_at, end_reason,
message_count, tool_call_count, cwd, git_repo_root, title, title_source,
last_activity_at, last_activity_description, archived, pinned, ...

`messages` columns: id, session_id, role, content, tool_call_id, tool_calls,
tool_name, effect_disposition, timestamp (REAL, epoch seconds), token_count,
finish_reason.

Useful queries:

```sql
-- agent roster with last activity
SELECT id, datetime(started_at,'unixepoch','localtime') AS started,
       datetime(last_activity_at,'unixepoch','localtime') AS last,
       substr(COALESCE(title,'(untitled)'),1,40) AS title, cwd
FROM sessions ORDER BY last_activity_at DESC LIMIT 10;

-- last N messages of a session (role + trimmed content)
SELECT datetime(timestamp,'unixepoch','localtime') AS t, role,
  CASE WHEN role='tool' THEN 'tool:'||COALESCE(tool_name,'')
       ELSE substr(replace(COALESCE(content,''), char(10),' '),1,160) END
FROM messages WHERE session_id='<id>' ORDER BY timestamp DESC LIMIT 12;
```

Notes:
- Assistant rows often have EMPTY content (reasoning-only turns) — read
  neighboring tool rows for actual activity.
- `hermes sessions list` / `hermes sessions export --session-id <id>` are the
  CLI equivalents.

## Tool-shell identity resolution (no tty)

Terminal tool shells run over pipes (`tty` → "not a tty"); `HERMES_SESSION_*`
env vars are unset in them. To find your own hermes process:

```bash
p=$$
for _ in $(seq 1 10); do
  cmd=$(ps -o cmd= -p "$p" 2>/dev/null)
  case "$cmd" in *hermes-agent/hermes*) break;; esac
  p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
  [ -z "$p" ] && break
done
ps -o tty= -p "$p"   # -> pts/12
```

## Roster snapshot (2026-08-12)

| name | pts | session | workspace | status |
|------|-----|---------|-----------|--------|
| helper1 | pts/0 | 20260812_111637_5b9dea | /cephfs/users/huebers | live, listener armed |
| helper2 | pts/12 | 20260812_185717_71bf9d | /cephfs/users/huebers | live, listener armed |
| fim | pts/1 | 20260812_110554_b93e1c | FIM | live, listener armed |
| gauge | pts/8 | 20260812_103357_f882bf | gauge-graph-network | registered, hello queued |
| qmc | pts/4 | 20260811_233834_8c4907 | diffusion-qmc | registered, hello queued (do not disturb while training) |

Live truth: `agent-net-list`.

## Environment facts that shaped the design

- All agent processes run on ml2ran02 (inside mission-control allocation,
  job 53157) — same host, so tty-based liveness works; cephfs is shared so
  inboxes work cross-host anyway.
- Hermes gateway runs in tmux session "gateway" on socket
  `~/.tmux-sock/mission` (`hermes gateway run`), connected to Discord.
- `hermes send` pipes text to messaging platforms only — NOT to local agents.
- Cross-agent pinging channels: (1) watcher-exit notification (the canonical
  one), (2) tty write (REJECTED by user, removed as --push). delegate_task /
  cronjob run / gateway messages do NOT reach other local CLI agents.
