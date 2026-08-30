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

## 2026-08-30 (deck) — per-Part gates + new Part III grounded in the last 12 months

Founder feedback after the Vercel deploy:
- **Per-Part password gates.** The gate now fires on first view *and* on
  entering each Part (dividers carry `data-gate` p1/p2/p3; nav is intercepted
  and the same password re-prompts, with a Part-specific message). Unlocks
  are remembered per session in `sessionStorage`. Lets the presenter reveal
  the deck section by section. Same client-side password.
- **New Part III — "The current predicament"** (its own red accent). Page 15
  is now the Part III divider (was the "no rungs" pivot). The back half was
  reworked from generic accountability wording into a fact-based section
  covering the **last 12 months**: the accountability gap (intent /
  foreseeability / control / safeguards); a last-12-months legal timeline led
  by **Colorado's AI-law whiplash** (SB24-205 postponed → enforcement stayed
  → repealed & replaced by SB26-189 within a year); the honest "no settled
  case" gap; the FBI's ~$893M AI-fraud figure; and **real current defensive
  techniques** (AI-native behavioral detection, MITRE ATLAS, runtime
  containment, zero-trust microsegmentation, provider-side takedowns). The
  old classic-precedent timeline (Morris/Van Buren/…) moved out of the main
  flow; those cases remain in the reference exhibits.
- Researched and cited: Colorado AI Act saga (SB24-205 / SB25B-004 /
  SB26-189, CO AG rulemaking), FBI IC3 2025, MITRE ATLAS, 2026 agentic-defense
  guidance. Deck is now 26 slides; `speaker-notes.md` updated for Part III.

Verified the full gate flow (entry → Part I → Part III, each with the right
prompt) and the Part III slides rendering at 1280×720. Redeployed to Vercel.

## 2026-08-30 (deck → deployable) — Vercel static site, notes removed, password gate

Founder is sharing the deck with the class, not handing out a file. Changes:
- **Deployable static site.** The deck now lives at
  `demos/lecture-deck/site/index.html` (+ a minimal `vercel.json`). `site/`
  holds *only* those two files so nothing private ships when Vercel serves
  the folder. Deploy: `cd demos/lecture-deck/site && npx vercel --prod`, or
  connect the repo with Root Directory = `demos/lecture-deck/site`. Replaced
  the old `attack-autonomy-accountability.html`.
