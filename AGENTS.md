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

## Releasing

Package releases go through PRs; never create or push tags manually.

- Prepare a release on the PR branch with
  `uvx tenzir-ship==2.3.1 --root <pkg> release create --title ... --intro ... --yes`,
  then run `uvx tenzir-ship==2.3.1 --root <pkg> validate`. Commit the new
  `changelog/releases/<version>/` and the consumed `changelog/unreleased/`
  entries. A PR may release several packages and versions.
- Only stable `vX.Y.Z` releases are allowed; do not use `--rc`.
- A new release must be newer than the package's existing releases and its
  `<pkg>/v*` tags. Some packages have legacy tags without release snapshots, so
  check `git ls-remote --tags origin 'refs/tags/<pkg>/*'` and pass an explicit
  version if `tenzir-ship` would infer an older one.
- Release snapshots are immutable. Do not edit or delete existing
  `changelog/releases/` directories, except when removing a whole package.
- After merge, the **Tests** workflow tags every new release as
  `<pkg>/vX.Y.Z` at the tested commit once all checks pass. If that run fails,
  rerun it; otherwise dispatch **Tests** on `main` with `release-base` set to
  the commit before the missed releases.
