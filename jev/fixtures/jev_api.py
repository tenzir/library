"""Deterministic System One responses and assertions on captured HTTP requests.

The fixture provides JEV_API_URL and temporary Tenzir configuration with dummy
secrets. Tests declare expected requests through assertions.fixtures.jev_api.
Responses are test data, not model predictions.
"""

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import time
from typing import Any

from tenzir_test import FixtureHandle, current_options, fixture


@dataclass(frozen=True)
class JevApiOptions:
    secrets: bool = True
    response_delay: float = 0


@dataclass(frozen=True)
class JevApiAssertions:
    max_concurrent_requests: int | None = None
    batch_sizes: list[int] | None = None
    paths: list[str] | None = None
    authorization: str | None = "Bearer default-dummy"
    model: str = "typesafe-ai/jev"
    states: list[str] | None = None
    questions: list[dict[str, Any]] | None = None
    question_ids: list[str] | None = None


def _answer(key: str, question: dict[str, Any]) -> dict[str, Any]:
    kind = question["type"]
    if kind == "noul":
        return {"type": kind, "noul": min(int(key) / 1000, 1.0) if key.isdecimal() else 0.99}
    if kind == "choice":
        choices = list(question["criteria"])
        return {
            "type": kind,
            "choice": choices[0],
            "probabilities": {
                choice: (1.0 if len(choices) == 1 else 0.75) if index == 0
                else 0.25 / (len(choices) - 1)
                for index, choice in enumerate(choices)
            },
            "confidence": 0.75,
        }
    if kind == "score":
        criteria = question["criteria"]
        return {
            "type": kind,
            "score": 0.75 * (len(criteria) - 1),
            "legend": {str(index): label for index, label in enumerate(criteria)},
            "confidence": 0.75,
        }
    raise ValueError(f"unsupported question type: {kind}")


@fixture(name="jev_api", options=JevApiOptions, assertions=JevApiAssertions)
def jev_api() -> FixtureHandle:
    options = current_options("jev_api")
    directory = tempfile.TemporaryDirectory(prefix="jev-api-")
    config = Path(directory.name) / "tenzir.yaml"
    config_text = "tenzir:\n  legacy-secret-model: true\n"
    if options.secrets:
        config_text += """  secrets:
    VERCEL_AI_GATEWAY_API_KEY: default-dummy
    JEV_REVIEW_DUMMY: override-dummy
"""
    config.write_text(config_text, encoding="utf-8")
    requests = []
    lock = threading.Lock()
    active_requests = 0
    max_concurrent_requests = 0

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            nonlocal active_requests, max_concurrent_requests
            with lock:
                active_requests += 1
                max_concurrent_requests = max(max_concurrent_requests, active_requests)
            response = None
            try:
                response = self.respond()
            finally:
                # A client can start its next request as soon as this write ends.
                # Account for completion before another handler increments the count.
                with lock:
                    try:
                        if response is not None:
                            self.wfile.write(response)
                    finally:
                        active_requests -= 1

        def respond(self):
            if self.path != "/v1/systemone":
                self.send_error(404)
                return
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            with lock:
                requests.append({
                    "path": self.path,
                    "authorization": self.headers.get("Authorization"),
                    "content_type": self.headers.get("Content-Type"),
                    "body": body,
                })
            if options.response_delay:
                time.sleep(options.response_delay)
            try:
                answers = {key: _answer(key, question) for key, question in body["questions"].items()}
                response_body = {
                    "answers": answers,
                    "usage": {"input_tokens": 10, "output_tokens": 1},
                }
            except (KeyError, TypeError, ValueError, IndexError) as error:
                self.send_error(400, str(error))
                return
            response = json.dumps(response_body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            return response

        def log_message(self, *args):
            pass

    def assert_test(*, assertions: JevApiAssertions, **_: Any) -> None:
        with lock:
            observed = list(requests)
            observed_concurrency = max_concurrent_requests
        if assertions.max_concurrent_requests is not None:
            assert observed_concurrency == assertions.max_concurrent_requests, (
                f"maximum concurrent requests: {observed_concurrency}"
            )
        sizes = sorted(len(request["body"]["questions"]) for request in observed)
        if assertions.batch_sizes is not None:
            assert sizes == sorted(assertions.batch_sizes), f"request sizes: {sizes}"
        if assertions.paths is not None:
            assert sorted(request["path"] for request in observed) == sorted(assertions.paths)
        for request in observed:
            assert request["authorization"] == assertions.authorization, request
            assert request["content_type"] == "application/json", request
            assert request["body"]["model"] == assertions.model, request
        if assertions.states is not None:
            states = sorted(request["body"]["state"] for request in observed)
            assert states == sorted(assertions.states), f"request states: {states}"
        if assertions.questions is not None:
            questions = [request["body"]["questions"] for request in observed]
            actual = sorted(json.dumps(value, sort_keys=True) for value in questions)
            expected = sorted(json.dumps(value, sort_keys=True) for value in assertions.questions)
            assert actual == expected, questions
        if assertions.question_ids is not None:
            ids = sorted(key for request in observed for key in request["body"]["questions"])
            assert ids == sorted(assertions.question_ids), f"question ids: {ids}"

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def teardown() -> None:
        server.shutdown()
        server.server_close()
        worker.join()
        directory.cleanup()

    return FixtureHandle(
        env={
            "JEV_API_URL": f"http://127.0.0.1:{server.server_port}/v1/systemone",
            "TENZIR_CONFIG": str(config),
        },
        teardown=teardown,
        hooks={"assert_test": assert_test},
    )
