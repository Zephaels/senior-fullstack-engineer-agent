#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
checks = []


def run(name, command):
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    checks.append({
        "name": name,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    })
    return result.returncode == 0


ok = run("rc", [sys.executable, "scripts/validate_rc.py"])
ok = run("plugin", [sys.executable, "scripts/validate_plugin.py", "plugins/senior-fullstack-engineer-agent"]) and ok
ok = run("release-security", [sys.executable, "scripts/run_release_security_review.py", "--output", "qualification-results/security/release-security-report.json"]) and ok

try:
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    entry = next(x for x in marketplace["plugins"] if x["name"] == "senior-fullstack-engineer-agent")
    assert entry["source"]["path"] == "./plugins/senior-fullstack-engineer-agent"
    assert entry["policy"]["installation"] in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
    assert entry["policy"]["authentication"] in {"ON_INSTALL", "ON_USE"}
except Exception as exc:
    ok = False
    checks.append({"name": "marketplace", "returncode": 1, "stderr": str(exc)})
else:
    checks.append({"name": "marketplace", "returncode": 0, "stdout": "marketplace validation passed"})

print(json.dumps({"ok": ok, "version": (ROOT / "VERSION").read_text().strip(), "checks": checks}, indent=2))
raise SystemExit(0 if ok else 1)
