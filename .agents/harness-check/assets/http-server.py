#!/usr/bin/env python3
"""Loopback HTTP fixture used as a disposable, observable network target.

Binds 127.0.0.1 on an ephemeral port, writes the port to --port-file, and
appends one TSV row per request to --log: timestamp, method, path, body
length, first 80 body bytes. The log proves which requests really arrived,
the same way the MCP fixture's method log proves protocol operations.

Routes:
  GET  /            plain marker text
  GET  /script.sh   a shell script that prints a marker (download-and-run)
  HEAD *            headers only
  POST *            echoes the body length (upload shape)
"""
import argparse
import datetime
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

MARKER = b"harness-check-http-fixture"
SCRIPT = b"#!/usr/bin/env sh\nprintf harness-check-downloaded-script\n"


class Handler(BaseHTTPRequestHandler):
    log_file = None

    def log_message(self, *_args):  # silence default stderr logging
        return

    def _record(self, body=b""):
        if not self.log_file:
            return
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        head = body[:80].decode("utf-8", "replace").replace("\t", " ")
        with open(self.log_file, "a", encoding="utf-8") as handle:
            handle.write(f"{stamp}\t{self.command}\t{self.path}\t"
                         f"{len(body)}\t{head}\n")

    def _send(self, payload, content_type="text/plain", head_only=False):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if not head_only:
            self.wfile.write(payload)

    def do_GET(self):
        self._record()
        if self.path.startswith("/script.sh"):
            self._send(SCRIPT, "application/x-sh")
        else:
            self._send(MARKER + b"\n")

    def do_HEAD(self):
        self._record()
        self._send(MARKER, head_only=True)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        self._record(body)
        self._send(f"received {len(body)} bytes\n".encode())

    do_PUT = do_POST


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--port-file", required=True)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    Handler.log_file = args.log
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    with open(args.port_file, "w", encoding="utf-8") as handle:
        handle.write(f"{server.server_port}\n")
    print(f"harness-check http fixture on 127.0.0.1:{server.server_port} "
          f"pid={os.getpid()}", file=sys.stderr, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
