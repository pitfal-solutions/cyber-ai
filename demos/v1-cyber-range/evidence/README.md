# Evidence

`tool_investigate_incident()` (in each scenario's `tool-api/server.py`)
backs up the real event/access/service logs here at the end of a run, as
part of the defender's "evidence preserved for trial" incident report —
see [../../../specs/local-llm-agents.md](../../../specs/local-llm-agents.md)
and [../../../specs/network-intrusion.md](../../../specs/network-intrusion.md).

Bind-mounted from the host on purpose, not the `cyberrange_events` Docker
volume everything else in `/data` lives in: `reset.sh` runs `docker compose
down -v`, which deletes named volumes — anything written there would be
gone before anyone could look at it, defeating the point of an incident
report. This directory survives resets.

Everything here is demo output, gitignored, and safe to delete any time:

```bash
rm -f demos/v1-cyber-range/evidence/evidence-*.jsonl
```
