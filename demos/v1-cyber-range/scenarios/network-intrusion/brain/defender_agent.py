"""
Defender brain loop -- host-side, NOT a container (see common.py's
docstring and specs/architecture.md's "Local LLM runtime"). Polls
tool-api's real, independently-detected alerts directly (no LLM call
needed just to check whether anything's new) and only engages the model
once there's something to react to. Same structure as
scenarios/agentic/brain/defender_agent.py -- see that file's comments for
the rehearsal findings behind the design (defender-signals-before-block
gating, no early-stop on the first block).

Usage: DEFENDER_MODEL=qwen2.5:3b-instruct python3 defender_agent.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import common

MODEL = os.environ.get("DEFENDER_MODEL", "qwen2.5:3b-instruct")
MAX_REACTIONS = int(os.environ.get("MAX_REACTIONS", "15"))
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "2"))
RUN_TIMEOUT = float(os.environ.get("RUN_TIMEOUT", "600"))

SYSTEM_PROMPT = (
    "You are a security analyst monitoring a small internal network of "
    "training targets. You'll be shown newly-fired detection alert(s) from "
    "real, independent detectors watching each host's own real logs. Call "
    "exactly one response tool: flag_session, block_attacker, or "
    "escalate_to_soc.\n\n"
    "Real SOC analysts don't jump straight to blocking on the first alert "
    "-- an early block also cuts off your own chance to observe what the "
    "attacker is actually doing. Use flag_session for a first-time or "
    "lower-severity alert to build a paper trail while you keep watching. "
    "Reserve block_attacker for once you have real confidence this is an "
    "ongoing, serious attack -- typically after you've already flagged "
    "this session at least once or twice, or the alert itself is severe "
    "(e.g. a real root shell via the vsftpd backdoor). Calling "
    "block_attacker too early with too little evidence will just flag "
    "instead -- that's expected, not an error.\n\n"
    "Unlike a simple credential reset, block_attacker here is a real "
    "network-level block and genuinely stops further exploitation from "
    "this source -- so once you've blocked, you likely won't see much "
    "more from this same attacker. That's a good outcome, not something "
    "to second-guess."
)


def build_alert_message(alerts):
    lines = [f"- {a.get('description', a.get('step_id'))}" for a in alerts]
    return "New detection alert(s):\n" + "\n".join(lines)


def main():
    tools = [t for t in common.get_tools("defender") if t["function"]["name"] != "check_alerts"]
    reactions = 0
    start = time.monotonic()

    print(f"=== defender brain starting (model={MODEL}) ===", flush=True)

    while reactions < MAX_REACTIONS and (time.monotonic() - start) < RUN_TIMEOUT:
        common.wait_while_paused("defender")
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
                scenario="network-intrusion", actor="defender", step_id="defender-stalled",
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
                scenario="network-intrusion", actor="defender", step_id="defender-noted",
                description=(msg.get("content") or "Reviewed the alert; no action taken yet.").strip(),
            )
            reactions += 1
            common.pace(control)
            if engagement_over:
                break
            continue

        args = common.ensure_reasoning(args, f"Reacting to: {alerts[-1].get('description', alerts[-1].get('step_id'))}")
        print(f"[reaction {reactions + 1}] defender calls {name}({args})", flush=True)
        common.call_tool(name, args)
        reactions += 1
        common.pace(control)
        if engagement_over:
            break

    common.post_event(
        scenario="network-intrusion", actor="defender", step_id="defender-stopped-watching",
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
