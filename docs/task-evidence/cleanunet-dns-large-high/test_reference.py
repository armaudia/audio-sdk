# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the CleanUNet DNS-large-high evidence.

No network, no downloads, no weights, no PyTorch, no skips.  Every check runs
against the synthetic boundary model only; nothing here qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_GATES = {
    "exact_asset_identity",
    "runtime_admission",
    "artifact_rights",
    "exact_reference_parity",
    "rights_cleared_paired_cohort",
    "independent_scoring_and_listening",
    "target_runtime_timing",
    "provider_intake_and_default_selection",
}
EXPECTED_CONFIG = {
    "wrong_sample_rate": "sample_rate_hz_mismatch",
    "wrong_channels": "channels_mismatch",
    "wrong_sample_format": "sample_format_mismatch",
    "wrong_frame_samples": "frame_samples_mismatch",
    "wrong_max_clip_samples": "max_clip_samples_mismatch",
    "streaming_mode_unsupported": "mode_unsupported",
    "caller_asset_unavailable": "asset_not_admitted",
    "surrogate_without_opt_in": "surrogate_opt_in_required",
    "wrong_asset_identity": "asset_identity_mismatch",
    "wrong_asset_bytes": "asset_identity_mismatch",
}
EXPECTED_CLIPS = {
    "empty_clip": "rejected:clip_empty",
    "oversized_clip": "rejected:clip_oversized",
    "nonfinite_sample": "rejected:sample_nonfinite",
    "infinite_sample": "rejected:sample_nonfinite",
    "string_clip": "rejected:clip_type_invalid",
    "boolean_sample": "rejected:sample_type_invalid",
    "out_of_range_sample": "rejected:sample_out_of_range",
    "second_clip": "rejected:offline_clip_already_complete",
    "after_close": "rejected:session_closed",
}


