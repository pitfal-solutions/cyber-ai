#!/usr/bin/env bash
# Dev/measurement tool -- NOT part of the demo run path. Runs the
# network-intrusion agentic scenario end to end N times and reports the
# attacker-vs-defender win ratio, so the BLOCK_SUCCESS_PROB balance dial
# (see tool-api/server.py) can be re-checked after any change that could
# affect it. Companion to how bench-models.sh is a dev artifact, not a
# demo step. See specs/network-intrusion.md ("Why block success is a coin
# flip") and REVIEW.md's 2026-08-25 defender-rebalance entry.
#
# Requires: `../../run.sh network-intrusion` already up, and Ollama running
# (same prerequisites as run-network-intrusion.sh).
#
# Usage (from this directory):
#   ./measure-balance.sh [runs] [delay_ms]
#   ./measure-balance.sh 8 3000
#   BLOCK_SUCCESS_PROB is read by the tool-api container, not here -- to test
#   a different value, set it on that service and re-run `run.sh` first.
#
# Win rule (from the real dashboard event stream):
#   defender-win = an `attacker-blocked` event fired BEFORE the attacker
#                  completed a main objective (plant-marker-success or
#                  smb-download-success) -- the block actually cut it short.
#   attacker-win = the attacker completed a main objective, or ran out the
#                  clock, without being blocked in time. A coin-flipped
#                  `block-evaded` counts here: the block didn't take.
set -uo pipefail
cd "$(dirname "$0")"

DASH="http://127.0.0.1:8080"
N="${1:-8}"
DELAY_MS="${2:-3000}"
export MAX_TURNS="${MAX_TURNS:-12}"
export MIN_TURNS_BEFORE_CONCLUDING="${MIN_TURNS_BEFORE_CONCLUDING:-6}"
ATTACKER_MODEL="${ATTACKER_MODEL:-qwen2.5:7b-instruct}"
DEFENDER_MODEL="${DEFENDER_MODEL:-qwen2.5:3b-instruct}"

att=0; def=0
for i in $(seq 1 "$N"); do
  ./reset.sh >/dev/null 2>&1
  sleep 3
  curl -sS -X POST -H 'Content-Type: application/json' -d "{\"delay_ms\": $DELAY_MS}" "$DASH/control" >/dev/null

  DEFENDER_MODEL="$DEFENDER_MODEL" python3 brain/defender_agent.py >/dev/null 2>&1 &
  DPID=$!
  ATTACKER_MODEL="$ATTACKER_MODEL" python3 brain/attacker_agent.py >/dev/null 2>&1
  curl -sS -X POST -H 'Content-Type: application/json' -d '{"attacker_finished": true}' "$DASH/control" >/dev/null 2>&1
  for _ in $(seq 1 15); do kill -0 "$DPID" 2>/dev/null || break; sleep 1; done
  kill "$DPID" 2>/dev/null

  verdict=$(curl -sS "$DASH/events" | python3 -c '
import sys, json
ev = json.load(sys.stdin).get("events", [])
def idx(step):
    for n, e in enumerate(ev):
        if e.get("step_id") == step: return n
    return None
blocked   = idx("attacker-blocked")
objective = min([x for x in (idx("plant-marker-success"), idx("smb-download-success")) if x is not None], default=None)
if blocked is not None and (objective is None or blocked < objective):
    print("defender")
elif objective is not None:
    print("attacker")
elif blocked is not None:
    print("defender")
else:
    print("attacker")
')
  if [ "$verdict" = "defender" ]; then def=$((def+1)); else att=$((att+1)); fi
  echo "run $i: $verdict   (attacker=$att defender=$def)"
done
echo "=== TOTAL over $N runs @ ${DELAY_MS}ms pace: attacker=$att  defender=$def ==="
