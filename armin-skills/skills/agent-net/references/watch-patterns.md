# watch_patterns for mailbox delivery (arm-once loop)

Mechanism verified end-to-end 2026-08-14 (dogfooded on the gateway agent):
message written to inbox → loop's `agent-net-listen` catches it, prints, exits
→ loop re-arms (sleep 2) → watch_patterns matches "agent-net message" → the
live session gets a watch_match notification with the matched output. Same
delivery semantics as the exit-ping, minus the re-arm dependency.

## The arm-once loop (recommended listener pattern)

```bash
while true; do agent-net-listen <name>; sleep 2; done
```

- Start as ONE background process with `watch_patterns=["agent-net message"]`
  and NO `notify_on_complete` (the process never exits).
- Auto-re-arms forever; nothing to forget; the 2s sleep prevents a hot spin.
- Pattern should match "agent-net message" (skip the emoji — encoding safety).

## Stock constants (tools/process_registry.py in the hermes-agent install)

- `WATCH_MIN_INTERVAL_SECONDS = 15` — max 1 watch notification per 15s per
  process session.
- `WATCH_STRIKE_LIMIT = 3` — operator-raised to **50** (2026-08-14). Semantics:
  matches arriving inside the 15s cooldown are dropped and count ONE strike
  per window; after the limit of CONSECUTIVE strike windows, watch_patterns is
  disabled for that session and it is promoted to notify_on_complete semantics
  — which never fires for a long-lived process = silent loss.
- Global breaker (all sessions): `WATCH_GLOBAL_MAX_PER_WINDOW = 15` per 10s
  window, `WATCH_GLOBAL_COOLDOWN_SECONDS = 30`.
- KEY: a batch delivery lands in ONE output chunk = 1 emit + 1 strike, so
  backlog drains (even 13 messages) don't trip even the STOCK limit of 3.
  Only sustained multi-chunk traffic (messages arriving in separate chunks
  across ≥3 consecutive 15s windows, e.g. a trickle every few seconds for a
  minute+) accumulates enough strikes to disable. Raised limit is
  defense-in-depth for exactly that pattern.

## Patch notes

- Location: `tools/process_registry.py` (core file — RE-APPLY after every
  `hermes update`, which overwrites it; the source comment marks it).
- Backup first: `cp tools/process_registry.py{,.bak-<date>}`.
- Constants are module globals read per-process at import — running agents
  keep old values until their session restarts (`hermes --resume <id>`); new
  sessions get the new value. The loop works fine with the STOCK limit for
  normal mailbox traffic; restart only matters for burst-hardening.

## Verification

- `tests/tools/test_watch_patterns.py`: 18 tests pass with the patch (no test
  hardcodes the strike value; they assert mechanics: first-match-delivers,
  suppressed-count reporting).
- Dogfood proof: self-message → watch notification with full content landed in
  the live session; loop respawned a fresh listener immediately (auto-re-arm
  confirmed via `ps` + seen-marker).
