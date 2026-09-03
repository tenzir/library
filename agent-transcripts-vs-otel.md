# Agent transcripts vs. OTEL telemetry

Working notes on whether to ingest agent session transcripts (Claude Code /
Codex JSONL, optionally normalized via Letta's
[Trajectory](https://github.com/letta-ai/trajectory)) alongside the OTLP feed
we already map in the `anthropic` and `openai` packages.

Measurements below come from the local machine on 2026-09-03: 103 Claude Code
session files under `~/.claude/projects/` (142 MB, ~46 MB in the last 7 days)
and 76 Codex rollout files under `~/.codex/sessions/YYYY/MM/DD/` (313 MB).
Codex transcripts are larger per session and differ structurally — see the
Codex section below before generalizing any Claude Code observation.

## Background: what Trajectory is

Trajectory (`npm install @letta-ai/trajectory`, `pip install agent-trajectory`)
is a **transcript normalization library**, not an instrumentation agent. It
reads the session files that coding harnesses already write to disk and
converts them into a unified `trajectory-v1` record format: a metadata record
(source, cwd, git branch, model), then timestamped user messages, assistant
prose, reasoning, tool calls with stable IDs, and tool results. It strips
harness bookkeeping, yielding ~5–6x fewer tokens than the raw logs. Adapters
exist for 18+ harnesses (Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI,
OpenHands, …). There is no CLI; the API is `listTrajectories()` and
`normalizeTranscript()`.

It gets its data purely by parsing files after the fact — no hooks, no
network interception. Claude Code appends every event to
`~/.claude/projects/<munged-cwd>/<session-id>.jsonl`; Codex writes rollout
JSONL under `~/.codex/sessions/`.

## How transcripts reach Tenzir

The transcripts are append-only NDJSON files, so any file-tailing shipper
works — no harness integration required:

| Shipper | Endpoint config | Tenzir listener |
|---|---|---|
| Filebeat / any Beat / Logstash | `filestream` input on the JSONL globs, standard Elasticsearch output | `accept_elasticsearch "0.0.0.0:9200"` (Bulk API emulation) |
| nxlog | `im_file` + `om_tcp` | `accept_tcp "0.0.0.0:9000" { read_ndjson }` |
| Fluent Bit | `tail` input + `forward` output | `from_fluent_bit "forward"` |
| Vector / Cribl / nxlog (HEC) | Splunk HEC output | `accept_splunk hec_token=secret("hec-token")` |
| No shipper installed | Tenzir client on the endpoint | `from_file "~/.claude/projects/**/*.jsonl", watch=true { read_ndjson }` |

Consequence: the shipper delivers **raw native envelope lines**, so
normalization moves to the Tenzir side as TQL (one `normalize` operator per
harness, same pattern as `anthropic/operators/claude_code/`). The Trajectory
repo then serves as a spec (`trajectory-v1.schema.json` and its adapter
logic), not as code we run — Beats cannot call a JS library. Running the
library at the edge is only an option with a custom shipper script.

## What each feed contains

**OTEL (ingested today via `accept_otlp` + the `anthropic` package):**
`tool_decision` (tool name, `tool_use_id`, allow/deny decision, full
`tool_parameters`), `tool_result` (name, id, success flag — not the output
content), `permission_mode_changed`, `mcp_server_connection`,
`hook_registered`, `plugin_loaded`, `skill_activated`, `subagent_completed`,
`api_error`, `assistant_response`, `llm_request` spans with latency, and
cost/token metrics. Real-time push, small, schema-stable, content-poor by
design (prompts redacted unless opted in).

**Transcripts (measured locally):** 11.5k assistant records, 6.5k user
records, 7k attachments, plus bookkeeping. Assistant records break down into
5.4k `tool_use` blocks (full arguments), 3.5k `thinking` blocks, and 2.6k
text blocks. Every record carries `sessionId`, `cwd`, `gitBranch`,
`isSidechain`, `requestId`, model, and per-message token `usage`. User
records embed the full `toolUseResult`. System records include
`compact_boundary` and `away_summary`. Human-typed commands (slash commands
and `!`-prefixed shell) land in `user` records, not `system` records, in
Claude Code 2.1.245 — see the Human activity note below. Subagent
conversations are separate
files: 60 `agent-*.jsonl` under `<session-id>/subagents/` locally — shipper
globs must be recursive (`**`) to catch them.

## What transcripts add over OTEL

1. **Reasoning — Claude Code only.** 3,511 plaintext thinking blocks on one
   machine — the *why* behind every action. Absent from OTEL entirely.
   Codex is the opposite: 10k+ reasoning payloads, all `encrypted_content`
   with empty summaries — unusable. (This is what Trajectory's "drops
   encrypted reasoning blobs" refers to.)
2. **Full tool outputs.** OTEL's `tool_result` says `success: true`; the
   transcript has the stdout/file content the model saw, truncated at 30,000
   characters (max observed is exactly 30,000; median 349, p90 1,853 across
   3,985 local samples — most outputs are complete).
3. **Full prompts and responses.** OTEL redacts prompt content by default.
4. **Subagent interiors.** OTEL emits one `subagent_completed`; the full
   subagent conversations exist as separate `agent-*.jsonl` files under
   `<session-id>/subagents/` (60 locally).
5. **File forensics.** `file-history-snapshot` / `file-history-delta`
   records track every file the agent touched — but they carry only
   *references* (`backupFileName@version`). The before-state content lives
   in a separate store, `~/.claude/file-history/` (4.6 MB / 609 files
   locally). A JSONL-only shipper gets pointers, not content — ship that
   directory too if before-states matter.
6. **Human activity.** Slash commands the user ran (`/model`,
   `/remote-control`, …) and their output are captured. Shell commands the
   user typed with the `!` prefix *are* captured too — re-verified in Claude
   Code 2.1.245, where a `!` command lands in two `user` records wrapping
   `<bash-input>` and `<bash-stdout>`/`<bash-stderr>`. In that version both
   slash and `!` commands are `user` records (slash commands via
   `<local-command-stdout>` plus a meta `<command-name>` record), not a
   `system`/`local_command` subtype — treat the record shape as
   version-dependent and match on the tags rather than the subtype.
7. **Retroactivity.** Transcripts exist for every session ever run,
   regardless of whether OTEL export was configured at the time.

## What OTEL has that transcripts never will

A grep across all 142 MB of Claude Code transcripts found **zero**
permission-decision records. The authorization outcome (`tool_decision`
allow/deny) — the anchor of our OCSF Authorization mapping — exists only in
OTEL. The same holds for MCP server connections, hook/plugin/skill
lifecycle, `api_error`, spans/latency, and all cost/token metric time
series. In short: the transcript records what happened; OTEL records what
was *permitted* and what it *cost*.

**Codex caveat:** Codex rollouts *do* record security posture — every
`turn_context` record carries `approval_policy` and `sandbox_policy` (with
values like `danger-full-access` + `approval: never` observed in 151 turns
locally). That is the *policy in force per turn*, still not per-tool
allow/deny decisions — no approval-decision records exist in the rollouts
either. But it means "posture only in OTEL" is wrong for Codex: transcript
ingestion alone can already detect sandbox-off/auto-approve sessions there.

## Codex rollouts (measured)

Codex's transcript is not "the same thing with different field names" — its
security content differs materially from Claude Code's. From the 76 local
rollouts (313 MB): 45k `event_msg`, 36.6k `response_item`, 3k
`turn_context`, 240 `world_state`, 81 `session_meta`, 75 `compacted`
records.

What Codex records **better** than Claude Code:

- **Process-grade command telemetry.** Each of the 3,928 `CommandExecution`
  items carries `command`, `parsed_cmd` (structured!), `cwd`, `exit_code`,
  `process_id`, `duration`, `status`, and full `stdout`/`stderr`/
  `aggregated_output`. Output median 1.3 KB, p90 16 KB, max ~1 MB — no 30k
  truncation like Claude Code. This is near-EDR-grade process data.
- **Per-turn security posture.** `turn_context` records `approval_policy`,
  `sandbox_policy`, `file_system_sandbox_policy`, `permission_profile`,
  `collaboration_mode`, model, cwd, and workspace roots on every turn.
  Locally observed: 550 turns `read-only`/`never`, 407
  `workspace-write` with `network_access: false`, 151
  `danger-full-access`/`never` — a directly detectable escalation signal.
- **File changes as items.** 640 `FileChange` items with `changes`, status,
  stdout/stderr — in-band, unlike Claude Code's out-of-band backup store.
- **Explicit MCP/subagent items.** `McpToolCall`, `SubAgentActivity`,
  `CollabAgentToolCall`, plus `inter_agent_communication_metadata` records.

What Codex records **worse**:

- **Reasoning is encrypted.** All reasoning payloads are
  `encrypted_content`; `raw_content`/`summary_text` on Reasoning items are
  empty locally. No injection-forensics reasoning from Codex, period.

Additional Codex-side stores beyond the rollouts (collectable, but not
NDJSON-shippable — needs a script or Tenzir on the endpoint):

- `~/.codex/history.jsonl` — cross-session log of user inputs, including
  pasted terminal content (observed: SSH banners, error output — a secrets
  exposure channel in itself).
- SQLite databases: `logs_2.sqlite` (81 MB), `state_5.sqlite`,
  `thread_history_1.sqlite`, `memories_1.sqlite`, `goals_1.sqlite`,
  `queue_1.sqlite`.

## Event presence matrix

Which signal lives where. "OTEL" means the Claude Code OTLP export as mapped
by the `anthropic` package; "Transcript" means the session JSONL under
`~/.claude/projects/`. The matrix is Claude-Code-specific — Codex differs
(see the Codex section): posture moves into the transcript, reasoning drops
out of it.

### In both feeds

| Signal | OTEL | Transcript | Notes |
|---|---|---|---|
| Tool call + full arguments | `tool_decision` / `tool_result` (`tool_parameters`) | `tool_use` content blocks | Join via `tool_use_id`; dedup required |
| Tool result status | `tool_result` (`success` flag only) | `toolUseResult` (full content) | Only the transcript has the actual output |
| Assistant response | `assistant_response` event | `assistant` text blocks | Full prose only in the transcript |
| User prompt | `user_prompt` event (redacted by default) | `user` records (full text) | OTEL carries content only with opt-in |
| Permission mode change | `permission_mode_changed` | `permission-mode` records | |
| Subagent activity | `subagent_completed` (summary) | `agent-*.jsonl` files under `subagents/` | Interior conversation only in the transcript; needs recursive glob |
| LLM request metadata | `llm_request` span | `requestId`, model per assistant record | Latency only in the span |
| Token usage | metrics time series | per-message `usage` | Different granularity; both usable |
| Session identity/context | resource attributes (`session.id`, host) | `sessionId`, `cwd`, `gitBranch`, `version` | Join via session ID |

### Only in OTEL

| Signal | Event/metric |
|---|---|
| Authorization outcome (allow/deny + source) | `tool_decision` — zero equivalents in 142 MB of transcripts |
| MCP server connections | `mcp_server_connection` |
| Hook lifecycle | `hook_registered` |
| Plugin lifecycle | `plugin_loaded` |
| Skill activation | `skill_activated` |
| API errors | `api_error` |
| Latency / spans | `llm_request` trace spans |
| Cost and lines-of-code metrics | metrics signal |

### Only in the transcript

| Signal | Record/block |
|---|---|
| Reasoning | `thinking` content blocks (3.5k locally) |
| Full tool output content | `toolUseResult` in user records |
| Attachments (images, pasted content) | `attachment` records (7k locally) |
| File-edit tracking (references only; content in `~/.claude/file-history/`) | `file-history-snapshot` / `file-history-delta` |
| Slash commands the human ran, with output | `user` records with `<local-command-stdout>` (2.1.245; earlier versions used `system`/`local_command`) |
| Shell the human typed with `!`, with output | `user` records with `<bash-input>` / `<bash-stdout>` (2.1.245) |
| Context compaction points | `system` records, subtype `compact_boundary` |
| Session summaries while user away | `system` records, subtype `away_summary` |
| Session bookkeeping (titles, queue ops, PR links) | `ai-title`, `agent-name`, `last-prompt`, `queue-operation`, `pr-link`, `frame-link`, `bridge-session` |

## Security relevance

Rating each signal by what it lets you detect or investigate. "High" means
it directly anchors a detection or is indispensable in an incident; "medium"
means supporting evidence or anomaly source; "low" means operational/UX
value only.

| Signal | Feed | Relevance | Why |
|---|---|---|---|
| Authorization outcome (`tool_decision`) | OTEL only | High | The allow/deny audit trail. Detects auto-approve abuse, denied-then-retried actions, unusual grant patterns. |
| Tool call + arguments | both | High | The actual commands, file paths, and URLs. Primary detection surface: destructive commands, exfil (`curl` to unknown hosts), credential access. |
| Full tool output | transcript only | High | What the model actually saw — secrets echoed into context, sensitive data available for leaking. DLP and blast-radius assessment. Truncated at 30k chars; most outputs complete (median 349). |
| Hook lifecycle (`hook_registered`) | OTEL only | High | Hooks execute arbitrary shell on harness events — a persistence mechanism. A new hook is the agent-world equivalent of a new cron job. |
| MCP server connections | OTEL only | High | New capability and supply-chain surface. A rogue MCP server is both a code-execution and a prompt-injection vector. |
| Plugin / skill activation | OTEL only | High | Same class as hooks/MCP: third-party instructions and code entering the agent. |
| Permission mode change | both | High | Escalation signal — switching to auto-approve/bypass modes changes the trust posture mid-session. |
| File-edit tracking (`file-history-*`) | transcript only | High | Tamper evidence: exactly what the agent changed, when, and a versioned backup reference. Recovery of prior content requires also shipping `~/.claude/file-history/`. |
| User prompt content | transcript (OTEL redacted) | High | Prompt-injection payloads arrive here (and via attachments); also the insider-misuse record of what the agent was asked to do. |
| Commands the human typed (slash and `!`-shell), with output | transcript only | Medium | Posture-relevant human actions (`/remote-control`, mode changes) and `!`-typed shell, with output. In 2.1.245 both are `user` records (slash: `<local-command-stdout>`; shell: `<bash-input>`/`<bash-stdout>`), not a `system`/`local_command` subtype. `!`-shell now verified present locally; match on the tags, since the subtype varies by version. |
| Reasoning (`thinking`) | transcript only, Claude Code only | Medium | Injection forensics gold: shows *why* the model acted, i.e. whether injected instructions steered it. Too noisy for detection, invaluable in IR. Codex reasoning is encrypted — unavailable. |
| Per-turn posture (`turn_context`, Codex only) | transcript only | High | `approval_policy` + `sandbox_policy` per turn; `danger-full-access` with `approval: never` is a directly detectable escalation. |
| Process telemetry (`CommandExecution`, Codex only) | transcript only | High | `parsed_cmd`, `exit_code`, `process_id`, `duration`, full output up to ~1 MB — near-EDR-grade. |
| Subagent interiors | transcript only | Medium | Delegated actions hide here; a subagent can exfiltrate while the parent looks clean. Summary event alone (OTEL) is insufficient in IR. |
| Attachments | transcript only | Medium | Inbound data channel: pasted secrets, images carrying injection payloads. |
| Assistant response text | both (full only in transcript) | Medium | Outbound leak channel — sensitive data can exit via prose, not just tool calls. |
| API errors | OTEL only | Medium | Abuse and anomaly hints (rate limits, auth failures), mostly ops. |
| Session context (cwd, branch, host) | both | Medium | Not a detection itself, but the correlation backbone for every other signal. |
| Token usage / cost | both | Low | FinOps; extreme spikes can flag runaway or abusive sessions. |
| Latency spans | OTEL only | Low | Operational. |
| Bookkeeping (titles, queue ops, PR links, summaries) | transcript only | Low | UX state; `away_summary` can contain sensitive text but has no detection value. |

By threat scenario:

- **Prompt injection:** user prompts, attachments, MCP connections → thinking
  (did it steer?) → tool calls (did it act?).
- **Data exfiltration:** tool arguments + outputs, assistant responses,
  subagent interiors.
- **Unauthorized/destructive actions:** tool decisions, permission mode
  changes, tool arguments, file before-states.
- **Persistence / supply chain:** hooks, plugins, skills, MCP servers.
- **Insider misuse / audit:** user prompts, local commands, session context.

The split is stark: the **detection-grade control-plane signals live almost
entirely in OTEL** (authorization, hooks, MCP, plugins), while the
**investigation-grade content lives almost entirely in the transcript**
(outputs, reasoning, file states, prompts). Neither feed covers a threat
scenario end to end on its own — injection, for example, needs OTEL's MCP
events *and* the transcript's prompt/thinking content.

## Overlap and join keys

Tool calls with full arguments appear in **both** feeds, and both carry
`tool_use_id` — the feeds join at tool-call granularity, not just per
session (`sessionId` / `session.id`). This also means naive dual-ingest into
the same OCSF classes would double-count every tool event.

## Volume, cost, risk

- ~6.5 MB/day per developer machine; ≈650 MB/day for a 100-dev fleet.
  Trivial for Tenzir.
- Transcript lines can be very large (pasted images, big tool outputs) —
  check shipper line caps (e.g. Filebeat `message_max_bytes`, 10 MB
  default).
- Content includes secrets echoed into tool output and effectively
  constitutes developer conversations: mandatory masking, TLS transport,
  shorter retention, tighter access control. In many jurisdictions this is a
  works-council/GDPR-level decision the customer must make — opt-in per
  deployment, never a default.

## Recommendation

Ingest transcripts — but as a second stream, not a second source for the
same events.

- **If the deployment is detection + compliance dashboards only:** OTEL
  alone suffices. It has the authorization signal, it is real-time, and it
  is ~100x smaller. Skip transcripts.
- **If the deployment includes incident response, DLP review, or
  agent-behavior analytics:** ingest transcripts. OTEL can say "Bash was
  permitted at 14:32"; only the transcript holds the command, its output,
  and the reasoning — the question every incident ends with.

Concrete design:

1. **OTEL stays the canonical event stream.** Sole source for OCSF
   activity/authorization events; never re-derive those from transcripts
   (double-counting).
2. **Transcripts become a content/forensic layer** in their own topic
   (`agent-transcripts`), normalized to a trajectory-v1-style schema, keyed
   by `sessionId` + `tool_use_id` for joins against the OTEL feed.
3. **Gate behind deliberate handling:** masking pipeline, TLS, retention
   limits, access controls, opt-in per deployment.

Net: two gains from OTEL (authorization, economics), one from transcripts
(complete content, retroactive), joined by session and tool-call IDs. Ship
the OTEL path as the default; offer the transcript path as an opt-in
forensics add-on package.