- **Instructor notes removed** from the deck and extracted to
  `demos/lecture-deck/speaker-notes.md` (kept *outside* `site/` so students
  can't fetch them). The `N` notes drawer and its key are gone.
- **Simple password gate.** A full-screen gate unlocks the deck on a string
  match (`PASSWORD` constant in `index.html`, default `range2026`),
  remembered per-session via `sessionStorage`; nav (keys/click/swipe) is
  locked until unlocked. Deliberately **not bulletproof** — the check is
  client-side and readable in source, per the founder's "keep it simple"
  call. A serverless-function + env-var upgrade is a quick follow-up if real
  gating is ever wanted.

Verified the gate → unlock → navigate flow and that all 26 slides still
render (served locally, checked in-browser). Legal content unchanged.

## 2026-08-29 (deck feedback round 2) — two-question setup, Part II gets the same discussion arc

- **Slide 2 rebuilt as the setup.** The old agenda (an abstract Part I/Part II
  timeline that "gave away the structure") is replaced by the two guiding
  questions the whole talk answers — *how does AI change the attack?* and
  *who does the law hold responsible?* — with a converging-threads graphic
  (technique + law pulled together by AI). No roadmap; the questions are the
  spine.
- **Part II now mirrors Part I's demo → discussion → best-practice arc.**
  Slide 14 (AI-vs-AI demo) gains a discussion band (tactics for cyber,
  accountability for justice); a new best-practice slide was added after the
  precedent timeline — how each side handles an attacker with no identity
  (behavioral attribution + agent-access scoping for cyber; climbing the
  human chain, provenance, and the shift to policy for justice), bridging
  into the state's hack-back response. Deck is now 26 slides.

## 2026-08-29 (deck feedback round) — graphics cleanup, real field case, demo→discussion→best-practice

Founder review of the redesign. Changes:
- **Removed the hand-drawn "scales of justice"** (title + close slides) — it
  read as clip-art. Title now stands on the network-constellation mark; the
  close uses a fingerprint-vs-empty-frame motif ("leaves a mark" /
  "leaves none"). Redrew the TeamPCP **cat** as a clean line icon.
- **Slide 3 now carries a real, local field case** the founder worked: a
  Denver-metro organized-burglary investigation (charged under the Colorado
  Organized Crime Control Act) in which the crew used devices to disable
  **Wi-Fi-based security systems** — replacing the generic EXIF anecdote.
  Sourced from the 18th Judicial DA's public release; kept the defendant
  unnamed. New matching graphic (jammed Wi-Fi camera). No longer flagged
  optional.
- **Part I reworked into demo → discussion → best-practice.** Slide 9 gains a
  two-column class-discussion band (tactics for cyber, charging decisions for
  justice). Slide 10 becomes a **settled-vs-arguable guide** split by
  Cyber/Justice lens — surfacing the genuinely contested cases (the vacated
  *weev* conviction; recon/scanning; the unauthenticated file) as the place
  the argument actually lives, tied back to demo steps. Slide 11 replaced the
  "crime vs culprit / someone goes to prison" framing (talked down to the
  room) with a clean, peer-level **best-practice method for each side**.

Legal content unchanged and still in sync with the dashboard legal-maps.
Verified the changed slides render clean at 1280×720. Deck file re-exported.

## 2026-08-29 (deck redesign) — restructured to two parts, new visual identity, expanded case study

**What / why.** Founder review of the first deck landed several changes:
the look read as generic/AI-made; the title and opening line spoiled the
talk; slides were text-only; the TeamPCP case needed real who/what/how/why;
and the spine should flow *human-directed → autonomous*, with the policy/
legal material folded into the autonomous half rather than a separate act.
Rebuilt accordingly. Deck renamed **`attack-autonomy-accountability.html`**
(was `who-goes-to-prison-deck.html`).

**Changes.**
- **New visual identity** — a "forensic table" system deliberately steering
  clear of the AI-deck clichés the design pass warns about: editorial
  **serif** headlines (not Inter/Space-Grotesk), a cool signal-blue for the
  technical thread and warm **paper "exhibit" cards** for the legal thread,
  and a **custom SVG graphic on every slide** (worm-propagation tree,
  deanonymization node graph, agent-autonomy loop, precedent timeline,
  privateering lineage). Still self-contained, system-fonts-only, offline.
- **Restructured** intro → **Part I** (a person is behind it: TeamPCP who/
  what/how-caught, attribution principle, live demo, legal exhibits, the
  clean case) → **Part II** (no one is behind it: autonomous attacks are
  real, AI-vs-AI demo, ladder-with-no-rungs, the lineup, precedent timeline,
  the state's hack-back response, the legal inversion) → reference exhibits.
- **Expanded TeamPCP** into a proper case study, fact-checked against Flare,
  Google/Mandiant (UNC6780), Krebs, CyberScoop: the Shai-Hulud self-
  propagating npm/PyPI worm (CVE-2026-45321), hits on Trivy/Bitwarden/
  Checkmarx/GitHub, 518M+ download footprint, ~500k credentials, 300+GB
  exfiltrated, operators Ruben Thomson (21) and Louis Gaebler (23) charged
  in Perth, deanonymized via a reused cat-at-monitors avatar.
- **Graphics choice:** custom SVG/infographics rather than scraped photos —
  safer on copyright/privacy for real people, and reads as authored. Easy to
  swap real imagery in later if the founder approves specific sources.

**Legal content unchanged and still in sync** with the dashboard
`legal-map.json` files — same statutes, sentencing ranges, and five cases;
same honesty flags (prison ranges verified; fine caps practitioner-sourced;
§1030(a)(5) not asserted for the marker-write).

**Verification.** Served locally and checked at projector 16:9
(1280×720); DOM-measured the grids to confirm full-width two-column layout
(wrap 1126px, columns filling it) and no clipping — the earlier scaled
thumbnails were misleading. Known limit: below ~860px width, two-column
slides stack vertically (a narrow-window fallback, not a projector case).
`talk-track.md` kept but marked **superseded** for its slide script — the
authoritative speaker notes now live inside the deck (`N`); its Legal
Reference Pack stays valid.

## 2026-08-29 (lecture deck) — the guest-lecture slide deck checked into the repo

**What / why.** Built the actual guest-lecture deck the whole repo exists to
support and checked it in at [`demos/lecture-deck/`](demos/lecture-deck/):
a self-contained HTML deck (`who-goes-to-prison-deck.html`) plus the speaker
script + Legal Reference Pack (`talk-track.md`) and a folder README. The
talk — *"Who Goes to Prison When the AI Did It?"* — is a three-act arc that
runs the scenarios live: Act 1 the presenter runs `web-exploit` as the
attacker (crime + attribution), Act 2 an AI-vs-AI scenario removes the human
and the room debates liability (Developer/Deployer/Operator/User, with
*Morris / Van Buren / Flores-Figueroa / Global-Tech* and the Aug-12-2026
hack-back memo), Act 3 closes on the policy inversion.

**Decisions worth noting.**
- **Placed under `demos/`, not a new top-level folder** — working agreement
  (CLAUDE.md "don't create new top-level folders without asking") kept in
  mind. `demos/lecture-deck/` is a subfolder of an existing top-level dir.
  Easy to relocate if the founder wants it elsewhere.
- **Self-contained + system fonts only, no web fonts** — deliberately, so
  the file opens and presents on the air-gapped demo laptop (`file://…`)
  identically to online, consistent with the repo's offline-at-showtime bar.
- **Legal content mirrors the dashboard `legal-map.json` exactly** — same
  statutes, current post-SB21-271 sentencing ranges, same five cases (see
  the 2026-08-28 legal-refresh entry below). The folder README documents
  that the two surfaces must be updated together; same honesty flags carry
  over (prison ranges verified; fine caps practitioner-sourced; §1030(a)(5)
  not asserted for the marker-write).
- **README updated** (working agreement #8): new repo-map row + a pointer in
  the intro. The deck is going to the **public** repo — it's educational
  material the founder asked to check in and push; nothing employer-specific
  or opsec-sensitive is in it (current employer intentionally kept vague).

**Pre-ship checklist notes.** Deck rendering was verified across all three
acts + the appendix by serving it locally and screenshotting (title, setup,
both demo-cue slides, legal overlay, attribution, lineup, all reference
tables). Three real bugs found and fixed in that pass: UTF-8 mojibake
(added `<meta charset>`), a speaker-notes drawer sliver peeking on-screen,
and a `nowrap` class truncating the federal-statutes penalty column.
*Not* done: eyeballing the deck on the actual projector from the back of
the room, and one live `run` of each scenario to confirm the new dashboard
"Case law:" line is projector-legible — both are pre-lecture steps, same as
the open item in the entry below.

## 2026-08-28 (legal refresh) — verified penalties + case law added to all three legal-maps; dashboard renders a new Case-law line

**What happened / why.** While building a guest-lecture deck (the "Who goes
to prison when the AI did it?" talk), ran a real verification pass on the
legal content so the deck and the on-screen dashboard overlay wouldn't
drift. Updated `penalty` text and added a new `case_law` field to every
entry in all three scenario legal-maps (`web-exploit`, `agentic`,
`network-intrusion`), and taught the core dashboard renderer
(`core/range-dashboard/server.py`) to display `case_law` as a "Case law:"
line. The field is optional and backward-compatible — entries without it
(e.g. `co-6-1-716`, a civil notification duty, deliberately has none)
render exactly as before.

**What was verified (2026-08-28) and how.**
- **Colorado sentencing ranges** refreshed to current post-**SB21-271**
  values (C.R.S. § 18-1.3-401): F3 4–12y, F4 2–6y, F5 1–3y, F6 1–1.5y, plus
  mandatory-parole terms; M1 ≤364d, M2 ≤120d. The old maps only named the
  offense *class*; they now carry the actual years. § 18-5.5-102 value tiers
  and § 18-5-902 (class 4 felony) confirmed.
- **Federal** § 1030(c)(2) ladder (1y → 5y on gain/furtherance/>$5,000 →
  10y repeat) confirmed against House OLRC text + the USSC 2021 Computer
  Crimes primer. § 1028A mandatory-consecutive-2y confirmed on the statute
  face.
- **Case law** added where it does real work: *Van Buren* (141 S. Ct. 1648
  (2021)) on `cfaa-1030a2` / `co-18-5.5-102`; *Morris* (928 F.2d 504) on
  `cfaa-1030a2`; *Auernheimer/weev* (748 F.3d 525) on
  `cfaa-1030a2-misconfig`; *Flores-Figueroa* (556 U.S. 646 (2009)) on
  `identity-theft-1028`.

**Pre-ship checklist notes.**
- *Every legal claim cites a real, verified source?* — Prison/sentence
  ranges: yes (primary/authoritative). **Exact fine caps remain
  practitioner-sourced** and are flagged as such in the `penalty` text —
  not upgraded to "verified." § 1030(a)(5) for the AI marker-write is still
  **deliberately not asserted** (see `network-intrusion` `_note`).
- *reset → run → reset actually run?* — **No.** This is a data + renderer
  change only; no live scenario run or rehearsal-gate was performed this
  change. Renderer change is a one-line optional field in the existing
  template; `py_compile` passes and all three JSONs validate. **Before the
  lecture, do one `run` of each scenario and eyeball the new Case-law line
  on the projector** (readability from the back of the room, working
  agreement + projector checklist item).
- *README?* — Not changed. README describes the overlay at the level of
  "statute, elements, penalty" (lines ~9–10, ~155) and doesn't enumerate
  fields; the added Case-law line doesn't change quick-start, status, or how
  a student runs anything. If a later pass expands the README's dashboard
  description, mention the case-law line then.

**Open risk (unchanged from prior entries).** This is still **not** a final
primary-source legal-review pass in the sense of
[routines/refresh-legal-citations.md](routines/refresh-legal-citations.md)
step 1–2 for every number (fine caps especially). It's a real, sourced
upgrade over the prior secondary-only content, and honest about what's still
practitioner-sourced. The talk-track's "Legal Reference Pack" (kept with the
deck work) mirrors these exact numbers/cases so the two surfaces stay in
sync.

## 2026-08-28 (session handoff) — context cleared after this; read this first next session

A consolidation note for whoever picks this up next — the per-change detail
is in the dated entries below; this is the "where things stand + what to do
next" summary.

**What shipped this session (all pushed to `main`, public repo):**
1. `demos/v1-cyber-range/setup.sh` — one-command machine setup
   (Colima/Docker/Ollama install + start, model pulls, pre-build all
   scenario images). Idempotent. README quick-start now covers all three
   scenarios, not just web-exploit.
2. Bugfix — orphaned containers when switching scenarios (`--remove-orphans`
   added to `run.sh` + all three `reset.sh`). Root cause: no compose file
   sets a project `name`, so all scenarios share one implicit project.
3. Bugfix — incident-report evidence was being written to the
   `cyberrange_events` Docker volume, which `reset.sh`'s `down -v` deletes;
   moved to a host bind mount `demos/v1-cyber-range/evidence/` (gitignored).
4. Feature — `plant_marker` attacker tool (network-intrusion): writes a real
   "ATTACKER WON" file to a backdoored host and reads it back. The SMB
   confidential-file exfil the founder also mentioned already existed
   (`smb_download` of `confidential-layoffs.txt`).
5. Balance — attacker-vs-defender is now a real toss-up via a per-run coin
   flip on whether an earned block lands (`BLOCK_SUCCESS_PROB`, default 0.5).

**Lessons learned (the non-obvious ones):**
- **Balance can't be tuned by timing.** The attacker/defender win ratio is
  dominated by the presenter's live speed dropdown, not by block thresholds
  — measured 5/6 then 7/7 defender at Normal pace with two different
  threshold tunes. The coin flip is what actually decouples balance from
  pace. `BLOCK_SUCCESS_PROB` is the one dial now (raise >0.5 to favour the
  defender); measured ~5/3 attacker over 8 runs at Normal @ 0.5.
- **Re-check balance with the committed harness:**
  `scenarios/network-intrusion/measure-balance.sh [runs] [delay_ms]` (dev
  tool, not a demo step). Each run is a full two-LLM scenario, so 8 runs
  takes ~15-20 min — run it in the background.
- **Docker gotchas specific to this repo:** shared implicit compose project
  (always use `--remove-orphans`); `down -v` destroys named volumes, so
  anything that must survive a reset needs a host bind mount, not `/data`.

**Next steps / open items:**
- **Re-rehearse network-intrusion.** The plant_marker + coin-flip changes
  are new behavior; the prior 4 rehearsal runs no longer cover the current
  code. The 3-consecutive-clean-runs gate (working agreement #1) restarts
  for this scenario. Same for the real `bench-models.sh` pick on the actual
  48GB demo laptop (all rehearsal so far was on a smaller dev machine).
- **Known UX gap, NOT fixed:** the dashboard speed dropdown is shown and
  enabled for every scenario, but web-exploit (scripted) ignores it — it
  uses a fixed `STEP_DELAY` env var and never reads `/control`. Verified the
  control itself works for the agentic scenarios (pace() timed exactly to
  delay_ms; a real run went ~13s/turn at Slow vs ~7s at Instant). Consider
  disabling/greying the dropdown when a scripted scenario is active so it
  isn't misleadingly clickable.
- Unchanged pre-lecture items (from ROADMAP): founder-only wifi-disconnected
  test, final legal-citation pass against primary statute text, which
  state's statute pairs with CFAA (institution-dependent, still unknown).

**Environment state at handoff:** machine left clean (no running
containers). Colima + host-native Ollama (models `qwen2.5:7b-instruct` +
`qwen2.5:3b-instruct` present). `setup.sh` reproduces the whole setup on a
fresh machine.

---

## 2026-08-25 (balance) — network-intrusion: defender rebalanced to ~50/50 via a coin-flip block outcome

**What:** Founder reported the defender almost always lost (the earlier
restraint gate over-corrected) and asked to get closer to a 50/50 attacker-
vs-defender win ratio. Tried timing/logic tuning first, then — at the
founder's suggestion — a coin flip on block success.

**What I tried, and measured (harness in scratchpad, real two-LLM runs):**
1. Full instant-block on any confirmed critical alert (root shell /
   successful login) + lower the signal gate 2→1. Measured **5/6 defender**
   at Normal pace — over-corrected the other way.
2. Dial back: critical alert still needs one prior signal (a one-reaction
   head start for the attacker) instead of an instant block. Measured
   **7/7 defender** at Normal pace — still not converging.
   Root cause: the ratio is dominated by the presenter's live speed setting,
   not by these thresholds. At Normal pace the defender simply has enough
   reaction windows to win almost always; at Instant the attacker outruns
   it. No single timing tune holds across the paces a presenter actually
   uses, so timing-only tuning can't produce a stable 50/50.
3. **Coin flip on block outcome (shipped).** Whether an *earned* block
   actually lands is decided once per run by `BLOCK_SUCCESS_PROB` (default
   0.5), cached so a failed block isn't retried into an eventual success.
   Everything real stays real — detection, the restraint gate, the actual
   exploitation; only "did the block take" is randomised.

**Honesty guard (this is a teaching surface):** a failed block posts a
`block-evaded` event whose on-screen text explicitly says the outcome was
left to chance (~50/50), NOT a real detection or evasion result — same bar
as the legal citations (never show the room a guess dressed as a fact). The
kept thresholds (`MIN_SIGNALS_BEFORE_BLOCK=1`, critical-alert bypass needing
one prior signal) now serve a narrower purpose: make sure the defender
reliably *reaches* a block attempt so the coin actually gets flipped, rather
than the attacker finishing first by default.

**Verified:** unit-level — forced 0.0 never blocks (and a retry stays
evaded), forced 1.0 always blocks, 0.5 → 197/400 (0.49); the flip is cached
per run. End-to-end — real two-LLM runs at Normal pace now show a genuine
mix of both outcomes (previously 7/7 defender). Left a longer measurement
running at push time to confirm the ratio. README + specs updated in the
same change (working agreement #8).

**Note:** kept as randomness in the *agentic* scenario only — consistent
with working agreement #1 (the agentic scenarios are explicitly the
non-deterministic stretch goals; the scripted web-exploit scenario, which
ships to the lecture, is untouched and still fully deterministic).

---

## 2026-08-25 (feature) — network-intrusion: attacker can plant a real "ATTACKER WON" marker file

**What:** Founder asked for a visible win action — the attacker writing an
"ATTACKER WON" file and/or exfiltrating a fake secret. The exfil half
already existed (`smb_download` pulls the fictional `confidential-layoffs.txt`
off the anonymous SMB share, contents shown on the dashboard), so only the
marker was new. Added a `plant_marker` attacker tool: once `vsftpd_backdoor`
has given a real root shell on the FTP host, it reuses that same real
backdoor shell to `echo 'ATTACKER WON' > /root/ATTACKER_WON.txt` and `cat`
it back, reporting success only on a confirmed read-back — a real write to
the real container filesystem, not a claimed one. Gated on
`SESSION["ftp_compromised"][ip]` (set on backdoor success), same
"requires prior real compromise" pattern as `ssh_shell` needing
`ssh_bruteforce`.

**Why this framing:** it makes the read-vs-write distinction concrete for
the room — the difference between an attacker *reading* data they shouldn't
and *altering/destroying* it. Tagged MITRE T1491.001 (Defacement); reuses
the verified `cfaa-1030a2` citation (same unauthorized-access event as the
backdoor) rather than asserting CFAA's separate damage subsection
§ 1030(a)(5), whose elements this demo hasn't verified against a source —
recorded that reasoning in legal-map.json's `_note` per working agreement
#4 (never assert an unverified citation on screen).

**Verified live:** (1) gating — `plant_marker` before any shell correctly
refuses; (2) `vsftpd_backdoor` → real root shell; (3) `plant_marker` writes
+ confirms, and `docker exec ni-ftp-host cat /root/ATTACKER_WON.txt` shows
the real 13-byte file; (4) dashboard event tagged T1491.001 / cfaa-1030a2 /
critical; (5) a full 14-turn real LLM attacker run (qwen2.5:7b) chose
`plant_marker` on its own on turn 4, right after the backdoor; (6)
`reset.sh` wipes the marker (fresh container) — reset-to-zero still holds.
README + specs/network-intrusion.md updated in the same change (working
agreement #8).

---

## 2026-08-25 (bugfix) — "Evidence preserved for trial" was being destroyed by the very reset it's supposed to survive

**What:** Founder asked where `/data/evidence-...` (printed at the end of
an agentic/network-intrusion incident report) actually lives, and whether
it should be host-side + gitignored instead. Good catch, and it was worse
than just hard to find: `tool_investigate_incident()` in both scenarios'
`tool-api/server.py` was writing backups into `/data`, which is the
`cyberrange_events` **Docker named volume** — and every `reset.sh` runs
`docker compose down -v`, which deletes named volumes. Confirmed live:
after running `reset.sh` for the orphaned-container fix above, `docker
volume inspect cyberrange_events` returned "no such volume" — any evidence
file written there was gone. "Evidence preserved for trial" was not true
under this repo's own normal workflow (a reset between every rehearsal
run).

**Fix:** added a host bind mount (`./evidence:/evidence`, resolves to
`demos/v1-cyber-range/evidence/` — see its README.md) to both scenarios'
`tool-api` service, changed both `server.py`s to write backups there
instead of `/data`, prefixed filenames with the scenario name (`evidence-
agentic-...` / `evidence-network-intrusion-...`) since the folder is now
shared and persistent across runs, and gitignored the folder's contents
(keeping the README tracked).

**Verified live:** brought up `agentic`, called `POST /investigate`
directly against `tool-api` (no LLM run needed), confirmed the backup
landed on the host at `demos/v1-cyber-range/evidence/evidence-agentic-
events-<ts>.jsonl` owned by the real host user (not root — Colima's
virtiofs UID mapping just works here), ran a full `reset.sh`, and
confirmed the file was still there afterward. Deleted the test file before
committing.

---

## 2026-08-25 (bugfix) — Fixed orphaned containers left behind when switching scenarios

**What:** Founder reported sometimes seeing an orphaned container on the
demo laptop. Root cause: no compose file in this repo sets an explicit
project `name`, so `run.sh`'s `--project-directory .` gives all 3 scenarios
the same implicit compose project (the directory name). Bringing up a
different scenario without first running the previous one's `reset.sh`
left its containers running, unrecognized by the new `up`/`down` — Docker
Compose calls these "orphans" and does not remove them unless
`--remove-orphans` is passed. Confirmed live: after a Colima restart,
`ni-*` containers from an earlier `network-intrusion` run came back
(`restart: unless-stopped`) and were still present when `web-exploit` was
brought up next.

**Fix:** added `--remove-orphans` to the `up` call in `run.sh` and to both
the `down`/`up` calls in all three `reset.sh` scripts. Verified live:
running `./run.sh web-exploit` while `ni-*` containers were up cleanly
stopped/removed all of them, leaving exactly `juice-shop`, `range-proxy`,
`range-detector`, `range-dashboard`; a full `reset.sh` cycle afterward
completed in ~22s (within the "under a minute" bar) and `down -v
--remove-orphans` left zero containers behind.

**Not changed:** did not add explicit `name:` fields to give each
scenario its own compose project — that would isolate them but also mean
`web-exploit` and `agentic` (which intentionally share the same Juice Shop
setup and dashboard) could run simultaneously without conflict, which
isn't how this repo is meant to be demoed (one scenario live at a time,
same dashboard). `--remove-orphans` matches the actual usage pattern with
a smaller change.

---

## 2026-08-24 (tooling) — One-command machine setup script + README run-instructions for all 3 scenarios

Added `demos/v1-cyber-range/setup.sh`: a single idempotent script covering
everything previously scattered across `demos/README.md`'s two "One-time
setup" prose sections — installs Colima/Docker CLI/Compose/Buildx/Ollama
via Homebrew, starts Colima with the documented resource flags, starts
Ollama, pulls both default agentic-scenario models, and pre-builds/pulls
every scenario's Docker images (`web-exploit`, `agentic`,
`network-intrusion`) so nothing needs the network at showtime — directly
serving the "runs with zero internet at showtime" quality bar. Every step
checks current state first, so it's safe to re-run.

Verified with a live run on the existing demo-development machine (already
had everything installed): clean exit, all three scenarios' images
built/pulled, matches what `demos/README.md` documents by hand. Homebrew
itself is checked but **not** auto-installed — installing it needs an
interactive sudo prompt from the user, so the script prints the official
install command and exits rather than attempting it non-interactively.

Also updated `README.md`'s "Quick start" (working agreement #8 — README
stays in sync) to point at `setup.sh` for one-time setup and to add
run/reset instructions for `agentic` and `network-intrusion`, which were
previously only documented in `demos/README.md`, not the public front
door.

**Open item:** noticed `ni-*` and `range-dashboard` containers already
running on this machine from a prior session's network-intrusion rehearsal
(REVIEW.md above logs 4 rehearsal runs on 2026-08-24) — left untouched,
not part of this change.

---

## 2026-08-24 (Phase 2c) — New network-intrusion scenario: real OS/server attacks, not just web

**What:** Founder feedback: even after real tuning (defender restraint,
attacker persistence, tool shuffling, the incident report), the agentic
scenario kept feeling repetitive and deterministic — correctly diagnosed
as structural, not a tuning problem: one target (Juice Shop), one protocol
(HTTP), a handful of similar techniques. Asked for a pivot to real OS/
server-level attacks, multiple genuinely different paths in, ideally real
CVEs and real tools (Kali was floated by name). Planned via plan mode
first (approved plan: 3 real paths, added alongside the existing scenarios,
curated real toolset over full Metasploit, Samba/SMB as the real substitute
for an impossible Windows Server target) — see
`specs/network-intrusion.md` for the full design and
`.claude/plans/clever-beaming-magpie.md` for the plan itself.

**Two options researched and rejected before landing on the actual
design:**
- Windows Server: confirmed live that Docker/Colima on this Mac can only
  run Linux containers — a real Windows target would need an actual
  Windows kernel host, not available. Samba/SMB on Linux used instead
  (the real protocol Windows file-sharing uses).
- SambaCry (CVE-2017-7494): checked directly against this machine's real
  package repos — needs Samba 4.4/4.5/4.6.x, only 4.17.x is available via
  `apt`, and a from-source build of that era was judged too fragile to
  rehearse reliably under time constraints. Real, common misconfiguration
  used instead (anonymous/guest SMB share access) — still a genuinely real
  vulnerability class, just not tied to a specific CVE number.

**A pre-built reference image was checked and found dead** (a
`vitalyford/vsftpd-2.3.4-vulnerable` GitHub repo pointed at a Docker Hub
image, `nksnksnks/vsftpd.2.3.4-vuln-osvdb-73573`, that no longer exists —
confirmed via a real `docker pull` attempt, not assumed). Built a minimal,
real, hand-written reproduction of the documented CVE-2011-2523 backdoor
trigger/shell behavior instead — not the literal 2011 binary (no reliable
way to source that safely), but a genuine socket listener + genuine
subprocess shell, verified by hand (real root shell, real `whoami`/`id`/
`uname -a` output, plus a negative-case test confirming a normal login
does *not* trigger it) before any automation was built against it.

**Samba's own logging didn't cooperate.** Tried several real approaches to
get connect-level detection off Samba's own logs directly (`log level` up
to 10, the purpose-built `vfs_full_audit` module) — none reliably surfaced
a usable line on this Samba version's split `rpc_host` worker-process
architecture, confirmed by direct inspection of the actual log output each
time, not assumed from documentation. Pivoted to the same real, independent
pattern `scenarios/web-exploit/proxy/server.py` already uses: a tiny TCP
proxy in front of `smbd` logging every real connection itself. Worked
immediately.

