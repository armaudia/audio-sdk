# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-LYRA-II-V2-CODEC-PLC.

This module is standard-library only and deterministic. It contains no
Lyra II / V2 source, codec, model, weight, TFLite bundle, inference runtime,
encoded packet stream, speech corpus, audio sample or vendor result. It records
the exact external blocker, probes a fixed list of task-local paths to evidence
the absence, validates a caller-supplied future cohort manifest that admits only
explicit packet-loss intervals over an encoded stream, and builds the canonical
report.

Nothing here is a Lyra II / V2 implementation, an upstream-parity result, a
packet-loss measurement, a quality result, a listening result, a device-timing
result, a benchmark or a release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-LYRA-II-V2-CODEC-PLC"
COMPONENT_ID = "lyra-ii-v2-codec-plc"
TASK_TITLE = "Lyra II / V2 codec PLC"
CONTRACT_ID = "audio-sdk/lyra-ii-v2-codec-plc-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "enhancement"
MODE = "feasibility"
BASE_COMMIT = "b4960fdba1991a35c07ff7f22cda5257c4749768"
BRANCH = "swarm/SDK-LYRA-II-V2-CODEC-PLC"
REVIEWER = "reviewer-LYRA-II-V2-CODEC-PLC"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-LYRA-II-V2-CODEC-PLC")
WRITE_SCOPE = "docs/task-evidence/lyra-ii-v2-codec-plc/ only"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
TASK_PREFIX = "docs/task-evidence/lyra-ii-v2-codec-plc/"


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable inputs. `source:` rows are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/findings.md":
        "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
    "research/voice-enhancement-20261101/evaluation_records.md":
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "research/voice-enhancement-20261101/agent-denoise/REPORT.md":
        "eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md":
        "5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14",
    "research/voice-enhancement-20261101/agent-matrix-audit/REPORT-followup7.md":
        "5865f2f16f1048ae9449ad6e8383728a1e5010a2d78346baa67728fc1c992fbe",
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md":
        "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
    "research/voice-enhancement-20261101/agent-opus-plc/provenance-audit.md":
        "ab36bab86f58e82ee139adfae011d17f13e23e26c3dba3f5ea80678713428b53",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/opus-deep-plc/README.md":
        "457346f71005fe76d0b9c9d54fba7625262f69391cfc8e60341607fedef1549d",
    "docs/task-evidence/opus-deep-plc/report.json":
        "df8cb2dad636a6d1ded205b872297ddf43936c65dfc75febc5e6c5f4f0415df2",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/report.json":
        "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e",
    "docs/task-evidence/opus-dred/report.json":
        "2997dc6cc9e623a762379ca498c178c22a9607591a39ea8bcf6ef2691544a3f2",
    "docs/task-evidence/complex-bin2bin-generative-plc/report.json":
        "6f6214f89eca8009a19e980c3cc5b24af918c600345573e861d18d2da1e54f23",
    "docs/task-evidence/autoregressive-plc/report.json":
        "4730ceb74e03782c90dcd78332443c2129cdf56af14ef29bcc89435b68007aec",
    "docs/task-evidence/pitch-period-repeat-plc/report.json":
        "114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445",
    "docs/task-evidence/linear-interpolation-plc/report.json":
        "0a711aa398be0f86559249781f429323cee2eaf31ced1585f5d8fc205248b323",
    "docs/task-evidence/zero-fill-plc/report.json":
        "3f23c4453caf289ab34ca61af6c94dacb5e9abe9b31fd71a6922ac305e7281ca",
    "docs/task-evidence/elastic-pcm-packets/README.md":
        "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/survey-rst-04/report.json":
        "da399d3192c14ce8471103464530cf3c684a28cde3c62249daeba7f163de6042",
    "docs/task-evidence/survey-eng-04/report.json":
        "c11355762f528e51c8ea92782d921414b8221b0eb0b3ecee74227ac735e97583",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-OPUS-DEEP-PLC",
        "title": "Opus deep PLC",
        "component": "opus-deep-plc",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
        "title": "Opus 1.4 standard decoder PLC",
        "component": "opus-1-4-standard-decoder-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-ELASTIC",
                       "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-OPUS-DRED",
        "title": "Opus DRED",
        "component": "opus-dred",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC",
        "title": "Complex-Bin2bin generative PLC",
        "component": "complex-bin2bin-generative-plc",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-AUTOREGRESSIVE-PLC",
        "title": "Autoregressive PLC",
        "component": "autoregressive-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-ELASTIC",
                       "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-PITCH-PERIOD-REPEAT-PLC",
        "title": "Pitch-period repeat PLC",
        "component": "pitch-period-repeat-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-ELASTIC",
                       "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-LINEAR-INTERPOLATION-PLC",
        "title": "Linear interpolation PLC",
        "component": "linear-interpolation-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-ELASTIC",
                       "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-ZERO-FILL-PLC",
        "title": "Zero-fill PLC",
        "component": "zero-fill-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-ELASTIC",
                       "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "data/checkouts/lyra",
    "data/checkouts/lyra-ii",
    "data/checkouts/lyra-v2",
    "data/checkouts/lyra-codec",
    "data/checkouts/lyra-ii-v2-codec-plc",
    "adapters/lyra",
    "adapters/lyra-ii-v2",
    "adapters/lyra-ii-v2-codec-plc",
    "third_party/lyra",
    "third_party/lyra-ii-v2",
    "deps/lyra",
    "deps/lyra-ii-v2",
    "src/lyra",
    "src/lyra_codec",
    "lyra",
    "lyra-ii-v2-codec-plc",
    "models/lyra",
    "data/models/lyra",
    "data/models/lyra-ii-v2",
    "data/assets/lyra",
    "data/assets/lyra-ii-v2",
    "data/checkpoints/lyra",
    "checkpoints/lyra",
    "data/traces/lyra",
    "data/runs/lyra-ii-v2-codec-plc",
    "research/voice-enhancement-20261101/agent-lyra",
    "LICENSES/Lyra.txt",
    "LICENSES/Lyra-II-V2.txt",
    "notices/third-party/lyra",
    "docs/provider-intake/lyra-ii-v2-codec-plc.json",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "permitted_source",
        "requirement": (
            "The exact permitted Google Lyra source tree for the declared "
            "Lyra II / V2 codec variant at an immutable 40-hex revision, "
            "containing the codec, decoder, PLC/concealment and packetization "
            "entry points and the exact build/environment lock, with an "
            "immutable archive SHA-256. No branch, tag or abbreviation is "
            "accepted."),
    },
    {
        "id": "ART-02",
        "kind": "license_and_model_terms",
        "requirement": (
            "The upstream license text, copyright notices, model/weight "
            "terms, third-party notices and any patent or use restrictions "
            "for the pinned revision and every model artifact, with an "
            "explicit rights review for acquisition, evaluation, "
            "redistribution, derived output and product use."),
    },
    {
        "id": "ART-03",
        "kind": "exact_codec_model_and_bitstream_state",
        "requirement": (
            "Every model or weight artifact (for example the declared TFLite "
            "model bundle) with exact SHA-256 and byte count, tensor-config "
            "and precision identity, input/output geometry, codec bitstream "
            "and decoder-state definition, PLC trigger behavior and "
            "permitted-use terms. A model without a pinned source revision "
            "and rights decision does not qualify."),
    },
    {
        "id": "ART-04",
        "kind": "reproducible_runtime",
        "requirement": (
            "A reproducible pinned codec runtime or container with the exact "
            "CLI/API names, model loader, dependency lock, compiler and "
            "accelerator requirements, install location, artifact SHA-256 "
            "and behavior when models, TFLite delegates or optional assets "
            "are absent."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_matched_packet_loss_cohort",
        "requirement": (
            "A rights-cleared frozen 16 kHz mono packetized cohort with the "
            "exact encoded packet stream, explicit loss masks or interval "
            "events, decoder reset/state policy, loss-rate and burst strata, "
            "clean/source references and a task-matched established baseline "
            "(Opus PLC or the identity codec). No inferred loss from a "
            "silent gap or waveform proxy is accepted as a codec event."),
    },
    {
        "id": "ART-06",
        "kind": "measurement_and_quality_harness",
        "requirement": (
            "An agreed enhancement evaluation harness: paired SI-SDR and "
            "STOI where permitted clean references exist, clean-speech "
            "preservation, output-peak and invalid/nonfinite-output "
            "accounting, codec alignment and content/availability delay, "
            "decoder-state and memory accounting, target-runtime timing and "
            "an authorized listening or separately labelled predictive "
            "screen protocol, with margins, deadlines and resource limits."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "No Google Lyra source snapshot, archive or exact Lyra II / V2 "
            "variant exists at any fixed probe location. The pinned candidate "
            "matrix already marks the candidate `unavailable/blocked`, and no "
            "revision or archive digest can be pinned from a local artifact. "
            "The exact II versus V2 variant and release are not pinned "
            "locally."),
        "required_action": (
            "Declare the exact Lyra II or V2 codec variant and supply its "
            "full 40-hex source revision and immutable archive SHA-256 from "
            "a source root that permits local review, including codec, "
            "decoder, PLC and packetization entry points."),
        "linked_gates": ["RG-01", "RG-04"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "The upstream license, copyright, model/weight terms and notice "
            "bundle are absent locally, so no acquisition, evaluation, "
            "redistribution, derived-output or product-use scope can be "
            "reviewed. A public repository URL, release note or blog post is "
            "not a license grant."),
        "required_action": (
            "Supply the complete license/notices/model-terms bundle for the "
            "pinned variant and revision, and record explicit rights "
            "decisions for every required artifact and intended use."),
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "No Lyra model, weight, TFLite bundle, tensor config, codec "
            "bitstream definition or decoder-state geometry is present. "
            "Nothing was downloaded, reconstructed, reverse-engineered or "
            "substituted with a generic neural, generative or waveform "
            "model."),
        "required_action": (
            "Supply every exact model artifact with SHA-256, byte count, "
            "architecture and tensor-config identity, precision, "
            "input/output geometry, bitstream/decoder-state definition and "
            "permitted-use terms."),
        "linked_gates": ["RG-03", "RG-04"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No built or reproducible Lyra codec/TFLite runtime, installed "
            "location or dependency lock is present. The exact CLI/API, "
            "decoder default state, delegate path and missing-runtime "
            "behavior cannot be exercised or verified."),
        "required_action": (
            "Supply a reproducible pinned runtime with exact CLI/API, model "
            "loader, dependency lock, compiler/accelerator requirements and "
            "artifact digest, plus the behavior when models or optional "
            "accelerators are absent."),
        "linked_gates": ["RG-04", "RG-07"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared packetized cohort, encoded packet stream, "
            "explicit loss mask, clean/source baseline or task-matched "
            "baseline exists. The pinned Opus and waveform PLC packages are "
            "separate controls and are not Lyra decoder concealment."),
        "required_action": (
            "Supply an immutable 16 kHz mono packetized cohort with the exact "
            "encoded stream, explicit loss intervals, decoder reset/state "
            "policy, declared strata, clean/source references and Opus PLC "
            "or identity-codec baseline."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No task-specific quality, listening, preservation, peak, "
            "invalid-output, alignment, delay, decoder-state, memory or "
            "target-runtime timing protocol and no agreed margins, deadlines "
            "or resource limits exist, so no result can qualify."),
        "required_action": (
            "Agree and staff the enhancement quality/listening, "
            "preservation, peak, invalid-output, alignment/delay, "
            "decoder-state/memory and target-runtime timing protocols before "
            "collecting results."),
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "upstream_source_and_revision_pin",
        "statement": (
            "An exact permitted Lyra II / V2 source variant and revision is "
            "pinned with an immutable archive before any implementation "
            "claim."),
        "reopen_condition": (
            "The exact variant, source revision, tree and archive digests are "
            "recorded and the source root permits local review."),
    },
    {
        "id": "RG-02",
        "title": "upstream_license_model_terms_and_notices",
        "statement": (
            "A reviewed license, model/weight terms and notice bundle exists "
            "for the pinned revision."),
        "reopen_condition": (
            "The complete license/notices/model-terms bundle is supplied, "
            "reviewed and its approved scope recorded for every asset."),
    },
    {
        "id": "RG-03",
        "title": "exact_codec_model_and_geometry_integrity",
        "statement": (
            "Every model/weight artifact is pinned by SHA-256 with exact "
            "architecture, precision, bitstream and input/output geometry."),
        "reopen_condition": (
            "Pin each model artifact, verify tensor config, precision, "
            "bitstream/decoder-state geometry and confirm permitted use."),
    },
    {
        "id": "RG-04",
        "title": "reproducible_runtime_and_decoder_parity",
        "statement": (
            "A reproducible pinned codec runtime and the exact model and "
            "decoder reproduce approved reference outputs."),
        "reopen_condition": (
            "Build or install the pinned runtime, map the exact CLI/API and "
            "decoder default state, and reproduce approved reference "
            "outputs."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_matched_packetized_cohort",
        "statement": (
            "A rights-cleared frozen packetized cohort with encoded streams, "
            "explicit loss intervals, clean/source references and a "
            "task-matched baseline is frozen before any result."),
        "reopen_condition": (
            "The immutable corpus, encoded packet streams, explicit loss "
            "events, metadata, strata, baseline and clean/source references "
            "are supplied and reviewed."),
    },
    {
        "id": "RG-06",
        "title": "enhancement_quality_and_independent_listening",
        "statement": (
            "Paired SI-SDR/STOI, clean-speech preservation and independent "
            "listening or an authorized predictive screen are completed for "
            "the exact conditions and rights scope."),
        "reopen_condition": (
            "Pinned scorers and an approved listening protocol/panel produce "
            "reviewed results on the frozen cohort."),
    },
    {
        "id": "RG-07",
        "title": "preservation_peak_invalid_delay_state_and_resources",
        "statement": (
            "Clean-speech preservation, output peaks, invalid/nonfinite "
            "outputs, codec alignment, content/availability delay, "
            "decoder-state, memory and target-runtime resource limits are "
            "measured, not inferred."),
        "reopen_condition": (
            "Paced target-runtime runs record preservation, peaks, invalid "
            "outputs, alignment, delay, decoder state, CPU, memory and "
            "deadline behavior against agreed limits."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "Opt-in provider intake, an explicit public-surface decision, "
            "independent review and release approval are complete."),
        "reopen_condition": (
            "A separate versioned intake accepts the component with an OFF "
            "default, records the public-surface decision and passes "
            "independent exact-head review."),
    },
)

