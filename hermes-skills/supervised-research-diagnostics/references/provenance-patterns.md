# Provenance Verification Patterns

## Overview

These patterns emerged from the v44-v48 provenance verification work under the gsd-supervisor.

## Atomic Write Pattern

```python
import tempfile
import os

def atomic_write(path, content):
    with tempfile.NamedTemporaryFile(dir=os.path.dirname(path), delete=False) as tmp:
        tmp_path = tmp.name
    with open(tmp_path, "wb") as f:
        f.write(content)
    os.rename(tmp_path, path)
```

## Strict JSON with Finite Validation

```python
import json
import numpy as np

def strict_validate_finite(obj, path="root"):
    """Recursively validate all floats are finite - fail-closed."""
    if isinstance(obj, float):
        if not np.isfinite(obj):
            raise ValueError(f"Non-finite float at {path}: {obj}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            strict_validate_finite(v, f"{path}.{k}")
    elif isinstance(obj, (list, np.ndarray)):
        for i, v in enumerate(obj):
            strict_validate_finite(v, f"{path}[{i}]")
    elif isinstance(obj, np.floating):
        if not np.isfinite(obj):
            raise ValueError(f"Non-finite numpy float at {path}: {obj}")

def convert_for_json(obj):
    if type(obj) is bool:
        return int(obj)
    elif type(obj) is np.bool_:
        return int(obj)
    elif isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, np.ndarray)):
        return [convert_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if not np.isfinite(obj):
            raise ValueError(f"Non-finite float: {obj}")
        return float(obj)
    elif isinstance(obj, np.floating):
        if not np.isfinite(obj):
            raise ValueError(f"Non-finite numpy float: {obj}")
        return float(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    return obj
```

## Baseline Hash Pattern

```python
import hashlib

FORBIDDEN_PATHS = {
    "vpd_stability_results.json": "/path/to/vpd_stability_results.json",
    "vpd_stability": "/path/to/vpd_stability/",
}

def get_file_hash(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def get_dir_hashes(path):
    if not os.path.exists(path):
        return {}
    hashes = {}
    for f in sorted(os.listdir(path)):
        fpath = os.path.join(path, f)
        if os.path.isfile(fpath):
            hashes[f] = get_file_hash(fpath)
    return hashes

# Record BEFORE run
baseline_hashes = {}
for name, path in FORBIDDEN_PATHS.items():
    if os.path.isfile(path):
        baseline_hashes[name] = get_file_hash(path)
    elif os.path.isdir(path):
        baseline_hashes[name] = get_dir_hashes(path)

# Check AFTER run
violations = []
for name, path in FORBIDDEN_PATHS.items():
    if os.path.isfile(path):
        if get_file_hash(path) != baseline_hashes.get(name):
            violations.append(f"{name} modified")
    elif os.path.isdir(path):
        if get_dir_hashes(path) != baseline_hashes.get(name):
            violations.append(f"{name} modified")
```

## Fail-Closed File Check

```python
REQUIRED_SEEDS = [42, 142, 242]
REQUIRED_FILES = ["samples.npz", "metrics.npz"]

def copy_npz_atomic(seed, source_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    
    missing_files = []
    for file_type in REQUIRED_FILES:
        src = os.path.join(source_dir, f"seed_{seed}_{file_type}")
        if not os.path.exists(src):
            missing_files.append(f"seed_{seed}_{file_type}")
    
    if missing_files:
        raise FileNotFoundError(f"FAIL-CLOSED: Missing required files: {missing_files}")
    
    # ... proceed with atomic copy
```

## Per-Seed Validation (not global)

```python
for seed in seeds:
    # Per-seed shape validation
    seed_shape_valid = (n_qv == n_samples and n_sc == n_samples and n_dc == n_samples)
    
    # Per-seed finite check
    all_finite = bool(np.all(np.isfinite(stored_qv)) and ...)
    
    # Per-seed metric comparison
    qv_match = np.allclose(stored_qv, recomputed_qv, rtol=1e-4, atol=1e-6)
    
    seed_passed = seed_shape_valid and all_finite and qv_match and sc_match and dc_match
    all_passed = all_passed and seed_passed
    
    verifier_results[f"seed_{seed}"] = {
        "seed_shape_valid": seed_shape_valid,
        "all_finite": all_finite,
        "seed_passed": seed_passed,
        ...
    }
```

## Loading Authoritative Metrics

```python
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

def load_joint_runner():
    runner_path = os.path.join(SCRIPT_DIR, "joint_runner.py")
    spec = spec_from_loader("joint_runner", SourceFileLoader("joint_runner", runner_path))
    module = module_from_spec(spec)
    sys.path.insert(0, SCRIPT_DIR)
    spec.loader.exec_module(module)
    return module

# Usage
jr = load_joint_runner()
compute_metrics_per_sample = jr.compute_metrics_per_sample
results = compute_metrics_per_sample(x, L, U)
```

## Collision-Safe Output Directory

```python
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "vpd_stability_v50")

# Fail if output already exists (collision-safe)
if os.path.exists(OUTPUT_DIR):
    for f in os.listdir(OUTPUT_DIR):
        print(f"FAIL: Output family already exists: {f}")
        sys.exit(1)
os.makedirs(OUTPUT_DIR)
```
