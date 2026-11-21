---
title: Caption derivation for ID-only OCSF in the CIM mapping
type: change
authors:
  - zedoraps
created: 2026-11-20T19:34:01.217006Z
---

`splunk::cim::from_ocsf` derives missing OCSF captions from their IDs, so ID-only OCSF maps like derived OCSF.

- `signature`, protocol names in `authentication_method`, activity-based `action`, and other caption fields are filled.
- Matching captions and the caption of Other stay; contradicting captions or unknown IDs warn.
- Events without a derivable `metadata.version` map as before.
