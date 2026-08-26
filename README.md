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

Requires macOS. One-time setup (installs Colima, Docker CLI/Compose/Buildx,
and Ollama via Homebrew; starts them; pulls the two default local-LLM
models; pre-builds/pre-pulls every scenario's images so nothing needs the
network at showtime):

```bash
cd demos/v1-cyber-range
./setup.sh
```

Safe to re-run — every step checks current state first. See the script's
comments, or [demos/README.md](demos/README.md), for what it does and how
to override the model pair (`ATTACKER_MODEL`/`DEFENDER_MODEL`).

Three scenarios exist. All run from `demos/v1-cyber-range/`, all share the
same dashboard (http://127.0.0.1:8080), and all reset to a clean slate with
their own `reset.sh`.

### `web-exploit` — the guaranteed, scripted scenario

```bash
./run.sh web-exploit
```

Open the dashboard (http://127.0.0.1:8080) and the target app, through the
traffic-logging proxy (http://127.0.0.1:3000) — give it a few seconds to
boot. Then trigger the attack on cue:

```bash
./scenarios/web-exploit/run-attack.sh
```

Watch it land on the dashboard in real time. Reset when done:

```bash
./scenarios/web-exploit/reset.sh
```

### `agentic` — two local LLMs vs. the same target app

Stretch-goal scenario (see [Why scripted](#why-scripted-the-guaranteed-scenario-is)
below) — needs Ollama running, which `./setup.sh` handles.

```bash
./run.sh agentic
```

Same dashboard URL, now with a Pause/Resume button and a speed selector.
Target app is also reachable at http://127.0.0.1:3000. Start both AI brains
when ready:

```bash
./scenarios/agentic/run-agentic.sh
```

Reset:

```bash
./scenarios/agentic/reset.sh
```

### `network-intrusion` — two local LLMs vs. a small real network

Second stretch-goal scenario — same two-LLM structure, but the attacker
targets three real Linux hosts (SSH, FTP, SMB) with real tools (`nmap`,
`hydra`, `smbclient`) instead of a web app. No host port for the targets
themselves — only the dashboard is reachable from your browser. The
attacker can steal a real (fictional) confidential file off the anonymous
SMB share, and — once it has a real root shell via the CVE-2011-2523
backdoor — actually write an "ATTACKER WON" marker file to the host's disk
and read it back to prove the compromise (a real write, cleaned up by
`reset.sh` like everything else).

```bash
./run.sh network-intrusion
cd scenarios/network-intrusion
./run-network-intrusion.sh
```

Reset:

```bash
./scenarios/network-intrusion/reset.sh
```

Full walkthrough for every scenario, including how to speed up or slow
down the pacing: [demos/README.md](demos/README.md).

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

## Why scripted (the guaranteed scenario is)

Because a live, one-shot classroom demo can't risk a fully autonomous AI
attacker wandering off-script in front of a room. The attack chain here is
deterministic and rehearsed — real requests, real vulnerabilities, real
detection, just a fixed running order. This is the scenario that's
guaranteed to be presented, no matter what.

**Two genuinely autonomous scenarios now also exist as stretch goals**: in
each, two small local LLMs — one attacking, one defending, both running
fully offline via a host-native Ollama — choose their own actions in real
time, with a live dashboard showing both sides plus a presenter-controlled
pause/speed. One targets the same Juice Shop app (web-layer techniques —
SQLi, credential guessing, broken access control); a second targets a
small network of real OS/server-level hosts instead (weak SSH credentials,
the real CVE-2011-2523 vsftpd backdoor, anonymous SMB file access) using
real tools (`nmap`, `hydra`, `smbclient`), added after the first felt too
repetitive on its own. Both are built and have passed rehearsal runs, but
**either only ever gets presented live if it survives 3 consecutive clean
rehearsal runs on the actual demo laptop first** — see
[specs/local-llm-agents.md](specs/local-llm-agents.md) and
[specs/network-intrusion.md](specs/network-intrusion.md) for what each
does and the real issues found (and fixed) while building them, and
[ROADMAP.md](ROADMAP.md) for the current gate status. If neither clears
that bar, the scripted scenario above is what the audience sees — that's
a fine outcome, not a failure.

## Responsible use

Every technique in this repo targets either **OWASP Juice Shop** (an
application built and maintained specifically to be attacked for
education) or purpose-built training hosts in this repo's own network-
intrusion scenario (a real backdoor, a real weak credential, a real
misconfigured file share — all deliberately built for this demo, none of
it a real production system) — that's their entire purpose, and attacking
them here breaks no law. **These same techniques, run against a system
you don't own or don't have explicit permission to test, are the real
crimes this repo's own legal-overlay panel describes.** That's the point
of the demo, not an incidental risk of it: don't be the case study.

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

The guaranteed lecture scenario — one scripted scenario, three challenges —
is built and verified end-to-end. Two additional, autonomous AI-vs-AI
scenarios (one web-layer, one real OS/network-level) are also built and
have passed rehearsal runs, but neither is yet rehearsal-gated for live use
(see "Why scripted" above). See [ROADMAP.md](ROADMAP.md) for full status,
including what's still designed but not built (ransomware and phishing
scenarios on the same shared infrastructure).

## License

[Apache License 2.0](LICENSE).
