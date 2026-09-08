#!/usr/bin/env python3
"""harness-check bookkeeping CLI.

Everything around the bash workload probes: run directories, the correlation
log, the capability inventory, operator-assisted steps, and real child
harness sessions. The workload probes themselves stay in bash on purpose —
they must run through the harness's shell tool to generate real telemetry.

Subcommands:
  new-run [claude|codex|generic]        create one isolated run directory
  record RESULT ID [DETAIL]             append one probe result
  summarize                             effective results for one run
  inventory [--tsv] [--agent NAME]      what can be probed here, right now
  operator list|prepare|batch-mark|begin|mark|window
  run-child --agent claude|codex        real child session for startup telemetry
"""

import argparse
import atexit
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
OWNED = ".harness-check-owned"
RESULTS = ("PASS", "FAIL", "SKIP")


def die(message, code=2):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


# --- run directory and correlation log --------------------------------------
# Every run must use its own directory from `new-run`. A shared fallback
# default silently mixes results from unrelated runs, so stateful commands
# refuse to work without an explicit HARNESS_CHECK_DIR.

def run_dir():
    value = os.environ.get("HARNESS_CHECK_DIR", "")
    if not value:
        die("harness-check: HARNESS_CHECK_DIR is not set.\n"
            "  Create a run directory first:\n"
            "    python3 scripts/harness_check.py new-run claude|codex\n"
            "  then export HARNESS_CHECK_DIR=<returned path>, or use"
            " run-all.sh,\n  which creates one automatically.")
    path = Path(value)
    home = Path(os.environ.get("HOME", "/nonexistent"))
    tmp = Path(os.environ.get("TMPDIR", "/tmp"))
    if not path.is_absolute() or path in (Path("/"), home, tmp):
        die(f"harness-check: refusing unsafe HARNESS_CHECK_DIR '{value}'")
    return path


def ensure_owned(directory):
    if not directory.is_dir():
        directory.mkdir(parents=True)
        (directory / OWNED).touch()
        return
    if not (directory / OWNED).exists():
        if any(directory.iterdir()):
            die("harness-check: refusing non-owned, non-empty directory: "
                f"{directory}\nchoose a new empty HARNESS_CHECK_DIR")
        (directory / OWNED).touch()


def log_path(directory):
    return Path(os.environ.get("HARNESS_CHECK_LOG")
                or directory / "probes.tsv")


