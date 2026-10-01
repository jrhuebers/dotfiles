# Machine registry

This file is the shared map of the computers and recurring compute
environments used for work, personal tasks, clusters, and services. Read it
before assuming where another agent, file, service, or job is running.

## How to maintain this registry

Add one section for every persistent computer or recurring remote environment
that is part of the working ensemble. Include machines even when they are
reached through a VPN, bastion, reverse tunnel, or another host.

For each entry, record:

- what kind of machine or environment it is and what it is used for;
- hardware when it matters: architecture, CPU model and core count, RAM,
  storage, GPU, and whether the resources are dedicated or shared;
- operating system and version, including whether it is a GUI workstation,
  headless server, login host, or compute host;
- the complete public SSH key or keys used by that machine, with a short label
  explaining the key's purpose; and
- comments about VPN requirements, bastions, tunnels, cluster policy, unusual
  access patterns, or anything an agent should know before acting there.

Use facts verified on the machine. Do not guess hardware or OS details; write
`Not recorded` when they have not been checked yet. Update an entry when a
machine is rebuilt, upgraded, or repurposed. This registry is deliberately
human-readable Markdown rather than a database or strict configuration file.

Public SSH keys may be recorded here in full. They are not secrets and are
useful when an agent needs to install or recognize a machine's key. Never
record private keys, passphrases, tokens, passwords, or secret environment
values. Distinguish a machine's login/authentication key from an SSH host key
when both are present.

A Slurm allocation or an SSH session into an individual Slurm job is usually
an execution context, not a persistent machine. Record the relevant cluster
under its own section and describe job-level access, ephemeral nodes, and
resource constraints in **Comments**. Add a separate entry only for a stable
node or environment that agents routinely address as its own system.

Every entry should use this shape, adding or removing hardware lines as
appropriate:

```markdown
## Name

- **Kind:**
- **Hardware:**
  - **Architecture:**
  - **CPU:**
  - **RAM:**
  - **Storage:**
  - **GPU:**
- **Operating system:**
- **Main use:**
- **Public SSH keys:**
  - **Purpose/label:** `ssh-ed25519 AAAA... comment`
- **Comments:**
  -
```

## Current machines and environments

## Oracle

- **Kind:** Personal headless server; cloud VM
- **Hardware:**
  - **Architecture:** ARM64 (`aarch64`)
  - **CPU:** Not recorded
  - **RAM:** Approximately 5.8 GiB
  - **Storage:** Oracle Cloud boot/block storage; exact allocation not recorded
  - **GPU:** None
- **Operating system:** Ubuntu 26.04 LTS
- **Main use:** Always-on personal server, Syncthing hub for the Obsidian
  vaults, SSH gateway, reverse-tunnel endpoint, and selected personal
  services.
- **Public SSH keys:**
  - **Outbound machine key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEQXQAx5TDV2v5BqqRXRLa9FIcKQix+cae6Xyx1y9FZz oracle`
- **Comments:**
  - The Syncthing vault folder is `/home/ubuntu/vaults/`; see
    [`obsidian-sync.md`](obsidian-sync.md).
  - Loopback-only reverse tunnels provide access to the EPFL LTS2 frontend
    and the RCP environment when direct access is unavailable.
  - Treat this as a server, not as a shared cluster login or compute host.

## X1 Carbon

## EPFL M1 MacBook Pro

## EPFL LTS2 frontend

## RCP environment

## TU Dortmund / LAMARR cluster endpoints
