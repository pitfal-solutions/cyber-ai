# Dashboard (defensive / blue-team view)

Status: **built and verified, 2026-08-22** — but as a lightweight custom
app, **not Wazuh**. This is a real change from the original spec, made
during the build under the 2-3 day timeline; documented here and in
[../REVIEW.md](../REVIEW.md) rather than left as a silent swap.

## Choice: a lightweight custom detector + dashboard, not Wazuh

The original spec called for Wazuh (see the superseded reasoning below —
still valid reasoning, just outweighed by the timeline once building
actually started). Under a 2-3 day runway, Wazuh's real footprint —
certificate generation for its single-node stack, an indexer with a real
memory floor, multi-container boot time — worked against two hard
requirements: reset-in-under-a-minute, and having something reliably
*working* in days rather than mostly-working.

**What was built instead** (`core/range-dashboard/`,
`scenarios/web-exploit/proxy/`, `scenarios/web-exploit/detector/`, all
stdlib-only Python, no pip installs):
- A reverse proxy in front of the scenario's target, logging every real
  request independently of the attacker script.
- A detector that tails that log and pattern-matches — regex on the login
  endpoint's body, a sliding-window enumeration check — and posts real
  alert events only when a real pattern actually fires.
- A single dashboard page (not two apps) rendering both the technical
  timeline and the legal overlay side by side from the shared event stream.

**This still meets the actual requirement below** ("real detection on real
traffic, not staged") — verified directly: the detector has no knowledge of
the attacker's script, it only reacts to the proxy's independently-recorded
log, and it fired correctly on both real attack patterns in two separate
test runs. See [../REVIEW.md](../REVIEW.md) for the verification.

**Wazuh remains a reasonable option to revisit in Phase 4** if a future
class wants a fuller, SOC-analyst-realistic dashboard experience — the
event-stream contract this dashboard reads/writes (see
[architecture.md](architecture.md)) would let a real Wazuh instance be
swapped in as an alternative consumer without touching the scenario's
attack/proxy/detector code.

### Superseded original reasoning (kept for context, not current status)

See [../context/tech-stack-research.md](../context/tech-stack-research.md)
for the original comparison. Wazuh ships a working dashboard UI and real
detection-rule engine out of the box (~6GB, single-node Docker deployment)
— the original call was that this would be faster than hand-building a
detection pipeline from scratch. In practice, standing up Wazuh's
cert-heavy multi-container stack reliably within the build window was the
higher-risk path, not the lower-risk one — see above.

## What "real" means here

The offense's *choice of actions* is scripted for v1 (working agreement #1)
— but the defense side must be genuinely wired to real traffic: a real
rule matching a real, reproducible request pattern from the scripted
attack, firing a real alert. Don't fake the alert by scripting its
appearance on a timer — if the rule doesn't actually fire off real traffic,
that's a bug to fix, not a shortcut to take. This is the credibility bar
for the cybersecurity track — see
[../customers/cybersecurity-student.md](../customers/cybersecurity-student.md).
**Verified, not assumed:** the detector was tested with no knowledge of the
attacker's script wired in, reacting only to the proxy's independent log,
and it correctly fired on both real patterns across two separate test
runs — see [../REVIEW.md](../REVIEW.md).

## Build requirements (as built)

1. ✅ `range-dashboard` service added to `core/docker-compose.core.yml` —
   shared across all scenarios per [architecture.md](architecture.md).
2. ✅ `proxy` (scenario-specific, `scenarios/web-exploit/proxy/`) sits in
   front of Juice Shop and logs every real request/body to a shared file —
   Juice Shop's own logging wasn't used directly, a dedicated proxy log was
   simpler and scenario-controllable.
3. ✅ Detection rules authored and verified for scenario 1's specific
   pattern (see [scenario-web-exploit.md](scenario-web-exploit.md)) — not
   assumed from any default ruleset.
4. ✅ Dashboard + proxy ports published to `127.0.0.1` via the
   `cyberrange_view` network per the corrected network-isolation design in
   [architecture.md](architecture.md).

## Projector legibility

**Not yet checked** — only viewed on a laptop browser (desktop viewport) so
far. The dashboard's CSS uses large type by design, but verifying actual
legibility from lecture-hall distance is still open — see the Phase 1 open
items in [../ROADMAP.md](../ROADMAP.md) and the pre-ship checklist in
[../REVIEW.md](../REVIEW.md). Do this before the lecture.
