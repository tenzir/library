## 💥 Breaking changes

### Geo Open context declared in the configuration

The package no longer ships a context, because packages can't contain contexts in Tenzir 7. Declare the `geo-open` GeoIP context in your configuration instead. It downloads the Geo Open database itself, so the update pipeline with `context_load` is gone:

```yaml
# contexts/geo-open.yaml
type: geoip
url: https://cra.circl.lu/opendata/geo-open/mmdb-country-asn/latest.mmdb
reload-interval: 1d
persist: true
```

The examples enrich events from it with `context_enrich "geo-open"`.

*By @mavam in #147 and #233.*
