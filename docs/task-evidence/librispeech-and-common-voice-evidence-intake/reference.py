# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence intake for LibriSpeech and Common Voice.

This module is a fail-closed intake gate, not a corpus, manifest, scorer or
candidate. A bounded read-only search finds no LibriSpeech ``test-clean``
archive, no extracted LibriSpeech tree, no Common Voice release, no prepared
manifest for either dataset and no written dataset-scoped rights decision. The
pinned notes record the exact upstream identities and the unresolved rights and
overlap conditions.

The module therefore builds an honest blocker package:

* strict caller-supplied intake-declaration validation at a synthetic
  structural boundary only;
* explicit LibriSpeech and Common Voice presence, manifest, rights and
  overlap probes;
* an admission gate with no admitting branch, so every valid request is
  ``DEFER`` and no missing result can qualify;
* a synthetic structural control that is not corpus evidence;
* stable linked-row identity projection only, never a hash of the mutable full
  ``plan/swarm/TASKS.json``.

No archive is downloaded, extracted, opened, decoded, hashed or copied. No
manifest is fabricated. No dataset, model, scorer, cohort, listening panel,
device measurement, benchmark or release claim is produced.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = (
    "audio-sdk/librispeech-and-common-voice-evidence-intake-"
    "reference-report/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/librispeech-and-common-voice-evidence-intake-contract/0.1")
REQUEST_SCHEMA_ID = "audio-sdk/dataset-intake-request/0.1"
TASK = "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE"
COMPONENT = "librispeech-and-common-voice-evidence-intake"
BRANCH = "swarm/SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE"
BASE_COMMIT = "b4960fdba1991a35c07ff7f22cda5257c4749768"
TASK_PREFIX = "docs/task-evidence/librispeech-and-common-voice-evidence-intake/"
MODE = "research-control"
VERIFICATION_PROFILE = "evidence"
REPOSITORY = "audio-sdk"
TITLE = "LibriSpeech and Common Voice evidence intake"

COMPARISON_STATUS = "blocked_exact_licensed_data_and_manifests_absent"
DEFER_BEFORE = "optional_evidence_adapter_exposure"

# Reported facts are retained from pinned notes. They are source-reported, not
# locally verified, and every local identity field below is null.
LIBRISPEECH_CORPUS_ID = "librispeech_test_clean"
COMMON_VOICE_CORPUS_ID = "common_voice_spontaneous_speech_5_0_english"

LIBRISPEECH_REPORTED_MD5 = "32fa31d27d2e1cad72775fee3f4849a9"

LIBRISPEECH = {
    "corpus_id": LIBRISPEECH_CORPUS_ID,
    "name": "LibriSpeech test-clean",
    "source": "OpenSLR SLR12",
    "source_url": "https://www.openslr.org/12/",
    "checksum_list_url": "https://openslr.trmal.net/resources/12/md5sum.txt",
    "subset": "test-clean",
    "source_revision": "openslr-slr12-test-clean",
    "archive_filename": "test-clean.tar.gz",
    "reported_archive_md5": LIBRISPEECH_REPORTED_MD5,
    "reported_license": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/legalcode.en",
    "reported_native_sample_rate_hz": 16000,
    "reported_media": "FLAC",
    "derived_from": "LibriVox audiobooks",
    "reported_transcript_backed": True,
    "reported_candidate_scope": (
        "transcript-backed speaker-split-eligible pool before limits"),
    "reported_not_verified": True,
}

COMMON_VOICE = {
    "corpus_id": COMMON_VOICE_CORPUS_ID,
    "name": "Common Voice Spontaneous Speech 5.0 English",
    "source": "Mozilla Data Collective",
    "source_url": (
        "https://mozilladatacollective.com/datasets/"
        "cmu5nqn1h00vwmi07b4dbk085"),
    "terms_url": "https://mozilladatacollective.com/terms/consumers",
    "dataset_id": "cmu5nqn1h00vwmi07b4dbk085",
    "release": "sps-corpus-5.0-2026-09-11",
    "subset": "en-5.0",
    "source_revision": "sps-corpus-5.0-2026-09-11",
    "archive_filename": None,
    "reported_archive_size": "519.05 MB",
    "reported_clips": 5898,
    "reported_speakers": 642,
    "reported_recorded_hours": 18.6,
    "reported_validated_hours": 8.39,
    "reported_media": "MP3",
    "reported_license": "CC0-1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "reported_intended_uses": [
        "ASR training or evaluation",
        "CALL",
        "language or heritage revitalization",
    ],
    "reported_forbidden_uses": [
        "speaker identification",
        "re-hosting or re-sharing",
    ],
    "native_sample_rate_hz_recorded": False,
    "native_sample_rate_hz": None,
    "reported_not_verified": True,
}

CORPORA = {
    LIBRISPEECH_CORPUS_ID: LIBRISPEECH,
    COMMON_VOICE_CORPUS_ID: COMMON_VOICE,
}

MODEL_IDS = ("speexdsp", "dpdfnet", "other_learned")
OVERLAP_STATUSES = (
    "not_reviewed",
    "exact_overlap_excluded",
    "not_applicable_no_training_corpus",
)

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    "realtime-audio-library/implementation_record.md":
        "12b7c17d6ae969cb3e9697f3309667518048f27792b283178d326746e1bbfb81",
    "realtime-audio-library/research/"
    "holdout_speech_source_assessment_20261028.md":
        "a3802ae6ebee5d1ddb1e41154ca2de01c338445fcf6561d7a223663dd3741450",
    "realtime-audio-library/docs/evaluation_plan.md":
        "56f03609e57d3e95c8d1a9ae75a44d345b77e3c476da26a60770b7718f90c2f6",
    "realtime-audio-library/docs/rights_clearance_inventory.md":
        "de540032406b5ca50803d52ba7cf1630a1eb8dcdf8d050e4f351cabbadc29818",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": TITLE,
    "mode": MODE,
    "repository": REPOSITORY,
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

SELF_PIN_FILES = (
    "README.md",
    "reference.py",
    "run.py",
    "test_reference.py",
    "verify.py",
)

# Bounded, read-only candidate paths. Absolute paths are the documented local
# preparation examples; no other filesystem location is searched.
LIBRISPEECH_ARCHIVE_PATHS = (
    "data/corpora/librispeech/test-clean.tar.gz",
    "data/corpora/librispeech-test-clean/test-clean.tar.gz",
    "data/librispeech/test-clean.tar.gz",
    "data/datasets/librispeech/test-clean.tar.gz",
    "/private/tmp/test-clean.tar.gz",
)
LIBRISPEECH_TREE_PATHS = (
    "data/corpora/librispeech/LibriSpeech/test-clean",
    "data/corpora/librispeech-test-clean/LibriSpeech/test-clean",
    "data/librispeech/LibriSpeech/test-clean",
    "data/datasets/librispeech/LibriSpeech/test-clean",
    "/private/tmp/librispeech-source/LibriSpeech/test-clean",
)
LIBRISPEECH_MANIFEST_PATHS = (
    "data/manifests/librispeech-test-clean.json",
    "data/corpora/librispeech/manifest.json",
    "data/corpora/librispeech-test-clean/manifest.json",
    "/private/tmp/audioml-librispeech-test-clean-16k-pink-5db/manifest.json",
)

COMMON_VOICE_ARCHIVE_PATHS = (
    "data/corpora/common-voice/sps-corpus-5.0-2026-09-11.tar.gz",
    "data/corpora/common-voice-spontaneous-speech-5.0-en/"
    "sps-corpus-5.0-2026-09-11.tar.gz",
    "data/datasets/common-voice/sps-corpus-5.0-2026-09-11.tar.gz",
)
COMMON_VOICE_METADATA_PATHS = (
    "data/corpora/common-voice/metadata.tsv",
    "data/corpora/common-voice/validated.tsv",
    "data/corpora/common-voice-spontaneous-speech-5.0-en/metadata.tsv",
    "data/corpora/common-voice-spontaneous-speech-5.0-en/validated.tsv",
    "data/datasets/common-voice/metadata.tsv",
)
COMMON_VOICE_MANIFEST_PATHS = (
    "data/manifests/common-voice-spontaneous-speech-5.0-en.json",
    "data/corpora/common-voice/manifest.json",
    "data/corpora/common-voice-spontaneous-speech-5.0-en/manifest.json",
    "/private/tmp/audioml-cv5-holdout-16k-pink-5db/manifest.json",
)

REQUEST_KEYS = frozenset({
    "schema_id", "corpus_id", "subset", "source_revision", "archive",
    "manifest", "rights", "model",
})
ARCHIVE_KEYS = frozenset({
    "filename", "checksum_kind", "checksum", "byte_count", "present",
})
MANIFEST_KEYS = frozenset({
    "present", "sha256", "item_count", "duration_seconds", "transcript_bound",
    "speaker_disjoint", "hashed_speaker_ids_only", "split_version",
})
RIGHTS_KEYS = frozenset({
    "listed_license", "license_text_present", "license_text_sha256",
    "download_terms_reviewed", "use_approved", "retention_approved",
    "redistribution_approved", "derived_output_approved",
    "listening_approved", "speaker_identification_forbidden_ack",
    "no_rehosting_ack", "attribution_recorded",
})
MODEL_KEYS = frozenset({
    "id", "overlap_status", "overlap_audit_sha256",
})

