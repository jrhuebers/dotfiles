---
name: hydra-recipe-pattern
description: "Use when adding or editing Hydra configs and recipes."
version: 1.0.0
author: huebers
platforms: [linux]
---

# Hydra Recipe Pattern

## When to Use

Creating a new training/eval variant in a Hydra-based repo, editing configs, or
launching a run that needs multiple overrides. The recipe system is how several
config changes get bundled: every variant gets a recipe that overwrites the
baseline.

## Architecture (repo-dependent, but the pattern is constant)

- Scripts are Hydra-decorated, e.g. `@hydra.main(config_path=configs/training,
  config_name="train")`, launched via `uv run <script> ...`.
- Every configurable script has a BASELINE config containing the defaults block.

## Defaults block ordering (the core rule)

A baseline `train.yaml` looks like:

    defaults:
      - hydra: no_output   # normal groups first
      - model: <baseline-model>
      - _self_             # then the baseline's own inline values
      - recipe: null       # recipe LAST -> overwrites everything above

Later entries override earlier ones. The recipe group comes after `_self_`, so a
selected recipe overrides ALL other settings (group defaults AND baseline
values). Never move `recipe` before `_self_`.

## Recipe files (`configs/<group>/recipe/<name>.yaml`)

Start from `recipe/TEMPLATE.yaml`. Anatomy:

    # @package _global_
    defaults:
      - /data: <dataset>  # select other groups via ABSOLUTE group paths
      - _self_
    experiment:
      name: <recipe-name>     # only experiment-specific overrides go here
    trainer:
      epochs: 200
    model:
      architecture:
        dim_embed: 264

- Put only what CHANGES vs the baseline in the recipe (model features/dims,
  run name, epochs, dataset).
- Select datasets/groups via the defaults list (`- /<group>: <value>`), never
  by editing inline values.
- Rejected alternative (documented in TEMPLATE): `recipe@_global_: <name>` in
  the baseline — forces ugly CLI syntax like
  `uv run train 'recipe@_global_=forward-backward'`. Don't use it.
- Abandoned recipes move to `recipe/historical/` — make a new recipe rather
  than resurrecting one.

## When a block of settings gets its own group directory

Give a block of settings its own group directory (`configs/<group>/<name>.yaml`)
only if at least one of these plausibly holds:

- The block will be reused across multiple configs/recipes (the same block
  selected in more than one place).
- There will plausibly be multiple block-level options to switch between — e.g.
  choosing between two different GNN architectures, each with its own config
  schema (different fields, not just different values).

Otherwise keep the block inline in the baseline. A group with a single member
and no expected variants adds indirection without payoff: it forces a
`- /group: name` selection line and a separate file for settings that could
live in the baseline. Split it out when the second variant actually appears,
not preemptively — but if you can already see the schema will differ between
options, that's the signal to group it now.

## Launch & verify

    uv run <script> recipe=<recipe-name>
    # inspect the RESOLVED config without running:
    uv run <script> recipe=<recipe-name> --cfg job

## Validating the resolved config with Pydantic (FIM pattern)

Hydra hands you an untyped OmegaConf tree. Validate it with nested Pydantic
models at the entry point, BEFORE any training/eval logic — this catches
typos, legacy fields, and wrong-schema mistakes at startup instead of
mid-run, which matters doubly with recipes (a bad recipe looks plausible).
Reference implementation: FIM `src/fim/config.py` + `src/fim/models/fimode/schema.py`.

1. **Strict base for everything:**

       class StrictConfig(BaseModel):
           model_config = ConfigDict(extra="forbid")

   `extra="forbid"` rejects unknown keys. A legacy field left in a recipe
   then fails loudly instead of being silently ignored while the base
   default stays selected (the "plausible-looking but wrong run" trap).

2. **Public schema mirrors the YAML layout exactly.** One nested
   `StrictConfig` class per config block (ExperimentInput, ModelInput →
   ArchitectureInput, TrainerInput, DataInput → LoaderInput, ...), nested as
   the public YAML is nested, so YAML/schema drift is visible at a glance.
   Optional fields carry explicit defaults (`= None`, `= True`).

3. **Single parse function at each Hydra entry point:**

       def parse_training_config(config: Mapping | DictConfig) -> RunConfig:
           raw_config = (
               OmegaConf.to_container(config, resolve=True, throw_on_missing=True)
               if isinstance(config, DictConfig) else config
           )
           # fail fast on a wrong schema
           if "architecture" not in raw_config.get("model", {}):
               raise ValueError("parse_training_config only accepts the public training schema.")
           public = PublicTrainingConfig.model_validate(raw_config)
           return RunConfig(  # internal, subsystem-owned typed config
               experiment=RunConfig.ExperimentConfig(
                   name=public.experiment.name, seed=public.experiment.seed, ...
               ),
               ...
           )

   - `OmegaConf.to_container(resolve=True)` resolves interpolations;
     `throw_on_missing=True` fails on missing keys.
   - `model_validate()` validates the whole tree in one shot.

4. **Two-layer split.** `Public*Config` = the resolved Hydra schema (matches
   YAML); `RunConfig` = internal config grouped by the runtime subsystem
   that owns it. Converter methods map public → internal
   (`def to_model_config(self, dropout: float) -> FIMODEModelConfig`).

5. **Keep the typed models through training code** — dot-access only;
   `model_dump()` / `to_dict()` only at serialization or helper boundaries.

6. **Conventions:** PEP 604 unions (`str | None`, never `Union`/`Optional`
   imports), `Literal[...]` for closed choices, string forward refs for
   nested self-references, `model_validator` for cross-field checks.

Payoff for recipes: a recipe with a typo'd or legacy key now dies at
`parse_*_config` with a precise error naming the offending field.

## Rules

- One recipe per variant; NEVER reconstruct a run by copying a saved run config
  (saved configs are snapshots, not sources of truth).
- Do not mix legacy config schemas into the current one — unknown legacy fields
  can be silently ignored while the base default stays selected, producing a
  plausible-looking but wrong run.
- Groups that use a different mechanism (`task: ???`, explicit eval configs
  passed to a CLI) don't use recipes — don't force recipes there.

## Pitfalls

- `recipe: null` in the baseline means "no recipe" — null is hydra's
  optional-group marker.
- The recipe filename IS the CLI value: `recipe=<name>` selects
  `recipe/<name>.yaml`.
- Set `experiment.name` to match the run-naming convention used by campaign
  skills so runs are greppable.
