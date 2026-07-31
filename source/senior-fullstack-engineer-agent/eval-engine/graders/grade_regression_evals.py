#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import canonical_skill_names,read_json,write_json,safe_div

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); ap.add_argument('--output',required=True); a=ap.parse_args(); data=read_json(a.run)
    total=correct=violations=0; details=[]
    for rec in data.get('runs',[]):
        if rec.get('configuration')!='regression' or rec.get('result',{}).get('status')!='completed': continue
        total+=1; case=rec['case']; selected=canonical_skill_names(rec['result'].get('selected_skills',[])); ok=case.get('expected_route') in selected; bad=sorted(selected.intersection(case.get('must_not_route',[]))); violations+=len(bad); correct+=int(ok and not bad); details.append({'id':case['id'],'pass':ok and not bad,'selected':sorted(selected),'violations':bad})
    status='COMPLETED' if total else 'BLOCKED_NO_PLUGIN_RUNTIME_RUNS'
    write_json(a.output,{'status':status,'correct':correct,'total':total,'accuracy':safe_div(correct,total) if total else None,'break_count':total-correct if total else None,'must_not_violations':violations,'details':details})
if __name__=='__main__': main()
