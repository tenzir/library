from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import shlex
import subprocess
import threading


package_dir = Path(__file__).resolve().parents[1]
requests = []


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode()
        requests.append(json.loads(body))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

url = f"http://127.0.0.1:{server.server_port}/webhook"
tenzir = shlex.split(os.environ.get("TENZIR_BINARY", "tenzir"))
pipelines = [
    f'from {{event: "login", severity: "high", empty: null}}\nslack::send "{url}"',
    f'from {{name: "Suspicious Login", severity: "high"}}\n'
    f'slack::alert "{url}", title=name, severity=severity, thread_ts="123.456"',
]

try:
    for pipeline in pipelines:
        subprocess.run(
            [*tenzir, "--neo", f"--package-dirs={package_dir}", pipeline],
            check=True,
            text=True,
            capture_output=True,
            timeout=10,
        )
finally:
    server.shutdown()

print(json.dumps(requests, indent=2, sort_keys=True))
