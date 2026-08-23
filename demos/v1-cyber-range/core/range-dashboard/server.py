"""
Core range dashboard. Scenario-agnostic: reads events + legal-map JSON that
whatever scenario is active drops into the shared /data volume. See
specs/architecture.md's "shared event stream" section.

Stdlib only, on purpose — no pip install at build time, no external
dependency to break offline/air-gapped operation.
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

EVENTS_PATH = os.environ.get("EVENTS_PATH", "/data/events.jsonl")
LEGAL_MAP_PATH = os.environ.get("LEGAL_MAP_PATH", "/data/legal-map.json")
PORT = int(os.environ.get("PORT", "8080"))
LOCK = threading.Lock()

INDEX_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Cyber Range</title>
<style>
  :root {
    --bg: #0b0f14;
    --panel: #121820;
    --border: #263140;
    --text: #e8edf2;
    --dim: #8ea0b3;
    --attacker: #ff5c5c;
    --defender: #4cc3ff;
    --legal: #ffd166;
    --tbd: #666;
    --crit: #ff5c5c;
    --high: #ff9d4c;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
    height: 100vh;
    overflow: hidden;
  }
  header {
    padding: 14px 24px;
    border-bottom: 2px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  /* Sizes below are tuned for projector legibility (lecture-hall viewing
     distance), not a laptop screen up close -- this dashboard's only real
     use case is presentation, so there's no smaller "desk mode" to balance
     against. See REVIEW.md 2026-08-22 (pre-lecture test) for the pass that
     set these. */
  header h1 { font-size: 40px; margin: 0; letter-spacing: 0.5px; }
  header .scenario { color: var(--dim); font-size: 24px; margin-left: 16px; }
  .cols {
    display: flex;
    height: calc(100vh - 78px);
  }
  .col {
    flex: 1;
    overflow-y: auto;
    padding: 22px 28px;
  }
  .col + .col { border-left: 2px solid var(--border); }
  .col h2 {
    font-size: 22px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--dim);
    margin: 0 0 18px 0;
  }
  .event {
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 16px;
    border-left: 6px solid var(--dim);
    background: var(--panel);
    animation: in 0.4s ease-out;
  }
  @keyframes in { from { opacity: 0; transform: translateY(6px);} to {opacity:1; transform: translateY(0);} }
  .event.attacker { border-left-color: var(--attacker); }
  .event.defender { border-left-color: var(--defender); }
  .event .top { display:flex; justify-content: space-between; font-size: 17px; color: var(--dim); margin-bottom: 8px; }
  .event .actor-tag { font-weight: 700; letter-spacing: 0.5px; }
  .event.attacker .actor-tag { color: var(--attacker); }
  .event.defender .actor-tag { color: var(--defender); }
  .event .desc { font-size: 27px; line-height: 1.35; }
  .event .technique { display:inline-block; margin-top: 10px; font-size: 17px; background:#1c2634; color: var(--dim); padding: 4px 10px; border-radius: 6px; }
  .sev-critical { box-shadow: 0 0 0 3px var(--crit) inset; }
  .sev-high { box-shadow: 0 0 0 3px var(--high) inset; }

  .legal-card {
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 18px;
    background: var(--panel);
    border-left: 6px solid var(--legal);
  }
  .legal-card.tbd { border-left-color: var(--tbd); opacity: 0.85; }
  .legal-card .statute { font-size: 27px; font-weight: 700; color: var(--legal); }
  .legal-card.tbd .statute { color: var(--tbd); }
  .legal-card .plain { font-size: 23px; margin: 10px 0; }
  .legal-card .meta { font-size: 18px; color: var(--dim); margin-top: 10px; }
  .badge-tbd { display:inline-block; background: #3a2f00; color: var(--legal); font-size: 16px; padding: 3px 10px; border-radius: 5px; margin-left: 10px; }

  .empty { color: var(--dim); font-size: 22px; padding-top: 40px; text-align: center; }
</style>
</head>
<body>
<header>
  <div><h1>CYBER RANGE</h1><span class="scenario" id="scenario-name">waiting for scenario...</span></div>
  <div style="color:var(--dim); font-size:17px;">event stream: live</div>
</header>
<div class="cols">
  <div class="col" id="tech-col">
    <h2>Attack &amp; Defense Timeline</h2>
    <div id="tech-events"><div class="empty">No events yet — run the scenario's attack script.</div></div>
  </div>
  <div class="col" id="legal-col">
    <h2>Legal Overlay</h2>
    <div id="legal-events"><div class="empty">No legal events yet.</div></div>
  </div>
</div>
<script>
let lastCount = -1;
async function poll() {
  try {
    const res = await fetch('/events');
    const data = await res.json();
    render(data.events || [], data.legal_map || {});
  } catch (e) { /* keep polling silently */ }
  setTimeout(poll, 1000);
}

function render(events, legalMap) {
  if (events.length === lastCount) return;
  lastCount = events.length;

  const scenario = events.length ? events[events.length - 1].scenario : null;
  document.getElementById('scenario-name').textContent = scenario ? scenario : 'waiting for scenario...';

  const techEl = document.getElementById('tech-events');
  const legalEl = document.getElementById('legal-events');

  if (!events.length) {
    techEl.innerHTML = '<div class="empty">No events yet — run the scenario\\'s attack script.</div>';
    legalEl.innerHTML = '<div class="empty">No legal events yet.</div>';
    return;
  }

  techEl.innerHTML = events.slice().reverse().map(ev => {
    const sevClass = ev.severity ? ('sev-' + ev.severity) : '';
    return `<div class="event ${ev.actor || ''} ${sevClass}">
      <div class="top"><span class="actor-tag">${(ev.actor || 'system').toUpperCase()}</span><span>${ev.ts || ''}</span></div>
      <div class="desc">${escapeHtml(ev.description || ev.step_id || '')}</div>
      ${ev.attack_technique_id ? `<div class="technique">ATT&amp;CK ${ev.attack_technique_id}</div>` : ''}
    </div>`;
  }).join('');

  const seen = new Set();
  const legalCards = [];
  events.forEach(ev => {
    if (!ev.legal_ref || seen.has(ev.legal_ref)) return;
    seen.add(ev.legal_ref);
    const ref = legalMap[ev.legal_ref];
    if (!ref) {
      legalCards.push(`<div class="legal-card tbd">
        <div class="statute">${ev.legal_ref} <span class="badge-tbd">TBD</span></div>
        <div class="plain">Legal mapping not yet defined for this event.</div>
      </div>`);
      return;
    }
    const tbd = !ref.penalty || ref.penalty === 'TBD';
    legalCards.push(`<div class="legal-card ${tbd ? 'tbd' : ''}">
      <div class="statute">${escapeHtml(ref.statute || ev.legal_ref)} ${tbd ? '<span class="badge-tbd">PENALTY TBD</span>' : ''}</div>
      <div class="plain">${escapeHtml(ref.plain_language || '')}</div>
      ${ref.penalty && ref.penalty !== 'TBD' ? `<div class="meta"><strong>Penalty:</strong> ${escapeHtml(ref.penalty)}</div>` : ''}
      ${ref.evidentiary_note ? `<div class="meta"><strong>Evidence:</strong> ${escapeHtml(ref.evidentiary_note)}</div>` : ''}
    </div>`);
  });
  legalEl.innerHTML = legalCards.length ? legalCards.join('') : '<div class="empty">No legal events yet.</div>';
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

poll();
</script>
</body>
</html>
"""


def read_events():
    if not os.path.exists(EVENTS_PATH):
        return []
    events = []
    with open(EVENTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def append_event(ev):
    os.makedirs(os.path.dirname(EVENTS_PATH), exist_ok=True)
    with LOCK:
        with open(EVENTS_PATH, "a") as f:
            f.write(json.dumps(ev) + "\n")


def read_legal_map():
    if not os.path.exists(LEGAL_MAP_PATH):
        return {}
    try:
        with open(LEGAL_MAP_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = INDEX_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/events":
            self._send_json({"events": read_events(), "legal_map": read_legal_map()})
        elif self.path == "/health":
            self._send_json({"ok": True})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/events":
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                self._send_json({"error": "bad json"}, 400)
                return
            ev.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            append_event(ev)
            self._send_json({"ok": True})
        elif self.path == "/reset":
            os.makedirs(os.path.dirname(EVENTS_PATH), exist_ok=True)
            with LOCK:
                open(EVENTS_PATH, "w").close()
            self._send_json({"ok": True})
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"range-dashboard listening on :{PORT}", flush=True)
    server.serve_forever()
