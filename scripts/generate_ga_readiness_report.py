#!/usr/bin/env python3
"""Generate an evidence-backed GA readiness summary without promoting an RC."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--security-report", required=True)
    parser.add_argument("--reproducibility-report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    metadata = load(ROOT / "docs/public-metadata.json") or {}
    scorecard = load(Path(args.scorecard))
    security = load(Path(args.security_report))
    reproducibility = load(Path(args.reproducibility_report))
    evidence_dir = ROOT / "release-evidence" / version

    blockers: list[dict] = []
    if not scorecard or scorecard.get("status") != "GA_GATE_PASS":
        failed = [gate["name"] for gate in (scorecard or {}).get("gates", []) if not gate.get("pass")]
        blockers.append({"id": "GA-QUALIFICATION", "detail": "full qualification scorecard has not passed", "failed_gates": failed})
    if not security or security.get("status") != "PASS":
        blockers.append({"id": "GA-LOCAL-SECURITY", "detail": "deterministic local release security review has not passed"})
    if not reproducibility or reproducibility.get("status") != "PASS":
        blockers.append({"id": "GA-REPRODUCIBILITY", "detail": "reproducible build qualification has not passed"})
    if metadata.get("status") != "APPROVED_FOR_PUBLICATION":
        blockers.append({"id": "GA-PUBLIC-METADATA", "detail": "public repository and policy metadata are not approved"})

    external = {
        "GA-INDEPENDENT-SECURITY": "independent-security-report.json",
        "GA-INDEPENDENT-JUDGE": "independent-judge-report.json",
        "GA-AUTONOMY-REHEARSAL": "autonomy-rehearsal-report.json",
        "GA-GITHUB-CHECKS": "github-checks.json",
        "GA-ATTESTATION": "attestation-verification.json",
    }
    for blocker_id, filename in external.items():
        report = load(evidence_dir / filename)
        if not report or report.get("status") != "PASS":
            blockers.append({"id": blocker_id, "detail": f"missing passing external evidence: release-evidence/{version}/{filename}"})

    local_ready = bool(
        security and security.get("status") == "PASS"
        and reproducibility and reproducibility.get("status") == "PASS"
        and any(g.get("name") == "bounded_autonomy_controls" and g.get("pass") for g in (scorecard or {}).get("gates", []))
    )
    result = {
        "schema_version": "1.0",
        "version": version,
        "status": "GA_READY" if not blockers and version == "1.0.0" else "GA_BLOCKED",
        "local_candidate_controls_ready": local_ready,
        "unattended_operation_model": "bounded-preauthorized-default-deny",
        "unlimited_autonomy_supported": False,
        "public_release_performed": False,
        "scorecard_status": (scorecard or {}).get("status"),
        "blockers": blockers,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"# GA Readiness - {version}",
        "",
        f"**Status:** `{result['status']}`",
        f"**Local candidate controls:** `{'PASS' if local_ready else 'BLOCKED'}`",
        "",
        "Unattended execution is supported only inside an explicit, bounded, preauthorized envelope. Unlimited autonomy is not supported.",
        "",
        "## Blocking gates",
        "",
    ]
    if blockers:
        lines.extend(f"- `{row['id']}` - {row['detail']}" for row in blockers)
    else:
        lines.append("- None")
    Path(args.markdown_output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "GA_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
