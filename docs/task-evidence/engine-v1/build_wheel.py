"""Build the third-party fixture wheel with offline stdlib tools only.

The archive is byte-reproducible: fixed entry order, fixed timestamps and
permissions, and a complete RECORD. No setuptools, wheel package, network or
build isolation is required. The wheel is installed with pip in the acceptance
probe, demonstrating an installed external fixture rather than an in-tree import.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "third_party" / "src" / "engine_v1_fixture"
NAME = "engine_v1_fixture"
VERSION = "0.1.0"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"
WHEEL_NAME = f"{NAME}-{VERSION}-py3-none-any.whl"
_FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def _record_line(path: str, data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
    return f"{path},sha256={digest},{len(data)}"


def build_wheel(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, bytes] = {}
    for source in sorted(SOURCE.glob("*.py")):
        payload[f"{NAME}/{source.name}"] = source.read_bytes()
    if not payload:
        raise RuntimeError("no third-party fixture sources")

    metadata = (
        "Metadata-Version: 2.1\n"
        f"Name: {NAME.replace('_', '-')}\n"
        f"Version: {VERSION}\n"
        "Summary: Model-free installed fixture for SDK-FND-ENGINE\n"
        "Requires-Python: >=3.11\n"
    ).encode("ascii")
    wheel_meta = (
        "Wheel-Version: 1.0\n"
        "Generator: sdk-fnd-engine-stdlib-wheel/0.1\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
    ).encode("ascii")
    payload[f"{DIST_INFO}/METADATA"] = metadata
    payload[f"{DIST_INFO}/WHEEL"] = wheel_meta
    record = [_record_line(path, data) for path, data in sorted(payload.items())]
    record.append(f"{DIST_INFO}/RECORD,,")
    payload[f"{DIST_INFO}/RECORD"] = ("\n".join(record) + "\n").encode("ascii")

    target = out_dir / WHEEL_NAME
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in sorted(payload.items()):
            info = zipfile.ZipInfo(path, date_time=_FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    wheel = build_wheel(args.out)
    print(f"{wheel}\nsha256:{hashlib.sha256(wheel.read_bytes()).hexdigest()}")
