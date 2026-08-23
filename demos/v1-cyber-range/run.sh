#!/usr/bin/env bash
# Bring up the core (network, dashboard) plus one scenario.
# Usage: ./run.sh web-exploit
set -euo pipefail
cd "$(dirname "$0")"

SCENARIO="${1:-web-exploit}"
SCENARIO_DIR="scenarios/${SCENARIO}"

if [ ! -f "${SCENARIO_DIR}/docker-compose.yml" ]; then
  echo "No such scenario: ${SCENARIO} (expected ${SCENARIO_DIR}/docker-compose.yml)" >&2
  exit 1
fi

echo "== bringing up core + ${SCENARIO} =="
# The attacker service is in the "manual" profile, so a plain `up` starts
# everything except it -- see run-attack.sh to trigger the attack on cue.
# --project-directory pins build-context resolution to this directory
# regardless of which -f file docker compose treats as "first".
docker compose --project-directory . -f core/docker-compose.core.yml -f "${SCENARIO_DIR}/docker-compose.yml" up -d --build

echo ""
echo "Dashboard:  http://127.0.0.1:8080"
echo "Target app: http://127.0.0.1:3000 (through the proxy)"
echo ""
echo "When ready to narrate the attack:"
echo "  ${SCENARIO_DIR}/run-attack.sh"
echo ""
echo "To reset to a clean state:"
echo "  ${SCENARIO_DIR}/reset.sh"
