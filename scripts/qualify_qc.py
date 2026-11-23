#!/usr/bin/env python3
"""Qualify the pinned HM450 raw QC panel and stage-specific p-value exports."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import re
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
    require(
        type(contract.get("schema_version")) is int
        and contract["schema_version"] == 1
        and contract.get("contract_id") == "sesame-hm450-qc-v1"
        and contract.get("preprocessing_contract_sha256") == digest(prep.CONTRACT)
        and contract.get("metrics") == list(METRICS)
        and contract.get("integer_metrics") == sorted(COUNTS)
        and contract.get("gct_reference") == GCT_REFERENCE
        and contract.get("r_source_revision") == R_REVISION
        and contract.get("reference_recipe") == REFERENCE_RECIPE
        and contract.get("reference_scope") == REFERENCE_SCOPE
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
    pins = prep.object_field(contract, "reference_files")
    require(set(pins) == REFERENCE_FILES, "required QC reference files differ")
    prep.checked_file(ROOT / REFERENCE_RECIPE, prep.object_field(contract, "reference_recipe_pin"))
    return {
        name: prep.checked_file(reference / name, prep.object_field(pins, name))
        for name in sorted(REFERENCE_FILES)
    }


def qualify(
    checkout: Path,
    data: Path,
    raw_reference: Path,
    reference: Path,
    output: Path,
    receipt: dict[str, object],
) -> None:
    implementation_paths = [Path(__file__), Path(prep.__file__), ROOT / "scripts/qualify_limma.py"]
    implementation = {path.name: digest(path) for path in implementation_paths}
    contract = read_object(CONTRACT)
    base = read_object(prep.CONTRACT)
    reference_hashes = check_contract(contract, reference)
    input_hashes = prep.check_inputs(data, raw_reference, base)
    prep.check_source(checkout, base)
    receipt.update(
        implementation_sha256=implementation,
        contract_sha256=digest(CONTRACT),
        input_sha256=input_hashes,
        reference_sha256=reference_hashes,
        source_revision=base["source_revision"],
        yame_revision=base["yame_revision"],
        gct_reference=GCT_REFERENCE,
        r_source_revision=R_REVISION,
        reference_recipe_pin=contract["reference_recipe_pin"],
    )
    commands: list[dict[str, object]] = []
    exports: list[dict[str, object]] = []
    receipt.update(commands=commands, exports=exports)
    environment = dict(os.environ)
    environment["YAME_DATA_HOME"] = str(data / "assets")
    binary = checkout / "sesame"
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
    require(check_contract(contract, reference) == reference_hashes, "QC references changed")
    require(prep.check_inputs(data, raw_reference, base) == input_hashes, "QC input bytes changed")
    require(digest(CONTRACT) == receipt["contract_sha256"], "QC contract changed")
    require({name: digest(checkout / name) for name in binaries} == binaries, "QC binaries changed")
    require(
        {path.name: digest(path) for path in implementation_paths} == implementation,
        "QC qualification implementation changed",
    )
    prep.check_source(checkout, base)
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
        "contract_id": "sesame-hm450-qc-v1",
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
