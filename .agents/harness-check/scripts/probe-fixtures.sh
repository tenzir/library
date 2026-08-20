#!/usr/bin/env bash
# Generate fixtures for the NATIVE TOOL probes. This script deliberately does
# not test anything itself — Bash cannot exercise Read/Write/Edit/NotebookEdit.
# It only lays out the material those tools are pointed at.
#
# See reference/agent-probes.md for the checklist that consumes these.
set -uo pipefail
. "$(dirname "$0")/_lib.sh"
sandbox

FIX="$HARNESS_CHECK_DIR/fixtures"
rm -rf "$FIX"
mkdir -p "$FIX/subdir"

S="harness-check-sentinel-42"

# --- text ------------------------------------------------------------------
printf 'first line\n%s\nlast line\n' "$S" > "$FIX/plain.txt"

# 200 numbered lines, for offset/limit windowing
awk 'BEGIN { for (i = 1; i <= 200; i++) printf "line %03d\n", i }' > "$FIX/long.txt"

: > "$FIX/empty.txt"

# exactly one occurrence — the uniqueness path
printf 'alpha\nreplace-me-once\nomega\n' > "$FIX/edit-unique.txt"

# three identical occurrences — the replace_all path
printf 'dup\ndup\ndup\n' > "$FIX/edit-multi.txt"

# pre-existing and NOT read by the agent — the clobber-protection path
printf 'pre-existing content that must not be silently destroyed\n' > "$FIX/clobber.txt"

# a file to delete out from under the agent
printf 'about to vanish\n' > "$FIX/vanishing.txt"

echo "nested" > "$FIX/subdir/nested.txt"

# --- binary and structured -------------------------------------------------
python3 - "$FIX" <<'PY'
import json, os, struct, sys, zlib

fix = sys.argv[1]

# 8x8 red PNG, hand-rolled so no image library is required
def chunk(tag, data):
    body = tag + data
    return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)

w = h = 8
raw = b''.join(b'\x00' + bytes([220, 40, 40] * w) for _ in range(h))
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(raw))
       + chunk(b'IEND', b''))
open(os.path.join(fix, 'pixel.png'), 'wb').write(png)

# minimal 2-page PDF with distinct text per page, xref computed exactly
def pdf(pages):
    objs, kids = [], []
    n_pages = len(pages)
    for i, text in enumerate(pages):
        pid, cid = 3 + i * 2, 4 + i * 2
        kids.append(pid)
        objs.append((pid, f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] "
                         f"/Contents {cid} 0 R /Resources << /Font << /F1 {3 + n_pages * 2} 0 R >> >> >>"))
        stream = f"BT /F1 12 Tf 20 50 Td ({text}) Tj ET"
        objs.append((cid, f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"))
    objs.append((3 + n_pages * 2, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))
    objs.insert(0, (2, "<< /Type /Pages /Kids [" + " ".join(f"{k} 0 R" for k in kids) + f"] /Count {n_pages} >>"))
    objs.insert(0, (1, "<< /Type /Catalog /Pages 2 0 R >>"))

    out, offsets = bytearray(b"%PDF-1.4\n"), {}
    for num, body in sorted(objs):
        offsets[num] = len(out)
        out += f"{num} 0 obj\n{body}\nendobj\n".encode()
    start = len(out)
    top = max(offsets) + 1
    out += f"xref\n0 {top}\n0000000000 65535 f \n".encode()
    for num in range(1, top):
        out += f"{offsets.get(num, 0):010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {top} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    return bytes(out)

open(os.path.join(fix, 'doc.pdf'), 'wb').write(
    pdf(["PDF page one harness-check", "PDF page two harness-check"]))

# Jupyter notebook with a stored output
nb = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# harness-check notebook\n"]},
        {"cell_type": "code", "execution_count": 1, "metadata": {},
         "source": ["print('notebook-cell-output')\n"],
         "outputs": [{"output_type": "stream", "name": "stdout",
                      "text": ["notebook-cell-output\n"]}]},
        {"cell_type": "code", "execution_count": None, "metadata": {},
         "source": ["replace-this-cell\n"], "outputs": []},
    ],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
    "nbformat": 4, "nbformat_minor": 5,
}
json.dump(nb, open(os.path.join(fix, 'notebook.ipynb'), 'w'), indent=1)
PY

# --- verify what we produced ----------------------------------------------
expect() {
  if [ -e "$FIX/$1" ]; then
    pass "fixture.$1" "$(wc -c < "$FIX/$1" | tr -d ' ') bytes"
  else
    fail "fixture.$1" "not generated"
  fi
}
for f in plain.txt long.txt empty.txt edit-unique.txt edit-multi.txt \
         clobber.txt vanishing.txt subdir/nested.txt pixel.png doc.pdf \
         notebook.ipynb; do
  expect "$f"
done

# structural sanity so a broken fixture is not misread as a broken tool
head -c 8 "$FIX/pixel.png" | grep -q 'PNG' && pass fixture.png.magic "" || fail fixture.png.magic "bad header"
head -c 8 "$FIX/doc.pdf"   | grep -q '%PDF'  && pass fixture.pdf.magic "" || fail fixture.pdf.magic "bad header"
python3 -c "import json,sys; json.load(open('$FIX/notebook.ipynb'))" 2>/dev/null \
  && pass fixture.ipynb.valid "" || fail fixture.ipynb.valid "invalid JSON"
check fixture.long.lines "200" "$(wc -l < "$FIX/long.txt" | tr -d ' ')"
check fixture.empty.size "0"   "$(wc -c < "$FIX/empty.txt" | tr -d ' ')"

echo
echo "fixtures at: $FIX"
summary fixtures
