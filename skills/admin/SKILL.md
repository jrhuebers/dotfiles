---
name: admin
description: TEMPLATE — complete this skill during machine provisioning with the local machine's verified administration facts. Do not use the uncompleted template as an operational skill.
---

# [MACHINE NAME] Administration

> **Provisioning template.** Copy this file into the target agent's active
> skills directory, replace every bracketed field with verified facts about
> that machine, remove inapplicable sections, and add machine-specific
> procedures. Keep the completed copy local; do not copy its host-specific
> details back into the dotfiles repository.

## Established machine facts

- **Machine profile:** [shared cluster login host / shared compute host /
  personal Linux GUI device / personal macOS device / personal headless server]
- **Hostname and purpose:** [verified hostname and short role]
- **Operating system and version:** [verified]
- **Architecture / virtualization:** [verified if relevant]
- **Service manager:** [for example, systemd / launchd / none]
- **Package manager and privilege boundary:** [verified package manager,
  whether sudo is available, and approval requirements]
- **Home and persistent-storage locations:** [non-secret local paths]
- **Network boundaries:** [VPN, proxy, outbound-access, or firewall facts that
  affect administration]
- **Local administration documentation:** [path to the local admin-doc map and
  the relevant documents]

## Role-specific boundaries

### [Keep and complete for a shared cluster host; otherwise remove]

- **Cluster role:** [login/access host, compute host, controller, or other —
  verified, not inferred from Slurm client commands]
- **Scheduler policy:** [how work is submitted, permitted read-only checks,
  and prohibited scheduler or other-user actions]
- **Service-change policy:** [authorization and documented procedure required
  before system-wide changes]
- **Package policy:** [user-local versus system package rules]

### [Keep and complete for a personal device or server; otherwise remove]

- **Ownership and backup policy:** [who owns the machine and what to back up
  before changing it]
- **Desktop/headless status:** [GUI and desktop environment, or explicitly
  headless]
- **Platform procedures:** [approved package, service, and update mechanisms]
- **Remote-cluster access:** [whether SSH/Slurm use is client-side only]

## Routine administration procedure

Before making a change:

1. Verify the relevant current state and consult the local administration
   documentation above.
2. Confirm that the requested operation is allowed for this machine and role.
3. Record the exact backup, rollback, verification, and restart procedure for
   the affected service or configuration.
4. Obtain explicit approval for destructive, privileged, security-sensitive,
   or externally visible changes.

After making a change:

1. Verify the intended service, configuration, or package state.
2. Update the local administration documentation and its map with durable
   machine-specific knowledge.
3. Update portable `~/dotfiles/docs/` only when the repository-managed setup
   changed; never add this machine's private paths, identifiers, operational
   state, or secrets there.

## Safety rules

- Never read, print, commit, or disclose private keys, tokens, passwords,
  authentication files, Compose secrets, or secret environment files.
- Prefer backups, dry runs, targeted operations, and narrow rollbacks over
  broad cleanup or removal commands.
- Re-check paths, versions, URLs, package names, network requirements, and
  service state instead of relying on assumptions or stale notes.
