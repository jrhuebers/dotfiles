---
name: supervised-research-diagnostics
description: "Diagnose model issues under supervisor feedback."
version: 1.0.0
author: huebers
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mlops, diagnostics, provenance, supervised, agent-net]
    related_skills: [agent-net-messaging, training-run-analysis]
---

# Supervised Research Diagnostics

## When to Use

Use when conducting model diagnostics, stability tests, or collapse investigations under supervisor feedback via agent-net. Triggered when:
- Supervisor provides iterative audit feedback
- Root-cause claims are rejected due to methodology issues
- Provenance gaps are discovered (checkpoint not saved, etc.)

## Core Principle: Artifact-Rigorous Diagnostics

**The golden rule: Never substitute fresh instances for the actual trained/produced artifacts.**

| What you might do | What supervisor expects |
|-------------------|-------------------------|
| Instantiate fresh model for diagnosis | Load the ACTUAL trained checkpoint |
| Run toy approximation of sampler | Run the ACTUAL `sample_reverse_sde_vpsde` pipeline |
| Save summary statistics only | Save raw stage NPZ arrays for per-stage diagnostics |
| Assume checkpoint was saved | VERIFY checkpoint file exists (may not!) |

## Common Failure Patterns (from past audits)

### 1. Fresh Model Substitution (v49 audit rejection)
- **Error**: Instantiated fresh `DenoiserMLP()` for diagnostics
- **Why rejected**: Fresh model = random weights ≠ trained model behavior
- **Fix**: Load actual checkpoint with `torch.load()` if it exists

### 2. Toy Sampler Substitution (v49 audit rejection)
- **Error**: Ran `x += 0.1 * randn_like(x)` as stage analysis
- **Why rejected**: Not the actual VPSDE reverse sampler with drift/score
- **Fix**: Call `sample_reverse_sde_vpsde()` with instrumentation

### 3. Missing Checkpoint Provenance (v50 discovery)
- **Error**: Assumed checkpoint was saved by producer
- **Actual**: `run_vpd_stability_test` has no `torch.save()` calls
- **Fix**: Always verify checkpoint existence before claiming to load it

### 4. Summary-Only Diagnostics (v49 audit)
- **Error**: Only JSON summaries, no raw NPZ per stage
- **Why rejected**: Can't independently verify claims
- **Fix**: Save raw arrays per stage, compute hashes

## Supervisor Feedback Patterns

The supervisor (gsd-supervisor) provides specific feedback:

| Feedback | Meaning | Action |
|----------|---------|--------|
| "VERIFIER-ONLY" / "not a producer" | You're verifying artifacts, not running producer | Accept label, don't overclaim |
| "preserved unchanged" | Don't touch that path/family | Use new directory |
| "ROOT-CAUSE REJECTED" | Your diagnosis method is flawed | Check artifact substitution |
| "PROVENANCE GAP" | Something expected is missing | Explicitly document the gap |

## Provenance Verification Pattern (v44-v48)

A robust verification package includes:

1. **Input hashes**: Record hashes of all source files before run
2. **Data hashes**: Laplacian, adjacency, train/test sets
3. **Baseline hashes**: Hash forbidden paths BEFORE execution
4. **Output artifacts**: Raw NPZ arrays, not just summaries
5. **Atomic writes**: Use temp + rename for all outputs
6. **Strict validation**: `allow_nan=False`, fail on nonfinite
7. **Boundary check**: Compare baseline vs post-execution hashes
8. **Fail-closed**: Exit 1 on missing required files/keys

## Diagnostic Structure

For model collapse investigation:

```
diagnostic_1: Initial noise per seed/sample (raw hashes)
diagnostic_2: Model parameters (nonzero/finite/norm diagnostics)
diagnostic_3: Forward pass (multiple input configurations)
diagnostic_4: Reverse sampler stages (raw arrays per stage)
diagnostic_5: Control/identity test (known-answer baseline)
diagnostic_6: Comparison to actual artifacts (v41 samples)
```

## Key Pitfalls

- **Never claim to load a checkpoint without verifying it exists**
- **Never diagnose with a fresh model - the trained weights matter**
- **Never run a toy sampler when the real pipeline is available**
- **Summary-only diagnostics are insufficient - save raw arrays**
- **Preservation boundary: don't overwrite prior artifact families**

### CPU/GPU Paired Comparisons

See `references/cpu-gpu-paired-comparison.md` for the pattern used in v73-v75 to run identical-config CPU and GPU runs for device consistency verification.

### Unit Test vs Runner Integration (v59-v62 lessons)

A common rejection pattern: checking imports/strings is NOT integration.

| What you might do | What supervisor expects |
|-------------------|-------------------------|
| Check `DenoiserUGNN in joint_runner.py` | Import module, instantiate, train, evaluate |
| Direct `train_model_vpsde()` call | Call actual `run_metr_la_benchmark()` function |
| No seed | `seed_everything(42)` for reproducibility |
| Print to terminal | Capture stdout/stderr to files |
| Exit 0 always | Fail-closed: try/except with sys.exit(1) on error |

The supervisor distinguishes between:
1. **Unit smoke**: Testing model forward pass in isolation
2. **Runner integration**: Running through production benchmark function with full dispatch

Both are valid, but claiming runner integration requires actually calling the benchmark function (or a shared dispatch used by it).

### Reproducibility Pattern (v62 lesson)

Always set seed for deterministic results:

```python
import joint_runner as jr
jr.seed_everything(42)  # Must come before any model instantiation
```

Without this, independent reruns produce different values (e.g., aMMD 4.8012 vs 4.8044).

### Fail-Closed Wrapper Pattern (v61-v62 lesson)

Never just print "PASS" - actually fail on errors:

```python
print("\n3. Testing U-GNN...")
try:
    ugnn = jr.DenoiserUGNN(S=A, Ks=3, t_dim=64, C=16)
    ugnn = jr.train_model_vpsde(ugnn, train_loader, sde, L, device, epochs=1)
    result = jr.evaluate_model_vpd(ugnn, sde, test_X, L, device, n_samples=2)
    print(f"  U-GNN: aMMD={result['distance']['aMMD']:.4f}")
except Exception as e:
    print(f"  U-GNN FAILED: {e}")
    sys.exit(1)
```

### Provenance Capture Pattern

Always capture stdout/stderr to files and include in results JSON:

```python
# Save stdout/stderr to files
with open("vpd_stability_vXX/vXX_stdout.txt", "w") as f:
    f.write(stdout)
with open("vpd_stability_vXX/vXX_stderr.txt", "w") as f:
    f.write(stderr)

# Include in results JSON
output = {
    "command": f"{sys.executable} {script}",
    "exit_code": exit_code,
    "seed": 42,
    "stdout_lines": len(stdout.split('\n')),
    "stderr_lines": len(stderr.split('\n')),
    ...
}
```

### Metric Comparison Pitfall (v52-v54 lesson)

When comparing surrogate vs authoritative metrics, they must use the SAME formula:

- v52 used frequency*power (wrong)
- v54 used joint_runner's `compute_metrics_per_sample` (correct)

If formulas differ, the "mismatch" is methodological, not a real comparison. Always verify the metric computation method matches between compared artifacts.

## CPU/GPU Divergence Localization (v80-v82 pattern)

This session developed a methodology for isolating the first divergent operation between CPU and GPU:

### Step 1: Production Hooks (v80)
Inject diagnostics directly into production functions, not wrapper scripts:

```python
# In joint_runner.py - add diagnostics parameter to production functions
def train_model_vpsde(model, train_loader, sde, L, device, epochs=100, lr=1e-3, diagnostics=None):
    if diagnostics is not None:
        diagnostics["train_input"] = {"hash": hash_tensor(batch_x0), ...}
        # ... capture all key stages

def sample_reverse_sde_vpsde(sde, net, shape, steps=1000, diagnostics=None):
    # Instrument inside the actual sampler
    if diagnostics is not None and k == 0:
        diagnostics["after_clamp"] = {"clamp_count": ..., "hash": ...}
```

**Critical**: Don't create synthetic evaluators - call the actual production functions.

### Step 2: State Capture/Replay (v81)
Serialize exact CPU state for GPU replay:

```python
# CPU captures full state
state_bundle = {
    "batch_indices": ...,
    "batch_x0": batch_x0.numpy(),
    "t_first": t_first.numpy(),
    "noise_first": noise_first.numpy(),
    "model_state": {k: v.numpy() for k, v in model.state_dict().items()},
    ...
}
with open("cpu_state_bundle.pkl", "wb") as f:
    pickle.dump(state_bundle, f)

# GPU loads exact same state
model.load_state_dict({k: torch.tensor(v).to("cuda") ...})
```

### Step 3: Per-Component Analysis (v82)
Compare each computation stage separately with tolerances:

```python
def max_abs(a, b):
    return float((a - b).abs().max())

def max_rel(a, b):
    diff = (a - b).abs()
    denom = (a.abs() + b.abs()).clamp_min(1e-8)
    return float((diff / denom).max())

TOLERANCE = 1e-5
mean_t_abs = max_abs(mean_t_cpu, mean_t_gpu_cpu)
std_t_abs = max_abs(std_t_cpu, std_t_gpu_cpu)
# ...

component_results = {
    "mean_t": {"max_abs": mean_t_abs, "pass": mean_t_abs < TOLERANCE},
    "std_t": {"max_abs": std_t_abs, "pass": std_t_abs < TOLERANCE},
    ...
}
```

### Key Findings from v80-v82

1. **Core computations are identical**: mean_t, std_t, x_t, score all within 1e-6 tolerance
2. **Sampler diverges**: Clamp counts differ at step 1+ (first clamp difference: CPU=1, GPU=0)
3. **Root cause**: The sampler clamp operation behaves differently on GPU after initial saturation

### Required Hash Closure

Supervisor requires ALL dependencies, not just main files:

```python
input_hashes = {
    "v82_runner.py": wrapper_hash,
    "v82_comparison.py": hash_file(producer_path),
    "slurm.sh": slurm_hash,
    "gad_models.py": gad_hash,
    "joint_runner.py": joint_hash,
    "cpu_state_bundle.pkl": bundle_hash,
    "metr_la_data/metr_x_train.npy": hash_file("..."),
    "metr_la_data/metr_la_adj.npy": adj_hash,
    "metr_la_data/metr_la_laplacian.npy": lap_hash,
}
```

### Slurm Step Status Check

Always check for CANCELLED Python step:

```python
# Slurm may show COMPLETED but Python step is CANCELLED
if "CANCELLED" in result.stderr or "CANCELLED" in result.stdout:
    exit_code = 1  # Fail-closed
```

The accounting shows parent/batch COMPLETED but step 0 CANCELLED - this must trigger failure.
