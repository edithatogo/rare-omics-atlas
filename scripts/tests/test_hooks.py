"""Native-hook contracts using disposable Git repositories and synthetic scanners."""

from __future__ import annotations

import io
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hooks

SCRIPTS = Path(hooks.__file__).resolve().parent


class NativeHookContracts(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "consumer"
        self.guard = self.base / "privacy"
        self.root.mkdir()
        self.guard.mkdir()
        self.environment = hooks.isolated_environment()
        self.original_versions = hooks.validate_versions
        for root in (self.root, self.guard):
            self.command("git", "init", "--quiet", "--initial-branch=main", str(root))
            self.command("git", "-C", str(root), "config", "user.name", "Hook fixture")
            self.command("git", "-C", str(root), "config", "user.email", "hook@example.invalid")
            self.command("git", "-C", str(root), "config", "commit.gpgsign", "false")
        (self.guard / "scripts").mkdir()
        self.mode = self.base / "scanner-mode"
        self.mode.write_text("0", encoding="utf-8")
        (self.guard / "scripts/privacy_guard.py").write_text(
            "import argparse, os, subprocess\nfrom pathlib import Path\n"
            "p=argparse.ArgumentParser();p.add_argument('--root');p.add_argument('--binary');"
            "p.add_argument('--staged',action='store_true');a=p.parse_args()\n"
            f"order=Path({str(self.root / '.git/order')!r})\n"
            "with order.open('a',encoding='utf-8') as f:f.write('privacy\\n')\n"
            "env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}\n"
            "data=subprocess.check_output(['git','-C',a.root,'show',':candidate.txt'],"
            "env=env,text=True)\n"
            f"raise SystemExit(1 if 'blocked-secret' in data else int(Path({str(self.mode)!r}).read_text()))\n",
            encoding="utf-8",
        )
        self.command("git", "-C", str(self.guard), "add", ".")
        self.command("git", "-C", str(self.guard), "commit", "--quiet", "-m", "scanner fixture")
        revision = self.command("git", "-C", str(self.guard), "rev-parse", "HEAD").stdout.strip()
        binary = self.base / "gitleaks"
        binary.write_text("synthetic binary", encoding="utf-8")
        self.tooling = hooks.Tooling(self.guard, Path(sys.executable).absolute(), binary)
        (self.root / "scripts").mkdir()
        (self.root / ".githooks").mkdir()
        (self.root / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
        (self.root / "candidate.txt").write_text("initial\n", encoding="utf-8")
        (self.root / "scripts/verify.py").write_text(
            "import os, subprocess\nfrom pathlib import Path\n"
            "assert not any(k.startswith('GIT_') for k in os.environ)\n"
            "root=Path(__file__).resolve().parents[1]\n"
            "with (root/'.git/order').open('a',encoding='utf-8') as f:f.write('verify\\n')\n"
            "m=root/'.git/verify-mode';mode=m.read_text() if m.exists() else ''\n"
            "if mode=='index':subprocess.run(['git','rm','--cached','candidate.txt'],check=True,stdout=subprocess.DEVNULL)\n"
            "if mode=='worktree':(root/'candidate.txt').write_text('changed by verifier\\n')\n"
            "if mode=='untracked':(root/'extra.py').write_text('unexpected = True\\n')\n"
            "raise SystemExit(7 if mode=='failure' else 0)\n",
            encoding="utf-8",
        )
        driver = self.root / "scripts/hook_driver.py"
        driver.write_text(
            "import sys\nfrom pathlib import Path\n"
            f"sys.path.insert(0,{str(SCRIPTS)!r})\nimport hooks\n"
            f"hooks.ROOT=Path({str(self.root)!r})\n"
            f"hooks.PRIVACY_REVISION={revision!r}\n"
            "hooks.validate_versions=lambda tooling:None\n"
            "hooks.VERIFY_COMMAND=[sys.executable,'scripts/verify.py']\n"
            "sys.argv=['hooks.py','run']\nraise SystemExit(hooks.main())\n",
            encoding="utf-8",
        )
        self.hook = self.root / ".githooks/pre-commit"
        self.hook.write_text(
            f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(driver))}\n",
            encoding="utf-8",
        )
        self.hook.chmod(0o755)
        self.command("git", "-C", str(self.root), "add", ".")
        self.command("git", "-C", str(self.root), "commit", "--quiet", "-m", "consumer fixture")
        contexts = ExitStack()
        self.addCleanup(contexts.close)
        contexts.enter_context(patch.object(hooks, "ROOT", self.root))
        contexts.enter_context(patch.object(hooks, "PRIVACY_REVISION", revision))
        contexts.enter_context(patch.object(hooks, "validate_versions", return_value=None))
        contexts.enter_context(
            patch.object(hooks, "VERIFY_COMMAND", [sys.executable, "scripts/verify.py"])
        )

    def command(
        self, *args: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args), env=env or self.environment, capture_output=True, text=True, check=True
        )

    def stage(self, text: str = "updated\n") -> None:
        (self.root / "candidate.txt").write_text(text, encoding="utf-8")
        self.command("git", "-C", str(self.root), "add", ".")

    def invoke(self, *args: str) -> int:
        with patch.object(sys, "argv", ["hooks.py", *args]), redirect_stderr(io.StringIO()):
            return hooks.main()

    def test_installer_activates_local_paths_and_is_idempotent(self) -> None:
        self.assertEqual(
            self.invoke(
                "install",
                "--privacy-root",
                str(self.guard),
                "--privacy-python",
                str(self.tooling.python),
                "--gitleaks",
                str(self.tooling.gitleaks),
            ),
            0,
        )
        hooks.install(self.tooling)
        self.assertEqual(hooks.config("core.hooksPath"), ".githooks")
        self.assertEqual(hooks.configured_tooling(), self.tooling)

    def test_installer_preserves_conflicting_configuration_and_existing_hooks(self) -> None:
        self.command("git", "-C", str(self.root), "config", "core.hooksPath", "other-hooks")
        with self.assertRaises(hooks.HookError):
            hooks.install(self.tooling)
        self.assertEqual(hooks.config("core.hooksPath"), "other-hooks")
        self.command("git", "-C", str(self.root), "config", "--unset", "core.hooksPath")
        existing = self.root / ".git/hooks/pre-push"
        existing.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        existing.chmod(0o755)
        with self.assertRaises(hooks.HookError):
            hooks.install(self.tooling)
        self.assertTrue(existing.exists())
        self.assertIsNone(hooks.config("core.hooksPath"))

    def test_installer_requires_an_executable_wrapper_and_complete_arguments(self) -> None:
        self.hook.unlink()
        with self.assertRaises(hooks.HookError):
            hooks.install(self.tooling)
        self.assertEqual(self.invoke("install"), 2)
        self.assertEqual(self.invoke("run"), 2)

    def test_scanner_checkout_pin_cleanliness_isolation_and_tools_are_required(self) -> None:
        for tooling in (
            replace(self.tooling, root=Path("relative")),
            replace(self.tooling, root=self.root),
            replace(self.tooling, python=self.base / "missing"),
            replace(self.tooling, root=self.base),
        ):
            with self.subTest(tooling=tooling), self.assertRaises(hooks.HookError):
                hooks.validate_tooling(tooling)
        with patch.object(hooks, "PRIVACY_REVISION", "0" * 40), self.assertRaises(hooks.HookError):
            hooks.validate_tooling(self.tooling)
        (self.guard / "unexpected.py").write_text("changed = True\n", encoding="utf-8")
        with self.assertRaises(hooks.HookError):
            hooks.validate_tooling(self.tooling)

    def test_hidden_candidate_and_scanner_edits_are_rejected(self) -> None:
        hooks.install(self.tooling)
        candidate = self.root / "candidate.txt"
        scanner = self.guard / "scripts/privacy_guard.py"
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self.command(
                    "git", "-C", str(self.root), "update-index", f"--{flag}", "candidate.txt"
                )
                candidate.write_text("hidden mutation\n", encoding="utf-8")
                self.assertEqual(self.invoke("run"), 2)
                self.command(
                    "git", "-C", str(self.root), "update-index", f"--no-{flag}", "candidate.txt"
                )
                self.stage("initial\n")
                original = scanner.read_text(encoding="utf-8")
                self.command(
                    "git",
                    "-C",
                    str(self.guard),
                    "update-index",
                    f"--{flag}",
                    "scripts/privacy_guard.py",
                )
                scanner.write_text(original + "\n# hidden mutation\n", encoding="utf-8")
                with self.assertRaises(hooks.HookError):
                    hooks.validate_tooling(self.tooling)
                scanner.write_text(original, encoding="utf-8")
                self.command(
                    "git",
                    "-C",
                    str(self.guard),
                    "update-index",
                    f"--no-{flag}",
                    "scripts/privacy_guard.py",
                )

    def test_scanner_checkout_root_and_resolved_tool_targets_are_verified(self) -> None:
        original_resolve = Path.resolve

        def resolve(path: Path, strict: bool = False) -> Path:
            if path == self.tooling.gitleaks:
                return self.root / "candidate.txt"
            return original_resolve(path, strict=strict)

        with patch.object(Path, "resolve", resolve), self.assertRaises(hooks.HookError):
            hooks.validate_tooling(self.tooling)
        nested = self.guard / "nested"
        (nested / "scripts").mkdir(parents=True)
        (nested / "scripts/privacy_guard.py").write_text("untrusted = True\n", encoding="utf-8")
        with self.assertRaises(hooks.HookError):
            hooks.validate_tooling(replace(self.tooling, root=nested))

    def test_exact_runtime_versions_and_git_errors_fail_closed(self) -> None:
        with (
            patch.object(hooks.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)),
            patch.object(hooks.subprocess, "check_output", return_value="8.30.1\n"),
        ):
            self.original_versions(self.tooling)
        with (
            patch.object(hooks.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)),
            patch.object(hooks.subprocess, "check_output", return_value="8.30.10\n"),
            self.assertRaises(hooks.HookError),
        ):
            self.original_versions(self.tooling)
        with (
            patch.object(hooks, "git", side_effect=subprocess.CalledProcessError(128, ["git"])),
            self.assertRaises(subprocess.CalledProcessError),
        ):
            hooks.config("missing")
        with patch.object(hooks, "run", side_effect=FileNotFoundError("missing executable")):
            self.assertEqual(self.invoke("run"), 2)

    def test_incomplete_installed_configuration_cannot_pass(self) -> None:
        self.command("git", "-C", str(self.root), "config", "core.hooksPath", ".githooks")
        self.assertEqual(self.invoke("run"), 2)

    def test_partial_staging_and_untracked_candidates_are_rejected(self) -> None:
        hooks.install(self.tooling)
        self.stage()
        (self.root / "candidate.txt").write_text("unstaged\n", encoding="utf-8")
        self.assertEqual(self.invoke("run"), 2)
        self.stage()
        extra = self.root / "untracked.py"
        extra.write_text("candidate = True\n", encoding="utf-8")
        self.assertEqual(self.invoke("run"), 2)
        self.assertFalse((self.root / ".git/order").exists())

    def test_real_candidate_scan_precedes_strict_gate_and_propagates_failures(self) -> None:
        hooks.install(self.tooling)
        self.stage()
        for scanner_code, verifier_mode, expected in (
            (0, "", 0),
            (1, "", 1),
            (2, "", 2),
            (0, "failure", 7),
        ):
            with self.subTest(scanner=scanner_code, verifier=verifier_mode):
                (self.root / ".git/order").unlink(missing_ok=True)
                self.mode.write_text(str(scanner_code), encoding="utf-8")
                (self.root / ".git/verify-mode").write_text(verifier_mode, encoding="utf-8")
                self.assertEqual(self.invoke("run"), expected)
                order = (self.root / ".git/order").read_text(encoding="utf-8").splitlines()
                self.assertEqual(order, ["privacy", "verify"] if scanner_code == 0 else ["privacy"])

    def test_index_worktree_and_untracked_mutations_cannot_be_certified(self) -> None:
        hooks.install(self.tooling)
        for mode in ("index", "worktree", "untracked"):
            with self.subTest(mode=mode):
                (self.root / "extra.py").unlink(missing_ok=True)
                self.stage()
                (self.root / ".git/verify-mode").write_text(mode, encoding="utf-8")
                self.assertEqual(self.invoke("run"), 2)

    def test_git_commit_invokes_hook_for_all_and_only_candidate_indexes(self) -> None:
        hooks.install(self.tooling)
        before = self.command("git", "-C", str(self.root), "rev-parse", "HEAD").stdout
        (self.root / "candidate.txt").write_text("first unstaged candidate\n", encoding="utf-8")
        self.command("git", "-C", str(self.root), "commit", "--quiet", "-am", "all candidate")
        after = self.command("git", "-C", str(self.root), "rev-parse", "HEAD").stdout
        self.assertNotEqual(before, after)
        (self.root / "candidate.txt").write_text("second unstaged candidate\n", encoding="utf-8")
        self.command(
            "git",
            "-C",
            str(self.root),
            "commit",
            "--quiet",
            "--only",
            "candidate.txt",
            "-m",
            "only candidate",
        )
        self.assertNotEqual(
            after, self.command("git", "-C", str(self.root), "rev-parse", "HEAD").stdout
        )

    def test_alternate_index_blocking_canary_aborts_real_commit_without_head_change(self) -> None:
        hooks.install(self.tooling)
        before = self.command("git", "-C", str(self.root), "rev-parse", "HEAD").stdout
        alternate = self.root / ".git/alternate-index"
        environment = dict(self.environment, GIT_INDEX_FILE=str(alternate))
        self.command("git", "-C", str(self.root), "read-tree", "HEAD", env=environment)
        (self.root / "candidate.txt").write_text("blocked-secret\n", encoding="utf-8")
        self.command("git", "-C", str(self.root), "add", "candidate.txt", env=environment)
        result = subprocess.run(
            ["git", "-C", str(self.root), "commit", "--quiet", "-m", "must reject canary"],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            before, self.command("git", "-C", str(self.root), "rev-parse", "HEAD").stdout
        )
        self.assertEqual(
            self.command("git", "-C", str(self.root), "show", ":candidate.txt").stdout, "initial\n"
        )
        self.assertEqual((self.root / ".git/order").read_text(encoding="utf-8"), "privacy\n")


if __name__ == "__main__":
    unittest.main()
