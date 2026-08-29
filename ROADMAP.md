# Roadmap

## Phase 0 — Workspace + research (done, 2026-08-22)

- Set up the AI-employee workspace structure (this file, `CLAUDE.md`,
  `REVIEW.md`, `context/`, `customers/`, `specs/`, `demos/`, `routines/`).
- Researched the tech stack: existing OSS cyber-range/adversary-emulation
  tooling, vulnerable target apps, SIEM/dashboard options, local-LLM
  feasibility on the M4/48GB laptop, and relevant skills on skills.sh. Full
  writeup: [context/tech-stack-research.md](context/tech-stack-research.md).
- Confirmed scope with the founder: speaker-run demo only, modular
  multi-scenario architecture from day one, one deterministic scripted
  scenario as the guaranteed lecture deliverable, agentic local-LLM scenario
  as a same-window stretch goal, fully offline/air-gapped at runtime.

**Open item carried forward:** which state's computer-crime statute to pair
with federal CFAA depends on the institution — not yet known. See
[context/legal-framework.md](context/legal-framework.md).

## Phase 1 — Scenario 1, scripted, deterministic (the lecture deliverable)

**Status: built and verified end-to-end, 2026-08-22.** Full build log in
[REVIEW.md](REVIEW.md). Live in `demos/v1-cyber-range/` — see
[demos/README.md](demos/README.md) to run it.

1. ✅ Core infra (`specs/architecture.md`): isolated Docker network
   (`internal: true`) plus a second, non-isolated network used only for
   publishing the dashboard/proxy ports to the host (see REVIEW.md for why
   a second network was needed — the original single-network design didn't
   actually work), reset script, base compose file.
2. ✅ Scenario module 1 — **web exploit → data breach** against OWASP Juice
   Shop (`specs/scenario-web-exploit.md`): a fixed sequence of real HTTP
   requests reproducing a verified SQLi login bypass + broken-object-level-
   authorization data exposure. Deterministic and rehearsed (twice, cleanly),
   not live-generated.
3. ✅ Defense side: a lightweight custom detector (not Wazuh — see
   `specs/dashboard.md` for why that swap was made) watches the proxy's
   independent traffic log and fires real alerts on the real attack
   pattern. The *detection* is real; only the offense's choice of actions is
   pre-set.
4. ✅ Legal-overlay panel (`specs/legal-overlay.md`): built into the same
   dashboard page as the technical timeline. Each event is tagged with a
   MITRE ATT&CK technique ID and a `legal_ref` key joined against
   `legal-map.json` (federal CFAA + Colorado statutes — see
   `context/legal-framework.md`).
5. ✅ Rehearsal: `reset → run → reset → run` cycle completed twice, ~22s per
   reset, identical results both times, zero manual intervention.
6. ✅ One-command machine setup (added 2026-08-28):
   `demos/v1-cyber-range/setup.sh` installs + starts Colima/Docker/Ollama,
   pulls the models, and pre-builds every scenario's images (offline-at-
   showtime prep). Idempotent; see [demos/README.md](demos/README.md).

**Pre-lecture checks:**
- ✅ Projector legibility — checked and **fixed**, not just confirmed fine.
  Dashboard fonts were sized for a laptop screen up close (19px event text,
  17px legal text); bumped to presentation-appropriate sizes (27px/23px,
  40px header) and verified at both a laptop viewport and 1920×1080. See
  [REVIEW.md](REVIEW.md).
- ⏸️ Wifi-disconnected test — **deferred by the founder**, 2026-08-22, to
  run later. Requires physically disabling the network, which is outside
  what Claude can do (system-settings changes are off-limits) — this is a
  founder-only step regardless of when it happens. Do this before the
  actual lecture, not skipped entirely.
- Legal-citation verification pass against primary statute text still not
  started — see
  [routines/refresh-legal-citations.md](routines/refresh-legal-citations.md).

**Out of scope for Phase 1:** anything non-deterministic, student-facing
access, additional scenarios, auth.

## Phase 2 — Agentic scenario (stretch goal, same build window if time allows)

