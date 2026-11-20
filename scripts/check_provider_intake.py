#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Validate an audio-sdk provider intake record and enforce fail-closed rights.

This is a policy checker, not a JSON Schema implementation. The normative
schema is schemas/provider-intake.schema.json; this script adds the admission
rules that the C runtime cannot enforce at registration time.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ID = "audio-sdk/provider-intake/0.1"
PROVIDER_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
ASSET_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")
MAX_ASSET_BYTES = 512 * 1024 * 1024
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
REVISION = re.compile(r"(?!0+$)(?:[0-9a-f]{40}|[0-9a-f]{64})")
DESCRIPTOR_FIELDS = (
    "provider_id", "implementation_id", "implementation_version",
    "contract_version", "source_revision", "source_digest",
)
SCOPES = ("acquisition", "evaluation", "redistribution", "public_playback")
REQUIRED = (
    "schema_id", *DESCRIPTOR_FIELDS, "descriptor_ref", "descriptor_digest",
    "source_manifest_ref", "distribution", "packages_assets", "assets",
    "rights", "runtime", "evaluation", "customer_scope", "playback_scope",
    "review", "reopen_condition",
)

# These two already shipped before intake. The exception is the exact
# asset-free descriptor bytes, not the provider IDs or an approval.
BASELINE = {
    "dsp.highpass80.v0.descriptor.json": "sha256:d664ddc7977b5ff193e184b12dca48f3923675e8a7f0d4feb79781b0ca7c77e3",
    "speex.ns.v0.descriptor.json": "sha256:8dcfbd3ca87ae85f0c1d6390ede34b62b5a44461bef65d52c7bf0cf5c303b733",
}


class DuplicateKey(ValueError):
    pass


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(f"duplicate key: {key}")
        result[key] = value
    return result


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_no_duplicates)


