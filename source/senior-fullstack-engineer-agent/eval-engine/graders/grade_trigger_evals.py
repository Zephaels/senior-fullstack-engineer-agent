#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json,safe_div

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--output',required=True); a=ap.parse_args(); data=read_json(a.run)
    tp=tn=fp=fn=route_ok=route_total=must_not_violations=completed=0; details=[]
    for rec in data.get('runs',[]):
        if rec.get('result',{}).get('status')!='completed': continue
        completed+=1; case=rec['case']; selected=set(rec['result'].get('selected_skills',[]))
        if 'target_skill' in case:
            actual=case['target_skill'] in selected; expected=case['should_trigger']
            if expected and actual: tp+=1
            elif expected and not actual: fn+=1
            elif not expected and actual: fp+=1
            else: tn+=1
            details.append({'id':case['id'],'pass':actual==expected,'selected':sorted(selected)})
        else:
            route_total+=1; ok=case['expected_route'] in selected; route_ok+=int(ok)
            violations=sorted(selected.intersection(case.get('must_not_route',[]))); must_not_violations+=len(violations)
            details.append({'id':case['id'],'pass':ok and not violations,'selected':sorted(selected),'violations':violations})
    status='COMPLETED' if completed else 'BLOCKED_NO_COMPLETED_RUNS'
    precision=safe_div(tp,tp+fp) if completed else None
    recall=safe_div(tp,tp+fn) if completed else None
    fpr=safe_div(fp,fp+tn) if completed else None
    binary_accuracy=safe_div(tp+tn,tp+tn+fp+fn) if completed else None
    route_accuracy=safe_div(route_ok,route_total) if route_total else None
    result={'status':status,'completed_runs':completed,'binary':{'tp':tp,'tn':tn,'fp':fp,'fn':fn,'precision':precision,'recall':recall,'false_positive_rate':fpr,'accuracy':binary_accuracy},'routing':{'correct':route_ok,'total':route_total,'accuracy':route_accuracy,'must_not_violations':must_not_violations},'details':details}
    write_json(a.output,result); print(Path(a.output).read_text())
if __name__=='__main__': main()
