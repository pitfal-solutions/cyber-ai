# Lecture deck — "Who Goes to Prison When the AI Did It?"

The guest-lecture slide deck this whole repo supports: a 45-minute,
dual-track talk (cybersecurity + criminal-justice students in one room)
that runs the cyber-range scenarios live and hangs them on a single
question — *when the attacker is an AI and no human chose the exploit path,
who is criminally accountable?*

## Files

| File | What it is |
|---|---|
| [`who-goes-to-prison-deck.html`](who-goes-to-prison-deck.html) | The deck. A single self-contained HTML file — no build step, no internet, no fonts to fetch. Open it in any browser. |
| [`talk-track.md`](talk-track.md) | The speaker script: slide-by-slide beats, demo cue cards, and a **Legal Reference Pack** (federal + Colorado statutes, current sentencing ranges, the five anchor cases, and a demo-step → law → case cheat sheet). |

## Presenting it

Open `who-goes-to-prison-deck.html` in a browser and go fullscreen.

| Key | Action |
|---|---|
| `←` / `→` / `Space` | Previous / next slide (or click the left / right half of the screen) |
| `O` | Overview grid — jump to any slide |
| `N` | Toggle speaker notes (hidden by default, so they never hit the projector) |
| `F` | Fullscreen |
| `#12` in the URL | Deep-link straight to slide 12 |

**Offline / air-gapped venues:** the file is fully standalone — copy it to
the demo laptop and open it locally (`file://…`). Nothing loads from the
network. It also prints to PDF cleanly (one slide per page) as a further
fallback.

## Structure

- **Cold open** — attribution runs on human mistakes (a reused cat avatar; a
  photo's EXIF). Slide 2 (the personal opener) is tagged **removable** —
  cut it and open on the cat with zero rewiring.
- **Act 1 — the human in the chair.** Present runs the scripted
  `web-exploit` scenario as the attacker; the statutes light up per step.
  Establishes crime **and** culprit — someone goes to prison.
- **Act 2 — pull the human out.** Run an AI-vs-AI scenario
  (`network-intrusion` is the hero); freeze on the crime and debate who's
  liable — Developer / Deployer / Operator / User — with real precedent.
- **Act 3 — the state's answer.** The Aug-12-2026 hack-back memo as
  letters-of-marque; the legal inversion; close.
- **Reference pack** — statutes, sentencing tables, cases, sources.

## Keep it in sync

The deck's legal content mirrors the cyber-range's on-screen legal overlay
exactly — the same statutes, penalties, and cases live in each scenario's
`legal-map.json`. If you re-run
[`routines/refresh-legal-citations.md`](../../routines/refresh-legal-citations.md)
and a number changes, update **both** the `legal-map.json` files and this
deck's Act-1 / reference slides so the two surfaces don't drift. Honesty
bar is the same as the rest of the repo: prison ranges are verified against
primary/authoritative sources; exact fine caps are flagged
practitioner-sourced; 18 U.S.C. § 1030(a)(5) is not asserted for the AI
marker-write without a primary pass.
