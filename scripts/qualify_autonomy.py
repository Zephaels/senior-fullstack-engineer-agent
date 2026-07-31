#!/usr/bin/env python3
"""Produce deterministic qualification evidence for bounded autonomy controls."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = "senior-fullstack-engineer-agent"
SOURCE = ROOT / "source" / NAME
PLUGIN_SKILL = ROOT / "plugins" / NAME / "skills" / "release-deployment"
SOURCE_SCRIPTS = SOURCE / "scripts"


def load(name: str, path: Path):
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "qualification-results" / "autonomy" / "autonomy-qualification.json"))
    args = parser.parse_args()
    envelope_validator = load("sfse_envelope_validator", SOURCE_SCRIPTS / "validate_autonomy_envelope.py")
    plan_validator = load("sfse_plan_validator", SOURCE_SCRIPTS / "validate_autonomy_plan.py")
    envelope = json.loads((SOURCE / "templates" / "autonomy-run-envelope.json").read_text(encoding="utf-8"))
    plan = json.loads((SOURCE / "templates" / "autonomy-run-plan.json").read_text(encoding="utf-8"))
    checks = []

    def add(name: str, ok: bool, detail: str):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    envelope_errors = envelope_validator.validate(envelope, allow_expired=True)
    add("authorization-envelope", not envelope_errors, "; ".join(envelope_errors) or "valid")
    plan_errors = plan_validator.validate_plan(envelope, plan, allow_expired=True)
    add("exact-run-plan", not plan_errors, "; ".join(plan_errors) or "valid")

    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_autonomy_policy", "tests.test_autonomy_supervisor", "-v"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=120,
    )
    add("fault-injection-tests", completed.returncode == 0, (completed.stdout + completed.stderr)[-4000:])

    required = [
        "references/templates/autonomy-run-envelope.json",
        "references/templates/autonomy-run-plan.json",
        "references/schemas/autonomy-run-envelope.schema.json",
        "references/schemas/autonomy-run-plan.schema.json",
        "scripts/validate_autonomy_envelope.py",
        "scripts/validate_autonomy_plan.py",
        "scripts/autonomy_supervisor.py",
    ]
    missing = [relative for relative in required if not (PLUGIN_SKILL / relative).is_file()]
    add("self-contained-plugin-runtime", not missing, "missing: " + ", ".join(missing) if missing else "all autonomy runtime files bundled")

    report = {
        "schema_version": "1.0",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "PASS" if all(item["ok"] for item in checks) else "FAIL",
        "ok": all(item["ok"] for item in checks),
        "scope": "deterministic bounded-autonomy controls; no real production deployment performed",
        "checks": checks,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
