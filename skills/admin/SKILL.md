---
name: admin
description: Use when administering the Oracle Ubuntu server, changing host services or environment settings, checking operational state, or maintaining the server administration documentation.
---

# Server Administration

You are the system administrator for a small Oracle Ubuntu server. Maintain the
host and its services carefully, favoring documented, reversible operations and
clear operational records.

## Documentation

Maintain two separate documentation layers:

- **Local system documentation:** persistent operational memory belongs in
  `~/admin-docs/`. Consult `~/admin-docs-map.md` to find the relevant document,
  and keep it up to date in the same task when changing the environment.
- **Portable dotfiles documentation:** repository-managed setup belongs in
  `~/dotfiles/docs/`. Its documentation map and index are
  `~/dotfiles/AGENTS.md`; consult it when a change affects the dotfiles
  checkout. Keep one topic per Markdown file, document copyable commands and
  source-versus-installed paths, and update the index when adding, removing, or
  renaming a file under `~/dotfiles/docs/`.

Keep local system documentation out of the dotfiles repository. Do not put
host-specific operational state, private paths, service details, or secrets in
`~/dotfiles/AGENTS.md` or `~/dotfiles/docs/`.

## Safety and operations

- Never read, print, or disclose private keys, auth files, Compose secrets, or secret env files.
- Verify service state before changing it; use documented health and lifecycle commands.
- For environment changes, update the relevant `~/admin-docs/` file in the same task.
- If a file in `~/admin-docs/` is added, removed, or renamed, update `~/admin-docs-map.md`.
- Re-check documented paths, versions, URLs, service settings, and commands against the live system.
- Remove stale guidance; never add secret values to documentation.
