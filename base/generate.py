#!/usr/bin/env python3
"""Render base/templates/<app>/ into apps/<app>/ from base/palette.json.

Placeholders: {{token}} is #RRGGBB, and {{token.lower}}, {{token.bare}} and
{{token.rgb}} give #rrggbb, RRGGBB and R,G,B.

  base/generate.py          write apps/ and the README apps table
  base/generate.py --check  fail on drift, low contrast or off-palette colours
"""
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "base"
APPS = ROOT / "apps"
README = ROOT / "README.md"
TABLE_START = "<!-- apps:start -->"
TABLE_END = "<!-- apps:end -->"
PLACEHOLDER = re.compile(r"\{\{([a-z0-9-]+)(?:\.([a-z]+))?\}\}")
HEX = re.compile(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?\b")
MIN_CONTRAST = 4.5
# ANSI black is a surface colour, not a text colour.
CONTRAST_EXEMPT = {"ansi-black"}
STATUS_LABELS = {
    "loaded": "Loaded in the app",
    "syntax": "Syntax checked only",
}


def load_tokens():
    palette = json.loads((BASE / "palette.json").read_text())
    tokens = {**palette["canonical"], **palette["derived"]}
    for role, target in palette["roles"].items():
        tokens[role] = tokens[target]
    return palette, tokens


def format_colour(value, form):
    if form is None:
        return value
    if form == "lower":
        return value.lower()
    if form == "bare":
        return value[1:]
    if form == "rgb":
        return ",".join(str(int(value[i : i + 2], 16)) for i in (1, 3, 5))
    raise ValueError(f"unknown colour format: {form}")


def render(text, tokens, source):
    def replace(match):
        name, form = match.groups()
        if name not in tokens:
            raise KeyError(f"{source}: unknown token {name}")
        return format_colour(tokens[name], form)

    return PLACEHOLDER.sub(replace, text)


def app_readme(app_id, app):
    lines = [f"# {app['name']}", "", app["summary"], ""]
    lines += ["## Install", ""]
    if app.get("manual"):
        lines += ["This one is applied by hand, see Activate below.", ""]
    else:
        lines += ["```bash", f"./install.py {app_id}", "```", ""]
        lines += ["| File | Installed to |", "|---|---|"]
        for item in app["files"]:
            for dest in item["dest"]:
                lines.append(f"| `{item['src']}` | `{dest}` |")
        lines.append("")
    lines += ["## Activate", "", app["activate"].strip(), ""]
    if app.get("notes"):
        lines += ["## Notes", "", app["notes"].strip(), ""]
    lines += [f"Status: {STATUS_LABELS[app['status']]}.", ""]
    return "\n".join(lines)


def build_outputs(apps, tokens):
    outputs = {}
    for app_id, app in apps.items():
        template_dir = BASE / "templates" / app_id
        for path in sorted(template_dir.rglob("*")):
            if path.is_file():
                rel = path.relative_to(template_dir)
                outputs[Path(app_id) / rel] = render(path.read_text(), tokens, path)
        outputs[Path(app_id) / "README.md"] = app_readme(app_id, app)
    return outputs


def apps_table(apps):
    lines = ["| Group | App | Install | Status |", "|---|---|---|---|"]
    for app_id, app in apps.items():
        how = "manual" if app.get("manual") else f"`./install.py {app_id}`"
        lines.append(
            f"| {app['group']} | [{app['name']}](apps/{app_id}/) | {how} | {STATUS_LABELS[app['status']]} |"
        )
    return "\n".join(lines)


def with_table(readme, table):
    pattern = re.compile(re.escape(TABLE_START) + ".*?" + re.escape(TABLE_END), re.S)
    return pattern.sub(lambda _: f"{TABLE_START}\n{table}\n{TABLE_END}", readme)


def luminance(value):
    channels = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check(outputs, palette, tokens, apps):
    problems = []
    for rel, content in outputs.items():
        path = APPS / rel
        if not path.exists() or path.read_text() != content:
            problems.append(f"out of date: apps/{rel}")
    for path in APPS.rglob("*"):
        if path.is_file() and path.relative_to(APPS) not in outputs:
            problems.append(f"not generated: {path.relative_to(ROOT)}")
    if README.exists() and README.read_text() != with_table(README.read_text(), apps_table(apps)):
        problems.append("out of date: README.md apps table")

    for role in palette["roles"]:
        if role.startswith(("ansi-", "syntax-")) and role not in CONTRAST_EXEMPT:
            ratio = contrast(tokens[role], tokens["bg"])
            if ratio < MIN_CONTRAST:
                problems.append(f"low contrast: {role} {tokens[role]} is {ratio:.2f}:1 on bg")

    allowed = {value.upper() for value in tokens.values()}
    for rel, content in outputs.items():
        for colour in HEX.findall(content):
            if colour[:7].upper() not in allowed:
                problems.append(f"off palette: {colour} in apps/{rel}")
    return problems


def main():
    palette, tokens = load_tokens()
    apps = tomllib.loads((BASE / "apps.toml").read_text())
    outputs = build_outputs(apps, tokens)
    if "--check" in sys.argv[1:]:
        problems = check(outputs, palette, tokens, apps)
        for problem in problems:
            print(problem, file=sys.stderr)
        print(f"{len(outputs)} files checked, {len(problems)} problems")
        return 1 if problems else 0
    if APPS.exists():
        shutil.rmtree(APPS)
    for rel, content in outputs.items():
        path = APPS / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if README.exists():
        README.write_text(with_table(README.read_text(), apps_table(apps)))
    print(f"wrote {len(outputs)} files for {len(apps)} apps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
