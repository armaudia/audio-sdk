# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for SDK-CLEARERVOICE-MOSSFORMER2-SE-48K.

No network, no model, no real audio, no runtime and no skips.  The checks use
only the task-local synthetic fixture and temporary caller-owned placeholder
files.

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
REPORT_CACHE = None


def report() -> dict:
    global REPORT_CACHE
    if REPORT_CACHE is None:
        REPORT_CACHE = reference.build_report()
    return REPORT_CACHE


def asset_manifest(root: Path, **overrides):
    model = root / reference.MODEL_FILENAME_HINT
    pointer = root / "last_best_checkpoint"
    if not model.exists():
        model.write_bytes(b"caller-owned-placeholder-model")
    if not pointer.exists():
        pointer.write_text(reference.MODEL_FILENAME_HINT + "\n", encoding="utf-8")
    manifest = {
        "checkpoint_file": reference.MODEL_FILENAME_HINT,
        "checkpoint_pointer_path": str(pointer),
        "checkpoint_pointer_sha256": reference.sha256_file(pointer),
        "channels": reference.CHANNELS,
        "input_format": "float32",
        "license_decision": "not_cleared",
        "mode": "offline",
        "model_bytes": model.stat().st_size,
        "model_name": reference.MODEL_NAME,
        "model_path": str(model),
        "model_sha256": reference.sha256_file(model),
        "package_version": reference.UPSTREAM_PACKAGE_VERSION,
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "source_revision": reference.UPSTREAM_SOURCE_REVISION,
    }
    manifest.update(overrides)
    return manifest


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_bytes_sorted_and_newline(self):
        data = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertTrue(data.endswith(b"\n"))
        self.assertLess(data.index(b'"a"'), data.index(b'"b"'))

    def test_strict_loads_accepts_object(self):
        self.assertEqual(reference.strict_loads('{"a": 1}'), {"a": 1})

    def test_strict_loads_rejects_duplicate_key(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1, "a": 2}')

    def test_strict_loads_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": NaN}')

    def test_strict_loads_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": Infinity}')

    def test_strict_loads_rejects_trailing_data(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1} trailing')

    def test_strict_object_loads_rejects_array_root(self):
        with self.assertRaises(ValueError):
            reference.strict_object_loads("[]")

    def test_canonical_normalizes_negative_zero(self):
        data = reference.canonical_bytes({"a": -0.0})
        self.assertIn(b'"a": 0.0', data)
        self.assertFalse(reference.has_negative_zero({"a": 0.0}))

    def test_round9_is_stable(self):
        self.assertEqual(reference.round9(1.234567890123), 1.23456789)
        self.assertEqual(reference.round9(-0.0), 0.0)
        self.assertIsNone(reference.round9(None))


class FixtureTests(unittest.TestCase):
    def test_fixture_lengths(self):
        fixture = reference.build_fixture()
        for key in ("clean", "noise", "observed"):
            self.assertEqual(len(fixture[key]), reference.TOTAL_SAMPLES)

    def test_segments_cover_exactly(self):
        segments = reference.fixture_spec()
        self.assertEqual(segments[0]["start_sample"], 0)
        self.assertEqual(segments[-1]["end_sample"], reference.TOTAL_SAMPLES)
        for left, right in zip(segments, segments[1:]):
            self.assertEqual(left["end_sample"], right["start_sample"])

    def test_fixture_is_deterministic(self):
        first = reference.build_fixture()
        second = reference.build_fixture()
        self.assertEqual(first["observed"], second["observed"])
        self.assertEqual(reference.fixture_digests(), reference.FIXTURE_DIGESTS)

    def test_silence_segments_are_exact_zero(self):
        fixture = reference.build_fixture()
        for segment in reference.SEGMENTS:
            if segment["kind"] == "silence":
                start = segment["start"]
                end = segment["end"]
                self.assertEqual(set(fixture["clean"][start:end]), {0})
                self.assertEqual(set(fixture["noise"][start:end]), {0})

    def test_observed_is_bounded_sum(self):
        fixture = reference.build_fixture()
        for index in range(0, reference.TOTAL_SAMPLES, 997):
            expected = reference.clamp16(
                fixture["clean"][index] + fixture["noise"][index]
            )
            self.assertEqual(fixture["observed"][index], expected)

    def test_int16_bytes_length(self):
        fixture = reference.build_fixture()
        self.assertEqual(
            len(reference.int16_bytes(fixture["observed"])),
            reference.TOTAL_SAMPLES * 2,
        )

    def test_fixture_spec_digest(self):
        self.assertEqual(reference.FIXTURE_SPEC_DIGEST,
                         reference.fixture_spec_digest())
        self.assertEqual(len(reference.FIXTURE_SPEC_DIGEST), 64)


