# Alacritty

Colour theme for Alacritty.

## Install

```bash
./install.py alacritty
```

| File | Installed to |
|---|---|
| `hotline-pink.toml` | `~/.config/alacritty/themes/hotline-pink.toml` |

## Switch it on

Your turn: the installer never edits your own configs.

1. Add this to `~/.config/alacritty/alacritty.toml`. If you already have a `[general]` section, add the `import` line to it:

   ```toml
   [general]
   import = ["~/.config/alacritty/themes/hotline-pink.toml"]
   ```


## Uninstall

```bash
./install.py --uninstall alacritty
```

1. Remove the `hotline-pink.toml` import from `alacritty.toml`.

Status: Syntax checked only.
