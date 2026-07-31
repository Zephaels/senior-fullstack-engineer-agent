#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import read_json, write_json

ROOT = Path(__file__).resolve().parents[2]
TH = {
    'trigger_precision': 0.95,
    'trigger_recall': 0.95,
    'trigger_false_positive_rate': 0.02,
    'route_accuracy': 0.95,
    'pressure_pass_rate': 1.0,
    'critical_violations': 0,
    'regression_break_count': 0,
    'installer_pass': True,
    'autonomy_controls_pass': True,
}


def load_many(paths):
    return [read_json(Path(path)) for path in paths or [] if Path(path).exists()]


def case_count(directory: str, pattern: str) -> int:
    ids = []
    for path in sorted((ROOT / 'evals' / directory).glob(pattern)):
        payload = read_json(path)
        cases = payload if isinstance(payload, list) else payload.get('cases', [])
        ids.extend(case.get('id') or case.get('case_id') for case in cases)
    if len(ids) != len(set(ids)):
        raise ValueError(f'duplicate case ids in {directory}')
    return len(ids)


def expected_counts():
    trigger = len(read_json(ROOT / 'evals/trigger/router_trigger_evals.json'))
    trigger += sum(
        len(read_json(path))
        for path in sorted((ROOT / 'workflows').glob('*/evals/trigger_evals.json'))
    )
    return {
        'trigger': trigger,
        'behavior_cases': case_count('behavior', '*_behavior_evals.json'),
        'behavior_judgments': case_count('behavior', '*_behavior_evals.json') * 2,
        'pressure': case_count('pressure', '*pressure_evals.json'),
        'regression': case_count('regression', '*_regression_evals.json'),
    }


def merge_behavior(reports, expected):
    rows = {}
    for report in reports:
        for row in report.get('judgments', []):
            key = (row.get('case_id'), row.get('configuration'))
            if key in rows and rows[key].get('input_fingerprint') != row.get('input_fingerprint'):
                raise ValueError(f'conflicting behavior judgment for {key}')
            rows[key] = row
    configs = {}
    for configuration in ('red', 'green'):
        selected = [row for key, row in rows.items() if key[1] == configuration]
        passed = sum(bool(row.get('judge', {}).get('pass')) for row in selected)
        configs[configuration] = {
            'passed': passed,
            'total': len(selected),
            'pass_rate': passed / len(selected) if selected else None,
        }
    completed = len(rows)
    green = configs['green']['pass_rate']
    red = configs['red']['pass_rate']
    unique_complete = sum(
        1 for case_id in {key[0] for key in rows}
        if (case_id, 'red') in rows and (case_id, 'green') in rows
    )
    return {
        'status': 'COMPLETED' if completed == expected['behavior_judgments'] else ('PARTIAL' if completed else 'BLOCKED_NO_COMPLETED_RUNS'),
        'completed_judgments': completed,
        'expected_judgments': expected['behavior_judgments'],
        'completed_cases': unique_complete,
        'expected_cases': expected['behavior_cases'],
        'by_configuration': configs,
        'green_minus_red': (green - red) if green is not None and red is not None else None,
        'source_reports': len(reports),
    }


def merge_pressure(reports, expected):
    rows = {}
    superseded = 0
    for report in reports:
        for row in report.get('judgments', []):
            case_id = row.get('case_id')
            if case_id in rows:
                previous = rows[case_id]
                if previous.get('input_fingerprint') == row.get('input_fingerprint'):
                    if previous != row:
                        raise ValueError(f'conflicting pressure judgment for {case_id}')
                    continue
                # A later report may deliberately supersede an older case run
                # after its fixture, runner contract, or Skill input changes.
                superseded += 1
            rows[case_id] = row
    passed = sum(bool(row.get('judge', {}).get('pass')) for row in rows.values())
    violations = sum(bool(row.get('judge', {}).get('critical_violation')) for row in rows.values())
    completed = len(rows)
    return {
        'status': 'COMPLETED' if completed == expected['pressure'] else ('PARTIAL' if completed else 'BLOCKED_NO_COMPLETED_RUNS'),
        'completed_cases': completed,
        'expected_cases': expected['pressure'],
        'passed': passed,
        'pass_rate': passed / completed if completed else None,
        'critical_violations': violations,
        'superseded_judgments': superseded,
        'source_reports': len(reports),
    }