class SurrogateTests(unittest.TestCase):
    def test_dc_block_preserves_length(self):
        values = [100, -200, 300] * 100
        output, clipped = reference.dc_block(values)
        self.assertEqual(len(output), len(values))
        self.assertEqual(clipped, 0)

    def test_dc_block_is_deterministic(self):
        values = reference.build_fixture()["observed"][:4000]
        self.assertEqual(reference.dc_block(values),
                         reference.dc_block(values))

    def test_dc_block_silence_exact_zero(self):
        output, clipped = reference.dc_block([0] * 1000)
        self.assertEqual(set(output), {0})
        self.assertEqual(clipped, 0)

    def test_dc_block_is_finite_and_bounded(self):
        output, _ = reference.dc_block(reference.build_fixture()["observed"])
        self.assertTrue(all(isinstance(value, int) for value in output))
        self.assertTrue(all(-32768 <= value <= 32767 for value in output))


class AssetTests(unittest.TestCase):
    def test_generic_mechanics_validate_without_pinning(self):
        with tempfile.TemporaryDirectory() as raw:
            details = reference.validate_asset_manifest(
                asset_manifest(Path(raw))
            )
        self.assertTrue(details["valid"])
        self.assertFalse(details["pinned_model"])
        self.assertFalse(details["loaded"])
        self.assertFalse(details["executed"])
        self.assertFalse(details["imported"])

    def test_candidate_rejects_unrecorded_identity(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = asset_manifest(Path(raw), license_decision="cleared")
            with self.assertRaises(reference.Reject) as caught:
                reference.admit_candidate_asset(manifest)
        self.assertEqual(caught.exception.reason,
                         "asset_model_identity_unrecorded")

    def test_candidate_rejects_uncleared_rights(self):
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(reference.Reject) as caught:
                reference.admit_candidate_asset(asset_manifest(Path(raw)))
        self.assertEqual(caught.exception.reason, "asset_rights_not_cleared")

    def test_asset_rejects_absent_and_relative_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name, override, reason in (
                ("absent", {"model_path": str(root / "missing.pt")},
                 "asset_file_missing:model_path"),
                ("relative", {"model_path": reference.MODEL_FILENAME_HINT},
                 "asset_path_not_absolute:model_path"),
            ):
                with self.subTest(name=name):
                    with self.assertRaises(reference.Reject) as caught:
                        reference.validate_asset_manifest(
                            asset_manifest(root, **override)
                        )
                    self.assertEqual(caught.exception.reason, reason)

    def test_asset_rejects_hash_byte_and_shape_errors(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = asset_manifest(root)
            cases = {
                "model_hash": {"model_sha256": "0" * 64},
                "pointer_hash": {"checkpoint_pointer_sha256": "0" * 64},
                "bytes": {"model_bytes": manifest["model_bytes"] + 1},
                "extra": {"extra": True},
                "wrong_source": {"source_revision": "0" * 40},
                "wrong_package": {"package_version": "0.0.0"},
                "wrong_model": {"model_name": "MossFormer2_SE_16K"},
                "wrong_rate": {"sample_rate_hz": 16000},
                "wrong_channels": {"channels": 2},
                "wrong_format": {"input_format": "int16"},
                "wrong_mode": {"mode": "streaming"},
                "wrong_license": {"license_decision": "unknown"},
                "pointer_content": {"checkpoint_file": "other.pt"},
            }
            for name, override in cases.items():
                with self.subTest(name=name):
                    with self.assertRaises(reference.Reject):
                        reference.validate_asset_manifest(
                            manifest | override
                        )

    def test_asset_rejects_missing_field(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = asset_manifest(Path(raw))
            manifest.pop("model_name")
            with self.assertRaises(reference.Reject) as caught:
                reference.validate_asset_manifest(manifest)
        self.assertEqual(caught.exception.reason, "asset_field_set_mismatch")


class ConfigTests(unittest.TestCase):
    def test_default_config_accepted(self):
        self.assertEqual(reference.validate_config(reference.default_config()),
                         reference.default_config())

    def test_config_rejects_geometry(self):
        for name, override in (
            ("sample_rate", {"sample_rate_hz": 16000}),
            ("channels", {"channels": 2}),
            ("format", {"input_format": "int16"}),
            ("frame_zero", {"frame_samples": 0}),
            ("frame_160", {"frame_samples": 160}),
            ("mode", {"mode": "streaming"}),
            ("resampling", {"resampling": "48k_to_16k"}),
        ):
            with self.subTest(name=name):
                config = reference.default_config() | override
                with self.assertRaises(reference.Reject):
                    reference.validate_config(config)

    def test_config_rejects_runtime_and_extra(self):
        for name, override in (
            ("real_runtime", {"real_runtime": True}),
            ("model_used", {"model_used": True}),
            ("extra", {"extra": True}),
            ("schema", {"schema_id": "audio-sdk/other"}),
        ):
            with self.subTest(name=name):
                config = reference.default_config() | override
                with self.assertRaises(reference.Reject):
                    reference.validate_config(config)

    def test_config_rejects_epochs(self):
        for name, override in (
            ("negative", {"epoch": -1}),
            ("bool", {"epoch": True}),
            ("float", {"epoch": 1.0}),
            ("first", {"first_input_sample": 1}),
        ):
            with self.subTest(name=name):
                config = reference.default_config() | override
                with self.assertRaises(reference.Reject):
                    reference.validate_config(config)


class SessionTests(unittest.TestCase):
    def test_adverse_chunks_leave_state_unchanged(self):
        session = reference.Session()
        digest = session.state_digest()
        for chunk in ([], "abcd", None, [[0.0]], [True], [float("nan")],
                      [float("inf")], [float("-inf")], [1.5], [-1.5]):
            with self.assertRaises(reference.Reject):
                session.push(chunk)
            self.assertEqual(session.state_digest(), digest)
        self.assertEqual(session.accepted_samples, 0)

    def test_nonfinite_is_not_silence(self):
        session = reference.Session()
        session.push([0.25] * 480)
        digest = session.state_digest()
        with self.assertRaises(reference.Reject) as caught:
            session.push([float("nan")])
        self.assertEqual(caught.exception.reason, "chunk_nonfinite")
        self.assertEqual(session.state_digest(), digest)
        self.assertEqual(session.accepted_samples, 480)

    def test_silence_session_exact_zero(self):
        session = reference.Session()
        session.push([0.0] * 2048)
        output = session.finish()
        self.assertEqual(len(output), 2048)
        self.assertEqual(set(output), {0})

    def test_chunking_parity(self):
        values = reference.float_samples(
            reference.build_fixture()["observed"][:12000]
        )
        reference_bytes = None
        for size in (1, 7, 160, 480, 481, 4096, 12000):
            session = reference.Session()
            for start in range(0, len(values), size):
                session.push(values[start:start + size])
            payload = reference.int16_bytes(session.finish())
            if reference_bytes is None:
                reference_bytes = payload
            self.assertEqual(payload, reference_bytes)

    def test_partial_tail_preserved(self):
        values = reference.float_samples(
            reference.build_fixture()["observed"][:48123]
        )
        session = reference.Session()
        session.push(values)
        output = session.finish()
        self.assertEqual(len(output), 48123)

    def test_reset_replays_fresh_session(self):
        values = reference.float_samples(
            reference.build_fixture()["observed"][:4000]
        )
        session = reference.Session()
        session.push(values)
        session.reset(1)
        session.push(values)
        after = reference.int16_bytes(session.finish())
        fresh = reference.Session(reference.default_config(1))
        fresh.push(values)
        self.assertEqual(after, reference.int16_bytes(fresh.finish()))

    def test_reset_rejects_non_higher_epoch(self):
        session = reference.Session(reference.default_config(1))
        digest = session.state_digest()
        for epoch in (1, 0, -1, True):
            with self.assertRaises(reference.Reject):
                session.reset(epoch)
            self.assertEqual(session.state_digest(), digest)

    def test_lifecycle_finish_and_close(self):
        session = reference.Session()
        session.push([0.0] * 160)
        session.finish()
        with self.assertRaises(reference.Reject) as caught:
            session.finish()
        self.assertEqual(caught.exception.reason, "session_already_finished")
        session.close()
        with self.assertRaises(reference.Reject) as closed:
            session.push([0.0])
        self.assertEqual(closed.exception.reason, "session_closed")

    def test_out_of_range_rejected(self):
        session = reference.Session()
        for value in (1.0001, -1.0001, 2.0):
            with self.assertRaises(reference.Reject) as caught:
                session.push([value])
            self.assertEqual(caught.exception.reason, "chunk_range")


class ReportTests(unittest.TestCase):
    def test_metrics_are_bounded(self):
        metrics = report()["metrics"]
        self.assertEqual(metrics["nonfinite_output_samples"], 0)
        self.assertEqual(metrics["output_peak_clipped_samples"], 0)
        self.assertTrue(metrics["silence_exact_zero"])
        self.assertLessEqual(metrics["max_abs_output"], 1.0)
        self.assertEqual(metrics["scored_samples"], reference.TOTAL_SAMPLES)
        self.assertIsNotNone(metrics["identity"]["si_sdr_db"])
        self.assertIsNotNone(metrics["surrogate"]["si_sdr_db"])

    def test_disposition_is_defer_and_not_qualified(self):
        payload = report()
        self.assertEqual(payload["decision"], "DEFER")
        self.assertEqual(payload["status"], reference.STATUS)
        self.assertEqual(payload["evidence_status"], "incomplete")
        self.assertTrue(payload["proposal_only"])
        self.assertEqual(payload["qualification"]["status"], "not_qualified")
        self.assertEqual(payload["qualification"]["release_gate_count"], 8)
        self.assertTrue(payload["qualification"]["all_blocked"])

    def test_eight_gates_are_blocked(self):
        gates = report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         reference.release_gate_ids())
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_missing_result_rule(self):
        payload = report()
        self.assertTrue(payload["no_missing_result_qualifies_candidate"])
        self.assertTrue(payload["missing_results"])
        self.assertTrue(payload["negative_claims"])

    def test_controls_fail_closed(self):
        controls = report()["controls"]
        for name in ("asset", "config", "chunk"):
            self.assertTrue(controls[name]["rejected_all"], name)
        self.assertTrue(controls["streaming_parity"]["all_identical"])
        self.assertTrue(controls["partial_tail"]["length_preserved"])
        self.assertTrue(controls["partial_tail"]["chunked_prefix_matches"])
        self.assertTrue(controls["reset"]["fresh_matches_reset"])
        self.assertTrue(controls["reset"]["stale_digest_unchanged"])
        self.assertTrue(controls["silence"]["exact_zero"])
        self.assertFalse(controls["nonfinite_counter"]["counted_as_silence"])
        self.assertTrue(
            controls["nonfinite_counter"]["accepted_counter_unchanged"]
        )

    def test_report_three_builds_identical(self):
        contract = reference.contract_bytes()
        digest = hashlib.sha256(contract).hexdigest()
        payloads = [
            reference.canonical_report_bytes(
                reference.build_report(contract_sha256=digest)
            )
            for _ in range(3)
        ]
        self.assertEqual(payloads[0], payloads[1])
        self.assertEqual(payloads[1], payloads[2])

    def test_contract_digest_matches(self):
        self.assertEqual(
            report()["contract_sha256"],
            hashlib.sha256(reference.contract_bytes()).hexdigest(),
        )

    def test_board_identity_is_stable_only(self):
        board = report()["board_row"]
        self.assertFalse(board["full_tasks_json_hashed"])
        self.assertEqual(board["stable_sha256"],
                         reference.BOARD_ROW_STABLE_SHA256)
        self.assertEqual(board["stable_fields"],
                         reference.BOARD_ROW_STABLE_FIELDS)

    def test_boundary_is_closed(self):
        boundary = report()["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertFalse(boundary["provider_registration"])
        self.assertFalse(boundary["shared_build_or_ci_change"])
        self.assertFalse(boundary["surrogate_is_candidate"])
        self.assertFalse(boundary["network_used"])

    def test_asset_pins_are_absent_not_loaded(self):
        pins = report()["asset_pins"]
        for key in ("model_checkpoint", "source_checkout",
                    "runtime_environment"):
            self.assertFalse(pins[key]["present"], key)
        self.assertFalse(pins["model_checkpoint"]["loaded"])
        self.assertIsNone(pins["model_checkpoint"]["sha256"])
        self.assertFalse(pins["model_checkpoint"]["identity_recorded"])


class ReadmeAndPinTests(unittest.TestCase):
    def test_readme_tables_roundtrip(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        sections = ("source", "boundary")
        updated = reference.update_readme_tables(
            text, report(), sections=sections
        )
        self.assertEqual(
            reference.update_readme_tables(updated, report(), sections=sections),
            updated,
        )
        counts = reference.verify_readme_digests(updated, sections=sections)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))

    def test_pin_parser_rejects_malformed(self):
        for text in ("deadbeef  key", "0" * 64 + " key"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(text)

    def test_pin_parser_rejects_duplicates(self):
        text = "0" * 64 + "  key\n" + "1" * 64 + "  key\n"
        with self.assertRaises(ValueError):
            reference.parse_pin_lines(text)

    def test_allowed_pin_keys_cover_artifacts(self):
        keys = reference.allowed_pin_keys()
        for name in reference.EXPECTED_DIR_FILES:
            if name == "SOURCES.sha256":
                continue
            self.assertIn(reference.TASK_PREFIX + "/" + name, keys)
        self.assertEqual(len(reference.GATE_REQUIREMENTS), 8)
        self.assertEqual(len(reference.EXACT_BLOCKERS), 6)


class ScopeTests(unittest.TestCase):
    def test_reference_has_no_network_or_model_imports(self):
        source = (HERE / "reference.py").read_text(encoding="utf-8")
        for token in ("import requests", "import socket", "import torch",
                      "import clearvoice", "urllib.request", "http.client"):
            self.assertNotIn(token, source)
        self.assertNotIn("TASKS.json\")", source)

    def test_task_prefix_is_local_only(self):
        self.assertEqual(reference.TASK_PREFIX,
                         "docs/task-evidence/" + reference.COMPONENT)
        self.assertEqual(len(reference.QUALIFICATION), len("not_qualified"))
        self.assertEqual(reference.DECISION, "DEFER")
        self.assertEqual(reference.GATE_REQUIREMENTS[0][0],
                         "exact_source_and_model_identity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
