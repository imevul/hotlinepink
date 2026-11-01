# zsh + Powerlevel10k

A small lean Powerlevel10k prompt in Hotline Pink colours.

## Install

```bash
./install.py zsh-p10k
```

| File | Installed to |
|---|---|
| `p10k.zsh` | `~/.p10k.zsh` |

## Activate

Open a new shell. Your `.zshrc` needs to source `~/.p10k.zsh`, as the Powerlevel10k setup does by default.

## Notes

Installing replaces `~/.p10k.zsh`, after backing up any existing file. To keep your own prompt layout, skip the installer and copy the block between the `hotline pink colours` markers to the end of the main function in your config.

Needs a Nerd Font. JetBrains Mono Nerd Font is the recommended choice.

Status: Loaded in the app.
