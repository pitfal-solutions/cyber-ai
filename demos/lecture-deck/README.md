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

## The bonus objective (end of deck)

The deck itself is **completely open** — no password to view any slide. The
last two slides are an optional **capture-the-password** challenge:

- **Slide 27 — "Bonus objective"** is locked. It tells the class a password
  is hidden in plain text in this deck's public source and challenges them to
  find it.
- **Slide 28 — "Congratulations"** is reachable *only* by entering that
  password. It reveals the point: a password sitting in source and committed
  to a public repo is one of the most common real breaches there is —
  *don't put secrets in your source.*

The password is **intentionally in plain text** in
[`site/index.html`](site/index.html) — finding it there (or via view-source)
*is* the exercise, so **don't move or obfuscate it**:

```js
var PASSWORD = "range2026";   // <- the bonus answer, left in plaintext on purpose
```

Change the value if you want a different answer, then redeploy. The locked
page is kept out of the overview grid and can't be reached by URL/hash
without the password.

## Files

| File | What it is |
|---|---|
| [`site/index.html`](site/index.html) | The deployable deck — self-contained, open to view, no notes (ends with a bonus password challenge). |
| [`site/vercel.json`](site/vercel.json) | Minimal Vercel static config. |
| [`speaker-notes.md`](speaker-notes.md) | **Presenter-only.** Per-slide speaker notes, kept *outside* `site/` so students never see them. |
| [`talk-track.md`](talk-track.md) | Legal Reference Pack (statutes, sentencing, cases, cheat sheet) + the superseded original script. |

## Presenting it

Open the deployed URL (or `site/index.html` locally), then:

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
attacks are real · AI-vs-AI demo + discussion prompts) → **Part III — the
current predicament** (the accountability gap · the law improvising over the
last 12 months, Colorado-first · what defenders actually do now · the state's
hack-back response · the legal inversion · close) → reference exhibits → a
**bonus password-hunt** (a locked page the class unlocks by finding the
password in the source, then a congratulations page — see below).

Parts I and II each run a **demo → discussion → best-practice** beat; Part
III grounds it all in the last twelve months of real case law, policy, and
defensive practice. The two setup questions on slide 2 — how technology
changes the attack, and who the law can hold responsible — are what every
later slide answers.

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
