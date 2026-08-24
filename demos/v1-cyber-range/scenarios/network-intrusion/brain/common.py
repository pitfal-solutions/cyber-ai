"""
Shared host-side helpers for the network-intrusion scenario's brain loops
(attacker_agent.py, defender_agent.py). Runs on the HOST, not in a
container -- Docker Desktop on macOS can't pass the Metal GPU through to a
container, so the actual LLM calls have to happen here; see
specs/architecture.md's "Local LLM runtime" section and
specs/local-llm-agents.md for the full reasoning.

Identical to scenarios/agentic/brain/common.py except TOOL_API's default
port (9100, not 9000 -- this scenario's tool-api publishes a different
port so both scenarios' brains could theoretically run side by side). All
the reliability lessons from that scenario's rehearsal (tool shuffling,
ensure_reasoning fallback, num_ctx bump, moderate temperature) are generic
-- reused verbatim, not re-derived.

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
TOOL_API = os.environ.get("TOOL_API", "http://127.0.0.1:9100")
DASHBOARD = os.environ.get("DASHBOARD", "http://127.0.0.1:8080")
# Higher than scenarios/agentic's 30s: rehearsal 2026-08-24 showed a real
# turn timeout after a verbose tool result (vsftpd_backdoor's raw shell
# output) bloated context right when both models were concurrently loaded.
# Trimmed that noise at the source too (see tool-api's tool_vsftpd_backdoor),
# but kept the extra headroom since real tool round-trips in this domain
# (hydra, nmap) are already slower than the web scenario's HTTP calls.
TURN_TIMEOUT = float(os.environ.get("TURN_TIMEOUT", "45"))


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
    return _http_json("POST", f"{TOOL_API}/tools/{name}", body=arguments, timeout=90)


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
    "fallback if a rehearsal run stalls" question. Moderate temperature and
    per-turn tool shuffling: see scenarios/agentic/brain/common.py's chat()
    docstring for the rehearsal findings behind both -- generic lessons
    about small-model tool-calling reliability, reused verbatim here."""
    shuffled = list(tools)
    random.shuffle(shuffled)
    body = {
        "model": model, "messages": messages, "tools": shuffled, "stream": False,
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
    after acting."""
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
    'reasoning' field -- rather than chase prompt-tuning on the weaker
    model, synthesize a fallback line so the dashboard still shows
    *something* instead of nothing. See
    scenarios/agentic/specs rehearsal notes for where this was first found."""
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
