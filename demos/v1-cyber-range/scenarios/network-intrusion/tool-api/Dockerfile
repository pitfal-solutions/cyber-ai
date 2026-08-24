FROM debian:bookworm-slim
# Real, industry-standard tools -- not custom HTTP-client tricks. Curated
# subset (not the full kalilinux/kali-rolling image) for build speed and
# reliability, per specs/network-intrusion.md: nmap (recon), hydra
# (credential brute-forcing), smbclient (real SMB protocol client). The
# vsftpd backdoor interaction is hand-written (server.py) since it's a
# specific documented protocol trigger, not something a general tool does.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 nmap hydra smbclient iproute2 openssh-client sshpass && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY tool-api/server.py .
COPY tool-api/wordlist.txt .
COPY legal-map.json /legal-map.json
# Drop this scenario's legal content into the shared volume so the
# scenario-agnostic core dashboard can read it -- see specs/architecture.md,
# same pattern as scenarios/agentic/tool-api/Dockerfile.
CMD sh -c "cp /legal-map.json /data/legal-map.json && python3 server.py"
