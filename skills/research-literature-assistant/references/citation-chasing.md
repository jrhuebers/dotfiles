# Citation chasing for literature discovery

Follow-the-citations is a first-class discovery channel (user-endorsed):
chase CITATIONS of corpus papers (who builds on them — catches brand-new
work before it shows in keyword searches) and REFERENCES (what they build on —
fills the foundation gaps). Worked example: qmc round 2 (2026-08-13) found
2511.10599 (cited BY both 2412.16416 and 2601.01072 — high-value signal) and
2503.21673 (triangular-transport intro) purely via chasing.

## Semantic Scholar API (the working channel, keyless)

- Citations: `https://api.semanticscholar.org/graph/v1/paper/arXiv:<id>/citations?fields=title,year,externalIds,abstract&limit=100`
- References: same with `/references` (response field: `citedPaper` instead of `citingPaper`).
- Use the bare arXiv ID (`arXiv:2601.01072`); the `externalIds.ArXiv` field on
  each hit gives the candidate's arXiv ID for dedup/download.
- Script: `scripts/chase_s2.py <aid>... [--direction citations|references]`.
- Rate limits: ~1.2s sleep per call is polite; bursts hit HTTP 429 — accept
  partial results, log which roots failed, retry those later. Do NOT treat a
  429 as the channel being down.

## OpenAlex (tested, do not use for this)

`https://api.openalex.org/works?filter=ids.arxiv:<id>` returned HTTP 400 on
the filter syntax in testing. Semantic Scholar covers the same need; don't
spend time debugging OpenAlex unless S2 goes away.

## Combining with fresh arXiv searches

- Run both in one discovery pass: 8-10 targeted arXiv boolean queries (1
  request/3s etiquette, `User-Agent` header) + S2 chases on the 4-6 most
  central corpus papers (citations for the newest roots — a paper 2 days old
  may have 0-1 cites; references for the foundational ones).
- Dedup candidates against the existing corpus IDs before reviewing.
- Prioritize: (a) papers cited BY multiple corpus papers (community
  convergence = high relevance), (b) papers that cite the corpus's reference
  implementation (the competitor's descendants), (c) fresh same-topic papers.
- Review the whole candidate list yourself before downloading; arXiv keyword
  hits are noisy (adjacent domains, e.g. RL-flow-matching papers surfacing in
  a QMC query) — curate hard, 10-15 adds max per round.

## Round checklist

1. `discover_qmc.py`-style pass (arXiv queries + chase) → candidate list file.
2. Curate to 10-15 papers; group by what each answers for the project.
3. `pipeline.py` download (staging dir → copy into project papers/).
4. Index README new pass section (grouped by theme).
5. Regenerate FIGURES.md (`figindex.py`).
6. Deliver one themed digest message per project.
7. Update the project state doc's literature map.
