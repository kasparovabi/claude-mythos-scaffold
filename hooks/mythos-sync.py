#!/usr/bin/env python
"""
Generic skill sync hook for Claude Code PostToolUse on Edit|Write.

Mirrors skill files from a source location (such as an Obsidian vault) to
the global Claude Code skills directory whenever they are edited. Useful
when you author skills in a vault but want them available to every Claude
Code session via the global skills directory.

Configure via environment variables (recommended) or edit CONFIG below.

Environment variables:
  SKILL_SYNC_PATTERN       Regex matched against the edited file_path.
                           Default matches markdown files inside any
                           "skills" / "Skills" directory, with or without
                           a "(C) " prefix.
  SKILL_SYNC_PREFIX_STRIP  Optional filename prefix to strip on copy
                           (default: "(C) "). Set to empty string to
                           disable.
  SKILL_SYNC_TARGET_DIR    Destination directory (default:
                           ~/.claude/skills/mythos).

Hook registration (in ~/.claude/settings.json):

    {
      "hooks": {
        "PostToolUse": [{
          "matcher": "Edit|Write",
          "hooks": [{
            "type": "command",
            "command": "python /path/to/mythos-sync.py",
            "timeout": 10
          }]
        }]
      }
    }

Silent on any error so it never blocks the parent tool.
"""
import json
import os
import re
import shutil
import sys


CONFIG = {
    "pattern": os.environ.get(
        "SKILL_SYNC_PATTERN",
        r"[Ss]kills[/\\](?:\(C\) )?[a-z][a-z0-9-]*\.md$",
    ),
    "prefix_strip": os.environ.get("SKILL_SYNC_PREFIX_STRIP", "(C) "),
    "target_dir": os.path.expanduser(
        os.environ.get("SKILL_SYNC_TARGET_DIR", "~/.claude/skills/mythos")
    ),
}


def main() -> None:
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    file_path = (
        (data.get("tool_input") or {}).get("file_path")
        or (data.get("tool_response") or {}).get("filePath")
        or ""
    )

    if not re.search(CONFIG["pattern"], file_path):
        return

    basename = os.path.basename(file_path)
    prefix = CONFIG["prefix_strip"]
    if prefix and basename.startswith(prefix):
        basename = basename[len(prefix):]

    target_path = os.path.join(CONFIG["target_dir"], basename)

    try:
        os.makedirs(CONFIG["target_dir"], exist_ok=True)
        shutil.copy2(file_path, target_path)
    except OSError:
        return


if __name__ == "__main__":
    main()
