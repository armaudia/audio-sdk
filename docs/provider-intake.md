# Provider intake and asset boundary

Status: normative checklist for contract 0.1 (`audio-sdk/descriptor/0.1`).
This page defines what an extension owner must supply before a provider, model,
tool or adapter is admitted to the public SDK, and how restricted material is
kept out of the default package.

The intake record is machine-readable. Use `schemas/provider-intake.schema.json`
and the source-tree checker `scripts/check_provider_intake.py`. An intake
record is a review artifact, not a release qualification or proof of rights.

## Fail-closed rule

A provider is admitted only with an approved review and concrete, reviewable
evidence for its intended use. Missing, denied or unknown permissions block
the use that needs them; they do not confer permission for a different use.
In particular:

- a required asset with no digest, size or rights decision is denied;
- execution requires `allowed` acquisition and evaluation for the provider and
  every required asset;
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
- `descriptor_ref` and `descriptor_digest` pin the `audio-sdk/descriptor/0.1`
  file and its exact byte digest. The checker compares identity, source and
  required assets against this descriptor.

### 2. Source and checkpoint provenance

- `source_revision` is a full nonzero 40- or 64-character lowercase Git commit
  ID (never a branch, tag, or abbreviation), or `null` only for a
  content-manifest snapshot. `source_digest` and all other SHA-256 fields use
  nonzero `sha256:<64 lowercase hex>`.
- Every record requires `source_manifest_ref`: sorted unique ASCII lines of
  `<64 lowercase hex>  <repository-relative path>`. The checker hashes each
  file (CRLF normalized to LF for files without NUL bytes), then verifies
  `source_digest` over the concatenated `path NUL hex LF` entries. A non-null
  revision must resolve to a local Git commit, and each listed file must match
  its blob at that commit. Use `--git-root` for an alternate local checkout when
  checking a record; release packaging uses the SDK checkout and does not
  fetch missing objects.
- For each model/checkpoint asset, set `checkpoint` to the object with
  `upstream_revision` (full Git object ID), `tensor_config_ref`, `precision`
  and `inventory_ref`; use the asset's `sha256` and `byte_count` for the exact
  checkpoint bytes. Non-model inputs use `checkpoint: null`.
- The source distribution mode: `source-linked`, `binary` or `service`.
- Attach the build recipe, compiler/runtime versions, dependency lock and
  platform requirements to the review evidence rather than the descriptor ABI.
- Any private artifact reference stays in approved private storage; public
  evidence contains only aggregate results and reviewed identifiers.

### 3. Assets and rights

Each external asset is declared with:

- asset ID (ASCII, at most 63 characters and unique within the provider);
- SHA-256 of the exact bytes and exact byte count (at most 512 MiB in total);
- class: `public`, `restricted` or `closed`;
- rights decisions for `acquisition`, `evaluation`, `redistribution` and
  `public_playback`, each with `evidence_ref`, `reviewer` and `review_date`
  (YYYY-MM-DD) when allowed.

The caller supplies exactly the declared assets at session creation. The
facade verifies ID, size and digest, copies the bytes, and never downloads or
searches the filesystem. A missing, changed or extra asset fails creation.

`restricted` and `closed` assets require:

- `packages_assets: false` and external caller-supplied loading;
- explicit acquisition and evaluation decisions for the approved use;
- exclusion from the public catalog and playback; closed assets cannot claim
  redistribution. Packaging public assets requires allowed redistribution for
  the provider and every packaged asset.

### 4. Evaluation scope

- `evaluation.task`, `evaluation.scope` and `evaluation.evidence_ref` identify
  the task, permitted use, and evidence file. Attach corpus/cohort revision and
  digest (when applicable), fixture manifest, validity rules, denominators,
  metrics and aggregation to the evidence.
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

- Review decision, named reviewer and date. `pending` uses `null` reviewer and
  date; `pending` and `rejected` both deny admission.
- License and notice files, including third-party notices and any exception.
- Disclosure of restrictions in the descriptor, README and any benchmark
  report; unsupported capabilities are absent or false, never silently
  ignored.
- `reopen_condition` names what must change to review a denied scope again or
  what would invalidate the current review.

## Admission commands

Check a completed intake record from the source tree:

```sh
python3 scripts/check_provider_intake.py --record path/to/intake.json
```

References are paths relative to the evidence root (the repository by default)
and must resolve to files within it. The checker validates recorded decisions
and provenance; it does not authenticate the signer or interpret a license.
It prints a JSON result and exits nonzero on failure.

`scripts/package.sh` uses the same release staging for native tarballs and
the Wasm ZIP. The installed descriptor set and bytes must match the generated
data used to register the compiled built-ins; missing, extra, and changed
entries all fail. Each new or changed built-in descriptor
must have `docs/provider-intake/<provider_id>.json` matching its exact bytes, an
approved intake that allows distribution of the provider, and no restricted
or closed required assets. A failure rejects the whole candidate rather than
shipping a partial catalog. Only the two previously released, exact asset-free
descriptor digests are grandfathered and both must still be installed.
This is a packaging gate for the public discovery catalog, not a change to
`as_register_provider_v0`, which remains available to explicit integrations.

The released no-model providers remain the installability control: a clean
configure/build/install/`ctest` and the installed external-provider fixture must
pass with no model assets present. See [the provider guide](provider-v0.md).
The source tree includes a pending, non-admitted example and the task evidence
under `docs/task-evidence/`.
