#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]

def load_cases():
    out=[]
    for p in sorted((ROOT/'evals/pressure').glob('*.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        for c in d.get('cases',[]): c=dict(c); c['_source']=str(p.relative_to(ROOT)); out.append(c)
    return out

def fixture_path(case):
    raw=case.get('workspace_fixture')
    if not raw: return None
    path=(ROOT/raw).resolve()
    try: path.relative_to(ROOT.resolve())
    except ValueError: raise ValueError(f"workspace fixture escapes the Skill source root: {raw}")
    if not path.is_dir(): raise ValueError(f"workspace fixture is not a directory: {raw}")
    return path

def fixture_files(case):
    path=fixture_path(case)
    return [p for p in sorted(path.rglob('*')) if p.is_file()] if path else []

def signature(case): return json.dumps({k:v for k,v in case.items() if k!='_source'},sort_keys=True,ensure_ascii=False)
def input_fingerprint(case,files,runner_revision=''):
    digest=hashlib.sha256((signature(case)+'\0'+runner_revision).encode('utf-8'))
    for path in sorted(Path(p).resolve() for p in files): digest.update(str(path).encode('utf-8')+b'\0'+path.read_bytes())
    return digest.hexdigest()

def write_report(path,report,total):
    completed=sum(1 for run in report['runs'] if run.get('result',{}).get('status')=='completed')
    report['cases_completed']=completed; report['cases_blocked']=total-completed
    if completed==total: report['status']='COMPLETED'
    elif completed: report['status']='PARTIAL_BLOCKED'
    else: report['status']='BLOCKED_NO_MODEL_RUNNER'
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runner-command'); ap.add_argument('--runner-revision',default='',help='Stable revision identifier for the external runner contract; changes invalidate resume entries.'); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--case',action='append',default=[],help='Run only this case ID; repeat for bounded batches.'); ap.add_argument('--resume',action='store_true'); ap.add_argument('--prepare-only',action='store_true'); ap.add_argument('--timeout',type=int,default=600); ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/pressure-run.json')); a=ap.parse_args()
    cases=load_cases()
    if a.case:
        available={case['id'] for case in cases}; unknown=sorted(set(a.case)-available)
        if unknown: ap.error(f"unknown case id(s): {', '.join(unknown)}")
        selected=set(a.case); cases=[case for case in cases if case['id'] in selected]
    cases=cases[:a.limit or None]; contexts=json.loads((ROOT/'eval-engine/config/context-map.json').read_text(encoding='utf-8'))['contexts']; out=Path(a.output); by_id={c['id']:c for c in cases}
    report={'suite':'pressure-v2','status':'BLOCKED_NO_MODEL_RUNNER','cases_requested':len(cases),'runner_revision':a.runner_revision or None,'runs':[],'limitations':[]}
    if a.resume and out.exists():
        old=json.loads(out.read_text(encoding='utf-8')); rejected=0
        for run in old.get('runs',[]):
            cid=run.get('case_id'); current=by_id.get(cid); old_case=run.get('case')
            result=run.get('result',run)
            files=[]
            if current:
                for skill in current.get('skills',[]): files.extend(ROOT/f for f in contexts.get(skill,[]))
            fingerprint=input_fingerprint(current,sorted(set(files))+fixture_files(current),a.runner_revision) if current else None
            if current and result.get('status')=='completed' and run.get('input_fingerprint')==fingerprint: report['runs'].append({'case_id':cid,'case':current,'input_fingerprint':fingerprint,'result':result})
            elif result.get('status')=='completed': rejected+=1
        report['limitations'].append(f"Resumed {len(report['runs'])} completed cases from the existing report.")
        if rejected: report['limitations'].append(f"Rejected {rejected} stale or unverifiable completed cases.")
    completed={run['case_id'] for run in report['runs']}
    if a.prepare_only: report['limitations'].append('Preparation-only mode: pending cases were not sent to a model runner.')
    elif not a.runner_command: report['limitations'].append('No external model runner supplied. No pressure score is claimed.')
    else:
        for case in cases:
            if case['id'] in completed: continue
            files=[]
            for skill in case.get('skills',[]): files.extend(contexts.get(skill,[]))
            req={'task_type':'pressure-eval','case_id':case['id'],'prompt':case['scenario'],'context_files':[str((ROOT/f).resolve()) for f in sorted(set(files))],'pressures':case.get('pressures',[])}
            fixture=fixture_path(case)
            if fixture: req['workspace_fixture']=str(fixture)
            req['runner_revision']=a.runner_revision or None
            report['runs'].append({'case_id':case['id'],'case':case,'input_fingerprint':input_fingerprint(case,[ROOT/f for f in sorted(set(files))]+fixture_files(case),a.runner_revision),'result':invoke_runner(a.runner_command,req,a.timeout)})
            write_report(out,report,len(cases))
    order={case['id']:i for i,case in enumerate(cases)}; report['runs'].sort(key=lambda run:order[run['case_id']]); report['limitations']=list(dict.fromkeys(report['limitations']))
    write_report(out,report,len(cases)); print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['status'] in {'COMPLETED','PARTIAL_BLOCKED'} else 2)
if __name__=='__main__': main()
