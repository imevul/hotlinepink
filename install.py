#!/usr/bin/env python3
"""Install or remove Hotline Pink theme files. Run with --help for usage.

Theme files are only added, and anything they would replace is backed up first.
Your own configs are never edited: each app prints its activation step instead.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIDE_SCRIPT = ROOT / "apps" / "fish" / "tide-colors.fish"
TIDE_LINE = re.compile(r"^set -U (\S+) (\S+)$", re.M)
VAR_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def state_dir():
    base = os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state"
    return Path(base) / "hotlinepink"


def load_manifest():
    path = state_dir() / "manifest.json"
    return json.loads(path.read_text()) if path.exists() else {"apps": {}, "tide": None}


def save_manifest(manifest):
    path = state_dir() / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(dest):
    return Path(dest).expanduser()


def targets(app):
    """Yield (source, destination) for every file this app installs here."""
    for item in app["files"]:
        only_if = item.get("only_if")
        for index, dest in enumerate(item["dest"]):
            if only_if is None or expand(only_if[index]).exists():
                yield item["src"], expand(dest)


def backup_path(path, stamp):
    candidate = path.with_name(f"{path.name}.bak-{stamp}")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.bak-{stamp}-{counter}")
        counter += 1
    return candidate


def fish_env():
    return {**os.environ, "fish_greeting": ""}


def fish_query(names):
    """Return {name: [values]} for the universal variables that are set."""
    script = (
        "for v in $argv\n"
        "  if set -q -U $v\n"
        '    printf "%s\\x1e" $v $$v\n'
        '    printf "\\x1f"\n'
        "  end\n"
        "end"
    )
    result = subprocess.run(
        ["fish", "-c", script, "--", *names],
        capture_output=True, text=True, env=fish_env(), check=True,
    )
    values = {}
    for record in result.stdout.split("\x1f"):
        parts = record.split("\x1e")
        if len(parts) >= 2 and VAR_NAME.match(parts[0]):
            values[parts[0]] = parts[1:-1]
    return values


def fish_quote(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def tide_theme():
    return dict(TIDE_LINE.findall(TIDE_SCRIPT.read_text()))


def snapshot_tide(manifest, dry_run):
    """Save the current Tide colours, once, so a reinstall keeps the originals."""
    if manifest.get("tide") is not None or not shutil.which("fish"):
        return
    names = list(tide_theme())
    if dry_run:
        print(f"  would save {len(names)} Tide colours")
        return
    current = fish_query(names)
    manifest["tide"] = {name: current.get(name) for name in names}
    print(f"  saved {len(current)} current Tide colours")


def restore_tide(manifest, dry_run):
    """Restore Tide colours still on their Hotline Pink value."""
    snapshot = manifest.get("tide")
    if not snapshot or not shutil.which("fish"):
        return
    theme = tide_theme()
    current = fish_query(list(snapshot))
    lines = []
    kept = 0
    for name, original in snapshot.items():
        if current.get(name) != [theme.get(name)]:
            kept += 1
        elif original is None:
            lines.append(f"set -e -U {name}")
        else:
            lines.append(" ".join(["set -U", name, *map(fish_quote, original)]))
    if dry_run:
        print(f"  would restore {len(lines)} Tide colours, {kept} left as they are")
        return
    if lines:
        subprocess.run(["fish", "-c", "\n".join(lines)], env=fish_env(), check=True)
    manifest["tide"] = None
    print(f"  restored {len(lines)} Tide colours, {kept} left as they are")


def install_app(app_id, app, manifest, dry_run):
    print(f"{app['name']}:")
    if app.get("manual"):
        print(f"  manual: see apps/{app_id}/README.md")
        print(f"  {app['activate'].strip()}")
        return
    record = manifest["apps"].setdefault(app_id, {})
    stamp = time.strftime("%Y%m%d-%H%M%S")
    installed = 0
    for src, dest in targets(app):
        source = ROOT / "apps" / app_id / src
        entry = record.get(str(dest))
        new_hash = sha256(source)
        if dest.exists() and sha256(dest) == new_hash:
            print(f"  up to date: {dest}")
            if entry is None and not dry_run:
                # Identical file that this installer did not put there: leave it on uninstall.
                record[str(dest)] = {"sha256": new_hash, "backup": None, "preexisting": True}
            installed += 1
            continue
        backup = entry["backup"] if entry else None
        ours = entry is not None and dest.exists() and sha256(dest) == entry["sha256"]
        if dest.exists() and not ours:
            new_backup = backup_path(dest, stamp)
            # The oldest backup holds the original, so it stays the one to restore.
            backup = backup or str(new_backup)
            print(f"  back up: {dest} -> {new_backup}")
            if not dry_run:
                shutil.copy2(dest, new_backup)
        print(f"  install: {dest}")
        if not dry_run:
            created = manifest.setdefault("created_dirs", [])
            created.extend(p for p in missing_parents(dest) if p not in created)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            record[str(dest)] = {"sha256": new_hash, "backup": backup}
        installed += 1
    if not installed:
        print("  skipped: the app's config folder does not exist here")
        manifest["apps"].pop(app_id, None)
        return
    if dry_run and not record:
        manifest["apps"].pop(app_id, None)
    if app_id == "fish":
        snapshot_tide(manifest, dry_run)
    print(f"  next: {app['activate'].strip()}")


def missing_parents(path):
    parents = []
    parent = path.parent
    while not parent.exists():
        parents.append(str(parent))
        parent = parent.parent
    return parents


def remove_created_dirs(manifest):
    """Remove folders the installer created, once nothing is left in them."""
    remaining = []
    for path in sorted(manifest.get("created_dirs", []), key=len, reverse=True):
        try:
            Path(path).rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            remaining.append(path)
    manifest["created_dirs"] = remaining


def uninstall_app(app_id, app, manifest, dry_run, force):
    record = manifest["apps"].get(app_id)
    print(f"{app['name']}:")
    if record is None:
        print("  not installed")
        return
    for dest_str, entry in list(record.items()):
        dest = Path(dest_str)
        backup = Path(entry["backup"]) if entry.get("backup") else None
        if entry.get("preexisting"):
            print(f"  keep (was already there): {dest}")
        elif dest.exists() and sha256(dest) != entry["sha256"] and not force:
            print(f"  warning: {dest} changed since install, kept it. Use --force to replace it.")
            if backup:
                print(f"  backup kept: {backup}")
            continue
        elif backup and backup.exists():
            print(f"  restore: {backup} -> {dest}")
            if not dry_run:
                backup.replace(dest)
        else:
            if backup:
                print(f"  warning: backup {backup} is missing")
            print(f"  remove: {dest}")
            if not dry_run:
                dest.unlink(missing_ok=True)
        if not dry_run:
            del record[dest_str]
    if app_id == "fish":
        restore_tide(manifest, dry_run)
    if not dry_run and not record:
        del manifest["apps"][app_id]
    print(f"  revert by hand if you added it: {app['activate'].strip()}")


def main():
    parser = argparse.ArgumentParser(description="Install or remove Hotline Pink theme files.")
    parser.add_argument("apps", nargs="*", help="app ids, see --list")
    parser.add_argument("--list", action="store_true", help="list apps and exit")
    parser.add_argument("--all", action="store_true", help="act on every app")
    parser.add_argument("--uninstall", action="store_true", help="remove files and restore backups")
    parser.add_argument("--force", action="store_true", help="on uninstall, also replace files you edited")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen, change nothing")
    args = parser.parse_args()

    apps = tomllib.loads((ROOT / "base" / "apps.toml").read_text())
    if args.list:
        for app_id, app in apps.items():
            print(f"{app_id:18} {app['name']}{' (manual)' if app.get('manual') else ''}")
        return 0
    unknown = [a for a in args.apps if a not in apps]
    if unknown:
        parser.error(f"unknown app: {', '.join(unknown)}. See --list.")
    chosen = list(apps) if args.all else args.apps
    if not chosen:
        parser.error("name at least one app, or use --all or --list")

    manifest = load_manifest()
    for app_id in chosen:
        if args.uninstall:
            uninstall_app(app_id, apps[app_id], manifest, args.dry_run, args.force)
        else:
            install_app(app_id, apps[app_id], manifest, args.dry_run)
    if not args.dry_run:
        if args.uninstall:
            remove_created_dirs(manifest)
        save_manifest(manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
