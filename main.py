#!/usr/bin/env python3
"""Copy entry.png to the make.fun output directory (stdlib only).

No network access. The output is a byte-for-byte copy of the bundled
image, so repeated runs are deterministic.
"""

import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SOURCE_NAME)
    with open(src, "rb") as handle:
        header = handle.read(len(PNG_MAGIC))
    if header != PNG_MAGIC:
        print(f"error: {src} is not a valid PNG file", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, SOURCE_NAME)
    shutil.copyfile(src, dest)
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
