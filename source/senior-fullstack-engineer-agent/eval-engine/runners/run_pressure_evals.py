#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]
def load_cases():
 out=[]
 for p in sorted((ROOT/'evals/pressure').glob('*.json')):
  d=json.loads(p.read_text(encoding='utf-8'))
  for c in d.get('cases',[]): c=dict(c); c['_source']=str(p.relative_to(ROOT)); out.append(c)
 return out
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--runner-command'); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--timeout',type=int,default=600); ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/pressure-run.json')); a=ap.parse_args()
 cases=load_cases(); cases=cases[:a.limit or None]; contexts=json.loads((ROOT/'eval-engine/config/context-map.json').read_text())['contexts']; report={'suite':'pressure-v2','status':'COMPLETED' if a.runner_command else 'BLOCKED_NO_MODEL_RUNNER','cases_requested':len(cases),'runs':[],'limitations':[]}
 if not a.runner_command: report['limitations'].append('No external model runner supplied. No pressure score is claimed.')
 else:
  for case in cases:
   files=[]
   for skill in case.get('skills',[]): files.extend(contexts.get(skill,[]))
   files=sorted(set(files))
   req={'task_type':'pressure-eval','case_id':case['id'],'prompt':case['scenario'],'context_files':[str((ROOT/f).resolve()) for f in files],'pressures':case.get('pressures',[])}
   report['runs'].append({'case_id':case['id'],'status':'completed',**invoke_runner(a.runner_command,req,a.timeout)})
 out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['status']=='COMPLETED' else 2)
if __name__=='__main__': main()
