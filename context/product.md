# Product

## What it is

A containerized, laptop-hosted "AI vs AI" cybersecurity demo: an attack runs
against a real (intentionally vulnerable) target, a real defense detects and
responds, and every attacker action is tagged live with the specific law it
breaks and the real-world penalty attached to it.

Built for a single guest lecture, but built to be reused and extended for
future classes rather than thrown away after one use.

## Why it exists

Guest lectures on cybersecurity usually pick one lane:

- A **technical** talk (tools, exploits, detection) that loses a
  law-enforcement / criminal-justice audience within ten minutes, or
- A **legal/policy** talk (statutes, case law, procedure) that loses a
  cybersecurity audience because there's nothing concrete happening.

This class has both majors in the room at once, for one lecture. The demo
has to serve both without dumbing either side down.

## The promise

1. **A real attack happens.** Not a slideshow narrating what an attack looks
   like — actual network traffic against an actual vulnerable target,
   running inside an isolated environment on the laptop.
2. **A real defense responds.** Detection rules fire, alerts appear on a
   dashboard, in something close to real time.
3. **The law is on screen the whole time.** Each attacker action is paired
   with the statute it violates and the real penalty range — so the
   law-enforcement track is never just watching a technical demo happen *at*
   them, they're seeing the case being built in parallel.
4. **It resets.** Run it once for rehearsal, run it again for the actual
   lecture, reuse it next semester — same environment, clean state every
   time.
5. **It grows.** One scenario ships for this lecture. The architecture is
   built so a second and third scenario are additive work, not a rewrite —
   see [../specs/architecture.md](../specs/architecture.md).

## What it deliberately is not (v1)

- Not a platform students log into and use themselves — see
  [../customers/instructor.md](../customers/instructor.md) and working
  agreement #6 in [../CLAUDE.md](../CLAUDE.md).
- Not cloud-hosted or internet-dependent at runtime — see working agreement
  #2. The whole point is that it's safe to run in a room with unknown wifi.
- Not a claim that the AI is doing something it isn't. If a scenario is
  scripted rather than autonomously decided by a model, it's presented that
  way — see [tech-stack-research.md](tech-stack-research.md) for the
  scripted-vs-agentic split and why v1 is scripted.