ENHANCEMENT_PROFILE_ROWS = (
    {
        "id": "ENH-01",
        "requirement": (
            "Run an identity/noisy control and an established task-matched "
            "baseline."),
        "status": "blocked",
        "evidence": (
            "No Lyra runtime exists, so no identity/noisy codec control and "
            "no Opus PLC or identity-codec baseline were run against it."),
    },
    {
        "id": "ENH-02",
        "requirement": (
            "Score paired SI-SDR and STOI where permitted clean references "
            "exist."),
        "status": "blocked",
        "evidence": (
            "No rights-cleared clean reference, decoded candidate output or "
            "pinned paired scorer exists for this candidate."),
    },
    {
        "id": "ENH-03",
        "requirement": "Measure clean-speech preservation.",
        "status": "blocked",
        "evidence": (
            "No clean speech and no decoded candidate output exist, so "
            "preservation cannot be measured."),
    },
    {
        "id": "ENH-04",
        "requirement": "Measure peaks and invalid outputs.",
        "status": "blocked",
        "evidence": (
            "No output samples exist, so no peak or invalid/nonfinite-output "
            "count was measured."),
    },
    {
        "id": "ENH-05",
        "requirement": (
            "For unpaired speech use a separately labeled predictive screen "
            "or authorized listening."),
        "status": "blocked",
        "evidence": (
            "No authorized listening result or separately labelled "
            "predictive screen exists for this candidate."),
    },
    {
        "id": "ENH-06",
        "requirement": (
            "Report alignment, state, memory and measured "
            "content/availability timing for the exact runtime."),
        "status": "blocked",
        "evidence": (
            "No runtime, decoder-state trace, memory measurement or paced "
            "content/availability timing exists."),
    },
)

