#!/usr/bin/env bash
# One-time (idempotent) machine setup for the cyber range: everything in
# demos/README.md's "One-time setup" sections, in one script, so a new
# laptop can go from zero to `./run.sh <scenario>` without hand-copying
# commands. Safe to re-run -- every step checks current state first.
#
# Installs: Colima + Docker CLI/Compose/Buildx (via Homebrew), Ollama
# (native, not containerized -- see specs/architecture.md's "Local LLM
# runtime": Docker Desktop on macOS can't pass the Metal GPU through to a
# container), and the two default agentic-scenario models. Also
# pre-builds/pre-pulls every scenario's Docker images, per CLAUDE.md's
# "Runs with zero internet at showtime" quality bar.
#
# Usage:
#   ./setup.sh
#   ATTACKER_MODEL=llama3.1:8b-instruct-q4_K_M DEFENDER_MODEL=llama3.2:3b ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

ATTACKER_MODEL="${ATTACKER_MODEL:-qwen2.5:7b-instruct}"
DEFENDER_MODEL="${DEFENDER_MODEL:-qwen2.5:3b-instruct}"

log() { echo; echo "== $1 =="; }

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This repo's agentic/network-intrusion scenarios rely on macOS-specific" >&2
  echo "Ollama/Metal GPU passthrough (see specs/architecture.md). Setup has only" >&2
  echo "been written/tested for macOS." >&2
  exit 1
fi

log "Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install it yourself first (https://brew.sh), then re-run this script:" >&2
  echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"' >&2
  exit 1
fi
echo "found: $(brew --version | head -1)"

log "Docker runtime (Colima) + CLI + Compose + Buildx"
for formula in colima docker docker-compose docker-buildx; do
  if brew list "$formula" >/dev/null 2>&1; then
    echo "already installed: $formula"
  else
    brew install "$formula"
  fi
done

log "Ollama"
if brew list ollama >/dev/null 2>&1; then
  echo "already installed: ollama"
else
  brew install ollama
fi

log "Starting Colima (this may take a minute on first boot)"
if colima status >/dev/null 2>&1; then
  echo "already running"
else
  colima start --cpu 4 --memory 8 --disk 60 --vm-type=vz --mount-type=virtiofs
fi
docker info >/dev/null
docker compose version >/dev/null
echo "docker + docker compose OK"

log "Starting Ollama"
if curl -sS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
  echo "already running"
else
  brew services start ollama
  for i in $(seq 1 15); do
    curl -sS http://127.0.0.1:11434/api/version >/dev/null 2>&1 && break
    sleep 1
  done
  curl -sS http://127.0.0.1:11434/api/version >/dev/null 2>&1 || {
    echo "Ollama didn't come up within 15s -- check 'brew services list'." >&2
    exit 1
  }
fi

log "Pulling agentic-scenario models ($ATTACKER_MODEL, $DEFENDER_MODEL)"
ollama pull "$ATTACKER_MODEL"
ollama pull "$DEFENDER_MODEL"

log "Pre-building/pulling scenario images (offline-at-showtime prep)"
for compose in scenarios/*/docker-compose.yml; do
  scenario_dir="$(dirname "$compose")"
  scenario="$(basename "$scenario_dir")"
  echo "-- ${scenario} --"
  docker compose --project-directory . -f core/docker-compose.core.yml -f "$compose" build
  docker compose --project-directory . -f core/docker-compose.core.yml -f "$compose" pull --ignore-pull-failures
done

log "Done"
cat <<EOF
Everything's installed and running. To run a scenario:

  cd $(pwd)
  ./run.sh web-exploit        # or: agentic | network-intrusion

Model pair for the agentic scenarios came from defaults, not a real
on-machine bench -- run ./scenarios/agentic/bench-models.sh on the actual
demo laptop before treating that pick as final (working agreement #7).
EOF
