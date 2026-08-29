# Network-intrusion scenario (Phase 2c)

Status: **built and passing, 2026-08-24** — 4 full live rehearsal runs (2
with real bugs found and fixed live, 2 fully clean end-to-end). Not yet
rehearsal-gated for the actual lecture (needs the 3-consecutive-clean-runs
gate on the real laptop, same bar as [local-llm-agents.md](local-llm-agents.md)).

## Why this exists

`scenarios/agentic/` (OWASP Juice Shop, web-layer techniques only) kept
feeling repetitive no matter how much the attacker/defender prompts were
tuned — the root cause was structural: one target, one protocol, a handful
of similar HTTP tricks. Founder ask: pivot to real OS/server-level attacks,
multiple genuinely different paths in, ideally using real tools and real
CVEs. See [ROADMAP.md](../ROADMAP.md) Phase 2c for the founder-approved
scope (3 paths, added alongside the existing scenarios, curated real
toolset over full Metasploit).

Two options explored and rejected before landing on the current design:
- **Windows Server target**: not possible on this Mac — Docker/Colima only
  run Linux containers, Windows containers need an actual Windows kernel
  host. Samba/SMB on Linux is the real substitute (the actual protocol
  Windows file-sharing uses).
- **SambaCry (CVE-2017-7494)**: checked directly — needs Samba
  4.4/4.5/4.6.x, not available via `apt` on current Debian (only 4.17.x
  is), and a from-source build of that era was judged too fragile to
  rehearse reliably. Real, common misconfiguration used instead: guest/
  anonymous SMB share access (T1021.002/T1135) — still genuinely real,
  just a different real vulnerability class.

## Architecture: same engine, real target/toolset

Reuses everything proven in `scenarios/agentic/` unchanged: the core
dashboard/`/control`/`/status` machinery, the host-native-Ollama brain/hands
split (`brain/common.py` is near-identical, just a different default
`TOOL_API` port), the deterministic end-of-run incident report + evidence
backup pattern, and every small-model reliability lesson (tool shuffling,
`ensure_reasoning()` fallback, `num_ctx` bump, defender-signals-before-block
gating, a minimum-turns floor before the attacker's allowed to conclude).

What's different: `scenarios/network-intrusion/tool-api/`'s attacker tools
shell out to **real, industry-standard tools** (`nmap`, `hydra`,
`smbclient`, `ssh`/`sshpass`) against real target containers, instead of
custom Python HTTP-client tricks against a web app.

### Three separate target hosts, not one multi-service box

`scenarios/network-intrusion/targets/` — richer and more realistic than a
single container: the attacker has to discover multiple real hosts on the
segment (a real `nmap` sweep) before picking a vector, not just enumerate
one target's port list.

- **`ssh-host`**: real OpenSSH, one account (`svc-backup`) with an
  intentionally weak password (`sunshine1`, buried 6th in a 10-entry
  wordlist so a real brute-force genuinely has to try several guesses
  first) — T1110.001.
- **`ftp-host`**: a minimal, real, hand-written reproduction of the
  documented CVE-2011-2523 vsftpd backdoor trigger and resulting shell —
  **not** the literal 2011 compromised binary (a candidate pre-built image
  was checked and found to no longer exist on Docker Hub; no other
  reliable, verifiable way to source the actual historical binary safely).
  A real FTP control-connection listener (`server.py`) that, on a username
  ending in `:)`, opens a real bind shell on port 6200 — genuine socket
  listener, genuine subprocess shell, verified by hand (real root shell,
  real `whoami`/`id`/`uname -a` output) before any automation was built
  against it. T1210.
- **`smb-host`**: real Samba (4.17.x), one share (`public`) configured for
  guest/anonymous access, holding one real sensitive-looking file
  (`confidential-layoffs.txt`) — T1021.002/T1135/T1039.

### Real, independent detection — same "watch real logs" pattern, harder to get right this time

`scenarios/network-intrusion/detector/detector.py` tails three real logs
and pattern-matches, same fired-once/sliding-window style as
`scenarios/web-exploit/detector/detector.py`:
- SSH: real OpenSSH auth log (`sshd -E`), regex on `Failed password`/
  `Accepted password` lines, sliding-window brute-force threshold.
- FTP: `ftp-host`'s own real connection log (JSONL — it's this repo's own
  code, so a structured format was the natural choice), watches for the
  backdoor-trigger and shell-connected events.