MEASUREMENT_ROWS = (
    {
        "id": "MR-01",
        "metric": "exact_source_variant_and_model_identity",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No source revision, archive, model or weight file exists at any "
            "fixed probe, and the exact Lyra II versus V2 variant is not "
            "pinned locally."),
    },
    {
        "id": "MR-02",
        "metric": "explicit_packet_loss_intervals",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No packetized cohort or explicit loss trace exists; no loss "
            "interval was observed or admitted."),
    },
    {
        "id": "MR-03",
        "metric": "paired_si_sdr_and_stoi",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No decoded candidate output, clean reference or pinned scorer "
            "exists, so no paired SI-SDR or STOI value was produced."),
    },
    {
        "id": "MR-04",
        "metric": "clean_speech_preservation",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No clean speech or decoded candidate output exists, so "
            "preservation was not measured."),
    },
    {
        "id": "MR-05",
        "metric": "output_peak_and_invalid_output_count",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No output samples exist, so no peak or invalid/nonfinite-output "
            "count was produced."),
    },
    {
        "id": "MR-06",
        "metric": "alignment_and_content_availability_delay",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No aligned decode or paced stream exists, so no content or "
            "availability delay was measured; the source-reported 20 ms "
            "codec delay is not a local measurement."),
    },
    {
        "id": "MR-07",
        "metric": "decoder_state_memory_and_target_runtime_timing",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No runtime was executed, so decoder state, memory and "
            "target-runtime timing were not measured."),
    },
    {
        "id": "MR-08",
        "metric": "independent_listening_or_authorized_screen",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No listening panel result or authorized, separately labelled "
            "predictive screen exists."),
    },
)

PROFILE_PHRASES = (
    "Run identity/noisy control and an established task-matched baseline.",
    "Score paired SI-SDR and STOI where permitted clean references exist.",
    "Measure clean-speech preservation, peaks and invalid outputs.",
    "For unpaired speech use a separately labeled predictive screen or "
    "authorized listening.",
    "Report alignment, state, memory and measured content/availability "
    "timing for the exact runtime.",
)

EXPLICIT_LOSS_POLICY = {
    "policy": "explicit_packet_loss_intervals_only",
    "codec_packets_required": True,
    "waveform_proxy_is_not_codec_plc": True,
    "inferred_loss_from_silence_or_sequence_gap": False,
    "loss_without_interval": "rejected",
    "intervals_ordered_non_overlapping": True,
    "event_count_observed": None,
    "intervals_recorded": False,
    "decoder_state_reset_policy_recorded": False,
    "concealment_outputs_recorded": False,
    "status": "blocked",
}

SOURCE_REPORTED_CLAIMS = {
    "evidence_class": "source_reported_not_reproduced",
    "source_urls": [
        "https://github.com/google/lyra/releases",
        ("https://opensource.googleblog.com/2022/09/"
         "lyra-v2-a-better-faster-and-more-versatile-speech-codec.html"),
    ],
    "claims": [
        {
            "id": "SRC-01",
            "claim": (
                "The pinned local note records that Google Lyra release "
                "1.2.0 folds packet-loss handling into DecodeSamples() and "
                "that the decoder switches to PLC when needed."),
            "local_verification": False,
            "qualifies_candidate": False,
        },
        {
            "id": "SRC-02",
            "claim": (
                "Google reports Android speed for the codec as a "
                "source-reported property, not a measurement from this "
                "repository."),
            "local_value": None,
            "local_verification": False,
            "qualifies_candidate": False,
        },
        {
            "id": "SRC-03",
            "claim": (
                "Google reports a 20 ms codec delay as a source-reported "
                "property; it is not measured here and is not adopted as "
                "candidate geometry."),
            "source_reported_delay_ms": 20,
            "local_value": None,
            "local_verification": False,
            "qualifies_candidate": False,
        },
        {
            "id": "SRC-04",
            "claim": (
                "The upstream release describes TFLite model artifacts; no "
                "TFLite model or runtime is present locally."),
            "present_locally": False,
            "local_verification": False,
            "qualifies_candidate": False,
        },
    ],
    "local_metrics": None,
    "reproduced_here": False,
    "qualifies_candidate": False,
}

CANDIDATE_IDENTITY = {
    "declared_name": "Lyra II / V2 codec PLC",
    "inventory_component_id": COMPONENT_ID,
    "upstream_repository": "google/lyra",
    "exact_variant_pinned": False,
    "exact_release_pinned": False,
    "source_revision": None,
    "model_revision": None,
    "decoder_geometry": None,
    "reason": (
        "Local notes name Lyra II/V2 and Google's Lyra repository/release, but "
        "no local artifact pins whether the intended candidate is Lyra II, "
        "Lyra V2, a specific release or a specific model bundle."),
    "qualifies_candidate": False,
}

NON_CLAIMS = (
    "No Lyra II / V2 source, codec, model, TFLite bundle, runtime or vendor "
    "result is present, linked or executed.",
    "No packetized loss cohort, encoded packet stream, loss trace, clean "
    "reference, real corpus or media file is present or read.",
    "No Lyra implementation, approximation, substitute or comparison is "
    "shipped; no waveform PLC proxy, Opus PLC, DRED, autoregressive, "
    "pitch-repeat, linear or zero-fill result stands in for Lyra decoder "
    "concealment.",
    "No packet-loss, quality, intelligibility, naturalness, "
    "speech-preservation, listening, delay, device-timing, benchmark or "
    "release result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, shared build or CI "
    "change is made.",
    "No Opus deep PLC, Opus 1.4 standard PLC, Complex-Bin2bin, DRED, LACE, "
    "NoLACE, autoregressive, pitch-repeat, linear, zero-fill or "
    "packetization result is reused, pooled or reinterpreted as Lyra "
    "evidence.",
    "No source-reported speed, delay or model claim is presented as a local "
    "measurement, and no missing, synthetic or schema-control result is "
    "promoted.",
)

