# Review Log

A running log of decisions, checkpoints, and risks — not a changelog of
every edit. Append new entries at the top. Don't rewrite or delete past
entries; if a past decision turned out wrong, add a new entry that says so
and links back to it.

Each entry: date, what happened/was decided, why, and any open risk.

---

## Pre-ship checklist

Run through before calling any scenario demo-ready. Note the result in that
change's log entry below, not here — this section is the checklist itself,
not a log.

**General:**
- Does the change match the current roadmap phase?
- Is the change small enough to review?
- Did a full `reset → run → reset` cycle actually happen, or only a partial
  run?
- Did we add unnecessary complexity (e.g. a scenario-specific hack that
  belongs in the core, or vice versa)?

**Cyber-range specific:**
- Does it run with the laptop's wifi/network fully disconnected? (Not just
  "should" — actually tested with the adapter off.)
- Does every legal claim on screen cite a real, verified statute section? Is
  anything unverified marked TBD instead of guessed?
- Is the reset genuinely clean — no leftover state, alert history, or
  container drift between runs?
- If this touches the agentic scenario: has it had 3 consecutive clean
  rehearsal runs with zero manual intervention? (Required before it's ever
  presented live — working agreement #1.)
- Is the attack technically real (real requests/real detection), even if
  the attacker's *choices* are scripted? Theater with no real traffic
  undermines credibility with the cybersecurity half of the audience.
- Is anything readable from the back of a room on a projector, not just a
  laptop screen at arm's length?

---

## 2026-08-22 (extend) — Scenario 1 grown from 1 challenge to 3, each independently detected + legally mapped

**What:** Founder asked to add a couple more of Juice Shop's built-in
challenges to the same demo, "complete with the legal side by side."
Extended `scenarios/web-exploit/` (same infra, same target, same proxy/
detector/dashboard) rather than building new scenario folders — this is
still one continuous narrative against the same app, not an
architecturally distinct scenario per Phase 3's definition. Two new
challenges added, both hand-verified against the live instance before
scripting, same discipline as the original build:

1. **Confidential document exposure** — `GET /ftp/acquisitions.md` returns
   the internal "Planned Acquisitions" memo (explicitly marked
   confidential in its own text) with **zero authentication of any kind**.
   Deliberately placed as the *legally weakest* step in the chain — see
   below.
2. **Account takeover via guessable security question** — Jim's
   (`jim@juice-sh.op`, one of the users enumerated in the existing IDOR
   step) password-reset flow asks "Your eldest sibling's middle name?";
   the publicly-known answer ("Samuel") resets his password, and the new
   credentials were confirmed to actually log in as him. Full account
   takeover, not just a successful-looking API call — verified end-to-end.

**New detector rules** (both tested firing off real, independent traffic —
not the attacker's own narration):
- `GET /ftp/*.{md,pdf,txt}` returning 200 → confidential-file alert.
- `POST /rest/user/reset-password` returning 200 (not 401, which is what a
  wrong guess correctly returns — verified both codes directly before
  writing the rule) → account-takeover alert.

To make the second rule possible, extended `proxy/server.py` to log each
request's **response status code**, not just the request itself (originally
only logged method/path/body) — needed to tell "attempted the reset" from
"the reset actually succeeded."

**Legal content added** (`legal-map.json`, two new entries):
- `identity-theft-1028`: federal 18 U.S.C. §§ 1028/1028A + Colorado § 18-5-902.
  Researched and cited (not general-knowledge guessed): federal § 1028A adds
  a mandatory, non-discretionary, consecutive 2-year sentence on top of the
  underlying felony; Colorado's version is typically a class 4 felony
  (2-6 years, up to $500,000 fine). Sourced from a Colorado criminal-defense
  firm's summary and general secondary sources on § 1028A — still not a
  primary-text verification pass.
- `cfaa-1030a2-misconfig`: same CFAA § 1030(a)(2) as the SQLi step, but
  written to be honest about a real legal nuance rather than reusing the
  confident framing of the bypass step. **This is intentional, not a
  hedge to avoid writing content:** courts have genuinely split on whether
  requesting a URL with zero authentication barrier counts as "without
  authorization" under the CFAA (the vacated AT&T/Weev case is the classic
  example). Framed on screen as the chain's weakest legal case and a
  deliberate discussion prompt for the law-enforcement track, not swept
  under the rug to keep every step looking equally prosecutable.

