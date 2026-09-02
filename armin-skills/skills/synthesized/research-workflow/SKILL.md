---
name: research-workflow
description: >-
  Research lifecycle: repo scaffolding, HPC experiment campaigns,
  literature search + PDF curation, Hydra config/recipe patterns,
  and pandoc PDF report generation.
version: 1.0.0
author: huebers
platforms: [linux, macos]
---

# Research Workflow

A condensed skill covering six research-adjacent concerns:

1. Research repo scaffolding
2. Autonomous HPC experiment campaigns
3. Literature search + PDF curation
4. Hydra config / recipe patterns
5. Pandoc PDF generation
6. Report writing

Portable scripts in `scripts/`: `chase_s2.py` (Semantic Scholar
citation/reference chase), `extract_text.py` (pypdf text extraction),
`figindex.py` (figure-caption index from LaTeX), `audit_readme_authors.py`
(bibliographic verification against the arXiv API).

---

## 1. Research Repo Scaffolding

### Tech stack

- **Python** `>=3.10,<3.13` (ruff target py312)
- **uv** for everything: `uv init`/`uv add`/`uv run`; `[dependency-groups]`;
  git deps pinned via `[tool.uv.sources]`; `uv run <script>` via `[project.scripts]`
- **Build**: hatchling, src/ layout
- **CLI**: typer for tool CLIs; hydra-core>=1.3 for experiment configs
- **Logging**: loguru + colorlog, root `logging_config.yaml`
- **Config**: pydantic nested models (`StrictConfig`, `extra="forbid"`);
  typed dot-access in code, `model_dump()` only at serialization boundaries
- **ML**: torch>=2.5, torchinfo, transformers, huggingface_hub
- **Tracking**: wandb + tensorboard
- **Tests**: pytest, pytest-cov
- **Lint/format**: ruff (`line-length = 140`), pre-commit, nbstripout

### Style

- PEP 604 unions (`A | B`, `A | None`); never import `Union`/`Optional`
- Typed configs, never unvalidated dicts; pydantic `extra="forbid"`
- Type hints everywhere; 140-char lines
- DDP for distributed training (no FSDP)
- Every training run dir gets a `.log` file (metrics, config, start/end)
  in addition to wandb
- Multi-seed evaluation for headline claims: >=3 train seeds x >=8 eval
  replicates; single-seed runs OK for screening but flagged as such
- Run/job naming `w1-<method>`, `w2-<variant>` for greppable batches

### Checkpoint / run-dir layout

Every training run lives under `models/<run-name>/`:

    models/<run-name>/
      checkpoints/epoch-<N>/   # 0-indexed epoch dirs
      checkpoints/best-model/
      logging/train.log        # REQUIRED local log
      logging/tensorboard/
      wandb/                   # local wandb mirror
      train_parameters.yaml   # resolved config snapshot

Rules:
- **Local .log is mandatory** — every run dir gets `logging/train.log` in
  addition to wandb.
- **Results land in the model's run dir**: any experiment result — pdf,
  json, figures, eval outputs — produced about a model goes into that
  model's run/checkpoint dir, never in cwd or ad-hoc locations.
- Checkpoint dirs named `epoch-<N>` (0-indexed); `best-model` holds best.

### Scaffold checklist

1. `uv init` + hatchling src-layout package
2. pyproject with `[project.scripts]`, `[dependency-groups]`,
   `[tool.uv.sources]`, ruff + pytest config blocks
3. .pre-commit-config.yaml + .yamllint + .gitattributes
4. tests/ with pytest setup
5. README.md + LICENSE.txt + CONTRIBUTING.md
6. configs/ with hydra baseline config + recipe/ dir
7. logging_config.yaml + run-dir .log convention

---

## 2. Autonomous HPC Experiment Campaigns

### When to use

Run experiments comparing methods on an HPC cluster with slurm and a git
repo containing an experiment codebase. The class is: hypothesis ->
controlled experiment batch -> diagnostics -> research log -> iterate,
without pestering the user.

### Workflow

