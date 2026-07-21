#!/usr/bin/env python3
import sys
import os
import re
import json
import tempfile

OPEN_MARK = re.compile(r"^\s*- \[[ ~!]\]")
BOX_PREFIX = re.compile(r"^\s*- \[[ ~!xX]\]\s*")
FIELD_LINE = re.compile(r"(?m)^([A-Za-z_]+):\s*(.*)$")
FRONTMATTER = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?(.*)$", re.DOTALL)
OPEN_FENCE = re.compile(r"^(---[ \t]*\r?\n)")


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


def strip_box(line):
    return BOX_PREFIX.sub("", line).strip()


def set_field(text, key, value):
    value = str(value)
    line_re = re.compile(r"(?m)^" + re.escape(key) + r":[ \t]*.*$")
    if line_re.search(text):
        return line_re.sub(lambda m: key + ": " + value, text, count=1)
    fence = OPEN_FENCE.match(text)
    if fence:
        idx = fence.end()
        return text[:idx] + key + ": " + value + "\n" + text[idx:]
    return text


def atomic_write(path, text):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".mythos-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def to_int(value, default):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def unlink_quiet(path):
    try:
        os.unlink(path)
    except OSError:
        pass


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
    stop_active = bool(payload.get("stop_hook_active"))
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
    status = fields.get("status", "open")
    if status == "done":
        unlink_quiet(ptr)
        return
    if status == "blocked":
        return
    open_items = open_item_lines(body)
    if not open_items:
        atomic_write(mission_path, set_field(text, "status", "done"))
        unlink_quiet(ptr)
        return
    cap = to_int(os.environ.get("MYTHOS_NUDGE_CAP"), to_int(fields.get("nudge_cap"), 3))
    nud = to_int(fields.get("nudges"), 0)
    lopen = to_int(fields.get("last_open"), -1)
    cur = len(open_items)
    nud = 0 if (lopen != -1 and cur < lopen) else nud + 1
    new_text = set_field(text, "nudges", nud)
    new_text = set_field(new_text, "last_open", cur)
    give_up = nud > cap or (stop_active and nud >= cap)
    if give_up:
        items = "; ".join(strip_box(x) for x in open_items[:5])
        new_text = new_text.rstrip("\n") + "\n> left open (nudge cap %d): %s\n" % (cap, items)
        atomic_write(mission_path, new_text)
        print(json.dumps(
            {"systemMessage": "mythos: %d madde açık, nudge tavanı (%d) doldu, bırakıldı." % (cur, cap)},
            ensure_ascii=False))
        return
    atomic_write(mission_path, new_text)
    listing = "\n".join(open_items[:8])
    reason = ("mythos görevi aktif, %d açık madde var, durma:\n%s\n"
              "(biteni kanıtıyla '- [x]' yap; gerçekten kullanıcı girdisi şartsa "
              "mission frontmatter'ına 'status: blocked' yaz ve soruyu sor)") % (cur, listing)
    if len(reason) > 2000:
        reason = reason[:2000]
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


try:
    main()
except SystemExit:
    raise
except Exception:
    pass
sys.exit(0)
