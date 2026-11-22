#!/usr/bin/env python3
"""Publish only a reviewed, content-hashed manifest through the official Hub API."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict, cast
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

if TYPE_CHECKING:
    from huggingface_hub import HfApi


class ObjectFields(TypedDict):
    path_in_repo: str
    size_bytes: int
    sha256: str
    redistribution_basis: str


class MetadataObject(ObjectFields):
    kind: Literal["metadata"]
    source_path: str


class ArchiveObject(ObjectFields):
    kind: Literal["source_archive"]
    cache_path: str
    source_url: str
    accession: str


class Manifest(TypedDict):
    schema_version: int
    repo_id: str
    source_repository: NotRequired[str]
    release_id: str
    objects: list[MetadataObject | ArchiveObject]


class Arguments(argparse.Namespace):
    manifest: Path
    root: Path
    data_root: Path
    source_revision: str | None
    receipt: Path
    upload: bool
    fetch_sources: bool


REPOSITORY = "https://github.com/edithatogo/rare-omics-atlas"
HUB_REPOSITORY = "edithatogo/rare-omics-atlas"
CHUNK = 8 * 1024 * 1024
SMALL_FILE = 10 * 1024 * 1024


class ReleaseError(ValueError):
    """A known validation failure whose message contains no credentials/data values."""


@dataclass(frozen=True)
class Payload:
    path_in_repo: str
    content: Path | bytes
    size_bytes: int
    sha256: str
    git_blob_sha1: str | None


def relative_path(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or not re.fullmatch(r"[A-Za-z0-9._/-]+", value):
        raise ReleaseError("invalid relative path")
    path = PurePosixPath(value)
    if (
        not path.parts
        or path.is_absolute()
        or str(path) != value
        or any(p in (".", "..", ".git") for p in path.parts)
    ):
        raise ReleaseError("unsafe or noncanonical relative path")
    return path


def local_path(root: Path, value: object) -> Path:
    relative = relative_path(value)
    root = root.absolute()
    # Check the lexical chain before resolve() could hide a symlink.
    for ancestor in [root, *root.parents]:
        if ancestor.is_symlink():
            raise ReleaseError("symlink in local root")
    candidate = root
    for component in relative.parts:
        candidate /= component
        if candidate.is_symlink():
            raise ReleaseError("symlink in selected source path")
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ReleaseError("source escapes its declared root")
    return candidate


def validate_source_url(url: object, accession: object) -> None:
    if not isinstance(accession, str) or not re.fullmatch(r"GSE[0-9]+", accession):
        raise ReleaseError("raw archive lacks a valid GEO accession")
    if not isinstance(url, str):
        raise ReleaseError("raw archive URL missing")
    bucket = accession[:-3] + "nnn" if len(accession[3:]) > 3 else "GSEnnn"
    expected_path = f"/geo/series/{bucket}/{accession}/suppl/{accession}_RAW.tar"
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "ftp.ncbi.nlm.nih.gov"
        or parsed.path != expected_path
        or parsed.query
        or parsed.fragment
    ):
        raise ReleaseError(
            "unsupported source URL; only exact public GEO raw archive HTTPS URLs are accepted"
        )


def generated_paths(manifest: Manifest) -> tuple[str, str]:
    prefix = f"releases/{manifest['release_id']}"
    return f"{prefix}/manifest.json", f"{prefix}/provenance.json"


def validate_manifest(value: object) -> None:
    if not isinstance(value, dict):
        raise ReleaseError("unsupported manifest schema")
    manifest = cast(dict[object, object], value)
    if manifest.get("schema_version") != 1:
        raise ReleaseError("unsupported manifest schema")
    if manifest.get("repo_id") != HUB_REPOSITORY:
        raise ReleaseError("manifest targets a different Hub repository")
    if manifest.get("source_repository", REPOSITORY) != REPOSITORY:
        raise ReleaseError("manifest names a different GitHub source repository")
    release_id = manifest.get("release_id")
    if not isinstance(release_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", release_id
    ):
        raise ReleaseError("invalid release identifier")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ReleaseError("manifest objects must be a nonempty list")
    seen = {f"releases/{release_id}/manifest.json", f"releases/{release_id}/provenance.json"}
    for item in cast(list[object], objects):
        if not isinstance(item, dict):
            raise ReleaseError("manifest object must be a record")
        obj = cast(dict[object, object], item)
        destination = str(relative_path(obj.get("path_in_repo")))
        if destination in seen:
            raise ReleaseError("duplicate or reserved destination")
        seen.add(destination)
        size = obj.get("size_bytes")
        if type(size) is not int or size < 0:
            raise ReleaseError("invalid expected object size")
        digest = obj.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ReleaseError("invalid expected SHA-256")
        basis = obj.get("redistribution_basis")
        if not isinstance(basis, str) or not basis.strip():
            raise ReleaseError("object redistribution basis missing")
        if obj.get("kind") == "metadata":
            relative_path(obj.get("source_path"))
            if "source_url" in obj or "cache_path" in obj:
                raise ReleaseError("metadata object has raw-source fields")
        elif obj.get("kind") == "source_archive":
            relative_path(obj.get("cache_path"))
            validate_source_url(obj.get("source_url"), obj.get("accession"))
            if "source_path" in obj:
                raise ReleaseError("source archive has a metadata source path")
        else:
            raise ReleaseError("unsupported object kind")


def read_manifest(content: bytes) -> Manifest:
    value: object = json.loads(content)
    validate_manifest(value)
    # The validator above checks every field consumed by the publication path.
    return cast(Manifest, value)


def verify_file(path: Path, obj: ObjectFields) -> Payload:
    if path.is_symlink() or not path.is_file():
        raise ReleaseError("selected source is missing or is not a regular file")
    size = path.stat().st_size
    if size != obj["size_bytes"]:
        raise ReleaseError(f"size mismatch for {obj['path_in_repo']}")
    digest = hashlib.sha256()
    git_digest = (
        hashlib.sha1(f"blob {size}\0".encode(), usedforsecurity=False)
        if size <= SMALL_FILE
        else None
    )
    observed_size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            observed_size += len(block)
            digest.update(block)
            if git_digest is not None:
                git_digest.update(block)
    if observed_size != size or digest.hexdigest() != obj["sha256"]:
        raise ReleaseError(f"hash/size mismatch for {obj['path_in_repo']}")
    return Payload(
        obj["path_in_repo"],
        path,
        size,
        digest.hexdigest(),
        git_digest.hexdigest() if git_digest else None,
    )


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Request, fp: object, code: int, msg: str, headers: object, newurl: str
    ) -> None:
        # Exact source URLs are part of the reviewed allowlist. Do not follow a redirect.
        return None


def fetch_archive(path: Path, obj: ArchiveObject) -> None:
    validate_source_url(obj["source_url"], obj["accession"])
    if path.exists() or path.is_symlink():
        # Even with --fetch-sources, an existing mismatch is never silently replaced.
        verify_file(path, obj)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    if part.exists() or part.is_symlink():
        raise ReleaseError("an existing partial download requires inspection")
    created = False
    try:
        request = Request(obj["source_url"], headers={"User-Agent": "rare-omics-atlas/0.1"})
        with build_opener(NoRedirect()).open(request, timeout=90) as response:
            if response.status != 200:
                raise ReleaseError("source download did not return HTTP 200")
            with part.open("xb") as stream:
                created = True
                received = 0
                for block in iter(lambda: response.read(CHUNK), b""):
                    received += len(block)
                    if received > obj["size_bytes"]:
                        raise ReleaseError("source download exceeded expected bytes")
                    stream.write(block)
        verify_file(part, obj)
        if path.exists() or path.is_symlink():
            raise ReleaseError("source destination appeared during download")
        part.rename(path)
    finally:
        # Only remove the partial created by this invocation, never a pre-existing object.
        if created and part.exists():
            part.unlink()


def bytes_payload(path: str, content: bytes) -> Payload:
    return Payload(
        path,
        content,
        len(content),
        hashlib.sha256(content).hexdigest(),
        hashlib.sha1(
            f"blob {len(content)}\0".encode() + content, usedforsecurity=False
        ).hexdigest(),
    )


def prepare(
    manifest: Manifest,
    manifest_bytes: bytes,
    root: Path,
    data_root: Path,
    fetch_sources: bool,
    source_revision: str | None,
) -> list[Payload]:
    validate_manifest(manifest)
    if source_revision is not None and not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ReleaseError("source revision must be a full lowercase Git SHA")
    payloads: list[Payload] = []
    for obj in manifest["objects"]:
        if obj["kind"] == "source_archive":
            path = local_path(data_root, obj["cache_path"])
            if fetch_sources:
                fetch_archive(path, obj)
        else:
            path = local_path(root, obj["source_path"])
        payloads.append(verify_file(path, obj))
    manifest_path, provenance_path = generated_paths(manifest)
    payloads.append(bytes_payload(manifest_path, manifest_bytes))
    provenance = {
        "schema_version": 1,
        "source_repository": REPOSITORY,
        "source_revision": source_revision,
        "source_commit_url": f"{REPOSITORY}/commit/{source_revision}" if source_revision else None,
        "release_id": manifest["release_id"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "publisher_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "objects": [
            {"path_in_repo": p.path_in_repo, "size_bytes": p.size_bytes, "sha256": p.sha256}
            for p in payloads
        ],
        "note": "Original source archives remain byte-identical; this provenance records publication, not scientific admission. Its own hash is recorded by the external publication receipt.",
    }
    payloads.append(
        bytes_payload(
            provenance_path, (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode()
        )
    )
    return payloads


def assert_source_checkout(
    root: Path, manifest_path: Path, manifest: Manifest, source_revision: str | None
) -> None:
    if not source_revision or not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ReleaseError("--upload requires a full --source-revision")
    root = root.resolve()
    publisher_dir = Path(__file__).resolve().parent
    if not publisher_dir.is_relative_to(root) or not manifest_path.resolve().is_relative_to(root):
        raise ReleaseError("publisher and manifest must belong to the source checkout")
    paths = [manifest_path.resolve().relative_to(root).as_posix()]
    paths += [obj["source_path"] for obj in manifest["objects"] if obj["kind"] == "metadata"]
    paths += [
        (publisher_dir / name).relative_to(root).as_posix()
        for name in ("publisher.py", "pyproject.toml", "uv.lock")
    ]

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            raise ReleaseError("source checkout validation failed")
        return result.stdout.strip()

    if git("rev-parse", "HEAD") != source_revision:
        raise ReleaseError("checkout HEAD differs from --source-revision")
    git("ls-files", "--error-unmatch", "--", *paths)
    if git("status", "--porcelain", "--", *paths):
        raise ReleaseError("selected publication inputs or publisher are not clean")


def verify_remote(
    api: HfApi, repo_id: str, revision: str, payloads: list[Payload]
) -> list[dict[str, object]]:
    from huggingface_hub.hf_api import RepoFile

    infos = api.get_paths_info(
        repo_id=repo_id,
        paths=[p.path_in_repo for p in payloads],
        revision=revision,
        repo_type="dataset",
    )
    by_path = {info.path: info for info in infos if isinstance(info, RepoFile)}
    if len(by_path) != len(payloads) or len(infos) != len(payloads):
        raise ReleaseError("Hub read-back is missing or duplicates a selected file")
    results: list[dict[str, object]] = []
    for payload in payloads:
        info = by_path.get(payload.path_in_repo)
        if info is None or info.size != payload.size_bytes:
            raise ReleaseError("Hub read-back size mismatch")
        if info.lfs is not None:
            if info.lfs.size != payload.size_bytes or info.lfs.sha256 != payload.sha256:
                raise ReleaseError("Hub LFS SHA-256 mismatch")
            method, observed = "lfs_sha256", info.lfs.sha256
        elif payload.git_blob_sha1 is not None:
            if info.blob_id != payload.git_blob_sha1:
                raise ReleaseError("Hub Git blob hash mismatch")
            method, observed = "git_blob_sha1", info.blob_id
        else:
            raise ReleaseError("large Hub object lacks verifiable LFS SHA-256 metadata")
        results.append(
            {
                "path_in_repo": payload.path_in_repo,
                "size_bytes": info.size,
                "local_sha256": payload.sha256,
                "verification_method": method,
                "observed_hash": observed,
                "status": "verified",
            }
        )
    return results


def publish(
    api: HfApi, manifest: Manifest, payloads: list[Payload], receipt: dict[str, object]
) -> None:
    from huggingface_hub import CommitOperationAdd
    from huggingface_hub.errors import RepositoryNotFoundError

    repo_id = manifest["repo_id"]
    try:
        info = api.repo_info(repo_id, repo_type="dataset")
    except RepositoryNotFoundError as exc:
        if exc.response.status_code != 404:
            raise
        api.create_repo(repo_id, repo_type="dataset", private=False, exist_ok=False)
        info = api.repo_info(repo_id, repo_type="dataset")
    if info.private is not False:
        raise ReleaseError("existing Hub target is private; visibility will not be changed")
    if not isinstance(info.sha, str) or not re.fullmatch(r"[0-9a-f]{40}", info.sha):
        raise ReleaseError("Hub target has no observable parent commit")
    receipt["hub_parent_commit"] = info.sha
    operations = [
        CommitOperationAdd(path_in_repo=p.path_in_repo, path_or_fileobj=p.content) for p in payloads
    ]
    # The official client rehashes file inputs before upload. Check its view too.
    for payload, operation in zip(payloads, operations, strict=True):
        if (
            operation.upload_info.size != payload.size_bytes
            or operation.upload_info.sha256.hex() != payload.sha256
        ):
            raise ReleaseError("publication input changed after validation")
    commit = api.create_commit(
        repo_id=repo_id,
        repo_type="dataset",
        revision="main",
        operations=operations,
        parent_commit=info.sha,
        commit_message=f"Publish source-bound atlas release {manifest['release_id']}",
        num_threads=2,
    )
    receipt["hub_commit"] = commit.oid
    receipt["hub_commit_url"] = commit.commit_url
    receipt["remote_objects"] = verify_remote(api, repo_id, commit.oid, payloads)
    receipt["status"] = "published_verified"


def write_receipt(path: Path, receipt: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ReleaseError("receipt path must not be a symlink")
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--source-revision")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--fetch-sources", action="store_true")
    args = parser.parse_args(namespace=Arguments())
    started = time.monotonic()
    receipt: dict[str, object] = {
        "schema_version": 1,
        "mode": "upload" if args.upload else "dry_run",
        "status": "started",
        "started_at": datetime.now(UTC).isoformat(),
        "source_repository": REPOSITORY,
        "source_revision": args.source_revision,
    }
    receipt_safe = False
    try:
        manifest_path = local_path(args.manifest.absolute().parent, args.manifest.name)
        receipt_path = local_path(args.receipt.absolute().parent, args.receipt.name)
        protected = {
            manifest_path.resolve(),
            *(
                Path(__file__).resolve().parent / name
                for name in ("publisher.py", "pyproject.toml", "uv.lock")
            ),
        }
        if receipt_path.resolve() in protected:
            raise ReleaseError("receipt would overwrite a publication input")
        manifest_bytes = manifest_path.read_bytes()
        manifest = read_manifest(manifest_bytes)
        protected.update(
            local_path(
                args.root if obj["kind"] == "metadata" else args.data_root,
                obj["source_path"] if obj["kind"] == "metadata" else obj["cache_path"],
            ).resolve()
            for obj in manifest["objects"]
        )
        if receipt_path.resolve() in protected:
            raise ReleaseError("receipt would overwrite a publication input")
        # Validation must identify every selected input before a failure receipt is safe.
        receipt_safe = True
        receipt.update(
            {
                "repo_id": manifest["repo_id"],
                "release_id": manifest["release_id"],
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            }
        )
        if args.upload:
            assert_source_checkout(args.root, args.manifest, manifest, args.source_revision)
        payloads = prepare(
            manifest,
            manifest_bytes,
            args.root,
            args.data_root,
            args.fetch_sources,
            args.source_revision,
        )
        receipt["local_objects"] = [
            {
                "path_in_repo": p.path_in_repo,
                "size_bytes": p.size_bytes,
                "sha256": p.sha256,
                "status": "verified",
            }
            for p in payloads
        ]
        receipt["status"] = "dry_run_verified"
        if args.upload:
            from huggingface_hub import HfApi

            publish(HfApi(), manifest, payloads, receipt)
        result = 0
    except Exception as exc:
        receipt["status"] = "failed"
        # Do not serialize arbitrary SDK/HTTP exceptions, which could include request details.
        failure: dict[str, object] = {
            "type": type(exc).__name__,
            "message": str(exc)
            if isinstance(exc, ReleaseError)
            else "operation failed; exception details withheld from public receipt",
        }
        receipt["failure"] = failure
        response = getattr(exc, "response", None)
        status_code: object = getattr(response, "status_code", None)
        if isinstance(status_code, int):
            failure["http_status"] = status_code
        result = 1
    receipt["completed_at"] = datetime.now(UTC).isoformat()
    receipt["elapsed_seconds"] = time.monotonic() - started
    receipt["python_version"] = sys.version.split()[0]
    if receipt_safe:
        write_receipt(args.receipt, receipt)
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "verified_local_objects": len(cast(list[object], receipt.get("local_objects", []))),
                "verified_remote_objects": len(
                    cast(list[object], receipt.get("remote_objects", []))
                ),
            }
        )
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
