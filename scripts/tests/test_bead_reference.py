"""Bounded regressions for the portable independent IDAT bead-reference replay."""

import csv
import gzip
import io
import json
import struct
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_beads


def complete_idat():
    count = 622399
    address_offset = 50
    bead_offset = address_offset + 4 * count
    return (
        b"IDAT"
        + struct.pack("<qi", 3, 3)
        + struct.pack("<HqHqHq", 1000, 46, 102, address_offset, 107, bead_offset)
        + struct.pack("<i", count)
        + struct.pack(f"<{count}I", *range(1, count + 1))
        + b"\x00\xff"
        + b"\x03" * (count - 2)
    )


class BeadReference(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def invoke(self, output):
        with (
            patch.object(
                sys,
                "argv",
                [
                    "check_beads.py",
                    "--data-root",
                    str(self.root / "data"),
                    "--reference-zero",
                    str(self.root / "zero"),
                    "--reference-three",
                    str(self.root / "three"),
                    "--output",
                    str(output),
                ],
            ),
            redirect_stdout(io.StringIO()),
        ):
            return check_beads.main()

    def test_field107_preserves_complete_addresses_and_uint8_values(self):
        path = self.root / "valid.idat"
        path.write_bytes(complete_idat())
        addresses, beads = check_beads.read_beads(path)
        self.assertEqual((len(addresses), addresses[0], addresses[-1]), (622399, 1, 622399))
        self.assertEqual(len(beads), 622399)
        self.assertEqual(beads[:3], b"\x00\xff\x03")

    def test_malformed_truncated_or_duplicate_idat_fields_fail(self):
        valid = complete_idat()
        cases = {"header": b"not IDAT", "directory": valid[:35], "beads": valid[:-1]}
        for name, offset, fmt, value in (
            ("duplicate_field", 26, "<H", 1000),
            ("directory_offset", 18, "<q", 16),
            ("missing_field107", 36, "<H", 999),
            ("incomplete_universe", 46, "<i", 622398),
            ("zero_address", 50, "<I", 0),
            ("duplicate_address", 54, "<I", 1),
        ):
            changed = bytearray(valid)
            struct.pack_into(fmt, changed, offset, value)
            cases[name] = changed
        for name, payload in cases.items():
            with self.subTest(case=name):
                path = self.root / (name + ".idat")
                path.write_bytes(payload)
                with self.assertRaises(ValueError):
                    check_beads.read_beads(path)

    def test_invalid_input_records_failure_and_produces_no_mask(self):
        output = self.root / "failed"
        self.assertEqual(self.invoke(output), 1)
        receipt = json.loads((output / "bead-verification.json").read_text())
        self.assertEqual(receipt["status"], "failed")
        self.assertIn("FileNotFoundError", receipt["error"])
        self.assertFalse((output / "independent-bead3-mask.u8").exists())
        self.assertIs(receipt["scientific_admitted"], False)

    def test_stream_errors_replace_running_receipt_with_failed(self):
        for number, error in enumerate((EOFError("truncated gzip"), csv.Error("malformed table"))):
            with self.subTest(error=type(error).__name__):
                output = self.root / str(number)

                def fail(*_args, output=output, error=error):
                    self.assertEqual(
                        json.loads((output / "bead-verification.json").read_text())["status"],
                        "running",
                    )
                    raise error

                with patch.object(check_beads, "verify", side_effect=fail):
                    self.assertEqual(self.invoke(output), 1)
                receipt = json.loads((output / "bead-verification.json").read_text())
                self.assertEqual(receipt["status"], "failed")
                self.assertIn(type(error).__name__, receipt["error"])

    def test_existing_output_cannot_overwrite_or_reuse_a_passed_receipt(self):
        output = self.root / "existing"
        output.mkdir()
        path = output / "bead-verification.json"
        path.write_text('{"status":"passed","script_sha256":"old"}')
        original = path.read_bytes()
        with patch.object(check_beads, "verify") as verify, self.assertRaises(FileExistsError):
            self.invoke(output)
        verify.assert_not_called()
        self.assertEqual(path.read_bytes(), original)

    def test_malformed_compressed_ordering_records_failure_without_a_mask(self):
        reference = self.root / "three"
        reference.mkdir()
        (reference / "original-address-ids.txt").write_text("1\n2\n")
        for color in ("green", "red"):
            (reference / f"original-{color}-beads.u8").write_bytes(b"\x03\x03")
        ordering = self.root / "data/assets/HM450/HM450.ordering.tsv.gz"
        ordering.parent.mkdir(parents=True)
        header = b"Probe_ID\tM\tU\tcol\n"
        invalid_deflate = bytearray(gzip.compress(header))
        invalid_deflate[10] = 7
        for name, data, error in (
            ("deflate", invalid_deflate, "error:"),
            ("csv", gzip.compress(header + b'"unterminated'), "Error:"),
        ):
            with self.subTest(name=name):
                ordering.write_bytes(data)
                output = self.root / name
                with patch.object(check_beads, "read_beads", return_value=((1, 2), b"\x03\x03")):
                    self.assertEqual(self.invoke(output), 1)
                receipt = json.loads((output / "bead-verification.json").read_text())
                self.assertEqual(receipt["status"], "failed")
                self.assertTrue(receipt["error"].startswith(error))
                self.assertFalse((output / "independent-bead3-mask.u8").exists())


if __name__ == "__main__":
    unittest.main()
