# CPU/GPU Paired Comparison Pattern

## Context

When the supervisor grants GPU authorization after a CPU gate, the GPU run may use different hyperparameters (epochs, n_eval_samples) than the CPU baseline. The supervisor explicitly rejects such comparisons as "protocol drift."

## The Solution: Paired CPU/GPU Runs

Run BOTH CPU and GPU with IDENTICAL configuration:

```python
# CONFIG - SINGLE SOURCE OF TRUTH
EPOCHS = 1
N_EVAL_SAMPLES = 2
SEED = 42
```

The producer code receives these via environment variables or f-string interpolation, NOT hardcoded values.

## v75 Pattern (Working)

```python
# Producer receives config from environment
EPOCHS = int(os.environ.get("GAD_EPOCHS", "1"))
N_EVAL_SAMPLES = int(os.environ.get("GAD_SAMPLES", "2"))
DEVICE = os.environ.get("GAD_DEVICE", "cpu")
```

Or embed at producer creation time:
```python
producer_code = f'''...
epochs = {EPOCHS}
n_eval_samples = {N_EVAL_SAMPLES}
...'''
```

## Common Pitfalls

### 1. Hardcoded config mismatch
- **Error**: Wrapper has EPOCHS=5 but producer hardcodes epochs=50
- **Fix**: Single source of truth - pass config to producer

### 2. CPU too slow
- **Fix**: Use minimal config (epochs=1, samples=2) just for device consistency check
- Report full GPU runs separately as standalone training results

### 3. Slurm directory pre-create
- Slurm creates output directory BEFORE script runs
- Check for actual artifacts, not just directory existence
- See: immutable-artifact-families.md for the fix pattern

## Artifact Structure

v75 produced:
- `cpu_stdout.txt`, `cpu_stderr.txt`
- `gpu_stdout.txt`, `gpu_stderr.txt`  
- `v75_results_cpu.json`, `v75_results_gpu.json`
- `v75_manifest.json`, `v75_hashes.json`
- `vpd_*_cpu_raw.npz`, `vpd_*_gpu_raw.npz` (8 files)

## Key Lesson

The supervisor accepts GPU authorization but REJECTS CPU/GPU comparison when protocols differ. The paired run with identical config proves device consistency at minimal cost, then full GPU runs are standalone.

## v73-v75 Iterations

| Version | Issue | Fix |
|---------|-------|-----|
| v73 | CPU/GPU with different epochs (1 vs 50) | Accepted as CPU gate, GPU separate |
| v74 (failed) | Hardcoded config mismatch in producer, no timeout handling | Single source of truth, timeout catch |
| v75 | Slurm pre-create dir, CPU slow | Check for actual artifacts, minimal config (1/2) |

The supervisor requires:
1. Fresh immutable family (no overwrite)
2. Single source of truth for config
3. Proper timeout handling with failure artifacts
4. Identical config for paired CPU/GPU
5. All hashes tracked (wrapper/producer/slurm)
