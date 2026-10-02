import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_project.py"


class InspectProjectTests(unittest.TestCase):
    def test_detects_python_pyside_and_hotspot(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo"
            (project / "views").mkdir(parents=True)
            (project / "core").mkdir()
            (project / "tests").mkdir()
            (project / "requirements.txt").write_text("PySide6>=6.7\npytest>=8\n", encoding="utf-8")
            (project / "main.py").write_text("from views.main_window import MainWindow\n", encoding="utf-8")
            methods = "\n".join(f"    def m{i}(self):\n        return {i}" for i in range(25))
            (project / "views" / "main_window.py").write_text(
                "from core.units import x\n\nclass MainWindow:\n" + methods + "\n",
                encoding="utf-8",
            )
            (project / "core" / "units.py").write_text("x = 1\n", encoding="utf-8")
            (project / "tests" / "test_smoke.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(project), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertIn("PySide6", data["frameworks"])
            self.assertTrue(data["tests"]["present"])
            self.assertTrue(any(row["path"] == "views/main_window.py" for row in data["python_hotspots"]))
            self.assertTrue(any(edge == {"from": "views", "to": "core"} for edge in data["python_module_edges"]))
            self.assertIn("analysis_tools", data)
            self.assertGreater(data["scale"]["source_files_measured"], 0)

    def test_write_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo"
            project.mkdir()
            (project / "main.py").write_text("print('ok')\n", encoding="utf-8")
            report = Path(tmp) / "report.json"
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(project), "--write", str(report)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(report.is_file())
            self.assertEqual(json.loads(report.read_text())["project_name"], "demo")


    def test_reports_git_churn_tools_and_generated_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "demo"
            project.mkdir()
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Test"], check=True)

            generated = project / "src" / "generated"
            generated.mkdir(parents=True)
            (project / "main.py").write_text("print('one')\n", encoding="utf-8")
            (generated / "ui.py").write_text("# AUTO-GENERATED - DO NOT EDIT\nvalue = 1\n", encoding="utf-8")
            (project / "opencode.jsonc").write_text('{"mcp": "codebase-memory-mcp codegraph"}\n', encoding="utf-8")
            subprocess.run(["git", "-C", str(project), "add", "."], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-qm", "initial"], check=True)
            (project / "main.py").write_text("print('two')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(project), "add", "main.py"], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-qm", "change main"], check=True)

            bindir = base / "bin"
            bindir.mkdir()
            for name in ("rg", "tgrep", "ast-grep", "codebase-memory-mcp"):
                tool = bindir / name
                tool.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                tool.chmod(0o755)

            env = os.environ.copy()
            env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(project), "--json"],
                text=True, capture_output=True, check=False, env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertTrue(data["analysis_tools"]["binaries"]["ripgrep"]["available"])
            self.assertTrue(data["analysis_tools"]["binaries"]["tgrep"]["available"])
            self.assertTrue(data["analysis_tools"]["binaries"]["ast_grep"]["available"])
            self.assertTrue(data["analysis_tools"]["binaries"]["codebase_memory_mcp"]["available"])
            self.assertIn("codegraph", data["analysis_tools"]["configured_integrations"])
            self.assertIn("codebase-memory-mcp", data["analysis_tools"]["configured_integrations"])
            self.assertTrue(any(row["path"] == "main.py" and row["commits_touching"] >= 2 for row in data["git_churn_hotspots"]))
            self.assertIn("src/generated/ui.py", data["generated_code_candidates"])

    def test_git_target_is_materialized_to_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            source.mkdir()
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Test"], check=True)
            (source / "requirements.txt").write_text("PySide6>=6.7\n", encoding="utf-8")
            (source / "main.py").write_text("print('ok')\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-qm", "init"], check=True)
            bare = base / "remote.git"
            subprocess.run(["git", "clone", "-q", "--bare", str(source), str(bare)], check=True)
            cache = base / "cache"

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(bare), "--cache-dir", str(cache)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["target"]["kind"], "git")
            self.assertTrue(Path(data["target"]["materialized_path"]).is_dir())
            self.assertIn("PySide6", data["frameworks"])


if __name__ == "__main__":
    unittest.main()
