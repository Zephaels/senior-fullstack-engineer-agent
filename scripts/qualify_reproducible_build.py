#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build() -> dict:
    completed = subprocess.run([sys.executable, "scripts/build_release.py"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return json.loads((ROOT / "dist/release-packages.json").read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    first = build()
    second = build()
    first_rows = {Path(row["path"]).name: row["sha256"] for row in first["packages"]}
    second_rows = {Path(row["path"]).name: row["sha256"] for row in second["packages"]}
    result = {
        "schema_version": "1.0",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "status": "PASS" if first_rows == second_rows else "FAIL",
        "source_date_epoch": first.get("source_date_epoch"),
        "first": first_rows,
        "second": second_rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
