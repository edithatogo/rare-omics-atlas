#!/usr/bin/env python3
"""Read-only verification of the 13-object metadata subset; never closes raw publication."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, cast

from huggingface_hub import HfApi
from huggingface_hub.hf_api import RepoFile

if TYPE_CHECKING:
    from publisher import ObjectFields, Payload


# The operational implementation and historical publication source have separate identities.
REVIEWED_PUBLISHER_SHA256 = "7f4211fae4e26a24f3b1d04382b57da2a0590df6f2075a7fae336d57220ca81a"
BASELINE_PUBLISHER_SHA256 = "1641709238710f6496b3fed1d8983aa9fa3f867cc50cd68753df69a85a447aea"


class Arguments(argparse.Namespace):
    root: Path
    hub_revision: str
    receipt: Path
    include_staging_manifest: bool


def record(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("metadata record expected")
    fields = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in fields):
        raise ValueError("metadata record keys must be strings")
    return cast(dict[str, object], value)


def records(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise ValueError("metadata object list expected")
    return [record(item) for item in cast(list[object], value)]


def text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("metadata text field expected")
    return value


def load_reviewed_publisher(root: Path) -> ModuleType:
    publisher_path = root / "tools/hf-release/publisher.py"
    # Reject lexical symlinks and unreviewed bytes before executing any shared code.
    if any(path.is_symlink() for path in [publisher_path, *publisher_path.parents]):
        raise ValueError("symlink in publisher path")
    if hashlib.sha256(publisher_path.read_bytes()).hexdigest() != REVIEWED_PUBLISHER_SHA256:
        raise ValueError("publisher differs from the reviewed implementation")
    spec = importlib.util.spec_from_file_location("publisher", publisher_path)
    if spec is None or spec.loader is None:
        raise ValueError("reviewed publisher cannot be loaded")
    publisher = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = publisher
    spec.loader.exec_module(publisher)
    return publisher


def verify_baseline_publisher(root: Path, baseline: str) -> None:
    original = subprocess.check_output(
        ["git", "-C", str(root), "show", f"{baseline}:tools/hf-release/publisher.py"]
    )
    # Preserve the publication's original source pin without relabelling later typed code.
    if hashlib.sha256(original).hexdigest() != BASELINE_PUBLISHER_SHA256:
        raise ValueError("historical publisher differs from the reviewed baseline")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--hub-revision", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--include-staging-manifest", action="store_true")
    args = parser.parse_args(namespace=Arguments())
    started = time.monotonic()
    receipt: dict[str, object] = {
        "schema_version": 1,
        "record_type": "metadata_subset_receipt",
        "status": "verification_started",
        "publication_route": "hugging_face_browser_editor",
        "automated_publisher_upload_executed": False,
        "official_github_actions_run_observed": False,
        "full_release_verified": False,
        "full_publication_track_status": "open_raw_transfer_blocked",
        "raw_archives_published_by_this_route": 0,
        "hub_revision": args.hub_revision,
        "checked_at": datetime.now(UTC).isoformat(),
        "verification_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": sys.version,
        "reviewed_publisher_sha256": REVIEWED_PUBLISHER_SHA256,
        "baseline_publisher_sha256": BASELINE_PUBLISHER_SHA256,
    }
    receipt_safe = False
    publisher: ModuleType | None = None
    receipt_path: Path | None = None
    remote_objects: list[dict[str, object]] = []
    try:
        publisher = load_reviewed_publisher(args.root)
        safe_receipt_path: Path = publisher.local_path(
            args.receipt.absolute().parent, args.receipt.name
        )
        receipt_path = safe_receipt_path
        manifest_path: Path = publisher.local_path(
            args.root,
            "research/releases/2026-11-22/hub-staging/staging-publication-manifest.json",
        )
        full_manifest_path: Path = publisher.local_path(
            args.root, "research/releases/2026-11-22/manifest.json"
        )
        script_path: Path = publisher.local_path(
            Path(__file__).absolute().parent, Path(__file__).name
        )
        protected = {manifest_path.resolve(), full_manifest_path.resolve(), script_path.resolve()}
        protected.update(
            publisher.local_path(args.root, f"tools/hf-release/{name}").resolve()
            for name in ("publisher.py", "pyproject.toml", "uv.lock")
        )
        if safe_receipt_path.resolve() in protected:
            raise ValueError("receipt would overwrite a verification input")
        manifest_bytes = manifest_path.read_bytes()
        manifest = record(json.loads(manifest_bytes))
        objects = records(manifest.get("objects"))
        protected.update(
            publisher.local_path(args.root, obj.get("source_path")).resolve() for obj in objects
        )
        if safe_receipt_path.resolve() in protected:
            raise ValueError("receipt would overwrite a verification input")
        # No failure report may be written until every consumed input is protected.
        receipt_safe = True
        if not re.fullmatch(r"[0-9a-f]{40}", args.hub_revision):
            raise ValueError("full immutable Hub SHA required")
        if importlib.metadata.version("huggingface-hub") != "2.4.0":
            raise ValueError("reviewed Hub client 2.4.0 required")
        baseline = text(manifest.get("baseline_source_revision"))
        if len(objects) != 13 or manifest.get("full_release_status") != "pending_raw_archives":
            raise ValueError("unexpected metadata subset contract")
        full_bytes = full_manifest_path.read_bytes()
        if hashlib.sha256(full_bytes).hexdigest() != manifest.get("planned_full_manifest_sha256"):
            raise ValueError("planned full release manifest changed")
        verify_baseline_publisher(args.root, baseline)
        payloads: list[Payload] = []
        origins: list[dict[str, object]] = []
        seen: set[str] = set()
        for obj in objects:
            destination = text(obj.get("path_in_repo"))
            if obj.get("kind") != "metadata" or destination in seen:
                raise ValueError("invalid or duplicate subset object")
            seen.add(destination)
            publisher.relative_path(destination)
            local: Path = publisher.local_path(args.root, obj.get("source_path"))
            size = obj.get("size_bytes")
            if type(size) is not int or size < 0:
                raise ValueError("invalid metadata object size")
            expected: ObjectFields = {
                "path_in_repo": destination,
                "size_bytes": size,
                "sha256": text(obj.get("sha256")),
                "redistribution_basis": text(obj.get("redistribution_basis")),
            }
            payload: Payload = publisher.verify_file(local, expected)
            origin = record(obj.get("origin"))
            if origin.get("kind") == "unchanged_github_blob":
                if origin.get("revision") != baseline:
                    raise ValueError("baseline source revision mismatch")
                original = subprocess.check_output(
                    ["git", "-C", str(args.root), "show", f"{baseline}:{text(origin.get('path'))}"]
                )
                if original != local.read_bytes() or payload.git_blob_sha1 != origin.get(
                    "git_blob_sha1"
                ):
                    raise ValueError("metadata differs from its immutable Git origin")
            elif origin.get("kind") == "new_staging_notice":
                if origin.get("revision") is not None:
                    raise ValueError("new notice must not claim an unverified baseline origin")
            else:
                raise ValueError("unknown notice/source origin")
            payloads.append(payload)
            origins.append(origin)
        if (
            sum(origin["kind"] == "unchanged_github_blob" for origin in origins) != 10
            or sum(origin["kind"] == "new_staging_notice" for origin in origins) != 3
        ):
            raise ValueError("unexpected source-origin counts")
        if args.include_staging_manifest:
            payloads.append(
                publisher.bytes_payload(
                    "releases/2026-11-22/staging-publication-manifest.json", manifest_bytes
                )
            )
        repo_id = text(manifest.get("repo_id"))
        api = HfApi(token=False)
        info = api.repo_info(repo_id, repo_type="dataset", revision=args.hub_revision)
        if info.private is not False or info.sha != args.hub_revision:
            raise ValueError("public exact Hub revision not confirmed")
        remote_objects = publisher.verify_remote(api, repo_id, args.hub_revision, payloads)
        receipt["remote_objects"] = remote_objects
        files = [
            item.path
            for item in api.list_repo_tree(
                repo_id, repo_type="dataset", revision=args.hub_revision, recursive=True
            )
            if isinstance(item, RepoFile)
        ]
        raw = [
            path for path in files if path.lower().endswith((".tar", ".idat", ".idat.gz", ".zip"))
        ]
        receipt["raw_archive_paths_observed"] = raw
        if raw:
            raise ValueError(
                "raw object present; reconcile metadata-only notices before acceptance"
            )
        receipt.update(
            {
                "status": "metadata_subset_ui_published_api_verified_raw_pending",
                "repo_id": repo_id,
                "hub_commit_url": f"https://huggingface.co/datasets/{repo_id}/commit/{args.hub_revision}",
                "baseline_source_revision": baseline,
                "staging_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "verified_metadata_objects": 13,
                "verified_additional_staging_manifest": args.include_staging_manifest,
                "unchanged_baseline_files": 10,
                "new_notice_files": 3,
                "raw_archive_absence_checked": True,
                "huggingface_hub_version": "2.4.0",
                "publication_acceptance": "metadata subset only; full T09 remains open",
            }
        )
        exit_code = 0
    except Exception as exc:
        receipt["status"] = "verification_failed"
        receipt["failure"] = {
            "type": type(exc).__name__,
            "message": str(exc)
            if type(exc).__name__ in ("ValueError", "ReleaseError")
            else "read-only verification failed; arbitrary exception details withheld",
        }
        exit_code = 1
    receipt["elapsed_seconds"] = time.monotonic() - started
    if receipt_safe and publisher is not None and receipt_path is not None:
        publisher.write_receipt(receipt_path, receipt)
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "verified_remote_objects": len(remote_objects),
                "full_release_verified": False,
            }
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
