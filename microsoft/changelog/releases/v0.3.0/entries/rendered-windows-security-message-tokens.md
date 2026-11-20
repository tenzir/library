---
title: Rendered Windows Security message tokens
type: change
authors:
  - zedoraps
created: 2026-11-19T12:12:30.415081Z
---

Security event data now carries the text of message-table tokens, so Windows Event XML, Fluent Bit, and Winlogbeat produce the same event.

| Field | Before | Now |
|---|---|---|
| `unmapped.EventData.KernelDebug` (4826) | `%%1843` | `No` |
| `status_detail` (4625) | `%%2313` | `Unknown user name or bad password.` |
| `access_list` (4661, 4662) | `["%%1537"]` | `["DELETE"]` |
| `reg_value.type` (4657) | Not set | `REG_EXPAND_SZ` |
| 4719 `entity.policy.data` | `category_id: "%%8272"`, `changes: "%%8448"` | `category: "System"`, `changes: ["Success removed"]` |
| Winlogbeat 4657 activity | Unknown | Set, Modify, or Delete |

Free-text fields, such as command lines, and unknown tokens stay unchanged.

**What you need to do**

| Query | Effect | Replacement |
|---|---|---|
| Tests on a token, such as `%%1843` | Silent | Test the text, such as `No` |
| Tests on 4719 `category_id` or `subcategory_id` | Silent | Test `category` or `subcategory` |
| Tests on 4719 `changes` as a string | Silent | `"Success removed" in entity.policy.data.changes` |

**Why:** Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text.
