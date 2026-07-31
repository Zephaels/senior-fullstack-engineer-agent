#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json,invoke_judge,safe_div

def load_cases(raw_paths):
    case_files=[]
    for raw in raw_paths:
        path=Path(raw); case_files.extend(sorted(path.glob('*.json')) if path.is_dir() else [path])
    cases={}
    for path in case_files:
        for case in read_json(path).get('cases',[]):
            case_id=case['id']
            if case_id in cases: raise ValueError(f'duplicate pressure case id {case_id!r} in {path}')
            cases[case_id]=case
    return cases

def fingerprint(case,model_output):
    payload={'case':case,'model_output':model_output}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

def summarize(judgments,expected):
    completed=[j for j in judgments if j['judge'].get('status')=='completed']; passed=sum(1 for j in completed if j['judge'].get('pass') is True); critical=sum(1 for j in completed if j['judge'].get('critical_violation') is True)
    status='COMPLETED' if len(completed)==expected else ('PARTIAL_BLOCKED' if completed else 'BLOCKED_NO_COMPLETED_JUDGMENTS')
    return {'status':status,'expected_judgments':expected,'completed_judgments':len(completed),'passed':passed,'total':len(completed),'pass_rate':safe_div(passed,len(completed)),'critical_violations':critical,'judge_independence':'fresh session required; same-model-family results are not cross-model evidence','judgments':judgments}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--cases',required=True,action='append',help='Pressure case JSON file or directory. Repeat to merge sources.'); ap.add_argument('--judge-command'); ap.add_argument('--output',required=True); ap.add_argument('--timeout',type=int,default=300); ap.add_argument('--resume',action='store_true'); ap.add_argument('--prepare-only',action='store_true'); ap.add_argument('--retry',action='append',default=[]); a=ap.parse_args(); run=read_json(a.run); cases=load_cases(a.cases); out=Path(a.output)
    current={}
    for record in run.get('runs',[]):
        cid=record.get('case_id'); case=cases.get(cid); result=record.get('result',record)
        if case and result.get('status')=='completed': current[cid]=(case,result,fingerprint(case,result.get('output','')))
    judgments=[]
    if a.resume and out.exists():
        for item in read_json(out).get('judgments',[]):
            cid=item.get('case_id'); expected=current.get(cid)
            if expected and cid not in a.retry and item.get('input_fingerprint')==expected[2] and item.get('judge',{}).get('status')=='completed': judgments.append(item)
    completed={j['case_id'] for j in judgments}
    if not a.prepare_only and a.judge_command:
        for cid,(case,result,digest) in current.items():
            if cid in completed: continue
            req={'task_type':'pressure-eval-judge','scenario':case['scenario'],'model_output':result.get('output',''),'expected_behavior':case.get('expected_behavior',[]),'prohibited_behaviors':case.get('prohibited_behaviors',[]),'response_contract':{'pass':True,'critical_violation':False,'reason':''}}
            judgments.append({'case_id':cid,'input_fingerprint':digest,'judge':invoke_judge(a.judge_command,req,a.timeout)}); write_json(out,summarize(judgments,len(current)))
    result=summarize(judgments,len(current))
    if not a.judge_command and not a.prepare_only and not judgments: result.update({'status':'BLOCKED_NO_INDEPENDENT_JUDGE','reason':'Pressure compliance requires an independent judge.'})
    result['judgments'].sort(key=lambda j:j['case_id']); write_json(out,result); print(out.read_text(encoding='utf-8'))
if __name__=='__main__': main()
