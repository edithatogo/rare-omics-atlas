"""Fictional source fixtures; no real study rows are committed."""

import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import molecular_replay as replay
from molecular_replay import CASE, CONTROL, review, table_s2a, write_review


def soft(label, number, group):
    return (
        f"^SAMPLE = GSM{number}\n!Sample_description = {label}\n"
        f"!Sample_characteristics_ch1 = sample type: {group}\n"
    )


def table(rows):
    return (
        "Table S2. Molecular data\na) KMT2D Loss of Function Mutations\n"
        + rows
        + "\nb) KMT2D Sequence Variants Classified Using the DNAm Signature\n"
        "KMT2D-9 c.9A>G p.X9Y missense\n"
    )


class SourceEligibility(unittest.TestCase):
    def test_exact_source_join_and_held_independence(self):
        geo = (
            soft("KMT2D-1", 1, CASE)
            + soft("C1", 2, CONTROL)
            + soft("KMT2D-9", 3, "KMT2D sequence variant")
        )
        report, manifest, decisions = review(
            geo, table_s2a(table("KMT2D-1 c.1A>T p.X1* nonsense")), "a" * 64, "b" * 64, expected=1
        )
        self.assertEqual(report["molecular_source_eligible"], 1)
        self.assertEqual(report["selected_control_assays"], 1)
        self.assertFalse(report["analysis_admitted"])
        self.assertEqual(len(manifest["samples"]), 2)
        self.assertEqual(manifest["samples"][0]["molecular_eligibility"], "eligible")
        self.assertEqual(manifest["samples"][1]["molecular_eligibility"], "not_applicable")
        self.assertTrue(
            all(
                s["participant_id"] is None
                and s["specimen_id"] is None
                and s["independence"] == "unknown"
                for s in manifest["samples"]
            )
        )
        self.assertEqual(decisions[0]["source_reported_basis"], "loss_of_function:nonsense")
        self.assertIsNone(decisions[0]["atlas_acmg_classification"])
        self.assertEqual(decisions[0]["supplement_sha256"], "b" * 64)
        self.assertNotIn("GSM1", json.dumps(report))
        self.assertNotIn("KMT2D-1", json.dumps(report))

    def test_vus_or_nonmatching_label_cannot_promote(self):
        geo = soft("KMT2D-9", 1, CASE) + soft("C1", 2, CONTROL)
        with self.assertRaisesRegex(ValueError, "exact"):
            review(
                geo,
                table_s2a(table("KMT2D-1 c.1A>T p.X1* nonsense")),
                "a" * 64,
                "b" * 64,
                expected=1,
            )
        with self.assertRaisesRegex(ValueError, "section"):
            table_s2a("KMT2D-1 c.1A>T p.X1* nonsense")

    def test_duplicate_and_count_failures(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            table_s2a(
                table("KMT2D-1 c.1A>T p.X1* nonsense\nKMT2D-1 c.2del p.X2fs*3 frameshift")
            )
        cases = table_s2a(table("KMT2D-1 c.1A>T p.X1* nonsense"))
        with self.assertRaisesRegex(ValueError, "count"):
            review(soft("KMT2D-1", 1, CASE), cases, "a" * 64, "b" * 64, expected=1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            review(
                soft("KMT2D-1", 1, CASE) + soft("C1", 1, CONTROL),
                cases,
                "a" * 64,
                "b" * 64,
                expected=1,
            )

    def test_fresh_output_and_only_aggregate_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report, manifest, decisions = review(
                soft("KMT2D-1", 1, CASE) + soft("C1", 2, CONTROL),
                table_s2a(table("KMT2D-1 c.1A>T p.X1* nonsense")),
                "a" * 64,
                "b" * 64,
                expected=1,
            )
            out = root / "new"
            write_review(out, report, manifest, decisions)
            self.assertEqual(json.loads((out / "aggregate.json").read_text()), report)
            self.assertEqual(json.loads((out / "declared-samples.json").read_text()), manifest)
            self.assertEqual(json.loads((out / "molecular-decisions.local.json").read_text()), decisions)
            with self.assertRaises(FileExistsError):
                write_review(out, report, manifest, decisions)

    def test_ambiguities_fail_closed(self):
        cases = table_s2a(table("KMT2D-1 c.1A>T p.X1* nonsense"))
        case = soft("KMT2D-1", 1, CASE)
        control = soft("C1", 2, CONTROL)
        with self.assertRaisesRegex(ValueError, "ambiguous selected"):
            review(
                case + f"!Sample_characteristics_ch1 = sample type: {CONTROL}\n" + control,
                cases,
                "a" * 64,
                "b" * 64,
                expected=1,
            )
        with self.assertRaisesRegex(ValueError, "study label"):
            review(
                case.replace("!Sample_description = KMT2D-1\n", "") + control,
                cases,
                "a" * 64,
                "b" * 64,
                expected=1,
            )
        with self.assertRaisesRegex(ValueError, "one-to-one"):
            review(
                case + control,
                {**cases, "KMT2D-2": ("synthetic", "frameshift")},
                "a" * 64,
                "b" * 64,
                expected=1,
            )

    def test_pinned_files_and_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            geo = root / "test.soft"
            pdf = root / "test.pdf"
            out = root / "out"
            geo.write_text(
                "".join(
                    soft(f"KMT2D-{n}", n, CASE) + soft(f"C{n}", n + 20, CONTROL)
                    for n in range(1, 12)
                )
            )
            pdf.write_bytes(b"synthetic PDF extraction fixture")
            args = ["--geo", str(geo), "--supplement", str(pdf), "--out", str(out)]
            with self.assertRaisesRegex(ValueError, "GEO source"):
                replay.main(args)
            with patch.object(replay, "GEO_SHA256", hashlib.sha256(geo.read_bytes()).hexdigest()):
                with self.assertRaisesRegex(ValueError, "supplement bytes"):
                    replay.main(args)
                with patch.object(replay, "SUPPLEMENT_BYTES", pdf.stat().st_size):
                    with self.assertRaisesRegex(ValueError, "supplement bytes"):
                        replay.main(args)
                    fixture = table(
                        "\n".join(f"KMT2D-{n} c.{n}A>T p.X{n}* nonsense" for n in range(1, 12))
                    )
                    with (
                        patch.object(
                            replay,
                            "SUPPLEMENT_MD5",
                            hashlib.md5(pdf.read_bytes(), usedforsecurity=False).hexdigest(),
                        ),
                        patch.object(replay.subprocess, "check_output", return_value=fixture) as extract,
                        redirect_stdout(io.StringIO()) as stdout,
                    ):
                        replay.main(args)
                    extract.assert_called_once_with(
                        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
                        text=True,
                        encoding="utf-8",
                        timeout=60,
                    )
                    report = json.loads(stdout.getvalue())
                    self.assertEqual(report["molecular_source_eligible"], 11)
                    self.assertEqual(
                        report["manifest_sha256"],
                        hashlib.sha256((out / "declared-samples.json").read_bytes()).hexdigest(),
                    )
                    self.assertNotIn("GSM1", stdout.getvalue())
