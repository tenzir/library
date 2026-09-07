#!/usr/bin/env python3
"""Fixture hook command for the child Claude Code session.

Reads the hook payload from stdin and behaves according to --mode so that one
real session exercises every hook outcome:

  pre-tool   PreToolUse on Bash. Denies a command carrying the marker
             harness-check-hook-deny through the documented JSON decision;
             lets every other command through.
  post-tool  PostToolUse on Bash. Exits 1 (non-blocking hook error) for a
             command carrying harness-check-hook-fail; otherwise prints the
             harness-check-hook-executed marker.
  mark       any other event: prints a harness-check-hook-<event> marker.

Every invocation appends "<event>\t<tool>\t<outcome>" to the file named by
HARNESS_CHECK_HOOK_LOG, which is how run-child proves which hook events fired
without trusting the model's transcript.
"""
import json
import os
import sys


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "mark"
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    event = payload.get("hook_event_name") or mode
    tool = payload.get("tool_name", "")
    command = str((payload.get("tool_input") or {}).get("command", ""))
    outcome = "ok"
    exit_code = 0
    if mode == "pre-tool" and "harness-check-hook-deny" in command:
        outcome = "deny"
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason":
                "harness-check fixture hook denied this marker command",
        }}))
    elif mode == "post-tool" and "harness-check-hook-fail" in command:
        outcome = "fail"
        print("harness-check-hook-failed", file=sys.stderr)
        exit_code = 1
    elif mode == "post-tool":
        print("harness-check-hook-executed")
    else:
        print(f"harness-check-hook-{event}")
    log = os.environ.get("HARNESS_CHECK_HOOK_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(f"{event}\t{tool}\t{outcome}\n")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