1. **Survey first**: README, configs, tests, existing run dirs (they encode
   prior work), GPU/partition availability (`squeue -p <part>` counts
   running vs pending).
2. **Write the research log BEFORE running**: `documentation/research_log.md`
   with hypothesis, success metric, matched budget, theory. Commit it.
3. **Controlled experiments**: baseline + variants at IDENTICAL budget
   (steps, batch size, seed, model size unless the variant is
   architectural). One knob per variant. Name runs `w1-<method>` etc.
4. **Batch launcher** (per wave): one bash function that sbatch's a job per
   variant with `--parsable` to capture job IDs. Keep total concurrent jobs
   within the user's limit. Prefer explicit `--output=slurm-logs/<name>-%j.out`.
5. **Monitor via per-run log FILES, not slurm .out** (see pitfalls).
6. **Diagnostics beyond the headline metric**: measure WHY (map regularity,
   discrepancy, curvature, gradient norms). A diagnose script per model
   dir that saves `summary.yaml` makes batch comparison trivial.
7. **Update the research log after each wave** with results table and
   findings; commit code + log together.
8. **Iterate**: winners -> longer runs, higher dimensions, new benchmarks
   (incl. low-intrinsic-dimensionality cases).

### Evaluation rigor

- **Multi-seed**: >= 3 training seeds x >= 8 eval replicates for headline
  claims. Single-seed fine for screening but flag it.
- **File logging**: every run dir gets a `.log` file, not just wandb.
- **CPU fallback**: if GPU partition saturated, run on CPU with
  `OMP_NUM_THREADS=8`. Small models often only 2-4x slower on CPU.
- **Benchmark coverage**: include low-intrinsic-dimensionality / manifold
  targets (support dimension < ambient dimension), not only full-dim.

### Pitfalls (all hit and fixed in practice)

- **hydra `job_logging=disabled` silently kills your logger**: dictConfig
  sets `disable_existing_loggers: true` so FileHandler writes vanish (file
  exists, 0 bytes). Fix: `logger.disabled = False` after attaching handler.
- **hydra CLI override of a NEW key dies with "Key is not in struct"**: add
  the key to the baseline defaults first (`penalty_cap: null`) then override,
  or use `+` prefix to append. Adding to defaults is better — key shows in
  `--cfg job`.
- **`sbatch --wrap` cannot take script arguments** — nested quotes break it.
  Write the arg list to a file and have the wrap run a driver script that
  reads it; or embed args in the wrap string, never `"$@"`.
- **Python stdout to slurm .out is block-buffered** — metrics appear late.
  Log to a file in the run dir instead.
- **Concurrent parallel jobs writing a shared YAML registry corrupt it**
  (read-modify-write race). Wrap writes in `fcntl.flock`.
- **`torch.linalg.svdvals` returns DESCENDING singular values** — index 0
  is the max; swapping yields condition numbers < 1 (impossible).
- **Aux-loss weight scale check**: log the raw regularizer value early. If
  weight x value < ~1% of main loss, the run is effectively the baseline.
- **GPU partitions can look idle on CPUs yet be saturated on GPU slots**
  (85 running / 20 pending while CPUs idle). Check `squeue -p` job counts.
- **CUDA/torch — check driver before assuming incompatibility**:
  `nvidia-smi --query-gpu=driver_version --format=csv,noheader`. torch
  runtime CUDA <= driver CUDA capability; cu128 torch runs fine on CUDA 13.0
  driver; cu130 does NOT run on CUDA 12.8 driver. Silent CPU-only fallback
  (`torch.cuda.is_available() == False`) is the failure mode.
- **Verify kills actually landed**: `scancel <id>` can silently miss when
  job name matched by grep isn't a substring of the real name. After any
  cancel: `squeue -u <user>` AND
  `srun --jobid=<alloc> --overlap bash -c 'ps aux | grep <proc>'` to confirm
  (python child can survive as orphan still holding GPU).
- **Wait-loop launchers with stale run-dir names hang forever**: kill and
  restart the launcher, don't wait for it.
