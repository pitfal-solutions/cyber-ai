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

**Still open before the lecture (not done yet):**
- Test with the laptop's wifi/network adapter physically disconnected —
  everything so far has been verified with network active.
- Check dashboard legibility from projector distance, not just a laptop
  screen.
- Run the legal-citation verification pass against primary statute text
  (current content is sourced from real secondary sources, not yet a final
  legal-review pass) — see
  [routines/refresh-legal-citations.md](routines/refresh-legal-citations.md).

**Out of scope for Phase 1:** anything non-deterministic, student-facing
access, additional scenarios, auth.

## Phase 2 — Agentic scenario (stretch goal, same build window if time allows)

Only attempted after Phase 1 is rehearsed and solid. One local LLM plays
attacker (tool-calling against a constrained toolset), a second plays
defender/analyst, both via Ollama, both fully offline. Ships as an
*additional* scenario module — Phase 1's scripted scenario stays as the
guaranteed fallback regardless of how this goes. See
[specs/local-llm-agents.md](specs/local-llm-agents.md) (design only, not yet
built) and working agreement #7 in `CLAUDE.md` on why exact model names
aren't pinned yet.

**Go/no-go for presenting this live:** only presented at the lecture if it
survives at least 3 clean rehearsal runs with no manual intervention. No
exceptions — see working agreement #1.

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
