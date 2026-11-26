"""Mock HarfangLab Manager that serves the pull exports.

Each pull route serves the files in `tests/inputs/pull/<connector>/` in name
order, one file per request, gzip-encoded like the real Manager. After the
last file, the queue is empty and the route answers with an empty body, as
the Manager does. Requests without the expected token get a 401.
"""

import gzip
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tenzir_test import fixture

TOKEN = "test-token"
INPUTS = Path(__file__).resolve().parent.parent / "tests" / "inputs" / "pull"


def _load_queues():
    queues = {}
    for connector in ("splunk", "elastic"):
        directory = INPUTS / connector
        files = sorted(directory.glob("*.json")) if directory.is_dir() else []
        queues[f"/api/data/connectors/{connector}/pull/"] = [
            path.read_bytes() for path in files
        ]
    return queues


def _handler(queues, lock):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.headers.get("Authorization") != f"Token {TOKEN}":
                self._send(401, b'{"detail":"Invalid token."}')
                return
            if self.path not in queues:
                self._send(404, b'{"detail":"Not found."}')
                return
            with lock:
                queue = queues[self.path]
                body = queue.pop(0) if queue else b""
            self._send(200, body)

        def _send(self, status, body):
            payload = gzip.compress(body) if body else b""
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            if payload:
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            try:
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                # The test pipeline stopped reading, for example after `head`.
                pass

        def log_message(self, *args):
            pass

    return Handler


@fixture()
def harfanglab_manager():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), _handler(_load_queues(), threading.Lock())
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield {
            "HARFANGLAB_URL": f"http://{host}:{port}",
            "HARFANGLAB_TOKEN": TOKEN,
        }
    finally:
        server.shutdown()
        server.server_close()