# Admission manifest is a task-local schema, not an upstream or SDK contract.
MANIFEST_SCHEMA_ID = "audio-sdk/lyra-ii-v2-cohort/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "cohort_id",
    "model",
    "geometry",
    "loss_trace",
    "clean_reference",
    "score_protocol",
)
MODEL_FIELDS = (
    "source_revision",
    "source_sha256",
    "source_path",
    "license_path",
    "license_sha256",
    "rights_decision",
    "model_path",
    "model_sha256",
    "model_bytes",
    "runtime_path",
    "runtime_sha256",
)
GEOMETRY_FIELDS = (
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "packet_samples",
    "expected_delay_samples",
)
LOSS_TRACE_FIELDS = ("path", "sha256", "intervals")
INTERVAL_FIELDS = ("first_sample", "sample_count")
CLEAN_REFERENCE_FIELDS = ("path", "sha256", "alignment", "offset_samples")
SCORE_PROTOCOL_FIELDS = (
    "metrics",
    "baseline",
    "paired_clean_reference",
    "minimum_items",
)
RIGHTS_DECISIONS = ("allowed", "denied")
ALIGNMENTS = ("sample_exact", "declared_offset")
BASELINES = (
    "opus_plc",
    "identity_codec",
)
METRICS = ("si_sdr", "stoi")
SDK_SAMPLE_RATE = 16000
SDK_CHANNELS = 1
SDK_FRAME_SAMPLES = 160
MAX_FRAME_SAMPLES = 96000
MAX_PACKET_SAMPLES = 96000
MAX_DELAY_SAMPLES = 96000
MAX_MODEL_BYTES = 512 * 1024 * 1024
MAX_INTERVALS = 10000
MAX_MINIMUM_ITEMS = 10000
MAX_PATH_LENGTH = 1024
MAX_INT64 = 2 ** 63 - 1
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


