#!/usr/bin/env python3
"""Deterministically validate a bounded unattended-autonomy envelope."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

ALLOWED_ACTIONS = {"build", "test", "package", "canary_deploy", "deploy", "health_check", "observe", "feature_flag", "rollback"}
SHELL_META = re.compile(r"[;&|<>`\r\n]")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def is_absolute_portable(value: str) -> bool:
    """Recognize explicit POSIX and Windows absolute paths on any host."""

    return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()


def is_root_path(value: str) -> bool:
    """Return whether a portable absolute path addresses a filesystem root."""

    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    return (
        posix.is_absolute()
        and posix == PurePosixPath(posix.anchor)
    ) or (
        windows.is_absolute()
        and windows == PureWindowsPath(windows.anchor)
    )


def parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def validate(data: dict, *, allow_expired: bool = False) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "run_id", "owner", "issued_at", "expires_at", "environment", "artifact_sha256", "trusted_executables", "environment_bindings", "allowed_actions", "allowed_paths", "allowed_commands", "limits", "health_checks", "rollback", "approval", "hard_stops"}
    missing = sorted(required - data.keys())
    if missing:
        return ["missing fields: " + ", ".join(missing)]
    if data.get("schema_version") != "1.0": errors.append("schema_version must be 1.0")
    if data.get("environment") not in {"development", "testing", "staging", "production"}: errors.append("invalid environment")
    if not SHA256.fullmatch(str(data.get("artifact_sha256", ""))): errors.append("artifact_sha256 must be 64 hexadecimal characters")
    trusted = data.get("trusted_executables")
    trusted_paths: set[str] = set()
    if not isinstance(trusted, list) or not trusted:
        errors.append("trusted_executables must be non-empty")
    else:
        for item in trusted:
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                errors.append("each trusted executable requires only path and sha256")
                continue
            executable = str(item.get("path", ""))
            if not is_absolute_portable(executable): errors.append(f"trusted executable path must be absolute: {item.get('path')!r}")
            if not SHA256.fullmatch(str(item.get("sha256", ""))): errors.append(f"trusted executable sha256 is invalid: {item.get('path')!r}")
            trusted_paths.add(str(item.get("path")))
    bindings = data.get("environment_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {"inherit", "required_sha256"}:
        errors.append("environment_bindings requires only inherit and required_sha256")
    else:
        inherited = bindings.get("inherit")
        required_hashes = bindings.get("required_sha256")
        name_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not isinstance(inherited, list) or len(inherited) != len(set(inherited)) or any(not isinstance(name, str) or not name_pattern.fullmatch(name) for name in inherited):
            errors.append("environment_bindings.inherit must contain unique environment variable names")
        if not isinstance(required_hashes, dict) or any(not isinstance(name, str) or not name_pattern.fullmatch(name) or not SHA256.fullmatch(str(value)) for name, value in (required_hashes or {}).items()):
            errors.append("environment_bindings.required_sha256 must map environment names to SHA-256")
        elif isinstance(inherited, list) and not set(required_hashes) <= set(inherited):
            errors.append("every required environment digest must also appear in inherit")
    actions = data.get("allowed_actions")
    if not isinstance(actions, list) or not actions or not set(actions) <= ALLOWED_ACTIONS: errors.append("allowed_actions contains unsupported or empty values")
    try:
        issued, expires = parse_time(data["issued_at"]), parse_time(data["expires_at"])
        if expires <= issued: errors.append("expires_at must be later than issued_at")
        if not allow_expired and expires <= dt.datetime.now(dt.timezone.utc): errors.append("authorization envelope is expired")
    except (TypeError, ValueError) as exc: errors.append(f"invalid authorization timestamps: {exc}")
    paths = data.get("allowed_paths")
    if not isinstance(paths, list) or not paths: errors.append("allowed_paths must be non-empty")
    else:
        for value in paths:
            text = str(value).strip()
            if not text or text in {"/", "\\", "~", "$HOME", "%USERPROFILE%"} or is_root_path(text):
                errors.append(f"allowed path is too broad: {text!r}")
    commands = data.get("allowed_commands")
    if not isinstance(commands, list) or not commands: errors.append("allowed_commands must be non-empty token arrays")
    else:
        for command in commands:
            if not isinstance(command, list) or not command or any(not isinstance(token, str) or not token for token in command):
                errors.append("every allowed command must be a non-empty token array")
            elif any(SHELL_META.search(token) for token in command):
                errors.append(f"shell control operators are forbidden in allowed command tokens: {command!r}")
            elif not is_absolute_portable(command[0]) or command[0] not in trusted_paths:
                errors.append(f"allowed command executable must be an exact trusted absolute path: {command[0]!r}")
    limits = data.get("limits")
    if not isinstance(limits, dict): errors.append("limits must be an object")
    else:
        bounds = {"max_duration_minutes": (1, 1440), "max_attempts_per_step": (1, 5), "max_changed_files": (0, 10000), "max_cost_usd": (0, 100000)}
        for key, (low, high) in bounds.items():
            value = limits.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not low <= value <= high: errors.append(f"invalid limit {key}")
    if not isinstance(data.get("health_checks"), list) or not data["health_checks"]: errors.append("at least one health check is required")
    rollback = data.get("rollback")
    if not isinstance(rollback, dict) or not isinstance(rollback.get("action"), list) or not rollback.get("action"): errors.append("an exact rollback action is required")
    elif rollback.get("action") not in commands:
        errors.append("rollback action must also appear in allowed_commands")
    approval = data.get("approval")
    if not isinstance(approval, dict) or approval.get("type") != "explicit-preauthorization" or not approval.get("evidence_ref"): errors.append("explicit preauthorization evidence is required")
    if not isinstance(data.get("hard_stops"), list) or not data["hard_stops"]: errors.append("hard_stops must be non-empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("envelope")
    parser.add_argument("--allow-expired", action="store_true")
    args = parser.parse_args()
    path = Path(args.envelope)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data, allow_expired=args.allow_expired)
    # Detailed validation errors can contain operator-provided paths or
    # environment variable names. Keep them available to in-process callers,
    # but do not copy them into CI or terminal logs.
    report = {
        "status": "PASS" if not errors else "FAIL",
        "envelope_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "error_count": len(errors),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