def _keys(value: object, required: tuple[str, ...], path: str,
          errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return False
    missing = [key for key in required if key not in value]
    extra = sorted(set(value) - set(required))
    if missing:
        errors.append(f"{path}: missing keys {missing}")
    if extra:
        errors.append(f"{path}: unknown keys {extra}")
    return not missing and not extra


def _text(value: object, path: str, errors: list[str], maximum: int = 512) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected nonempty string")
        return ""
    if len(value) > maximum:
        errors.append(f"{path}: exceeds {maximum} characters")
    return value


def _digest(value: object, path: str, errors: list[str]) -> None:
    if (not isinstance(value, str) or not DIGEST.fullmatch(value)
            or value == "sha256:" + "0" * 64):
        errors.append(f"{path}: expected nonzero sha256:<64 lowercase hex>")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _revision(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not REVISION.fullmatch(value):
        errors.append(f"{path}: expected a full immutable Git object ID (40 or 64 lowercase hex)")


def _file(value: object, path: str, root: Path, errors: list[str]) -> Path | None:
    ref = _text(value, path, errors)
    if not ref:
        return None
    posix = PurePosixPath(ref)
    if posix.is_absolute() or ".." in posix.parts or any(c in ref for c in "\\:\x00"):
        errors.append(f"{path}: expected a repository-relative file path")
        return None
    try:
        target = (root / ref).resolve()
        if target.is_relative_to(root) and target.is_file():
            return target
    except (OSError, RuntimeError, ValueError):
        pass
    errors.append(f"{path}: file not found within evidence root: {ref}")
    return None


def _source_manifest(manifest: Path, digest: object, root: Path, errors: list[str]) -> None:
    path = "record.source_manifest_ref"
    previous = ""
    identity = bytearray()
    try:
        for line in manifest.read_text(encoding="ascii").splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  (\S+)", line)
            if not match or match[2] <= previous:
                errors.append(f"{path}: expected sorted, unique '<sha256-hex>  <path>' entries")
                return
            expected, relative = match.groups()
            source = _file(relative, path, root, errors)
            if source is None:
                return
            data = source.read_bytes()
            if b"\0" not in data:
                data = data.replace(b"\r\n", b"\n")
            if _sha256(data) != "sha256:" + expected:
                errors.append(f"{path}: source hash mismatch: {relative}")
                return
            identity.extend(f"{relative}\0{expected}\n".encode("ascii"))
            previous = relative
    except (OSError, ValueError) as error:
        errors.append(f"{path}: {error}")
        return
    if not identity or _sha256(identity) != digest:
        errors.append(f"{path}: inventory does not match record.source_digest")


def _date(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        errors.append(f"{path}: expected YYYY-MM-DD date")
        return
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{path}: invalid ISO date")


def _decision(value: object, path: str, root: Path, errors: list[str]) -> str:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected decision object")
        return "unknown"
    extra = sorted(set(value) - {"decision", "evidence_ref", "reviewer",
                                 "review_date"})
    if extra:
        errors.append(f"{path}: unknown keys {extra}")
    if "decision" not in value:
        errors.append(f"{path}: missing decision")
        return "unknown"
    decision = value["decision"]
    if decision not in ("allowed", "denied", "unknown"):
        errors.append(f"{path}.decision: expected allowed, denied or unknown")
        return "unknown"
    for key in ("evidence_ref", "reviewer", "review_date"):
        if decision == "allowed" and key not in value:
            errors.append(f"{path}: allowed decision needs {key}")
    if "evidence_ref" in value:
        _file(value["evidence_ref"], f"{path}.evidence_ref", root, errors)
    if "reviewer" in value:
        _text(value["reviewer"], f"{path}.reviewer", errors, 128)
    if "review_date" in value:
        _date(value["review_date"], f"{path}.review_date", errors)
    return decision


def _rights(value: object, path: str, root: Path, errors: list[str]) -> dict[str, str]:
    if not _keys(value, SCOPES, path, errors):
        return {scope: "unknown" for scope in SCOPES}
    return {scope: _decision(value[scope], f"{path}.{scope}", root, errors)
            for scope in SCOPES}


def _require_rights(rights: dict[str, str], path: str, scopes: tuple[str, ...],
                    use: str, errors: list[str]) -> None:
    for scope in scopes:
        if rights[scope] != "allowed":
            errors.append(f"{path}.{scope}: {use} requires an allowed decision")


def _check_descriptor(file: Path, record: dict, assets: list[dict], errors: list[str]) -> None:
    path = "record.descriptor_ref"
    try:
        data = file.read_bytes()
        descriptor = json.loads(data, object_pairs_hook=_no_duplicates)
    except (OSError, ValueError) as error:
        errors.append(f"{path}: {error}")
        return
    if _sha256(data) != record["descriptor_digest"]:
        errors.append("record.descriptor_digest: does not match descriptor bytes")
    if not isinstance(descriptor, dict) or descriptor.get("schema_id") != "audio-sdk/descriptor/0.1":
        errors.append(f"{path}: expected an audio-sdk/descriptor/0.1 object")
        return
    for field in DESCRIPTOR_FIELDS:
        if field not in descriptor or descriptor[field] != record[field]:
            errors.append(f"record.{field}: does not match descriptor")
    required = descriptor.get("required_assets")
    if not isinstance(required, list) or any(
            not isinstance(item, dict) or type(item.get("byte_count")) is not int
            for item in required):
        errors.append(f"{path}: invalid required_assets")
        return
    keys = ("id", "sha256", "byte_count")
    expected = [{"storage": "external", **{key: asset[key] for key in keys}}
                for asset in assets]
    if len(expected) != len(required) or any(asset not in required for asset in expected):
        errors.append(f"{path}: record.assets do not match descriptor required_assets")


def validate(record: object, root: Path = ROOT, *, public: bool = False) -> list[str]:
    errors: list[str] = []
    if not _keys(record, REQUIRED, "record", errors):
        return errors
    assert isinstance(record, dict)

    if record["schema_id"] != SCHEMA_ID:
        errors.append(f"record.schema_id: expected {SCHEMA_ID}")
    provider = _text(record["provider_id"], "record.provider_id", errors, 96)
    if provider and not PROVIDER_ID.fullmatch(provider):
        errors.append("record.provider_id: invalid ASCII provider ID")
    _text(record["implementation_id"], "record.implementation_id", errors, 96)
    _text(record["implementation_version"], "record.implementation_version",
          errors, 64)
    if record["contract_version"] != "0.1":
        errors.append("record.contract_version: expected 0.1")
    if record["source_revision"] is not None:
        _revision(record["source_revision"], "record.source_revision", errors)
    elif record["source_manifest_ref"] is None:
        errors.append("record.source_manifest_ref: required for a null source_revision")
    _digest(record["source_digest"], "record.source_digest", errors)
    if record["source_manifest_ref"] is not None:
        manifest = _file(record["source_manifest_ref"], "record.source_manifest_ref", root, errors)
        if manifest is not None:
            _source_manifest(manifest, record["source_digest"], root, errors)
    _digest(record["descriptor_digest"], "record.descriptor_digest", errors)
    descriptor = _file(record["descriptor_ref"], "record.descriptor_ref", root, errors)
    if record["distribution"] not in ("source-linked", "binary", "service"):
        errors.append("record.distribution: invalid distribution mode")
    if not isinstance(record["packages_assets"], bool):
        errors.append("record.packages_assets: expected boolean")

    assets = record["assets"]
    if not isinstance(assets, list):
        errors.append("record.assets: expected array")
        assets = []
    if len(assets) > 16:
        errors.append("record.assets: at most 16 assets are admitted")
    seen: set[str] = set()
    checked_assets: list[dict] = []
    total_bytes = 0
    packages = record["packages_assets"] is True
    execution = "execution and customer_scope=allowed" if record["customer_scope"] == "allowed" else "execution"
    uses = [(("acquisition", "evaluation"), execution)]
    if record["playback_scope"] == "allowed":
        uses.append((("public_playback",), "playback_scope=allowed"))
    global_rights = _rights(record["rights"], "record.rights", root, errors)
    for scopes, use in uses:
        _require_rights(global_rights, "record.rights", scopes, use, errors)
    if packages or public:
        _require_rights(global_rights, "record.rights", ("redistribution",),
                        "public distribution", errors)
    for index, asset in enumerate(assets):
        path = f"record.assets[{index}]"
        if not _keys(asset, ("id", "sha256", "byte_count", "class", "rights", "checkpoint"),
                      path, errors):
            continue
        assert isinstance(asset, dict)
        checked_assets.append(asset)
        asset_id = _text(asset["id"], f"{path}.id", errors, 63)
        if asset_id and not ASSET_ID.fullmatch(asset_id):
            errors.append(f"{path}.id: invalid ASCII asset ID")
        if asset_id in seen:
            errors.append(f"{path}.id: duplicate asset ID {asset_id}")
        seen.add(asset_id)
        _digest(asset["sha256"], f"{path}.sha256", errors)
        count = asset["byte_count"]
        if type(count) is not int or not 0 <= count <= MAX_ASSET_BYTES:
            errors.append(f"{path}.byte_count: expected integer 0..512 MiB")
        else:
            total_bytes += count
        if asset["class"] not in ("public", "restricted", "closed"):
            errors.append(f"{path}.class: expected public, restricted or closed")
        elif asset["class"] != "public":
            if packages:
                errors.append(f"{path}: packages_assets cannot include a non-public asset")
            if public:
                errors.append(f"{path}: {asset['class']} asset excludes provider from public discovery")
            if record["playback_scope"] == "allowed":
                errors.append(f"{path}: non-public asset excludes playback_scope=allowed")
        asset_rights = _rights(asset["rights"], f"{path}.rights", root, errors)
        for scopes, use in uses:
            _require_rights(asset_rights, f"{path}.rights", scopes, use, errors)
        if packages:
            _require_rights(asset_rights, f"{path}.rights", ("redistribution",),
                            "packages_assets=true", errors)
        if asset["class"] == "closed" and asset_rights["redistribution"] == "allowed":
            errors.append(f"{path}: closed asset cannot be redistributed")
        checkpoint = asset["checkpoint"]
        if checkpoint is not None and _keys(
                checkpoint, ("upstream_revision", "tensor_config_ref", "precision", "inventory_ref"),
                f"{path}.checkpoint", errors):
            _revision(checkpoint["upstream_revision"], f"{path}.checkpoint.upstream_revision", errors)
            _file(checkpoint["tensor_config_ref"], f"{path}.checkpoint.tensor_config_ref", root, errors)
            _text(checkpoint["precision"], f"{path}.checkpoint.precision", errors, 64)
            _file(checkpoint["inventory_ref"], f"{path}.checkpoint.inventory_ref", root, errors)
    if total_bytes > MAX_ASSET_BYTES:
        errors.append("record.assets: total exceeds 512 MiB")
    if descriptor is not None:
        _check_descriptor(descriptor, record, checked_assets, errors)

    runtime = record["runtime"]
    if _keys(runtime, ("kind", "optional_dependency", "platforms"),
             "record.runtime", errors):
        assert isinstance(runtime, dict)
        if runtime["kind"] not in ("none", "cpu", "gpu", "npu", "service"):
            errors.append("record.runtime.kind: invalid runtime kind")
        _text(runtime["optional_dependency"],
              "record.runtime.optional_dependency", errors, 128)
        platforms = runtime["platforms"]
        if not isinstance(platforms, list) or not platforms:
            errors.append("record.runtime.platforms: expected nonempty array")
        else:
            for index, platform in enumerate(platforms):
                _text(platform, f"record.runtime.platforms[{index}]", errors, 64)

    evaluation = record["evaluation"]
    if _keys(evaluation, ("task", "scope", "evidence_ref", "paired_quality", "runtime_claim"),
             "record.evaluation", errors):
        assert isinstance(evaluation, dict)
        _text(evaluation["task"], "record.evaluation.task", errors, 128)
        _text(evaluation["scope"], "record.evaluation.scope", errors)
        _file(evaluation["evidence_ref"], "record.evaluation.evidence_ref", root, errors)
        if evaluation["paired_quality"] not in ("supported", "not-supported", "unknown"):
            errors.append("record.evaluation.paired_quality: invalid value")
        if evaluation["runtime_claim"] not in ("supported", "not-supported", "unknown"):
            errors.append("record.evaluation.runtime_claim: invalid value")

    if record["customer_scope"] not in ("allowed", "denied", "unknown"):
        errors.append("record.customer_scope: invalid value")
    if record["playback_scope"] not in ("allowed", "denied", "unknown"):
        errors.append("record.playback_scope: invalid value")
    _text(record["reopen_condition"], "record.reopen_condition", errors)

    review = record["review"]
    if _keys(review, ("reviewer", "review_date", "decision"),
             "record.review", errors):
        assert isinstance(review, dict)
        if review["decision"] == "pending":
            if review["reviewer"] is not None or review["review_date"] is not None:
                errors.append("record.review: pending review must not name a reviewer or date")
        else:
            _text(review["reviewer"], "record.review.reviewer", errors, 128)
            _date(review["review_date"], "record.review.review_date", errors)
        if review["decision"] != "approved":
            errors.append("record.review.decision: admission requires approved review")
    return errors


def check_public_catalog(catalog: Path, root: Path) -> list[str]:
    errors: list[str] = []
    descriptors = sorted(catalog.rglob("*.descriptor.json"))
    if not descriptors:
        return ["public catalog: no provider descriptors found"]
    for descriptor in descriptors:
        try:
            provider = descriptor.name.removesuffix(".descriptor.json")
            if descriptor.parent != catalog or not PROVIDER_ID.fullmatch(provider):
                errors.append(f"{descriptor}: expected <provider_id>.descriptor.json at catalog root")
                continue
            digest = _sha256(descriptor.read_bytes())
            if digest == BASELINE.get(descriptor.name):
                continue
            record = load(root / "docs/provider-intake" / f"{provider}.json")
            problems = validate(record, root, public=True)
            if isinstance(record, dict) and (
                    record.get("provider_id") != provider or record.get("descriptor_digest") != digest):
                problems.append("intake does not match the public descriptor ID and bytes")
            errors.extend(f"{descriptor.name}: {problem}" for problem in problems)
        except (OSError, ValueError) as error:
            errors.append(f"{descriptor.name}: {error}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", type=Path)
    mode.add_argument("--public-catalog", type=Path, help="staged public SDK provider descriptor directory")
    parser.add_argument("--evidence-root", type=Path, default=ROOT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    path = args.record if args.record is not None else args.public_catalog
    try:
        root = args.evidence_root.resolve()
        errors = (validate(load(path), root) if args.record is not None
                  else check_public_catalog(path, root))
    except (OSError, ValueError, RecursionError) as error:
        errors = [str(error)]
    if errors or not args.quiet:
        label = "record" if args.record is not None else "public_catalog"
        print(json.dumps({label: str(path), "ok": not errors,
                          "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
