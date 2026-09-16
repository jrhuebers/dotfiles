# Deep-read subagent prompt template

Use with delegate_task (parallel batch, one leaf subagent per paper). Every
field below has proven necessary — the two things subagents get wrong when
omitted are: (a) not reading the FULL text, (b) writing a vague summary
instead of the structured note. Include the note-format spec verbatim.

## Per-task context block

- Project: <name> (<absolute repo path>) — 2-4 lines of the project's actual
  state from its README/research log, so the relevance verdict lands (e.g.
  gauge: per-graph U(1) connections, flat connections are gauge-trivial,
  curvature only under supervised holonomy; fim: per-system torchode
  fine-tuning HURTS ODEBench R2 vs base).
- Text file: pypdf extraction of the arXiv PDF — math renders poorly, header
  noise present; ignore artifacts. State the file size and tell them to read
  in chunks with read_file until the end.
- WARNING: verify the first-page title matches the expected paper before
  writing notes (arXiv IDs have been mixed up before — gauge had a
  2012.06233-vs-06333 swap).

## Goal block

"Deep-read arXiv <id> (<Title>, <authors>) from <abs path to .txt> (read the
FULL file in chunks with read_file; ~N KB). Then WRITE a literature-notes
file to <project>/papers/notes/<slug>-<id>.md using write_file, in the style
of the existing notes in that folder (see <project>/papers/notes/<example>.md:
numbered sections, equations where extractable, 'KEY QUESTION' flags,
concrete mechanism details, final section 'Relevance to <project>').
Cover: <1-7 numbered questions specific to this paper and the request>.
Then print a condensed summary (~250 words) with the most important facts and
your relevance assessment."

## Question set that has worked (adapt per paper)

1. Exact method/architecture — parameterization, where the key object enters.
2. Learned per graph, per graph-SIGNAL, or fixed? (The per-graph-vs-per-signal
   distinction recurs across all three projects — always ask explicitly.)
3. Relation to the project's core baselines/mechanisms.
4. Datasets + results vs baselines (exact numbers).
5. Theoretical claims (expressivity, spectral properties, limits).
6. Limitations and open problems.
7. Relevance section: what transfers, what would be a fair comparison, what
   experiment it suggests.

## Review before forwarding

- Subagent summaries are self-reports: spot-check any surprising number
  against the .txt before relaying to the requesting agent.
- Verify the note file exists and is non-trivial (read it back).
- Attribute peer additions when folding them into shared docs.
