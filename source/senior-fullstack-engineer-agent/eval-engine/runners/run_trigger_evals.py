#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import invoke_runner
ROOT=Path(__file__).resolve().parents[2]

def load_catalog(path): return json.loads(Path(path).read_text(encoding='utf-8'))['skills']

def collect_cases(root):
    cases=[]
    router=root/'evals/trigger/router_trigger_evals.json'
    sources=[('senior-fullstack-engineer-agent',router)]
    for p in sorted((root/'workflows').glob('*/evals/trigger_evals.json')):
        sources.append((p.parent.parent.name,p))
    for skill,p in sources:
        for idx,c in enumerate(json.loads(p.read_text(encoding='utf-8')),1):
            case={'id':c.get('id',f'T-{skill}-{idx:03d}'),'prompt':c.get('query') or c.get('prompt'),'target_skill':skill,'should_trigger':bool(c['should_trigger']),'source':str(p.relative_to(root))}
            if c.get('allowed_companion_skills'):
                case['allowed_companion_skills']=sorted(set(c['allowed_companion_skills']))
            cases.append(case)
    return cases

def same_case_definition(previous,current):
    keys=('id','prompt','target_skill','should_trigger','allowed_companion_skills')
    return all(previous.get(key)==current.get(key) for key in keys)

def canonical_catalog(catalog):
    return [{'name':row['name'],'description':row['description']} for row in catalog]

def digest(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

def catalog_fingerprint(catalog):
    return digest(canonical_catalog(catalog))

def case_fingerprint(catalog,case):
    return digest({'catalog':canonical_catalog(catalog),'case':case})

def suite_fingerprint(catalog,cases):
    return digest({'catalog':canonical_catalog(catalog),'cases':cases})

def write_report(path,report):
    completed=sum(1 for run in report['runs'] if run.get('result',{}).get('status')=='completed')
    report['cases_completed']=completed
    report['cases_blocked']=report['cases_requested']-completed
    if completed==report['cases_requested']:
        report['status']='COMPLETED'
    elif not report.get('runner_configured') and completed:
        report['status']='PARTIAL_BLOCKED'
    elif not report.get('runner_configured'):
        report['status']='BLOCKED_NO_MODEL_RUNNER'
    elif completed:
        report['status']='PARTIAL_BLOCKED'
    else:
        report['status']='BLOCKED_RUNNER_ERRORS'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--catalog',default=str(ROOT/'eval-engine/catalog/skill-catalog.json'))
    ap.add_argument('--runner-command')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--batch-size',type=int,default=1,help='Evaluate this many independent prompts per model call.')
    ap.add_argument('--resume',action='store_true',help='Keep completed cases from an existing output and retry only missing or failed cases.')
    ap.add_argument('--prepare-only',action='store_true',help='Normalize an existing report against the current official case set without invoking a model runner.')
    ap.add_argument('--timeout',type=int,default=300)
    ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/trigger-run.json'))
    a=ap.parse_args(); cases=collect_cases(ROOT); cases=cases[:a.limit or None]; catalog=load_catalog(a.catalog); out=Path(a.output)
    fingerprint=suite_fingerprint(catalog,cases)
    catalog_hash=catalog_fingerprint(catalog)
    report={'suite':'metadata-first-trigger-v2','status':'COMPLETED' if a.runner_command else 'BLOCKED_NO_MODEL_RUNNER','suite_fingerprint':fingerprint,'catalog_fingerprint':catalog_hash,'catalog_size':len(catalog),'cases_requested':len(cases),'runs':[],'limitations':[],'runner_configured':bool(a.runner_command)}
    if a.resume and out.exists():
        previous=json.loads(out.read_text(encoding='utf-8'))
        current_by_id={case['id']:case for case in cases}
        provenance_matches=previous.get('catalog_fingerprint')==catalog_hash
        if not provenance_matches:
            prior_runs=previous.get('runs',[])
            prior_cases=[run.get('case',{}) for run in prior_runs]
            complete_prior_suite=(
                len(prior_cases)==previous.get('cases_requested')
                and len({case.get('id') for case in prior_cases})==len(prior_cases)
            )
            provenance_matches=(
                complete_prior_suite
                and suite_fingerprint(catalog,prior_cases)==previous.get('suite_fingerprint')
            )
        reusable=[
            run for run in previous.get('runs',[])
            if run.get('case',{}).get('id') in current_by_id
            and run.get('result',{}).get('status')=='completed'
            and same_case_definition(run['case'],current_by_id[run['case']['id']])
            and provenance_matches
        ]
        report['runs']=[
            {
                'case':current_by_id[run['case']['id']],
                'input_fingerprint':case_fingerprint(catalog,current_by_id[run['case']['id']]),
                'result':run['result'],
            }
            for run in reusable
        ]
        prior_completed=sum(1 for run in previous.get('runs',[]) if run.get('result',{}).get('status')=='completed')
        report['limitations'].append(f"Resumed {len(report['runs'])} completed cases from the existing report.")
        rejected=prior_completed-len(report['runs'])
        if rejected:
            report['limitations'].append(f"Rejected {rejected} stale completed cases whose definitions or suite provenance no longer match.")
    completed_ids={run['case']['id'] for run in report['runs']}
    pending=[case for case in cases if case['id'] not in completed_ids]
    if a.prepare_only:
        report['limitations'].append('Preparation-only mode: pending cases were not sent to a model runner.')
    elif not a.runner_command:
        report['limitations'].append('No external model runner supplied. No trigger metrics are claimed.')
    else:
        batch_size=max(1,a.batch_size)
        catalog_payload=[{'name':s['name'],'description':s['description']} for s in catalog]
        for start in range(0,len(pending),batch_size):
            batch=pending[start:start+batch_size]
            if batch_size==1:
                case=batch[0]
                req={'task_type':'skill-discovery','prompt':case['prompt'],'skills':catalog_payload,'response_contract':{'selected_skills':['skill-name'],'reason':'short reason'}}
                report['runs'].append({'case':case,'input_fingerprint':case_fingerprint(catalog,case),'result':invoke_runner(a.runner_command,req,a.timeout)})
                write_report(out,report)
                continue
            req={
                'task_type':'skill-discovery-batch',
                'cases':[{'id':case['id'],'prompt':case['prompt']} for case in batch],
                'skills':catalog_payload,
                'response_contract':{'results':[{'id':'case-id','selected_skills':['skill-name'],'reason':'short reason'}]},
            }
            batch_result=invoke_runner(a.runner_command,req,a.timeout)
            by_id={item.get('id'):item for item in batch_result.get('results',[])} if batch_result.get('status')=='completed' else {}
            for case in batch:
                item=by_id.get(case['id'])
                if item is None:
                    result={'status':'runner_error','error':batch_result.get('error','missing result id'),'batch_metadata':batch_result.get('runner_metadata')}
                else:
                    result={'status':'completed','selected_skills':item.get('selected_skills',[]),'reason':item.get('reason',''),'batch_metadata':batch_result.get('runner_metadata')}
                report['runs'].append({'case':case,'input_fingerprint':case_fingerprint(catalog,case),'result':result})
            write_report(out,report)
    order={case['id']:index for index,case in enumerate(cases)}
    report['runs'].sort(key=lambda run:order[run['case']['id']])
    write_report(out,report); print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status'] in {'COMPLETED','PARTIAL_BLOCKED'} else 2)
if __name__=='__main__': main()
