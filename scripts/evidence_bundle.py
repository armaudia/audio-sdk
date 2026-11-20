#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Create and validate portable audio-sdk evidence handoffs.

The handoff is the SDK-side artifact described by
schemas/evidence-handoff.schema.json. It carries exact integer clocks, source
intervals, denominators, runtime conditions, provenance and hashed artifacts so
audio-bench can validate a bundle without trusting paths or floats.

This tool uses only the Python standard library; it is not a general JSON
Schema implementation.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path, PureWindowsPath

SCHEMA_ID = "audio-sdk/evidence-handoff/0.1"
IDENTITY = "jcs-sha256-v1"
UINT = re.compile(r"^(0|[1-9][0-9]*)$")
INT = re.compile(r"^(0|-?[1-9][0-9]*)$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
ARTIFACT_PART = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]*")
PROFILES = {"Analysis", "Enhancement", "Room", "DSP", "Restoration", "Spatial",
            "Rate", "Voice", "Evidence", "Tool", "External", "Pipeline"}
REQUIRED_CHECKS = {"identity", "interval_conservation", "artifact_integrity"}
SAMPLE_NS = 62500


class DuplicateKey(ValueError):
    pass


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(f"duplicate key: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_no_duplicates)


def canonical(value: object) -> bytes:
    # Validated records have only ASCII keys and small, fixed numeric literals.
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def identity_digest(record: dict) -> str:
    return sha256_bytes(canonical({key: value for key, value in record.items()
                                   if key not in ("artifact_id", "handoff_id")}))


def _uint(value: object, path: str, errors: list[str]) -> int | None:
    if not isinstance(value, str) or not UINT.fullmatch(value):
        errors.append(f"{path}: expected canonical unsigned integer string")
        return None
    if len(value) > 20 or int(value) > 2**64 - 1:
        errors.append(f"{path}: outside uint64 range")
        return None
    return int(value)


def _int(value: object, path: str, errors: list[str]) -> int | None:
    if not isinstance(value, str) or not INT.fullmatch(value):
        errors.append(f"{path}: expected canonical signed integer string")
        return None
    if len(value) > 20 or not -(2**63) <= int(value) < 2**63:
        errors.append(f"{path}: outside int64 range")
        return None
    return int(value)


def _text(value: object, path: str, errors: list[str], maximum: int = 512) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected nonempty string")
    elif len(value) > maximum:
        errors.append(f"{path}: exceeds {maximum} characters")


def _digest(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        errors.append(f"{path}: expected sha256:<64 lowercase hex>")


def _keys(value: object, required: set[str] | tuple[str, ...], path: str,
          errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return False
    missing = sorted(set(required) - set(value))
    extra = sorted(set(value) - set(required))
    if missing:
        errors.append(f"{path}: missing keys {missing}")
    if extra:
        errors.append(f"{path}: unknown keys {extra}")
    return not missing and not extra


def _denominator(value: object, path: str, errors: list[str]) -> dict | None:
    keys = ("accepted", "valid", "produced", "delivered", "failed", "dropped")
    if not _keys(value, keys, path, errors):
        return None
    assert isinstance(value, dict)
    parsed = {}
    for key in keys:
        parsed[key] = _uint(value[key], f"{path}.{key}", errors)
    return parsed


def _artifact(value: object, path: str, errors: list[str]) -> None:
    if not _keys(value, ("path", "media_type", "byte_count", "sha256"),
                 path, errors):
        return
    assert isinstance(value, dict)
    relative = value["path"]
    if not _artifact_path(relative):
        errors.append(f"{path}.path: expected a portable relative path")
    _text(value["media_type"], f"{path}.media_type", errors, 128)
    _uint(value["byte_count"], f"{path}.byte_count", errors)
    _digest(value["sha256"], f"{path}.sha256", errors)


def _artifact_path(value: object) -> bool:
    return (isinstance(value, str) and len(value) <= 256 and
            all(ARTIFACT_PART.fullmatch(part) and not part.endswith(".")
                and not PureWindowsPath(part).is_reserved() for part in value.split("/")))


def _artifact_files(root: Path) -> dict[str, Path]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("artifacts root must be a real directory")
    files = {}

    def fail(error: OSError) -> None:
        raise error

    for directory, dirs, names in os.walk(root, onerror=fail):
        for name in dirs + names:
            path = Path(directory) / name
            if path.is_symlink() or not (path.is_dir() or path.is_file()):
                raise ValueError("artifact tree must contain only regular files and directories")
        for name in names:
            path = Path(directory) / name
            files[path.relative_to(root).as_posix()] = path
    return files


def validate_record(record: object, artifacts_root: Path | None = None) -> tuple[list[str], bool, list[str]]:
    """Return (errors, incomplete, failed_check_ids)."""
    errors: list[str] = []
    top = ("schema_id", "identity_algorithm", "artifact_id", "handoff_id",
           "profile", "provider", "toolchain", "inputs", "runtime", "trace",
           "checks", "artifacts", "provenance", "support_scope", "limitations")
    if not _keys(record, top, "record", errors):
        return errors, False, []
    assert isinstance(record, dict)
    if record["schema_id"] != SCHEMA_ID:
        errors.append(f"record.schema_id: expected {SCHEMA_ID}")
    if record["identity_algorithm"] != IDENTITY:
        errors.append(f"record.identity_algorithm: expected {IDENTITY}")
    _digest(record["artifact_id"], "record.artifact_id", errors)
    _digest(record["handoff_id"], "record.handoff_id", errors)
    if not isinstance(record["profile"], str) or record["profile"] not in PROFILES:
        errors.append("record.profile: unknown acceptance profile")

    provider = record["provider"]
    if _keys(provider, ("id", "implementation_version", "contract_version",
                        "descriptor_digest", "configuration_id"), "record.provider", errors):
        assert isinstance(provider, dict)
        if not isinstance(provider["id"], str) or not re.fullmatch(
                r"[a-z0-9][a-z0-9._-]{0,95}", provider["id"]):
            errors.append("record.provider.id: invalid provider ID")
        _text(provider["implementation_version"],
              "record.provider.implementation_version", errors, 64)
        version = provider["contract_version"]
        if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+", version):
            errors.append("record.provider.contract_version: expected major.minor")
        for key in ("descriptor_digest", "configuration_id"):
            _digest(provider[key], f"record.provider.{key}", errors)

    toolchain = record["toolchain"]
    if _keys(toolchain, ("source_revision", "build_id", "compiler", "os", "arch"),
             "record.toolchain", errors):
        assert isinstance(toolchain, dict)
        for key, maximum in (("source_revision", 128), ("build_id", 256),
                             ("compiler", 128), ("os", 128), ("arch", 64)):
            _text(toolchain[key], f"record.toolchain.{key}", errors, maximum)

    inputs = record["inputs"]
    if _keys(inputs, ("fixture_manifest_id", "source_digests", "model_digests",
                      "dataset_digests"), "record.inputs", errors):
        assert isinstance(inputs, dict)
        _digest(inputs["fixture_manifest_id"],
                "record.inputs.fixture_manifest_id", errors)
        for key in ("source_digests", "model_digests", "dataset_digests"):
            value = inputs[key]
            if not isinstance(value, list):
                errors.append(f"record.inputs.{key}: expected array")
                continue
            for index, digest in enumerate(value):
                _digest(digest, f"record.inputs.{key}[{index}]", errors)

    runtime = record["runtime"]
    if _keys(runtime, ("execution_mode", "pacing", "hardware", "load", "workers",
                       "input_queue", "output_queue", "deadline_ns"),
             "record.runtime", errors):
        assert isinstance(runtime, dict)
        mode = runtime["execution_mode"]
        if type(mode) is not int or mode not in (1, 2, 3):
            errors.append("record.runtime.execution_mode: expected 1, 2 or 3")
        else:
            expected = (1, 3, 3) if mode == 3 else (0, 0, 0)
            actual = tuple(runtime[key] for key in ("workers", "input_queue", "output_queue"))
            if actual != expected or any(type(value) is not int for value in actual):
                errors.append("record.runtime: worker and queue bounds do not match execution mode")
        if runtime["pacing"] not in ("unpaced", "paced"):
            errors.append("record.runtime.pacing: expected unpaced or paced")
        _text(runtime["hardware"], "record.runtime.hardware", errors, 256)
        _text(runtime["load"], "record.runtime.load", errors)
        if runtime["deadline_ns"] is not None:
            _uint(runtime["deadline_ns"], "record.runtime.deadline_ns", errors)

    trace = record["trace"]
    total_valid = 0
    total_produced = 0
    if _keys(trace, ("epoch", "sample_rate_hz", "origin_monotonic_ns", "entries"),
             "record.trace", errors):
        assert isinstance(trace, dict)
        _uint(trace["epoch"], "record.trace.epoch", errors)
        if type(trace["sample_rate_hz"]) is not int or trace["sample_rate_hz"] != 16000:
            errors.append("record.trace.sample_rate_hz: only 16000 is supported")
        origin = _int(trace["origin_monotonic_ns"],
                      "record.trace.origin_monotonic_ns", errors)
        entries = trace["entries"]
        if not isinstance(entries, list) or not entries:
            errors.append("record.trace.entries: expected nonempty array")
            entries = []
        previous_end: int | None = None
        for expected_sequence, entry in enumerate(entries):
            path = f"record.trace.entries[{expected_sequence}]"
            keys = ("sequence", "source_first_sample", "valid_offset",
                    "valid_count", "produced_count", "consumed_count", "flags",
                    "source_end_sample", "available_monotonic_ns")
            if not _keys(entry, keys, path, errors):
                continue
            assert isinstance(entry, dict)
            sequence = _uint(entry["sequence"], f"{path}.sequence", errors)
            if sequence is not None and sequence != expected_sequence:
                errors.append(f"{path}.sequence: expected {expected_sequence}")
            source = _int(entry["source_first_sample"],
                          f"{path}.source_first_sample", errors)
            offset = _uint(entry["valid_offset"], f"{path}.valid_offset", errors)
            count = _uint(entry["valid_count"], f"{path}.valid_count", errors)
            produced = _uint(entry["produced_count"],
                             f"{path}.produced_count", errors)
            _uint(entry["consumed_count"], f"{path}.consumed_count", errors)
            end = _int(entry["source_end_sample"],
                       f"{path}.source_end_sample", errors)
            available = _int(entry["available_monotonic_ns"],
                             f"{path}.available_monotonic_ns", errors)
            flags = entry["flags"]
            if not isinstance(flags, list) or any(flag not in (
                    "startup_padding", "final_padding", "concealment")
                    for flag in flags):
                errors.append(f"{path}.flags: invalid or non-array flags")
                flags = []
            elif len(flags) != len(set(flags)):
                errors.append(f"{path}.flags: duplicate flag")
            if "concealment" in flags and count != 0:
                errors.append(f"{path}: concealment must have valid_count=0")
            if None in (source, offset, count, produced, end, available):
                continue
            if offset + count > produced:
                errors.append(f"{path}: valid interval exceeds produced_count")
            if end != source + offset + count:
                errors.append(f"{path}: source_end_sample != source_first + valid_offset + valid_count")
            total_produced += produced
            if count == 0:
                continue
            start = source + offset
            finish = start + count
            total_valid += count
            if previous_end is not None and start != previous_end:
                errors.append(f"{path}: valid interval {start}..{finish} does not continue at {previous_end}")
            previous_end = finish
            if origin is not None:
                capture = origin + start * SAMPLE_NS
                if available < capture:
                    errors.append(f"{path}: negative availability delay (available before capture)")

    checks = record["checks"]
    failed_checks: list[str] = []
    check_ids: set[str] = set()
    run_denominator = None
    if not isinstance(checks, list) or not checks:
        errors.append("record.checks: expected nonempty array")
        checks = []
    for index, check in enumerate(checks):
        path = f"record.checks[{index}]"
        keys = ("id", "profile", "status", "expected", "observed", "reason",
                "denominator")
        if not _keys(check, keys, path, errors):
            continue
        assert isinstance(check, dict)
        identifier = check["id"]
        if not isinstance(identifier, str) or not re.fullmatch(
                r"[a-z0-9][a-z0-9._-]{0,63}", identifier):
            errors.append(f"{path}.id: invalid check ID")
        elif identifier in check_ids:
            errors.append(f"{path}.id: duplicate check ID {identifier}")
        else:
            check_ids.add(identifier)
        if not isinstance(check["profile"], str) or check["profile"] not in PROFILES:
            errors.append(f"{path}.profile: unknown acceptance profile")
        status = check["status"]
        if status not in ("passed", "failed", "blocked", "invalid", "not_run"):
            errors.append(f"{path}.status: invalid status")
        _text(check["expected"], f"{path}.expected", errors)
        _text(check["observed"], f"{path}.observed", errors)
        reason = check["reason"]
        if status in ("failed", "blocked", "invalid", "not_run") and not isinstance(reason, str):
            errors.append(f"{path}.reason: a non-passing check needs a stable reason")
        elif reason is not None:
            _text(reason, f"{path}.reason", errors, 128)
        if status == "failed" and isinstance(identifier, str):
            failed_checks.append(identifier)
        parsed = _denominator(check["denominator"], f"{path}.denominator", errors)
        if parsed and None not in parsed.values():
            if run_denominator is None:
                run_denominator = parsed
            elif run_denominator != parsed:
                errors.append(f"{path}.denominator: differs from other run checks")
            if parsed["valid"] != total_valid:
                errors.append(f"{path}.denominator.valid: expected trace total {total_valid}")
            if parsed["produced"] != total_produced:
                errors.append(f"{path}.denominator.produced: expected trace total {total_produced}")
            if parsed["delivered"] > parsed["valid"]:
                errors.append(f"{path}.denominator.delivered: exceeds valid output")
            if parsed["accepted"] != parsed["delivered"] + parsed["failed"] + parsed["dropped"]:
                errors.append(f"{path}.denominator.accepted: must equal delivered+failed+dropped")

    artifacts = record["artifacts"]
    seen_paths: set[str] = set()
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("record.artifacts: expected nonempty array")
        artifacts = []
    files = None
    if artifacts_root is not None:
        try:
            files = _artifact_files(artifacts_root)
        except (OSError, ValueError) as error:
            errors.append(f"record.artifacts: {error}")
    for index, artifact in enumerate(artifacts):
        path = f"record.artifacts[{index}]"
        _artifact(artifact, path, errors)
        if not isinstance(artifact, dict) or not _artifact_path(artifact.get("path")):
            continue
        relative = artifact["path"]
        if relative in seen_paths:
            errors.append(f"{path}.path: duplicate artifact path {relative}")
        seen_paths.add(relative)
        if files is None:
            continue
        try:
            data = files[relative].read_bytes()
        except (KeyError, OSError):
            errors.append(f"{path}: artifact file is missing: {relative}")
            continue
        if artifact.get("byte_count") != str(len(data)):
            errors.append(f"{path}.byte_count: does not match {relative}")
        if artifact.get("sha256") != sha256_bytes(data):
            errors.append(f"{path}.sha256: does not match {relative}")
    if files is not None:
        for extra in sorted(files.keys() - seen_paths):
            errors.append(f"record.artifacts: unlisted artifact file {extra}")

    provenance = record["provenance"]
    if _keys(provenance, ("producer", "reviewer", "created_utc", "evidence_refs"),
             "record.provenance", errors):
        assert isinstance(provenance, dict)
        _text(provenance["producer"], "record.provenance.producer", errors, 128)
        _text(provenance["reviewer"], "record.provenance.reviewer", errors, 128)
        created = provenance["created_utc"]
        try:
            datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            errors.append("record.provenance.created_utc: expected ISO date-time")
        refs = provenance["evidence_refs"]
        if not isinstance(refs, list):
            errors.append("record.provenance.evidence_refs: expected array")
        else:
            for index, ref in enumerate(refs):
                _text(ref, f"record.provenance.evidence_refs[{index}]", errors)
    _text(record["support_scope"], "record.support_scope", errors)
    limitations = record["limitations"]
    if not isinstance(limitations, list):
        errors.append("record.limitations: expected array")
    else:
        for index, limitation in enumerate(limitations):
            _text(limitation, f"record.limitations[{index}]", errors)

    incomplete = bool(REQUIRED_CHECKS - check_ids) or any(
        isinstance(check, dict) and check.get("status") in ("blocked", "invalid", "not_run")
        for check in checks)
    return errors, incomplete, failed_checks


def create(input_path: Path, artifacts: Path, output: Path) -> int:
    try:
        record = load(input_path)
        if not isinstance(record, dict) or not isinstance(record.get("artifacts"), list):
            raise ValueError("input needs an artifacts array")
        if output.exists() or output.is_symlink() or output.resolve().is_relative_to(artifacts.resolve()):
            raise ValueError("output must be a new path outside the source tree")
        files = _artifact_files(artifacts)
        paths = set()
        for artifact in record["artifacts"]:
            if not isinstance(artifact, dict) or not _artifact_path(artifact.get("path")):
                raise ValueError("each artifact needs a portable relative path")
            relative = artifact["path"]
            if relative not in files:
                raise ValueError(f"missing source artifact {relative}")
            paths.add(relative)
            data = files[relative].read_bytes()
            artifact.setdefault("media_type", "application/octet-stream")
            artifact["byte_count"] = str(len(data))
            artifact["sha256"] = sha256_bytes(data)
        if files.keys() != paths:
            raise ValueError("source tree contains unlisted artifacts")
        record["artifact_id"] = record["handoff_id"] = "sha256:" + "0" * 64
        errors, _, _ = validate_record(record)
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2))
            return 1
        digest = identity_digest(record)
        record["artifact_id"] = record["handoff_id"] = digest
        payload = canonical(record)
        output.mkdir(parents=True)
        shutil.copytree(artifacts, output / "artifacts")
        (output / "handoff.json").write_bytes(payload)
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "errors": [str(error)]}, indent=2))
        return 1
    print(json.dumps({"ok": True, "bundle": str(output),
                      "artifact_id": digest}, indent=2))
    return 0


