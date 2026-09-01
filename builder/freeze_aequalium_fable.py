#!/usr/bin/env python3
"""
freeze_aequalium_fable.py -- one-shot freezer for Fable's AEQUALIUM v2.3..v2.4.3.
KERNELIC_MAGIC compliant: ASCII-only source, one script one run (Path VI).

Fable delivered standalone HTML (kernel embedded verbatim). We freeze each as its
own immutable shell/ artifact (Path X) after healing a Curse-25 escape leak:
literal \\uXXXX sequences that leaked into VISIBLE HTML TEXT (they render as the
raw backslash-u text, not the glyph). We heal ONLY text nodes (between > and <)
in non-<script>/<style> regions, so real JS string escapes are never touched.

We never TYPE a unicode glyph here (Curse 2) -- we decode the \\uXXXX numerically.
Normalize CRLF->LF, write utf-8 newline='\\n', no BOM.
"""
import re
from pathlib import Path

SRC = Path(r"C:\Users\vladi\Downloads")
DST = Path(__file__).parent.parent / "shell"

MAP = {
    "shell__aequalium_v2_3.html":   "aequalium_v2.3.html",
    "shell__aequalium_v2_4.html":   "aequalium_v2.4.html",
    "shell__aequalium_v2_4_1.html": "aequalium_v2.4.1.html",
    "shell__aequalium_v2_4_2.html": "aequalium_v2.4.2.html",
    "shell__aequalium_v2_4_3.html": "aequalium_v2.4.3.html",
}

UESC  = re.compile(r"\\u([0-9a-fA-F]{4})")
BLOCK = re.compile(r"(?is)<(script|style)\b.*?</\1>")
TEXT  = re.compile(r">([^<]*)<")


def _decode(m):
    return chr(int(m.group(1), 16))


def _fix_text(m):
    return ">" + UESC.sub(_decode, m.group(1)) + "<"


def freeze(src_name, dst_name):
    raw = (SRC / src_name).read_bytes().decode("utf-8")
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")   # normalize first

    before = len(UESC.findall(raw))

    blocks = []

    def stash(m):
        blocks.append(m.group(0))
        return "\x00B%d\x00" % (len(blocks) - 1)

    masked = BLOCK.sub(stash, raw)          # protect JS/CSS escapes
    healed = TEXT.sub(_fix_text, masked)    # heal only text-node escapes
    for i, b in enumerate(blocks):
        healed = healed.replace("\x00B%d\x00" % i, b)

    after = len(UESC.findall(healed))       # remaining are legit JS-context escapes

    (DST / dst_name).write_text(healed, encoding="utf-8", newline="\n")
    print("  %-22s <- %-30s  esc(all)=%d text-healed=%d js-left=%d"
          % (dst_name, src_name, before, before - after, after))


def main():
    print("Freezing Fable's AEQUALIUM lineage into shell/ (Curse-25 heal on text nodes):")
    for s, d in MAP.items():
        freeze(s, d)
    print("done. verify with a byte scan + browser.")


if __name__ == "__main__":
    main()