- SMB: **not** Samba's own internal logging. Several real attempts were
  made first — `log level` up to 10, the purpose-built `vfs_full_audit`
  module — and none reliably surfaced a connect-level line on this Samba
  version's split `rpc_host` worker-process architecture. Pivoted to the
  same pattern `scenarios/web-exploit/proxy/server.py` already uses: a
  tiny, independent TCP proxy (`targets/smb-host/proxy.py`) in front of
  `smbd`, logging every real connection (source, byte counts) completely
  independently of Samba itself. Fully within this repo's own control, and
  it worked immediately once built.

### The attacker's tools

`GET /tools?role=attacker` on `tool-api` (port 9100, published to
`127.0.0.1` like every other scenario's hands layer):

| Tool | What it really does | Technique |
|---|---|---|
| `network_sweep` | Real `nmap -sn` ping sweep of the actual `cyberrange_net` subnet (computed at runtime by resolving a known single-homed target's hostname — see "Real bugs found" below for why not tool-api's own hostname) | T1018 |
| `port_scan_host` | Real `nmap -sV` service scan on one host | T1046 |
| `ssh_bruteforce` | Real `hydra` run against a 10-entry wordlist | T1110.001 |
| `ssh_shell` | Real `ssh`/`sshpass` login with cracked credentials, runs real enumeration commands | T1021.004 |
| `vsftpd_backdoor` | Real protocol trigger + real shell, runs real enumeration commands | T1210 |
| `plant_marker` | Reuses the real backdoor shell to actually write `/root/ATTACKER_WON.txt` to the host's real filesystem and `cat` it back to confirm — a real, verified write, gated on a prior successful `vsftpd_backdoor` on that host | T1491.001 |
| `smb_enum` | Real `smbclient -L` (shares) + `ls` per share (files) | T1135 |
| `smb_download` | Real `smbclient get` (pulls the fictional `confidential-layoffs.txt` HR memo off the anonymous share) | T1039 |
| `cover_tracks` | Real burst of decoy TCP connects through the real channel | T1070 |

`plant_marker` exists to make the "read vs. write" distinction concrete for
the room: `smb_download`/`ssh_shell` show an attacker *reading* data they
shouldn't; `plant_marker` shows the same root shell *altering* the disk —
the write access that, in a real breach, is what plants ransomware or
destroys evidence. It writes one harmless marker instead, and reads it back
so the "win" is a confirmed real file (visible with `docker exec ni-ftp-host
cat /root/ATTACKER_WON.txt`), never a claimed one. Legally it reuses
`cfaa-1030a2` — the same unauthorized-access event as the backdoor shell
that enabled it — rather than asserting an unverified new citation for
CFAA's separate damage subsection (§ 1030(a)(5)); see the legal-map note.
`reset.sh`'s full container recreation wipes the marker, so reset-to-zero
still holds.

`block_attacker` here is **more final** than `scenarios/agentic`'s version,
on purpose: a network-level block on a source is genuinely more effective
than revoking one web-app session token (which doesn't patch anything).
Recon tools stay available after a block; the exploitation tools don't, and
there's no re-authentication bypass path in this domain the way there is in
`scenarios/agentic`. It's gated on a restraint mechanism (the defender must
have raised at least one prior signal — `MIN_SIGNALS_BEFORE_BLOCK`, with a
lower bar once the detector has fired a confirmed critical alert), so the
defender still can't hair-trigger a block on nothing.

### Why block *success* is a coin flip

Whether an earned block actually **lands** is decided by a one-per-run coin
flip (`BLOCK_SUCCESS_PROB`, default `0.5`), not by the timing race between
the two models. We tried to tune the timing to a stable ~50/50 attacker-vs-
defender ratio and it isn't achievable: the ratio swings almost entirely on
the presenter's live speed setting (at Normal pace the defender reacts fast
enough to win nearly every run; at Instant the attacker outruns it), so no
fixed timing tune holds across the paces a presenter actually uses live.
Measured runs bore this out — every timing-only configuration landed at one
extreme or the other, never in the middle.

