---
name: research-literature-assistant
description: "Literature search + PDF curation for research-assistant."
version: 1.0.0
author: curator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [research, literature, arxiv, papers, agent-net]
    related_skills: [arxiv, agent-net]
---

# Research Literature Assistant

Role: search the literature for the fim, qmc, and gauge agents (and any future
research project), download PDFs into project-specific papers/ dirs, index
them, deep-read on request, and deliver pointers over agent-net.

## When to use

- User says "you are research-assistant" or asks to find papers for
  fim/qmc/gauge.
- A peer agent requests a deep read, a new search direction, or an
  implementation check ("does X have official code?").
- Periodic literature sweeps for the projects.

## Project papers layout (convention, user/peer-confirmed)

- `FIM/papers/`, `diffusion-qmc/papers/`, `gauge-graph-network/papers/`.
- Corpus format per arXiv paper (user decision 2026-08-13):
  - `arxiv_<id>.pdf` — ALWAYS downloaded (bare ID = latest version).
  - `arxiv_<id>.tex` — flattened via latexpand + verbatim-aware comment
    strip, version-stamped header; THE primary LLM-reading format (native
    math, ~1.13x pandoc-md tokens, often less). Derived artifact.
  - `src/<id>.tar.gz` — original e-print source tarball, canonical ground
    truth (figures live inside; flattening is zero-risk).
  - Non-arXiv journal/workshop papers: PDF only, no source. Author-page PDFs
    (book chapters, classic papers without arXiv): curl -skL from the
    author's site (expired certs are common), verify %PDF magic with `file`,
    name <author><year>_<slug>.pdf, README row marked PDF-only.
  - `.txt` (pypdf extraction) is RETIRED as a format — a few legacy .txt
    remain in the dirs; don't generate new ones.
- Index: `papers/README.md` table `| File | Paper | arXiv | Why it matters |`.
  gauge's README is organized in passes (Pass 1 / Pass 2 ...) — append new
  rows, don't rewrite.
- Deep-read status line: after any deep-read batch, add a line under the
  README table listing which papers have notes in notes/ (and which are in
  flight / index-only). Peers DO request deep-reads of papers already
  deep-read (happened twice in one day — 2511.10599 then 2511.04579) when
  the README doesn't show status; the line prevents duplicate dispatch.
- `papers/FIGURES.md` — regenerable caption index (label, image file +
  tarball path, full caption) via `figindex.py`; derived from the tex.
  The configured LLM is TEXT-ONLY: captions are the LLM-visible surface of
  figures. For actual image content (plot trends, diagrams) use the dots.ocr
  VLM on a GPU node (~1 min/page, venv ~/.venvs/dots-ocr) or a vision-capable
  provider if one is configured; TikZ-drawn figures have no image file.
- Deep-read notes: `papers/notes/<slug>-<arxiv-id>.md` in the style of gauge's
  notes (numbered sections, equations where extractable, KEY QUESTION flags,
  final "Relevance to <project>" section). FIM adopted the same pattern.
- `papers/` dirs are GITIGNORED in all three repos (PDFs/tex/tarballs are
  large artifacts); the agents own committing the staged removals.

## Corpus tooling (~/research-assistant/, scripts mirrored in this skill)

- `pipeline.py <outdir> <aid>...` — full corpus pipeline: fetch LATEST
  e-print (bare ID), safe-extract, find main tex (LARGEST \documentclass
  file — 2KB stubs that \input the real main.tex exist, e.g. 2208.07698),
  latexpand --empty-comments from the paper dir, verbatim-aware comment
  strip (latin1 sources decoded with errors=replace, e.g. 1502.06299), emit
  <id>.tex + <id>.pdf + src/<id>.tar.gz. Run into a staging dir, then copy
  artifacts into the project papers dir; clean the staging copy.
- `qa_corpus.py <papers_dir>` — post-pipeline QA (documentclass present,
  version stamp, sane comment density, pdf >= 50KB, tarball present).
- `figindex.py <papers_dir>...` — build FIGURES.md: brace-matched
  \caption{} extraction (handles multi-line + math captions), figure*
  environments, multi-image figures joined, tarball path prefix.
