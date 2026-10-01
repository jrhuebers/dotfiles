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
- a Syncthing device ID when the user explicitly requests that it be recorded;
  otherwise keep device IDs out of this repository (see
  [`obsidian-sync.md`](obsidian-sync.md)); and
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

- **Kind:** EPFL-managed personal GUI workstation
- **Hardware:** Apple MacBook Pro (MacBookPro18,3)
  - **Architecture:** ARM64 (`arm64`)
  - **CPU:** Apple M1 Pro
  - **RAM:** 16 GiB
  - **Storage:** Not recorded
  - **GPU:** Integrated Apple M1 Pro GPU
- **Operating system:** macOS 15.8.1
- **Main use:** Work and research workstation; Syncthing client for Obsidian vaults.
- **Public SSH keys:** Not recorded here.
- **Syncthing device ID:** `QS6X2WE-TEKAYMX-GAX7UZN-L22L6AD-5KYV6ZH-HJ3K5PS-5FDILO4-BQBZPAY`
- **Comments:** Syncs the Oracle `/home/ubuntu/vaults/` folder to `~/vaults/`; see [`obsidian-sync.md`](obsidian-sync.md). The Syncthing GUI is loopback-only.

## EPFL LTS2 frontend (`stivm0163`)

- **Kind:** Shared cluster login/access host; VMware guest
- **Hardware:**
  - **Architecture:** x86_64
  - **CPU:** Intel Xeon Gold 6248 @ 2.50GHz; 2 vCPUs visible
  - **RAM:** Approximately 7.7 GiB
  - **Storage:** 39 GiB root filesystem; shared NAS-backed `/nfs_home` (8.0 TiB filesystem visible)
  - **GPU:** VMware SVGA II virtual display adapter; no compute GPU
- **Operating system:** Ubuntu 24.04.5 LTS
- **Main use:** Shared EPFL LTS2 Slurm frontend for cluster access, development, and job submission.
- **Public SSH keys:**
  - **User login/authentication key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAA3hpVrw0wZS1ibG4eUdrfMmspZaqdCVuIc3mr83Z0t huebers@stivm0163`
  - **GitHub dotfiles access key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICCBkOjad5k/WS8f8UFfSpm5+vIj5C71Y4r1sI7fTmO8 github-dotfiles-stivm0163-20260916`
  - **Oracle reverse-tunnel key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDVWTRtXXMuZgFUditg+mIglCTd67qLc3L1HRah+kPC/ lts2-to-oracle-tunnel`
- **Comments:**
  - This is shared infrastructure, not a compute node. Submit substantial or intensive workloads through Slurm rather than running them on the frontend.
  - User-local software belongs under `~/.local`; persistent home storage is shared through `/nfs_home`.

## RCP access host (`haas034.ds-a3-r02.cct.rcp.epfl.ch`)

- **Kind:** Shared cluster login/access host
- **Hardware:**
  - **Architecture:** x86_64
  - **CPU:** AMD EPYC 9124 16-Core Processor; 32 logical CPUs visible
  - **RAM:** Approximately 251.5 GiB
  - **Storage:** 100 GiB root filesystem; persistent home on NAS-backed storage
  - **GPU:** ASPEED Graphics Family management adapter; no compute GPU
- **Operating system:** Ubuntu 24.04.4 LTS
- **Main use:** RCP SSH access host for cluster work; submit compute workloads through approved site workflows rather than running them here.
- **Public SSH keys:**
  - **Outbound user-managed SSH key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMKEjunklnnW0o9mOQcfmCCKYbHsSSjcq+XWyO6IUbKb`
- **Comments:**
  - Reach it through the SSH alias `rcp` and the RCP jump host; the backend hostname is the name above.
  - This is shared infrastructure. Do not modify shared services or run heavy workloads on the access host.
  - No Slurm client was present when recorded; verify scheduler tooling before using Slurm commands.
  - User-local software belongs under `~/.local`; no non-interactive sudo permission is available.


## TU Dortmund / LAMARR cluster endpoints