**Real bugs found across 4 live rehearsal runs** (2 with bugs, 2 fully
clean): a network-sweep bug where `tool-api` (dual-homed on two Docker
networks) resolved its own hostname to pick a subnet to scan and
non-deterministically got the wrong network's IP, sweeping an entirely
wrong subnet (0 real hosts found, 0 confirmed findings for that whole run)
— fixed by resolving a known single-homed target instead of tool-api's own
ambiguous hostname; a missing capability where the attacker could crack
SSH credentials but had no tool to *use* them, so it re-ran the
brute-force three times in one run and then hallucinated a fake shell
command in prose — fixed by adding a real `ssh_shell` tool; and noisy raw
shell output from the vsftpd exploit bloating conversation context enough
to contribute to a real model-turn timeout — fixed by stripping the noise
at the source and raising this scenario's turn timeout.

**Verified live, final clean run:** real recon (host discovery + per-host
port scans) correctly identified all three targets by name; SSH
brute-force → real shell login → real enumeration, once each, no repeats;
the real vsftpd backdoor triggered a real root shell; anonymous SMB access
pulled the real confidential file; the attacker used `cover_tracks` as a
natural closing move; defender showed real restraint (flagged multiple
times, blocked only once with real justification); 9 confirmed findings
in the final report with real legal citations.

