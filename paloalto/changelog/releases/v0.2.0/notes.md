Traffic records from PAN-OS versions before 11.1 parse without warnings. The OCSF mapping also carries the PAN-OS repeat count, no longer treats session ID 0 as a connection, and leaves empty fields out of `unmapped`.

## 🔧 Changes

### Repeat counts, session IDs, and empty fields in PAN-OS events

The OCSF mapping represents three PAN-OS values more accurately:

- The repeat count becomes `count`, instead of staying in `unmapped`.
- Session ID 0, which PAN-OS writes when it created no session, no longer becomes `connection_info.uid` and stays in `unmapped`.
- Empty PAN-OS fields no longer appear as null fields in `unmapped`.

*By @zedoraps.*

## 🐞 Bug fixes

### Traffic records from older PAN-OS versions without warnings

Traffic records with fewer columns than the current layout, such as the 115 columns that PAN-OS writes before 11.1, parse without a `csv parser found too few values` warning. Records shorter than the 65 columns of PAN-OS 8.1 keep the warning.

*By @zedoraps.*
