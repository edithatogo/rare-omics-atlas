import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("publisher", Path(__file__).parents[1] / "publisher.py")
publisher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = publisher
spec.loader.exec_module(publisher)


class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "note.txt").write_bytes(b"metadata\n")
        self.row = {"path_in_repo": "silver/metadata/note.txt", "kind": "metadata", "source_path": "note.txt", "size_bytes": 9, "sha256": hashlib.sha256(b"metadata\n").hexdigest(), "redistribution_basis": "Original project metadata"}
        self.manifest = {"schema_version": 1, "repo_id": "edithatogo/rare-omics-atlas", "release_id": "2026-11-22", "objects": [self.row]}

    def tearDown(self):
        self.temp.cleanup()

    def test_rejects_duplicate_destinations(self):
        self.manifest["objects"].append(dict(self.row))
        with self.assertRaises(publisher.ReleaseError):
            publisher.validate_manifest(self.manifest)

    def test_rejects_auto_generated_path_collision(self):
        self.row["path_in_repo"] = "releases/2026-11-22/provenance.json"
        with self.assertRaises(publisher.ReleaseError):
            publisher.validate_manifest(self.manifest)

    def test_rejects_path_escape_and_aliases(self):
        for path in ["../secrets", "/tmp/file", "a/../file", "a//file", "C:/file", r"a\file", "."]:
            with self.subTest(path=path), self.assertRaises(publisher.ReleaseError):
                publisher.relative_path(path)

    def test_rejects_symlink_source(self):
        (self.root / "alias.txt").symlink_to(self.root / "note.txt")
        with self.assertRaises(publisher.ReleaseError):
            publisher.local_path(self.root, "alias.txt")

    def test_rejects_wrong_hash_and_size(self):
        for changes in [{"sha256": "0" * 64}, {"size_bytes": 8}]:
            with self.subTest(changes=changes), self.assertRaises(publisher.ReleaseError):
                publisher.verify_file(self.root / "note.txt", {**self.row, **changes})

    def test_rejects_unsupported_source_or_query(self):
        for url in ["http://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar", "https://example.org/GSE97362_RAW.tar", "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar?token=x", "https://ftp.ncbi.nlm.nih.gov@evil.example/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar"]:
            with self.subTest(url=url), self.assertRaises(publisher.ReleaseError):
                publisher.validate_source_url(url, "GSE97362")

    def test_accepts_only_expected_geo_archive(self):
        publisher.validate_source_url("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar", "GSE97362")
        with self.assertRaises(publisher.ReleaseError):
            publisher.validate_source_url("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar", "GSE116300")

    def test_dry_run_generates_exact_manifest_and_deterministic_provenance(self):
        body = json.dumps(self.manifest).encode()
        payloads = publisher.prepare(self.manifest, body, self.root, self.root, False, None)
        self.assertEqual(len(payloads), 3)
        self.assertEqual(payloads[-2].content, body)
        self.assertEqual(payloads[-1].content, publisher.prepare(self.manifest, body, self.root, self.root, False, None)[-1].content)
        self.assertEqual(payloads[0].git_blob_sha1, hashlib.sha1(b"blob 9\0metadata\n", usedforsecurity=False).hexdigest())


