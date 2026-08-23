# Tech stack research (2026-08-22)

Research pass done before any building started, to answer: is the
Docker-containers-for-attack-and-defense instinct sound, and what should we
actually build on top of vs. reuse. Sources are linked inline; treat model
names and specific numbers from blog-style sources as directional, not
verified — several were not corroborated further given the timeline (see
the local-LLM section).

## Is "two Docker containers, attacker vs. defender" the right approach?

**Yes — this is what the existing ecosystem already does.** It's not a
naive instinct that needs correcting:

- **AgentCyberRange** is a containerized benchmark environment built exactly
  this way — attacker agents instantiated as dedicated Docker containers
  connected to benchmark networks, orchestrated with Docker Compose.
  ([arxiv.org/pdf/2606.14295](https://arxiv.org/pdf/2606.14295))
- **MITRE Caldera** (now under the Apache Software Foundation as
  `apache/caldera`) is the reference automated-adversary-emulation platform
  the security industry already uses for this kind of exercise — async C2
  server, REST API, web UI, 527+ ATT&CK-mapped procedures out of the box,
  official Docker image (`mitre/caldera` on Docker Hub).
  ([github.com/apache/caldera](https://github.com/apache/caldera),
  [hub.docker.com/r/mitre/caldera](https://hub.docker.com/r/mitre/caldera))
- A cataloged ecosystem of 70+ open-source AI pentesting tools exists as of
  early-to-mid 2026, several with Docker-sandboxed multi-agent architectures
  (e.g. PentAGI). This confirms the "AI agent attacks a Docker target" shape
  is well-trodden, not novel risk.
  ([appsecsanta.com/research/ai-pentesting-agents-2026](https://appsecsanta.com/research/ai-pentesting-agents-2026))

**Conclusion:** keep the Docker approach. Don't build a custom VM-based lab
unless a specific scenario needs Windows/AD (see the GOAD section below for
why we're avoiding that even then).

## Target / vulnerable application (scenario 1: web exploit → data breach)

**Recommendation: OWASP Juice Shop.**

- Official OWASP project, described as "probably the most modern and
  sophisticated insecure web application" for training/CTF use — a
  realistic Node.js e-commerce app with 100+ scored vulnerabilities across
  every OWASP Top 10 category.
  ([owasp.org/www-project-juice-shop](https://owasp.org/www-project-juice-shop/))
- Has an official **trainer's guide** written specifically for running
  classroom sessions, including guidance on distributing instances (or using
  MultiJuicer for multi-instance hosting, not needed for our speaker-run-only
  scope).
  ([help.owasp-juice.shop/appendix/trainers.html](https://help.owasp-juice.shop/appendix/trainers.html))
- Single Docker container, no external data seeding required.

**DVWA** (PHP/MySQL) was the alternative considered — its per-vulnerability
pages show source code inline, which is a nice teaching aid, but Juice Shop's
realism and official training documentation make it the stronger fit for a
credible-looking one-shot demo.
([offensive360.com — vulnerable web apps guide](https://offensive360.com/blog/intentionally-vulnerable-web-applications-guide/))

## Defensive dashboard / SIEM

**Recommendation: Wazuh (Docker single-node stack).**

- Official Docker deployment path exists
  ([documentation.wazuh.com — Docker deployment](https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html)).
- A single-node stack (manager + indexer + dashboard) runs on one machine at
  roughly 6GB total — reasonable alongside everything else on a 48GB laptop.
- Ships with real detection rules and a working dashboard UI out of the box
  — faster to get a *real*, working "alert fires when the attack happens"
  moment in 2-3 days than hand-building Grafana panels from nothing.
- A public reference project
  (`charan-s108/Wazuh-on-Docker`) demonstrates exactly this shape: simulate
  attacks, generate real alerts, visualize in the Wazuh dashboard, all
  Docker, all one machine.
  ([github.com/charan-s108/Wazuh-on-Docker](https://github.com/charan-s108/Wazuh-on-Docker))

**Security Onion** was considered and set aside for v1 — heavier, more
sensor-oriented, better suited to network-wide monitoring than a
single-target laptop demo.

**Grafana** is not needed for v1's dashboard. It remains a good option later
*specifically* for the bespoke "legal overlay" panel or for visualizing the
Phase 2 agentic decision loop, since no OSS tool ships that content —
`grafana/skills` (see the skills.sh section below) is a real, installable
skill collection to lean on if/when that gets built.

## Ransomware / lateral-movement scenario (Phase 3) — GOAD evaluated and rejected for now

**GOAD (Game of Active Directory)** is the standard free lab for practicing
AD lateral movement — five target machines across multiple domains, many
built-in AD vulnerabilities.
([orange-cyberdefense.github.io/GOAD](https://orange-cyberdefense.github.io/GOAD/))

**Rejected for this project's timeline:** GOAD is provisioned via
Vagrant/Proxmox as full VMs (Windows Server domain controllers, multiple
machines), not lightweight Docker containers. That's a heavy, slow-to-
provision footprint for a laptop demo built in days, and it breaks the
"reset in under a minute" quality bar (working agreement in `CLAUDE.md`).

**Recommendation when Phase 3 starts:** build a minimal Docker-only
lateral-movement mock instead — 2-3 small Linux containers with
intentionally weak/shared SSH credentials, enough to demonstrate the
*technique* (credential reuse → lateral movement → encryption of a target's
files) without standing up real Active Directory.

## Local LLMs for the agentic scenario (Phase 2)

**Hardware:** MacBook, Apple M4, 48GB unified memory, target: fully offline
via Ollama, two models running concurrently (one attacker-loop, one
narration/analysis).

Research surfaced specific model recommendations from several 2026 "best
local LLM" roundups (e.g. dual setups combining a ~20B and a ~27B-class
model, totaling ~50GB "hot"). **These are treated as directional, not
adopted directly** — several specific model names in the sources couldn't be
independently corroborated with confidence in this pass, and local-model
recommendations age out within months. Working agreement #7 in
[`../CLAUDE.md`](../CLAUDE.md) covers why: the real decision happens via an
actual `ollama run <model>` memory/latency check on the real machine, not a
blog post.

**What to try first (a starting point, not a commitment):**
- A **7-14B-class tool-calling-capable model** for the live agent loop
  (attacker or defender action selection) — this is the class of model
  well-established general-purpose local options (e.g. Llama 3.x, Qwen2.5/3
  in the 7-14B range) target for reliable structured tool use.
- A **smaller ~3B-class model** for narration/commentary generation, run
  alongside the first, to keep total resident memory well under the 48GB
  ceiling with headroom for the rest of the Docker stack and macOS itself.

**Prior art worth reading (not adopting wholesale) for the agent-loop
design:**
- **Strix** (`usestrix/strix`) — an actively maintained open-source
  autonomous AI pentesting agent, surfaced via a skills.sh "pentest" search
  (see below). Real project, real architecture reference for how to
  structure an LLM-driven attacker's tool loop.
- **MITRE/Apache Caldera** — see above; also relevant as an *inspiration*
  for a structured, ATT&CK-mapped action space to constrain the local LLM
  to (a fixed menu of allowed techniques is both safer and more reliable
  than an unconstrained agent for a live demo).

## skills.sh findings

Searched the live site (`skills.sh`) directly — search box, not just the
static homepage — for: `docker`, `security`, `grafana`, `pentest`, and
browsed `/topic` (topic categories: frontend, Next.js, design/UI, mobile,
agent-workflow, database, testing, marketing — **no cybersecurity, red-team/
blue-team, or network-design topic category exists** as of this search).

**Nothing purpose-built for "build a cyber range / attack-defense
simulation" exists on skills.sh.** Closest real, installable results:

| Search | Notable real results | Useful here? |
|---|---|---|
| `docker` | `multi-stage-dockerfile` (github/awesome-copilot), `docker-patterns` (affaan-m/ecc), `tag-run-on-local-docker` (nvidia/skills) | Generic Dockerfile-authoring help — marginal, our compose setup is simple enough not to need it. |
| `grafana` | Official `grafana/skills` repo — `promql`, `dashboarding`, `alerting-irm`, `loki`, `tempo`, etc. | Not needed for v1 (Wazuh covers the dashboard). Worth installing later only if a bespoke Grafana panel gets built for the legal overlay or the agentic decision loop. |
| `security` | `security-review` / `security-audit` (getsentry, cloudflare, github/awesome-copilot, openai/skills), `security-and-hardening` (addyosmani/agent-skills) | These are **code-review/hardening skills** (review your own code for vulnerabilities), not attack-simulation or red-team skills. Not directly useful for building the demo. |
| `pentest` | `usestrix/strix` (managed-pentesting-with-strix), `yaklang/hack-skills` (android/kubernetes/iOS pentesting tricks), `zhaoxuya520/reverse-skill` | Real prior-art projects, not "skills" in the sense of packaged instructions we'd install — see the local-LLM section above for how these inform Phase 2 design. |

**Conclusion:** no skill install closes any part of this build. The build
itself (compose files, scenario scripts, legal-mapping data, agent-loop
design) has to be written directly, informed by the prior art above rather
than assembled from off-the-shelf skills.
