#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${HOOKS_DIR:-$HOME/.config/wasteland/hooks}"

mkdir -p "$DEST_DIR"
cp "$SRC_DIR/mythos-stop.py" "$DEST_DIR/mythos-stop.py"
cp "$SRC_DIR/mythos-session.py" "$DEST_DIR/mythos-session.py"
chmod 755 "$DEST_DIR/mythos-stop.py" "$DEST_DIR/mythos-session.py"

echo "Installed:"
echo "  $DEST_DIR/mythos-stop.py"
echo "  $DEST_DIR/mythos-session.py"
echo
echo "Merge these objects into ~/.claude/settings.json under \"hooks\"."
echo "Add the Stop object to the \"Stop\" array, and the SessionStart object"
echo "to the \"SessionStart\" array as a new UNMATCHED entry (no \"matcher\" key,"
echo "so it fires on every source: startup, resume, clear, compact, fork)."
echo
cat <<EOF
"Stop": [
  {
    "hooks": [
      { "type": "command", "command": "$DEST_DIR/mythos-stop.py", "timeout": 5 }
    ]
  }
]

"SessionStart": [
  {
    "hooks": [
      { "type": "command", "command": "$DEST_DIR/mythos-session.py", "timeout": 5 }
    ]
  }
]
EOF
echo
echo "Optional UserPromptSubmit reminder:"
echo "  Insert the block from $SRC_DIR/autoskill-mythos-rule.snippet into"
echo "  $DEST_DIR/autoskill.py (see that file for the anchor). It re-surfaces"
echo "  an active mission and flips a blocked mission back to open on the next prompt."
echo
echo "Kill-switch: export MYTHOS_HOOKS=0 disables all mythos hooks without uninstalling."
echo "This script does not edit settings.json; apply the merge yourself."
