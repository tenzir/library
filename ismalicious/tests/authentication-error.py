# fixtures: [ismalicious_api]
# assertions: {fixtures: {ismalicious_api: {query: "192.0.2.1", credential: "invalid-credential"}}}

import json
import os
import shutil
import subprocess
from pathlib import Path

pipeline = (
    'ismalicious::check query="192.0.2.1", api_credential=env("ISMALICIOUS_TEST_CREDENTIAL"), '
    + "base_url="
    + json.dumps(os.environ["ISMALICIOUS_TEST_URL"])
    + ""
)
result = subprocess.run(
    [
        os.environ.get("TENZIR_BINARY") or shutil.which("tenzir"),
        "--bare-mode",
        "--package-dirs=" + str(Path(__file__).resolve().parents[1]),
        pipeline,
    ],
    capture_output=True,
    timeout=10,
    env={**os.environ, "ISMALICIOUS_TEST_CREDENTIAL": "invalid-credential"},
)
assert result.returncode != 0, result
diagnostic = result.stdout + result.stderr
assert b"\n{\n" not in diagnostic, diagnostic
assert b"401" in diagnostic.lower(), result.stderr
assert b"invalid-credential" not in diagnostic, diagnostic
print("HTTP 401: failed without emitting a report")
