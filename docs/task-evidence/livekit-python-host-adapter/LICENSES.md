<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing

This task-local evidence package is licensed under the Apache License 2.0.
The repository's canonical licence text is `LICENSES/Apache-2.0.txt` at the
pinned SDK base. The package contains only Markdown, JSON and Python source.
Generated JSON artifacts carry adjacent `.license` sidecars with the SPDX
file copyright and licence identifier.

No LiveKit package, wheel, sdist, lock file, source file, binary, model,
patch, licence text or media file is copied, vendored or redistributed.
No host licence conclusion is asserted: no LiveKit package or licence record
is present, and none was downloaded, installed or inspected in this task.

No audio recording, reference, transcript, participant media, room token or
derived media is present. No third-party asset is bundled.

The package's Python modules are standard-library-only and must remain so.
`reference.py` performs fixed path probes and module-spec checks; it does not
import a host package, load the SDK native library or execute audio.

The `.license` sidecars in this directory cover `SOURCES.sha256`,
`contract.json`, `report.json` and `report.json.sha256`. `README.md`,
`LICENSES.md`, `run.py`, `reference.py`, `verify.py` and `test_reference.py`
carry SPDX headers in the file body. This package is covered by the repository
`REUSE.toml` `docs/**` rule and is checked by `python3 -m reuse lint`.
