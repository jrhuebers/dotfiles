# Lessons

- When a Yazi-to-tmux opener misbehaves, timing delays are not a reliable fix. Avoid stacking waits; isolate the shell/UI lifecycle and prefer the simplest direct tmux command.
- For GNOME Wayland custom XKB layouts, use the registry's `custom` layout name when installing a user-defined symbols file; an arbitrary source ID can be rejected and fall back to US.
