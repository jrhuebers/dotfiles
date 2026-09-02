#!/usr/bin/env bash
# Per-node and cluster-wide free GPU count on a Slurm cluster.
# Usage: bash scripts/gpu_free.sh   (from the skill dir, or copy to ~/bin)
#
# Why not sinfo: `sinfo -N -o "%n %G %e"` — %e is free MEMORY, not free GPUs.
# Reliable source: `scontrol show nodes` — configured Gres= vs AllocTRES=.
# Only AllocTRES counts real allocations (ReqTRES includes PENDING requests,
# TRES_PER_NODE double-counts). See references/gpu-counting-pitfalls.md.
set -u

scontrol show nodes | awk '
/^NodeName=/{split($1,a,"="); node=a[2]}
/^   Gres=/{
  # configured gres, e.g. gpu:nvidia_a100-sxm4-40gb:8(S:1,3,5,7)
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
