# GSD Supervisor Workflow

## Supervisor Hierarchy

- **gsd** (this agent): graph-signal-diffusion implementation, runs under
  supervision of **gsd-supervisor**
- **gsd-supervisor** (ml2ran02 /pts/28): supervises gsd's research, verifies
  setups, approves GPU experiments, verifies claims and artifacts

## Coordination Pattern

### Before GPU Experiments (2026-08-19 operator directive)

1. **Check in with gsd-supervisor** — describe:
   - Architecture (U-GNN vs plain transformer)
   - Dataset generation approach
   - Training config (epochs, batch, lr)
   - The exact slurm/srun command
2. **Get approval** — supervisor catches bugs before GPU hours burn
3. **Run** — execute when approved

### After Results

Supervisor pushes for:
- Ablations (what actually matters?)
- Alternative architectures (try X, try Y)
- More baselines (how does plain transformer compare?)
- Scaling (bigger models?)
- Different datasets (generalization?)

Expect continuous research — one experiment leads to the next question.

## Agent-Net Registration

Register at session start:

```bash
agent-net-register gsd "graph-signal-diffusion agent"
```

Verify registration:

```bash
agent-net-list  # check 'gsd' appears with ● on correct tty
```

## Arming the Listener (RECOMMENDED: arm-once loop)

```bash
export AGENT_NAME=gsd
while true; do agent-net-listen gsd; sleep 2; done
```

**MUST** be run as a background process with `watch_patterns=["agent-net message"]`:
- WITHOUT `watch_patterns`, messages ARE delivered but you are NEVER notified
- The agent goes dark silently (observed 2026-08-18 qmc incident)

## Dataset Generation

### Full Run
- **Networks:** 128 (32 per density × 4 densities: high, mid, low, ultralow)
- **Nodes per network:** N=400
- **QoS levels:** 0.4, 0.5, 0.6, 0.7, 0.8
- **Samples per network:** 200
- **Split:** 5:1:2 (train:val:test) → 20:4:8 per density

### Tiny Mode (CPU smoke)
```bash
python scripts/generate_dataset.py --tiny
```
- **Networks:** 2 per density (8 total)
- **Nodes:** N=20
- **Samples:** 4
- **QoS:** single (0.6)
- **Expert iterations:** max_iter=60, window=20, n_fade=2, primal_steps=2

## Training

### Shared DDPM objective
- T=500 diffusion steps
- DDIM sampling disabled during training (DDIM_STEPS=0)
- Loss: MSE on noise prediction (`diff.p_loss`)

### Tiny Mode
```bash
python scripts/train_denoiser.py --model ugnn|transformer --tiny --out models/{model}_tiny.pt
```
- Epochs: capped at 6
- Batch: 64
- Train/val split: 5:1 on samples (64 total)

### Full Mode
- Epochs: 5000
- Batch: 64
- Learning rate: 1e-4
- Checkpoint saved by best val loss

### Architecture Details

**U-GNN** (`src/ugnn.py`)
- Interface: `model(x, t, u)` where `x:(B,N,1)`, `t:(B,)`, `u:(B,N,3)`
- Parameters: depth=3, hidden=64, cond_dim=128, hops=2, conv_layers=2
- Per-network shift operator: `shift_for(net)` in `src/trainhelpers.py`

**Plain Dense Transformer** (`src/transformer.py`)
- NO graph inductive bias (no adjacency matrix, no graph conv)
- Nodes treated as tokens (sequence of N node features)
- Standard transformer encoder → per-node noise prediction
- Interface matches U-GNN: `model(x, t, u)`

### Shared-Shift Simplification (Training)
- Train on fixed reference shift (identity) during training
- Per-network shift applied only at evaluation time
- This is a documented simplification, not the paper's full per-network conditioning

## Evaluation

### Metrics (paper experiments.tex)
- **Protocol:** 100-slot horizon, per-receiver cumulative ergodic rate
- **Reported:** p1, p5, mean rate pooled across all test receivers

