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

## Activate

```fish
fish_config theme choose "Hotline Pink"
fish ~/.config/fish/hotline-pink-tide-colors.fish
```

Skip the second line if you don't use Tide. `theme choose` only lasts for the current session, so add that line to `config.fish` to keep the theme.

## Notes

The installer saves your current Tide colours first. `./install.py --uninstall fish` restores any colour still set to its Hotline Pink value, and leaves colours you changed since then alone.

Status: Syntax checked only.