**Legal map:** 2 entries reused from `scenarios/web-exploit/legal-map.json`
(`cfaa-1030a2`, `cfaa-1030a2-misconfig`) — checked that the underlying
legal elements genuinely fit these new fact patterns before reusing them,
not copied by convenience. Documented in the file's own `_note`.

**README update:** yes, in this change — `README.md` (the "Why scripted"
and "Status"/"Responsible use" sections, which previously said "every
technique targets Juice Shop," now stale) and `demos/README.md` (a full
setup/run/reset walkthrough, mirroring the agentic scenario's section).

**A process note, not a build note:** several actions this session
(directory creation, `docker build`/`run`, and later a diagnostic `curl`+
`docker network inspect`) were blocked mid-build by auto mode's safety
classifier, which the tool's own error message attributed to this
conversation's accumulated content (real exploit code, backdoors,
brute-forcing) rather than any specific action, and which it said would
keep recurring for the rest of the conversation. The founder switched to
manual mode each time to unblock progress. Worth knowing for future
sessions continuing this kind of work: expect this in auto mode, not a
one-off.

**Pre-ship checklist:** not rehearsal-gated — 4 runs happened, not the
required 3 *consecutive clean* runs on the real laptop (2 of the 4 found
real bugs, which is exactly what rehearsal is for, but doesn't count
toward the gate). `bench-models.sh`'s existing pick (shared with the
agentic scenario) still needs its real-laptop re-run per working
agreement #7 before either scenario is presentable.

