#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
STRICT_VERSION = re.compile(r"^1\.0\.0$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_external_report(name: str, report: dict, version: str, target_commit: str | None = None) -> list[str]:
    errors: list[str] = []
    if report.get("version") != version:
        errors.append(f"{name} version must match {version}")
    if report.get("status") != "PASS":
        errors.append(f"{name} status must be PASS")
    if not COMMIT_SHA.fullmatch(str(report.get("target_commit_sha", ""))):
        errors.append(f"{name} target_commit_sha must be a full Git commit SHA")
    elif target_commit and report.get("target_commit_sha") != target_commit:
        errors.append(f"{name} target_commit_sha does not match the tagged commit")
    if not https_url(report.get("report_url")):
        errors.append(f"{name} report_url must be an approved HTTPS URL")
    if not SHA256.fullmatch(str(report.get("evidence_sha256", ""))):
        errors.append(f"{name} evidence_sha256 must be SHA-256")

    if name == "independent_security":
        if report.get("type") != "independent-security-assessment":
            errors.append("independent_security type is invalid")
        assessor = report.get("assessor") or {}
        if not assessor.get("organization") or not assessor.get("tool"):
            errors.append("independent_security assessor organization and tool are required")
        findings = report.get("findings") or {}
        if findings.get("critical") != 0 or findings.get("high") != 0:
            errors.append("independent_security requires zero open critical and high findings")
    elif name == "independent_judge":
        if report.get("type") != "independent-model-evaluation":
            errors.append("independent_judge type is invalid")
        candidate = report.get("candidate_model_family")
        judge = report.get("judge_model_family")
        if not candidate or not judge or candidate == judge:
            errors.append("independent_judge must use a different model family")
        if report.get("judge_session_isolated") is not True:
            errors.append("independent_judge requires an isolated judge session")
        counts = report.get("evaluated_case_counts") or {}
        required = {"trigger": 230, "behavior": 57, "pressure": 80, "regression": 60}
        for key, expected in required.items():
            if counts.get(key) != expected:
                errors.append(f"independent_judge {key} coverage must be {expected}")
        if (report.get("metrics") or {}).get("critical_violations") != 0:
            errors.append("independent_judge requires zero critical violations")
    elif name == "autonomy_rehearsal":
        if report.get("type") != "bounded-autonomy-staging-rehearsal":
            errors.append("autonomy_rehearsal type is invalid")
        if report.get("environment") not in {"staging", "preproduction"}:
            errors.append("autonomy_rehearsal must run in staging or preproduction")
        for field in ("artifact_sha256", "envelope_sha256", "plan_sha256", "journal_sha256"):
            if not SHA256.fullmatch(str(report.get(field, ""))):
                errors.append(f"autonomy_rehearsal {field} must be SHA-256")
        for field in ("dry_run_pass", "canary_pass", "health_gate_pass", "rollback_fault_injection_pass", "no_unauthorized_actions"):
            if report.get(field) is not True:
                errors.append(f"autonomy_rehearsal {field} must be true")
        if report.get("final_state") not in {"succeeded", "rolled_back"}:
            errors.append("autonomy_rehearsal final_state must be succeeded or rolled_back")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--target-commit", required=True)
    parser.add_argument("--scorecard")
    parser.add_argument("--security-report", required=True)
    parser.add_argument("--reproducibility-report", required=True)
    parser.add_argument("--github-checks", required=True)
    parser.add_argument("--independent-security-report", required=True)
    parser.add_argument("--independent-judge-report", required=True)
    parser.add_argument("--autonomy-rehearsal-report", required=True)
    args = parser.parse_args()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    evidence = ROOT / "release-evidence" / version
    scorecard_path = Path(args.scorecard) if args.scorecard else evidence / "scorecard.json"
    metadata = load(ROOT / "docs/public-metadata.json")
    errors: list[str] = []

    if not COMMIT_SHA.fullmatch(args.target_commit):
        errors.append("target_commit must be a full Git commit SHA")

    if not STRICT_VERSION.fullmatch(version):
        errors.append(f"public v1 GA requires VERSION 1.0.0, found {version}")
    if args.tag != f"v{version}":
        errors.append(f"tag {args.tag} does not match VERSION {version}")
    if metadata.get("status") != "APPROVED_FOR_PUBLICATION":
        errors.append("public metadata is not approved")
    if metadata.get("license_spdx") != "Apache-2.0":
        errors.append("license_spdx must be Apache-2.0")
    if metadata.get("public_release_channel") != "ga":
        errors.append("public_release_channel must be ga")
    for key in ("repository_url", "homepage_url", "support_url", "security_contact_url", "privacy_policy_url", "terms_of_service_url"):
        if not https_url(metadata.get(key)):
            errors.append(f"{key} must be an approved HTTPS URL")

    reports = {
        "scorecard": (scorecard_path, "GA_GATE_PASS"),
        "security": (Path(args.security_report), "PASS"),
        "reproducibility": (Path(args.reproducibility_report), "PASS"),
        "github_checks": (Path(args.github_checks), "PASS"),
    }
    observed = {}
    for name, (path, expected) in reports.items():
        if not path.is_file():
            errors.append(f"missing {name} evidence: {path}")
            continue
        report = load(path)
        observed[name] = {"path": str(path), "status": report.get("status")}
        if report.get("version") not in (None, version):
            errors.append(f"{name} version does not match {version}")
        if report.get("status") != expected:
            errors.append(f"{name} status must be {expected}, found {report.get('status')}")
        if name == "github_checks" and report.get("target_commit_sha") != args.target_commit:
            errors.append("github_checks target_commit_sha does not match the tagged commit")

    external_reports = {
        "independent_security": Path(args.independent_security_report),
        "independent_judge": Path(args.independent_judge_report),
        "autonomy_rehearsal": Path(args.autonomy_rehearsal_report),
    }
    for name, path in external_reports.items():
        if not path.is_file():
            errors.append(f"missing {name} evidence: {path}")
            continue
        report = load(path)
        observed[name] = {"path": str(path), "status": report.get("status")}
        errors.extend(validate_external_report(name, report, version, args.target_commit))

    result = {"version": version, "tag": args.tag, "status": "PASS" if not errors else "BLOCKED", "reports": observed, "errors": errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
