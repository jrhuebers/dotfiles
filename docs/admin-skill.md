# Admin skill

`skills/admin/SKILL.md` is the provisioning **template** for the admin skill
on every machine profile: cluster host, personal Linux GUI machine, personal
macOS machine, and personal headless server. The repository copy deliberately
contains no machine facts. During setup, create and complete a local copy with
verified facts and procedures for that particular machine. The running agent
uses that completed local skill; it must not rediscover basic machine facts on
every administration task.

## Install

For a Pi agent, copy the tracked template into the active user skill path:

```sh
mkdir -p ~/.pi/agent/skills/admin
install -m 0644 ~/dotfiles/skills/admin/SKILL.md \
  ~/.pi/agent/skills/admin/SKILL.md
```

Then complete `~/.pi/agent/skills/admin/SKILL.md` **on that machine**:

1. Replace all bracketed template fields with verified platform, role,
   package/service, network, storage, and local-documentation facts.
2. Keep only the shared-cluster or personal-device/server section that applies.
3. Add the machine's safe operational boundaries, routine checks, and rollback
   procedures.
4. Remove the provisioning-template notice and change the front-matter
   description to describe the completed local skill.

Do not overwrite a completed local skill with the template during a normal
repository refresh, and never copy the completed host-specific skill back into
this repository. If another agent runtime uses a different active-skills path,
copy and complete the same template there according to that runtime's
documentation. Do not install any skill from `hermes-skills/`; it is a
reference archive. See [`hermes-skills.md`](hermes-skills.md).

Restart or reload the agent runtime after completing or changing its skill.

## Verify

Confirm that the completed local copy has no bracketed template fields, names
the correct machine profile and operating system, records the local
administration-documentation location, and contains only applicable
role-specific boundaries. Review it after any material change to the machine
or its operational procedures.

[`device-profiles.md`](device-profiles.md) tells the setup agent which
repository settings and software apply to the machine. The completed local
admin skill supplies the durable machine facts used during routine work.

## Removal

Remove only the completed local copy when the active runtime should no longer
load this skill:

```sh
rm ~/.pi/agent/skills/admin/SKILL.md
```
