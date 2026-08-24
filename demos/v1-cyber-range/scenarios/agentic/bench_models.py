"""
Fires a representative tool-calling turn at each candidate model while both
are concurrently loaded, and times it. Companion to bench-models.sh -- see
../../../specs/local-llm-agents.md ("Model selection + concurrency shape")
for how the result should be recorded.

Stdlib only, matching the rest of this repo's Python (see
core/range-dashboard/server.py).
"""
import json
import sys
import time
import urllib.request

# A trimmed stand-in for the real constrained action menu the attacker
# brain will use (see specs/local-llm-agents.md) -- just enough tool-
# calling surface to exercise the same code path the real loop will hit.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "attempt_sqli_login_bypass",
            "description": "Attempt a SQL-injection login bypass against the target's login endpoint.",
            "parameters": {
                "type": "object",
                "properties": {"endpoint": {"type": "string"}},
                "required": ["endpoint"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "enumerate_endpoint",
            "description": "Probe a guessable URL for exposed data.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
]

ATTACKER_PROMPT = (
    "You are a penetration tester probing a practice web app. Choose exactly "
    "one tool call for your next step. Do not explain, just call a tool."
)
DEFENDER_PROMPT = (
    "You are a security analyst reviewing a new alert: a login request with a "
    "SQL-injection pattern was just detected. In one sentence, say what you'd "
    "check next."
)


def timed_chat(host, model, system_prompt, use_tools):
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}],
        "stream": False,
    }
    if use_tools:
        body["tools"] = TOOLS
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{host}/api/chat", data=data, headers={"Content-Type": "application/json"}
    )
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
    elapsed = time.monotonic() - start
    return elapsed, result


def main():
    attacker_model, defender_model, host = sys.argv[1], sys.argv[2], sys.argv[3]

    print(f"[attacker:{attacker_model}] cold-start tool-calling turn...")
    elapsed, result = timed_chat(host, attacker_model, ATTACKER_PROMPT, use_tools=True)
    msg = result.get("message", {})
    tool_calls = msg.get("tool_calls")
    print(f"  {elapsed:.1f}s -- tool_calls={tool_calls!r}")
    if not tool_calls:
        print(f"  [warn] no tool call returned -- content was: {msg.get('content', '')[:200]!r}")

    print(f"[defender:{defender_model}] cold-start turn (loads alongside attacker)...")
    elapsed, result = timed_chat(host, defender_model, DEFENDER_PROMPT, use_tools=False)
    msg = result.get("message", {})
    print(f"  {elapsed:.1f}s -- content={msg.get('content', '')[:200]!r}")

    print(f"[attacker:{attacker_model}] warm turn, both models loaded concurrently...")
    elapsed, result = timed_chat(host, attacker_model, ATTACKER_PROMPT, use_tools=True)
    msg = result.get("message", {})
    print(f"  {elapsed:.1f}s -- tool_calls={msg.get('tool_calls')!r}")

    print(f"[defender:{defender_model}] warm turn, both models loaded concurrently...")
    elapsed, result = timed_chat(host, defender_model, DEFENDER_PROMPT, use_tools=False)
    msg = result.get("message", {})
    print(f"  {elapsed:.1f}s -- content={msg.get('content', '')[:200]!r}")


if __name__ == "__main__":
    main()
