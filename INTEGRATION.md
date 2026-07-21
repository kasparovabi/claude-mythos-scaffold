# Integration: route, don't duplicate

The scaffold delegates overlapping concerns to neighbors when they exist. Rows marked
(optional) degrade gracefully when the neighbor is absent.

| Concern | Owner | Rule |
|---|---|---|
| Write-time code discipline | `guard-20` skill (optional) | Load before the first edit of any coding task; the scaffold never restates its rules. Absent: the kernel's verification section still applies. |
| Final verification fleet | `audit-20` skill (optional) | Runs once, only when the user declares the project final. Mid-iteration verification is always typecheck + tests + build + smoke. |
| Minimalism / YAGNI | `ponytail` skill (optional) | Conflicts resolve in favor of guard-20 (trust-boundary validation, error paths, timeouts are never "simplified away"). |
| Sub-agent orchestration doctrine | kernel + `/mythos-mode` step 3 | Explicit model per spawn, reference-not-content returns, blackboard files, parallel launches in one message, no delegation under ~5K tokens, cheap-verify every verdict. |
| Budget metering | `~/.cache/wasteland/fable-share` (optional) | Mission `budget_flag` mirrors it at creation. `yellow`: prefer sonnet workers, avoid opus fan-out. `red`: no fan-out, defer heavy work, tell the user. Absent: `green`. |
| Cross-session memory | host memory surfaces (auto-memory, vault, claude-mem) | The kernel's memory trigger points at whatever the host session provides; `core/memory.md` covers the heavy variant. |
| Loop / schedule runner | ralph-loop plugin, cron, `claude -p` | The scaffold supplies `core/headless.md` (preamble) and the mission file (cross-run state); it is never the runner itself. |
| Prompt-time routing | UserPromptSubmit router (optional) | `hooks/autoskill-mythos-rule.snippet` documents the rule: remind about the active mission, or hint `/mythos-mode` on big multi-step prompts. |
| Stop-time persistence | `hooks/mythos-stop.py` | Blocks premature stops while mission items are open; bounded by the nudge cap; disabled entirely by `MYTHOS_HOOKS=0` or pointer absence. |
| Compaction survival | `hooks/mythos-session.py` | Re-surfaces the active mission after compact/resume/clear; silent on unrelated projects at startup. |
