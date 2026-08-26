#!/usr/bin/env bash
# Reset to a clean state: tear down containers + volumes, bring the core and
# this scenario back up fresh. Full down -v && up, not a lightweight event
# clear -- the detector holds in-memory dedup state, and the target hosts'
# real logs (ni_service_logs volume) persist across a plain restart, both
# of which only a real container/volume recreation clears. See
# scenarios/agentic/reset.sh for the same lesson learned there first.
set -euo pipefail
cd "$(dirname "$0")/../.."

COMPOSE=(docker compose --project-directory . -f core/docker-compose.core.yml -f scenarios/network-intrusion/docker-compose.yml)

echo "== tearing down (containers + volumes) =="
# --remove-orphans: no compose file sets an explicit project `name`, so all
# 3 scenarios share one implicit project -- this also cleans up any other
# scenario's containers left running from a switch without a prior reset.
"${COMPOSE[@]}" down -v --remove-orphans

echo "== bringing up clean =="
"${COMPOSE[@]}" up -d --build --remove-orphans

echo ""
echo "Clean. Dashboard: http://127.0.0.1:8080"
