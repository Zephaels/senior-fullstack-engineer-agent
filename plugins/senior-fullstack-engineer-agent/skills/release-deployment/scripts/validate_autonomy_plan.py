#!/usr/bin/env python3
"""Validate that an autonomy run plan is an exact subset of its envelope."""
from __future__ import annotations

import argparse
import hashlib
import json
import ntpath
from pathlib import Path, PurePosixPath, PureWindowsPath
import posixpath
import re

from validate_autonomy_envelope import SHELL_META, validate as validate_envelope

SAFE_RETRY_ACTIONS = {"build", "test", "package", "health_check", "observe"}
STEP_ACTIONS = SAFE_RETRY_ACTIONS | {"canary_deploy", "deploy", "feature_flag"}
STEP_ID = re.compile(r"^[A-Za-z0-9._-]{3,128}$")


PortablePath = PurePosixPath | PureWindowsPath


def portable_absolute_path(value: str) -> PortablePath | None:
    """Normalize an absolute POSIX or Windows path without host dependence."""

    windows = PureWindowsPath(value)
    if windows.is_absolute():
        return PureWindowsPath(ntpath.normpath(str(windows)))
    posix = PurePosixPath(value)
    if posix.is_absolute():
        return PurePosixPath(posixpath.normpath(str(posix)))
    return None


def within(path: PortablePath, roots: list[PortablePath]) -> bool:
    return any(
        type(path) is type(root) and (path == root or root in path.parents)
        for root in roots
    )


def validate_plan(envelope: dict, plan: dict, *, allow_expired: bool = False) -> list[str]:
    errors = [f"envelope: {item}" for item in validate_envelope(envelope, allow_expired=allow_expired)]
    required = {"schema_version", "run_id", "artifact_path", "workspace", "steps"}
    missing = sorted(required - plan.keys())
    if missing:
        return errors + ["plan missing fields: " + ", ".join(missing)]
    if plan.get("schema_version") != "1.0":
        errors.append("plan schema_version must be 1.0")
    if plan.get("run_id") != envelope.get("run_id"):
        errors.append("plan run_id does not match envelope")

    roots: list[PortablePath] = []
    for raw in envelope.get("allowed_paths", []):
        path = portable_absolute_path(str(raw))
        if path is None:
            errors.append(f"allowed path must be absolute: {raw!r}")
        else:
            roots.append(path)

    artifact = portable_absolute_path(str(plan.get("artifact_path", "")))
    workspace = portable_absolute_path(str(plan.get("workspace", "")))
    for label, path in (("artifact_path", artifact), ("workspace", workspace)):
        if path is None:
            errors.append(f"{label} must be absolute")
        elif roots and not within(path, roots):
            errors.append(f"{label} is outside allowed_paths")

    commands = envelope.get("allowed_commands", [])
    allowed_actions = set(envelope.get("allowed_actions", []))
    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        return errors + ["steps must be a non-empty array"]

    seen: set[str] = set()
    health_ids: set[str] = set()
    deploy_indexes: list[int] = []
    observe_indexes: list[int] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"step {index} must be an object")
            continue
        expected = {"id", "action", "command", "cwd", "timeout_seconds", "transient_exit_codes"}
        extra = sorted(set(step) - expected)
        missing_step = sorted(expected - set(step))
        if extra: errors.append(f"step {index} has unsupported fields: {', '.join(extra)}")
        if missing_step: errors.append(f"step {index} missing fields: {', '.join(missing_step)}")
        step_id = step.get("id")
        if not isinstance(step_id, str) or not STEP_ID.fullmatch(step_id): errors.append(f"step {index} has invalid id")
        elif step_id in seen: errors.append(f"duplicate step id: {step_id}")
        else: seen.add(step_id)
        action = step.get("action")
        if action not in STEP_ACTIONS or action not in allowed_actions: errors.append(f"step {index} action is not authorized: {action!r}")
        command = step.get("command")
        if not isinstance(command, list) or not command or any(not isinstance(token, str) or not token for token in command):
            errors.append(f"step {index} command must be a non-empty token array")
        elif any(SHELL_META.search(token) for token in command):
            errors.append(f"step {index} contains shell control operators")
        elif command not in commands:
            errors.append(f"step {index} command is not an exact allowed_commands entry")
        cwd = portable_absolute_path(str(step.get("cwd", "")))
        if cwd is None: errors.append(f"step {index} cwd must be absolute")
        elif roots and not within(cwd, roots): errors.append(f"step {index} cwd is outside allowed_paths")
        timeout = step.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 3600: errors.append(f"step {index} timeout_seconds is invalid")
        transient = step.get("transient_exit_codes")
        if not isinstance(transient, list) or any(not isinstance(code, int) or isinstance(code, bool) or not 1 <= code <= 255 for code in transient):
            errors.append(f"step {index} transient_exit_codes is invalid")
        elif transient and action not in SAFE_RETRY_ACTIONS:
            errors.append(f"step {index} action {action!r} cannot be retried unattended")
        if action == "health_check": health_ids.add(str(step_id))
        if action in {"canary_deploy", "deploy"}: deploy_indexes.append(index)
        if action == "observe": observe_indexes.append(index)

    expected_health = set(envelope.get("health_checks", []))
    if health_ids != expected_health:
        errors.append("health_check step ids must exactly match envelope health_checks")
    if envelope.get("environment") == "production":
        if not deploy_indexes: errors.append("production plan requires canary_deploy or deploy")
        if not health_ids: errors.append("production plan requires health checks")
        if not observe_indexes: errors.append("production plan requires an observation step")
        if deploy_indexes and any(index < max(deploy_indexes) for index, step in enumerate(steps) if isinstance(step, dict) and step.get("action") in {"health_check", "observe"}):
            errors.append("production health and observation steps must follow the final deployment step")
    if "rollback" not in allowed_actions:
        errors.append("rollback must be authorized for an unattended run")
    if envelope.get("rollback", {}).get("action") not in commands:
        errors.append("rollback action is not an exact allowed_commands entry")
    if envelope.get("limits", {}).get("max_cost_usd") != 0:
        errors.append("supervisor v1 requires max_cost_usd=0 because no external cost meter is configured")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("envelope")
    parser.add_argument("plan")
    parser.add_argument("--allow-expired", action="store_true")
    args = parser.parse_args()
    envelope_path, plan_path = Path(args.envelope), Path(args.plan)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors = validate_plan(envelope, plan, allow_expired=args.allow_expired)
    report = {
        "status": "PASS" if not errors else "FAIL",
        "envelope_sha256": hashlib.sha256(envelope_path.read_bytes()).hexdigest(),
        "plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        # Validation details may contain operator-provided command or path
        # values. The CLI emits only the count; library callers retain access
        # to the detailed list returned by validate_plan().
        "error_count": len(errors),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