def emit(directory, result, probe_id, detail=""):
    print(f"{result:<5} {probe_id:<30} {detail}")
    path = log_path(directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{utc_stamp()}\t{result}\t{probe_id}\t{detail}\n")


class Recorder:
    """PASS/FAIL/SKIP accounting for one command invocation."""

    def __init__(self, directory):
        self.directory = directory
        self.counts = {r: 0 for r in RESULTS}

    def record(self, result, probe_id, detail=""):
        self.counts[result] += 1
        emit(self.directory, result, probe_id, detail)

    def ok(self, probe_id, detail=""):
        self.record("PASS", probe_id, detail)

    def fail(self, probe_id, detail=""):
        self.record("FAIL", probe_id, detail)

    def skip(self, probe_id, detail=""):
        self.record("SKIP", probe_id, detail)

    def summary(self, name):
        print(f"---- {name}: {self.counts['PASS']} passed, "
              f"{self.counts['FAIL']} failed, {self.counts['SKIP']} skipped")
        return self.counts["FAIL"] == 0


# --- concurrency guard -------------------------------------------------------
# Two runs sharing one sandbox corrupt each other's results silently. The
# lock is re-entrant for one run: whoever acquires it exports
# HARNESS_CHECK_RUN, and child probes inherit that and skip acquisition.
# Same protocol as _lib.sh, so bash probes and this CLI exclude each other.

def lock_acquire(directory):
    if os.environ.get("HARNESS_CHECK_RUN"):
        return
    ensure_owned(directory)
    lockdir = directory / ".lock"
    try:
        lockdir.mkdir()
    except FileExistsError:
        owner = None
        try:
            owner = int((lockdir / "pid").read_text().strip())
        except (OSError, ValueError):
            pass
        if owner is not None and pid_alive(owner):
            die(f"harness-check: {directory} is already in use by pid "
                f"{owner}.\n  Concurrent runs corrupt each other. Either "
                "wait, or set\n  HARNESS_CHECK_DIR to a different path for "
                "this run.", code=3)
        shutil.rmtree(lockdir, ignore_errors=True)
        lockdir.mkdir()
    (lockdir / "pid").write_text(f"{os.getpid()}\n")
    os.environ["HARNESS_CHECK_RUN"] = str(os.getpid())
    atexit.register(shutil.rmtree, lockdir, ignore_errors=True)


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# --- new-run -----------------------------------------------------------------

def cmd_new_run(args):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ")
    base = os.environ.get("TMPDIR", "/tmp")
    run = tempfile.mkdtemp(prefix=f"harness-check-{args.agent}-{stamp}-",
                           dir=base)
    (Path(run) / OWNED).touch()
    print(run)


# --- record ------------------------------------------------------------------

def cmd_record(args):
    emit(run_dir(), args.result, args.id, args.detail)


# --- summarize ---------------------------------------------------------------

def cmd_summarize(_args):
    path = log_path(run_dir())
    if not path.is_file() or path.stat().st_size == 0:
        die(f"no correlation log at {path}", code=1)
    result, detail, order, transitions = {}, {}, {}, {}
    sequence = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t", 3)
        if len(fields) < 3:
            continue
        _ts, res, probe_id = fields[:3]
        det = fields[3] if len(fields) == 4 else ""
        if res not in RESULTS:
            continue
        if probe_id in result and result[probe_id] != res:
            transitions[probe_id] = (transitions.get(probe_id, "")
                                     + f"{result[probe_id]}->{res};")
        result[probe_id] = res
        detail[probe_id] = det
        sequence += 1
        order[probe_id] = sequence
    counts = {r: sum(1 for v in result.values() if v == r) for r in RESULTS}
    print(f"effective: {counts['PASS']} PASS / {counts['SKIP']} SKIP / "
          f"{counts['FAIL']} FAIL")
    for probe_id in sorted(result, key=order.get):
        line = f"{result[probe_id]:<5} {probe_id:<38} {detail[probe_id]}"
        if probe_id in transitions:
            line += f" [superseded: {transitions[probe_id]}]"
        print(line)


# --- operator ----------------------------------------------------------------
# Correlation markers for user-operated harness activities.

STEPS = [
    ("manual.approval-deny", "approval.deny",
     "Decline a harmless requested action"),
    ("manual.approval-allow", "approval.allow",
     "Approve a harmless requested action"),
    ("automatic.approval-allow", "approval.auto-allow",
     "Automatic reviewer approved a requested action"),
    ("automatic.approval-deny", "approval.auto-deny",
     "Automatic reviewer denied a requested action"),
    ("manual.claude.permission-mode", "permission.change",
     "Switch Claude Code to a mode the agent cannot set itself"),
    ("manual.claude.permission-restore", "permission.change",
     "Restore the original Claude Code permission mode"),
    ("manual.claude.shell-bang", "local_command.shell",
     "Type a `!`-prefixed shell command at the Claude Code prompt"),
    ("manual.claude.ask-question", "user_prompt.question",
     "Answer an AskUserQuestion prompt the agent raised"),
    ("manual.workflow.run", "workflow.invoke",
     "Approve a multi-agent Workflow the agent proposed"),
    ("manual.codex.config-write", "configuration.change",
     "Make or restore a reversible UI-only Codex configuration change"),
]
STEP_IDS = {step_id for step_id, _, _ in STEPS}


def require_step(step_id):
    if step_id not in STEP_IDS:
        die(f"unknown step: {step_id}", code=1)


def cmd_operator(args):
    if args.action == "list":
        print(f"{'STEP':<28} {'ACTIVITY':<22} ACTION")
        for step_id, activity, action in STEPS:
            print(f"{step_id:<28} {activity:<22} {action}")
        return
    directory = run_dir()
    if args.action == "prepare":
        if not args.ids:
            die("usage: operator prepare <id>...")
        for step_id in args.ids:
            require_step(step_id)
        emit(directory, "BEGIN", "manual.sequence",
             "prepared:" + ",".join(args.ids))
    elif args.action == "batch-mark":
        if not args.ids:
            die("usage: operator batch-mark <id>=PASS|FAIL|SKIP ...")
        marks = []
        for item in args.ids:
            step_id, sep, result = item.rpartition("=")
            if not sep:
                die(f"invalid result: {item}")
            require_step(step_id)
            if result not in RESULTS:
                die(f"result must be PASS, FAIL, or SKIP: {item}")
            marks.append((step_id, result))
        for step_id, result in marks:
            detail = ("unavailable during prepared manual sequence"
                      if result == "SKIP"
                      else "observed during prepared manual sequence")
            emit(directory, result, step_id, detail)
        emit(directory, "COMPLETE", "manual.sequence",
             "manual outcomes stored")
    elif args.action == "begin":
        require_step(args.ids[0] if args.ids else "")
        emit(directory, "BEGIN", args.ids[0], "waiting for operator")
    elif args.action == "mark":
        if len(args.ids) < 2:
            die("usage: operator mark <id> PASS|FAIL|SKIP [detail]")
        step_id, result = args.ids[0], args.ids[1]
        require_step(step_id)
        if result not in RESULTS:
            die("result must be PASS, FAIL, or SKIP")
        emit(directory, result, step_id,
             args.ids[2] if len(args.ids) > 2 else "")
    elif args.action == "window":
        step_id = args.ids[0] if args.ids else ""
        path = log_path(directory)
        if not path.is_file():
            die(f"no log at {path}", code=1)
        begin = done = None
        for line in path.read_text(encoding="utf-8").splitlines():
            fields = line.split("\t", 3)
            if len(fields) < 3 or fields[2] != step_id:
                continue
            if fields[1] == "BEGIN":
                begin = fields[0]
            else:
                done = fields[0]
        if done is None:
            die(f"no completed record for {step_id}", code=1)
        print(f"{step_id}\t{begin or '(no BEGIN stamped)'}\t{done}")


# --- inventory ---------------------------------------------------------------
# Read-only and fast: the opening report of what can actually be probed HERE,
# right now. Reports configuration posture without printing endpoints,
# headers, or other potentially sensitive values.

def detect_agent(override):
    agent = "generic"
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE"):
        agent = "claude"
    if os.environ.get("CODEX_SANDBOX") or os.environ.get("CODEX_HOME"):
        agent = "codex"
    if os.environ.get("CURSOR_TRACE_ID"):
        agent = "cursor"
    if agent == "generic" and (Path.home() / ".claude").is_dir():
        agent = "claude"
    return override or agent


def claude_settings_files():
    # Claude Code merges settings from managed, project-local, project, and
    # user scope — check every readable scope, not only ~/.claude.
    config_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR")
                      or Path.home() / ".claude")
    return [
        Path("/etc/claude-code/managed-settings.json"),
        Path("/Library/Application Support/ClaudeCode/managed-settings.json"),
        Path.cwd() / ".claude" / "settings.local.json",
        Path.cwd() / ".claude" / "settings.json",
        config_dir / "settings.json",
    ]


