# Microsoft Terminal

Colour scheme for Windows Terminal.

## Install

The installer doesn't copy anything for this app, so follow the steps below.

## Switch it on

Your turn: the installer never edits your own configs.

1. On Windows, open Terminal's Settings, then Open JSON file.
2. Add the contents of `hotline-pink.json` as a new entry in the `schemes` array.
3. Add this under `profiles.defaults`:

   ```json
   "colorScheme": "Hotline Pink"
   ```


## Uninstall

1. Remove the Hotline Pink entry from `schemes` and the `colorScheme` line from `profiles.defaults`.

Status: Syntax checked only.
