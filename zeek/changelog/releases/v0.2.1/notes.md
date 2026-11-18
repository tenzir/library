This release makes Zeek event times independent of the Tenzir version by rounding them to the microsecond precision that Zeek logs.

## 🐞 Bug fixes

### Microsecond Zeek timestamps

Zeek events report their time and SMB file times with the microsecond precision that Zeek logs. Readers previously added floating-point noise below the microsecond, which differed between Tenzir versions, so the same Zeek log could normalize to slightly different times and notice finding UIDs. SMB file times from native JSON also become time values when only some of them are present.

*By @zedoraps in #242.*
