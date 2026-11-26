"""Mock HarfangLab Manager that serves the pull exports and the IOC API.

Each pull route serves the files in `tests/inputs/pull/<connector>/` in name
order, one file per request, gzip-encoded like the real Manager. After the
last file, the queue is empty and the route answers with an empty body, as
the Manager does.

The threat intelligence routes keep IOC sources and IOC rules in memory, so
that the tests of one suite see each other's changes:

- `GET IOCSource/` and `GET IOCRule/` filter by the query parameters that
  the operators use and page with `limit` and `offset`. Pages hold at most
  `MAX_LIMIT` results, so that small tests exercise the pagination. Like the
  real Manager, `next` is a path without scheme and host.
- `value` matches exactly but case-insensitively, as on the Manager. Values
  are stored as sent, also IP addresses in a non-canonical form.
- `POST IOCRule/` answers 201 with the rule, as the Manager 6.2.28 did for a
  single JSON rule, and 400 for a type and value that already exist in the
  source, compared case-insensitively, or an invalid IP address.
  `global_state: disabled` also disables the rule.
- `PATCH IOCRule/<id>/` updates a rule, `DELETE IOCRule/<id>/` answers 204
  without a body.
- `POST IOCRule/update/` changes the state of the rules in `rule_ids` and
  ignores unknown ids. How the Manager treats unknown ids is not known.
- `DELETE IOCSource/<id>/items/` deletes the rules in `ids` and answers 200
  without a body, or 400 if one of them doesn't exist.
- `fields` limits the listed fields to a comma-separated list.

Sources with these names fail on purpose, so that tests can cover the error
paths:

- `tenzir-fault-listing`: `GET IOCRule/` answers 403.
- `tenzir-fault-truncated`: `GET IOCRule/` answers with the first page only,
  as if the Manager ignored `offset`.
- `tenzir-fault-bulk`: `POST IOCRule/update/` and
  `DELETE IOCSource/<id>/items/` answer 400.
- `tenzir-fault-empty`: `POST IOCRule/update/` answers 200 without a body.

The mock routes help the tests:

- `GET /mock/requests` returns the number of API requests per method since
  the previous call and resets the counter, so that tests can show how many
  requests a run sent.
- `GET /mock/writes` returns the write requests in the order of their arrival
  since the previous call, with the rule ids left out, and resets the list.
- `POST /mock/seed` adds the rules `{type, value}` in `rules` to the source
  `source`, which it creates if needed, with the `global_state`, `enabled`,
  `rule_confidence`, and `comment` of the request. Tests use it to set up
  rules that the operator didn't create, for example blocking rules as the
  CSV import leaves them.

Requests without the expected token get a 401.
"""

import gzip
import ipaddress
import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

from tenzir_test import fixture

TOKEN = "test-token"
INPUTS = Path(__file__).resolve().parent.parent / "tests" / "inputs" / "pull"
TI = "/api/data/threat_intelligence"
MAX_LIMIT = 1000
TIMESTAMP = "2026-01-01T00:00:00Z"
STATES = {"alert", "backend_alert", "block", "disabled", "quarantine"}
TYPES = {
    "domain_name",
    "filename",
    "filepath",
    "hash",
    "ip_both",
    "ip_dst",
    "ip_src",
    "url",
}
SOURCE_FIELDS = {
    "name",
    "description",
    "enabled",
    "global_state",
    "endpoint_detection",
    "block_on_agent",
    "quarantine_on_agent",
    "rule_level_default",
    "rule_confidence_default",
}
RULE_FIELDS = {
    "description",
    "comment",
    "enabled",
    "global_state",
    "hl_status",
    "rule_confidence",
    "rule_level_override",
    "endpoint_detection",
    "block_on_agent",
    "quarantine_on_agent",
}


def _load_queues():
    queues = {}
    for connector in ("splunk", "elastic"):
        directory = INPUTS / connector
        files = sorted(directory.glob("*.json")) if directory.is_dir() else []
        queues[f"/api/data/connectors/{connector}/pull/"] = [
            path.read_bytes() for path in files
        ]
    return queues


