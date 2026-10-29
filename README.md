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

Use the OCSF functions to finalize mapped records, for example
`this = ocsf_cast(ocsf_derive(this))` for a top-level event or
`ocsf = ocsf_cast(ocsf_derive(ocsf))` for an event in a field.

OCSF mapping tests call `ocsf_cast` to report missing required fields and
object-constraint violations as warnings in the test output. If a source omits
an identity required by its activity class, mappers preserve the candidate under
`unmapped.incomplete_activity` and emit a Base Event. Incomplete optional
objects remain under `unmapped.ocsf_residue`.

## ⚖️ License

The Tenzir Library is licensed under the [Apache License 2.0](LICENSE).
