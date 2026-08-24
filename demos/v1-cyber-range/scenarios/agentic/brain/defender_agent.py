"""
Defender brain loop -- host-side, NOT a container (see common.py's
docstring and specs/architecture.md's "Local LLM runtime"). Polls
tool-api's real, independently-detected alerts directly (no LLM call
needed just to check whether anything's new -- a human analyst doesn't
"think" when their screen is empty) and only engages the model once
there's something to react to.

Usage: DEFENDER_MODEL=qwen2.5:3b-instruct python3 defender_agent.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import common

MODEL = os.environ.get("DEFENDER_MODEL", "qwen2.5:3b-instruct")
# block_attacker only revokes a session now, it doesn't end the engagement
# (see tool-api's tool_block_attacker) -- a persistent attacker keeps
# coming back, so the defender needs room to react more than once. Founder
# feedback 2026-08-23: attacker's turn cap was raised from 14 to 40 for the
# same reason.
MAX_REACTIONS = int(os.environ.get("MAX_REACTIONS", "15"))
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "2"))
RUN_TIMEOUT = float(os.environ.get("RUN_TIMEOUT", "600"))

SYSTEM_PROMPT = (
    "You are a security analyst monitoring OWASP Juice Shop, an intentionally "
    "vulnerable practice web app. You'll be shown newly-fired detection "
    "alert(s) from a real, independent detector. Call exactly one response "
    "tool: flag_session, block_attacker, or escalate_to_soc.\n\n"
    "Real SOC analysts don't jump straight to blocking on the first alert -- "
    "an early block also cuts off your own chance to observe what the "
    "attacker is actually doing. Use flag_session for a first-time or "
    "lower-severity alert (a misconfigured file, a single suspicious "
    "request) to build a paper trail while you keep watching. Reserve "
    "block_attacker for once you have real confidence this is an ongoing, "
    "serious attack -- typically after you've already flagged this session "
    "at least once or twice, or the alert itself is severe (e.g. a "
    "completed account takeover). Calling block_attacker too early with "
    "too little evidence will just flag instead -- that's expected, not an "
    "error, keep responding to whatever comes next.\n\n"
    "block_attacker only revokes the attacker's current session -- it costs "
    "them a turn to recover, but doesn't fix the underlying vulnerability, so "
    "don't assume blocking once means you're done watching. If new alerts "
    "keep appearing after you've already blocked, that's the same attacker "
    "back with a new session -- keep responding."
)


def build_alert_message(alerts):
    lines = [f"- {a.get('description', a.get('step_id'))}" for a in alerts]
    return "New detection alert(s):\n" + "\n".join(lines)


def main():
    # check_alerts is excluded here: the loop below already polls it
    # directly, so the model only ever sees tools that actually respond to
    # an alert -- keeps a small model from wasting a turn re-checking
    # something it was just handed in the prompt.
    tools = [t for t in common.get_tools("defender") if t["function"]["name"] != "check_alerts"]
    reactions = 0
    start = time.monotonic()

    print(f"=== defender brain starting (model={MODEL}) ===", flush=True)

    while reactions < MAX_REACTIONS and (time.monotonic() - start) < RUN_TIMEOUT:
        common.wait_while_paused("defender")
        # run-agentic.sh sets this once the attacker brain loop exits. Still
        # run this iteration's check_alerts/react below first, so a trailing
        # alert from the attacker's last action gets one real chance to be
        # handled -- only stop *after* that, not before it.
        engagement_over = common.get_control().get("attacker_finished", False)
        try:
            check = common.call_tool("check_alerts", {"reasoning": "periodic monitoring check"})
        except Exception as e:
            print(f"[warn] check_alerts failed: {e}", file=sys.stderr, flush=True)
            if engagement_over:
                break
            time.sleep(POLL_INTERVAL)
            continue

        alerts = check.get("alerts") or []
        if not alerts:
            if engagement_over:
                break
            time.sleep(POLL_INTERVAL)
            continue

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_alert_message(alerts)},
        ]
        common.set_status("defender", "thinking")
        try:
            msg = common.chat(MODEL, messages, tools)
        except Exception as e:
            common.set_status("defender", "idle")
            common.post_event(
                scenario="agentic", actor="defender", step_id="defender-stalled",
                description="The defender model didn't respond in time to a new alert -- moving on.",
                severity="medium",
            )
            print(f"[error] defender turn: {e}", file=sys.stderr, flush=True)
            if engagement_over:
                break
            time.sleep(POLL_INTERVAL)
            continue
        common.set_status("defender", "idle")

        control = common.get_control()
        name, args = common.parse_tool_call(msg)
        if name is None:
            common.post_event(
                scenario="agentic", actor="defender", step_id="defender-noted",
                description=(msg.get("content") or "Reviewed the alert; no action taken yet.").strip(),
            )
            reactions += 1
            common.pace(control)
            if engagement_over:
                break
            continue

        args = common.ensure_reasoning(args, f"Reacting to: {alerts[-1].get('description', alerts[-1].get('step_id'))}")
        print(f"[reaction {reactions + 1}] defender calls {name}({args})", flush=True)
        common.call_tool(name, args)  # the event itself is posted by the tool handler
        reactions += 1
        common.pace(control)
        if engagement_over:
            break

    common.post_event(
        scenario="agentic", actor="defender", step_id="defender-stopped-watching",
        description=(
            "Attacker engagement over -- moving to final investigation."
            if engagement_over else
            "Reaction cap or timeout reached -- moving to final investigation."
        ),
    )
    common.set_status("defender", "thinking")
    try:
        result = common.investigate_incident()
        print(f"=== incident report compiled ({result.get('confirmed_count', '?')} confirmed finding(s)) ===", flush=True)
    except Exception as e:
        print(f"[error] investigate_incident failed: {e}", file=sys.stderr, flush=True)
    common.set_status("defender", "idle")
    print("=== defender brain finished ===", flush=True)


if __name__ == "__main__":
    main()
