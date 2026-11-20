#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Validate an audio-sdk provider intake record and enforce fail-closed rights.

This is a policy checker, not a JSON Schema implementation. The normative
schema is schemas/provider-intake.schema.json; this script adds the admission
rules that the Rust/C runtime cannot enforce at registration time.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

SCHEMA_ID = "audio-sdk/provider-intake/0.1"
PROVIDER_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
ASSET_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
SCOPES = ("acquisition", "evaluation", "redistribution", "public_playback")
REQUIRED = (
    "schema_id", "provider_id", "implementation_version", "contract_version",
    "source_revision", "source_digest", "distribution", "packages_assets",
    "assets", "rights", "runtime", "evaluation", "customer_scope",
    "playback_scope", "review",
)


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
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        errors.append(f"{path}: expected sha256:<64 lowercase hex>")


def _date(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{path}: expected ISO date")
        return
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{path}: invalid ISO date")


def _decision(value: object, path: str, errors: list[str]) -> str:
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
    if decision == "allowed":
        for key in ("evidence_ref", "reviewer", "review_date"):
            if key not in value:
                errors.append(f"{path}: allowed decision needs {key}")
        if "evidence_ref" in value:
            _text(value["evidence_ref"], f"{path}.evidence_ref", errors)
        if "reviewer" in value:
            _text(value["reviewer"], f"{path}.reviewer", errors, 128)
        if "review_date" in value:
            _date(value["review_date"], f"{path}.review_date", errors)
    return decision


def _rights(value: object, path: str, errors: list[str]) -> dict[str, str]:
    if not _keys(value, SCOPES, path, errors):
        return {scope: "unknown" for scope in SCOPES}
    return {scope: _decision(value[scope], f"{path}.{scope}", errors)
            for scope in SCOPES}


def validate(record: object) -> list[str]:
    errors: list[str] = []
    if not _keys(record, REQUIRED, "record", errors):
        return errors
    assert isinstance(record, dict)

    if record["schema_id"] != SCHEMA_ID:
        errors.append(f"record.schema_id: expected {SCHEMA_ID}")
    provider = _text(record["provider_id"], "record.provider_id", errors, 96)
    if provider and not PROVIDER_ID.fullmatch(provider):
        errors.append("record.provider_id: invalid ASCII provider ID")
    _text(record["implementation_version"], "record.implementation_version",
          errors, 64)
    contract = _text(record["contract_version"], "record.contract_version",
                     errors, 16)
    if contract and not re.fullmatch(r"[0-9]+\.[0-9]+", contract):
        errors.append("record.contract_version: expected major.minor")
    revision = record["source_revision"]
    if revision is not None:
        _text(revision, "record.source_revision", errors, 128)
        if len(revision) < 7:
            errors.append("record.source_revision: immutable revision is too short")
    _digest(record["source_digest"], "record.source_digest", errors)
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
    non_public: list[str] = []
    for index, asset in enumerate(assets):
        path = f"record.assets[{index}]"
        if not _keys(asset, ("id", "sha256", "byte_count", "class", "rights"),
                     path, errors):
            continue
        assert isinstance(asset, dict)
        asset_id = _text(asset["id"], f"{path}.id", errors, 64)
        if asset_id and not ASSET_ID.fullmatch(asset_id):
            errors.append(f"{path}.id: invalid ASCII asset ID")
        if asset_id in seen:
            errors.append(f"{path}.id: duplicate asset ID {asset_id}")
        seen.add(asset_id)
        _digest(asset["sha256"], f"{path}.sha256", errors)
        count = asset["byte_count"]
        if not isinstance(count, int) or isinstance(count, bool) or not 0 <= count <= 536870912:
            errors.append(f"{path}.byte_count: expected integer 0..512 MiB")
        if asset["class"] not in ("public", "restricted", "closed"):
            errors.append(f"{path}.class: expected public, restricted or closed")
        elif asset["class"] != "public":
            non_public.append(asset_id)
        asset_rights = _rights(asset["rights"], f"{path}.rights", errors)
        if asset["class"] in ("restricted", "closed") and asset_rights["evaluation"] == "denied":
            errors.append(f"{path}: {asset['class']} asset is denied evaluation")
        if asset["class"] == "closed" and asset_rights["redistribution"] == "allowed":
            errors.append(f"{path}: closed asset cannot be redistributed")

    global_rights = _rights(record["rights"], "record.rights", errors)
    if record["packages_assets"] and non_public:
        errors.append("record.packages_assets: public package contains "
                      f"non-public assets {non_public}")
    if non_public and record["packages_assets"]:
        errors.append("record: restricted/closed assets must be caller-supplied")

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
    if _keys(evaluation, ("task", "evidence_ref", "paired_quality", "runtime_claim"),
             "record.evaluation", errors):
        assert isinstance(evaluation, dict)
        _text(evaluation["task"], "record.evaluation.task", errors, 128)
        _text(evaluation["evidence_ref"], "record.evaluation.evidence_ref", errors)
        if evaluation["paired_quality"] not in ("supported", "not-supported", "unknown"):
            errors.append("record.evaluation.paired_quality: invalid value")
        if evaluation["runtime_claim"] not in ("supported", "not-supported", "unknown"):
            errors.append("record.evaluation.runtime_claim: invalid value")

    if record["customer_scope"] not in ("allowed", "denied", "unknown"):
        errors.append("record.customer_scope: invalid value")
    elif record["customer_scope"] == "allowed" and global_rights["evaluation"] != "allowed":
        errors.append("record.customer_scope: allowed customer use needs an allowed evaluation right")
    if record["playback_scope"] not in ("allowed", "denied", "unknown"):
        errors.append("record.playback_scope: invalid value")
    elif record["playback_scope"] == "allowed" and global_rights["public_playback"] != "allowed":
        errors.append("record.playback_scope: allowed public playback needs an allowed public_playback right")

    review = record["review"]
    if _keys(review, ("reviewer", "review_date", "decision"),
             "record.review", errors):
        assert isinstance(review, dict)
        _text(review["reviewer"], "record.review.reviewer", errors, 128)
        _date(review["review_date"], "record.review.review_date", errors)
        if review["decision"] not in ("approved", "rejected"):
            errors.append("record.review.decision: expected approved or rejected")
        if review["decision"] == "approved" and errors:
            errors.append("record.review.decision: cannot approve a record with errors")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    try:
        record = load(args.record)
    except (OSError, ValueError, DuplicateKey) as error:
        print(json.dumps({"record": str(args.record), "ok": False,
                          "errors": [str(error)]}, indent=2))
        return 1
    errors = validate(record)
    if not args.quiet:
        print(json.dumps({"record": str(args.record), "ok": not errors,
                          "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
