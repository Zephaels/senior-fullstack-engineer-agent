#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json,invoke_judge,safe_div

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--cases',required=True); ap.add_argument('--judge-command'); ap.add_argument('--output',required=True); a=ap.parse_args(); run=read_json(a.run); cases={c['id']:c for c in read_json(a.cases).get('cases',[])}
    if not a.judge_command:
        write_json(a.output,{'status':'BLOCKED_NO_INDEPENDENT_JUDGE','reason':'Pressure compliance requires an independent judge.','judgments':[]}); return
    judgments=[]
    for r in run.get('runs',[]):
        cid=r.get('case_id'); case=cases.get(cid)
        if not case or r.get('status')!='completed': continue
        req={'task_type':'pressure-eval-judge','scenario':case['scenario'],'model_output':r.get('output',''),'expected_behavior':case.get('expected_behavior',[]),'prohibited_behaviors':case.get('prohibited_behaviors',[]),'response_contract':{'pass':True,'critical_violation':False,'reason':''}}
        judgments.append({'case_id':cid,'judge':invoke_judge(a.judge_command,req)})
    comp=[j for j in judgments if j['judge'].get('status')=='completed']; passed=sum(1 for j in comp if j['judge'].get('pass') is True); critical=sum(1 for j in comp if j['judge'].get('critical_violation') is True)
    write_json(a.output,{'status':'COMPLETED' if comp else 'BLOCKED_NO_COMPLETED_JUDGMENTS','passed':passed,'total':len(comp),'pass_rate':safe_div(passed,len(comp)),'critical_violations':critical,'judgments':judgments})
if __name__=='__main__': main()
