# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the SDK-v0 tool replay fixture.

    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_fixture.py

No skips, no network, no device and no generated binaries.  Every case uses
frozen bytes, caller-owned buffers and the pinned interpreter.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

import fixture as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PYTHON = sys.executable
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
ADAPTER = HERE / "adapter.json"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def strict_json(data: bytes | str) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError("nonfinite JSON constant " + value)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key " + key)
            result[key] = value
        return result

    payload = json.loads(data, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(payload, dict):
        raise ValueError("JSON root is not an object")
    return payload


def run_cli(*args: str) -> subprocess.CompletedProcess[bytes]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([PYTHON, str(HERE / "run.py"), *args],
                          capture_output=True, env=env, check=False)


class PinTests(unittest.TestCase):
    def test_01_source_and_header_pins_match_committed_bytes(self) -> None:
        for pin in fx.SOURCE_PINS:
            with self.subTest(path=pin["path"]):
                path = SOURCE_ROOT / pin["path"]
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 pin["sha256"])

    def test_02_toolchain_pin_matches_installed_libfuzzer_runtime(self) -> None:
        path = Path("/") / fx.TOOLCHAIN_PIN["path"]
        self.assertTrue(path.is_file())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         fx.TOOLCHAIN_PIN["sha256"])

    def test_03_artifact_pins_match_task_files(self) -> None:
        for pin in fx.artifact_pins():
            with self.subTest(path=pin["path"]):
                path = HERE / pin["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 pin["sha256"])

    def test_04_sha256_manifest_is_complete_and_correct(self) -> None:
        lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        expected = {
            f"source:{pin['path']}": pin["sha256"] for pin in fx.SOURCE_PINS
        }
        expected[f"toolchain:{fx.TOOLCHAIN_PIN['path']}"] = fx.TOOLCHAIN_PIN["sha256"]
        for pin in fx.artifact_pins():
            expected[f"docs/task-evidence/{fx.SLUG}/{pin['path']}"] = pin["sha256"]
        # SOURCES.sha256 cannot contain its own digest; every other local file
        # is pinned here.
        for name in ("README.md", "report.json", "report.json.sha256"):
            path = HERE / name
            expected[f"docs/task-evidence/{fx.SLUG}/{name}"] = (
                hashlib.sha256(path.read_bytes()).hexdigest())
        manifest: dict[str, str] = {}
        for line in lines:
            digest, raw_path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            manifest[raw_path] = digest
        self.assertEqual(set(manifest), set(expected))
        for path, digest in expected.items():
            with self.subTest(path=path):
                self.assertEqual(manifest[path], digest)

    def test_05_spdx_headers_present_in_new_python_and_readme(self) -> None:
        for name in ("fixture.py", "run.py", "test_fixture.py", "verify.py"):
            with self.subTest(path=name):
                head = "\n".join((HERE / name).read_text().splitlines()[:4])
                self.assertIn(SPDX_LICENSE, head)
                self.assertIn(SPDX_COPYRIGHT, head)
        self.assertIn(SPDX_LICENSE, (HERE / "README.md").read_text()[:400])
        reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
        self.assertIn('"docs/**"', reuse)
        self.assertIn('SPDX-License-Identifier = "Apache-2.0"', reuse)


class GeneratorTests(unittest.TestCase):
    def test_06_seeded_bytes_are_repeatable_and_finite(self) -> None:
        first = fx.fuzz_bytes(fx.SEED, "stream_sequence", 512)
        self.assertEqual(first, fx.fuzz_bytes(fx.SEED, "stream_sequence", 512))
        self.assertNotEqual(first, fx.fuzz_bytes(fx.SEED + 1,
                                                 "stream_sequence", 512))
        self.assertEqual(len(first), 512)

    def test_07_labels_domain_separate_the_two_scenarios(self) -> None:
        self.assertNotEqual(fx.fuzz_bytes(fx.SEED, "stream_sequence", 128),
                            fx.fuzz_bytes(fx.SEED, "malformed_output", 128))

    def test_08_splitmix64_state_is_version_stable(self) -> None:
        seed = fx.derive_seed(fx.SEED, "unit")
        self.assertEqual(seed, 11090943324954409154)
        state, value = fx.splitmix64_next(seed)
        self.assertEqual((state, value),
                         (4044914070568056023, 10585432016878760332))
        self.assertEqual(fx.fuzz_bytes(1, "one", 8).hex(),
                         "dc1696535f6f465f")

    def test_09_caller_samples_are_finite_and_bounded(self) -> None:
        samples = fx.caller_samples(fx.fuzz_bytes(fx.SEED, "samples", 64), 0)
        self.assertEqual(len(samples), fx.FRAME_SAMPLES)
        self.assertTrue(all(math.isfinite(value) and abs(value) <= 1.0
                            for value in samples))


class BoundaryTests(unittest.TestCase):
    def test_10_public_geometry_and_statuses_are_exact(self) -> None:
        self.assertEqual((fx.SAMPLE_RATE_HZ, fx.CHANNELS, fx.FRAME_SAMPLES),
                         (16000, 1, 160))
        self.assertEqual((fx.ABI_MAJOR, fx.ABI_MINOR), (0, 1))
        self.assertEqual([fx.STATUS[name] for name in (
            "AS_OK", "AS_INVALID_ARGUMENT", "AS_UNSUPPORTED",
            "AS_RESOURCE_EXHAUSTED", "AS_BACKEND_FAILURE", "AS_NEEDS_RESET",
            "AS_NOT_READY", "AS_END_OF_STREAM", "AS_BUSY", "AS_CLOSED",
            "AS_DUPLICATE")], list(range(11)))

    def test_11_valid_inline_frame_accepted_with_exact_mapping(self) -> None:
        data = fx.fuzz_bytes(fx.SEED, "inline_ok", 64)
        frame, output, session = fx.build_output_case(
            fx.OutputCase("ok"), data, 0, epoch=4, next_input=320)
        record = session.process(frame, output)
        self.assertEqual(record["status"], "AS_OK")
        self.assertEqual(record["expected_write"], "full_160")
        self.assertEqual(record["result"]["produced_count"], 160)
        self.assertEqual(record["result"]["source_first_sample"], 320)
        self.assertEqual(record["result"]["epoch"], 4)
        self.assertEqual(output.samples[:160], frame.input[:160])
        self.assertEqual(output.samples[160:], [fx.SENTINEL] * len(
            output.samples[160:]))

    def test_12_final_partial_frame_sets_final_padding_flag(self) -> None:
        data = fx.fuzz_bytes(fx.SEED, "inline_partial", 64)
        frame, output, session = fx.build_output_case(
            fx.OutputCase("partial", input_valid_count=37,
                          flags=fx.FLAG_FINAL_INPUT), data, 0)
        record = session.process(frame, output)
        self.assertEqual(record["status"], "AS_OK")
        self.assertEqual(record["result"]["valid_count"], 37)
        self.assertEqual(record["result"]["flags"], fx.FLAG_FINAL_PADDING)
        self.assertTrue(session.final_accepted)

    def test_13_nonfinal_partial_is_rejected_without_state_change(self) -> None:
        data = fx.fuzz_bytes(fx.SEED, "inline_partial_bad", 64)
        frame, output, session = fx.build_output_case(
            fx.OutputCase("bad", input_valid_count=159), data, 0)
        record = session.process(frame, output)
        self.assertEqual(record["status"], "AS_INVALID_ARGUMENT")
        self.assertEqual(record["rule"], "R03")
        self.assertEqual(output.samples[:160], [0.0] * 160)
        self.assertTrue(record["state_unchanged_on_reject"])

    def test_14_invalid_output_never_writes_speculatively(self) -> None:
        for case in (fx.OutputCase("null", output_null=True),
                     fx.OutputCase("short", capacity=159),
                     fx.OutputCase("alias", overlap="exact_alias")):
            with self.subTest(case=case.name):
                data = fx.fuzz_bytes(fx.SEED, "no_write_" + case.name, 64)
                frame, output, session = fx.build_output_case(case, data, 0)
                before = list(output.samples)
                record = session.process(frame, output)
                self.assertEqual(record["status"], "AS_INVALID_ARGUMENT")
                self.assertEqual(record["rule"], "R06")
                self.assertEqual(record["actual_write"], "none")
                self.assertEqual(output.samples, before)

    def test_15_nonfinite_input_and_bad_padding_are_rejected(self) -> None:
        for case, rule in ((fx.OutputCase("nan", finite_ok=False), "R04"),
                           (fx.OutputCase("pad", input_valid_count=100,
                                          flags=fx.FLAG_FINAL_INPUT,
                                          padding_ok=False), "R05")):
            with self.subTest(rule=rule):
                data = fx.fuzz_bytes(fx.SEED, "invalid_" + rule, 64)
                frame, output, session = fx.build_output_case(case, data, 0)
                record = session.process(frame, output)
                self.assertEqual(record["status"], "AS_INVALID_ARGUMENT")
                self.assertEqual(record["rule"], rule)
                self.assertEqual(record["actual_write"], "zero_prefix")

    def test_16_backend_failure_enters_needs_reset_and_recovers(self) -> None:
        case = fx.OutputCase("backend", backend_mode="bad_count")
        data = fx.fuzz_bytes(fx.SEED, "backend", 64)
        frame, output, session = fx.build_output_case(case, data, 0)
        first = session.process(frame, output)
        self.assertEqual(first["status"], "AS_BACKEND_FAILURE")
        self.assertEqual(session.state, "needs_reset")
        second = session.process(frame, output)
        self.assertEqual(second["status"], "AS_NEEDS_RESET")
        self.assertEqual(session.drain(), "AS_NEEDS_RESET")
        self.assertEqual(session.reset(2, 0), "AS_OK")
        self.assertEqual(session.epoch, 2)
        self.assertEqual(session.next_input, 0)

    def test_17_lifecycle_and_epoch_are_enforced(self) -> None:
        data = fx.fuzz_bytes(fx.SEED, "lifecycle", 64)
        frame, output, session = fx.build_output_case(
            fx.OutputCase("old", epoch_ok=False), data, 0)
        self.assertEqual(session.process(frame, output)["rule"], "R08")
        session.state = "draining"
        self.assertEqual(session.process(frame, output)["status"],
                         "AS_INVALID_ARGUMENT")
        self.assertEqual(session.drain(), "AS_END_OF_STREAM")
        self.assertEqual(session.close(), "AS_OK")
        self.assertEqual(session.process(frame, output)["status"], "AS_CLOSED")


class StreamSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stream = fx.replay_stream()

    def test_18_all_fixed_and_generated_streams_pass(self) -> None:
        self.assertTrue(self.stream["all_replays_pass"])
        for label, replay in self.stream["fixed_corpus"].items():
            with self.subTest(label=label):
                self.assertTrue(replay["all_invariants_pass"])
                self.assertTrue(all(replay["invariants"].values()))

    def test_19_queue_bound_fifo_and_eos(self) -> None:
        for replay in self.stream["fixed_corpus"].values():
            self.assertLessEqual(max(r["queue_depth"] for r in replay["trace"]),
                                 fx.BUFFERED_QUEUE_CAPACITY)
            for final in replay["finalization"].values():
                observations = final["observations"]
                self.assertEqual(observations, sorted(set(observations)))
                self.assertTrue(final["drain_statuses"][-1] in
                                ("AS_END_OF_STREAM", "AS_CLOSED"))
                self.assertEqual(final["queue_depth"], 0)

    def test_20_sessions_are_uncoupled(self) -> None:
        for replay in self.stream["generated_seeds"].values():
            self.assertTrue(all(record["other_session_unchanged"]
                                for record in replay["trace"]))

    def test_21_rejections_never_advance_stream_state(self) -> None:
        for replay in self.stream["generated_seeds"].values():
            for record in replay["trace"]:
                if record["actual"].startswith("AS_") and record["actual"] != "AS_OK":
                    self.assertEqual(record["expected"], record["actual"])
                    self.assertEqual(record["state_before"],
                                     record["state_after"])

    def test_22_missing_optional_selection_is_rejected(self) -> None:
        session = fx.SdkBufferedSession(epoch=1)
        self.assertEqual(session.stats("unregistered.tool.v0")[0],
                         "AS_UNSUPPORTED")
        status, payload = session.stats()
        self.assertEqual(status, "AS_OK")
        self.assertEqual(strict_json(payload)["schema"], "audio-sdk/stats/0.1")

    def test_23_repeated_close_is_idempotent_and_later_calls_fail(self) -> None:
        session = fx.SdkBufferedSession()
        self.assertEqual(session.close(), "AS_OK")
        self.assertEqual(session.close(), "AS_OK")
        self.assertEqual(session.submit(fx.Frame(input=[0.0] * 160)).status,
                         "AS_CLOSED")
        self.assertEqual(session.pull().status, "AS_CLOSED")
        self.assertEqual(session.begin_drain(), "AS_CLOSED")


class MalformedOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.malformed = fx.replay_malformed_output()

    def test_24_every_explicit_case_matches_the_oracle(self) -> None:
        self.assertEqual(self.malformed["failing_explicit_cases"], [])
        for record in self.malformed["explicit_corpus"]:
            with self.subTest(case=record["name"]):
                self.assertTrue(record["oracle_ok"])
                self.assertEqual(record["status"], record["expected_status"])
                self.assertTrue(record["input_unchanged"])
                self.assertTrue(record["payload_beyond_produced_unchanged"])
                self.assertTrue(record["state_unchanged_on_reject"])

    def test_25_accept_and_reject_paths_are_both_covered(self) -> None:
        counts = self.malformed["explicit_summary"]["status_counts"]
        self.assertGreaterEqual(counts.get("AS_OK", 0), 2)
        self.assertGreaterEqual(counts.get("AS_INVALID_ARGUMENT", 0), 15)
        self.assertGreaterEqual(counts.get("AS_BACKEND_FAILURE", 0), 3)

    def test_26_every_rule_is_exercised(self) -> None:
        inline_rules = set(self.malformed["explicit_summary"]["rule_counts"])
        stream_rules: set[str] = set()
        for replay in fx.replay_stream()["fixed_corpus"].values():
            stream_rules |= set(replay["rule_counts"])
        # R10 is a cross-cutting invariant rather than a single rejection path.
        r10_records = [record for record in self.malformed["explicit_corpus"]
                       if record["expected_status"] == "AS_INVALID_ARGUMENT"]
        self.assertTrue(r10_records)
        r10_covered = all(
            record["state_unchanged_on_reject"]
            and record["input_unchanged"]
            and record["payload_beyond_produced_unchanged"]
            for record in r10_records)
        covered = inline_rules | stream_rules | ({"R10"} if r10_covered else set())
        self.assertTrue(set(fx.RULES) <= covered,
                        f"missing rules: {set(fx.RULES) - covered}")
        self.assertTrue(set("R01 R02 R03 R04 R05 R06 R07 R08 R09 R11".split())
                        <= inline_rules)
        self.assertTrue(set("R12 R13 R14 R15".split()) <= stream_rules)

    def test_27_generated_cohorts_pass_and_mix_statuses(self) -> None:
        for seed, summary in self.malformed["generated_seeds"].items():
            with self.subTest(seed=seed):
                self.assertTrue(summary["all_oracle_checks_pass"])
                self.assertGreater(summary["accepted"], 0)
                self.assertGreater(summary["rejected"], 0)


class ReportAndCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT.read_bytes())
        cls.adapter = strict_json(ADAPTER.read_bytes())
        cls.expected_bytes = fx.canonical_report_bytes()

    def test_28_report_is_strict_finite_and_byte_reproducible(self) -> None:
        self.assertEqual(REPORT.read_bytes(), self.expected_bytes)
        def walk(value: Any) -> None:
            if isinstance(value, float):
                self.assertTrue(math.isfinite(value))
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(self.report)

    def test_29_report_shape_profile_and_status(self) -> None:
        report = self.report
        self.assertEqual(report["profile"], "Tool")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertEqual(report["base_commit"], fx.BASE_COMMIT)
        self.assertTrue(report["boundary"]["no_missing_result_qualifies_candidate"]
                        if "no_missing_result_qualifies_candidate" in
                        report["boundary"] else True)
        self.assertFalse(report["boundary"]["registered"])
        self.assertFalse(report["boundary"]["enabled_by_default"])
        self.assertEqual(report["boundary"]["descriptor_settings"], {})
        self.assertEqual(report["boundary"]["compiled_sdk_calls"], 0)

    def test_30_gates_and_evidence_classes_are_explicit(self) -> None:
        gates = {gate["id"]: gate for gate in self.report["gates"]}
        for name in ("clean_checkout_and_pins", "one_typical_api_use",
                     "caller_owned_inputs", "malformed_input_oracle",
                     "missing_optional_selection", "stream_sequence_replay",
                     "deterministic_reproduction"):
            self.assertEqual(gates[name]["status"], "pass", name)
        for name in ("sdk_libfuzzer_target", "native_sdk_linked_replay",
                     "measured_workload_support", "provider_intake"):
            self.assertEqual(gates[name]["status"], "blocked", name)
            self.assertTrue(gates[name]["reopen"])
        evidence = self.report["evidence_classes"]
        self.assertEqual(evidence["compile_build"]["status"], "probe_only")
        self.assertEqual(evidence["synthetic_runtime"]["status"], "pass")
        self.assertEqual(evidence["measured_workload_support"]["status"],
                         "blocked")
        self.assertTrue(all(not item["qualifying"]
                            for item in evidence.values()))

    def test_31_libfuzzer_provenance_is_recorded(self) -> None:
        tool = self.report["toolchain"]["libfuzzer"]
        self.assertEqual(tool["sdk_target_status"], "blocked")
        self.assertEqual(tool["authoritative_evidence"],
                         "deterministic_python_replay")
        self.assertIn("-runs=10000", tool["future_sdk_target_invocation"])
        probes = {probe["compiler_path"]: probe
                  for probe in tool["probe_invocations"]}
        self.assertEqual(probes["/usr/bin/clang++"]["result"], "link_failed")
        self.assertIn("libclang_rt.fuzzer_osx.a' not found",
                      probes["/usr/bin/clang++"]["stderr_excerpt"])
        self.assertEqual(probes["/opt/homebrew/opt/llvm/bin/clang++"]["result"],
                         "compiled_and_ran")

    def test_32_report_sha256_file_matches_report(self) -> None:
        lines = [line for line in REPORT_SHA.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        self.assertEqual(len(lines), 1)
        digest, name = lines[0].split()
        self.assertEqual(name, "report.json")
        self.assertEqual(digest, hashlib.sha256(REPORT.read_bytes()).hexdigest())

    def test_33_cli_report_is_byte_identical_and_inspect_is_stable(self) -> None:
        report_run = run_cli("--report")
        self.assertEqual(report_run.returncode, 0, report_run.stderr)
        self.assertEqual(report_run.stdout, REPORT.read_bytes())
        inspect_run = run_cli("--inspect")
        self.assertEqual(inspect_run.returncode, 0, inspect_run.stderr)
        self.assertEqual(inspect_run.stdout,
                         fx.canonical_bytes(fx.inspect()) + b"\n")
        self.assertEqual(strict_json(inspect_run.stdout), self.adapter)

    def test_34_typical_cli_scenario_and_caller_bytes(self) -> None:
        typical = run_cli("--scenario", "stream_sequence", "--seed",
                          str(fx.SEED))
        self.assertEqual(typical.returncode, 0, typical.stderr)
        payload = strict_json(typical.stdout)
        self.assertTrue(payload["all_invariants_pass"])
        self.assertEqual(payload["scenario"], "stream_sequence")
        caller = run_cli("--scenario", "stream_sequence", "--bytes", "8101414101022242")
        self.assertEqual(caller.returncode, 0, caller.stderr)
        caller_payload = strict_json(caller.stdout)
        self.assertEqual(caller_payload["input_hex"], "8101414101022242")
        self.assertEqual(len(caller_payload["invariants"]), 6)

    def test_35_cli_rejects_invalid_requests(self) -> None:
        bad_hex = run_cli("--scenario", "malformed_output", "--bytes", "zz")
        self.assertEqual(bad_hex.returncode, 2)
        self.assertIn(b"request_error", bad_hex.stderr)
        both = run_cli("--report", "--inspect")
        self.assertNotEqual(both.returncode, 0)


if __name__ == "__main__":
    unittest.main()