MD5_RE = re.compile(r"^[0-9a-f]{32}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SPLIT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "LibriSpeech test-clean archive and license identity",
        "required": (
            "The official OpenSLR SLR12 test-clean.tar.gz whose MD5 is "
            "32fa31d27d2e1cad72775fee3f4849a9, with the byte-identical "
            "CC BY 4.0 license text, attribution record and archive SHA-256"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "LibriSpeech prepared manifest",
        "required": (
            "A prepared manifest that binds consumed FLAC and transcript bytes "
            "to the verified archive, records the transcript-backed candidate "
            "scope before limits, and freezes a speaker-disjoint split from "
            "hashed speaker identifiers"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "Common Voice exact release and download-time license",
        "required": (
            "The exact Mozilla Data Collective English Spontaneous Speech 5.0 "
            "release sps-corpus-5.0-2026-09-11 for dataset "
            "cmu5nqn1h00vwmi07b4dbk085 with an archive checksum and the "
            "download-time Data Consumer License text and acceptance record"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "Common Voice prepared manifest and split",
        "required": (
            "A prepared manifest that binds audio and metadata to the exact "
            "release, groups speakers only by hashed client_id, freezes a "
            "speaker-disjoint reserved split and records no real identities"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "dataset-scoped rights decision",
        "required": (
            "A written decision per dataset permitting the exact use, "
            "retention, evaluation, listening and any redistribution or "
            "derived-output scope, including LibriSpeech attribution and "
            "privacy/publicity review and Common Voice no-identification and "
            "no-rehosting terms"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "model-overlap audit",
        "required": (
            "An exact per-model, per-dataset overlap audit: the LibriVox / MLS "
            "risk for DPDFNet and LibriSpeech, independent Common Voice "
            "training-overlap review for every learned candidate, and the "
            "explicit no-training-corpus finding for SpeexDSP"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A7",
        "artifact": "frozen cohort, scorer and controls",
        "required": (
            "A frozen rights-cleared matched cohort with an untouched holdout, "
            "a pinned scorer and aggregation, a failed-item policy, paired / "
            "unpaired / synthetic / human / source-reported separation, and "
            "one invalid/missing plus one representative valid result through "
            "the reported bundle"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A8",
        "artifact": "optional adapter, review and release package",
        "required": (
            "An explicit opt-in evidence-adapter decision, benchmark "
            "validation, authorized listening where permitted, independent "
            "exact-head review and release approval"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
)

GATES = (
    {
        "id": "RG-01",
        "gate": "librispeech_archive_and_license_identity",
        "status": "blocked",
        "reason": (
            "No LibriSpeech test-clean archive or extracted tree exists at "
            "any bounded candidate path; the official OpenSLR SLR12 MD5 "
            "32fa31d27d2e1cad72775fee3f4849a9 is recorded but no local byte "
            "was hashed. No CC BY 4.0 license text or attribution record is "
            "staged."),
        "reopen": (
            "Stage the official test-clean.tar.gz, verify the exact OpenSLR "
            "MD5 and a recorded SHA-256, pin the CC BY 4.0 license text and "
            "attribution, and record the exact archive provenance before "
            "reading any audio."),
    },
    {
        "id": "RG-02",
        "gate": "librispeech_manifest_and_speaker_split",
        "status": "blocked",
        "reason": (
            "No LibriSpeech prepared manifest exists, so no consumed FLAC and "
            "transcript bytes are archive-bound, no candidate-count scope is "
            "recorded, and no speaker-disjoint reserved split is frozen."),
        "reopen": (
            "Produce the prepared manifest from verified archive bytes, bind "
            "every consumed FLAC and transcript snapshot, record the "
            "transcript-backed candidate scope before limits, and freeze a "
            "speaker-disjoint split with hashed speaker identifiers only."),
    },
    {
        "id": "RG-03",
        "gate": "common_voice_archive_and_download_license",
        "status": "blocked",
        "reason": (
            "No Common Voice release archive, extracted release or metadata "
            "exists locally. The MDC listing is reported as CC0-1.0, but the "
            "download-time Data Consumer License was not inspected or "
            "accepted and its scope for speech enhancement is unresolved."),
        "reopen": (
            "Obtain the exact sps-corpus-5.0-2026-09-11 release for dataset "
            "cmu5nqn1h00vwmi07b4dbk085, record its archive checksum, preserve "
            "the byte-identical download-time license and terms, and record a "
            "written scope decision that covers this intended use."),
    },
    {
        "id": "RG-04",
        "gate": "common_voice_manifest_and_hashed_split",
        "status": "blocked",
        "reason": (
            "No Common Voice prepared manifest exists, no audio or metadata "
            "bytes are bound to the exact release, and no speaker-disjoint "
            "reserved split from hashed client_id values is verified."),
        "reopen": (
            "Produce and pin the prepared manifest from verified release "
            "bytes, verify the speaker grouping from hashed client_id values "
            "only, reserve the held-out group before processing and record "
            "the split version without exposing real identities."),
    },
    {
        "id": "RG-05",
        "gate": "dataset_scoped_rights_decision",
        "status": "blocked",
        "reason": (
            "No written per-dataset rights record exists. LibriSpeech has only "
            "the reported CC BY 4.0 label with privacy/publicity and intended "
            "use unreviewed; Common Voice has only a CC0-1.0 listing whose "
            "download-time MDC license and enhancement scope are not accepted."),
        "reopen": (
            "Record separate LibriSpeech and Common Voice decisions for use, "
            "retention, evaluation, listening, redistribution and derived "
            "outputs, including attribution and privacy/publicity for "
            "LibriSpeech and no-identification / no-rehosting for Common "
            "Voice. Do not pool the decisions."),
    },
    {
        "id": "RG-06",
        "gate": "per_model_dataset_overlap_audit",
        "status": "blocked",
        "reason": (
            "No exact overlap audit exists. LibriSpeech and MLS are both "
            "reported as derived from LibriVox and DPDFNet is reported trained "
            "on 4,000 hours of MLS; this is a risk, not proof of exact "
            "recording or speaker overlap. Common Voice learned-model overlap "
            "is also unreviewed; only SpeexDSP has no training corpus."),
        "reopen": (
            "Audit each model against each dataset separately: establish "
            "exact file-level exclusion for DPDFNet and LibriSpeech, record "
            "any recording or speaker overlap, review Common Voice training "
            "overlap for every learned candidate, and retain SpeexDSP's "
            "no-training-corpus finding with the rights gate still separate."),
    },
    {
        "id": "RG-07",
        "gate": "frozen_cohort_scorer_and_representative_result",
        "status": "blocked",
        "reason": (
            "No frozen matched cohort, pinned scorer, aggregation, failed-item "
            "policy, control result or representative valid result exists. "
            "Only local structural rejections and the live missing-artifact "
            "control are recorded."),
        "reopen": (
            "Freeze a rights-cleared matched cohort and untouched holdout, pin "
            "the scorer and aggregation, define failed-item handling, preserve "
            "paired / unpaired / synthetic / human / source-reported "
            "separation, and validate one invalid/missing and one "
            "representative valid result through the reported bundle."),
    },
    {
        "id": "RG-08",
        "gate": "optional_adapter_review_and_release",
        "status": "blocked",
        "reason": (
            "No opt-in evidence adapter, benchmark validation, authorized "
            "listening, independent exact-head review or release approval "
            "exists. There is no provider, registry, default, shared-build, "
            "CI or installed-v0 change."),
        "reopen": (
            "Complete RG-01 through RG-07, record an explicit opt-in adapter "
            "decision with no default registration or fallback, validate a "
            "benchmark bundle, run authorized listening where permitted, and "
            "obtain independent exact-head review and release approval."),
    },
)

BLOCKER = {
    "status": COMPARISON_STATUS,
    "defer_before": DEFER_BEFORE,
    "artifact": (
        "LibriSpeech test-clean archive, prepared manifest and rights record; "
        "Common Voice exact release archive, prepared manifest, download-time "
        "license and rights record; per-model overlap audit; frozen cohort, "
        "scorer, aggregation and representative result"),
    "librispeech": {
        "status": "absent",
        "archive_present": False,
        "source_tree_present": False,
        "prepared_manifest_present": False,
        "archive_md5": None,
        "archive_sha256": None,
        "archive_byte_count": None,
        "manifest_sha256": None,
        "item_count": None,
        "duration_seconds": None,
        "speaker_split_verified": False,
        "license_text_present": False,
        "license_text_sha256": None,
        "rights_approved": False,
    },
    "common_voice": {
        "status": "absent",
        "archive_present": False,
        "source_metadata_present": False,
        "prepared_manifest_present": False,
        "archive_sha256": None,
        "archive_byte_count": None,
        "manifest_sha256": None,
        "item_count": None,
        "duration_seconds": None,
        "speaker_split_verified": False,
        "download_terms_reviewed": False,
        "license_text_present": False,
        "license_text_sha256": None,
        "rights_approved": False,
    },
    "litigation_safe": True,
    "no_fabricated_identity": True,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "A dataset-specific written decision is required for use, retention, "
        "evaluation, listening, redistribution and derived outputs; the exact "
        "license text and acceptance record must be preserved; LibriSpeech "
        "attribution and privacy/publicity must be reviewed; Common Voice "
        "must honour no speaker identification and no re-hosting or "
        "re-sharing; no audio or derivative may be published without an "
        "explicit grant."),
    "workspace_search": (
        "Bounded read-only existence checks of documented workspace and local "
        "preparation paths found no LibriSpeech test-clean archive, extracted "
        "tree or manifest and no Common Voice release archive, metadata or "
        "manifest. No archive, audio byte, transcript or metadata file was "
        "opened, hashed, decoded, downloaded, extracted or copied."),
    "not_attempted": [
        "no archive download, clone, extraction, transcoding or copy",
        "no audio, transcript or metadata file opened, hashed or decoded",
        "no fabricated archive checksum, byte count, manifest, item count or duration",
        "no fabricated license text, terms acceptance or rights decision",
        "no speaker identity inference, speaker-disjoint claim or split verification",
        "no model, scorer, cohort, mixture, listening, device-timing or benchmark run",
        "no result promoted from a missing, invalid or source-reported case",
    ],
    "reopen": (
        "Stage and verify the exact LibriSpeech test-clean archive and its "
        "prepared manifest; obtain and verify the exact Common Voice release, "
        "download-time license and prepared manifest; record separate "
        "dataset-scoped rights decisions; complete per-model overlap audits; "
        "freeze a rights-cleared matched cohort with an untouched holdout; pin "
        "the scorer, aggregation and failed-item policy; validate an "
        "invalid/missing and a representative valid result; then record an "
        "opt-in adapter decision and obtain independent review."),
}

NON_CLAIMS = (
    "No LibriSpeech or Common Voice archive, audio byte, transcript, metadata file or manifest is downloaded, copied, opened, hashed or decoded.",
    "No archive checksum, byte count, item count, duration, speaker split or manifest identity is fabricated.",
    "No license text, download-time acceptance or written rights decision exists for either dataset.",
    "No dataset is cleared for enhancement evaluation, retention, redistribution, derived outputs or listening.",
    "No dataset, model, scorer, cohort, mixture, listening panel, device measurement, benchmark or release result is produced.",
    "No DPDFNet, MLS or LibriVox overlap is claimed established or excluded; the risk is recorded only.",
    "No Common Voice speaker identity is inferred and no unhashed client_id is used.",
    "No installed v0, public API, C ABI, descriptor, registry, default, shared build or CI change exists.",
    "No provider is registered or enabled by default and there is no automatic discovery or fallback.",
    "No missing, rejected, source-reported or structural-control result qualifies either dataset.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/librispeech-and-common-voice-evidence-intake/ is touched.",
    "The reference is a task-local dataset-intake gate, not a corpus or manifest.",
    "LibriSpeech and Common Voice identities, scopes, terms and gaps stay distinct.",
    "All local controls are analytic structural checks; no corpus byte is read.",
    "Missing, invalid, nonfinite, inconsistent and out-of-scope declarations fail closed.",
    "Source-reported facts remain source-reported and never become local measurements.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

SOURCE_EVIDENCE_STATEMENTS = (
    "realtime-audio-library/implementation_record.md records that LibriSpeech test-clean preparation exists only as a tool path: the archive was absent locally and the 2026-10-29 OpenSLR probe could not resolve the host, so no LibriSpeech audio was processed or included.",
    "the same record and realtime-audio-library/docs/evaluation_plan.md record the official OpenSLR SLR12 test-clean archive MD5 32fa31d27d2e1cad72775fee3f4849a9, the reported CC BY 4.0 license, 16 kHz read English speech and LibriVox derivation, while the archive remains absent.",
    "realtime-audio-library/research/holdout_speech_source_assessment_20261028.md records Common Voice Spontaneous Speech 5.0 English dataset cmu5nqn1h00vwmi07b4dbk085 as release sps-corpus-5.0-2026-09-11, listed CC0-1.0, with reported 519.05 MB MP3, 5,898 clips, 642 speakers, 18.6 recorded hours and 8.39 validated hours.",
    "the same assessment records that the MDC consumer terms require accepting a provider-specific Data Consumer License, that enhancement is not among the stated intended uses, and that speaker identification and re-hosting or re-sharing are forbidden; no terms were accepted and no data were acquired.",
    "realtime-audio-library/docs/rights_clearance_inventory.md keeps both datasets uncleared: LibriSpeech is a potential Speex engineering source only and DPDFNet requires exact overlap exclusion, while Common Voice is not cleared for enhancement evaluation, retention or listening.",
    "realtime-audio-library/docs/evaluation_plan.md records that LibriSpeech and MLS are both derived from LibriVox, that DPDFNet is reported trained on 4,000 hours of MLS, and that the exact recording or speaker overlap is not established; SpeexDSP has no learned training corpus.",
    "plan/INVENTORY.json assigns this component the evidence verification profile, disposition research-control, evidence_status considered and the plan note to keep overlap, terms and development/test scope distinct per dataset and model.",
    "plan/swarm/VERIFICATION.md defines the evidence profile: pin the scorer, corpus and cohort, aggregation, failed items and controls; separate paired, unpaired, synthetic, human and source-reported evidence; and validate one invalid/missing case and one representative valid result through the reported bundle.",
)


class EvidenceError(ValueError):
    """Base error with a stable machine-readable code."""

    code = "EVIDENCE_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class JsonError(EvidenceError):
    code = "INVALID_JSON"


class AdmissionError(EvidenceError):
    code = "NO_ADMITTING_BRANCH"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("INVALID_JSON: " + str(error), "INVALID_JSON")


def strict_json_load(path: Path) -> Any:
    value = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise JsonError("JSON_NOT_OBJECT: " + str(path), "JSON_NOT_OBJECT")
    return value


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _require_bool(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(code, code)
    return value


def _require_str(value: Any, code: str,
                 minimum: int = 1, maximum: int = 4096) -> str:
    if not isinstance(value, str):
        raise ConfigError(code, code)
    if len(value) < minimum or len(value) > maximum:
        raise ConfigError(code, code)
    return value


def _require_int(value: Any, code: str,
                 minimum: int | None = None,
                 maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    if maximum is not None and value > maximum:
        raise ConfigError(code, code)
    return value


def _require_positive_float(value: Any, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(code, code)
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ConfigError(code, code)
    return number


def _optional_digest(value: Any, length: int, code: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != length:
        raise ConfigError(code, code)
    if any(character not in "0123456789abcdef" for character in value):
        raise ConfigError(code, code)
    return value


def _exact_object(value: Any, keys: frozenset[str], code: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(code, code)
    unknown = sorted(set(value) - keys)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(keys - set(value))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
    return value


def _safe_basename(value: str, code: str) -> str:
    name = _require_str(value, code, 1, 255)
    if ("/" in name or "\\" in name or name in (".", "..") or
            name.startswith(".")):
        raise ConfigError(code, code)
    return name


def validate_intake(request: Any) -> Dict[str, Any]:
    """Validate a dataset intake declaration without admitting any corpus."""
    request = _exact_object(request, REQUEST_KEYS, "INVALID_REQUEST")
    if request["schema_id"] != REQUEST_SCHEMA_ID:
        raise ConfigError("UNKNOWN_SCHEMA", "UNKNOWN_SCHEMA")
    corpus_id = request["corpus_id"]
    if corpus_id not in CORPORA:
        raise ConfigError("UNKNOWN_CORPUS", "UNKNOWN_CORPUS")
    spec = CORPORA[corpus_id]
    if request["subset"] != spec["subset"]:
        raise ConfigError("WRONG_SUBSET", "WRONG_SUBSET")
    if request["source_revision"] != spec["source_revision"]:
        raise ConfigError("WRONG_SOURCE_REVISION", "WRONG_SOURCE_REVISION")

    archive = _exact_object(request["archive"], ARCHIVE_KEYS,
                            "INVALID_ARCHIVE")
    filename = _safe_basename(archive["filename"],
                              "INVALID_ARCHIVE_FILENAME")
    checksum_kind = archive["checksum_kind"]
    if checksum_kind not in ("md5", "sha256"):
        raise ConfigError("INVALID_CHECKSUM_KIND", "INVALID_CHECKSUM_KIND")
    present = _require_bool(archive["present"], "INVALID_ARCHIVE_PRESENT")
    byte_count = archive["byte_count"]
    checksum = archive["checksum"]
    if corpus_id == LIBRISPEECH_CORPUS_ID:
        if filename != LIBRISPEECH["archive_filename"]:
            raise ConfigError("ARCHIVE_NAME_MISMATCH", "ARCHIVE_NAME_MISMATCH")
        if checksum_kind != "md5":
            raise ConfigError("CHECKSUM_KIND_MISMATCH", "CHECKSUM_KIND_MISMATCH")
        if checksum != LIBRISPEECH_REPORTED_MD5:
            raise ConfigError("ARCHIVE_CHECKSUM_MISMATCH",
                              "ARCHIVE_CHECKSUM_MISMATCH")
    elif checksum is not None:
        length = 32 if checksum_kind == "md5" else 64
        _optional_digest(checksum, length, "INVALID_ARCHIVE_CHECKSUM")
    if present:
        _require_int(byte_count, "INVALID_ARCHIVE_BYTES", 1, 10 ** 12)
        if checksum is None:
            raise ConfigError("MISSING_ARCHIVE_CHECKSUM",
                              "MISSING_ARCHIVE_CHECKSUM")
    elif byte_count is not None:
        raise ConfigError("INCONSISTENT_ARCHIVE_BYTES",
                          "INCONSISTENT_ARCHIVE_BYTES")

    manifest = _exact_object(request["manifest"], MANIFEST_KEYS,
                             "INVALID_MANIFEST")
    manifest_present = _require_bool(manifest["present"],
                                     "INVALID_MANIFEST_PRESENT")
    manifest_sha = _optional_digest(manifest["sha256"], 64,
                                    "INVALID_MANIFEST_DIGEST")
    item_count = manifest["item_count"]
    duration = manifest["duration_seconds"]
    flags = (
        _require_bool(manifest["transcript_bound"],
                      "INVALID_TRANSCRIPT_BOUND"),
        _require_bool(manifest["speaker_disjoint"],
                      "INVALID_SPEAKER_DISJOINT"),
        _require_bool(manifest["hashed_speaker_ids_only"],
                      "INVALID_HASHED_IDS"),
    )
    split_version = manifest["split_version"]
    if manifest_present:
        if manifest_sha is None:
            raise ConfigError("MISSING_MANIFEST_DIGEST",
                              "MISSING_MANIFEST_DIGEST")
        if not all(flags):
            raise ConfigError("INCOMPLETE_MANIFEST", "INCOMPLETE_MANIFEST")
        _require_int(item_count, "INVALID_ITEM_COUNT", 1, 10000000)
        _require_positive_float(duration, "INVALID_DURATION")
        if not isinstance(split_version, str) or not SPLIT_RE.match(
                split_version):
            raise ConfigError("INVALID_SPLIT_VERSION",
                              "INVALID_SPLIT_VERSION")
    else:
        if manifest_sha is not None or item_count is not None or (
                duration is not None):
            raise ConfigError("INCONSISTENT_MANIFEST",
                              "INCONSISTENT_MANIFEST")
        if any(flags) or split_version is not None:
            raise ConfigError("MANIFEST_CLAIM_WITHOUT_MANIFEST",
                              "MANIFEST_CLAIM_WITHOUT_MANIFEST")

    rights = _exact_object(request["rights"], RIGHTS_KEYS, "INVALID_RIGHTS")
    if rights["listed_license"] != spec["reported_license"]:
        raise ConfigError("LICENSE_LABEL_MISMATCH", "LICENSE_LABEL_MISMATCH")
    license_present = _require_bool(rights["license_text_present"],
                                    "INVALID_LICENSE_PRESENT")
    license_sha = _optional_digest(rights["license_text_sha256"], 64,
                                   "INVALID_LICENSE_DIGEST")
    if license_present != (license_sha is not None):
        raise ConfigError("INCONSISTENT_LICENSE_DIGEST",
                          "INCONSISTENT_LICENSE_DIGEST")
    download_reviewed = _require_bool(rights["download_terms_reviewed"],
                                      "INVALID_TERMS_REVIEW")
    use = _require_bool(rights["use_approved"], "INVALID_USE_APPROVAL")
    retention = _require_bool(rights["retention_approved"],
                              "INVALID_RETENTION_APPROVAL")
    redistribution = _require_bool(rights["redistribution_approved"],
                                   "INVALID_REDISTRIBUTION_APPROVAL")
    derived = _require_bool(rights["derived_output_approved"],
                            "INVALID_DERIVED_APPROVAL")
    listening = _require_bool(rights["listening_approved"],
                              "INVALID_LISTENING_APPROVAL")
    no_identification = _require_bool(
        rights["speaker_identification_forbidden_ack"],
        "INVALID_NO_IDENTIFICATION_ACK")
    no_rehosting = _require_bool(rights["no_rehosting_ack"],
                                 "INVALID_NO_REHOSTING_ACK")
    attribution = _require_bool(rights["attribution_recorded"],
                                "INVALID_ATTRIBUTION")
    approvals = (use, retention, redistribution, derived, listening)
    if any(approvals) and not (license_present and download_reviewed):
        raise ConfigError("APPROVAL_WITHOUT_TERMS",
                          "APPROVAL_WITHOUT_TERMS")
    if listening and not (use and retention):
        raise ConfigError("LISTENING_WITHOUT_USE", "LISTENING_WITHOUT_USE")
    if corpus_id == COMMON_VOICE_CORPUS_ID:
        if redistribution:
            raise ConfigError("REDISTRIBUTION_FORBIDDEN_BY_TERMS",
                              "REDISTRIBUTION_FORBIDDEN_BY_TERMS")
        if any(approvals) and not (no_identification and no_rehosting):
            raise ConfigError("TERMS_ACK_REQUIRED", "TERMS_ACK_REQUIRED")
    else:
        if (redistribution or derived) and not attribution:
            raise ConfigError("ATTRIBUTION_REQUIRED", "ATTRIBUTION_REQUIRED")

    model = _exact_object(request["model"], MODEL_KEYS, "INVALID_MODEL")
    model_id = _require_str(model["id"], "UNKNOWN_MODEL", 1, 64)
    if model_id not in MODEL_IDS:
        raise ConfigError("UNKNOWN_MODEL", "UNKNOWN_MODEL")
    overlap_status = model["overlap_status"]
    if overlap_status not in OVERLAP_STATUSES:
        raise ConfigError("INVALID_OVERLAP_STATUS", "INVALID_OVERLAP_STATUS")
    overlap_sha = _optional_digest(model["overlap_audit_sha256"], 64,
                                   "INVALID_OVERLAP_DIGEST")
    if model_id == "speexdsp":
        if overlap_status != "not_applicable_no_training_corpus":
            raise ConfigError("MODEL_OVERLAP_INVALID", "MODEL_OVERLAP_INVALID")
        if overlap_sha is not None:
            raise ConfigError("INCONSISTENT_OVERLAP_AUDIT",
                              "INCONSISTENT_OVERLAP_AUDIT")
    else:
        if overlap_status == "not_applicable_no_training_corpus":
            raise ConfigError("MODEL_OVERLAP_INVALID", "MODEL_OVERLAP_INVALID")
        if overlap_status == "exact_overlap_excluded" and overlap_sha is None:
            raise ConfigError("MISSING_OVERLAP_AUDIT",
                              "MISSING_OVERLAP_AUDIT")
        if overlap_status == "not_reviewed" and overlap_sha is not None:
            raise ConfigError("INCONSISTENT_OVERLAP_AUDIT",
                              "INCONSISTENT_OVERLAP_AUDIT")

    return {
        "schema_id": REQUEST_SCHEMA_ID,
        "corpus_id": corpus_id,
        "subset": spec["subset"],
        "source_revision": spec["source_revision"],
        "archive": {
            "filename": filename,
            "checksum_kind": checksum_kind,
            "checksum": checksum,
            "byte_count": byte_count,
            "present": present,
        },
        "manifest": {
            "present": manifest_present,
            "sha256": manifest_sha,
            "item_count": item_count,
            "duration_seconds": duration,
            "transcript_bound": flags[0],
            "speaker_disjoint": flags[1],
            "hashed_speaker_ids_only": flags[2],
            "split_version": split_version,
        },
        "rights": {
            "listed_license": spec["reported_license"],
            "license_text_present": license_present,
            "license_text_sha256": license_sha,
            "download_terms_reviewed": download_reviewed,
            "use_approved": use,
            "retention_approved": retention,
            "redistribution_approved": redistribution,
            "derived_output_approved": derived,
            "listening_approved": listening,
            "speaker_identification_forbidden_ack": no_identification,
            "no_rehosting_ack": no_rehosting,
            "attribution_recorded": attribution,
        },
        "model": {
            "id": model_id,
            "overlap_status": overlap_status,
            "overlap_audit_sha256": overlap_sha,
        },
    }


def _base_request(corpus_id: str = LIBRISPEECH_CORPUS_ID) -> Dict[str, Any]:
    spec = CORPORA[corpus_id]
    if corpus_id == LIBRISPEECH_CORPUS_ID:
        archive = {
            "filename": "test-clean.tar.gz",
            "checksum_kind": "md5",
            "checksum": LIBRISPEECH_REPORTED_MD5,
            "byte_count": 1,
            "present": True,
        }
        rights = {
            "listed_license": "CC BY 4.0",
            "license_text_present": True,
            "license_text_sha256": "a" * 64,
            "download_terms_reviewed": True,
            "use_approved": True,
            "retention_approved": True,
            "redistribution_approved": True,
            "derived_output_approved": True,
            "listening_approved": True,
            "speaker_identification_forbidden_ack": True,
            "no_rehosting_ack": True,
            "attribution_recorded": True,
        }
    else:
        archive = {
            "filename": "sps-corpus-5.0-2026-09-11.tar.gz",
            "checksum_kind": "sha256",
            "checksum": "b" * 64,
            "byte_count": 1,
            "present": True,
        }
        rights = {
            "listed_license": "CC0-1.0",
            "license_text_present": True,
            "license_text_sha256": "a" * 64,
            "download_terms_reviewed": True,
            "use_approved": True,
            "retention_approved": True,
            "redistribution_approved": False,
            "derived_output_approved": False,
            "listening_approved": True,
            "speaker_identification_forbidden_ack": True,
            "no_rehosting_ack": True,
            "attribution_recorded": False,
        }
    return {
        "schema_id": REQUEST_SCHEMA_ID,
        "corpus_id": corpus_id,
        "subset": spec["subset"],
        "source_revision": spec["source_revision"],
        "archive": archive,
        "manifest": {
            "present": True,
            "sha256": "c" * 64,
            "item_count": 1,
            "duration_seconds": 1.0,
            "transcript_bound": True,
            "speaker_disjoint": True,
            "hashed_speaker_ids_only": True,
            "split_version": "structural-validator-fixture-v1",
        },
        "rights": rights,
        "model": {
            "id": "speexdsp",
            "overlap_status": "not_applicable_no_training_corpus",
            "overlap_audit_sha256": None,
        },
    }


def _variant(base: Dict[str, Any], **changes: Any) -> Dict[str, Any]:
    value = json.loads(json.dumps(base))
    for key, item in changes.items():
        if "." in key:
            outer, inner = key.split(".", 1)
            value[outer][inner] = item
        else:
            value[key] = item
    return value


def _adverse_request_specs() -> List[Tuple[str, Any]]:
    ls = _base_request()
    cv = _base_request(COMMON_VOICE_CORPUS_ID)
    nan_duration = _variant(ls)
    nan_duration["manifest"]["duration_seconds"] = float("nan")
    inf_duration = _variant(ls)
    inf_duration["manifest"]["duration_seconds"] = float("inf")
    negative_inf_duration = _variant(ls)
    negative_inf_duration["manifest"]["duration_seconds"] = float("-inf")
    absent_manifest = _variant(
        ls, **{
            "manifest.present": False,
            "manifest.sha256": None,
            "manifest.item_count": None,
            "manifest.duration_seconds": None,
            "manifest.transcript_bound": False,
            "manifest.speaker_disjoint": False,
            "manifest.hashed_speaker_ids_only": False,
            "manifest.split_version": None,
        })
    specs: List[Tuple[str, Any]] = [
        ("request_not_object", "not-an-object"),
        ("unknown_field", _variant(ls, extra=True)),
        ("missing_field", {key: value for key, value in ls.items()
                           if key != "manifest"}),
        ("unknown_schema", _variant(ls, schema_id="audio-sdk/other/0.1")),
        ("unknown_corpus", _variant(ls, corpus_id="librispeech")),
        ("librispeech_wrong_subset", _variant(ls, subset="dev-clean")),
        ("librispeech_wrong_revision",
         _variant(ls, source_revision="librispeech-test-clean")),
        ("common_voice_wrong_subset", _variant(cv, subset="en-27.0")),
        ("common_voice_wrong_revision", _variant(cv, source_revision="en")),
        ("archive_not_object", _variant(ls, archive="test-clean.tar.gz")),
        ("archive_unknown_field", _variant(ls, **{"archive.extra": True})),
        ("archive_missing_field",
         _variant(ls, archive={"filename": "test-clean.tar.gz"})),
        ("archive_traversal_filename",
         _variant(ls, **{"archive.filename": "../test-clean.tar.gz"})),
        ("archive_absolute_filename",
         _variant(ls, **{"archive.filename": "/tmp/test-clean.tar.gz"})),
        ("archive_backslash_filename",
         _variant(ls, **{"archive.filename": "dir\\test-clean.tar.gz"})),
        ("archive_hidden_filename",
         _variant(ls, **{"archive.filename": ".test-clean.tar.gz"})),
        ("librispeech_wrong_filename",
         _variant(ls, **{"archive.filename": "dev-clean.tar.gz"})),
        ("librispeech_wrong_md5",
         _variant(ls, **{"archive.checksum": "0" * 32})),
        ("librispeech_uppercase_md5",
         _variant(ls, **{"archive.checksum": "A" * 32})),
        ("librispeech_sha256_kind",
         _variant(ls, **{"archive.checksum_kind": "sha256"})),
        ("archive_invalid_kind",
         _variant(ls, **{"archive.checksum_kind": "crc32"})),
        ("archive_missing_checksum_present",
         _variant(ls, **{"archive.checksum": None})),
        ("archive_absent_with_bytes",
         _variant(ls, **{"archive.present": False})),
        ("archive_zero_bytes",
         _variant(ls, **{"archive.byte_count": 0})),
        ("archive_negative_bytes",
         _variant(ls, **{"archive.byte_count": -1})),
        ("archive_bool_bytes",
         _variant(ls, **{"archive.byte_count": True})),
        ("archive_bool_present",
         _variant(ls, **{"archive.present": "yes"})),
        ("manifest_not_object", _variant(ls, manifest="manifest.json")),
        ("manifest_unknown_field",
         _variant(ls, **{"manifest.extra": True})),
        ("manifest_missing_digest",
         _variant(ls, **{"manifest.sha256": None})),
        ("manifest_short_digest",
         _variant(ls, **{"manifest.sha256": "c" * 63})),
        ("manifest_uppercase_digest",
         _variant(ls, **{"manifest.sha256": "C" * 64})),
        ("manifest_nonhex_digest",
         _variant(ls, **{"manifest.sha256": "g" * 64})),
        ("manifest_zero_items",
         _variant(ls, **{"manifest.item_count": 0})),
        ("manifest_negative_items",
         _variant(ls, **{"manifest.item_count": -1})),
        ("manifest_bool_items",
         _variant(ls, **{"manifest.item_count": True})),
        ("manifest_nan_duration", nan_duration),
        ("manifest_inf_duration", inf_duration),
        ("manifest_negative_inf_duration", negative_inf_duration),
        ("manifest_zero_duration",
         _variant(ls, **{"manifest.duration_seconds": 0.0})),
        ("manifest_negative_duration",
         _variant(ls, **{"manifest.duration_seconds": -1.0})),
        ("manifest_bool_duration",
         _variant(ls, **{"manifest.duration_seconds": True})),
        ("manifest_string_duration",
         _variant(ls, **{"manifest.duration_seconds": "1.0"})),
        ("manifest_not_transcript_bound",
         _variant(ls, **{"manifest.transcript_bound": False})),
        ("manifest_not_speaker_disjoint",
         _variant(ls, **{"manifest.speaker_disjoint": False})),
        ("manifest_not_hashed_ids",
         _variant(ls, **{"manifest.hashed_speaker_ids_only": False})),
        ("manifest_uppercase_split",
         _variant(ls, **{"manifest.split_version": "Split-V1"})),
        ("manifest_unicode_split",
         _variant(ls, **{"manifest.split_version": "split-v1-\u00e9"})),
        ("manifest_path_split",
         _variant(ls, **{"manifest.split_version": "../split"})),
        ("absent_manifest_with_digest",
         _variant(absent_manifest, **{"manifest.sha256": "c" * 64})),
        ("absent_manifest_with_split",
         _variant(absent_manifest,
                  **{"manifest.split_version": "split-v1"})),
        ("absent_manifest_with_item_count",
         _variant(absent_manifest, **{"manifest.item_count": 1})),
        ("rights_not_object", _variant(ls, rights=[])),
        ("rights_unknown_field",
         _variant(ls, **{"rights.extra": True})),
        ("rights_wrong_license",
         _variant(ls, **{"rights.listed_license": "CC0-1.0"})),
        ("rights_cv_wrong_license",
         _variant(cv, **{"rights.listed_license": "CC BY 4.0"})),
        ("rights_text_without_digest",
         _variant(ls, **{"rights.license_text_sha256": None})),
        ("rights_digest_without_text",
         _variant(ls, **{"rights.license_text_present": False})),
        ("rights_use_without_text",
         _variant(ls, **{"rights.license_text_present": False,
                         "rights.license_text_sha256": None})),
        ("rights_use_without_terms_review",
         _variant(ls, **{"rights.download_terms_reviewed": False})),
        ("rights_cv_redistribution",
         _variant(cv, **{"rights.redistribution_approved": True})),
        ("rights_cv_without_no_identification",
         _variant(cv,
                  **{"rights.speaker_identification_forbidden_ack": False})),
        ("rights_cv_without_no_rehosting",
         _variant(cv, **{"rights.no_rehosting_ack": False})),
        ("rights_librispeech_without_attribution",
         _variant(ls, **{"rights.attribution_recorded": False})),
        ("rights_listening_without_use",
         _variant(ls, **{"rights.use_approved": False})),
        ("rights_bool_license_present",
         _variant(ls, **{"rights.license_text_present": 1})),
        ("model_not_object", _variant(ls, model="speexdsp")),
        ("model_unknown_field",
         _variant(ls, **{"model.extra": True})),
        ("model_unknown_id", _variant(ls, **{"model.id": "rnnoise"})),
        ("model_bool_id", _variant(ls, **{"model.id": True})),
        ("model_invalid_overlap",
         _variant(ls, **{"model.overlap_status": "probably_clean"})),
        ("model_speex_with_exact_overlap",
         _variant(ls, **{"model.overlap_status": "exact_overlap_excluded"})),
        ("model_speex_with_audit",
         _variant(ls, **{"model.overlap_audit_sha256": "d" * 64})),
        ("model_learned_not_applicable",
         _variant(ls, **{"model.id": "other_learned",
                         "model.overlap_status":
                         "not_applicable_no_training_corpus"})),
        ("model_exact_overlap_without_audit",
         _variant(ls, **{"model.id": "dpdfnet",
                         "model.overlap_status": "exact_overlap_excluded"})),
        ("model_not_reviewed_with_audit",
         _variant(ls, **{"model.id": "dpdfnet",
                         "model.overlap_audit_sha256": "d" * 64})),
        ("model_short_audit",
         _variant(ls, **{"model.id": "dpdfnet",
                         "model.overlap_status": "exact_overlap_excluded",
                         "model.overlap_audit_sha256": "d" * 63})),
        ("model_uppercase_audit",
         _variant(ls, **{"model.id": "dpdfnet",
                         "model.overlap_status": "exact_overlap_excluded",
                         "model.overlap_audit_sha256": "D" * 64})),
    ]
    return specs


def _adverse_intake_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, request in _adverse_request_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_intake(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
        "note": (
            "Invalid, inconsistent, overclaiming and nonfinite declarations "
            "are rejected before any presence or artifact check. No metrics "
            "exist and nothing qualifies."),
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
        ("json_not_object", '[1,2,3]'),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            value = strict_json_loads(text)
            accepted = not isinstance(value, list)
        except JsonError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": COMPARISON_STATUS,
        "metrics": None,
        "qualifies": False,
        "note": "No exact dataset or manifest exists; a missing result never qualifies.",
    }


def _resolve_path(label: str) -> Path:
    if label.startswith("/"):
        return Path(label)
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return WORKSPACE / label


def _path_rows(labels: Sequence[str]) -> List[Dict[str, Any]]:
    return [{"path": label, "present": _resolve_path(label).exists()}
            for label in labels]


def _any_present(rows: Sequence[Dict[str, Any]]) -> bool:
    return any(row["present"] for row in rows)


def librispeech_probe() -> Dict[str, Any]:
    archives = _path_rows(LIBRISPEECH_ARCHIVE_PATHS)
    trees = _path_rows(LIBRISPEECH_TREE_PATHS)
    manifests = _path_rows(LIBRISPEECH_MANIFEST_PATHS)
    archive_present = _any_present(archives)
    tree_present = _any_present(trees)
    manifest_present = _any_present(manifests)
    present = archive_present or tree_present or manifest_present
    return {
        "status": ("present_unverified" if present
                   else "blocked_archive_tree_manifest_absent"),
        "present": present,
        "archive_present": archive_present,
        "source_tree_present": tree_present,
        "prepared_manifest_present": manifest_present,
        "archive_paths": archives,
        "tree_paths": trees,
        "manifest_paths": manifests,
        "reported": dict(LIBRISPEECH),
        "local": {
            "archive_md5": None,
            "archive_sha256": None,
            "archive_byte_count": None,
            "manifest_sha256": None,
            "item_count": None,
            "duration_seconds": None,
            "speaker_split_verified": False,
            "rights_record": None,
        },
        "note": (
            "Read-only existence checks only. No archive, FLAC, transcript or "
            "manifest is opened, hashed, decoded or copied. A path that "
            "appears later is present_unverified, not evidence."),
    }


def common_voice_probe() -> Dict[str, Any]:
    archives = _path_rows(COMMON_VOICE_ARCHIVE_PATHS)
    metadata = _path_rows(COMMON_VOICE_METADATA_PATHS)
    manifests = _path_rows(COMMON_VOICE_MANIFEST_PATHS)
    archive_present = _any_present(archives)
    metadata_present = _any_present(metadata)
    manifest_present = _any_present(manifests)
    present = archive_present or metadata_present or manifest_present
    return {
        "status": ("present_unverified" if present
                   else "blocked_archive_metadata_manifest_absent"),
        "present": present,
        "archive_present": archive_present,
        "source_metadata_present": metadata_present,
        "prepared_manifest_present": manifest_present,
        "archive_paths": archives,
        "metadata_paths": metadata,
        "manifest_paths": manifests,
        "reported": dict(COMMON_VOICE),
        "local": {
            "archive_sha256": None,
            "archive_byte_count": None,
            "manifest_sha256": None,
            "item_count": None,
            "duration_seconds": None,
            "speaker_split_verified": False,
            "download_terms_reviewed": False,
            "rights_record": None,
        },
        "note": (
            "Read-only existence checks only. No archive, MP3, metadata TSV or "
            "manifest is opened, hashed, decoded or copied. A path that "
            "appears later is present_unverified, not evidence."),
    }


def presence_probe() -> Dict[str, Any]:
    librispeech = librispeech_probe()
    common_voice = common_voice_probe()
    return {
        "bounded": True,
        "librispeech": librispeech,
        "common_voice": common_voice,
        "probed_path_count": (
            len(librispeech["archive_paths"]) + len(librispeech["tree_paths"]) +
            len(librispeech["manifest_paths"]) +
            len(common_voice["archive_paths"]) +
            len(common_voice["metadata_paths"]) +
            len(common_voice["manifest_paths"])),
        "present": librispeech["present"] or common_voice["present"],
        "note": (
            "Presence is probed only at the documented workspace and local "
            "preparation paths. Absence elsewhere is not excluded. No network "
            "probe is performed and no directory is scanned recursively."),
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "approval_record": None,
        "use_approved": False,
        "retention_approved": False,
        "evaluation_approved": False,
        "listening_approved": False,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "privacy_or_publicity_reviewed": False,
        "librispeech": {
            "status": "not_cleared",
            "reported_license": "CC BY 4.0",
            "reported_source": "https://www.openslr.org/12/",
            "license_text_present": False,
            "license_text_sha256": None,
            "attribution_recorded": False,
            "privacy_or_publicity_grant": False,
            "intended_use_reviewed": False,
            "note": (
                "CC BY 4.0 is a reported source label, not a local license "
                "text or a privacy/publicity grant. The archive is absent and "
                "no use decision exists."),
        },
        "common_voice": {
            "status": "not_cleared",
            "reported_license": "CC0-1.0",
            "reported_source": (
                "https://mozilladatacollective.com/datasets/"
                "cmu5nqn1h00vwmi07b4dbk085"),
            "license_text_present": False,
            "license_text_sha256": None,
            "download_terms_reviewed": False,
            "download_terms_accepted": False,
            "enhancement_use_confirmed": False,
            "speaker_identification_forbidden_ack": False,
            "no_rehosting_ack": False,
            "note": (
                "The public listing is labelled CC0-1.0, but the MDC "
                "download-time Data Consumer License was not inspected or "
                "accepted and enhancement is not a stated intended use. No "
                "data were acquired."),
        },
        "note": (
            "The two datasets keep independent rights states. No license text, "
            "acceptance, attribution, privacy/publicity review or written "
            "decision is present."),
    }


def overlap_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "dataset": LIBRISPEECH_CORPUS_ID,
            "model": "speexdsp",
            "status": "not_applicable_no_training_corpus",
            "exact_audit_present": False,
            "reason": (
                "SpeexDSP has no learned training corpus, so the LibriVox / "
                "MLS training-overlap risk does not apply to its signal path. "
                "Rights, privacy and synthetic-noise limitations still apply."),
        },
        {
            "dataset": LIBRISPEECH_CORPUS_ID,
            "model": "dpdfnet",
            "status": "risk_unresolved_exact_exclusion_missing",
            "exact_audit_present": False,
            "reason": (
                "LibriSpeech and MLS are both reported derived from LibriVox "
                "and DPDFNet is reported trained on 4,000 hours of MLS. This "
                "is an overlap risk, not proof of exact recording or speaker "
                "overlap. DPDFNet requires file-level exclusion before use."),
        },
        {
            "dataset": LIBRISPEECH_CORPUS_ID,
            "model": "other_learned",
            "status": "unreviewed",
            "exact_audit_present": False,
            "reason": (
                "Every other learned model needs its own training-overlap "
                "review against LibriSpeech; no model-independent claim is "
                "made."),
        },
        {
            "dataset": COMMON_VOICE_CORPUS_ID,
            "model": "speexdsp",
            "status": "not_applicable_no_training_corpus",
            "exact_audit_present": False,
            "reason": (
                "SpeexDSP has no learned training corpus. Common Voice rights, "
                "speaker privacy and synthetic-noise limitations remain."),
        },
        {
            "dataset": COMMON_VOICE_CORPUS_ID,
            "model": "dpdfnet",
            "status": "unreviewed",
            "exact_audit_present": False,
            "reason": (
                "Common Voice v5 training overlap must be reviewed for DPDFNet "
                "independently; a recent release date does not prove "
                "independence."),
        },
        {
            "dataset": COMMON_VOICE_CORPUS_ID,
            "model": "other_learned",
            "status": "unreviewed",
            "exact_audit_present": False,
            "reason": (
                "Every learned candidate needs an independent training-overlap "
                "review against Common Voice v5 before evaluation."),
        },
    ]


def evidence_separation() -> Dict[str, Any]:
    return {
        "paired": {
            "status": "absent",
            "present": False,
            "note": "No clean/noisy pair, render/capture pair or paired score exists.",
        },
        "unpaired": {
            "status": "absent",
            "present": False,
            "note": "No unpaired speech or predictive score exists.",
        },
        "synthetic": {
            "status": "declared_only_not_run",
            "present": False,
            "note": (
                "Only analytic structural controls exist. No synthetic noise "
                "mixture, clean/noisy pair or corpus-derived sample is made."),
        },
        "human": {
            "status": "absent",
            "present": False,
            "listening": False,
            "note": "No listening panel, rating or human judgment exists.",
        },
        "source_reported": {
            "status": "retained_not_reproduced",
            "present": True,
            "note": (
                "LibriSpeech and Common Voice identities, counts and terms are "
                "retained from pinned notes as source-reported facts. They are "
                "not local measurements."),
        },
        "pooling": False,
        "note": (
            "Evidence kinds stay separate. No category is pooled, promoted or "
            "used to fill another category."),
    }


def acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": "evidence",
        "source": SOURCE_PINS[PROFILE_SOURCE],
        "required_items": {
            "pinned_scorer_corpus_and_cohort": {
                "status": "blocked",
                "evidence": (
                    "No scorer, rights-cleared corpus or frozen cohort is "
                    "staged; neither exact dataset archive nor manifest is "
                    "present."),
            },
            "pinned_aggregation_failed_items_and_controls": {
                "status": "blocked",
                "evidence": (
                    "No aggregation, failed-item policy or scored control "
                    "result exists. Only local structural rejections exist."),
            },
            "separation_of_evidence_kinds": {
                "status": "declared_only",
                "evidence": (
                    "Paired, unpaired, synthetic, human and source-reported "
                    "categories are declared and kept separate, but only the "
                    "source-reported category has content; nothing is scored."),
            },
            "invalid_or_missing_case_validated": {
                "status": "recorded",
                "evidence": (
                    "The live control rejects both datasets with 0 archives, "
                    "0 prepared manifests and 0 rights records present; every "
                    "adverse declaration is rejected without state change."),
            },
            "representative_valid_result_validated": {
                "status": "blocked",
                "evidence": (
                    "No representative valid item or result exists; the "
                    "required valid half of the profile cannot be validated."),
            },
            "exact_references_and_rights": {
                "status": "blocked",
                "evidence": (
                    "Reported archive and release identities exist, but no "
                    "local byte identity or rights approval exists."),
            },
        },
        "mapped_cases": {
            "librispeech_absence": (
                "archive, extracted tree and prepared manifest all absent"),
            "common_voice_absence": (
                "archive, metadata and prepared manifest all absent"),
            "source_reported_evidence": (
                "pinned notes only; not a local measurement"),
            "adverse_declarations": (
                "strict schema, digest, split, rights and overlap rejections"),
        },
        "not_applicable": [
            "paired SI-SDR/STOI or ASR scoring without permitted data",
            "listening, device timing, benchmark and release qualification",
        ],
    }


def required_results() -> Dict[str, str]:
    return {
        "librispeech_archive_and_license": (
            "blocked_archive_and_license_text_absent"),
        "librispeech_manifest_and_speaker_split": "blocked_manifest_absent",
        "common_voice_archive_and_download_license": (
            "blocked_archive_and_download_terms_unreviewed"),
        "common_voice_manifest_and_hashed_split": "blocked_manifest_absent",
        "dataset_scoped_rights": "blocked_rights_unrecorded",
        "per_model_overlap": "blocked_overlap_unresolved",
        "pinned_scorer_corpus_and_cohort": "blocked_no_frozen_cohort",
        "aggregation_failed_items_and_controls": (
            "blocked_no_aggregation_or_failed_item_policy"),
        "invalid_and_missing_control": "partial_local_harness_rejection_only",
        "representative_valid_result": "blocked_no_valid_result",
        "release_qualification": "blocked_no_release_evidence",
    }


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "dataset_qualified": False,
        "decision": "DEFER",
        "evidence_status": "incomplete",
        "invalid_or_missing_control": True,
        "manifest_verified": False,
        "missing_result_promoted": False,
        "proposal_only": True,
        "provider_intake": False,
        "readiness": "incomplete",
        "release_claim": False,
        "representative_valid_result": False,
        "rights_approved": False,
        "scorer_pinned": False,
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "adapter_added": False,
        "asset_bundled": False,
        "audio_executed": False,
        "audio_loaded": False,
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "device_timing_claim": False,
        "enabled_by_default": False,
        "installed_v0_behavior_change": False,
        "listening_run": False,
        "network_used": False,
        "processor_exposure": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "real_corpus_read": False,
        "release_claim": False,
        "sdk_data_dir_added": False,
        "shared_build_or_ci_change": False,
        "weights_vendored": False,
        "format": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
        },
    }


def _request_blockers(request: Dict[str, Any]) -> List[str]:
    blockers: List[str] = []
    if not request["archive"]["present"]:
        blockers.append("archive_absent")
    else:
        blockers.append("archive_identity_unverified")
    if not request["manifest"]["present"]:
        blockers.append("prepared_manifest_absent")
        blockers.append("speaker_split_unverified")
    else:
        blockers.append("manifest_identity_unverified")
        if not (request["manifest"]["speaker_disjoint"] and
                request["manifest"]["hashed_speaker_ids_only"]):
            blockers.append("speaker_split_unverified")
    rights = request["rights"]
    if not rights["license_text_present"]:
        blockers.append("license_text_absent")
    if not rights["download_terms_reviewed"]:
        blockers.append("download_terms_unreviewed")
    if not (rights["use_approved"] and rights["retention_approved"]):
        blockers.append("rights_not_approved")
    if not rights["redistribution_approved"]:
        blockers.append("redistribution_not_approved")
    model = request["model"]
    if model["overlap_status"] == "not_reviewed":
        blockers.append("model_overlap_unresolved")
    if (request["corpus_id"] == COMMON_VOICE_CORPUS_ID and
            model["id"] != "speexdsp" and
            model["overlap_status"] != "exact_overlap_excluded"):
        blockers.append("common_voice_training_overlap_unreviewed")
    blockers.append("frozen_cohort_and_scorer_absent")
    blockers.append("representative_valid_result_absent")
    return sorted(set(blockers))


def _live_blockers(corpus_id: str) -> List[str]:
    blockers = [
        "dataset_rights_unrecorded",
        "frozen_cohort_and_scorer_absent",
        "representative_valid_result_absent",
    ]
    names = {
        LIBRISPEECH_CORPUS_ID: "librispeech",
        COMMON_VOICE_CORPUS_ID: "common_voice",
    }
    for name, probe in (
            (LIBRISPEECH_CORPUS_ID, librispeech_probe()),
            (COMMON_VOICE_CORPUS_ID, common_voice_probe())):
        label = names[name]
        if not probe["present"]:
            blockers.append(label + "_archive_and_manifest_absent")
        if name == corpus_id and probe["prepared_manifest_present"]:
            blockers.append(label + "_manifest_identity_unverified")
    return blockers


def admit(request: Any) -> Dict[str, Any]:
    """Validate an intake declaration, then fail closed with no admitting branch."""
    validated = validate_intake(request)
    blockers = sorted(set(_request_blockers(validated) +
                          _live_blockers(validated["corpus_id"])))
    if not blockers:
        blockers = ["no_admitting_branch_in_this_blocker_package"]
    return {
        "status": "DEFER",
        "admissible": False,
        "qualifies": False,
        "input_validated": True,
        "candidate_processing": False,
        "metrics": None,
        "result": None,
        "blockers": blockers,
        "note": (
            "A structurally valid declaration is still not admissible: the "
            "exact archive, prepared manifest, dataset-scoped rights, overlap "
            "audit, frozen cohort, scorer and representative result are "
            "absent. This package has no admitting branch and no fallback."),
    }


def collect_blockers() -> List[str]:
    blockers: List[str] = []
    librispeech = librispeech_probe()
    common_voice = common_voice_probe()
    rights = rights_probe()
    if not librispeech["archive_present"]:
        blockers.append("librispeech_archive_absent")
    if not librispeech["prepared_manifest_present"]:
        blockers.append("librispeech_manifest_absent")
    if not common_voice["archive_present"]:
        blockers.append("common_voice_archive_absent")
    if not common_voice["prepared_manifest_present"]:
        blockers.append("common_voice_manifest_absent")
    if rights["status"] != "approved":
        blockers.append("dataset_rights_unrecorded")
    blockers.extend([
        "speaker_splits_unverified",
        "model_overlap_unresolved",
        "frozen_cohort_and_scorer_absent",
        "representative_valid_result_absent",
        "no_admitting_branch",
    ])
    return sorted(blockers)


def control_probe() -> Dict[str, Any]:
    ledger = {
        "datasets": [
            {
                "corpus_id": LIBRISPEECH_CORPUS_ID,
                "archives_present": 0,
                "manifests_present": 0,
                "items_verified": 0,
                "rights_approved": False,
            },
            {
                "corpus_id": COMMON_VOICE_CORPUS_ID,
                "archives_present": 0,
                "manifests_present": 0,
                "items_verified": 0,
                "rights_approved": False,
            },
        ],
        "pooled": False,
    }
    payload = canonical_bytes(ledger)
    return {
        "purpose": (
            "analytic structural control only; not a corpus manifest, not a "
            "dataset result and not candidate output"),
        "ledger": ledger,
        "digest": sha256_bytes(payload),
        "byte_identical": (
            strict_json_loads(payload.decode("utf-8")) == ledger and
            canonical_bytes(strict_json_loads(payload.decode("utf-8"))) ==
            payload),
        "datasets_separate": (
            ledger["datasets"][0]["corpus_id"] !=
            ledger["datasets"][1]["corpus_id"] and
            ledger["pooled"] is False),
        "candidate_processing": False,
        "real_corpus_read": False,
    }


def _board_projection(board: Any) -> Tuple[List[Dict[str, Any]], str]:
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    rows = [row for row in board["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ConfigError("linked task row is missing or duplicated",
                          "BOARD_ROW_MISSING")
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    projected = [stable]
    return projected, sha256_bytes(canonical_bytes(projected))


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    return _board_projection(board)


def artifact_pins(names: Sequence[str] = SELF_PIN_FILES) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in names:
        path = HERE / name
        if not path.is_file():
            raise ConfigError("missing package artifact: " + name,
                              "MISSING_ARTIFACT")
        pins[name] = sha256_file(path)
    return pins


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    librispeech = librispeech_probe()
    common_voice = common_voice_probe()
    rights = rights_probe()
    adverse = _adverse_intake_cases()
    adverse_json = _json_adverse_cases()
    control = control_probe()
    gates = [dict(gate) for gate in GATES]
    required = [dict(row) for row in REQUIRED_ARTIFACTS]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "librispeech_archive_absent": not librispeech["archive_present"],
        "librispeech_manifest_absent":
            not librispeech["prepared_manifest_present"],
        "common_voice_archive_absent": not common_voice["archive_present"],
        "common_voice_manifest_absent":
            not common_voice["prepared_manifest_present"],
        "rights_not_approved": rights["status"] != "approved",
        "speaker_splits_unverified": (
            not librispeech["local"]["speaker_split_verified"] and
            not common_voice["local"]["speaker_split_verified"]),
        "model_overlap_unresolved": all(
            not row["exact_audit_present"] for row in overlap_matrix()
            if row["model"] != "speexdsp"),
        "invalid_declarations_rejected": adverse["all_rejected"],
        "nonfinite_values_rejected": all(
            not case["accepted"] for case in adverse["cases"]
            if "nan" in case["id"] or "inf" in case["id"]),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("dataset_placeholder")["status"] == "blocked",
        "structural_control_bit_exact": control["byte_identical"],
        "datasets_kept_separate": control["datasets_separate"],
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "external_boundary_closed": (
            boundary()["provider_registration"] is False and
            boundary()["public_api_abi_change"] is False and
            boundary()["network_used"] is False),
        "no_result_qualifies": True,
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "verification_profile": VERIFICATION_PROFILE,
        "status": "proposal_only_incomplete",
        "decision": "DEFER",
        "incomplete": True,
        "proposal_only": True,
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
        "defer_before": DEFER_BEFORE,
        "comparison_status": COMPARISON_STATUS,
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": VERIFICATION_PROFILE,
            "source": SOURCE_PINS[PROFILE_SOURCE],
        },
        "acceptance_profile": acceptance_profile(),
        "profile_mapping": {
            "pinned_scorer_corpus_and_cohort": "blocked_no_frozen_cohort",
            "aggregation_failed_items_and_controls":
                "blocked_no_aggregation_or_failed_item_policy",
            "separation_of_evidence_kinds": "declared_only_not_scored",
            "invalid_or_missing_case": "partial_local_harness_rejection_only",
            "representative_valid_result": "blocked_no_valid_result",
            "exact_references_and_rights": "blocked_rights_unrecorded",
        },
        "datasets": {
            LIBRISPEECH_CORPUS_ID: {
                "reported": dict(LIBRISPEECH),
                "local": dict(librispeech["local"]),
                "probe_status": librispeech["status"],
                "archive_present": librispeech["archive_present"],
                "source_tree_present": librispeech["source_tree_present"],
                "prepared_manifest_present":
                    librispeech["prepared_manifest_present"],
                "rights": dict(rights["librispeech"]),
            },
            COMMON_VOICE_CORPUS_ID: {
                "reported": dict(COMMON_VOICE),
                "local": dict(common_voice["local"]),
                "probe_status": common_voice["status"],
                "archive_present": common_voice["archive_present"],
                "source_metadata_present":
                    common_voice["source_metadata_present"],
                "prepared_manifest_present":
                    common_voice["prepared_manifest_present"],
                "rights": dict(rights["common_voice"]),
            },
        },
        "overlap_matrix": overlap_matrix(),
        "evidence_separation": evidence_separation(),
        "rights": rights,
        "external_boundary": {
            "documented": True,
            "datasets": [LIBRISPEECH_CORPUS_ID, COMMON_VOICE_CORPUS_ID],
            "librispeech_source_present": False,
            "librispeech_manifest_present": False,
            "common_voice_source_present": False,
            "common_voice_manifest_present": False,
            "license_text_present": False,
            "download_terms_accepted": False,
            "rights_approved": False,
            "scorer_present": False,
            "cohort_present": False,
            "representative_result_present": False,
            "adapter_implemented": False,
            "adapter_default_registration": False,
            "automatic_discovery": False,
            "fallback": "none",
            "source_reported_separate_from_local": True,
            "note": (
                "The dataset boundary is documented from pinned notes and "
                "public dataset pages only. No archive, manifest, license "
                "text, scorer or cohort is present, and this host target is "
                "not approved for either dataset."),
        },
        "blocker": dict(BLOCKER),
        "required_artifacts": required,
        "missing_artifacts": [row["artifact"] for row in required
                              if row["status"] == "absent"],
        "presence_probe": presence_probe(),
        "admission_controls": {
            "admission_policy": {
                "admitting_branch_exists": False,
                "always_defer": True,
                "metadata_only_can_qualify": False,
                "reported_identity_can_qualify": False,
                "caller_bytes_can_qualify_without_rights": False,
                "rights_and_bytes_still_require_cohort_and_review": True,
            },
            "recorded_declaration_live": {
                "decision": "DEFER",
                "qualifies": False,
                "reason": COMPARISON_STATUS,
                "librispeech_archive_present": False,
                "librispeech_manifest_present": False,
                "common_voice_archive_present": False,
                "common_voice_manifest_present": False,
                "rights_approved": False,
                "representative_valid_result": False,
            },
            "structural_valid_declaration": {
                "exercise": "unit_test_only_structural_fixture",
                "decision": "DEFER",
                "qualifies": False,
                "identity_recorded": False,
                "note": (
                    "Tests exercise the validator with a clearly labelled "
                    "non-corpus placeholder declaration. Its synthetic "
                    "checksums are never reported as dataset identity and it "
                    "is rejected at admission."),
            },
            "representative_valid_result": {
                "status": "absent",
                "present": False,
                "qualifies": False,
                "note": (
                    "No rights-cleared representative item, output or scored "
                    "result exists. A missing result is never promoted."),
            },
        },
        "required_results": required_results(),
        "adverse": {
            "invalid_declarations": adverse,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("dataset_placeholder"),
        },
        "control_probe": control,
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "no_missing_result_qualifies": True,
        "no_result_qualifies": True,
        "source_evidence_statements": list(SOURCE_EVIDENCE_STATEMENTS),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "board_full_file_hashed": False,
        "artifact_pins": artifact_pins(),
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "generated_by": "run.py --all",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
