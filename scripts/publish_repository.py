#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Audit the complete Git history and bootstrap exactly one authorized repository."""
import argparse,json,re,shlex,subprocess,sys
from pathlib import Path


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--gh',default='gh')
 p.add_argument('--apply',action='store_true',help='Create the repository if needed and push main after checks')
 args=p.parse_args()
 root=Path(__file__).resolve().parents[1]
 if root.name not in ('audio-sdk','audio-bench','audio-pro'):raise SystemExit('Unexpected source repository')
 private=root.name=='audio-pro';full='armaudia/'+root.name
 def git(*command):return subprocess.check_output(['git',*command],cwd=root,text=True).strip()
 if git('status','--porcelain'):raise SystemExit('Commit or resolve the working tree before publication')
 forbidden=[]
 for item in git('rev-list','--objects','--all').splitlines():
  parts=item.split(' ',1)
  if len(parts)!=2:continue
  sha,path=parts
  if git('cat-file','-t',sha)!='blob':continue
  if Path(path).suffix.lower() in ('.onnx','.f32','.pem','.key','.p12') or Path(path).name=='.env':forbidden.append(path)
  data=subprocess.check_output(['git','cat-file','blob',sha],cwd=root)
  patterns=[rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'github_pat_[A-Za-z0-9_]{40,}',
            rb'AKIA[A-Z0-9]{16}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
  if any(re.search(pattern,data) for pattern in patterns):forbidden.append(path)
 if forbidden:raise SystemExit('Review protected assets/secret patterns in history: '+', '.join(sorted(set(forbidden))))
 revision=git('rev-parse','HEAD')
 print(json.dumps({'repository':full,'private':private,'source_revision':revision,'history_audit':'passed'},indent=2),flush=True)
 if not args.apply:return
 if not private:
  decision=json.loads((root/'licensing/decision.json').read_text())
  if not decision.get('approved_for_publication'):raise RuntimeError('Public outbound licensing has not been approved')
 def api(method,path,payload=None,missing=False):
  command=[args.gh,'api','--method',method,'--header','X-GitHub-Api-Version: 2026-03-10',path]
  if payload is not None:command+=['--input','-']
  result=subprocess.run(command,input=json.dumps(payload) if payload is not None else None,text=True,capture_output=True)
  if result.returncode:
   if missing and 'HTTP 404' in result.stderr:return None
   raise RuntimeError(result.stderr.strip())
  return json.loads(result.stdout) if result.stdout.strip() else None
 repo=api('GET','repos/'+full,missing=True)
 if repo is None:
  repo=api('POST','orgs/armaudia/repos',{'name':root.name,'private':private,'auto_init':False,
   'description':{'audio-sdk':'Fixed-rate C11 audio processing SDK and provider conformance',
                  'audio-bench':'Reproducible synthetic audio evaluation and offline evidence reports',
                  'audio-pro':'Private rights-gated processor engineering'}[root.name],
   'has_wiki':False,'has_projects':False})
 if repo['private']!=private:raise RuntimeError('Existing repository visibility differs; investigate before changing it')
 if not repo.get('permissions',{}).get('admin'):raise RuntimeError('Repository administration access is required')
 remote='https://github.com/'+full+'.git'
 origins=git('remote').splitlines()
 if 'origin' in origins:
  if git('remote','get-url','origin')!=remote:raise RuntimeError('Refusing to replace an existing origin')
 else:subprocess.run(['git','remote','add','origin',remote],cwd=root,check=True)
 helper='!'+shlex.quote(args.gh)+' auth git-credential'
 subprocess.run(['git','-c','credential.helper=','-c','credential.helper='+helper,
                 'push','--set-upstream','origin','HEAD:refs/heads/main'],cwd=root,check=True)
 observed=api('GET',f'repos/{full}/git/ref/heads/main')
 if observed['object']['sha']!=revision:raise RuntimeError('Published branch does not match the audited source revision')
 print('Published and verified https://github.com/'+full)
 print('Wait for CI quality to pass, then run scripts/github_admin.py for this repository.')

if __name__=='__main__':
 try:main()
 except (RuntimeError,subprocess.CalledProcessError) as error:sys.exit(str(error))