def validate(bundle: Path, allow_incomplete: bool) -> int:
    try:
        manifest = bundle / "handoff.json"
        if manifest.is_symlink() or not manifest.is_file():
            raise ValueError("handoff.json must be a regular file")
        record = load(manifest)
        errors, incomplete, failed = validate_record(record, bundle / "artifacts")
        if not errors:
            expected = identity_digest(record)
            for key in ("artifact_id", "handoff_id"):
                if record[key] != expected:
                    errors.append(f"record.{key}: does not match the canonical identity digest")
            if manifest.read_bytes() != canonical(record):
                errors.append("handoff.json: not stored as canonical JSON")
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "status": "invalid",
                          "errors": [str(error)]}, indent=2))
        return 1
    status = "invalid" if errors else ("incomplete" if incomplete else "complete")
    print(json.dumps({"bundle": str(bundle), "ok": not errors,
                      "status": status, "incomplete": incomplete,
                      "failed_checks": failed, "errors": errors}, indent=2))
    if errors:
        return 1
    return 0 if (allow_incomplete or not incomplete) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    make = subcommands.add_parser("create")
    make.add_argument("--input", type=Path, required=True)
    make.add_argument("--artifacts", type=Path, required=True)
    make.add_argument("--output", type=Path, required=True)
    check = subcommands.add_parser("validate")
    check.add_argument("bundle", type=Path)
    check.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    if args.command == "create":
        return create(args.input, args.artifacts, args.output)
    return validate(args.bundle, args.allow_incomplete)


if __name__ == "__main__":
    sys.exit(main())
