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
CHECK = parser.parse_args().check

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESCRIPTOR_SCHEMA = "audio-sdk/descriptor/0.1"
CONFIG_SCHEMA = "audio-sdk/provider-config/0.1"


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


def config_digest(path):
    return "sha256:" + sha256_file(path)


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

speex_config = {
    "schema_id": CONFIG_SCHEMA,
    "provider_id": "speex.ns.v0",
    "settings": {
        "agc": {"default": False, "type": "boolean"},
        "denoise": {"default": True, "type": "boolean"},
        "dereverb": {"default": False, "type": "boolean"},
        "suppression_db": {"default": -20, "maximum": 0, "minimum": -100, "type": "integer"},
        "vad_continue": {"default": 20, "maximum": 100, "minimum": 0, "type": "integer"},
        "vad_start": {"default": 35, "maximum": 100, "minimum": 0, "type": "integer"},
    },
    "units": {},
}
highpass_config = {
    "schema_id": CONFIG_SCHEMA,
    "provider_id": "dsp.highpass80.v0",
    "settings": {
        "cutoff_hz": {"default": "80", "type": "decimal_string", "unit": "Hz"},
        "q": {"default": "0.7071067811865476", "type": "decimal_string"},
    },
    "units": {},
}

write("schemas/providers/speex.ns.v0.json", canonical(speex_config))
write("schemas/providers/dsp.highpass80.v0.json", canonical(highpass_config))

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
        "configuration_schema_digest": config_digest(
            ROOT / "schemas/providers/speex.ns.v0.json"
        ),
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
        "configuration_schema_digest": config_digest(
            ROOT / "schemas/providers/dsp.highpass80.v0.json"
        ),
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

output = ['/* SPDX-' 'FileCopyrightText: 2026 Tsakanyan Hovhannes\n * SPDX-' 'License-Identifier: MPL-2.0 */\n#include <stdint.h>\n']
for key, name in (("speex", "as_speex_descriptor"), ("highpass", "as_highpass_descriptor")):
    text = canonical(descriptors[key])
    path = f"schemas/providers/{descriptors[key]['provider_id']}.descriptor.json"
    write(path, text)
    output.append(f"const char {name}[] = {c_string(text)};\n")
    output.append(f"const uint32_t {name}_length = {len(text)}u;\n")

output.append(
    '#ifndef AS_BUILD_ID\n'
    '#define AS_BUILD_ID "audio-sdk/0.1.0+unconfigured"\n'
    '#endif\n'
    'const char as_build_identity[] = AS_BUILD_ID;\n'
)
write("core/src/descriptors/descriptors.c", "\n".join(output))

print("descriptors verified" if CHECK else "descriptors written")
for key, descriptor in descriptors.items():
    print(key, descriptor["source_digest"], descriptor["configuration_schema_digest"])