- `extract_text.py` (mirrored in this skill's scripts/) — pypdf extraction
  via `uv run --with pypdf`; still handy for quick greps.

## Workflow (first pass / new direction)

1. Register + intro: `agent-net-register research-assistant`,
   `agent-net-broadcast` a short intro, `agent-net-list` to see who is online.
   Bus mechanics live in the `agent-net` skill.
2. Ground in the projects: read each project README + research log first so
   pointers anchor to their actual state (e.g. fim: FT-hurts-R2; qmc:
   FM-ISQMC unbiased estimators; gauge: flat-vs-curved connections,
   holonomy supervision).
3. Search: arXiv API (see `arxiv` skill's `scripts/search_arxiv.py`). Batch
   queries per project, ~3-4s sleep between queries (rate limit), sort by
   submittedDate for freshness. Prefer targeted boolean queries over one
   generic query.
4. Curate: pick 5-15 papers per direction. The most valuable finds are often
   days/weeks old — e.g. 2608.11055 (Diffusion QMC) was published the day
   before the search found it.
5. Download: `curl -sL https://arxiv.org/pdf/<id> -o arxiv_<id>.pdf`, skip
   existing files. Always list the target papers/ dir first
   (search_files, target='files') to avoid dupes.
6. Extract text: `scripts/extract_text.py` via
   `uv run --with pypdf python3 extract_text.py <dir> ...` — system pdftotext
   is NOT installed on this cluster; the uv throwaway-env trick works
   anywhere uv exists.
7. Index: write/extend `papers/README.md` with the new rows.
8. Deliver: `agent-net-send <agent>` with concise highlights (2-4 per agent),
   each tied to their project state; point to README/notes paths. Direct
   messages for per-agent content; broadcast only for intros/announcements.
9. Re-arm the inbox listener — OPERATOR-APPROVED CONVENTION (2026-08-14,
   supersedes exit-based arming): run ONCE per session as a single background
   process with watch_patterns=['agent-net message'] and NO
   notify_on_complete:
   `while true; do agent-net-listen <name>; sleep 2; done`
   The loop auto-re-arms forever; the watch-strike limit is 50 (raised in the
   hermes source so repeated matches no longer auto-disable). Exit-based
   arming (one-shot listen + notify_on_complete + manual re-arm after every
   ping) is RETIRED — timeout exits were how listeners died silently. The
   heartbeat/watchdog layer still applies: agent-net-listen writes
   heartbeat/<name> each poll; a watchdog cron (agent-net-watch, every 2 min)
   flags any agent with unread mail but no live listener and leaves a re-arm
   nudge. At session start: check heartbeat/<name> freshness — a stale
   heartbeat with a live-looking loop means the old loop orphaned; kill it
   before starting the new one. A watchdog message in the inbox means mail is
   queued — re-arm and process.

## Deep reads (on request)

- Dispatch PARALLEL leaf subagents (delegate_task), one per paper, with: exact
  .txt path + size, project context + the question being answered, required
  output structure, note-file write instruction, and the title-vs-arXiv-ID
  verification step. Template: `references/deep-read-prompt.md`.
- Subagents write `notes/` files directly and return ~250-word summaries.
  Peers may request a QUICK NOTE (4-6 sections, no fact table) for utility
  papers (e.g. error-estimation/reporting tools) — honor the lighter format;
  the summary stays short too.
- REVIEW the returned summaries before forwarding — subagent claims are
  self-reports; spot-check surprising numbers against the .txt.
- Implementation questions ("official code?"): verify with the GitHub API
  (repo live, stars, last push) and check whether the arXiv version is
  superseded (e.g. ICON: arXiv 2304.07993 is an outdated preprint; the
  authoritative version is PNAS 10.1073/pnas.2310142120).

## Discovery rounds (fresh searches + citation chasing)

Two complementary channels, run together in a discovery round (see
`references/citation-chasing.md` for the full recipe + worked example):

1. Fresh arXiv API boolean queries (8-10 per round, 1 req/3s, UA header) —
   keep the query angles NEW each round; the first pass's queries go stale.
2. Citation chasing via the Semantic Scholar API (keyless, the working
   channel): `/paper/arXiv:<id>/citations` (who builds on it — catches
   brand-new work) and `/references` (its foundations). Script:
   `scripts/chase_s2.py`. OpenAlex's `ids.arxiv:` filter 400'd in testing —
   use S2, don't debug OpenAlex.

Chase the corpus's most central papers (the reference implementation, the
closest competitor, the newest additions). Papers cited BY multiple corpus
papers are the highest-value finds. Dedup against the corpus before reviewing;
curate hard (10-15 adds max per round); group the delivery by what each paper
answers for the project; then pipeline-download, index, regen FIGURES.md,
deliver one themed digest, and update the state doc.

## Read → view loop (user expectation — not optional)

The user expects real reading and an up-to-date view of each project, not PDF
hoarding ("do you actually read those papers you retrieve? and update your
view of the researchers' projects?"). The mechanism:

- Maintain a living state doc per project: `research-assistant/state/<project>-state.md`
  — goal, current state with EXACT numbers, open questions, literature map
  (paper → question → deep-read status), and a gap analysis (what the
  literature does NOT cover = their novelty). Template:
  `references/state-doc-template.md`.
- Ground it in the projects' research_log.md files — read them IN FULL
  (they are 10-45KB; the tail is the current state). If a project has no
  research log, say so and suggest the peer start one.
- Run a prioritized DEEP-READ QUEUE, not just on-demand reads: rank corpus
  papers by relevance to the project's open questions, dispatch in batches of
  3 parallel leaf subagents (delegation.max_concurrent_children=3), verify
  the notes, then deliver ONE consolidated themed summary per batch.
- Refresh the state doc's literature map the moment each note lands (status
  queued → in flight → ✓ with one-line takeaway), and fold peer corrections
  in with date + attribution.
- PEER EMPIRICAL RESULTS BELONG IN THE PAPER NOTES TOO: when a peer's
  reproduction/verification contradicts a paper's claims (e.g. gauge's GESC
  full-config reproduction: the paper's ablation gap does NOT reproduce at
  matched settings), add a dated ⚠️ REPRODUCTION UPDATE addendum right under
  the note's provenance header — anyone reading the paper note later sees the
  contradiction up front, not just in the state doc. Same for peer
  harness-verification of a deep-read (fim confirmed beam 50/T 0.1 but found
  NO best-of-beam selection → harness numbers are a LOWER BOUND): record it
  in the note/protocol doc with their code's file:line, and update the state
  doc's literature-map row.
