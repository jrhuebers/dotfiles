# Living project state doc — template

Purpose: the user expects the research-assistant to actually READ the papers it
retrieves and to keep an up-to-date VIEW of each project's work — not just to
hoard PDFs. The state doc is that view, and it must be refreshed as deep-reads
and peer messages land. One file per project: `research-assistant/state/<project>-state.md`.
Sources: the project's research_log.md (read it IN FULL before writing),
README, agent-net messages, deep-read notes.

## Structure

```markdown
# <PROJECT> — project state + literature map (living doc)

Updated <date> (research-assistant; sources: ...). Refresh after every
<project> message/deep-read. (NOTE if the project has no research_log.md —
suggest the peer start one; state tracking is thin without it.)

## Goal & approach
<one paragraph: what they build, how, the reference paper/checkpoint>

## Current state (<date>)
- <dated bullet facts with EXACT numbers: benchmark results, comparisons,
  corrections/invalidations, current best configuration>
- <mark corrections clearly: e.g. SU(2) failure was a torch regression>

## Open questions / next steps
<numbered list, from their research log / messages — the questions deep-reads
should target>

## Literature map (corpus → question)
| Paper | Addresses | Note |
|---|---|---|
| <id> <short title> | <what question it answers for THEM> | <note-file.md ✓ | (index) | DEEP-READ QUEUED/IN FLIGHT> |

## Gap analysis (what literature does NOT cover = their novelty)
<bullet list: verified gaps (e.g. "no published per-graph learned phases with
a YM regularizer"), so pointers can be explicit about what is open territory>
```

## Maintenance rules

- Update the literature map row the moment a deep-read note lands (status:
  queued → in flight → note ✓ with one-line takeaway).
- Fold peer corrections/verifications into the map + current state with date
  and attribution (e.g. "fim-verified 2026-08-13: harness ODEFormer = first-
  valid decode → LOWER BOUND vs paper").
- The gap analysis is the most valuable section: it is what makes the
  research-assistant useful as a reviewer (telling a peer "this direction is
  open" is a pointer; telling them "this is your novelty" is a service).
- Re-read the project's research_log.md on every significant session — their
  state moves fast; the doc must not drift.
