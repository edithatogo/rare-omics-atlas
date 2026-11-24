import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "publisher", Path(__file__).parents[1] / "publisher.py"
)
publisher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = publisher
spec.loader.exec_module(publisher)


class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "note.txt").write_bytes(b"metadata\n")
        self.row = {
            "path_in_repo": "silver/metadata/note.txt",
            "kind": "metadata",
            "source_path": "note.txt",
            "size_bytes": 9,
            "sha256": hashlib.sha256(b"metadata\n").hexdigest(),
            "redistribution_basis": "Original project metadata",
        }
        self.manifest = {
            "schema_version": 1,
            "repo_id": "edithatogo/rare-omics-atlas",
            "release_id": "2026-11-22",
            "objects": [self.row],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_rejects_duplicate_destinations(self):
        self.manifest["objects"].append(dict(self.row))
        with self.assertRaises(publisher.ReleaseError):
            publisher.validate_manifest(self.manifest)

    def test_rejects_untyped_manifest_and_invalid_object_contracts(self):
        invalid_manifests = [None, [], {**self.manifest, "schema_version": 2}]
        for fields in ({"objects": []}, {"repo_id": "other/repository"}):
            invalid_manifests.append({**self.manifest, **fields})
        for fields in (
            {"size_bytes": True},
            {"size_bytes": -1},
            {"sha256": "unverified"},
            {"redistribution_basis": " "},
            {"kind": "unknown"},
        ):
            candidate = copy.deepcopy(self.manifest)
            candidate["objects"][0].update(fields)
            invalid_manifests.append(candidate)
        invalid_manifests.append({**self.manifest, "objects": [None]})
        for manifest in invalid_manifests:
            with self.subTest(manifest=manifest), self.assertRaises(publisher.ReleaseError):
                publisher.validate_manifest(manifest)

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
        for url in [
            "http://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
            "https://example.org/GSE97362_RAW.tar",
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar?token=x",
            "https://ftp.ncbi.nlm.nih.gov@evil.example/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
        ]:
            with self.subTest(url=url), self.assertRaises(publisher.ReleaseError):
                publisher.validate_source_url(url, "GSE97362")

    def test_accepts_only_expected_geo_archive(self):
        publisher.validate_source_url(
            "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
            "GSE97362",
        )
        with self.assertRaises(publisher.ReleaseError):
            publisher.validate_source_url(
                "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
                "GSE116300",
            )

    def test_dry_run_generates_exact_manifest_and_deterministic_provenance(self):
        body = json.dumps(self.manifest).encode()
        payloads = publisher.prepare(self.manifest, body, self.root, self.root, False, None)
        self.assertEqual(len(payloads), 3)
        self.assertEqual(payloads[-2].content, body)
        self.assertEqual(
            payloads[-1].content,
            publisher.prepare(self.manifest, body, self.root, self.root, False, None)[-1].content,
        )
        self.assertEqual(
            payloads[0].git_blob_sha1,
            hashlib.sha1(b"blob 9\0metadata\n", usedforsecurity=False).hexdigest(),
        )


class HubContracts(unittest.TestCase):
    setUp = Contracts.setUp
    tearDown = Contracts.tearDown

    def payloads(self):
        return publisher.prepare(
            self.manifest, json.dumps(self.manifest).encode(), self.root, self.root, False, "a" * 40
        )

    def fake_api(self, payloads, private=False, corrupt=False):
        from types import SimpleNamespace

        from huggingface_hub.hf_api import RepoFile

        class Api:
            calls = []

            def repo_info(inner, *args, **kwargs):
                return SimpleNamespace(private=private, sha="1" * 40)

            def create_commit(inner, **kwargs):
                inner.calls.append(kwargs)
                return SimpleNamespace(
                    oid="2" * 40,
                    commit_url="https://huggingface.co/datasets/edithatogo/rare-omics-atlas/commit/"
                    + "2" * 40,
                )

            def get_paths_info(inner, **kwargs):
                self.assertEqual(kwargs["revision"], "2" * 40)
                return [
                    RepoFile(
                        path=p.path_in_repo,
                        size=p.size_bytes,
                        oid="0" * 40 if corrupt else p.git_blob_sha1,
                    )
                    for p in payloads
                ]

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
        self.assertEqual(
            [o.path_in_repo for o in api.calls[0]["operations"]], [p.path_in_repo for p in payloads]
        )
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
        info = RepoFile(
            path=payload.path_in_repo,
            size=payload.size_bytes,
            oid=payload.git_blob_sha1,
            lfs={"size": payload.size_bytes, "oid": "0" * 64, "pointerSize": 100},
        )
        api = SimpleNamespace(get_paths_info=lambda **kwargs: [info])
        with self.assertRaises(publisher.ReleaseError):
            publisher.verify_remote(api, publisher.HUB_REPOSITORY, "2" * 40, [payload])

    def test_failed_download_removes_only_its_partial(self):
        from io import BytesIO
        from types import SimpleNamespace
        from unittest.mock import patch

        obj = {
            **self.row,
            "kind": "source_archive",
            "accession": "GSE97362",
            "source_url": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
        }
        response = BytesIO(b"badbytes\n")
        response.status = 200
        destination = self.root / "GSE97362_RAW.tar"
        with (
            patch.object(
                publisher,
                "build_opener",
                return_value=SimpleNamespace(open=lambda *a, **k: response),
            ),
            self.assertRaises(publisher.ReleaseError),
        ):
            publisher.fetch_archive(destination, obj)
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_name(destination.name + ".part").exists())

    def test_existing_bad_file_is_not_overwritten(self):
        from unittest.mock import patch

        destination = self.root / "GSE97362_RAW.tar"
        destination.write_bytes(b"badbytes\n")
        obj = {
            **self.row,
            "kind": "source_archive",
            "accession": "GSE97362",
            "source_url": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
        }
        with (
            patch.object(publisher, "build_opener") as opener,
            self.assertRaises(publisher.ReleaseError),
        ):
            publisher.fetch_archive(destination, obj)
        opener.assert_not_called()
        self.assertEqual(destination.read_bytes(), b"badbytes\n")

    def test_source_archive_preparation_preserves_bytes_and_uses_explicit_cache(self):
        from io import BytesIO
        from types import SimpleNamespace
        from unittest.mock import patch

        cache = self.root / "bronze"
        original = b"synthetic archive bytes\n"
        archive = {
            "kind": "source_archive",
            "path_in_repo": "bronze/GSE97362_RAW.tar",
            "cache_path": "GSE97362_RAW.tar",
            "accession": "GSE97362",
            "source_url": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar",
            "size_bytes": len(original),
            "sha256": hashlib.sha256(original).hexdigest(),
            "redistribution_basis": "Synthetic fixture bytes only",
        }
        manifest = {**self.manifest, "objects": [archive]}
        response = BytesIO(original)
        response.status = 200
        with patch.object(
            publisher,
            "build_opener",
            return_value=SimpleNamespace(open=lambda *args, **kwargs: response),
        ) as opener:
            first = publisher.prepare(
                manifest, json.dumps(manifest).encode(), self.root, cache, True, None
            )
            self.assertEqual((cache / archive["cache_path"]).read_bytes(), original)
            self.assertFalse((self.root / archive["cache_path"]).exists())
            self.assertFalse((cache / (archive["cache_path"] + ".part")).exists())
            opener.assert_called_once()
            opener.reset_mock()
            replay = publisher.prepare(
                manifest, json.dumps(manifest).encode(), self.root, cache, False, None
            )
            self.assertEqual(first, replay)
            opener.assert_not_called()

    def test_changed_input_between_validation_and_commit_is_rejected(self):
        payloads = self.payloads()
        api = self.fake_api(payloads)
        (self.root / "note.txt").write_bytes(b"changed!\n")
        with self.assertRaisesRegex(publisher.ReleaseError, "changed after validation"):
            publisher.publish(api, self.manifest, payloads, {})
        self.assertEqual(api.calls, [])


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
            manifest = {"objects": [{"kind": "metadata", "source_path": "metadata.txt"}]}
            manifest_path.write_text(json.dumps(manifest))

            def git(*args):
                return subprocess.check_output(
                    ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL, text=True
                ).strip()

            git("init")
            git("add", ".")
            git(
                "-c",
                "user.name=Publisher fixture",
                "-c",
                "user.email=fixture@example.org",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "-m",
                "fixture",
            )
            revision = git("rev-parse", "HEAD")
            with patch.object(publisher, "__file__", str(folder / "publisher.py")):
                publisher.assert_source_checkout(root, manifest_path, manifest, revision)
                with self.assertRaises(publisher.ReleaseError):
                    publisher.assert_source_checkout(root, manifest_path, manifest, "0" * 40)
                (root / "metadata.txt").write_text("changed\n")
                with self.assertRaises(publisher.ReleaseError):
                    publisher.assert_source_checkout(root, manifest_path, manifest, revision)


