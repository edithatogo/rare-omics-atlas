#!/usr/bin/env python3
"""Install pinned verification tools; Python 3.11+, git and rustup are prerequisites."""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import platform
import subprocess
import tarfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

RUST = "1.95.0"
CARGO_TOOLS = {"cargo-llvm-cov": "0.8.7", "cargo-audit": "0.23.0"}
NATIVE_TOOLS = {
    "gitleaks": (
        "8.30.1",
        "gitleaks/gitleaks",
        "061476c21adaf5441516f96f185c1a4706a83cd6329b9b38762271b3d4a52fae",
    ),
    "actionlint": (
        "1.7.12",
        "rhysd/actionlint",
        "433028cf0ba3c42163ea1a668dedce30fcdbe84fe912b1a5e288c006eab8a4f5",
    ),
}


def verified(data: bytes, expected: str) -> bytes:
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Downloaded verification tool failed SHA-256 validation")
    return data


def download(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:
        return response.read()


def extract_binary(archive: bytes, name: str, windows: bool) -> bytes:
    """Read exactly the expected binary; never extract arbitrary archive paths."""
    if windows:
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            return zipped.read(name)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        member = tar.getmember(name)
        if not member.isfile():
            raise ValueError("Expected a regular tool binary")
        stream = tar.extractfile(member)
        if stream is None:
            raise ValueError("Tool binary is missing")
        return stream.read()


def install_native(destination: Path) -> None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system not in {"linux", "darwin", "windows"} or machine not in {
        "x86_64",
        "amd64",
        "arm64",
        "aarch64",
    }:
        raise ValueError(f"Unsupported verification-tool platform: {system}/{machine}")
    windows = system == "windows"
    arch = "arm64" if machine in {"arm64", "aarch64"} else "amd64"
    destination.mkdir(parents=True, exist_ok=True)
    for name, (version, repository, checksum_digest) in NATIVE_TOOLS.items():
        base = f"https://github.com/{repository}/releases/download/v{version}"
        manifest = verified(
            download(f"{base}/{name}_{version}_checksums.txt"), checksum_digest
        ).decode("utf-8")
        checksums = {
            line.split()[1].lstrip("*"): line.split()[0]
            for line in manifest.splitlines()
            if line.strip()
        }
        tool_arch = "x64" if name == "gitleaks" and arch == "amd64" else arch
        filename = f"{name}_{version}_{system}_{tool_arch}.{'zip' if windows else 'tar.gz'}"
        archive = verified(download(f"{base}/{filename}"), checksums[filename])
        executable = name + (".exe" if windows else "")
        target = destination / executable
        target.write_bytes(extract_binary(archive, executable, windows))
        target.chmod(0o755)
        print(f"Installed {name} {version}", flush=True)


def main() -> None:
    os.environ.setdefault("CARGO_BUILD_JOBS", "2")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--native-only", action="store_true", help="only install Gitleaks and actionlint"
    )
    parser.add_argument(
        "--bin-dir", type=Path, default=Path(__file__).resolve().parents[1] / "artifacts/tools/bin"
    )
    args = parser.parse_args()
    if not args.native_only:
        subprocess.run(
            [
                "rustup",
                "toolchain",
                "install",
                RUST,
                "--profile",
                "minimal",
                "--component",
                "rustfmt",
                "--component",
                "clippy",
                "--component",
                "llvm-tools-preview",
            ],
            check=True,
        )
        for tool, version in CARGO_TOOLS.items():
            subprocess.run(
                ["cargo", f"+{RUST}", "install", tool, "--locked", "--version", version], check=True
            )
    install_native(args.bin_dir)
    print(f"Native tools: {args.bin_dir.resolve()}")


if __name__ == "__main__":
    main()
