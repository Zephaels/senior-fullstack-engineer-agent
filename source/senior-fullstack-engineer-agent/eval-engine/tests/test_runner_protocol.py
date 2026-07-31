import importlib.util
import json
import sys
import tempfile
import unittest
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RunnerProtocolTests(unittest.TestCase):
    def _resume_runner(self, script_name, command_flag, expected_calls):
        common = load_module(ROOT / 'runners' / 'common.py', f'{script_name}_common')
        runner = ROOT / 'runners' / script_name
        with tempfile.TemporaryDirectory(prefix=f'sfse {script_name} ') as td:
            td = Path(td); stub = td / 'stub.py'; counter = td / 'counter.txt'; output = td / 'report.json'
            stub.write_text(
                "import json,sys\n"
                "request=json.load(open(sys.argv[1],encoding='utf-8'))\n"
                f"open({str(counter)!r},'a',encoding='utf-8').write('1\\n')\n"
                "json.dump({'output':'stub','selected_skills':[request.get('expected_skill','')] if request.get('expected_skill') else []},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template=f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            command=[sys.executable,str(runner),command_flag,template,'--limit','1','--output',str(output)]
            subprocess.check_call(command); subprocess.check_call(command+['--resume']); subprocess.check_call(command+['--resume'])
            self.assertEqual(len(counter.read_text(encoding='utf-8').splitlines()),expected_calls)

    def test_runner_paths_are_valid_on_current_platform(self):
        common = load_module(ROOT / 'runners' / 'common.py', 'runner_common')
        with tempfile.TemporaryDirectory(prefix='sfse runner ') as td:
            stub = Path(td) / 'stub runner.py'
            stub.write_text(
                "import json,sys\n"
                "request=json.load(open(sys.argv[1],encoding='utf-8'))\n"
                "json.dump({'echo':request['value']},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template = f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            result = common.invoke_runner(template, {'value': 'ok'})
            self.assertEqual(result['status'], 'completed', result)
            self.assertEqual(result['echo'], 'ok')

    def test_runner_preserves_structured_transport_failure_status(self):
        common = load_module(ROOT / 'runners' / 'common.py', 'runner_status_common')
        with tempfile.TemporaryDirectory(prefix='sfse runner status ') as td:
            stub = Path(td) / 'stub.py'
            stub.write_text(
                "import json,sys\n"
                "json.dump({'status':'runner_error','error_class':'transient_host_exhausted'},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template = f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            result = common.invoke_runner(template, {'value': 'ok'})
            self.assertEqual(result['status'], 'runner_error', result)
            self.assertEqual(result['error_class'], 'transient_host_exhausted')

    def test_judge_paths_are_valid_on_current_platform(self):
        common = load_module(ROOT / 'graders' / 'common.py', 'grader_common')
        with tempfile.TemporaryDirectory(prefix='sfse judge ') as td:
            stub = Path(td) / 'stub judge.py'
            stub.write_text(
                "import json,sys\n"
                "request=json.load(open(sys.argv[1],encoding='utf-8'))\n"
                "json.dump({'pass':request['pass']},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template = f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            result = common.invoke_judge(template, {'pass': True})
            self.assertEqual(result['status'], 'completed', result)
            self.assertTrue(result['pass'])

    def test_trigger_runner_batches_cases_and_expands_results(self):
        common = load_module(ROOT / 'runners' / 'common.py', 'batch_runner_common')
        runner = ROOT / 'runners' / 'run_trigger_evals.py'
        with tempfile.TemporaryDirectory(prefix='sfse trigger batch ') as td:
            td = Path(td)
            stub = td / 'stub runner.py'
            counter = td / 'counter.txt'
            output = td / 'report.json'
            stub.write_text(
                "import json,sys\n"
                "request=json.load(open(sys.argv[1],encoding='utf-8'))\n"
                f"open({str(counter)!r},'a',encoding='utf-8').write('1\\n')\n"
                "cases=request.get('cases',[])\n"
                "result={'results':[{'id':case['id'],'selected_skills':[],'reason':'stub'} for case in cases]}\n"
                "json.dump(result,open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template = f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            subprocess.check_call([
                sys.executable, str(runner), '--runner-command', template,
                '--limit', '3', '--batch-size', '2', '--output', str(output),
            ])
            report = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(len(report['runs']), 3)
            self.assertTrue(all(run['result']['status'] == 'completed' for run in report['runs']))
            self.assertEqual(len(counter.read_text(encoding='utf-8').splitlines()), 2)

    def test_trigger_runner_resume_reuses_completed_cases(self):
        common = load_module(ROOT / 'runners' / 'common.py', 'resume_runner_common')
        runner = ROOT / 'runners' / 'run_trigger_evals.py'
        with tempfile.TemporaryDirectory(prefix='sfse trigger resume ') as td:
            td = Path(td); stub = td / 'stub.py'; counter = td / 'counter.txt'; output = td / 'report.json'
            stub.write_text(
                "import json,sys\n"
                "request=json.load(open(sys.argv[1],encoding='utf-8'))\n"
                f"open({str(counter)!r},'a',encoding='utf-8').write('1\\n')\n"
                "json.dump({'selected_skills':[],'reason':'stub'},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template=f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            command=[sys.executable,str(runner),'--runner-command',template,'--limit','2','--output',str(output)]
            subprocess.check_call(command); subprocess.check_call(command+['--resume'])
            self.assertEqual(len(counter.read_text(encoding='utf-8').splitlines()),2)
            report=json.loads(output.read_text(encoding='utf-8')); self.assertEqual(report['status'],'COMPLETED'); self.assertEqual(report['cases_completed'],2)

    def test_trigger_runner_resume_rejects_stale_case_metadata(self):
        runner = ROOT / 'runners' / 'run_trigger_evals.py'
        with tempfile.TemporaryDirectory(prefix='sfse trigger metadata ') as td:
            output = Path(td) / 'report.json'
            output.write_text(json.dumps({
                'runs': [{
                    'case': {
                        'id': 'T-senior-fullstack-engineer-agent-001',
                        'prompt': 'stale prompt',
                        'target_skill': 'wrong-skill',
                        'should_trigger': False,
                    },
                    'result': {'status': 'completed', 'selected_skills': ['senior-fullstack-engineer-agent']},
                }],
            }), encoding='utf-8')
            completed = subprocess.run([
                sys.executable, str(runner), '--resume', '--prepare-only',
                '--limit', '1', '--output', str(output),
            ], check=False)
            self.assertEqual(completed.returncode, 2)
            report = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['runs'], [])
            self.assertTrue(any('Rejected 1 stale' in item for item in report['limitations']))

    def test_behavior_runner_resume_reuses_red_and_green(self):
        self._resume_runner('run_behavior_evals_v2.py','--runner-command',2)

    def test_behavior_runner_selects_named_cases(self):
        runner = ROOT / 'runners' / 'run_behavior_evals_v2.py'
        with tempfile.TemporaryDirectory(prefix='sfse behavior selection ') as td:
            output=Path(td)/'report.json'
            completed=subprocess.run([
                sys.executable,str(runner),'--prepare-only',
                '--case','B6-intent-interview-1',
                '--case','B6-architecture-design-1',
                '--output',str(output),
            ],check=False)
            self.assertEqual(completed.returncode,2)
            report=json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['cases_requested'],2)
            self.assertEqual(report['runs_expected'],4)

    def test_behavior_runner_can_select_one_configuration(self):
        runner = ROOT / 'runners' / 'run_behavior_evals_v2.py'
        with tempfile.TemporaryDirectory(prefix='sfse behavior config ') as td:
            output=Path(td)/'report.json'
            completed=subprocess.run([
                sys.executable,str(runner),'--prepare-only',
                '--case','B6-intent-interview-1',
                '--configuration','green','--output',str(output),
            ],check=False)
            self.assertEqual(completed.returncode,2)
            report=json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['runs_expected'],1)
            self.assertEqual(report['cases_requested'],1)

    def test_behavior_runner_rejects_runs_without_context_provenance(self):
        common = load_module(ROOT / 'runners' / 'common.py', 'behavior_provenance_common')
        runner = ROOT / 'runners' / 'run_behavior_evals_v2.py'
        with tempfile.TemporaryDirectory(prefix='sfse behavior provenance ') as td:
            td=Path(td); stub=td/'stub.py'; counter=td/'counter.txt'; output=td/'report.json'
            stub.write_text(
                "import json,sys\n"
                f"open({str(counter)!r},'a',encoding='utf-8').write('1\\n')\n"
                "json.dump({'output':'stub','selected_skills':[]},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template=f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            command=[sys.executable,str(runner),'--runner-command',template,'--limit','1','--output',str(output)]
            subprocess.check_call(command)
            report=json.loads(output.read_text(encoding='utf-8'))
            for run in report['runs']: run.pop('input_fingerprint',None)
            output.write_text(json.dumps(report),encoding='utf-8')
            subprocess.check_call(command+['--resume'])
            self.assertEqual(len(counter.read_text(encoding='utf-8').splitlines()),4)

    def test_pressure_runner_resume_reuses_completed_case(self):
        self._resume_runner('run_pressure_evals.py','--runner-command',1)

    def test_pressure_runner_revision_invalidates_resume(self):
        common = load_module(ROOT / 'runners' / 'common.py', 'pressure_revision_common')
        runner = ROOT / 'runners' / 'run_pressure_evals.py'
        with tempfile.TemporaryDirectory(prefix='sfse pressure revision ') as td:
            td = Path(td); stub = td / 'stub.py'; counter = td / 'counter.txt'; output = td / 'report.json'
            stub.write_text(
                "import json,sys\n"
                f"open({str(counter)!r},'a',encoding='utf-8').write('1\\n')\n"
                "json.dump({'output':'stub','selected_skills':[]},open(sys.argv[2],'w',encoding='utf-8'))\n",
                encoding='utf-8',
            )
            template = f'{common.command_arg(sys.executable)} {common.command_arg(stub)} {{request}} {{response}}'
            base = [sys.executable, str(runner), '--runner-command', template, '--limit', '1', '--output', str(output)]
            subprocess.check_call(base + ['--runner-revision', 'adapter-v1'])
            subprocess.check_call(base + ['--runner-revision', 'adapter-v1', '--resume'])
            subprocess.check_call(base + ['--runner-revision', 'adapter-v2', '--resume'])
            self.assertEqual(len(counter.read_text(encoding='utf-8').splitlines()), 2)

    def test_pressure_runner_selects_named_cases(self):
        runner = ROOT / 'runners' / 'run_pressure_evals.py'
        with tempfile.TemporaryDirectory(prefix='sfse pressure named ') as td:
            output = Path(td) / 'report.json'
            completed = subprocess.run([
                sys.executable, str(runner), '--prepare-only',
                '--case', 'P-001', '--case', 'P3-019', '--output', str(output),
            ], check=False)
            self.assertEqual(completed.returncode, 2)
            report = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report['cases_requested'], 2)
            self.assertEqual(report['cases_blocked'], 2)

    def test_regression_runner_resume_reuses_completed_case(self):
        self._resume_runner('run_regression_evals.py','--runtime-runner-command',1)


if __name__ == '__main__':
    unittest.main()