- **Checkpoint poisoning on NaN**: final checkpoint.pt can be NaN while
  periodic checkpoints are clean — check `torch.isnan(v).any()` over the
  state_dict before evaluating; swap the last clean periodic checkpoint.
- **`python -m <module>` can exit 0 with ZERO output (silent no-op)**:
  workaround: run the module's `main()` directly —
  `python -u -c "import sys; sys.argv=[...]; from <mod> import main; main()"`.
- **Double-backprop Jacobian penalties OOM at large batch**: VJP+JVP with
  `create_graph` doubles memory. Compute penalty on a subsample
  (`penalty_batch=64`) — it's a Hutchinson estimate, batch size only affects
  estimate quality. Use `interval=100`, `probes=1`. Smooth `log1p(penalty)`
  variant for gradient stability (magnitude bounded by 1/(1+x) <= 1).

---

## 3. Literature Search + PDF Curation

### Papers layout (convention)

- `papers/` dir per project (gitignored — PDFs/tex/tarballs are large).
- Corpus format per arXiv paper:
  - `arxiv_<id>.pdf` — ALWAYS downloaded (bare ID = latest version).
  - `arxiv_<id>.tex` — flattened via `latexpand --empty-comments` +
    verbatim-aware comment strip, version-stamped header; the primary
    LLM-reading format (native math). Derived artifact.
  - `src/<id>.tar.gz` — original e-print source tarball, canonical ground
    truth (figures live inside; flattening is zero-risk).
  - Non-arXiv papers: PDF only. Author-page PDFs: `curl -skL` (expired certs
    common), verify `%PDF` magic with `file`.
- Index: `papers/README.md` table `| File | Paper | arXiv | Why it matters |`.
- Deep-read status line: after any deep-read batch, add a line under the
  README table listing which papers have notes in `notes/`.
- `papers/FIGURES.md` — regenerable caption index via `scripts/figindex.py`;
  captions are the LLM-visible surface of figures.
- Deep-read notes: `papers/notes/<slug>-<arxiv-id>.md` — numbered sections,
  equations where extractable, KEY QUESTION flags, final "Relevance to
  <project>" section.

### Workflow (first pass / new direction)

1. Ground in the projects: read each project README + research log first.
2. Search: arXiv API. Batch queries per project, ~3-4s sleep between
   queries (rate limit), sort by submittedDate for freshness. Prefer
   targeted boolean queries over one generic query.
3. Curate: pick 5-15 papers per direction. The most valuable finds are
   often days/weeks old.
4. Download: `curl -sL https://arxiv.org/pdf/<id> -o arxiv_<id>.pdf`,
   skip existing files. List the target `papers/` dir first to avoid dupes.
5. Extract text: `uv run --with pypdf python3 scripts/extract_text.py <dir>`.
6. Index: write/extend `papers/README.md` with the new rows.
7. Regenerate FIGURES.md: `scripts/figindex.py <papers_dir>`.

### Discovery rounds (fresh searches + citation chasing)

Two complementary channels, run together:

1. **Fresh arXiv API boolean queries** (8-10 per round, 1 req/3s, UA
   header) — keep query angles NEW each round; first-pass queries go stale.
2. **Citation chasing via Semantic Scholar API** (keyless, the working
   channel):
   - Citations: `https://api.semanticscholar.org/graph/v1/paper/arXiv:<id>/citations?fields=title,year,externalIds,abstract&limit=100`
   - References: same with `/references` (response field: `citedPaper`).
   - `externalIds.ArXiv` on each hit gives candidate's arXiv ID for dedup.
   - Script: `scripts/chase_s2.py <aid>... [--direction citations|references]`.
   - Rate limits: ~1.2s sleep per call; bursts hit HTTP 429 — accept
     partial results, retry failed roots. Do NOT treat 429 as channel down.
   - OpenAlex's `ids.arxiv:` filter 400s — use S2, don't burn time on OpenAlex.

Chase the corpus's most central papers. Papers cited BY multiple corpus
papers are the highest-value finds (community convergence = high
relevance). Dedup against the corpus before reviewing; curate hard
(10-15 adds max per round).

