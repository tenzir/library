# A walk that fails on a malformed page leaves the rule file untouched, which
# 07-rule-file-unchanged verifies. The test checks the failure instead of a
# diagnostic snapshot, because diagnostics name the absolute paths of operators
# in other packages.

import os
from pathlib import Path

# The Python runner does not load packages, so load this one and the STIX
# package that its feed builds on.
package = Path(os.environ["TENZIR_TEST_ROOT"])
os.environ["TENZIR_PACKAGE_DIRS"] = f"{package},{package.parent / 'stix'}"
result = Executor.from_env(os.environ).run(
    """
truepattern::feed credential=env("TRUEPATTERN_TEST_CREDENTIAL"),
  collection="malformed",
  base_url=env("TRUEPATTERN_TEST_URL")
truepattern::sigma::update_rules path=f"{env("TRUEPATTERN_TEST_DIR")}/sigma.yaml"
"""
)
print("failed:", result.returncode != 0)
# Both engines reject the malformed page; only the parser wording differs.
json_errors = (
    b"failed to parse a JSON value",
    b"json parser: failed to parse a value in the JSON document",
)
json_error = any(message in result.stderr for message in json_errors)
print("reason:", "failed to parse a JSON value" if json_error else result.stderr.decode())
