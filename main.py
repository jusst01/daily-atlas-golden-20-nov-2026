#!/usr/bin/env python3
"""Submitted entrypoint for make.fun news-image-20261120.

Standard library only.  Deploys the bundled entry.png into
$MAKEFUN_OUTPUT_DIR (default /output) via a staged copy + atomic rename.
"""

import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
NAME = "entry.png"
MAX_BYTES = 1024 * 1024


def die(msg):
    sys.stderr.write("main.py: ERROR: %s\n" % msg)
    raise SystemExit(1)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"

    if not os.path.isfile(SRC):
        die("bundled image not found: %s" % SRC)
    src_size = os.path.getsize(SRC)
    if src_size == 0:
        die("bundled image is empty: %s" % SRC)
    if src_size > MAX_BYTES:
        die("bundled image is %d bytes, over the 1 MiB limit" % src_size)
    with open(SRC, "rb") as fh:
        if fh.read(4) != b"\x89PNG":
            die("bundled image is not a PNG: %s" % SRC)

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        die("cannot create output directory %r: %s" % (out_dir, exc))

    dest = os.path.join(out_dir, NAME)
    staged = None
    try:
        fd, staged = tempfile.mkstemp(prefix=".entry-", suffix=".png.tmp", dir=out_dir)
        with os.fdopen(fd, "wb") as out:
            with open(SRC, "rb") as src:
                shutil.copyfileobj(src, out, 1024 * 256)
            out.flush()
            os.fsync(out.fileno())

        staged_size = os.path.getsize(staged)
        if staged_size != src_size:
            die("size mismatch after copy: staged=%d source=%d" % (staged_size, src_size))

        # mkstemp makes 0600 and os.replace keeps the mode; the grader reads as
        # a different user, so widen to 0644 before the rename goes live.
        os.chmod(staged, 0o644)
        os.replace(staged, dest)
        staged = None
    except OSError as exc:
        die("failed to deploy %s: %s" % (dest, exc))
    finally:
        if staged is not None and os.path.exists(staged):
            try:
                os.unlink(staged)
            except OSError:
                pass

    if os.path.getsize(dest) != src_size:
        die("deployed size %d != source size %d" % (os.path.getsize(dest), src_size))

    sys.stdout.write("wrote %s (%d bytes)\n" % (dest, src_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
