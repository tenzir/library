"""Keep sibling-package diagnostics independent of the checkout path."""

from pathlib import Path
import sys

from tenzir_test import Executor

result = Executor().run(r"""
from_file env("TENZIR_INPUT") {
  read_json
}
@name = "otel.log"
anthropic::claude_code::ocsf::normalize include_content=true
this = ocsf_cast(ocsf_derive(this))
assert class_uid == 1001
tenzir::detect::agent::hidden_unicode
this = ocsf_cast(ocsf_derive(this))
assert class_uid == 2004
assert start_time == 2026-09-07T21:19:49.166Z
assert evidences[0].ai_agent.name != null
summarize findings=count()
assert findings == 1
""")
root = str(Path(__file__).resolve().parents[5]).encode() + b"/"
sys.stdout.buffer.write(result.stderr.replace(root, b""))
sys.stdout.buffer.write(result.stdout)
result.check_returncode()
