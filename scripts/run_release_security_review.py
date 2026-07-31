#!/usr/bin/env python3
"""Deterministic local release security checks; not an independent audit."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", "dist", "qualification-results", "release-evidence", "__pycache__"}
ACTION_REF = re.compile(r"^[^\s@]+@[0-9a-f]{40}$")
USES_LINE = re.compile(r"^\s*uses:\s*([^\s#]+)(?:\s+#.*)?$", re.MULTILINE)
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai-key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
}


def included(path: Path) -> bool:
    return path.is_file() and not any(part in IGNORED for part in path.parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    findings: list[dict] = []

    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        for match in USES_LINE.finditer(text):
            value = match.group(1)
            if not ACTION_REF.fullmatch(value):
                findings.append({"severity": "high", "rule": "unpinned-action", "file": str(workflow.relative_to(ROOT)), "value": match.group(1)})

    for base in (ROOT / "scripts", ROOT / "source"):
        for path in sorted(base.rglob("*.py")):
            if not included(path):
                continue
            text = path.read_text(encoding="utf-8")
            if re.search(r"\bshell\s*=\s*True\b", text):
                findings.append({"severity": "high", "rule": "shell-true", "file": str(path.relative_to(ROOT))})

    for path in sorted(ROOT.rglob("*")):
        if not included(path) or path.suffix.lower() in {".zip", ".png", ".jpg", ".jpeg", ".gif", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append({"severity": "critical", "rule": name, "file": str(path.relative_to(ROOT))})

    release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    if re.search(r"ENABLE_ARTIFACT_ATTESTATION|\bif:\s*.*attest", release):
        findings.append({"severity": "high", "rule": "optional-attestation", "file": ".github/workflows/release.yml"})
    if "gh attestation verify" not in release:
        findings.append({"severity": "high", "rule": "attestation-not-verified", "file": ".github/workflows/release.yml"})
    if "validate_public_release.py" not in release:
        findings.append({"severity": "high", "rule": "public-gate-missing", "file": ".github/workflows/release.yml"})

    result = {
        "schema_version": "1.0",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "status": "PASS" if not findings else "FAIL",
        "scope": "deterministic-local-release-review",
        "independent_security_audit": False,
        "findings": findings,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    # The report file is the controlled review artifact. Avoid copying file
    # contents, workflow references, or secret-scanner findings into CI logs.
    summary = {
        "status": result["status"],
        "scope": result["scope"],
        "finding_count": len(findings),
    }
    print(json.dumps(summary, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
