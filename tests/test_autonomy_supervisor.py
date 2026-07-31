import datetime as dt
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "source" / "senior-fullstack-engineer-agent" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

plan_module = importlib.import_module("validate_autonomy_plan")
supervisor_module = importlib.import_module("autonomy_supervisor")


def timestamp(delta_minutes: int) -> str:
    value = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=delta_minutes)
    return value.isoformat().replace("+00:00", "Z")


class AutonomySupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.artifact = self.root / "artifact.zip"
        self.artifact.write_bytes(b"qualified artifact")
        self.deploy = [sys.executable, "-c", "raise SystemExit(0)"]
        self.health = [sys.executable, "-c", "raise SystemExit(0)", "health"]
        self.observe = [sys.executable, "-c", "raise SystemExit(0)", "observe"]
        self.rollback = [sys.executable, "-c", "raise SystemExit(0)", "rollback"]
        self.envelope = {
            "schema_version": "1.0",
            "run_id": "prod-run-0001",
            "owner": "release-owner",
            "issued_at": timestamp(-1),
            "expires_at": timestamp(30),
            "environment": "production",
            "artifact_sha256": hashlib.sha256(self.artifact.read_bytes()).hexdigest(),
            "trusted_executables": [{"path": sys.executable, "sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()}],
            "environment_bindings": {"inherit": [], "required_sha256": {}},
            "allowed_actions": ["deploy", "health_check", "observe", "rollback"],
            "allowed_paths": [str(self.root)],
            "allowed_commands": [self.deploy, self.health, self.observe, self.rollback],
            "limits": {"max_duration_minutes": 10, "max_attempts_per_step": 2, "max_changed_files": 0, "max_cost_usd": 0},
            "health_checks": ["post-deploy-health"],
            "rollback": {"action": self.rollback, "deadline_minutes": 5},
            "approval": {"type": "explicit-preauthorization", "evidence_ref": "change-001"},
            "hard_stops": ["artifact mismatch", "failed health gate"],
        }
        self.plan = {
            "schema_version": "1.0",
            "run_id": self.envelope["run_id"],
            "artifact_path": str(self.artifact),
            "workspace": str(self.workspace),
            "steps": [
                {"id": "deploy-release", "action": "deploy", "command": self.deploy, "cwd": str(self.workspace), "timeout_seconds": 10, "transient_exit_codes": []},
                {"id": "post-deploy-health", "action": "health_check", "command": self.health, "cwd": str(self.workspace), "timeout_seconds": 10, "transient_exit_codes": []},
                {"id": "observe-release", "action": "observe", "command": self.observe, "cwd": str(self.workspace), "timeout_seconds": 10, "transient_exit_codes": []},
            ],
        }

    def tearDown(self):
        self.temp.cleanup()

    def run_supervisor(self, execute=True):
        return supervisor_module.supervise(self.envelope, self.plan, "e" * 64, "p" * 64, execute_run=execute)

    def test_plan_is_exact_subset_of_envelope(self):
        self.assertEqual(plan_module.validate_plan(self.envelope, self.plan), [])

    def test_dry_run_never_executes_commands(self):
        code, report = self.run_supervisor(execute=False)
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "validated")
        self.assertFalse((self.workspace / ".sfse-autonomy").exists())

    def test_successful_production_run_creates_redacted_journal(self):
        code, report = self.run_supervisor()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "succeeded")
        journal = json.loads((self.workspace / ".sfse-autonomy" / "prod-run-0001.json").read_text(encoding="utf-8"))
        self.assertEqual(len(journal["steps"]), 3)
        self.assertIn("command_sha256", journal["steps"][0])
        self.assertNotIn("command", journal["steps"][0])
        self.assertNotIn("output", json.dumps(journal))

    def test_failed_health_gate_rolls_back(self):
        failing = [sys.executable, "-c", "raise SystemExit(2)", "health"]
        self.envelope["allowed_commands"].append(failing)
        self.plan["steps"][1]["command"] = failing
        code, report = self.run_supervisor()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "rolled_back")
        self.assertEqual(report["rollback"]["status"], "passed")

    def test_unapproved_command_is_denied(self):
        self.plan["steps"][0]["command"] = [sys.executable, "-c", "print('not approved')"]
        errors = plan_module.validate_plan(self.envelope, self.plan)
        self.assertTrue(any("not an exact allowed_commands" in error for error in errors), errors)

    def test_deployment_retries_are_denied(self):
        self.plan["steps"][0]["transient_exit_codes"] = [75]
        errors = plan_module.validate_plan(self.envelope, self.plan)
        self.assertTrue(any("cannot be retried unattended" in error for error in errors), errors)

    def test_nonzero_cost_budget_is_denied_without_meter(self):
        self.envelope["limits"]["max_cost_usd"] = 1
        errors = plan_module.validate_plan(self.envelope, self.plan)
        self.assertTrue(any("external cost meter" in error for error in errors), errors)

    def test_trusted_executable_digest_mismatch_is_blocked(self):
        self.envelope["trusted_executables"][0]["sha256"] = "0" * 64
        code, report = self.run_supervisor()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["phase"], "validation")
        self.assertTrue(any("executable digest mismatch" in error for error in report["errors"]), report)

    def test_artifact_identity_change_after_deploy_triggers_rollback(self):
        mutate = [sys.executable, "-c", f"__import__('pathlib').Path({str(self.artifact)!r}).write_bytes(b'tampered')"]
        self.envelope["allowed_commands"].append(mutate)
        self.plan["steps"][0]["command"] = mutate
        code, report = self.run_supervisor()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "rolled_back")
        self.assertEqual(report["rollback"]["reason"], "artifact identity changed during run")

    def test_required_environment_digest_mismatch_is_blocked(self):
        self.envelope["environment_bindings"] = {
            "inherit": ["SFSE_TEST_CREDENTIAL"],
            "required_sha256": {"SFSE_TEST_CREDENTIAL": "0" * 64},
        }
        code, report = self.run_supervisor()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["phase"], "validation")
        self.assertTrue(any("environment variable" in error for error in report["errors"]), report)

    def test_workspace_snapshot_failure_after_deploy_rolls_back(self):
        with mock.patch.object(supervisor_module, "workspace_snapshot", side_effect=[{}, OSError("snapshot unavailable")]):
            code, report = self.run_supervisor()
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "rolled_back")
        self.assertIn("workspace snapshot failed", report["rollback"]["reason"])

    def test_validator_and_supervisor_cli_outputs_are_redacted(self):
        sensitive_path = str(self.root.parent / "private-customer-path")
        self.plan["workspace"] = sensitive_path
        envelope_path = self.root / "envelope.json"
        plan_path = self.root / "plan.json"
        envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        plan_path.write_text(json.dumps(self.plan), encoding="utf-8")

        for script in ("validate_autonomy_plan.py", "autonomy_supervisor.py"):
            completed = subprocess.run(
                [sys.executable, str(SCRIPTS / script), str(envelope_path), str(plan_path)],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0, script)
            payload = json.loads(completed.stdout)
            self.assertGreater(payload["error_count"], 0, script)
            self.assertNotIn(sensitive_path, completed.stdout, script)


if __name__ == "__main__":
    unittest.main()