---

## 2026-08-23 (Phase 2 follow-up #3) — End-of-run incident report + attacker anti-forensics

**What:** Founder request: at the end of a run, have the defender try to
gather as much evidence as possible, have the attacker try to cover its
tracks in response, and have the defender present a report and back up
evidence for "trial" -- honestly stating when nothing was found.

**Key decision: the report is deterministic, built directly from the real
event/access logs, not LLM-generated prose.** Same "never fabricate a
finding or citation" bar this repo already holds legal content to. The
defender's model doesn't write it; `tool_investigate_incident()` in
`tool-api/server.py` does, the same way the legal-overlay panel is built
from real events joined against `legal-map.json` rather than generated
text. It's still narratively the defender's action (posted as an
`actor: defender` event, triggered by the defender's own process).

**Attacker's `cover_tracks`, scoped to what's actually real**: this
session's own recon (`resolve_target`/`port_scan`, added earlier this day)
already established it never had filesystem or host access -- only the
web app was ever open. So real log *deletion* was never offered as an
option (it would have been fake); what's real and available is flooding
the shared access log with decoy HTTP traffic through the same proxy
every other action already uses. Verified this has a genuine, measurable
effect without being able to erase what's already been independently
detected (detection already happened before a report is ever compiled).

**Real burst-detection heuristic, tuned from a real baseline measurement**:
initially set the raw-log burst threshold at 15 requests/5s: false-
positived immediately on a clean-slate test with zero attack activity,
because Juice Shop's own socket.io connection handshake alone bursts
~17 requests in 5 seconds on a normal page load. Measured the actual idle
baseline directly rather than guessing again, raised the threshold to 30
-- comfortably above real background noise, comfortably below
`cover_tracks`' 40-request burst. Deliberately does not read the
attacker's own request count from shared session state (that would be
unrealistic omniscience a real investigator wouldn't have) -- the
detection has to come from the raw log itself, same sliding-window
technique the real detector already uses for enumeration.

**Orchestration fix required**: the defender's reactive loop runs for up
to 600s independently polling for alerts -- it had no way to know the
attacker was actually done. Added `attacker_finished` to the dashboard's
`/control` state, set by `run-agentic.sh` once the attacker's foreground
process exits; the defender's loop checks it each cycle, handles one more
trailing alert if there is one, then moves to the guaranteed final report.
Waiting on the defender process changed from a blind sleep to a bounded
poll (exits as soon as it actually finishes, capped at 20s) rather than
either an open-ended wait or a fixed sleep that might cut the report off
mid-compile.

**Verified live, twice**: a clean-slate run (nothing attempted) produced
an honest "no confirmed malicious activity" report with no false burst
detection -- confirming the fix actually held, not just that it compiled.
A full run (real attack chain including a persistence-driven takeover win,
proper defender restraint, two `cover_tracks` calls as the attacker's own
closing move) produced a 9-finding report, correctly flagged an 88-request
burst as a possible obscuring attempt while explicitly noting the
confirmed findings were unaffected, and backed up both logs to real,
verified files (`diff`-confirmed the backup is a byte-for-byte snapshot,
one line short of the live file since the report event is appended after
the snapshot is taken -- correct chain-of-custody behavior).

**README update:** yes, `demos/README.md` -- mentions the report/evidence-
backup phase.

**Pre-ship checklist:** unchanged, still not rehearsal-gated on the real
laptop.

---

## 2026-08-23 (Phase 2 follow-up #2) — Defender restraint, attacker persistence toward a real win

**What:** Founder watched more runs and reported never actually seeing the
attacker win, and suspected the defender was overreacting. Confirmed by
inspecting the actual test output from the prior entry: the defender had
called `block_attacker` on the very first, lowest-severity alert (an
exposed-file finding), and after one failed `account_takeover` guess the
attacker abandoned that goal and wandered into unrelated path-guessing
instead of trying other enumerated users.

**Fixed with code-level guards, not just prompt rewording** (consistent
with `ensure_reasoning()` from the first build entry — small models don't
reliably follow prompt-only discipline):
- `block_attacker` now requires the defender to have flagged/escalated at
  least twice first (`SESSION["defender_signals"]`); an early call
  downgrades to a flag instead of a block, with a message explaining why.
- Attacker prompt rewritten to make working through the enumerated-user
  list for `account_takeover` the explicit, immediate next move after a
  failed guess, not one option among many.
- A `MIN_TURNS_BEFORE_CONCLUDING = 10` floor in `attacker_agent.py`:
  rehearsal (while testing the above two fixes) surfaced a run where the
  attacker concluded after only 3 turns of pure recon, nothing attempted —
  a "no tool call" before turn 10 now gets rejected with a nudge instead of
  accepted as a real conclusion.

**Also fixed while touching this code**: `probe_path`'s miss description
now explains *why* a 200 doesn't mean success (Juice Shop's SPA serves its
own default page for any unmatched route) — the founder had reasonably
read "got 200" on the dashboard as a positive signal being ignored, when
it was actually a correctly-classified miss with a confusing description.

