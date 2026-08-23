# Routine: pre-demo rehearsal

**Trigger:** before every rehearsal run and before the live lecture itself
— event-triggered, not scheduled.

**What "done" looks like for one run:**

1. Physically disconnect the laptop's wifi/network adapter (belt-and-
   suspenders on top of the Docker network isolation — see
   [../specs/architecture.md](../specs/architecture.md)).
2. `docker compose -f core/... -f scenarios/<scenario>/... up` from a clean
   state (confirm via `docker ps` that nothing stale is running first).
3. Run the full scenario start to finish, timing it.
4. Confirm the dashboard shows the expected alert(s) and the legal-overlay
   panel shows the expected steps, in sync, legible from across the room
   (not just up close).
5. Run `reset.sh` and confirm it completes in under a minute and leaves no
   stale state (spot-check: re-run the scenario immediately after and
   confirm it behaves identically to the first run).
6. Reconnect the network only after the rehearsal is fully torn down.

**Log the result** as a `REVIEW.md` entry if anything broke, was slow, or
needed a manual fix — don't let rehearsal failures go unrecorded, since
they're exactly what the next rehearsal needs to check again.
