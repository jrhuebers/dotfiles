---
name: slurm-resource-status
description: "Use when checking free GPUs or queue state on Slurm."
version: 1.0.0
platforms: [linux]
---

# Slurm Resource Status

## When to Use

"How many GPUs are free?", "which nodes are idle?", "is the queue saturated?"
— any read-only Slurm cluster resource question. Complements
`start-slurm-job` (submission/monitoring); this skill covers the counting and
introspection side. Verified on Lamarr (A100-40/80GB + B300 nodes).

## Free GPU count — the reliable way

Do NOT trust `sinfo -N -o "%n %G %e %t"`: **%e is free MEMORY, not free GPUs**
(the GRES column shows configured capacity, e.g. `gpu:...:8`, never what's
free). The scheduler's ground truth is `scontrol show nodes` — compare the
configured `Gres=` count against `AllocTRES=` per node.

Run the packaged probe instead of hand-typing awk:

    bash scripts/gpu_free.sh

Output: per-node `used/free` by GPU type plus cluster total. Verified: 100/104
held on Lamarr matches the per-job count exactly.

## The counting traps (all hit in one session, Aug 2026)

1. Per-node: sum `AllocTRES` `gres/gpu=N` across nodes; free = capacity − sum
   (13 nodes × 8 = 104 → 4 free). This is authoritative.
2. NEVER sum `gres/gpu` across `scontrol show jobs` naively. A bare `/TRES=/`
   match hits THREE line kinds: `ReqTRES` (includes PENDING requests →
   overcount, observed 215), `AllocTRES` (correct), and `TRES_PER_NODE`
   (double-counts, observed 200 vs real 100). Only `AllocTRES=` lines with
   `JobState=RUNNING` count.
3. Cross-check the two methods (per-node AllocTRES sum == per-job AllocTRES
   sum). Disagreement means you matched the wrong TRES line.
4. awk substr off-by-one: `gres/gpu=` is 9 chars →
   `substr($0, RSTART+9, RLENGTH-9)`.
5. CPU-partition jobs running on GPU nodes consume 0 GPUs — never count them.
6. A node can read 8/8 allocated with few visible jobs (whole-node allocations
   by other users). Trust AllocTRES, not the running-job list.

## Queue context

`squeue -o "%.10P %.8u %.8T %.10M %.6D %R"` — count PENDING jobs and read
their reasons (Priority / Resources / held). A long pending line means the few
free GPUs will be grabbed quickly. Jobs stuck as "user env retrieval failed
requeued held" hold nothing but clog the queue.

## Checking what's running on an allocation (srun --overlap)

To inspect processes on a running job's node from outside the job, use
`srun --jobid=<id> --overlap`. The job doesn't need to be yours.

CRITICAL: `--overlap` steps do NOT inherit the job's CPU mask. Without
extra flags, srun fails with "CPU binding outside of job step allocation"
and "Unable to satisfy cpu bind request." The working incantation:

    srun --jobid=<id> --overlap --cpu-bind=none --gres=gpu:0 --mem=2G \
      bash -c "ps -u huebers -o pid,etime,rss,args --sort=-rss"

- `--cpu-bind=none` — disables CPU binding so the step can launch.
- `--gres=gpu:0` — requests no GPU (you're just inspecting).
- `--mem=2G` — required or the step may fail to allocate.
- NOTE: `--gres=gpu:0` means nvidia-smi shows "No devices were found"
  because no GPU is allocated to the inspection step. To see actual GPU
  utilization, run nvidia-smi from WITHIN the job's own session, or use
  `--gres=gpu:1` (may block if the job holds all GPU GRES slots).
- NOTE: `--exact` also fails with the same CPU binding error — don't
  bother trying it. `--cpu-bind=none` is the fix.

## Pitfalls

- The sinfo %e trap (free memory ≠ free GPUs).
- Pending-job requests inflate totals — always filter on JobState=RUNNING.
- Quote a number only after two independent methods agree.
- `srun --overlap` CPU binding error — use `--cpu-bind=none --gres=gpu:0
  --mem=2G` (see section above).

## References

- `references/gpu-counting-pitfalls.md` — the exact awk one-liners and the
  debugging sequence (215 → 200 → 100) that produced this skill.
- `scripts/gpu_free.sh` — the ready-to-run per-node probe.
