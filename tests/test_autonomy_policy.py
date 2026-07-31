import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "source" / "senior-fullstack-engineer-agent" / "scripts" / "validate_autonomy_envelope.py"
TEMPLATE = ROOT / "source" / "senior-fullstack-engineer-agent" / "templates" / "autonomy-run-envelope.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_autonomy_envelope", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AutonomyPolicyTests(unittest.TestCase):
    def setUp(self):
        self.module = load_validator()
        self.envelope = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_static_template_is_structurally_valid(self):
        self.assertEqual(self.module.validate(self.envelope, allow_expired=True), [])

    def test_expired_envelope_is_denied_at_runtime(self):
        errors = self.module.validate(self.envelope)
        self.assertIn("authorization envelope is expired", errors)

    def test_broad_path_is_denied(self):
        self.envelope["allowed_paths"] = ["C:\\"]
        errors = self.module.validate(self.envelope, allow_expired=True)
        self.assertTrue(any("too broad" in error for error in errors), errors)

    def test_shell_control_operator_is_denied(self):
        self.envelope["allowed_commands"] = [["release-tool", "deploy; remove-everything"]]
        errors = self.module.validate(self.envelope, allow_expired=True)
        self.assertTrue(any("control operators" in error for error in errors), errors)

    def test_missing_explicit_approval_is_denied(self):
        self.envelope["approval"] = {"type": "implicit", "evidence_ref": ""}
        errors = self.module.validate(self.envelope, allow_expired=True)
        self.assertIn("explicit preauthorization evidence is required", errors)


if __name__ == "__main__":
    unittest.main()
