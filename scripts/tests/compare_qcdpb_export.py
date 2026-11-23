#!/usr/bin/env python3
"""Qualify one production beta-only QCDPB text export directly against fresh R."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import struct
from pathlib import Path

PROBE_COUNT = 486427
SAMPLE = "3999492009_R01C01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serialized_beta(value: float) -> float:
    binary32 = struct.unpack("<f", struct.pack("<f", value))[0]
    return float(format(binary32, ".6g"))


def compare_export(reference: Path, candidate: Path, index: Path) -> dict[str, object]:
    ids = (reference / "probe-ids.txt").read_text(encoding="utf-8").splitlines()
    if len(ids) != PROBE_COUNT or len(set(ids)) != len(ids) or any(not p.strip() for p in ids):
        raise ValueError("R reference has the wrong complete probe universe")
    payload = (reference / "qcdpb-beta.f64").read_bytes()
    if len(payload) != len(ids) * 8:
        raise ValueError("truncated or trailing R numerical bytes")
    expected = struct.unpack(f"<{len(ids)}d", payload)
    if index.read_text(encoding="utf-8") != f"{SAMPLE}\t0\n":
        raise ValueError("production sample index differs")
    missing = finite = endpoints = collapses = 0
    max_beta_error = max_m_error = 0.0
    with candidate.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        if next(reader, None) != ["Probe_ID", SAMPLE]:
            raise ValueError("production sample header differs")
        for probe, value, row in zip(ids, expected, reader, strict=True):
            if len(row) != 2 or row[0] != probe:
                raise ValueError("complete ordered production identity/schema differs")
            if math.isnan(value):
                if row[1] != "NA":
                    raise ValueError("production replaced a reference NA")
                missing += 1
                continue
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("invalid R beta")
            if row[1] == "NA":
                raise ValueError("production removed a finite reference beta")
            actual = float(row[1])
            if not math.isfinite(actual) or actual != serialized_beta(value):
                raise ValueError("production beta differs from the declared R serialization")
            finite += 1
            max_beta_error = max(max_beta_error, abs(actual - value))
            if value in (0.0, 1.0):
                endpoints += 1
            elif actual in (0.0, 1.0):
                collapses += 1
            else:
                max_m_error = max(
                    max_m_error,
                    abs(math.log2(actual / (1 - actual)) - math.log2(value / (1 - value))),
                )
    return {
        "status": "passed",
        "rows": len(ids),
        "missing": missing,
        "finite": finite,
        "reference_endpoints": endpoints,
        "finite_to_endpoint_collapses": collapses,
        "maximum_absolute_beta_serialization_error": max_beta_error,
        "maximum_finite_absolute_m_serialization_error": max_m_error,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-output", required=True, type=Path)
    parser.add_argument("--text-export", required=True, type=Path)
    parser.add_argument("--sample-index", required=True, type=Path)
    parser.add_argument("--binary-output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    receipt_path: Path = args.receipt
    if receipt_path.exists() or receipt_path.is_symlink():
        raise ValueError("receipt must be a new file")
    receipt: dict[str, object] = {
        "status": "running",
        "scope": "selected public HM450 QCDPB production beta-only export versus fresh R",
        "acceptance": "exact complete ordered text numeric values after declared binary32 then six-significant-digit serialization, including NA and sample index",
        "direct_stored_binary_word_audit": False,
        "qc_metrics_accepted": False,
        "scientific_m_error_budget_accepted": False,
        "scientific_admitted": False,
        "official_owner_device_accepted": False,
        "not_admitted": [
            "EPIC",
            "full sesame package installation",
            "disease inference",
        ],
        "comparison_script_sha256": sha256(Path(__file__)),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    try:
        receipt.update(compare_export(args.r_output, args.text_export, args.sample_index))
        receipt["sha256"] = {
            "text_export": sha256(args.text_export),
            "sample_index": sha256(args.sample_index),
            "binary_output": sha256(args.binary_output),
            "r_values": sha256(args.r_output / "qcdpb-beta.f64"),
            "ordered_probe_ids": sha256(args.r_output / "probe-ids.txt"),
        }
    except (OSError, ValueError, csv.Error, struct.error) as error:
        receipt.update(status="failed", error=f"{type(error).__name__}: {error}")
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