def _no_duplicates(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError("duplicate key: " + key)
        seen.add(key)
    return dict(pairs)


def load_strict(name: str):
    return json.loads((HERE / name).read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)


def report() -> dict:
    return reference.build_report()


class TestCanonicalJson(unittest.TestCase):
    def test_canonical_bytes_sorted_compact(self):
        value = {"b": 1, "a": [2, 3]}
        self.assertEqual(reference.canonical_bytes(value), b'{"a":[2,3],"b":1}')

    def test_negative_zero_normalized(self):
        self.assertEqual(reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}')

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference.canonical_bytes({"x": bad})

    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.json"
            path.write_text('{"a":1,"a":2}\n', encoding="ascii")
            with self.assertRaises(ValueError):
                json.loads(path.read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)

    def test_report_bytes_end_with_single_newline(self):
        payload = reference.canonical_report_bytes(report())
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        payload.decode("ascii")


class TestTaskIdentity(unittest.TestCase):
    def test_stable_digest_is_stable_and_excludes_mutable_fields(self):
        identity = reference.task_identity()
        self.assertEqual(identity["stable_sha256"], reference.stable_identity_digest())
        for key in ("status", "owner", "claim", "review", "handoff", "blocked_reason"):
            self.assertNotIn(key, identity)
        self.assertFalse(identity["board_full_file_hashed"])
        self.assertEqual(identity["id"], reference.TASK)

    def test_stable_digest_ignores_reordered_input(self):
        reordered = dict(reversed(list(reference.STABLE_TASK_IDENTITY.items())))
        self.assertEqual(
            reference.stable_identity_digest(reordered),
            reference.stable_identity_digest(),
        )

    def test_mutable_board_file_is_not_pinned(self):
        text = "\n".join(reference.SOURCE_PINS) + "\n" + "\n".join(reference.BOUNDARY_PINS)
        self.assertNotIn("plan/swarm/TASKS.json", text)
        self.assertFalse(report()["pins"]["board_file_pinned"])


class TestAssetBoundary(unittest.TestCase):
    def test_exact_candidate_pins(self):
        ref = reference.asset_ref()
        self.assertEqual(ref["asset_id"], "pretrained.pkl")
        self.assertEqual(ref["byte_count"], 184_336_765)
        self.assertEqual(
            ref["sha256"],
            "513d9e4f69483bf2bcc3059dd6b3644140763bf3f22df41d7ee366cc2cbd1829",
        )
        self.assertEqual(ref["lfs_path"], "exp/DNS-large-high/checkpoint/pretrained.pkl")
        self.assertEqual(ref["source_revision"], "2f930ce6660e76b6265c07da4027b414adb24ab1")
        self.assertEqual(ref["model_revision"], ref["source_revision"])
        self.assertEqual(ref["storage"], "external")
        self.assertFalse(ref["runtime_available"])
        self.assertFalse(ref["runtime_dependency_pinned"])
        self.assertIsNone(ref["runtime_lock_digest"])
        self.assertFalse(ref["rights_cleared"])
        self.assertFalse(ref["asset_bytes_read"])

    def test_candidate_admission_blocked(self):
        admission = reference.asset_admission()
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(
            admission["reason_codes"],
            [
                "asset_bytes_absent",
                "runtime_unavailable",
                "runtime_dependency_unpinned",
                "rights_not_cleared",
            ],
        )
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vendor_runtime_invoked"])

    def test_candidate_bytes_absent(self):
        self.assertFalse((reference.SDK_ROOT / reference.ASSET_PATH).is_file())
        self.assertFalse(report()["asset_boundary"]["bytes_present_in_worktree"])

    def test_synthetic_admission_control_is_not_candidate(self):
        control = reference.synthetic_admission_control()
        self.assertEqual(control["status"], "admitted_synthetic_control")
        self.assertFalse(control["candidate_asset"])
        self.assertFalse(control["vendor_runtime_invoked"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertNotEqual(control["asset_id"], reference.ASSET_ID)

    def test_synthetic_asset_is_derived_not_model_bytes(self):
        self.assertEqual(
            reference.SYNTHETIC_ASSET_SHA256,
            hashlib.sha256(reference.SYNTHETIC_ASSET_BYTES).hexdigest(),
        )
        self.assertLess(len(reference.SYNTHETIC_ASSET_BYTES), 100_000)
        self.assertNotEqual(len(reference.SYNTHETIC_ASSET_BYTES), reference.ASSET_BYTES)
        self.assertNotIn(b"\x80\x02", reference.SYNTHETIC_ASSET_BYTES)
        self.assertNotIn(b"PK\x03\x04", reference.SYNTHETIC_ASSET_BYTES)


class TestPaddingContract(unittest.TestCase):
    def test_official_padded_length_values(self):
        self.assertEqual(reference.official_padded_length(160), 766)
        self.assertEqual(reference.official_padded_length(16_000), 16_126)
        self.assertEqual(reference.official_padded_length(32_000), 32_254)
        self.assertEqual(reference.official_padded_length(32_123), 32_254)
        self.assertEqual(reference.official_padded_length(160_000), 160_254)

    def test_padded_length_formula_and_residue(self):
        for length in (2, 5, 97, 160, 1_000, 31_999, 32_000, 160_000):
            padded = reference.official_padded_length(length)
            self.assertEqual(padded % 256, 254, length)
            self.assertGreaterEqual(padded, length, length)

    def test_matches_reference_recurrence(self):
        def recurrence(length: int) -> int:
            size = length
            for _ in range(8):
                size = 1 + math.ceil((size - 4) / 2) if size >= 4 else 1
            for _ in range(8):
                size = (size - 1) * 2 + 4
            return size

        for length in (1, 4, 159, 160, 16_000, 32_123, 160_000):
            self.assertEqual(reference.official_padded_length(length), recurrence(length), length)

    def test_contract_rows(self):
        contract = report()["padding_contract"]
        self.assertEqual(contract["ten_second_clip_padded_to"], 160_254)
        self.assertEqual(contract["ten_second_clip_padding_samples"], 254)
        self.assertEqual(contract["padded_length_residue_mod_256"], 254)
        self.assertTrue(contract["padded_always_at_least_input"])


class TestConfigRejections(unittest.TestCase):
    def test_matrix_exact_statuses(self):
        cases = reference.config_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_CONFIG) | {"synthetic_admission_control"})
        for name, reason in EXPECTED_CONFIG.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], "rejected")
                self.assertEqual(cases[name]["reason_codes"], [reason])
                self.assertFalse(cases[name]["processing_attempted"])
        self.assertEqual(cases["synthetic_admission_control"]["status"], "admitted_synthetic_control")

    def test_unknown_key_rejected(self):
        config = reference.default_config()
        config["unknown"] = 1
        self.assertEqual(reference.admit_config(config)["reason_codes"], ["config_keys_mismatch"])

    def test_non_dict_config_rejected(self):
        self.assertEqual(reference.admit_config([])["reason_codes"], ["config_type_invalid"])

    def test_candidate_config_never_creates(self):
        session = reference.OfflineSession()
        self.assertFalse(session.created)
        result = session.process_clip([0.0] * reference.FRAME_SAMPLES)
        self.assertEqual(result["status"], "rejected:not_admitted")
        self.assertFalse(result["qualifies"])

    def test_synthetic_requires_opt_in(self):
        config = reference.synthetic_config()
        config["surrogate_opt_in"] = False
        result = reference.admit_config(config)
        self.assertEqual(result["reason_codes"], ["surrogate_opt_in_required"])


