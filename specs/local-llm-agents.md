# Local LLM agentic scenario (Phase 2)

Status: **built and passing on the dev machine, 2026-08-22 — not yet
rehearsal-gated.** One full clean `reset → run` cycle verified end-to-end
(real attack chain, real detection, real defender response). Still needs:
`bench-models.sh` re-run on the actual demo laptop (not this dev machine —
see "Model selection" below), and the 3-consecutive-clean-runs gate before
this is ever presented live. Stretch goal — see working agreement #1 and
the Phase 2 go/no-go rule in [../ROADMAP.md](../ROADMAP.md).

## Runtime decision: Ollama runs on the host, not in Docker

Confirmed 2026-08-22, live check: Docker Desktop on macOS still cannot pass
the Apple Silicon GPU (Metal) through to a container — this is architectural
to Docker Desktop's Linux-VM design on Mac, not a version gap. A dockerized
Ollama on this laptop would mean CPU-only inference, too slow for live,
turn-by-turn pacing. This corrects [architecture.md](architecture.md)'s
original "Ollama runs as a core service" line, which assumed a Docker
service.

This also sidesteps a trap already hit and documented in
[../REVIEW.md](../REVIEW.md): a Docker network with `internal: true` blocks
*all* routing out of it, including a container reaching
`host.docker.internal` — not just internet egress. Giving attacker/defender
containers a second network leg to reach a host-side Ollama would break the
"attack containers never join any other network" invariant the isolation
story rests on.

**Resolution — split brain from hands, same trust boundary the dashboard
already uses:**
- **Brain** (the actual LLM calls + tool-selection loop) runs as a **host
  Python process** (`brain/attacker_agent.py`, `brain/defender_agent.py` in
  the new `scenarios/agentic/` module), talking to local Ollama at
  `127.0.0.1:11434` and to the sandbox only through the same kind of
  narrow, published `127.0.0.1` port the presenter's own browser already
  uses to reach the dashboard. The brain is host-trusted, exactly like the
  presenter's browser is today — no new trust boundary invented.
- **Hands** (actually executing a chosen action against the target) stay
  containerized on the existing isolated `cyberrange_net`, exactly like
  today's `web-exploit/attacker/` container — via a new `tool-api`
  container exposing the constrained action menu below as HTTP endpoints.

## Goal

A genuinely non-deterministic scenario: one local LLM plays attacker
(chooses and executes actions via tool-calling against a constrained
toolset), a second plays defender/analyst (interprets alerts, responds),
both running fully offline via Ollama on the M4/48GB laptop.

## Why constrained, not open-ended

An unconstrained agent (free-form shell access, arbitrary tool choice) is
both a reliability risk for a live demo and unnecessary — the useful
signal for the audience is "the model chose this specific ATT&CK-mapped
technique," not "the model has root." Constrain the attacker's tool
surface to a fixed menu of scripted-but-parameterized actions (e.g. "attempt
SQLi against endpoint X with payload Y" as a callable tool, not raw shell
exec), mirroring how Caldera structures its ability library — see
[../context/tech-stack-research.md](../context/tech-stack-research.md).

## Model selection + concurrency shape

Per working agreement #7: don't commit to a specific model name from
research alone. Decision framework settled 2026-08-22 — two real Ollama
mechanisms map directly onto "run 2 models vs. serve 2 users off 1 model":
`OLLAMA_MAX_LOADED_MODELS` (distinct models loaded concurrently) vs.
`OLLAMA_NUM_PARALLEL` (one model, N concurrent request slots, memory scaling
with `NUM_PARALLEL × context_length`).

**Recommendation (not yet bench-verified on the actual machine — see
`scenarios/agentic/bench-models.sh`): two distinct models**, one per role —
attacker on a 7-14B-class tool-calling model, defender on a lighter ~3B
class, matching the split below. Distinct models give the attacker and
defender distinguishable "voices" on a projector, which a single model with
two system prompts wouldn't. Fall back to one shared model +
`OLLAMA_NUM_PARALLEL=2` only if the bench script's real memory/latency
numbers say two concurrent models miss the pacing target.

- Attacker agent loop: a 7-14B-class tool-calling-capable model (e.g. try
  Llama 3.x or Qwen2.5/3 in that size range as starting points — directional,
  not committed).
