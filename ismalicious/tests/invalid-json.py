# fixtures: [ismalicious_api]
# assertions: {fixtures: {ismalicious_api: {query: "invalid-json.invalid"}}}

import json
import os
import shutil
import subprocess
from pathlib import Path

pipeline = (
    'ismalicious::check query="invalid-json.invalid", '
    'api_credential=env("ISMALICIOUS_TEST_CREDENTIAL"), '
    + "base_url="
    + json.dumps(os.environ["ISMALICIOUS_TEST_URL"])
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
    env={**os.environ, "ISMALICIOUS_TEST_CREDENTIAL": "synthetic-test-credential"},
)
diagnostic = result.stdout + result.stderr
assert result.returncode != 0, result
assert b"\n{\n" not in diagnostic, diagnostic
assert b"invalid json" in diagnostic.lower(), diagnostic
assert b"synthetic-test-credential" not in diagnostic, diagnostic
print("Invalid JSON: failed without emitting a report")