# --------------------------------------------------------------------------
# Strict JSON and digests
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def loads_strict(text: str) -> dict:
    """Parse a strict JSON object; reject duplicate keys, NaN and Infinity."""
    if text.startswith("\ufeff"):
        raise ValueError("json_byte_order_mark")
    parsed = json.loads(text, object_pairs_hook=_unique_object,
                        parse_constant=_reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict:
    return loads_strict(Path(path).read_text(encoding="utf-8"))


def canonical_text(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: Any) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# Pins, board identity and absence probes
# --------------------------------------------------------------------------
def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative in sorted(pins):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != pins[relative]:
            raise ValueError("pin_digest_mismatch:" + relative)
        rows[relative] = {"sha256": pins[relative], "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(path: Path) -> dict:
    board = read_strict_json(path)
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ValueError("board_row_not_unique:" + TASK)
    return {field: rows[0].get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([{field: row.get(field) for field in BOARD_ROW_FIELDS}
                          for row in rows])


def absence_probes(audio_root: Path, probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory; any present path blocks shipping."""
    sdk_root = WORKTREE if worktree is None else worktree
    rows: list[dict] = []
    for relative in probes:
        workspace_path = Path(audio_root) / relative
        sdk_candidate = sdk_root / relative
        if workspace_path.exists() or sdk_candidate.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
        "all_probes_absent": all(not row["present"] for row in rows),
    }


# --------------------------------------------------------------------------
# Admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def _nonfinite_path(value: Any, path: str = "") -> str | None:
    if isinstance(value, float) and not math.isfinite(value):
        return path or "<root>"
    if isinstance(value, dict):
        for key in sorted(value):
            found = _nonfinite_path(value[key],
                                    (path + "." + str(key)).lstrip("."))
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _nonfinite_path(item, f"{path}[{index}]")
            if found:
                return found
    return None


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if len(value) > MAX_PATH_LENGTH or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    if ".." in Path(value).parts or "~" in value:
        return False
    return os.path.normpath(value) == value


def _object_problem(value: Any, fields: tuple[str, ...],
                    prefix: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        return "invalid_object", prefix
    missing = sorted(set(fields) - set(value))
    if missing:
        return "missing_field", (prefix + "." + missing[0]).lstrip(".")
    unknown = sorted(set(value) - set(fields))
    if unknown:
        return "unknown_field", (prefix + "." + unknown[0]).lstrip(".")
    return "", ""


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and HEX64.match(value) is not None


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed cohort admission. No audio is read and no model runs."""
    checks = 0
    nonfinite = _nonfinite_path(document)
    if nonfinite:
        return _reject("nonfinite_value", nonfinite)
    if not isinstance(document, dict):
        return _reject("manifest_not_object")
    code, field = _object_problem(document, MANIFEST_FIELDS, "")
    if code:
        return _reject(code, field)
    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema", "schema_id")
    if (not isinstance(document["cohort_id"], str)
            or not SLUG.match(document["cohort_id"])):
        return _reject("invalid_value", "cohort_id")
    checks += 1

    model = document["model"]
    code, field = _object_problem(model, MODEL_FIELDS, "model")
    if code:
        return _reject(code, field)
    if (not isinstance(model["source_revision"], str)
            or not HEX40.match(model["source_revision"])):
        return _reject("invalid_value", "model.source_revision")
    for name in ("source_sha256", "license_sha256", "model_sha256",
                 "runtime_sha256"):
        if not _is_sha(model[name]):
            return _reject("invalid_value", "model." + name)
    for name in ("source_path", "license_path", "model_path",
                 "runtime_path"):
        if not _path_is_canonical(model[name]):
            return _reject("invalid_path", "model." + name)
    if model["rights_decision"] == "denied":
        return _reject("rights_denied", "model.rights_decision")
    if model["rights_decision"] not in RIGHTS_DECISIONS:
        return _reject("invalid_value", "model.rights_decision")
    if (not _is_int(model["model_bytes"])
            or model["model_bytes"] < 1
            or model["model_bytes"] > MAX_MODEL_BYTES):
        return _reject("invalid_value", "model.model_bytes")
    checks += 1

    geometry = document["geometry"]
    code, field = _object_problem(geometry, GEOMETRY_FIELDS, "geometry")
    if code:
        return _reject(code, field)
    if geometry["sample_rate_hz"] != SDK_SAMPLE_RATE:
        return _reject("invalid_value", "geometry.sample_rate_hz")
    if geometry["channels"] != SDK_CHANNELS:
        return _reject("invalid_value", "geometry.channels")
    if (not _is_int(geometry["frame_samples"])
            or geometry["frame_samples"] < 1
            or geometry["frame_samples"] > MAX_FRAME_SAMPLES):
        return _reject("invalid_value", "geometry.frame_samples")
    if (not _is_int(geometry["packet_samples"])
            or geometry["packet_samples"] < 1
            or geometry["packet_samples"] > MAX_PACKET_SAMPLES):
        return _reject("invalid_value", "geometry.packet_samples")
    if (not _is_int(geometry["expected_delay_samples"])
            or geometry["expected_delay_samples"] < 0
            or geometry["expected_delay_samples"] > MAX_DELAY_SAMPLES):
        return _reject("invalid_value", "geometry.expected_delay_samples")
    checks += 1

    trace = document["loss_trace"]
    code, field = _object_problem(trace, LOSS_TRACE_FIELDS, "loss_trace")
    if code:
        return _reject(code, field)
    if not _path_is_canonical(trace["path"]):
        return _reject("invalid_path", "loss_trace.path")
    if not _is_sha(trace["sha256"]):
        return _reject("invalid_value", "loss_trace.sha256")
    intervals = trace["intervals"]
    if not isinstance(intervals, list) or not intervals:
        return _reject("invalid_value", "loss_trace.intervals")
    if len(intervals) > MAX_INTERVALS:
        return _reject("invalid_value", "loss_trace.intervals")
    previous_end = 0
    for index, interval in enumerate(intervals):
        code, field = _object_problem(
            interval, INTERVAL_FIELDS, f"loss_trace.intervals[{index}]")
        if code:
            return _reject(code, field)
        first = interval["first_sample"]
        count = interval["sample_count"]
        if (not _is_int(first) or first < 0
                or first > MAX_INT64 - 1):
            return _reject("invalid_value",
                           f"loss_trace.intervals[{index}].first_sample")
        if (not _is_int(count) or count < 1
                or first + count > MAX_INT64):
            return _reject("invalid_value",
                           f"loss_trace.intervals[{index}].sample_count")
        if index > 0 and first < previous_end:
            return _reject("invalid_value", "loss_trace.intervals.order")
        previous_end = first + count
    checks += 1

    clean = document["clean_reference"]
    code, field = _object_problem(clean, CLEAN_REFERENCE_FIELDS,
                                  "clean_reference")
    if code:
        return _reject(code, field)
    if not _path_is_canonical(clean["path"]):
        return _reject("invalid_path", "clean_reference.path")
    if not _is_sha(clean["sha256"]):
        return _reject("invalid_value", "clean_reference.sha256")
    if clean["alignment"] not in ALIGNMENTS:
        return _reject("invalid_value", "clean_reference.alignment")
    if (not _is_int(clean["offset_samples"])
            or clean["offset_samples"] < 0
            or clean["offset_samples"] > MAX_DELAY_SAMPLES):
        return _reject("invalid_value", "clean_reference.offset_samples")
    if clean["alignment"] == "sample_exact" and clean["offset_samples"] != 0:
        return _reject("invalid_value", "clean_reference.offset_samples")
    checks += 1

    score = document["score_protocol"]
    code, field = _object_problem(score, SCORE_PROTOCOL_FIELDS,
                                  "score_protocol")
    if code:
        return _reject(code, field)
    metrics = score["metrics"]
    if (not isinstance(metrics, list) or len(metrics) != len(METRICS)
            or metrics != list(METRICS)):
        return _reject("invalid_value", "score_protocol.metrics")
    if score["baseline"] not in BASELINES:
        return _reject("invalid_value", "score_protocol.baseline")
    if score["paired_clean_reference"] is not True:
        return _reject("invalid_value", "score_protocol.paired_clean_reference")
    if (not _is_int(score["minimum_items"])
            or score["minimum_items"] < 1
            or score["minimum_items"] > MAX_MINIMUM_ITEMS):
        return _reject("invalid_value", "score_protocol.minimum_items")
    checks += 1

    if probe_paths:
        for name in ("source_path", "license_path", "model_path",
                     "runtime_path"):
            if not Path(model[name]).is_file():
                return _reject("probe_missing", "model." + name)
        if not Path(trace["path"]).is_file():
            return _reject("probe_missing", "loss_trace.path")
        if not Path(clean["path"]).is_file():
            return _reject("probe_missing", "clean_reference.path")
    return _accept(checks)


def _manifest_control() -> dict:
    """A structural manifest only; its paths and bytes do not exist."""
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "synthetic-schema-control",
        "model": {
            "source_revision": "a" * 40,
            "source_sha256": "b" * 64,
            "source_path": "/synthetic/lyra/source",
            "license_path": "/synthetic/lyra/LICENSE",
            "license_sha256": "c" * 64,
            "rights_decision": "allowed",
            "model_path": "/synthetic/lyra/model.pt",
            "model_sha256": "d" * 64,
            "model_bytes": 1024,
            "runtime_path": "/synthetic/lyra/runtime",
            "runtime_sha256": "e" * 64,
        },
        "geometry": {
            "sample_rate_hz": SDK_SAMPLE_RATE,
            "channels": SDK_CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
            "packet_samples": SDK_FRAME_SAMPLES,
            "expected_delay_samples": 0,
        },
        "loss_trace": {
            "path": "/synthetic/lyra/loss.json",
            "sha256": "f" * 64,
            "intervals": [{"first_sample": 1600, "sample_count": 160}],
        },
        "clean_reference": {
            "path": "/synthetic/lyra/clean.wav",
            "sha256": "1" * 64,
            "alignment": "sample_exact",
            "offset_samples": 0,
        },
        "score_protocol": {
            "metrics": list(METRICS),
            "baseline": "opus_plc",
            "paired_clean_reference": True,
            "minimum_items": 12,
        },
    }


def _set(path: tuple[Any, ...], value: Any):
    def mutate(document: dict) -> None:
        target: Any = document
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def _delete(path: tuple[Any, ...]):
    def mutate(document: dict) -> None:
        target: Any = document
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    return mutate


CASE_DEFINITIONS = (
    ("M01", "root is not an object", None, "manifest_not_object", ""),
    ("M02", "missing top-level field", ("delete", ("cohort_id",)),
     "missing_field", "cohort_id"),
    ("M03", "unknown top-level field", ("set", ("extra",), "x"),
     "unknown_field", "extra"),
    ("M04", "wrong manifest schema", ("set", ("schema_id",), "wrong"),
     "invalid_schema", "schema_id"),
    ("M05", "uppercase cohort id", ("set", ("cohort_id",), "Synthetic"),
     "invalid_value", "cohort_id"),
    ("M06", "empty cohort id", ("set", ("cohort_id",), ""),
     "invalid_value", "cohort_id"),
    ("M07", "model missing field", ("delete", ("model", "source_sha256")),
     "missing_field", "model.source_sha256"),
    ("M08", "model unknown field", ("set", ("model", "extra"), "x"),
     "unknown_field", "model.extra"),
    ("M09", "uppercase revision", ("set", ("model", "source_revision"),
                                   "A" * 40),
     "invalid_value", "model.source_revision"),
    ("M10", "short revision", ("set", ("model", "source_revision"), "a" * 39),
     "invalid_value", "model.source_revision"),
    ("M11", "relative source path", ("set", ("model", "source_path"),
                                     "relative/source"),
     "invalid_path", "model.source_path"),
    ("M12", "path traversal license path", ("set", ("model", "license_path"),
                                             "/caller/../LICENSE"),
     "invalid_path", "model.license_path"),
    ("M13", "null byte runtime path", ("set", ("model", "runtime_path"),
                                       "/caller/lib\x00.so"),
     "invalid_path", "model.runtime_path"),
    ("M14", "short source hash", ("set", ("model", "source_sha256"), "b" * 63),
     "invalid_value", "model.source_sha256"),
    ("M15", "nonhex model hash",
     ("set", ("model", "model_sha256"), "g" * 64),
     "invalid_value", "model.model_sha256"),
    ("M16", "model bytes zero",
     ("set", ("model", "model_bytes"), 0),
     "invalid_value", "model.model_bytes"),
    ("M17", "model bytes bool",
     ("set", ("model", "model_bytes"), True),
     "invalid_value", "model.model_bytes"),
    ("M18", "model bytes float",
     ("set", ("model", "model_bytes"), 1.5),
     "invalid_value", "model.model_bytes"),
    ("M19", "model bytes over bound",
     ("set", ("model", "model_bytes"), MAX_MODEL_BYTES + 1),
     "invalid_value", "model.model_bytes"),
    ("M20", "rights denied", ("set", ("model", "rights_decision"), "denied"),
     "rights_denied", "model.rights_decision"),
    ("M21", "rights unknown", ("set", ("model", "rights_decision"), "unknown"),
     "invalid_value", "model.rights_decision"),
    ("M22", "geometry missing field", ("delete", ("geometry", "channels")),
     "missing_field", "geometry.channels"),
    ("M23", "geometry unknown field", ("set", ("geometry", "extra"), 1),
     "unknown_field", "geometry.extra"),
    ("M24", "wrong sample rate", ("set", ("geometry", "sample_rate_hz"),
                                  48000),
     "invalid_value", "geometry.sample_rate_hz"),
    ("M25", "stereo channels", ("set", ("geometry", "channels"), 2),
     "invalid_value", "geometry.channels"),
    ("M26", "frame samples zero", ("set", ("geometry", "frame_samples"), 0),
     "invalid_value", "geometry.frame_samples"),
    ("M27", "frame samples bool", ("set", ("geometry", "frame_samples"), True),
     "invalid_value", "geometry.frame_samples"),
    ("M28", "packet samples zero",
     ("set", ("geometry", "packet_samples"), 0),
     "invalid_value", "geometry.packet_samples"),
    ("M29", "packet samples over bound",
     ("set", ("geometry", "packet_samples"), MAX_PACKET_SAMPLES + 1),
     "invalid_value", "geometry.packet_samples"),
    ("M30", "negative delay",
     ("set", ("geometry", "expected_delay_samples"), -1),
     "invalid_value", "geometry.expected_delay_samples"),
    ("M31", "delay over bound",
     ("set", ("geometry", "expected_delay_samples"),
      MAX_DELAY_SAMPLES + 1),
     "invalid_value", "geometry.expected_delay_samples"),
    ("M32", "loss trace missing field", ("delete", ("loss_trace", "sha256")),
     "missing_field", "loss_trace.sha256"),
    ("M33", "loss trace unknown field", ("set", ("loss_trace", "extra"), 1),
     "unknown_field", "loss_trace.extra"),
    ("M34", "relative loss trace path", ("set", ("loss_trace", "path"),
                                          "relative/loss.json"),
     "invalid_path", "loss_trace.path"),
    ("M35", "bad loss trace hash", ("set", ("loss_trace", "sha256"), "x" * 64),
     "invalid_value", "loss_trace.sha256"),
    ("M36", "empty intervals", ("set", ("loss_trace", "intervals"), []),
     "invalid_value", "loss_trace.intervals"),
    ("M37", "intervals not list", ("set", ("loss_trace", "intervals"), {}),
     "invalid_value", "loss_trace.intervals"),
    ("M38", "interval missing field",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": 0}]),
     "missing_field", "loss_trace.intervals[0].sample_count"),
    ("M39", "interval unknown field",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": 0, "sample_count": 1, "extra": 1}]),
     "unknown_field", "loss_trace.intervals[0].extra"),
    ("M40", "negative interval start",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": -1, "sample_count": 1}]),
     "invalid_value", "loss_trace.intervals[0].first_sample"),
    ("M41", "zero interval count",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": 0, "sample_count": 0}]),
     "invalid_value", "loss_trace.intervals[0].sample_count"),
    ("M42", "bool interval count",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": 0, "sample_count": True}]),
     "invalid_value", "loss_trace.intervals[0].sample_count"),
    ("M43", "overlapping intervals",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": 100, "sample_count": 100},
       {"first_sample": 150, "sample_count": 10}]),
     "invalid_value", "loss_trace.intervals.order"),
    ("M44", "clean missing field",
     ("delete", ("clean_reference", "alignment")),
     "missing_field", "clean_reference.alignment"),
    ("M45", "clean unknown field",
     ("set", ("clean_reference", "extra"), 1),
     "unknown_field", "clean_reference.extra"),
    ("M46", "relative clean path", ("set", ("clean_reference", "path"),
                                     "relative/clean.wav"),
     "invalid_path", "clean_reference.path"),
    ("M47", "bad clean hash", ("set", ("clean_reference", "sha256"), "x" * 64),
     "invalid_value", "clean_reference.sha256"),
    ("M48", "bad alignment", ("set", ("clean_reference", "alignment"), "guess"),
     "invalid_value", "clean_reference.alignment"),
    ("M49", "sample_exact nonzero offset",
     ("set", ("clean_reference", "offset_samples"), 5),
     "invalid_value", "clean_reference.offset_samples"),
    ("M50", "negative clean offset",
     ("set", ("clean_reference", "offset_samples"), -1),
     "invalid_value", "clean_reference.offset_samples"),
    ("M51", "score missing field", ("delete", ("score_protocol", "baseline")),
     "missing_field", "score_protocol.baseline"),
    ("M52", "score unknown field", ("set", ("score_protocol", "extra"), 1),
     "unknown_field", "score_protocol.extra"),
    ("M53", "empty metrics", ("set", ("score_protocol", "metrics"), []),
     "invalid_value", "score_protocol.metrics"),
    ("M54", "duplicate metrics",
     ("set", ("score_protocol", "metrics"), ["stoi", "stoi"]),
     "invalid_value", "score_protocol.metrics"),
    ("M55", "unknown metric",
     ("set", ("score_protocol", "metrics"), ["mos", "stoi"]),
     "invalid_value", "score_protocol.metrics"),
    ("M56", "missing SI-SDR metric",
     ("set", ("score_protocol", "metrics"), ["stoi"]),
     "invalid_value", "score_protocol.metrics"),
    ("M57", "unknown baseline", ("set", ("score_protocol", "baseline"),
                                  "identity"),
     "invalid_value", "score_protocol.baseline"),
    ("M58", "unpaired reference",
     ("set", ("score_protocol", "paired_clean_reference"), False),
     "invalid_value", "score_protocol.paired_clean_reference"),
    ("M59", "minimum items zero", ("set", ("score_protocol", "minimum_items"),
                                   0),
     "invalid_value", "score_protocol.minimum_items"),
    ("M60", "minimum items over bound",
     ("set", ("score_protocol", "minimum_items"), MAX_MINIMUM_ITEMS + 1),
     "invalid_value", "score_protocol.minimum_items"),
    ("M61", "minimum items bool",
     ("set", ("score_protocol", "minimum_items"), True),
     "invalid_value", "score_protocol.minimum_items"),
    ("M62", "nonfinite interval count",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": 0, "sample_count": float("inf")}]),
     "nonfinite_value", "loss_trace.intervals[0].sample_count"),
    ("M63", "nonfinite model bytes",
     ("set", ("model", "model_bytes"), float("nan")),
     "nonfinite_value", "model.model_bytes"),
    ("M64", "nonfinite delay",
     ("set", ("geometry", "expected_delay_samples"), float("-inf")),
     "nonfinite_value", "geometry.expected_delay_samples"),
    ("M65", "nonfinite score",
     ("set", ("score_protocol", "minimum_items"), float("nan")),
     "nonfinite_value", "score_protocol.minimum_items"),
    ("M66", "bool interval start",
     ("set", ("loss_trace", "intervals"),
      [{"first_sample": True, "sample_count": 1}]),
     "invalid_value", "loss_trace.intervals[0].first_sample"),
    ("M67", "metrics not list",
     ("set", ("score_protocol", "metrics"), "si_sdr"),
     "invalid_value", "score_protocol.metrics"),
    ("M68", "empty baseline",
     ("set", ("score_protocol", "baseline"), ""),
     "invalid_value", "score_protocol.baseline"),
    ("M69", "model path traversal",
     ("set", ("model", "model_path"), "/caller/../model.pt"),
     "invalid_path", "model.model_path"),
    ("M70", "cohort id whitespace",
     ("set", ("cohort_id",), "bad id"),
     "invalid_value", "cohort_id"),
    ("M71", "geometry not object",
     ("set", ("geometry",), []),
     "invalid_object", "geometry"),
    ("M72", "model not object",
     ("set", ("model",), []),
     "invalid_object", "model"),
    ("M73", "loss trace not object",
     ("set", ("loss_trace",), []),
     "invalid_object", "loss_trace"),
    ("M74", "clean reference not object",
     ("set", ("clean_reference",), []),
     "invalid_object", "clean_reference"),
    ("M75", "score protocol not object",
     ("set", ("score_protocol",), []),
     "invalid_object", "score_protocol"),
)


def _apply(case: tuple, document: dict | None) -> dict | None:
    if document is None:
        return None
    definition = case[2]
    if definition is None:
        return document
    kind = definition[0]
    if kind == "set":
        _set(definition[1], definition[2])(document)
    elif kind == "delete":
        _delete(definition[1])(document)
    return document


def admission_controls() -> dict:
    """Validate every adverse control; one schema-only control is admitted."""
    cases: list[dict] = []
    for case in CASE_DEFINITIONS:
        case_id, description, definition, expected_code, expected_field = case
        document = None if definition is None else _manifest_control()
        document = _apply(case, document)
        result = validate_manifest(document, probe_paths=False)
        if (result["accepted"] or result["code"] != expected_code
                or result["field"] != expected_field):
            raise ValueError(
                "admission_control_mismatch:" + case_id + ":" +
                result["code"] + ":" + result["field"])
        cases.append({
            "id": case_id,
            "description": description,
            "status": "rejected",
            "code": result["code"],
            "field": result["field"],
            "expected_code": expected_code,
            "expected_field": expected_field,
            "state_unchanged": True,
            "qualifies": False,
        })
    control = validate_manifest(_manifest_control(), probe_paths=False)
    if not control["accepted"]:
        raise ValueError("schema_control_rejected:" + control["code"])
    return {
        "cases": cases,
        "controls": [{
            "id": "C01",
            "description": (
                "Structural schema control with synthetic, nonexistent paths "
                "and placeholder digests."),
            "status": "accepted_schema_control",
            "evidence_class": "synthetic_schema_control_not_evidence",
            "checks": control["checks"],
            "probe_paths": False,
            "qualifies": False,
        }],
    }


# --------------------------------------------------------------------------
# Canonical contract and report
# --------------------------------------------------------------------------
def _artifact_rows() -> list[dict]:
    return [{
        "id": artifact["id"],
        "kind": artifact["kind"],
        "requirement": artifact["requirement"],
        "present": False,
        "verified": False,
        "sha256": None,
        "blocked": True,
    } for artifact in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict]:
    return [{
        "id": blocker["id"],
        "artifact_id": blocker["artifact_id"],
        "statement": blocker["statement"],
        "required_action": blocker["required_action"],
        "linked_gates": list(blocker["linked_gates"]),
        "status": "open",
        "qualifies": False,
    } for blocker in EXACT_BLOCKERS]


def _gate_rows() -> list[dict]:
    identity = {"task_id": TASK, "component_id": COMPONENT_ID, "mode": MODE}
    return [{
        "id": gate["id"],
        "title": gate["title"],
        "statement": gate["statement"],
        "reopen_condition": gate["reopen_condition"],
        "status": "blocked",
        "qualifies": False,
        "linked_row": identity,
    } for gate in RELEASE_GATES]


def linked_row_identity() -> dict:
    projection = {field: BOARD_ROW_PROJECTION[field]
                  for field in BOARD_ROW_FIELDS}
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "selector": "stable-row-identity/0.1:" + ",".join(BOARD_ROW_FIELDS),
        "gating": "stable_identity_only",
        "mutable_fields_excluded": ["status", "owner", "claim", "review",
                                    "handoff", "blocked_reason",
                                    "dispatch_priority"],
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
    }


