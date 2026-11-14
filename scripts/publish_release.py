#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Publish only successful CI archives and checksums after environment approval."""
import hashlib,os,subprocess,json
from pathlib import Path

decision=json.loads((Path(__file__).resolve().parents[1]/'licensing/decision.json').read_text())
if not decision.get('approved_for_publication'):
    raise SystemExit('Public outbound licensing has not been approved')
root=Path('release-assets')
archives=sorted(p for p in root.rglob('*') if p.is_file() and (p.name.endswith('.tar.gz') or p.suffix=='.zip'))
if len(archives)!=4:
    raise SystemExit('Linux, macOS, Windows and WebAssembly archives are required')
assets=[]
for archive in archives:
    checksum=archive.with_name(archive.name+'.sha256')
    expected=checksum.read_text().split()[0]
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Release archive checksum mismatch')
    assets.extend([str(archive),str(checksum)])
assets.extend(str(path) for path in sorted(root.rglob('*.spdx')))
tag=os.environ['TAG']
command=['gh','release','create',tag,'--verify-tag','--generate-notes','--draft',*assets]
if '-' in tag:command+=['--prerelease','--latest=false']
subprocess.run(command,check=True)
subprocess.run(['gh','release','edit',tag,'--draft=false','--latest='+('false' if '-' in tag else 'true')],check=True)
