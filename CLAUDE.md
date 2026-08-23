# CLAUDE.md

Operating manual for Claude acting as an AI employee in this workspace,
working with the guest speaker who owns this project. Read this first in any
new session before touching code or docs.

## Work style

- Prefer small, reviewable changes over large ones.
- Explain the plan before editing when the change affects demo behavior
  (what the audience sees, attack/defense logic, legal content, scoring/
  timing). Docs-only or internal-refactor changes don't need a
  pre-explanation.
- Keep changes focused — don't bundle unrelated cleanup into a scenario
  change.
- Run the relevant checks after changes: `docker compose config` (validates
  compose files) at minimum; a full `reset → run → reset` cycle for anything
  touching a scenario, since this has to survive a live, one-shot
  performance.
- Summarize what changed, what was tested, and what needs human review —
  every time, not just on request.

## What this project is

**Product:** A modern, AI-driven cybersecurity demo: a containerized "AI vs
AI" cyber range that runs a real (simulated) attack and a real defensive
response, live, on one laptop.
**Buyer:** The instructor who books the guest lecture.
**Audience (dual-track):** One class, two majors sitting in the same room —
cybersecurity students and law enforcement / criminal justice students.
**Pain we solve:** Most guest lectures pick one lane — either a technical
deep-dive that loses the law-enforcement half of the room, or a legal/policy
talk that loses the technical half. This demo does both at once: an attack
unfolds, the defense responds, and every attacker action is tagged live with
the actual law it breaks and the real penalty attached to it.
**Product promise:** A safe, fully offline, reset-to-zero demo that a
non-technical proctor could eventually re-run, and that's built to grow —
new attack/defense scenarios bolt onto the same core instead of starting
over each semester.
**Our bet:** Build one shared core (isolated network, dashboard, reset
mechanism, local LLM runtime) and treat each attack/defense storyline as a
pluggable **scenario module** on top of it — so "add a new scenario" is
additive work, not a rebuild. See
[specs/architecture.md](specs/architecture.md).

> **Known constraint:** the actual lecture is **2-3 days out** as of
> 2026-08-22. Working agreement #1 below exists because of this — the v1
> scenario must be deterministic and rehearsed, not a live bet on
> non-deterministic AI. See [ROADMAP.md](ROADMAP.md) Phase 1.

Full context: [`/context`](context/). Personas: [`/customers`](customers/).

## Quality bar

- **Runs with zero internet at showtime.** Venue wifi is not a dependency.
  Every image, model, and package must be pulled/pinned ahead of the lecture.
- **Resets to zero in under a minute.** Rehearsal means running this many
  times before the real thing — a slow or unreliable reset kills rehearsal
  time and risks a broken live run.
- **Legally accurate, not legally vibes-based.** Every "this breaks the law"
  claim on screen cites a real statute section. If we haven't verified it,
  it's marked TBD on screen — never a plausible-sounding guess. This is the
  same data-honesty bar the founder runs the photographer-directory project
  on, applied to law instead of contact data.
- **Technically credible.** Cybersecurity students in the room will know if
  an "attack" is fake theater. Prefer real tools and real (if scripted)
  exploitation of a real vulnerable app over a simulated narrative with no
  actual traffic.
- **Clarity for the non-technical half of the room.** The law-enforcement
  track needs to follow what happened and why it matters without parsing
  packet captures — the legal-overlay panel exists specifically for them.

## Repo map

| Path | Purpose |
|---|---|
| `README.md` | **The public front door — students read this first.** Must stay current; see working agreement #8. |
| `LICENSE` | Apache 2.0. Predates this workspace (set when the GitHub repo was created) — preserve, don't replace. |
| `CLAUDE.md` | This file — how to work in this repo. |
| `ROADMAP.md` | Phased plan, current phase, what's next. |
| `REVIEW.md` | Running log of decisions and periodic self-review. Append, don't rewrite history. |
| `context/` | Business context: audience, tech-stack research, legal framework. |
| `customers/` | Personas: the instructor (buyer) and the two student tracks (audience). |
| `specs/` | Architecture and scenario specs — what's built vs. designed. |
| `demos/` | Runnable prototypes. Nothing built yet — see [demos/README.md](demos/README.md). |
| `routines/` | Recurring-task definitions (rehearsal checklist, legal-citation refresh). Documentation only until explicitly scheduled — see [routines/README.md](routines/README.md). |

