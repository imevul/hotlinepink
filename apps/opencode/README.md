# opencode

TUI theme for opencode.

## Install

```bash
./install.py opencode
```

| File | Installed to |
|---|---|
| `hotline-pink.json` | `~/.config/opencode/themes/hotline-pink.json` |

## Switch it on

Your turn: the installer never edits your own configs.

1. Add this key to `~/.config/opencode/tui.jsonc` or `tui.json`:

   ```json
   "theme": "hotline-pink"
   ```


## Uninstall

```bash
./install.py --uninstall opencode
```

1. Remove the `theme` key from `tui.jsonc` or `tui.json`.

Status: Syntax checked only.
