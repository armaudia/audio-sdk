#!/usr/bin/env python3
"""Publish only successful CI archives and checksums after environment approval."""
import hashlib,os,subprocess
from pathlib import Path

root=Path('release-assets')
archives=sorted(p for p in root.rglob('*') if p.is_file() and (p.name.endswith('.tar.gz') or p.suffix=='.zip'))
if len(archives)!=2:
    raise SystemExit('Both platform archives are required')
assets=[]
for archive in archives:
    checksum=archive.with_name(archive.name+'.sha256')
    expected=checksum.read_text().split()[0]
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Release archive checksum mismatch')
    assets.extend([str(archive),str(checksum)])
tag=os.environ['TAG']
command=['gh','release','create',tag,'--verify-tag','--generate-notes',*assets]
if '-' in tag:command+=['--prerelease','--latest=false']
subprocess.run(command,check=True)
