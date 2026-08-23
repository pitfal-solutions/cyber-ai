# Cyber AI Range

**A live, offline "attack vs. defense" demo that shows both sides of a
cybercrime at once: how it actually works, and what law it actually
breaks.**

Built as a guest-lecture demo for a class with two majors in the room —
cybersecurity and law enforcement / criminal justice — so it does not pick
a lane. Every real exploit step lands on screen next to the real statute it
violates, the elements of that offense, and the penalty.

Nothing here touches the real internet. Everything runs in isolated Docker
containers on one laptop, against an intentionally vulnerable practice
app — [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/), a
project built specifically so people can learn to find and exploit real
web vulnerabilities without breaking any law or touching anyone else's
system. See [Responsible use](#responsible-use) below.

## What you'll see

One continuous, scripted attack chain against a real running app, three
real vulnerabilities deep:

1. **A confidential file, exposed to anyone** — an internal "Planned
   Acquisitions" memo sitting at a guessable URL with zero login required.
2. **A SQL-injection login bypass** — a crafted login request that tricks
   the database into authenticating as the admin, with no valid password.
3. **A full account takeover** — a customer's password reset flow uses a
   guessable security question ("Your eldest sibling's middle name?"); the
   answer resets the password, and the new credentials really do log in as
   them.

A detector — a separate piece of code that never sees the attack script,
only the real network traffic — independently catches all three and fires
a real alert each time. A dashboard shows both timelines side by side:
what technique just fired (mapped to [MITRE
ATT&CK](https://attack.mitre.org/)), and what law it violates (federal
CFAA, Colorado state statutes, real penalty ranges — sourced, not
invented).

Everything resets to a clean slate in under 30 seconds, so it can be run
over and over — in rehearsal, in class, or by you, right now.

## Quick start

Requires [Docker](https://docs.docker.com/) (any way you like to run it —
Docker Desktop, [Colima](https://github.com/abiosoft/colima), etc.) and
`docker compose`.

```bash
cd demos/v1-cyber-range
./run.sh web-exploit
```

Then open:

- **Dashboard** (the attack/defense timeline + the legal overlay):
  http://127.0.0.1:8080
- **Target app** (the live storefront being attacked, viewed through the
  traffic-logging proxy): http://127.0.0.1:3000

Give it a few seconds to boot, then trigger the attack on cue:

```bash
./scenarios/web-exploit/run-attack.sh
```

Watch it land on the dashboard in real time. When you're done, reset to a
clean slate:

```bash
./scenarios/web-exploit/reset.sh
```

Full walkthrough, including how to speed up or slow down the pacing:
[demos/README.md](demos/README.md).

## How it's built

- **Isolated by design.** The target app, the attacker, and the detector
  all run on a Docker network with `internal: true` — no route to the
  internet exists for any of them. Only two small "viewer" services (the
  dashboard and the proxy) can be reached from your browser.
- **Real detection, scripted attack.** The attacker's *choices* are
  pre-scripted, on purpose — see [Why scripted?](#why-scripted) below. But
  the requests it sends are real, and the detector genuinely doesn't know
  what's coming; it just watches real traffic and pattern-matches, the
  same way a real detection rule would.
- **One shared event stream drives both views.** Every attack step and
  every detection posts one small event; the dashboard joins it against a
  statute file to render the legal side. Adding a new challenge means
  adding a new step and a new statute entry — not building a new app.

Full architecture and design decisions: [specs/](specs/) — including a
couple of things that didn't work on the first try and had to be corrected
(see [REVIEW.md](REVIEW.md) for the honest version of how this got built).

## The legal side

Every statute cited in the dashboard is sourced from a real reference —
codified statute text or a cited legal summary — not general knowledge
alone, and every entry says so. Where a fact pattern is genuinely
contested (courts have split, for example, on whether visiting an
unlocked-but-unlinked URL counts as "unauthorized access" under federal
law), the demo says that too, instead of pretending every step is an
equally clean case. See [context/legal-framework.md](context/legal-framework.md).

**This is teaching material, not legal advice**, and the citations are a
strong starting point rather than a final legal-review pass — see
[routines/refresh-legal-citations.md](routines/refresh-legal-citations.md)
for what "final" would actually require.

## Why scripted?

Because a live, one-shot classroom demo can't risk a fully autonomous AI
attacker wandering off-script in front of a room. The attack chain here is
deterministic and rehearsed — real requests, real vulnerabilities, real
detection, just a fixed running order. A genuinely autonomous, local-LLM-
driven version (two small models, one attacking and one defending, both
running offline) is a designed-but-not-yet-built stretch goal — see
[specs/local-llm-agents.md](specs/local-llm-agents.md) and
[ROADMAP.md](ROADMAP.md).

## Responsible use

Every technique in this repo targets **OWASP Juice Shop**, an application
built and maintained specifically to be attacked for education — that's
its entire purpose, and doing so here breaks no law. **These same
techniques, run against a system you don't own or don't have explicit
permission to test, are the real crimes this repo's own legal-overlay
panel describes.** That's the point of the demo, not an incidental risk of
it: don't be the case study.

## Repo map

| Path | What's there |
|---|---|
| [`demos/v1-cyber-range/`](demos/v1-cyber-range/) | The actual runnable demo — start here to run it. |
| [`specs/`](specs/) | How it's built and why, including corrections made along the way. |
| [`context/`](context/) | The business/teaching context: audience, legal framework, tech research. |
| [`customers/`](customers/) | Who this is built for — the instructor and both student tracks. |
| [`ROADMAP.md`](ROADMAP.md) | What's built, what's next, what was deliberately cut for time. |
| [`REVIEW.md`](REVIEW.md) | A running, honest log of decisions, corrections, and open risks. |
| [`CLAUDE.md`](CLAUDE.md) | How this repo is built and maintained with an AI pair — working agreements, quality bar. |

## Status

One scenario, three challenges, built and verified end-to-end — see
[ROADMAP.md](ROADMAP.md) for what's shipped versus what's still designed
(an autonomous agentic scenario, plus ransomware and phishing scenarios on
the same shared infrastructure).

## License

[Apache License 2.0](LICENSE).
