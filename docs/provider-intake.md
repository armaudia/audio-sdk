# Provider intake and asset boundary

Status: normative checklist for contract 0.1 (`audio-sdk/descriptor/0.1`).
This page defines what an extension owner must supply before a provider, model,
tool or adapter is admitted to the public SDK, and how restricted material is
kept out of the default package.

The intake record is machine-readable. The schema is
[`schemas/provider-intake.schema.json`](../schemas/provider-intake.schema.json)
and the checker is
[`scripts/check_provider_intake.py`](../scripts/check_provider_intake.py).
An intake record is a review artifact, not a release qualification.

## Fail-closed rule

A provider is admitted only when every requirement below has a concrete,
reviewable value. Missing, empty, unknown or contradictory evidence denies
admission. In particular:

- a required asset with no digest, size or rights decision is denied;
- a rights scope of `unknown` is treated as `denied` for execution or export
  that needs that scope;
- a restricted or closed asset may not be included in a public package,
  public archive, default discovery set or public playback scope;
- a model or checkpoint whose source revision cannot be pinned is not admitted
  as a reference provider; it may only be described as a feasibility lead.

## Checklist

### 1. Identity and contract

- Provider ID matching `^[a-z0-9][a-z0-9._-]{0,95}$`, unique within the
  registry.
- Implementation ID and implementation version. A version identifies immutable
  behavior; changing preprocessing, weights or defaults requires a new version.
- Contract revision implemented. Contract 0.1 providers are fixed at
  float32, 16 kHz, mono, 160 samples per application frame.
- Descriptor schema and digest. The shipped descriptor is immutable and its
  `source_digest` covers the exact inventoried implementation files.

### 2. Source and checkpoint provenance

- Exact source revision (immutable commit or `null` only for a content-manifest
  snapshot) and source digest.
- For a model or checkpoint: immutable upstream revision, checkpoint SHA-256,
  byte count, tensor/config schema, precision, and the exact file inventory.
- The source distribution mode: `source-linked`, `binary` or `service`.
- Build recipe, compiler/runtime versions, dependency lock and platform
  requirements sufficient to reproduce the tested artifact.
- Any private artifact reference stays in approved private storage; public
  evidence contains only aggregate results and reviewed identifiers.

### 3. Assets and rights

Each external asset is declared with:

- asset ID (ASCII, unique within the provider);
- SHA-256 of the exact bytes and exact byte count;
- class: `public`, `restricted` or `closed`;
- rights decisions for `acquisition`, `evaluation`, `redistribution` and
  `public_playback`, each with an evidence reference and reviewer when allowed.

The caller supplies exactly the declared assets at session creation. The
facade verifies ID, size and digest, copies the bytes, and never downloads or
searches the filesystem. A missing, changed or extra asset fails creation.

`restricted` and `closed` assets require:

- `packages_assets: false` and external caller-supplied loading;
- an explicit evaluation decision that names the approved scope;
- no public redistribution or public playback unless separately approved;
- a named reopen condition for any scope that remains denied.

### 4. Evaluation scope

- Task and corpus/cohort pinned by revision and digest.
- Fixture manifest, validity rules, denominators, metrics and aggregation.
- Paired quality evidence separated from unpaired/no-reference evidence.
- Runtime, host, device, compiler and load condition for timing claims.
- Negative and failure cases retained, including missing assets, denied
  rights, malformed configuration and backend failure.
- A comparison-only or feasibility result is labeled as such; it is not
  implementation or release approval.

### 5. Runtime, customer and playback scope

- Runtime: `none` (DSP/no model), `cpu`, `gpu`, `npu` or `service`, with the
  exact optional dependency and the behavior when it is absent.
- Customer scope: `allowed`, `denied` or `unknown`, with the applicable rights
  scope. Customer use cannot exceed acquisition/evaluation rights.
- Playback scope: `allowed`, `denied` or `unknown`. Public playback requires an
  allowed `public_playback` decision for every input and output asset.
- Default installability: the SDK baseline must build, install and pass
  conformance with the optional runtime and all model assets absent. The
  provider must fail discovery/loading clearly when a required optional
  runtime or asset is missing.

### 6. Review and disclosure

- Named reviewer and review date.
- License and notice files, including third-party notices and any exception.
- Disclosure of restrictions in the descriptor, README and any benchmark
  report; unsupported capabilities are absent or false, never silently
  ignored.
- A reopened condition for anything not admitted.

## Admission commands

Validate an intake record before review:

```sh
python3 scripts/check_provider_intake.py --record path/to/intake.json
```

The checker rejects unknown keys, duplicate asset IDs, bad digests, incomplete
rights decisions and public packages containing restricted or closed assets.
It prints a short JSON result and exits non-zero on failure.

The released no-model providers remain the installability control: a clean
configure/build/install/`ctest` and the installed external-provider fixture must
pass with no model assets present. See
[`docs/provider-v0.md`](provider-v0.md) and
[`docs/task-evidence/provider-intake.md`](task-evidence/provider-intake.md).
