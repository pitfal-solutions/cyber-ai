# Demos

## `v1-cyber-range/` — built and verified, 2026-08-22

Core infra + scenario 1 (web exploit → data breach) are built and have been
run end-to-end repeatedly, cleanly, with the detector firing real alerts
off real traffic every time. Scenario 1 now covers **3 distinct Juice Shop
challenges in one continuous run**: a confidential file exposed with zero
auth, a SQLi login bypass, and a full account takeover via a guessable
security question — each with its own real detection rule and its own
legal-overlay entry (see
[../specs/scenario-web-exploit.md](../specs/scenario-web-exploit.md)). Full
build/verification log: [../REVIEW.md](../REVIEW.md). Still-open items
before the actual lecture (wifi-disconnected test, projector legibility,
final legal-citation pass) are tracked in [../ROADMAP.md](../ROADMAP.md)
Phase 1.

### One-time setup (already done on this machine)

Docker runs via [Colima](https://github.com/abiosoft/colima) (not Docker
Desktop — scriptable, no GUI/license flow):

```bash
brew install colima docker docker-compose docker-buildx
colima start --cpu 4 --memory 8 --disk 60 --vm-type=vz --mount-type=virtiofs
```

### Run it

```bash
cd demos/v1-cyber-range
./run.sh web-exploit
```

This builds and starts the core dashboard plus Juice Shop, the proxy, and
the detector (the attacker does **not** auto-start — see below). Then:

- **Dashboard** (technical timeline + legal overlay): http://127.0.0.1:8080
- **Target app** (through the proxy, so traffic is watched): http://127.0.0.1:3000

Wait a few seconds for Juice Shop to finish booting before hitting either
URL.

### Trigger the attack (on cue, during narration)

```bash
./scenarios/web-exploit/run-attack.sh
```

Runs the full deterministic chain — recon → confidential-file exposure →
SQLi login bypass → broken object-level authorization → account takeover →
breach framing — ~4 seconds between steps by default (`STEP_DELAY` env var on the `attacker` service in
`scenarios/web-exploit/docker-compose.yml` — set lower for a fast test run,
e.g. `docker compose ... run --rm -e STEP_DELAY=0.5 attacker`). Watch it
land on the dashboard in real time.

### Reset to a clean state

```bash
./scenarios/web-exploit/reset.sh
```

Tears down containers + volumes, brings everything back up clean. Verified
at ~22 seconds, well under the "under a minute" bar in
[../CLAUDE.md](../CLAUDE.md). Run this between every rehearsal, per
[../routines/pre-demo-rehearsal.md](../routines/pre-demo-rehearsal.md).

### Layout

```
demos/v1-cyber-range/
  run.sh
  core/
    docker-compose.core.yml   # both networks + the shared dashboard
    range-dashboard/           # stdlib-Python: serves the merged technical + legal view
  scenarios/
    web-exploit/
      docker-compose.yml
      legal-map.json           # CFAA + Colorado statutes, see context/legal-framework.md
      reset.sh
      run-attack.sh
      proxy/                  # logs real traffic to Juice Shop, independent of the attacker
      detector/                # tails that log, fires real alerts on real patterns
      attacker/                # the verified, deterministic exploit chain
```

Full design rationale (including two corrections made mid-build — the
network-isolation design and the Wazuh→lightweight-detector swap) is in
[../specs/architecture.md](../specs/architecture.md),
[../specs/scenario-web-exploit.md](../specs/scenario-web-exploit.md), and
[../specs/dashboard.md](../specs/dashboard.md).
