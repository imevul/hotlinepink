# bat

Syntax theme for bat. delta uses it too.

## Install

```bash
./install.py bat
```

| File | Installed to |
|---|---|
| `hotline-pink.tmTheme` | `~/.config/bat/themes/hotline-pink.tmTheme` |

## Switch it on

Your turn: the installer never edits your own configs.

1. Rebuild bat's theme cache:

   ```bash
   bat cache --build
   ```

2. Add this line to `~/.config/bat/config`:

   ```
   --theme="hotline-pink"
   ```


## Uninstall

```bash
./install.py --uninstall bat
```

1. Remove `--theme="hotline-pink"` from `~/.config/bat/config`, then run `bat cache --build`.

Status: Loaded in the app.
