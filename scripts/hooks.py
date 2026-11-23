#!/usr/bin/env python3
"""Install and run the native staged-privacy and strict-verification Git hook."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVACY_REVISION = "2efdbd988064f6857795b9fa9ed4e1d08d18791d"
HOOKS_PATH = ".githooks"
CONFIG_KEYS = ("strictHooks.privacyRoot", "strictHooks.privacyPython", "strictHooks.gitleaks")
VERIFY_COMMAND = [sys.executable, "scripts/verify.py", "--deep"]


class HookError(Exception):
    """A fixed diagnostic that never includes staged content."""


@dataclass(frozen=True)
class Tooling:
    root: Path
    python: Path
    gitleaks: Path


def isolated_environment() -> dict[str, str]:
    """Keep tool locations, but prevent hook Git state escaping into another repo."""
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def git(*args: str, root: Path | None = None, isolated: bool = False) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root or ROOT), *args],
        env=isolated_environment() if isolated else None,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
    ).strip()


def config(key: str, *, local: bool = True) -> str | None:
    try:
        return git("config", *(["--local"] if local else []), "--get", key)
    except subprocess.CalledProcessError as error:
        if error.returncode != 1:
            raise
        return None


def validate_versions(tooling: Tooling) -> None:
    subprocess.run(
        [
            str(tooling.python),
            "-I",
            "-c",
            "import sys; assert sys.version_info[:3] == (3, 15, 2); "
            "assert sys.prefix != sys.base_prefix",
        ],
        env=isolated_environment(),
        check=True,
        capture_output=True,
        timeout=30,
    )
    version = subprocess.check_output(
        [str(tooling.gitleaks), "version"],
        env=isolated_environment(),
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    ).strip()
    if version != "8.30.1":
        raise HookError("The isolated Gitleaks version must be 8.30.1.")


def validate_tooling(tooling: Tooling) -> None:
    paths = (tooling.root, tooling.python, tooling.gitleaks)
    if any(not path.is_absolute() for path in paths):
        raise HookError("Scanner paths must be absolute.")
    if any(
        (path.parent.resolve() / path.name).is_relative_to(ROOT.resolve())
        or path.resolve().is_relative_to(ROOT.resolve())
        for path in paths
    ):
        raise HookError("The privacy checkout and environment must be outside this repository.")
    if not tooling.python.is_file() or not tooling.gitleaks.is_file():
        raise HookError("The configured isolated scanner tools are missing.")
    if not (tooling.root / "scripts/privacy_guard.py").is_file():
        raise HookError("The configured privacy checkout is incomplete.")
    if (
        Path(git("rev-parse", "--show-toplevel", root=tooling.root, isolated=True)).resolve()
        != tooling.root.resolve()
    ):
        raise HookError("The privacy path must be the root of its verified checkout.")
    if git("rev-parse", "HEAD", root=tooling.root, isolated=True) != PRIVACY_REVISION:
        raise HookError("The privacy checkout must match the workflow's pinned commit.")
    require_normal_index(root=tooling.root, isolated=True)
    if git("status", "--porcelain", root=tooling.root, isolated=True):
        raise HookError("The pinned privacy checkout must have no source changes.")
    validate_versions(tooling)


def configured_tooling() -> Tooling:
    def required(key: str) -> Path:
        value = config(key)
        if not value:
            raise HookError("Install the local hook with all three isolated scanner paths first.")
        return Path(value)

    return Tooling(required(CONFIG_KEYS[0]), required(CONFIG_KEYS[1]), required(CONFIG_KEYS[2]))


def install(tooling: Tooling) -> None:
    validate_tooling(tooling)
    current = config("core.hooksPath", local=False)
    if current is not None and current != HOOKS_PATH:
        raise HookError(
            "An existing core.hooksPath needs explicit integration; it was not replaced."
        )
    legacy = Path(git("rev-parse", "--git-path", "hooks"))
    if not legacy.is_absolute():
        legacy = ROOT / legacy
    if (
        current is None
        and legacy.is_dir()
        and any(
            path.is_file() and os.access(path, os.X_OK) and not path.name.endswith(".sample")
            for path in legacy.iterdir()
        )
    ):
        raise HookError("Existing executable Git hooks need integration; they were not replaced.")
    hook = ROOT / HOOKS_PATH / "pre-commit"
    if not hook.is_file() or not os.access(hook, os.X_OK):
        raise HookError("The tracked pre-commit hook must exist and be executable.")
    for key, path in zip(
        CONFIG_KEYS, (tooling.root, tooling.python, tooling.gitleaks), strict=True
    ):
        git("config", "--local", key, str(path))
    git("config", "--local", "core.hooksPath", HOOKS_PATH)
    print("Installed the native pre-commit hook in this clone.")


def require_normal_index(*, root: Path | None = None, isolated: bool = False) -> None:
    entries = git("ls-files", "-v", "-z", root=root, isolated=isolated).split("\0")
    if any(entry and not entry.startswith("H ") for entry in entries):
        raise HookError("Remove assume-unchanged, skip-worktree or unresolved index entries first.")


def require_staged_worktree() -> None:
    require_normal_index()
    try:
        git("diff", "--quiet", "--")
    except subprocess.CalledProcessError as error:
        if error.returncode != 1:
            raise
        raise HookError(
            "Stage all tracked changes before committing; partial staging is rejected."
        ) from error
    if git("ls-files", "--others", "--exclude-standard", "-z"):
        raise HookError("Stage or remove untracked candidate files before committing.")


def run() -> int:
    if config("core.hooksPath", local=False) != HOOKS_PATH:
        raise HookError("The native hook is not installed in this clone.")
    tooling = configured_tooling()
    validate_tooling(tooling)
    require_staged_worktree()
    # These operations intentionally inherit Git's actual candidate index, including -a/--only.
    tree = git("write-tree")
    head = git("rev-parse", "HEAD")
    environment = isolated_environment()
    with tempfile.TemporaryDirectory(prefix="staged-privacy-") as directory:
        snapshot = Path(directory) / "candidate"
        git(
            "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(snapshot), isolated=True
        )
        git("update-ref", "HEAD", head, root=snapshot, isolated=True)
        git("read-tree", tree, root=snapshot, isolated=True)
        # The central scanner sanitizes Git environment variables. Give it a normal
        # index containing the exact captured candidate instead of the caller's alternate index.
        result = subprocess.run(
            [
                str(tooling.python),
                "-I",
                str(tooling.root / "scripts/privacy_guard.py"),
                "--root",
                str(snapshot),
                "--binary",
                str(tooling.gitleaks),
                "--staged",
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            timeout=1800,
        )
        if result.returncode:
            return result.returncode
    # The worktree was proven equal to the candidate. Isolate the suite's own
    # disposable Git repositories from the committing process's Git-local state.
    result = subprocess.run(VERIFY_COMMAND, cwd=ROOT, env=environment, check=False, timeout=3600)
    if result.returncode:
        return result.returncode
    if git("write-tree") != tree or git("rev-parse", "HEAD") != head:
        raise HookError(
            "The candidate index or HEAD changed during verification; retry the commit."
        )
    require_staged_worktree()
    print("Staged privacy and strict verification passed for the unchanged candidate.")
    return 0


class Arguments(argparse.Namespace):
    action: str
    privacy_root: Path | None = None
    privacy_python: Path | None = None
    gitleaks: Path | None = None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "run"))
    parser.add_argument("--privacy-root", type=Path)
    parser.add_argument("--privacy-python", type=Path)
    parser.add_argument("--gitleaks", type=Path)
    args = parser.parse_args(namespace=Arguments())
    try:
        if args.action == "install":
            if args.privacy_root is None or args.privacy_python is None or args.gitleaks is None:
                raise HookError(
                    "Installation requires --privacy-root, --privacy-python and --gitleaks."
                )
            install(Tooling(args.privacy_root, args.privacy_python, args.gitleaks))
            return 0
        return run()
    except HookError as error:
        print(f"pre-commit: {error}", file=sys.stderr)
    except (OSError, subprocess.SubprocessError):
        print(
            "pre-commit: a required Git, scanner or verification operation could not complete.",
            file=sys.stderr,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