So the *outcome* of a block is randomised while **every other part stays
real**: the detector still fires on real traffic, the defender still has to
earn the block through real alerts and the restraint gate, and the attacker
still does real exploitation. Only "did the firewall rule actually stop
them, or did they already have enough of a foothold to slip it" is the toss-
up — which is itself a real property of incident response, not pure
invention. The flip is resolved once and cached per run (a failed block
isn't silently retried into an eventual success, which would collapse back
to the defender always winning). Crucially, a failed block is labelled on
screen as a deliberate ~50/50 chance outcome, **not** a real detection or
evasion result — same honesty bar as the legal citations: the room is never
shown a coin flip dressed up as a technical fact. Set `BLOCK_SUCCESS_PROB`
to `0.0` or `1.0` on the `tool-api` service to force a scripted outcome for
a rehearsed run. To re-check the ratio after any change, run the dev
harness `scenarios/network-intrusion/measure-balance.sh [runs] [delay_ms]`
(runs the full two-LLM scenario N times and classifies each from the real
event stream — not part of the demo run path).

## Real bugs found by actually running it, not by review

Same discipline as every other scenario in this repo — four real issues,
found across four live rehearsal runs:

1. **Wrong-subnet sweep, 0 hosts found.** `own_subnet()` originally
   resolved tool-api's own hostname to determine what to scan — but
   `tool-api` is dual-homed (`cyberrange_net` + `cyberrange_view`), and
   resolving its own hostname non-deterministically picked up the wrong
   network's IP in one rehearsal run, sweeping an entirely wrong subnet
   (0 real hosts found, 0 confirmed findings for the whole run). Fixed by
   resolving a known **single-homed** target (`ssh-host`) instead —
   unambiguous by construction.
2. **No post-exploitation path for SSH.** The attacker cracked SSH
   credentials via `ssh_bruteforce` but had no tool to actually *use*
   them — it re-ran the brute-force three times in one run, then
   hallucinated a fake `ls` command in prose instead of calling a real
   tool (there wasn't one). Added `ssh_shell`, which logs in with the
   already-cracked password and runs real commands — the attacker used
   the crack-then-shell sequence correctly, once each, in every
   subsequent run.
3. **Noisy shell output causing a real turn timeout.** `vsftpd_backdoor`'s
   raw shell output included real tty/prompt artifacts
   (`/bin/sh: can't access tty...`, `/app #`) that bloated conversation
   context enough to contribute to a genuine model-turn timeout later in
   one run. Stripped the noise at the source; also raised this scenario's
   `TURN_TIMEOUT` (30s → 45s) since real tool round-trips here (hydra, nmap)
   are already slower than the web scenario's HTTP calls.
4. **Confusing miss/false-positive risk carried over from `scenarios/agentic`
   already fixed there** — not re-found here, but the same "don't trust a
   bare success signal without checking what's real" discipline applied
   throughout (e.g. `own_subnet()`'s bug above was caught exactly this way:
   noticing the *result* — 0 hosts — didn't match reality, not by
   inspecting the code and assuming it was right).

## Legal map

`scenarios/network-intrusion/legal-map.json` deliberately **reuses** two
entries from `scenarios/web-exploit/legal-map.json` (`cfaa-1030a2`,
`cfaa-1030a2-misconfig`) rather than writing new ones from scratch — but
only after checking the underlying legal elements genuinely fit these new
fact patterns (SSH brute-forcing / backdoor exploitation vs. web SQLi
bypass are both "never had authorized access, circumvented a real
control"; anonymous SMB access vs. the web scenario's unauthenticated-file
case are both "no control was ever defeated, there simply wasn't one") —
documented reuse, not lazy copying. See the file's own `_note`.

## Running it

```bash
cd demos/v1-cyber-range
./run.sh network-intrusion
brew services start ollama   # or: ollama serve
cd scenarios/network-intrusion
./run-network-intrusion.sh
```

Reset: `scenarios/network-intrusion/reset.sh` — same full `down -v && up`
pattern as every other scenario (in-memory detector dedup state and the
`ni_service_logs` volume both only clear on a real recreation).
