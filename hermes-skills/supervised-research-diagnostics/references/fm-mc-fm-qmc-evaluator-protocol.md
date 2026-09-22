# FM-MC/FM-QMC Evaluator Protocol - August 2026

## Background
Supervised evaluation of FM transport models under qmc-supervisor. Key decisions made in this session.

## Authorization
- Supervisor 13:35:05: Authorized FM-MC + FM-QMC only (ISQMC blocked)
- Supervisor 13:39:45: Smoke v10 audit passed, authorized full panel

## Protocol (Canonical)
- r values: 1, 4, 16, 30
- R: 10 replicates  
- powers: 5-13 (N=32 to 8192)
- seed: 7
- 64-step Heun, Gaussian base
- FM-MC: logistic (clamped to [1e-6, 1-1e-6]) → transport.from_base()
- FM-QMC: scrambled Sobol → transport()
- allow_pickle=False

## JSON Hash Pitfall

**Problem**: Self-referential JSON hash always mismatches.

**Bad pattern** (rejected):
```python
# Write content
with open(json_path, "w") as f:
    json.dump(metadata, f, indent=2)
# Compute hash (but file now has no hash field)
json_hash = compute_hash(json_path)
# Add hash field - NOW FILE CHANGES, hash becomes invalid
metadata["json_hash"] = json_hash
with open(json_path, "w") as f:
    json.dump(metadata, f, indent=2)  # File changed, hash doesn't match!
```

**Solution**: Don't include self-referential hash. Use npz_hash to verify NPZ, trust JSON for metadata.

## ISQMC Blocking

- Supervisor rejected simplified ISQMC as "not true ISQMC"
- Exact Jacobian: 17s/sample → 32 days per r-value (infeasible)
- Exact divergence (batched_flow_log_prob): >600s timeout (infeasible)
- Mark as `isqmc_available: false` in JSON, omit from NPZ

## Smoke v10 Verification (Passed)
- NPZ: 8c7c1f1097a9ad1fda8b1c70f60615e435097573e3682649c6d4a0d463e4722e
- JSON: 06c7c53f7b133381f64dbb9da6a989b397514acc55a2592ce5d54f956b4a3487
- Shapes: (4,9,10) per cell
- All FM-MC, FM-QMC finite, no NaN
- Full commit SHA in metadata

## Artifacts
Each: `models/bg_alpha{ALPHA}-20260819-061419/evaluation_full/`
- results.npz: FM_MC, FM_QMC, FM_MC_mean, FM_MC_std, FM_QMC_mean, FM_QMC_std
- metadata.json: npz_hash, checkpoint_hash, commit_sha, isqmc_available=false
