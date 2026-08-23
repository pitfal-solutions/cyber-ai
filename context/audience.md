# Audience

One lecture, one room, two majors. Full persona detail lives in
[`/customers`](../customers/); this file is the short version for quick
reference while writing scenario/legal content.

## The buyer: the instructor

Books the guest lecture, needs it to serve *both* halves of the room in one
session, and would like to reuse or extend it for future semesters rather
than commission a one-off. See
[../customers/instructor.md](../customers/instructor.md).

## Track 1: cybersecurity students

Want to see real technique — recognizable tools, real traffic, real
detection logic, ideally mapped to something they already know (MITRE
ATT&CK). Will notice and lose trust in the whole demo if the "attack" is
obviously theater with no real requests behind it. See
[../customers/cybersecurity-student.md](../customers/cybersecurity-student.md).

## Track 2: law enforcement / criminal justice students

Want to follow what happened without needing to read packet captures, and
care most about: what crime occurred, which statute, what the evidentiary
trail looks like, and what the actual penalty is. The legal-overlay panel
(see [../specs/legal-overlay.md](../specs/legal-overlay.md)) exists
specifically so this track has something concrete to track alongside the
technical timeline instead of sitting through a demo aimed past them. See
[../customers/law-enforcement-student.md](../customers/law-enforcement-student.md).

## The design implication

Every scenario needs two synchronized outputs from the same underlying
event stream: a technical view (attack timeline, ATT&CK technique IDs,
detection alerts) and a legal view (statute, elements of the offense,
penalty range) — not two separate demos bolted together. See
[../specs/architecture.md](../specs/architecture.md) for how the event
stream is structured to drive both.
