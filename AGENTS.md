# Tenzir Library

This repository hosts the Tenzir Library, a collection of
[packages](https://tenzir.com/docs/explanations/packages.md) that
contain user-defined operators, pipelines, examples, and context definitions.

Every top-level directory that does not start with `.` is a package.

Integration packages typically have the name of the primary vendor, like
`amazon`, `google`, or `microsoft`.

## Workflows

All key workflows are well-supported by agents. See
<https://tenzir.com/docs/guides/ai-workbench/use-agent-skills.md> for a list
of relevant agent skills during package development.

Always load the `tenzir` skill when working with TQL content.

Prefer running the following commands through `uvx` instead of executing them
locally, unless you are testing a specific feature that's not available in the
respective latest release:

- `tenzir`
- `tenzir-node`
- `tenzir-test`
- `tenzir-ship`

E.g., run `uvx tenzir -f path/to/pipe.tql` to execute a TQL program.

### Evolve a package

Use the `tenzir-manage-packages` skill to manage the lifecycle of a package.

### Check the agent harness

`.agents/harness-check/` generates a broad, security-relevant OpenTelemetry
workload from the current agent harness: native agent tools, file operations,
process lifecycle, scheduled jobs, CLI invocation, web access, MCP, and
permission decisions.

It is agent-agnostic: the scripted core is plain bash and runs under any
agent, or by hand.

- `$harness-check` runs the autonomous and guided workflow in Codex or Claude
  Code (both project skill paths point to the same source)
- `.agents/harness-check/scripts/run-all.sh` runs every safe scripted probe

Use it to test agent telemetry collection, especially after changing harness
settings, permissions, MCP servers, or the OTEL pipeline.

### Test packages

Use [tenzir-test](https://tenzir.com/docs/reference/test-framework.md) for
testing packages.

Primary operations:

- `uvx tenzir-test` runs all tests on every package in the library
- `uvx tenzir-test <pkg>` runs all tests for the package