**Status: built, 2026-08-22, one clean run verified on the dev machine —
not yet rehearsal-gated for the actual lecture.** One local LLM plays
attacker (tool-calling against a constrained toolset), a second plays
defender/analyst, both via a host-native Ollama (not Docker — Metal GPU
passthrough isn't available to containers on macOS, see
[specs/architecture.md](specs/architecture.md)'s "Local LLM runtime"),
both fully offline. Ships as an *additional* scenario module
(`demos/v1-cyber-range/scenarios/agentic/`) — Phase 1's scripted scenario
stays as the guaranteed fallback regardless of how this goes. Full design,
what was built, and real bugs found+fixed during the first rehearsal pass:
[specs/local-llm-agents.md](specs/local-llm-agents.md).

**Still open before this can be presented:**
- `bench-models.sh` re-run on the actual 48GB demo laptop (the build/
  rehearsal above happened on a different, 16GB dev machine — see working
  agreement #7 and local-llm-agents.md's model-selection section).
- The 3-consecutive-clean-runs gate itself (one clean run ≠ three).

**Go/no-go for presenting this live:** only presented at the lecture if it
survives at least 3 clean rehearsal runs with no manual intervention, on
the actual demo laptop. No exceptions — see working agreement #1.

## Phase 2c — Network-intrusion scenario (real OS/server attacks, not just web)

**Status: built, 2026-08-24, 4 live rehearsal runs (2 with real bugs found
and fixed live, 2 fully clean) — not yet rehearsal-gated.** Founder
feedback on Phase 2: even after real tuning, the Juice Shop scenario kept
feeling repetitive — one target, one protocol, a handful of similar HTTP
techniques. This is a second, additional agentic scenario
(`demos/v1-cyber-range/scenarios/network-intrusion/`) targeting real
OS/network-level services instead: three separate hosts (weak SSH
credentials, the real CVE-2011-2523 vsftpd backdoor, anonymous SMB share
access), attacked with real industry-standard tools (`nmap`, `hydra`,
`smbclient`) rather than custom HTTP-client code. Reuses the same core,
brain/hands split, and every reliability lesson from Phase 2's build —
this is a target/toolset swap, not a rebuild. Full design, the real CVE/
tooling research, and the bugs found rehearsing it:
[specs/network-intrusion.md](specs/network-intrusion.md).

**Updated 2026-08-28 — two behavior changes landed this session (see
[REVIEW.md](REVIEW.md)):** (1) a `plant_marker` attacker tool that writes a
real "ATTACKER WON" file to a backdoored host and reads it back (the
"visible win" the founder asked for; the SMB confidential-file exfil already
existed), and (2) the attacker-vs-defender outcome is now balanced to a real
toss-up via a per-run coin flip on whether an earned block lands
(`BLOCK_SUCCESS_PROB`, default 0.5) — timing tuning alone could not produce
a stable ratio. Measured ~5/3 attacker over 8 runs at Normal pace.

**Still open before this can be presented:** same as Phase 2 above — a
real `bench-models.sh` pick on the actual demo laptop, and the
3-consecutive-clean-runs gate. **The gate clock effectively restarts for
this scenario:** the prior 4 rehearsal runs predate the plant_marker +
coin-flip changes, so the 3 clean runs must be re-done against the current
code. Also additive, not a replacement — both Phase 2 and Phase 2c are
optional; the scripted Phase 1 scenario is the only guaranteed lecture
deliverable either way.

## Phase 3 — Additional scenarios (post-lecture, reuse-driven)

Add as new scenario-plugin modules on the same core, no core changes
required per working agreement #3:

- **Ransomware / lateral movement.** Researched full Active Directory labs
  (GOAD) for this and rejected them for this project — VM-based, heavy
  provisioning, poor fit for a laptop demo on this timeline. Prefer a
  lightweight Docker-only lateral-movement mock (2-3 minimal Linux
  containers with intentionally weak shared credentials) instead of a full
  AD environment. See [context/tech-stack-research.md](context/tech-stack-research.md).
- **Phishing → credential theft → account takeover.** Simplest infra of the
  three original candidates; strong identity-theft/wire-fraud legal angle.

## Phase 4 — Reuse hardening for future classes

- Legal-citation refresh routine (statutes and penalty ranges can change) —
  see [routines/refresh-legal-citations.md](routines/refresh-legal-citations.md).
- CVE/technique refresh for the target app if Juice Shop ships a version
  bump that changes exploitability.
- Optional take-home / self-serve version for students, if a future
  instructor wants hands-on access instead of (or in addition to) the
  speaker-run format — this would revisit working agreement #6 and needs
  its own scoping pass, not an assumption.
- Polish: tighten narration timing, add a second dashboard view sized for
  projector readability from the back of a lecture hall.
