"""Failure reporting must never replace a publication input."""

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "publisher", Path(__file__).parents[1] / "publisher.py"
)
assert SPEC is not None and SPEC.loader is not None
PUBLISHER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PUBLISHER
SPEC.loader.exec_module(PUBLISHER)


class ReceiptInputProtection(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.txt"
        self.original = b"synthetic input sentinel\n"
        self.source.write_bytes(self.original)
        self.manifest_path = self.root / "manifest.json"
        self.manifest = {
            "schema_version": 1,
            "repo_id": PUBLISHER.HUB_REPOSITORY,
            "release_id": "fixture",
            "objects": [
                {
                    "kind": "metadata",
                    "path_in_repo": "silver/source.txt",
                    "source_path": "source.txt",
                    "size_bytes": len(self.original),
                    "sha256": hashlib.sha256(self.original).hexdigest(),
                    "redistribution_basis": "Synthetic fixture",
                }
            ],
        }

    def run_publisher(self, receipt):
        self.manifest_path.write_text(json.dumps(self.manifest))
        argv = [
            "publisher.py",
            "--manifest",
            str(self.manifest_path),
            "--root",
            str(self.root),
            "--data-root",
            str(self.root),
            "--receipt",
            str(receipt),
        ]
        with patch.object(sys, "argv", argv), redirect_stdout(StringIO()):
            return PUBLISHER.main()

    def test_invalid_manifest_cannot_overwrite_source_with_failure_receipt(self):
        self.manifest["objects"][0]["sha256"] = "invalid"
        self.assertEqual(self.run_publisher(self.source), 1)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_valid_manifest_cannot_overwrite_source_with_failure_receipt(self):
        self.assertEqual(self.run_publisher(self.source), 1)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_valid_dry_run_writes_safe_receipt_and_preserves_source(self):
        output = self.root / "reports/receipt.json"
        self.assertEqual(self.run_publisher(output), 0)
        receipt = json.loads(output.read_text())
        self.assertEqual(receipt["status"], "dry_run_verified")
        self.assertEqual(len(receipt["local_objects"]), 3)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_http_failure_retains_status_without_disclosing_exception_details(self):
        output = self.root / "reports/failure.json"
        failure = RuntimeError("synthetic confidential transport detail")
        failure.response = SimpleNamespace(status_code=503)
        with patch.object(PUBLISHER, "prepare", side_effect=failure):
            self.assertEqual(self.run_publisher(output), 1)
        receipt = json.loads(output.read_text())
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["failure"]["http_status"], 503)
        self.assertNotIn("confidential", output.read_text())
        self.assertEqual(self.source.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