- When a peer REVISES an earlier empirical reading, revise the addendum too
  with a dated "REVISED" marker — the note must track the latest state, not
  the first report. (GESC again: the initial "free phases converge to exactly
  zero" was wrong — the released implementation's phase channel is INERT:
  no gradient reaches the phase parameter, a phase_init 1.0/2.0 rad positive
  control is unchanged after 300ep. "Never trained" ≠ "collapsed", and the
  distinction matters for how the paper frames the result.)
- Deep-reads are the currency of this loop: after enough of them, pointers
  become reviews ("your direction is open territory" + the three papers that
  prove it).

## Apples-to-apples protocol mapping (peer requests)

When a peer agent needs to judge their results against a paper's published
numbers (e.g. fim's 5-seed ODEBench vs FIM-ODE 1's single-run table), the
deliverable is a protocol doc in the peer's papers/notes/, built like this:

1. Deep-read the paper first (notes file), extracting the EXACT eval spec:
   systems/subset, grid, corruption, context construction, tasks, metric
   definition, denominator, seeds.
2. Read the peer's eval code: entry point (pyproject [project.scripts]),
   config dataclass, data loading, corruption config, metric/stat classes,
   reporting/aggregation. Build a mapping table `Paper | Codebase (file:line)
   | Status`.
3. Enumerate the DELTAS explicitly (grid resolution, solver, pooling,
   denominator, seeds) — usually 2-3 real ones; label everything else
   "exact match". Propose one-line fixes with file:line.
4. Anchor: pull the peer's actual result artifacts (r2_summary md, per-seed
   r2.json) and diff against the paper's published table. Residual |delta| in
   the 1-2pt range = harnesses compatible; bigger = protocol divergence.
5. Verify denominators arithmetically from raw artifacts (e.g. 92.9% = 260/280
   pooled => 46/56/20 per-seed trajectories for dim 1/2/3). Do NOT trust
   memory or paper prose for per-dim splits — check the data.
6. Deliverable contents: mapping table, deltas + fixes, exact commands (one
   invocation often covers all configs), an anchor table vs the paper, and a
   re-run checklist. Send the peer a tight summary; the doc carries the detail.

Worked example: `references/protocol-mapping-odebench.md`.

## Bibliographic metadata: verify, never invent

Every author/title/ID in READMEs, notes, and bibs must come from the arXiv API
(or S2/Crossref for non-arXiv) — NEVER filled in from memory. This session
produced a real hallucination: BuNN (2405.15540) got "Hansen, Gebhart" (the
SheafNN 2012.06333 authors) instead of Bamberger, Barbero, Dong, Bronstein — a
memory conflation of two papers from the same search. Peers' citation lists
carry the same failure mode: Sol's "no arXiv ID in hand, please search"
entries, and a "Kenney et al. 2021 ICLR tensor message passing" that does not
exist on OpenReview, arXiv, or S2.

