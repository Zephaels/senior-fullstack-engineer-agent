#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
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
            cases.append({'id':c.get('id',f'T-{skill}-{idx:03d}'),'prompt':c.get('query') or c.get('prompt'),'target_skill':skill,'should_trigger':bool(c['should_trigger']),'source':str(p.relative_to(root))})
    for p in sorted((root/'evals/regression').glob('*.json')):
        for c in json.loads(p.read_text(encoding='utf-8')).get('cases',[]):
            cases.append({'id':c['id'],'prompt':c['prompt'],'expected_route':c['expected_route'],'must_not_route':c.get('must_not_route',[]),'source':str(p.relative_to(root))})
    return cases

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--catalog',default=str(ROOT/'eval-engine/catalog/skill-catalog.json'))
    ap.add_argument('--runner-command')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--timeout',type=int,default=300)
    ap.add_argument('--output',default=str(ROOT/'eval-engine/reports/trigger-run.json'))
    a=ap.parse_args(); cases=collect_cases(ROOT); cases=cases[:a.limit or None]; catalog=load_catalog(a.catalog)
    report={'suite':'metadata-first-trigger-v2','status':'COMPLETED' if a.runner_command else 'BLOCKED_NO_MODEL_RUNNER','catalog_size':len(catalog),'cases_requested':len(cases),'runs':[],'limitations':[]}
    if not a.runner_command:
        report['limitations'].append('No external model runner supplied. No trigger metrics are claimed.')
    else:
        for case in cases:
            req={'task_type':'skill-discovery','prompt':case['prompt'],'skills':[{'name':s['name'],'description':s['description']} for s in catalog], 'response_contract':{'selected_skills':['skill-name'],'reason':'short reason'}}
            result=invoke_runner(a.runner_command,req,a.timeout)
            report['runs'].append({'case':case,'result':result})
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status']=='COMPLETED' else 2)
if __name__=='__main__': main()
