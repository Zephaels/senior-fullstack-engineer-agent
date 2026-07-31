#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import invoke_runner

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = ROOT.parents[1]


def normalize_skill(value: str) -> str:
    return value.split(":", 1)[-1]


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*"), key=lambda value: value.as_posix()):
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode() + b"\0" + item.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-runner-command")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--output", default=str(ROOT / "eval-engine" / "reports" / "brownfield-e2e.json"))
    args = parser.parse_args()
    case_path = ROOT / "evals" / "brownfield" / "brownfield_e2e.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))["cases"][0]
    fixture = (ROOT / case["workspace_fixture"]).resolve()
    plugin = (REPOSITORY / "plugins" / "senior-fullstack-engineer-agent").resolve()
    report = {
        "suite": "brownfield-plugin-e2e-v1",
        "case_id": case["id"],
        "fixture_sha256": fingerprint(fixture),
        "plugin_sha256": fingerprint(plugin),
        "status": "BLOCKED_NO_CODEX_RUNTIME_RUNNER",
        "pass": False,
        "result": None,
        "checks": [],
    }
    if args.runtime_runner_command:
        request = {
            "task_type": "brownfield-e2e",
            "prompt": case["prompt"],
            "plugin_path": str(plugin),
            "workspace_fixture": str(fixture),
            "verification_commands": case["verification_commands"],
            "force_reload": True,
            "new_session": True,
            "response_contract": {"selected_skills": [case["expected_skill"]], "output": "text", "tool_calls": [], "changed_files": case["expected_changed_files"]},
        }
        result = invoke_runner(args.runtime_runner_command, request, args.timeout)
        if result.get("status") != "completed":
            blocked = result.get("error_class") == "transient_host_exhausted" or result.get("status") == "runner_error"
            report.update({
                "status": "BLOCKED_HOST_RUNTIME" if blocked else "FAILED",
                "pass": False,
                "result": result,
                "checks": [{"name": "real-runtime-completed", "pass": False, "classification": "host-blocker" if blocked else "candidate-failure"}],
            })
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 2
        selected = [normalize_skill(value) for value in result.get("selected_skills", [])]
        verification = result.get("runner_metadata", {}).get("verification_results", [])
        checks = [
            {"name": "real-runtime-completed", "pass": result.get("status") == "completed"},
            {"name": "specialist-route", "pass": case["expected_skill"] in selected},
            {"name": "exact-diff-scope", "pass": sorted(result.get("changed_files", [])) == sorted(case["expected_changed_files"])},
            {"name": "verification-command", "pass": bool(verification) and all(item.get("returncode") == 0 for item in verification)},
            {"name": "no-declined-operations", "pass": not any(not item.get("accepted") for item in result.get("runner_metadata", {}).get("approval_decisions", []))},
        ]
        report.update({"status": "COMPLETED" if all(item["pass"] for item in checks) else "FAILED", "pass": all(item["pass"] for item in checks), "result": result, "checks": checks})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