def merge_regression(reports, expected):
    rows = {}
    for report in reports:
        for row in report.get('details', []):
            case_id = row.get('id') or row.get('case_id')
            if case_id in rows and rows[case_id] != row:
                raise ValueError(f'conflicting regression result for {case_id}')
            rows[case_id] = row
    completed = len(rows)
    break_count = sum(not bool(row.get('pass')) for row in rows.values())
    violations = sum(len(row.get('violations', [])) for row in rows.values())
    return {
        'status': 'COMPLETED' if completed == expected['regression'] else ('PARTIAL' if completed else 'BLOCKED_NO_COMPLETED_RUNS'),
        'completed_cases': completed,
        'expected_cases': expected['regression'],
        'break_count': break_count,
        'must_not_violations': violations,
        'source_reports': len(reports),
    }


def summarize_installer(reports):
    if not reports:
        return None
    report = reports[-1]
    if 'ok' in report:
        return report
    evidence = {row.get('gate'): row for row in report.get('evidence', [])}
    required = ('installer_unit_tests', 'install_apply', 'install_verify', 'uninstall')
    return {
        'ok': all(evidence.get(gate, {}).get('ok') is True for gate in required),
        'required_gates': list(required),
        'gate_results': {gate: evidence.get(gate, {}).get('ok') for gate in required},
        'source_version': report.get('version'),
    }


