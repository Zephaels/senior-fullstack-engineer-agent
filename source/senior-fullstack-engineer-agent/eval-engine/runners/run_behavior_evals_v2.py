#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]

def load_cases():
    out=[]
    for p in sorted((ROOT/'evals/behavior').glob('*_behavior_evals.json')):
        for c in json.loads(p.read_text(encoding='utf-8')).get('cases',[]):
            c=dict(c); c['_source']=str(p.relative_to(ROOT)); out.append(c)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runner-command')
    ap.add_argument('--runtime-runner-command',help='Required for true Plugin regression; must run a fresh Codex session against plugin_path.')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/behavior-run.json'))
    a=ap.parse_args(); cases=load_cases(); cases=cases[:a.limit or None]
    contexts=json.loads((ROOT/'eval-engine/config/context-map.json').read_text(encoding='utf-8'))['contexts']
    report={'suite':'isolated-behavior-v2','status':'COMPLETED','cases_requested':len(cases),'runs':[],'blocked_configurations':[]}
    for case in cases:
        for config in ['red','green']:
            if not a.runner_command:
                report['blocked_configurations'].append({'case_id':case['id'],'configuration':config,'reason':'no model runner'}); continue
            files=[] if config=='red' else contexts.get(case['skill'],[])
            req={'task_type':'behavior-eval','configuration':config,'case_id':case['id'],'prompt':case['prompt'],'context_files':[str((ROOT/f).resolve()) for f in files], 'expected_output':case.get('expected_output'),'expectations':case.get('expectations',[])}
            report['runs'].append({'case':case,'configuration':config,'result':invoke_runner(a.runner_command,req,a.timeout)})
        if a.runtime_runner_command:
            req={'task_type':'plugin-runtime-regression','configuration':'regression','case_id':case['id'],'prompt':case['prompt'],'plugin_path':str((ROOT.parents[1]/'plugins'/'senior-fullstack-engineer-agent').resolve()),'force_reload':True,'expected_skill':case['skill']}
            report['runs'].append({'case':case,'configuration':'regression','result':invoke_runner(a.runtime_runner_command,req,a.timeout)})
        else:
            report['blocked_configurations'].append({'case_id':case['id'],'configuration':'regression','reason':'no real Codex Plugin runtime runner'})
    if report['blocked_configurations']:
        report['status']='PARTIAL_BLOCKED' if report['runs'] else 'BLOCKED_NO_MODEL_RUNNER'
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status'] in {'COMPLETED','PARTIAL_BLOCKED'} else 2)
if __name__=='__main__': main()
