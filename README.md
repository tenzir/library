# 📚 Tenzir Library

This repository contains a collection of open-source
[packages](https://docs.tenzir.com/explanations/packages/) for Tenzir.

## ✨ Why packages matter

- Package once, deploy anywhere: ship contexts, operators, and runnable examples as a
  single unit.
- Examples keep packages environment-agnostic and show how to pass local
  configuration directly to UDOs and source/sink operators.
- Tests and examples travel with the package so behaviour stays predictable.

Learn more about the concept in the [packages
explanation](https://docs.tenzir.com/explanations/packages/).

## 🧱 Package anatomy

A package lives in a directory with these building blocks:

- `operators/`: user-defined operators (UDOs) you can reuse across examples and custom pipelines.
- `examples/`: runnable TQL snippets that demonstrate package UDOs and complete
  workflows.
- `tests/`: deterministic integration tests that verify UDOs and examples via
  the [test framework](https://docs.tenzir.com/reference/test-framework).
- `package.yaml`: the manifest with metadata and optional
  enrichment contexts.

## 🚀 Install packages

Pick the workflow that fits your environment. For details, see our [installation
guide](https://docs.tenzir.com/guides/package-management/install-a-package/):

1. **Tenzir Library UI**: browse
   [app.tenzir.com/library](https://app.tenzir.com/library), configure inputs,
   and click _Install_.
2. **Interactive TQL**: run
   [`package::add`](https://docs.tenzir.com/reference/operators/package/add)
   against a local directory, and remove it later with
   [`package::remove`](https://docs.tenzir.com/reference/operators/package/remove).
3. **Infrastructure as Code**: place packages under `packages/` inside your
   configuration directory (or another path listed in `tenzir.package-dirs`) and
   include an optional `config.yaml` for inputs.

## 🤝 Contribute a package

Follow the [write-a-package
tutorial](https://docs.tenzir.com/tutorials/write-a-package/) to scaffold, test,
and document a new idea, then:

- Share it on the [Community Discord](https://docs.tenzir.com/discord) to gather
  feedback.
- Open a pull request in
  [github.com/tenzir/library](https://github.com/tenzir/library) so the package
  appears in the public Tenzir Library.
- Keep iterating—tests and good docs make it easier for others to adopt your
  work.
