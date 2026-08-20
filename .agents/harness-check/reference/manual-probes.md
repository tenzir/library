# Unavoidable user actions

Before the first manual action, determine the entire applicable sequence and
run `bash scripts/probe-operator.sh prepare <id>...` exactly once. Reveal one
action per turn. On each reply, observe and retain the result in the
conversation, then advance without running Bash. After the final result, store
all outcomes with one `batch-mark` command. Do not run `begin`, `mark`,
`record.sh`, or another bookkeeping command between manual steps.

Do not ask the user to run commands, edit files, configure fixture servers, or
restart a child harness when the agent can do that itself.

## Approval denied

Use `manual.approval-deny`. Tell the user only that the next prompt is a safe
denial probe. Request approval for a harmless, reversible action that the
current harness genuinely gates—for example an HTTP HEAD request through a
network-restricted shell. Ask the user to decline the actual approval dialog.
Do not use a destructive command or touch an existing file.

In Claude Code, say explicitly: “Decline the approval dialog. When Claude asks
what it should do instead, type `continue`.” The follow-up is required because
denial ends the tool attempt and returns control to the user.

## Approval accepted

Use `manual.approval-allow`. Tell the user only that the next prompt is the
safe acceptance probe. Request the equivalent harmless action and ask them to
approve the actual dialog. Clean up any disposable artifact automatically.

These two decisions require user input by definition. If the harness cannot
produce a real approval dialog, retain `SKIP` for the final batch; do not
imitate one in prose.
After requesting approval, inspect the native result before waiting for a user
reply. When an automatic reviewer resolves the request, immediately mark the
corresponding `manual.*` result as `SKIP`, retain
`automatic.approval-allow` or `automatic.approval-deny` as `PASS` for the final
batch, and proceed. Never tell the user to reply after an automatic decision
has already prevented the human dialog.

## Claude Code permission mode

Claude Code emits a dedicated permission-mode-change event. If the current
mode can be changed only through the interactive UI:

1. Use `manual.claude.permission-mode` and ask the user to switch once to
   `manual` with the native permission control. Wait.
2. Run the approval denied and accepted probes above.
3. Use `manual.claude.permission-restore` and ask the user to restore the
   original mode. Wait.

Skip the first change when already in `manual`, but still restore any mode the
test changed. Never ask for a restart merely to change this live control.

## Conditional UI-only configuration

Only when encountered during autonomous probing:

- `manual.codex.config-write`: when the running Codex product exposes an
  authenticated UI/API configuration write that cannot be invoked by the
  agent, ask the user to make one reversible test change, verify it, then ask
  them to restore it in the next turn.

Do not log out, install software, change credentials, or restart the user's
main session merely to broaden the workload. Real child sessions cover
startup and lifecycle activity without disrupting the main session.
