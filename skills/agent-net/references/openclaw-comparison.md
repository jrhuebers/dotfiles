# OpenClaw — fleet-migration comparison (2026-08)

Research done at the operator's request ("more openclaw research") when the
agent-net re-arm problem was under discussion. Question: does any alternative
framework have an agent-communication system free of the re-arm / watcher /
tty-injection issues?

## Verdict

OpenClaw eliminates the re-arm problem **by architecture**: agents are
sessions inside ONE always-on Gateway daemon, so there is nothing to arm and
nothing to forget. But that is the same architectural tradeoff as Hermes's
gateway-hosted mode (this Discord session receives messages with zero arming)
— the re-arm tax exists only because the fleet runs interactive CLI processes
in tmux. Migration cost + same-gateway scoping make it a "revisit for real
external multi-host peers" option, not a current fix.

## Grounded facts (docs.openclaw.ai/llms-full.txt, 2026-08)

- **One Gateway daemon hosts all agents.** An "agent" is a per-persona scope:
  workspace, `agentDir`, SQLite session store (`~/.openclaw/agents/<id>/…`).
  NOT independent processes. Agent CLI one-shots (`openclaw agent --agent ops
  --message …`) still route through the Gateway.
- **sessions_send** — "Run another session on the same Gateway and optionally
  wait." Peer messaging with A2A follow-up path: inject message → wait for
  target reply → bounded follow-up turns → announce result to the visible
  channel. Push-based into a live (daemon-hosted) session — no watcher, no
  re-arm.
- **sessions_spawn / sub-agents** — isolated background sessions
  (`agent:<id>:subagent:<uuid>`) that announce results back to the requester;
  tracked as background tasks; sub-agents don't get session/message tools by
  default; configurable nesting depth.
- **Multi-agent routing via bindings** — a binding maps a channel account
  (WhatsApp number, Slack workspace) to an agent; parallel specialist lanes
  add ownership policy (purpose, non-goals, chat budget, handoff rules).
  Per-session locks serialize runs; command queue caps global parallelism.
- **Steering queue** (concepts/queue-steering) — real answer to "steer queue":
  prompts arriving mid-run are steered into the active runtime at tool-launch
  boundaries (queue modes steer/followup/collect; steer is default). Codex
  harness exposes turn/steer instead.
- **Presence** = Gateway client roster (mac app/WebChat/nodes), not agent
  discovery. Delegate architecture = org identity (on-behalf-of), separate
  concern.
- Cross-session recall: sessions_list / sessions_search / sessions_history
  (bounded redacted view — strips thinking blocks, tool payloads).

## Caveats (why the fleet stays on Hermes CLI agents)

- **Same-Gateway scoping**: sessions_send runs on *the same Gateway*.
  Multi-node agent comms = multi-gateway setup → ports/tunnels, painful
  inside Slurm (same problem helper1 flagged for Hermes A2A).
- **Single point of failure**: one daemon hosts all agents — the fleet lives
  and dies together.
- **Node/TypeScript runtime**; younger, fast-evolving multi-agent surface
  (open issues exist, e.g. agentToAgent vs sessions_spawn conflicts).
- For the cluster use case (per-repo workspaces, srun --overlap joins,
  long-running jobs) the independent-process model the Hermes fleet uses is
  the deliberate choice; its cost is the re-arm convention.

## Generalizable insight (the class-level lesson)

Interactive-CLI agent fleets inherit the "can't push into a process that
isn't listening" problem; daemon/gateway-hosted agents (OpenClaw, Hermes
gateway mode) receive push messages with zero arming. Choose per fleet: if
inter-agent reliability dominates, daemon-host; if isolation-per-repo and
cluster ergonomics dominate, CLI processes + an armed-listener convention
(agent-net) + watchdog safety net.
