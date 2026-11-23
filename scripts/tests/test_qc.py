"""Independent named QC/p-value fixtures and fail-closed orchestration checks."""

import copy
import gzip
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_preprocessing as prep
import qualify_qc as qc
from test_preprocessing import Fixture, pin, table_text, write_table

# Each row is metric, independent reference text, literal ten-digit producer text.
# These expected strings never pass through the production formatting functions.
QC_ROWS = [
    line.split()
    for line in """
num_dtna 1 1
frac_dtna 0.125 0.125
num_dt 2 2
frac_dt 0.25 0.25
num_dt_mk 1 1
frac_dt_mk 0.125 0.125
num_dt_cg 2 2
frac_dt_cg 0.4 0.4
num_dt_ch 0 0
frac_dt_ch 0 0
num_dt_rs 0 0
frac_dt_rs 0 0
num_probes 8 8
num_probes_II 3 3
num_probes_IR 2 2
num_probes_IG 3 3
num_probes_cg 5 5
num_probes_ch 1 1
num_probes_rs 1 1
mean_intensity 123.4567891234 123.4567891
mean_intensity_MU 246.9135782468 246.9135782
mean_ii 123.4567891234 123.4567891
mean_inb_grn 17.123456789012 17.12345679
mean_inb_red 19.123456789012 19.12345679
mean_oob_grn 8.765432198765 8.765432199
mean_oob_red 9.876543219876 9.87654322
na_intensity_M 1 1
na_intensity_U 1 1
na_intensity_ig 0 0
na_intensity_ir 0 0
na_intensity_ii 1 1
InfI_switch_R2R 2 2
InfI_switch_G2G 3 3
InfI_switch_R2G 0 0
InfI_switch_G2R 0 0
medR 10 10
medG 20 20
topR 30 30
topG 40 40
RGratio 0.5 0.5
RGdistort 1.25 1.25
GCT 0.987654321098 0.9876543211
mean_beta 0.1234567891234 0.1234567891
median_beta 0.234567891234 0.2345678912
frac_unmeth 0.25 0.25
frac_meth 0.125 0.125
num_na 1 1
frac_na 0.125 0.125
mean_beta_cg 0.345678912345 0.3456789123
median_beta_cg 0.456789123456 0.4567891235
frac_unmeth_cg 0.4 0.4
frac_meth_cg 0.2 0.2
num_na_cg 0 0
frac_na_cg 0 0
mean_beta_ch 0.234567891234 0.2345678912
median_beta_ch 0.234567891234 0.2345678912
frac_unmeth_ch 0 0
frac_meth_ch 0 0
num_na_ch 0 0
frac_na_ch 0 0
mean_beta_rs NA NA
median_beta_rs NA NA
frac_unmeth_rs NA NA
frac_meth_rs NA NA
num_na_rs 1 1
frac_na_rs 1 1
""".strip().splitlines()
]
QC_NAMES = tuple(row[0] for row in QC_ROWS)
INTEGER_NAMES = frozenset(
    """
num_dtna num_dt num_dt_mk num_dt_cg num_dt_ch num_dt_rs
num_probes num_probes_II num_probes_IR num_probes_IG num_probes_cg num_probes_ch num_probes_rs
na_intensity_M na_intensity_U na_intensity_ig na_intensity_ir na_intensity_ii
InfI_switch_R2R InfI_switch_G2G InfI_switch_R2G InfI_switch_G2R
num_na num_na_cg num_na_ch num_na_rs
""".split()
)
GCT_SCOPE = (
    "R arithmetic over pinned published extension lists; "
    "native bisConversionControl parity is not claimed"
)


