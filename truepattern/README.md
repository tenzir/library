# TruePattern

[TruePattern](https://truepattern.io) curates detection rules from public and
commercial rule repositories, with change analysis, ATT&CK techniques, and
license information for every rule. It publishes the rules as a STIX 2.1
collection over TAXII. Each rule is a STIX Indicator that carries the native
rule text in `pattern` and its language, such as `sigma`, `splunk`, `kql`,
`yara`, or `sublime-security`, in `pattern_type`.

This package runs the Sigma rules on your events with the `sigma` operator,
enriches the resulting findings with TruePattern's rule metadata, and
routes the rules in other formats to the systems that run them.

## Architecture

Two pipelines work together. A scheduled pipeline walks the feed and writes
all current Sigma rules into one file, and it records their metadata in a rule
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

The package requires the `stix` package and a Tenzir build that includes the
empty Sigma source and HTTP retry fixes (tenzir/mono#771 and tenzir/mono#772).
The published Tenzir 6.20.0-rc.3 predates these fixes: it retains obsolete rules
when a source becomes empty and fails transient HTTP retries under `strict`.
Tenzir 6.19.1 can also assert on malformed Sigma YAML. No minimum engine
version is enforced by the package manifest.

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
    truepattern::sigma::update_rules path="/var/lib/tenzir/truepattern/sigma-windows.yaml",
      product="windows"
    discard
  }
  truepattern::sigma::update_rules path="/var/lib/tenzir/truepattern/sigma.yaml"
  truepattern::ocsf::normalize
  truepattern::update_context
}
```

The walk writes two files: all rules, and with `product="windows"` only the
rules whose Sigma `logsource.product` is `windows`. The Windows file is a
subset of the complete file, so the catalog only needs the rules of the
complete file. A successful complete walk without any qualifying rule writes
an empty YAML stream to the corresponding file. If the last Windows rule
leaves the feed or changes its product, `sigma` clears the obsolete Windows
rules on reload, so they no longer fire.

`truepattern::sigma::update_rules` writes the latest version of every Sigma
rule into one multi-document YAML file, one document per rule. It removes a
leading preamble of blank lines, comments, and a document marker from each
rule, as well as a final document end marker, and it skips three kinds of
rules:

- Rules with invalid YAML, because one invalid document makes the `sigma`
  operator ignore the complete file.
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
  shows, reading XML from a file and writing findings to NDJSON. Most
  TruePattern Sigma rules are Windows rules, and they name the
  fields of the native events, so practically all of them run after one
  reshaping step. This only works for Windows rules.

For native events, lift `System` and `EventData` of the parsed event to the
top level, and add `Provider_Name`, which Windows rules use for the event
provider:

```tql
from_file "/var/log/windows/events.xml" {
  read_delimited "</Event>\n", include_separator=true
}
this = data.parse_winlog()
this = {...System, Provider_Name: System.Provider.Name?, ...EventData}
sigma path="/var/lib/tenzir/truepattern/sigma-windows.yaml"
truepattern::enrich
to_file "/var/lib/tenzir/truepattern/findings/windows-{uuid}.ndjson" {
  write_ndjson
}
```

Only give native events the Windows file. Without OCSF, the `sigma` operator
does not check a rule's `logsource`, and an absent field never matches, so a
rule for another product with a negated condition fires on every Windows
event.

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

Sigma rules without an ID get no catalog entry, so their findings stay
unenriched.

## Route rules in other formats

Tenzir does not execute Splunk, KQL, YARA, Sublime Security, and the other
formats. `examples/route-new-rules.tql` polls for new rule versions every hour
and archives them as OCSF NDJSON files by format. The files retain the rule
text, metadata, and license references; they do not install rules in Splunk,
Sentinel, or other engines. Replace each file sink with your deployment
integration as needed:

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

Use `tenzir-test` 2.3.1 or later and a Tenzir build containing the engine fixes
listed earlier. From the library root, select both the CLI and node binaries
from that build:

```sh
TENZIR_BINARY=/path/to/build/bin/tenzir \
TENZIR_NODE_BINARY=/path/to/build/bin/tenzir-node \
uvx --refresh 'tenzir-test>=2.3.1' truepattern stix
```

The runner loads each test's enclosing package automatically, including for
Python tests. Keep the `package-dirs` declaration in `tests/test.yaml`: it loads
the separate `stix` dependency. You don't need to set `TENZIR_PACKAGE_DIRS`
manually.

## Respect rule licenses

TruePattern redistributes rules from third-party repositories under their
original licenses, such as the Detection Rule License (DRL) 1.1, Apache 2.0,
MIT, or GPL. Each rule names its license in an external reference with the
source name `rule-vendor-license`, with the license name in `external_id` and
its text in `url`, and links its upstream source with the source name
`rule-source`. Keep this attribution when you store, forward, or modify rules.
A rule without a license reference does not grant any permission.
