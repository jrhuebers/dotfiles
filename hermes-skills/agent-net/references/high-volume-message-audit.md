# High-volume message audit

Use when an agent-net watch notification says matches were suppressed, shows only a preview, or several messages may have arrived between reviews.

1. Treat inbox JSON files as the authoritative record, not watch notification text. Read the newest relevant `inbox/<agent>/*-<sender>.json` bodies in timestamp order.
2. Before acting on a claimed completion, independently inspect the cited artifact/process/log. Notifications and agent summaries are claims, not proof.
3. If a sender is awaiting a response, send one concrete acknowledgement through `agent-net-send --from <name> ...`; use `--file` for detailed messages to avoid shell quoting/truncation.
4. In the reply, distinguish what was verified from what remains blocked. Do not authorize subsequent stages based solely on a summary.

This preserves reliable coordination when watch-pattern delivery is rate-limited.