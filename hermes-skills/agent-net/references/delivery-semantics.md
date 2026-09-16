# Hermes ping channels — what can push INTO an agent's context

Inventory from the 2026-08 agent-net design session. Useful whenever a future
session needs to deliver an event/message to an agent and wonders what
mechanism exists.

## Into a LIVE session

1. **Background process completion** (`terminal(background=true,
   notify_on_complete=true)`) — a watcher process exits, its output re-enters
   the conversation as a tool notification. THE general-purpose event-driven
   channel (slurm start/end watchers, agent-net-listen). One-shot per process:
   each delivery consumes its watcher — re-arm required.
2. **watch_patterns** — mid-process signal on a never-exit process, for RARE
   one-shot readiness lines (e.g. vLLM "Application startup complete").
   NOT for message delivery: rate-limited to 1 notification/15s, and repeated
   firing auto-disables pattern watching, falling back to notify-on-exit —
   which never fires for a long-lived process → SILENT delivery loss.
3. **delegate_task** — a subagent's result re-enters the DELEGATING agent's
   conversation (child→parent).
4. **cronjob action='run'** — job outcome re-enters the CALLER's conversation
   (self/scheduled ping).
5. **Out-of-band user messages** — the user injects mid-turn; appended to a
   tool result with an explicit marker.
6. **Gateway platform messages** — Discord/Telegram/etc. events, but ONLY into
   gateway-hosted sessions. Plain CLI agents are not reachable this way.

## NOT into live sessions

- Recurring cron ticks, webhooks, monitor_script/monitor_url change-detection —
  they run in FRESH sessions and deliver to the gateway or the local store.

## Tools are pull-only

A tool executes only when the agent invokes it; its result lands in context as
the answer to that call. There is NO tool that asynchronously injects content
into a conversation on its own. Push requires one of the channels above.

## Cross-agent implications

- Pinging another agent requires IT to have armed a watcher; otherwise the
  message waits (durable by design — the inbox is the queue).
- Tty injection (writing to /dev/pts/N) works same-host and masquerades as
  typed user input — the user VETOED this (--push removed 2026-08). Never do
  it without explicit user request.
- Zero-re-arm delivery would need a Hermes-native inbox event source (a
  feature request upstream). The MCP hub is the standard-protocol middle path:
  `hermes mcp add <name> --command <cmd>` (connect a server; a stdio server is
  spawned per agent, no daemons) and `hermes mcp serve` (run Hermes as an MCP
  server, "expose conversations to other agents"). Receive stays pull-based
  (agent calls an inbox tool) but send/discovery become real tools.

## Timing when the target is BUSY (delivery vs action)

A delivered message (listener armed) is INJECTED into context immediately,
even mid-turn — but the agent acts on it at its next decision point:

- between tool calls → seconds (near-steering);
- blocked on ONE long tool call (e.g. a 400s terminal command) → when that
  call returns, before necessarily finishing the whole task;
- listener UNARMED (agent deep in a task, hasn't re-armed after its last
  ping) → the message waits in the inbox until the agent re-arms (its
  protocol does this at the end of the current turn). Lossless, deferred.

This is NOT out-of-band user steering (injected into the running turn,
processed immediately). Rule of thumb: armed + between calls = seconds;
armed + long call in flight = when it returns; unarmed = end of current turn.
