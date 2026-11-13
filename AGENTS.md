# Tenzir Library

This repository hosts the official Tenzir Library. Every non-hidden directory is
a package.

## Authoring

- Always load the `tenzir` skill when producing or changing TQL. Stop and inform
  the user if the skill is not available.
- Write idiomatic, streamlined TQL by default according to the skill.

## Testing

Use `tenzir-test` for testing packages:

- `uvx tenzir-test` runs all tests on every package in the library
- `uvx tenzir-test <pkg>` runs all tests for the package

## Releasing

Always create a new package release when filing a pull request that includes
user-visible behavior changes. This means:

1. Create a changelog entry that describes the effect
2. Release via: `uvx tenzir-ship --root <pkg> release create`

CI does the rest.
