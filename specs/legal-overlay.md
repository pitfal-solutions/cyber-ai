# Legal-overlay panel

Status: **built and verified, 2026-08-22.** Lives inside
`core/range-dashboard/server.py` as the right-hand column of the same page
as the technical timeline (not a separate app — see the "open build
question" below, now resolved).

## Purpose

The synchronized legal view for the law-enforcement/criminal-justice track
— see [../context/audience.md](../context/audience.md). Updates in step
with the attack timeline instead of being a single end-of-demo legal
summary slide.

## What it shows per step (as built)

Driven by joining the shared event stream's `legal_ref` field (see
[architecture.md](architecture.md)) against the active scenario's
`legal-map.json`:

- Plain-language description of what just happened.
- Statute cited (e.g. "18 U.S.C. § 1030(a)(2) — Computer Fraud and Abuse
  Act (federal)") — or a visibly distinct **TBD** badge if the event's
  `legal_ref` has no matching entry yet. See working agreement #4 in
  [../CLAUDE.md](../CLAUDE.md).
- Penalty text — rendered with a **PENALTY TBD** badge if the map entry's
  `penalty` field is missing or literally `"TBD"`, so an unverified number
  can never silently read as final.
- Evidentiary note, where the map entry has one.

Verified live: ran the full scenario 1 attack chain and confirmed all three
legal-map entries (federal CFAA + two Colorado statutes) rendered correctly
in sync with their corresponding timeline events — see
[../REVIEW.md](../REVIEW.md).

## `legal-map.json` shape (as built — JSON, not `.yaml` as originally
drafted; see [architecture.md](architecture.md) for why)

```json
{
  "cfaa-1030a2": {
    "statute": "18 U.S.C. § 1030(a)(2) -- Computer Fraud and Abuse Act (federal)",
    "plain_language": "...",
    "elements": ["..."],
    "penalty": "...",
    "evidentiary_note": "..."
  }
}
```

An entry with `"penalty": "TBD"` (or no `penalty` key at all) renders the
TBD badge automatically — no separate flag needed. See
`scenarios/web-exploit/legal-map.json` for the real, populated example.

## Display requirements

- Legible from the back of a lecture hall on a projector — large type, high
  contrast. **Not yet verified at projector distance**, only on a laptop
  browser so far — open item in [../ROADMAP.md](../ROADMAP.md) Phase 1.
- Runs alongside the technical dashboard, same page, two columns,
  synchronized by the same polled event stream (1-second poll interval).

## Resolved: real-time web view, not a separate app

A small stdlib-Python HTTP server (`core/range-dashboard/server.py`) serves
one HTML page that polls `/events` every second and renders both columns
client-side. Simpler than running two separate apps/panels, and keeps the
"one shared event stream drives both views" design (see
[architecture.md](architecture.md)) concrete in actual code rather than
just a diagram.
