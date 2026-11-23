#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Generate provider descriptors, provider config schemas and embedded C bytes.

Deterministic: descriptor bytes are canonical JSON (sorted keys, no spaces),
so the SHA-256 digests are reproducible from this script and the source tree.

Source digest recipe (documented for S01/S03): SHA-256 over the concatenation
of "<relative-path>\\0<sha256-hex>\\n" for every inventoried implementation
file, sorted by relative path. Text-file CRLF endings are normalized to LF so
the source identity does not depend on Git checkout settings.
"""
import hashlib
import json
import pathlib
import re
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true")
parser.add_argument("--catalog", type=pathlib.Path, help="also compare the installed built-in catalog")
args = parser.parse_args()
CHECK = args.check
if args.catalog and not CHECK:
    parser.error("--catalog requires --check")

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESCRIPTOR_SCHEMA = "audio-sdk/descriptor/0.1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_file(path):
    data = path.read_bytes()
    if b"\0" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def source_digest(paths):
    lines = []
    for rel in sorted(paths):
        digest = sha256_file(ROOT / rel)
        lines.append(rel.encode("ascii") + b"\0" + digest.encode("ascii") + b"\n")
    return "sha256:" + hashlib.sha256(b"".join(lines)).hexdigest()


def write(path, text):
    if CHECK:
        target = ROOT / path
        if not target.is_file() or target.read_bytes() != text.encode("ascii"):
            raise SystemExit(f"stale generated descriptor/configuration: {path}; run scripts/generate_descriptors.py")
        return
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_bytes(text.encode("ascii"))


def c_string(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


speex_sources = ["core/providers/speex/speex_provider.c"]
for path in sorted((ROOT / "third_party/speexdsp").rglob("*")):
    if path.is_file():
        speex_sources.append(path.relative_to(ROOT).as_posix())

highpass_sources = ["core/providers/highpass/highpass_provider.c"]

descriptors = {
    "speex": {
        "schema_id": DESCRIPTOR_SCHEMA,
        "provider_id": "speex.ns.v0",
        "implementation_id": "speex.preprocess.floating.smallft",
        "implementation_version": "1.0.0",
        "source_revision": "7a158783df74efe7c2d1c6ee8363c1e695c71226",
        "source_digest": source_digest(speex_sources),
        "contract_version": "0.1",
        "supported_formats": [
            {
                "sample_format": "f32",
                "sample_rate_hz": 16000,
                "channels": 1,
                "frame_samples": 160,
            }
        ],
        "native_hop_samples": 160,
        "buffering_delay_samples": 160,
        "edge_exclusions": {"start_samples": 0, "end_samples": 0},
        "max_drain_calls": 2,
        "callback_safe": False,
        "execution_modes": [2, 3],
        "required_assets": [],
        "upstream": {
            "name": "Xiph.Org SpeexDSP",
            "license": "BSD-3-Clause",
            "notice_path": "licenses/third-party/speexdsp-COPYING.txt",
        },
        "platform": {
            "cpu_requirements": "baseline",
            "architectures": ["arm64", "x86_64"],
        },
    },
    "highpass": {
        "schema_id": DESCRIPTOR_SCHEMA,
        "provider_id": "dsp.highpass80.v0",
        "implementation_id": "dsp.highpass.biquad.f64",
        "implementation_version": "1.0.0",
        "source_revision": None,
        "source_digest": source_digest(highpass_sources),
        "contract_version": "0.1",
        "supported_formats": [
            {
                "sample_format": "f32",
                "sample_rate_hz": 16000,
                "channels": 1,
                "frame_samples": 160,
            }
        ],
        "native_hop_samples": 160,
        "buffering_delay_samples": 0,
        "edge_exclusions": {"start_samples": 0, "end_samples": 0},
        "max_drain_calls": 1,
        "callback_safe": False,
        "execution_modes": [2, 3],
        "required_assets": [],
        "upstream": {
            "name": "audio-sdk first-party high-pass",
            "license": "MPL-2.0",
            "notice_path": "licenses/MPL-2.0.txt",
        },
        "platform": {
            "cpu_requirements": "baseline",
            "architectures": ["arm64", "x86_64"],
        },
    },
}

output = ['/* SPDX-' 'FileCopyrightText: 2026 Tsakanyan Hovhannes\n * SPDX-' 'License-Identifier: MPL-2.0 */\n#include "core/as_internal.h"\n']
catalog = {}
register = [
    'as_status_v0 as_registry_register_builtins(as_registry_v0 *registry, as_error_v0 *error) {',
    '    as_status_v0 status = AS_OK;',
]
for key, descriptor in descriptors.items():
    provider_id = descriptor["provider_id"]
    config_path = f"core/providers/{key}/config/config.json"
    config = json.loads((ROOT / config_path).read_text(encoding="utf-8"))
    if (config.get("provider_id") != provider_id or
            config.get("schema_id") != "audio-sdk/provider-config/0.1"):
        raise SystemExit(f"wrong provider or schema ID in {config_path}")
    config_text = canonical(config)
    write(f"schemas/providers/{provider_id}.json", config_text)
    descriptor["configuration_schema_digest"] = (
        "sha256:" + hashlib.sha256(config_text.encode("ascii")).hexdigest())
    name = f"as_{key}_descriptor"
    text = canonical(descriptor)
    filename = f"{provider_id}.descriptor.json"
    if filename in catalog:
        raise SystemExit(f"duplicate built-in provider: {filename}")
    write(f"schemas/providers/{filename}", text)
    catalog[filename] = text.encode("ascii")
    output.append(f"const char {name}[] = {c_string(text)};\n")
    output.append(f"const uint32_t {name}_length = {len(text)}u;\n")
    register.extend([
        '    if (status == AS_OK)',
        f'        status = as_registry_register_builtin_v0(registry, as_{key}_provider_table(),',
        f'                                                {name}, {name}_length, error);',
    ])
register.extend(['    return status;', '}', ''])
output.append("\n".join(register))

output.append(
    '#ifndef AS_BUILD_ID\n'
    '#define AS_BUILD_ID "audio-sdk/0.1.0+unconfigured"\n'
    '#endif\n'
    'const char as_build_identity[] = AS_BUILD_ID;\n'
)
write("core/src/descriptors/descriptors.c", "\n".join(output))

if args.catalog:
    actual = {path.relative_to(args.catalog).as_posix(): path
              for path in args.catalog.rglob("*.descriptor.json")}
    missing = sorted(catalog.keys() - actual.keys())
    extra = sorted(actual.keys() - catalog.keys())
    changed = sorted(name for name in catalog.keys() & actual.keys()
                     if actual[name].read_bytes() != catalog[name])
    if missing or extra or changed:
        raise SystemExit(f"installed catalog differs from compiled registry: "
                         f"missing={missing}, unexpected={extra}, changed={changed}")

print("descriptors verified" if CHECK else "descriptors written")
for key, descriptor in descriptors.items():
    print(key, descriptor["source_digest"], descriptor["configuration_schema_digest"])