- Defender agent loop / narration: a ~3B-class model, run concurrently.
- Pacing target: ~3-5s per agent turn (model latency, not artificial delay)
  feels dramatic rather than sluggish on a live projector — the bench
  script's real numbers decide the final pick against this target.
- Budget check: both models resident simultaneously, plus the rest of the
  demo's Docker infra (Juice Shop, proxy, detector, dashboard, tool-api —
  all lightweight, no Wazuh in this build, see
  [dashboard.md](dashboard.md)), must fit comfortably under 48GB with real
  headroom — verify actual resident memory via `ollama ps` / Activity
  Monitor during a real run, not just parameter-count math.
- **Dev-machine validation run, 2026-08-22** (`qwen2.5:7b-instruct` +
  `qwen2.5:3b-instruct`, both Q4): both loaded concurrently, **100% Metal
  GPU offload**, 4.7GB + 2.2GB = **6.9GB combined**. Warm-turn latency
  (both models loaded, back-to-back turns) — attacker 1.1s, defender 0.6s,
  both well inside the ~3-5s target. Tool-calling worked correctly
  (`enumerate_endpoint` called with sensible arguments both times).
  **This run was on the 16GB dev Mac mini this build happened on, not the
  48GB demo laptop** (see the runtime-decision section above) — it
  validates the *mechanism* (two concurrent models, Metal offload, tool-
  calling reliability) and that `qwen2.5:7b-instruct` / `qwen2.5:3b-
  instruct` is a solid starting pair, but `bench-models.sh` must be re-run
  on the actual demo laptop before this is the final, working-agreement-#7
  pick — a bigger memory budget likely means room to size up (e.g. a
  14B-class attacker model) rather than a constraint to work around.

## Reliability bar before this is ever presented live

Per the Phase 2 go/no-go rule in [../ROADMAP.md](../ROADMAP.md): **3
consecutive clean rehearsal runs with zero manual intervention**, on the
actual demo laptop, fully offline. If it doesn't hit that bar, Scenario 1
(scripted) is what gets presented — that's an acceptable, planned outcome,
not a failure state.

## Build + rehearsal notes, 2026-08-22 (dev machine)

First build pass, `scenarios/agentic/` (`tool-api/`, `brain/`). Four real
issues surfaced by actually running it against the containerized target,
not by inspection — each is now fixed in `tool-api/server.py` /
`brain/`:

1. **False-positive "exposed file."** The attacker's `probe_path` tool
   originally accepted any path and flagged `status == 200` as exposure.
   Juice Shop's Angular SPA returns 200 for *any* unmatched path (client-
   side routing fallback), so a model-invented path like
   `/.well-known/passive-info` was wrongly reported as an exposed
   confidential file — and the real detector's regex (correctly) never
   fired on it, so tool-api and the detector disagreed. Fixed by matching
   the exact same pattern the detector uses
   (`^/ftp/.+\.(md|pdf|txt)$`) before calling something "exposed."
2. **Unreliable SQLi payload.** Letting the model free-text the injection
   payload (`email_payload` param) failed on a close-but-wrong variant
   (`' OR '1'='1--` got a 401; the verified-working payload is
   `' OR 1=1--`, same as `scenarios/web-exploit/attacker/attacker.py`). A
   small model reliably *decides* to attempt SQLi but doesn't reliably
   craft working injection syntax — removed the parameter entirely; the
   mechanics are now fixed server-side, the model only chooses whether/
   when to call the tool.
3. **Text instead of a tool call.** At default temperature, the 7B
   attacker model sometimes described its next move in prose ("Proceeding
   with further exploration...") instead of calling the next tool, which
   the brain loop (correctly) reads as "done." Fixed with a firmer system
   prompt (explicit "call a tool on EVERY turn," explicit chain order) and
   `temperature: 0.2` in the Ollama request — reliability over creative
   variety, per working agreement #1.
4. **Required schema field silently omitted.** The 3B defender model
   never filled the tool schema's required `reasoning` field (the 7B
   attacker model always did) — rather than chase prompt-tuning on the
   weaker model, `brain/common.py`'s `ensure_reasoning()` synthesizes a
   fallback line (e.g. "Reacting to: <alert description>") when a model
   omits it, so the dashboard always shows something.

