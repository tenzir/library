"""Synthetic TAXII 2.1 server that serves a collection in two pages."""

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

OBJECTS = "/api-root/collections/indicators/objects/"
TOKEN = "page/2+="
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
PAGES = {
    None: {"more": True, "next": TOKEN, "objects": [IDENTITY, *INDICATORS[:3]]},
    TOKEN: {"more": False, "objects": INDICATORS[3:]},
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
            body = json.dumps(page).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/taxii+json;version=2.1")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions, **kwargs):
        assert len(requests) == 2, requests
        filters = {"added_after": [assertions.added_after]} if assertions.added_after else {}
        for (path, params, headers), token in zip(requests, [None, TOKEN]):
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
