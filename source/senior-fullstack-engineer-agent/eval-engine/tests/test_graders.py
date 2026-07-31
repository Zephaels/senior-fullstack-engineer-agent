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

 def test_trigger_grader_normalizes_plugin_skill_namespace(self):
  data={'runs':[
   {'case':{'id':'1','target_skill':'code-review','should_trigger':True},'result':{'status':'completed','selected_skills':['senior-fullstack-engineer-agent:code-review']}}
  ]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data))
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_trigger_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text()); self.assertEqual(r['binary']['tp'],1); self.assertEqual(r['binary']['fn'],0)

 def test_positive_trigger_route_requires_only_the_target_skill(self):
  data={'runs':[
   {'case':{'id':'1','target_skill':'code-review','should_trigger':True},'result':{'status':'completed','selected_skills':['code-review','security-engineering']}}
  ]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data),encoding='utf-8')
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_trigger_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text(encoding='utf-8')); self.assertEqual(r['binary']['recall'],1.0); self.assertEqual(r['routing']['accuracy'],0.0); self.assertEqual(r['routing']['must_not_violations'],1); self.assertFalse(r['details'][0]['pass'])

 def test_positive_trigger_route_accepts_declared_companion_skill(self):
  data={'runs':[
   {'case':{'id':'1','target_skill':'architecture-design','should_trigger':True,'allowed_companion_skills':['security-engineering']},'result':{'status':'completed','selected_skills':['architecture-design','security-engineering']}}
  ]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data),encoding='utf-8')
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_trigger_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text(encoding='utf-8')); self.assertEqual(r['routing']['accuracy'],1.0); self.assertEqual(r['routing']['must_not_violations'],0); self.assertTrue(r['details'][0]['pass'])

 def test_regression_uses_expected_route_and_normalizes_namespace(self):
  data={'runs':[
   {'configuration':'regression','case':{'id':'1','expected_route':'systematic-debugging','must_not_route':['product-discovery']},'result':{'status':'completed','selected_skills':['senior-fullstack-engineer-agent:systematic-debugging']}}
  ]}
  with tempfile.TemporaryDirectory() as td:
   inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(data))
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_regression_evals.py'),'--run',str(inp),'--output',str(out)])
   r=json.loads(out.read_text()); self.assertEqual(r['status'],'COMPLETED'); self.assertEqual(r['accuracy'],1.0); self.assertEqual(r['break_count'],0)

 def test_pressure_grader_loads_every_case_file_in_directory(self):
  run={'runs':[
   {'case_id':'P-1','status':'completed','output':'safe one'},
   {'case_id':'P-2','status':'completed','output':'safe two'}
  ]}
  judge="""import json,sys; req=json.load(open(sys.argv[1],encoding='utf-8')); json.dump({'status':'completed','pass':True,'critical_violation':False,'reason':'ok'},open(sys.argv[2],'w',encoding='utf-8'))"""
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); case_dir=root/'cases'; case_dir.mkdir()
   (case_dir/'one.json').write_text(json.dumps({'cases':[{'id':'P-1','scenario':'one'}]}),encoding='utf-8')
   (case_dir/'two.json').write_text(json.dumps({'cases':[{'id':'P-2','scenario':'two'}]}),encoding='utf-8')
   inp=root/'run.json'; out=root/'out.json'; script=root/'judge.py'
   inp.write_text(json.dumps(run),encoding='utf-8'); script.write_text(judge,encoding='utf-8')
   command=f'{subprocess.list2cmdline([sys.executable])} {subprocess.list2cmdline([str(script)])} {{request}} {{response}}'
   subprocess.check_call([sys.executable,str(ROOT/'graders/grade_pressure_evals.py'),'--run',str(inp),'--cases',str(case_dir),'--judge-command',command,'--output',str(out)])
   result=json.loads(out.read_text(encoding='utf-8')); self.assertEqual(result['status'],'COMPLETED'); self.assertEqual(result['total'],2); self.assertEqual(result['pass_rate'],1.0)

 def test_pressure_grader_rejects_duplicate_case_ids(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); case_dir=root/'cases'; case_dir.mkdir()
   payload=json.dumps({'cases':[{'id':'P-1','scenario':'duplicate'}]})
   (case_dir/'one.json').write_text(payload,encoding='utf-8'); (case_dir/'two.json').write_text(payload,encoding='utf-8')
   inp=root/'run.json'; out=root/'out.json'; inp.write_text(json.dumps({'runs':[]}),encoding='utf-8')
   completed=subprocess.run([sys.executable,str(ROOT/'graders/grade_pressure_evals.py'),'--run',str(inp),'--cases',str(case_dir),'--output',str(out)],capture_output=True,text=True)
   self.assertNotEqual(completed.returncode,0); self.assertIn('duplicate pressure case id',completed.stderr)

if __name__=='__main__': unittest.main()
