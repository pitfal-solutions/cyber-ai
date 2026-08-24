#!/usr/bin/env bash
# On-machine model memory/latency bench for the Phase 2 agentic scenario.
#
# This is the working-agreement-#7 decision artifact: don't pick a model
# from a blog post, pick it from a real `ollama ps`/latency check on the
# actual demo laptop. Run this on THAT machine before recording a final
# pick in ../../../specs/local-llm-agents.md -- results are hardware-
# specific and a dev-machine run does not set the final choice.
#
# Usage:
#   ./bench-models.sh
#   ATTACKER_MODEL=llama3.1:8b-instruct-q4_K_M DEFENDER_MODEL=llama3.2:3b ./bench-models.sh
set -euo pipefail

ATTACKER_MODEL="${ATTACKER_MODEL:-qwen2.5:7b-instruct}"
DEFENDER_MODEL="${DEFENDER_MODEL:-qwen2.5:3b-instruct}"
OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

echo "== Bench: attacker=$ATTACKER_MODEL  defender=$DEFENDER_MODEL =="
echo "Ollama host: $OLLAMA_HOST"
echo

if ! curl -sS "$OLLAMA_HOST/api/version" >/dev/null 2>&1; then
  echo "ERROR: Ollama not reachable at $OLLAMA_HOST -- is 'ollama serve' (or" >&2
  echo "'brew services start ollama') running?" >&2
  exit 1
fi

echo "-- Pulling models (skips already-present layers) --"
ollama pull "$ATTACKER_MODEL"
ollama pull "$DEFENDER_MODEL"

echo
echo "-- Loading both concurrently and timing representative tool-calling turns --"
python3 "$(dirname "$0")/bench_models.py" "$ATTACKER_MODEL" "$DEFENDER_MODEL" "$OLLAMA_HOST"

echo
echo "-- ollama ps (resident memory / GPU offload -- confirms both stayed loaded) --"
ollama ps

echo
echo "Record the numbers above in specs/local-llm-agents.md under"
echo "'Actual on-machine result'. Target: ~3-5s per turn, both models"
echo "listed in 'ollama ps' with 100% GPU processor."