### Baselines
- **FP:** full power (all nodes transmit at PMAX_MW=10mW)
- **AP:** expert conditional mean (mean of primal-dual iterates)
- **Expert:** sample from primal-dual iterates

### Learned Policies
- Load checkpoint: `models/{model}_tiny.pt` (or `{model}.pt` for full)
- DDIM sampling with 100 steps (configurable)
- Per-network shift for U-GNN, shared for transformer

## Common Pitfalls & Fixes

### 1. Import mismatch: `UGraphSignalDiffusion` vs `UGNN`
**Symptom:** `ImportError: cannot import name 'UGraphSignalDiffusion'`

**Fix:** Update all imports:
```python
from src.ugnn import UGNN  # NOT UGraphSignalDiffusion
```
Files: `scripts/train_denoiser.py`, `src/trainhelpers.py`

### 2. Batch axis layout mismatch
**Symptom:** `RuntimeError: mat1 and mat2 shapes cannot be multiplied (26x400 and 1x32)`

**Cause:** Dataset shape is `(nets, samples, N)` but models expect `(B,N,1)`.

**Fix:** Reshape + broadcast in `load_all()`:
```python
P = P.reshape(-1, P.shape[-1])  # (nets*samples, N)
U = np.broadcast_to(U[:, None], (U.shape[0], P.shape[0] // U.shape[0],
                                 U.shape[1], U.shape[2])).reshape(-1, U.shape[1], U.shape[2])
F = np.repeat(F, P.shape[0] // F.shape[0])
```
And in training:
```python
x0 = torch.tensor(Ptr[b, :, None], dtype=torch.float32, device=device)  # (B,N,1)
```

### 3. Transformer output shape
**Symptom:** `RuntimeError: The size of tensor a (26) must match the size of tensor b (400)`

**Cause:** Transformer outputs `(B,N)` but noise target is `(B,N,1)`.

**Fix:** Remove `[..., 0]` from final output:
```python
return self.out(tokens)  # (B,N,1) matches noise target
```

### 4. Expert smoke timeout (CPU too slow)
**Symptom:** `timeout 400 python -u scripts/generate_dataset.py --tiny` exits 124

**Cause:** Primal-dual iterations on CPU with full `n_fade=16`, `max_iter=60`.

**Fix:** Reduce params in tiny mode:
```python
n_fade = 2 if args.tiny else None
max_iter = 60 if args.tiny else None
window = 20 if args.tiny else None
primal_steps = 2 if args.tiny else None
```
And in `generate_expert_samples`:
```python
res = generate_expert_samples(..., n_fade=n_fade, max_iter=max_iter,
                               window=window, primal_steps=primal_steps)
```

### 5. Checkpoint naming inconsistency
**Symptom:** `[transformer] no checkpoint /models/transformer.pt; skipping`

**Cause:** Tiny training saves to `{model}_tiny.pt`, eval looks for `{model}.pt`.

**Fix:** Eval script uses `model_name + ('_tiny' if args.tiny else '')`.

### 6. Array `max()` vs `np.maximum`
**Symptom:** `max(dist, D_MIN_M)` fails on array inputs.

**Fix:** Use `np.maximum(dist, D_MIN_M)` for vectorized comparison.

## Related References

- `agent-net` skill SKILL.md — complete agent-net protocol & arming patterns
- Paper 2604.05175 sections (in `papers/`): diffusion.tex, experiments.tex,
  ugnn_architecture_training.tex, baselines.tex, dual_descent_algorithm.tex,
  optimal_resource_allocation.tex
- `src/wireless.py` — network generation, large-scale gain, rate computation
- `src/diffusion.py` — DDPM/DDIM outer loop, p_loss objective
- `src/ugnn.py` — U-GNN architecture with poly conv, zero-pad pooling
- `src/transformer.py` — plain dense transformer (nodes as tokens)
- `src/expert.py` — primal-dual expert policy with ergodic rates
- `src/trainhelpers.py` — shared eval helpers, shift_for per-network operator
