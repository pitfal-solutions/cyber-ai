FROM python:3.12-alpine
WORKDIR /app
COPY tool-api/server.py .
COPY legal-map.json /legal-map.json
# Drop this scenario's legal content into the shared volume so the
# scenario-agnostic core dashboard can read it -- see specs/architecture.md,
# same one-time-copy pattern as scenarios/web-exploit/attacker/Dockerfile.
CMD sh -c "cp /legal-map.json /data/legal-map.json && python3 server.py"
