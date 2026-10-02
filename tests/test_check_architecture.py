import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_architecture.py"


def handoff(checks):
    return {
        "schema_version": 1,
        "architecture_revision": 1,
        "project": {"name": "demo", "archetype": "desktop"},
        "architecture": {"pattern": "modular-monolith", "organization": "feature-oriented", "intervention": "ORGANIZE"},
        "boundaries": {"rules": [{"rule": "core must not import ui", "enforcement": "mechanical"}]},
        "verification": {"commands": ["python -m unittest"], "architecture_checks": checks},
        "completion": {"criteria": ["all checks pass"]},
        "work_ledger": {"policy": "decompose_do_not_reinterpret", "checkpoint_after_each_work_unit": True},
    }


class CheckArchitectureTests(unittest.TestCase):
    def test_forbidden_python_import_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "core").mkdir()
            (project / "ui").mkdir()
            (project / "core" / "bad.py").write_text("from ui.window import MainWindow\n", encoding="utf-8")
            arch = project / ".architecture"
            arch.mkdir()
            (arch / "handoff.json").write_text(json.dumps(handoff([
                {
                    "type": "forbid_python_import",
                    "source_glob": "core/**/*.py",
                    "forbidden_prefixes": ["ui"],
                    "phase": "current"
                }
            ])), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(SCRIPT), str(project)], text=True, capture_output=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("imports forbidden module ui.window", proc.stdout)

    def test_completion_checks_are_skipped_until_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            arch = project / ".architecture"
            arch.mkdir()
            (arch / "handoff.json").write_text(json.dumps(handoff([
                {"type": "require_path", "path": "features/new_feature", "phase": "completion"}
            ])), encoding="utf-8")
            initial = subprocess.run([sys.executable, str(SCRIPT), str(project)], text=True, capture_output=True)
            self.assertEqual(initial.returncode, 0, initial.stdout)
            final = subprocess.run([sys.executable, str(SCRIPT), str(project), "--completion"], text=True, capture_output=True)
            self.assertEqual(final.returncode, 1)
            self.assertIn("required path missing", final.stdout)


if __name__ == "__main__":
    unittest.main()
