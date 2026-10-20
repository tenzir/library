# timeout: 60

# Keep one Sigma process alive across a successful empty product snapshot.
# A separate control rule proves that post-clear input is still being evaluated.
import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory

package = Path(os.environ["TENZIR_TEST_ROOT"])
# Work around the Python runner's missing package loading (TNZ-1733).
os.environ["TENZIR_PACKAGE_DIRS"] = f"{package},{package.parent / 'stix'}"
executor = Executor.from_env(os.environ)
rule_id = "00000000-0000-4000-8000-000000000001"
control_id = "00000000-0000-4000-8000-000000000002"
rule = f"""title: Synthetic Windows rule
id: {rule_id}
logsource:
  product: windows
detection:
  selection:
    CommandLine: whoami
  condition: selection
"""
with TemporaryDirectory(prefix="truepattern-live-reload-") as directory:
    root = Path(directory)
    target = root / "windows.yaml"
    control = root / "control.yaml"
    target.write_text(rule)
    control.write_text(rule.replace(rule_id, control_id).replace("whoami", "control"))
    pipeline = f'''
from_stdin {{ read_ndjson }}
sigma path=["{target}", "{control}"], refresh_interval=100ms
select phase=evidences[0].data.phase,
       sequence=evidences[0].data.sequence,
       id=finding_info.analytic.uid
to_stdout {{ write_ndjson }}
'''
    output = queue.Queue()
    with (root / "stderr").open("w+") as errors:
        process = subprocess.Popen(
            [*executor.binary, "--bare-mode", "--console-verbosity=warning", pipeline],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
            text=True,
        )

        def read_output():
            for line in process.stdout:
                output.put(json.loads(line))

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()

        def probe(phase):
            # Matching inputs precede a control batch; its final finding is a
            # barrier proving that all preceding input has been processed.
            events = [
                {"CommandLine": command, "phase": phase, "sequence": sequence}
                for command in ("whoami", "control") for sequence in range(100)
            ]
            process.stdin.write("".join(json.dumps(event) + "\n" for event in events))
            process.stdin.flush()
            matches = 0
            deadline = time.monotonic() + 10
            while True:
                finding = output.get(timeout=max(0.01, deadline - time.monotonic()))
                assert finding["phase"] == phase, finding
                if finding["id"] == rule_id:
                    matches += 1
                if finding["id"] == control_id and finding["sequence"] == 99:
                    return matches

        try:
            assert probe("loaded") == 100
            # The last Windows rule moves to Linux. Use the actual package
            # writer rather than clearing the source directly from Python.
            source = root / "objects.ndjson"
            source.write_text(json.dumps({
                "type": "indicator", "id": "indicator--1",
                "modified": "2026-10-02T00:00:00Z", "pattern_type": "sigma",
                "pattern": rule.replace("product: windows", "product: linux"),
            }) + "\n")
            result = executor.run(f'''
from_file "{source}" {{ read_ndjson }}
truepattern::sigma::update_rules path="{target}", product="windows"
''')
            assert result.returncode == 0, result.stderr.decode()
            assert not result.stderr and not result.stdout
            assert target.read_bytes() == b"\n"
            # Allow asynchronous refresh, then require an entire probe batch
            # without obsolete matches. Polling avoids relying on one sleep.
            deadline = time.monotonic() + 10
            while True:
                time.sleep(0.2)
                if probe("cleared") == 0:
                    break
                assert time.monotonic() < deadline, "empty source retained obsolete rules"
            target.write_text(rule)
            deadline = time.monotonic() + 10
            while True:
                time.sleep(0.2)
                if probe("restored") == 100:
                    break
                assert time.monotonic() < deadline, "restored source did not reload"
            process.stdin.close()
            assert process.wait(timeout=10) == 0
            reader.join(timeout=5)
            errors.seek(0)
            assert not errors.read(), "unexpected Sigma diagnostics"
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            reader.join(timeout=5)
    print("one Sigma process: loaded rules match")
    print("empty Windows snapshot: obsolete rules stop matching; control still matches")
    print("restored source: rules match again without restarting Sigma")
