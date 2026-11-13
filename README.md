# 📚 Tenzir Library

This repository hosts the official collection of content
[packages](https://tenzir.com/docs/explanations/packages/) for Tenzir.

Packages require Tenzir 6.20.0 or later, which uses Nova by default.

## 🚀 Install packages

Pick the workflow that fits your environment. For details, see our [installation
guide](https://tenzir.com/docs/guides/package-management/install-a-package/):

1. **Web UI**: browse to
   [app.tenzir.com/library](https://app.tenzir.com/library) and click _Install_.
2. **Interactive**: run
   [`package_add`](https://tenzir.com/docs/reference/operators/package/add)
   against a local directory, and remove it later with
   [`package_remove`](https://tenzir.com/docs/reference/operators/package/remove).
3. **As code**: place packages under `packages/` inside your
   configuration directory (or another path listed in `tenzir.package-dirs`) and
   include an optional `config.yaml` for inputs.

## 🧱 Package anatomy

A package lives in a directory with these building blocks:

- `operators/`: user-defined operators (UDOs) you can reuse across pipelines.
- `examples/`: runnable TQL snippets that demonstrate package UDOs.
- `tests/`: deterministic [integration
  tests](https://tenzir.com/docs/reference/test-framework) that verify UDOs.
- `package.yaml`: the package manifest with metadata and optional
  enrichment contexts.

## 🤝 Contribute a package

Join us on our mission to democratize the world of security data integrations.
Follow our [tutorials](https://tenzir.com/docs/tutorials) to learn how to
package up use cases. Then:

- Share it on the [Community Discord](https://discord.tenzir.com) to gather
  feedback.
- Open a pull request in
  [github.com/tenzir/library](https://github.com/tenzir/library) so the package
  appears in the public Tenzir Library.
- Keep iterating—tests and good docs make it easier for others to adopt your
  work.

Run the package tests with the latest Tenzir release:

```sh
TENZIR_BINARY="uvx tenzir" \
TENZIR_NODE_BINARY="uvx --from tenzir tenzir-node" \
  uvx tenzir-test */
```

## 📦 Release packages

Prepare releases on your PR branch with
[`tenzir-ship`](https://tenzir.com/docs/guides/packages/maintain-a-changelog/).
For example, to release the `tenzir` package:

```sh
uvx tenzir-ship==2.3.1 --root tenzir release create \
  --title "Release title" \
  --intro "Describe the release highlights." \
  --yes
uvx tenzir-ship==2.3.1 --root tenzir validate
```

Commit the generated `changelog/releases/<version>/` files and changes to
`changelog/unreleased/` in the PR. Repeat for any other packages you want to
release. One PR can contain multiple releases, including multiple versions of
one package. Omit the version to let `tenzir-ship` infer the next release. The
library supports only stable `vX.Y.Z` releases; CI rejects release candidates.

After merge, the **Tests** workflow validates every package changelog and runs
syntax checks and package tests on `main`. Only after all those jobs pass does
it create annotated tags for every new release, such as `tenzir/v0.1.0` and
`suricata/v0.3.0`. All tags point to the exact commit that passed CI, and CI
pushes them atomically. No local `release publish` or manual tag creation is
needed. CI does not create GitHub release pages.

Release history is immutable. CI rejects changes to existing release snapshots
and tags that already point to another commit. Removing a whole package also
removes its release history; its existing tags remain. Some packages have older tags
without corresponding changelog releases. Before their first `tenzir-ship`
release, check `git ls-remote --tags origin 'refs/tags/<package>/*'` and choose
an explicit version newer than those tags if automatic inference would reuse
one.

If tagging fails, rerun the failed workflow jobs after resolving the cause.
Tags already pointing to the tested commit are safe to retry; CI never moves
existing tags. Releases introduced by a failed run are not picked up by a
later push. If rerunning the original workflow is not possible, run the
**Tests** workflow manually on `main` with `release-base` set to the commit
before those releases. After all checks pass, CI tags the missing releases at
the commit it tested. Without `release-base`, a manual run only performs checks.

Repository maintainers should require **Validate package releases** alongside
the existing test checks in the `main` ruleset. The tag job depends on all test
and validation jobs regardless of that setting. It uses the built-in
`GITHUB_TOKEN` with `contents: write`; tags created with that token do not
trigger additional GitHub Actions workflows.

## ⚖️ License

The Tenzir Library is licensed under the [Apache License 2.0](LICENSE).