# --------------------------------------------------------------------------
# Task-local git scope
# --------------------------------------------------------------------------
# The merged squash lands on `main`; later merges add unrelated sibling task
# packages. A fixed historical commit therefore cannot be the scope base: it
# would report those siblings as out-of-scope edits of this task. The base is
# the newest merge-base between HEAD and the PR base refs, so the comparison
# contains exactly the commits this branch added and fail-closed scope checks
# still catch any edit outside TASK_PREFIX.
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


def qualification_block() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "real_source_present": False,
        "real_model_present": False,
        "real_runtime_present": False,
        "real_model_geometry_verified": False,
        "exact_variant_pinned": False,
        "real_packetized_cohort_present": False,
        "real_packet_loss_cohort_present": False,
        "real_loss_trace_present": False,
        "real_clean_baseline_present": False,
        "real_result_present": False,
        "source_reported_claims_reproduced": False,
        "candidate_implementation_result": False,
        "packet_loss_result": False,
        "quality_result": False,
        "preservation_result": False,
        "listening_result": False,
        "output_peak_bound": False,
        "invalid_output_result": False,
        "delay_result": False,
        "state_or_memory_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def disposition_block() -> dict:
    return {
        "status": "incomplete",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "promotion": "defer",
        "production_exposure": "DEFER",
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "installed_v0_behavior_change": False,
        "processor_exposure": False,
        "task_local_only": True,
        "files_outside_task_directory_written": False,
    }