**Attack chain is now 6 steps** (recon → confidential-file exposure → SQLi
login bypass → broken-access-control enumeration → account takeover →
breach declared), all in one continuous run. Full detail in
[specs/scenario-web-exploit.md](specs/scenario-web-exploit.md).

**Verified:** rebuilt and reset, ran the full chain twice (once mid-testing
with stale state mixed in from an unbuilt image — caught and corrected by
re-running with `--build` — then once more from a fully clean reset). The
clean run produced exactly 15 events: 6 attacker narration events + 4
independent defender detections + 1 breach-declared, matching the design
with no manual fixes needed. Confirmed visually in the dashboard — the
misconfig step's hedged legal framing renders distinctly from the other
entries' more confident penalty language.

**Open risks / not yet done (unchanged from the prior entry, still open):**
wifi-disconnected test, projector legibility check, primary-source legal
verification pass (now covering 5 statute entries, not 3).

---

## 2026-08-22 (build) — Phase 1 built and verified end-to-end: environment + scenario 1

**What:** Built and personally verified `demos/v1-cyber-range/` — core infra
plus scenario 1 (web exploit → data breach), per Phase 1 in
[ROADMAP.md](ROADMAP.md). Founder confirmed Colorado as the state and
confirmed the scripted-first framing before this started.

