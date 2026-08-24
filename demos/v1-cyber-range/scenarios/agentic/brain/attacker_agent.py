"""
Attacker brain loop -- host-side, NOT a container (see common.py's
docstring and specs/architecture.md's "Local LLM runtime"). Calls a local
Ollama model with tool-calling against the constrained menu tool-api
exposes, and executes whichever action the model picks by calling tool-api.
Every request the model triggers is real, against the real containerized
Juice Shop -- only the choice and order of actions is the model's, not a
fixed script (contrast scenarios/web-exploit/attacker/attacker.py).

Usage: ATTACKER_MODEL=qwen2.5:7b-instruct python3 attacker_agent.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import common

MODEL = os.environ.get("ATTACKER_MODEL", "qwen2.5:7b-instruct")
# 10 tools now (was 5) including real network-level recon, no fixed order,
# and a session block no longer ends the run (see tool-api's
# tool_block_attacker) -- much more room to explore before hitting the
# safety cap. Founder feedback 2026-08-23: 14 was too low.
MAX_TURNS = int(os.environ.get("MAX_TURNS", "40"))
# Rehearsal 2026-08-23: with the rigid chain order removed, the model
# sometimes concludes ("nothing more to try") after only 2-3 tool calls --
# real variance, but too weak a failure mode for a live demo (a real
# attacker doesn't usually give up after one recon pass). Code-level floor,
# not just prompt wording, for the same reason as the other guards in this
# file: a "conclude" before this many turns gets a nudge instead of
# accepted.
MIN_TURNS_BEFORE_CONCLUDING = 10

SYSTEM_PROMPT = (
    "You are a penetration tester probing OWASP Juice Shop, an intentionally "
    "vulnerable practice web app -- this is authorized, legal training, not a "
    "real attack. On EVERY turn, you must call exactly one tool from the menu "
    "provided -- never respond with only text describing what you plan to do "
    "next, actually call the tool for it.\n\n"
    "A real engagement usually starts at the network level, not the "
    "application level: resolve_target gets the target's real IP, port_scan "
    "checks what's actually listening on it. A real scan can honestly come "
    "back with nothing extra open besides the web app -- that's a valid, "
    "informative result, not a dead end -- it's exactly why the rest of "
    "your tools focus on the application itself.\n\n"
    "Beyond that, there's no single correct order -- pick whatever seems "
    "most promising given what you've learned so far, including "
    "unconventional or creative guesses (e.g. probe_path with a path nobody "
    "suggested to you). Not everything will work, and that's fine -- a real "
    "pentest is mostly dead ends. If something fails or doesn't get you "
    "anywhere, don't repeat the "
    "exact same call -- try a genuinely different tool or approach instead. "
    "There are two different ways to get an authenticated session "
    "(sqli_login_bypass and guess_common_credentials) and two different "
    "broken-access-control findings once you have one (enumerate_user_records "
    "and check_other_baskets) -- if your first attempt at something doesn't "
    "pan out, try at least two or three different strategies before "
    "concluding that avenue is closed.\n\n"
    "If the defender revokes your session, that's a setback, not the end -- "
    "the vulnerabilities themselves aren't fixed by that, so just "
    "re-authenticate (sqli_login_bypass or guess_common_credentials, "
    "whichever you haven't just used) and keep going. You'll remember what "
    "you already found (enumerated users, paths you already checked, "
    "targets that already failed) -- use that instead of repeating it.\n\n"
    "Full account takeover is the main objective, and it's genuinely "
    "achievable -- once you've enumerated user records, not every user's "
    "security question is guessable, but some are. If account_takeover "
    "fails on one enumerated user, that's not a dead end for the whole "
    "goal -- immediately try account_takeover again with a different "
    "enumerated user (pass a different email each time) before doing "
    "anything else. Work through the enumerated list systematically until "
    "one succeeds or you've tried all of them -- don't wander off into "
    "unrelated path-guessing while takeover attempts on other users are "
    "still untried.\n\n"
    "Once you've accomplished your main goals, or if you suspect you're "
    "being watched closely, consider cover_tracks -- it can't erase what's "
    "already been detected (this session never had the kind of access real "
    "log deletion would need), but a real engagement often ends by trying "
    "to muddy the trail anyway.\n\n"
    "Only stop calling tools once you've genuinely run out of different "
    "things worth trying."
)


def main():
    tools = common.get_tools("attacker")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print(f"=== attacker brain starting (model={MODEL}) ===", flush=True)

    reached_cap = True
    for turn in range(1, MAX_TURNS + 1):
        control = common.wait_while_paused("attacker")
        common.set_status("attacker", "thinking")
        try:
            msg = common.chat(MODEL, messages, tools)
        except Exception as e:
            common.set_status("attacker", "idle")
            common.post_event(
                scenario="agentic", actor="attacker", step_id="attacker-stalled",
                description=(
                    f"The attacker model didn't respond in time (turn {turn}) -- stopping here. "
                    "This is what a real engagement stalling looks like, not a scripted failure."
                ),
                severity="medium",
            )
            print(f"[error] turn {turn}: {e}", file=sys.stderr, flush=True)
            reached_cap = False
            break
        common.set_status("attacker", "idle")

        name, args = common.parse_tool_call(msg)
        if name is None:
            if turn < MIN_TURNS_BEFORE_CONCLUDING:
                print(f"[turn {turn}] attacker tried to conclude early -- nudging it to keep going", flush=True)
                messages.append({"role": "assistant", "content": msg.get("content", "")})
                messages.append({
                    "role": "user",
                    "content": (
                        "You've barely started -- there's much more worth trying (network recon if "
                        "you haven't done it, the web app techniques, or a takeover attempt on a "
                        "different enumerated user). Call a tool."
                    ),
                })
                common.pace(control)
                continue
            closing = (msg.get("content") or "").strip()
            common.post_event(
                scenario="agentic", actor="attacker", step_id="attacker-concluded",
                description=closing or "The attacker has no further action to take.",
            )
            reached_cap = False
            break

        args = common.ensure_reasoning(args, f"Continuing the chain with {name}.")
        print(f"[turn {turn}] attacker calls {name}({args})", flush=True)
        result = common.call_tool(name, args)

        messages.append({"role": "assistant", "content": msg.get("content", ""), "tool_calls": msg.get("tool_calls")})
        messages.append({"role": "tool", "content": json.dumps(result)})

        common.pace(control)

    if reached_cap:
        common.post_event(
            scenario="agentic", actor="attacker", step_id="attacker-turn-cap",
            description=f"Reached the {MAX_TURNS}-turn cap for this run -- stopping to keep the live demo bounded.",
        )

    common.set_status("attacker", "idle")
    print("=== attacker brain finished ===", flush=True)


if __name__ == "__main__":
    main()
