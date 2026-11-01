# fzf

Colour options for fzf, for fish and zsh.

## Install

```bash
./install.py fzf
```

| File | Installed to |
|---|---|
| `hotline-pink.fish` | `~/.config/fzf/hotline-pink.fish` |
| `hotline-pink.zsh` | `~/.config/fzf/hotline-pink.zsh` |

## Switch it on

Your turn: the installer never edits your own configs.

1. For fish, add this line to `~/.config/fish/config.fish`:

   ```fish
   source ~/.config/fzf/hotline-pink.fish
   ```

2. For zsh, add this line to `~/.zshrc`:

   ```zsh
   source ~/.config/fzf/hotline-pink.zsh
   ```


## Uninstall

```bash
./install.py --uninstall fzf
```

1. Remove the `source` line from `config.fish` or `.zshrc`, or your shell will warn that the file is missing.

Status: Syntax checked only.
