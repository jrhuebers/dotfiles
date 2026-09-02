---
name: create-new-research-repo
description: "Use when scaffolding a new research repo or project setup."
version: 1.0.0
author: huebers
platforms: [linux, macos]
---

# Create New Research Repo

## When to Use

Scaffolding a new Python research project/repo, or aligning an existing one
with the user's conventions. The FIM repo is the reference implementation.

## Tech stack (as used in FIM)

- **Python** `>=3.10,<3.13` (ruff target py312)
- **uv** for everything: `uv init`/`uv add`/`uv run`; `[dependency-groups]`
  (dev/test/notebooks/datagen); git deps pinned via `[tool.uv.sources]`
  (rev-pinned); `uv run <script>` via `[project.scripts]`
- **Build**: hatchling, src/ layout (`packages = ["src/<pkg>", "scripts"]`)
- **CLI**: typer for tool CLIs (the `app` pattern; entry points like
  train/finetune/eval-*); hydra-core>=1.3 for experiment configs (see the
  fim-hydra-recipes skill for the recipe workflow)
- **rich** for all CLI output
- **Logging**: loguru + colorlog, root `logging_config.yaml`
- **Config**: pydantic nested models (`StrictConfig`, `extra="forbid"`);
  typed dot-access in code, `model_dump()` only at serialization boundaries
- **ML**: torch>=2.5, torchdiffeq/torchode, torchinfo, transformers,
  huggingface_hub, model-registry (own git dep)
- **Data/sci**: numpy, pandas, scipy, scikit-learn, h5py, matplotlib, seaborn
- **Tracking**: wandb + tensorboard
- **Tests**: pytest (`testpaths=["tests"]`, `addopts = "-ra"`), pytest-cov,
  pytest-env
- **Lint/format**: ruff (`line-length = 140`, `select = ["C","E","F","I","W"]`,
  ignore C901/E501/E741/F402/F823), pre-commit, tox, nbstripout/nbdime
- **Repo hygiene**: AGENTS.md at root, CONTRIBUTING.md,
  LICENSE.txt, .gitattributes, .github/workflows, .yamllint,
  .pre-commit-config.yaml
- **CI**: single `.github/workflows/test.yml` — runs on push/PR to `develop`
  (the default branch), one Python version, install deps then pytest + ruff;
  secrets (e.g. HF_TOKEN) via workflow `env`, never committed

## Style

- PEP 604 unions (`A | B`, `A | None`); never import `Union`/`Optional`
- Typed configs, never unvalidated dicts; pydantic `extra="forbid"`
- Type hints everywhere; 140-char lines
- DDP for distributed training (no FSDP)
- Every training run dir gets a `.log` file (metrics, config, start/end) in
  addition to wandb
- Multi-seed evaluation for headline claims: >=3 train seeds x >=8 eval
  replicates; single-seed runs OK for screening but flagged as such
- Run/job naming `w1-<method>`, `w2-<variant>` for greppable batches

## Checkpoint / run-dir layout

Every training run lives under `models/<run-name>/` (config:
`checkpointing.experiment_dir: ./models`):

    models/<run-name>/
      checkpoints/epoch-<N>/   # 0-indexed epoch dirs (AGENTS.md convention)
      checkpoints/best-model/
      logging/train.log        # REQUIRED local log (metrics, config, start/end)
      logging/tensorboard/
      wandb/                   # local wandb mirror
      wandb-run-id.txt
      model_architecture.txt
      train_parameters.yaml    # resolved config snapshot

Rules:
- **Local .log is mandatory** — every run dir gets `logging/train.log` in
  addition to wandb (wandb is primary tracking, but the file log must exist).
- **Results land in the model's run dir**: any experiment result — pdf, json,
  figures, eval outputs — produced about a model goes into that model's
  run/checkpoint dir (`models/<run-name>/...`), never in cwd or ad-hoc
  locations. If you run an experiment on a model, write the result next to its
  checkpoints.
- Checkpoint dirs are named `epoch-<N>` with 0-indexed epochs; `best-model`
  holds the best checkpoint.

## Scaffold checklist

1. `uv init` + hatchling src-layout package
2. pyproject with `[project.scripts]`, `[dependency-groups]`,
   `[tool.uv.sources]`, ruff + pytest config blocks
3. .pre-commit-config.yaml + .yamllint + .gitattributes
4. tests/ with pytest setup
5. AGENTS.md + README.md + LICENSE.txt + CONTRIBUTING.md
6. configs/ with hydra baseline config + recipe/ dir (fim-hydra-recipes)
7. logging_config.yaml + run-dir .log convention
