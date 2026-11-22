"""Keep operational-code trust separate from the historical publication source."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / "research/releases/2026-11-22/hub-staging/verify-metadata.py"
SPEC = importlib.util.spec_from_file_location("verifier_pin_fixture", HELPER)
assert SPEC is not None and SPEC.loader is not None
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class PublisherPins(unittest.TestCase):
    def test_current_reviewed_implementation_loads(self):
        with patch.dict(sys.modules):
            publisher = VERIFIER.load_reviewed_publisher(ROOT)
        self.assertEqual(Path(publisher.__file__), ROOT / "tools/hf-release/publisher.py")

    def test_changed_current_publisher_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            publisher = root / "tools/hf-release/publisher.py"
            publisher.parent.mkdir(parents=True)
            marker = root / "unreviewed-code-executed"
            publisher.write_text(
                "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n"
            )
            with self.assertRaisesRegex(ValueError, "reviewed implementation"):
                VERIFIER.load_reviewed_publisher(root)
            self.assertFalse(marker.exists())

    def test_historical_pin_requires_original_bytes_and_exact_revision(self):
        baseline = "a" * 40
        original = b"synthetic original reviewed implementation\n"
        original_hash = hashlib.sha256(original).hexdigest()
        with (
            patch.object(VERIFIER, "BASELINE_PUBLISHER_SHA256", original_hash),
            patch.object(VERIFIER.subprocess, "check_output", return_value=original) as git,
        ):
            VERIFIER.verify_baseline_publisher(ROOT, baseline)
            git.assert_called_once_with(
                ["git", "-C", str(ROOT), "show", f"{baseline}:tools/hf-release/publisher.py"]
            )
            # A later implementation cannot stand in for the historical publisher.
            git.return_value = (ROOT / "tools/hf-release/publisher.py").read_bytes()
            with self.assertRaisesRegex(ValueError, "historical publisher"):
                VERIFIER.verify_baseline_publisher(ROOT, baseline)

    def test_unavailable_module_loader_never_executes_reviewed_source(self):
        for module_spec in (None, type("MissingLoader", (), {"loader": None})()):
            with (
                self.subTest(spec=module_spec),
                patch.object(
                    VERIFIER.importlib.util, "spec_from_file_location", return_value=module_spec
                ),
            ):
                with self.assertRaisesRegex(ValueError, "cannot be loaded"):
                    VERIFIER.load_reviewed_publisher(ROOT)


if __name__ == "__main__":
    unittest.main()
