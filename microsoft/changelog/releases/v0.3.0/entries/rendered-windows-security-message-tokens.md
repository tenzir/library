---
title: Rendered Windows Security message tokens
type: change
authors:
  - zedoraps
created: 2026-11-19T12:12:30.415081Z
---

The Windows normalizer now replaces the message-table tokens in Security events with the text that Windows renders, such as `No` for `%%1843`. Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text, so all collectors now produce the same event.

Only the event data fields that hold tokens change. Free-text fields, such as command lines and paths, stay unchanged even if they contain a token. Values that list several tokens, such as access rights, access reasons, or `UserAccountControl` flags, render each token and keep their separators, GUIDs, and SDDL strings. The texts are the en-US message strings of `msobjs.dll`. Unknown tokens stay unchanged, and Winlogbeat records rendered in another language keep that language.

For example, the Boot Configuration Data settings of 4826 now read `unmapped.EventData.KernelDebug: "No"`, so detections for test signing, kernel debugging, or disabled integrity checks can match on `"Yes"`. The rendered text also improves mapped fields:

- 4625 failure reasons in `status_detail`, such as `Unknown user name or bad password.`
- 4657 registry value types in `reg_value.type_id` and `reg_value.type`, such as `REG_EXPAND_SZ`. Unknown value types stay in `unmapped.EventData`.
- 4661 and 4662 access rights in `access_list`, such as `Read Property`.
- 4662 and 5136 directory operations in `entity.data.operation`, such as `Value Added`.
- 4719 audit policy categories, subcategories, and changes in `entity.policy.data`.

The 4719 fields in `entity.policy.data` have new names because they now hold names instead of tokens: `category_id` is now `category`, and `subcategory_id` is now `subcategory`. `changes` is now a list, such as `["Success Added", "Failure added"]`, instead of a comma-separated string. Update queries and detections that use the previous names. The subcategory GUID remains the policy's `uid`.

Winlogbeat records now also map 4657 registry operations to their activity instead of Unknown, and keep rendered access rights that contain spaces as one entry in `access_list`.
