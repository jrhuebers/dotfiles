# Device profiles

Use this page as the **entry point when setting up a machine**. Identify the
machine below before installing software or deploying a tracked configuration,
then follow only the applicable rows. The individual guides contain copyable
install, deployment, verification, and removal commands.

A repository checkout is not a single configuration to install everywhere.
**On** means that the tracked item is appropriate for that profile when its
program is wanted; **off** means do not deploy it. **Optional** means it is
valid only when the prerequisite application, desktop environment, or use case
exists.

## Identify the machine

| Profile | Use it for | Baseline rule |
| --- | --- | --- |
| **Cluster** | Shared Slurm login or compute hosts | Use cluster-only Pi settings and terminal tools. Do not assume a GUI, local model service, macOS paths, or permission to install system software. |
| **Personal Linux GUI** | Linux laptop or desktop with a graphical session | Use personal Pi settings. Desktop/editor and Linux keyboard settings are optional according to the applications and desktop environment in use. |
| **Personal macOS** | Mac laptop or desktop | Use personal Pi settings. The tracked Zsh and Finder-service configurations apply here; Linux XKB does not. |
| **Personal headless server** | A personal server, including the Oracle server when it is not used as a desktop | Use personal Pi settings and optional terminal tools. Do not deploy GUI, GNOME, Finder, or macOS shell configuration. |
| **Other or unsupported platform** | For example, a native Windows installation | No deployment profile exists. Do not infer that POSIX dotfiles or desktop integrations apply; document and add a profile first. |

If the role is unclear, verify it first. In particular, the presence of Slurm
commands does not by itself establish that a host is a cluster login or compute
node.

## Profile matrix

| Item or software | Cluster | Personal Linux GUI | Personal macOS | Personal headless server | What to do |
| --- | --- | --- | --- | --- | --- |
| Pi settings | **on:** `pi/cluster/settings.json` | **on:** `pi/personal/settings.json` | **on:** `pi/personal/settings.json` | **on:** `pi/personal/settings.json` | Follow [`pi.md`](pi.md). The cluster profile alone enables `pi-slurm` and `pi-subagents`. |
| Pi model configuration | local | local | local | local | Configure `~/.pi/agent/models.json` per machine when custom providers/models are needed; do not track credentials or machine-specific model endpoints here. |
| Pi web tools | optional | optional | optional | optional | The package is currently in both Pi profiles, but each machine needs its own Exa credential and must allow outbound access. Follow [`pi-simple-web-tools.md`](pi-simple-web-tools.md). |
| Bash startup | **on, after review** | **off** | **off** | **off** | `.bashrc` hard-codes the cluster `/cephfs` home and path; it is cluster-specific. See [`shell.md`](shell.md). |
| Zsh startup | **off** | **off** | **on, after review** | **off** | `.zshrc` contains macOS `/Users/...` and Antigravity paths; do not copy it unchanged to Linux. See [`shell.md`](shell.md). |
| SSH client config | optional | **on** when accessing the cluster | **on** when accessing the cluster | optional | `.ssh/config` is a client-side convenience configuration, not a server or compute-node setting. Never track private keys. See [`ssh.md`](ssh.md). |
| tmux | **on** | optional | optional | optional | The shared `.tmux.conf` is portable; create a small host wrapper for the per-machine status style. See [`tmux.md`](tmux.md). |
| Vim | optional | optional | optional | optional | `.vimrc` is shared. See [`vim.md`](vim.md). |
| Git | optional | optional | optional | optional | `.gitconfig` is shared. See [`git.md`](git.md). |
| Glow | optional | optional | optional | optional | Shared configuration, with OS-specific installation commands. See [`glow.md`](glow.md). |
| Yazi | optional | optional | optional | optional | Shared configuration, with Linux/macOS installation differences. See [`yazi.md`](yazi.md). |
| VS Code settings | **off** | optional | optional | **off** | `VSCode/settings.json` is a GUI workstation configuration. It may be used by a local editor client connected to a cluster. See [`vscode.md`](vscode.md). |
| Zed settings, tasks, themes | **off** | optional | optional | **off** | `zed/` is a GUI workstation configuration. Its default agent is local Ollama, which must not be assumed on a cluster or server. See [`zed.md`](zed.md). |
| Linux keyboard layout | **off** | optional for GNOME/Wayland | **off** | **off** | Install `.config/xkb/symbols/custom` only on a Linux graphical machine using the documented desktop integration. See [`linux-keyboard-layout.md`](linux-keyboard-layout.md). |
| Cursor Finder service | **off** | **off** | optional | **off** | `Open in Cursor.workflow` is macOS Finder-only. See [`open-in-cursor.md`](open-in-cursor.md). |
| Admin-skill template | **on** | **on** | **on** | **on** | Copy `skills/admin/SKILL.md` everywhere, then complete the local installed copy with that machine's verified facts and boundaries. See [`admin-skill.md`](admin-skill.md). |
| Other active skills | optional | optional | optional | optional | `skills/` also contains selected research, workflow, and Slurm skills. Load a Slurm skill only when operating a remote or local cluster; do not infer that Slurm is present. See [`hermes-skills.md`](hermes-skills.md). |
| Archived Hermes skills | **off** | **off** | **off** | **off** | `hermes-skills/` is historical reference material and must not be installed or automatically loaded. See [`hermes-skills.md`](hermes-skills.md). |

## Pi profile procedure

Install exactly one settings profile as `~/.pi/agent/settings.json`:

```sh
PI_PROFILE=cluster    # use personal on any personal device or server
case "$PI_PROFILE" in cluster|personal) ;; *) exit 2 ;; esac
mkdir -p ~/.pi/agent
cp -p ~/dotfiles/pi/$PI_PROFILE/settings.json ~/.pi/agent/settings.json
```

Do not recreate a single root-level `pi/settings.json`; doing so would remove
the profile boundary. [`pi.md`](pi.md) documents refresh and verification.

## Current explicit splits

The paired configuration variant is Pi: `pi-slurm` and `pi-subagents` are
**on** in the cluster settings and **off** in the personal settings. The other explicit
profile boundaries are single-purpose files: cluster Bash, macOS Zsh and Finder
integration, Linux GNOME/Wayland keyboard integration, and workstation-only
editor configuration. tmux, Vim, Git, Glow, and Yazi are currently shared
rather than split into profile variants.