class Store:
    """In-memory IOC sources and rules with deterministic ids."""

    def __init__(self):
        self.lock = threading.Lock()
        self.requests = {}
        self.sources = []
        self.rules = {}
        self.writes = []
        # A source that the tests must leave alone.
        self.add_source({"name": "unrelated-source", "global_state": "block"})

    def add_source(self, data):
        source = {
            # Derive the id from the name, so that the ids don't depend on the
            # order in which the tests create sources.
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"source/{data['name']}")),
            "name": data["name"],
            "description": "",
            "enabled": True,
            "global_state": "alert",
            "endpoint_detection": True,
            "block_on_agent": False,
            "quarantine_on_agent": False,
            "rule_level_default": "high",
            "rule_confidence_default": "moderate",
            "provided_by_hlab": False,
            "creation_date": TIMESTAMP,
            "last_update": TIMESTAMP,
        }
        source.update({k: v for k, v in data.items() if k in SOURCE_FIELDS})
        self.sources.append(source)
        return source

    def source_named(self, name):
        return next((s for s in self.sources if s["name"] == name), None)

    def source(self, source_id):
        return next((s for s in self.sources if s["id"] == source_id), None)

    def rule(self, rule_id):
        return self.rules.get(rule_id)

    def add_rule(self, rule):
        self.rules[rule["id"]] = rule

    def apply(self, rule, data):
        rule.update({k: v for k, v in data.items() if k in RULE_FIELDS})
        if rule["global_state"] == "disabled":
            rule["enabled"] = False
        source = self.source(rule["source_id"])
        rule["effective_state"] = rule["global_state"]
        rule["rule_effective_level"] = (
            rule["rule_level_override"] or source["rule_level_default"]
        )
        rule["rule_effective_confidence"] = (
            rule["rule_confidence"] or source["rule_confidence_default"]
        )
        rule["last_update"] = TIMESTAMP


def _page(path, query, items):
    limit = min(int(query.get("limit", [MAX_LIMIT])[0]), MAX_LIMIT)
    offset = int(query.get("offset", ["0"])[0])

    def link(start):
        params = {k: v[0] for k, v in query.items()}
        params.update(limit=limit, offset=start)
        return f"{path}?{urlencode(sorted(params.items()))}"

    end = offset + limit
    return {
        "count": len(items),
        "next": link(end) if end < len(items) else None,
        "previous": link(max(offset - limit, 0)) if offset > 0 else None,
        "results": [_select(item, query) for item in items[offset:end]],
    }


def _select(item, query):
    if "fields" not in query:
        return item
    fields = query["fields"][0].split(",")
    return {k: v for k, v in item.items() if k in fields}


