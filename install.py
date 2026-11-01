#!/usr/bin/env python3
"""Install or remove Hotline Pink theme files. Run with --help for usage.

Theme files are only added, and anything they would replace is backed up first.
Your own configs are never edited. The output ends with the steps left for you.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIDE_SCRIPT = ROOT / "apps" / "fish" / "tide-colors.fish"
TIDE_LINE = re.compile(r"^set -U (\S+) (\S+)$", re.M)
VAR_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FILE_REF = re.compile(r"\{file:([^}]+)\}")
INLINE_CODE = re.compile(r"`([^`]+)`")
WIDTH = 88
KEEP_SPACE = "\x00"
USE_COLOUR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def style(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOUR else text


def heading(text):
    return style(text, "1;38;2;255;20;147")


def app_title(text):
    return style(text, "1")


def inline_code(text):
    """Colour `code` spans. Without colour the backticks stay, to mark where they end."""
    if not USE_COLOUR:
        return text
    return INLINE_CODE.sub(lambda m: style(m.group(1), "38;2;255;92;184"), text)


def show(path):
    """Shorten a path under the home folder to ~/..."""
    path, home = str(path), str(Path.home())
    return "~" + path[len(home):] if path == home or path.startswith(home + "/") else path


def wrapped(text, indent, first=None):
    """Wrap before colouring, so escape codes don't count towards the width."""
    # Hold the spaces inside `code` spans so a span never splits across lines.
    held = INLINE_CODE.sub(lambda m: m.group(0).replace(" ", KEEP_SPACE), text)
    lines = textwrap.wrap(
        held, WIDTH, initial_indent=first or indent, subsequent_indent=indent,
        break_long_words=False, break_on_hyphens=False,
    )
    return "\n".join(inline_code(line.replace(KEEP_SPACE, " ")) for line in lines)


def resolve_files(text, app_id):
    return FILE_REF.sub(lambda m: show(ROOT / "apps" / app_id / m.group(1)), text)


class Report:
    """What happened to one app, printed once every app is done."""

    def __init__(self, app_id, app):
        self.app_id = app_id
        self.app = app
        self.changes = []  # (word, path text, optional detail)
        self.touched = False  # a file was added, replaced, removed or restored
        self.installed = False  # the theme file is in place after this run

    def add(self, word, path, detail=None, touched=True):
        self.changes.append((word, path, detail))
        self.touched = self.touched or touched


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


def snapshot_tide(manifest, dry_run, report):
    """Save the current Tide colours, once, so a reinstall keeps the originals."""
    if manifest.get("tide") is not None or not shutil.which("fish"):
        return
    names = list(tide_theme())
    if not dry_run:
        current = fish_query(names)
        manifest["tide"] = {name: current.get(name) for name in names}
    report.add("saved", "your current Tide colours, for uninstall", touched=False)


def restore_tide(manifest, dry_run, report):
    """Restore Tide colours still on their Hotline Pink value."""
    snapshot = manifest.get("tide")
    if not snapshot or not shutil.which("fish"):
        return
    theme = tide_theme()
    current = fish_query(list(snapshot))
    lines = []
    kept = 0
    for name, original in snapshot.items():
        if name not in theme:
            continue
        if current.get(name) != [theme[name]]:
            kept += 1
        elif original is None:
            lines.append(f"set -e -U {name}")
        else:
            lines.append(" ".join(["set -U", name, *map(fish_quote, original)]))
    if not dry_run:
        if lines:
            subprocess.run(["fish", "-c", "\n".join(lines)], env=fish_env(), check=True)
        manifest["tide"] = None
    detail = f"kept {kept} you changed yourself" if kept else None
    report.add("restored", f"{len(lines)} Tide colours", detail)


def install_app(app_id, app, manifest, dry_run):
    report = Report(app_id, app)
    if app.get("manual"):
        return report
    record = manifest["apps"].setdefault(app_id, {})
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for src, dest in targets(app):
        source = ROOT / "apps" / app_id / src
        entry = record.get(str(dest))
        new_hash = sha256(source)
        report.installed = True
        if dest.exists() and sha256(dest) == new_hash:
            report.add("up to date", show(dest), touched=False)
            if entry is None and not dry_run:
                # Identical file that this installer did not put there: leave it on uninstall.
                record[str(dest)] = {"sha256": new_hash, "backup": None, "preexisting": True}
            continue
        backup = entry["backup"] if entry else None
        ours = entry is not None and dest.exists() and sha256(dest) == entry["sha256"]
        if dest.exists() and not ours:
            new_backup = backup_path(dest, stamp)
            # The oldest backup holds the original, so it stays the one to restore.
            backup = backup or str(new_backup)
            report.add("replaced", show(dest), f"old version saved as {show(new_backup)}")
            if not dry_run:
                shutil.copy2(dest, new_backup)
        elif ours:
            report.add("updated", show(dest))
        else:
            report.add("added", show(dest))
        if not dry_run:
            created = manifest.setdefault("created_dirs", [])
            created.extend(p for p in missing_parents(dest) if p not in created)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            record[str(dest)] = {"sha256": new_hash, "backup": backup}
    if not record:
        manifest["apps"].pop(app_id, None)
    if report.installed and app_id == "fish":
        snapshot_tide(manifest, dry_run, report)
    return report


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
    report = Report(app_id, app)
    record = manifest["apps"].get(app_id)
    if record is None:
        return report
    report.installed = True
    for dest_str, entry in list(record.items()):
        dest = Path(dest_str)
        backup = Path(entry["backup"]) if entry.get("backup") else None
        if entry.get("preexisting"):
            report.add("kept", show(dest), "it was there before the install", touched=False)
        elif dest.exists() and sha256(dest) != entry["sha256"] and not force:
            detail = "changed since install. Use --force to replace it"
            if backup:
                detail += f". Backup kept at {show(backup)}"
            report.add("kept", show(dest), detail, touched=False)
            continue
        elif backup and backup.exists():
            report.add("restored", show(dest), f"from {show(backup)}")
            if not dry_run:
                backup.replace(dest)
        else:
            detail = f"backup {show(backup)} is missing, so nothing was restored" if backup else None
            report.add("removed", show(dest), detail)
            if not dry_run:
                dest.unlink(missing_ok=True)
        if not dry_run:
            del record[dest_str]
    if app_id == "fish":
        restore_tide(manifest, dry_run, report)
    if not dry_run and not record:
        del manifest["apps"][app_id]
    return report


