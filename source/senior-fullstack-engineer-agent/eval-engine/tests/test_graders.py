import json, tempfile, unittest, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestGraders(unittest.TestCase):
 def test_trigger_metrics(self):
  data={'runs':[
   {'case':{'id':'1','target_skill':'a','should_trigger':True},'result':{'status':'completed','selected_skills':['a']}},
   {'case':{'id':'2','target_skill':'a','should_trigger':False},'result':{'status':'completed','selected_skills':[]}},
   {'case':{'id':'3','target_skill':'a','should_trigger':False},'result':{'status':'completed','selected_skills':['a']}},
   {'case':{'id':'4','expected_route':'b','must_not_route':['c']},'result':{'status':'completed','selected_skills':['b']}}
  ]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data))
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_trigger_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text()); self.assertEqual(r['binary']['tp'],1); self.assertEqual(r['binary']['fp'],1); self.assertEqual(r['routing']['accuracy'],1.0)
 def test_blocked_trigger_metrics_are_null(self):
  data={'runs':[]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data))
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_trigger_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text()); self.assertEqual(r['status'],'BLOCKED_NO_COMPLETED_RUNS'); self.assertIsNone(r['binary']['precision']); self.assertIsNone(r['binary']['recall']); self.assertIsNone(r['routing']['accuracy'])

 def test_blocked_regression_metrics_are_null(self):
  data={'runs':[]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data))
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_regression_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text()); self.assertEqual(r['status'],'BLOCKED_NO_PLUGIN_RUNTIME_RUNS'); self.assertIsNone(r['accuracy']); self.assertIsNone(r['break_count'])

if __name__=='__main__': unittest.main()
