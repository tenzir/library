"""Synthetic TAXII 2.1 server that pages by date added instead of `next`.

TAXII 2.1 lets servers omit the `next` token. Clients then page with
`added_after` set to the `X-TAXII-Date-Added-Last` header of the previous
response.
"""

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

OBJECTS_PATH = "/api-root/collections/indicators/objects/"
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
# Objects in the order the server added them, with microsecond timestamps.
ENTRIES = [
    (f"2026-09-01T10:00:0{i}.000000Z", obj)
    for i, obj in enumerate([IDENTITY, *INDICATORS])
]
LIMIT = 3


@dataclass(frozen=True)
class RequestAssertions:
    match_type: str | None = None


@fixture(name="taxii_date_added_server", assertions=RequestAssertions)
def taxii_date_added_server() -> FixtureHandle:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params))
            if url.path != OBJECTS_PATH or "next" in params:
                self.send_response(404)
                self.end_headers()
                return
            # The fixed-width timestamps compare like the times they encode.
            after = params.get("added_after", [""])[0]
            entries = [entry for entry in ENTRIES if entry[0] > after]
            page = entries[:LIMIT]
            body = json.dumps(
                {"more": len(entries) > LIMIT, "objects": [obj for _, obj in page]}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/taxii+json;version=2.1")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-TAXII-Date-Added-First", page[0][0])
            self.send_header("X-TAXII-Date-Added-Last", page[-1][0])
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions, **kwargs):
        cursors = [None, ENTRIES[LIMIT - 1][0], ENTRIES[2 * LIMIT - 1][0]]
        assert len(requests) == len(cursors), requests
        for (path, params), cursor in zip(requests, cursors):
            assert path == OBJECTS_PATH, path
            expected = {"match[type]": [assertions.match_type]} if assertions.match_type else {}
            if cursor:
                expected["added_after"] = [cursor]
            assert params == expected, params

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown():
        server.shutdown()
        server.server_close()
        worker.join()

    return FixtureHandle(
        env={"TAXII_DATE_ADDED_URL": f"http://127.0.0.1:{server.server_port}{OBJECTS_PATH}"},
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
