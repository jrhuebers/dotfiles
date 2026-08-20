# Claude Code hooks on the agent-net bus (observed 2026-08)

Fleet: `claude-gauge` and `claude-qmc` — Claude Code CLIs running in tmux
sessions (`claude-gauge`, `claude-qmc` on ~/.tmux-sock/mission), registered
on agent-net, each wired with hooks that post `claude-<name> digest: <text>`
messages to the bus.

## Observed message shapes

- Debug/test: `Test digest from hook debug` — hook bring-up verification.
- Assessment (valuable): `Assessment complete — the multi-cycle gate does not
  pass yet, recovery is well-diagnosed.` — the agent's verdict on a milestone.
- Closing-statement capture: `I'll send the requested reply to helper1.` —
  the turn's final plan/statement; useful as a status digest.
- Lifecycle noise: `[claude-gauge turn completed]` / `[claude-qmc turn
  completed]` — fires after EVERY finished turn.

## Pitfall: per-turn lifecycle pings flood the operator inbox

- 4+ `[... turn completed]` pings arrived within ~5 minutes across the two
  agents, each hitting the operator (helper2).
- Every ping consumes the recipient's `agent-net-listen` watcher -> re-arm
  churn on top of context noise.
- Lifecycle pings are for hook debugging, not production. The useful digest
  is the turn's closing statement / assessment / result.

## Tuning guidance (hook config lives with the user)

- Fire the digest on substance only: turn end AND (file change | assessment
  produced | command result | gate outcome), or a rolling summary (digest
  every N turns / on task completion).
- Alternatively route lifecycle pings to the project's own agent (e.g. the
  Hermes agent working the same repo) instead of the operator inbox.
- The operator's inbox should only see material events.

## Two runtimes, one project

- claude-gauge (Claude Code) and gauge (Hermes) both work
  gauge-graph-network; claude-qmc and qmc both work diffusion-qmc.
- Make scope division between the Claude instance and the Hermes agent
  explicit, or the parallel-editors-collision rule applies.
