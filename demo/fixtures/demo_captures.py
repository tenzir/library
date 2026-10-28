"""Public capture inputs shared by the demo normalization validation suite."""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import tempfile

from tenzir_test import FixtureHandle, fixture


CAPTURES = {
    "zeek": "M57/zeek-all.log.zst",
    "suricata": "M57/suricata.json.zst",
    "openssh": "openssh/syslog.log.zst",
    "windows": "windows/events.ndjson.zst",
    "claude-code": "claude-code/otel.json.zst",
    "codex": "codex/otel.json.zst",
}


@fixture(name="demo_captures")
def demo_captures() -> FixtureHandle:
    supplied = os.environ.get("TENZIR_DEMO_CAPTURE_DIR")
    if supplied:
        directory = Path(supplied).resolve()
        for name in CAPTURES:
            if not (directory / f"{name}.zst").is_file():
                raise FileNotFoundError(directory / f"{name}.zst")
        return FixtureHandle(env={"TENZIR_DEMO_CAPTURE_DIR": str(directory)})

    temporary = tempfile.TemporaryDirectory(prefix="demo-captures-")
    directory = Path(temporary.name)

    def download(item: tuple[str, str]) -> None:
        name, path = item
        subprocess.run(
            [
                "curl", "--fail", "--silent", "--show-error", "--location",
                "--retry", "2", "--max-time", "120",
                "--output", str(directory / f"{name}.zst"),
                f"https://datasets.tenzir.tools/{path}",
            ],
            check=True,
        )

    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(download, CAPTURES.items()))
    except BaseException:
        temporary.cleanup()
        raise
    return FixtureHandle(
        env={"TENZIR_DEMO_CAPTURE_DIR": str(directory)},
        teardown=temporary.cleanup,
    )
