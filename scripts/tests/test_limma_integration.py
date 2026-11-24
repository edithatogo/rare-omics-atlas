"""Reject corrupt received contracts; the strict gate also runs the real exporter."""

import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qualify_limma


def write_csv(path, header, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def exchange(root):
    """Tiny parser fixture, not a numerical oracle. The real gate uses independent R."""
    fixture, received = root / "reference", root / "received"
    fixture.mkdir(exist_ok=True)
    received.mkdir(exist_ok=True)
    features = ["feature,quoted", "missing"]
    write_csv(
        fixture / "input_log2.csv",
        ["row", "s1", "s2", "s3"],
        [[features[0], 1, 2, 3], [features[1], "NA", 2, 3]],
    )
    write_csv(fixture / "design.csv", ["row", "intercept"], [["s1", 1], ["s2", 1], ["s3", 1]])
    write_csv(fixture / "contrasts.csv", ["row", "contrast"], [["intercept", 1]])
    for filename, value in [
        ("contrasts_stdev_unscaled.csv", 0.5),
        (f"{qualify_limma.PREFIX}_moderated_se.csv", 1),
    ]:
        write_csv(
            fixture / filename, ["row", "contrast"], [[features[0], value], [features[1], "NA"]]
        )
    write_csv(
        fixture / "lmfit_scalars.csv",
        ["row", "sigma", "df_residual"],
        [[feature, 3, 2] for feature in features],
    )
    write_csv(
        fixture / f"{qualify_limma.PREFIX}_scalars.csv",
        ["row", "s2_post", "df_total"],
        [[feature, 4, 5] for feature in features],
    )
    write_csv(
        fixture / f"{qualify_limma.PREFIX}_toptable_1.csv",
        ["row", "logFC", "t", "P.Value", "adj.P.Val", "CI.L", "CI.R"],
        [[features[0], 2, 2, 0.1, 0.2, -0.5, 4.5], [features[1], *["NA"] * 6]],
    )
    metadata = {
        "schema_version": 1,
        "contract_id": "limma-named-contrasts-v1",
        "crate_version": "0.1.0",
        "purpose": "synthetic_qualification",
        "input_scale": "log2_expression",
        "feature_ids": features,
        "sample_ids": ["s1", "s2", "s3"],
        "design_ids": ["intercept"],
        "contrast_ids": ["contrast"],
        "layout": "contrast_major_then_feature",
        "columns": qualify_limma.COLUMNS,
        "method": qualify_limma.METHOD,
        "warnings": [],
    }
    (received / "metadata.json").write_text(json.dumps(metadata))
    rows = [
        [
            features[0],
            "contrast",
            2,
            0.5,
            4,
            1.5,
            1,
            2,
            5,
            2,
            0.1,
            0.2,
            -0.5,
            4.5,
            "false",
            "log2_expression",
        ],
        [
            features[1],
            "contrast",
            "NaN",
            "NaN",
            4,
            "NaN",
            "NaN",
            2,
            5,
            "NaN",
            "NaN",
            "NaN",
            "NaN",
            "NaN",
            "true",
            "log2_expression",
        ],
    ]
    write_csv(received / "estimates.csv", qualify_limma.COLUMNS, rows)
    return fixture, received, metadata, rows


class NumericTransport(unittest.TestCase):
    def test_nonfinite_values_are_compared_instead_of_skipped(self):
        self.assertTrue(qualify_limma.matches(float("nan"), float("nan"), "estimate"))
        self.assertTrue(qualify_limma.matches(float("inf"), float("inf"), "estimate"))
        self.assertFalse(qualify_limma.matches(float("inf"), float("-inf"), "estimate"))
        self.assertFalse(qualify_limma.matches(0.0, float("nan"), "estimate"))
        self.assertFalse(qualify_limma.matches(float("nan"), 0.0, "estimate"))
        self.assertFalse(qualify_limma.matches(0.001, 0.0, "estimate"))
        self.assertTrue(qualify_limma.matches(0.0, 1e-13, "p_value"))
        self.assertFalse(qualify_limma.matches(1e-9, 1e-13, "adj_p_value"))
        self.assertTrue(qualify_limma.matches(1 + 1e-7, 1, "df_total"))
        self.assertFalse(qualify_limma.matches(1 + 1e-7, 1, "moderated_se"))

    def test_received_quoted_identity_and_nonestimable_row_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture, received, _, _ = exchange(Path(folder))
            result = qualify_limma.validate_exchange(fixture, received, "log2_expression")
            self.assertEqual(result["rows"], 2)
            self.assertEqual(result["numeric_comparisons"], 24)
            self.assertEqual(result["nonfinite_values_preserved"], 9)
            self.assertEqual(result["worst_finite_relative_error"], 0)
            self.assertEqual(len(result["output_sha256"]), 2)

    def test_metadata_identity_method_scale_or_warning_drift_fails(self):
        changes = {
            "schema_version": 2,
            "contract_id": "other",
            "crate_version": "2",
            "input_scale": "log2_methylation_odds",
            "feature_ids": ["missing", "feature,quoted"],
            "sample_ids": ["s2", "s1", "s3"],
            "design_ids": ["other"],
            "contrast_ids": ["other"],
            "layout": "sorted_by_p",
            "columns": [],
            "method": {"robust": True},
            "warnings": ["new diagnostic"],
        }
        for key, value in changes.items():
            with self.subTest(key=key), tempfile.TemporaryDirectory() as folder:
                fixture, received, metadata, _ = exchange(Path(folder))
                metadata[key] = value
                (received / "metadata.json").write_text(json.dumps(metadata))
                with self.assertRaisesRegex(ValueError, "metadata differs"):
                    qualify_limma.validate_exchange(fixture, received, "log2_expression")

    def test_only_the_declared_missing_scalar_oracle_uses_exact_input_row_numbers(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture, received, _, _ = exchange(Path(folder))
            scalar = fixture / f"{qualify_limma.PREFIX}_scalars.csv"
            write_csv(scalar, ["row", "s2_post", "df_total"], [["1", 4, 5], ["2", 4, 5]])
            with self.assertRaisesRegex(ValueError, "reference feature order"):
                qualify_limma.validate_exchange(fixture, received, "log2_expression")
            missing = fixture.with_name("missing")
            fixture.rename(missing)
            result = qualify_limma.validate_exchange(missing, received, "log2_expression")
            self.assertEqual(result["reference_scalar_rows"], "one_based_input_order")
            write_csv(
                missing / scalar.name, ["row", "s2_post", "df_total"], [["2", 4, 5], ["1", 4, 5]]
            )
            with self.assertRaisesRegex(ValueError, "reference feature order"):
                qualify_limma.validate_exchange(missing, received, "log2_expression")

    def test_csv_corruption_and_replaced_nonfinite_results_fail(self):
        changes = [
            ("order", None),
            ("missing_row", None),
            ("extra_column", None),
            ("missing_cell", None),
            ("feature_id", "other"),
            ("contrast_id", "other"),
            ("input_scale", "log2_methylation_odds"),
            ("non_estimable", "true"),
            ("moderated_se", 0.5),
            ("adj_p_value", 0.01),
            ("ci_lower", -0.7),
            ("estimate", "not-a-number"),
            ("missingness", 0),
        ]
        for key, value in changes:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as folder:
                fixture, received, _, rows = exchange(Path(folder))
                if key == "order":
                    rows.reverse()
                elif key == "missing_row":
                    rows.pop()
                elif key == "extra_column":
                    rows[0].append("unexpected")
                elif key == "missing_cell":
                    rows[0].pop()
                elif key == "missingness":
                    rows[1][2] = value
                else:
                    rows[0][qualify_limma.COLUMNS.index(key)] = value
                write_csv(received / "estimates.csv", qualify_limma.COLUMNS, rows)
                with self.assertRaises(ValueError):
                    qualify_limma.validate_exchange(fixture, received, "log2_expression")

    def test_json_boolean_and_numeric_types_cannot_substitute_for_each_other(self):
        for key, value in [
            ("schema_version", True),
            ("schema_version", 1.0),
            ("method", qualify_limma.METHOD | {"robust": 0}),
            ("method", qualify_limma.METHOD | {"trend": 0.0}),
        ]:
            with self.subTest(key=key, value=value), tempfile.TemporaryDirectory() as folder:
                fixture, received, metadata, _ = exchange(Path(folder))
                (received / "metadata.json").write_text(json.dumps(metadata | {key: value}))
                with self.assertRaisesRegex(ValueError, "metadata differs"):
                    qualify_limma.validate_exchange(fixture, received, "log2_expression")

    def test_invalid_headers_reference_axes_and_duplicate_json_are_rejected(self):
        for scenario in [
            "header",
            "empty",
            "duplicate_id",
            "duplicate_column",
            "shape",
            "axes",
            "feature_order",
            "csv_header",
            "json_duplicates",
            "json_nonobject",
            "scale",
        ]:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as folder:
                fixture, received, _, _ = exchange(Path(folder))
                target = fixture / "input_log2.csv"
                if scenario == "header":
                    target.write_text("wrong,s1\nf,1\n")
                elif scenario == "empty":
                    target.write_text("")
                elif scenario == "duplicate_id":
                    target.write_text("row,s1\nf,1\nf,2\n")
                elif scenario == "duplicate_column":
                    target.write_text("row,s1,s1\nf,1,2\n")
                elif scenario == "shape":
                    target.write_text("row,s1\nf,1,2\n")
                elif scenario == "axes":
                    (fixture / "design.csv").write_text("row,intercept\nwrong,1\n")
                elif scenario == "feature_order":
                    (fixture / "lmfit_scalars.csv").write_text("row,sigma,df_residual\nwrong,1,2\n")
                elif scenario == "csv_header":
                    (received / "estimates.csv").write_text("wrong\n")
                elif scenario == "json_duplicates":
                    (received / "metadata.json").write_text('{"method":1,"method":2}')
                elif scenario == "json_nonobject":
                    (received / "metadata.json").write_text("[]")
                with self.assertRaises(ValueError):
                    qualify_limma.validate_exchange(
                        fixture, received, "unknown" if scenario == "scale" else "log2_expression"
                    )


class PinnedSource(unittest.TestCase):
    def test_manifest_rejects_floating_revisions_and_wrong_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            original = {
                "schema_version": 1,
                "contract_id": qualify_limma.CONTRACT,
                "source_repository": qualify_limma.REPOSITORY,
                "source_revision": "a" * 40,
            }
            path.write_text(json.dumps(original))
            self.assertEqual(qualify_limma.read_manifest(path), "a" * 40)
            for key, value in [
                ("schema_version", 2),
                ("schema_version", True),
                ("schema_version", 1.0),
                ("contract_id", "other"),
                ("source_repository", "other"),
                ("source_revision", "main"),
                ("source_revision", None),
            ]:
                path.write_text(json.dumps(original | {key: value}))
                with self.assertRaises(ValueError):
                    qualify_limma.read_manifest(path)

    def test_actual_git_checkout_rejects_dirty_mismatched_and_hidden_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)

            def git(*args):
                return subprocess.check_output(
                    ["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL
                ).strip()

            git("init")
            git("config", "user.name", "Contract test")
            git("config", "user.email", "test@example.invalid")
            git("remote", "add", "origin", qualify_limma.REPOSITORY)
            (root / "source.txt").write_text("original")
            git("add", ".")
            git("commit", "-m", "fixture")
            revision = git("rev-parse", "HEAD")
            qualify_limma.prepare_source(root, revision)
            with self.assertRaisesRegex(ValueError, "revision"):
                qualify_limma.check_source(root, "b" * 40)
            child = root / "nested"
            child.mkdir()
            with self.assertRaisesRegex(ValueError, "repository root"):
                qualify_limma.check_source(child, revision)
            (root / "untracked").write_text("new")
            with self.assertRaisesRegex(ValueError, "uncommitted"):
                qualify_limma.check_source(root, revision)
            (root / "untracked").unlink()
            for flag in ["assume-unchanged", "skip-worktree"]:
                git("update-index", f"--{flag}", "source.txt")
                with self.assertRaisesRegex(ValueError, "hidden"):
                    qualify_limma.check_source(root, revision)
                git("update-index", f"--no-{flag}", "source.txt")
            (root / "source.txt").write_text("changed")
            with self.assertRaisesRegex(ValueError, "uncommitted"):
                qualify_limma.check_source(root, revision)
            git("remote", "set-url", "origin", "https://example.invalid/other")
            with self.assertRaisesRegex(ValueError, "origin"):
                qualify_limma.check_source(root, revision)

    def test_failed_export_or_stale_receipt_cannot_become_success(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / "artifacts/verification/test"
            output.mkdir(parents=True)
            receipt = output / "limma-contract.json"
            receipt.write_text('{"status":"passed"}')
            manifest = root / "pin.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "contract_id": qualify_limma.CONTRACT,
                        "source_repository": qualify_limma.REPOSITORY,
                        "source_revision": "a" * 40,
                    }
                )
            )
            with (
                patch.object(qualify_limma, "ROOT", root),
                patch.object(
                    qualify_limma,
                    "qualify",
                    side_effect=subprocess.CalledProcessError(7, ["cargo", "run"]),
                ),
                patch.object(
                    sys,
                    "argv",
                    ["qualify_limma.py", "--manifest", str(manifest), "--output", str(output)],
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(qualify_limma.main(), 1)
            result = json.loads(receipt.read_text())
            self.assertEqual(result["status"], "failed")
            self.assertFalse(result["scientific_admitted"])
            self.assertFalse(result["reference_regenerated"])
            self.assertEqual(result["exit_code"], 7)
            self.assertEqual(result["failed_command"], ["cargo", "run"])

    def test_output_aliases_are_rejected_before_input_or_existing_files_are_written(self):
        for scenario in ["same_path", "symlink", "hardlink", "directory_symlink"]:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                output = root / "artifacts/verification/test"
                output.mkdir(parents=True)
                receipt = output / "limma-contract.json"
                manifest = root / "source.json"
                original = b'{"preserve":"source input"}'
                manifest.write_bytes(original)
                if scenario == "same_path":
                    manifest = receipt
                    manifest.write_bytes(original)
                elif scenario == "symlink":
                    receipt.symlink_to(manifest)
                elif scenario == "hardlink":
                    os.link(manifest, receipt)
                else:
                    linked = output.parent / "link"
                    linked.symlink_to(output, target_is_directory=True)
                    output = linked
                with (
                    patch.object(qualify_limma, "ROOT", root),
                    patch.object(
                        sys,
                        "argv",
                        ["qualify_limma.py", "--manifest", str(manifest), "--output", str(output)],
                    ),
                    self.assertRaises(ValueError),
                ):
                    qualify_limma.main()
                self.assertEqual(manifest.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
