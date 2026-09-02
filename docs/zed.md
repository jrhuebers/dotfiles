# Zed config

Custom Zed settings, tasks, and themes, backed up from `~/.config/zed/`.

## Contents

- `settings.json` — Zed settings
- `tasks.json` — Zed tasks
- `themes/` — custom theme files (`GitLab Light.json`, `VSCode Light Modern.json`)

Not included: `prompts/` and `conversations/` (left in place under `~/.config/zed/`, not backed up here).

## Setting up on a new machine

1. Clone/pull this dotfiles repo.
2. Make sure `~/.config/zed/` exists:
   ```sh
   mkdir -p ~/.config/zed
   ```
3. Symlink each item from this repo into `~/.config/zed/`:
   ```sh
   ln -s ~/dotfiles/zed/settings.json ~/.config/zed/settings.json
   ln -s ~/dotfiles/zed/tasks.json ~/.config/zed/tasks.json
   ln -s ~/dotfiles/zed/themes ~/.config/zed/themes
   ```
4. Restart Zed (or run "zed: reload settings" from the command palette) to pick up the changes.

## Notes

- Editing `~/.config/zed/settings.json` after symlinking edits this repo's copy directly — commit and push as usual to keep other machines in sync.
- If `~/.config/zed/settings.json` (etc.) already exists as a real file on the new machine, remove or rename it before creating the symlink, otherwise `ln -s` will fail.
