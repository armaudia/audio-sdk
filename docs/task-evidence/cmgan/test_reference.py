# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the task-local CMGAN package."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class IdentityTests(unittest.TestCase):
    def test_task_identity_constants(self) -> None:
        self.assertEqual(reference.TASK, "SDK-CMGAN")
        self.assertEqual(reference.COMPONENT, "cmgan")
        self.assertEqual(reference.PROFILE, "enhancement")
        self.assertEqual(reference.DECISION, "DEFER")
        self.assertEqual(reference.EVIDENCE_STATUS, "incomplete")
        self.assertEqual(reference.QUALIFICATION_STATUS, "not_qualified")
        self.assertEqual(reference.BASE_COMMIT,
                         "d45e0f22883021412b4206c77df4e1d8cf89dbd5")


class AssetTests(unittest.TestCase):
    def test_asset_reference_exact(self) -> None:
        ref = reference.asset_ref()
        self.assertEqual(ref["checkpoint_sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(ref["checkpoint_bytes"], 7_488_051)
        self.assertEqual(ref["source_revision"],
                         "39946005d9b66fa1e824edf4bb6bc9a06088e443")
        self.assertEqual(ref["checkpoint_git_blob"],
                         "cbafab9a5fe739f3662c65cfe7be009dc475e0d1")
        self.assertEqual(ref["storage"], "external")
        self.assertFalse(ref["provider_file_access"])
        self.assertFalse(ref["download_attempted"])

    def test_asset_admission_admits_exact_but_not_qualifies(self) -> None:
        result = reference.asset_admission(reference.asset_ref())
        self.assertTrue(result["admitted"])
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["errors"], [])

    def test_asset_admission_rejects_provider_storage(self) -> None:
        ref = reference.asset_ref()
        ref["storage"] = "provider"
        result = reference.asset_admission(ref)
        self.assertFalse(result["admitted"])
        self.assertIn("provider_storage", result["errors"])

    def test_asset_admission_rejects_download(self) -> None:
        ref = reference.asset_ref()
        ref["download_attempted"] = True
        ref["provider_file_access"] = True
        result = reference.asset_admission(ref)
        self.assertFalse(result["admitted"])
        self.assertIn("download_attempted", result["errors"])
        self.assertIn("provider_file_access", result["errors"])

    def test_asset_admission_rejects_wrong_sha(self) -> None:
        ref = reference.asset_ref()
        ref["checkpoint_sha256"] = "0" * 64
        result = reference.asset_admission(ref)
        self.assertFalse(result["admitted"])
        self.assertIn("wrong_checkpoint_sha", result["errors"])

    def test_asset_admission_rejects_malformed_sha(self) -> None:
        ref = reference.asset_ref()
        ref["checkpoint_sha256"] = "abc"
        result = reference.asset_admission(ref)
        self.assertFalse(result["admitted"])
        self.assertIn("malformed_checkpoint_sha", result["errors"])

    def test_asset_admission_rejects_missing_and_unknown(self) -> None:
        ref = reference.asset_ref()
        ref.pop("checkpoint_sha256")
        ref["extra"] = 1
        result = reference.asset_admission(ref)
        self.assertFalse(result["admitted"])
        self.assertIn("missing_field", result["errors"])
        self.assertIn("unknown_field", result["errors"])
        self.assertFalse(reference.asset_admission(None)["admitted"])

    def test_asset_adverse_case_set(self) -> None:
        cases = reference.asset_adverse_cases()
        self.assertEqual(len(cases), 17)
        self.assertTrue(all(case["rejected"] for case in cases.values()))
        self.assertIn("bool_checkpoint_bytes", cases)
        self.assertIn("wrong_checkpoint_git_blob", cases)

    def test_asset_admission_rejects_wrong_bytes_and_license(self) -> None:
        ref = reference.asset_ref()
        ref["checkpoint_bytes"] = 1
        ref["code_license"] = "Apache-2.0"
        result = reference.asset_admission(ref)
        self.assertFalse(result["admitted"])
        self.assertIn("wrong_checkpoint_bytes", result["errors"])
        self.assertIn("wrong_code_license", result["errors"])


class ConfigTests(unittest.TestCase):
    def test_config_default_valid(self) -> None:
        self.assertEqual(reference.validate_config(
            reference.default_config(surrogate_opt_in=True)), [])

    def test_config_requires_opt_in(self) -> None:
        errors = reference.validate_config(reference.default_config())
        self.assertIn("surrogate_without_opt_in", errors)
        with self.assertRaises(ValueError):
            reference.OfflineSurrogateSession(reference.default_config())

    def test_config_rejects_wrong_geometry_values(self) -> None:
        for field, value in (("sample_rate_hz", 8000), ("n_fft", 512),
                             ("hop_length", 160), ("cut_length_samples", 16000),
                             ("power_exponent", 0.5), ("num_features", 257)):
            config = reference.default_config(surrogate_opt_in=True)
            config[field] = value
            self.assertTrue(reference.validate_config(config))

    def test_config_adverse_case_set(self) -> None:
        cases = reference.config_adverse_cases()
        self.assertEqual(len(cases), 17)
        self.assertTrue(all(case["rejected"] for case in cases.values()))
        self.assertIn("wrong_power_exponent", cases)
        self.assertIn("mode_unsupported", cases)


class GeometryTests(unittest.TestCase):
    def test_geometry_32000(self) -> None:
        info = reference.geometry(32_000)
        self.assertEqual(info["padded_len_samples"], 32_000)
        self.assertEqual(info["wrap_padding_samples"], 0)
        self.assertEqual(info["batch_size"], 1)
        self.assertEqual(info["stft_bins"], 201)
        self.assertEqual(info["stft_frames_per_row"], 321)

    def test_geometry_32123_tail(self) -> None:
        info = reference.geometry(32_123)
        self.assertEqual(info["padded_len_samples"], 32_200)
        self.assertEqual(info["wrap_padding_samples"], 77)
        self.assertEqual(info["output_samples"], 32_123)

    def test_geometry_16s_boundary(self) -> None:
        self.assertEqual(reference.geometry(256_000)["batch_size"], 1)
        beyond = reference.geometry(256_001)
        self.assertEqual(beyond["wrap_padding_samples"], 99)
        self.assertEqual(beyond["padded_len_samples"], 256_100)
        self.assertEqual(beyond["batch_size"], 2)
        self.assertEqual(beyond["samples_per_batch_row"], 128_050)

    def test_geometry_spans_multiple_batches(self) -> None:
        info = reference.geometry(1_000_000)
        self.assertEqual(info["batch_size"], 4)
        self.assertEqual(info["samples_per_batch_row"], 250_000)
        self.assertEqual(info["stft_frames_per_row"], 2501)

    def test_geometry_length_preserving(self) -> None:
        for length in (1, 99, 100, 101, 160, 32_000, 256_001):
            info = reference.geometry(length)
            self.assertEqual(info["output_samples"], length)
            self.assertEqual(info["padded_samples_emitted"], 0)
            self.assertEqual(info["source_time_mapping"], "identity")
            self.assertEqual(info["delay_compensation_samples"], 0)
            self.assertEqual(info["padded_len_samples"] % info["batch_size"], 0)

    def test_geometry_rejects_invalid_length(self) -> None:
        for bad in (0, -1, True, 1.5, "160", reference.MAX_CLIP_SAMPLES + 1):
            with self.assertRaises(ValueError):
                reference.geometry(bad)  # type: ignore[arg-type]

    def test_normalization_scale_roundtrip(self) -> None:
        samples = [0.1, -0.2, 0.3, -0.4]
        scale = reference.normalization_scale(samples)
        energy = sum(value * value for value in samples)
        self.assertAlmostEqual(scale * scale * energy, len(samples), places=12)
        self.assertEqual(reference.normalization_scale([0.0, 0.0]), 0.0)

    def test_tail_probe(self) -> None:
        tail = reference.tail_probe()
        self.assertEqual(tail["input_samples"], 32_123)
        self.assertEqual(tail["wrap_padding_samples"], 77)
        self.assertEqual(tail["output_samples"], 32_123)
        self.assertTrue(tail["output_length_equals_input"])


class SurrogateTests(unittest.TestCase):
    def test_synth_conditions_finite_and_bounded(self) -> None:
        for condition in reference.CONDITIONS:
            clean, observed = reference.synth(condition)
            self.assertEqual(len(clean), reference.SAMPLES)
            self.assertEqual(len(observed), reference.SAMPLES)
            self.assertTrue(all(math.isfinite(value) for value in observed))
            self.assertLessEqual(max(abs(value) for value in observed), 1.0)
            if condition == "idle_noise":
                self.assertTrue(all(value == 0.0 for value in clean))

    def test_identity_control_exact(self) -> None:
        _, observed = reference.synth("active_speech")
        identity = reference.identity_passthrough(observed)
        self.assertEqual(identity, list(observed))
        self.assertIsNot(identity, observed)

    def test_surrogate_deterministic(self) -> None:
        _, observed = reference.synth("active_speech")
        first, first_state = reference.enhance_offline(observed)
        second, second_state = reference.enhance_offline(observed)
        self.assertEqual(first, second)
        self.assertEqual(first_state, second_state)

    def test_surrogate_length_and_finite(self) -> None:
        _, observed = reference.synth("low_snr_speech")
        output, _ = reference.enhance_offline(observed)
        self.assertEqual(len(output), len(observed))
        self.assertTrue(all(math.isfinite(value) for value in output))
        self.assertLessEqual(max(abs(value) for value in output), 1.0)

    def test_surrogate_chunk_invariance(self) -> None:
        _, observed = reference.synth("active_speech")
        whole = reference.run_offline(observed, len(observed))["output"]
        for chunk in (7, 160, 1280):
            self.assertEqual(reference.run_offline(observed, chunk)["output"], whole)

    def test_state_chain_independent(self) -> None:
        state = reference.state_evidence()
        self.assertTrue(state["identical_state_chain"])
        self.assertEqual(len(state["state_steps"]), 3)

    def test_reset_restores_state(self) -> None:
        self.assertTrue(reference.state_evidence()["reset_restores_initial_state"])

    def test_session_lifecycle_rejections(self) -> None:
        lifecycle = reference.lifecycle_evidence()
        for key in ("finish_twice_rejected", "feed_after_finish_rejected",
                    "reset_after_finish_allowed", "close_idempotent",
                    "feed_after_close_rejected"):
            self.assertTrue(lifecycle[key], key)

    def test_session_rejects_adverse_chunks(self) -> None:
        cases = reference.frame_adverse_cases()
        self.assertEqual(len(cases), 6)
        for name, case in cases.items():
            self.assertTrue(case["rejected"], name)
            self.assertTrue(case["state_unchanged"], name)

    def test_empty_clip(self) -> None:
        session = reference.OfflineSurrogateSession()
        self.assertEqual(session.finish(), [])
        lifecycle = reference.lifecycle_evidence()
        self.assertEqual(lifecycle["empty_clip_output_samples"], 0)


class MetricTests(unittest.TestCase):
    def test_metrics_identity_matches_noisy(self) -> None:
        for condition in reference.CONDITIONS:
            block = reference.condition_block(condition)
            self.assertTrue(block["identity_matches_noisy_control"])
            self.assertTrue(block["identity_exact"])

    def test_idle_noise_has_no_snr(self) -> None:
        block = reference.condition_block("idle_noise")
        self.assertIsNone(block["noisy_control"]["snr_db"])
        self.assertIsNone(block["noisy_control"]["si_sdr_db"])
        self.assertIsNotNone(block["rms_change_db"])

    def test_regressions_recomputed(self) -> None:
        blocks = reference._condition_blocks()
        regressions = reference._regressions(blocks)
        self.assertEqual(regressions, reference._regressions(blocks))
        for regression in regressions:
            self.assertLess(regression["delta"], 0.0)


class ReportTests(unittest.TestCase):
    def test_report_disposition(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], reference.STATUS)
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualifying_results"], 0)
        self.assertFalse(report["synthetic_surrogate"]["qualifies"])
        self.assertTrue(report["synthetic_surrogate"]["not_cmgan"])

    def test_report_gates_and_blockers(self) -> None:
        report = reference.build_report()
        gates = {item["gate"]: item["status"] for item in report["gates"]}
        self.assertEqual(gates["exact_asset_identity"], "clear")
        self.assertEqual(sum(1 for value in gates.values() if value == "blocked"), 8)
        self.assertEqual(report["open_exact_blockers"], 4)
        self.assertTrue(report["exact_blockers"][0].startswith("PRIMARY:"))
        self.assertEqual(report["counts"]["caller_chunks_total"], 37_699)

    def test_report_canonical_and_no_negative_zero(self) -> None:
        payload = reference.canonical_report_bytes(reference.build_report())
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(payload, reference.canonical_report_bytes(
            reference.build_report()))
        self.assertIsNone(re.search(rb"-0\.0(?=[,}\]])", payload))
        json.loads(payload.decode("utf-8"))
        self.assertEqual(len(hashlib.sha256(payload).hexdigest()), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
