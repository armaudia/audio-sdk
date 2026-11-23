"""External consumer of the installed third-party fixture wheel.

Run from a directory outside the source tree with the installed wheel first on
PYTHONPATH. The only third-party imports are from the installed package; the
reference scheduler comes from the task's evidence directory. No source
third_party/src path is used. Output is deterministic and contains no paths.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED_REPORT_DIGEST = "5bee590bd662aa09517ae9e6302e410ee6e55745894fcd2dacdf33fa19d4d724"
EXPECTED_DOMAIN_DIGEST = "190dbf721bd18295ec835a34a463cff4232dc1db209e848de320c8aa1518b9ef"
EXPECTED_GRAPH_DIGEST = "91604256df7f75b72a20c3633a9cf775117a1882ab74be72fb895e6009db9f5f"


def _frame(ref, epoch, first_sample, values, valid_count, flags=0):
    samples = list(values[:valid_count]) + [0.0] * (ref.FRAME_SAMPLES - valid_count)
    return ref.Frame(tuple(samples), valid_count, epoch, first_sample, flags)


def main() -> int:
    install_target = Path(sys.argv[1]).resolve()
    evidence = Path(sys.argv[2]).resolve()

    import engine_v1_fixture as fixture_package  # must come from install target
    installed_path = Path(fixture_package.__file__).resolve()
    if install_target not in installed_path.parents:
        raise SystemExit("fixture_not_installed")

    sys.path.insert(0, str(evidence))
    import fixture as ref  # noqa: E402

    config = json.loads((evidence / "domain.json").read_text(encoding="ascii"))
    raw_graph = json.loads((evidence / "graph.json").read_text(encoding="ascii"))
    factories = ref.builtin_provider_factories()
    factories.update(fixture_package.installed_provider_factories())
    expected_ids = set(fixture_package.installed_provider_ids())
    if not expected_ids.issubset(set(factories)):
        raise SystemExit("installed_factories_missing")

    domain = ref.Domain(config, factories)
    stream, status, reason, _ = domain.admit(
        raw_graph, {"epoch": 1, "first_input_sample": 0, "assets": []})
    if status is not ref.Status.OK or stream is None:
        raise SystemExit(f"admission_rejected:{status.value}:{reason}")
    if domain.config.digest != EXPECTED_DOMAIN_DIGEST or stream.graph.digest != EXPECTED_GRAPH_DIGEST:
        raise SystemExit("identity_mismatch")

    inputs = (
        (0, tuple((i % 11) / 11 for i in range(160)), 160, 0),
        (160, tuple(((i + 3) % 13) / 13 for i in range(160)), 160, 0),
        (320, (0.5, -0.25, 0.75, 0.0, 1.0), 5, ref.FINAL_INPUT),
    )
    expected_mapping = ((-80, 80, 80), (80, 0, 160), (240, 0, 85))
    for index, (first, values, count, flags) in enumerate(inputs):
        capture = domain.clock.origin_ns + (index + 1) * ref.NS_PER_FRAME
        accepted = stream.enqueue(
            _frame(ref, 1, first, values, count, flags), capture, capture + 60_000_000)
        if accepted.status is not ref.Status.OK:
            raise SystemExit(f"enqueue_rejected:{accepted.reason}")
        if domain.scheduler.step() is not ref.Status.OK:
            raise SystemExit("scheduler_step_failed")
        pulled = stream.pull()
        if pulled.status is not ref.Status.OK or pulled.lease is None:
            raise SystemExit("pull_failed")
        lease = pulled.lease
        mapping = (lease.source_first_sample, lease.valid_offset, lease.valid_count)
        if mapping != expected_mapping[index]:
            raise SystemExit("frame_mapping_mismatch")
        if stream.release(lease.lease_id) is not ref.Status.OK:
            raise SystemExit("release_failed")
    if stream.end_input(325) is not ref.Status.OK:
        raise SystemExit("end_input_failed")
    for _ in range(4):
        domain.scheduler.step()
        if stream.pull().status is ref.Status.END_OF_STREAM:
            break
    else:
        raise SystemExit("end_of_stream_missing")

    _, report_digest = ref.canonical_report(domain, stream)
    if report_digest != EXPECTED_REPORT_DIGEST:
        raise SystemExit("report_digest_mismatch")
    if [(lease.source_first_sample + lease.valid_offset,
         lease.source_first_sample + lease.valid_offset + lease.valid_count)
            for lease in stream.delivered_leases] != [(0, 80), (80, 240), (240, 325)]:
        raise SystemExit("interval_conservation_mismatch")
    if stream.counters["analysis_accepted"] != 2:
        raise SystemExit("analysis_mismatch")

    print(json.dumps({
        "contract": ref.CONTRACT_ID,
        "fixture_id": fixture_package.FIXTURE_ID,
        "installed": True,
        "fixture_source_digest": fixture_package.source_digest(),
        "domain_digest": domain.config.digest,
        "graph_digest": stream.graph.digest,
        "report_digest": report_digest,
        "status": "end_of_stream",
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
