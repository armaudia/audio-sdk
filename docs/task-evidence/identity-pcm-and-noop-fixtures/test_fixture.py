# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the identity PCM fixture and its source pins."""

from __future__ import annotations

import hashlib
import math
import os
import struct
import unittest
from pathlib import Path

from fixture import (
    BASE_COMMIT,
    FRAME_LENGTHS,
    FRAME_SAMPLES,
    SAMPLE_RATE_HZ,
    SOURCE_PINS,
    accepted_samples,
    canonical_fixture,
    canonical_json,
    digest,
    pcm_bytes,
    payload,
    sample,
)


class IdentityPcmFixtureTest(unittest.TestCase):
    def test_fixed_format_and_lengths(self) -> None:
        self.assertEqual(SAMPLE_RATE_HZ, 16000)
        self.assertEqual(FRAME_SAMPLES, 160)
        self.assertEqual(FRAME_LENGTHS, (160, 160, 37))
        self.assertEqual(len(accepted_samples()), 357)

    def test_samples_are_exact_binary_fractions(self) -> None:
        values = accepted_samples()
        self.assertTrue(all(math.isfinite(value) for value in values))
        for value in values:
            scaled = value * 128
            self.assertTrue(scaled.is_integer())
            self.assertEqual(struct.unpack("<f", struct.pack("<f", value))[0],
                             value)

    def test_generator_is_repeatable_and_frame_aware(self) -> None:
        self.assertEqual(sample(0, 0), -50 / 128)
        self.assertEqual(sample(0, 1), -13 / 128)
        self.assertEqual(sample(1, 0), -33 / 128)
        self.assertEqual(accepted_samples(), accepted_samples())

    def test_canonical_fixture_digest_is_stable(self) -> None:
        first_text, first_digest = canonical_fixture()
        second_text, second_digest = canonical_fixture()
        self.assertEqual(first_text, second_text)
        self.assertEqual(first_digest, second_digest)
        self.assertRegex(first_digest, r"^[0-9a-f]{64}$")
        self.assertIn(BASE_COMMIT, first_text)
        self.assertEqual(canonical_json(payload()), first_text)

    def test_source_pin_constants_are_well_formed(self) -> None:
        self.assertEqual(len(SOURCE_PINS), 2)
        for path, value in SOURCE_PINS.items():
            self.assertTrue(path)
            self.assertRegex(value, r"^[0-9a-f]{64}$")

    def test_pinned_source_bytes_when_paths_are_supplied(self) -> None:
        candidates = {
            "cpp-library/src/stages/identity.cpp": os.environ.get("IDENTITY_CPP"),
            "adapters/controls/adapter.json": os.environ.get("ADAPTER_JSON"),
        }
        if any(path is None for path in candidates.values()):
            self.skipTest("source paths not supplied (IDENTITY_CPP, ADAPTER_JSON)")
        for name, supplied in candidates.items():
            data = Path(supplied).read_bytes()  # type: ignore[arg-type]
            self.assertEqual(hashlib.sha256(data).hexdigest(), SOURCE_PINS[name])

    def test_pcm_bytes_length_matches_accepted_samples(self) -> None:
        self.assertEqual(len(pcm_bytes(accepted_samples())), 357 * 4)


if __name__ == "__main__":
    unittest.main()