**Tooling installed:** Docker Desktop was not used — installed
[Colima](https://github.com/abiosoft/colima) + `docker` CLI + `docker-compose`
+ `docker-buildx` via Homebrew instead (`brew install colima docker
docker-compose docker-buildx`), since it's scriptable/license-free and
doesn't need an interactive GUI install. Colima VM: 4 CPU / 8GB RAM / 60GB
disk (`colima start --cpu 4 --memory 8 --disk 60 --vm-type=vz`) — leaves
~40GB headroom on the 48GB machine for Ollama (Phase 2, runs natively on the
host, not inside the VM) plus everything else. Registered the Homebrew CLI
plugin directory in `~/.docker/config.json` so `docker compose` works as a
subcommand.

**Architecture correction — internal networks block published ports
entirely, not just egress.** `specs/architecture.md`'s original design
assumed a Docker network with `internal: true` would still let a
host-published port through (host↔container ports as a separate mechanism
from network egress). **Tested this directly and it's wrong** — with only
an `internal: true` network attached, Docker silently never binds the port
at all (`docker inspect` showed `"8080/tcp": null` despite a `ports:` entry;
`curl` got connection-refused). Fixed by adding a second, non-internal
network (`cyberrange_view`) that *only* the dashboard and the proxy join, in
addition to `cyberrange_net`. Juice Shop, the attacker, and the detector
never join it — they stay exclusively on the internal network, so the
isolation guarantee for anything "attack"-shaped is unchanged. Updated
`specs/architecture.md` to match what was actually verified working, not
the original assumption.

**Dashboard: built a lightweight custom event-stream dashboard instead of
Wazuh, for this build pass.** `specs/dashboard.md` originally called for
Wazuh (real SIEM, real ruleset). Given the 2-3 day runway and Wazuh's
heavier footprint (cert generation, indexer memory floor, slower boot —
works against the "reset in under a minute" quality bar), built instead: a
small reverse proxy (`scenarios/web-exploit/proxy/`) that logs every real
request to the target, a detector (`.../detector/`) that independently
tails that log and pattern-matches (SQLi-payload regex on the login
endpoint; sequential-user-ID enumeration within a 10s window), and a
scenario-agnostic dashboard (`core/range-dashboard/`) that renders both the
technical timeline and the legal overlay from one shared JSON event stream
in a single two-column page. All three are stdlib-only Python (no pip
installs), which also keeps image builds fast and fully reproducible
offline. **This is still real detection on real traffic** — the detector
never reads the attacker's script, only the proxy's independently-recorded
log — which was the actual requirement in `specs/dashboard.md`, just met
with lighter tooling than originally specced. Wazuh remains a reasonable
option to revisit in Phase 4 if a fuller SOC-analyst-style dashboard is
wanted later; not needed for this lecture.

**Scenario 1 attack chain — verified against a live Juice Shop instance
before being scripted, not written from documentation alone.** Pulled
`bkimminich/juice-shop` (version 20.2.0 at build time) and hand-tested both
steps with `curl` first:
- SQL-injection login bypass: `POST /rest/user/login` with
  `{"email": "' OR 1=1--", "password": "irrelevant"}` — confirmed it
  authenticates as `admin@juice-sh.op` with a valid JWT, zero real
  credentials.
- Broken access control: that JWT against `GET /api/Users/{id}` for
  IDs 1-5 — confirmed it returns **any** user's full record (email, role,
  and one user's `deluxeToken` secret), with only a "is there a token"
  check, no "does this record belong to the caller" check. Unauthenticated
  requests to the same endpoint correctly get 401 — so the real bug here is
  broken *object-level* authorization, not missing authentication.
This is now what `scenarios/web-exploit/attacker/attacker.py` actually
executes — real requests, not a simulation of them.

**Rehearsed twice, per the pre-ship checklist:** `reset.sh` completed in
~22 seconds both times (well under the 1-minute bar), dashboard/events
came back empty after reset, and the full attack chain — including both
detector alerts firing off real traffic — reproduced identically on the
second run with no manual intervention.

**Legal content: Colorado citations added, still not a final legal-review
pass.** `scenarios/web-exploit/legal-map.json` now cites federal CFAA §
1030(a)(2), Colorado's Computer Crime Act (§ 18-5.5-102), and Colorado's
breach-notification statute (§ 6-1-716) — sourced from Justia's codified
statute mirror and a Colorado criminal-defense firm's practitioner summary
(shouselaw.com), not just general knowledge. This is a strong starting
point but is explicitly flagged inside the file itself and in
`context/legal-framework.md` as **not yet a final verification pass**
against primary/official statute text — see
[routines/refresh-legal-citations.md](routines/refresh-legal-citations.md).
Don't present the penalty language as final without that pass.

**Pre-ship checklist results:**
- Matches roadmap: yes — this is Phase 1.
- Reset tested with a real `reset → run → reset → run` cycle: yes, twice,
  see above.
- Runs with wifi disconnected: **not yet tested** — everything so far has
  been verified with the laptop's normal network active (image pulls
  needed it). Physically disconnecting and re-testing is still open, and
  should happen before the lecture, not assumed from the `internal: true`
  network config alone (see working agreement #2's "second, independent
  layer" framing).
- Legal claims cited: yes, with the "not yet final" caveat stated above.
- Projector legibility: **not yet checked** — only viewed on a laptop
  browser so far (desktop viewport). Dashboard CSS uses relatively large
  type but hasn't been checked from an actual distance/projector.
- Real traffic, not staged: yes — verified directly, detector fires off the
  proxy's independent log, not the attacker's own narration.

**Open risks / not yet done:**
- Wifi-disconnected test (see above) — do this before the lecture.
- Projector legibility check — do this before the lecture.
- Legal-citation verification pass against primary statute text — see
  `routines/refresh-legal-citations.md`.
- Scenario 2/3 (Phase 3) and the agentic scenario (Phase 2) are unstarted.
- No `.gitignore` yet for this repo — nothing sensitive has been committed
  (nothing has been committed at all yet — see the 2026-08-22 workspace-
  setup entry below), but worth adding before any `git add .`.

---

## 2026-08-22 — Workspace setup + tech-stack research

**What:** Set up this AI-employee workspace from scratch (this repo was
empty, not a git repo, before today) and researched the tech stack for a
containerized "AI vs AI" cybersecurity demo for a one-time, dual-audience
(cybersecurity + law enforcement) college guest lecture.

**Key decisions made with the founder (via direct Q&A before any building
started):**
- **Timeline is 2-3 days out** — the tightest of the offered options. This
  drove the single biggest architectural decision below.
- **Speaker-run demo only** — no student-facing/multi-tenant infra for v1.
- **Modular, multi-scenario architecture from day one**, even though only
  one scenario ships for the actual lecture. The founder explicitly wants to
  keep adding scenarios on the same core over time, so scenario-as-plugin
  was treated as a real requirement, not gold-plating.
- **AI-driving approach:** the founder wants one non-deterministic (real
  agentic, local-LLM-driven) scenario *and* two-or-more deterministic
  scripted scenarios, sharing infrastructure. Also wants this to run fully
  offline on local LLMs (Ollama, M4/48GB laptop) with the network air-gapped
  for safety — not cloud APIs.

**Why the scripted-first working agreement exists:** a 2-3-day runway is not
enough time to make a genuinely non-deterministic, live LLM-driven attack
loop reliable for a one-shot, unrepeatable lecture performance. Rather than
water down the founder's "real AI vs AI" vision or silently drop it, the
plan keeps it as an explicit, real deliverable (Phase 2) *behind* a
guaranteed, fully rehearsed, deterministic scenario (Phase 1) — see
working agreement #1 in [CLAUDE.md](CLAUDE.md). This was proposed here, not
yet re-confirmed with the founder as a standalone question — flagging it
explicitly since it's a real interpretation of "how literally AI vs AI"
should behave under time pressure, and the founder should sanity-check it
before Phase 1 build work starts.

**Research findings (full detail + sources in
[context/tech-stack-research.md](context/tech-stack-research.md)):**
- Docker-based containment is the right call, not a wrong instinct to
  second-guess — it matches what the current OSS ecosystem (MITRE/Apache
  Caldera, AgentCyberRange, Wazuh) already does for exactly this kind of
  exercise.
- **GOAD** (Game of Active Directory) was evaluated for the future
  ransomware/lateral-movement scenario and rejected — it's a multi-VM
  Vagrant/Proxmox lab, not laptop-friendly on this timeline. A lightweight
  Docker-only mock is the better fit when that scenario gets built.
- **OWASP Juice Shop** is the recommended v1 target app — Docker-native,
  100+ scored vulnerabilities across the OWASP Top 10, an official trainer's
  guide, no data-seeding complexity.
- **Wazuh** is the recommended dashboard/SIEM — single-machine Docker
  deployment (~6GB), ships real detection rules and a working dashboard UI
  out of the box, which is faster to stand up in 2-3 days than a hand-built
  Grafana panel from scratch.
- **skills.sh had nothing purpose-built for this** (searched "docker",
  "security", "grafana", "pentest", browsed `/topic`). Closest real,
  installable things: the official `grafana/skills` repo (useful only if a
  supplementary custom Grafana panel gets built later) and generic
  code-level `security-review`/`security-audit` skills (not attack-
  simulation skills, not directly useful here). `usestrix/strix` (an actual
  open-source autonomous AI pentesting agent) and `yaklang/hack-skills`
  surfaced under a "pentest" search and are worth reading as prior art for
  the Phase 2 agent-loop design — not adopted wholesale.
- Local LLM model names from research (e.g. specific "48GB-tier" model
  picks from blog posts) were **not** trusted as final — model availability
  moves too fast and some cited names couldn't be corroborated with
  confidence. Recorded as a *class* of model to try (7-14B tool-calling
  class + ~3B narration class), final pick deferred to a real memory/latency
  check on the actual machine in Phase 2 (working agreement #7).

**Open risks / not yet resolved:**
- **Which state's computer-crime statute pairs with federal CFAA is
  unknown** — depends on the institution, not yet asked. Flagged in
  [context/legal-framework.md](context/legal-framework.md); needs an answer
  before the legal-overlay content can be finalized.
- **Exact CFAA subsection-to-penalty mapping needs a real legal-citation
  pass**, not the general-knowledge summary in this session's research.
  Nothing quantitative should reach the screen until that's done — see
  working agreement #4.
- **Nothing is built yet.** This entry covers workspace + research only.
  Phase 1 build (see [ROADMAP.md](ROADMAP.md)) hasn't started.
- **The "scripted-first" interpretation above is a proposal**, not yet
  independently re-confirmed by the founder as its own decision — flag this
  explicitly at the start of the next session if it hasn't been discussed.

**Environment notes:** this directory was empty and not a git repository
before this session. Not yet initialized as git — that's a reasonable next
step but wasn't done automatically here since it wasn't explicitly part of
the ask.
