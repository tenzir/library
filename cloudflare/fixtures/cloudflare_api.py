"""Synthetic Cloudflare API that serves account audit logs in two pages."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tenzir_test import FixtureHandle, fixture

ACCOUNT = "023e105f4ecef8ad9ca31a8372d0c353"
PATH = f"/client/v4/accounts/{ACCOUNT}/logs/audit"
TOKEN = "synthetic-api-token"
CURSOR = "AAd160kJUzHn+/page=2"
RECORDS = json.loads(
    (Path(__file__).parents[1] / "tests" / "inputs" / "audit_logs_api.json").read_text()
)
# The API returns a cursor while more records may follow, and no cursor on an
# empty page.
PAGES = {
    None: {"result": RECORDS[:4], "result_info": {"count": 4, "cursor": CURSOR}},
    CURSOR: {"result": RECORDS[4:], "result_info": {"count": len(RECORDS) - 4}},
}


@fixture(name="cloudflare_api")
def cloudflare_api() -> FixtureHandle:
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            params = parse_qs(url.query)
            requests.append((url.path, params, dict(self.headers)))
            page = PAGES.get(params.get("cursor", [None])[0])
            authorized = self.headers.get("Authorization") == f"Bearer {TOKEN}"
            if url.path != PATH or page is None:
                status, body = 404, {"success": False, "errors": [{"code": 7003, "message": "Not found"}]}
            elif not authorized:
                status, body = 403, {"success": False, "errors": [{"code": 10000, "message": "Authentication error"}]}
            else:
                status, body = 200, {"success": True, "errors": [], "messages": [], **page}
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    def assert_test(**kwargs):
        assert len(requests) == len(PAGES), requests
        for (path, params, headers), cursor in zip(requests, PAGES):
            assert path == PATH, path
            assert headers["Authorization"] == f"Bearer {TOKEN}", headers
            assert params["direction"] == ["asc"], params
            assert params["limit"] == ["1000"], params
            assert params["since"] == ["2026-12-17T00:00:00Z"], params
            assert params["before"] == ["2026-12-18T00:00:00Z"], params
            assert params.get("cursor") == ([cursor] if cursor else None), params

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown():
        server.shutdown()
        server.server_close()
        worker.join()

    return FixtureHandle(
        env={
            "CLOUDFLARE_API_URL": f"http://127.0.0.1:{server.server_port}/client/v4",
            "CLOUDFLARE_ACCOUNT_ID": ACCOUNT,
            "CLOUDFLARE_API_TOKEN": TOKEN,
        },
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