def scope_block() -> dict:
    return {
        "source_present": False,
        "model_present": False,
        "runtime_present": False,
        "runtime_executed": False,
        "model_asset_present": False,
        "real_corpus": False,
        "real_packet_trace": False,
        "encoded_bitstream_present": False,
        "explicit_loss_intervals_present": False,
        "audio_read": False,
        "codec_invoked": False,
        "decoder_executed": False,
        "model_inference_performed": False,
        "packet_loss_simulated": False,
        "quality_scored": False,
        "listening": False,
        "device_timing": False,
        "output_peak_bound": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "single_component": COMPONENT_ID,
        "provider_work": False,
        "runtime_work": False,
        "release_work": False,
        "write_scope": WRITE_SCOPE,
    }


def profile_source_block() -> dict:
    return {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "row": "Enhancement",
        "phrases": list(PROFILE_PHRASES),
    }


def admission_contract_block() -> dict:
    return {
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "model_fields": list(MODEL_FIELDS),
        "geometry_fields": list(GEOMETRY_FIELDS),
        "loss_trace_fields": list(LOSS_TRACE_FIELDS),
        "interval_fields": list(INTERVAL_FIELDS),
        "clean_reference_fields": list(CLEAN_REFERENCE_FIELDS),
        "score_protocol_fields": list(SCORE_PROTOCOL_FIELDS),
        "rights_decisions": list(RIGHTS_DECISIONS),
        "alignments": list(ALIGNMENTS),
        "baselines": list(BASELINES),
        "metrics": list(METRICS),
        "sdk_sample_rate_hz": SDK_SAMPLE_RATE,
        "sdk_channels": SDK_CHANNELS,
        "sdk_frame_samples": SDK_FRAME_SAMPLES,
        "frame_samples_bounds": [1, MAX_FRAME_SAMPLES],
        "packet_samples_bounds": [1, MAX_PACKET_SAMPLES],
        "expected_delay_samples_bounds": [0, MAX_DELAY_SAMPLES],
        "model_bytes_bounds": [1, MAX_MODEL_BYTES],
        "minimum_items_bounds": [1, MAX_MINIMUM_ITEMS],
        "max_intervals": MAX_INTERVALS,
        "loss_representation": "explicit_packet_loss_intervals",
        "codec_packets_required": True,
        "waveform_proxy_is_not_codec_plc": True,
        "inferred_loss_allowed": False,
        "audio_read": False,
        "runtime_invoked": False,
        "model_inference_performed": False,
        "packet_loss_simulated": False,
        "replay_performed": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "admission_contract": admission_contract_block(),
        "explicit_loss_policy": dict(EXPLICIT_LOSS_POLICY),
        "candidate_identity": dict(CANDIDATE_IDENTITY),
        "source_reported_claims": dict(SOURCE_REPORTED_CLAIMS),
        "enhancement_profile_requirements": [dict(row)
                                             for row in
                                             ENHANCEMENT_PROFILE_ROWS],
        "measurement_requirements": [dict(row) for row in MEASUREMENT_ROWS],
        "profile_source": profile_source_block(),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    contract = read_strict_json(HERE / "contract.json")
    probes = absence_probes(AUDIO_ROOT)
    controls = admission_controls()
    rejected = [case for case in controls["cases"]
                if case["status"] == "rejected"]
    accepted_controls = [case for case in controls["controls"]
                         if case["status"] == "accepted_schema_control"]
    gates = _gate_rows()
    artifacts = _artifact_rows()
    blockers = _blocker_rows()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "task_id": TASK,
        "task_title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "decision": "DEFER",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "observed_unqualified_binaries": [],
            "conclusion": (
                "No Google Lyra source, codec, model, TFLite bundle, "
                "inference runtime, encoded packet stream, packet-loss "
                "cohort, clean baseline or vendor result exists at any fixed "
                "probe location. The pinned candidate matrix already marks "
                "the candidate unavailable/blocked, and the exact Lyra II "
                "versus V2 variant is not pinned locally."),
        },
        "candidate_identity": dict(CANDIDATE_IDENTITY),
        "source_reported_claims": dict(SOURCE_REPORTED_CLAIMS),
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "enhancement_profile": {
            "profile": PROFILE,
            "rows": [dict(row) for row in ENHANCEMENT_PROFILE_ROWS],
            "identity_or_noisy_control": False,
            "task_matched_baseline": False,
            "paired_si_sdr": False,
            "paired_stoi": False,
            "clean_speech_preservation": False,
            "output_peak_bounds": False,
            "invalid_output_accounting": False,
            "unpaired_predictive_screen_or_listening": False,
            "alignment_and_content_delay": False,
            "state_and_memory": False,
            "target_runtime_timing": False,
            "status": "blocked",
        },
        "measurements": {
            "rows": [dict(row) for row in MEASUREMENT_ROWS],
            "source_and_model_identity_measured": False,
            "explicit_loss_intervals_measured": False,
            "paired_quality_measured": False,
            "preservation_measured": False,
            "peak_and_invalid_outputs_measured": False,
            "alignment_delay_measured": False,
            "state_memory_timing_measured": False,
            "listening_or_screen_measured": False,
            "status": "blocked",
        },
        "explicit_loss_policy": dict(EXPLICIT_LOSS_POLICY),
        "required_results": {
            "source_and_model_result": False,
            "explicit_loss_interval_result": False,
            "packet_loss_concealment_result": False,
            "paired_si_sdr_and_stoi_result": False,
            "clean_speech_preservation_result": False,
            "output_peak_bound": False,
            "invalid_output_accounting": False,
            "task_matched_baseline_result": False,
            "independent_listening_or_screen": False,
            "alignment_and_content_delay_measured": False,
            "state_memory_and_runtime_timing": False,
            "decoder_state_reset_policy_result": False,
            "source_reported_claim_reproduced": False,
            "no_result_qualifies": True,
        },
        "admission": {
            "policy": "task_local_fail_closed_admission_not_runtime_behavior",
            "cases": controls["cases"],
            "schema_controls": controls["controls"],
            "summary": {
                "case_count": len(controls["cases"]),
                "rejected_count": len(rejected),
                "accepted_schema_controls": len(accepted_controls),
                "qualifying_results": 0,
                "state_advanced_on_rejection": any(
                    case["state_unchanged"] is not True for case in rejected),
                "runtime_invoked": False,
                "audio_read": False,
                "model_inference_performed": False,
                "packet_loss_simulated": False,
            },
        },
        "qualification": qualification_block(),
        "prohibited_claims": list(NON_CLAIMS),
        "gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "linked_row_identity": linked_row_identity(),
        "profile_source": profile_source_block(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": {
            "runs": 3,
            "byte_identical": True,
            "cold_start_processes": True,
            "canonical_json": True,
            "sorted_keys": True,
            "compact_separators": True,
            "trailing_newline": True,
        },
        "reproduction": {
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                      "test_reference.py"),
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract.get("profile") != PROFILE or contract.get("mode") != MODE:
        raise ValueError("contract_profile_or_mode")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_commit")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch")
    if contract.get("reviewer") != REVIEWER:
        raise ValueError("contract_reviewer")
    if contract.get("worktree") != CLAIM_WORKTREE:
        raise ValueError("contract_worktree")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked"
           for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    if contract.get("board_row_sha256") != board_row_digest(
            BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_row_digest")
    if contract.get("linked_rows") != [dict(row) for row in LINKED_ROWS]:
        raise ValueError("contract_linked_rows")
    if contract.get("candidate_identity") != CANDIDATE_IDENTITY:
        raise ValueError("contract_candidate_identity")
    if contract["candidate_identity"].get("exact_variant_pinned") is not False:
        raise ValueError("contract_variant_pinned")
    if contract.get("source_reported_claims") != SOURCE_REPORTED_CLAIMS:
        raise ValueError("contract_source_reported_claims")
    if contract["source_reported_claims"].get("qualifies_candidate") is not False:
        raise ValueError("contract_source_claim_qualifies")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
