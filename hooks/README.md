# Mythos hooks

Harness-enforced persistence for the Mythos scaffold. Two Claude Code hooks read the
active **mission file** and keep a long-horizon run from stalling or getting lost after a
context compaction. An optional third snippet wires the same awareness into the
`UserPromptSubmit` autoskill router.

## What each hook does

### `mythos-stop.py` — Stop hook
Fires when Claude tries to end its turn. If there is no active mission it is a no-op. With
an active mission it:
- flips the mission to `status: done` and removes the pointer when every checklist item is
  checked, then allows the stop;
- otherwise blocks the stop with `{"decision": "block", ...}` and a Turkish reason listing
  the open items, telling Claude to finish them (or to set `status: blocked` and ask if it
  genuinely needs the user);
- counts nudges so it can never loop forever. Progress (fewer open items than last time)
  resets the counter; no progress increments it. Once the count passes the cap it gives up:
  it appends a `> left open (...)` line to the mission, emits a `systemMessage`, and allows
  the stop. `stop_hook_active` lowers the ceiling by one so a hard stop is honored sooner.

### `mythos-session.py` — SessionStart hook
Registered without a matcher, so it fires on every source (`startup`, `resume`, `clear`,
`compact`, `fork`). If a mission is active and `open` it prints a short context block (the
mission path, the goal, the first open items, how to close it) that Claude Code injects as
context. On `startup` it stays silent when the mission's `cwd` does not prefix the session
`cwd`, so a mission never bleeds into another project.

### `autoskill-mythos-rule.snippet` — UserPromptSubmit (optional)
A block to paste into `~/.config/wasteland/hooks/autoskill.py`. With an active mission it
re-surfaces it on every prompt and flips a `blocked` mission back to `open` (the user is
answering). With no mission it suggests `/mythos-mode` when the prompt looks like real
multi-step work.

## Mission-file contract (`mythos_mission` v1)

- **Pointer:** `~/.cache/mythos/active` holds one line: the absolute path to the active
  mission markdown file. Override with the `MYTHOS_PTR` env var (used by the tests).
- **Frontmatter:** flat `key: value` lines between `---` fences (no nested YAML). Fields the
  hooks read: `status` (`open` | `blocked` | `done`), `nudges` (int), `last_open` (int, `-1`
  when unset), `nudge_cap` (int, optional, default 3), `cwd` (absolute path).
- **Body:** the goal line starts with `# G:`. Checklist markers: `- [ ]`, `- [~]`, `- [!]`
  count as **open**; `- [x]` / `- [X]` count as **done**.

The `/mythos-mode` command owns the mission lifecycle and writes this exact shape.

## Registration

`install.sh` copies both hooks to `~/.config/wasteland/hooks/`, makes them executable, and
prints the settings objects to merge (with machine-absolute command paths). It never edits
`settings.json`. The portable form to merge into `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "$HOME/.config/wasteland/hooks/mythos-stop.py", "timeout": 5 } ] }
    ],
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "$HOME/.config/wasteland/hooks/mythos-session.py", "timeout": 5 } ] }
    ]
  }
}
```

Add the `SessionStart` object as a new **unmatched** entry (no `matcher` key) alongside any
existing `SessionStart` hooks.

## Kill-switch

`export MYTHOS_HOOKS=0` makes both hooks exit immediately without touching anything. The cap
is tunable per run with `MYTHOS_NUDGE_CAP` (overrides the mission's `nudge_cap`).

## Uninstall

1. Remove the two objects from the `Stop` and `SessionStart` arrays in `settings.json`.
2. `rm ~/.config/wasteland/hooks/mythos-stop.py ~/.config/wasteland/hooks/mythos-session.py`.
3. If you added it, remove the snippet block from `autoskill.py`.

## Design guarantees

- **O(1) no-op without a pointer.** The first real check is `os.stat` on the pointer; if it
  is absent the hook returns before reading stdin or parsing anything.
- **Fail-silent.** The whole body runs under `try/except`; any error is swallowed and the
  hook still exits `0`, so it can never block Claude Code.
- **Bounded nudges.** No-progress stalls are capped, and `stop_hook_active` guarantees a hard
  stop is eventually honored. Termination holds: progress resets the counter, no-progress is
  bounded by the cap, and the stop ceiling is the backstop.
- **Atomic writes.** Every mission update is written to a temp file in the same directory and
  `os.replace`d into place, so a mission file is never left half-written.
