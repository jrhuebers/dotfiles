# CUDA / Torch Compatibility on gwkilab GPU Nodes

## Driver history

| Date       | Driver       | CUDA | Notes                                    |
|------------|-------------|------|------------------------------------------|
| Pre-2026-08 | 570.211.01  | 12.8 | cu130 torch FAILED ("NVIDIA driver too old") |
| 2026-08-20 | 580.167.08  | 13.0 | cu128 AND cu130 both work                 |

Verified 2026-08-20 on durian (job 53685, ml2ran05) and coconut (job 53769,
ml2ran01), both A100-SXM4-40GB.

## Torch wheel compatibility matrix (driver 580.167.08 / CUDA 13.0)

| Wheel           | Torch version | `cuda.is_available()` | Status |
|-----------------|---------------|-----------------------|--------|
| cu128           | 2.11.0+cu128  | True                  | Works  |
| cu130 (default) | 2.13.0+cu130  | True                  | Works  |

Both verified via `srun --jobid=<id> --overlap --cpu-bind=none --mem=2G` on
durian.

## The original failure (driver 570.x / CUDA 12.8)

When drivers were 570.211.01 (CUDA 12.8), the default PyPI torch wheel was
cu130. The cu130 wheel requires CUDA 13.0+ runtime, so it reported
`torch.cuda.is_available() == False` with the error "NVIDIA driver too
old" — a silent CPU-only fallback.

### Impact (before the driver upgrade)

- **FIM**: ODEBench evals ran on CPU for hours instead of GPU minutes.
- **gauge**: torch 2.13 (cu130) had a `Tensor.norm(dim)` regression that
  broke the SU(2) exponential map — the model appeared to "never learn"
  but the math was silently broken.
- **marker-pdf**: PDF conversion took 25 min on CPU instead of 1 min on GPU.

### Original fix (still works, backward compatible)

- Prebuilt venv: `~/.venvs/torch-cu128` (torch 2.11.0+cu128 + numpy)
- Wrapper: `~/.local/bin/torch-gpu <script.py>`
- uv pin: `--index-url https://download.pytorch.org/whl/cu128`

## Current guidance (driver 580.x / CUDA 13.0)

The cu128 pinning is NO LONGER STRICTLY NECESSARY — default cu130 torch
works. However:

1. **cu128 venv remains a safe default** — it works on all nodes
   (including any that haven't been upgraded yet).
2. **Always check the driver first** before debugging CUDA issues:
   `nvidia-smi --query-gpu=driver_version --format=csv,noheader`
3. **The torch.version.cuda string does not need to match nvidia-smi's
   CUDA version exactly** — torch's CUDA runtime just needs to be <= the
   driver's CUDA capability. cu128 torch (runtime 12.8) runs fine on a
   CUDA 13.0 driver; cu130 torch (runtime 13.0) does NOT run on a CUDA
   12.8 driver.

## Verification commands

```bash
# Check driver
nvidia-smi --query-gpu=driver_version --format=csv,noheader

# Test torch CUDA from a job
srun --jobid=<id> --overlap --cpu-bind=none --mem=2G \
  ~/.venvs/torch-cu128/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available())"

# Test default (cu130) torch from a job
srun --jobid=<id> --overlap --cpu-bind=none --mem=2G \
  uv run --with torch python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```