**After all four fixes: a fully clean run**, attacker chain (recon →
exposed file → SQLi bypass → enumeration → account takeover, real
requests, real success) plus a defender that escalated correctly —
`flag_session` on the first three real alerts, `block_attacker` on the
critical account-takeover one — with reasoning lines populated on both
sides. Full `reset.sh` → `run-agentic.sh` cycle: **22.8s reset + 23.7s run**
(at 500ms pacing) on the dev machine. This is one clean run, not the
3-consecutive-runs gate (`ROADMAP.md` Phase 2 go/no-go) — that still needs
to happen on the real demo laptop before this is presented live.

**A design trade-off worth naming**: the attacker's system prompt now
states the intended chain order explicitly ("recon, then probe_path, then
sqli_login_bypass, then...") to keep a small model reliably on-task. This
is more deterministic than a fully open-ended agent, but it's a deliberate
choice, not a compromise forced by accident — the audience signal that
matters is "the model chose to attempt this technique, in real time,
against real infrastructure," not "the model discovered a novel attack
order," and reliability for a live demo outweighs order-of-operations
novelty (working agreement #1).

## Quick local test on a smaller machine (dev-machine convenience, not a model pick)

The two-distinct-model recommendation above targets the real 48GB demo
laptop. For iterating on this repo's code itself on a smaller box (this
build's 16GB dev Mac mini), a **single shared model for both roles**
(Option B from "Model selection" above) works well and needs no extra
downloads if `qwen2.5:3b-instruct` is already pulled:

```bash
OLLAMA_NUM_PARALLEL=2 ollama serve   # required -- default is 1, which would
                                      # serialize the two roles' requests
                                      # instead of running them concurrently
ATTACKER_MODEL=qwen2.5:3b-instruct DEFENDER_MODEL=qwen2.5:3b-instruct \
  ./scenarios/agentic/run-agentic.sh
```

Verified 2026-08-22: one full clean run, 18.5s total, 2.3GB resident
(one model, not two), 100% Metal offload — complete real chain (recon →
miss → SQLi bypass → enumeration → account takeover), defender escalated
correctly (flag → flag → block), and the attacker correctly recognized
being blocked and stopped. **This is a dev-convenience config, not a
replacement for the real bench** — when moving to the 48GB laptop, re-run
`bench-models.sh` there and use its two-model recommendation; don't assume
this smaller config's numbers carry over to a different machine.

## Founder feedback, 2026-08-23: more variety, more freedom, real network recon

After the first working runs, founder feedback: it looked the same every
time, and wanted (a) real freedom for the attacker to try unconventional
things, (b) genuine network-level recon (resolve the target's IP, scan its
ports) alongside the web-app techniques, and (c) a much higher turn budget,
with the attacker learning from a defender block instead of just stopping.
All four implemented and verified:

- **Two new, verified-real attacker tools**: `guess_common_credentials`
  (weak/default creds against the real login endpoint — verified live that
  `admin@juice-sh.op` / `admin123` is a genuine seeded weak credential in
  this app, not invented for the demo) and `check_other_baskets` (a real
  IDOR verified live: one session token reads other users' shopping
  baskets by guessing sequential basket IDs, `/rest/basket/{id}`).
- **Real network-level recon tools**: `resolve_target` (DNS-resolves the
  actual `juice-shop` container, not the demo's own logging proxy —
  T1590) and `port_scan` (a real TCP connect scan, stdlib `socket`, no new
  dependency — T1046). Verified live: only port 3000 is genuinely open on
  the target container; several plausible-looking paths tried during this
  work (`/.git/HEAD`, `/backup/config.json`) turned out to be the Angular
  SPA's fallback shell (200, but not real files) — confirmed by content-
  type/body inspection, not assumed, and correctly excluded from the
  exposure pattern. A real scan honestly coming back with "nothing else
  open" is treated as a valid, informative result in the attacker's system
  prompt, not a dead end — it's why the rest of the toolset targets the
  web app specifically.
- **Rigid chain order removed** from the attacker's system prompt (it
  previously stated "recon, then probe_path, then sqli_login_bypass,
  then..." explicitly, for reliability — now it names the two ways to get
  a session and the two IDOR findings as equally valid, and instructs
  trying 2-3 different strategies before concluding an avenue is closed).
  `temperature` raised 0.2 → 0.4, and the tool list is now **shuffled per
  turn** (`brain/common.py`) — rehearsal showed a fixed list order biased
  the model toward whichever tool was listed first (`sqli_login_bypass`
  over the equally-valid `guess_common_credentials`) almost every run,
  independent of prompt wording.
- **`account_takeover` now honors the model's own target choice** (an
  `email` param) instead of silently overriding it with a server-computed
  default — previously the model's stated reasoning ("targeting
  bender@...") could disagree with what the tool actually did (always
  jim). Only jim@juice-sh.op's security answer is actually known
  ("Samuel"), so a different model-chosen target now honestly fails,
  which is correct, not a bug.
