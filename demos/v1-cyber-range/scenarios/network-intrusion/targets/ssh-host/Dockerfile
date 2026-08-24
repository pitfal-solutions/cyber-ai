FROM debian:bookworm-slim
# A real OpenSSH server with one intentionally weak-password account --
# T1110 (Brute Force) / T1078 (Valid Accounts). Same "real, not simulated"
# bar as every other target in this repo: a genuine sshd, a genuine weak
# credential, genuinely crackable with a real tool (hydra), not a fake
# result. See specs/network-intrusion.md.
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/sshd && \
    useradd -m -s /bin/bash svc-backup && \
    echo 'svc-backup:sunshine1' | chpasswd && \
    # Password auth only -- no key-based login to muddy what's being
    # demonstrated; root login disabled, this is a low-priv service account,
    # matching a realistic "someone reused a weak password for a utility
    # account" fact pattern rather than a root compromise.
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    ssh-keygen -A

EXPOSE 22
# -E writes sshd's own real auth log (including every failed/accepted
# password attempt) directly to the shared volume the detector tails --
# real OpenSSH log format, not a synthetic one.
CMD ["/usr/sbin/sshd", "-D", "-E", "/logs/ssh-auth.log"]