class TestClipRejections(unittest.TestCase):
    def test_matrix_exact_statuses_and_state_unchanged(self):
        cases = reference.clip_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_CLIPS))
        for name, status in EXPECTED_CLIPS.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], status)
                self.assertTrue(cases[name]["state_unchanged"])
                self.assertEqual(cases[name]["output_samples"], 0)

    def test_boundary_lengths(self):
        session = reference.OfflineSession(reference.synthetic_config())
        result = session.process_clip([0.0] * reference.MAX_CLIP_SAMPLES)
        self.assertEqual(result["status"], "ok_synthetic")
        self.assertEqual(result["output_samples"], reference.MAX_CLIP_SAMPLES)
        self.assertEqual(result["official_padded_length"], 160_254)
        self.assertEqual(result["internal_padding_samples"], 254)
        self.assertTrue(result["length_preserved"])

    def test_max_abs_boundary(self):
        session = reference.OfflineSession(reference.synthetic_config())
        result = session.process_clip([reference.MAX_ABS_INPUT] + [0.0] * 159)
        self.assertEqual(result["status"], "ok_synthetic")
        session = reference.OfflineSession(reference.synthetic_config())
        result = session.process_clip([reference.MAX_ABS_INPUT + 1e-6] + [0.0] * 159)
        self.assertEqual(result["status"], "rejected:sample_out_of_range")

    def test_rejection_after_success_does_not_advance(self):
        session = reference.OfflineSession(reference.synthetic_config())
        first = session.process_clip([0.01] * reference.FRAME_SAMPLES)
        self.assertEqual(first["status"], "ok_synthetic")
        digest = session.state_digest()
        for bad in ([], "x", [float("nan")], [True]):
            result = session.process_clip(bad)
            self.assertTrue(result["status"].startswith("rejected:"))
            self.assertEqual(session.state_digest(), digest)


