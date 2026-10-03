"""Local synthetic responses, with request checks at the HTTP boundary."""

import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture


@dataclass(frozen=True)
class RequestAssertions:
    count: int = 1
    query: str = "192.0.2.1"
    credential: str = "synthetic-test-credential"


@fixture(name="ismalicious_api", assertions=RequestAssertions)
def ismalicious_api() -> FixtureHandle:
    requests = []
    inputs = Path(__file__).parents[1] / "tests" / "inputs"

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params, self.headers.get("X-API-KEY")))
            indicator = params.get("query", [""])[0]
            if self.headers.get("X-API-KEY") != "synthetic-test-credential":
                status, body = 401, b'{"error":"synthetic authentication failure"}'
            elif indicator == "rate-limit.invalid":
                status, body = 429, b'{"error":"synthetic rate limit"}'
            elif indicator == "redirect.invalid":
                status, body = 302, b'{"redirect":true}'
            elif indicator == "invalid-json.invalid":
                status, body = 200, b"not JSON"
            elif indicator == "non-object.invalid":
                status, body = 200, b"[1,2]"
            else:
                if indicator == "slow.invalid":
                    time.sleep(0.5)
                name = (
                    "minimal-optional-fields"
                    if indicator == "minimal.invalid"
                    else "unknown-hash"
                    if indicator == "0" * 64
                    else "context-only"
                    if indicator.startswith("https://")
                    else "malicious-evidence"
                )
                status, body = 200, (inputs / f"{name}.json").read_bytes()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                if indicator == "redirect.invalid":
                    self.send_header(
                        "Location", f"http://127.0.0.1:{server.server_port}/redirected"
                    )
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except BrokenPipeError:
                pass

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions, **kwargs):
        assert len(requests) == assertions.count, requests
        if not requests:
            return
        path, params, credential = requests[0]
        assert path == "/check", path
        assert params == {"query": [assertions.query], "enrichment": ["standard"]}, (
            params
        )
        assert credential == assertions.credential

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
