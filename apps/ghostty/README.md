# Ghostty

Colour theme for Ghostty.

## Install

```bash
./install.py ghostty
```

| File | Installed to |
|---|---|
| `hotline-pink` | `~/.config/ghostty/themes/hotline-pink` |

## Switch it on

Your turn: the installer never edits your own configs.

1. Open your Ghostty config: `~/.config/ghostty/config.ghostty`, or `~/.config/ghostty/config` on older setups.
2. Delete any `background`, `foreground`, `cursor-color`, `cursor-text`, `selection-background`, `selection-foreground` and `palette` lines, and any existing `theme` line. They override the theme.
3. Add this line:

   ```ini
   theme = hotline-pink
   ```

4. Reload Ghostty's config, or restart it.

## Uninstall

```bash
./install.py --uninstall ghostty
```

1. Remove `theme = hotline-pink` from your Ghostty config, and put back any colour lines you deleted.

Status: Loaded in the app.
