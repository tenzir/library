"""Synthetic TruePattern TAXII 2.1 collection that records requests."""

import base64
import json
import shutil
import tempfile
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

COLLECTION = "91a9eb95-e096-4774-80fb-6db78007a346"
OBJECTS = f"/taxii/collections/{COLLECTION}/objects/"
# Collections whose second page is malformed or fails, as broken walks deliver.
MALFORMED = "/taxii/collections/malformed/objects/"
FAILING = "/taxii/collections/failing/objects/"
RECOVERING = "/taxii/collections/recovering/objects/"
EMPTY = "/taxii/collections/empty/objects/"
FAILING_EMPTY = "/taxii/collections/failing-empty/objects/"
UNAUTHORIZED = "/taxii/collections/unauthorized/objects/"
INCOMPLETE = "/taxii/collections/incomplete/objects/"
INCOMPLETE_LATER = "/taxii/collections/incomplete-later/objects/"
CREDENTIAL = base64.b64encode(b"synthetic-user:synthetic-password").decode()
PAGE_SIZE = 3
# The objects in the order the collection added them, with `modified` as the
# time added. The collection serves every rule version as a separate object.
COLLECTION_OBJECTS = json.loads(
    (Path(__file__).parents[1] / "tests" / "inputs" / "objects.json").read_text()
)


@dataclass(frozen=True)
class RequestAssertions:
    match_type: str = "indicator"
    added_after: str | None = None
    pages: int = 3
    collection: str = COLLECTION
    retries: int = 0


@fixture(name="truepattern_taxii", assertions=RequestAssertions)
def truepattern_taxii() -> FixtureHandle:
    requests = []
    retry_attempts = 0

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal retry_attempts
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params, dict(self.headers)))
            if self.headers.get("Authorization") != f"Basic {CREDENTIAL}":
                return self.reply(401, {"title": "Unauthorized"})
            if url.path == UNAUTHORIZED:
                return self.reply(401, {"title": "Unauthorized"})
            if url.path == EMPTY:
                return self.reply(200, {"more": False})
            if url.path == INCOMPLETE:
                return self.reply(200, {"more": True})
            if url.path == INCOMPLETE_LATER:
                if "next" not in params:
                    return self.reply(200, {"more": True, "next": "1", "objects": COLLECTION_OBJECTS[1:2]})
                return self.reply(200, {"more": True, "next": ""})
            if url.path == FAILING_EMPTY:
                if "next" not in params:
                    return self.reply(200, {"more": True, "next": "1"})
                return self.reply(200, b'{"more": false, "objects": [broken]}')
            if url.path == RECOVERING and "next" in params and retry_attempts < 2:
                retry_attempts += 1
                return self.reply(503, {"title": "Service unavailable"})
            if url.path in (MALFORMED, FAILING):
                if "next" not in params:
                    return self.reply(200, {"more": True, "next": "1", "objects": COLLECTION_OBJECTS[1:2]})
                if url.path == MALFORMED:
                    return self.reply(200, b'{"more": false, "objects": [broken]}')
                return self.reply(500, {"title": "Internal server error"})
            if url.path not in (OBJECTS, RECOVERING):
                return self.reply(404, {"title": "Not found"})
            types = params.get("match[type]", [""])[0].split(",")
            added_after = params.get("added_after", [""])[0]
            selected = [
                x
                for x in COLLECTION_OBJECTS
                if x["type"] in types and x["modified"] > added_after
            ]
            offset = int(params.get("next", ["0"])[0])
            end = offset + PAGE_SIZE
            page = {"more": end < len(selected)}
            if page["more"]:
                page["next"] = str(end)
            if selected[offset:end]:
                page["objects"] = selected[offset:end]
            self.reply(200, page)

        def reply(self, status, body):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/taxii+json;version=2.1")
            self.send_header("Content-Length", str(len(data)))
            if status in (500, 503):
                self.send_header("Retry-After", "0")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: RequestAssertions | dict, **kwargs):
        # Suites share the server, so every test only checks its own requests.
        recorded = list(requests)
        requests.clear()
        if isinstance(assertions, dict):
            if not assertions:
                return
            assertions = RequestAssertions(**assertions)
        assert len(recorded) == assertions.pages + assertions.retries, recorded
        expected = {"limit": ["2000"], "match[type]": [assertions.match_type]}
        if assertions.added_after:
            expected["added_after"] = [assertions.added_after]
        for index, (path, params, headers) in enumerate(recorded):
            assert path == f"/taxii/collections/{assertions.collection}/objects/", path
            # The recovering collection retries the second page twice.
            page_index = max(1, index - assertions.retries) if index else 0
            token = {"next": [str(page_index * PAGE_SIZE)]} if page_index else {}
            assert params == expected | token, params
            assert headers["Authorization"] == f"Basic {CREDENTIAL}", headers

    # A directory for rule files that outlives single tests of a suite.
    directory = tempfile.mkdtemp(prefix="truepattern-")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown():
        server.shutdown()
        server.server_close()
        worker.join()
        shutil.rmtree(directory, ignore_errors=True)

    return FixtureHandle(
        env={
            "TRUEPATTERN_TEST_URL": f"http://127.0.0.1:{server.server_port}",
            "TRUEPATTERN_TEST_CREDENTIAL": CREDENTIAL,
            "TRUEPATTERN_TEST_DIR": directory,
        },
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
