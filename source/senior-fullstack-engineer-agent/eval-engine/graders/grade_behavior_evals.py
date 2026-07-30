#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json,invoke_judge,safe_div

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--judge-command'); ap.add_argument('--output',required=True); ap.add_argument('--timeout',type=int,default=300); a=ap.parse_args(); data=read_json(a.run)
    judgments=[]
    if not a.judge_command:
        result={'status':'BLOCKED_NO_INDEPENDENT_JUDGE','reason':'Semantic behavior expectations require an independent judge or deterministic case-specific assertions. No score is claimed.','judgments':[]}; write_json(a.output,result); print(Path(a.output).read_text()); return
    for rec in data.get('runs',[]):
        r=rec.get('result',{})
        if r.get('status')!='completed': continue
        case=rec['case']; req={'task_type':'independent-eval-judge','prompt':case['prompt'],'model_output':r.get('output',''),'expected_output':case.get('expected_output'),'expectations':case.get('expectations',[]),'response_contract':{'pass':True,'expectation_results':[{'expectation':'','pass':True,'evidence':''}],'prohibited_behavior_hits':[],'reason':''}}
        j=invoke_judge(a.judge_command,req,a.timeout); judgments.append({'case_id':case['id'],'configuration':rec['configuration'],'judge':j})
    completed=[j for j in judgments if j['judge'].get('status')=='completed']; passed=sum(1 for j in completed if j['judge'].get('pass') is True)
    by={}
    for j in completed:
        by.setdefault(j['configuration'],[0,0]); by[j['configuration']][1]+=1; by[j['configuration']][0]+=int(j['judge'].get('pass') is True)
    metrics={k:{'passed':v[0],'total':v[1],'pass_rate':safe_div(v[0],v[1])} for k,v in by.items()}
    red=metrics.get('red',{}).get('pass_rate'); green=metrics.get('green',{}).get('pass_rate'); delta=(green-red) if red is not None and green is not None else None
    result={'status':'COMPLETED' if completed else 'BLOCKED_NO_COMPLETED_JUDGMENTS','passed':passed,'total':len(completed),'pass_rate':safe_div(passed,len(completed)),'by_configuration':metrics,'green_minus_red':delta,'judgments':judgments}; write_json(a.output,result); print(Path(a.output).read_text())
if __name__=='__main__': main()
