---
name: harness-check
description: Generate nearly all security-relevant native OpenTelemetry activity from a real Claude Code or Codex harness with minimal user interaction. Use when testing agent OTEL export or telemetry pipelines, exercising native agent tools, model turns, files, commands, processes, sandbox decisions, web, MCP, skills, plugins, hooks, subagents, schedulers, approvals, and startup posture without fabricating telemetry.
---

# Generate native harness telemetry

Generate events through Claude Code or Codex itself. Permit disposable test
targets, but never fabricate an event, directly drive a protocol to imitate the
harness, or claim a lookalike file/process action covers a native lifecycle
event.

## Start or resume

Use the directory containing this file as `<skill>`, regardless of the current
working directory. For every new invocation, run `python3
scripts/harness_check.py new-run claude|codex` once. Save its returned
absolute path as `<run>` and pass
`HARNESS_CHECK_DIR=<run>` to every script command, including commands resumed
after user interaction. Never reuse another invocation's directory or the
legacy UID-only default.

If continuing during a prepared manual sequence, inspect the transcript,
remember the observed outcome, and advance by exactly one step without running
a bookkeeping command. Do not restart the autonomous workload.

For a new run:

1. Read `reference/coverage.md` as the completion contract.
2. Run `python3 scripts/harness_check.py inventory --agent claude` or
   `--agent codex` according to the harness executing this skill. Do not rely
   on home-directory detection when both clients are installed.
3. Check the `TELEMETRY` section before generating the workload. If telemetry
   is disabled or no exporter is configured, do not pretend the run can emit
   OTEL. Configure it through an already-authorized mechanism, or give the user
   exactly one required setup/restart action and wait. Never print endpoint
   credentials or headers.
4. Run `scripts/run-all.sh`. It generates dense real filesystem, command,
   process, failure, CLI, and shell-network activity inside the harness
   sandbox. Continue after individual failures.
5. Read and execute `reference/agent-probes.md` using the current harness's
   native tools. Append every outcome through `python3
   scripts/harness_check.py record`.
6. Read `reference/child-sessions.md` and run `python3
   scripts/harness_check.py run-child --agent claude|codex` for the current
   product to generate startup-only, plugin, hook, and MCP activity.
   Do not ask the user to perform work the child can perform.
7. Compare the run with every row in `reference/coverage.md`. Run missing safe
   native triggers before moving to manual actions.
8. Attempt collector receipt verification as described in
   `reference/telemetry-verification.md`, and record the outcome.

Do not ask for scope selection or approval for ordinary disposable probes.
Never send messages, modify production records, push repositories, expose
secrets, or operate on the user's real data merely to increase coverage.

## Perform unavoidable manual probes

Read `reference/manual-probes.md`. User interaction is allowed only for a real
approval decision, Claude Code's interactive permission-mode control, or a
product UI/API control the agent truly cannot invoke.

Determine all applicable manual steps, then run `python3
scripts/harness_check.py operator prepare <id>...` once before presenting any
of them. Present exactly one action and end the turn. On each user reply,
retain the observed result in the conversation and present the next single
action without running Bash. Never reveal the remaining checklist. After the
last manual result, run one command only: `python3 scripts/harness_check.py
operator batch-mark <id>=PASS|FAIL|SKIP ...`.

The native approval result is authoritative. If the transcript says an
automatic reviewer approved or denied the request, immediately mark the human
decision probe `SKIP`, record the automatic decision separately, and continue.
Do not ask the user to confirm a dialog that was never shown.

## Report

Report:

- native event families and tool boundaries exercised;
- conditional gaps with the exact missing tool, configuration, transport, or
  authentication prerequisite;
- failures separately from expected denials and skips;
- the correlation log path and its fields: timestamp, result, probe id,
  detail.

Run `python3 scripts/harness_check.py summarize` and report its effective
counts. The latest result
for a probe supersedes earlier attempts. Describe a `FAIL` followed by `PASS`
as a recovered attempt, not as a current failure. Never aggregate logs from
different run directories.

Do not infer that the collector received an event merely because its trigger
ran. If a telemetry query or capture endpoint is available, verify receipt;
otherwise state that the workload was generated but delivery was not checked.
