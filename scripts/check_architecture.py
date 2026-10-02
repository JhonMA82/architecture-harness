#!/usr/bin/env python3
"""Validate Architecture Harness handoff and supported mechanical invariants."""
from __future__ import annotations

import argparse
import ast
import glob
import json
from pathlib import Path
import sys


def load_handoff(arg: str) -> tuple[Path, Path, dict]:
    p = Path(arg).expanduser().resolve()
    if p.is_dir():
        root = p
        handoff_path = root / ".architecture" / "handoff.json"
    else:
        handoff_path = p
        if handoff_path.name != "handoff.json":
            raise ValueError("File target must be a handoff.json")
        root = handoff_path.parent.parent
    if not handoff_path.is_file():
        raise FileNotFoundError(f"Missing handoff: {handoff_path}")
    return root, handoff_path, json.loads(handoff_path.read_text(encoding="utf-8"))


def validate_shape(data: dict) -> list[str]:
    errors: list[str] = []
    required = ["schema_version", "architecture_revision", "project", "architecture", "boundaries", "verification", "completion", "work_ledger"]
    for key in required:
        if key not in data:
            errors.append(f"missing required key: {key}")
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("architecture_revision"), int) or data.get("architecture_revision", 0) < 1:
        errors.append("architecture_revision must be an integer >= 1")
    if data.get("work_ledger", {}).get("policy") != "decompose_do_not_reinterpret":
        errors.append("work_ledger.policy must be decompose_do_not_reinterpret")
    if not data.get("architecture", {}).get("pattern"):
        errors.append("architecture.pattern is required")
    if not isinstance(data.get("boundaries", {}).get("rules"), list):
        errors.append("boundaries.rules must be an array")
    if not isinstance(data.get("verification", {}).get("commands"), list):
        errors.append("verification.commands must be an array")
    if not data.get("completion", {}).get("criteria"):
        errors.append("completion.criteria must contain at least one item")
    return errors


def import_names(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def run_check(root: Path, check: dict) -> list[str]:
    kind = check.get("type")
    if kind == "require_path":
        path = root / check["path"]
        return [] if path.exists() else [f"required path missing: {check['path']}"]

    if kind == "forbid_path":
        path = root / check["path"]
        return [] if not path.exists() else [f"forbidden path exists: {check['path']}"]

    if kind == "forbid_python_import":
        source_glob = check["source_glob"]
        forbidden = tuple(check["forbidden_prefixes"])
        failures: list[str] = []
        pattern = str(root / source_glob)
        for filename in sorted(glob.glob(pattern, recursive=True)):
            p = Path(filename)
            if not p.is_file() or p.suffix != ".py":
                continue
            for name in sorted(import_names(p)):
                if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden):
                    failures.append(f"{p.relative_to(root).as_posix()} imports forbidden module {name}")
        return failures

    return [f"unsupported architecture check type: {kind}"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Architecture Harness handoff and invariants")
    parser.add_argument("target", help="Project/output root or .architecture/handoff.json")
    parser.add_argument("--completion", action="store_true", help="Also run checks marked for completion")
    args = parser.parse_args()

    try:
        root, handoff_path, data = load_handoff(args.target)
    except Exception as exc:
        print(f"FAIL handoff: {exc}")
        return 2

    failures = validate_shape(data)
    checks = data.get("verification", {}).get("architecture_checks", []) or []
    ran = 0
    skipped = 0
    for check in checks:
        phase = check.get("phase", "completion")
        if phase == "completion" and not args.completion:
            skipped += 1
            continue
        ran += 1
        failures.extend(run_check(root, check))

    if failures:
        print(f"FAIL {handoff_path}")
        for failure in failures:
            print(f"- {failure}")
        print(f"checks_ran={ran} checks_skipped={skipped}")
        return 1

    print(f"PASS {handoff_path}")
    print(f"checks_ran={ran} checks_skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
