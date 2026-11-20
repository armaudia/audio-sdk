# Reproducible evidence handoff

Status: SDK conformance record `audio-sdk/evidence-handoff/0.1`, not a session ABI.

This page defines the portable record an SDK run hands to `audio-bench`. The
record accompanies independent synthetic or applied fixture results and never
substitutes for qualification. The schema is
[`schemas/evidence-handoff.schema.json`](../schemas/evidence-handoff.schema.json)
and the tool is [`scripts/evidence_bundle.py`](../scripts/evidence_bundle.py).

## Why a handoff

The benchmark project already executes standalone fixtures and validates
observations. The SDK contributes the parts only the runtime knows: exact
source-sample intervals, produced and consumed counts, availability clocks,
partial-tail handling, cancellation outcomes and the artifact that was actually
built. The handoff carries those facts in exact integer form so a reader can
recompute them without trusting paths, wall-clock timestamps or floating point.

## Rules

- Sample positions, clock ticks and counters use canonical decimal integer
  strings, so values above `2**53` survive JSON transport unchanged. The origin
  is the capture time of source sample zero on the collector monotonic clock.
- Source intervals are half-open `[source_first_sample + valid_offset,
  source_end_sample)` and must continue without overlap or gap at the first
  valid sample. Startup, final padding and concealment are explicit flags.
- `available_monotonic_ns` is the monotonic time at which the produced block
  became available. It must not precede the capture time of its first valid
  source sample; a negative delay is invalid evidence, not a clamp.
- Denominators are exact strings: `accepted`, `valid`, `produced`, `delivered`,
  `failed`, `dropped`. Every check repeats the run's totals, so a report cannot
  silently change the denominator between checks.
- Runtime conditions and provenance are part of the identity: execution mode,
  pacing, workers, queue depths, hardware, compiler, OS, architecture, source
  revision, fixture and model digests, producer, reviewer and creation time.
- Artifacts are relative paths with media type, byte count and SHA-256. The
  bundle is exactly the listed files; an unlisted file is an error.
- `artifact_id` and `handoff_id` are aliases for the SHA-256 of the RFC 8785
  canonical record with those two fields removed. Object keys are fixed ASCII
  and JSON numbers are small integer literals in this schema. A
  changed byte anywhere in the record changes the ID, so two reviewers can
  confirm they saw the same bundle.

## Statuses

| Status | Meaning |
| --- | --- |
| `complete` | Schema, intervals, denominators, artifacts and identity are valid. Failed checks are allowed and preserved. |
| `incomplete` | Structurally valid but missing one of `identity`, `interval_conservation` or `artifact_integrity`, or contains a blocked, invalid or unrun check. Validation fails unless `--allow-incomplete` is passed. |
| `invalid` | Any schema, clock, interval, denominator, artifact, identity or duplicate-key violation. |

A `failed` check requires a stable reason such as `below_control`; the failure
stays in the record and does not make the bundle invalid. `blocked`,
`not_run` and `invalid` are also preserved, so a negative or missing result is
evidence rather than an omission.

## Commands

```sh
python3 scripts/evidence_bundle.py create \
  --input conformance/evidence/positive/input.json \
  --artifacts conformance/evidence/positive/artifacts \
  --output build/evidence/positive
python3 scripts/evidence_bundle.py validate build/evidence/positive
```

`create` requires a new output directory, recomputes every artifact size and
digest, refuses missing or unlisted files, and writes canonical `handoff.json` plus an
`artifacts/` tree. `validate` re-checks the whole record, including that both
IDs still match the canonical content.

## Bridge to audio-bench

1. Freeze the provider descriptor, effective config and build, the fixtures,
   the applicable profile, and the expected checks. Keep paired quality,
   unpaired screening, timing and synthetic correctness as distinct claims.
2. Run the SDK fixture, record its trace and denominators in `input.json`, and
   seal and validate those artifacts with `evidence_bundle.py`. For example,
   a DSP profile needs response, timing and numerical checks, not just a
   well-formed record. Use the requirements of the chosen profile to set the
   checks and limits before running it.
3. For the independent baseline, use the pinned
   [audio-bench development or extracted package](https://github.com/armaudia/audio-bench/tree/e623e14a4e85a6be7f6061aa50a30bb8824af132#development).
   With its wheel installed, run from the extracted package:

   ```sh
   python -m audio_bench smoke --output "$BENCH_BUNDLE" --native-build bin \
     --sdk-prefix sdk/audio-sdk-0.1.0 --provider speex.ns.v0
   python -m audio_bench validate "$BENCH_BUNDLE"
   ```

4. Keep the outputs side by side and cite the SDK handoff ID and the bench
   run ID. Compare provider, build, config, fixture and runtime identities
   before treating them as matched evidence. The SDK handoff is not a bench
   observation bundle: `audio_bench validate` validates the output from
   `audio_bench smoke`, not the SDK handoff. Metric identifiers, cohorts and
   publication decisions remain owned by audio-bench.

Publish only reviewed aggregate results and bundle IDs. Never include
restricted assets in a public bundle.

The synthetic fixtures under `conformance/evidence/` exercise a positive run, a
preserved negative quality result and an incomplete handoff. They contain no
workload claim and are not a qualification.