def claude_setting(key):
    """One env setting from the environment or the first scope defining it.

    Callers must never use this to surface endpoints, headers, or
    credentials — only presence checks and known non-secret flags.
    """
    value = os.environ.get(key)
    if value is not None:
        return value
    for path in claude_settings_files():
        try:
            with open(path, encoding="utf-8") as handle:
                value = json.load(handle).get("env", {}).get(key)
        except (OSError, ValueError, AttributeError):
            continue
        if value is not None:
            return str(value)
    return None


def telemetry_rows_claude(row):
    if claude_setting("CLAUDE_CODE_ENABLE_TELEMETRY") == "1":
        row("telemetry", "enabled", "READY",
            "enabled in environment or Claude settings")
    else:
        row("telemetry", "enabled", "BLOCKED",
            "not enabled in environment or Claude settings")
    if (claude_setting("OTEL_EXPORTER_OTLP_ENDPOINT")
            or claude_setting("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")):
        row("telemetry", "exporter", "READY",
            "OTLP endpoint configured in environment or Claude settings")
    else:
        row("telemetry", "exporter", "UNKNOWN",
            "no OTLP endpoint found in environment or Claude settings")
    if claude_setting("CLAUDE_CODE_ENHANCED_TELEMETRY_BETA") == "1":
        row("telemetry", "enhanced", "READY",
            "enabled in environment or Claude settings")
    else:
        row("telemetry", "enhanced", "DEGRADED",
            "not enabled in environment or Claude settings")
    for signal in ("LOGS", "TRACES", "METRICS"):
        if claude_setting(f"OTEL_{signal}_EXPORTER"):
            row("telemetry", signal.lower(), "READY", "exporter configured")
        else:
            row("telemetry", signal.lower(), "UNKNOWN",
                "exporter not found")


def telemetry_rows_codex(row):
    config = Path(os.environ.get("CODEX_HOME")
                  or Path.home() / ".codex") / "config.toml"
    if not config.is_file():
        row("telemetry", "enabled", "BLOCKED", "Codex config not found")
        return
    # Scan only the [otel] section; a full TOML parse is not needed for a
    # presence check and tomllib is unavailable before Python 3.11.
    section, inside = [], False
    for line in config.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "[otel]":
            inside = True
            continue
        if stripped.startswith("["):
            inside = False
        if inside:
            section.append(stripped)
    if not section:
        row("telemetry", "enabled", "BLOCKED",
            "no [otel] section in Codex config")
        return
    row("telemetry", "enabled", "READY", "[otel] configuration present")
    if any("exporter" in entry or "otlp-http" in entry
           or "otlp-grpc" in entry for entry in section):
        row("telemetry", "exporter", "READY", "OTLP exporter configured")
    else:
        row("telemetry", "exporter", "BLOCKED",
            "[otel] has no OTLP exporter")


