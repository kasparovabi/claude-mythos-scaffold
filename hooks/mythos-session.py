#!/usr/bin/env python3
import sys
import os
import re
import json

OPEN_MARK = re.compile(r"^\s*- \[[ ~!]\]")
FIELD_LINE = re.compile(r"(?m)^([A-Za-z_]+):\s*(.*)$")
FRONTMATTER = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?(.*)$", re.DOTALL)
GOAL_LINE = re.compile(r"(?m)^#\s*G:\s*(.*)$")


def default_pointer():
    return os.environ.get("MYTHOS_PTR") or os.path.expanduser("~/.cache/mythos/active")


def read_pointer(ptr):
    with open(ptr, encoding="utf-8") as f:
        return os.path.expanduser(f.read().strip())


def read_mission(mission_path):
    with open(mission_path, encoding="utf-8-sig") as f:
        return f.read()


def split_frontmatter(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def parse_fields(fm_text):
    fields = {}
    for m in FIELD_LINE.finditer(fm_text):
        fields[m.group(1)] = m.group(2).strip()
    return fields


def open_item_lines(body):
    return [line.strip() for line in body.splitlines() if OPEN_MARK.match(line)]


def goal_text(body):
    m = GOAL_LINE.search(body)
    return m.group(1).strip() if m else ""


def main():
    if os.environ.get("MYTHOS_HOOKS") == "0":
        return
    ptr = default_pointer()
    try:
        os.stat(ptr)
    except OSError:
        return
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    source = payload.get("source") or ""
    cwd = payload.get("cwd") or ""
    try:
        mission_path = read_pointer(ptr)
    except OSError:
        return
    if not mission_path:
        return
    try:
        text = read_mission(mission_path)
    except OSError:
        return
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        return
    fields = parse_fields(fm_text)
    if fields.get("status", "open") != "open":
        return
    mission_cwd = fields.get("cwd", "")
    if source == "startup" and mission_cwd and not cwd.startswith(mission_cwd):
        return
    open_items = open_item_lines(body)
    lines = ["[mythos] aktif görev: %s — dosyayı oku ve kaldığın yerden devam et." % mission_path,
             "hedef: %s" % goal_text(body),
             "açık maddeler (%d):" % len(open_items)]
    lines.extend("  " + item for item in open_items[:6])
    lines.append("biteni '- [x]' + kanıtla işaretle; görevi kapatmak: status: done ya da rm %s" % ptr)
    print("\n".join(lines))


try:
    main()
except SystemExit:
    raise
except Exception:
    pass
sys.exit(0)