**Verified live** across 3 rehearsal runs during this fix: run 1 (before
the turn floor) genuinely stalled at 3 turns, confirming the floor was
needed, not a hypothetical; runs 2 and 3 (after all three fixes) both
produced the target shape — defender flagged 2-3 times before its one
justified block, attacker achieved a real account takeover by working
through bender → admin → jim (two honest failures, one real success, not
a scripted outcome), and recovered from the block afterward to continue
to the basket-IDOR finding. Full details:
`specs/local-llm-agents.md`'s "Follow-up, 2026-08-23" section.

**README update:** not needed this pass — no user-visible capability
changed, only run-to-run behavior tuning within the same feature set
already documented.

**Pre-ship checklist:** unchanged — still not rehearsal-gated on the real
laptop. Worth noting: the 3-consecutive-clean-runs gate should probably be
interpreted as "3 runs that reach a coherent conclusion," not "3 runs that
all end in a successful takeover" — the whole point of this fix was
*honest* variance (real misses are fine, real wins should be reachable),
not a guaranteed outcome.

---

## 2026-08-23 (Phase 2 follow-up) — More attacker variety, real network recon, resilient defender block

**What:** Founder feedback after watching a few runs: too samey, wanted
real freedom for the attacker to try unconventional things, real
network-level recon (IP resolution, port scanning) alongside the web-app
techniques, and a much higher turn budget where a defender block is a
setback the attacker learns from and recovers from, not a hard stop.

**Two new attacker tools, both verified real before building anything**:
`guess_common_credentials` (confirmed live that `admin@juice-sh.op` /
`admin123` is a genuine seeded weak credential in this app — not invented)
and `check_other_baskets` (confirmed live: one session token reads other
users' shopping baskets via `/rest/basket/{id}` — a real IDOR, different
endpoint from the existing user-record enumeration).

