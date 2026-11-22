"""Exercise the strict patch gate with real Git diffs and coverage reports."""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify


class PatchCoverageContracts(unittest.TestCase):
    def test_partial_branches_fail_even_with_a_disjoint_covered_report(self):
        run_check = verify.run_check
        git = verify.git
        for branch_hits, expected_code in ((1, 1), (2, 0)):
            with self.subTest(branch_hits=branch_hits), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                subprocess.run(
                    ["git", "init", "--initial-branch=main", str(root)],
                    check=True,
                    capture_output=True,
                )
                (root / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
                subprocess.run(["git", "-C", str(root), "add", "."], check=True)
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(root),
                        "-c",
                        "user.name=Coverage fixture",
                        "-c",
                        "user.email=coverage@example.invalid",
                        "-c",
                        "commit.gpgsign=false",
                        "commit",
                        "-m",
                        "Baseline",
                    ],
                    check=True,
                    capture_output=True,
                )
                (root / "example.py").write_text("if enabled:\n    value = 1\n", encoding="utf-8")
                (root / "example.rs").write_text("fn ready() -> bool { true }\n", encoding="utf-8")
                python_report = (
                    "<coverage><sources><source>.</source></sources><packages><package>"
                    '<classes><class filename="example.py"><lines>'
                    '<line number="1" hits="1" branch="true" '
                    f'condition-coverage="{branch_hits * 50}% ({branch_hits}/2)"/>'
                    '<line number="2" hits="1"/>'
                    "</lines></class></classes></package></packages></coverage>"
                )
                rust_report = (
                    "<coverage><sources><source>.</source></sources><packages><package>"
                    '<classes><class filename="example.rs"><lines><line number="1" hits="1"/>'
                    "</lines></class></classes></package></packages></coverage>"
                )
                artifacts = {
                    "python-coverage": ("python-coverage.xml", python_report),
                    "rust-coverage-xml": ("rust-coverage.xml", rust_report),
                    "rust-coverage": ("rust-lcov.info", "TN:fixture\n"),
                    "python-advisories": ("python-sbom.json", '{"components":[]}'),
                }

                def fixture_git(*args, root=root):
                    return git(*args, root=root)

                def check(
                    name,
                    command,
                    output,
                    environment,
                    *,
                    expected=None,
                    root=root,
                    artifacts=artifacts,
                ):
                    if name == "patch-coverage":
                        # Run the production command unchanged, including its gate options.
                        return run_check(name, command, output, environment, root=root)
                    if name in artifacts:
                        filename, contents = artifacts[name]
                        (output / filename).write_text(contents, encoding="utf-8")
                    return {"name": name, "command": command, "status": "passed", "exit_code": 0}

                with (
                    patch.object(verify, "ROOT", root),
                    patch.object(verify, "git", side_effect=fixture_git),
                    patch.object(verify, "run_check", side_effect=check),
                    patch.object(sys, "argv", ["verify.py", "--base", "HEAD"]),
                    redirect_stdout(io.StringIO()),
                ):
                    code = verify.main()
                output = root / "artifacts/verification/latest"
                receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
                log = (output / "patch-coverage.log").read_text(encoding="utf-8")
                self.assertEqual(code, expected_code, log)
                self.assertIn("example.py", log)
                self.assertIn("example.rs", log)
                self.assertEqual(
                    receipt["failed_checks"], ["patch-coverage"] if expected_code else []
                )


if __name__ == "__main__":
    unittest.main()
