import ast, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class QualificationCommandTests(unittest.TestCase):
    def test_validators_decode_text_as_utf8(self):
        for relative_path in [
            'scripts/validate_rc.py',
            'scripts/validate_plugin.py',
            'scripts/run_rc_qualification.py',
            'scripts/generate_manifests.py',
            'scripts/build_release.py',
        ]:
            path = ROOT / relative_path
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            missing_encoding = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute) or node.func.attr != 'read_text':
                    continue
                if not any(keyword.arg == 'encoding' for keyword in node.keywords):
                    missing_encoding.append(node.lineno)
            self.assertEqual(
                missing_encoding,
                [],
                f'{relative_path} has locale-dependent read_text calls at lines {missing_encoding}',
            )

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

    def test_qualification_script_uses_allowed_final_decision(self):
        source = (ROOT / 'scripts' / 'run_rc_qualification.py').read_text(encoding='utf-8')
        self.assertNotIn('RC_READY_WITH_BLOCKERS', source)
        self.assertIn("'decision':'RC_BLOCKED'", source)

    def test_scorecard_heading_has_no_mojibake(self):
        source = (
            ROOT
            / 'source'
            / 'senior-fullstack-engineer-agent'
            / 'eval-engine'
            / 'graders'
            / 'generate_scorecard.py'
        ).read_text(encoding='utf-8')
        self.assertNotIn('\ufffd', source)
        self.assertIn("# RC Scorecard", source)

    def test_release_build_uses_versioned_root_and_excludes_runtime_evidence(self):
        build = (ROOT / 'scripts' / 'build_release.py').read_text(encoding='utf-8')
        manifests = (ROOT / 'scripts' / 'generate_manifests.py').read_text(encoding='utf-8')
        validator = (ROOT / 'scripts' / 'validate_rc.py').read_text(encoding='utf-8')
        self.assertIn("f'senior-fullstack-engineer-agent-{VERSION}'", build)
        self.assertIn("f'{NAME}-{VERSION}'", manifests)
        for source in [build, manifests, validator]:
            self.assertIn("'validation'", source)

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
