#!/usr/bin/env bash
# Per-node and cluster-wide free GPU count on a Slurm cluster.
# Usage: bash scripts/gpu_free.sh
#
# Why not sinfo: `sinfo -N -o "%n %G %e"` — %e is free MEMORY, not free GPUs.
# Reliable source: `scontrol show nodes` — configured Gres= vs AllocTRES=.
# Only AllocTRES counts real allocations (ReqTRES includes PENDING requests,
# TRES_PER_NODE double-counts).
set -u

scontrol show nodes | awk '
/^NodeName=/{split($1,a,"="); node=a[2]}
/^   Gres=/{
  if (match($0, /gpu:[^:]+:[0-9]+/)) {
    g = substr($0, RSTART, RLENGTH)
    split(g, b, ":")
    conf[node] = b[3] + 0
    gputype[node] = b[2]
  }
}
/^   AllocTRES=/{
  if (match($0, /gres\/gpu=[0-9]+/)) {
    alloc[node] = substr($0, RSTART+9, RLENGTH-9) + 0
  }
}
END {
  tot_conf = 0; tot_alloc = 0
  for (n in conf) {
    a = (n in alloc) ? alloc[n] : 0
    tot_conf += conf[n]; tot_alloc += a
    printf "%-10s %-24s %d/%d used  %d free\n", n, gputype[n], a, conf[n], conf[n]-a
  }
  printf "%-10s %-24s %d/%d used  %d free\n", "TOTAL", "(all types)", tot_alloc, tot_conf, tot_conf-tot_alloc
}'
