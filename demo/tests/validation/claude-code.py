"""Keep diagnostics from sibling packages independent of the checkout path."""

from pathlib import Path
import sys

from tenzir_test import Executor

result = Executor().run(r"""
from_file f"{env("TENZIR_DEMO_CAPTURE_DIR")}/claude-code.zst" {
  decompress_zstd
  demo::agents::read
}
anthropic::claude_code::ocsf::normalize include_content=true
ocsf = this
ocsf = ocsf_cast(ocsf_derive(ocsf))
assert ocsf != null
summarize class_uid=ocsf.class_uid, events=count()
sort class_uid
""")
root = str(Path(__file__).resolve().parents[3]).encode() + b"/"
sys.stdout.buffer.write(result.stderr.replace(root, b""))
sys.stdout.buffer.write(result.stdout)
result.check_returncode()
