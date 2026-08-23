# Routines

Definitions for recurring tasks this AI-employee workspace should eventually
run on a schedule. **Nothing here is actually scheduled yet** — these are
proposals. Setting up an actual recurring/cron task is a standing-
configuration change, which needs the user's explicit go-ahead before it's
created — don't self-schedule from this folder without asking first.

Each routine file should say: what it does, how often, what triggers it
(time-based vs. event-based), and what "done" looks like for one run.

## Proposed routines

- [pre-demo-rehearsal.md](pre-demo-rehearsal.md) — run before every live or
  rehearsal performance, not on a calendar schedule (event-triggered, not
  time-triggered).
- [refresh-legal-citations.md](refresh-legal-citations.md) — re-verify
  statute text and penalty ranges before each reuse in a future class.

## Not yet proposed, but implied by the roadmap

- **CVE/version refresh** (Phase 4): periodically check whether the pinned
  Juice Shop (or future scenario target) version has changed in a way that
  breaks the scripted attack chain. Needs a defined cadence once this is
  reused across multiple semesters — don't build until Phase 4 starts.