Round checklist: (1) arXiv queries + S2 chases -> candidate list, (2)
curate to 10-15, (3) download into papers/, (4) index README new section
(grouped by theme), (5) regen FIGURES.md, (6) deliver themed digest,
(7) update the state doc's literature map.

### Deep reads (on request)

- Dispatch parallel reads, one per paper, with: exact text path + size,
  project context + the question being answered, required output structure,
  note-file write instruction, and title-vs-arXiv-ID verification step
  (arXiv IDs have been mixed up before).
- Question set: (1) exact method/architecture, (2) learned per-graph vs
  per-signal vs fixed, (3) relation to project baselines, (4) datasets +
  results (exact numbers), (5) theoretical claims, (6) limitations,
  (7) relevance section.
- REVIEW returned summaries before forwarding — claims are self-reports;
  spot-check surprising numbers against source text. Never forward
  unverified numbers.
- Implementation questions ("official code?"): verify with the GitHub API
  (repo live, stars, last push) and check whether the arXiv version is
  superseded by a published version.

### Read -> view loop (state tracking)

The user expects real reading and an up-to-date view of each project, not
PDF hoarding. Maintain a living state doc per project:
`state/<project>-state.md` with:

- **Goal & approach** (one paragraph)
- **Current state** (dated bullet facts with EXACT numbers)
- **Open questions / next steps** (numbered list — questions deep-reads
  should target)
- **Literature map** (corpus -> question): `| Paper | Addresses | Note |`
  with status (queued -> in flight -> ✓ with one-line takeaway)
- **Gap analysis** (what the literature does NOT cover = their novelty)

Update the literature map row the moment each deep-read note lands. Fold
peer corrections in with date + attribution. The gap analysis is the most
valuable section — telling a peer "this is your novelty" is a service.
Re-read the project's research log on every significant session.

State-doc status discipline: record proposed mitigations as PROPOSED,
never as done, until confirmed. Keep state docs open-ended — don't write
"freeze"/"closed" markers unless the operator says so. When direction
changes, record the supersede with date + attribution and remove the stale
marker in the same edit.

### Apples-to-apples protocol mapping

When judging results against a paper's published numbers:

1. Deep-read the paper first, extracting the EXACT eval spec (systems,
   grid, corruption, metric definition, denominator, seeds).
2. Read the codebase eval code: entry point, config, data loading, metric
   classes, reporting. Build a mapping table `Paper | Codebase (file:line)
   | Status`.
3. Enumerate the DELTAS explicitly — usually 2-3 real ones; label
   everything else "exact match". Propose one-line fixes with file:line.
4. Anchor: pull actual result artifacts and diff against the paper's
   table. Residual |delta| in the 1-2pt range = harnesses compatible.
5. Verify denominators arithmetically from raw artifacts. Do NOT trust
   memory or paper prose for per-dim splits — check the data.

### Bibliographic metadata: verify, never invent

- Every author/title/ID must come from the arXiv API (or S2/Crossref for
  non-arXiv) — NEVER from memory. Memory conflation of two papers from the
  same search is a real failure mode.
- Author lists: read from `export.arxiv.org` (batched `id_list` queries
  need `max_results=100` or only 10 entries come back).
- Peer-supplied arXiv IDs can be WRONG — verify the title via the API
  before fetching; search by title if the ID fails.
- Ambiguous acronyms: resolve by author + title, not the acronym.
- Unresolvable citations: say so explicitly, flag as likely-hallucinated,
  offer closest REAL alternatives (verified).
- API typos exist — whitelist known cases in the audit script.
- Run `scripts/audit_readme_authors.py` before any submission: checks
  every `arxiv_<id>` README row against the API (surname-set containment).

### Pitfalls

- Duplicate downloads: always check the target `papers/` dir first.
- Provenance: an arXiv ID can point to an unrelated paper. Verify the
  first-page title on downloaded PDFs before writing notes.
- pypdf text is noisy (headers, garbled math) — tell readers to ignore
  artifacts.
