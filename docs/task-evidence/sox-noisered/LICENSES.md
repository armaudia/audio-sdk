<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License notices for the SoX `noisered` evidence package

All files in this task-local directory are original task evidence under
Apache-2.0, with the copyright and SPDX identifiers in each file header or in
the adjacent `.license` sidecars. No SoX source, binary, header, archive, noise
profile, audio asset or third-party package is vendored, downloaded, loaded or
executed here, so no third-party license text is reproduced in this directory.

The upstream SoX project is commonly distributed under GPL-2.0-or-later with
optional library-dependent configurations. That statement is context only: the
exact source revision, archive digest, build ID and build licensing
configuration are not pinned in this package and are recorded as blocker
`XB-01`. A future opt-in intake must stage the exact upstream notices and a
reviewed build-license configuration before any implementation is qualified.

`report.json`, `report.json.sha256`, `SOURCES.sha256` and `contract.json` are
generated artifacts. Their `.license` sidecars carry the same Apache-2.0
notice as the source files. REUSE configuration at the SDK root covers
`docs/**` as aggregate Apache-2.0; no shared licensing file is changed.
