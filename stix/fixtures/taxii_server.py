"""Synthetic TAXII 2.1 server that serves a collection in two pages."""

import json
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

OBJECTS = "/api-root/collections/indicators/objects/"
TOKENS = ["page/2+=", "page/3+="]
INDICATORS = [
    json.loads(line)
    for line in (Path(__file__).parents[1] / "tests" / "inputs" / "indicators.ndjson")
    .read_text()
    .splitlines()
]
IDENTITY = {
    "type": "identity",
    "spec_version": "2.1",
    "id": "identity--f431f809-377b-45e0-aa1c-6a4751cae5ff",
    "created": "2024-01-01T00:00:00.000Z",
    "modified": "2024-01-01T00:00:00.000Z",
    "name": "Synthetic TAXII provider",
    "identity_class": "organization",
}
# TAXII 2.1 omits `objects` from an empty page, which filtered requests yield.
PAGES = {
    None: {"more": True, "next": TOKENS[0], "objects": [IDENTITY, *INDICATORS[:3]]},
    TOKENS[0]: {"more": True, "next": TOKENS[1]},
    TOKENS[1]: {"more": False, "objects": INDICATORS[3:]},
}


@dataclass(frozen=True)
class RequestAssertions:
    added_after: str | None = None
    authorization: str = "Basic c3ludGhldGljOnRlc3Q="


@fixture(name="taxii_server", assertions=RequestAssertions)
def taxii_server() -> FixtureHandle:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params, dict(self.headers)))
            page = PAGES.get(params.get("next", [None])[0])
            status = 200 if url.path == OBJECTS and page else 404
            body = json.dumps(page, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/taxii+json;version=2.1")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            # Split the body inside a multi-byte character, as network chunks do.
            split = body.find("…".encode()) + 1 or len(body)
            self.wfile.write(body[:split])
            self.wfile.flush()
            time.sleep(0.1)
            self.wfile.write(body[split:])

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions, **kwargs):
        assert len(requests) == len(PAGES), requests
        filters = {"added_after": [assertions.added_after]} if assertions.added_after else {}
        for (path, params, headers), token in zip(requests, PAGES):
            assert path == OBJECTS, path
            assert params == (filters | {"next": [token]} if token else filters), params
            assert headers["Accept"] == "application/taxii+json;version=2.1", headers
            assert headers["Authorization"] == assertions.authorization, headers

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown():
        server.shutdown()
        server.server_close()
        worker.join()

    return FixtureHandle(
        env={"TAXII_TEST_URL": f"http://127.0.0.1:{server.server_port}/api-root/collections/indicators/objects/"},
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
