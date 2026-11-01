# herdr

Colour overrides for herdr's UI.

## Install

The installer doesn't copy anything for this app, so follow the steps below.

## Switch it on

Your turn: the installer never edits your own configs.

1. Open `~/.config/herdr/config.toml`.
2. Delete your existing `[theme]` section, along with any `[theme.custom]` section.
3. Paste the whole of `theme.toml` in its place.
4. Reload the config:

   ```bash
   herdr server reload-config
   ```


## Uninstall

1. Replace the `[theme]` and `[theme.custom]` sections in `~/.config/herdr/config.toml` with your previous theme, then run `herdr server reload-config`.

## Notes

herdr has no way to add a named theme, so its colours live in its main config. `name` stays `tokyo-night` as the base, and `[theme.custom]` overrides the colours on top of it.

Status: Syntax checked only.
