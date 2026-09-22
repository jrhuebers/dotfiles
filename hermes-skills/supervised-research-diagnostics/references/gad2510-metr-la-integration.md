# GAD2510 METR-LA U-GNN/Transformer Integration

## Session Context

Working on reproducing arXiv:2510.05036 (GAD) - Graph Adversarial Diffusion. Focus: integrating U-GNN and Transformer models into the METR-LA benchmark pipeline.

## Key Artifacts

| Version | Purpose | Status |
|---------|---------|--------|
| v59 | CPU smoke test for model forward pass | ACCEPTED NARROWLY |
| v60 | Parameter/gradient registration + time sensitivity | ACCEPTED |
| v61 | Direct VPSDE smoke (2 models) | ACCEPTED NARROWLY |
| v62 | Runner integration with reproducibility | PENDING |

## U-GNN/Transformer Integration Steps

### 1. Fix gad_models.py

Two bugs found and fixed:

```python
# DenoiserUGNN - was creating nn.Linear inside forward() (line 199)
# Fixed: Use registered self.t_proj layer
t_feat = self.t_proj(t_emb)  # NOT: nn.Linear(self.t_dim, self.C, ...)

# DenoiserTransformer - same issue
# Fixed: Added self.t_proj in __init__, use it in forward
```

### 2. Add to joint_runner.py imports (lines 31-33)

```python
from gad_models import (
    DenoiserMLP,
    DenoiserGNN,
    DenoiserUGNN,      # ADDED
    DenoiserTransformer,  # ADDED
    ...
)
```

### 3. Add to run_metr_la_benchmark() (after GNN cells)

```python
# U-GNN - all three SDEs
print("\n--- Training GASDE U-GNN ---")
ugnn = DenoiserUGNN(S=A, Ks=3, t_dim=64, C=16)
ugnn = train_model(ugnn, train_loader, sde_gasde, L, device, epochs=epochs)
results["METR_LA_GASDE_UGNN"] = evaluate_model(ugnn, sde_gasde, test_X, L, device, n_samples=n_eval_samples)

# ... similar for VPSDE, VESDE

# Transformer - all three SDEs
print("\n--- Training GASDE Transformer ---")
trans = DenoiserTransformer(S=A, t_dim=64, C=64, n_heads=4, n_layers=2)
trans = train_model(trans, train_loader, sde_gasde, L, device, epochs=epochs)
results["METR_LA_GASDE_Transformer"] = evaluate_model(trans, sde_gasde, test_X, L, device, n_samples=n_eval_samples)

# ... similar for VPSDE, VESDE
```

## v62 Results

With seed_everything(42):

| Model | aMMD |
|-------|------|
| METR_LA_VPD_UGNN | 4.7497 |
| METR_LA_VPD_Transformer | 3.7228 |

## Molene Dataset

Canonical source: https://github.com/bgirault-usc/Molene-Dataset

Acquired files:
- `aggregated_data.csv` (SHA256: a61cbb8ef6a984c1...)
- `weather_stations.csv` (SHA256: 0c17e597f87ff7c1...)

**Provenance gap**: Paper specifies 37 stations, 670 train / 74 test. Source has 49 stations but only 27 with valid lat/lon coordinates. Current acquisition: 27 stations × 669 train / 75 test (hourly temporal split).

Supervisor rejected as "canonical benchmark dataset" - needs resolution.

## Model Collapse Root Cause (v51-v52)

Unnormalized training data (mean=56.4, std=17.2) + clamp(-10,10) + prior N(0,I) → model outputs ~10 regardless of input.

Fix: Standardization (Condition C in v52 ablation):
- A(raw+clamp): COLLAPSE to 10.0
- B(raw,no clamp): EXPLODE to -2e15
- C(std+clamp): HEALTHY (mean=60.37, std=15.75, unique=1035)
- D(std,no clamp): UNSTABLE (367±513)

## Relevant File Hashes

| File | Hash |
|------|------|
| gad_models.py | 153d8fbb2ccbea69... |
| joint_runner.py | 786d9bd73607989c... |
| v62_runner_integration.py | 3c10b85249c8721f... |
| v62_results.json | e12731bc375b1bc3... |
