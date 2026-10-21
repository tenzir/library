# timeout: 60

# Reject incomplete envelopes even without an outer strict operator.
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

executor = Executor.from_env(os.environ)
cases = {
    "missing-next": ({"more": True}, None),
    "empty-next": ({"more": True, "next": ""}, None),
    "null-next": ({"more": True, "next": None}, None),
    "objects-without-cursor": ({"more": True, "objects": [{"type": "indicator"}]}, None),
    "empty-date-header": ({"more": True, "objects": [{"type": "indicator"}]}, ""),
    "empty-page-with-date": ({"more": True}, "2026-10-01T00:00:00Z"),
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        envelope, date = cases[self.path.split("?", 1)[0].strip("/")]
        body = json.dumps(envelope).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/taxii+json;version=2.1")
        self.send_header("Content-Length", str(len(body)))
        if date is not None:
            self.send_header("X-TAXII-Date-Added-Last", date)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
try:
    for name in cases:
        result = executor.run(
            f'stix::taxii::fetch "http://127.0.0.1:{server.server_port}/{name}"'
        )
        assert result.returncode != 0, (name, result.stdout.decode())
        assert b"without a usable continuation" in result.stderr, result.stderr.decode()
        assert not result.stdout, result.stdout.decode()
        print(f"{name}: incomplete walk rejected")
finally:
    server.shutdown()
    server.server_close()
    worker.join()
