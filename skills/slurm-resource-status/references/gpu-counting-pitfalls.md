# GPU counting pitfalls — debugging sequence from Aug 2026 (Lamarr)

Goal: answer "how many GPUs are free?" Three attempts, three wrong numbers,
before the reliable method emerged. The exact commands:

## Attempt 1 — sinfo looks right but isn't

    sinfo -N -o "%n %G %e %t"

`%e` = FREE MEMORY (e.g. 586715 MiB), NOT free GPUs. `%G` is the configured
gres (e.g. `gpu:nvidia_a100-sxm4-40gb:8(S:1,3,5,7)`), not the free count.
There is no sinfo -N field for free GRES count on this cluster.

## Attempt 2 — scontrol show nodes (CORRECT base)

Per-node ground truth:

    scontrol show nodes | awk '/^NodeName=/{split($1,a,"="); node=a[2]} /AllocTRES=/{n=$0; sub(/.*gres\/gpu=/, "", n); sub(/,.*/, "", n); print node, "alloc_gpus=" n}'

Summed to 100 across 13 nodes (each 8 GPUs) → 4 free. This is the number that
turned out to be correct.

## Attempt 3 — scontrol show jobs (the trap field)

Summing gres/gpu per job gave WRONG totals twice:

    /TRES=/  match, all jobs      -> 215   (ReqTRES of PENDING jobs included)
    /TRES=/  match, RUNNING only  -> 200   (TRES_PER_NODE lines double-count)

Why: `scontrol show job` prints THREE lines that match a bare `/TRES=/`:
`ReqTRES=` (requested — pending jobs request GPUs they do not hold),
`AllocTRES=` (what the job actually holds — correct), and `TRES_PER_NODE=`
(a duplicate of AllocTRES for 1-node jobs). 200 = 100 × 2 from
AllocTRES+TRES_PER_NODE. The working filter:

    scontrol show jobs | awk '/JobId=/{jid=$1; st=""} /JobState=/{st=$0} /AllocTRES=/{if (st ~ /RUNNING/ && match($0, /gres\/gpu=[0-9]+/)) {v=substr($0, RSTART+9, RLENGTH-9)+0; s+=v; cnt++}} END {print "RUNNING jobs with gpu:", cnt, "| gpus held:", s}'

→ 92 jobs, 100 GPUs. Matches the per-node method.

## Micro-pitfalls

- awk off-by-one: `gres/gpu=` is 9 characters (`g`,`r`,`e`,`s`,`/`,`g`,`p`,`u`,`=`),
  so `substr($0, RSTART+9, RLENGTH-9)`. Using +10 silently returns empty
  (sum printed 0 — the first bug seen).
- An empty result from a tighter awk pattern (e.g. `/^   TRES=/`) means the
  line's leading whitespace differs — check the real format with
  `scontrol show job <id> | grep -E "JobState|TRES"` before filtering.
- CPU-partition jobs on GPU nodes (e.g. a CPU job on ml2ran02) hold no gres —
  never count them.
- Whole-node GPU allocations are common: a node at 8/8 with only a couple of
  visible GPU jobs is normal, not a contradiction.
- Held jobs ("user env retrieval failed requeued held") and PENDING jobs
  inflate request sums; only RUNNING AllocTRES counts.

## Verification habit

Per-node AllocTRES sum == per-job AllocTRES sum (both 100) before quoting.
If they disagree, a wrong line got matched.
