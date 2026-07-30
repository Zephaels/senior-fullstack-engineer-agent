import subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class QualificationCommandTests(unittest.TestCase):
    def test_verify_local_install_accepts_documented_arguments(self):
        with tempfile.TemporaryDirectory() as td:
            cp = subprocess.run(
                [sys.executable, str(ROOT / 'scripts' / 'verify_local_install.py'), '--home', td],
                text=True,
                capture_output=True,
            )
            # An empty home should fail verification, but argparse must accept the command.
            self.assertNotIn('unrecognized arguments', cp.stderr)
            self.assertNotEqual(cp.returncode, 2, cp.stderr)

    def test_documented_compile_paths_exist(self):
        paths = [
            ROOT / 'scripts',
            ROOT / 'source' / 'senior-fullstack-engineer-agent' / 'scripts',
            ROOT / 'source' / 'senior-fullstack-engineer-agent' / 'eval-engine',
        ]
        self.assertTrue(all(p.exists() for p in paths), paths)

    def test_qualification_plan_uses_supported_verify_command(self):
        plan = (ROOT / 'docs' / 'CODEX_RC_TEST_PLAN.md').read_text(encoding='utf-8')
        self.assertIn('python scripts/verify_local_install.py --home "$RC_HOME"', plan)
        self.assertNotIn('verify_local_install.py --repository', plan)

class QualificationOutputIsolationTests(unittest.TestCase):
    def test_validator_ignores_in_progress_qualification_outputs(self):
        q = ROOT / 'qualification-results' / 'self-test-empty.json'
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text('', encoding='utf-8')
        try:
            cp = subprocess.run(
                [sys.executable, str(ROOT / 'scripts' / 'validate_rc.py')],
                text=True,
                capture_output=True,
            )
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        finally:
            q.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
