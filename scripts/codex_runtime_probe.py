#!/usr/bin/env python3
"""Probe Codex runtime prerequisites without fabricating qualification evidence."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess
from pathlib import Path


def run(cmd: list[str]) -> dict:
    try:
        cp = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
        return {"command": cmd, "returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}
    except Exception as exc:
        return {"command": cmd, "error": type(exc).__name__, "detail": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output')
    args = ap.parse_args()
    codex = shutil.which('codex')
    result = {
        "status": "READY" if codex else "BLOCKED_CODEX_NOT_INSTALLED",
        "codex_path": codex,
        "openai_api_key": bool(os.environ.get('OPENAI_API_KEY')),
        "checks": [],
        "limitations": [],
    }
    if codex:
        result["checks"].append(run([codex, '--version']))
        result["checks"].append(run([codex, 'login', 'status']))
        result["checks"].append(run([codex, 'app-server', '--help']))
        if any(c.get('returncode', 1) != 0 for c in result['checks'][:2]):
            result['status'] = 'BLOCKED_CODEX_AUTH_OR_RUNTIME'
    else:
        result['limitations'].append('Codex CLI is not installed; skills/list and Plugin runtime evidence cannot be collected.')
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        Path(args.output).parent.mkdir(parents=True,exist_ok=True)
        Path(args.output).write_text(text,encoding='utf-8')
    print(text,end='')
    return 0 if result['status']=='READY' else 2

if __name__=='__main__':
    raise SystemExit(main())
