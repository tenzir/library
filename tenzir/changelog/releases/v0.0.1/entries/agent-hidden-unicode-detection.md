---
title: Agent hidden Unicode detection operator
type: feature
authors:
  - codex
---

The `tenzir` package now flags invisible Unicode formatting characters in
agent prompts, responses, and file edits:

```tql
subscribe "ocsf"
tenzir::detect::agent::hidden_unicode
publish "findings"
```

A single pattern over Unicode category "Format" catches zero-width spaces,
bidirectional overrides, and Unicode tag characters in one check, the three
families documented for hiding instructions from human review while an LLM
still parses them. The detector reads `message_context.prompt_text`,
`message_context.response_text`, and `file_diff` on any event carrying the
AI Operation profile, which requires the source package's `include_content`
parameter to be enabled.

Lives in the new `tenzir::detect::agent` namespace, alongside
`tenzir::detect::network` and `tenzir::detect::behavior`.
