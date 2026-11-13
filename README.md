# 📚 Tenzir Library

This repository hosts the official collection of content
[packages](https://tenzir.com/docs/explanations/packages/) for Tenzir.

Packages require Tenzir 7 or later.

## 🚀 Install packages

A package becomes available to your pipelines once your configuration lists it
under `dependencies` in its `package.yaml`. For details, see our [installation
guide](https://tenzir.com/docs/guides/packages/install-a-package/):

1. **Web UI**: open **Packages** in the
   [app](https://app.tenzir.com), select a package, click _Install_, and
   commit the draft.
2. **Command line**: run `tenzir package add <package>` inside a working copy
   of your configuration, then push it with `tenzir config apply`.

## 🧱 Package anatomy

A package lives in a directory with these building blocks:

- `operators/`: user-defined operators (UDOs) you can reuse across pipelines.
- `examples/`: runnable TQL snippets that demonstrate package UDOs.
- `tests/`: deterministic [integration
  tests](https://tenzir.com/docs/reference/test-framework) that verify UDOs.
- `package.yaml`: the package manifest with metadata and dependencies.

Packages contain no pipelines or contexts. Your configuration declares the
contexts that a package's operators use, as the package description shows.

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
TENZIR_BINARY="uvx tenzir" uvx tenzir-test */
```

## ⚖️ License

The Tenzir Library is licensed under the [Apache License 2.0](LICENSE).
