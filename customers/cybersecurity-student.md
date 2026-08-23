# Cybersecurity student

## Who they are

Studying security/CS, has some hands-on exposure already (labs, CTFs, or
coursework covering the OWASP Top 10 / basic networking). Sitting through a
guest lecture they've probably seen a version of before.

## What they want from this demo

- **Real technique, not narrated fiction.** If they can tell the "attack" is
  a slideshow rather than actual requests hitting an actual vulnerable app,
  the whole demo loses credibility with this half of the room immediately.
- Recognizable tools and mapped-out technique names (MITRE ATT&CK IDs are a
  language this audience already reads).
- To see the *defense* side do something real too — a detection rule firing
  is more interesting to this audience than watching an exploit land, since
  they've likely built the exploit side themselves in coursework already.
- Enough transparency to ask "wait, how did that step actually work?" and
  get a real answer, not a hand-wave.

## What loses them

- Attacks that are fully simulated/faked with no real traffic.
- Vague claims ("the AI figured out a vulnerability") without the
  underlying technique named.
- A defense dashboard that's just for show and isn't wired to real
  detection logic.

## Design implication

Every scripted attack step should be a real request against the real Juice
Shop target, tagged with its actual ATT&CK technique ID — see
[../specs/scenario-web-exploit.md](../specs/scenario-web-exploit.md). The
"scripted, not autonomous" framing for v1 (see
[../context/tech-stack-research.md](../context/tech-stack-research.md))
should be stated honestly if asked, not oversold as live AI decision-making
— this audience will ask.
