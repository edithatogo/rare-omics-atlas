from __future__ import annotations

import contextlib
import gzip
import io
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import patch

import compare_raw_q


class ReferenceReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.r_output = self.root / "r-output"
        self.r_output.mkdir()
        self.reference = self.root / "expected.tsv.gz"
        self.table = (
            "Probe_ID\tchannel\tM_signal\tU_signal\traw_beta\tq_mask\tq_beta\n"
            "p1\tG\t3\t1\t0.75\t0\t0.75\n"
            "p2\t2\t1\t1\t0.5\t1\tNA\n"
            "p3\tR\tNA\tNA\tNA\t0\tNA\n"
        )
        self.write_table(self.table)
        (self.r_output / "probe-ids.txt").write_text("p1\np2\np3\n", encoding="utf-8")
        self.signals: dict[str, tuple[float, ...]] = {
            "M-signal.f64": (3.0, 1.0, math.nan),
            "U-signal.f64": (1.0, 1.0, math.nan),
            "raw-beta.f64": (0.75, 0.5, math.nan),
            "q-beta.f64": (0.75, math.nan, math.nan),
        }
        for name, values in self.signals.items():
            (self.r_output / name).write_bytes(struct.pack("<3d", *values))
        (self.r_output / "q-mask.u8").write_bytes(bytes([0, 1, 0]))

    def write_table(self, text: str) -> None:
        self.reference.write_bytes(gzip.compress(text.encode("utf-8"), mtime=0))

    def invoke(self, name: str, expected_exit: int) -> dict[str, object]:
        path = self.root / f"{name}.json"
        with (
            patch.object(compare_raw_q, "PROBE_COUNT", 3),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = compare_raw_q.main(
                [
                    "--reference",
                    str(self.reference),
                    "--r-output",
                    str(self.r_output),
                    "--receipt",
                    str(path),
                ]
            )
        self.assertEqual(result, expected_exit)
        document: object = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            self.fail("receipt must be a JSON object")
        return cast(dict[str, object], document)

    def test_complete_known_values_and_missingness_pass(self) -> None:
        receipt = self.invoke("complete", 0)
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["rows"], 3)
        self.assertEqual(
            receipt["mismatches"],
            {"M_signal": 0, "U_signal": 0, "raw_beta": 0, "q_beta": 0, "q_mask": 0},
        )
        self.assertEqual(
            receipt["missing"],
            {"M_signal": 1, "U_signal": 1, "raw_beta": 1, "q_beta": 2},
        )

    def test_malformed_schema_and_universe_produce_failed_receipts(self) -> None:
        cases = {
            "header": self.table.replace("Probe_ID", "wrong", 1),
            "extra_header": self.table.replace("q_beta\n", "q_beta\textra\n", 1),
            "extra_field": self.table.replace("0.75\t0\t0.75\n", "0.75\t0\t0.75\textra\n", 1),
            "short": "\n".join(self.table.splitlines()[:-1]) + "\n",
            "trailing": self.table + "p4\tG\t3\t1\t0.75\t0\t0.75\n",
            "order": self.table.replace("p1\tG", "p2\tG", 1),
        }
        for name, table in cases.items():
            with self.subTest(name=name):
                self.write_table(table)
                receipt = self.invoke(name, 1)
                self.assertEqual(receipt["status"], "failed")
                self.assertIn("error", receipt)

    def test_bad_binary_or_lost_finite_value_fails_without_nonfinite_receipt(
        self,
    ) -> None:
        path = self.r_output / "raw-beta.f64"
        original = path.read_bytes()
        for name, payload in {
            "truncated": original[:-1],
            "trailing": original + b"x",
            "infinite": struct.pack("<3d", math.inf, 0.5, math.nan),
        }.items():
            with self.subTest(name=name):
                path.write_bytes(payload)
                receipt = self.invoke(name, 1)
                self.assertEqual(receipt["status"], "failed")
                self.assertIn("error", receipt)
        path.write_bytes(struct.pack("<3d", math.nan, 0.5, math.nan))
        receipt = self.invoke("lost-finite", 1)
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(
            receipt["mismatches"],
            {"M_signal": 0, "U_signal": 0, "raw_beta": 1, "q_beta": 0, "q_mask": 0},
        )

    def test_existing_receipts_and_input_aliases_are_preserved(self) -> None:
        receipt = self.root / "existing.json"
        receipt.write_text("prior evidence\n", encoding="utf-8")
        original = self.reference.read_bytes()
        absent_alias = self.root / "absent.tsv.gz"
        for expected, destination in [
            (self.reference, receipt),
            (self.reference, self.reference),
            (absent_alias, absent_alias),
        ]:
            with self.subTest(destination=destination):
                with self.assertRaises(ValueError):
                    compare_raw_q.main(
                        [
                            "--reference",
                            str(expected),
                            "--r-output",
                            str(self.r_output),
                            "--receipt",
                            str(destination),
                        ]
                    )
        self.assertEqual(receipt.read_text(encoding="utf-8"), "prior evidence\n")
        self.assertEqual(self.reference.read_bytes(), original)
        self.assertFalse(absent_alias.exists())


if __name__ == "__main__":
    unittest.main()
