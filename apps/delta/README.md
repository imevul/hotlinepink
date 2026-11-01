# delta

Diff colours for delta.

## Install

```bash
./install.py delta
```

| File | Installed to |
|---|---|
| `hotline-pink.gitconfig` | `~/.config/delta/hotline-pink.gitconfig` |

## Switch it on

Your turn: the installer never edits your own configs.

1. Install the bat theme too, if you haven't, because delta takes its syntax colours from it:

   ```bash
   ./install.py bat
   ```

2. Point git at the theme:

   ```bash
   git config --global --add include.path ~/.config/delta/hotline-pink.gitconfig
   git config --global delta.features hotline-pink
   ```


## Uninstall

```bash
./install.py --uninstall delta
```

1. Run `git config --global --unset include.path '.*hotline-pink.*'` and `git config --global --unset delta.features`.

Status: Syntax checked only.
