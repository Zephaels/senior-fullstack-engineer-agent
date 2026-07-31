import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseGateTests(unittest.TestCase):
    def test_all_actions_are_pinned_to_full_commit_shas(self):
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if "uses:" not in line:
                    continue
                value = line.split("uses:", 1)[1].split("#", 1)[0].strip()
                self.assertRegex(value, r"^[^\s@]+@[0-9a-f]{40}$", path)

    def test_attestation_is_mandatory_and_verified(self):
        text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertNotIn("ENABLE_ARTIFACT_ATTESTATION", text)
        self.assertIn("actions/attest@508db95dd578ae2727ebd6217d5ba78e4fbda05d", text)
        self.assertIn("gh attestation verify", text)
        self.assertIn("validate_public_release.py", text)
        self.assertIn("independent-security-report.json", text)
        self.assertIn("independent-judge-report.json", text)
        self.assertIn("autonomy-rehearsal-report.json", text)

    def test_eval_commands_do_not_use_a_shell(self):
        for relative in (
            "source/senior-fullstack-engineer-agent/eval-engine/runners/common.py",
            "source/senior-fullstack-engineer-agent/eval-engine/graders/common.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"shell\s*=\s*True")
            self.assertRegex(text, r"shell\s*=\s*False")

    def test_local_release_security_review_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "security.json"
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/run_release_security_review.py"), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "PASS")

    def test_current_rc_cannot_be_published_as_ga(self):
        with tempfile.TemporaryDirectory() as directory:
            placeholder = Path(directory) / "placeholder.json"
            placeholder.write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/validate_public_release.py"),
                    "--tag",
                    "v1.0.0-rc.4.8",
                    "--target-commit",
                    "0" * 40,
                    "--security-report",
                    str(placeholder),
                    "--reproducibility-report",
                    str(placeholder),
                    "--github-checks",
                    str(placeholder),
                    "--independent-security-report",
                    str(placeholder),
                    "--independent-judge-report",
                    str(placeholder),
                    "--autonomy-rehearsal-report",
                    str(placeholder),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertTrue(any("VERSION 1.0.0" in error for error in payload["errors"]))

    def test_sparse_external_reports_cannot_satisfy_ga_contracts(self):
        module_path = ROOT / "scripts/validate_public_release.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("public_release_gate", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        for name in ("independent_security", "independent_judge", "autonomy_rehearsal"):
            errors = module.validate_external_report(name, {"status": "PASS"}, "1.0.0", "0" * 40)
            self.assertTrue(errors, name)

    def test_github_check_verification_is_bound_to_exact_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "checks.json"
            output = Path(directory) / "verified.json"
            source.write_text(json.dumps({"check_runs": [
                {"name": "validate", "head_sha": "1" * 40, "status": "completed", "conclusion": "success"},
                {"name": "analyze", "head_sha": "1" * 40, "status": "completed", "conclusion": "success"},
            ]}), encoding="utf-8")
            completed = subprocess.run([
                sys.executable, str(ROOT / "scripts/verify_github_checks.py"),
                "--input", str(source), "--output", str(output), "--commit", "0" * 40,
            ], cwd=ROOT, text=True, capture_output=True)
            self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
