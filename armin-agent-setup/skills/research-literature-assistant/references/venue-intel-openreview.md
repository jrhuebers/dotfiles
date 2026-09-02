# Venue / workshop intelligence via the OpenReview API

Pattern for answering "where should we submit / what's the deadline / does
paper X exist at venue Y" without scraping websites. Worked 2026-08-13 for
gauge's NeurIPS 2026 workshop paper phase.

## Endpoints that work (api2.openreview.net)

- List all workshop groups for a conference:
  `GET /groups?prefix=NeurIPS.cc/2026/Workshop`
  → `groups[].id` (short workshop IDs, e.g. `NeurReps_Proceedings`, `GDDL`),
  `groups[].content.title.value`, `groups[].content.website.value`.
- Submission deadline: `GET /invitations?id=NeurIPS.cc/2026/Workshop/<ID>/-/Submission`
  → the deadline is the invitation's **TOP-LEVEL `duedate` field** (epoch ms),
  NOT a content field. `cdate` = submissions open, `expdate` = hard close.
  The `prefix=` param 400s on this endpoint — use `id=` (exact match).
  (A first attempt that read `content.duedate` returned "due ?" for every
  workshop — the field simply isn't in content.)
- Existence checks (hallucinated-citation screening):
  `GET /notes/search?term=<query>&group=ICLR.cc/2021/Conference&content=all&limit=20`
  → empty `notes` = no such title/author at that venue. Used to prove
  "Kenney tensor message passing ICLR 2021" does not exist.
- `GET /groups?id=NeurIPS.cc/2026/Workshop/<ID>` → content keys include
  `website`, `instructions`, `location`, `start_date` — not deadlines.

## arXiv API quirks (adjacent, hit in the same session)

- `id_list=` batch queries return at most 10 entries unless
  `&max_results=100` is appended — without it, most IDs come back missing.
- API typos exist: 2209.00546 lists "Michael Permultter" (real: Michael
  Perlmutter). Whitelist in audit scripts; don't propagate the typo.

## Worked example — NeurIPS 2026 workshops (2026-08-13)

- Official announcement: blog.neurips.cc (102 workshops: 48 Sydney / 28 Paris
  / 26 Atlanta, Dec 11-13 2026); the conference site's workshop list page
  404'd, the blog post + OpenReview were the sources.
- Enrichment: sites carry CfP detail (page limits, blind policy, tracks) but
  deadlines were OpenReview-authoritative (site vs OpenReview can differ by a
  day — AoE vs UTC). E.g. NeurReps site "Aug 24 AoE" = OpenReview due
  2026-08-25 UTC.
- Delivery shape that worked: one reference file in the requester's papers/
  dir (workshop table per target topic: venue, deadline, notes) + a compact
  agent-net digest with the top picks and the timing warning (main-track
  deadlines already passed → workshops are the live target, most due
  Aug 29-30).
- Non-arXiv classics (e.g. Chung 2005 book chapter): fetch the author-hosted
  PDF (UCSD cert is expired — curl -k for a public PDF is fine) and record
  the canonical journal citation (Ann. Comb. 9(1):1-19, 2005) in the README
  row; PDF-only, no tex/src.
