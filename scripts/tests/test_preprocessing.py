"""Named-universe and failure-propagation tests for the technical qualifier.

The eight-row fixture deliberately retains cg/ch/rs/control probes, NA, finite
values, exact endpoints and values that collapse to endpoints on serialization.
External tools are mocked; parsing, pin checks, exports and receipts are real.
"""

import copy
import csv
import gzip
import hashlib
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
import qualify_preprocessing as qualifier


def table_text(rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, delimiter="\t", lineterminator="\n").writerows(rows)
    return stream.getvalue()


def write_table(path, rows):
    payload = table_text(rows).encode()
    path.write_bytes(gzip.compress(payload, mtime=0) if path.suffix == ".gz" else payload)


def pin(path):
    payload = path.read_bytes()
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


class Fixture:
    """A complete small data space, with only external command execution replaced."""

    def __init__(self, root):
        self.root = root
        self.data = root / "data"
        self.assets = self.data / "assets/HM450"
        self.checkout = root / "source"
        self.output = root / "artifacts/verification/run"
        self.reference = root / "reference.tsv.gz"
        self.annotation = root / "annotation.tsv"
        self.actual = root / "beta.tsv"
        self.index = root / "beta.cg.idx"
        self.contract_path = root / "contract.json"
        self.driver = root / "checker/qualify_preprocessing.py"
        self.helper = self.driver.with_name("qualify_limma.py")
        for path in (
            self.assets,
            self.data / "idats/HM450",
            self.checkout / "YAME",
            self.driver.parent,
        ):
            path.mkdir(parents=True)
        self.driver.write_text("synthetic checker identity\n")
        self.helper.write_text("synthetic shared helper identity\n")
        self.ids = [
            "cg000001",
            "cg000002",
            "ch000003",
            "rs000004",
            "control-1",
            "cg000005",
            "cg000006",
            "cg000007",
        ]
        self.ordering = [
            ["Probe_ID", "M", "U", "col"],
            [self.ids[0], "NA", "11", "2"],
            [self.ids[1], "12", "13", "G"],
            [self.ids[2], "14", "15", "R"],
            [self.ids[3], "NA", "16", "2"],
            [self.ids[4], "17", "18", "G"],
            [self.ids[5], "19", "20", "R"],
            [self.ids[6], "NA", "21", "2"],
            [self.ids[7], "22", "23", "G"],
        ]
        self.coordinates = [
            ["CpG_chrm", "CpG_beg", "strand", "mapQ"],
            ["chr1", "0", "+", "60"],
            ["chr1", "101", "-", "60"],
            ["chrX", "201", "+", "60"],
            ["chrY", "301", "+", "60"],
            ["NA", "NA", "NA", "NA"],
            ["chr2", "401", "-", "60"],
            ["chr2", "501", "+", "60"],
            ["chr3", "601", "+", "60"],
        ]
        self.extensions = [["ext"], ["NA"], ["A"], ["C"], ["NA"], ["G"], ["T"], ["NA"], ["A"]]
        self.annotation_table = [
            ["Probe_ID", "CpG_chrm", "CpG_beg", "strand", "mapQ"],
            *[[probe, *coord] for probe, coord in zip(self.ids, self.coordinates[1:], strict=True)],
        ]
        raw = ["0", "1", "0.2", "NA", "0.123456789", "0.99999999", "1e-50", "0.25"]
        q = ["NA", "1", "0.2", "NA", "0.123456789", "0.99999999", "1e-50", "NA"]
        self.reference_table = [
            list(qualifier.REFERENCE_COLUMNS),
            *[
                [probe, order[3], "1", "1", a, "1" if b == "NA" else "0", b]
                for probe, order, a, b in zip(self.ids, self.ordering[1:], raw, q, strict=True)
            ],
        ]
        # Literal producer text, independent of serialized_beta's implementation.
        self.serialized = {
            "raw": ["0", "1", "0.2", "NA", "0.123457", "1", "0", "0.25"],
            "Q": ["NA", "1", "0.2", "NA", "0.123457", "1", "0", "NA"],
        }
        write_table(self.assets / qualifier.ASSETS[0], self.ordering)
        write_table(self.assets / qualifier.ASSETS[1], self.coordinates)
        write_table(self.assets / qualifier.ASSETS[2], self.extensions)
        for name in qualifier.INPUT_NAMES:
            path = self.data / name
            if not path.exists():
                path.write_bytes(("synthetic bytes: " + name).encode())
        write_table(self.reference, self.reference_table)
        write_table(self.annotation, self.annotation_table)
        write_table(self.actual, self.export_table("raw"))
        self.index.write_text(f"{qualifier.SAMPLE}\t0\n")
        self.contract = json.loads(qualifier.CONTRACT.read_text())
        self.contract.update(
            inputs={name: pin(self.data / name) for name in qualifier.INPUT_NAMES},
            reference=pin(self.reference),
            probe_count=len(self.ids),
            ordered_probe_ids_sha256=hashlib.sha256(
                "".join(probe + "\n" for probe in self.ids).encode()
            ).hexdigest(),
        )
        self.revisions = {
            self.checkout: self.contract["source_revision"],
            self.checkout / "YAME": self.contract["yame_revision"],
        }
        self.write_contract()
        self.git_overrides = {}
        self.commands = []
        self.preparations = []
        self.scenario = "success"
        self.observed_initial_status = None

    def write_contract(self):
        self.contract_path.write_text(json.dumps(self.contract))

    def export_table(self, stage):
        return [
            ["Probe_ID", qualifier.SAMPLE],
            *[list(pair) for pair in zip(self.ids, self.serialized[stage], strict=True)],
        ]

    def git(self, checkout, *args):
        key = (checkout, args)
        if key in self.git_overrides:
            return self.git_overrides[key]
        if args == ("rev-parse", "--show-toplevel"):
            return str(self.checkout)
        if args == ("remote", "get-url", "origin"):
            return qualifier.REPOSITORY
        if args == ("rev-parse", "HEAD"):
            return self.revisions[checkout]
        if args == ("status", "--porcelain", "--untracked-files=all"):
            return ""
        if args == ("ls-files", "-v"):
            return "H tracked-source\nH nested/source\n"
        raise AssertionError(f"unexpected git operation: {args}")

    def execute(self, command, **kwargs):
        self.commands.append(command)
        if self.observed_initial_status is None:
            self.observed_initial_status = json.loads(
                (self.output / "preprocessing-contract.json").read_text()
            )["status"]
        assert kwargs["cwd"] == self.checkout
        assert kwargs["env"]["YAME_DATA_HOME"] == str(self.data / "assets")
        assert kwargs["check"] is False
        assert kwargs["timeout"] == 1200
        if self.scenario == "missing_tool":
            raise FileNotFoundError("synthetic missing make")
        if self.scenario == "timeout":
            raise subprocess.TimeoutExpired(command, 1200)
        if self.scenario == "command_failure":
            kwargs["stderr"].write("synthetic command failure\n")
            return subprocess.CompletedProcess(command, 7)
        if command == ["make", "clean"]:
            (self.checkout / "sesame").unlink(missing_ok=True)
        elif command == ["make", "-C", "YAME", "clean"]:
            (self.checkout / "YAME/yame").unlink(missing_ok=True)
        elif command == ["make", "-j2", "sesame"]:
            (self.checkout / "sesame").write_bytes(b"synthetic freshly built sesame")
            (self.checkout / "YAME/yame").write_bytes(b"synthetic freshly built yame")
        elif command[1] == "version":
            kwargs["stdout"].write("synthetic pinned producer\n")
        elif command[1] == "preprocess":
            stage = command[command.index("--prep") + 1] or "raw"
            threads = int(command[command.index("--threads") + 1])
            self.preparations.append((stage, threads))
            assert command[command.index("--min-beads") + 1] == "0"
            assert command[command.index("--mask") + 1] == str(self.assets / qualifier.ASSETS[3])
            target = Path(command[command.index("--out") + 1])
            target.mkdir()
            if self.scenario != "missing_binary_output":
                (target / "beta.cg").write_bytes(f"synthetic {stage} {threads}".encode())
            if self.scenario != "missing_sample_index":
                sample = (
                    "wrong-sample" if self.scenario == "wrong_sample_index" else qualifier.SAMPLE
                )
                (target / "beta.cg.idx").write_text(f"{sample}\t0\n")
        elif command[1] == "describe-probe" and "--all" not in command:
            rows = copy.deepcopy(self.annotation_table)
            if self.scenario == "bad_annotation":
                rows[1][2] = "99999"
            kwargs["stdout"].write(table_text(rows))
        elif command[1] == "describe-probe" and "--all" in command:
            target = Path(command[-1]).parent
            stage = target.name.split("-")[0]
            rows = self.export_table(stage)
            if self.scenario == "bad_beta":
                rows[1][1] = "0.5"
            kwargs["stdout"].write(table_text(rows))
            if target.name == "Q-2":
                self.mutate_after_last_export()
        else:
            raise AssertionError(f"unexpected external command: {command}")
        return subprocess.CompletedProcess(command, 0)

    def mutate_after_last_export(self):
        paths = {
            "input_drift": self.data / sorted(qualifier.INPUT_NAMES)[0],
            "reference_drift": self.reference,
            "contract_drift": self.contract_path,
            "binary_drift": self.checkout / "sesame",
            "yame_binary_drift": self.checkout / "YAME/yame",
            "checker_drift": self.driver,
            "helper_drift": self.helper,
        }
        if self.scenario in paths:
            path = paths[self.scenario]
            # A valid empty gzip member keeps all reference rows readable, so
            # the final pin check must catch this change after all four exports.
            extra = gzip.compress(b"", mtime=0) if self.scenario == "reference_drift" else b" "
            path.write_bytes(path.read_bytes() + extra)
        elif self.scenario == "source_drift":
            self.git_overrides[(self.checkout, ("rev-parse", "HEAD"))] = "f" * 40
        elif self.scenario == "yame_source_drift":
            self.git_overrides[(self.checkout / "YAME", ("rev-parse", "HEAD"))] = "f" * 40

    def main(self, output=None):
        output = self.output if output is None else output
        with (
            patch.object(qualifier, "ROOT", self.root),
            patch.object(qualifier, "CONTRACT", self.contract_path),
            patch.object(qualifier, "__file__", str(self.driver)),
            patch.object(qualifier, "git", side_effect=self.git),
            patch.object(qualifier.subprocess, "run", side_effect=self.execute),
            patch.object(
                sys,
                "argv",
                [
                    "qualify_preprocessing.py",
                    "--checkout",
                    str(self.checkout),
                    "--data-root",
                    str(self.data),
                    "--reference",
                    str(self.reference),
                    "--output",
                    str(output),
                ],
            ),
            redirect_stdout(io.StringIO()),
        ):
            return qualifier.main()

    def receipt(self):
        return json.loads((self.output / "preprocessing-contract.json").read_text())


class PreprocessingContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def fixture(self, name="fixture"):
        return Fixture(self.root / name)

    def test_annotations_preserve_every_probe_kind_and_coordinate(self):
        f = self.fixture()
        ids, summary = qualifier.annotation_rows(f.assets, f.annotation)
        self.assertEqual(ids, f.ids)
        self.assertEqual(summary["rows"], 8)
        self.assertEqual(summary["probe_kinds"], {"cg": 5, "ch": 1, "rs": 1, "control": 1})
        self.assertEqual(summary["channels"], {"2": 3, "G": 3, "R": 2})
        self.assertEqual(summary["coordinate_contigs"]["NA"], 1)
        self.assertEqual(
            summary["ordered_probe_ids_sha256"], f.contract["ordered_probe_ids_sha256"]
        )

    def test_annotation_schemas_widths_and_counts_are_checked_for_all_companions(self):
        for stream in range(4):
            for corruption in ("schema", "width", "drop", "extra"):
                with self.subTest(stream=stream, corruption=corruption):
                    f = self.fixture(f"{stream}-{corruption}")
                    paths = [f.assets / name for name in qualifier.ASSETS[:3]] + [f.annotation]
                    tables = [f.ordering, f.coordinates, f.extensions, f.annotation_table]
                    rows = copy.deepcopy(tables[stream])
                    if corruption == "schema":
                        rows[0][0] = "incorrect-column"
                    elif corruption == "width":
                        rows[1].append("extra-column")
                    elif corruption == "drop":
                        rows.pop()
                    else:
                        rows.append(rows[-1])
                    write_table(paths[stream], rows)
                    with self.assertRaises(ValueError):
                        qualifier.annotation_rows(f.assets, f.annotation)

    def test_annotation_identity_alignment_and_duplicate_universe_fail(self):
        for scenario in ("coordinate", "reorder", "duplicate", "empty", "blank_probe"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                if scenario == "coordinate":
                    f.annotation_table[1][2] = "1"
                elif scenario == "reorder":
                    f.annotation_table[1:3] = reversed(f.annotation_table[1:3])
                elif scenario == "duplicate":
                    f.ordering[2][0] = f.ordering[1][0]
                    f.annotation_table[2][0] = f.ordering[1][0]
                elif scenario == "blank_probe":
                    f.ordering[1][0] = f.annotation_table[1][0] = " "
                else:
                    for rows in (f.ordering, f.coordinates, f.extensions, f.annotation_table):
                        del rows[1:]
                for name, rows in zip(
                    qualifier.ASSETS[:3], (f.ordering, f.coordinates, f.extensions), strict=True
                ):
                    write_table(f.assets / name, rows)
                write_table(f.annotation, f.annotation_table)
                with self.assertRaises(ValueError):
                    qualifier.annotation_rows(f.assets, f.annotation)

    def test_annotation_address_and_channel_semantics_fail_closed(self):
        mutations = [
            (1, 3, "X"),
            (1, 1, "12"),
            (1, 2, "0"),
            (1, 2, "-1"),
            (1, 2, "NA"),
            (2, 1, "NA"),
            (2, 1, "0"),
            (2, 1, "1.5"),
        ]
        for number, (row, column, value) in enumerate(mutations):
            with self.subTest(row=row, column=column, value=value):
                f = self.fixture(str(number))
                f.ordering[row][column] = value
                write_table(f.assets / qualifier.ASSETS[0], f.ordering)
                with self.assertRaisesRegex(ValueError, "identity/channel|address semantics"):
                    qualifier.annotation_rows(f.assets, f.annotation)

    def test_full_raw_and_q_exports_preserve_na_and_report_endpoint_losses(self):
        f = self.fixture()
        for stage, missing, endpoints in (("raw", 1, 2), ("Q", 3, 1)):
            with self.subTest(stage=stage):
                write_table(f.actual, f.export_table(stage))
                result = qualifier.validate_export(
                    f.reference, f.actual, f.index, f.ids, stage, qualifier.SAMPLE
                )
                self.assertEqual(result["rows"], 8)
                self.assertEqual(result["missing"], missing)
                self.assertEqual(result["finite"], 8 - missing)
                self.assertEqual(result["reference_endpoints"], endpoints)
                self.assertEqual(result["finite_to_endpoint_collapses"], 2)
                self.assertAlmostEqual(
                    result["maximum_absolute_beta_serialization_error"],
                    0.123457 - 0.123456789,
                    places=15,
                )
                self.assertGreater(result["maximum_finite_absolute_m_serialization_error"], 0)
                self.assertFalse(result["scientific_m_error_budget_accepted"])

    def test_beta_tokens_and_binary32_serialization_boundary(self):
        self.assertIsNone(qualifier.beta_value("NA"))
        for token, number in (("0", 0), ("1", 1), ("0.25", 0.25)):
            self.assertEqual(qualifier.beta_value(token), number)
        for token in ("NaN", "nan", "Inf", "-inf", "", "null", "N/A", "-0.1", "1.1"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                qualifier.beta_value(token)
        for number, expected in ((0.123456789, 0.123457), (0.99999999, 1), (1e-50, 0)):
            self.assertEqual(qualifier.serialized_beta(number), expected)

    def test_export_rejects_schema_order_drop_duplicate_and_added_rows(self):
        for stream in ("actual", "reference"):
            for corruption in ("schema", "order", "drop", "duplicate", "extra", "width"):
                with self.subTest(stream=stream, corruption=corruption):
                    f = self.fixture(stream + corruption)
                    rows = f.export_table("raw") if stream == "actual" else f.reference_table
                    if corruption == "schema":
                        rows[0][0] = "wrong-column"
                    elif corruption == "order":
                        rows[1:3] = reversed(rows[1:3])
                    elif corruption == "drop":
                        rows.pop()
                    elif corruption == "duplicate":
                        rows[2] = rows[1]
                    elif corruption == "extra":
                        rows.append(rows[-1])
                    else:
                        rows[1].append("extra-column")
                    write_table(f.actual if stream == "actual" else f.reference, rows)
                    with self.assertRaises(ValueError):
                        qualifier.validate_export(
                            f.reference, f.actual, f.index, f.ids, "raw", qualifier.SAMPLE
                        )

    def test_export_rejects_missingness_and_unserialized_or_changed_values(self):
        for number, (row, value) in enumerate(
            ((4, "0"), (3, "NA"), (5, "0.123456789"), (5, "0.123458"))
        ):
            with self.subTest(row=row, value=value):
                f = self.fixture(str(number))
                rows = f.export_table("raw")
                rows[row][1] = value
                write_table(f.actual, rows)
                with self.assertRaisesRegex(ValueError, "reference NA|production beta"):
                    qualifier.validate_export(
                        f.reference, f.actual, f.index, f.ids, "raw", qualifier.SAMPLE
                    )

    def test_export_sample_index_header_and_stage_are_bound(self):
        for number, index in enumerate(
            ("other\t0\n", f"{qualifier.SAMPLE}\t1\n", f"{qualifier.SAMPLE}\t0", "")
        ):
            with self.subTest(index=index):
                f = self.fixture(str(number))
                f.index.write_text(index)
                with self.assertRaisesRegex(ValueError, "sample index"):
                    qualifier.validate_export(
                        f.reference, f.actual, f.index, f.ids, "raw", qualifier.SAMPLE
                    )
        f = self.fixture("header")
        rows = f.export_table("raw")
        rows[0][1] = "other-sample"
        write_table(f.actual, rows)
        with self.assertRaisesRegex(ValueError, "beta schema"):
            qualifier.validate_export(
                f.reference, f.actual, f.index, f.ids, "raw", qualifier.SAMPLE
            )
        with self.assertRaisesRegex(ValueError, "unsupported preprocessing stage"):
            qualifier.validate_export(
                f.reference, f.actual, f.index, f.ids, "QCDPB", qualifier.SAMPLE
            )

    def test_input_contract_binds_all_files_and_supported_semantics(self):
        f = self.fixture()
        hashes = qualifier.check_inputs(f.data, f.reference, f.contract)
        self.assertEqual(set(hashes), qualifier.INPUT_NAMES | {"independent_reference"})
        cases = [
            ("schema_version", True),
            ("schema_version", 2),
            ("contract_id", "different"),
            ("source_repository", "https://wrong.example/repo"),
            ("sample", "other"),
            ("platform", "EPIC"),
            ("genome_build", "hg19"),
            ("minimum_beads", True),
            ("minimum_beads", 1),
            ("stages", ["Q", "raw"]),
            ("threads", [True, 2]),
            ("threads", [1]),
            ("q_tracks", []),
            ("q_tracks", list(reversed(f.contract["q_tracks"]))),
            ("scientific_admitted", True),
            ("official_owner_device_accepted", 0),
            ("full_qcdpb_accepted", None),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                contract = copy.deepcopy(f.contract)
                contract[key] = value
                with self.assertRaisesRegex(ValueError, "unsupported"):
                    qualifier.check_inputs(f.data, f.reference, contract)

    def test_input_object_shapes_file_sets_and_strict_pin_types(self):
        f = self.fixture()
        first = sorted(qualifier.INPUT_NAMES)[0]
        for scenario in (
            "inputs_object",
            "pin_object",
            "reference_object",
            "missing_input",
            "extra_input",
            "boolean_length",
            "wrong_length",
            "wrong_hash",
        ):
            with self.subTest(scenario=scenario):
                contract = copy.deepcopy(f.contract)
                if scenario == "inputs_object":
                    contract["inputs"] = []
                elif scenario == "pin_object":
                    contract["inputs"][first] = "not-an-object"
                elif scenario == "reference_object":
                    contract["reference"] = None
                elif scenario == "missing_input":
                    del contract["inputs"][first]
                elif scenario == "extra_input":
                    contract["inputs"]["unrequested"] = contract["inputs"][first]
                else:
                    key, value = {
                        "boolean_length": ("bytes", True),
                        "wrong_length": ("bytes", 0),
                        "wrong_hash": ("sha256", "0" * 64),
                    }[scenario]
                    contract["inputs"][first][key] = value
                with self.assertRaises(ValueError):
                    qualifier.check_inputs(f.data, f.reference, contract)

    def test_input_or_reference_byte_drift_and_missing_file_fail(self):
        for scenario in ("input", "reference", "missing"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                path = (
                    f.reference
                    if scenario == "reference"
                    else f.data / sorted(qualifier.INPUT_NAMES)[0]
                )
                if scenario == "missing":
                    path.unlink()
                else:
                    raw = path.read_bytes()
                    path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
                with self.assertRaises((ValueError, OSError)):
                    qualifier.check_inputs(f.data, f.reference, f.contract)

    def test_input_symlink_and_ancestor_are_rejected_before_reading(self):
        f = self.fixture()
        path = f.data / sorted(qualifier.INPUT_NAMES)[0]
        original = Path.is_symlink
        # Exercise link rejection without needing Windows symlink privileges.
        for link in (path, path.parent):
            with (
                self.subTest(link=link),
                patch.object(Path, "is_symlink", lambda p, link=link: p == link or original(p)),
                patch.object(qualifier, "digest") as digest,
            ):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    qualifier.checked_file(path, pin(path))
                digest.assert_not_called()

    def test_source_requires_exact_origin_roots_commits_and_visible_clean_indexes(self):
        cases = [
            ("root", ("rev-parse", "--show-toplevel"), "nested"),
            ("root", ("remote", "get-url", "origin"), "https://wrong.example/repo"),
            ("root", ("rev-parse", "HEAD"), "f" * 40),
            ("yame", ("rev-parse", "HEAD"), "f" * 40),
            ("root", ("status", "--porcelain", "--untracked-files=all"), " M source"),
            ("yame", ("status", "--porcelain", "--untracked-files=all"), "?? extra"),
            ("root", ("ls-files", "-v"), "h assumed-unchanged"),
            ("yame", ("ls-files", "-v"), "S skip-worktree"),
        ]
        f = self.fixture("clean")
        with patch.object(qualifier, "git", side_effect=f.git):
            qualifier.check_source(f.checkout, f.contract)
        for number, (where, command, value) in enumerate(cases):
            with self.subTest(where=where, command=command):
                f = self.fixture(str(number))
                f.git_overrides[
                    (f.checkout if where == "root" else f.checkout / "YAME", command)
                ] = value
                with (
                    patch.object(qualifier, "git", side_effect=f.git),
                    self.assertRaises(ValueError),
                ):
                    qualifier.check_source(f.checkout, f.contract)

    def test_source_revisions_and_symlinks_fail_before_external_checks(self):
        for value in (None, "main", "a" * 39, "A" * 40, 123):
            with self.subTest(value=value), self.assertRaises(ValueError):
                qualifier.revision({"source_revision": value}, "source_revision")
        f = self.fixture()
        original = Path.is_symlink
        for link in (f.checkout, f.checkout / "YAME", f.checkout.parent):
            with (
                self.subTest(link=link),
                patch.object(Path, "is_symlink", lambda p, link=link: p == link or original(p)),
                patch.object(qualifier, "git") as git,
            ):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    qualifier.check_source(f.checkout, f.contract)
                git.assert_not_called()

    def test_orchestrator_runs_all_four_real_contract_exports_then_records_success(self):
        f = self.fixture()
        self.assertEqual(f.main(), 0)
        receipt = f.receipt()
        self.assertEqual(f.observed_initial_status, "running")
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(f.preparations, [("raw", 1), ("raw", 2), ("Q", 1), ("Q", 2)])
        self.assertEqual(
            [(row["stage"], row["threads"]) for row in receipt["exports"]], f.preparations
        )
        self.assertEqual(len(receipt["commands"]), 13)
        self.assertTrue(all(row["status"] == "passed" for row in receipt["commands"]))
        self.assertTrue(all(row["rows"] == 8 for row in receipt["exports"]))
        for key in ("scientific_admitted", "official_owner_device_accepted", "full_qcdpb_accepted"):
            self.assertIs(receipt[key], False)
        self.assertEqual(
            receipt["implementation_sha256"],
            {p.name: pin(p)["sha256"] for p in (f.driver, f.helper)},
        )
        self.assertEqual(receipt["yame_binary_sha256"], pin(f.checkout / "YAME/yame")["sha256"])

    def test_orchestrator_failure_paths_never_leave_a_success_receipt(self):
        scenarios = (
            "command_failure",
            "missing_tool",
            "timeout",
            "bad_annotation",
            "bad_beta",
            "missing_binary_output",
            "missing_sample_index",
            "wrong_sample_index",
            "input_drift",
            "reference_drift",
            "contract_drift",
            "binary_drift",
            "yame_binary_drift",
            "checker_drift",
            "helper_drift",
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
                self.assertEqual(f.observed_initial_status, "running")
                self.assertIn("error", receipt)
                self.assertIs(receipt["scientific_admitted"], False)
                if scenario in ("command_failure", "missing_tool", "timeout"):
                    self.assertEqual(len(receipt["commands"]), 1)
                    command = receipt["commands"][0]
                    self.assertEqual(command["status"], "failed")
                    self.assertIn("elapsed_seconds", command)
                    if scenario == "command_failure":
                        self.assertEqual(command["exit_code"], 7)
                        self.assertIn(
                            "synthetic command failure", (f.output / command["stderr"]).read_text()
                        )
                    else:
                        self.assertIn("error", command)
                if scenario.endswith("_drift"):
                    self.assertEqual(len(receipt["exports"]), 4)

    def test_wrong_pinned_universe_fails_before_any_preprocessing(self):
        for key, value in (
            ("probe_count", 7),
            ("probe_count", True),
            ("ordered_probe_ids_sha256", "0" * 64),
        ):
            with self.subTest(key=key, value=value):
                f = self.fixture(key + str(value))
                f.contract[key] = value
                f.write_contract()
                self.assertEqual(f.main(), 1)
                self.assertEqual(f.preparations, [])
                self.assertIn("pinned probe universe", f.receipt()["error"])

    def test_invalid_initial_contract_or_pins_fail_before_any_external_command(self):
        for scenario in ("duplicate_key", "non_object", "missing_reference", "bad_hash"):
            with self.subTest(scenario=scenario):
                f = self.fixture(scenario)
                if scenario == "duplicate_key":
                    f.contract_path.write_text('{"schema_version":1,"schema_version":1}')
                elif scenario == "non_object":
                    f.contract_path.write_text("[]")
                elif scenario == "missing_reference":
                    f.reference.unlink()
                else:
                    f.contract["reference"]["sha256"] = "0" * 64
                    f.write_contract()
                self.assertEqual(f.main(), 1)
                self.assertEqual(f.receipt()["status"], "failed")
                self.assertEqual(f.commands, [])

    def test_existing_output_is_immutable_and_cannot_be_reused_as_success(self):
        f = self.fixture()
        f.output.mkdir(parents=True)
        stale = f.output / "preprocessing-contract.json"
        stale.write_text('{"status":"passed","source_revision":"old"}')
        before = stale.read_bytes()
        with self.assertRaises(FileExistsError):
            f.main()
        self.assertEqual(stale.read_bytes(), before)
        self.assertEqual(f.commands, [])

    def test_output_escape_and_symlink_fail_without_creating_a_receipt(self):
        f = self.fixture()
        outside = f.root / "outside"
        with self.assertRaisesRegex(ValueError, "output must be under"):
            f.main(outside)
        self.assertFalse(outside.exists())
        original = Path.is_symlink
        for link in (f.output, f.output.parent):
            with (
                self.subTest(link=link),
                patch.object(Path, "is_symlink", lambda p, link=link: p == link or original(p)),
                self.assertRaisesRegex(ValueError, "symlinks"),
            ):
                f.main()
        self.assertFalse(f.output.exists())
        self.assertEqual(f.commands, [])


if __name__ == "__main__":
    unittest.main()
