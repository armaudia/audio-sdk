#!/usr/bin/env python3
"""Create a normalized gzip/tar and per-file SHA-256 manifest."""
from __future__ import annotations

import gzip
import hashlib
import io
import pathlib
import sys
import tarfile


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: create_archive.py <source-dir> <archive>", file=sys.stderr)
        return 2
    root = pathlib.Path(sys.argv[1])
    archive_path = pathlib.Path(sys.argv[2])
    files = sorted(path for path in root.rglob("*") if path.is_file())
    manifest = []
    for path in files:
        relative = path.as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.append(f"{digest}  {relative}\n")
    (archive_path.parent / "audio-sdk-0.1.0.files.sha256").write_text(
        "".join(manifest), encoding="ascii"
    )
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|") as archive:
                for path in files:
                    data = path.read_bytes()
                    info = tarfile.TarInfo(path.as_posix())
                    info.size = len(data)
                    info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    archive.addfile(info, io.BytesIO(data))
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    (archive_path.parent / f"{archive_path.name}.sha256").write_text(
        f"{digest}  {archive_path.name}\n", encoding="ascii"
    )
    print(f"sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