Rules:
- Author lists: read from export.arxiv.org (batched id_list), never memory.
  Expand "et al." rows to API-verified full lists; last-name-only is the
  README convention.
- Peer-supplied arXiv IDs can be WRONG (gauge's "GNNSync 2307.11339" was
  Chrion, an unrelated systems paper) — verify the title via the API before
  fetching; search by title if the ID fails.
- Peer download requests may already be SATISFIED: check the corpus + README
  before searching (gauge's CycleNet request was already fetched via Sol's
  eval — 2311.14333; fim's ODEFormer was in corpus since pass 1). Reply with
  the existing path + the wrong-ID evidence instead of re-fetching; run the
  peer's suggested search string once to prove there is no other candidate.
- Ambiguous acronyms: resolve by author + title, not the acronym (two MGCs
  exist: MagNet-family "Magnetic Graph Convolutional Networks" and "MGC: A
  Complex-Valued Graph Convolutional Network" — different papers, both real).
- Unresolvable citations: say so explicitly, flag as likely-hallucinated,
  offer closest REAL alternatives (verified), and tell the peer not to cite
  it without a real source.
- API typos exist: arXiv lists "Michael Permultter" for 2209.00546 (real
  name Perlmutter) — whitelist known cases in the audit script, don't "fix"
  the README to match the typo.
- Run scripts/audit_readme_authors.py before any submission: checks every
  arxiv_<id> README row against the API (surname-set containment) and prints
  mismatches. Batch gotcha: arXiv id_list queries need max_results=100 or
  only 10 entries come back.

## External-model library evaluations (Sol / Opus pattern)

Peers/operator may forward another model's review of the corpus with a
recommended-papers list (GPT-5.6 Sol and Claude Opus 5 both did this in one
session). Process it as a VERIFIED fetch list, not a trust list:

- Verify EVERY cited arXiv ID against the API before fetching; reviewer IDs
  can be wrong (Opus's Di Giovanni over-squashing was cited as 2202.02941,
  actually a gravitational-wave paper; real ID 2302.02941). Search by title
  when an ID fails; report the correction with evidence.
- Titles quoted from memory are loose — match by author + topic, confirm the
  real title via API (Sol's "Cycle holonomy ... via twisted Laplacian
  spectra" is actually 2604.19682 "Cycle holonomy captures higher-order
  compatibility constraints in remote synchronization").
- Honor scoping flags: "optional" items get fetched but marked optional in
  the README; "don't add more X" is respected — no additions in that line
  (Sol: no more magnetic-Laplacian papers).
- Books/journals without arXiv = citation-only bib entries, no PDF chase
  (Creutz 1983, Kavitha et al. 2009 min-cycle-basis survey, Barrachina 2023
  JSP — all cited as-is). Author-page PDFs: curl -skL (academic sites often
  have expired certs), verify %PDF magic via `file`, name
  <author><year>_<slug>.pdf, README row marked PDF-only (Chung 2005 case).
- Map each addition to the evaluator's gap list in the README section
  header, and flag the highest-stakes gaps (benchmark-critique papers like
  Platonov 2302.11640) so the peer prioritizes reading them first.
- Forward the evaluation VERBATIM to the peer as well (wrapped in
  BEGIN/END markers), not just your processed summary — the original
  reasoning (why each gap costs review points) is what the peer needs for
  related-work/review-prep. Deliver the summary immediately, offer the
  verbatim text, and send it on request (the operator asked for it twice:
  "message gauge about this", "also send it sol's stuff"). Include
  verification notes on any quoted titles/IDs that differed from reality.

## Baseline completeness for project papers (own-paper benchmark rule)

When the project's OWN published paper (or its central reference) is in the
corpus, the methods it benchmarks against belong in the library too — a
reviewer's first question is whether the comparison methods are known. This
came from fim's request to add FIM-ODE 1's baselines (7 methods: GP-DNF,
BNeuralODE, Neural ODE, ODE2VAE, LatentSDE, GPODE, npODE + ODEFormer).

Recipe:
1. Extract the paper's own `bibliography.bib` from `src/<id>.tar.gz` — the
   GROUND TRUTH for exact titles/authors of every baseline (keys like
   `chen2018neural` map to full entries; no guessing needed).
2. Verify every baseline ID against the arXiv API (batch id_list) — the bib
   gives titles; the API gives IDs/versions. Papers without arXiv (books,
   journals) stay citation-only.
3. Fetch all through the pipeline, index in a dedicated README section
   ("<Paper> benchmark baselines") with API-verified metadata, and note each
   baseline's role (primary / neural per-dataset / GP per-dataset).
4. Ask the peer which baselines are RUNNABLE in their harness vs cite-only:
   fim could run only ODEFormer + GPODE (`model_type odeformer/gpode` in the
   odebench CLI); the other 5 would be paper-reported numbers or need
   porting. That split decides deep-read priorities — protocol deep-reads for
   the cite-only ones when the peer builds comparison tables.
5. Team self-citations in the bib (e.g. berghaus2024foundation) — OFFER to
   fetch, don't fetch unprompted; peers may want them "on the shelf".

## Pitfalls

- Duplicate downloads: always check the target papers/ dir first.
- Provenance: an arXiv ID can point to an unrelated paper (gauge had a
  2012.06233-vs-06333 mixup). Always verify the first-page title — including
  on downloaded PDFs, before writing notes.
- Extraction artifacts: pypdf text is noisy (headers, garbled math) — tell
  subagents to ignore artifacts.
- Don't edit other agents' domain skills or repo code; the papers/ dirs are
  the shared curation space.
- Message hygiene: long agent-net messages are fine (they are files), but
  keep the highlights section tight; full detail lives in the notes files.
- When a peer contributes design ideas (e.g. fim's anti-degeneracy guard,
  plumbing reuse), fold them into the shared design/notes doc with
  attribution — do not only mention them in the reply.
- VERIFY BEFORE SEND: subagent deep-read claims are self-reports. Grep the
  source tex for the load-bearing facts before messaging a peer — e.g.
  forward-only training: `grep -i 'backward|reverse|time.reversal'` must be
  empty; loss form: grep the equation; headline numbers: grep the table
  (row/column semantics in raw tex are easy to misread — check the note or
  the rendered table). Never forward unverified numbers.
- Peer corrections cut both ways: when a peer corrects a number in a doc you
  wrote, verify their correction against raw artifacts before patching
  (fim's per-dim split 46/56/20 was right; my 220/260/130 draft was wrong —
  summary-md arithmetic proved it).
- Citation chasing: Semantic Scholar 429s on bursts (1.2s sleep is polite;
  accept partial results and retry failed roots later). OpenAlex ids.arxiv
  filter 400s — S2 is the channel, don't burn time on OpenAlex.
- Deep-read queue: batches of 3 parallel subagents max (the configured
  max_concurrent_children); batch 2 only after batch 1's results re-enter.
  Deliver one consolidated themed message per batch, not per paper.
- Hermes blocks oversized inline terminal one-liners (nested quotes, loops,
  heredocs) — write a script file first, then run it; do not retry inline.
- Gitignore housekeeping: to untrack already-committed papers use
  `git rm -r --cached papers/` (files stay on disk), append `papers/` to
  .gitignore, verify with `git check-ignore`, and NEVER touch peers' other
  uncommitted work (check `git status --short | grep -v papers/`); ping the
  repo owners on agent-net so the staged removals don't surprise them.

## Related

- `arxiv` skill — search/retrieval mechanics, BibTeX, Semantic Scholar.
- `references/protocol-mapping-odebench.md` — worked protocol-mapping example
  (FIM-ODE 1 ODEBench case: 10-of-12 match, two deltas, anchor arithmetic).
- `references/citation-chasing.md` — S2 citation/reference chase recipe,
  OpenAlex caveat, round checklist. `scripts/chase_s2.py` — the chase tool.
- `references/venue-intel-openreview.md` — workshop/venue discovery via the
  OpenReview API (deadlines live in the Submission invitation's TOP-LEVEL
  duedate; id= not prefix=; /notes/search for title/author existence checks;
  NeurIPS 2026 workshop-deadline worked example).
- `scripts/audit_readme_authors.py` — bibliographic verification: every
  arxiv_<id> README row vs the arXiv API (see "Bibliographic metadata").
- `references/state-doc-template.md` — per-project living state doc structure
  (the read→view loop's backbone).
- `agent-net` / `agent-net-messaging` — bus mechanics, listener loop, etiquette.
- `start-slurm-job` — if literature sweeps ever need allocations.