class QCFixture(Fixture):
    def __init__(self, root):
        super().__init__(root)
        self.reference_root = root / "qc-reference"
        self.reference_root.mkdir()
        self.qc_reference = self.reference_root / "qc-reference.tsv"
        self.pvalue_reference = self.reference_root / "pvalues-reference.tsv.gz"
        self.qc_actual = root / "qc.tsv"
        self.pvalue_actual = root / "pvalues.tsv"
        self.pvalue_index = root / "pval.cg.idx"
        self.qc_driver = root / "scripts/qualify_qc.py"
        self.qc_driver.parent.mkdir()
        self.qc_driver.write_text("synthetic QC checker identity\n")
        self.qc_helper = self.qc_driver.with_name("qualify_limma.py")
        self.qc_helper.write_text("synthetic shared helper identity\n")
        self.r_recipe = root / "scripts/tests/run_qc_reference.R"
        self.r_recipe.parent.mkdir()
        self.r_recipe.write_text("synthetic independent R recipe identity\n")
        self.qc_contract_path = root / "qc-contract-input.json"
        self.metric_reference_rows = [["metric", "value"], *[row[:2] for row in QC_ROWS]]
        self.metric_actual_rows = [
            ["sample", *QC_NAMES],
            [prep.SAMPLE, *[row[2] for row in QC_ROWS]],
        ]
        raw = ["0", "1", "0.123456789", "NA", "0.25", "0.99999999", "1e-50", "0.05"]
        qcd = ["0.75", "0.03", "0.234567891", "NA", "0.9", "0.99999999", "1e-50", "0.05"]
        self.pvalue_reference_rows = [
            ["Probe_ID", "raw_pval", "qcd_pval"],
            *[list(row) for row in zip(self.ids, raw, qcd, strict=True)],
        ]
        self.pvalue_text = {
            "raw": ["0", "1", "0.123457", "NA", "0.25", "1", "0", "0.05"],
            "QCDPB": ["0.75", "0.03", "0.234568", "NA", "0.9", "1", "0", "0.05"],
        }
        write_table(self.qc_reference, self.metric_reference_rows)
        write_table(self.pvalue_reference, self.pvalue_reference_rows)
        write_table(self.qc_actual, self.metric_actual_rows)
        write_table(self.pvalue_actual, self.pvalue_table("raw"))
        self.pvalue_index.write_text(f"{prep.SAMPLE}\t0\n")
        self.qc_contract = {
            "schema_version": 1,
            "contract_id": "sesame-hm450-qc-v1",
            "preprocessing_contract_sha256": pin(self.contract_path)["sha256"],
            "metrics": list(QC_NAMES),
            "integer_metrics": sorted(INTEGER_NAMES),
            "gct_reference": GCT_SCOPE,
            "r_source_revision": "8b1fcfaed89b28e0def8b031a81611a0a770053c",
            "reference_recipe": "scripts/tests/run_qc_reference.R",
            "reference_recipe_pin": pin(self.r_recipe),
            "reference_scope": (
                "Unchanged native R 65-field panel plus separately declared GCT published-list arithmetic; "
                "not full package or native bisConversionControl parity."
            ),
            "native_r_qc_metrics": 65,
            "qc_stage": "raw",
            "qc_beta_stage": "DBP",
            "qc_float_format": ".10g",
            "pvalue_format": "binary32 then .6g",
            "pvalue_reference_stages": {"raw": "raw", "QCDPB": "QCD before P masking and B"},
            "stages": ["raw", "QCDPB"],
            "threads": [1, 2],
            "minimum_beads": 0,
            "detection_threshold": 0.05,
            "reference_files": {p.name: pin(p) for p in (self.qc_reference, self.pvalue_reference)},
            "scientific_admitted": False,
            "official_owner_device_accepted": False,
            "sample_rejection_policy_accepted": False,
            "scientific_precision_budget_accepted": False,
        }
        self.write_qc_contract()

    def write_qc_contract(self):
        self.qc_contract_path.write_text(json.dumps(self.qc_contract))

    def pvalue_table(self, stage):
        return [
            ["Probe_ID", prep.SAMPLE],
            *[list(row) for row in zip(self.ids, self.pvalue_text[stage], strict=True)],
        ]

    def check_contract(self):
        with (
            patch.object(prep, "CONTRACT", self.contract_path),
            patch.object(qc, "ROOT", self.root),
        ):
            return qc.check_contract(self.qc_contract, self.reference_root)

    def compare_pvalues(self, stage="raw", ids=None):
        return qc.compare_pvalues(
            self.pvalue_reference,
            self.pvalue_actual,
            self.pvalue_index,
            self.ids if ids is None else ids,
            stage,
            prep.SAMPLE,
        )

    def execute(self, command, **kwargs):
        if self.observed_initial_status is None:
            self.observed_initial_status = self.receipt()["status"]
        if (
            command[0] == "make"
            or command[1] == "version"
            or (command[1] == "describe-probe" and "--all" not in command)
        ):
            return super().execute(command, **kwargs)
        self.commands.append(command)
        assert kwargs["cwd"] == self.checkout
        assert kwargs["env"]["YAME_DATA_HOME"] == str(self.data / "assets")
        if command[1] == "preprocess":
            stage = command[command.index("--prep") + 1] or "raw"
            threads = int(command[command.index("--threads") + 1])
            self.preparations.append((stage, threads))
            assert command[command.index("--output") + 1] == "pval,qc"
            assert command[command.index("--min-beads") + 1] == "0"
            assert command[command.index("--mask") + 1] == str(self.assets / prep.ASSETS[3])
            target = Path(command[command.index("--out") + 1])
            target.mkdir()
            if self.scenario != "missing_binary_output":
                binary = ("synthetic p-values " + stage).encode()
                if self.scenario == "binary_thread_variation" and target.name == "raw-2":
                    binary += b"changed"
                (target / "pval.cg").write_bytes(binary)
            if self.scenario != "missing_sample_index":
                (target / "pval.cg.idx").write_text(f"{prep.SAMPLE}\t0\n")
            rows = copy.deepcopy(self.metric_actual_rows)
            if self.scenario == "numeric_qc_failure":
                for field, text in {
                    "num_dtna": "2",
                    "frac_dtna": "0.5",
                    "mean_intensity": "124.4567891",
                    "mean_beta_rs": "0",
                }.items():
                    rows[1][1 + QC_NAMES.index(field)] = text
            if self.scenario == "qc_stage_variation" and stage == "QCDPB":
                rows[1][1 + QC_NAMES.index("mean_intensity")] = "123.45678910"
            if self.scenario != "missing_qc_output":
                write_table(target / "qc.tsv", rows)
        elif command[1] == "describe-probe" and "--all" in command:
            target = Path(command[-1]).parent
            stage = target.name.split("-")[0]
            rows = self.pvalue_table(stage)
            if self.scenario == "numeric_pvalue_failure":
                rows[3][1] = "0.8"
            if self.scenario == "text_thread_variation" and target.name == "raw-2":
                rows[3][1] = "0.1234570"
            if self.scenario != "missing_pvalue_export":
                kwargs["stdout"].write(table_text(rows))
            if target.name == "QCDPB-2":
                self.mutate_after_qc_export()
        else:
            raise AssertionError(f"unexpected external command: {command}")
        return subprocess.CompletedProcess(command, 0)

    def mutate_after_qc_export(self):
        paths = {
            "input_drift": self.data / sorted(prep.INPUT_NAMES)[0],
            "raw_reference_drift": self.reference,
            "qc_reference_drift": self.qc_reference,
            "pvalue_reference_drift": self.pvalue_reference,
            "base_contract_drift": self.contract_path,
            "qc_contract_drift": self.qc_contract_path,
            "binary_drift": self.checkout / "sesame",
            "yame_binary_drift": self.checkout / "YAME/yame",
            "checker_drift": self.qc_driver,
            "preprocessing_checker_drift": self.driver,
            "helper_drift": self.qc_helper,
            "recipe_drift": self.r_recipe,
        }
        if self.scenario in paths:
            path = paths[self.scenario]
            if self.scenario == "qc_reference_drift":
                # Preserve all numerical comparisons so the final byte pin is required.
                path.write_text(path.read_text().replace("num_dtna\t1\n", "num_dtna\t01\n"))
            else:
                extra = gzip.compress(b"", mtime=0) if path.suffix == ".gz" else b" "
                path.write_bytes(path.read_bytes() + extra)
        elif self.scenario in ("source_drift", "yame_source_drift"):
            path = self.checkout if self.scenario == "source_drift" else self.checkout / "YAME"
            self.git_overrides[(path, ("rev-parse", "HEAD"))] = "f" * 40

    def main(self, output=None):
        output = self.output if output is None else output
        with (
            patch.object(qc, "ROOT", self.root),
            patch.object(qc, "CONTRACT", self.qc_contract_path),
            patch.object(qc, "__file__", str(self.qc_driver)),
            patch.object(prep, "CONTRACT", self.contract_path),
            patch.object(prep, "__file__", str(self.driver)),
            patch.object(prep, "git", side_effect=self.git),
            patch.object(qc.subprocess, "run", side_effect=self.execute),
            patch.object(
                sys,
                "argv",
                [
                    "qualify_qc.py",
                    "--checkout",
                    str(self.checkout),
                    "--data-root",
                    str(self.data),
                    "--raw-reference",
                    str(self.reference),
                    "--reference-root",
                    str(self.reference_root),
                    "--output",
                    str(output),
                ],
            ),
            redirect_stdout(io.StringIO()),
        ):
            return qc.main()

    def receipt(self):
        return json.loads((self.output / "qc-contract.json").read_text())


class QCContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def fixture(self, name="fixture"):
        return QCFixture(self.root / name)

    def test_exact_66_field_panel_has_26_integer_and_40_float_metrics(self):
        self.assertEqual(qc.METRICS, QC_NAMES)
        self.assertEqual(qc.COUNTS, INTEGER_NAMES)
        self.assertEqual(len(QC_NAMES), 66)
        self.assertEqual(len(INTEGER_NAMES), 26)
        self.assertEqual(len(set(QC_NAMES) - INTEGER_NAMES), 40)
        f = self.fixture()
        result = qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["metrics_checked"], 66)
        self.assertEqual(result["metrics_failed"], 0)
        comparisons = {row["metric"]: row for row in result["comparisons"]}
        self.assertEqual(comparisons["mean_intensity"]["expected_serialized"], 123.4567891)
        self.assertEqual(comparisons["GCT"]["expected_serialized"], 0.9876543211)
        self.assertIsNone(comparisons["mean_beta_rs"]["reference"])
        self.assertEqual(comparisons["mean_beta_rs"]["status"], "passed")
        self.assertEqual(set(row["status"] for row in comparisons.values()), {"passed"})

    def test_counts_remain_exact_integers_beyond_float_precision_and_ten_digits(self):
        f = self.fixture()
        f.metric_reference_rows[1][1] = "9007199254740993"
        f.metric_actual_rows[1][1] = "9007199254740993"
        write_table(f.qc_reference, f.metric_reference_rows)
        write_table(f.qc_actual, f.metric_actual_rows)
        result = qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["comparisons"][0]["expected_serialized"], 9007199254740993)
        self.assertIsInstance(result["comparisons"][0]["expected_serialized"], int)
        f.metric_actual_rows[1][1] = "9007199254740992"
        write_table(f.qc_actual, f.metric_actual_rows)
        self.assertEqual(
            qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)["metrics_failed"], 1
        )

    def test_numeric_qc_mismatches_and_na_changes_are_failed_not_skipped(self):
        cases = [
            ("num_dt", "3"),
            ("mean_intensity", "123.4567892"),
            ("mean_intensity", "123.4567891234"),
            ("mean_beta_rs", "0"),
            ("mean_beta", "NA"),
        ]
        for number, (metric, value) in enumerate(cases):
            with self.subTest(metric=metric, value=value):
                f = self.fixture(str(number))
                f.metric_actual_rows[1][1 + QC_NAMES.index(metric)] = value
                write_table(f.qc_actual, f.metric_actual_rows)
                result = qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["metrics_checked"], 66)
                self.assertEqual(result["metrics_failed"], 1)
                failures = [
                    row["metric"] for row in result["comparisons"] if row["status"] == "failed"
                ]
                self.assertEqual(failures, [metric])

    def test_reference_metric_schema_requires_all_unique_known_fields(self):
        for scenario in ("schema", "missing", "duplicate", "extra", "width"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                rows = f.metric_reference_rows
                if scenario == "schema":
                    rows[0].reverse()
                elif scenario == "missing":
                    rows.pop()
                elif scenario == "duplicate":
                    rows.append(rows[1])
                elif scenario == "extra":
                    rows.append(["unrequested_metric", "1"])
                else:
                    rows[1].append("extra")
                write_table(f.qc_reference, rows)
                with self.assertRaises(ValueError):
                    qc.reference_metrics(f.qc_reference)

    def test_qc_output_schema_and_sample_identity_are_exact(self):
        scenarios = (
            "missing_metric",
            "duplicate_metric",
            "extra_metric",
            "order",
            "missing_sample",
            "duplicate_sample",
            "other_sample",
            "width",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                rows = f.metric_actual_rows
                if scenario == "missing_metric":
                    rows[0].pop()
                    rows[1].pop()
                elif scenario == "duplicate_metric":
                    rows[0][2] = rows[0][1]
                elif scenario == "extra_metric":
                    rows[0].append("extra")
                    rows[1].append("0")
                elif scenario == "order":
                    rows[0][1:3] = reversed(rows[0][1:3])
                elif scenario == "missing_sample":
                    rows.pop()
                elif scenario == "duplicate_sample":
                    rows.append(rows[1])
                elif scenario == "other_sample":
                    rows[1][0] = "other-sample"
                else:
                    rows[1].pop()
                write_table(f.qc_actual, rows)
                with self.assertRaises(ValueError):
                    qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)

    def test_metric_parsing_rejects_invalid_counts_nonfinite_values_and_bad_fractions(self):
        for text in ("NA", "-1", "1.0", "1e0", "+1", "NaN", "", "true"):
            with self.subTest(count=text), self.assertRaises(ValueError):
                qc.metric_value("num_probes", text)
        for text in ("nan", "NaN", "Inf", "-inf", "-0.1", "", "null"):
            with self.subTest(value=text), self.assertRaises(ValueError):
                qc.metric_value("mean_intensity", text)
        for metric in ("frac_dt", "mean_beta", "median_beta_cg"):
            with self.subTest(metric=metric), self.assertRaises(ValueError):
                qc.metric_value(metric, "1.00001")
        self.assertEqual(qc.metric_value("mean_intensity", "1234.5"), 1234.5)
        self.assertIsNone(qc.metric_value("mean_beta_rs", "NA"))
        self.assertEqual(qc.metric_value("frac_dt", "1"), 1)

    def test_literal_full_pvalue_exports_bind_raw_and_qcd_before_masking(self):
        f = self.fixture()
        for stage in ("raw", "QCDPB"):
            with self.subTest(stage=stage):
                write_table(f.pvalue_actual, f.pvalue_table(stage))
                result = f.compare_pvalues(stage)
                self.assertEqual(result["status"], "passed")
                self.assertEqual(result["rows"], 8)
                self.assertEqual(result["reference_missing"], 1)
                self.assertEqual(result["serialized_mismatches"], 0)
                self.assertEqual(result["detection_decision_changes_at_upstream_0_05"], 0)
                self.assertGreater(result["maximum_absolute_serialization_error"], 0)
                expected = "raw" if stage == "raw" else "QCD, before P masking and B correction"
                self.assertEqual(result["reference_stage"], expected)
        wrong_stage = f.compare_pvalues("raw")
        self.assertEqual(wrong_stage["status"], "failed")
        self.assertEqual(wrong_stage["serialized_mismatches"], 4)

    def test_serialized_threshold_crossing_fails_even_when_serialized_value_is_exact(self):
        f = self.fixture()
        f.pvalue_reference_rows[8][1] = "0.050000001"
        write_table(f.pvalue_reference, f.pvalue_reference_rows)
        result = f.compare_pvalues()
        self.assertEqual(result["serialized_mismatches"], 0)
        self.assertEqual(result["detection_decision_changes_at_upstream_0_05"], 1)
        self.assertEqual(result["status"], "failed")

    def test_pvalue_na_and_numeric_disagreements_retain_failure_counts(self):
        for number, (row, value, missing) in enumerate(((4, "0", 1), (3, "NA", 1), (3, "0.8", 0))):
            with self.subTest(row=row, value=value):
                f = self.fixture(str(number))
                rows = f.pvalue_table("raw")
                rows[row][1] = value
                write_table(f.pvalue_actual, rows)
                result = f.compare_pvalues()
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["rows"], 8)
                self.assertEqual(result["serialized_mismatches"], 1)
                self.assertEqual(result["missingness_mismatches"], missing)

    def test_pvalue_universe_schema_and_sample_corruption_are_rejected(self):
        for stream in ("reference", "actual"):
            for corruption in ("schema", "drop", "extra", "duplicate", "order", "width"):
                with self.subTest(stream=stream, corruption=corruption):
                    f = self.fixture(stream + corruption)
                    rows = (
                        f.pvalue_reference_rows if stream == "reference" else f.pvalue_table("raw")
                    )
                    if corruption == "schema":
                        rows[0][0] = "wrong"
                    elif corruption == "drop":
                        rows.pop()
                    elif corruption == "extra":
                        rows.append(rows[-1])
                    elif corruption == "duplicate":
                        rows[2] = rows[1]
                    elif corruption == "order":
                        rows[1:3] = reversed(rows[1:3])
                    else:
                        rows[1].pop()
                    write_table(
                        f.pvalue_reference if stream == "reference" else f.pvalue_actual, rows
                    )
                    with self.assertRaises(ValueError):
                        f.compare_pvalues()
        f = self.fixture("index")
        for index in ("other\t0\n", f"{prep.SAMPLE}\t1\n", f"{prep.SAMPLE}\t0", ""):
            f.pvalue_index.write_text(index)
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "sample index"):
                f.compare_pvalues()

    def test_both_pvalue_reference_columns_are_validated_and_empty_or_wrong_stages_fail(self):
        for number, value in enumerate(("nan", "Inf", "-0.1", "1.1", "not-a-number")):
            with self.subTest(nonselected_reference=value):
                f = self.fixture(str(number))
                f.pvalue_reference_rows[1][2] = value
                write_table(f.pvalue_reference, f.pvalue_reference_rows)
                with self.assertRaises(ValueError):
                    f.compare_pvalues("raw")
        f = self.fixture("empty")
        write_table(f.pvalue_reference, f.pvalue_reference_rows[:1])
        write_table(f.pvalue_actual, f.pvalue_table("raw")[:1])
        with self.assertRaisesRegex(ValueError, "empty p-value universe"):
            f.compare_pvalues(ids=[])
        with self.assertRaisesRegex(ValueError, "unsupported p-value stage"):
            f.compare_pvalues("Q")

    def test_contract_binds_schema_formats_reference_scope_and_false_admission_flags(self):
        f = self.fixture()
        self.assertEqual(set(f.check_contract()), {"qc-reference.tsv", "pvalues-reference.tsv.gz"})
        changes = [
            ("schema_version", True),
            ("contract_id", "other"),
            ("preprocessing_contract_sha256", "0" * 64),
            ("metrics", list(QC_NAMES[:-1])),
            ("integer_metrics", []),
            ("gct_reference", "native bisConversionControl"),
            ("r_source_revision", "0" * 40),
            ("reference_recipe", "missing-reference.R"),
            ("reference_scope", "unrelated reference"),
            ("native_r_qc_metrics", True),
            ("native_r_qc_metrics", 66),
            ("qc_stage", "QCDPB"),
            ("qc_beta_stage", "raw"),
            ("qc_float_format", ".6g"),
            ("pvalue_format", "binary64"),
            ("pvalue_reference_stages", {"QCDPB": "QCDPB"}),
            ("stages", ["raw", "Q"]),
            ("threads", [True, 2]),
            ("minimum_beads", True),
            ("minimum_beads", 1),
            ("detection_threshold", 0),
            ("detection_threshold", 0.050001),
            ("scientific_admitted", True),
            ("official_owner_device_accepted", 0),
            ("sample_rejection_policy_accepted", None),
            ("scientific_precision_budget_accepted", True),
        ]
        original = copy.deepcopy(f.qc_contract)
        for field, value in changes:
            with self.subTest(field=field):
                f.qc_contract = copy.deepcopy(original)
                f.qc_contract[field] = value
                with self.assertRaisesRegex(ValueError, "unsupported QC contract"):
                    f.check_contract()
        for field, value in (("sha256", "0" * 64), ("bytes", 1)):
            with self.subTest(recipe_pin=field):
                f.qc_contract = copy.deepcopy(original)
                f.qc_contract["reference_recipe_pin"][field] = value
                with self.assertRaisesRegex(ValueError, "input (hash|length) differs"):
                    f.check_contract()

    def test_reference_file_set_pins_and_symlinks_fail_closed(self):
        for scenario in (
            "missing_pin",
            "extra_pin",
            "pin_object",
            "wrong_hash",
            "wrong_length",
            "missing_file",
        ):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                pins = f.qc_contract["reference_files"]
                if scenario == "missing_pin":
                    del pins["qc-reference.tsv"]
                elif scenario == "extra_pin":
                    pins["extra"] = pin(f.qc_reference)
                elif scenario == "pin_object":
                    pins["qc-reference.tsv"] = None
                elif scenario == "wrong_hash":
                    pins["qc-reference.tsv"]["sha256"] = "0" * 64
                elif scenario == "wrong_length":
                    pins["qc-reference.tsv"]["bytes"] = True
                else:
                    f.qc_reference.unlink()
                with self.assertRaises((ValueError, OSError)):
                    f.check_contract()
        f = self.fixture("symlink")
        original = Path.is_symlink
        for link in (f.qc_reference, f.reference_root):
            with (
                self.subTest(link=link),
                patch.object(Path, "is_symlink", lambda p, link=link: p == link or original(p)),
                self.assertRaisesRegex(ValueError, "symlink"),
            ):
                f.check_contract()

    def test_full_orchestration_runs_four_exports_with_real_comparisons(self):
        f = self.fixture()
        self.assertEqual(f.main(), 0)
        receipt = f.receipt()
        self.assertEqual(f.observed_initial_status, "running")
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(f.preparations, [("raw", 1), ("raw", 2), ("QCDPB", 1), ("QCDPB", 2)])
        self.assertEqual(len(receipt["commands"]), 13)
        self.assertEqual([(r["stage"], r["threads"]) for r in receipt["exports"]], f.preparations)
        self.assertTrue(
            all(
                r["qc"]["metrics_checked"] == 66 and r["pvalues"]["rows"] == 8
                for r in receipt["exports"]
            )
        )
        self.assertEqual(receipt["gct_reference"], GCT_SCOPE)
        for key in (
            "scientific_admitted",
            "official_owner_device_accepted",
            "sample_rejection_policy_accepted",
        ):
            self.assertIs(receipt[key], False)

    def test_numeric_qc_or_pvalue_failure_is_preserved_after_all_four_exports(self):
        for scenario in ("numeric_qc_failure", "numeric_pvalue_failure"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                f.scenario = scenario
                self.assertEqual(f.main(), 1)
                receipt = f.receipt()
                self.assertEqual(receipt["status"], "failed")
                self.assertIn("reference comparison failed", receipt["error"])
                self.assertEqual(len(receipt["exports"]), 4)
                self.assertTrue(
                    all(command["status"] == "passed" for command in receipt["commands"])
                )
                for export in receipt["exports"]:
                    key, other = (
                        ("qc", "pvalues") if scenario == "numeric_qc_failure" else ("pvalues", "qc")
                    )
                    self.assertEqual(export[key]["status"], "failed")
                    self.assertEqual(export[other]["status"], "passed")
                    if key == "qc":
                        self.assertEqual(export[key]["metrics_failed"], 4)
                        self.assertEqual(len(export[key]["comparisons"]), 66)
                    else:
                        self.assertEqual(export[key]["serialized_mismatches"], 1)

    def test_numeric_agreement_cannot_hide_stage_or_thread_byte_variation(self):
        for scenario in ("qc_stage_variation", "binary_thread_variation", "text_thread_variation"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                f.scenario = scenario
                self.assertEqual(f.main(), 1)
                receipt = f.receipt()
                self.assertEqual(len(receipt["exports"]), 4)
                self.assertTrue(
                    all(
                        row[key]["status"] == "passed"
                        for row in receipt["exports"]
                        for key in ("qc", "pvalues")
                    )
                )
                self.assertIn(
                    "stage or thread" if scenario == "qc_stage_variation" else "thread settings",
                    receipt["error"],
                )

    def test_missing_commands_and_outputs_record_failure_without_success(self):
        for scenario in (
            "command_failure",
            "missing_tool",
            "timeout",
            "missing_binary_output",
            "missing_sample_index",
            "missing_qc_output",
            "missing_pvalue_export",
            "bad_annotation",
        ):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                f.scenario = scenario
                self.assertEqual(f.main(), 1)
                receipt = f.receipt()
                self.assertEqual(receipt["status"], "failed")
                self.assertIn("error", receipt)
                if scenario in ("command_failure", "missing_tool", "timeout"):
                    self.assertEqual(len(receipt["commands"]), 1)
                    self.assertEqual(receipt["commands"][0]["status"], "failed")

    def test_end_integrity_drift_cannot_be_hidden_by_successful_exports(self):
        scenarios = (
            "input_drift",
            "raw_reference_drift",
            "qc_reference_drift",
            "pvalue_reference_drift",
            "base_contract_drift",
            "qc_contract_drift",
            "binary_drift",
            "yame_binary_drift",
            "checker_drift",
            "preprocessing_checker_drift",
            "helper_drift",
            "recipe_drift",
            "source_drift",
            "yame_source_drift",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                f.scenario = scenario
                self.assertEqual(f.main(), 1)
                receipt = f.receipt()
                self.assertEqual(receipt["status"], "failed")
                self.assertEqual(len(receipt["exports"]), 4)
                self.assertTrue(
                    all(
                        row[key]["status"] == "passed"
                        for row in receipt["exports"]
                        for key in ("qc", "pvalues")
                    )
                )

    def test_initial_invalid_contract_and_pinned_universe_fail_before_consumption(self):
        f = self.fixture("invalid")
        f.qc_contract_path.write_text('{"schema_version":1,"schema_version":1}')
        self.assertEqual(f.main(), 1)
        self.assertEqual(f.commands, [])
        self.assertEqual(f.receipt()["status"], "failed")
        f = self.fixture("universe")
        f.contract["ordered_probe_ids_sha256"] = "0" * 64
        f.write_contract()
        f.qc_contract["preprocessing_contract_sha256"] = pin(f.contract_path)["sha256"]
        f.write_qc_contract()
        self.assertEqual(f.main(), 1)
        self.assertEqual(f.preparations, [])
        self.assertIn("pinned QC probe universe", f.receipt()["error"])

    def test_malformed_streams_leave_failed_receipts(self):
        for kind, exception_name in (
            ("truncated_gzip", "EOFError:"),
            ("invalid_deflate", "error:"),
            ("malformed_csv", "Error:"),
        ):
            with self.subTest(kind=kind):
                f = self.fixture(kind)
                if kind == "malformed_csv":
                    path = f.qc_reference
                    path.write_text('metric\tvalue\nGCT\t"unterminated')
                else:
                    path = f.pvalue_reference
                    payload = bytearray(path.read_bytes())
                    if kind == "truncated_gzip":
                        payload = payload[:10]
                    else:
                        payload[10] = 7  # Invalid DEFLATE block type, after a valid gzip header.
                    path.write_bytes(payload)
                f.qc_contract["reference_files"][path.name] = pin(path)
                f.write_qc_contract()
                self.assertEqual(f.main(), 1)
                self.assertEqual(f.receipt()["status"], "failed")
                self.assertTrue(f.receipt()["error"].startswith(exception_name))

    def test_reference_recipe_cannot_be_missing_or_linked(self):
        f = self.fixture("missing_recipe")
        f.r_recipe.unlink()
        with self.assertRaises(FileNotFoundError):
            f.check_contract()
        f = self.fixture("linked_recipe")
        target = f.root / "outside-recipe.R"
        target.write_bytes(f.r_recipe.read_bytes())
        f.r_recipe.unlink()
        f.r_recipe.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            f.check_contract()

    def test_output_must_be_new_local_and_free_of_symlinks(self):
        f = self.fixture("stale")
        f.output.mkdir(parents=True)
        receipt = f.output / "qc-contract.json"
        receipt.write_text('{"status":"passed","source_revision":"old"}')
        original_bytes = receipt.read_bytes()
        with self.assertRaises(FileExistsError):
            f.main()
        self.assertEqual(receipt.read_bytes(), original_bytes)
        self.assertEqual(f.commands, [])
        f = self.fixture("outside")
        with self.assertRaisesRegex(ValueError, "output must be under"):
            f.main(f.root / "outside")
        self.assertFalse((f.root / "outside").exists())
        original = Path.is_symlink
        for link in (f.output, f.output.parent):
            with (
                self.subTest(link=link),
                patch.object(Path, "is_symlink", lambda p, link=link: p == link or original(p)),
                self.assertRaisesRegex(ValueError, "symlinks"),
            ):
                f.main()
        self.assertFalse(f.output.exists())


if __name__ == "__main__":
    unittest.main()
