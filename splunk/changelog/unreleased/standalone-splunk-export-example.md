---
title: Standalone Splunk export example
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:17:14.979503Z
---

The Splunk package now ships the HTTP Event Collector workflow as an example
instead of installing a configured export pipeline.

Copy the example into your own deployment and provide the HEC endpoint, token,
index, and event settings explicitly. Installing the package no longer starts a
background Splunk export based on package inputs.
