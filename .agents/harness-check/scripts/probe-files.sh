#!/usr/bin/env bash
# Probe: full file lifecycle — create, read, modify, rename, delete, and the
# failure modes that matter. Writes only inside $HARNESS_CHECK_DIR.
set -uo pipefail
. "$(dirname "$0")/_lib.sh"
sandbox

SENTINEL="harness-check-sentinel-42"
F="probe.txt"
rm -rf "$HARNESS_CHECK_DIR"/* 2>/dev/null

# 1. create
printf 'line one\nline two\n%s\n' "$SENTINEL" > "$F"
[ -f "$F" ] && pass files.create "$HARNESS_CHECK_DIR/$F" || fail files.create "file not created"

# 2. read
check files.read "$SENTINEL" "$(sed -n '3p' "$F")"

# 3. modify in place
sed -i 's/line one/line ONE/' "$F"
check files.modify.inplace "line ONE" "$(head -n1 "$F")"

# 4. modify by append
echo "appended" >> "$F"
check files.modify.append "4" "$(wc -l < "$F" | tr -d ' ')"

# 5. modify by full rewrite (heredoc)
cat > "$F" <<INNER
rewritten
$SENTINEL
INNER
check files.modify.rewrite "rewritten" "$(head -n1 "$F")"

# 6. permissions are readable/writable
[ -r "$F" ] && [ -w "$F" ] && pass files.perms "rw ok" || fail files.perms "not rw"

# 7. nested directory creation
mkdir -p nested/deep && echo hi > nested/deep/x.txt
check files.mkdir "hi" "$(cat nested/deep/x.txt 2>/dev/null)"

# 8. rename / move
mv "$F" renamed.txt
{ [ -f renamed.txt ] && [ ! -f "$F" ]; } && pass files.rename "" || fail files.rename "move failed"

# 9. write to a missing parent must fail
if ( echo x > no/such/dir/file.txt ) 2>/dev/null; then
  fail files.badparent "wrote into a nonexistent directory"
else
  pass files.badparent "correctly refused"
fi

# 10. delete
rm -f renamed.txt
[ ! -f renamed.txt ] && pass files.delete "" || fail files.delete "still present"

# 11. read after delete must fail
if cat renamed.txt >/dev/null 2>&1; then
  fail files.readdeleted "read a deleted file"
else
  pass files.readdeleted "correctly errored"
fi

# 12. recursive delete
rm -rf nested
[ ! -d nested ] && pass files.rmdir "" || fail files.rmdir "directory survived"

# leave one artifact behind for the dedicated Read/Edit/Glob/Grep tool probes
printf 'tool probe file\n%s\nreplace-me\n' "$SENTINEL" > tool-probe.txt

summary files
