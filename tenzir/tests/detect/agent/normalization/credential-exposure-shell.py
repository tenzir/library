"""Keep sibling-package diagnostics independent of the checkout path."""

from pathlib import Path
import sys

from tenzir_test import Executor

result = Executor().run(r"""
// Synthetic regression case, not a captured OTLP record.
from {
  time: 2026-09-10T12:00:00Z,
  observed_time: 2026-09-10T12:00:00Z,
  trace_id: null,
  span_id: null,
  severity_number: 0,
  severity_text: null,
  flags: 1,
  resource: {attributes: {"service.name": "claude-code"}},
  scope: {name: "com.anthropic.claude_code.events"},
  receiver: {transport: "grpc"},
  body: null,
  attributes: {
    "event.name": "tool_result",
    tool_name: "Bash",
    tool_use_id: "synthetic-background-success",
    success: "true",
    tool_input: "{\"command\":\"echo AKIAIOSFODNN7EXAMPLE\",\"run_in_background\":true}",
  },
}
@name = "otel.log"
anthropic::claude_code::ocsf::normalize include_content=true
this = ocsf_cast(ocsf_derive(this))
assert class_uid == 0
tenzir::detect::agent::credential_exposure
this = ocsf_cast(ocsf_derive(this))
assert class_uid == 2004
assert start_time == 2026-09-10T12:00:00Z
assert not print_json(this).search("AKIAIOSFODNN7EXAMPLE")
summarize findings=count()
assert findings == 1
""")
root = str(Path(__file__).resolve().parents[5]).encode() + b"/"
sys.stdout.buffer.write(result.stderr.replace(root, b""))
sys.stdout.buffer.write(result.stdout)
result.check_returncode()