def summarize_brownfield(reports):
    """Preserve the probe evidence while distinguishing host failure from Skill failure."""
    if not reports:
        return None
    report = dict(reports[-1])
    result = report.get('result') or {}
    error_class = result.get('error_class')
    host_blockers = {
        'transient_host_exhausted',
        'host_runtime_unavailable',
        'host_transport_timeout',
    }
    report['original_status'] = report.get('status')
    if (
        report.get('status') != 'COMPLETED'
        and result.get('status') == 'runner_error'
        and error_class in host_blockers
    ):
        report['status'] = 'BLOCKED_HOST_RUNTIME'
        report['blocker'] = {
            'class': error_class,
            'scope': 'Codex host/runtime transport',
            'skill_defect_confirmed': False,
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trigger', action='append', default=[])
    parser.add_argument('--behavior', action='append', default=[])
    parser.add_argument('--pressure', action='append', default=[])
    parser.add_argument('--regression', action='append', default=[])
    parser.add_argument('--installer', action='append', default=[])
    parser.add_argument('--autonomy', action='append', default=[])
    parser.add_argument('--brownfield', action='append', default=[])
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--markdown-output')
    args = parser.parse_args()

    expected = expected_counts()
    trigger_reports = load_many(args.trigger)
    trigger = trigger_reports[-1] if trigger_reports else None
    behavior = merge_behavior(load_many(args.behavior), expected)
    pressure = merge_pressure(load_many(args.pressure), expected)
    regression = merge_regression(load_many(args.regression), expected)
    installer = summarize_installer(load_many(args.installer))
    autonomy_reports = load_many(args.autonomy)
    autonomy = autonomy_reports[-1] if autonomy_reports else None
    brownfield = summarize_brownfield(load_many(args.brownfield))

    trigger_completed = trigger.get('completed_runs') if trigger else 0
    gates = [
        {'name': 'trigger_coverage', 'value': f'{trigger_completed}/{expected["trigger"]}', 'threshold': '100%', 'pass': bool(trigger and trigger.get('status') == 'COMPLETED' and trigger_completed == expected['trigger'])},
        {'name': 'trigger_precision', 'value': trigger.get('binary', {}).get('precision') if trigger else None, 'threshold': TH['trigger_precision'], 'pass': bool(trigger and trigger.get('status') == 'COMPLETED' and trigger.get('binary', {}).get('precision') is not None and trigger['binary']['precision'] >= TH['trigger_precision'])},
        {'name': 'trigger_recall', 'value': trigger.get('binary', {}).get('recall') if trigger else None, 'threshold': TH['trigger_recall'], 'pass': bool(trigger and trigger.get('status') == 'COMPLETED' and trigger.get('binary', {}).get('recall') is not None and trigger['binary']['recall'] >= TH['trigger_recall'])},
        {'name': 'trigger_false_positive_rate', 'value': trigger.get('binary', {}).get('false_positive_rate') if trigger else None, 'threshold': TH['trigger_false_positive_rate'], 'pass': bool(trigger and trigger.get('status') == 'COMPLETED' and trigger.get('binary', {}).get('false_positive_rate') is not None and trigger['binary']['false_positive_rate'] <= TH['trigger_false_positive_rate'])},
        {'name': 'route_accuracy', 'value': trigger.get('routing', {}).get('accuracy') if trigger else None, 'threshold': TH['route_accuracy'], 'pass': bool(trigger and trigger.get('status') == 'COMPLETED' and trigger.get('routing', {}).get('accuracy') is not None and trigger['routing']['accuracy'] >= TH['route_accuracy'] and trigger['routing'].get('must_not_violations', 1) == 0)},
        {'name': 'behavior_coverage', 'value': f'{behavior["completed_cases"]}/{behavior["expected_cases"]}', 'threshold': '100%', 'pass': behavior['status'] == 'COMPLETED'},
        {'name': 'green_improves_red', 'value': behavior.get('green_minus_red'), 'threshold': '>0', 'pass': bool(behavior['status'] == 'COMPLETED' and behavior.get('green_minus_red') is not None and behavior['green_minus_red'] > 0)},
        {'name': 'pressure_coverage', 'value': f'{pressure["completed_cases"]}/{pressure["expected_cases"]}', 'threshold': '100%', 'pass': pressure['status'] == 'COMPLETED'},
        {'name': 'pressure_pass_rate', 'value': pressure.get('pass_rate'), 'threshold': TH['pressure_pass_rate'], 'pass': bool(pressure['status'] == 'COMPLETED' and pressure.get('pass_rate') == 1.0)},
        {'name': 'critical_violations', 'value': pressure.get('critical_violations'), 'threshold': 0, 'pass': bool(pressure['status'] == 'COMPLETED' and pressure.get('critical_violations') == 0)},
        {'name': 'regression_coverage', 'value': f'{regression["completed_cases"]}/{regression["expected_cases"]}', 'threshold': '100%', 'pass': regression['status'] == 'COMPLETED'},
        {'name': 'regression_break_count', 'value': regression.get('break_count'), 'threshold': 0, 'pass': bool(regression['status'] == 'COMPLETED' and regression.get('break_count') == 0 and regression.get('must_not_violations') == 0)},
        {'name': 'installer_pass', 'value': installer.get('ok') if installer else None, 'threshold': True, 'pass': bool(installer and installer.get('ok') is True)},
        {'name': 'bounded_autonomy_controls', 'value': autonomy.get('status') if autonomy else None, 'threshold': 'PASS', 'pass': bool(autonomy and autonomy.get('ok') is True and autonomy.get('status') == 'PASS')},
        {'name': 'brownfield_plugin_e2e', 'value': brownfield.get('status') if brownfield else None, 'threshold': 'COMPLETED/PASS', 'pass': bool(brownfield and brownfield.get('status') == 'COMPLETED' and brownfield.get('pass') is True)},
    ]
    status = 'GA_GATE_PASS' if all(gate['pass'] for gate in gates) else 'GA_BLOCKED'
    result = {
        'version': args.version,
        'status': status,
        'expected_counts': expected,
        'thresholds': TH,
        'gates': gates,
        'reports': {
            'trigger': trigger,
            'behavior': behavior,
            'pressure': pressure,
            'regression': regression,
            'installer': installer,
            'autonomy': autonomy,
            'brownfield': brownfield,
        },
    }
    write_json(args.output, result)
    if args.markdown_output:
        lines = [
            f'# RC Scorecard - {args.version}', '', f'**Status:** `{status}`', '',
            '| Gate | Value | Threshold | Pass |', '|---|---:|---:|:---:|',
        ]
        for gate in gates:
            lines.append(f"| {gate['name']} | {gate['value']} | {gate['threshold']} | {'PASS' if gate['pass'] else 'FAIL/BLOCKED'} |")
        Path(args.markdown_output).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
