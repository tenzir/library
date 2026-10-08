"""Synthetic IsMalicious API that records requests for assertions."""

import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

INPUTS = Path(__file__).parents[1] / "tests" / "inputs"


@dataclass(frozen=True)
class RequestAssertions:
    query: str = "192.0.2.1"
    credential: str = "synthetic-test-credential"


@fixture(name="ismalicious_api", assertions=RequestAssertions)
def ismalicious_api() -> FixtureHandle:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params, self.headers.get("X-API-KEY")))
            query = params.get("query", [""])[0]
            name = "context-only" if query.startswith("https://") else "malicious-evidence"
            body = (INPUTS / f"{name}.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions, **kwargs):
        assert len(requests) == 1, requests
        path, params, credential = requests[0]
        assert path == "/check", path
        assert params == {"query": [assertions.query], "enrichment": ["standard"]}, params
        assert credential == assertions.credential, credential

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown():
        server.shutdown()
        server.server_close()
        worker.join()

    return FixtureHandle(
        env={"ISMALICIOUS_TEST_URL": f"http://127.0.0.1:{server.server_port}"},
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