- **`block_attacker` redesigned: revokes the current session token, not a
  permanent flag.** The original design made every attacker tool refuse
  forever after one block — technically simple, but not an honest model of
  what blocking a session actually accomplishes (it doesn't patch the
  vulnerability), and it meant the attacker just stopped rather than
  "learning" anything, which is what was actually asked for. Now: recon
  tools were never gated by a session at all; `sqli_login_bypass` and
  `guess_common_credentials` still work after a block (the vulnerabilities
  aren't fixed by revoking one token) so the attacker can re-authenticate;
  `enumerate_user_records`/`check_other_baskets`/`account_takeover` need a
  live token and fail with a clear "get a new one" message otherwise.
  Everything **learned** (`enumerated_emails`, `target_email`,
  `tried_paths`, `tried_takeover_emails`) persists across a block — a
  retried `probe_path` on an already-checked path returns a fast, no-
  network-call "already checked, try something different" result instead
  of repeating it, and a retried `account_takeover` on an already-failed
  email does the same. The defender's loop no longer stops forever after
  its first `block_attacker` call, for the same reason.
- **Turn/reaction caps raised substantially**: attacker `MAX_TURNS` 14 → 40
  (was 8 before that), defender `MAX_REACTIONS` 6 → 15,
  `RUN_TIMEOUT` 300s → 600s. `run-agentic.sh`'s post-attacker wait for the
  defender changed from an unbounded `wait` to a fixed 8s grace period —
  with the defender no longer stopping at its first block, an unbounded
  wait would hang the script for minutes with nothing left to react to.
- **Context window raised explicitly**: `num_ctx: 8192` in every Ollama
  call (`brain/common.py`), up from Ollama's 4096 default. A 40-turn run
  with full tool-call/tool-result history appended every turn would
  otherwise silently overflow context on a long run — which would mean
  the model actually *forgetting* what it already tried, the opposite of
  what raising the turn cap for "learn and don't repeat mistakes" was for.

**Verified live, 2026-08-23** (20-turn cap for observability, not the real
40): blocked immediately after the first successful SQLi bypass; the next
`enumerate_user_records` correctly failed ("no active session"); the
attacker recovered by calling `guess_common_credentials` (a genuinely
different re-auth method, not a repeat of `sqli_login_bypass`) and
succeeded; enumeration then succeeded on retry without needing to be
re-explained. Explored 9 further distinct paths (`.git`, `.env`,
`.htaccess`, `.DS_Store`, `security.txt`, two backup-file guesses, two
admin-path guesses) with zero exact repeats, plus a self-chosen
`account_takeover` attempt (failed honestly on `bender@juice-sh.op`, as
expected). One gap observed: after that failure it moved on to more path
exploration rather than retrying takeover on a different enumerated user
(e.g. `jim`) — acceptable for now (it chose breadth over depth, which is
still real variety), worth revisiting if rehearsal on the real laptop shows
it's a consistent pattern rather than one run's choice.

**Follow-up, 2026-08-23: defender too trigger-happy, attacker didn't
persist toward a real win.** Founder feedback after watching more runs:
the defender was calling `block_attacker` on the very first, lowest-
severity alert (observed live), cutting the attack off before it could go
anywhere; and after one failed `account_takeover` guess the attacker moved
on to unrelated path-guessing instead of trying other enumerated users, so
a genuine full compromise was never actually witnessed. Three fixes,
all code-level guards, not just prompt wording (the same lesson as
`ensure_reasoning()`):

1. **`block_attacker` gated on `defender_signals >= 2`** — calling it
   before the defender has flagged/escalated at least twice downgrades it
   to a flag instead, with a message explaining why. Prompt updated to
   explain real SOC escalation discipline (flag first, block once you have
   real confidence).
2. **Attacker prompt strengthened to persist specifically toward account
   takeover**: on a failed guess, immediately try a different enumerated
   user rather than wandering into unrelated exploration. Since only
   jim@juice-sh.op's security answer is actually known, this doesn't
   guarantee success — it makes success achievable through honest,
   in-fiction persistence (working through a list until one door opens)
   rather than a lucky first guess.
3. **A `MIN_TURNS_BEFORE_CONCLUDING = 10` floor** — rehearsal surfaced a
   run where the attacker concluded after only 3 turns (recon only,
   nothing attempted). A "no tool call" before turn 10 is now rejected
   with a nudge message appended to history rather than accepted as a real
   conclusion. Root cause not fully pinned down (temperature 0.4 variance
   vs. the system prompt having grown long enough to dilute the "always
   call a tool" instruction) — the floor guards against the outcome either
   way, which matters more for a live demo than diagnosing the exact cause.

**Verified live, 2026-08-23, after all three fixes**: a full clean run —
recon, port scan, exposed file, SQLi bypass, enumeration, three
`account_takeover` attempts (bender fails, admin fails, jim succeeds — a
real win, not scripted), defender flagged three times before blocking
(only after the takeover actually succeeded), attacker recovered from the
block by re-authenticating and continued to the basket IDOR, then
concluded naturally with a substantive summary. This is the reference
shape for what a good run looks like.

**Known, honest gap — not fixed in this pass**: the real detector
(`scenarios/web-exploit/detector/detector.py`, reused unchanged) has no
rule for weak-credential logins or basket IDOR — only the original four
patterns (confidential file, SQLi, enumeration, account takeover). Trying
either new technique currently goes undetected by the defender's real,
independent detection. This is left as-is rather than silently patched
over: real detectors don't catch everything either, and it's an honest
teaching moment (alert coverage gaps are real) rather than a bug — but
it's worth knowing this is *why* the defender sometimes has nothing to
react to even when the attacker found something real. A future pass could
add detection rules for these two, following the same pattern as the
existing four.

## End-of-run incident report (added 2026-08-23)

Founder request: at the end of a run, have the defender attempt to gather
as much information about the attack as possible, have the attacker try to
cover its tracks in response, and have the defender present a report and
back up evidence for "trial" -- honestly noting when nothing was found.

**Design call: the report is deterministic, not LLM-generated.** The same
"never fabricate a finding or a citation" bar this repo holds legal
content to (`CLAUDE.md` working agreement #4/#5) applies here -- an LLM
asked to "write an incident report" could plausibly embellish or
misattribute findings, which is exactly what this project can't do. So
`tool_investigate_incident()` in `tool-api/server.py` builds the report
directly from the real event log and the real raw access log, the same
way the legal-overlay panel is built from real events joined against
`legal-map.json`, not generated prose. It's still "the defender's action"
narratively (posted as an `actor: defender` event, triggered by the
defender's own process) -- the LLM just isn't the one writing the factual
content.

**Attacker: `cover_tracks`.** Real log *deletion* was deliberately never
made available -- `resolve_target`/`port_scan` already established this
session never had filesystem or host access (only port 3000 was ever
open), so an attacker that never escalated past the web app has no
realistic way to touch the actual log files. What it CAN honestly do,
purely at the HTTP layer: flood the real access log (via the same proxy
every other action already goes through) with 40 decoy requests per call,
burying the real attack traffic in noise. This is a real, known technique
(indicator removal via noise injection, not deletion) and has a genuine,
verifiable effect on the raw log -- it does not, and structurally cannot,
erase anything the independent detector already fired on, since detection
already happened before this ever runs.

**Defender: `investigate_incident`** (not `/tools/`, not in the LLM's
choosable menu -- a guaranteed final step, called directly by
`defender_agent.py` once the engagement is over, not left to a small
model's discretion given this session's repeated lesson that reliability-
critical steps need code guarantees, not just prompt hope):
- Confirmed findings: every event with a `legal_ref`, listed with its
  technique ID and statute reference. If there are none, the report says
  so explicitly ("this reflects an absence of confirmed findings, not a
  guarantee nothing happened") -- satisfies "if none are found they need
  to make it clear."
- Raw traffic analysis: total real request count, plus a **real sliding-
  window burst detector** (same technique the actual detector already
  uses for enumeration, `detector.py`'s `check_enum`) over the raw access
  log. Deliberately does NOT read the attacker's own decoy-request count
  from shared session state -- a real investigator wouldn't have access to
  that, only the raw log itself, so the detection has to be a real,
  honest inference, not omniscience. Threshold tuned from a real baseline
  measurement: Juice Shop's own socket.io connection handshake alone can
  burst ~17 requests in 5 seconds on a normal page load, so an initial
  threshold of 15 false-positived on pure background/presenter traffic
  with zero attack activity -- raised to 30, comfortably above that noise
  floor and comfortably below `cover_tracks`' 40-request burst.
- Evidence backup: real file copies of `events.jsonl` and `access.jsonl`,
  timestamped, written to the shared volume (`/data/evidence-*.jsonl`) --
  verified live that the backup is a genuine snapshot (byte-for-byte
  match with the live file at that moment, one line short of the final
  file since the report event itself is appended after the snapshot is
  taken -- correct chain-of-custody behavior, not a bug).

**Orchestration**: `run-agentic.sh` POSTs `attacker_finished: true` to the
dashboard's `/control` once the attacker's foreground process exits (a new
field alongside `paused`/`delay_ms`); `defender_agent.py`'s independently-
polling loop checks this each cycle and, after handling any one trailing
alert, breaks out and calls `investigate_incident` unconditionally before
exiting. Waiting on the defender changed from a blind sleep to a bounded
poll (up to 20s, exits early once the process actually finishes) rather
than either an open-ended `wait` (would hang for minutes given the
defender's now-long `RUN_TIMEOUT`) or a too-short fixed sleep (might cut
off the report mid-compile).

**Verified live, 2026-08-23**: a full run -- real attack chain including a
persistence-driven takeover win, defender restraint (3 flags before the
one justified block), attacker's own conclusion including two
`cover_tracks` calls -- produced a 9-finding report, correctly detected an
88-request burst from the cover_tracks activity, explicitly noted
confirmed findings are unaffected by it, and backed up both logs to real,
verified files. A clean-slate run (no activity at all) produced an
honest "no confirmed malicious activity" report with no false burst
detection.

## Event stream + legal overlay

Same shared event shape as every other scenario (see
[architecture.md](architecture.md)) — the agent loop must emit
`attack_technique_id` / `legal_ref` per action it takes, meaning the
constrained tool menu should be defined with these tags attached to each
tool, not inferred after the fact.

## Design questions — resolved 2026-08-22

- **Defender constraint: same constrained-tool treatment as the attacker**,
  not open-ended reasoning, for v1. Reliability for a live demo outweighs
  the marginal realism gain of a freer defender — revisit only if rehearsal
  shows the constrained defender reads as uninteresting.
- **Reasoning shown to the audience: a short one-liner per action**, not raw
  chain-of-thought. The event stream gains an optional `reasoning` field
  (see [architecture.md](architecture.md)) rendered under each action's
  description — legible from projector distance, not a wall of text.
- **Stall fallback: a per-turn timeout (~30s) in each brain loop.** On
  timeout, auto-abort the run and emit a distinct `stalled` event so the
  dashboard shows a graceful narration beat instead of freezing or dead air.

## Pause / speed control (new requirement, 2026-08-22)

The presenter needs to pause the run and adjust pacing live — slow motion
for narration, full speed for dramatic effect — not just via a fixed
env-var delay set at container start (that's `web-exploit`'s `STEP_DELAY`
model, which is fine for a scripted scenario but not for one the presenter
narrates live).

Implementation: extend `core/range-dashboard/server.py` (already a stdlib
`ThreadingHTTPServer` with a locked in-memory event store) with `GET/POST
/control` holding `{"paused": bool, "delay_ms": int}`. Both brain processes
poll it once per turn — sleeping in short increments while paused, so pause
is responsive rather than blocking on one long sleep — and use `delay_ms` to
pace between turns. The dashboard header gets a Pause/Resume button and a
Slow/Normal/Fast/Instant speed selector wired to this endpoint. No new
service — same pattern as the existing event store, just a second locked
dict.

## Visualization (new requirement, 2026-08-22)

Reuses the existing two-column dashboard (`--attacker`/`--defender` CSS vars
already exist) rather than a new page. Adds: the `reasoning` one-liner above,
and a live "thinking…" status pill per actor while a brain is mid-turn (a
lightweight `POST /status` the brain pings at turn start/end, rendered by
the existing 1s poll loop) — turns real LLM latency into visible tension
instead of apparent lag.
