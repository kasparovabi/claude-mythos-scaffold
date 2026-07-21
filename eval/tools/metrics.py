import json
import re
import sys

VERIF_RE = re.compile(
    r"(pytest|unittest|npm (run )?(test|build)|tsc|cargo (test|build|check)"
    r"|go (test|build)|make|ruff|eslint|python3? -m unittest"
    r"|python3? .*(test|main)\.py|check\.sh|\./check)"
)

ZERO = {
    "turns": 0,
    "tool_calls": 0,
    "parallel_ratio": 0.0,
    "verif_before_done": 0,
    "premature_qs": 0,
    "subagents_with_model": 0,
    "parallel_task_batches": 0,
    "in_tokens": 0,
    "out_tokens": 0,
    "cache_tokens": 0,
    "cost_usd": 0.0,
    "wall_s": 0.0,
}


def load_events(path):
    events = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except (ValueError, TypeError):
                continue
    return events


def message_blocks(ev):
    msg = ev.get("message")
    if not isinstance(msg, dict):
        return []
    content = msg.get("content")
    return content if isinstance(content, list) else []


def is_assistant(ev):
    return ev.get("type") == "assistant" and isinstance(ev.get("message"), dict)


def as_int(value):
    return int(value) if isinstance(value, (int, float)) else 0


def compute(events):
    m = dict(ZERO)
    assistant_count = 0
    assistant_with_tool = 0
    assistant_parallel = 0
    result_turns = None
    last_text_idx = -1
    verif_indices = []

    for i, ev in enumerate(events):
        if ev.get("type") == "result":
            if isinstance(ev.get("num_turns"), int):
                result_turns = ev["num_turns"]
            if isinstance(ev.get("total_cost_usd"), (int, float)):
                m["cost_usd"] = round(float(ev["total_cost_usd"]), 6)
            if isinstance(ev.get("duration_ms"), (int, float)):
                m["wall_s"] = round(ev["duration_ms"] / 1000.0, 2)
            continue

        if not is_assistant(ev):
            continue

        assistant_count += 1
        blocks = message_blocks(ev)
        tool_uses = [b for b in blocks if isinstance(b, dict) and b.get("type") == "tool_use"]
        texts = [b for b in blocks if isinstance(b, dict) and b.get("type") == "text"]
        task_blocks = [b for b in tool_uses if b.get("name") == "Task"]

        m["tool_calls"] += len(tool_uses)
        if tool_uses:
            assistant_with_tool += 1
        if len(tool_uses) >= 2:
            assistant_parallel += 1
        if texts:
            last_text_idx = i

        if not tool_uses and texts:
            joined = "".join(t.get("text", "") for t in texts).strip()
            if joined.endswith("?"):
                m["premature_qs"] += 1

        for tb in tool_uses:
            if tb.get("name") == "Bash":
                cmd = (tb.get("input") or {}).get("command", "")
                if isinstance(cmd, str) and VERIF_RE.search(cmd):
                    verif_indices.append(i)

        for tb in task_blocks:
            if (tb.get("input") or {}).get("model"):
                m["subagents_with_model"] += 1
        if len(task_blocks) >= 2:
            m["parallel_task_batches"] += 1

        usage = ev["message"].get("usage")
        if isinstance(usage, dict):
            m["in_tokens"] += as_int(usage.get("input_tokens"))
            m["out_tokens"] += as_int(usage.get("output_tokens"))
            m["cache_tokens"] += as_int(usage.get("cache_read_input_tokens"))
            m["cache_tokens"] += as_int(usage.get("cache_creation_input_tokens"))

    m["turns"] = result_turns if result_turns is not None else assistant_count
    if assistant_with_tool:
        m["parallel_ratio"] = round(assistant_parallel / assistant_with_tool, 2)
    m["verif_before_done"] = 1 if any(idx < last_text_idx for idx in verif_indices) else 0
    return m


def main():
    if len(sys.argv) < 2:
        out = dict(ZERO)
        out["error"] = "usage: metrics.py <run.jsonl>"
        print(json.dumps(out))
        return

    try:
        events = load_events(sys.argv[1])
    except OSError as exc:
        out = dict(ZERO)
        out["error"] = "read_failed: " + exc.__class__.__name__
        print(json.dumps(out))
        return

    if not events:
        out = dict(ZERO)
        out["error"] = "empty_or_unparseable"
        print(json.dumps(out))
        return

    print(json.dumps(compute(events)))


if __name__ == "__main__":
    main()
