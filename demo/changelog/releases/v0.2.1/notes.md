This release lets pipelines with a demo feed stop within seconds.

## 🐞 Bug fixes

### Stoppable demo feeds

Pipelines with a demo feed now stop within seconds instead of staying in **Stopping**. Events come one to three seconds after their time, and a replay cycle can last up to a day.

*By @zedoraps in #268.*

### Unset times in Zeek NTP events

`demo::zeek` keeps unset NTP times at 1970-01-01T00:00:00Z instead of moving them by hours.

*By @zedoraps in #268.*
