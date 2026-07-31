#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json,invoke_judge,safe_div

def fingerprint(case,configuration,model_output):
    payload={'id':case['id'],'configuration':configuration,'prompt':case['prompt'],'model_output':model_output,'expected_output':case.get('expected_output'),'expectations':case.get('expectations',[]),'prohibited_behaviors':case.get('prohibited_behaviors',[])}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

def summarize(judgments,expected):
    completed=[j for j in judgments if j['judge'].get('status')=='completed']; passed=sum(1 for j in completed if j['judge'].get('pass') is True); by={}
    for j in completed:
        by.setdefault(j['configuration'],[0,0]); by[j['configuration']][1]+=1; by[j['configuration']][0]+=int(j['judge'].get('pass') is True)
    metrics={k:{'passed':v[0],'total':v[1],'pass_rate':safe_div(v[0],v[1])} for k,v in by.items()}; red=metrics.get('red',{}).get('pass_rate'); green=metrics.get('green',{}).get('pass_rate'); delta=(green-red) if red is not None and green is not None else None
    if len(completed)==expected: status='COMPLETED'
    elif completed: status='PARTIAL_BLOCKED'
    else: status='BLOCKED_NO_COMPLETED_JUDGMENTS'
    return {'status':status,'expected_judgments':expected,'completed_judgments':len(completed),'passed':passed,'total':len(completed),'pass_rate':safe_div(passed,len(completed)),'by_configuration':metrics,'green_minus_red':delta,'judge_independence':'fresh session required; same-model-family results are not cross-model evidence','judgments':judgments}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--judge-command'); ap.add_argument('--output',required=True); ap.add_argument('--timeout',type=int,default=300); ap.add_argument('--resume',action='store_true'); ap.add_argument('--prepare-only',action='store_true'); ap.add_argument('--retry',action='append',default=[],metavar='CASE[:CONFIG]'); a=ap.parse_args(); data=read_json(a.run); out=Path(a.output)
    model_runs=[rec for rec in data.get('runs',[]) if rec.get('configuration') in {'red','green'} and rec.get('result',{}).get('status')=='completed']; current={}
    for rec in model_runs:
        key=(rec['case']['id'],rec['configuration']); current[key]=(rec,fingerprint(rec['case'],rec['configuration'],rec['result'].get('output','')))
    judgments=[]; retry_cases=set(); retry_keys=set()
    for item in a.retry:
        if ':' in item: retry_keys.add(tuple(item.split(':',1)))
        else: retry_cases.add(item)
    if a.resume and out.exists():
        old=read_json(out)
        for item in old.get('judgments',[]):
            key=(item.get('case_id'),item.get('configuration')); expected=current.get(key); forced=key[0] in retry_cases or key in retry_keys
            if expected and not forced and item.get('input_fingerprint')==expected[1] and item.get('judge',{}).get('status')=='completed': judgments.append(item)
    completed_keys={(j['case_id'],j['configuration']) for j in judgments}
    if not a.prepare_only and a.judge_command:
        for key,(rec,digest) in current.items():
            if key in completed_keys: continue
            case=rec['case']; result=rec['result']; req={'task_type':'independent-eval-judge','prompt':case['prompt'],'model_output':result.get('output',''),'expected_output':case.get('expected_output'),'expectations':case.get('expectations',[]),'prohibited_behaviors':case.get('prohibited_behaviors',[]),'response_contract':{'pass':True,'expectation_results':[{'expectation':'','pass':True,'evidence':''}],'prohibited_behavior_hits':[],'reason':''}}
            judgments.append({'case_id':case['id'],'configuration':rec['configuration'],'input_fingerprint':digest,'judge':invoke_judge(a.judge_command,req,a.timeout)})
            write_json(out,summarize(judgments,len(current)))
    result=summarize(judgments,len(current))
    if not a.judge_command and not a.prepare_only and not judgments: result.update({'status':'BLOCKED_NO_INDEPENDENT_JUDGE','reason':'Semantic behavior expectations require an independent judge or deterministic case-specific assertions. No score is claimed.'})
    result['judgments'].sort(key=lambda j:(j['case_id'],j['configuration'])); write_json(out,result); print(out.read_text(encoding='utf-8'))
if __name__=='__main__': main()
