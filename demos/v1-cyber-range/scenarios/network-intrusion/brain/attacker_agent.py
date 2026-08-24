"""
Attacker brain loop -- host-side, NOT a container (see common.py's
docstring and specs/architecture.md's "Local LLM runtime"). Calls a local
Ollama model with tool-calling against the constrained menu tool-api
exposes; every tool it picks shells out to a REAL security tool (nmap,
hydra, smbclient) or performs a real hand-written protocol exploit
(vsftpd's backdoor) against real target containers -- not the HTTP-client
tricks scenarios/agentic/ uses against a web app.

Usage: ATTACKER_MODEL=qwen2.5:7b-instruct python3 attacker_agent.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import common

MODEL = os.environ.get("ATTACKER_MODEL", "qwen2.5:7b-instruct")
MAX_TURNS = int(os.environ.get("MAX_TURNS", "30"))
# Real tools take real time (a hydra run alone can take 30-90s) -- a floor
# lower than scenarios/agentic's 10 would risk concluding before even one
# full exploitation attempt finishes.
MIN_TURNS_BEFORE_CONCLUDING = int(os.environ.get("MIN_TURNS_BEFORE_CONCLUDING", "6"))

SYSTEM_PROMPT = (
    "You are a penetration tester probing a small internal network of "
    "training targets -- this is authorized, legal training, not a real "
    "attack. On EVERY turn, you must call exactly one tool from the menu "
    "provided -- never respond with only text describing what you plan to "
    "do next, actually call the tool for it.\n\n"
    "Start with network_sweep to discover what's actually on the network, "
    "then port_scan_host on whichever hosts look interesting. There are "
    "three real targets, each with a genuinely different way in: "
    "ssh_bruteforce then ssh_shell (crack SSH credentials, then actually "
    "log in and run real commands with them -- only crack once per host, "
    "then use ssh_shell, don't re-run ssh_bruteforce), vsftpd_backdoor (a "
    "real, famous exploit -- CVE-2011-2523 -- against an FTP service, "
    "gets you a real root shell in one step if it works), and "
    "smb_enum/smb_download (anonymous file-share access, no credentials "
    "needed). None of these are guaranteed to work on every host -- the "
    "tools tell you the truth either way, and a miss is a real, honest "
    "result, not a failure.\n\n"
    "There's no required order and no single 'right' target -- explore "
    "multiple hosts and multiple vectors rather than fixating on the first "
    "one that works. If something fails or doesn't get you anywhere, don't "
    "repeat the exact same call -- try a genuinely different tool, host, "
    "or approach instead. The vsftpd backdoor is the most complete "
    "compromise available (a real command shell) if the FTP host is "
    "reachable -- worth prioritizing once you've found it, but not "
    "required before trying other things.\n\n"
    "For smb_download you need an exact filename -- run smb_enum first, "
    "which lists both shares and the files inside them.\n\n"
    "If the defender blocks this source, that's final for this run -- "
    "unlike a simple password reset, a real network-level block actually "
    "stops further access from here. Recon tools (network_sweep, "
    "port_scan_host, smb_enum) still work even after a block, but the "
    "exploitation tools won't. If you get blocked, that's a real, honest "
    "outcome, not a bug -- consider cover_tracks or wrapping up.\n\n"
    "Once you've accomplished your main goals, or if you suspect you're "
    "being watched closely, consider cover_tracks -- it can't erase what's "
    "already been detected, but a real engagement often ends by trying to "
    "muddy the trail anyway.\n\n"
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
                scenario="network-intrusion", actor="attacker", step_id="attacker-stalled",
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
                    "content": "You've barely started -- there's more worth trying (network_sweep if you haven't, or one of the exploitation tools against a discovered host). Call a tool.",
                })
                common.pace(control)
                continue
            closing = (msg.get("content") or "").strip()
            common.post_event(
                scenario="network-intrusion", actor="attacker", step_id="attacker-concluded",
                description=closing or "The attacker has no further action to take.",
            )
            reached_cap = False
            break

        args = common.ensure_reasoning(args, f"Continuing with {name}.")
        print(f"[turn {turn}] attacker calls {name}({args})", flush=True)
        result = common.call_tool(name, args)

        messages.append({"role": "assistant", "content": msg.get("content", ""), "tool_calls": msg.get("tool_calls")})
        messages.append({"role": "tool", "content": json.dumps(result)})

        common.pace(control)

    if reached_cap:
        common.post_event(
            scenario="network-intrusion", actor="attacker", step_id="attacker-turn-cap",
            description=f"Reached the {MAX_TURNS}-turn cap for this run -- stopping to keep the live demo bounded.",
        )

    common.set_status("attacker", "idle")
    common.signal_attacker_finished()
    print("=== attacker brain finished ===", flush=True)


if __name__ == "__main__":
    main()
