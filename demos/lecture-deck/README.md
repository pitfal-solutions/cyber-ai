# Lecture deck — "Attack, Autonomy & Accountability"

The guest-lecture slide deck this repo supports: a dual-track talk
(cybersecurity + criminal-justice students in one room) on how technology is
reshaping offensive cyber — and straining a legal system built on the idea
that every crime has a person behind it.

The deployable deck lives in [`site/`](site/) as a single self-contained
`index.html` — no build step, no dependencies, no web fonts. It carries a
simple **password gate** and **no instructor notes** (those live in
[`speaker-notes.md`](speaker-notes.md), kept out of the deployed site), so
it's safe to share with a class.

## Deploy to Vercel

The deck is a static site; **`site/` is the deploy root** (it holds only
`index.html` + `vercel.json`, so nothing private ships with it).

**Quickest — Vercel CLI:**

```bash
cd demos/lecture-deck/site
npx vercel          # first run links/creates a project, gives a preview URL
npx vercel --prod   # production URL to share with the class
```

**Or connect the GitHub repo** in the Vercel dashboard and set **Root
Directory = `demos/lecture-deck/site`** (Framework preset: *Other* — no build
command). Every push to the repo then redeploys.

Either way you get a URL like `https://<name>.vercel.app` to hand out with
the password.

## The password gate

A simple string password unlocks the deck. It's deliberately **not
bulletproof** — it keeps casual or early access out, nothing more. Change it
in one place, the `PASSWORD` constant near the top of the `<script>` in
[`site/index.html`](site/index.html):

```js
var PASSWORD = "range2026";   // <- change this, then redeploy
```

The check runs client-side, so anyone who views source can read it. If you
ever want real gating, it becomes a one-file Vercel serverless function
reading the password from an environment variable — ask and it's a quick
add.

## Files

| File | What it is |
|---|---|
| [`site/index.html`](site/index.html) | The deployable deck — self-contained, password-gated, no notes. |
| [`site/vercel.json`](site/vercel.json) | Minimal Vercel static config. |
| [`speaker-notes.md`](speaker-notes.md) | **Presenter-only.** Per-slide speaker notes, kept *outside* `site/` so students never see them. |
| [`talk-track.md`](talk-track.md) | Legal Reference Pack (statutes, sentencing, cases, cheat sheet) + the superseded original script. |

## Presenting it

Open the deployed URL (or `site/index.html` locally), enter the password,
then:

| Key | Action |
|---|---|
| `←` / `→` / `Space` | previous / next slide (or click the left / right half of the screen) |
| `O` | overview grid — jump to any slide |
| `F` | fullscreen |
| `#12` in the URL | deep-link straight to slide 12 |

Runs offline too — `site/index.html` opens straight from disk (the article
link on slide 3 needs internet, but nothing else does). Prints to PDF (one
slide per page) as a fallback. Designed for 16:9; below ~860px wide,
two-column slides stack vertically.

## Structure at a glance

Introduction (title · two guiding questions · a field case from Colorado —
first-hand work on a Wi-Fi-jamming organized-burglary investigation) →
**Part I** (TeamPCP: who / what / how caught · the attribution principle ·
live demo + class-discussion prompts · a settled-vs-arguable discussion
guide · a best-practice method for each side) → **Part II** (autonomous
attacks are real · AI-vs-AI demo + discussion prompts · the ladder with no
rungs · the lineup · precedent timeline · a best-practice method for each
side · the state's response · the legal inversion · close) → reference
exhibits.

**Both parts follow the same demo → discussion → best-practice arc**, and
the two setup questions on slide 2 — how technology changes the attack, and
who the law can hold responsible — are what every later slide answers.

## Keep it in sync

The deck's legal content mirrors the cyber-range's on-screen legal overlay
exactly — same statutes, penalties, and cases as each scenario's
`legal-map.json`. If you re-run
[`routines/refresh-legal-citations.md`](../../routines/refresh-legal-citations.md)
and a number changes, update **both** the `legal-map.json` files and this
deck's exhibits. Same honesty bar: prison ranges verified against
primary/authoritative sources; exact fine caps flagged practitioner-sourced;
18 U.S.C. § 1030(a)(5) is not asserted for the AI marker-write without a
primary pass.
