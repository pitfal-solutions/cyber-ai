FROM debian:bookworm-slim
# Real Samba (4.17.x -- current Debian, not version-matched to a specific
# RCE CVE; see specs/network-intrusion.md for why SambaCry (CVE-2017-7494)
# was checked and rejected: it needs Samba 4.4/4.5/4.6.x, not available via
# apt, and a from-source build of that era was judged too fragile to
# rehearse reliably). Real, common misconfiguration instead: guest/
# anonymous access to a share holding a sensitive file -- T1021.002.
RUN apt-get update && \
    apt-get install -y --no-install-recommends samba python3 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /srv/public /var/log/samba /run/samba

COPY smb.conf /etc/samba/smb.conf
COPY confidential-layoffs.txt /srv/public/confidential-layoffs.txt
COPY proxy.py /app/proxy.py
RUN chmod -R a+rX /srv/public

EXPOSE 445
# smbd listens internally on 4450 (see smb.conf); proxy.py fronts the real
# 445 and is this container's main process, logging every real connection
# independently -- see proxy.py's docstring.
CMD sh -c "smbd --foreground --no-process-group --debug-stdout & exec python3 /app/proxy.py"
