"""Exercise the full immutable-source to Hub read-back contract without networking."""

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from huggingface_hub.hf_api import RepoFile

ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = ROOT / "research/releases/2026-11-22/hub-staging/verify-metadata.py"
STAGING = "research/releases/2026-11-22/hub-staging/staging-publication-manifest.json"
HUB_SHA = "c" * 40
SPEC = importlib.util.spec_from_file_location("metadata_readback_fixture", HELPER_PATH)
assert SPEC is not None and SPEC.loader is not None
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


class MetadataReadbackContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "checkout"
        # A local clone preserves actual historical Git objects. No public source is changed.
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(self.root)],
            check=True,
        )
        self.publisher = (ROOT / "tools/hf-release/publisher.py").read_bytes()
        (self.root / "tools/hf-release/publisher.py").write_bytes(self.publisher)
        self.manifest_path = self.root / STAGING
        self.manifest = json.loads(self.manifest_path.read_text())
        self.output = Path(self.temporary.name).resolve() / "reports/receipt.json"
        # Independent expected blob identities come from the immutable staging manifest.
        self.remote = {
            obj["path_in_repo"]: RepoFile(
                path=obj["path_in_repo"], size=obj["size_bytes"], oid=obj["git_blob_sha1"]
            )
            for obj in self.manifest["objects"]
        }
        manifest_bytes = self.manifest_path.read_bytes()
        self.remote["releases/2026-11-22/staging-publication-manifest.json"] = RepoFile(
            path="releases/2026-11-22/staging-publication-manifest.json",
            size=len(manifest_bytes),
            oid=self.git_blob(manifest_bytes),
        )
        self.private = False
        self.observed_sha = HUB_SHA
        self.raw_objects = []
        self.client_called = False

    @staticmethod
    def git_blob(content):
        return (
            subprocess.check_output(["git", "hash-object", "--stdin"], input=content)
            .decode()
            .strip()
        )

    def save_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest))

    def first_baseline_object(self):
        return next(
            obj
            for obj in self.manifest["objects"]
            if obj["origin"]["kind"] == "unchanged_github_blob"
        )

    def run_verifier(self, include_manifest=False, hub_revision=HUB_SHA):
        def repo_info(repo_id, *, repo_type, revision):
            self.assertEqual(
                (repo_id, repo_type, revision), (self.manifest["repo_id"], "dataset", HUB_SHA)
            )
            return SimpleNamespace(private=self.private, sha=self.observed_sha)

        def get_paths_info(*, repo_id, paths, repo_type, revision):
            self.assertEqual(
                (repo_id, repo_type, revision), (self.manifest["repo_id"], "dataset", HUB_SHA)
            )
            return [self.remote[path] for path in paths if path in self.remote]

        def list_repo_tree(repo_id, *, repo_type, revision, recursive):
            self.assertEqual(
                (repo_id, repo_type, revision), (self.manifest["repo_id"], "dataset", HUB_SHA)
            )
            self.assertTrue(recursive)
            return [*self.remote.values(), *self.raw_objects]

        api = SimpleNamespace(
            repo_info=repo_info, get_paths_info=get_paths_info, list_repo_tree=list_repo_tree
        )
        argv = [
            str(HELPER_PATH),
            "--root",
            str(self.root),
            "--hub-revision",
            hub_revision,
            "--receipt",
            str(self.output),
        ]
        if include_manifest:
            argv.append("--include-staging-manifest")
        with (
            patch.dict(sys.modules),
            patch.object(HELPER, "HfApi", return_value=api) as client,
            patch.object(sys, "argv", argv),
            redirect_stdout(StringIO()),
        ):
            code = HELPER.main()
            self.client_called = client.called
            if client.called:
                client.assert_called_once_with(token=False)
        receipt = json.loads(self.output.read_text()) if self.output.exists() else None
        return code, receipt

    def assert_failure(self, expected_message, *, before_api=False):
        code, receipt = self.run_verifier()
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "verification_failed")
        self.assertIn(expected_message, receipt["failure"]["message"])
        self.assertFalse(receipt["full_release_verified"])
        if before_api:
            self.assertFalse(self.client_called)

    def test_thirteen_real_metadata_objects_and_optional_manifest_verify(self):
        for include_manifest in (False, True):
            with self.subTest(include_manifest=include_manifest):
                code, receipt = self.run_verifier(include_manifest)
                self.assertEqual(code, 0)
                self.assertEqual(
                    receipt["status"], "metadata_subset_ui_published_api_verified_raw_pending"
                )
                self.assertEqual(len(receipt["remote_objects"]), 14 if include_manifest else 13)
                self.assertEqual(receipt["unchanged_baseline_files"], 10)
                self.assertEqual(receipt["new_notice_files"], 3)
                self.assertTrue(receipt["raw_archive_absence_checked"])
                self.assertFalse(receipt["full_release_verified"])
                self.assertEqual(
                    receipt["baseline_source_revision"], self.manifest["baseline_source_revision"]
                )
                self.assertEqual(
                    receipt["baseline_publisher_sha256"], HELPER.BASELINE_PUBLISHER_SHA256
                )
                self.assertEqual(
                    receipt["reviewed_publisher_sha256"], hashlib.sha256(self.publisher).hexdigest()
                )

    def test_modified_local_metadata_fails_before_remote_access(self):
        path = self.root / self.first_baseline_object()["source_path"]
        original = path.read_bytes()
        path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        self.assert_failure("hash/size mismatch", before_api=True)

    def test_rehashed_local_metadata_cannot_replace_immutable_git_source(self):
        obj = self.first_baseline_object()
        path = self.root / obj["source_path"]
        altered = path.read_bytes() + b"\nSynthetic unauthorised replacement\n"
        path.write_bytes(altered)
        obj["size_bytes"] = len(altered)
        obj["sha256"] = hashlib.sha256(altered).hexdigest()
        obj["git_blob_sha1"] = self.git_blob(altered)
        obj["origin"]["git_blob_sha1"] = obj["git_blob_sha1"]
        self.save_manifest()
        self.assert_failure("immutable Git origin", before_api=True)

    def test_different_historical_publisher_commit_is_rejected(self):
        path = self.root / "tools/hf-release/publisher.py"
        path.write_text("# Synthetic unreviewed historical publisher\n")
        subprocess.run(
            ["git", "-C", str(self.root), "add", "tools/hf-release/publisher.py"], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "-c",
                "user.name=Verification fixture",
                "-c",
                "user.email=fixture@example.org",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "--quiet",
                "-m",
                "Synthetic alternate historical source",
            ],
            check=True,
        )
        self.manifest["baseline_source_revision"] = subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True
        ).strip()
        path.write_bytes(self.publisher)
        self.save_manifest()
        self.assert_failure("historical publisher", before_api=True)

    def test_source_origin_revision_must_match_the_frozen_baseline(self):
        self.first_baseline_object()["origin"]["revision"] = "f" * 40
        self.save_manifest()
        self.assert_failure("baseline source revision mismatch", before_api=True)

    def test_reclassifying_a_baseline_source_as_a_notice_is_rejected(self):
        origin = self.first_baseline_object()["origin"]
        origin["kind"] = "new_staging_notice"
        origin["revision"] = None
        self.save_manifest()
        self.assert_failure("source-origin counts", before_api=True)

    def test_full_release_manifest_remains_content_bound(self):
        path = self.root / "research/releases/2026-11-22/manifest.json"
        path.write_bytes(path.read_bytes() + b"\n")
        self.assert_failure("planned full release manifest changed", before_api=True)

    def test_metadata_fields_require_declared_json_types(self):
        for function, invalid, message in (
            (HELPER.record, [], "metadata record expected"),
            (HELPER.record, {1: "value"}, "keys must be strings"),
            (HELPER.records, {}, "object list expected"),
            (HELPER.records, [None], "metadata record expected"),
            (HELPER.text, 123, "text field expected"),
        ):
            with self.subTest(function=function.__name__, value=invalid):
                with self.assertRaisesRegex(ValueError, message):
                    function(invalid)

    def test_subset_invariants_reject_invalid_claims_before_remote_access(self):
        original = json.dumps(self.manifest)
        for scenario, expected in (
            ("wrong_count", "unexpected metadata subset contract"),
            ("claimed_complete", "unexpected metadata subset contract"),
            ("raw_kind", "invalid or duplicate subset object"),
            ("duplicate", "invalid or duplicate subset object"),
            ("boolean_size", "invalid metadata object size"),
            ("negative_size", "invalid metadata object size"),
            ("notice_origin_claim", "unverified baseline origin"),
            ("unknown_origin", "unknown notice/source origin"),
        ):
            with self.subTest(scenario=scenario):
                self.manifest = json.loads(original)
                first = self.manifest["objects"][0]
                if scenario == "wrong_count":
                    self.manifest["objects"].pop()
                elif scenario == "claimed_complete":
                    self.manifest["full_release_status"] = "complete"
                elif scenario == "raw_kind":
                    first["kind"] = "source_archive"
                elif scenario == "duplicate":
                    self.manifest["objects"][1]["path_in_repo"] = first["path_in_repo"]
                elif scenario in ("boolean_size", "negative_size"):
                    first["size_bytes"] = True if scenario == "boolean_size" else -1
                elif scenario == "notice_origin_claim":
                    notice = next(
                        obj
                        for obj in self.manifest["objects"]
                        if obj["origin"]["kind"] == "new_staging_notice"
                    )
                    notice["origin"]["revision"] = "a" * 40
                else:
                    first["origin"]["kind"] = "unverified"
                self.save_manifest()
                self.output.unlink(missing_ok=True)
                self.assert_failure(expected, before_api=True)

    def test_mutable_hub_reference_and_unreviewed_client_are_rejected(self):
        code, receipt = self.run_verifier(hub_revision="main")
        self.assertEqual(code, 1)
        self.assertIn("immutable Hub SHA", receipt["failure"]["message"])
        self.assertFalse(self.client_called)
        self.output.unlink()
        with patch.object(HELPER.importlib.metadata, "version", return_value="2.4.1"):
            self.assert_failure("reviewed Hub client", before_api=True)

    def test_remote_readback_requires_public_exact_revision(self):
        for private, revision in ((True, HUB_SHA), (False, "d" * 40)):
            with self.subTest(private=private, revision=revision):
                self.private, self.observed_sha = private, revision
                self.assert_failure("public exact Hub revision")

    def test_missing_remote_object_is_not_a_verified_subset(self):
        self.remote.pop(self.manifest["objects"][0]["path_in_repo"])
        self.assert_failure("missing or duplicates")

    def test_wrong_remote_hash_is_not_a_verified_subset(self):
        obj = self.manifest["objects"][0]
        self.remote[obj["path_in_repo"]] = RepoFile(
            path=obj["path_in_repo"], size=obj["size_bytes"], oid="0" * 40
        )
        self.assert_failure("Hub Git blob hash mismatch")

    def test_remote_raw_archive_keeps_metadata_only_acceptance_closed(self):
        self.raw_objects = [RepoFile(path="bronze/unexpected_RAW.tar", size=1, oid="e" * 40)]
        self.assert_failure("raw object present")
        receipt = json.loads(self.output.read_text())
        self.assertEqual(receipt["raw_archive_paths_observed"], ["bronze/unexpected_RAW.tar"])
        self.assertEqual(len(receipt["remote_objects"]), 13)


if __name__ == "__main__":
    unittest.main()
