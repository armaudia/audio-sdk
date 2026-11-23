# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""External consumer of the installed third-party identity fixture.

Run from a directory outside the source tree with the installed wheel first on
PYTHONPATH. The package under third_party/src is never imported. Output is
deterministic and contains no volatile paths, clocks or measurements.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPECTED_REPORT_DIGEST = "64428914ee08309ab0bb3e18eec739d59f543711f342e488673ddd6246fe21ec"
EXPECTED_FIXTURE_SOURCE_DIGEST = "53397ac16064e748a24526bc80fcbacd5d4a5fb30484ee17bb04ed30dbf4f7ee"
EXPECTED_RECIPE_DIGEST = "d9581a6ee806ec5afcae8bad1c99761ca604fcfb2770ab7b0eb9ded03dbed7c3"
EXPECTED_FALLBACK_RECIPE_DIGEST = "b7bbfb8d798e0f376b1d05cd0013b6e65ab5e7db89130e2e422d36b185649192"
EXPECTED_BASELINE_DIGEST = "9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2"
EXPECTED_COMBINED_DIGEST = "f815d34666505ecc0d85796145df3dad57a9bcef23b4a813fa0f02537bf39167"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    install_target = Path(sys.argv[1]).resolve()
    evidence = Path(sys.argv[2]).resolve()

    import pipe_control_fixture as pkg  # must come from the install target
    installed_path = Path(pkg.__file__).resolve()
    if install_target not in installed_path.parents:
        raise SystemExit("fixture_not_installed")

    sys.path.insert(0, str(evidence))
    import fixture as ref  # noqa: E402

    stages = pkg.installed_stages()
    base_digest = _digest(pkg.canonical_recipe_bytes(pkg.base_recipe()))
    fallback_digest = _digest(pkg.canonical_recipe_bytes(pkg.fallback_recipe()))
    if (base_digest != EXPECTED_RECIPE_DIGEST
            or fallback_digest != EXPECTED_FALLBACK_RECIPE_DIGEST):
        raise SystemExit("installed_recipe_identity_mismatch")
    if pkg.source_digest() != EXPECTED_FIXTURE_SOURCE_DIGEST:
        raise SystemExit("installed_source_digest_mismatch")
    if ref.source_tree_digest() != pkg.source_digest():
        raise SystemExit("installed_source_tree_mismatch")

    report = ref.build_report(stages)
    report_digest = _digest(ref.canonical_bytes(report))
    checked_in = (evidence / "report.json").read_bytes()
    if report_digest != EXPECTED_REPORT_DIGEST or report_digest != _digest(checked_in):
        raise SystemExit("report_digest_mismatch")
    baseline = report["baseline"]
    switch = report["session_switch"]
    if not baseline["bit_exact"]:
        raise SystemExit("baseline_not_bit_exact")
    if (baseline["delivered_valid_f32_digest"] != EXPECTED_BASELINE_DIGEST
            or switch["combined_delivered_f32_digest"] != EXPECTED_COMBINED_DIGEST
            or switch["old_epoch_or_duplicate_samples_accepted"] != 0
            or not switch["intervals_disjoint"]):
        raise SystemExit("session_conservation_mismatch")
    if report["qualification"] != "incomplete":
        raise SystemExit("qualification_status_mismatch")

    print(json.dumps({
        "contract": ref.CONTRACT_ID,
        "fixture_id": pkg.FIXTURE_ID,
        "installed": True,
        "fixture_source_digest": pkg.source_digest(),
        "recipe_digest": base_digest,
        "fallback_recipe_digest": fallback_digest,
        "input_f32_digest": baseline["input_f32_digest"],
        "delivered_valid_f32_digest": baseline["delivered_valid_f32_digest"],
        "combined_delivered_f32_digest": switch["combined_delivered_f32_digest"],
        "accepted_samples": baseline["counters"]["accepted_samples"],
        "delivered_valid_samples": baseline["counters"]["delivered_valid_samples"],
        "report_digest": report_digest,
        "status": report["status"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
