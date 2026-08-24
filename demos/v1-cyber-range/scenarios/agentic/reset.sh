#!/usr/bin/env bash
# Reset to a clean state: tear down containers + volumes, bring the core and
# this scenario back up fresh. Full down -v && up, not a lightweight event
# clear -- the detector holds in-memory dedup state (see
# scenarios/web-exploit/detector/detector.py) that only a real container
# recreation clears; verified the hard way during this scenario's build
# (see REVIEW.md). See routines/pre-demo-rehearsal.md -- this must complete
# in under a minute.
#
# Does NOT touch Ollama or the host-side brain processes (scenarios/agentic/
# brain/) -- those aren't containers, see specs/architecture.md's "Local
# LLM runtime". If a brain process is still running from a prior run, stop
# it (Ctrl-C on run-agentic.sh) before starting a fresh one.
set -euo pipefail
cd "$(dirname "$0")/../.."

COMPOSE=(docker compose --project-directory . -f core/docker-compose.core.yml -f scenarios/agentic/docker-compose.yml)

echo "== tearing down (containers + volumes) =="
"${COMPOSE[@]}" down -v

echo "== bringing up clean =="
"${COMPOSE[@]}" up -d --build

echo ""
echo "Clean. Dashboard: http://127.0.0.1:8080  Target: http://127.0.0.1:3000"