def _handler(queues, store):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            if url.path == "/mock/requests":
                with store.lock:
                    counts, store.requests = store.requests, {}
                self._json(200, counts)
                return
            if url.path == "/mock/writes":
                with store.lock:
                    writes, store.writes = store.writes, []
                self._json(200, {"writes": writes})
                return
            if not self._authorized():
                return
            query = parse_qs(url.query)
            if url.path in queues:
                with store.lock:
                    queue = queues[url.path]
                    body = queue.pop(0) if queue else b""
                self._send(200, body)
            elif url.path == f"{TI}/IOCSource/":
                with store.lock:
                    items = [
                        s
                        for s in store.sources
                        if "name" not in query or s["name"] == query["name"][0]
                    ]
                    self._json(200, _page(url.path, query, items))
            elif url.path == f"{TI}/IOCRule/":
                with store.lock:
                    fault = self._fault(query.get("source_id", [None])[0])
                    if fault == "listing":
                        self._json(403, {"detail": "Permission denied."})
                        return
                    items = [
                        r for r in store.rules.values() if self._matches(r, query)
                    ]
                    page = _page(url.path, query, items)
                    if fault == "truncated":
                        page["next"] = None
                    self._json(200, page)
            else:
                with store.lock:
                    found = self._rule_from_path() or self._source_from_path()
                    if found is None:
                        self._json(404, {"detail": "Not found."})
                    else:
                        self._json(200, found)

        def do_POST(self):
            path = urlsplit(self.path).path
            if path == "/mock/seed":
                with store.lock:
                    self._seed(self._body())
                return
            if not self._authorized():
                return
            data = self._body()
            with store.lock:
                self._log_write()
                if path == f"{TI}/IOCSource/":
                    if not data.get("name"):
                        self._json(400, {"name": ["This field is required."]})
                        return
                    self._json(201, store.add_source(data))
                elif path == f"{TI}/IOCRule/":
                    self._create_rule(data)
                elif path == f"{TI}/IOCRule/update/":
                    self._bulk_update(data)
                else:
                    self._json(404, {"detail": "Not found."})

        def do_PATCH(self):
            if not self._authorized():
                return
            data = self._body()
            with store.lock:
                self._log_write()
                rule = self._rule_from_path()
                if rule is None:
                    self._json(404, {"detail": "Not found."})
                    return
                if data.get("global_state", "alert") not in STATES:
                    self._json(400, {"global_state": ["Not a valid choice."]})
                    return
                store.apply(rule, data)
                self._json(200, rule)

        def do_DELETE(self):
            if not self._authorized():
                return
            path = urlsplit(self.path).path
            if path.startswith(f"{TI}/IOCSource/") and path.endswith("/items/"):
                source_id = path[len(f"{TI}/IOCSource/") : -len("/items/")]
                ids = self._body().get("ids", [])
                with store.lock:
                    self._log_write()
                    if store.source(source_id) is None:
                        self._json(404, {"detail": "Not found."})
                        return
                    if self._fault(source_id) == "bulk":
                        self._json(400, {"status": "Injected failure."})
                        return
                    rules = [store.rule(i) for i in ids]
                    missing = [r for r in rules if r is None]
                    if missing or any(r["source_id"] != source_id for r in rules):
                        self._json(
                            400, {"status": "Some specified ids do not exist"}
                        )
                        return
                    for rule_id in ids:
                        del store.rules[rule_id]
                    self._send(200, b"")
                return
            with store.lock:
                self._log_write()
                rule = self._rule_from_path()
                if rule is None:
                    self._json(404, {"detail": "Not found."})
                    return
                del store.rules[rule["id"]]
                self._send(204, b"")

        def _bulk_update(self, data):
            if data.get("global_state", "alert") not in STATES:
                self._json(400, {"status": "Not a valid choice."})
                return
            changes = {
                k: v for k, v in data.items() if k in {"global_state", "enabled"}
            }
            rules = [store.rule(i) for i in data.get("rule_ids", [])]
            rules = [r for r in rules if r is not None]
            faults = {self._fault(r["source_id"]) for r in rules}
            if "bulk" in faults:
                self._json(400, {"status": "Injected failure."})
                return
            for rule in rules:
                store.apply(rule, changes)
            if "empty" in faults:
                self._send(200, b"")
                return
            self._json(200, {"status": "rules updated"})

        def _create_rule(self, data):
            source = store.source(data.get("source_id"))
            if source is None:
                self._json(400, {"source_id": ["Invalid source."]})
                return
            if data.get("type") not in TYPES or not data.get("value"):
                self._json(400, {"type": ["Not a valid choice."]})
                return
            if data.get("global_state", "alert") not in STATES:
                self._json(400, {"global_state": ["Not a valid choice."]})
                return
            if data["type"].startswith("ip_"):
                try:
                    ipaddress.ip_address(data["value"])
                except ValueError:
                    self._json(
                        400, {"value": ["Enter a valid IPv4 or IPv6 address."]}
                    )
                    return
            # Derive the id from the rule, so that concurrent requests give
            # the same ids in every run.
            key = f"{source['id']}/{data['type']}/{data['value'].lower()}"
            rule_id = str(uuid.uuid5(uuid.NAMESPACE_URL, key))
            if store.rule(rule_id) is not None:
                self._json(
                    400,
                    {
                        "__all__": [
                            "Ioc rule with this Type, Value and Source"
                            " already exists."
                        ]
                    },
                )
                return
            rule = {
                "id": rule_id,
                "source_id": source["id"],
                "source": source["id"],
                "type": data["type"],
                "value": data["value"],
                "name": "",
                "description": None,
                "comment": None,
                "enabled": True,
                "global_state": source["global_state"],
                "hl_status": "stable",
                "rule_level": None,
                "rule_level_override": None,
                "rule_confidence": None,
                "endpoint_detection": True,
                "block_on_agent": False,
                "quarantine_on_agent": False,
                "creation_date": TIMESTAMP,
            }
            store.add_rule(rule)
            store.apply(rule, data)
            self._json(201, rule)

        def _seed(self, data):
            source = store.source_named(data["source"]) or store.add_source(
                {"name": data["source"]}
            )
            for item in data.get("rules", []):
                key = f"{source['id']}/{item['type']}/{item['value'].lower()}"
                rule = {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, key)),
                    "source_id": source["id"],
                    "source": source["id"],
                    "type": item["type"],
                    "value": item["value"],
                    "name": "",
                    "description": None,
                    "comment": None,
                    "enabled": True,
                    "global_state": source["global_state"],
                    "hl_status": "stable",
                    "rule_level": None,
                    "rule_level_override": None,
                    "rule_confidence": None,
                    "endpoint_detection": True,
                    "block_on_agent": False,
                    "quarantine_on_agent": False,
                    "creation_date": TIMESTAMP,
                }
                store.add_rule(rule)
                store.apply(
                    rule,
                    {
                        k: v
                        for k, v in data.items()
                        if k in {"global_state", "enabled", "rule_confidence", "comment"}
                    },
                )
            self._json(200, {"source_id": source["id"], "rules": len(data["rules"])})

        def _fault(self, source_id):
            source = store.source(source_id)
            name = source["name"] if source else ""
            prefix = "tenzir-fault-"
            return name[len(prefix) :] if name.startswith(prefix) else None

        def _log_write(self):
            path = urlsplit(self.path).path[len(TI) :]
            rule = self._rule_from_path()
            if rule is not None:
                path = path.replace(rule["id"], "<id>")
            source = self._source_from_path_prefix(path)
            if source is not None:
                path = path.replace(source["id"], "<id>")
            store.writes.append(f"{self.command} {path}")

        def _source_from_path_prefix(self, path):
            prefix = "/IOCSource/"
            if not path.startswith(prefix):
                return None
            return store.source(path[len(prefix) :].split("/")[0])

        def _matches(self, rule, query):
            for key in ("source_id", "type", "global_state"):
                if key in query and rule[key] != query[key][0]:
                    return False
            if "value" in query:
                return rule["value"].lower() == query["value"][0].lower()
            return True

        def _rule_from_path(self):
            path = urlsplit(self.path).path
            prefix = f"{TI}/IOCRule/"
            if not path.startswith(prefix) or not path.endswith("/"):
                return None
            return store.rule(path[len(prefix) : -1])

        def _source_from_path(self):
            path = urlsplit(self.path).path
            prefix = f"{TI}/IOCSource/"
            if not path.startswith(prefix) or not path.endswith("/"):
                return None
            return store.source(path[len(prefix) : -1])

        def _authorized(self):
            with store.lock:
                method = self.command
                store.requests[method] = store.requests.get(method, 0) + 1
            if self.headers.get("Authorization") == f"Token {TOKEN}":
                return True
            self._json(401, {"detail": "Invalid token."})
            return False

        def _body(self):
            length = int(self.headers.get("Content-Length") or 0)
            if length == 0:
                return {}
            try:
                return json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                return {}

        def _json(self, status, value):
            self._send(status, json.dumps(value).encode())

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


def serve():
    return ThreadingHTTPServer(("127.0.0.1", 0), _handler(_load_queues(), Store()))


@fixture()
def harfanglab_manager():
    server = serve()
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
