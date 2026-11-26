<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and digest
files).

## Upstream Rapidly SDK

No Rapidly SDK source checkout, native library, binary or model byte is
present. The census links `https://github.com/rapidly-labs/rapidly-sdk` and
`https://www.rapidly.io/docs/sdk/introduction/models` and records a commercial
on-device denoiser with 48 kHz trained models and latency variants. No commit,
release version, license text, notice, file list or per-file digest is locally
verified. The vendor SDK identity, revision, license identity and component map
remain open blockers. Source code being `available` upstream is not a rights
grant or a locally verified artifact.

## Model assets and entitlement

No Rapidly model variant, weight fragment, native library, entitlement or
license key is present. The pinned candidate-store snapshot records weights as
`located_unverified`, `commercial_license_required: true` and
`watermarked_without_license: true`. The four reported latency variants
(11/21/32/96 ms) and four reported model sizes (615/851/854/925 KB) are
provenance only: no model revision, byte count or SHA-256 is locally verified.
A suitable watermark-free commercial entitlement must be supplied through an
approved runtime mechanism; no key, token or entitlement secret may be
committed, logged or embedded in a manifest, report or digest file.

## Unlicensed output

The census records an audible watermark on unlicensed output and states that
demo mode cannot yield valid quality scores. No Rapidly output is generated,
retained, decoded, played, listened to or scored in this package. Any future
quality measurement must first prove a watermark-free entitled runtime and
separate that proof from the quality evidence.

## Corpus, audio and outputs

No recording, corpus, speaker consent, clean reference, enhanced output or
output-use grant is present. Corpus rights, clean-reference permission and
output use are independent open gates. Census and store facts are
source-reported provenance, not local measurements.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.th`, `.onnx`, `.safetensors`, binary library
or compiled object.
