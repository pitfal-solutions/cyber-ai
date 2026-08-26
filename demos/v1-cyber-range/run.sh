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
# --remove-orphans: no compose file here sets an explicit project `name`,
# so all 3 scenarios share one implicit project (this directory's name) --
# switching scenarios without resetting the previous one first otherwise
# leaves its containers behind as unrecognized "orphans" of this project.
docker compose --project-directory . -f core/docker-compose.core.yml -f "${SCENARIO_DIR}/docker-compose.yml" up -d --build --remove-orphans

echo ""
echo "Dashboard:  http://127.0.0.1:8080"
# web-exploit and agentic both reuse the Juice Shop proxy's published port;
# network-intrusion's targets are attacker-only, no host port at all.
if [ "${SCENARIO}" = "web-exploit" ] || [ "${SCENARIO}" = "agentic" ]; then
  echo "Target app: http://127.0.0.1:3000 (through the proxy)"
fi
echo ""
# Scenario-aware on purpose: scripted scenarios trigger on cue with
# run-attack.sh, agentic-style scenarios start both host-side brain loops
# with their own run-*.sh (see specs/local-llm-agents.md) -- printing the
# wrong filename here would send the presenter looking for a script that
# doesn't exist.
if [ -f "${SCENARIO_DIR}/run-attack.sh" ]; then
  echo "When ready to narrate the attack:"
  echo "  ${SCENARIO_DIR}/run-attack.sh"
else
  RUN_SCRIPT=$(find "${SCENARIO_DIR}" -maxdepth 1 -name "run-*.sh" | head -1)
  if [ -n "$RUN_SCRIPT" ]; then
    echo "When ready to start both AI brain loops (requires Ollama running"
    echo "natively -- see specs/local-llm-agents.md):"
    echo "  ${RUN_SCRIPT}"
  fi
fi
echo ""
echo "To reset to a clean state:"
echo "  ${SCENARIO_DIR}/reset.sh"
