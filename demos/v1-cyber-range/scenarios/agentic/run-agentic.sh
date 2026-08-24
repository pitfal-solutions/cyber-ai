#!/usr/bin/env bash
# Trigger both brain loops on cue during the live narration -- host-side
# processes, NOT containers (see specs/architecture.md's "Local LLM
# runtime" and brain/common.py's docstring for why).
#
# Requires: `./run.sh agentic` already up, and Ollama running natively
# ('brew services start ollama' or 'ollama serve') with both models pulled
# -- see bench-models.sh. Use the dashboard's pause/speed controls
# (http://127.0.0.1:8080) to control pacing live; this script just starts
# both loops and gets out of the way.
set -euo pipefail
cd "$(dirname "$0")"

ATTACKER_MODEL="${ATTACKER_MODEL:-qwen2.5:7b-instruct}"
DEFENDER_MODEL="${DEFENDER_MODEL:-qwen2.5:3b-instruct}"

if ! curl -sS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
  echo "ERROR: Ollama not reachable at 127.0.0.1:11434 -- start it first" >&2
  echo "('brew services start ollama' or 'ollama serve')." >&2
  exit 1
fi
if ! curl -sS http://127.0.0.1:9000/health >/dev/null 2>&1; then
  echo "ERROR: tool-api not reachable at 127.0.0.1:9000 -- run './run.sh agentic' first." >&2
  exit 1
fi

echo "== starting defender (model=${DEFENDER_MODEL}) -- watching in the background =="
DEFENDER_MODEL="$DEFENDER_MODEL" python3 brain/defender_agent.py &
DEFENDER_PID=$!
trap 'kill "$DEFENDER_PID" 2>/dev/null || true' EXIT

echo "== starting attacker (model=${ATTACKER_MODEL}) =="
ATTACKER_MODEL="$ATTACKER_MODEL" python3 brain/attacker_agent.py
ATTACKER_STATUS=$?

echo "== attacker finished -- signaling the defender to wrap up and compile the incident report =="
# Tells the defender's independently-polling loop the engagement is over
# (defender_agent.py checks this each cycle) -- see
# specs/local-llm-agents.md's "End-of-run incident report". Without this,
# the defender would keep watching for up to its own MAX_REACTIONS/
# RUN_TIMEOUT (defender_agent.py) with nothing left to react to.
curl -sS -X POST -H 'Content-Type: application/json' -d '{"attacker_finished": true}' \
  http://127.0.0.1:8080/control >/dev/null || true

# Bounded wait, not open-ended: gives the defender a real chance to react
# to any trailing alert and compile the report, but exits as soon as it
# actually finishes rather than always waiting the full timeout. The trap
# above still cleans it up if something hangs.
for _ in $(seq 1 20); do
  kill -0 "$DEFENDER_PID" 2>/dev/null || break
  sleep 1
done

exit "$ATTACKER_STATUS"
