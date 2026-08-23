# Routine: refresh legal citations

**Trigger:** before each reuse of this demo in a future class — not on a
fixed calendar cadence, since "how often statutes change" doesn't map
cleanly to a schedule.

**What "done" looks like for one run:**

1. Re-pull the current text of every statute cited in any scenario's
   `legal-map.yaml` (see [../specs/legal-overlay.md](../specs/legal-overlay.md)).
2. Confirm penalty ranges are still accurate against current law — statutes
   and sentencing guidelines can and do change.
3. If the lecture is now at a different institution/state than before,
   re-run the state-statute-pairing question from
   [../context/legal-framework.md](../context/legal-framework.md) — don't
   assume the previous state's pairing still applies.
4. Update any changed citation, and note the change (with date and what
   changed) in [../REVIEW.md](../REVIEW.md).
5. If anything can't be verified in time, mark it TBD in the relevant
   `legal-map.yaml` rather than leaving stale/unverified content live — per
   working agreement #4 in [../CLAUDE.md](../CLAUDE.md).
