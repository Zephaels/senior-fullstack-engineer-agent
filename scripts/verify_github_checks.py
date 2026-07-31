#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--required", action="append", default=["validate", "analyze"])
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    runs = payload.get("check_runs", [])
    matched = {}
    for required in args.required:
        candidates = [
            row for row in runs
            if required.lower() in str(row.get("name", "")).lower()
            and row.get("head_sha") == args.commit
        ]
        matched[required] = [
            {"name": row.get("name"), "status": row.get("status"), "conclusion": row.get("conclusion"), "details_url": row.get("details_url")}
            for row in candidates
        ]
    ok = all(rows and any(row.get("status") == "completed" and row.get("conclusion") == "success" for row in rows) for rows in matched.values())
    result = {"schema_version": "1.0", "status": "PASS" if ok else "FAIL", "target_commit_sha": args.commit, "required_checks": matched}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