## Working agreements

These were decided explicitly (2026-08-22, via direct Q&A with the founder)
— don't silently relitigate them without flagging it to the user first:

1. **Scripted-first, agentic-second.** The live lecture runs on a fully
   deterministic, rehearsed scenario. A non-deterministic, locally-hosted
   agentic scenario (two local LLMs, one attacking, one defending) is an
   additive stretch goal for the same build window, and a fast-follow after
   it either way — but it is **never the only thing that can be presented**.
   If the agentic scenario isn't reliable in rehearsal, the scripted
   scenario is what ships to the lecture, and that's a fine outcome, not a
   failure. See [ROADMAP.md](ROADMAP.md) Phase 1 vs. Phase 2.
2. **Fully offline / air-gapped at runtime.** No dependency on venue
   internet or wifi during the demo. All Docker images and LLM weights are
   pulled and pinned in advance; the attack/target/defender containers run
   on a Docker network with `internal: true` (no egress) so there's zero
   risk of the "attack" touching anything real. The presenter's dashboard is
   still viewable via a published localhost port — that's host↔container,
   not network egress, so it doesn't violate the isolation.
3. **One core, many scenario plugins — from day one**, even though v1 ships
   exactly one scenario. A scenario = an attack chain + a defense playbook +
   a legal-mapping file, dropped into the shared network/dashboard/reset
   machinery. New scenarios must not require touching the core. See
   [specs/architecture.md](specs/architecture.md).
4. **Legal content must be real and cited.** Federal CFAA (18 U.S.C. § 1030)
   is the baseline; state statute is TBD until we know the institution's
   state (flag this to the founder — see [context/legal-framework.md](context/legal-framework.md)).
   Never fabricate a statute, citation, or penalty number. Mark unverified
   items as TBD on screen rather than guessing — same honesty principle as
   the photographer-directory project's data rules, applied to law.
5. **Reset-to-zero is a hard requirement.** Every scenario must cleanly
   return to its starting state (`docker compose down -v && up`) — this
   will be rehearsed many times before the live run and reused in future
   semesters.
6. **Speaker-run only, v1.** No student-facing access, no auth, no
   multi-tenant infra. One presenter, one laptop. (Confirmed 2026-08-22 —
   don't add multi-tenant scope without re-asking.)
7. **Don't pin exact local-LLM model names from research alone.** Model
   availability and quality shift fast; the research in
   [context/tech-stack-research.md](context/tech-stack-research.md) gives a
   *class* of model to start from (7-14B tool-calling class for the agent
   loop, ~3B class for narration), but the final pick happens via a real
   `ollama run` memory/latency check on the actual M4/48GB machine in
   Phase 2, not by trusting a blog post's specific model name.
8. **This repo is public, on GitHub, meant to be read by students —
   [`README.md`](README.md) is a real, load-bearing deliverable, not
   internal scratch.** Confirmed 2026-08-22: pushed to
   `pitfal-solutions/cyber-ai` (public, Apache 2.0 — see `LICENSE`, which
   predates this workspace and was preserved, not replaced). Every change
   that touches what's built, how to run it, or what's next — a new
   scenario, a new challenge, a corrected instruction, a status change —
   **must update `README.md` in the same change**, not as a follow-up.
   `README.md` is the front door; `CLAUDE.md`/`ROADMAP.md`/`REVIEW.md`/
   `specs/` are where the detail lives, but if README goes stale it's the
   only one a student actually reads.

## When you finish meaningful work

- Update `ROADMAP.md` if scope/phase changed.
- **Update `README.md`** if anything changed that a student running this repo
  would need to know — new capability, changed quick-start steps, new repo
  map entry, changed status. See working agreement #8. This is not optional
  and not a "later" task.
- Append an entry to `REVIEW.md` if you made a non-obvious decision, found a
  risk, or shipped something worth a checkpoint — and note there that
  `README.md` was updated (or explicitly wasn't, and why). Before marking
  something demo-ready, run it through the "Pre-ship checklist" pinned near
  the top of `REVIEW.md`.
- Don't create new top-level folders beyond the ones in the repo map without
  asking first.
