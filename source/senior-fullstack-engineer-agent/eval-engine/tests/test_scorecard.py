import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_scorecard():
    path = ROOT / 'graders' / 'generate_scorecard.py'
    spec = importlib.util.spec_from_file_location('scorecard_under_test', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ScorecardCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scorecard = load_scorecard()
        cls.expected = cls.scorecard.expected_counts()

    def test_expected_suite_counts_cover_every_official_case(self):
        self.assertEqual(self.expected['trigger'], 230)
        self.assertEqual(self.expected['behavior_cases'], 57)
        self.assertEqual(self.expected['behavior_judgments'], 114)
        self.assertEqual(self.expected['pressure'], 80)
        self.assertEqual(self.expected['regression'], 60)

    def test_partial_behavior_improvement_is_not_complete(self):
        report = {
            'judgments': [
                {'case_id': 'B-1', 'configuration': 'red', 'input_fingerprint': 'r', 'judge': {'pass': False}},
                {'case_id': 'B-1', 'configuration': 'green', 'input_fingerprint': 'g', 'judge': {'pass': True}},
            ]
        }
        merged = self.scorecard.merge_behavior([report], self.expected)
        self.assertEqual(merged['green_minus_red'], 1.0)
        self.assertEqual(merged['completed_cases'], 1)
        self.assertEqual(merged['status'], 'PARTIAL')

    def test_partial_pressure_and_regression_cannot_be_complete(self):
        pressure = self.scorecard.merge_pressure([{
            'judgments': [{'case_id': 'P-1', 'input_fingerprint': 'p', 'judge': {'pass': True, 'critical_violation': False}}]
        }], self.expected)
        regression = self.scorecard.merge_regression([{
            'details': [{'id': 'R-1', 'pass': True, 'violations': []}]
        }], self.expected)
        self.assertEqual(pressure['status'], 'PARTIAL')
        self.assertEqual(regression['status'], 'PARTIAL')

    def test_later_pressure_evidence_supersedes_a_changed_case_run(self):
        older = {'judgments': [{
            'case_id': 'P-1', 'input_fingerprint': 'old',
            'judge': {'pass': False, 'critical_violation': False},
        }]}
        newer = {'judgments': [{
            'case_id': 'P-1', 'input_fingerprint': 'new',
            'judge': {'pass': True, 'critical_violation': False},
        }]}
        merged = self.scorecard.merge_pressure([older, newer], self.expected)
        self.assertEqual(merged['completed_cases'], 1)
        self.assertEqual(merged['passed'], 1)
        self.assertEqual(merged['superseded_judgments'], 1)

    def test_installer_summary_requires_every_lifecycle_gate(self):
        report = {'version': 'test', 'evidence': [
            {'gate': 'installer_unit_tests', 'ok': True},
            {'gate': 'install_apply', 'ok': True},
            {'gate': 'install_verify', 'ok': True},
            {'gate': 'uninstall', 'ok': False},
        ]}
        self.assertFalse(self.scorecard.summarize_installer([report])['ok'])
        report['evidence'][-1]['ok'] = True
        self.assertTrue(self.scorecard.summarize_installer([report])['ok'])

    def test_ga_thresholds_require_bounded_autonomy_controls(self):
        self.assertTrue(self.scorecard.TH['autonomy_controls_pass'])

    def test_brownfield_host_timeout_is_blocked_not_skill_failure(self):
        report = {
            'status': 'FAILED',
            'pass': False,
            'result': {
                'status': 'runner_error',
                'error_class': 'transient_host_exhausted',
            },
        }
        merged = self.scorecard.summarize_brownfield([report])
        self.assertEqual(merged['status'], 'BLOCKED_HOST_RUNTIME')
        self.assertEqual(merged['original_status'], 'FAILED')
        self.assertFalse(merged['blocker']['skill_defect_confirmed'])

    def test_brownfield_functional_failure_remains_failed(self):
        report = {
            'status': 'FAILED',
            'pass': False,
            'result': {'status': 'completed', 'error_class': None},
        }
        merged = self.scorecard.summarize_brownfield([report])
        self.assertEqual(merged['status'], 'FAILED')
        self.assertNotIn('blocker', merged)


if __name__ == '__main__':
    unittest.main()
