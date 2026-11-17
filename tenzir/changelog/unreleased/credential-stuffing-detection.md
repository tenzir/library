---
title: Credential stuffing detection
type: feature
authors:
  - mavam
created: 2026-11-17T08:19:31.124409Z
---

Two new operators detect credential stuffing and report each attacking source as an OCSF Detection Finding:

- `tenzir::detect::http::credential_stuffing` reads OCSF HTTP Activity, such as CDN, WAF, or web server logs. It counts failed logins against your login endpoints per source network and reports a source when at least 50 failures in five minutes make up at least 90% of its failed and successful logins. Configure the login endpoints with `paths` and `methods`, and the response codes that mean a failed or successful login with `failure_codes` and `success_codes`.
- `tenzir::detect::authentication::credential_stuffing` reads OCSF Authentication from identity providers and hosts. It reports a source when at least 20 failed logons across at least 10 accounts in ten minutes make up at least 80% of its logons, which separates credential stuffing and password spraying from a forgotten password.

Both operators group IPv6 sources by `/64`, so an attacker who rotates addresses within one prefix stays one source. Successful logins from a reported source raise the severity to high, because they indicate credentials that worked:

```tql
subscribe "ocsf"
tenzir::detect::http::credential_stuffing paths=["/login", "/api/login"]
publish "findings"
```

The operator descriptions list the known false negatives and false positives and how to tune the thresholds for your traffic.
