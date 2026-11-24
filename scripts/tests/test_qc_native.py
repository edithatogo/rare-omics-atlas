"""Native QC v2 lineage, complete annotation and preserved-export regressions."""

import copy
import gzip
import hashlib
import io
import json
import os
import shutil
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
from test_preprocessing import pin, table_text, write_table
from test_qc import QC_NAMES, QCFixture

NATIVE_EXTENSION = [["ext"], ["."], ["."], ["C"], ["."], ["."], ["T"], ["."], ["."]]
ABSENT_SIGNAL_NATIVE = {"num_dtna": "0", "frac_dtna": "0", "frac_dt": "0.25", "frac_dt_mk": "0.125"}
ABSENT_SIGNAL_OLD = {
    "num_dtna": "2",
    "frac_dtna": "0.25",
    "frac_dt": "0.3333333333",
    "frac_dt_mk": "0.1666666667",
}


class NativeFixture(QCFixture):
    def __init__(self, root):
        super().__init__(root)
        self.previous_reference_root = self.reference_root
        self.reference_root = root / "native-reference"
        self.reference_root.mkdir()
        self.qc_reference = self.reference_root / "qc-reference.tsv"
        self.pvalue_reference = self.reference_root / "pvalues-reference.tsv.gz"
        self.native_contract_path = root / "native-contract.json"
        self.native_recipe = root / "scripts/tests/run_native_gct_reference.R"
        self.native_recipe.write_text("synthetic independent native R recipe\n")
        self.c_regression = root / "scripts/tests/test_qc_missing_signal.c"
        self.c_regression.write_text("/* synthetic regression source identity */\n")
        self.producer_patch = root / "research/patches/sesame/native-qc-missing-signal.patch"
        self.producer_patch.parent.mkdir(parents=True)
        self.patch_text = "diff --git a/src/qc.c b/src/qc.c\n--- a/src/qc.c\n+++ b/src/qc.c\n@@ -1 +1 @@\n-old\n+native\n"
        self.producer_patch.write_text(self.patch_text)
        self.tree = "a" * 40
        self.native_git_overrides = {}
        self.actual_commands = []
        for row in self.metric_reference_rows[1:]:
            if row[0] in ABSENT_SIGNAL_NATIVE:
                row[1] = ABSENT_SIGNAL_NATIVE[row[0]]
        self.set_actual_metrics(ABSENT_SIGNAL_NATIVE)
        write_table(self.qc_reference, self.metric_reference_rows)
        write_table(self.pvalue_reference, self.pvalue_reference_rows)
        write_table(self.reference_root / "native-typeI-ext.tsv.gz", NATIVE_EXTENSION)
        (self.reference_root / "native-curated-C.ids.txt").write_text("ch000003\n")
        (self.reference_root / "native-curated-T.ids.txt").write_text("cg000005\n")
        native_object = root / "synthetic-native-object.txt"
        native_object.write_text("synthetic native annotation object\n")
        self.native_annotation = {
            "source_object": "HM450.probeInfo",
            "source_metadata_revision": "c" * 40,
            "source_version": "synthetic-version",
            "source_object_pin": pin(native_object),
            "selection": "intersect raw InfIR Probe_ID with typeI.extC and typeI.extT, separately",
            "native_curated_C": 1,
            "native_curated_T": 1,
            "ordering_sha256": self.contract["ordered_probe_ids_sha256"],
            "mask_applied": False,
            "missing_green_values": "omit per value within each mean",
            "zero_or_empty_denominator": "no coercion; nonfinite output is outside this finite-fixture contract",
        }
        self.qc_contract.update(
            contract_id="sesame-hm450-qc-v2",
            gct_annotation=copy.deepcopy(self.native_annotation),
            gct_reference="Native bisConversionControl with pinned HM450.probeInfo C/T sets intersected with raw InfIR",
            reference_scope="Unchanged native R 65-field QC panel plus independently called native bisConversionControl; not full package qualification.",
            reference_recipe="scripts/tests/run_native_gct_reference.R",
            reference_recipe_pin=pin(self.native_recipe),
            previous_contract_sha256=pin(self.qc_contract_path)["sha256"],
            parent_reference_recipe="scripts/tests/run_qc_reference.R",
            parent_reference_recipe_pin=pin(self.r_recipe),
            missing_signal_policy={
                "both_channels_absent_pvalue": 1.0,
                "num_dtna_counts": "missing p-values after native pOOBAH absent-signal handling",
                "overall_denominator": "all nonmissing p-values, including absent-signal failures",
                "unmasked_denominator": "all nonmissing p-values with existing mask false",
                "subtype_denominator": "all nonmissing p-values within the cg/ch/rs prefix",
                "empty_denominator": "NA",
                "raw_mask": "unchanged",
            },
            producer_patch={
                "path": "research/patches/sesame/native-qc-missing-signal.patch",
                "pin": pin(self.producer_patch),
                "result_tree": self.tree,
            },
            reference_files={p.name: pin(p) for p in self.reference_root.iterdir()},
        )
        self.write_native_contract()

    def set_actual_metrics(self, values):
        for name, value in values.items():
            self.metric_actual_rows[1][1 + QC_NAMES.index(name)] = value
        write_table(self.qc_actual, self.metric_actual_rows)

    def repin(self, name):
        self.qc_contract["reference_files"][name] = pin(self.reference_root / name)

    def write_native_contract(self):
        self.native_contract_path.write_text(json.dumps(self.qc_contract))

    def check_contract(self):
        with (
            patch.object(qc, "ROOT", self.root),
            patch.object(qc, "CONTRACT", self.qc_contract_path),
            patch.object(qc, "NATIVE_ANNOTATION", self.native_annotation),
            patch.object(prep, "CONTRACT", self.contract_path),
        ):
            return qc.check_contract(self.qc_contract, self.reference_root)

    def native_git(self, checkout, *args):
        key = (checkout, args)
        if key in self.native_git_overrides:
            return self.native_git_overrides[key]
        if args == ("rev-parse", "--show-toplevel"):
            return str(checkout)
        if checkout == self.checkout / "YAME" and args == ("remote", "get-url", "origin"):
            return "https://github.com/zhou-lab/YAME.git"
        if args == ("write-tree",):
            return self.tree
        if args == ("diff", "--no-ext-diff", "--no-textconv", "--name-only"):
            return ""
        if args == ("ls-files", "--others", "--exclude-standard"):
            return ""
        if args[0] == "diff" and "--full-index" in args:
            return self.patch_text.strip()
        return self.git(checkout, *args)

    def check_source(self):
        with (
            patch.object(qc, "ROOT", self.root),
            patch.object(qc, "native_git", side_effect=self.native_git),
        ):
            qc.check_qc_source(self.checkout, self.contract, self.qc_contract)

    def build_assets(self):
        return qc.native_assets(
            self.data, self.reference_root, self.output, self.ids, self.qc_contract
        )

    def execute(self, command, **kwargs):
        self.actual_commands.append(command)
        if self.observed_initial_status is None:
            self.observed_initial_status = self.receipt()["status"]
        native_root = self.output / "native-assets"
        expected_root = native_root if native_root.exists() else self.data / "assets"
        if kwargs["env"]["YAME_DATA_HOME"] != str(expected_root):
            raise AssertionError("producer did not receive the selected asset store")
        if "--mask" in command and command[command.index("--mask") + 1] != str(
            expected_root / "HM450" / prep.ASSETS[3]
        ):
            raise AssertionError("producer mask did not come from the selected asset store")
        if command[0] == "cc":
            if self.scenario == "missing_compiler":
                raise FileNotFoundError("synthetic missing C compiler")
            if command == ["cc", "--version"]:
                kwargs["stdout"].write("synthetic C compiler version\n")
            elif self.scenario == "compile_failure":
                return subprocess.CompletedProcess(command, 7)
            else:
                Path(command[command.index("-o") + 1]).write_bytes(
                    b"synthetic C regression executable"
                )
            return subprocess.CompletedProcess(command, 0)
        if command[0] == str(self.output / "test-qc-missing-signal"):
            if self.scenario == "c_regression_failure":
                return subprocess.CompletedProcess(command, 7)
            kwargs["stdout"].write("synthetic C regressions passed\n")
            return subprocess.CompletedProcess(command, 0)
        if (
            len(command) > 1
            and command[1] == "preprocess"
            and command[command.index("--output") + 1] == "beta"
        ):
            self.commands.append(command)
            stage = command[command.index("--prep") + 1] or "raw"
            threads = int(command[command.index("--threads") + 1])
            self.preparations.append((stage, threads))
            if self.scenario == "beta_command_failure":
                return subprocess.CompletedProcess(command, 7)
            target = Path(command[command.index("--out") + 1])
            target.mkdir()
            if self.scenario != "missing_beta_binary":
                payload = ("synthetic beta " + stage).encode()
                if self.scenario == "beta_thread_difference" and threads == 2:
                    payload += b"changed"
                (target / "beta.cg").write_bytes(payload)
            if self.scenario != "missing_beta_index":
                (target / "beta.cg.idx").write_text(f"{prep.SAMPLE}\t0\n")
            return subprocess.CompletedProcess(command, 0)
        if (
            len(command) > 1
            and command[1] == "describe-probe"
            and Path(command[-1]).name == "beta.cg"
        ):
            self.commands.append(command)
            target = Path(command[-1]).parent
            stage = target.name.split("-")[-2]
            rows = self.export_table(stage)
            if self.scenario == "beta_value_failure":
                rows[2][1] = "0.5"
            kwargs["stdout"].write(table_text(rows))
            if target.name == "raw-q-check-Q-2":
                if self.scenario == "native_overlay_drift":
                    path = native_root / "HM450" / prep.ASSETS[2]
                    path.write_bytes(path.read_bytes() + gzip.compress(b"", mtime=0))
                elif self.scenario == "regression_binary_drift":
                    (self.output / "test-qc-missing-signal").write_bytes(
                        b"changed regression executable"
                    )
                elif self.scenario == "native_tree_drift":
                    self.tree = "b" * 40
                elif self.scenario in (
                    "native_recipe_drift",
                    "parent_recipe_drift",
                    "native_contract_drift",
                    "previous_contract_drift",
                ):
                    path = {
                        "native_recipe_drift": self.native_recipe,
                        "parent_recipe_drift": self.r_recipe,
                        "native_contract_drift": self.native_contract_path,
                        "previous_contract_drift": self.qc_contract_path,
                    }[self.scenario]
                    path.write_bytes(path.read_bytes() + b" ")
            return subprocess.CompletedProcess(command, 0)
        # Reuse the existing fake producer only after checking the actual native paths.
        normalized = command.copy()
        if "--mask" in normalized:
            normalized[normalized.index("--mask") + 1] = str(self.assets / prep.ASSETS[3])
        legacy_kwargs = dict(kwargs)
        legacy_kwargs["env"] = {**kwargs["env"], "YAME_DATA_HOME": str(self.data / "assets")}
        return super().execute(normalized, **legacy_kwargs)

    def main(self):
        with (
            patch.object(qc, "ROOT", self.root),
            patch.object(qc, "CONTRACT", self.qc_contract_path),
            patch.object(qc, "NATIVE_ANNOTATION", self.native_annotation),
            patch.object(qc, "NATIVE_CONTRACT", self.native_contract_path),
            patch.object(qc, "__file__", str(self.qc_driver)),
            patch.object(prep, "CONTRACT", self.contract_path),
            patch.object(prep, "__file__", str(self.driver)),
            patch.object(qc, "native_git", side_effect=self.native_git),
            patch.object(prep, "git", side_effect=self.git),
            patch.object(qc.subprocess, "run", side_effect=self.execute),
            patch.object(
                sys,
                "argv",
                [
                    "qualify_qc.py",
                    "--contract",
                    "v2",
                    "--checkout",
                    str(self.checkout),
                    "--data-root",
                    str(self.data),
                    "--raw-reference",
                    str(self.reference),
                    "--reference-root",
                    str(self.reference_root),
                    "--output",
                    str(self.output),
                ],
            ),
            redirect_stdout(io.StringIO()),
        ):
            return qc.main()


class NativeQCContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def fixture(self, name="fixture"):
        return NativeFixture(self.root / name)

    def test_v1_default_contract_and_orchestration_remain_unchanged(self):
        f = QCFixture(self.root / "v1")
        self.assertEqual(set(f.check_contract()), {"qc-reference.tsv", "pvalues-reference.tsv.gz"})
        self.assertEqual(f.main(), 0)
        receipt = f.receipt()
        self.assertEqual(receipt["contract_id"], "sesame-hm450-qc-v1")
        self.assertEqual(len(receipt["exports"]), 4)
        self.assertNotIn("native_asset_sha256", receipt)
        self.assertNotIn("raw_q_exports", receipt)

    def test_literal_absent_signal_denominators_reject_the_previous_four_differences(self):
        f = self.fixture()
        self.assertEqual(
            qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)["status"], "passed"
        )
        f.set_actual_metrics(ABSENT_SIGNAL_OLD)
        result = qc.compare_qc(f.qc_reference, f.qc_actual, prep.SAMPLE)
        self.assertEqual(result["metrics_failed"], 4)
        self.assertEqual(
            {row["metric"] for row in result["comparisons"] if row["status"] == "failed"},
            set(ABSENT_SIGNAL_OLD),
        )
        self.assertEqual(result["status"], "failed")

    def test_v2_contract_rejects_semantic_lineage_and_patch_pin_changes(self):
        f = self.fixture()
        self.assertEqual(len(f.check_contract()), 5)
        original = copy.deepcopy(f.qc_contract)
        changes = [
            (("gct_annotation", "source_object"), "unrelated object"),
            (("gct_annotation", "source_metadata_revision"), "f" * 40),
            (("gct_annotation", "source_version"), "another version"),
            (("gct_annotation", "source_object_pin", "sha256"), "0" * 64),
            (("gct_annotation", "source_object_pin", "bytes"), 1),
            (("gct_annotation", "selection"), "all channels"),
            (("gct_annotation", "native_curated_C"), True),
            (("gct_annotation", "native_curated_T"), 2),
            (("gct_annotation", "ordering_sha256"), "0" * 64),
            (("gct_annotation", "mask_applied"), 0),
            (("gct_annotation", "missing_green_values"), "impute zero"),
            (("gct_annotation", "zero_or_empty_denominator"), "zero"),
            (("gct_reference",), "published-list arithmetic"),
            (("reference_scope",), "unqualified alternative"),
            (("reference_recipe",), "scripts/tests/run_qc_reference.R"),
            (("previous_contract_sha256",), "0" * 64),
            (("parent_reference_recipe",), "unrelated.R"),
            (("parent_reference_recipe_pin", "sha256"), "0" * 64),
            (("reference_recipe_pin", "bytes"), 1),
            (("missing_signal_policy", "both_channels_absent_pvalue"), True),
            (("missing_signal_policy", "overall_denominator"), "drop absent-signal probes"),
            (("missing_signal_policy", "empty_denominator"), "0"),
            (("missing_signal_policy", "raw_mask"), "recomputed"),
            (("producer_patch", "path"), "unreviewed.patch"),
            (("producer_patch", "result_tree"), "bad-tree"),
            (("producer_patch", "pin", "sha256"), "0" * 64),
        ]
        for keys, value in changes:
            with self.subTest(field=keys):
                f.qc_contract = copy.deepcopy(original)
                parent = f.qc_contract
                for key in keys[:-1]:
                    parent = parent[key]
                parent[keys[-1]] = value
                with self.assertRaises(ValueError):
                    f.check_contract()

    def test_native_source_requires_exact_patch_tree_and_clean_visible_worktrees(self):
        cases = [
            ("root", ("rev-parse", "--show-toplevel"), "wrong-root"),
            ("yame", ("rev-parse", "--show-toplevel"), "wrong-root"),
            ("yame", ("remote", "get-url", "origin"), "https://example.invalid/source"),
            ("root", ("remote", "get-url", "origin"), "https://example.invalid/source"),
            ("root", ("rev-parse", "HEAD"), "f" * 40),
            ("yame", ("rev-parse", "HEAD"), "f" * 40),
            ("root", ("ls-files", "-v"), "h hidden\n"),
            ("yame", ("ls-files", "-v"), "S hidden\n"),
            ("root", ("write-tree",), "f" * 40),
            ("root", ("diff", "--no-ext-diff", "--no-textconv", "--name-only"), "src/qc.c"),
            ("root", ("ls-files", "--others", "--exclude-standard"), "untracked.c"),
            ("yame", ("status", "--porcelain", "--untracked-files=all"), " M source.c"),
        ]
        for number, (where, args, value) in enumerate(cases):
            with self.subTest(where=where, args=args):
                f = self.fixture(str(number))
                f.check_source()
                path = f.checkout if where == "root" else f.checkout / "YAME"
                f.native_git_overrides[(path, args)] = value
                with self.assertRaises(ValueError):
                    f.check_source()
        f = self.fixture("patch")
        f.patch_text += "+unreviewed change\n"
        with self.assertRaisesRegex(ValueError, "producer patch differs"):
            f.check_source()
        f = self.fixture("source-symlink")
        actual_is_symlink = Path.is_symlink
        selected = f.checkout / "YAME"
        with patch.object(
            Path, "is_symlink", lambda path: path == selected or actual_is_symlink(path)
        ):
            with self.assertRaisesRegex(ValueError, "symlink"):
                f.check_source()

    def test_native_git_removes_caller_git_redirection_and_global_configuration(self):
        with (
            patch.dict(
                os.environ, {"GIT_DIR": "/wrong", "GIT_CONFIG_COUNT": "1", "KEEP_ME": "yes"}
            ),
            patch.object(qc.subprocess, "check_output", return_value="answer\n") as run,
        ):
            self.assertEqual(qc.native_git(self.root, "rev-parse", "HEAD"), "answer")
        environment = run.call_args.kwargs["env"]
        self.assertNotIn("GIT_DIR", environment)
        self.assertNotIn("GIT_CONFIG_COUNT", environment)
        self.assertEqual(environment["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(environment["GIT_CONFIG_GLOBAL"], os.devnull)
        self.assertEqual(environment["KEEP_ME"], "yes")
        self.assertIn("core.fsmonitor=false", run.call_args.args[0])
        self.assertIn("--no-replace-objects", run.call_args.args[0])

    def test_native_overlay_preserves_four_original_assets_and_complete_literal_extension(self):
        f = self.fixture()
        original = {name: pin(f.assets / name) for name in prep.ASSETS}
        root, hashes = f.build_assets()
        self.assertEqual(root, f.output / "native-assets")
        with gzip.open(root / "HM450" / prep.ASSETS[2], "rt") as stream:
            self.assertEqual(stream.read(), "ext\n.\n.\nC\n.\n.\nT\n.\n.\n")
        self.assertEqual(set(hashes), set(prep.ASSETS))
        for name in prep.ASSETS:
            expected = (
                pin(f.reference_root / "native-typeI-ext.tsv.gz")
                if name == prep.ASSETS[2]
                else original[name]
            )
            self.assertEqual(pin(root / "HM450" / name), expected)
            self.assertEqual(pin(f.assets / name), original[name])
        before = {name: pin(root / "HM450" / name) for name in prep.ASSETS}
        with self.assertRaises(FileExistsError):
            f.build_assets()
        self.assertEqual({name: pin(root / "HM450" / name) for name in prep.ASSETS}, before)

    def test_native_sets_reject_empty_duplicate_unknown_and_overlapping_identities(self):
        for scenario, content in (
            ("empty", ""),
            ("duplicate", "ch000003\nch000003\n"),
            ("unknown", "unlisted\n"),
            ("overlap", "cg000005\n"),
        ):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                name = "native-curated-C.ids.txt"
                (f.reference_root / name).write_text(content)
                f.repin(name)
                with self.assertRaises(ValueError):
                    f.build_assets()
                self.assertFalse((f.output / "native-assets").exists())

    def test_native_set_counts_and_order_are_bound_to_the_annotation_declaration(self):
        for scenario in ("C_count", "T_count", "order", "duplicate"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                annotation = f.qc_contract["gct_annotation"]
                if scenario.endswith("_count"):
                    annotation["native_curated_" + scenario[0]] = 2
                elif scenario == "order":
                    f.ids.reverse()
                else:
                    f.ids[1] = f.ids[0]
                    annotation["ordering_sha256"] = hashlib.sha256(
                        "".join(probe + "\n" for probe in f.ids).encode()
                    ).hexdigest()
                expected = (
                    "set count differs" if scenario.endswith("_count") else "ordering lineage"
                )
                with self.assertRaisesRegex(ValueError, expected):
                    f.build_assets()

    def test_native_overlay_rejects_schema_row_order_channel_and_extension_corruption(self):
        scenarios = (
            "schema",
            "drop",
            "extra",
            "width",
            "missing_C",
            "extra_C",
            "order",
            "identity",
            "raw_channel",
            "ordering_width",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                ext = copy.deepcopy(NATIVE_EXTENSION)
                order = copy.deepcopy(f.ordering)
                if scenario == "schema":
                    ext[0] = ["other"]
                elif scenario == "drop":
                    ext.pop()
                elif scenario == "extra":
                    ext.append(["."])
                elif scenario == "width":
                    ext[1].append(".")
                elif scenario == "missing_C":
                    ext[3] = ["."]
                elif scenario == "extra_C":
                    ext[1] = ["C"]
                elif scenario == "order":
                    order[1:3] = reversed(order[1:3])
                elif scenario == "identity":
                    order[2][0] = order[1][0]
                elif scenario == "raw_channel":
                    order[3][3] = "G"
                else:
                    order[3].pop()
                write_table(f.reference_root / "native-typeI-ext.tsv.gz", ext)
                f.repin("native-typeI-ext.tsv.gz")
                write_table(f.assets / prep.ASSETS[0], order)
                with self.assertRaises(ValueError):
                    f.build_assets()

    def test_native_assets_reject_missing_symlinked_or_corrupted_copies(self):
        f = self.fixture("missing")
        (f.reference_root / "native-curated-T.ids.txt").unlink()
        with self.assertRaises(OSError):
            f.build_assets()
        f = self.fixture("symlink")
        actual_is_symlink = Path.is_symlink
        selected = f.reference_root / "native-curated-C.ids.txt"
        with patch.object(
            Path, "is_symlink", lambda path: path == selected or actual_is_symlink(path)
        ):
            with self.assertRaisesRegex(ValueError, "symlink"):
                f.build_assets()
        f = self.fixture("copy")
        actual_copy = shutil.copyfile

        def corrupt_copy(source, target):
            actual_copy(source, target)
            Path(target).write_bytes(Path(target).read_bytes() + b"changed")

        with patch.object(qc.shutil, "copyfile", side_effect=corrupt_copy):
            with self.assertRaisesRegex(ValueError, "copy differs"):
                f.build_assets()

    def test_native_main_runs_all_eight_exports_and_keeps_admission_false(self):
        f = self.fixture()
        self.assertEqual(f.main(), 0, f.receipt())
        result = f.receipt()
        self.assertEqual(f.observed_initial_status, "running")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["contract_id"], "sesame-hm450-qc-v2")
        self.assertEqual(len(result["exports"]), 4)
        self.assertEqual(len(result["raw_q_exports"]), 4)
        self.assertEqual(
            {(r["stage"], r["threads"]) for r in result["raw_q_exports"]},
            {("raw", 1), ("raw", 2), ("Q", 1), ("Q", 2)},
        )
        self.assertTrue(
            all(r["rows"] == 8 and r["status"] == "passed" for r in result["raw_q_exports"])
        )
        self.assertFalse(result["scientific_admitted"])
        self.assertFalse(result["official_owner_device_accepted"])
        self.assertEqual(set(result["native_asset_sha256"]), set(prep.ASSETS))
        self.assertEqual(result["gct_annotation"], f.native_annotation)
        saved = (f.output / "qc-contract.json").read_bytes()
        with self.assertRaises(FileExistsError):
            f.main()
        self.assertEqual((f.output / "qc-contract.json").read_bytes(), saved)

    def test_wrong_gct_or_old_missing_signal_outputs_keep_failed_receipts_and_beta_checks(self):
        for scenario, values in (("old_counts", ABSENT_SIGNAL_OLD), ("wrong_GCT", {"GCT": "0.5"})):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                f.set_actual_metrics(values)
                self.assertEqual(f.main(), 1)
                receipt = f.receipt()
                self.assertEqual(receipt["status"], "failed")
                self.assertEqual(len(receipt["exports"]), 4)
                self.assertEqual(len(receipt["raw_q_exports"]), 4)
                self.assertTrue(
                    all(row["qc"]["metrics_failed"] == len(values) for row in receipt["exports"])
                )
                self.assertTrue(
                    all(row["pvalues"]["status"] == "passed" for row in receipt["exports"])
                )
                self.assertTrue(all(row["status"] == "passed" for row in receipt["raw_q_exports"]))

    def test_beta_failures_and_late_native_integrity_drift_cannot_leave_a_success_receipt(self):
        scenarios = (
            "missing_compiler",
            "compile_failure",
            "c_regression_failure",
            "regression_binary_drift",
            "beta_command_failure",
            "missing_beta_binary",
            "missing_beta_index",
            "beta_value_failure",
            "beta_thread_difference",
            "native_overlay_drift",
            "native_tree_drift",
            "native_recipe_drift",
            "parent_recipe_drift",
            "native_contract_drift",
            "previous_contract_drift",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                f.scenario = scenario
                self.assertEqual(f.main(), 1)
                self.assertEqual(f.receipt()["status"], "failed")
                self.assertIn("error", f.receipt())


if __name__ == "__main__":
    unittest.main()
