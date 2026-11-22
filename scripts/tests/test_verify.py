"""Regression checks for failure propagation and invalid execution dependencies."""

import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bootstrap
import check_contracts
import verify
from bootstrap import extract_binary, verified
from check_contracts import validate_graph
from verify import run_check


class VerificationContracts(unittest.TestCase):
    def test_missing_and_failing_commands_cannot_report_success(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            environment = dict(os.environ)
            missing = run_check("missing", [str(output / "missing-tool")], output, environment)
            failed = run_check(
                "failed", [sys.executable, "-c", "raise SystemExit(7)"], output, environment
            )
            version = run_check(
                "version",
                [sys.executable, "--version"],
                output,
                environment,
                expected="wrong-version",
            )
            self.assertEqual(
                [missing["exit_code"], failed["exit_code"], version["exit_code"]], [127, 7, 1]
            )
            self.assertTrue(all(item["status"] == "failed" for item in [missing, failed, version]))

    def test_pinned_versions_reject_near_matches_and_timeout(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            environment = dict(os.environ)
            for observed in ("18.30.1", "8.30.10", "8.30.1-beta", "8.30.1+local"):
                with (
                    self.subTest(observed=observed),
                    patch.object(verify.subprocess, "run") as execute,
                ):

                    def respond(command, observed=observed, **kwargs):
                        kwargs["stdout"].write(observed + "\n")
                        return subprocess.CompletedProcess(command, 0)

                    execute.side_effect = respond
                    result = run_check(
                        "version", ["gitleaks", "version"], output, environment, expected="8.30.1"
                    )
                    self.assertEqual(result["status"], "failed")
            with patch.object(
                verify.subprocess, "run", side_effect=subprocess.TimeoutExpired(["tool"], 1)
            ):
                result = run_check("timeout", ["tool"], output, environment, timeout=1)
            self.assertEqual(result["exit_code"], 124)

    def test_source_identity_includes_file_changes_and_broken_symlinks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.py"
            source.write_text("first\n")
            link = root / "broken-link"
            original_is_symlink = Path.is_symlink
            # Model a tracked broken link without requiring Windows symlink privileges.
            with (
                patch.object(verify, "git", return_value="source.py\0broken-link\0"),
                patch.object(
                    Path, "is_symlink", lambda path: path == link or original_is_symlink(path)
                ),
                patch.object(verify.os, "readlink", return_value="missing-one") as readlink,
            ):
                first = verify.source_hash(root)
                self.assertIn(link, verify.source_files(root))
                source.write_text("second\n")
                self.assertNotEqual(first, verify.source_hash(root))
                second = verify.source_hash(root)
                readlink.return_value = "missing-two"
                self.assertNotEqual(second, verify.source_hash(root))

    def test_initialization_failure_replaces_old_success_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / "artifacts/verification/latest"
            output.mkdir(parents=True)
            receipt = output / "receipt.json"
            receipt.write_text(json.dumps({"status": "passed", "source_revision": "old"}))
            with (
                patch.object(verify, "ROOT", root),
                patch.object(verify, "git", return_value="new"),
                patch.object(verify, "source_hash", side_effect=OSError("unreadable source")),
                patch.object(sys, "argv", ["verify.py"]),
            ):
                with self.assertRaises(OSError):
                    verify.main()
            self.assertNotEqual(json.loads(receipt.read_text())["status"], "passed")

    def test_complete_harness_passes_only_with_fresh_successful_outputs(self):
        for scenario in (
            "success",
            "command_failure",
            "missing_tool",
            "missing_artifact",
            "source_changed",
        ):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                source = root / "source.py"
                source.write_text("original\n")
                output = root / "artifacts/verification/latest"
                output.mkdir(parents=True)
                (output / "receipt.json").write_text('{"status":"passed"}')
                (output / "python-coverage.xml").write_text("stale coverage")
                (output / "old.log").write_text("stale log")

                def git_info(*args, **kwargs):
                    if args[0] == "ls-files":
                        return "source.py\0"
                    return "a" * 40 if args == ("rev-parse", "HEAD") else ""

                versions = {
                    "rustc": f"rustc {bootstrap.RUST} (fixture)",
                    sys.executable: "Python 3.15.2",
                    "uv": "uv 0.13.9 (fixture)",
                    **{
                        name: f"{name} {version}" for name, version in bootstrap.CARGO_TOOLS.items()
                    },
                    **{name: values[0] for name, values in bootstrap.NATIVE_TOOLS.items()},
                }

                def execute(command, scenario=scenario, versions=versions, source=source, **kwargs):
                    if scenario == "missing_tool" and command[0] == "actionlint":
                        raise FileNotFoundError("missing fixture tool")
                    if "--version" in command or "-version" in command or "version" in command:
                        tool = (
                            "cargo-llvm-cov"
                            if command[0] == "cargo" and "llvm-cov" in command
                            else command[0]
                        )
                        kwargs["stdout"].write(versions[tool] + "\n")
                    if "scripts/check_contracts.py" in command:
                        if scenario == "command_failure":
                            return subprocess.CompletedProcess(command, 7)
                        if scenario == "source_changed":
                            source.write_text("changed during verification\n")
                    if (
                        "coverage" in command
                        and "xml" in command
                        and scenario != "missing_artifact"
                    ):
                        Path(command[command.index("-o") + 1]).write_text("<coverage />")
                    if "--output-path" in command:
                        Path(command[command.index("--output-path") + 1]).write_text("TN:fresh\n")
                    if "pip_audit" in command:
                        Path(command[command.index("--output") + 1]).write_text('{"components":[]}')
                    return subprocess.CompletedProcess(command, 0)

                with (
                    patch.object(verify, "ROOT", root),
                    patch.object(verify, "git", side_effect=git_info),
                    patch.object(
                        verify.platform, "platform", return_value="synthetic-test-platform"
                    ),
                    patch.object(
                        verify.platform, "machine", return_value="synthetic-test-architecture"
                    ),
                    patch.object(verify.subprocess, "run", side_effect=execute),
                    patch.object(sys, "argv", ["verify.py", "--deep"]),
                    redirect_stdout(io.StringIO()),
                ):
                    code = verify.main()
                receipt = json.loads((output / "receipt.json").read_text())
                self.assertEqual(code, int(scenario != "success"))
                self.assertEqual(receipt["status"], "passed" if scenario == "success" else "failed")
                self.assertEqual(receipt["source_revision"], "a" * 40)
                self.assertFalse(receipt["official_owner_device_accepted"])
                self.assertFalse((output / "old.log").exists())
                names = {item["name"] for item in receipt["checks"]}
                self.assertTrue(
                    {"rust-test-debug", "rust-test-release", "rust-advisories", "history-secrets"}
                    <= names
                )
                if scenario == "missing_artifact":
                    self.assertFalse((output / "python-coverage.xml").exists())
                    self.assertIn("artifact-python-coverage.xml", receipt["failed_checks"])
                elif scenario == "source_changed":
                    self.assertIn("source-unchanged", receipt["failed_checks"])

    def test_output_outside_verification_directory_is_rejected(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(sys, "argv", ["verify.py", "--output", folder]),
            redirect_stdout(io.StringIO()),
            patch("sys.stderr", new=io.StringIO()),
        ):
            with self.assertRaises(SystemExit) as raised:
                verify.main()
            self.assertEqual(raised.exception.code, 2)

    def test_cycles_and_missing_prerequisites_are_rejected(self):
        for graph in [
            [{"id": "A", "requires": ["B"], "status": "pending"}],
            [
                {"id": "A", "requires": ["B"], "status": "pending"},
                {"id": "B", "requires": ["A"], "status": "pending"},
            ],
            [
                {"id": "A", "requires": [], "status": "pending"},
                {"id": "A", "requires": [], "status": "pending"},
            ],
        ]:
            with self.assertRaises(ValueError):
                validate_graph(graph)

    def test_document_checks_reject_invalid_json_and_broken_links(self):
        for scenario in ("valid", "invalid_json", "broken_link"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                (root / "conductor").mkdir()
                (root / "conductor/dependencies.json").write_text(
                    json.dumps({"milestones": [{"id": "A", "requires": [], "status": "pending"}]})
                )
                (root / "data.json").write_text("{" if scenario == "invalid_json" else "{}")
                (root / "README.md").write_text(
                    "[data](missing.json)" if scenario == "broken_link" else "[data](data.json)"
                )
                names = "README.md\0data.json\0conductor/dependencies.json\0"
                with (
                    patch.object(check_contracts, "ROOT", root),
                    patch.object(check_contracts.subprocess, "check_output", return_value=names),
                    redirect_stdout(io.StringIO()),
                ):
                    if scenario == "valid":
                        check_contracts.main()
                    else:
                        with self.assertRaises(ValueError):
                            check_contracts.main()

    def test_tool_installation_rejects_wrong_hash_and_link_member(self):
        with self.assertRaises(ValueError):
            verified(b"unexpected", "0" * 64)
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w:gz") as archive:
            member = tarfile.TarInfo("gitleaks")
            member.type = tarfile.SYMTYPE
            member.linkname = "outside"
            archive.addfile(member)
        with self.assertRaises(ValueError):
            extract_binary(payload.getvalue(), "gitleaks", False)

    @staticmethod
    def native_fixture(system, machine, suffix):
        resources = {}
        tools = {}
        for name, (version, repository, _) in bootstrap.NATIVE_TOOLS.items():
            architecture = (
                "arm64" if machine == "arm64" else ("x64" if name == "gitleaks" else "amd64")
            )
            filename = f"{name}_{version}_{system}_{architecture}.{suffix}"
            executable = name + (".exe" if suffix == "zip" else "")
            payload = io.BytesIO()
            contents = f"fixture binary: {name}".encode()
            if suffix == "zip":
                with zipfile.ZipFile(payload, "w") as archive:
                    archive.writestr(executable, contents)
            else:
                with tarfile.open(fileobj=payload, mode="w:gz") as archive:
                    member = tarfile.TarInfo(executable)
                    member.size = len(contents)
                    archive.addfile(member, io.BytesIO(contents))
            binary_archive = payload.getvalue()
            manifest = f"{hashlib.sha256(binary_archive).hexdigest()}  {filename}\n".encode()
            base = f"https://github.com/{repository}/releases/download/v{version}"
            resources[f"{base}/{name}_{version}_checksums.txt"] = manifest
            resources[f"{base}/{filename}"] = binary_archive
            tools[name] = (version, repository, hashlib.sha256(manifest).hexdigest())
        return resources, tools

    def test_native_installation_uses_verified_platform_binaries(self):
        for system, machine, suffix in (
            ("linux", "x86_64", "tar.gz"),
            ("darwin", "arm64", "tar.gz"),
            ("windows", "AMD64", "zip"),
        ):
            with self.subTest(system=system), tempfile.TemporaryDirectory() as folder:
                resources, tools = self.native_fixture(system, machine, suffix)
                with (
                    patch.object(bootstrap.platform, "system", return_value=system),
                    patch.object(bootstrap.platform, "machine", return_value=machine),
                    patch.object(bootstrap, "NATIVE_TOOLS", tools),
                    patch.object(
                        bootstrap,
                        "urlopen",
                        side_effect=lambda url, resources=resources, **kwargs: io.BytesIO(
                            resources[url]
                        ),
                    ),
                    redirect_stdout(io.StringIO()),
                ):
                    bootstrap.install_native(Path(folder))
                for name in tools:
                    target = Path(folder) / (name + (".exe" if suffix == "zip" else ""))
                    self.assertEqual(target.read_bytes(), f"fixture binary: {name}".encode())

    def test_native_installation_rejects_tampering_and_unsupported_platforms(self):
        for kind in ("checksums.txt", "tar.gz"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                resources, tools = self.native_fixture("linux", "x86_64", "tar.gz")
                altered = next(url for url in resources if url.endswith(kind))
                resources[altered] = b"tampered"
                with (
                    patch.object(bootstrap.platform, "system", return_value="Linux"),
                    patch.object(bootstrap.platform, "machine", return_value="x86_64"),
                    patch.object(bootstrap, "NATIVE_TOOLS", tools),
                    patch.object(
                        bootstrap,
                        "urlopen",
                        side_effect=lambda url, resources=resources, **kwargs: io.BytesIO(
                            resources[url]
                        ),
                    ),
                ):
                    with self.assertRaises(ValueError):
                        bootstrap.install_native(Path(folder))
                self.assertEqual(list(Path(folder).iterdir()), [])
        with (
            patch.object(bootstrap.platform, "system", return_value="unsupported"),
            patch.object(bootstrap, "urlopen") as download,
        ):
            with self.assertRaises(ValueError):
                bootstrap.install_native(Path("unused"))
            download.assert_not_called()

    def test_bootstrap_tool_failure_stops_native_installation(self):
        with (
            patch.object(sys, "argv", ["bootstrap.py"]),
            patch.object(
                bootstrap.subprocess,
                "run",
                side_effect=subprocess.CalledProcessError(1, ["rustup"]),
            ),
            patch.object(bootstrap, "install_native") as native,
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                bootstrap.main()
            native.assert_not_called()


if __name__ == "__main__":
    unittest.main()
