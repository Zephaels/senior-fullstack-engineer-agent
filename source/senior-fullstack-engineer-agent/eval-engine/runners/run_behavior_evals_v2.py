#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]

def load_cases():
    out=[]
    for p in sorted((ROOT/'evals/behavior').glob('*_behavior_evals.json')):
        for c in json.loads(p.read_text(encoding='utf-8')).get('cases',[]):
            c=dict(c); c['_source']=str(p.relative_to(ROOT)); out.append(c)
    return out

def case_signature(case):
    return json.dumps({k:v for k,v in case.items() if k!='_source'},sort_keys=True,ensure_ascii=False)

def input_fingerprint(case,configuration,files):
    digest=hashlib.sha256((case_signature(case)+'\0'+configuration).encode('utf-8'))
    for path in sorted(Path(p).resolve() for p in files):
        digest.update(str(path).encode('utf-8')); digest.update(b'\0'); digest.update(path.read_bytes())
    return digest.hexdigest()

def plugin_files(plugin):
    return [p for p in sorted(plugin.rglob('*')) if p.is_file() and p.name not in {'MANIFEST.json','SBOM.spdx.json'}]

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

def write_report(path,report,expected_keys):
    completed={
        (run['case']['id'],run['configuration']) for run in report['runs']
        if run.get('result',{}).get('status')=='completed'
    }
    report['runs_completed']=len(completed)
    report['runs_blocked']=len(expected_keys-completed)
    if len(completed)==len(expected_keys): report['status']='COMPLETED'
    elif completed: report['status']='PARTIAL_BLOCKED'
    else: report['status']='BLOCKED_NO_MODEL_RUNNER'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runner-command')
    ap.add_argument('--runtime-runner-command',help='Required for true Plugin regression; must run a fresh Codex session against plugin_path.')
    ap.add_argument('--include-regression',action='store_true',help='Also run each case through the real Plugin runtime. The dedicated regression suite remains the GA routing gate.')
    ap.add_argument('--case',action='append',default=[],dest='case_ids',help='Run only the named case. Repeat for a bounded multi-case batch.')
    ap.add_argument('--configuration',action='append',choices=('red','green'),default=[],help='Run only RED or GREEN; repeat to select both. Defaults to both.')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--retry',action='append',default=[],metavar='CASE[:CONFIG]',help='Discard and rerun one case or case/configuration when resuming.')
    ap.add_argument('--prepare-only',action='store_true')
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/behavior-run.json'))
    a=ap.parse_args(); cases=load_cases()
    if a.case_ids:
        available={case['id'] for case in cases}
        unknown=sorted(set(a.case_ids)-available)
        if unknown: ap.error(f"unknown behavior case(s): {', '.join(unknown)}")
        selected=set(a.case_ids)
        cases=[case for case in cases if case['id'] in selected]
    cases=cases[:a.limit or None]
    contexts=json.loads((ROOT/'eval-engine/config/context-map.json').read_text(encoding='utf-8'))['contexts']
    out=Path(a.output); by_id={case['id']:case for case in cases}
    plugin=(ROOT.parents[1]/'plugins'/'senior-fullstack-engineer-agent').resolve()
    include_regression=a.include_regression or bool(a.runtime_runner_command)
    base_configurations=tuple(dict.fromkeys(a.configuration)) or ('red','green')
    configurations=base_configurations + (('regression',) if include_regression else ())
    expected_keys={(case['id'],config) for case in cases for config in configurations}
    report={'suite':'isolated-behavior-v2','status':'BLOCKED_NO_MODEL_RUNNER','cases_requested':len(cases),'runs_expected':len(expected_keys),'runs':[],'limitations':[]}
    if a.resume and out.exists():
        previous=json.loads(out.read_text(encoding='utf-8')); rejected=0
        retry_keys=set()
        retry_cases=set()
        for item in a.retry:
            if ':' in item: retry_keys.add(tuple(item.split(':',1)))
            else: retry_cases.add(item)
        for run in previous.get('runs',[]):
            old=run.get('case',{}); current=by_id.get(old.get('id')); config=run.get('configuration')
            forced=old.get('id') in retry_cases or (old.get('id'),config) in retry_keys
            files=fixture_files(current) if current else []
            if current and config=='green': files.extend(ROOT/f for f in contexts.get(current['skill'],[]))
            elif current and config=='regression': files.extend(plugin_files(plugin))
            fingerprint=input_fingerprint(current,config,files) if current and config in configurations else None
            if current and config in configurations and not forced and run.get('result',{}).get('status')=='completed' and run.get('input_fingerprint')==fingerprint:
                report['runs'].append({'case':current,'configuration':config,'input_fingerprint':fingerprint,'result':run['result']})
            elif run.get('result',{}).get('status')=='completed': rejected+=1
        report['limitations'].append(f"Resumed {len(report['runs'])} completed runs from the existing report.")
        if rejected: report['limitations'].append(f"Rejected {rejected} stale completed runs.")
    completed={(run['case']['id'],run['configuration']) for run in report['runs']}
    if a.prepare_only:
        report['limitations'].append('Preparation-only mode: pending runs were not sent to a model runner.')
    else:
        for case in cases:
            for config in base_configurations:
                key=(case['id'],config)
                if key in completed: continue
                if not a.runner_command:
                    report['limitations'].append(f'{case["id"]}/{config}: no model runner')
                    continue
                context_files=[] if config=='red' else contexts.get(case['skill'],[])
                fixture=fixture_path(case)
                req={'task_type':'behavior-eval','configuration':config,'case_id':case['id'],'prompt':case['prompt'],'context_files':[str((ROOT/f).resolve()) for f in context_files], 'expected_output':case.get('expected_output'),'expectations':case.get('expectations',[])}
                if fixture: req['workspace_fixture']=str(fixture)
                fingerprint=input_fingerprint(case,config,[ROOT/f for f in context_files]+fixture_files(case))
                report['runs'].append({'case':case,'configuration':config,'input_fingerprint':fingerprint,'result':invoke_runner(a.runner_command,req,a.timeout)})
                write_report(out,report,expected_keys)
            if not include_regression: continue
            key=(case['id'],'regression')
            if key in completed: continue
            if a.runtime_runner_command:
                req={'task_type':'plugin-runtime-regression','configuration':'regression','case_id':case['id'],'prompt':case['prompt'],'plugin_path':str((ROOT.parents[1]/'plugins'/'senior-fullstack-engineer-agent').resolve()),'force_reload':True,'expected_skill':case['skill']}
                fixture=fixture_path(case)
                if fixture: req['workspace_fixture']=str(fixture)
                report['runs'].append({'case':case,'configuration':'regression','input_fingerprint':input_fingerprint(case,'regression',plugin_files(plugin)+fixture_files(case)),'result':invoke_runner(a.runtime_runner_command,req,a.timeout)})
                write_report(out,report,expected_keys)
            else:
                report['limitations'].append(f'{case["id"]}/regression: no real Codex Plugin runtime runner')
    order={(case['id'],config):index*len(configurations)+offset for index,case in enumerate(cases) for offset,config in enumerate(configurations)}
    report['runs'].sort(key=lambda run:order[(run['case']['id'],run['configuration'])])
    report['limitations']=list(dict.fromkeys(report['limitations']))
    write_report(out,report,expected_keys); print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status'] in {'COMPLETED','PARTIAL_BLOCKED'} else 2)
if __name__=='__main__': main()
