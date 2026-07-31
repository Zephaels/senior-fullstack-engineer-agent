#!/usr/bin/env python3
from pathlib import Path
import argparse, datetime, json, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]; NAME='senior-fullstack-engineer-agent'
def run(cmd,allow_failure=False):
 cp=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
 return {'command':[str(x) for x in cmd],'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'ok':cp.returncode==0 or allow_failure}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',default=str(ROOT/'dist/rc-qualification.json')); ap.add_argument('--runner-command'); ap.add_argument('--runtime-runner-command'); a=ap.parse_args(); evidence=[]
 evidence.append({'gate':'release_validation',**run([sys.executable,'scripts/validate_release.py'])})
 evidence.append({'gate':'installer_unit_tests',**run([sys.executable,'-m','unittest','discover','-s','tests','-v'])})
 evidence.append({'gate':'bounded_autonomy_controls',**run([sys.executable,'scripts/qualify_autonomy.py'])})
 with tempfile.TemporaryDirectory(prefix='sfse-rcq-') as home:
  installer=[sys.executable,'scripts/sfse_installer.py']; plugin=ROOT/'plugins'/NAME
  evidence.append({'gate':'install_dry_run',**run(installer+['install','--source',str(plugin),'--home',home,'--dry-run'])})
  evidence.append({'gate':'install_apply',**run(installer+['install','--source',str(plugin),'--home',home])})
  evidence.append({'gate':'install_verify',**run(installer+['verify','--home',home])})
  evidence.append({'gate':'uninstall',**run(installer+['uninstall','--home',home])})
 source=ROOT/'source'/NAME; ee=source/'eval-engine/runners'; model=[]
 trigger=[sys.executable,str(ee/'run_trigger_evals.py')]
 behavior=[sys.executable,str(ee/'run_behavior_evals_v2.py')]
 regression=[sys.executable,str(ee/'run_regression_evals.py')]
 if a.runner_command: trigger+=['--runner-command',a.runner_command]; behavior+=['--runner-command',a.runner_command]
 if a.runtime_runner_command: behavior+=['--runtime-runner-command',a.runtime_runner_command]; regression+=['--runtime-runner-command',a.runtime_runner_command]
 model.append({'gate':'trigger_eval_probe',**run(trigger,allow_failure=True)})
 model.append({'gate':'behavior_eval_probe',**run(behavior,allow_failure=True)})
 model.append({'gate':'regression_eval_probe',**run(regression,allow_failure=True)})
 evidence.extend(model)
 real_model=bool(a.runner_command); real_runtime=bool(a.runtime_runner_command)
 blockers=[]
 if not real_model: blockers.append('real_model_red_green_evaluation')
 if not real_runtime: blockers.append('real_codex_plugin_runtime_regression')
 blockers += ['chatgpt_plugin_install','github_release','artifact_attestation']
 report={'version':(ROOT/'VERSION').read_text(encoding='utf-8').strip(),'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'RC_BLOCKED','ga_status':'GA_BLOCKED' if blockers else 'GA_GATE_CANDIDATE','environment':{'codex_cli':shutil.which('codex'),'github_cli':shutil.which('gh'),'python':sys.version.split()[0]},'evidence':evidence,'blockers':blockers,'rules':{'filesystem_install_is_not_runtime_discovery':True,'mock_is_not_model_eval':True,'prompt_concatenation_is_not_plugin_regression':True}}
 out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
 critical=all(x.get('ok',True) for x in evidence if x.get('gate') in {'release_validation','installer_unit_tests','bounded_autonomy_controls','install_apply','install_verify','uninstall'}); return 0 if critical else 1
if __name__=='__main__': raise SystemExit(main())
