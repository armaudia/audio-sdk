#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Apply and verify repository settings after bootstrap CI succeeds."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--gh',default='gh')
 p.add_argument('--repo',required=True,choices=['audio-sdk','audio-bench','audio-pro'])
 p.add_argument('--allow-private-plan-limit',action='store_true')
 args=p.parse_args(); root=Path(__file__).resolve().parents[1]
 full='armaudia/'+args.repo
 def api(method,path,payload=None,missing=False):
  command=[args.gh,'api','--method',method,'--header','X-GitHub-Api-Version: 2026-03-10',path]
  if payload is not None:command+=['--input','-']
  result=subprocess.run(command,input=json.dumps(payload) if payload is not None else None,text=True,capture_output=True)
  if result.returncode:
   if missing and 'HTTP 404' in result.stderr:return None
   raise RuntimeError(result.stderr.strip())
  return json.loads(result.stdout) if result.stdout.strip() else None
 repo=api('GET','repos/'+full)
 expected=args.repo=='audio-pro'
 if repo['private']!=expected:raise RuntimeError('Repository visibility does not match the authorized publication scope')
 if not repo.get('permissions',{}).get('admin'):raise RuntimeError('Repository administration permission is required')
 sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
 checks=api('GET',f'repos/{full}/commits/{sha}/check-runs')['check_runs']
 quality=[c for c in checks if c['name']=='quality' and c['app']['slug']=='github-actions']
 if not quality or quality[0]['conclusion']!='success':raise RuntimeError('The current commit must pass GitHub Actions quality before protection is activated')
 settings={'default_branch':'main','allow_squash_merge':True,'allow_merge_commit':False,
           'allow_rebase_merge':False,'allow_auto_merge':False,'delete_branch_on_merge':True,
           'has_wiki':False,'has_projects':False,'allow_update_branch':True}
 api('PATCH','repos/'+full,settings)
 api('PUT',f'repos/{full}/immutable-releases')
 immutability=api('GET',f'repos/{full}/immutable-releases')
 if not immutability.get('enabled'):raise RuntimeError('Release immutability readback mismatch')
 api('PUT',f'repos/{full}/actions/permissions',{'enabled':True,'allowed_actions':'selected'})
 api('PUT',f'repos/{full}/actions/permissions/selected-actions',
     {'github_owned_allowed':True,'verified_allowed':False,'patterns_allowed':[]})
 api('PUT',f'repos/{full}/actions/permissions/workflow',
     {'default_workflow_permissions':'read','can_approve_pull_request_reviews':False})
 api('PUT',f'repos/{full}/actions/permissions/fork-pr-contributor-approval',
     {'approval_policy':'all_external_contributors'})
 if not expected:
  api('PUT',f'repos/{full}/private-vulnerability-reporting')
  api('PATCH','repos/'+full,{'security_and_analysis':{
   'secret_scanning':{'status':'enabled'},'secret_scanning_push_protection':{'status':'enabled'}}})
 if expected and args.allow_private_plan_limit:
  organization=api('GET','orgs/armaudia')
  if organization.get('plan',{}).get('name')=='free':
   report={'repository':api('GET','repos/'+full),
           'actions':api('GET',f'repos/{full}/actions/permissions/workflow'),
           'protection_status':'unavailable_on_github_free_private_repository',
           'accepted_by_owner':True,'rulesets_enforced':False,
           'commercial_release_workflow':'disabled',
           'required_resolution':'GitHub Team/Enterprise for organization-private branch protections'}
   output=root/'build/github-settings.json';output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')
   print('Verified private repository and Actions permissions; branch protections remain unavailable on the accepted Free plan')
   return
 existing=api('GET',f'repos/{full}/rulesets')
 expected_rules=[]
 for name in ['main-ruleset.json','tag-ruleset.json','release-tag-creators.json']:
  rule=json.loads((root/'.github'/name).read_text())
  if name=='main-ruleset.json':rule['rules'][-1]['parameters']['required_status_checks'][0]['integration_id']=quality[0]['app']['id']
  match=next((r for r in existing if r['name']==rule['name']),None)
  path=f'repos/{full}/rulesets'+('/'+str(match['id']) if match else '')
  written=api('PUT' if match else 'POST',path,rule)
  observed=api('GET',f'repos/{full}/rulesets/{written["id"]}')
  for key in ['name','target','enforcement','conditions']:
   if observed[key]!=rule[key]:raise RuntimeError('Ruleset readback mismatch: '+key)
  by_type={r['type']:r for r in observed['rules']}
  if set(by_type)!={r['type'] for r in rule['rules']}:raise RuntimeError('Ruleset rule readback mismatch')
  for expected_rule in rule['rules']:
   parameters=by_type[expected_rule['type']].get('parameters',{})
   for key,value in expected_rule.get('parameters',{}).items():
    if parameters.get(key)!=value:raise RuntimeError('Ruleset parameter readback mismatch: '+key)
  normalize=lambda actors: sorted((actor['actor_type'],actor['bypass_mode']) for actor in actors)
  if normalize(observed['bypass_actors'])!=normalize(rule['bypass_actors']):raise RuntimeError('Unexpected bypass actors')
  expected_rules.append(observed)
 user=api('GET','user')
 environment=api('PUT',f'repos/{full}/environments/release',{
  'wait_timer':0,'prevent_self_review':False,'can_admins_bypass':False,
  'reviewers':[{'type':'User','id':user['id']}],
  'deployment_branch_policy':{'protected_branches':False,'custom_branch_policies':True}})
 policies=api('GET',f'repos/{full}/environments/release/deployment-branch-policies')['branch_policies']
 if not any(x['name']=='v*' and x.get('type')=='tag' for x in policies):
  api('POST',f'repos/{full}/environments/release/deployment-branch-policies',{'name':'v*','type':'tag'})
 environment=api('GET',f'repos/{full}/environments/release')
 reviewers=[reviewer.get('reviewer',{}).get('id') for protection in environment['protection_rules']
            if protection['type']=='required_reviewers' for reviewer in protection.get('reviewers',[])]
 if user['id'] not in reviewers:raise RuntimeError('Release reviewer readback mismatch')
 branch_policies=api('GET',f'repos/{full}/environments/release/deployment-branch-policies')['branch_policies']
 if not any(x['name']=='v*' and x.get('type')=='tag' for x in branch_policies):raise RuntimeError('Release tag policy readback mismatch')
 action_policy=api('GET',f'repos/{full}/actions/permissions')
 if not action_policy['enabled'] or action_policy['allowed_actions']!='selected':raise RuntimeError('Actions allowlist readback mismatch')
 report={'immutable_releases':immutability, 'repository':api('GET','repos/'+full), 'rulesets':expected_rules,
         'actions':api('GET',f'repos/{full}/actions/permissions/workflow'),
         'release_environment':api('GET',f'repos/{full}/environments/release')}
 for key,value in settings.items():
  if report['repository'].get(key)!=value:raise RuntimeError('Repository setting readback mismatch: '+key)
 if report['actions']['default_workflow_permissions']!='read' or report['actions']['can_approve_pull_request_reviews']:
  raise RuntimeError('Actions permission readback mismatch')
 output=root/'build/github-settings.json';output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')
 print(f'Verified visibility, settings, rulesets and release environment: https://github.com/{full}')

if __name__=='__main__':
 try:main()
 except (RuntimeError,subprocess.CalledProcessError) as error:sys.exit(str(error))
