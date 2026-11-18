This release adds credential stuffing detection for OCSF HTTP Activity and Authentication events. Both operators report attacking source networks as OCSF Detection Findings and escalate when a login from the attacker succeeds.

## 🚀 Features

### Credential stuffing detection

Two new operators detect credential stuffing and report each attacking source as an OCSF Detection Finding:

- `tenzir::detect::http::credential_stuffing` reads OCSF HTTP Activity, such as CDN, WAF, or web server logs. It counts failed logins against your login endpoints per source network and reports a source when at least 50 failures in five minutes make up at least 90% of its failed and successful logins. Configure the login endpoints with `paths` and the response codes that mean a failed login with `failure_codes`.
- `tenzir::detect::authentication::credential_stuffing` reads OCSF Authentication from identity providers and hosts. It reports a source when at least 20 failed logons across at least 10 accounts in ten minutes make up at least 80% of its logons, which separates credential stuffing and password spraying from a forgotten password.

Both operators group IPv6 sources by `/64`, so an attacker who rotates addresses within one prefix stays one source. Successful logins from a reported source raise the severity to high, because they indicate credentials that worked. For identity providers that log several events per sign-in, such as Okta, keep one event per attempt:

```tql
okta::fetch "example.okta.com", bearer_token=secret("okta-bearer-token")
okta::ocsf::normalize
where metadata.event_code == "user.session.start"
tenzir::detect::authentication::credential_stuffing
to_splunk "https://splunk.example.com:8088", hec_token=secret("splunk-hec-token")
```

The operator descriptions list the known false negatives and false positives and how to tune the thresholds for your traffic.

*By @mavam in #239.*