- Semantic Scholar 429s on bursts (1.2s sleep is polite; accept partial
  results and retry failed roots later).
- Verify before sending: grep the source tex for load-bearing facts
  before messaging — forward-only training, loss form, headline numbers.
- Peer corrections cut both ways: when a peer corrects a number, verify
  their correction against raw artifacts before patching.

---

## 4. Hydra Config / Recipe Patterns

### When to use

Creating a new training/eval variant in a Hydra-based repo, editing
configs, or launching a run needing multiple overrides. The recipe system
bundles several config changes: every variant gets a recipe that
overwrites the baseline.

### Defaults block ordering (the core rule)

    defaults:
      - hydra: no_output   # normal groups first
      - model: <baseline-model>
      - _self_             # then the baseline's own inline values
      - recipe: null       # recipe LAST -> overwrites everything above

Later entries override earlier ones. The recipe group comes after
`_self_`, so a selected recipe overrides ALL other settings. Never move
`recipe` before `_self_`.

### Recipe files (`configs/<group>/recipe/<name>.yaml`)

    # @package _global_
    defaults:
      - /data: <dataset>  # select groups via ABSOLUTE group paths
      - _self_
    experiment:
      name: <recipe-name>     # only experiment-specific overrides
    trainer:
      epochs: 200
    model:
      architecture:
        dim_embed: 264

- Put only what CHANGES vs the baseline in the recipe.
- Select datasets/groups via the defaults list (`- /<group>: <value>`),
  never by editing inline values.
- Abandoned recipes move to `recipe/historical/` — make a new recipe
  rather than resurrecting one.

### When a block gets its own group directory

Give a block its own group directory (`configs/<group>/<name>.yaml`) only
if at least one holds:

- The block will be reused across multiple configs/recipes.
- There will plausibly be multiple block-level options to switch between
  (different config schemas, not just different values).

Otherwise keep it inline in the baseline. Split it out when the second
variant actually appears, not preemptively — but if the schema will differ
between options, group it now.

### Launch & verify

    uv run <script> recipe=<recipe-name>
    # inspect the RESOLVED config without running:
    uv run <script> recipe=<recipe-name> --cfg job

### Validating the resolved config with Pydantic

Hydra hands you an untyped OmegaConf tree. Validate with nested Pydantic
models at the entry point, BEFORE any training/eval logic — catches typos,
legacy fields, and wrong-schema at startup instead of mid-run (matters
doubly with recipes: a bad recipe looks plausible).

1. **Strict base**: `extra="forbid"` rejects unknown keys. A legacy field
   in a recipe fails loudly instead of being silently ignored while the
   base default stays selected (the "plausible-looking but wrong run" trap).
2. **Public schema mirrors YAML layout**: one nested `StrictConfig` class
   per config block, nested as the public YAML is nested, so YAML/schema
   drift is visible at a glance. Optional fields carry explicit defaults.
3. **Single parse function**: `OmegaConf.to_container(config,
   resolve=True, throw_on_missing=True)` then
   `PublicConfig.model_validate(raw_config)`.
4. **Two-layer split**: `Public*Config` = resolved Hydra schema (matches
   YAML); `RunConfig` = internal config grouped by the runtime subsystem.
   Converter methods map public -> internal.
5. **Keep typed models through code** — dot-access only; `model_dump()`
   only at serialization boundaries.
6. **Conventions**: PEP 604 unions, `Literal[...]` for closed choices,
   `model_validator` for cross-field checks.

### Rules

- One recipe per variant; NEVER reconstruct a run by copying a saved run
  config (saved configs are snapshots, not sources of truth).
