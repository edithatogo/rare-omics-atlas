#!/usr/bin/env python3
"""Run the same strict code gates locally and in CI; save every command's outcome."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from bootstrap import CARGO_TOOLS, NATIVE_TOOLS, RUST

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "tools/catalogue/Cargo.toml"


def git(*args: str, root: Path = ROOT) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def source_files(root: Path) -> list[Path]:
    names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z", root=root)
    return sorted(
        {
            root / name
            for name in names.split("\0")
            if name and ((root / name).is_file() or (root / name).is_symlink())
        }
    )


def source_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in source_files(root):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(b"symlink\0" if path.is_symlink() else b"file\0")
        digest.update(os.readlink(path).encode() if path.is_symlink() else path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def run_check(
    name: str,
    command: list[str],
    output: Path,
    environment: dict[str, str],
    *,
    expected: str | None = None,
    root: Path = ROOT,
    timeout: int = 1200,
) -> dict[str, object]:
    started = time.monotonic()
    log = output / f"{name}.log"
    try:
        with log.open("w", encoding="utf-8") as stream:
            result = subprocess.run(
                command,
                cwd=root,
                env=environment,
                stdout=stream,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                timeout=timeout,
            )
        code = result.returncode
        if (
            code == 0
            and expected is not None
            and not re.search(
                r"(?<![\w.+-])" + re.escape(expected.strip()) + r"(?![\w.+-])",
                log.read_text(encoding="utf-8"),
            )
        ):
            code = 1
            with log.open("a", encoding="utf-8") as stream:
                stream.write(f"\nRequired version not observed: {expected}\n")
    except (OSError, subprocess.TimeoutExpired) as exc:
        code = 124 if isinstance(exc, subprocess.TimeoutExpired) else 127
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"\nCheck could not finish: {type(exc).__name__}\n")
    print(f"{name}: {'passed' if code == 0 else 'FAILED'} ({code})", flush=True)
    return {
        "name": name,
        "command": command,
        "exit_code": code,
        "status": "passed" if code == 0 else "failed",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "log": log.name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/verification/latest")
    parser.add_argument(
        "--base",
        default=os.environ.get("VERIFY_BASE", "origin/main"),
        help="review base for the unchanged template patch-coverage gate",
    )
    parser.add_argument(
        "--deep", action="store_true", help="also scan complete reachable Git history"
    )
    args = parser.parse_args()
    selected_output: Path = args.output.absolute()
    output = selected_output.resolve()
    if not output.is_relative_to(ROOT / "artifacts/verification") or any(
        path.is_symlink() for path in [selected_output, *selected_output.parents]
    ):
        parser.error("--output must be inside artifacts/verification")
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output / "receipt.json"
    receipt_path.write_text(
        '{"status":"initializing","quality_level":"strict"}\n', encoding="utf-8"
    )
    # Remove only this harness's prior generated receipt/logs; do not reuse stale success.
    for stale in output.glob("*.log"):
        stale.unlink()
    for name in (
        ".coverage",
        "python-coverage.xml",
        "rust-lcov.info",
        "rust-coverage.xml",
        "python-sbom.json",
    ):
        (output / name).unlink(missing_ok=True)
    started = time.monotonic()
    environment = dict(os.environ)
    for key in ("GITLEAKS_CONFIG", "GITLEAKS_CONFIG_TOML"):
        environment.pop(key, None)
    tool_paths = [str(ROOT / "artifacts/tools/bin")]
    if environment.get("CARGO_HOME"):
        tool_paths.append(str(Path(environment["CARGO_HOME"]) / "bin"))
    environment["PATH"] = os.pathsep.join([*tool_paths, environment.get("PATH", "")])
    environment["RUSTDOCFLAGS"] = "-D warnings"
    environment["PYTHONWARNINGS"] = "error"
    environment["CARGO_BUILD_JOBS"] = environment.get("CARGO_BUILD_JOBS", "2")
    environment["COVERAGE_FILE"] = str(output / ".coverage")
    receipt: dict[str, object] = {
        "schema_version": 1,
        "quality_level": "strict",
        "status": "running",
        "started_at": datetime.now(UTC).isoformat(),
        "source_revision": git("rev-parse", "HEAD"),
        "coverage_base_revision": git(
            "rev-parse", "--verify", "--end-of-options", args.base + "^{commit}"
        ),
        "source_tree_sha256": source_hash(ROOT),
        "dirty_paths": git("status", "--porcelain").splitlines(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python": sys.version,
        "official_owner_device_accepted": False,
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "peak_rss_bytes": None,
        "limitations": [
            "Code gates do not establish scientific or owner-device acceptance.",
            "Local secret scan covers the source snapshot; the central privacy guard is a separate gate.",
            "Atlas code licence is unresolved; this receipt is not Community Standards acceptance.",
        ],
    }
    checks: list[dict[str, object]] = []
    receipt["checks"] = checks

    def save() -> None:
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    def check(name: str, command: list[str], expected: str | None = None) -> None:
        checks.append(run_check(name, command, output, environment, expected=expected))
        save()

    save()
    python = sys.executable
    cargo = ["cargo", f"+{RUST}"]
    common = ["--manifest-path", MANIFEST, "--locked", "--all-features"]
    check("rust-version", ["rustc", f"+{RUST}", "--version", "--verbose"], f"rustc {RUST} ")
    check("python-version", [python, "--version"], "Python 3.15.2")
    check("uv-version", ["uv", "--version"], "uv 0.13.9 ")
    for tool, version in CARGO_TOOLS.items():
        command = (
            [*cargo, "llvm-cov", "--version"] if tool == "cargo-llvm-cov" else [tool, "--version"]
        )
        check(f"{tool}-version", command, f"{tool} {version}")
    for tool, (version, _, _) in NATIVE_TOOLS.items():
        check(f"{tool}-version", [tool, "version" if tool == "gitleaks" else "-version"], version)
    check("diff", ["git", "diff", "--check"])
    check("python-lock", ["uv", "lock", "--check", "--project", "tools/hf-release"])
    check("contracts", [python, "scripts/check_contracts.py"])
    check("workflow-lint", ["actionlint", "-shellcheck="])
    check("rust-format", [*cargo, "fmt", "--manifest-path", MANIFEST, "--all", "--", "--check"])
    check("rust-clippy", [*cargo, "clippy", *common, "--all-targets", "--", "-D", "warnings"])
    check("rust-test-debug", [*cargo, "test", *common, "--all-targets"])
    check("rust-test-release", [*cargo, "test", *common, "--all-targets", "--release"])
    check("rust-doctests", [*cargo, "test", *common, "--doc"])
    check("rust-docs", [*cargo, "doc", *common, "--no-deps"])
    check("python-lint", [python, "-m", "ruff", "check", "."])
    check("python-format", [python, "-m", "ruff", "format", "--check", "."])
    check("python-types", [python, "-m", "pyright"])
    check(
        "harness-tests",
        [
            python,
            "-m",
            "coverage",
            "run",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts/tests",
            "-v",
        ],
    )
    check(
        "publisher-tests",
        [
            python,
            "-m",
            "coverage",
            "run",
            "--append",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tools/hf-release/tests",
            "-v",
        ],
    )
    check(
        "python-coverage",
        [python, "-m", "coverage", "xml", "-o", str(output / "python-coverage.xml")],
    )
    check("python-coverage-summary", [python, "-m", "coverage", "report"])
    check(
        "rust-coverage",
        [
            *cargo,
            "llvm-cov",
            *common,
            "--all-targets",
            "--lcov",
            "--output-path",
            str(output / "rust-lcov.info"),
        ],
    )
    check(
        "rust-advisories",
        [*cargo, "audit", "--file", "tools/catalogue/Cargo.lock", "--deny", "warnings"],
    )
    check(
        "rust-coverage-xml",
        [
            *cargo,
            "llvm-cov",
            "report",
            "--manifest-path",
            MANIFEST,
            "--cobertura",
            "--output-path",
            str(output / "rust-coverage.xml"),
        ],
    )
    check(
        "patch-coverage",
        [
            "diff-cover",
            str(output / "python-coverage.xml"),
            str(output / "rust-coverage.xml"),
            "--compare-branch",
            str(receipt["coverage_base_revision"]),
            "--include-untracked",
            "--branch-coverage",
            "--fail-under",
            "90",
        ],
    )
    check(
        "python-advisories",
        [
            python,
            "-m",
            "pip_audit",
            "--strict",
            "--progress-spinner",
            "off",
            "--format",
            "cyclonedx-json",
            "--output",
            str(output / "python-sbom.json"),
        ],
    )
    check(
        "rust-dependency-inventory",
        [*cargo, "metadata", "--manifest-path", MANIFEST, "--locked", "--format-version", "1"],
    )
    with tempfile.TemporaryDirectory(prefix="atlas-source-scan-") as directory:
        scan_root = Path(directory)
        snapshot = scan_root / "source"
        snapshot.mkdir()
        config = scan_root / "default.toml"
        config.write_text("[extend]\nuseDefault = true\n", encoding="utf-8")
        ignore = scan_root / "empty-ignore"
        ignore.write_text("", encoding="utf-8")
        secret_flags = [
            "--no-banner",
            "--redact=100",
            "--config",
            str(config),
            "--gitleaks-ignore-path",
            str(ignore),
            "--ignore-gitleaks-allow",
        ]
        for path in source_files(ROOT):
            if not path.is_symlink():
                target = snapshot / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        check("source-secrets", ["gitleaks", "dir", str(snapshot), *secret_flags])
        if args.deep:
            check(
                "complete-history",
                [
                    python,
                    "-c",
                    "import subprocess; assert subprocess.check_output(['git','rev-parse','--is-shallow-repository'],text=True).strip() == 'false'",
                ],
            )
            if checks[-1]["exit_code"] == 0:
                check(
                    "history-secrets", ["gitleaks", "git", ".", "--log-opts=--all", *secret_flags]
                )
    if source_hash(ROOT) != receipt["source_tree_sha256"]:
        checks.append({"name": "source-unchanged", "status": "failed", "exit_code": 1})
    for name in ("python-coverage.xml", "rust-lcov.info", "rust-coverage.xml", "python-sbom.json"):
        path = output / name
        if not path.is_file() or path.stat().st_size == 0:
            checks.append({"name": f"artifact-{name}", "status": "failed", "exit_code": 1})
    failed = [item["name"] for item in checks if item["exit_code"] != 0]
    receipt.update(
        {
            "status": "failed" if failed else "passed",
            "failed_checks": failed,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "completed_at": datetime.now(UTC).isoformat(),
        }
    )
    save()
    print(f"Strict verification {receipt['status']}: {receipt_path}", flush=True)
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
