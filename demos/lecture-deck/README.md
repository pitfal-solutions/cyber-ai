# Lecture deck — "Attack, Autonomy & Accountability"

The guest-lecture slide deck this repo supports: a dual-track talk
(cybersecurity + criminal-justice students in one room) on how AI is
reshaping offensive cyber — and straining a legal system built on the idea
that every crime has a person behind it. It runs the cyber-range scenarios
live and is built around a single arc:

- **Part I — when a person is behind it.** Attacks are still run by people
  (now AI-accelerated). One real campaign end to end — the **TeamPCP**
  supply-chain worm — shows what it did, how it spread, and how its
  operators were identified and charged. Then the presenter runs the
  scripted `web-exploit` scenario and the statutes land per step.
- **Part II — when no one is behind it.** Autonomous agents run an intrusion
  end to end. The presenter runs an AI-vs-AI scenario; the attribution
  ladder loses its rungs; the room debates who is accountable (developer /
  deployer / operator / user) against real precedent — and the state's
  answer (licensed private "hack-back") is folded in here.

## Files

| File | What it is |
|---|---|
| [`attack-autonomy-accountability.html`](attack-autonomy-accountability.html) | The deck. One self-contained HTML file — no build step, no internet, no web fonts. Open it in any browser. |
| [`talk-track.md`](talk-track.md) | The Legal Reference Pack (federal + Colorado statutes, current sentencing ranges, the five anchor cases, and a demo-step → law → case cheat sheet). **Note:** its slide-by-slide script predates the two-part restructure; the authoritative, current speaker notes now live *inside the deck* — press `N`. |

## Presenting it

Open `attack-autonomy-accountability.html` in a browser and go fullscreen.

| Key | Action |
|---|---|
| `←` / `→` / `Space` | Previous / next slide (or click the left / right half of the screen) |
| `O` | Overview grid — jump to any slide |
| `N` | Speaker notes (hidden by default, so they never hit the projector) |
| `F` | Fullscreen |
| `#12` in the URL | Deep-link straight to slide 12 |

**Offline / air-gapped venues:** the file is fully standalone — copy it to
the demo laptop and open it locally (`file://…`). Nothing loads from the
network. It also prints to PDF cleanly (one slide per page) as a fallback.
Designed for 16:9; on very narrow displays (< ~860px) two-column slides
stack vertically.

## Structure at a glance

Introduction (title · agenda · a field case from Colorado — the presenter's
first-hand work on a Wi-Fi-jamming organized-burglary investigation) →
**Part I** (TeamPCP: who / what / how caught · the attribution principle ·
live demo + class-discussion prompts · a settled-vs-arguable discussion
guide · a best-practice method for each side) → **Part II** (autonomous
attacks are real · AI-vs-AI demo + discussion prompts · the ladder with no
rungs · the lineup · precedent timeline · a best-practice method for each
side · the state's response · the legal inversion · close) → reference
exhibits.

**Both parts follow the same demo → discussion → best-practice arc:** run
the scenario, prompt the room (tactics for the cyber half, charging /
accountability decisions for the justice half), work the discussion (the
settled-vs-arguable guide in Part I; the lineup + precedent in Part II), then
land a clean method both tracks can defend. The two setup questions on
slide 2 — how AI changes the attack, and who the law can hold responsible —
are what every later slide answers.

## Keep it in sync

The deck's legal content mirrors the cyber-range's on-screen legal overlay
exactly — the same statutes, penalties, and cases live in each scenario's
`legal-map.json`. If you re-run
[`routines/refresh-legal-citations.md`](../../routines/refresh-legal-citations.md)
and a number changes, update **both** the `legal-map.json` files and this
deck's exhibits so the two surfaces don't drift. Same honesty bar: prison
ranges verified against primary/authoritative sources; exact fine caps
flagged practitioner-sourced; 18 U.S.C. § 1030(a)(5) is not asserted for the
AI marker-write without a primary pass.
