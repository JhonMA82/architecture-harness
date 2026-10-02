#!/usr/bin/env python3
"""Deterministic, dependency-free repository inspector for Architecture Harness.

Accepts a local directory or Git URL. Remote repositories are shallow-cloned into
.architecture-cache/ inside the harness so the architect can inspect relevant files.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Iterable
from urllib.parse import urlparse

HARNESS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = HARNESS_ROOT / ".architecture-cache"

IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv", "env",
    "node_modules", "vendor", "dist", "build", "target", "coverage", ".coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__", ".next", ".nuxt",
    ".turbo", ".cache", ".architecture-cache",
}
IGNORE_FILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "uv.lock", "composer.lock"}
TEXT_EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".php", ".rb", ".go", ".rs",
    ".java", ".kt", ".kts", ".cs", ".cpp", ".cc", ".c", ".h", ".hpp", ".swift",
    ".dart", ".vue", ".svelte", ".html", ".css", ".scss", ".sql", ".sh", ".ps1",
    ".toml", ".yaml", ".yml", ".json", ".jsonc", ".md", ".txt", ".xml",
}
LANG_BY_EXT = {
    ".py": "Python", ".pyi": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".php": "PHP", ".rb": "Ruby",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".cs": "C#", ".cpp": "C++", ".cc": "C++", ".c": "C", ".swift": "Swift",
    ".dart": "Dart", ".vue": "Vue", ".svelte": "Svelte",
}
MANIFEST_NAMES = {
    "pyproject.toml", "requirements.txt", "Pipfile", "poetry.lock", "setup.py", "setup.cfg",
    "package.json", "bun.lock", "bun.lockb", "pnpm-lock.yaml", "yarn.lock", "package-lock.json",
    "composer.json", "composer.lock", "Cargo.toml", "go.mod", "Gemfile", "mix.exs",
    "pubspec.yaml", "pom.xml", "build.gradle", "build.gradle.kts",
}
ENTRYPOINT_NAMES = {
    "main.py", "app.py", "manage.py", "artisan", "server.py", "cli.py", "index.ts", "index.js",
    "main.ts", "main.js", "main.go", "main.rs", "Program.cs", "manage.rb",
}

ANALYSIS_BINARIES = {
    "git": ("git",),
    "ripgrep": ("rg",),
    "tgrep": ("tgrep",),
    "ast_grep": ("ast-grep",),
    "codebase_memory_mcp": ("codebase-memory-mcp",),
    "codegraph": ("codegraph", "codegraph-mcp"),
}
GENERATED_DIR_NAMES = {"generated", "gen", "autogen", "ui_generated", "generated_src"}
TOOL_CONFIG_PATHS = (
    ".mcp.json", "mcp.json", "opencode.json", "opencode.jsonc",
    ".opencode/opencode.json", ".opencode/opencode.jsonc",
    "sgconfig.yml", "sgconfig.yaml", "ast-grep.yml", "ast-grep.yaml",
    "Makefile", "justfile", "Justfile", "Taskfile.yml", "Taskfile.yaml",
)


def is_git_url(value: str) -> bool:
    return bool(re.match(r"^(https?://|ssh://|git@).+", value)) or value.endswith(".git")


def slug_from_url(url: str) -> str:
    if url.startswith("git@"):
        path = url.split(":", 1)[-1]
    else:
        path = urlparse(url).path
    name = Path(path.rstrip("/")).name.removesuffix(".git") or "repo"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-") or "repo"
    return f"{safe}-{digest}"


def materialize_target(target: str, cache_dir: Path) -> tuple[Path, dict]:
    if is_git_url(target):
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / slug_from_url(target)
        if dest.exists():
            shutil.rmtree(dest)
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", target, str(dest)],
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"git clone failed: {proc.stderr.strip() or proc.stdout.strip()}")
        return dest.resolve(), {"kind": "git", "source": target, "materialized_path": str(dest.resolve())}

    path = Path(os.path.expanduser(target)).resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"Target directory does not exist: {path}")
    return path, {"kind": "local", "source": str(path), "materialized_path": str(path)}


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".tox"))
        base = Path(current)
        for filename in sorted(files):
            if filename in IGNORE_FILES:
                # Locks are useful as manifest signals but usually too large to scan.
                yield base / filename
                continue
            yield base / filename


def safe_text(path: Path, max_bytes: int = 512_000) -> str | None:
    try:
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None


def count_lines(path: Path) -> int | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in MANIFEST_NAMES:
        return None
    text = safe_text(path, max_bytes=2_000_000)
    if text is None:
        return None
    return text.count("\n") + (1 if text else 0)


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def top_tree(root: Path, depth: int = 2) -> list[str]:
    out: list[str] = []
    for current, dirs, files in os.walk(root):
        rel = Path(current).relative_to(root)
        level = len(rel.parts)
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS)
        if level >= depth:
            dirs[:] = []
            continue
        if level == 0:
            continue
        out.append(f"{'  ' * (level - 1)}{rel.name}/")
    return out[:300]


def detect_frameworks(root: Path, manifests: dict[str, str]) -> list[str]:
    evidence = "\n".join(manifests.values()).lower()
    frameworks: set[str] = set()

    checks = [
        ("PySide6", ["pyside6"]),
        ("Django", ["django"]),
        ("FastAPI", ["fastapi"]),
        ("Flask", ["flask"]),
        ("Laravel", ["laravel/framework"]),
        ("Rails", ["rails"]),
        ("Next.js", ["\"next\"", "'next'"]),
        ("TanStack Start", ["@tanstack/react-start", "@tanstack/start"]),
        ("NestJS", ["@nestjs/core"]),
        ("Wails", ["github.com/wailsapp/wails"]),
        ("Tauri", ["@tauri-apps", "tauri"]),
        ("Flutter", ["flutter:"]),
        ("Qt", ["pyqt6", "pyqt5"]),
    ]
    for name, needles in checks:
        if any(n.lower() in evidence for n in needles):
            frameworks.add(name)

    if (root / "artisan").exists() and (root / "routes").exists():
        frameworks.add("Laravel")
    if (root / "manage.py").exists() and any((root / p).exists() for p in ["settings.py", "config/settings.py"]):
        frameworks.add("Django")
    if (root / "wails.json").exists():
        frameworks.add("Wails")
    if (root / "src-tauri").is_dir():
        frameworks.add("Tauri")
    return sorted(frameworks)


def detect_package_manager(root: Path) -> list[str]:
    found: list[str] = []
    indicators = [
        ("uv", "uv.lock"), ("Bun", "bun.lock"), ("Bun", "bun.lockb"),
        ("pnpm", "pnpm-lock.yaml"), ("Yarn", "yarn.lock"), ("npm", "package-lock.json"),
        ("Composer", "composer.lock"), ("Cargo", "Cargo.lock"), ("Go modules", "go.mod"),
        ("Bundler", "Gemfile.lock"),
    ]
    for name, path in indicators:
        if (root / path).exists() and name not in found:
            found.append(name)
    if not found and (root / "requirements.txt").exists():
        found.append("pip/requirements")
    return found


def _ignored_repo_path(value: str) -> bool:
    parts = Path(value).parts
    return any(part in IGNORE_DIRS for part in parts)


def detect_analysis_tools(root: Path) -> dict:
    binaries: dict[str, dict] = {}
    for label, candidates in ANALYSIS_BINARIES.items():
        found = None
        for command in candidates:
            location = shutil.which(command)
            if location:
                found = command
                break
        binaries[label] = {"available": found is not None, "command": found}

    project_native: list[str] = []
    configured_integrations: set[str] = set()
    config_files: list[str] = []
    for rel in TOOL_CONFIG_PATHS:
        path = root / rel
        if not path.is_file():
            continue
        config_files.append(rel)
        lower_name = path.name.lower()
        if lower_name in {"makefile", "justfile", "taskfile.yml", "taskfile.yaml"}:
            project_native.append(rel)
        if "sgconfig" in lower_name or "ast-grep" in lower_name:
            project_native.append(rel)
        text = safe_text(path, max_bytes=250_000) or ""
        lower = text.lower()
        if "codebase-memory-mcp" in lower or "codebase_memory" in lower:
            configured_integrations.add("codebase-memory-mcp")
        if "codegraph" in lower or "code-graph" in lower:
            configured_integrations.add("codegraph")

    # Existing architecture/static-analysis rules are valuable project-native evidence.
    for rel in (".engineering/rules/ast-grep", ".ast-grep", "ast-grep"): 
        path = root / rel
        if path.exists():
            project_native.append(rel)

    return {
        "binaries": binaries,
        "config_files": sorted(set(config_files)),
        "project_native": sorted(set(project_native)),
        "configured_integrations": sorted(configured_integrations),
        "policy": "cheapest_sufficient_evidence; no indexing by default",
    }


def git_facts_and_churn(root: Path, max_commits: int = 200) -> tuple[dict, list[dict]]:
    if not (root / ".git").exists():
        return {}, []
    try:
        branch = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            text=True, capture_output=True, timeout=5,
        )
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True, capture_output=True, timeout=5,
        )
        shallow = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
            text=True, capture_output=True, timeout=5,
        )
        log = subprocess.run(
            ["git", "-C", str(root), "log", f"-n{max_commits}", "--format=__COMMIT__%H", "--name-only", "--"],
            text=True, capture_output=True, timeout=12,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}, []

    churn: Counter[str] = Counter()
    commits_sampled = 0
    if log.returncode == 0:
        current_seen: set[str] = set()
        for raw in log.stdout.splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith("__COMMIT__"):
                for filename in current_seen:
                    churn[filename] += 1
                current_seen = set()
                commits_sampled += 1
                continue
            if not _ignored_repo_path(line):
                current_seen.add(line)
        for filename in current_seen:
            churn[filename] += 1

    facts = {
        "branch": branch.stdout.strip() or None,
        "head": head.stdout.strip() or None,
        "shallow": shallow.stdout.strip().lower() == "true" if shallow.returncode == 0 else None,
        "history_commits_sampled": commits_sampled,
    }
    hotspots = [
        {"path": path, "commits_touching": touches}
        for path, touches in churn.most_common(30)
    ]
    return facts, hotspots


def detect_generated_files(root: Path, files: list[Path]) -> list[str]:
    generated: set[str] = set()
    marker = re.compile(r"(generated|auto[- ]?generated).*(do not edit|do not modify)|(do not edit|do not modify).*generated", re.I | re.S)
    for path in files:
        rel = relative(root, path)
        if any(part.lower() in GENERATED_DIR_NAMES for part in Path(rel).parts[:-1]):
            generated.add(rel)
            continue
        if path.suffix.lower() not in LANG_BY_EXT:
            continue
        try:
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                prefix = "".join(fh.readline() for _ in range(12))
        except OSError:
            continue
        if marker.search(prefix):
            generated.add(rel)
    return sorted(generated)[:100]


def python_stats(root: Path, files: list[Path], module_root: Path) -> tuple[list[dict], list[dict], list[list[str]]]:
    stats: list[dict] = []
    edges: set[tuple[str, str]] = set()
    candidate_owners = {p.name for p in module_root.iterdir() if p.is_dir() and not p.name.startswith(".")}

    for path in files:
        if path.suffix != ".py":
            continue
        text = safe_text(path, max_bytes=1_500_000)
        if text is None:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        classes = 0
        functions = 0
        methods = 0
        max_method_lines = 0
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes += 1
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods += 1
                        end = getattr(child, "end_lineno", child.lineno)
                        max_method_lines = max(max_method_lines, end - child.lineno + 1)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions += 1
            elif isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])

        try:
            rel_mod = path.relative_to(module_root)
            source_owner = rel_mod.parts[0] if len(rel_mod.parts) > 1 else "<root>"
        except ValueError:
            source_owner = relative(root, path).split("/", 1)[0]
        for imp in imports:
            if imp in candidate_owners and imp != source_owner:
                edges.add((source_owner, imp))

        line_count = text.count("\n") + (1 if text else 0)
        if line_count >= 300 or methods >= 20 or classes >= 8 or max_method_lines >= 80:
            stats.append({
                "path": relative(root, path),
                "lines": line_count,
                "classes": classes,
                "functions": functions,
                "methods": methods,
                "largest_method_lines": max_method_lines,
            })

    stats.sort(key=lambda x: (x["lines"], x["methods"]), reverse=True)
    edge_list = [{"from": a, "to": b} for a, b in sorted(edges)]
    cycles = [[a, b] for a, b in sorted(edges) if (b, a) in edges and a < b]
    return stats[:40], edge_list[:200], cycles[:50]


def detect_module_root(root: Path) -> Path:
    src = root / "src"
    if src.is_dir():
        packages = [p for p in src.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name != "__pycache__"]
        if len(packages) == 1:
            return packages[0]
    return root


def inspect(root: Path, source_info: dict) -> dict:
    files = list(iter_files(root))
    manifests: dict[str, str] = {}
    languages = Counter()
    file_rows: list[dict] = []
    tests: list[str] = []
    ci: list[str] = []
    entrypoints: list[str] = []

    for path in files:
        rel = relative(root, path)
        ext = path.suffix.lower()
        if ext in LANG_BY_EXT:
            languages[LANG_BY_EXT[ext]] += 1

        if path.name in MANIFEST_NAMES:
            text = safe_text(path, max_bytes=200_000)
            manifests[rel] = text or ""

        lower_parts = [p.lower() for p in Path(rel).parts]
        name_lower = path.name.lower()
        if (
            "tests" in lower_parts or "test" in lower_parts
            or name_lower.startswith("test_") or name_lower.endswith("_test.py")
            or re.search(r"\.(test|spec)\.[^.]+$", name_lower)
        ):
            tests.append(rel)

        if rel.startswith(".github/workflows/") or rel in {".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml"}:
            ci.append(rel)

        if path.name in ENTRYPOINT_NAMES or rel in {"cmd/main.go", "src/main.rs", "src/main.ts", "src/main.tsx"}:
            entrypoints.append(rel)

        lines = count_lines(path)
        if lines is not None:
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            file_rows.append({"path": rel, "lines": lines, "bytes": size})

    file_rows.sort(key=lambda x: (x["lines"], x["bytes"]), reverse=True)
    module_root = detect_module_root(root)
    py_hotspots, py_edges, py_cycles = python_stats(root, files, module_root)

    top_level_dirs = sorted(p.name for p in root.iterdir() if p.is_dir() and p.name not in IGNORE_DIRS)
    top_level_files = sorted(p.name for p in root.iterdir() if p.is_file())

    git, git_churn = git_facts_and_churn(root)
    analysis_tools = detect_analysis_tools(root)
    generated_files = detect_generated_files(root, files)
    source_rows = [row for row in file_rows if Path(row["path"]).suffix.lower() in LANG_BY_EXT]
    source_lines = sum(row["lines"] for row in source_rows)

    return {
        "schema_version": 1,
        "target": source_info,
        "project_name": root.name,
        "root": str(root),
        "module_root": str(module_root),
        "git": git,
        "git_churn_hotspots": git_churn,
        "analysis_tools": analysis_tools,
        "scale": {
            "files_scanned": len(files),
            "source_files_measured": len(source_rows),
            "source_lines_measured": source_lines,
        },
        "generated_code_candidates": generated_files,
        "languages": [{"name": k, "files": v} for k, v in languages.most_common()],
        "frameworks": detect_frameworks(root, manifests),
        "package_managers": detect_package_manager(root),
        "manifests": sorted(manifests.keys()),
        "entrypoints": sorted(set(entrypoints))[:50],
        "tests": {"present": bool(tests), "count": len(tests), "examples": sorted(tests)[:30]},
        "ci": sorted(ci),
        "top_level": {"directories": top_level_dirs, "files": top_level_files},
        "tree_depth_2": top_tree(root, depth=3),
        "largest_text_files": file_rows[:30],
        "python_hotspots": py_hotspots,
        "python_module_edges": py_edges,
        "python_mutual_dependencies": py_cycles,
        "counts": {
            "files_scanned": len(files),
            "text_files_measured": len(file_rows),
            "source_files_measured": len(source_rows),
            "source_lines_measured": source_lines,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a project deterministically for Architecture Harness")
    parser.add_argument("target", help="Local directory or Git URL")
    parser.add_argument("--json", action="store_true", help="Print JSON (default output is also JSON-compatible summary)")
    parser.add_argument("--write", help="Write the JSON report to this path")
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE), help="Cache directory for remote Git materialization")
    args = parser.parse_args()

    try:
        root, source_info = materialize_target(args.target, Path(args.cache_dir).expanduser().resolve())
        report = inspect(root, source_info)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2

    encoded = json.dumps(report, indent=2, ensure_ascii=False)
    if args.write:
        out = Path(args.write)
        if not out.is_absolute():
            out = Path.cwd() / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