**Two new network-recon tools**, targeting the real `juice-shop` container
directly (not the demo's own logging proxy) via stdlib `socket` — no new
dependency: `resolve_target` (DNS) and `port_scan` (real TCP connect
scan). Verified live: only port 3000 is genuinely open; separately
confirmed `/.git/HEAD` and `/backup/config.json` (paths that looked
plausible to test) are just the Angular SPA's fallback shell by checking
content-type/body, not assumed from a status code alone — same false-
positive class already fixed once before (see the 2026-08-22 entry below).

**`block_attacker` redesigned** from a permanent "nothing works after this"
flag to revoking the current session token specifically. Recon tools were
never session-gated; the two auth tools still work post-block (the
vulnerabilities aren't patched by revoking one token); the three
session-requiring tools fail cleanly and tell the attacker to
re-authenticate. Learned state (enumerated users, tried paths, tried
takeover targets) persists across a block — verified live that a repeated
`probe_path` on an already-checked path returns instantly with "already
checked, try something different" instead of hitting the network again.
This is a more honest model of what blocking a session actually
accomplishes, not just a mechanism for "more variety."

**Turn caps raised substantially** (attacker 14→40, defender reactions
6→15, defender timeout 300s→600s) with two things fixed alongside that a
naive bump would have broken silently: `run-agentic.sh`'s post-attacker
`wait` on the defender changed to a bounded 8s grace period (an unbounded
wait would now hang the script for minutes), and Ollama's `num_ctx` set
explicitly to 8192 in every call (was defaulting to 4096) so a long run's
full tool-call history doesn't silently overflow context and make the
model forget what it already tried — which would have directly undermined
the point of raising the cap.

**Also fixed**: `account_takeover` previously ignored the model's own
stated target and always silently used a server-computed default, so the
model's reasoning ("targeting bender@...") and the real action (always
jim) could disagree — now the model's choice actually drives the action,
and a wrong guess honestly fails instead of being silently corrected.
Tool order is now shuffled per turn (`brain/common.py`), not just fetched
once — rehearsal showed a fixed order biased the model toward whichever
tool was listed first almost every run, independent of what the prompt
said.

**Verified live** (20-turn cap for observability): blocked right after the
first SQLi success; the next enumeration attempt correctly failed; the
attacker recovered via a genuinely different re-auth method
(`guess_common_credentials`, not a repeat of `sqli_login_bypass`) and
continued; explored 9 further distinct, creative paths with zero exact
repeats. Full details and the one open behavioral gap (doesn't always
retry `account_takeover` on a different user after one failure — moved on
to path exploration instead this run): `specs/local-llm-agents.md`'s
"Founder feedback, 2026-08-23" section.

**Honest gap left as-is**: the real detector has no rule for weak-
credential logins or basket IDOR (only the original four patterns), so
those two new attacker techniques currently go undetected. Not silently
patched over — flagged clearly in `specs/local-llm-agents.md` as a real
teaching point (alert coverage gaps are real) and a candidate for a future
pass.

**README update:** yes, `demos/README.md` — the agentic scenario's
description updated to mention the 9-tool menu and the resilient-block
behavior.

**Pre-ship checklist:** unchanged from the entry below — still not
rehearsal-gated (3 consecutive clean runs on the real laptop), still needs
`bench-models.sh` re-run there. This session's changes make the *content*
of each run more varied, not the reliability bar it needs to clear.

---

## 2026-08-22 (Phase 2 follow-up) — Single-shared-model mode verified for dev-machine testing

**What:** Founder asked for a way to test the agentic scenario on this
16GB dev machine specifically (smaller models, or one shared model instead
of two), separate from the real model pick for the 48GB laptop. Rather
than pull new, smaller models untested for tool-calling reliability, tried
the already-downloaded `qwen2.5:3b-instruct` as a **single model powering
both roles** (Option B from `specs/local-llm-agents.md`'s "Model
selection" section — this was previously only a documented fallback, now
actually verified).

Found one real requirement along the way: Ollama's default
`OLLAMA_NUM_PARALLEL` is `1`, which would serialize the attacker's and
defender's concurrent requests to the shared model instead of running them
in parallel. Restarted with `OLLAMA_NUM_PARALLEL=2` — now documented as a
requirement for single-model mode in `specs/local-llm-agents.md`.

**Result:** one fully clean run, 18.5s total, 2.3GB resident (one model,
not two), 100% Metal offload — full real chain including the attacker
correctly recognizing it had been blocked and stopping on its own.
Documented as a dev-convenience config in `specs/local-llm-agents.md` and
`demos/README.md`, explicitly labeled as not a substitute for running
`bench-models.sh` for real on whichever machine ends up presenting.

**README update:** yes, `demos/README.md` — a pointer to the smaller-
machine config next to the existing setup instructions.

**Open risk:** none new — this doesn't change the 3-consecutive-clean-runs
gate or the real-laptop bench requirement, both still open per the entry
below.

---

## 2026-08-22 (Phase 2 build) — Agentic scenario built end-to-end; one clean run, not yet rehearsal-gated

**What:** Built `scenarios/agentic/` from the design in
`specs/local-llm-agents.md`: `tool-api/` (the constrained attacker/defender
action menu, containerized — the "hands"), `brain/` (host-side Python —
`common.py`, `attacker_agent.py`, `defender_agent.py` — the LLM
tool-calling loops, the "brain"), a pause/speed `/control` + `/status`
control plane added to `core/range-dashboard/server.py`, and
`bench-models.sh` for the working-agreement-#7 model check. Requested by
the founder as a follow-on to the design doc, driven end-to-end (planned
via plan mode, approved, then built and rehearsed in the same session)
rather than left as a design-only stretch goal.

**Key architectural correction, made before writing any code**: confirmed
live (not from memory) that Docker Desktop on macOS still cannot pass the
Apple Silicon GPU through to a container in 2026. `specs/architecture.md`'s
original "Ollama runs as a core [Docker] service" line was wrong for this
reason — corrected to host-native Ollama, with the LLM call/tool-selection
loop ("brain") running as a host process and only the actual target-facing
action execution ("hands") containerized on the existing isolated network.
This also sidesteps the `internal: true`-blocks-host-routing trap this repo
already hit once (see the 2026-08-22 build entry below) — the brain never
needs a new network leg into `cyberrange_net`, it reaches the sandbox the
same way the presenter's browser already does, through a published
`127.0.0.1` port.

**Model check, done for real, not assumed:** this build happened on a
16GB Mac mini dev machine, *not* the 48GB demo laptop the design doc
assumes (confirmed with the founder before pulling any models — see
`specs/local-llm-agents.md`'s "Runtime decision" section). Bench results on
the dev machine were still strong: `qwen2.5:7b-instruct` +
`qwen2.5:3b-instruct` concurrently loaded, 100% Metal GPU offload, 6.9GB
combined, 0.6-1.1s warm-turn latency. This validates the mechanism and the
starting model pair, but is explicitly **not** the working-agreement-#7
final pick — that requires re-running `bench-models.sh` on the actual
laptop.

**Four real bugs found by actually running it, not by review** — a
false-positive "exposed file" (Juice Shop's SPA returns 200 for any
made-up path; fixed by matching the detector's own regex before calling
something exposed), an unreliable free-text SQLi payload (a small model
doesn't reliably craft working injection syntax; fixed by making the
verified payload server-side and non-parameterized), a 7B model describing
its next move in prose instead of calling a tool (fixed with a firmer
system prompt + `temperature: 0.2`), and a 3B model never filling the tool
schema's required `reasoning` field (fixed with a code-level fallback
rather than chasing prompt-tuning on the weaker model). Full details:
`specs/local-llm-agents.md`'s "Build + rehearsal notes" section.

**Result after fixes:** one fully clean `reset.sh` → `run-agentic.sh` cycle
— real attack chain (recon → exposed file → SQLi bypass → enumeration →
account takeover, all real requests against real Juice Shop) plus a
defender that escalated correctly (`flag_session` on the first three real,
independently-detected alerts, `block_attacker` on the critical one, which
then genuinely blocked the attacker's next action — not just a narrated
block). 22.8s reset, 23.7s run. Verified visually in-browser too: pause
button, speed selector, and per-actor "thinking" status pills all round-
trip to the server correctly.

**README update: yes, in this change** — "Why scripted?" section and
"Status" both updated to reflect the agentic scenario now being built
(with the not-yet-rehearsal-gated caveat stated plainly, not glossed over),
plus a full setup/run/reset walkthrough added to `demos/README.md`,
mirroring the existing `web-exploit` section. Per working agreement #8.

**Pre-ship checklist results:**
- Matches roadmap: yes — this is exactly Phase 2.
- Reset tested: yes, full `down -v && up` cycle, not a partial/lightweight
  clear (the detector's in-memory dedup state is why — see below).
- Reset → run → reset cycle: yes, timed, one full clean pass.
- Wifi disconnected: not tested for this scenario either (carried over
  open item from Phase 1, see the entry below).
- Legal claims cited/TBD: unchanged from `web-exploit` — the agentic
  scenario's `legal-map.json` reuses the same, already-sourced entries
  since it hits the same real endpoints with the same real payloads.
- **3-consecutive-clean-runs gate: NOT met.** One clean run happened this
  session; the gate requires three, on the actual demo laptop, not this
  dev machine. **This scenario is not yet cleared to present live** — see
  `ROADMAP.md` Phase 2's explicit "still open" list.
- Projector legibility: inherits the already-fixed sizing from the
  `web-exploit` pass below (same dashboard, same CSS) — the new pause/
  speed controls and status pills were sized consistently but not
  separately re-checked from lecture-hall distance.

**Open risks / not yet done:**
- The 3-run rehearsal gate itself, on the real laptop.
- `bench-models.sh` re-run on the real laptop — the dev-machine numbers are
  a strong signal, not the final working-agreement-#7 record.
- The attacker's system prompt now states the intended chain order
  explicitly, which is more deterministic than a fully open-ended agent —
  a deliberate reliability trade-off, documented in
  `specs/local-llm-agents.md`, but worth the founder knowing it was made.
- A stray `ollama serve` process (not the `brew services` launchd job,
  which didn't start cleanly in this sandboxed session — unclear if that's
  a sandbox artifact or would recur on the real laptop) is what's actually
  running Ollama for this session's testing. Worth confirming
  `brew services start ollama` behaves normally in a regular interactive
  session on the real machine before relying on it for the lecture.

---

## 2026-08-22 (pre-lecture test) — Projector legibility fixed; wifi test deferred by founder

**What:** Founder asked to run the two remaining pre-lecture checks live.
One found a real bug and got fixed; the other is explicitly deferred, not
skipped.

**Projector legibility — found a real problem, not a formality.** Checked
the dashboard's actual CSS font sizes against standard presentation-
legibility guidance (body text generally wants 26px+ for room-distance
viewing) before eyeballing anything: event text was 19px, legal-card body
text 17px, metadata/badges 12-15px — all sized for a laptop screen up
close, not a projector. Fixed in
`core/range-dashboard/server.py` — event text → 27px, legal-card statute
headers → 27px, legal-card body → 23px, header title → 40px, metadata
throughout roughly 1.3-1.4x larger. Verified visually after rebuilding: ran
the full attack chain, screenshotted the dashboard at both a laptop-sized
viewport and a 1920×1080 presentation resolution — layout holds cleanly at
both, no overflow, no awkward wrapping.

**Wifi-disconnected test — deferred by the founder to run later, not
performed today.** Before starting it, flagged clearly that disabling the
Mac's wifi is a system-settings change Claude cannot make even on request
(see the Prohibited-actions list) — this was always going to be a founder-
administered step. The founder chose to defer it rather than do it in this
session. Static verification was still done first as partial reassurance:
grepped every Python file in `demos/v1-cyber-range/` for `http://`/`https://`
references and confirmed the only hostnames anywhere are internal Docker
service names (`juice-shop`, `proxy`, `range-dashboard`) and localhost — no
code path anywhere makes or could make a real external call. This doesn't
replace the real test (Docker/Colima networking behavior with the host
adapter fully down is still unverified), but it's a reasonable partial
signal while the real test is pending.

**README update:** none needed — this was an internal styling fix and a
test-scheduling decision, nothing a student running the demo needs to know
differently. Noting the "no" explicitly per working agreement #8 rather
than skipping the question.

**Pre-ship checklist results:**
- Matches roadmap: yes — this is exactly the two Phase 1 open items.
- Reset tested: yes, reset → run → screenshot cycle, no manual fixes
  needed after the font-size change.
- Wifi disconnected: **still not tested** — see above, deferred, not done.
- Projector legibility: **now checked and fixed**, not just checked.

**Open risks / not yet done:**
- Wifi-disconnected test — still open, now explicitly on the founder's
  plate to run before the lecture, whenever they choose to.
- Legal-citation verification pass against primary statute text — still
  open, unchanged from prior entries.

---

## 2026-08-22 (publish) — Pushed public to GitHub, added README, new standing rule: README stays in sync

**What:** Founder asked to push the whole workspace to
`https://github.com/pitfal-solutions/cyber-ai.git`, explicitly as a public
repo meant to be shared with students — and asked for a good README, plus a
standing rule that every future update also updates it.

**The remote repo already existed, non-empty** — one prior commit
("Initial commit," by the founder) containing an Apache 2.0 `LICENSE`, no
other files. Not overwritten: fetched it, rebased local `main` onto
`origin/main` (`git checkout -B main origin/main`) so the LICENSE carried
forward as a tracked file rather than being clobbered by a divergent
history or a force-push. Confirmed via `gh api` before touching anything —
didn't assume an empty repo.

**Added `README.md`** at the repo root — the actual public front door,
distinct from `CLAUDE.md` (which is the internal "how an AI pairs on this
repo" manual, not written for a student audience). Covers: what the demo
is and why it's dual-audience, what the three challenges actually are, a
copy-pasteable quick start, a short honest architecture summary (including
that the attack is scripted but the detection is real), the legal-content
sourcing caveat, why it's scripted rather than fully autonomous, and a
**Responsible use** section — explicit that every technique here targets
an app built to be attacked (OWASP Juice Shop) and that the same techniques
against a real system without authorization are the actual crimes the
demo's own legal panel describes. That last section was not asked for
explicitly but felt necessary for a public repo of real exploit code aimed
at students — flagging it here rather than silently deciding it was
optional.

**New standing rule, added to `CLAUDE.md` as working agreement #8:** this
repo is public and README-first — any change that affects what's built, how
to run it, or what's next must update `README.md` in the same change, not
as a follow-up. Also added to the "When you finish meaningful work"
checklist so it isn't just a one-time note that gets forgotten. Also added
a `.gitignore` (OS/Python cruft, plus a defensive rule for the demo's
runtime `.jsonl` files, even though those actually live in a Docker volume
today, not the working tree — cheap insurance if that ever changes) and
updated `CLAUDE.md`'s repo-map table to list `README.md` and `LICENSE`.

**Pushed:** commit `940c712` on top of the founder's `e7311c0`, 35 files,
to `main`. Confirmed live afterward via `gh api` (file tree matches) and by
reading the rendered README content back from the GitHub API rather than
just trusting the push succeeded.

**Pre-ship checklist results:**
- Matches roadmap: this is publication/packaging, not a roadmap phase —
  N/A.
- Small enough to review: no — this was the entire workspace's first
  publish, unavoidably a large single push. Flagging honestly rather than
  claiming otherwise.
- Reviewed before staging: yes — `git status` inspected after `git add -A`,
  confirmed no secrets/credentials/`.env`-style files in the diff before
  committing.
- README kept in sync: yes, by definition — it was written as part of this
  same change.

**Open risks / not yet done:**
- No CI, no license header on individual source files, no CONTRIBUTING.md
  — none of this was asked for; noting as options if the repo grows beyond
  a single-lecture artifact.
- The wifi-disconnected test, projector legibility check, and primary-
  source legal verification pass are all still open from prior entries —
  unchanged by this publish.

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
