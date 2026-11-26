<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-OPENVOICE-V2

This task-local evidence package is authored under Apache-2.0. It includes no
vendored OpenVoice source, generated waveform, binary, model weight, converter
checkpoint, speaker embedding, config, lifecycle archive, runtime, license
text, notice or corpus from MyShell or any third party. It pins read-only files
by SHA-256 and records provenance only.

The upstream MyShell OpenVoice code checkout is present at revision
`74a1d147b17a8c3092dd5430504bd83ef6c7eb23` and carries an MIT `LICENSE`
(SHA-256 `bb3541f421e6273d3a3e3dd5bdba2bd3b79a3c2eadca65cde9c62c2467903ac0`).
That license text is **not copied** into this directory. The upstream README
asserts that OpenVoice V1 and V2, released from April 2024, are MIT licensed and
free for commercial use. This package records that assertion but does not treat
it as a verified release-archive license, a speaker-embedding availability
record, a consent record for any reference speaker or an output-use decision.

No release archive, checkpoint, config, speaker embedding or output-use term has
been staged or reviewed. The research record states the 125 MiB converter
checkpoint was removed after the one historical run; this package treats that
as a provenance note, not a rights grant. A V2 converter config-shaped copy
inside the Seed-VC vendored module is disclosed and hashed, but it is not
admitted as the exact `checkpoints_v2_0417.zip` member. The historical output
`source_to_p360.wav` and the source/target audio are hashed as whole files and
are not decoded, played, reused or promoted.

No file in this directory may be treated as an upstream license grant, a weight
or archive term, a speaker-asset availability record or a product-use decision.
A future qualified run must stage the exact release-archive terms and notice
bundle, explicit speaker-reference availability and output-use records before
any artifact is used (see `BLK-01`, `BLK-03` and `RG-02`/`RG-04` in
`contract.json`).