- `recipe: null` = "no recipe" (hydra's optional-group marker).
- The recipe filename IS the CLI value: `recipe=<name>` selects
  `recipe/<name>.yaml`.
- Set `experiment.name` to match the run-naming convention for greppable
  batches.
- Do not mix legacy config schemas — unknown legacy fields can be
  silently ignored while the base default stays selected.

---

## 5. Pandoc PDF Generation

### User-space install (no root, HPC login node)

1. Resolve latest versions from GitHub API:
   - pandoc: `curl -s https://api.github.com/repos/jgm/pandoc/releases/latest | grep browser_download_url.*linux-amd64`
   - tectonic: `curl -s https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest | grep browser_download_url.*x86_64-unknown-linux-gnu`
2. `curl -sL -o` the tarballs to /tmp, extract, `cp` binaries to
   `~/.local/bin`, `chmod +x`, then `hash -r`.
3. Why tectonic: single self-contained binary (~20 MB); fetches LaTeX
   packages on demand, caches in `~/.cache/Tectonic`. Avoids multi-GB
   TeX Live install.

### Compile

    pandoc report.md -o report.pdf --pdf-engine=tectonic

- YAML front matter (title/author/date) renders as the title block
  automatically.
- Citations: `--citeproc --bibliography=refs.bib` — pandoc builds the
  bibliography, no biber needed.
- Styling: thin margins `-V geometry:margin=2cm`; sans-serif body via
  header-includes `\renewcommand{\familydefault}{\sfdefault}` (Latin
  Modern Sans, bundled in tectonic). Math keeps its own serif font.
- `--template=<file>` for custom LaTeX templates; `--reference-doc=<docx>`
  for the office-format route.

### Markdown + LaTeX math

- Inline: `$x^2 + y^2 = z^2$`
- Display: `$$\mathcal{L}(\theta) = \sum_{i=1}^{n} \frac{1}{2}\|y_i - f(x_i;\theta)\|^2$$` (own lines)
- Full LaTeX works inside delimiters: `\frac \sum \sqrt \int \nabla`.
- Pipe tables render natively, no LaTeX needed.

### Verify the output (important pitfall)

- Check exit code AND inspect: `file out.pdf` should say "PDF document".
- Tectonic/pandoc emit COMPRESSED object streams: grepping raw bytes for
  `/Type /Page` returns 0 matches even on a valid PDF — false negative,
  NOT corruption. Don't chase it.
- Reliable byte-level checks: `data.rstrip().endswith(b'%%EOF')` and
  `b'startxref' in data`; plus `file` for the type.

### Pitfalls

- First compile needs internet (tectonic package fetch). Pre-warm
  `~/.cache/Tectonic` before running on offline compute nodes.
- Non-zero exit = LaTeX failed to compile — usually a math syntax error
  in the markdown; fix the math, not the toolchain.
- Only `$...$` / `$$...$$` delimiters; pandoc's markdown reader does not
  parse `\(\)` style.

---

## 6. Report Writing

### Structure

- YAML front matter: `title`, `author`, `date`.
- Numbered sections, equations where extractable, KEY QUESTION flags.
- Final section: relevance / conclusions.

### Citation integrity (mandatory for papers/reports)

1. Only cite papers DOWNLOADED into the project corpus (`papers/` — check
   `papers/README.md` for the authoritative list of downloaded IDs).
2. Take ALL citation metadata (title, authors, year, arXiv ID) from the
   corpus index/notes — never invent or guess entries, never cite from
   memory or web search alone.
3. Verify every `\cite` key resolves to a bib entry AND every bib entry
   corresponds to a downloaded paper: check both directions.
4. AUTHOR LISTS must be verified against the arXiv API before submission
   (first names are the classic hallucination — even corpus README entries
   can carry fabricated first names). Run `scripts/audit_readme_authors.py`;
   every entry must pass. A known arXiv typo may be whitelisted with a
   comment.
5. Hallucinated citations are a paper-blocking defect. NEVER silently drop
   a citation the text needs: download and index first, then cite with
   verified provenance. Mentioning a line of work by name without a key is
   only TEMPORARY while the download is pending — follow up and add the
   citation once indexed.

### Pitfalls

- `--pdf-engine=tectonic` is required — default engine is pdflatex, which
  may not be installed.
- Only `$...$` / `$$...$$` math delimiters.
- Verify end-to-end with a test file (inline + display math + table)
  compiling to a valid PDF.
