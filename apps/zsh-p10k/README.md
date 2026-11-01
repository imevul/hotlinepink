# zsh + Powerlevel10k

A small lean Powerlevel10k prompt in Hotline Pink colours.

## Install

```bash
./install.py zsh-p10k
```

| File | Installed to |
|---|---|
| `p10k.zsh` | `~/.p10k.zsh` |

## Switch it on

Nothing more to do. Open a new zsh session to see it. This assumes your `.zshrc` loads `~/.p10k.zsh`, which is the Powerlevel10k default.

## Uninstall

```bash
./install.py --uninstall zsh-p10k
```

## Notes

Installing replaces `~/.p10k.zsh`, after backing up any existing file. To keep your own prompt layout, skip the installer and copy the block between the `hotline pink colours` markers to the end of the main function in your config.

Needs a Nerd Font. JetBrains Mono Nerd Font is the recommended choice.

Status: Loaded in the app.
