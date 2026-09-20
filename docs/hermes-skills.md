# Archived Hermes skills

`hermes-skills/` is an archive of historical skills created by a
self-improving Hermes agent or later synthesized from large Hermes skills. It
is **reference material, not an installable skill collection**.

Tools that discover or install skills must use `skills/` and must not scan,
symlink, or install `hermes-skills/`. The active directory contains the
selected admin, research, and workflow skills:

- `admin`, `computational-research`, `create-new-research-repo`,
  `hydra-config-management`,
  `report-writing`, `research-paper-writing`, and
  `supervised-research-diagnostics`;
- `start-slurm-job` and `training-run-analysis` (the Codex-imported skills);
- `synthesized/agent-coordination`, `synthesized/arxiv-latex-sources`,
  `synthesized/ml-diagnostics`, `synthesized/paper-writing`,
  `synthesized/research-workflow`, and `synthesized/slurm-ops`.

The remaining Hermes-generated, curator-authored, mixed-authorship, and
unattributed skills stay archived. In particular, `supervisor` remains
archived because its recorded authorship is `huebers, Hermes Agent`, not
solely `huebers`.

## Use and promotion

Read an archived skill only when its historical guidance is specifically
useful. Do not load it automatically into an agent context or treat it as
current operational policy.

To make an archived skill active, first review it for correctness, security,
current tool availability, authorship, and overlap with existing guidance.
Make a purposeful copy into `skills/`, document why it is active, and update
[`device-profiles.md`](device-profiles.md) if its deployment scope differs by
machine profile. Do not promote a whole archive directory.

## Removal

The archive has no installation. To remove the historical material from a
checkout, delete `hermes-skills/`; this does not affect active `skills/`.
