"""Synthetic TAXII 2.1 server that pages by date added instead of `next`.

TAXII 2.1 lets servers omit the `next` token or leave it empty. Clients then
page with `added_after` set to the `X-TAXII-Date-Added-Last` header of the
previous response.
"""

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

COLLECTIONS = "/api-root/collections/"
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
# Objects in the order the server added them. The timestamps differ only in
# microseconds, so a cursor truncated to seconds would lose objects.
ENTRIES = [
    (f"2026-09-01T10:00:00.{i + 1:06d}Z", obj)
    for i, obj in enumerate([IDENTITY, *INDICATORS])
]
DEFAULT_LIMIT = 3


@dataclass(frozen=True)
class RequestAssertions:
    collection: str = "indicators"
    added_after: str | None = None
    limit: int | None = None
    match_type: str | None = None


@fixture(name="taxii_date_added_server", assertions=RequestAssertions)
def taxii_date_added_server() -> FixtureHandle:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params))
            collection = url.path.removeprefix(COLLECTIONS).removesuffix("/objects/")
            if collection not in ("indicators", "quirky") or "next" in params:
                self.send_response(404)
                self.end_headers()
                return
            limit = int(params.get("limit", [DEFAULT_LIMIT])[0])
            # Fixed-width timestamps compare like the times they encode.
            after = params.get("added_after", [""])[0]
            entries = [entry for entry in ENTRIES if entry[0] > after]
            page = entries[:limit]
            envelope = {"more": len(entries) > limit, "objects": [obj for _, obj in page]}
            first, last = "X-TAXII-Date-Added-First", "X-TAXII-Date-Added-Last"
            if collection == "quirky":
                # An empty `next` token, lowercase headers, and a custom
                # property that must not affect pagination.
                envelope |= {"next": "", "next_url": f"{COLLECTIONS}indicators/objects/"}
                first, last = first.lower(), last.lower()
            body = json.dumps(envelope).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/taxii+json;version=2.1")
            self.send_header("Content-Length", str(len(body)))
            self.send_header(first, page[0][0])
            self.send_header(last, page[-1][0])
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions, **kwargs):
        limit = assertions.limit or DEFAULT_LIMIT
        start = sum(
            1 for date, _ in ENTRIES if assertions.added_after and date <= assertions.added_after
        )
        # Every page but the last ends with the cursor of the next request.
        pages = list(range(start, len(ENTRIES), limit))
        cursors = [assertions.added_after] + [ENTRIES[i + limit - 1][0] for i in pages[:-1]]
        assert len(requests) == len(cursors), requests
        filters = {}
        if assertions.limit:
            filters["limit"] = [str(assertions.limit)]
        if assertions.match_type:
            filters["match[type]"] = [assertions.match_type]
        for (path, params), cursor in zip(requests, cursors):
            assert path == f"{COLLECTIONS}{assertions.collection}/objects/", path
            assert params == filters | ({"added_after": [cursor]} if cursor else {}), params

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown():
        server.shutdown()
        server.server_close()
        worker.join()

    return FixtureHandle(
        env={"TAXII_DATE_ADDED_URL": f"http://127.0.0.1:{server.server_port}{COLLECTIONS}"},
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
