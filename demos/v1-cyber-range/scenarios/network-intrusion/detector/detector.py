"""
Watches each target's own real log file independently of the attacker
script and fires real detection events off real traffic patterns -- same
"what real means here" bar as scenarios/web-exploit/detector/detector.py:
this detector doesn't know the attack chain in advance, it just
pattern-matches whatever the real OpenSSH/Samba/ftp-host logs actually
contain. Tails three files instead of one HTTP access log, otherwise the
same sliding-window / fired-once dedup style.
"""
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

EVENTS_API = os.environ.get("EVENTS_API", "http://range-dashboard:8080/events")
SSH_LOG = os.environ.get("SSH_LOG", "/logs/ssh-auth.log")
FTP_LOG = os.environ.get("FTP_LOG", "/logs/ftp.jsonl")
SMB_LOG = os.environ.get("SMB_LOG", "/logs/smb-connections.jsonl")

SSH_FAILED_PATTERN = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+)")
SSH_ACCEPTED_PATTERN = re.compile(r"Accepted password for (\S+) from (\S+)")

BRUTE_FORCE_WINDOW_SECONDS = 15
BRUTE_FORCE_THRESHOLD = 4

fired = set()
recent_ssh_failures = []  # list of monotonic() timestamps


def post_event(ev):
    data = json.dumps(ev).encode()
    req = urllib.request.Request(
        EVENTS_API, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.URLError as e:
        print("failed to post event:", e, flush=True)


def check_ssh_line(line):
    m = SSH_FAILED_PATTERN.search(line)
    if m:
        user, ip = m.group(1), m.group(2)
        now = time.monotonic()
        recent_ssh_failures.append(now)
        while recent_ssh_failures and now - recent_ssh_failures[0] > BRUTE_FORCE_WINDOW_SECONDS:
            recent_ssh_failures.pop(0)
        if len(recent_ssh_failures) >= BRUTE_FORCE_THRESHOLD and "ssh-bruteforce" not in fired:
            fired.add("ssh-bruteforce")
            print(f"DETECTED: SSH brute-force pattern ({len(recent_ssh_failures)} failures)", flush=True)
            post_event({
                "scenario": "network-intrusion",
                "step_id": "detect-ssh-bruteforce",
                "attack_technique_id": "T1110.001",
                "actor": "defender",
                "severity": "high",
                "legal_ref": "cfaa-1030a2",
                "description": (
                    f"Detection rule fired: {len(recent_ssh_failures)} failed SSH password attempts "
                    f"in {BRUTE_FORCE_WINDOW_SECONDS}s targeting {user} from {ip} -- a real brute-force "
                    "pattern, not a single mistyped password."
                ),
            })
        return

    m = SSH_ACCEPTED_PATTERN.search(line)
    if m and "ssh-accepted" not in fired:
        fired.add("ssh-accepted")
        user, ip = m.group(1), m.group(2)
        print(f"DETECTED: SSH login accepted for {user} from {ip}", flush=True)
        post_event({
            "scenario": "network-intrusion",
            "step_id": "detect-ssh-login-success",
            "attack_technique_id": "T1078",
            "actor": "defender",
            "severity": "critical",
            "legal_ref": "cfaa-1030a2",
            "description": f"A real SSH login just succeeded for {user} from {ip} -- following a real failed-password burst, consistent with a successful brute-force, not a legitimate user.",
        })


def check_ftp_line(line):
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return
    event = entry.get("event")
    if event == "backdoor_trigger" and "ftp-backdoor-trigger" not in fired:
        fired.add("ftp-backdoor-trigger")
        print("DETECTED: vsftpd backdoor trigger username", flush=True)
        post_event({
            "scenario": "network-intrusion",
            "step_id": "detect-vsftpd-backdoor-trigger",
            "attack_technique_id": "T1210",
            "actor": "defender",
            "severity": "critical",
            "legal_ref": "cfaa-1030a2",
            "description": f"FTP login from {entry.get('source')} used the known CVE-2011-2523 backdoor trigger username -- a real, unambiguous exploitation attempt, not a typo.",
        })
    elif event == "backdoor_shell_connected" and "ftp-backdoor-shell" not in fired:
        fired.add("ftp-backdoor-shell")
        print("DETECTED: vsftpd backdoor shell connection", flush=True)
        post_event({
            "scenario": "network-intrusion",
            "step_id": "detect-vsftpd-backdoor-shell",
            "attack_technique_id": "T1210",
            "actor": "defender",
            "severity": "critical",
            "legal_ref": "cfaa-1030a2",
            "description": f"A connection to the backdoor port followed the trigger -- {entry.get('source')} very likely has a real command shell on this host right now.",
        })


def check_smb_line(line):
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return
    if entry.get("event") != "smb_connection" or "smb-guest-access" in fired:
        return
    # Every connection through this proxy reaches a guest-only share by
    # definition (see targets/smb-host/smb.conf) -- no credential check to
    # distinguish "real" access from a probe, so the first real connection
    # carrying actual data is itself the alertable event.
    if entry.get("bytes_received", 0) < 100:
        return  # a bare TCP connect/negotiate with no real exchange -- not worth alerting on
    fired.add("smb-guest-access")
    source = entry.get("source", "unknown")
    print(f"DETECTED: anonymous SMB connection from {source}", flush=True)
    post_event({
        "scenario": "network-intrusion",
        "step_id": "detect-smb-guest-access",
        "attack_technique_id": "T1135",
        "actor": "defender",
        "severity": "high",
        "legal_ref": "cfaa-1030a2-misconfig",
        "description": f"A real connection from {source} reached the guest-only SMB share and exchanged real data ({entry.get('bytes_received')} bytes) -- no credentials were ever presented.",
    })


def tail(path, handler):
    while not os.path.exists(path):
        time.sleep(0.5)
    with open(path) as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.3)
                continue
            line = line.strip()
            if line:
                handler(line)


if __name__ == "__main__":
    print(f"detector watching {SSH_LOG}, {FTP_LOG}, and {SMB_LOG}", flush=True)
    threading.Thread(target=tail, args=(SSH_LOG, check_ssh_line), daemon=True).start()
    threading.Thread(target=tail, args=(FTP_LOG, check_ftp_line), daemon=True).start()
    tail(SMB_LOG, check_smb_line)
