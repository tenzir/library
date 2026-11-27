This release fixes demo feeds so they report live ongoing ingress event throughput instead of dropping to zero after the initial download.

## 🐞 Bug fixes

### Ongoing ingress throughput for demo feeds

Replayed events from `demo::zeek`, `demo::suricata`, `demo::openssh`, `demo::windows`, `demo::claude_code`, and `demo::codex` now report ongoing ingress event throughput instead of dropping to zero after the initial download. Each feed still downloads its recording once at startup without inflating ingress byte counts.

*By @mavam in #280.*