class TestSyntheticSurrogate(unittest.TestCase):
    def test_deterministic_outputs(self):
        _target, observed = reference.synth("active_speech")
        first = reference.surrogate_whole_clip(observed)
        second = reference.surrogate_whole_clip(observed)
        self.assertEqual(first, second)
        self.assertEqual(reference.output_digest(first), reference.output_digest(second))

    def test_frame_loop_matches_whole_clip(self):
        _target, observed = reference.synth("active_speech")
        self.assertEqual(
            reference.surrogate_frame_loop_control(observed),
            reference.surrogate_whole_clip(observed),
        )

    def test_split_halves_not_equivalent(self):
        _target, observed = reference.synth("active_speech")
        self.assertNotEqual(
            reference.surrogate_split_halves(observed),
            reference.surrogate_whole_clip(observed),
        )

    def test_prefix_is_not_final(self):
        _target, observed = reference.synth("active_speech")
        whole = reference.surrogate_whole_clip(observed)
        prefix = reference.surrogate_whole_clip(observed[:16_000])
        self.assertNotEqual(prefix, whole[:16_000])
        self.assertEqual(len(prefix), 16_000)

    def test_partial_tail_length_and_padding(self):
        semantics = reference.offline_semantics()
        self.assertEqual(semantics["partial_tail_input_samples"], 32_123)
        self.assertEqual(semantics["partial_tail_output_samples"], 32_123)
        self.assertEqual(semantics["partial_tail_official_padded_length"], 32_254)
        self.assertEqual(semantics["partial_tail_padding_discarded_samples"], 131)

    def test_scale_control_is_approximately_equivariant(self):
        semantics = reference.offline_semantics()
        self.assertFalse(semantics["scale_equivariance_exact"])
        self.assertTrue(semantics["scale_equivariance_approx"])
        self.assertLessEqual(semantics["scale_equivariance_rel_error"], 1e-12)

    def test_silence_is_exactly_zero(self):
        self.assertEqual(reference.surrogate_whole_clip([0.0] * 160), [0.0] * 160)
        self.assertEqual(reference.offline_semantics()["silent_clip_peak"], 0.0)

    def test_impulse_peak_preserved(self):
        semantics = reference.offline_semantics()
        self.assertTrue(semantics["impulse_peak_preserved"])
        self.assertEqual(semantics["impulse_output_peak_index"], 4_000)

    def test_outputs_finite_and_peak_bounded(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant in ("identity_passthrough", "noisy_control", "surrogate_whole_clip",
                            "surrogate_frame_loop_control", "surrogate_split_halves"):
                with self.subTest(condition=condition, variant=variant):
                    metrics = results[condition][variant]
                    self.assertEqual(metrics["nonfinite_count"], 0)
                    self.assertEqual(metrics["output_samples"], reference.SAMPLES)
                    self.assertLessEqual(metrics["peak_abs"], 1.0)

    def test_identity_is_exact_passthrough(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            self.assertTrue(results[condition]["identity_exact"])
            self.assertEqual(
                results[condition]["identity_passthrough"]["output_sha256"],
                results[condition]["noisy_control"]["output_sha256"],
            )

    def test_idle_noise_has_no_target_metrics(self):
        metrics = reference.synthetic_results()["idle_noise"]["surrogate_whole_clip"]
        self.assertIsNone(metrics["noisy_snr_db"])
        self.assertIsNone(metrics["surrogate_snr_db"])
        self.assertIsNone(metrics["delta_snr_db"])

    def test_metrics_are_finite_or_none(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant, metrics in results[condition].items():
                if not isinstance(metrics, dict):
                    continue
                for key, value in metrics.items():
                    if isinstance(value, float):
                        self.assertTrue(math.isfinite(value), f"{condition}/{variant}/{key}")


class TestSessionLifecycle(unittest.TestCase):
    def test_one_call_close_and_replay(self):
        _target, observed = reference.synth("active_speech")
        session = reference.OfflineSession(reference.synthetic_config())
        first = session.process_clip(observed)
        self.assertEqual(first["status"], "ok_synthetic")
        self.assertEqual(first["internal_padding_samples"], 254)
        self.assertTrue(first["length_preserved"])
        digest = session.state_digest()
        second = session.process_clip(observed)
        self.assertEqual(second["status"], "rejected:offline_clip_already_complete")
        self.assertEqual(session.state_digest(), digest)
        session.close()
        session.close()
        self.assertTrue(session.closed)
        after = session.process_clip(observed)
        self.assertEqual(after["status"], "rejected:session_closed")

    def test_replay_bit_identical_and_no_cross_clip_state(self):
        semantics = reference.offline_semantics()
        self.assertTrue(semantics["replay_bit_identical"])
        self.assertFalse(semantics["cross_clip_state_carried"])

    def test_state_digest_deterministic(self):
        _target, observed = reference.synth("quiet_speech")
        one = reference.OfflineSession(reference.synthetic_config())
        two = reference.OfflineSession(reference.synthetic_config())
        one.process_clip(observed)
        two.process_clip(observed)
        self.assertEqual(one.state_digest(), two.state_digest())


class TestReportDisposition(unittest.TestCase):
    def test_machine_readable_disposition(self):
        value = report()
        self.assertEqual(value["decision"], "DEFER")
        self.assertEqual(value["defer_before"], "processor_exposure")
        self.assertEqual(value["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(value["evidence_status"], "incomplete")
        self.assertEqual(value["qualification"]["status"], "not_qualified")
        self.assertFalse(value["qualification"]["qualified"])
        self.assertFalse(value["qualification"]["missing_result_may_qualify"])

    def test_exactly_eight_blocked_gates(self):
        value = report()
        gates = value["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(value["release_gate_count"], 8)
        self.assertEqual({gate["name"] for gate in gates}, EXPECTED_GATES)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])
        self.assertEqual(value["counts"]["release_gates_blocked"], 8)

    def test_no_claim_is_true(self):
        for name, claimed in report()["claims"].items():
            with self.subTest(claim=name):
                self.assertFalse(claimed)

    def test_boundary_preserved(self):
        boundary = report()["boundary"]
        for name in ("registered", "enabled_by_default", "default_selected",
                     "public_api_abi_change", "provider_registration",
                     "descriptor_registry_change", "installed_v0_behavior_change",
                     "shared_build_or_ci_change", "processor_exposure",
                     "task_board_or_handoff_write", "streaming_mode_added",
                     "adapter_json_added", "readiness_json_added"):
            self.assertFalse(boundary[name], name)
        self.assertTrue(boundary["installed_v0_geometry_preserved"])

    def test_enhancement_profile_unmeasured_fields(self):
        profile = report()["enhancement_profile"]
        self.assertEqual(profile["stoi"], "blocked_unmeasured")
        self.assertEqual(profile["content_availability_timing"], "blocked_unmeasured")
        self.assertEqual(profile["listening"], "not_run")
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["candidate_result_present"])

    def test_report_has_no_self_digest(self):
        value = report()
        self.assertNotIn("report_sha256", value)
        self.assertNotIn("artifact_pins", value)


class TestRegeneration(unittest.TestCase):
    def test_report_sha256_sidecar_and_contract_pins(self):
        value = report()
        payload = reference.canonical_report_bytes(value)
        digest = hashlib.sha256(payload).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")
        self.assertEqual((HERE / "report.json").read_bytes(), payload)

        pins = cli.contract_pins()
        self.assertNotIn("contract.json", pins)
        self.assertIn("README.md", pins)
        contract = load_strict("contract.json")
        self.assertEqual(contract["artifact_pins"], pins)
        for name, pinned in pins.items():
            self.assertEqual(reference.sha256_file(HERE / name), pinned)

    def test_manifest_pins_and_no_board_hash(self):
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines[0].startswith("#"))
        entries = [line for line in lines[1:] if line]
        paths = [line.split("  ", 1)[1] for line in entries]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("plan/swarm/TASKS.json", "\n".join(paths))
        self.assertNotIn("source:audio-benchmark-platform/plan/swarm/TASKS.json", paths)
        for line in entries:
            digest, path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            if path.startswith("source:"):
                self.assertEqual(reference.sha256_file(reference.SOURCE_ROOT / path[len("source:"):]), digest)
            elif path.startswith("worktree:"):
                self.assertEqual(reference.sha256_file(reference.SDK_ROOT / path[len("worktree:"):]), digest)

    def test_readme_digest_table_matches(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split("<!-- DIGEST_TABLE_END -->", 1)[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            self.assertIn(row, block)

    def test_three_cold_start_regenerations_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "evidence"
            shutil.copytree(
                HERE,
                copy,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            baseline = {
                name: (HERE / name).read_bytes()
                for name in reference.LOCAL_FILES
                if (HERE / name).is_file()
            }
            baseline["SOURCES.sha256"] = (HERE / "SOURCES.sha256").read_bytes()
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["SDK_ROOT"] = str(reference.SDK_ROOT)
            env["SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
            snapshots = []
            for _ in range(3):
                result = subprocess.run(
                    [sys.executable, str(copy / "run.py"), "--all"],
                    cwd=str(copy),
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                snapshot = {}
                for name in sorted(baseline):
                    snapshot[name] = (copy / name).read_bytes()
                snapshots.append(snapshot)
            self.assertEqual(snapshots[0], snapshots[1])
            self.assertEqual(snapshots[1], snapshots[2])
            self.assertEqual(snapshots[0], baseline)


class TestLicensingAndScope(unittest.TestCase):
    def test_python_spdx_headers(self):
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
            self.assertEqual(head, ["# " + SPDX_C, "# " + SPDX_L], name)

    def test_markdown_spdx_header(self):
        head = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
        self.assertEqual(head, ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"])

    def test_sidecars(self):
        for name in SIDECAR_FILES:
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), SIDECAR, name)

    def test_fail_closed_local_set(self):
        present = {
            path.relative_to(HERE).as_posix()
            for path in HERE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
        self.assertEqual(present, expected)

    def test_no_network_or_download_imports(self):
        forbidden = ("import " + "requests", "import " + "urllib", "import " + "socket",
                     "import " + "http.client", "url" + "open", "url" + "retrieve",
                     "pip " + "install")
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{name}: {token}")

    def test_no_asset_path_access_in_reference(self):
        text = (HERE / "reference.py").read_text(encoding="utf-8")
        self.assertIn("(SDK_ROOT / ASSET_PATH).is_file()", text)
        self.assertNotIn("ASSET_PATH).read", text)
        self.assertNotIn("open(ASSET_PATH", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
