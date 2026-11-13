#!/usr/bin/env python3
"""Recreate a Darwin static archive with zeroed member timestamps."""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: normalize_macos_archive.py <archive> <ar> <libtool>",
              file=sys.stderr)
        return 2
    archive = pathlib.Path(sys.argv[1]).resolve()
    ar, libtool = sys.argv[2:]
    with tempfile.TemporaryDirectory(prefix="audio-sdk-ar-") as temp_name:
        temporary = pathlib.Path(temp_name)
        subprocess.run([ar, "-x", str(archive)], cwd=temporary, check=True)
        objects = sorted(temporary.glob("*.o"), key=lambda path: path.name)
        if not objects:
            raise RuntimeError("static library contains no object members")
        filelist = temporary / "objects.list"
        filelist.write_text("".join(f"{path}\n" for path in objects),
                            encoding="utf-8")
        normalized = temporary / "normalized.a"
        subprocess.run(
            [libtool, "-static", "-D", "-o", str(normalized),
             "-filelist", str(filelist)],
            cwd=temporary,
            check=True,
        )
        archive_bytes = bytearray(normalized.read_bytes())
        # Apple's libtool -D zeroes object-member timestamps but leaves the
        # archive's __.SYMDEF header timestamp as the current time.
        if archive_bytes[:8] != b"!<arch>\n":
            raise RuntimeError("libtool produced an invalid archive")
        archive_bytes[24:36] = b"0           "
        normalized.write_bytes(archive_bytes)
        normalized.replace(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
