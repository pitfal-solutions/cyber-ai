"""
Shared host-side helpers for the agentic scenario's brain loops
(attacker_agent.py, defender_agent.py). Runs on the HOST, not in a
container -- Docker Desktop on macOS can't pass the Metal GPU through to a
container, so the actual LLM calls have to happen here; see
specs/architecture.md's "Local LLM runtime" section and
specs/local-llm-agents.md for the full reasoning.

Every network call in this module hits either local Ollama or one of the
range's published 127.0.0.1 ports -- the same trust boundary the
presenter's own browser already uses to reach the dashboard.

Stdlib only, matching the rest of this repo's Python.
"""
import json
import os
import random
import time
import urllib.error
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
TOOL_API = os.environ.get("TOOL_API", "http://127.0.0.1:9000")
DASHBOARD = os.environ.get("DASHBOARD", "http://127.0.0.1:8080")
TURN_TIMEOUT = float(os.environ.get("TURN_TIMEOUT", "30"))


def _http_json(method, url, body=None, timeout=15):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def get_tools(role):
    return _http_json("GET", f"{TOOL_API}/tools?role={role}")["tools"]


def call_tool(name, arguments):
    return _http_json("POST", f"{TOOL_API}/tools/{name}", body=arguments, timeout=20)


def investigate_incident():
    """The guaranteed, deterministic end-of-run report -- see tool-api's
    build_incident_report() docstring for why this isn't LLM-generated.
    Not under /tools/, so it never appears in the LLM's choosable menu."""
    return _http_json("POST", f"{TOOL_API}/investigate", body={}, timeout=20)


def signal_attacker_finished():
    _http_json("POST", f"{DASHBOARD}/control", body={"attacker_finished": True}, timeout=5)


def chat(model, messages, tools):
    """One turn against local Ollama. Raises on timeout/error -- callers
    treat that as a stall, per specs/local-llm-agents.md's resolved
    "fallback if a rehearsal run stalls" question.

    Moderate temperature: reliable tool-calling still matters (working
    agreement #1 in CLAUDE.md) -- rehearsal 2026-08-22 showed
    default-temperature models sometimes describing their next move in
    prose instead of calling a tool, fixed with a firmer system prompt --
    but some variety in which tool gets picked is the actual point of this
    scenario (founder feedback 2026-08-23: more variety, let the attacker
    try unconventional things). 0.2 was too deterministic for that; 0.4
    keeps tool-calling reliable in rehearsal while giving real run-to-run
    variety in strategy order and path guesses.

    Tool order is shuffled per call, not just once at loop start: models
    lean toward whichever tool is listed first (rehearsal 2026-08-23 showed
    sqli_login_bypass, always first in tool-api's registry, beating the
    equally-valid guess_common_credentials almost every run) -- shuffling
    only at loop start would just move the bias to a different fixed tool."""
    shuffled = list(tools)
    random.shuffle(shuffled)
    body = {
        "model": model, "messages": messages, "tools": shuffled, "stream": False,
        # num_ctx explicit, not left at Ollama's 4096 default: with MAX_TURNS
        # raised to 40 (founder feedback 2026-08-23) and the full tool-call/
        # tool-result history appended every turn, a long run genuinely
        # needs more room -- an overflowed context would silently drop
        # early turns, which is exactly the "forget what it already tried"
        # failure mode the higher turn cap was meant to avoid.
        "options": {"temperature": 0.4, "num_ctx": 8192},
    }
    result = _http_json("POST", f"{OLLAMA_HOST}/api/chat", body=body, timeout=TURN_TIMEOUT)
    return result["message"]


def get_control():
    try:
        return _http_json("GET", f"{DASHBOARD}/control", timeout=5)
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return {"paused": False, "delay_ms": 3000}


def wait_while_paused(actor):
    """Blocks in short increments while paused, so pause is responsive
    instead of stuck behind one long sleep -- see
    specs/local-llm-agents.md 'Pause / speed control'. Returns the control
    state as of the moment it un-blocks."""
    while True:
        control = get_control()
        if not control.get("paused"):
            return control
        set_status(actor, "paused")
        time.sleep(0.5)


def pace(control):
    """The presenter's live speed setting -- applied once per turn/reaction,
    after acting, same placement as the scripted scenario's step_delay()
    (scenarios/web-exploit/attacker/attacker.py)."""
    delay = (control or {}).get("delay_ms", 3000) / 1000.0
    if delay > 0:
        time.sleep(delay)


def set_status(actor, state):
    try:
        _http_json("POST", f"{DASHBOARD}/status", body={"actor": actor, "state": state}, timeout=5)
    except (urllib.error.URLError, json.JSONDecodeError):
        pass


def post_event(**ev):
    try:
        _http_json("POST", f"{DASHBOARD}/events", body=ev, timeout=5)
    except (urllib.error.URLError, json.JSONDecodeError):
        pass
    print(f"  >> [{ev.get('actor')}] {ev.get('description')}", flush=True)


def ensure_reasoning(args, fallback):
    """A smaller model doesn't always fill the tool schema's required
    'reasoning' field (rehearsal 2026-08-22: the 3B defender model omitted
    it on every call, while the 7B attacker model never did) -- rather than
    chase prompt-tuning on the weaker model, synthesize a fallback line so
    the dashboard still shows *something* instead of nothing. See
    specs/local-llm-agents.md's rehearsal notes."""
    if not (args.get("reasoning") or "").strip():
        args["reasoning"] = fallback
    return args


def parse_tool_call(msg):
    """Returns (name, args_dict) for the first tool call in an Ollama
    response message, or (None, None) if the model didn't call one."""
    calls = msg.get("tool_calls") or []
    if not calls:
        return None, None
    fn = calls[0]["function"]
    args = fn.get("arguments") or {}
    if isinstance(args, str):  # some models emit a JSON string instead of an object
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    return fn["name"], args
