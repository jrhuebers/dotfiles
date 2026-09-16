# A2A plugin — research & migration assessment (2026-08)

Archived from the gateway session: the operator asked whether the fleet should
migrate from agent-net to Hermes's bundled A2A plugin. helper1 (with gateway
corroboration from the source) concluded: **keep agent-net as the fleet
backbone; A2A is an external-interop complement at most, never a replacement.**

## What A2A is (verified against the installed source)

- Bundled in Hermes v0.20.0 at `plugins/platforms/a2a/` (protocol.py, adapter.py,
  security.py, tools.py). Zero core edits, stdlib only, no extra dependencies.
- A2A = open Agent2Agent protocol v1.0 (Linux Foundation). Docs:
  hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a
- Two directions: inbound adapter (exposes Hermes as an A2A agent over HTTP) +
  outbound tools in the `a2a` toolset: `a2a_discover`, `a2a_call`, `a2a_list`,
  `a2a_history`, `a2a_orchestrate`. Toolset is OFF by default
  (`_DEFAULT_OFF_TOOLSETS`).
- **Task-based protocol**: a task is a tracked unit of delegated work with a
  lifecycle (SUBMITTED → WORKING → INPUT_REQUIRED → COMPLETED/FAILED/CANCELED),
  artifacts (results), a durable task store (tasks/get, tasks/list), and SSE
  streaming (statusUpdate/artifactUpdate). Simple use = one message/one reply;
  the machinery only surfaces for multi-turn clarification, cancellation, and
  long-running work.
- Settings are env vars: A2A_PORT (9900), A2A_HOST, A2A_PUBLIC_URL,
  A2A_AGENT_NAME, A2A_AGENT_DESCRIPTION, A2A_ADVERTISED_TOOLSETS,
  A2A_BEARER_TOKEN, A2A_PEER_TOKENS (name:token per peer), A2A_TRUSTED_PEERS,
  A2A_ALLOWED_USERS, A2A_ALLOW_ALL_USERS, A2A_PUSH_SECRET, A2A_RATE_LIMIT
  (60/min sliding window per identity), A2A_MAX_PINGPONG_TURNS (default 5,
  hard max 20), A2A_REPLY_TIMEOUT (default 300s), plus provider routing vars.
- No queue-depth knob: one outstanding task per conversation context, HTTP
  worker threads for concurrent contexts.

## The killer limitation for a CLI fleet

Inbound A2A is hosted by the GATEWAY process only. Tasks routed to named agents
are NOT injected into their live sessions — the adapter (adapter.py:867) spawns
a headless `hermes chat -q <text> --resume <session-id>` subprocess per task
with a hard reply timeout (300s default; TimeoutExpired fails the task).
Consequences: no inbox hook, no unread-mail injection, no listener-armed
wake-up, fresh process boot + context reload per task, and long review turns
die on the timeout. Live-session injection applies only to the gateway's own
session. agent-net's watcher-exit ping is the opposite: it delivers INTO the
live conversation.

Also: claude-gauge/claude-qmc are Claude Code processes with file hooks — they
cannot speak A2A at all without a translation bridge.

## helper1's phased rollout (complement, never swap)

- Phase 0: agent-net backbone unchanged.
- Phase 1: enable a2a toolset for CLI (outbound calls to external peers).
- Phase 2: enable a2a platform in the existing gateway, localhost-only first,
  per-peer tokens if real remote peers appear.
- Phase 3: optional agent-net ↔ A2A bridge so external peers reach the fleet
  through one entry point.

## Gotchas worth remembering

- Raise A2A_MAX_PINGPONG_TURNS before supervised multi-turn dialogs (cap 5).
- Raise A2A_REPLY_TIMEOUT (300s default < the supervisor poller's 600s).
- Inbound binds 127.0.0.1 unless tokens + A2A_HOST are set; remote peers need
  a tunnel (Slurm ports are painful).
- Bearer-token auth bypasses the gateway user allowlist by design.
- Agent card advertises toolsets from the live registry — restrict
  A2A_ADVERTISED_TOOLSETS before exposing to external peers.
- Enabling requires gateway restart (brief Discord downtime; sessions persist).

## When to revisit

Only when a real EXTERNAL A2A peer appears (another Hermes on a different host,
CrewAI, Google ADK, OpenClaw, ...). Internal fleet messaging stays on agent-net.
