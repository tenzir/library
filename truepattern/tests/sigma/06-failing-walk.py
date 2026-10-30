# A walk that fails on an HTTP error leaves the rule file untouched, which
# 07-rule-file-unchanged verifies. The test checks the failure instead of a
# diagnostic snapshot, because diagnostics name the absolute paths of operators
# in other packages and the retry policy of the HTTP client.

import os
import re

result = Executor.from_env(os.environ).run(
    """
truepattern::feed credential=env("TRUEPATTERN_TEST_CREDENTIAL"),
  collection="failing",
  base_url=env("TRUEPATTERN_TEST_URL")
truepattern::sigma::update_rules path=f"{env("TRUEPATTERN_TEST_DIR")}/sigma.yaml"
"""
)
print("failed:", result.returncode != 0)
http_error = re.search(rb"HTTP error (status )?500", result.stderr)
print("reason:", "HTTP error 500" if http_error else result.stderr.decode())
