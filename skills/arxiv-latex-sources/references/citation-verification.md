# Citation & metadata verification — case log and rules

Context: literature-curation sessions (2026-08) where README indexes, bib
entries, and paper notes carried author/title/ID metadata. Two incidents made
verification mandatory: (a) a fabricated author list written from memory, and
(b) wrong arXiv IDs supplied by three different external models in the same
week. Every one was caught by the same cheap check: query the arXiv API and
compare title + authors, never trust the ID or the name string.

## The failure modes (all real, all caught)

| Claimed | Reality (API-verified) | Failure class |
|---|---|---|
| 2405.15540 = 'Hansen, Gebhart' (BuNN) | Bamberger, Barbero, Dong, Bronstein | authors filled from memory (conflated with SheafNN 2012.06333) |
| 2307.11339 = 'Graph Neural Networks from Pairwise Connection Data' | Chrion (CPU/GPU inference optimization) | wrong ID, title doesn't exist |
| 2402.01679 = CycleNet | STICKERCONV (multimodal empathetic responses NLP) | wrong ID |
| 2202.02941 = over-squashing paper | Revisiting the ringdown of GW150914 (gravitational waves) | year-prefix swap; real ID 2302.02941 |
| 2203.08742 = stochastic interpolants | Cactus Doodles (math art) | wrong ID; real ID 2209.15571 |
| 'CycleNet graph' search | only 2311.14333 exists in GNN/cycle-basis space | negative result: one search settles it |

Pattern: confident-but-plausible IDs that are real arXiv IDs — of the WRONG
paper. Title+author verification is the only defense; the ID alone proves
nothing.

## The verification workflow

1. Batch-verify candidate IDs BEFORE fetching:
   `https://export.arxiv.org/api/query?id_list=id1,id2,...&max_results=100`
   — **max_results=100 is required**; the default (10) silently drops rows,
   which looks like "no API entry" for ~half a batch.
2. Compare title (normalized whitespace) AND surname sets against what you
   were given / what's in the README row. Flag: extra README surnames, missing
   API surnames, or a fully different title.
3. If the provider (agent/model) says "search for it": search by title phrase
   first (`ti:"..."`), then by distinctive content terms; report the single
   best match with its ID, and say explicitly when nothing matches (Kenney
   tensor message passing ICLR 2021: no match anywhere → likely hallucinated,
   tell the requester not to cite it without a first name/exact title).
4. For benchmark-baseline metadata: extract the paper's own
   `bibliography.bib` from `src/<id>.tar.gz` — exact titles, no guessing.
5. Keep a known-API-typo exception list in the audit script (e.g. 2209.00546
   lists 'Permultter' for Michael Perlmutter) so reruns don't re-flag.

## Index author conventions (adopted)

- README rows: full surname list from the API, comma-separated; expand `et al.`
  to the full API list (13 rows expanded in one pass); never abbreviate to an
  unverifiable form.
- Non-arXiv papers (journal/workshop): mark "PDF-only, no arXiv source" and
  give the journal citation (e.g. Chung 2005 Ann. Comb. 9:1-19; Ko UAI 2023
  PMLR 216); fetch the author's page PDF when reachable (-k for expired certs).
- Re-run `scripts/audit_readme_authors.py` after ANY corpus addition and
  before any submission/bib export.

## Cross-checking bibliographies from external evaluations

When a model evaluates the corpus and names papers (Sol/Opus-style reviews):
fetch every named paper with the same API verification, map each to the gap it
addresses in the index, deliver the VERBATIM evaluation text to the requesting
agent (summaries lose the argumentation), and record verification notes where
the evaluation's quotes diverged from reality (e.g. Sol's Torres-Hugas title
vs the actual arXiv title — content matched, so accept after noting).
