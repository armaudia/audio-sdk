<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and digest
files). No third-party source file, wheel, license text, RIR, waveform,
checkpoint or asset byte is copied into this directory.

## PyRoomAcoustics candidate

No PyRoomAcoustics source checkout, wheel, extracted package or installed
module is present. The pinned registry catalogues three source leads: S16
(denoising documentation), S24 (beamforming source excerpt) and S26
(DOA documentation). Those are URLs and titles only. No immutable revision,
source digest, upstream license text, notice, per-file inventory or runtime
identity was verified locally. The upstream project URLs are recorded for a
future caller-supplied intake, not as an imported or approved dependency.

`https://github.com/LCAV/pyroomacoustics` and
`https://pyroomacoustics.readthedocs.io/` are external references. Their terms
and exact revisions remain open blockers. No assertion is made that any
upstream licence permits product use, redistribution or a public default.

## Room and spatial evidence

No measured RIR, simulated RIR, room impulse response byte, array calibration,
timestamp alignment, corpus, label or audio file is present. The task-local
caller-tool schema contains one labelled synthetic geometry control. That
control is a plain JSON object used only to fail-closed validate field shapes;
it is not room-simulation output and is not real RIR or reverberation evidence.
Adjacent WPE, beamforming and survey results from other components are not
inherited or relicensed here.

## SDK boundary

The SDK files pinned in `SOURCES.sha256` are read-only inputs under their
existing project licences. This package does not vendor them, modify them,
claim their content as its own or add any provider, descriptor, registry,
default, ABI, build, CI, board or handoff entry.