class MetadataVerifierReceiptContract(unittest.TestCase):
    def test_invalid_revision_cannot_overwrite_inputs_or_follow_symlinks(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch

        real_root = Path(__file__).resolve().parents[3]
        helper_relative = Path("research/releases/2026-11-22/hub-staging/verify-metadata.py")
        helper_bytes = (real_root / helper_relative).read_bytes()
        publisher_bytes = (real_root / "tools/hf-release/publisher.py").read_bytes()
        cases = (
            "source",
            "staging_manifest",
            "full_manifest",
            "helper",
            "publisher",
            "pyproject",
            "lockfile",
            "receipt_symlink",
            "receipt_parent_symlink",
            "source_symlink",
            "publisher_symlink",
            "publisher_modified",
            "malformed_manifest",
            "safe_output",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "checkout"
                helper = root / helper_relative
                helper.parent.mkdir(parents=True)
                helper.write_bytes(helper_bytes)
                tool = root / "tools/hf-release"
                tool.mkdir(parents=True)
                (tool / "publisher.py").write_bytes(publisher_bytes)
                (tool / "pyproject.toml").write_text("tooling sentinel\n")
                (tool / "uv.lock").write_text("lock sentinel\n")
                source = root / "source.txt"
                source.write_text("selected input sentinel\n")
                staging = helper.parent / "staging-publication-manifest.json"
                staging.write_text(json.dumps({"objects": [{"source_path": "source.txt"}]}))
                full = helper.parent.parent / "manifest.json"
                full.write_text("full manifest sentinel\n")
                protected = {
                    "source": source,
                    "staging_manifest": staging,
                    "full_manifest": full,
                    "helper": helper,
                    "publisher": tool / "publisher.py",
                    "pyproject": tool / "pyproject.toml",
                    "lockfile": tool / "uv.lock",
                }
                output = Path(temporary) / "reports/failure.json"
                marker = Path(temporary) / "unreviewed-module-executed"
                if case == "receipt_symlink":
                    output = root / "receipt-alias.json"
                    output.symlink_to(source)
                elif case == "receipt_parent_symlink":
                    alias = root / "receipt-parent"
                    alias.symlink_to(root, target_is_directory=True)
                    output = alias / "source.txt"
                elif case in ("source_symlink", "publisher_symlink"):
                    selected = source if case == "source_symlink" else tool / "publisher.py"
                    outside = Path(temporary) / "outside-sentinel"
                    outside.write_bytes(selected.read_bytes())
                    selected.unlink()
                    selected.symlink_to(outside)
                elif case == "publisher_modified":
                    (tool / "publisher.py").write_text(
                        "from pathlib import Path\nPath("
                        + repr(str(marker))
                        + ").write_text('executed')\n"
                    )
                elif case == "malformed_manifest":
                    staging.write_text('{"source_sentinel":true}\n')
                    output = staging
                elif case != "safe_output":
                    output = protected[case]
                before = {path: path.read_bytes() for path in protected.values()}
                links = {path: path.is_symlink() for path in protected.values()}
                module_spec = importlib.util.spec_from_file_location(
                    "metadata_verifier_fixture", helper
                )
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                argv = [
                    str(helper),
                    "--root",
                    str(root),
                    "--hub-revision",
                    "invalid",
                    "--receipt",
                    str(output),
                ]
                with (
                    patch.object(sys, "argv", argv),
                    patch.dict(sys.modules, {"publisher": publisher}),
                    patch.object(module, "HfApi") as api,
                    redirect_stdout(StringIO()),
                ):
                    self.assertEqual(module.main(), 1)
                api.assert_not_called()
                for path, original in before.items():
                    self.assertEqual(path.read_bytes(), original)
                    self.assertEqual(path.is_symlink(), links[path])
                if case == "safe_output":
                    self.assertEqual(
                        json.loads(output.read_text())["status"], "verification_failed"
                    )
                elif case in ("source_symlink", "publisher_symlink", "publisher_modified"):
                    self.assertFalse(output.exists())
                self.assertFalse(marker.exists())
                if case == "receipt_symlink":
                    self.assertTrue(output.is_symlink())


if __name__ == "__main__":
    unittest.main()
