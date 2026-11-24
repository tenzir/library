---
title: Declare the `stix` dependency
type: bugfix
---

The `ismalicious` package now declares that it uses the `stix` package for
fetching and normalizing its TAXII feeds. Package managers install `stix`
alongside it, and Tenzir versions that let a package use only what it declares
accept it.
