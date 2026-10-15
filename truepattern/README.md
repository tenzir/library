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
catalog. A long-running pipeline matches your events against that file and
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

The package requires the `stix` package.

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

`examples/update-sigma-rules.tql` walks the feed daily and keeps both the rule
file and the catalog current:

```tql
cron "0 0 6 * * *" {
  truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL")
  truepattern::sigma::update_rules path="/var/lib/tenzir/truepattern/sigma.yaml"
  truepattern::ocsf::normalize
  truepattern::update_context
}
```

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

`examples/detect-with-sigma-rules.tql` runs the rules on your OCSF events:

```tql
subscribe "ocsf"
sigma path="/var/lib/tenzir/truepattern/sigma.yaml"
truepattern::enrich
publish "truepattern-findings"
```

The `sigma` operator skips rules that use fields without an OCSF equivalent
and warns once per rule. See [Check Sigma rule compatibility with
OCSF](https://tenzir.com/docs/guides/detect/check-sigma-rule-compatibility-with-ocsf)
for the supported log sources.

### Keep the rule file complete

The walk replaces the file with the rules of its input, so only run
`truepattern::sigma::update_rules` on a complete walk. A poll with
`added_after` returns only the new versions, and writing them would remove all
other rules. To pick up Sigma rule changes sooner, run the walk more often
than daily, such as every few hours; it only takes a handful of requests.

A walk fails on the first HTTP error or malformed page and leaves the rule file
and the catalog untouched; the next scheduled walk tries again. After a
complete walk, `truepattern::sigma::update_rules` rewrites the file in place,
and `truepattern::update_context` updates the catalog alongside. Neither step
is transactional: the `sigma` operator can read a partially written file, and
the file and the catalog can briefly disagree.

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
and publishes them per format, so that other pipelines can deploy them:

```tql
cron "0 0 * * * *" {
  truepattern::feed credential=secret("TRUEPATTERN_CREDENTIAL"),
    added_after=now() - 2h
  truepattern::latest
  truepattern::ocsf::normalize
  if osint[0].detection_pattern_type == "splunk" {
    publish "truepattern-splunk"
  } else if osint[0].detection_pattern_type in ["kql", "sentinel"] {
    publish "truepattern-kql"
  } else if osint[0].detection_pattern_type == "yara" {
    publish "truepattern-yara"
  } else {
    publish "truepattern-other"
  }
}
```

TruePattern currently imports new rules daily, so polling every hour picks up
changes promptly. Each poll looks back two hours, which covers a failed poll
but makes consecutive windows overlap. A poll can therefore deliver a rule
version that an earlier poll already delivered, so key downstream consumers on
the STIX `id` and `modified` time.

## Respect rule licenses

TruePattern redistributes rules from third-party repositories under their
original licenses, such as the Detection Rule License (DRL) 1.1, Apache 2.0,
MIT, or GPL. Each rule names its license in an external reference with the
source name `rule-vendor-license`, with the license name in `external_id` and
its text in `url`, and links its upstream source with the source name
`rule-source`. Keep this attribution when you store, forward, or modify rules.
A rule without a license reference does not grant any permission.
