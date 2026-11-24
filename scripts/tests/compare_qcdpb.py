#!/usr/bin/env python3
"""Compare every named C internal QCDPB beta with the independent R execution."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import struct
from pathlib import Path

PROBE_COUNT = 486427
MAX_ABSOLUTE_ERROR = 1e-12
THRESHOLD_SOURCE = (
    "https://github.com/zhou-lab/sesame/blob/"
    "f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/compare_qcdpb.R"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(reference: Path, candidate: Path) -> dict[str, object]:
    ids = (reference / "probe-ids.txt").read_text(encoding="utf-8").splitlines()
    if len(ids) != PROBE_COUNT or len(set(ids)) != len(ids) or any(not p.strip() for p in ids):
        raise ValueError("R reference has the wrong complete probe universe")
    payload = (reference / "qcdpb-beta.f64").read_bytes()
    if len(payload) != len(ids) * 8:
        raise ValueError("truncated or trailing R numerical bytes")
    expected = struct.unpack(f"<{len(ids)}d", payload)
    missing = finite = na_mismatches = exceeded = 0
    maximum = 0.0
    with candidate.open(encoding="utf-8", newline="") as handle:
        for probe, value, row in zip(
            ids, expected, csv.reader(handle, delimiter="\t"), strict=True
        ):
            if len(row) != 2 or row[0] != probe:
                raise ValueError("complete ordered C probe identity/schema differs")
            if math.isnan(value):
                missing += 1
                na_mismatches += row[1] != "NA"
                continue
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("invalid R beta")
            if row[1] == "NA":
                na_mismatches += 1
                continue
            actual = float(row[1])
            if not math.isfinite(actual) or not 0 <= actual <= 1:
                raise ValueError("invalid C beta")
            finite += 1
            difference = abs(actual - value)
            maximum = max(maximum, difference)
            exceeded += difference > MAX_ABSOLUTE_ERROR
    return {
        "status": "passed" if na_mismatches == 0 and exceeded == 0 else "failed",
        "rows": len(ids),
        "reference_missing": missing,
        "paired_finite": finite,
        "na_mismatches": na_mismatches,
        "values_exceeding_tolerance": exceeded,
        "maximum_absolute_error": maximum,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-output", required=True, type=Path)
    parser.add_argument("--c-values", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    receipt_path: Path = args.receipt
    if receipt_path.exists() or receipt_path.is_symlink():
        raise ValueError("receipt must be a new file")
    receipt: dict[str, object] = {
        "status": "running",
        "scope": "independent R source-level QCDPB versus C internal float64 test helper",
        "maximum_allowed_absolute_error": MAX_ABSOLUTE_ERROR,
        "threshold_source": THRESHOLD_SOURCE,
        "acceptance": "complete ordered identity, exact NA pattern, every finite absolute error <= 1e-12",
        "not_admitted": [
            "production export precision",
            "full sesame package installation",
            "EPIC",
            "owner devices",
            "disease inference",
        ],
        "comparison_script_sha256": sha256(Path(__file__)),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    try:
        receipt.update(compare(args.r_output, args.c_values))
        receipt["c_values_sha256"] = sha256(args.c_values)
        receipt["r_values_sha256"] = sha256(args.r_output / "qcdpb-beta.f64")
        receipt["ordered_probe_ids_sha256"] = sha256(args.r_output / "probe-ids.txt")
    except (OSError, ValueError, csv.Error, struct.error) as error:
        receipt.update(status="failed", error=f"{type(error).__name__}: {error}")
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
