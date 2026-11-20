# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Policy tests for scripts/check_provider_intake.py."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_provider_intake.py"
DIGEST = "sha256:" + "a" * 64
EXAMPLE = ROOT / "docs/task-evidence/provider-intake.example.json"
BASELINE = ROOT / "schemas/providers/dsp.highpass80.v0.descriptor.json"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def decision(value: str = "allowed") -> dict:
    if value != "allowed":
        return {"decision": value}
    return {
        "decision": "allowed",
        "evidence_ref": "evidence.md",
        "reviewer": "synthetic-test-reviewer",
        "review_date": "2026-11-20",
    }


def rights(value: str = "allowed") -> dict:
    return {
        "acquisition": decision(value),
        "evaluation": decision(value),
        "redistribution": decision(value),
        "public_playback": decision(value),
    }


def record() -> dict:
    return {
        "schema_id": "audio-sdk/provider-intake/0.1",
        "provider_id": "dsp.example.v0",
        "implementation_id": "test.identity",
        "implementation_version": "1.0.0",
        "contract_version": "0.1",
        "source_revision": "4c3b3be864c3ecdcf48a94358c6dde229aecb703",
        "source_digest": DIGEST,
        "source_manifest_ref": None,
        "descriptor_ref": "staged/dsp.example.v0.descriptor.json",
        "descriptor_digest": DIGEST,
        "distribution": "source-linked",
        "packages_assets": False,
        "assets": [],
        "rights": rights(),
        "runtime": {
            "kind": "none",
            "optional_dependency": "none",
            "platforms": ["arm64", "x86_64"],
        },
        "evaluation": {
            "task": "identity conformance",
            "scope": "synthetic fixtures only",
            "evidence_ref": "evidence.md",
            "paired_quality": "not-supported",
            "runtime_claim": "not-supported",
        },
        "customer_scope": "allowed",
        "playback_scope": "denied",
        "review": {
            "reviewer": "synthetic-test-reviewer",
            "review_date": "2026-11-20",
            "decision": "approved",
        },
        "reopen_condition": "Changes to reviewed implementation or scope.",
    }


def asset(identifier: str = "model.f32", klass: str = "public") -> dict:
    return {
        "id": identifier,
        "sha256": DIGEST,
        "byte_count": 1,
        "class": klass,
        "rights": rights(),
        "checkpoint": None,
    }


class IntakePolicyTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "evidence.md").write_text("Synthetic test evidence.", encoding="utf-8")

    def write_descriptor(self, value: dict) -> None:
        descriptor = json.loads(BASELINE.read_bytes())
        for key in ("provider_id", "implementation_id", "implementation_version",
                    "contract_version", "source_revision", "source_digest"):
            descriptor[key] = value[key]
        descriptor["required_assets"] = [
            {"storage": "external", **{key: item[key] for key in ("id", "sha256", "byte_count")}}
            for item in value["assets"]
        ]
        data = json.dumps(descriptor, sort_keys=True, separators=(",", ":")).encode("ascii")
        target = self.root / value["descriptor_ref"]
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(data)
        value["descriptor_digest"] = digest(data)

    def run_cli(self, mode: str, path: Path, root: Path) -> tuple[int, list[str]]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), mode, str(path), "--evidence-root", str(root)],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.stderr, "", result)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["ok"], result.returncode == 0)
        return result.returncode, payload["errors"]

    def run_check(self, value: dict, *, refresh: bool = True) -> tuple[int, list[str]]:
        if refresh:
            self.write_descriptor(value)
        path = self.root / "intake.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return self.run_cli("--record", path, self.root)

    def assert_denied(self, value: dict, reason: str, *, refresh: bool = True) -> None:
        status, errors = self.run_check(value, refresh=refresh)
        self.assertEqual(status, 1, errors)
        self.assertTrue(any(reason in error for error in errors), errors)

    def test_valid_no_model_provider(self) -> None:
        status, errors = self.run_check(record())
        self.assertEqual(status, 0, errors)
        self.assertEqual(errors, [])

    def test_valid_restricted_caller_supplied_asset(self) -> None:
        value = record()
        value["runtime"]["kind"] = "cpu"
        value["runtime"]["optional_dependency"] = "caller-supplied checkpoint"
        value["assets"] = [asset("model.f32", "restricted")]
        value["rights"]["redistribution"] = {"decision": "denied"}
        value["rights"]["public_playback"] = {"decision": "denied"}
        value["customer_scope"] = "denied"
        status, errors = self.run_check(value)
        self.assertEqual(status, 0, errors)

    def test_missing_digest_fails(self) -> None:
        for bad in ("not-a-digest", "sha256:" + "0" * 64):
            with self.subTest(bad=bad):
                value = record()
                value["source_digest"] = bad
                self.assert_denied(value, "record.source_digest: expected nonzero")

    def test_closed_asset_in_public_package_fails(self) -> None:
        value = record()
        value["packages_assets"] = True
        value["assets"] = [asset("model.f32", "closed")]
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("packages_assets" in error for error in errors), errors)
        self.assertTrue(any("closed" in error for error in errors), errors)

    def test_unknown_rights_denies_customer_use(self) -> None:
        value = record()
        value["rights"]["evaluation"] = {"decision": "unknown"}
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("customer_scope" in error for error in errors), errors)

    def test_needed_rights_must_be_allowed_at_provider_and_asset_levels(self) -> None:
        for level in ("provider", "asset"):
            for scope, flag, reason in (
                ("acquisition", "customer_scope", "customer_scope=allowed"),
                ("evaluation", None, "execution"),
                ("public_playback", "playback_scope", "playback_scope=allowed"),
                ("redistribution", "packages_assets", "requires an allowed decision"),
            ):
                for blocked in ("denied", "unknown"):
                    with self.subTest(level=level, scope=scope, blocked=blocked):
                        value = record()
                        item = asset()
                        value["assets"] = [item]
                        if flag is not None:
                            value[flag] = True if flag == "packages_assets" else "allowed"
                        rights_owner = value if level == "provider" else item
                        rights_owner["rights"][scope] = decision(blocked)
                        status, errors = self.run_check(value)
                        path = ("record" if level == "provider" else "record.assets[0]")
                        self.assertEqual(status, 1, errors)
                        self.assertTrue(any(
                            error.startswith(f"{path}.rights.{scope}:") and reason in error
                            for error in errors), errors)

    def test_rejected_review_denies_admission(self) -> None:
        value = record()
        value["review"]["decision"] = "rejected"
        self.assert_denied(value, "record.review.decision: admission requires approved review")

    def test_non_public_assets_need_explicit_evaluation_permission(self) -> None:
        for klass in ("restricted", "closed"):
            for blocked in ("denied", "unknown"):
                with self.subTest(klass=klass, blocked=blocked):
                    value = record()
                    item = asset(klass=klass)
                    item["rights"]["evaluation"] = decision(blocked)
                    item["rights"]["redistribution"] = decision("denied")
                    value["assets"] = [item]
                    self.assert_denied(value, "record.assets[0].rights.evaluation: execution")

    def test_bad_revision_or_missing_manifest_fails_without_crashing(self) -> None:
        for bad in (12, [], {}, "refs/heads/main", "abcdef1", "0" * 40):
            with self.subTest(bad=bad):
                value = record()
                value["source_revision"] = bad
                self.assert_denied(value, "record.source_revision: expected a full immutable Git object ID")
        value = record()
        value["source_revision"] = None
        self.assert_denied(value, "record.source_manifest_ref: required")

    def test_snapshot_inventory_binds_source_bytes(self) -> None:
        value = record()
        content = b"test source\n"
        file_hash = digest(content).removeprefix("sha256:")
        (self.root / "source.c").write_bytes(content)
        (self.root / "snapshot.sha256").write_bytes(f"{file_hash}  source.c\n".encode("ascii"))
        value["source_revision"] = None
        value["source_manifest_ref"] = "snapshot.sha256"
        value["source_digest"] = digest(f"source.c\0{file_hash}\n".encode("ascii"))
        self.assertEqual(self.run_check(value), (0, []))
        (self.root / "source.c").write_bytes(b"changed source\n")
        self.assert_denied(value, "source hash mismatch")

    def test_nonexistent_evidence_fails(self) -> None:
        value = record()
        value["rights"]["acquisition"]["evidence_ref"] = "absent.md"
        value["evaluation"]["evidence_ref"] = "../outside.md"
        status, errors = self.run_check(value)
        self.assertEqual(status, 1, errors)
        for path in ("record.rights.acquisition.evidence_ref", "record.evaluation.evidence_ref"):
            self.assertTrue(any(error.startswith(path) for error in errors), errors)

    def test_descriptor_digest_and_required_assets_are_bound(self) -> None:
        value = record()
        value["assets"] = [asset()]
        self.write_descriptor(value)
        value["assets"] = []
        value["descriptor_digest"] = DIGEST
        status, errors = self.run_check(value, refresh=False)
        self.assertEqual(status, 1, errors)
        self.assertIn("record.descriptor_digest: does not match descriptor bytes", errors)
        self.assertIn("record.descriptor_ref: record.assets do not match descriptor required_assets", errors)

    def test_v0_asset_size_limit_applies_to_the_total(self) -> None:
        value = record()
        value["assets"] = [asset(), asset("second.bin")]
        value["assets"][0]["byte_count"] = 512 * 1024 * 1024
        self.assert_denied(value, "record.assets: total exceeds 512 MiB")

    def test_checkpoint_provenance_and_reopen_condition(self) -> None:
        value = record()
        value["assets"] = [asset()]
        value["assets"][0]["checkpoint"] = {
            "upstream_revision": value["source_revision"],
            "tensor_config_ref": "evidence.md",
            "precision": "float32",
            "inventory_ref": "evidence.md",
        }
        self.assertEqual(self.run_check(value), (0, []))
        value["assets"][0]["checkpoint"]["upstream_revision"] = "latest"
        self.assert_denied(value, "checkpoint.upstream_revision: expected a full immutable Git object ID")
        del value["evaluation"]["scope"]
        self.assert_denied(value, "record.evaluation: missing keys ['scope']")
        del value["reopen_condition"]
        self.assert_denied(value, "missing keys ['reopen_condition']")

    def test_public_catalog_blocks_same_candidate_on_denied_policy(self) -> None:
        value = record()
        value["assets"] = [asset()]
        self.write_descriptor(value)
        catalog = self.root / "staged"
        self.assertEqual(self.run_cli("--public-catalog", catalog, self.root)[0], 1)
        intake = self.root / "docs/provider-intake/dsp.example.v0.json"
        intake.parent.mkdir(parents=True)
        intake.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.run_cli("--public-catalog", catalog, self.root), (0, []))
        for klass in ("restricted", "closed"):
            with self.subTest(klass=klass):
                value["assets"][0]["class"] = klass
                value["assets"][0]["rights"]["redistribution"] = decision("denied")
                intake.write_text(json.dumps(value), encoding="utf-8")
                status, errors = self.run_cli("--public-catalog", catalog, self.root)
                self.assertEqual(status, 1, errors)
                self.assertTrue(any(
                    f"{klass} asset excludes provider from public discovery" in error for error in errors), errors)
        value["assets"][0]["class"] = "public"
        value["rights"]["redistribution"] = decision("denied")
        intake.write_text(json.dumps(value), encoding="utf-8")
        status, errors = self.run_cli("--public-catalog", catalog, self.root)
        self.assertEqual(status, 1, errors)
        self.assertTrue(any("public distribution requires an allowed decision" in error for error in errors), errors)

    def test_example_has_real_provenance_but_no_approval(self) -> None:
        status, errors = self.run_cli("--record", EXAMPLE, ROOT)
        self.assertEqual(status, 1, errors)
        self.assertEqual(errors, [
            "record.rights.acquisition: execution requires an allowed decision",
            "record.rights.evaluation: execution requires an allowed decision",
            "record.review.decision: admission requires approved review",
        ])

    def test_duplicate_asset_id_fails(self) -> None:
        value = record()
        value["assets"] = [asset("model.f32"), asset("model.f32")]
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("duplicate" in error for error in errors), errors)

    def test_package_with_restricted_asset_fails(self) -> None:
        value = record()
        value["packages_assets"] = True
        value["assets"] = [asset("model.f32", "restricted")]
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("non-public" in error for error in errors), errors)

    def test_allowed_decision_needs_evidence(self) -> None:
        value = record()
        value["rights"]["evaluation"] = {"decision": "allowed"}
        status, errors = self.run_check(value)
        self.assertNotEqual(status, 0)
        self.assertTrue(any("needs evidence_ref" in error for error in errors), errors)

    def test_schema_document_is_valid_json(self) -> None:
        schema = json.loads((ROOT / "schemas/provider-intake.schema.json").read_text())
        self.assertEqual(schema["$id"], "audio-sdk/provider-intake/0.1")
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
