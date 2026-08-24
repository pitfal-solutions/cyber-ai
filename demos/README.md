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

## The agentic scenario (`scenarios/agentic/`) — built, one clean run verified, 2026-08-22

Two small local LLMs choose their own actions in real time — one attacker,
one defender — against the same real Juice Shop target, with the dashboard
showing both sides live plus a presenter-controlled pause/speed. The
attacker picks from 10 real tools (network recon — resolve the target's IP,
scan its ports — plus web-app techniques: two different ways to get a
session, two different broken-access-control findings, account takeover,
and a decoy-traffic "cover tracks" move once it's done) in whatever order
it wants, and a defender's session-revoke is a real setback, not a
permanent stop — the attacker re-authenticates and keeps going, using what
it already learned. Once the attacker's done, the defender compiles a
real, log-derived incident report (confirmed findings with statute
references, or an honest "nothing confirmed" if there's nothing to
report) and backs up the evidence to timestamped files. See
[../specs/local-llm-agents.md](../specs/local-llm-agents.md) for the full
toolset and design notes. **Not yet rehearsal-gated** (needs 3 consecutive
clean runs on the actual demo laptop, and `bench-models.sh` re-run there);
the scripted scenario above is what ships to the lecture regardless.

### One-time setup

Ollama runs **on the host, not in Docker** — Docker Desktop on macOS can't
pass the Metal GPU through to a container, so a dockerized Ollama would
mean CPU-only inference (see
[../specs/architecture.md](../specs/architecture.md)'s "Local LLM runtime"):

```bash
brew install ollama
brew services start ollama   # or: ollama serve
```

Then pick a model pair by actually running the bench script on your
machine (don't trust a blog post's model recommendation — working
agreement #7 in [../CLAUDE.md](../CLAUDE.md)):

```bash
cd demos/v1-cyber-range/scenarios/agentic
./bench-models.sh
```

Defaults to `qwen2.5:7b-instruct` (attacker) + `qwen2.5:3b-instruct`
(defender), overridable via `ATTACKER_MODEL`/`DEFENDER_MODEL` env vars.

**Testing on a smaller machine?** A single shared `qwen2.5:3b-instruct` for
both roles works well and needs no extra downloads if you already have it
— see [../specs/local-llm-agents.md](../specs/local-llm-agents.md)'s
"Quick local test on a smaller machine" section for the exact command.
This is a dev-convenience config, not a replacement for running
`bench-models.sh` for real on whichever machine ends up presenting.

### Run it

```bash
cd demos/v1-cyber-range
./run.sh agentic
```

Then, when ready to start both AI brains:

```bash
./scenarios/agentic/run-agentic.sh
```

Dashboard (same one as `web-exploit`, with a Pause/Resume button and a
Slow/Normal/Fast/Instant speed selector added): http://127.0.0.1:8080

### Reset to a clean state

```bash
./scenarios/agentic/reset.sh
```

Full container teardown/rebuild, not a lightweight event clear — the
detector holds in-memory dedup state that only a real recreation clears
(found the hard way — see [../REVIEW.md](../REVIEW.md)). ~23 seconds.

### Layout

```
scenarios/agentic/
  docker-compose.yml   # Juice Shop + proxy + detector (reused from web-exploit) + tool-api
  legal-map.json       # same fact patterns as web-exploit's
  tool-api/             # the constrained attacker/defender action menu ("hands")
  brain/                # host-side, NOT containers -- common.py, attacker_agent.py, defender_agent.py
  bench-models.sh / bench_models.py
  run-agentic.sh / reset.sh
```

## The network-intrusion scenario (`scenarios/network-intrusion/`) — built, 4 rehearsal runs, 2026-08-24

A second, additional AI-vs-AI scenario, added because the agentic scenario
above kept feeling repetitive (one web app, one family of techniques) no
matter how much it was tuned. Same two-LLM structure, but the attacker
targets a small network of three real Linux hosts using real tools instead
of a web app: `nmap` for recon, `hydra` for SSH credential brute-forcing,
a real reproduction of the CVE-2011-2523 vsftpd backdoor for a real root
shell, and `smbclient` for anonymous SMB file access. See
[../specs/network-intrusion.md](../specs/network-intrusion.md) for the
full design, the real CVEs/tooling research, and the bugs found rehearsing
it. **Not yet rehearsal-gated**, same bar as the agentic scenario above.

### Setup and run

Same Ollama setup as the agentic scenario above (shared `bench-models.sh`
artifact — no need to re-run it for this scenario specifically):

```bash
cd demos/v1-cyber-range
./run.sh network-intrusion
cd scenarios/network-intrusion
./run-network-intrusion.sh
```

Dashboard: http://127.0.0.1:8080 (same instance, same pause/speed controls).
Reset: `./scenarios/network-intrusion/reset.sh` (same full teardown/rebuild
pattern, needed here too — both the detector's in-memory dedup state and
the real service logs in the `ni_service_logs` volume only clear on a real
recreation).

### Layout

```
scenarios/network-intrusion/
  docker-compose.yml   # 3 target hosts + detector + tool-api, all on cyberrange_net
  legal-map.json       # 2 entries reused from web-exploit's, verified to genuinely fit
  targets/
    ssh-host/           # real OpenSSH, one weak-password account
    ftp-host/           # real, hand-written reproduction of the vsftpd 2.3.4 backdoor
    smb-host/           # real Samba + a small independent connection-logging proxy
  tool-api/             # real nmap/hydra/smbclient/ssh invocations ("hands")
  detector/              # tails 3 real logs (SSH auth log, FTP's own log, the SMB proxy's log)
  brain/                # host-side, NOT containers -- same structure as scenarios/agentic/brain/
  run-network-intrusion.sh / reset.sh
```
