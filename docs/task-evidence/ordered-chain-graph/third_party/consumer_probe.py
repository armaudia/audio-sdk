"""External consumer of the installed third-party fixture wheel.

Run from a directory outside the source tree with the installed wheel first on
PYTHONPATH. The only imports are the installed fixture package and the reference
executor supplied by the task's evidence directory. No source third_party/src
path is used. Output is deterministic and contains no volatile paths.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPECTED_REPORT_DIGEST = "a496d36fdfaae4796ab620065d424e0c03c4738da47875f2b26b84b3c4c013aa"
FIXED_ORIGIN_NS = 1_000_000_000


def _frame(ref, epoch, first_sample, values, valid_count, flags=0):
    samples = list(values[:valid_count]) + [0.0] * (160 - valid_count)
    return ref.Frame(tuple(samples), valid_count, epoch, first_sample, flags)


def main() -> int:
    install_target = Path(sys.argv[1]).resolve()
    evidence = Path(sys.argv[2]).resolve()

    import ordered_chain_fixture as fixture_package  # must come from install target
    installed_path = Path(fixture_package.__file__).resolve()
    if install_target not in installed_path.parents:
        raise SystemExit("fixture_not_installed")

    sys.path.insert(0, str(evidence))
    import fixture as ref  # noqa: E402

    stages = dict(fixture_package.installed_stages())
    stages["fixture.delay.v0"] = ref.DelayStage()
    raw = fixture_package.recipe()
    recipe, status, reason = ref.validate_recipe(raw, stages)
    if status is not ref.Status.OK or recipe is None:
        raise SystemExit(f"recipe_rejected:{status.value}:{reason}")
    if hashlib.sha256(fixture_package.canonical_recipe_bytes()).hexdigest() != recipe.digest:
        raise SystemExit("recipe_identity_mismatch")

    executor = ref.SequentialExecutor(recipe, stages, stream_origin_ns=FIXED_ORIGIN_NS)
    first = tuple((i % 11) / 11 for i in range(160))
    second = tuple(((i + 3) % 13) / 13 for i in range(160))
    final_values = (0.5, -0.25, 0.75, 0.0, 1.0)

    first_result = executor.process(_frame(ref, 1, 0, first, 160))
    if first_result.lease is None:
        raise SystemExit("first_frame_rejected")
    lease = first_result.lease
    if (lease.stage_order != ("gain", "delay", "limiter")
            or lease.source_first_sample != -80
            or (lease.valid_offset, lease.valid_count) != (80, 80)
            or lease.availability_ns != FIXED_ORIGIN_NS + 675000):
        raise SystemExit("first_frame_mapping_mismatch")
    if executor.release(lease.lease_id) is not ref.Status.OK:
        raise SystemExit("release_failed")

    second_result = executor.process(_frame(ref, 1, 160, second, 160))
    if second_result.lease is None:
        raise SystemExit("second_frame_rejected")
    lease = second_result.lease
    if (lease.source_first_sample != 80
            or (lease.valid_offset, lease.valid_count) != (0, 160)
            or lease.availability_ns != FIXED_ORIGIN_NS + 10_000_000 + 675000):
        raise SystemExit("second_frame_mapping_mismatch")
    if executor.release(lease.lease_id) is not ref.Status.OK:
        raise SystemExit("release_failed")

    final_result = executor.process(_frame(ref, 1, 320, final_values, 5, ref.FINAL_INPUT))
    if final_result.lease is None:
        raise SystemExit("final_frame_rejected")
    lease = final_result.lease
    if (lease.source_first_sample != 240
            or (lease.valid_offset, lease.valid_count) != (0, 85)
            or lease.availability_ns != FIXED_ORIGIN_NS + 20_000_000 + 675000):
        raise SystemExit("final_frame_mapping_mismatch")
    if executor.release(lease.lease_id) is not ref.Status.OK:
        raise SystemExit("release_failed")

    if executor.begin_drain() is not ref.Status.OK:
        raise SystemExit("begin_drain_failed")
    drain = executor.drain_next()
    if drain.status is not ref.Status.END_OF_STREAM:
        raise SystemExit("drain_not_complete")

    known = [event for event in executor.events if event.status == ref.Status.OK.value]
    if (len(known) != 2 or known[0].validity != "known" or known[0].value != 0.75
            or known[1].validity != "unknown" or known[1].value is not None
            or executor.hold_last["pcm.gain.out"] != 0.75):
        raise SystemExit("side_output_mismatch")

    _, report_digest = ref.canonical_report(recipe, executor, ref.Status.END_OF_STREAM)
    if report_digest != EXPECTED_REPORT_DIGEST:
        raise SystemExit("report_digest_mismatch")
    if executor.valid_intervals != [(0, 80), (80, 240), (240, 325)]:
        raise SystemExit("interval_conservation_mismatch")

    print(json.dumps({
        "contract": ref.CONTRACT_ID,
        "fixture_id": fixture_package.FIXTURE_ID,
        "installed": True,
        "fixture_source_digest": fixture_package.source_digest(),
        "recipe_digest": recipe.digest,
        "report_digest": report_digest,
        "status": "end_of_stream",
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
