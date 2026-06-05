# Tenzir Library

This repository hosts the Tenzir Library, a collection of
[packages](https://docs.tenzir.com/explanations/packages.md) that
contain user-defined operators, pipelines, examples, and context definitions.

Every top-level directory that does not start with `.` is a package.

Integration packages typically have the name of the primary vendor, like
`amazon`, `google`, or `microsoft`.

## Workflows

All key workflows are well-supported by agents. See
<https://docs.tenzir.com/guides/ai-workbench/use-agent-skills.md> for a list
of relevant agent skills during package development.

Always load the `tenzir-docs` skill when working with TQL content.

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

### Test packages

Use [tenzir-test](https://docs.tenzir.com/reference/test-framework.md) for
testing packages.

Primary operations:

- `uvx tenzir-test` runs all tests on every package in the library
- `uvx tenzir-test <pkg>` runs all tests for the package
