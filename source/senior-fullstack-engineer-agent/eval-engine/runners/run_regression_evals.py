#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]
def load_cases():
 out=[]
 for p in sorted((ROOT/'evals/regression').glob('*.json')):
  for c in json.loads(p.read_text(encoding='utf-8')).get('cases',[]): c=dict(c); c['_source']=str(p.relative_to(ROOT)); out.append(c)
 return out
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--runtime-runner-command'); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--timeout',type=int,default=900); ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/regression-run.json')); a=ap.parse_args(); cases=load_cases(); cases=cases[:a.limit or None]
 plugin=(ROOT.parents[1]/'plugins/senior-fullstack-engineer-agent').resolve(); report={'suite':'real-plugin-regression-v2','status':'COMPLETED' if a.runtime_runner_command else 'BLOCKED_NO_CODEX_RUNTIME_RUNNER','plugin_path':str(plugin),'cases_requested':len(cases),'runs':[],'limitations':[]}
 if not a.runtime_runner_command: report['limitations'].append('Regression requires a fresh Codex session with Plugin discovery and forceReload. Prompt concatenation is not accepted as runtime evidence.')
 else:
  for case in cases:
   req={'task_type':'codex-plugin-regression','prompt':case['prompt'],'plugin_path':str(plugin),'force_reload':True,'new_session':True,'response_contract':{'selected_skills':['skill-name'],'output':'text','tool_calls':[],'changed_files':[]}}
   report['runs'].append({'case':case,'configuration':'regression','result':invoke_runner(a.runtime_runner_command,req,a.timeout)})
 out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['status']=='COMPLETED' else 2)
if __name__=='__main__': main()
