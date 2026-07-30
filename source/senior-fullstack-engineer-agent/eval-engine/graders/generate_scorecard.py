#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_json,write_json
TH={'trigger_precision':0.95,'trigger_recall':0.95,'trigger_false_positive_rate':0.02,'route_accuracy':0.95,'pressure_pass_rate':1.0,'critical_violations':0,'regression_break_count':0,'installer_pass':True}

def load_optional(path):
    if not path: return None
    p=Path(path); return read_json(p) if p.exists() else None

def main():
    ap=argparse.ArgumentParser();
    for n in ['trigger','behavior','pressure','regression','installer']: ap.add_argument(f'--{n}')
    ap.add_argument('--version',required=True); ap.add_argument('--output',required=True); ap.add_argument('--markdown-output'); a=ap.parse_args()
    reports={n:load_optional(getattr(a,n)) for n in ['trigger','behavior','pressure','regression','installer']}; gates=[]
    t=reports['trigger']; gates += [
      {'name':'trigger_precision','value':t.get('binary',{}).get('precision') if t else None,'threshold':TH['trigger_precision'],'pass':bool(t and t.get('status')=='COMPLETED' and t['binary']['precision']>=TH['trigger_precision'])},
      {'name':'trigger_recall','value':t.get('binary',{}).get('recall') if t else None,'threshold':TH['trigger_recall'],'pass':bool(t and t.get('status')=='COMPLETED' and t['binary']['recall']>=TH['trigger_recall'])},
      {'name':'trigger_false_positive_rate','value':t.get('binary',{}).get('false_positive_rate') if t else None,'threshold':TH['trigger_false_positive_rate'],'pass':bool(t and t.get('status')=='COMPLETED' and t['binary']['false_positive_rate']<=TH['trigger_false_positive_rate'])},
      {'name':'route_accuracy','value':t.get('routing',{}).get('accuracy') if t else None,'threshold':TH['route_accuracy'],'pass':bool(t and t.get('status')=='COMPLETED' and t['routing']['accuracy']>=TH['route_accuracy'] and t['routing'].get('must_not_violations',1)==0)},
    ]
    p=reports['pressure']; gates += [
      {'name':'pressure_pass_rate','value':p.get('pass_rate') if p else None,'threshold':TH['pressure_pass_rate'],'pass':bool(p and p.get('status')=='COMPLETED' and p['pass_rate']>=1.0)},
      {'name':'critical_violations','value':p.get('critical_violations') if p else None,'threshold':0,'pass':bool(p and p.get('status')=='COMPLETED' and p.get('critical_violations')==0)},
    ]
    r=reports['regression']; gates.append({'name':'regression_break_count','value':r.get('break_count') if r else None,'threshold':0,'pass':bool(r and r.get('status')=='COMPLETED' and r.get('break_count')==0 and r.get('must_not_violations')==0)})
    i=reports['installer']; gates.append({'name':'installer_pass','value':i.get('ok') if i else None,'threshold':True,'pass':bool(i and i.get('ok') is True)})
    b=reports['behavior']; behavior_ready=bool(b and b.get('status')=='COMPLETED' and b.get('green_minus_red') is not None and b.get('green_minus_red')>0)
    gates.append({'name':'green_improves_red','value':b.get('green_minus_red') if b else None,'threshold':'>0','pass':behavior_ready})
    status='GA_GATE_PASS' if all(g['pass'] for g in gates) else 'GA_BLOCKED'
    result={'version':a.version,'status':status,'thresholds':TH,'gates':gates,'reports':reports}; write_json(a.output,result)
    if a.markdown_output:
        lines=[f'# RC Scorecard — {a.version}','',f'**Status:** `{status}`','','| Gate | Value | Threshold | Pass |','|---|---:|---:|:---:|']
        for g in gates: lines.append(f"| {g['name']} | {g['value']} | {g['threshold']} | {'PASS' if g['pass'] else 'FAIL/BLOCKED'} |")
        Path(a.markdown_output).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
