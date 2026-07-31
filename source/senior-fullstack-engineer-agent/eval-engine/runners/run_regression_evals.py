#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]

def load_cases():
    out=[]
    for p in sorted((ROOT/'evals/regression').glob('*.json')):
        for c in json.loads(p.read_text(encoding='utf-8')).get('cases',[]): c=dict(c); c['_source']=str(p.relative_to(ROOT)); out.append(c)
    return out

def signature(case): return json.dumps({k:v for k,v in case.items() if k!='_source'},sort_keys=True,ensure_ascii=False)
def plugin_fingerprint(plugin):
    digest=hashlib.sha256()
    for path in sorted(plugin.rglob('*')):
        if path.is_file() and path.name not in {'MANIFEST.json','SBOM.spdx.json'}:
            digest.update(path.relative_to(plugin).as_posix().encode('utf-8')+b'\0'+path.read_bytes())
    return digest.hexdigest()
def input_fingerprint(case,plugin_hash): return hashlib.sha256((signature(case)+'\0'+plugin_hash).encode('utf-8')).hexdigest()

def write_report(path,report,total):
    completed=sum(1 for run in report['runs'] if run.get('result',{}).get('status')=='completed')
    report['cases_completed']=completed; report['cases_blocked']=total-completed
    if completed==total: report['status']='COMPLETED'
    elif completed: report['status']='PARTIAL_BLOCKED'
    else: report['status']='BLOCKED_NO_CODEX_RUNTIME_RUNNER'
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime-runner-command'); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--resume',action='store_true'); ap.add_argument('--prepare-only',action='store_true'); ap.add_argument('--timeout',type=int,default=900); ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/regression-run.json')); a=ap.parse_args(); cases=load_cases(); cases=cases[:a.limit or None]
    plugin=(ROOT.parents[1]/'plugins/senior-fullstack-engineer-agent').resolve(); plugin_hash=plugin_fingerprint(plugin); out=Path(a.output); by_id={c['id']:c for c in cases}
    report={'suite':'real-plugin-regression-v2','status':'BLOCKED_NO_CODEX_RUNTIME_RUNNER','plugin_path':str(plugin),'plugin_fingerprint':plugin_hash,'cases_requested':len(cases),'runs':[],'limitations':[]}
    if a.resume and out.exists():
        old=json.loads(out.read_text(encoding='utf-8')); rejected=0
        for run in old.get('runs',[]):
            prior=run.get('case',{}); current=by_id.get(prior.get('id'))
            fingerprint=input_fingerprint(current,plugin_hash) if current else None
            if current and run.get('input_fingerprint')==fingerprint and run.get('result',{}).get('status')=='completed': report['runs'].append({'case':current,'configuration':'regression','input_fingerprint':fingerprint,'result':run['result']})
            elif run.get('result',{}).get('status')=='completed': rejected+=1
        report['limitations'].append(f"Resumed {len(report['runs'])} completed cases from the existing report.")
        if rejected: report['limitations'].append(f"Rejected {rejected} stale completed cases.")
    completed={run['case']['id'] for run in report['runs']}
    if a.prepare_only: report['limitations'].append('Preparation-only mode: pending cases were not sent to a Codex runtime.')
    elif not a.runtime_runner_command: report['limitations'].append('Regression requires a fresh Codex session with Plugin discovery and forceReload. Prompt concatenation is not accepted as runtime evidence.')
    else:
        for case in cases:
            if case['id'] in completed: continue
            req={'task_type':'codex-plugin-regression','prompt':case['prompt'],'plugin_path':str(plugin),'force_reload':True,'new_session':True,'response_contract':{'selected_skills':['skill-name'],'output':'text','tool_calls':[],'changed_files':[]}}
            report['runs'].append({'case':case,'configuration':'regression','input_fingerprint':input_fingerprint(case,plugin_hash),'result':invoke_runner(a.runtime_runner_command,req,a.timeout)})
            write_report(out,report,len(cases))
    order={case['id']:i for i,case in enumerate(cases)}; report['runs'].sort(key=lambda run:order[run['case']['id']]); report['limitations']=list(dict.fromkeys(report['limitations']))
    write_report(out,report,len(cases)); print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['status'] in {'COMPLETED','PARTIAL_BLOCKED'} else 2)
if __name__=='__main__': main()
