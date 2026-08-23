# Tenzir Library

This repository hosts the official Tenzir Library. Every directory (except those
leading with `.`) is a package.

## Authoring

Always load the `tenzir` skill when producing or changing TQL. Stop and inform
the user if the skill is not available.

Write clear and idiomatic TQL by default unless the user provides a specific
reason to do otherwise.

## Testing

Use `tenzir-test` for testing packages:

- `uvx tenzir-test` runs all tests on every package in the library
- `uvx tenzir-test <pkg>` runs all tests for the package

Use `uvx tenzir -f pipeline.tql` for one-shot TQL program execution. 
