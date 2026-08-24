#!/usr/bin/env bash
# Trigger both brain loops on cue during the live narration -- host-side
# processes, NOT containers (see specs/architecture.md's "Local LLM
# runtime" and brain/common.py's docstring for why).
#
# Requires: `./run.sh network-intrusion` already up, and Ollama running
# natively ('brew services start ollama' or 'ollama serve') with both
# models pulled -- see ../agentic/bench-models.sh (same model-decision
# artifact, reused across scenarios). Use the dashboard's pause/speed
# controls (http://127.0.0.1:8080) to control pacing live.
set -euo pipefail
cd "$(dirname "$0")"

ATTACKER_MODEL="${ATTACKER_MODEL:-qwen2.5:7b-instruct}"
DEFENDER_MODEL="${DEFENDER_MODEL:-qwen2.5:3b-instruct}"

if ! curl -sS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
  echo "ERROR: Ollama not reachable at 127.0.0.1:11434 -- start it first" >&2
  echo "('brew services start ollama' or 'ollama serve')." >&2
  exit 1
fi
if ! curl -sS http://127.0.0.1:9100/health >/dev/null 2>&1; then
  echo "ERROR: tool-api not reachable at 127.0.0.1:9100 -- run './run.sh network-intrusion' first." >&2
  exit 1
fi

echo "== starting defender (model=${DEFENDER_MODEL}) -- watching in the background =="
DEFENDER_MODEL="$DEFENDER_MODEL" python3 brain/defender_agent.py &
DEFENDER_PID=$!
trap 'kill "$DEFENDER_PID" 2>/dev/null || true' EXIT

echo "== starting attacker (model=${ATTACKER_MODEL}) =="
# attacker_agent.py signals attacker_finished itself at the end of its own
# run (see its main()) -- simpler than having this script do it, and still
# correct if the script is ever run directly during dev/testing.
ATTACKER_MODEL="$ATTACKER_MODEL" python3 brain/attacker_agent.py
ATTACKER_STATUS=$?

echo "== attacker finished -- giving the defender a bounded window to react and report =="
for _ in $(seq 1 30); do
  kill -0 "$DEFENDER_PID" 2>/dev/null || break
  sleep 1
done

exit "$ATTACKER_STATUS"