class HubContracts(unittest.TestCase):
    setUp = Contracts.setUp
    tearDown = Contracts.tearDown

    def payloads(self):
        return publisher.prepare(self.manifest, json.dumps(self.manifest).encode(), self.root, self.root, False, "a" * 40)

    def fake_api(self, payloads, private=False, corrupt=False):
        from types import SimpleNamespace
        from huggingface_hub.hf_api import RepoFile
        class Api:
            calls = []
            def repo_info(inner, *args, **kwargs):
                return SimpleNamespace(private=private, sha="1" * 40)
            def create_commit(inner, **kwargs):
                inner.calls.append(kwargs)
                return SimpleNamespace(oid="2" * 40, commit_url="https://huggingface.co/datasets/edithatogo/rare-omics-atlas/commit/" + "2" * 40)
            def get_paths_info(inner, **kwargs):
                self.assertEqual(kwargs["revision"], "2" * 40)
                return [RepoFile(path=p.path_in_repo, size=p.size_bytes, oid="0" * 40 if corrupt else p.git_blob_sha1) for p in payloads]
        return Api()

    def test_private_target_is_never_changed(self):
        payloads = self.payloads()
        api = self.fake_api(payloads, private=True)
        with self.assertRaises(publisher.ReleaseError):
            publisher.publish(api, self.manifest, payloads, {})
        self.assertEqual(api.calls, [])

    def test_commit_is_parent_guarded_and_pinned_readback_is_verified(self):
        payloads = self.payloads()
        api = self.fake_api(payloads)
        receipt = {}
        publisher.publish(api, self.manifest, payloads, receipt)
        self.assertEqual(receipt["status"], "published_verified")
        self.assertEqual(api.calls[0]["parent_commit"], "1" * 40)
        self.assertEqual(api.calls[0]["revision"], "main")
        self.assertEqual([o.path_in_repo for o in api.calls[0]["operations"]], [p.path_in_repo for p in payloads])
        self.assertEqual(len(receipt["remote_objects"]), 3)

    def test_failed_postcheck_retains_observed_commit(self):
        payloads = self.payloads()
        api = self.fake_api(payloads, corrupt=True)
        receipt = {}
        with self.assertRaises(publisher.ReleaseError):
            publisher.publish(api, self.manifest, payloads, receipt)
        self.assertEqual(receipt["hub_commit"], "2" * 40)
        self.assertNotEqual(receipt.get("status"), "published_verified")

    def test_bad_lfs_hash_cannot_fall_back_to_git_blob(self):
        from types import SimpleNamespace
        from huggingface_hub.hf_api import RepoFile
        payload = self.payloads()[0]
        info = RepoFile(path=payload.path_in_repo, size=payload.size_bytes, oid=payload.git_blob_sha1, lfs={"size":payload.size_bytes,"oid":"0"*64,"pointerSize":100})
        api = SimpleNamespace(get_paths_info=lambda **kwargs: [info])
        with self.assertRaises(publisher.ReleaseError):
            publisher.verify_remote(api, publisher.HUB_REPOSITORY, "2" * 40, [payload])

    def test_failed_download_removes_only_its_partial(self):
        from io import BytesIO
        from types import SimpleNamespace
        from unittest.mock import patch
        obj = {**self.row, "kind":"source_archive", "accession":"GSE97362", "source_url":"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar"}
        response = BytesIO(b"badbytes\n")
        response.status = 200
        destination = self.root / "GSE97362_RAW.tar"
        with patch.object(publisher, "build_opener", return_value=SimpleNamespace(open=lambda *a,**k:response)), self.assertRaises(publisher.ReleaseError):
            publisher.fetch_archive(destination, obj)
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_name(destination.name + ".part").exists())

    def test_existing_bad_file_is_not_overwritten(self):
        from unittest.mock import patch
        destination = self.root / "GSE97362_RAW.tar"
        destination.write_bytes(b"badbytes\n")
        obj = {**self.row, "kind":"source_archive", "accession":"GSE97362", "source_url":"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar"}
        with patch.object(publisher,"build_opener") as opener, self.assertRaises(publisher.ReleaseError):
            publisher.fetch_archive(destination,obj)
        opener.assert_not_called()
        self.assertEqual(destination.read_bytes(),b"badbytes\n")


class GitSourceContracts(unittest.TestCase):
    def test_upload_requires_matching_clean_tracked_source(self):
        import subprocess
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "tools/hf-release"
            folder.mkdir(parents=True)
            for name in ("publisher.py", "pyproject.toml", "uv.lock"):
                (folder / name).write_text("fixture\n")
            (root / "metadata.txt").write_text("metadata\n")
            manifest_path = root / "manifest.json"
            manifest = {"objects":[{"kind":"metadata","source_path":"metadata.txt"}]}
            manifest_path.write_text(json.dumps(manifest))
            def git(*args):
                return subprocess.check_output(["git","-C",str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()
            git("init")
            git("add", ".")
            git("-c","user.name=Publisher fixture","-c","user.email=fixture@example.org","-c","commit.gpgsign=false","commit","-m","fixture")
            revision = git("rev-parse","HEAD")
            with patch.object(publisher,"__file__",str(folder/"publisher.py")):
                publisher.assert_source_checkout(root,manifest_path,manifest,revision)
                with self.assertRaises(publisher.ReleaseError):
                    publisher.assert_source_checkout(root,manifest_path,manifest,"0"*40)
                (root/"metadata.txt").write_text("changed\n")
                with self.assertRaises(publisher.ReleaseError):
                    publisher.assert_source_checkout(root,manifest_path,manifest,revision)


if __name__ == "__main__":
    unittest.main()
