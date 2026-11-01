# fish + Tide

Syntax colours for fish, and colours for the Tide prompt.

## Install

```bash
./install.py fish
```

| File | Installed to |
|---|---|
| `Hotline Pink.theme` | `~/.config/fish/themes/Hotline Pink.theme` |
| `tide-colors.fish` | `~/.config/fish/hotline-pink-tide-colors.fish` |

## Switch it on

Your turn: the installer never edits your own configs.

1. Add this line to `~/.config/fish/config.fish`, then open a new fish session:

   ```fish
   fish_config theme choose "Hotline Pink"
   ```

2. If you use Tide, run this once to apply its colours:

   ```bash
   fish ~/.config/fish/hotline-pink-tide-colors.fish
   ```


## Uninstall

```bash
./install.py --uninstall fish
```

1. Remove the `fish_config theme choose` line from `config.fish`.

## Notes

The installer saves your current Tide colours first. `./install.py --uninstall fish` restores any colour still set to its Hotline Pink value, and leaves colours you changed since then alone.

Status: Loaded in the app.
