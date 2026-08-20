#!/usr/bin/env bash
# check_progress.sh — gather everything the agent needs to judge a job's ETA.
# Usage: check_progress.sh <jobid> [progress-regex]
# Prints: job state, elapsed vs walltime limit, log path/size, last 15 log lines,
# and the most recent progress-marker matches (default: "N/N" style fractions).
set -u
JOBID="${1:?usage: check_progress.sh <jobid> [progress-regex]}"
REGEX="${2:-[0-9]+ ?[/-] ?[0-9]+}"

INFO=$(scontrol show job "$JOBID" 2>/dev/null)
[ -n "$INFO" ] || { echo "job $JOBID not found"; exit 1; }

STATE=$(printf '%s\n' "$INFO" | sed -n 's/.*JobState=\([A-Za-z]*\).*/\1/p' | head -1)
RUNTIME=$(printf '%s\n' "$INFO" | sed -n 's/.*RunTime=\([^ ]*\).*/\1/p' | head -1)
LIMIT=$(printf '%s\n' "$INFO" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
LOG=$(printf '%s\n' "$INFO" | sed -n 's/.*StdOut=\([^ ]*\).*/\1/p' | head -1)

echo "=== job $JOBID: state=$STATE elapsed=$RUNTIME limit=$LIMIT"
echo "=== log: $LOG"
if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
    echo "(no log file yet)"
    exit 0
fi
SIZE=$(stat -c %s "$LOG" 2>/dev/null || echo "?")
LINES=$(wc -l < "$LOG" 2>/dev/null || echo "?")
echo "=== size=${SIZE}B lines=${LINES}"
echo "=== last 15 lines:"
tail -n 15 "$LOG"
echo "=== progress matches ('$REGEX'), last 6:"
grep -oE "$REGEX" "$LOG" 2>/dev/null | tail -n 6
M=$(grep -cE "$REGEX" "$LOG" 2>/dev/null); M=${M:-0}
echo "=== match count: $M"
