#!/usr/bin/env python3
"""Qualify the pinned HM450 raw QC panel and stage-specific p-value exports."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import zlib
from datetime import UTC, datetime
from itertools import zip_longest
from pathlib import Path
from typing import cast

import qualify_preprocessing as prep
from qualify_limma import digest, read_object, require

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/contracts/sesame-hm450-qc-v1.json"
NATIVE_CONTRACT = ROOT / "research/contracts/sesame-hm450-qc-v2.json"
PRODUCER_PATCH = "research/patches/sesame/native-qc-missing-signal.patch"
NATIVE_RECIPE = "scripts/tests/run_native_gct_reference.R"
NATIVE_HARNESS = "scripts/tests/test_qc_missing_signal.c"
NATIVE_FILES = {"native-typeI-ext.tsv.gz", "native-curated-C.ids.txt", "native-curated-T.ids.txt"}
NATIVE_GCT = (
    "Native bisConversionControl with pinned HM450.probeInfo C/T sets intersected with raw InfIR"
)
NATIVE_SCOPE = "Unchanged native R 65-field QC panel plus independently called native bisConversionControl; not full package qualification."
NATIVE_ANNOTATION = {
    "source_object": "HM450.probeInfo",
    "source_metadata_revision": "119df217cea4da8cb18173226fa85e6152d13e51",
    "source_version": "15-Mar-2018",
    "source_object_pin": {
        "sha256": "4faf0f8a4c5afceeb51b899a5eee93660c26ce599642f2d19dee09e1d8b8d6cd",
        "bytes": 10616007,
    },
    "selection": "intersect raw InfIR Probe_ID with typeI.extC and typeI.extT, separately",
    "native_curated_C": 45427,
    "native_curated_T": 15148,
    "ordering_sha256": "c209c3788843d3f08950806b8dd240aaa0e6646d697a67ba710c11c2903f49ad",
    "mask_applied": False,
    "missing_green_values": "omit per value within each mean",
    "zero_or_empty_denominator": "no coercion; nonfinite output is outside this finite-fixture contract",
}
MISSING_SIGNAL_POLICY = {
    "both_channels_absent_pvalue": 1.0,
    "num_dtna_counts": "missing p-values after native pOOBAH absent-signal handling",
    "overall_denominator": "all nonmissing p-values, including absent-signal failures",
    "unmasked_denominator": "all nonmissing p-values with existing mask false",
    "subtype_denominator": "all nonmissing p-values within the cg/ch/rs prefix",
    "empty_denominator": "NA",
    "raw_mask": "unchanged",
}
METRICS = (
    "num_dtna",
    "frac_dtna",
    "num_dt",
    "frac_dt",
    "num_dt_mk",
    "frac_dt_mk",
    "num_dt_cg",
    "frac_dt_cg",
    "num_dt_ch",
    "frac_dt_ch",
    "num_dt_rs",
    "frac_dt_rs",
    "num_probes",
    "num_probes_II",
    "num_probes_IR",
    "num_probes_IG",
    "num_probes_cg",
    "num_probes_ch",
    "num_probes_rs",
    "mean_intensity",
    "mean_intensity_MU",
    "mean_ii",
    "mean_inb_grn",
    "mean_inb_red",
    "mean_oob_grn",
    "mean_oob_red",
    "na_intensity_M",
    "na_intensity_U",
    "na_intensity_ig",
    "na_intensity_ir",
    "na_intensity_ii",
    "InfI_switch_R2R",
    "InfI_switch_G2G",
    "InfI_switch_R2G",
    "InfI_switch_G2R",
    "medR",
    "medG",
    "topR",
    "topG",
    "RGratio",
    "RGdistort",
    "GCT",
    "mean_beta",
    "median_beta",
    "frac_unmeth",
    "frac_meth",
    "num_na",
    "frac_na",
    "mean_beta_cg",
    "median_beta_cg",
    "frac_unmeth_cg",
    "frac_meth_cg",
    "num_na_cg",
    "frac_na_cg",
    "mean_beta_ch",
    "median_beta_ch",
    "frac_unmeth_ch",
    "frac_meth_ch",
    "num_na_ch",
    "frac_na_ch",
    "mean_beta_rs",
    "median_beta_rs",
    "frac_unmeth_rs",
    "frac_meth_rs",
    "num_na_rs",
    "frac_na_rs",
)
COUNTS = frozenset(m for m in METRICS if m.startswith(("num_", "na_intensity", "InfI_switch")))
REFERENCE_FILES = {"qc-reference.tsv", "pvalues-reference.tsv.gz"}
PVALUE_COLUMNS = ["Probe_ID", "raw_pval", "qcd_pval"]
GCT_REFERENCE = "R arithmetic over pinned published extension lists; native bisConversionControl parity is not claimed"
R_REVISION = "8b1fcfaed89b28e0def8b031a81611a0a770053c"
REFERENCE_RECIPE = "scripts/tests/run_qc_reference.R"
REFERENCE_SCOPE = (
    "Unchanged native R 65-field panel plus separately declared GCT published-list arithmetic; "
    "not full package or native bisConversionControl parity."
)


def metric_value(name: str, text: str) -> float | None:
    if text == "NA":
        require(name not in COUNTS, "a required QC count is missing")
        return None
    if name in COUNTS:
        require(re.fullmatch(r"[0-9]+", text) is not None, "invalid integer QC count")
        return int(text)
    value = float(text)
    require(math.isfinite(value) and value >= 0, "invalid QC value")
    if name.startswith(("frac_", "mean_beta", "median_beta")):
        require(value <= 1, "QC fraction or beta exceeds one")
    return value


def reference_metrics(path: Path) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream, delimiter="\t", strict=True)
        require(next(rows, None) == ["metric", "value"], "QC reference schema differs")
        for row in rows:
            require(len(row) == 2 and row[0] in METRICS, "unknown or malformed reference metric")
            require(row[0] not in values, "duplicated reference metric")
            values[row[0]] = metric_value(row[0], row[1])
    require(set(values) == set(METRICS), "complete QC reference metric set differs")
    return values


def compare_qc(reference: Path, actual: Path, sample: str) -> dict[str, object]:
    targets = reference_metrics(reference)
    with actual.open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream, delimiter="\t", strict=True)
        require(next(rows, None) == ["sample", *METRICS], "complete QC output schema differs")
        row = next(rows, None)
        require(row is not None and len(row) == len(METRICS) + 1, "malformed QC sample row")
        row = cast(list[str], row)
        require(row[0] == sample and next(rows, None) is None, "QC sample identity/count differs")
    comparisons: list[dict[str, object]] = []
    for name, text in zip(METRICS, row[1:], strict=True):
        target = targets[name]
        value = metric_value(name, text)
        expected = target if target is None or name in COUNTS else float(format(target, ".10g"))
        comparisons.append(
            {
                "metric": name,
                "reference": target,
                "expected_serialized": expected,
                "observed": value,
                "status": "passed" if value == expected else "failed",
            }
        )
    failed = sum(item["status"] == "failed" for item in comparisons)
    return {
        "status": "failed" if failed else "passed",
        "metrics_checked": len(comparisons),
        "metrics_failed": failed,
        "comparisons": comparisons,
        "acceptance": "all counts/NA exact; all floats exact ten-significant-digit reference serialization",
        "sha256": digest(actual),
    }


def compare_pvalues(
    reference: Path, actual: Path, index: Path, ids: list[str], stage: str, sample: str
) -> dict[str, object]:
    require(stage in ("raw", "QCDPB"), "unsupported p-value stage")
    require(index.read_text(encoding="utf-8") == f"{sample}\t0\n", "p-value sample index differs")
    count = missing = mismatches = missingness_mismatches = decision_changes = 0
    maximum_error = 0.0
    with (
        gzip.open(reference, "rt", encoding="utf-8", newline="") as expected_stream,
        actual.open(encoding="utf-8", newline="") as actual_stream,
    ):
        expected_rows = csv.reader(expected_stream, delimiter="\t", strict=True)
        actual_rows = csv.reader(actual_stream, delimiter="\t", strict=True)
        require(
            next(expected_rows, None) == PVALUE_COLUMNS
            and next(actual_rows, None) == ["Probe_ID", sample],
            "p-value schema differs",
        )
        for probe, expected, row in zip_longest(ids, expected_rows, actual_rows):
            require(
                probe is not None and expected is not None and row is not None,
                "complete p-value universe differs",
            )
            expected = cast(list[str], expected)
            row = cast(list[str], row)
            require(len(expected) == 3 and len(row) == 2, "malformed p-value row")
            require(expected[0] == row[0] == probe, "p-value identity/order differs")
            # Validate both reference columns even when receiving only one stage.
            references = [prep.beta_value(token) for token in expected[1:]]
            target = references[0 if stage == "raw" else 1]
            value = prep.beta_value(row[1])
            count += 1
            if target is None:
                missing += 1
            if (target is None) != (value is None):
                missingness_mismatches += 1
                mismatches += 1
            elif target is not None and value is not None:
                mismatches += value != prep.serialized_beta(target)
                maximum_error = max(maximum_error, abs(value - target))
                decision_changes += (value <= 0.05) != (target <= 0.05)
    require(count > 0, "empty p-value universe")
    return {
        "status": "failed" if mismatches or decision_changes else "passed",
        "rows": count,
        "reference_missing": missing,
        "serialized_mismatches": mismatches,
        "missingness_mismatches": missingness_mismatches,
        "detection_decision_changes_at_upstream_0_05": decision_changes,
        "maximum_absolute_serialization_error": maximum_error,
        "reference_stage": "raw" if stage == "raw" else "QCD, before P masking and B correction",
        "acceptance": "exact binary32/six-digit reference serialization; no detection-decision changes",
        "sha256": digest(actual),
        "sample_index_sha256": digest(index),
    }


def check_contract(contract: dict[str, object], reference: Path) -> dict[str, str]:
    native = contract.get("contract_id") == "sesame-hm450-qc-v2"
    recipe = NATIVE_RECIPE if native else REFERENCE_RECIPE
    require(
        type(contract.get("schema_version")) is int
        and contract["schema_version"] == 1
        and contract.get("contract_id") in ("sesame-hm450-qc-v1", "sesame-hm450-qc-v2")
        and contract.get("preprocessing_contract_sha256") == digest(prep.CONTRACT)
        and contract.get("metrics") == list(METRICS)
        and contract.get("integer_metrics") == sorted(COUNTS)
        and contract.get("gct_reference") == (NATIVE_GCT if native else GCT_REFERENCE)
        and contract.get("r_source_revision") == R_REVISION
        and contract.get("reference_recipe") == recipe
        and contract.get("reference_scope") == (NATIVE_SCOPE if native else REFERENCE_SCOPE)
        and type(contract.get("native_r_qc_metrics")) is int
        and contract["native_r_qc_metrics"] == 65
        and contract.get("qc_stage") == "raw"
        and contract.get("qc_beta_stage") == "DBP"
        and contract.get("qc_float_format") == ".10g"
        and contract.get("pvalue_format") == "binary32 then .6g"
        and contract.get("pvalue_reference_stages")
        == {"raw": "raw", "QCDPB": "QCD before P masking and B"}
        and contract.get("stages") == ["raw", "QCDPB"]
        and json.dumps(contract.get("threads")) == "[1, 2]"
        and type(contract.get("minimum_beads")) is int
        and contract["minimum_beads"] == 0
        and type(contract.get("detection_threshold")) is float
        and contract["detection_threshold"] == 0.05
        and contract.get("scientific_admitted") is False
        and contract.get("official_owner_device_accepted") is False
        and contract.get("sample_rejection_policy_accepted") is False
        and contract.get("scientific_precision_budget_accepted") is False,
        "unsupported QC contract",
    )
    if native:
        policy = prep.object_field(contract, "missing_signal_policy")
        require(
            type(policy.get("both_channels_absent_pvalue")) is float
            and policy == MISSING_SIGNAL_POLICY
            and contract.get("previous_contract_sha256") == digest(CONTRACT)
            and contract.get("parent_reference_recipe") == REFERENCE_RECIPE,
            "unsupported native QC semantics or parent contract",
        )
        require(
            json.dumps(prep.object_field(contract, "gct_annotation"), sort_keys=True)
            == json.dumps(NATIVE_ANNOTATION, sort_keys=True),
            "unsupported native GCT annotation lineage",
        )
        producer = prep.object_field(contract, "producer_patch")
        require(producer.get("path") == PRODUCER_PATCH, "unsupported producer patch path")
        prep.revision(producer, "result_tree")
        prep.checked_file(ROOT / PRODUCER_PATCH, prep.object_field(producer, "pin"))
        prep.checked_file(
            ROOT / REFERENCE_RECIPE, prep.object_field(contract, "parent_reference_recipe_pin")
        )
    pins = prep.object_field(contract, "reference_files")
    names = REFERENCE_FILES | NATIVE_FILES if native else REFERENCE_FILES
    require(set(pins) == names, "required QC reference files differ")
    prep.checked_file(ROOT / recipe, prep.object_field(contract, "reference_recipe_pin"))
    return {
        name: prep.checked_file(reference / name, prep.object_field(pins, name))
        for name in sorted(names)
    }


def native_git(checkout: Path, *args: str) -> str:
    """Do not let caller Git environment or global configuration redirect a source check."""
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.check_output(
        ["git", "--no-replace-objects", "-C", str(checkout), "-c", "core.fsmonitor=false", *args],
        env=environment,
        text=True,
    ).strip()


def check_qc_source(checkout: Path, base: dict[str, object], contract: dict[str, object]) -> None:
    if contract["contract_id"] == "sesame-hm450-qc-v1":
        prep.check_source(checkout, base)
        return
    require(
        not any(path.is_symlink() for path in [checkout / "YAME", checkout, *checkout.parents]),
        "source path contains a symlink",
    )
    require(
        Path(native_git(checkout, "rev-parse", "--show-toplevel")).resolve() == checkout.resolve()
        and native_git(checkout, "remote", "get-url", "origin") == prep.REPOSITORY,
        "native QC source root or origin differs",
    )
    for path, key in ((checkout, "source_revision"), (checkout / "YAME", "yame_revision")):
        require(
            Path(native_git(path, "rev-parse", "--show-toplevel")).resolve() == path.resolve(),
            "native QC source is not its own repository root",
        )
        require(
            native_git(path, "rev-parse", "HEAD") == prep.revision(base, key),
            "source revision drift",
        )
        require(
            all(line.startswith("H ") for line in native_git(path, "ls-files", "-v").splitlines()),
            "source has hidden index entries",
        )
    require(
        native_git(checkout / "YAME", "remote", "get-url", "origin")
        == "https://github.com/zhou-lab/YAME.git",
        "native QC YAME origin differs",
    )
    producer = prep.object_field(contract, "producer_patch")
    require(
        native_git(checkout, "write-tree") == prep.revision(producer, "result_tree")
        and not native_git(checkout, "diff", "--no-ext-diff", "--no-textconv", "--name-only")
        and not native_git(checkout, "ls-files", "--others", "--exclude-standard")
        and not native_git(checkout / "YAME", "status", "--porcelain", "--untracked-files=all"),
        "patched source tree, worktree or YAME differs",
    )
    actual = native_git(
        checkout,
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "--no-renames",
        "--full-index",
        "--no-color",
        "--src-prefix=a/",
        "--dst-prefix=b/",
        "--unified=3",
        "--diff-algorithm=myers",
        "--no-indent-heuristic",
        "HEAD",
    )
    require(
        actual == (ROOT / PRODUCER_PATCH).read_text(encoding="utf-8").strip(),
        "producer patch differs",
    )


def native_assets(
    data: Path, reference: Path, output: Path, ids: list[str], contract: dict[str, object]
) -> tuple[Path, dict[str, str]]:
    """Project the complete named native GCT sets into a fresh pinned asset store."""
    pins = prep.object_field(contract, "reference_files")
    for name in sorted(NATIVE_FILES):
        prep.checked_file(reference / name, prep.object_field(pins, name))
    groups: dict[str, set[str]] = {}
    universe = set(ids)
    annotation = prep.object_field(contract, "gct_annotation")
    require(
        len(ids) == len(universe)
        and hashlib.sha256("".join(probe + "\n" for probe in ids).encode()).hexdigest()
        == annotation["ordering_sha256"],
        "native GCT ordering lineage differs",
    )
    for code in ("C", "T"):
        names = (
            (reference / f"native-curated-{code}.ids.txt").read_text(encoding="utf-8").splitlines()
        )
        groups[code] = set(names)
        require(
            bool(names) and len(names) == len(groups[code]) and groups[code] <= universe,
            "native GCT set is empty, duplicated or outside the probe universe",
        )
        require(len(names) == annotation[f"native_curated_{code}"], "native GCT set count differs")
    require(not groups["C"] & groups["T"], "native GCT sets overlap")
    with (
        gzip.open(reference / "native-typeI-ext.tsv.gz", "rt", encoding="utf-8", newline="") as ext,
        gzip.open(
            data / "assets/HM450" / prep.ASSETS[0], "rt", encoding="utf-8", newline=""
        ) as order,
    ):
        extension = csv.reader(ext, delimiter="\t", strict=True)
        ordering = csv.reader(order, delimiter="\t", strict=True)
        require(
            next(extension, None) == ["ext"]
            and next(ordering, None) == ["Probe_ID", "M", "U", "col"],
            "native GCT annotation schema differs",
        )
        for probe, row, ordered_row in zip_longest(ids, extension, ordering):
            require(
                probe is not None and row is not None and ordered_row is not None,
                "native GCT complete universe differs",
            )
            row = cast(list[str], row)
            ordered_row = cast(list[str], ordered_row)
            code = "C" if probe in groups["C"] else "T" if probe in groups["T"] else "."
            require(
                len(ordered_row) == 4
                and ordered_row[0] == probe
                and row == [code]
                and (code == "." or ordered_row[3] == "R"),
                "native GCT identity, extension or raw InfIR selection differs",
            )
    root = output / "native-assets"
    target = root / "HM450"
    target.mkdir(parents=True, exist_ok=False)
    for name in prep.ASSETS:
        source = (
            reference / "native-typeI-ext.tsv.gz"
            if name == prep.ASSETS[2]
            else data / "assets/HM450" / name
        )
        shutil.copyfile(source, target / name)
        require(digest(source) == digest(target / name), "native GCT asset copy differs")
    return root, {name: digest(target / name) for name in prep.ASSETS}


def qualify(
    checkout: Path,
    data: Path,
    raw_reference: Path,
    reference: Path,
    output: Path,
    receipt: dict[str, object],
    contract_version: str = "v1",
) -> None:
    implementation_paths = [Path(__file__), Path(prep.__file__), ROOT / "scripts/qualify_limma.py"]
    if contract_version == "v2":
        implementation_paths.append(ROOT / NATIVE_HARNESS)
    implementation = {path.name: digest(path) for path in implementation_paths}
    contract_path = NATIVE_CONTRACT if contract_version == "v2" else CONTRACT
    contract = read_object(contract_path)
    require(
        contract.get("contract_id") == f"sesame-hm450-qc-{contract_version}",
        "QC contract selection differs",
    )
    base = read_object(prep.CONTRACT)
    reference_hashes = check_contract(contract, reference)
    input_hashes = prep.check_inputs(data, raw_reference, base)
    check_qc_source(checkout, base, contract)
    receipt.update(
        implementation_sha256=implementation,
        contract_sha256=digest(contract_path),
        input_sha256=input_hashes,
        reference_sha256=reference_hashes,
        source_revision=base["source_revision"],
        yame_revision=base["yame_revision"],
        gct_reference=contract["gct_reference"],
        r_source_revision=R_REVISION,
        reference_recipe_pin=contract["reference_recipe_pin"],
    )
    if contract_version == "v2":
        receipt.update(
            producer_patch=contract["producer_patch"],
            missing_signal_policy=contract["missing_signal_policy"],
            gct_annotation=contract["gct_annotation"],
        )
    commands: list[dict[str, object]] = []
    exports: list[dict[str, object]] = []
    receipt.update(commands=commands, exports=exports)
    environment = dict(os.environ)
    environment["YAME_DATA_HOME"] = str(data / "assets")
    binary = checkout / "sesame"
    if contract_version == "v2":
        regression_binary = output / "test-qc-missing-signal"
        for name, command in (
            ("compiler-version", ["cc", "--version"]),
            (
                "missing-signal-compile",
                [
                    "cc",
                    "-D_GNU_SOURCE",
                    "-std=c11",
                    "-O1",
                    "-g",
                    "-Wall",
                    "-Wextra",
                    "-Wpedantic",
                    "-Wshadow",
                    "-Wconversion",
                    "-Wstrict-prototypes",
                    "-Werror",
                    "-I" + str(checkout / "include"),
                    str(ROOT / NATIVE_HARNESS),
                    *[
                        str(checkout / "src" / (unit + ".c"))
                        for unit in ("qc", "prep", "numerics", "sigdf", "index", "util")
                    ],
                    "-lz",
                    "-lm",
                    "-o",
                    str(regression_binary),
                ],
            ),
            ("missing-signal-run", [str(regression_binary), str(output)]),
        ):
            prep.run(command, checkout, environment, output, name, commands)
        receipt["regression_binary_sha256"] = digest(regression_binary)
    for name, command in (
        ("clean-sesame", ["make", "clean"]),
        ("clean-yame", ["make", "-C", "YAME", "clean"]),
        ("build", ["make", "-j2", "sesame"]),
        ("version", [str(binary), "version"]),
    ):
        prep.run(command, checkout, environment, output, name, commands)
    binaries = {
        str(path.relative_to(checkout)): digest(path) for path in (binary, checkout / "YAME/yame")
    }
    receipt["binary_sha256"] = binaries
    assets = data / "assets/HM450"
    prep.run(
        [str(binary), "describe-probe", "--platform", "HM450", str(assets / prep.ASSETS[1])],
        checkout,
        environment,
        output,
        "annotation",
        commands,
    )
    ids, annotation = prep.annotation_rows(assets, output / "annotation.stdout")
    require(
        len(ids) == base["probe_count"]
        and annotation["ordered_probe_ids_sha256"] == base["ordered_probe_ids_sha256"],
        "pinned QC probe universe differs",
    )
    receipt["annotation"] = annotation
    asset_hashes: dict[str, str] = {}
    if contract_version == "v2":
        asset_root, asset_hashes = native_assets(data, reference, output, ids, contract)
        expected = {
            name: reference_hashes["native-typeI-ext.tsv.gz"]
            if name == prep.ASSETS[2]
            else input_hashes[f"assets/HM450/{name}"]
            for name in prep.ASSETS
        }
        require(asset_hashes == expected, "native GCT overlay differs from pinned input bytes")
        environment["YAME_DATA_HOME"] = str(asset_root)
        assets = asset_root / "HM450"
        receipt["native_asset_sha256"] = asset_hashes
    for stage in ("raw", "QCDPB"):
        for threads in (1, 2):
            name = f"{stage}-{threads}"
            target = output / name
            prep.run(
                [
                    str(binary),
                    "preprocess",
                    "--platform",
                    "HM450",
                    "--prep",
                    "" if stage == "raw" else stage,
                    "--mask",
                    str(assets / prep.ASSETS[3]),
                    "--min-beads",
                    "0",
                    "--threads",
                    str(threads),
                    "--output",
                    "pval,qc",
                    "--out",
                    str(target),
                    "--tmp",
                    str(output),
                    str(data / f"idats/HM450/{prep.SAMPLE}"),
                ],
                checkout,
                environment,
                output,
                name,
                commands,
            )
            prep.run(
                [
                    str(binary),
                    "describe-probe",
                    "--platform",
                    "HM450",
                    "--all",
                    str(target / "pval.cg"),
                ],
                checkout,
                environment,
                output,
                name + "-pval",
                commands,
            )
            exports.append(
                {
                    "stage": stage,
                    "threads": threads,
                    "qc": compare_qc(
                        reference / "qc-reference.tsv", target / "qc.tsv", prep.SAMPLE
                    ),
                    "pvalues": compare_pvalues(
                        reference / "pvalues-reference.tsv.gz",
                        output / f"{name}-pval.stdout",
                        target / "pval.cg.idx",
                        ids,
                        stage,
                        prep.SAMPLE,
                    ),
                    "pvalue_binary_sha256": digest(target / "pval.cg"),
                }
            )
    if contract_version == "v2":
        raw_q: list[dict[str, object]] = []
        receipt["raw_q_exports"] = raw_q
        for stage in ("raw", "Q"):
            for threads in (1, 2):
                name = f"raw-q-check-{stage}-{threads}"
                target = output / name
                prep.run(
                    [
                        str(binary),
                        "preprocess",
                        "--platform",
                        "HM450",
                        "--prep",
                        "" if stage == "raw" else stage,
                        "--mask",
                        str(assets / prep.ASSETS[3]),
                        "--min-beads",
                        "0",
                        "--threads",
                        str(threads),
                        "--output",
                        "beta",
                        "--out",
                        str(target),
                        "--tmp",
                        str(output),
                        str(data / f"idats/HM450/{prep.SAMPLE}"),
                    ],
                    checkout,
                    environment,
                    output,
                    name,
                    commands,
                )
                prep.run(
                    [
                        str(binary),
                        "describe-probe",
                        "--platform",
                        "HM450",
                        "--all",
                        str(target / "beta.cg"),
                    ],
                    checkout,
                    environment,
                    output,
                    name + "-export",
                    commands,
                )
                result = prep.validate_export(
                    raw_reference,
                    output / f"{name}-export.stdout",
                    target / "beta.cg.idx",
                    ids,
                    stage,
                    prep.SAMPLE,
                )
                result.update(
                    status="passed",
                    stage=stage,
                    threads=threads,
                    binary_output_sha256=digest(target / "beta.cg"),
                )
                raw_q.append(result)
        for stage in ("raw", "Q"):
            runs = [item for item in raw_q if item["stage"] == stage]
            require(
                len({item["binary_output_sha256"] for item in runs}) == 1
                and len({item["text_sha256"] for item in runs}) == 1,
                "raw/Q preservation differs between thread settings",
            )
        require(
            all(item["status"] == "passed" for item in raw_q),
            "raw/Q preservation comparison failed",
        )
        require(
            {name: digest(assets / name) for name in asset_hashes} == asset_hashes,
            "native GCT asset overlay changed",
        )
        require(
            digest(output / "test-qc-missing-signal") == receipt["regression_binary_sha256"],
            "QC regression binary changed",
        )
    require(check_contract(contract, reference) == reference_hashes, "QC references changed")
    require(prep.check_inputs(data, raw_reference, base) == input_hashes, "QC input bytes changed")
    require(digest(contract_path) == receipt["contract_sha256"], "QC contract changed")
    require({name: digest(checkout / name) for name in binaries} == binaries, "QC binaries changed")
    require(
        {path.name: digest(path) for path in implementation_paths} == implementation,
        "QC qualification implementation changed",
    )
    check_qc_source(checkout, base, contract)
    require(
        len({prep.object_field(item, "qc")["sha256"] for item in exports}) == 1,
        "raw QC output depends on stage or thread setting",
    )
    for stage in ("raw", "QCDPB"):
        runs = [item for item in exports if item["stage"] == stage]
        require(
            len({item["pvalue_binary_sha256"] for item in runs}) == 1
            and len({prep.object_field(item, "pvalues")["sha256"] for item in runs}) == 1,
            "p-value output differs between thread settings",
        )
    require(
        all(
            prep.object_field(item, key)["status"] == "passed"
            for item in exports
            for key in ("qc", "pvalues")
        ),
        "QC or detection reference comparison failed; method admission remains held",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", choices=("v1", "v2"), default="v1")
    for name in ("checkout", "data-root", "raw-reference", "reference-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    require(
        output.resolve().is_relative_to(ROOT / "artifacts/verification")
        and not any(path.is_symlink() for path in [output, *output.parents]),
        "output must be under artifacts/verification without symlinks",
    )
    output.mkdir(parents=True, exist_ok=False)
    receipt: dict[str, object] = {
        "schema_version": 1,
        "contract_id": f"sesame-hm450-qc-{args.contract}",
        "status": "running",
        "started_at": datetime.now(UTC).isoformat(),
        "scientific_admitted": False,
        "official_owner_device_accepted": False,
        "sample_rejection_policy_accepted": False,
        "limitations": [
            "One HM450 technical pair; explicit minimum beads zero.",
            "Raw QC beta summaries use DBP; QCDPB p-values are captured before B.",
            "No disease analysis, sample rejection policy or scientific precision budget.",
        ],
    }
    path = output / "qc-contract.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    started = time.monotonic()
    try:
        qualify(
            args.checkout.absolute(),
            args.data_root.absolute(),
            args.raw_reference.absolute(),
            args.reference_root.absolute(),
            output,
            receipt,
            args.contract,
        )
        receipt["status"] = "passed"
    except (
        OSError,
        ValueError,
        EOFError,
        csv.Error,
        zlib.error,
        subprocess.SubprocessError,
    ) as exc:
        receipt.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
    path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(f"QC qualification {receipt['status']}: {path}")
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