def print_changes(reports, dry_run):
    with_changes = [r for r in reports if r.changes]
    if not with_changes:
        print(heading("Files"))
        print("  Nothing would change." if dry_run else "  Nothing changed.")
        return
    if not any(r.touched for r in with_changes):
        title = "Files: nothing to change" if dry_run else "Files: nothing changed"
    else:
        title = "What would change" if dry_run else "What changed"
    print(heading(title))
    width = max(len(c[0]) for r in with_changes for c in r.changes)
    for report in with_changes:
        print(f"  {app_title(report.app['name'])}")
        for word, path, detail in report.changes:
            print(f"    {word:<{width}}  {path}")
            if detail:
                print(wrapped(detail, " " * (width + 6)))


def print_steps(steps, app_id):
    for number, step in enumerate(steps, 1):
        first = f"    {number}. "
        print(wrapped(resolve_files(step["do"], app_id), " " * len(first), first))
        if "code" in step:
            print()
            for line in step["code"].splitlines():
                print(" " * (len(first) + 2) + style(line, "38;2;255;92;184"))
            if number < len(steps):
                print()


def print_install_summary(reports, dry_run):
    active = [r for r in reports if r.installed and "active" in r.app]
    todo = [r for r in reports if r.installed and "steps" in r.app]
    manual = [r for r in reports if r.app.get("manual")]
    absent = [r for r in reports if not r.installed and not r.app.get("manual")]

    if absent:
        print()
        print(heading("Skipped"))
        print("  The app's config folder doesn't exist on this machine:")
        for report in absent:
            print(f"  {report.app['name']}")

    if active:
        print()
        print(heading("Ready, nothing more to do"))
        for report in active:
            print(f"  {app_title(report.app['name'])}")
            print(wrapped(report.app["active"], "    "))

    if todo or manual:
        print()
        print(heading("Your turn: these aren't switched on yet"))
        print("  The installer never edits your own configs, so these steps are yours.")
        print("  It can't see whether you've already done them.")
        for report in todo + manual:
            print()
            if report.app.get("manual"):
                state = "nothing was installed, this one is all by hand"
            elif report.touched:
                state = "theme file would be installed" if dry_run else "theme file installed"
            else:
                state = "theme file already in place"
            print(f"  {app_title(report.app['name'])}: {state}")
            print_steps(report.app["steps"], report.app_id)

    print()
    waiting = len(todo) + len(manual)
    parts = [f"{len(active)} ready", f"{waiting} {'needs' if waiting == 1 else 'need'} steps from you"]
    if absent:
        parts.append(f"{len(absent)} skipped")
    print(heading("Summary") + ": " + ", ".join(parts))


def print_uninstall_summary(reports):
    done = [r for r in reports if r.installed and "undo" in r.app]
    manual = [r for r in reports if not r.installed and r.app.get("manual") and "undo" in r.app]
    absent = [r for r in reports if not r.installed and not r.app.get("manual")]

    if absent:
        print()
        print(heading("Not installed, so nothing to remove"))
        for report in absent:
            print(f"  {report.app['name']}")

    if done or manual:
        print()
        print(heading("Your turn: undo anything you switched on"))
        print("  The uninstaller never edits your own configs. Skip any step you didn't do.")
        for report in done + manual:
            print()
            suffix = ": set up by hand, so nothing was removed" if report in manual else ""
            print(f"  {app_title(report.app['name'])}{suffix}")
            print_steps([{"do": text} for text in report.app["undo"]], report.app_id)

    print()
    removed = sum(r.touched for r in reports)
    parts = [f"{removed} {'app' if removed == 1 else 'apps'} removed"]
    kept = [r for r in reports if any(c[0] == "kept" for c in r.changes)]
    if kept:
        parts.append(f"{len(kept)} with files kept")
    print(heading("Summary") + ": " + ", ".join(parts))


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
    reports = []
    for app_id in chosen:
        if args.uninstall:
            reports.append(uninstall_app(app_id, apps[app_id], manifest, args.dry_run, args.force))
        else:
            reports.append(install_app(app_id, apps[app_id], manifest, args.dry_run))
    if not args.dry_run:
        if args.uninstall:
            remove_created_dirs(manifest)
        save_manifest(manifest)

    if args.dry_run:
        print("Dry run: nothing has been changed.\n")
    print_changes(reports, args.dry_run)
    if args.uninstall:
        print_uninstall_summary(reports)
    else:
        print_install_summary(reports, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
