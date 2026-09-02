# Immutable Artifact Families (v66-v69)

Patterns for producing supervisor-grade artifact packages with strict provenance requirements.

## The Problem: Output-Path Closure

A common rejection pattern: the claimed producer writes to a relative path, but execution happens from a different directory. The result ends up in the wrong place, breaking the hash chain.

**v66 error**:
- Producer wrote `open("v67_results.json", "w")` (relative)
- Wrapper ran with `cwd=SCRIPT_DIR`
- Results ended up at `/stock_forecast/v67_results.json`
- But manifest claimed they were in `vpd_stability_v67/`

**The fix**: Producer must explicitly change into the artifact directory:

```python
ARTIFACT_DIR = "vpd_stability_v69"
os.chdir(ARTIFACT_DIR)  # Producer runs INSIDE the artifact directory
# Now all relative paths resolve to v69_dir
```

## Dead Code: Shared Dispatch Must Be CALLED

**v67 error**: `run_vpd_cell` function existed but was NEVER called:
- VPD cells directly instantiated models inline
- Shared dispatch was dead code
- Supervisor requires actual shared dispatch usage

**The fix**: ALL VPD cells must call `run_vpd_cell`:

```python
# In joint_runner.py run_metr_la_benchmark:
if should_run_cell("METR_LA_VPD_MLP", selected_cells):
    result = run_vpd_cell(
        "METR_LA_VPD_MLP",
        lambda: DenoiserMLP(n_nodes=N, t_dim=64, hidden=256),
        train_loader, sde_vpsde, test_X, L, device,
        epochs=epochs, n_samples=n_eval_samples, return_raw=True
    )
    if result["status"] == "FAIL":
        raise RuntimeError(f"VPD MLP failed: {result.get('error')}")
    results["METR_LA_VPD_MLP"] = result["metrics"]
```

## Raw Sample Propagation

**v67 error**: `return_raw=True` was passed, but raw data was silently dropped:
- `evaluate_model_vpd` returns `raw_generated`, `per_sample_qv`, etc.
- But `run_vpd_cell` looked for `result['raw']`, not the actual keys
- Raw data never made it to the output

**The fix**: Propagate all raw keys through run_vpd_cell:

```python
if return_raw:
    raw_data = {}
    if 'raw_generated' in result:
        raw_data['generated'] = result['raw_generated']
    if 'per_sample_qv' in result:
        raw_data['per_sample_qv'] = result['per_sample_qv']
    if 'per_sample_sc' in result:
        raw_data['per_sample_sc'] = result['per_sample_sc']
    if 'per_sample_dc' in result:
        raw_data['per_sample_dc'] = result['per_sample_dc']
    if raw_data:
        metrics['raw'] = raw_data
```

## Atomic Writes for NPZ

**v68 error**: Results used atomic writes, but NPZ files used direct `np.savez_compressed()`:
- Crash could leave partial NPZ
- Manifest claimed `atomic_writes: true` without covering NPZ

**The fix**: Atomic NPZ writes:

```python
def atomic_npz(path, **arrays):
    fd, tmp = tempfile.mkstemp(dir=".", suffix=".npz", prefix=".tmp_")
    os.close(fd)
    try:
        np.savez_compressed(tmp, **arrays)
        os.rename(tmp, path)
    except:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

# In producer:
atomic_npz(npz_name, **npz_data)
```

## Immutable Preservation: Never Overwrite

**v67 error**: Wrapper did `shutil.rmtree(v67_dir)` before running:
- Rerunning destroys prior evidence
- Violates "preserve v66 unchanged" directive

**The fix**: Fail if directory exists:

```python
v69_dir = "vpd_stability_v69"
if os.path.exists(v69_dir):
    print(f"ERROR: {v69_dir} already exists!")
    sys.exit(1)  # Refuse to overwrite
os.makedirs(v69_dir)
```

## Complete v69 Artifact Package

The final v69 pattern includes:

1. **Producer writes inside artifact directory** - explicit `os.chdir()`
2. **Atomic writes for JSON and NPZ** - temp + rename
3. **Recursive validation** - all numeric fields, shapes, dtypes, finiteness
4. **Explicit cell-to-NPZ mapping** - in results and manifest
5. **Induced failure test** - run with GAD_INDUCE_FAILURE=1, preserve exit=1
6. **Deterministic rerun** - run 3 times, compare hashes
7. **All runs captured** - run1/run2/run3 with stdout/stderr

```python
# v69 complete structure:
vpd_stability_v69/
├── run1_stdout.txt     # Normal run
├── run1_stderr.txt
├── run2_stdout.txt     # Induced failure
├── run2_stderr.txt
├── run3_stdout.txt     # Rerun
├── run3_stderr.txt
├── v69_producer.py
├── v69_results.json    # From run1
├── v69_manifest.json   # Full provenance
├── vpd_mlp_raw.npz     # Atomic write
├── vpd_gnn_raw.npz
├── vpd_ugnn_raw.npz
└── vpd_transformer_raw.npz
```

## Manifest Contents

The manifest must include:

- Input hashes: gad_models.py, joint_runner.py, metr-la.h5
- Data hashes: train/test/adjacency/Laplacian
- Output hashes: all stdout/stderr/NPZ/JSON files
- Run info: exit codes for all 3 runs, rerun_match boolean
- npz_map: explicit cell → file → keys → shapes mapping

## Induced Failure Test

Always preserve a failure run:

```python
import os
INDUCE_FAILURE = os.environ.get("GAD_INDUCE_FAILURE", "") == "1"

if INDUCE_FAILURE:
    raise RuntimeError("Induced failure test")

# Run twice: normal + induced
# Compare: run1 exit=0, run2 exit=1
# Both preserved in artifact family
```

## Rerun Verification

Prove determinism with hash comparison:

```python
run1_hash = hash_file("v69_results.json")
run3_hash = hash_file(...)  # After rerun
rerun_match = (run1_hash == run3_hash)
# Include in manifest
```
