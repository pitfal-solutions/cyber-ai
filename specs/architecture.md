# Architecture

Status: **built and verified, 2026-08-22** (`demos/v1-cyber-range/`). See
[../REVIEW.md](../REVIEW.md) for what changed from the original design
during the build and why — most notably the network isolation section
below, which was corrected after direct testing showed the original design
didn't actually work.

## Shape: one core, many scenario plugins

Working agreement #3 in [../CLAUDE.md](../CLAUDE.md) requires this even
though v1 ships exactly one scenario.

Actual layout, as built (`demos/v1-cyber-range/`):

```
demos/v1-cyber-range/
  run.sh                      # up the core + a named scenario
  core/
    docker-compose.core.yml   # both networks, shared volume, the dashboard
    range-dashboard/           # stdlib-Python app: serves + renders the shared event stream

  scenarios/
    web-exploit/                # Phase 1 — built, v1 lecture deliverable
      docker-compose.yml        # Juice Shop + proxy + detector + attacker (manual profile)
      legal-map.json             # attack step -> ATT&CK ID -> statute -> penalty
      reset.sh / run-attack.sh
      proxy/                    # logs real traffic to the target, independent of the attacker
      detector/                 # tails that log, pattern-matches, posts real alert events
      attacker/                 # the verified, deterministic exploit chain

    agentic/                    # Phase 2 — stretch goal, not built yet
    ransomware-lateral/         # Phase 3 — not built yet
    phishing-atk/               # Phase 3 — not built yet
```

`legal-map.json`, not `.yaml` as originally drafted — same content shape,
switched to JSON so the stdlib-only Python dashboard doesn't need a YAML
parser dependency (see the "stdlib only" note in `range-dashboard/server.py`
and REVIEW.md's dependency-minimalism reasoning).

Run a scenario with `./run.sh web-exploit` (wraps `docker compose
--project-directory . -f core/docker-compose.core.yml -f
scenarios/web-exploit/docker-compose.yml up -d --build` — the
`--project-directory .` flag matters: without it, multi-file `-f` build
contexts resolve inconsistently against whichever file compose treats as
"first," not each file's own directory — found the hard way, see
REVIEW.md). A new scenario means adding a new folder under `scenarios/`,
not editing `core/`.

## Network isolation

**Two networks, not one** — this is a correction from the original design,
made after testing showed the original assumption was wrong (see
[../REVIEW.md](../REVIEW.md) 2026-08-22 build entry):

- `cyberrange_net` (`internal: true`) is the real isolation boundary.
  Juice Shop, the attacker, and the detector live **only** here. An
  `internal: true` network has no route out through the Docker
  gateway/NAT — nothing on it can reach the real internet.
- `cyberrange_net` alone turned out to also block **host-published ports
  entirely**, not just outbound egress — tested directly: with only this
  network attached, `docker inspect` showed the port never bound at all
  (`"8080/tcp": null`), and `curl` from the host got connection-refused.
  The original spec's assumption ("port publishing is host↔container, a
  separate mechanism from egress") was wrong for Docker's `internal` flag
  specifically.
- `cyberrange_view` (a normal, non-internal network) exists purely to give
  Docker something to bind a host-published port to. **Only** the
  dashboard and the proxy join it, in addition to `cyberrange_net`. Juice
  Shop, the attacker, and the detector never join it — so the isolation
  guarantee for anything "attack"-shaped is unchanged; only the two
  view-only services get a second network leg.
- Before the lecture, the laptop's wifi/network adapter should still be
  physically disconnected as a second, independent layer of assurance —
  don't rely on Docker network config alone for the "isolated" promise made
  to the instructor. **Not yet tested with wifi actually off** — see
  [../ROADMAP.md](../ROADMAP.md) Phase 1 open items. See
  [../routines/pre-demo-rehearsal.md](../routines/pre-demo-rehearsal.md).

## Reset-to-zero

Every scenario ships a `reset.sh` that does, at minimum:
`docker compose down -v` (removes containers *and* volumes, so no stateful
drift survives a reset) followed by `up -d`, plus any scenario-specific
re-seeding. Must complete in under a minute — see the quality bar in
[../CLAUDE.md](../CLAUDE.md). **Verified for scenario 1:** ~22 seconds per
reset, two consecutive clean cycles, identical results both times — see
[../REVIEW.md](../REVIEW.md).

## The shared event stream

Every scenario, scripted or agentic, emits the same shape of event so the
dashboard and legal-overlay panel don't need per-scenario logic:

```json
{
  "ts": "2026-08-24T18:03:11Z",
  "scenario": "web-exploit",
  "step_id": "sqli-login-bypass",
  "attack_technique_id": "T1190",     // MITRE ATT&CK
  "actor": "attacker",                 // attacker | defender
  "description": "Crafted login payload bypasses authentication",
  "legal_ref": "cfaa-1030a2"           // key into legal-map.yaml
}
```

- The **dashboard** (Wazuh) consumes the technical fields to drive alerts/
  timeline.
- The **legal-overlay panel** joins `legal_ref` against
  `legal-map.yaml` to render the statute/penalty/TBD state in sync.
- This is what makes "two synchronized views from one event stream" (see
  [../context/audience.md](../context/audience.md)) actually work instead
  of being two demos glued together.

## Local LLM runtime (Phase 2 only)

Ollama runs as a core service (so any future agentic scenario can use it
without redefining it), but no scenario in Phase 1 depends on it. See
[local-llm-agents.md](local-llm-agents.md) for the Phase 2 design and
working agreement #7 for why exact models aren't pinned here.
