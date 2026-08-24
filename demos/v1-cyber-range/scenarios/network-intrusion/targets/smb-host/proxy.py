"""
A tiny, independent TCP proxy in front of smbd -- same pattern as
scenarios/web-exploit/proxy/server.py: log every real connection
independently of the application itself, rather than depending on Samba's
own internal logging (tried first; modern Samba's split rpc_host worker
architecture didn't surface a reliable "connect to service" log line at
any debug level tried, including the purpose-built vfs_full_audit module --
this sidesteps that entirely and is fully within our own control, same
"real, not staged" bar, just implemented differently). Listens on the real
SMB port (445) and forwards raw bytes to smbd, which listens internally on
PORT_INTERNAL (see smb.conf's `smb ports`).
"""
import json
import os
import socket
import threading
import time

LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "445"))
UPSTREAM_PORT = int(os.environ.get("UPSTREAM_PORT", "4450"))
LOG_PATH = os.environ.get("LOG_PATH", "/logs/smb-connections.jsonl")
LOG_LOCK = threading.Lock()


def log_event(**fields):
    fields.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    line = json.dumps(fields)
    print(f"[smb-proxy] {line}", flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with LOG_LOCK, open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError as e:
        print(f"[warn] could not write log: {e}", flush=True)


def pipe(src, dst, counter):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            counter[0] += len(data)
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def handle(client, addr):
    try:
        upstream = socket.create_connection(("127.0.0.1", UPSTREAM_PORT), timeout=5)
    except OSError as e:
        log_event(event="proxy_error", source=addr[0], error=str(e))
        client.close()
        return

    sent = [0]
    recv = [0]
    t1 = threading.Thread(target=pipe, args=(client, upstream, sent))
    t2 = threading.Thread(target=pipe, args=(upstream, client, recv))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    client.close()
    upstream.close()
    log_event(event="smb_connection", source=addr[0], bytes_sent=sent[0], bytes_received=recv[0])


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", LISTEN_PORT))
    srv.listen(5)
    log_event(event="startup", port=LISTEN_PORT)
    while True:
        client, addr = srv.accept()
        threading.Thread(target=handle, args=(client, addr), daemon=True).start()


if __name__ == "__main__":
    main()
