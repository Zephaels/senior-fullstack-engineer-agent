#!/usr/bin/env python3
"""Execute a preauthorized unattended run with default-deny supervision."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from validate_autonomy_envelope import parse_time
from validate_autonomy_plan import SAFE_RETRY_ACTIONS, validate_plan


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command_digest(command: list[str]) -> str:
    canonical = json.dumps(command, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def output_evidence(value: bytes) -> dict:
    return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def workspace_snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in {".git", ".sfse-autonomy", "__pycache__"}:
            continue
        result[relative.as_posix()] = sha256_file(path)
    return result


def changed_count(before: dict, after: dict) -> int:
    return sum(1 for key in set(before) | set(after) if before.get(key) != after.get(key))


def execute(command: list[str], cwd: Path, timeout: int, environment: dict[str, str]) -> dict:
    started = time.monotonic()
    try:
        completed = subprocess.run(command, cwd=cwd, env=environment, shell=False, capture_output=True, timeout=timeout, check=False)
        return {
            "status": "passed" if completed.returncode == 0 else "failed",
            "exit_code": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": output_evidence(completed.stdout),
            "stderr": output_evidence(completed.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or "").encode()
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or "").encode()
        return {
            "status": "timeout",
            "exit_code": None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": output_evidence(stdout),
            "stderr": output_evidence(stderr),
        }
    except OSError as exc:
        encoded = str(exc).encode("utf-8", errors="replace")
        return {
            "status": "launch_error",
            "exit_code": None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": output_evidence(b""),
            "stderr": output_evidence(encoded),
        }


def acquire_lock(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)


def bound_environment(bindings: dict) -> tuple[dict[str, str], list[str]]:
    inherited = bindings.get("inherit", [])
    required = bindings.get("required_sha256", {})
    environment = {name: os.environ[name] for name in inherited if name in os.environ}
    errors: list[str] = []
    for name, expected in required.items():
        if name not in os.environ:
            errors.append(f"required environment variable is unavailable: {name}")
            continue
        observed = hashlib.sha256(os.environ[name].encode("utf-8")).hexdigest()
        if observed.lower() != str(expected).lower():
            errors.append(f"required environment variable digest mismatch: {name}")
    return environment, errors


def supervise(envelope: dict, plan: dict, envelope_hash: str, plan_hash: str, *, execute_run: bool) -> tuple[int, dict]:
    errors = validate_plan(envelope, plan, allow_expired=False)
    artifact = Path(plan["artifact_path"]).resolve()
    workspace = Path(plan["workspace"]).resolve()
    if not artifact.is_file(): errors.append("artifact_path does not exist or is not a file")
    if not workspace.is_dir(): errors.append("workspace does not exist or is not a directory")
    if artifact.is_file() and sha256_file(artifact).lower() != str(envelope["artifact_sha256"]).lower(): errors.append("artifact digest mismatch")
    trusted = {str(item["path"]): str(item["sha256"]).lower() for item in envelope.get("trusted_executables", []) if isinstance(item, dict) and "path" in item and "sha256" in item}
    for executable, expected in trusted.items():
        path = Path(executable)
        if not path.is_file(): errors.append(f"trusted executable is unavailable: {executable}")
        elif sha256_file(path).lower() != expected: errors.append(f"trusted executable digest mismatch: {executable}")
    environment, environment_errors = bound_environment(envelope.get("environment_bindings", {}))
    errors.extend(environment_errors)
    if errors:
        return 2, {"status": "blocked", "phase": "validation", "errors": errors}
    if not execute_run:
        return 0, {"status": "validated", "run_id": envelope["run_id"], "execute": False, "errors": []}

    journal_dir = workspace / ".sfse-autonomy"
    journal_path = journal_dir / f"{envelope['run_id']}.json"
    lock_path = journal_dir / f"{envelope['run_id']}.lock"
    try:
        lock_fd = acquire_lock(lock_path)
    except FileExistsError:
        return 3, {"status": "blocked", "phase": "lease", "errors": ["exclusive run lock already exists"]}
    os.write(lock_fd, f"pid={os.getpid()}\n".encode())
    os.close(lock_fd)

    started_wall = utc_now()
    deadline = started_wall + dt.timedelta(minutes=envelope["limits"]["max_duration_minutes"])
    expires = parse_time(envelope["expires_at"])
    try:
        before = workspace_snapshot(workspace)
    except OSError as exc:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        return 11, {"status": "blocked", "phase": "workspace-snapshot", "errors": [str(exc)]}
    journal = {
        "schema_version": "1.0",
        "run_id": envelope["run_id"],
        "status": "running",
        "started_at": iso_now(),
        "envelope_sha256": envelope_hash,
        "plan_sha256": plan_hash,
        "artifact_sha256": envelope["artifact_sha256"].lower(),
        "approval_evidence_ref": envelope["approval"]["evidence_ref"],
        "steps": [],
        "rollback": None,
    }
    atomic_json(journal_path, journal)
    deployment_started_at: dt.datetime | None = None
    passed_health: set[str] = set()

    def rollback(reason: str) -> str:
        nonlocal journal
        if deployment_started_at is None:
            return "not_required"
        rollback_deadline = deployment_started_at + dt.timedelta(minutes=envelope["rollback"]["deadline_minutes"])
        if utc_now() > min(rollback_deadline, expires):
            journal["rollback"] = {"status": "needs_operator", "reason": "rollback deadline expired"}
            return "needs_operator"
        rollback_command = envelope["rollback"]["action"]
        executable = Path(rollback_command[0])
        if not executable.is_file() or sha256_file(executable).lower() != trusted.get(rollback_command[0]):
            journal["rollback"] = {"status": "needs_operator", "reason": "rollback executable identity changed"}
            return "needs_operator"
        remaining = max(1, int((min(rollback_deadline, expires) - utc_now()).total_seconds()))
        current_environment, environment_errors = bound_environment(envelope["environment_bindings"])
        if environment_errors:
            journal["rollback"] = {"status": "needs_operator", "reason": "; ".join(environment_errors)}
            return "needs_operator"
        result = execute(rollback_command, workspace, min(3600, envelope["rollback"]["deadline_minutes"] * 60, remaining), current_environment)
        journal["rollback"] = {
            "status": "passed" if result["status"] == "passed" else "needs_operator",
            "reason": reason,
            "command_sha256": command_digest(envelope["rollback"]["action"]),
            "result": result,
            "completed_at": iso_now(),
        }
        atomic_json(journal_path, journal)
        return "rolled_back" if result["status"] == "passed" else "needs_operator"

    try:
        for step in plan["steps"]:
            if utc_now() >= min(deadline, expires):
                outcome = rollback("authorization or run deadline reached")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 4, journal
            if sha256_file(artifact).lower() != str(envelope["artifact_sha256"]).lower():
                outcome = rollback("artifact identity changed during run")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 8, journal
            current_environment, environment_errors = bound_environment(envelope["environment_bindings"])
            if environment_errors or current_environment != environment:
                outcome = rollback("bound execution environment changed during run")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 10, journal
            executable = Path(step["command"][0])
            if not executable.is_file() or sha256_file(executable).lower() != trusted.get(step["command"][0]):
                outcome = rollback("command executable identity changed during run")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 9, journal
            if step["action"] in {"canary_deploy", "deploy", "feature_flag"} and deployment_started_at is None:
                deployment_started_at = utc_now()
            attempts: list[dict] = []
            max_attempts = envelope["limits"]["max_attempts_per_step"] if step["action"] in SAFE_RETRY_ACTIONS else 1
            for attempt in range(1, max_attempts + 1):
                remaining_seconds = int((min(deadline, expires) - utc_now()).total_seconds())
                if remaining_seconds <= 0:
                    result = {"status": "authorization_expired", "exit_code": None, "duration_seconds": 0, "stdout": output_evidence(b""), "stderr": output_evidence(b"")}
                    attempts.append({**result, "attempt": attempt})
                    break
                result = execute(step["command"], Path(step["cwd"]), min(step["timeout_seconds"], remaining_seconds), environment)
                result["attempt"] = attempt
                attempts.append(result)
                if result["status"] == "passed": break
                if result["status"] != "failed" or result["exit_code"] not in step["transient_exit_codes"]: break
                if attempt < max_attempts: time.sleep(min(2 ** (attempt - 1), 8))
            try:
                after = workspace_snapshot(workspace)
            except OSError as exc:
                outcome = rollback(f"workspace snapshot failed: {exc}")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 11, journal
            modifications = changed_count(before, after)
            record = {
                "id": step["id"],
                "action": step["action"],
                "command_sha256": command_digest(step["command"]),
                "cwd_sha256": hashlib.sha256(str(Path(step["cwd"]).resolve()).encode()).hexdigest(),
                "attempts": attempts,
                "changed_files": modifications,
                "completed_at": iso_now(),
            }
            journal["steps"].append(record)
            atomic_json(journal_path, journal)
            if modifications > envelope["limits"]["max_changed_files"]:
                outcome = rollback("changed-file limit exceeded")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 5, journal
            if attempts[-1]["status"] != "passed":
                outcome = rollback(f"step failed: {step['id']}")
                journal["status"] = outcome if outcome != "not_required" else "blocked"
                journal["completed_at"] = iso_now()
                atomic_json(journal_path, journal)
                return 6, journal
            if step["action"] == "health_check": passed_health.add(step["id"])
            before = after

        if passed_health != set(envelope["health_checks"]):
            outcome = rollback("required health gate missing")
            journal["status"] = outcome if outcome != "not_required" else "blocked"
            journal["completed_at"] = iso_now()
            atomic_json(journal_path, journal)
            return 7, journal
        journal["status"] = "succeeded"
        journal["completed_at"] = iso_now()
        atomic_json(journal_path, journal)
        return 0, journal
    finally:
        try: lock_path.unlink()
        except FileNotFoundError: pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("envelope")
    parser.add_argument("plan")
    parser.add_argument("--execute", action="store_true", help="execute exact authorized commands; otherwise validate only")
    args = parser.parse_args()
    envelope_path, plan_path = Path(args.envelope), Path(args.plan)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    code, report = supervise(
        envelope,
        plan,
        hashlib.sha256(envelope_path.read_bytes()).hexdigest(),
        hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        execute_run=args.execute,
    )
    # The durable journal contains the detailed local evidence. Terminal and
    # CI logs receive a bounded summary so operator-provided paths, approval
    # references, and validation messages are not logged in clear text.
    summary = {
        "status": report.get("status"),
        "phase": report.get("phase"),
        "execute": bool(args.execute),
        "completed_steps": len(report.get("steps", [])),
        "error_count": len(report.get("errors", [])),
        "rollback_status": (report.get("rollback") or {}).get("status"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
