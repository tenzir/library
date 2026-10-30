# TruePattern

[TruePattern](https://truepattern.io) curates detection rules from public and
commercial rule repositories, with change analysis, ATT&CK techniques, and
license information where available. It publishes the rules as a STIX 2.1
collection over TAXII. Each rule is a STIX Indicator that carries the native
rule text in `pattern` and its language, such as `sigma`, `splunk`, `kql`,
`yara`, or `sublime-security`, in `pattern_type`.

This package runs the Sigma rules on your events with the `sigma` operator,
enriches the resulting findings with TruePattern's rule metadata, and
routes the rules in other formats to the systems that run them.

## Architecture

Two pipelines work together. A scheduled pipeline walks the feed and writes
current Sigma rules into one file. It also records their metadata in a rule
catalog. A detection pipeline matches your events against that file and
enriches every finding from the catalog:

```text
              TruePattern TAXII collection
                           │
  Daily walk               ▼
  ┌───────────────────────────────────────┐
  │ truepattern::feed                     │
  │ truepattern::sigma::update_rules ─────┼──► sigma.yaml
  │ truepattern::ocsf::normalize          │        │
  │ truepattern::update_context ──────────┼──┐     │ reload
  └───────────────────────────────────────┘  │     │
                                             ▼     │
                       truepattern-sigma-rules     │
                                             │     │
  Detection                                  │     │
  ┌───────────────────────────────────────┐  │     │
  │ OCSF events                           │  │     │
  │ sigma path="sigma.yaml" ◄─────────────┼──┼─────┘
  │ truepattern::enrich ◄─────────────────┼──┘
  └───────────────────────────────────────┘
                           │
                           ▼
           Enriched OCSF Detection Findings
```

The `sigma` operator only accepts constant rules or a path, so rules can't flow
from the feed into the operator as events. Instead, the walk writes a file,
and the `sigma` operator reloads it within seconds of every change.

The package requires the `stix` package and Tenzir 6.20.0 or later. The package
tests pass with stable Tenzir 6.20.0, which includes the empty Sigma source and
HTTP retry fixes (tenzir/mono#771 and tenzir/mono#772). No minimum engine version
is enforced by the package manifest.

The package does not filter execution or onward routing by license metadata.
Rules fetched through the authenticated API remain eligible when that metadata
is absent, null, empty, or whitespace-only. Existing format, validity, version,
and logsource selection still apply. See
[Respect rule licenses](#respect-rule-licenses) for attribution and applicable
terms.

## Configure credentials

Store the Base64 encoding of your TruePattern `username:password` pair in the
managed secret `TRUEPATTERN_CREDENTIAL`. The operator sends it with HTTP Basic
authentication. Wrong or missing credentials fail the request with HTTP status
`401`.

## Fetch the rules

`truepattern::feed` fetches the STIX Indicators of the collection:

```tql
truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL")
```

The collection holds every version of every rule. An update keeps the rule's
`id` and adds a version with a later `modified` time, and TruePattern never
revokes a version. `truepattern::latest` keeps the current version of each
rule. A walk of all rule versions takes a handful of requests.

Pass `added_after` to fetch only the versions that the collection received
since then. To fetch other STIX objects, such as the weekly reports that list
new rules, override the type filter:

```tql
truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL"),
  params={"match[type]": "report"}
```

`truepattern::ocsf::normalize` maps a rule to OCSF OSINT Inventory Info. The
rule text lands in `osint.detection_pattern`, the change analysis in
`osint.desc`, the upstream rule in `osint.src_url`, the ATT&CK techniques in
`osint.attacks`, the Lockheed Martin kill chain phases in `osint.kill_chain`,
and the rule name in `osint.related_analytics`. For Sigma rules, the analytic
also carries the Sigma rule ID. The required `osint.value` stays null, because
a detection rule has no single observable value.

## Run the Sigma rules

`examples/update-sigma-rules.tql` walks the feed daily and keeps the rule
files and the catalog current:

```tql
cron "0 0 6 * * *" {
  truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL")
  fork {
    truepattern::sigma::update_rules path="/var/lib/tenzir/truepattern/sigma-windows-security.yaml",
      logsource={product: "windows", service: "security"}
    discard
  }
  truepattern::sigma::update_rules path="/var/lib/tenzir/truepattern/sigma.yaml"
  truepattern::ocsf::normalize
  truepattern::update_context
}
```

The walk writes two files: all rules, and the subset whose complete Sigma
`logsource` is `{product: "windows", service: "security"}`. The latter excludes
rules with a category or any other logsource constraint. It is a subset of the
complete file, so the catalog only needs the rules of the complete file. A
successful complete walk without any qualifying rule writes an empty YAML
stream to the corresponding file, and `sigma` clears obsolete rules on reload.

The optional `product="windows"` filter selects all Windows rules, but does
not make them safe for native matching across Windows services or categories.
Use the exact `logsource` filter with a correspondingly scoped event source.

`truepattern::sigma::update_rules` writes the latest Sigma rules into one
multi-document YAML file, one document per rule. It removes a leading document
marker and a final document end marker, but keeps comments and notices,
including comments attached to those markers. When supplied, it adds the STIX
external references as a JSON-encoded YAML comment on the rule, preserving
source and license references and their descriptions. It skips these kinds of
rules:

- Rules with invalid YAML, so the published snapshot contains only valid YAML
  documents.
- Rules with several YAML documents, such as correlation rules. The operator
  warns about each one.
- Older rules that share a Sigma rule ID with a more recently modified rule,
  because the `sigma` operator ignores every rule with a duplicate ID. Forks of
  the same upstream rule can share an ID.

`examples/detect-with-sigma-rules.tql` reads an OCSF NDJSON export and writes
enriched findings to NDJSON files:

```tql
from_file "/var/log/ocsf/events.ndjson" {
  read_ndjson
}
sigma path="/var/lib/tenzir/truepattern/sigma.yaml"
truepattern::enrich
to_file "/var/lib/tenzir/truepattern/findings/ocsf-{uuid}.ndjson" {
  write_ndjson
}
```

Run the rule update first to populate the rule files and catalog. Adapt the
example paths to files accessible to the executing node, with readable inputs
and writable output directories. These file-based detection examples process
an export once. To process new OCSF exports continuously, use
`from_file "/var/log/ocsf/*.ndjson", watch=10s` with the same `read_ndjson`
subpipeline. This watches for new files; it does not tail an appended file.
Keep `sigma` and `truepattern::enrich` between your source and destination.
The `{uuid}` filenames keep separate runs and rotated files from overwriting
one another.

The `sigma` operator skips rules that use fields without an OCSF equivalent
and warns once per rule. See [Check Sigma rule compatibility with
OCSF](https://tenzir.com/docs/guides/detect/check-sigma-rule-compatibility-with-ocsf)
for the supported log sources.

### Choose between OCSF and native Windows events

You can run the rules in two ways:

- On OCSF events, as `examples/detect-with-sigma-rules.tql` shows. This works
  across sources, but covers only the rules whose fields Tenzir's Sigma-to-OCSF
  translation supports today.
- On native Windows event logs, as `examples/detect-in-windows-event-logs.tql`
  shows, selecting Security-channel auditing events from XML and writing
  findings to NDJSON. This example only runs rules scoped exactly to the
  Windows Security service, without category or other logsource constraints.
  It deliberately does not run the complete set of Windows rules.

For native events, first select the matching channel and provider. Then lift
`System` and `EventData` to the top level and add `Provider_Name`, which Windows
rules use for the event provider:

```tql
from_file "/var/log/windows/events.xml" {
  read_delimited "</Event>\n", include_separator=true
}
this = data.parse_winlog()
where System.Channel? == "Security"
where System.Provider.Name? == "Microsoft-Windows-Security-Auditing"
this = {...System, Provider_Name: System.Provider.Name?, ...EventData}
sigma path="/var/lib/tenzir/truepattern/sigma-windows-security.yaml"
truepattern::enrich
to_file "/var/lib/tenzir/truepattern/findings/windows-{uuid}.ndjson" {
  write_ndjson
}
```

Without OCSF, `sigma` does not check a rule's `logsource`. Product-only
filtering is insufficient: event IDs can collide across services, and negated
conditions can match unrelated events with absent fields. Keep the exact rule
logsource and event filters aligned. To support other services or categories,
create separate rule files and event pipelines that enforce their complete
logsource constraints; don't feed mixed Windows events to a product-only file.

### Keep the rule file complete

The walk replaces the file with the rules of its input, so only run
`truepattern::sigma::update_rules` on a complete walk. A poll with
`added_after` returns only the new versions, and writing them would remove all
other rules. To pick up Sigma rule changes sooner, run the walk more often
than daily, such as every few hours; it only takes a handful of requests.

The HTTP client retries transient failures, including HTTP `429` and `5xx`
responses, within the same walk. A non-retryable HTTP error, exhausted retries,
a malformed page, or missing pagination continuation fails the walk and leaves
the rule file and the catalog untouched; the next scheduled walk tries again.
An incomplete walk must not be treated as an empty collection.

After a successful complete walk, `truepattern::sigma::update_rules` rewrites
the file in place, even when no rules qualify, and `truepattern::update_context`
updates the catalog alongside. Neither step is transactional: `to_file` does
not publish files atomically, so `sigma` can observe an empty or partially
written file during replacement, and the file and the catalog can briefly
disagree. Atomic same-filesystem renames in `from_file` do not change this
writer's behavior. A malformed or unreadable Sigma source retains its
last-known-good rules; a readable empty source intentionally clears them.

## Enrich findings

A Sigma Detection Finding carries the Sigma rule ID in
`finding_info.analytic.uid`. Every rule in the file is a single document, and
no two rules share a Sigma rule ID, so `truepattern::update_context` stores
exactly one entry per rule in the `truepattern-sigma-rules` lookup table, keyed
by that ID. `truepattern::enrich` looks up the ID and adds:

- The rule's OCSF `osint` object to `osint`, with the TruePattern ID in
  `external_uid`, the change analysis in `desc`, the upstream rule in
  `src_url`, and the ATT&CK techniques in `attacks`.
- The rule license to `unmapped.truepattern.license`, with the license `name`
  and `url`.
- The full supplied rule text and external references to
  `unmapped.truepattern.rule_text` and `unmapped.truepattern.external_references`.
  These retain attribution and notices, including YAML comments that the
  parsed rule in `policy.data` does not retain. This also increases finding size.

Sigma rules without an ID get no catalog entry, so their findings stay
unenriched.

## Route rules in other formats

Tenzir does not execute Splunk, KQL, YARA, Sublime Security, and the other
formats. `examples/route-new-rules.tql` polls for new rule versions every hour
and archives them as OCSF NDJSON files by format. The files retain the rule
text, metadata, and license references; they do not install rules in Splunk,
Sentinel, or other engines. Replace each file sink with your deployment
integration as needed, after evaluating the applicable terms. Every output
branch, including the fallback for other formats, routes rules regardless of
whether license metadata is present:

```tql
cron "0 0 * * * *" {
  truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL"), added_after=now() - 2h
  truepattern::latest
  where pattern_type != "sigma"
  truepattern::ocsf::normalize
  match osint[0].detection_pattern_type {
    "splunk" => {
      to_file "/var/lib/tenzir/truepattern/rules/splunk/{uuid}.ndjson" {
        write_ndjson
      }
    }
    "kql" | "sentinel" => {
      to_file "/var/lib/tenzir/truepattern/rules/kql/{uuid}.ndjson" {
        write_ndjson
      }
    }
    "yara" => {
      to_file "/var/lib/tenzir/truepattern/rules/yara/{uuid}.ndjson" {
        write_ndjson
      }
    }
    _ => {
      to_file "/var/lib/tenzir/truepattern/rules/other/{uuid}.ndjson" {
        write_ndjson
      }
    }
  }
}
```

TruePattern currently imports new rules daily, so polling every hour picks up
changes promptly. Each poll looks back two hours, which covers a failed poll
but makes consecutive windows overlap. A poll can therefore deliver a rule
version that an earlier poll already delivered, so key downstream consumers on
the STIX `id` and `modified` time.

## Test the package

Use `tenzir-test` 2.3.1 or later. From the library root, select both the CLI
and node from the validated stable Tenzir 6.20.0 distribution:

```sh
TENZIR_BINARY='uvx --from tenzir==6.20.0 tenzir' \
TENZIR_NODE_BINARY='uvx --from tenzir==6.20.0 tenzir-node' \
uvx --refresh 'tenzir-test>=2.3.1' truepattern stix
```

To test a different build containing the engine fixes listed earlier, set
both variables to its CLI and node binaries.

The runner loads each test's enclosing package automatically, including for
Python tests. Keep the `package-dirs` declaration in `tests/test.yaml`: it loads
the separate `stix` dependency. You don't need to set `TENZIR_PACKAGE_DIRS`
manually.

## Respect rule licenses

Upstream rules retain their original licenses, such as the Detection Rule
License (DRL) 1.1, Apache 2.0, MIT, or GPL. A TruePattern subscription does not
expand those permissions. According to TruePattern's clarification, active
subscribers may ingest and use content in workflows, including MDR/MSSP
services within their subscription scope; customers connect their own
subscriptions. Resale or bundling requires a separate written agreement.
These subscription terms do not replace the upstream licenses.

Where available, a `rule-vendor-license` external reference identifies the
license in `external_id` and links its text in `url`; a `rule-source` reference
links the upstream rule. This metadata is informational: its presence or
absence does not determine which rules the package executes or routes.

**A populated license field does not grant permission.** The package does not
validate license texts, resolve conflicting references, or decide whether
execution, modification, redistribution, or deployment is permitted for your
use case. Evaluate and honor the actual upstream terms and your subscription
scope when using these pipelines. API access does not override third-party
terms.

Keep source attribution and required notices when storing, transforming, or
forwarding rules and findings. The supported transforms preserve the supplied
rule text and external references; they do not fetch linked license files or
other repository notices. Obtain and carry any additional notices or license
texts that the actual terms require, including in custom deployment adapters.

The incremental routing example does not retract previously exported or
deployed rules. Existing catalog entries expire under `max_age`; the catalog
is enrichment metadata, not an execution or permission allowlist.