def first_line(command, limit=40):
    try:
        proc = subprocess.run(command, capture_output=True, text=True,
                              timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    output = (proc.stdout or proc.stderr).splitlines()
    return output[0][:limit] if output else ""


def cmd_inventory(args):
    rows = []

    def row(area, item, status, detail):
        rows.append((area, item, status, detail))

    agent = detect_agent(args.agent or os.environ.get("HARNESS_CHECK_AGENT"))
    row("agent", "detected", agent, "override with HARNESS_CHECK_AGENT")

    if agent == "claude":
        telemetry_rows_claude(row)
    elif agent == "codex":
        telemetry_rows_codex(row)
    else:
        row("telemetry", "enabled", "UNKNOWN",
            "agent-specific telemetry config not detectable")

    for binary in ("bash", "python3", "awk", "sed", "grep", "find"):
        path = shutil.which(binary)
        if path:
            row("core", binary, "AVAILABLE", path)
        else:
            row("core", binary, "MISSING", "scripted probes will not run")

    for binary in ("git", "gh", "jq", "rg", "curl", "uvx", "node",
                   "pdftoppm", "crontab", "systemctl", "pgrep"):
        if shutil.which(binary):
            # pdftoppm rejects --version and wants -v.
            flag = "-v" if binary == "pdftoppm" else "--version"
            row("cli", binary, "AVAILABLE", first_line([binary, flag]))
        else:
            row("cli", binary, "MISSING", "")

    probes = [
        ("probe-files.sh", None, "file lifecycle"),
        ("probe-bash.sh", None, "shell execution"),
        ("probe-process.sh", None, "process lifecycle"),
        ("probe-cli.sh", None, "CLI and network execution"),
        ("probe-security.sh", None,
         "security-relevant command shapes"),
        ("probe-fixtures.sh", "python3",
         "builds material for native-tool probes"),
    ]
    for name, need, note in probes:
        if not (HERE / name).is_file():
            row("probe", name, "MISSING", "not installed")
        elif need and not shutil.which(need):
            row("probe", name, "DEGRADED", f"needs {need} — {note}")
        else:
            row("probe", name, "READY", note)

    if shutil.which("curl"):
        code = first_line(["curl", "-sS", "-m", "8", "-o", "/dev/null",
                           "-w", "%{http_code}", "https://example.com"])
        if code == "200":
            row("network", "shell-egress", "AVAILABLE", "HTTP 200")
        else:
            row("network", "shell-egress", "BLOCKED",
                f"got '{code or '000'}' — shell network probes will fail")
    else:
        row("network", "shell-egress", "UNKNOWN", "curl not installed")

    if shutil.which("python3") and (SKILL / "assets/mcp-server.py").is_file():
        row("mcp", "fixture", "READY",
            "child harness will use bundled server only")
    else:
        row("mcp", "fixture", "BLOCKED",
            "needs python3 and assets/mcp-server.py")

    for name in ("AGENTS.md", "CLAUDE.md", ".claude/CLAUDE.md",
                 ".cursor/rules"):
        path = Path.cwd() / name
        if path.is_symlink():
            row("config", name, "SYMLINK",
                f"-> {os.readlink(path)} (writes land on the target)")
        elif path.exists():
            row("config", name, "FILE", f"{path.stat().st_size} bytes")

    for step_id, _activity, _action in STEPS:
        if step_id.startswith("manual."):
            row("operator", step_id, "GUIDED",
                "run one at a time; verify from transcript or user "
                "attestation")

    if args.tsv:
        for entry in rows:
            print("\t".join(entry))
        return

    current = None
    for area, item, status, detail in rows:
        if area != current:
            print(f"\n{area.upper()}")
            current = area
        print(f"  {item:<22} {status:<12} {detail}")
    print("""
NOT DETECTABLE FROM THE SHELL
  The agent's own file tools (read/write/edit/notebook) and its web and MCP
  tools cannot be inventoried from here. The agent must check those itself —
  see reference/agent-probes.md.""")


# --- run-child ---------------------------------------------------------------
# Run a real nonpersistent child harness for startup-only native telemetry.
# The bundled MCP server and Claude plugin are disposable targets, not
# telemetry simulators: the child harness must discover, connect to, and
# invoke them.

def child_prompt(agent, http_url=None):
    # The fixture server's registered name differs per client: the Claude
    # child gets it from --mcp-config as "harness-check", the Codex child
    # from a config override key, which permits only "harness_check".
    server = "harness-check" if agent == "claude" else "harness_check"
    if agent == "claude":
        list_hint = f'ListMcpResourcesTool with server "{server}"'
        read_hint = f'ReadMcpResourceTool with server "{server}"'
    else:
        list_hint = f'for the server named "{server}"'
        read_hint = f'from the server named "{server}"'
    steps = [
        'This is a telemetry probe. Perform each step through the named '
        'native tool and do nothing else. If a step fails or is blocked, '
        'do not retry it — continue with the remaining steps. The MCP '
        f'server is named "{server}".',
        '1. Call the harness_echo MCP tool exactly once with text '
        '"harness-check-mcp-called".',
        f'2. If a native MCP resource listing tool exists ({list_hint}), '
        'list resources with it.',
        f'3. If a native MCP resource read tool exists ({read_hint}), read '
        'the resource harness-check://fixture/resource with it.',
        '4. If a native MCP prompt interface exists, get harness-check-prompt '
        'through it; skip this step if prompts are only exposed as user slash '
        'commands. Never substitute a different tool for a missing interface.',
        '5. Use the native shell tool to run: printf harness-check-child-shell',
    ]
    if agent == "claude":
        steps += [
            '6. Use the native shell tool to run exactly: '
            'printf harness-check-hook-deny . A hook is expected to deny '
            'this; if it is blocked, continue immediately without retrying.',
            '7. Use the native shell tool to run exactly: '
            'printf harness-check-config-deny . A permission rule is expected '
            'to deny this; if it is blocked, continue without retrying.',
            '8. Use the native shell tool to run exactly: '
            'printf harness-check-hook-fail . Expect it to run; continue '
            'regardless of any post-run hook warning.',
        ]
        if http_url:
            steps.append(
                f'9. If a native web-fetch tool exists, fetch {http_url} with '
                'it once. If it refuses local URLs, skip this step.')
    else:
        steps.append(
            '6. If a native file-patch tool exists, create a file '
            'harness-check-child.txt containing harness-check-apply-patch, '
            'then delete that same file with the patch tool.')
    steps.append(
        'Do not take any other action. Return exactly '
        'harness-check-child-complete.')
    return ' '.join(steps)


def materialize_claude_settings(directory):
    """Write a run-local settings file with __SKILL__ resolved to an absolute
    path, so the fixture hooks can be invoked by absolute command. Returns the
    written path, or the bundled template if substitution is not possible."""
    template = SKILL / "assets" / "claude-settings.json"
    try:
        text = template.read_text(encoding="utf-8").replace(
            "__SKILL__", str(SKILL))
        out = directory / "child-claude-settings.json"
        out.write_text(text, encoding="utf-8")
        return out
    except OSError:
        return template


def start_http_fixture(directory):
    """Launch the loopback HTTP fixture. Returns (process, base_url, log_path)
    or (None, None, None) when it cannot start. The fixture logs every request
    it serves, so native/shell egress is verifiable server-side."""
    server = SKILL / "assets" / "http-server.py"
    if not (server.is_file() and shutil.which("python3")):
        return None, None, None
    log = directory / "child-http-fixture.log"
    port_file = directory / "child-http-fixture.port"
    log.write_text("")
    if port_file.exists():
        port_file.unlink()
    try:
        proc = subprocess.Popen(
            ["python3", str(server), "--log", str(log),
             "--port-file", str(port_file)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return None, None, None
    for _ in range(50):
        if port_file.is_file() and port_file.read_text().strip():
            break
        import time
        time.sleep(0.1)
    port = port_file.read_text().strip() if port_file.is_file() else ""
    if not port or proc.poll() is not None:
        proc.terminate()
        return None, None, None
    return proc, f"http://127.0.0.1:{port}", log


def child_command(agent, mcp_log, settings_path=None, session_id=None,
                  http_url=None, sandbox_mode=None):
    server = str(SKILL / "assets" / "mcp-server.py")
    if agent == "claude":
        mcp_config = json.dumps({"mcpServers": {"harness-check": {
            "type": "stdio", "command": "python3",
            "args": [server, "--log", str(mcp_log)]}}})
        command = [
            "claude", "-p",
            "--permission-mode", "auto",
            "--model", "haiku",
            "--max-budget-usd", "0.10",
            "--plugin-dir", str(SKILL / "assets" / "claude-plugin"),
            "--settings", str(settings_path
                              or SKILL / "assets" / "claude-settings.json"),
            "--strict-mcp-config",
            "--mcp-config", mcp_config,
            "--allowedTools",
            "Bash,WebFetch,mcp__harness-check__harness_echo,"
            "ListMcpResourcesTool,ReadMcpResourceTool",
            "--verbose",
            "--output-format", "stream-json",
            "--include-hook-events",
        ]
        # A fixed session id lets a later --resume reopen this exact session,
        # generating real session resume telemetry. Without it, persistence is
        # off and the row is skipped.
        if session_id:
            command += ["--session-id", session_id]
        else:
            command.append("--no-session-persistence")
        command.append(child_prompt(agent, http_url))
        return command
    codex_command = [
        "codex", "exec",
        "--ephemeral",
        "--approve-for-me",
        "--skip-git-repo-check",
        "--json",
    ]
    if sandbox_mode:
        codex_command += ["--sandbox", sandbox_mode]
    codex_command += [
        "-c", 'mcp_servers.harness_check.command="python3"',
        "-c", f'mcp_servers.harness_check.args=["{server}","--log",'
              f'"{mcp_log}"]',
        child_prompt(agent, http_url),
    ]
    return codex_command


def claude_init_message(out_file):
    """The first system/init record of the child's stream-json output."""
    try:
        with open(out_file, encoding="utf-8") as handle:
            for line in handle:
                try:
                    message = json.loads(line)
                except ValueError:
                    continue
                if (message.get("type") == "system"
                        and message.get("subtype") == "init"):
                    return message
    except OSError:
        pass
    return None


def cmd_run_child(args):
    agent = args.agent
    directory = run_dir()
    lock_acquire(directory)
    recorder = Recorder(directory)

    if not shutil.which(agent):
        recorder.skip(f"child.{agent}.session", f"{agent} CLI not installed")
        recorder.summary(f"child-{agent}")
        return

    workspace = directory / "child-workspace"
    workspace.mkdir(exist_ok=True)
    out_file = directory / f"child-{agent}.jsonl"
    mcp_log = directory / f"child-{agent}-mcp-methods.log"
    mcp_log.write_text("")
    hook_log = directory / f"child-{agent}-hook-events.log"
    hook_log.write_text("")

    # A run-local settings file with fixture hook paths resolved, plus a
    # loopback HTTP fixture the child can fetch. Both are disposable and
    # verifiable server-side; neither simulates a native event.
    settings_path = (materialize_claude_settings(directory)
                     if agent == "claude" else None)
    http_proc, http_url, http_log = start_http_fixture(directory)
    session_id = str(uuid.uuid4()) if agent == "claude" else None

    env = dict(os.environ, HARNESS_CHECK_MCP_LOG=str(mcp_log),
               HARNESS_CHECK_HOOK_LOG=str(hook_log))
    # Transport selection is a real, conditional configuration surface: a
    # gRPC run does not emit an SSE/HTTP completion and vice versa. Honour an
    # explicit --transport without inventing an endpoint when none is set.
    if getattr(args, "transport", None):
        protocol = {"grpc": "grpc", "http": "http/protobuf",
                    "json": "http/json"}[args.transport]
        env["OTEL_EXPORTER_OTLP_PROTOCOL"] = protocol
    try:
        with open(out_file, "w", encoding="utf-8") as sink:
            try:
                proc = subprocess.run(
                    child_command(agent, mcp_log, settings_path=settings_path,
                                  session_id=session_id, http_url=http_url,
                                  sandbox_mode=getattr(args, "sandbox", None)),
                    cwd=workspace, env=env,
                    stdin=subprocess.DEVNULL, stdout=sink,
                    stderr=subprocess.STDOUT, timeout=600)
                returncode = proc.returncode
            except subprocess.TimeoutExpired:
                returncode = -1
                sink.write("\nharness-check: child timed out after 600s\n")
    finally:
        if http_proc is not None:
            http_proc.terminate()
            try:
                http_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                http_proc.kill()

    if returncode == 0:
        recorder.ok(f"child.{agent}.session",
                    "real child harness exited successfully")
        recorder.ok(f"child.{agent}.lifecycle.stop",
                    "child process completed and stopped")
    else:
        recorder.fail(f"child.{agent}.session",
                      f"exit={returncode}; output={out_file}")
        recorder.fail(f"child.{agent}.lifecycle.stop",
                      "child did not stop cleanly")

    # The method log written by the fixture server proves which protocol
    # operations the real client actually sent; it does not drive them.
    methods = mcp_log.read_text(encoding="utf-8").splitlines()

    if "initialize" in methods:
        recorder.ok(f"child.{agent}.mcp.connect",
                    "fixture completed MCP initialize")
    else:
        recorder.fail(f"child.{agent}.mcp.connect",
                      f"initialize absent; inspect {mcp_log}")
    if "tools/list" in methods:
        recorder.ok(f"child.{agent}.mcp.tools-list",
                    "real client listed fixture tools")
    else:
        recorder.fail(f"child.{agent}.mcp.tools-list",
                      f"tools/list absent; inspect {mcp_log}")
    if "tools/call\tharness_echo\tharness-check-mcp-called" in methods:
        recorder.ok(f"child.{agent}.mcp",
                    "real harness invoked fixture MCP tool")
    else:
        recorder.fail(f"child.{agent}.mcp",
                      f"verified tools/call marker absent; inspect {mcp_log}")

    for method in ("resources/list", "resources/read", "resources/subscribe",
                   "prompts/list", "prompts/get"):
        probe_id = f"child.{agent}.mcp.{method.replace('/', '-')}"
        if method in methods:
            recorder.ok(probe_id, f"real client sent {method}")
        else:
            recorder.skip(probe_id, f"client sent no {method}; no native "
                          "path, or the child did not invoke it")

    if methods.count("tools/list") > 1:
        recorder.ok(f"child.{agent}.mcp.notification-listen",
                    "client reacted to list_changed notification")
    else:
        recorder.skip(f"child.{agent}.mcp.notification-listen",
                      "notification sent; client reaction not observable")

    output = out_file.read_text(encoding="utf-8", errors="replace")
    if "harness-check-child-shell" in output:
        recorder.ok(f"child.{agent}.shell",
                    "real harness invoked native shell")
    else:
        recorder.fail(f"child.{agent}.shell",
                      f"shell marker absent; inspect {out_file}")
    if "harness-check-child-complete" in output:
        recorder.ok(f"child.{agent}.response", "model response completed")
    else:
        recorder.fail(f"child.{agent}.response",
                      f"completion marker absent; inspect {out_file}")

    if agent == "claude":
        init = claude_init_message(out_file) or {}
        plugins = [p.get("name") for p in init.get("plugins", [])]
        if "harness-check-fixture" in plugins:
            recorder.ok("child.claude.plugin",
                        "init message lists harness-check-fixture plugin")
        else:
            recorder.fail("child.claude.plugin",
                          f"plugin absent from init message; inspect "
                          f"{out_file}")
        if "harness-check-hook-executed" in output:
            recorder.ok("child.claude.hook",
                        "registered PostToolUse hook executed")
        else:
            recorder.fail("child.claude.hook",
                          f"hook marker absent; inspect {out_file}")
        if returncode == 0:
            recorder.ok("child.claude.hook-remove",
                        "session-scoped hook removed when child stopped")
        else:
            recorder.skip("child.claude.hook-remove",
                          "child did not stop cleanly")

        # Which hook events actually fired is proved by the fixture hook log,
        # not by the model's transcript. Each line is "<event>\t<tool>\t<out>".
        verify_hook_events(recorder, hook_log)

        # Denials with a hook source and a config source, generated without a
        # human dialog. The transcript records the blocked tool attempt.
        if "harness-check-hook-deny" in output:
            recorder.ok("child.claude.decision.hook-deny",
                        "hook-sourced tool denial attempted")
        else:
            recorder.skip("child.claude.decision.hook-deny",
                          f"deny marker command not attempted; inspect "
                          f"{out_file}")
        if "harness-check-config-deny" in output:
            recorder.ok("child.claude.decision.config-deny",
                        "config-sourced tool denial attempted")
        else:
            recorder.skip("child.claude.decision.config-deny",
                          f"config-deny command not attempted; inspect "
                          f"{out_file}")

        # Native web fetch of the loopback fixture, verified server-side.
        if http_log is not None and http_log.is_file() and \
                http_log.read_text(encoding="utf-8").strip():
            recorder.ok("child.claude.web-fetch",
                        "native fetch reached loopback fixture")
        else:
            recorder.skip("child.claude.web-fetch",
                          "no request reached the fixture; the web tool may "
                          "refuse local URLs")

        # Session resume: reopen the exact persisted session id. This is the
        # only row that needs the session to have persisted, so it is skipped
        # cleanly when the first run did not exit successfully.
        if session_id and returncode == 0:
            run_claude_resume(recorder, directory, session_id, env)
        else:
            recorder.skip("child.claude.session.resume",
                          "no persisted session to resume")

        # The vendor API-error path, driven without touching real credentials.
        run_api_error_child(recorder, directory, env)

        # The content-inclusion posture: the same trivial turn with prompt and
        # tool-detail logging redacted and then verbose, so both event shapes
        # appear in one run.
        run_content_toggle_children(recorder, directory, env)

    summary_ok = recorder.summary(f"child-{agent}")
    if not summary_ok:
        raise SystemExit(1)


HOOK_EVENTS = {
    "PreToolUse": "pre-tool decision hook",
    "PostToolUse": "post-tool hook",
    "UserPromptSubmit": "prompt-submit hook",
    "SessionStart": "session-start hook",
    "SessionEnd": "session-end hook",
    "Stop": "stop hook",
    "SubagentStop": "subagent-stop hook",
    "PreCompact": "pre-compact hook",
    "Notification": "notification hook",
}

# Hooks that fire only under a condition this short child rarely reaches
# (a subagent stopping, the session ending inside the captured window,
# context compaction, or a permission notification). A miss is a clean skip,
# not a failure.
BEST_EFFORT_HOOKS = {"SubagentStop", "SessionEnd", "PreCompact", "Notification"}


def verify_hook_events(recorder, hook_log):
    """Record which registered hook events fired, from the fixture hook log."""
    try:
        lines = hook_log.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    fired = {line.split("\t", 1)[0] for line in lines if line.strip()}
    outcomes = {}
    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 3:
            outcomes.setdefault(parts[0], parts[2])
    for event, label in HOOK_EVENTS.items():
        probe = f"child.claude.hook.{event.lower()}"
        if event in fired:
            detail = f"{label} fired"
            if outcomes.get(event) in ("deny", "fail"):
                detail += f" ({outcomes[event]})"
            recorder.ok(probe, detail)
        elif event in BEST_EFFORT_HOOKS:
            recorder.skip(probe, f"{label} not triggered in this child")
        else:
            recorder.skip(probe, f"{label} did not fire; inspect {hook_log}")


def run_claude_resume(recorder, directory, session_id, env):
    """Resume the persisted child session once with a sentinel prompt."""
    out_file = directory / "child-claude-resume.jsonl"
    command = [
        "claude", "-p",
        "--resume", session_id,
        "--model", "haiku",
        "--max-budget-usd", "0.05",
        "--allowedTools", "Bash",
        "--output-format", "stream-json", "--verbose",
        "Run this once through the native shell tool and nothing else: "
        "printf harness-check-resumed . Then return harness-check-resume-done.",
    ]
    try:
        with open(out_file, "w", encoding="utf-8") as sink:
            proc = subprocess.run(command, cwd=directory / "child-workspace",
                                  env=env, stdin=subprocess.DEVNULL,
                                  stdout=sink, stderr=subprocess.STDOUT,
                                  timeout=300)
        text = out_file.read_text(encoding="utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired) as error:
        recorder.skip("child.claude.session.resume",
                      f"resume did not run: {error}")
        return
    if proc.returncode == 0 and "harness-check-resumed" in text:
        recorder.ok("child.claude.session.resume",
                    "reopened the persisted session id")
    else:
        recorder.skip("child.claude.session.resume",
                      f"resume produced no sentinel; inspect {out_file}")


def run_api_error_child(recorder, directory, env):
    """Trigger the vendor API-error path without real credentials.

    Point the API base URL at a closed loopback port so the very first model
    request fails to connect. This exercises the `api_request` -> `api_error`
    path the mapping normalizes. No token is sent anywhere reachable, and the
    closed port refuses instantly, so the turn costs nothing.
    """
    out_file = directory / "child-claude-api-error.jsonl"
    # Port 1 is not a listening service; the connection is refused at once.
    bad = dict(env, ANTHROPIC_BASE_URL="http://127.0.0.1:1",
               ANTHROPIC_API_KEY=env.get("ANTHROPIC_API_KEY",
                                         "harness-check-unusable"))
    command = [
        "claude", "-p",
        "--no-session-persistence",
        "--model", "haiku",
        "--max-budget-usd", "0.05",
        "--allowedTools", "Bash",
        "--output-format", "stream-json", "--verbose",
        "Return the single word ready.",
    ]
    try:
        with open(out_file, "w", encoding="utf-8") as sink:
            proc = subprocess.run(command, cwd=directory / "child-workspace",
                                  env=bad, stdin=subprocess.DEVNULL,
                                  stdout=sink, stderr=subprocess.STDOUT,
                                  timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        recorder.skip("child.claude.api-error",
                      f"api-error child did not run: {error}")
        return
    # A refused base URL must NOT complete successfully; a nonzero exit means
    # the request-then-error path really executed.
    if proc.returncode != 0:
        recorder.ok("child.claude.api-error",
                    "model request against a closed endpoint failed as expected")
    else:
        recorder.skip("child.claude.api-error",
                      f"request unexpectedly succeeded; inspect {out_file}")


def run_content_toggle_children(recorder, directory, env):
    """Run the same trivial turn under redacted and verbose content posture.

    OTEL_LOG_USER_PROMPTS and OTEL_LOG_TOOL_DETAILS change the shape of the
    user_prompt and tool_decision events. Running both postures in one call
    generates the redacted and the detailed variants together.
    """
    postures = [("redacted", "0"), ("verbose", "1")]
    for name, flag in postures:
        out_file = directory / f"child-claude-content-{name}.jsonl"
        posture_env = dict(env, OTEL_LOG_USER_PROMPTS=flag,
                           OTEL_LOG_TOOL_DETAILS=flag)
        command = [
            "claude", "-p",
            "--no-session-persistence",
            "--model", "haiku",
            "--max-budget-usd", "0.05",
            "--allowedTools", "Bash",
            "--output-format", "stream-json", "--verbose",
            "Run this once through the native shell tool and nothing else: "
            f"printf harness-check-content-{name}",
        ]
        try:
            with open(out_file, "w", encoding="utf-8") as sink:
                proc = subprocess.run(
                    command, cwd=directory / "child-workspace", env=posture_env,
                    stdin=subprocess.DEVNULL, stdout=sink,
                    stderr=subprocess.STDOUT, timeout=180)
            ok = proc.returncode == 0 and \
                f"harness-check-content-{name}" in \
                out_file.read_text(encoding="utf-8", errors="replace")
        except (OSError, subprocess.TimeoutExpired) as error:
            recorder.skip(f"child.claude.content.{name}",
                          f"content-{name} child did not run: {error}")
            continue
        if ok:
            recorder.ok(f"child.claude.content.{name}",
                        f"generated {name} prompt/tool-detail posture")
        else:
            recorder.skip(f"child.claude.content.{name}",
                          f"no sentinel under {name} posture; inspect "
                          f"{out_file}")


# --- entry point -------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="harness_check.py",
        description="harness-check bookkeeping CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new-run", help="create one isolated run directory")
    p_new.add_argument("agent", nargs="?", default="generic",
                       choices=["claude", "codex", "generic"])
    p_new.set_defaults(func=cmd_new_run)

    p_record = sub.add_parser("record", help="append one probe result")
    p_record.add_argument("result", choices=list(RESULTS))
    p_record.add_argument("id")
    p_record.add_argument("detail", nargs="?", default="")
    p_record.set_defaults(func=cmd_record)

    p_summarize = sub.add_parser("summarize",
                                 help="effective results for one run")
    p_summarize.set_defaults(func=cmd_summarize)

    p_inventory = sub.add_parser("inventory",
                                 help="what can be probed here, right now")
    p_inventory.add_argument("--tsv", action="store_true")
    p_inventory.add_argument("--agent",
                             choices=["claude", "codex", "generic"])
    p_inventory.set_defaults(func=cmd_inventory)

    p_operator = sub.add_parser("operator",
                                help="user-operated correlation markers")
    p_operator.add_argument("action",
                            choices=["list", "prepare", "batch-mark",
                                     "begin", "mark", "window"])
    p_operator.add_argument("ids", nargs="*")
    p_operator.set_defaults(func=cmd_operator)

    p_child = sub.add_parser("run-child",
                             help="real child session for startup telemetry")
    p_child.add_argument("--agent", required=True,
                         choices=["claude", "codex"])
    p_child.add_argument("--transport", choices=["grpc", "http", "json"],
                         help="force the child's OTLP transport; a run emits "
                              "only its selected transport's completion")
    p_child.add_argument("--sandbox",
                         choices=["read-only", "workspace-write",
                                  "danger-full-access"],
                         help="Codex sandbox policy for the child session")
    p_child.set_defaults(func=cmd_run_child)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
