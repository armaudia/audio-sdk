"""Unit checks for the task-local SpeexDSP MDF reference evidence."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parent
TASK_DIR = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import evaluate  # noqa: E402
import fixture  # noqa: E402
import verify  # noqa: E402

ORACLE = TASK_DIR / "evidence" / "oracle.json"
SOURCES = TASK_DIR / "SOURCES.sha256"
LEGACY_BLOBS = TASK_DIR / "LEGACY_BLOBS.sha1"
SDK_ROOT = TASK_DIR.parents[2]
WS_ROOT = pathlib.Path("/Users/htsakanyan/workspace/audio/audioml")


class FixtureTests(unittest.TestCase):
    def test_generation_is_deterministic(self) -> None:
        first = fixture.generate()
        second = fixture.generate()
        self.assertEqual(set(first), set(fixture.CASES))
        for case in fixture.CASES:
            self.assertEqual(first[case], second[case])
            self.assertEqual(len(first[case]["render"]), fixture.SAMPLE_COUNT)
            self.assertEqual(len(first[case]["capture"]), fixture.SAMPLE_COUNT)

    def test_f32_pack_roundtrip(self) -> None:
        values = [0.0, 0.25, -0.5, 1.0]
        unpacked = struct.unpack("<4f", fixture.pack_f32(values))
        self.assertEqual(unpacked, tuple(values))

    def test_metric_helpers(self) -> None:
        values = [0.5] * 32
        self.assertEqual(fixture.erle_db(values, values, 0, 32), 0.0)
        self.assertEqual(fixture.amplitude_ratio(values, values, 0, 32), 1.0)

    def test_canonical_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            fixture.canonical({"bad": float("nan")})

    def test_fixture_digest_is_frozen(self) -> None:
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        streams = fixture.generate()
        digests = {
            case: {
                "render": fixture.digest_f32(values["render"]),
                "capture": fixture.digest_f32(values["capture"]),
            }
            for case, values in streams.items()
        }
        payload = {"spec": fixture.spec(), "digests": digests}
        digest = fixture.digest_text(fixture.canonical(payload))
        self.assertEqual(digest, oracle["fixture_digest"])
        self.assertEqual(digests, oracle["fixture_digests"])


class OracleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.oracle = json.loads(ORACLE.read_text(encoding="utf-8"))

    def test_oracle_sidecar(self) -> None:
        digest = hashlib.sha256(ORACLE.read_bytes()).hexdigest()
        sidecar = ORACLE.with_suffix(".json.sha256").read_text(
            encoding="utf-8").split()[0]
        self.assertEqual(digest, sidecar)

    def test_repeat_protocol(self) -> None:
        self.assertEqual(self.oracle["repeat_count"], 3)
        self.assertEqual(set(self.oracle["cases"]), set(fixture.CASES))
        for name, case in self.oracle["cases"].items():
            self.assertEqual(len(case["output_digests"]), 3, name)
            self.assertEqual(len(set(case["output_digests"])), 1, name)
            self.assertTrue(case["repeat_bytes_identical"], name)
            self.assertEqual(case["nonfinite_count"], 0, name)
            self.assertEqual(case["duration_samples"], fixture.SAMPLE_COUNT, name)

    def test_exact_frozen_values(self) -> None:
        expected = {
            "echo_only": (16.453939, 0.171306,
                          "4b6b1ba808f3f3919aa6f64dcec1661545208d0e382cb9199ff2a5a6d5ac63eb"),
            "near_end_only": (0.0, 1.0,
                              "0559befd3a5c3fe44d67f2c93a26e4df4b27ebba2c9a501dcd1a2551c491da05"),
            "overlap_small": (16.453939, 0.985161,
                              "abb6cdc25f2371ecbeac05ef6ba564d51adf0c66390da09091948f23d2ab9327"),
            "no_reference_passthrough": (0.0, 1.0,
                                         "198eaadb2fb1eed9db1fab8f99e58608cd33c84f55c3ff3aea6d2c1d4fcb82d5"),
            "misaligned_reference": (16.888932, 0.159131,
                                     "a1fa383eacc50cde77e8881a0369b67fe09f233b0f8a76769ad0734d2f1ab71b"),
        }
        for name, (erle, ratio, output_digest) in expected.items():
            case = self.oracle["cases"][name]
            self.assertEqual(case["erle_db_converged"], erle, name)
            self.assertEqual(case["output_over_near_rms_overlap"], ratio, name)
            self.assertEqual(case["output_digests"][0], output_digest, name)

    def test_passthrough_controls(self) -> None:
        for name in ("near_end_only", "no_reference_passthrough"):
            case = self.oracle["cases"][name]
            self.assertTrue(case["passthrough_bit_exact"])
            self.assertEqual(case["output_digests"][0], case["capture_digest"])

    def test_negative_controls_passed(self) -> None:
        controls = self.oracle["controls"]
        self.assertEqual(set(controls), {
            "pinned_sources_verified", "reject_missing_render",
            "reject_nonfinite_capture", "reject_wrong_length", "reject_wrong_rate"})
        for name, control in controls.items():
            self.assertTrue(control["passed"], name)
            if name != "pinned_sources_verified":
                self.assertFalse(control["output_written"], name)

    def test_measured_limitations_are_recorded(self) -> None:
        # Not a quality gate: these assertions only prevent silently hiding
        # the observed non-ideal evidence in the frozen record.
        cases = self.oracle["cases"]
        self.assertLess(cases["overlap_small"]["output_over_near_rms_overlap"], 1.0)
        self.assertGreater(cases["misaligned_reference"]["erle_db_converged"],
                           cases["echo_only"]["erle_db_converged"])


class PinTests(unittest.TestCase):
    def test_source_pins_resolve_and_are_recorded(self) -> None:
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        sources = evaluate.load_sources(SOURCES, SDK_ROOT, WS_ROOT)
        self.assertEqual(len(sources), 16)
        self.assertEqual(sources, oracle["source_digests"])
        self.assertEqual(oracle["source_manifest_digest"],
                         hashlib.sha256(SOURCES.read_bytes()).hexdigest())

    def test_tampered_pin_manifest_fails_closed(self) -> None:
        original = SOURCES.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            bad = pathlib.Path(directory) / "SOURCES.sha256"
            lines = original.splitlines()
            digest, name = lines[0].split(None, 1)
            lines[0] = "0" * len(digest) + "  " + name
            bad.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                evaluate.load_sources(bad, SDK_ROOT, WS_ROOT)

    def test_legacy_blob_ids_match_exact_files(self) -> None:
        self.assertEqual(verify.check_blobs(LEGACY_BLOBS, SDK_ROOT, WS_ROOT, None), 7)

    def test_legacy_rev_parse_when_checkout_available(self) -> None:
        repo = WS_ROOT / "cpp-library"
        if not (repo / ".git").exists():
            self.skipTest("legacy checkout unavailable")
        self.assertEqual(
            verify.check_blobs(LEGACY_BLOBS, SDK_ROOT, WS_ROOT, repo), 7)


class OptionalCliTests(unittest.TestCase):
    def test_cli_rejects_nonfinite_input(self) -> None:
        cli = os.environ.get("MDF_CLI")
        if cli is None or not pathlib.Path(cli).is_file():
            self.skipTest("MDF_CLI not set to a built reference CLI")
        streams = fixture.generate()
        case = streams["echo_only"]
        bad = list(case["capture"])
        bad[17] = float("nan")
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "r.f32").write_bytes(fixture.pack_f32(case["render"]))
            (root / "c.f32").write_bytes(fixture.pack_f32(bad))
            result = subprocess.run(
                [cli, "--render", str(root / "r.f32"), "--capture", str(root / "c.f32"),
                 "--output", str(root / "o.f32")], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "o.f32").exists())


if __name__ == "__main__":
    unittest.main()
