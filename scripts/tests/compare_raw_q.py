#!/usr/bin/env python3
"""Compare the complete ordered independently generated Python and R references."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import struct
from pathlib import Path

PROBE_COUNT = 486427
COLUMNS = [
    "Probe_ID",
    "channel",
    "M_signal",
    "U_signal",
    "raw_beta",
    "q_mask",
    "q_beta",
]
FILES = {
    "M_signal": "M-signal.f64",
    "U_signal": "U-signal.f64",
    "raw_beta": "raw-beta.f64",
    "q_beta": "q-beta.f64",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(root: Path, expected: Path) -> dict[str, object]:
    ids = (root / "probe-ids.txt").read_text(encoding="utf-8").splitlines()
    if len(ids) != PROBE_COUNT or len(set(ids)) != len(ids) or any(not p.strip() for p in ids):
        raise ValueError("R reference has the wrong complete probe universe")
    values: dict[str, tuple[float, ...]] = {}
    for field, name in FILES.items():
        payload = (root / name).read_bytes()
        if len(payload) != len(ids) * 8:
            raise ValueError(f"truncated or trailing R numerical bytes: {name}")
        values[field] = struct.unpack(f"<{len(ids)}d", payload)
        if any(math.isinf(value) for value in values[field]):
            raise ValueError(f"infinite R reference value: {name}")
    mask = (root / "q-mask.u8").read_bytes()
    if len(mask) != len(ids) or any(v not in (0, 1) for v in mask):
        raise ValueError("invalid R mask bytes")
    mismatch = dict.fromkeys([*FILES, "q_mask"], 0)
    missing = dict.fromkeys(FILES, 0)
    maximum = dict.fromkeys(FILES, 0.0)
    with gzip.open(expected, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        if next(reader, None) != COLUMNS:
            raise ValueError("Python reference header differs")
        for i, (probe, fields) in enumerate(zip(ids, reader, strict=True)):
            if len(fields) != len(COLUMNS):
                raise ValueError("Python reference row has missing or extra fields")
            row = dict(zip(COLUMNS, fields, strict=True))
            if probe != row["Probe_ID"]:
                raise ValueError(f"complete ordered identity differs at row {i + 1}")
            if row["channel"] not in ("G", "R", "2") or row["q_mask"] not in ("0", "1"):
                raise ValueError("invalid Python reference channel or mask")
            mismatch["q_mask"] += mask[i] != int(row["q_mask"])
            for field in FILES:
                actual = values[field][i]
                if row[field] == "NA":
                    mismatch[field] += not math.isnan(actual)
                    missing[field] += 1
                else:
                    value = float(row[field])
                    if not math.isfinite(value):
                        raise ValueError("Python reference has a nonfinite numeric token")
                    mismatch[field] += actual != value
                    if math.isfinite(actual):
                        maximum[field] = max(maximum[field], abs(actual - value))
    paths = [root / name for name in ["probe-ids.txt", "q-mask.u8", *FILES.values()]]
    return {
        "status": "passed" if not any(mismatch.values()) else "failed",
        "rows": len(ids),
        "mismatches": mismatch,
        "missing": missing,
        "maximum_absolute_error": maximum,
        "python_reference": {"path": str(expected), "sha256": sha256(expected)},
        "r_outputs": {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in paths},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--r-output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args(argv)
    receipt_path: Path = args.receipt
    root: Path = args.r_output
    expected: Path = args.reference
    inputs = [
        expected,
        *[root / name for name in ["probe-ids.txt", "q-mask.u8", *FILES.values()]],
    ]
    if receipt_path.resolve() in {path.resolve() for path in inputs}:
        raise ValueError("receipt aliases an input")
    if receipt_path.exists() or receipt_path.is_symlink():
        raise ValueError("receipt must be a new file")
    receipt: dict[str, object] = {
        "status": "running",
        "scope": "complete ordered R source-level raw/Q versus independent Python mathematical reference",
        "acceptance": "exact finite binary64 values, exact NA pattern, exact mask and complete ordered identity",
        "comparison_script_sha256": sha256(Path(__file__)),
        "does_not_admit": [
            "full sesame package installation",
            "QCDPB",
            "EPIC",
            "owner devices",
            "disease inference",
        ],
    }
    with receipt_path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, indent=2) + "\n")
    try:
        receipt.update(compare(root, expected))
    except (OSError, ValueError, EOFError, csv.Error, struct.error) as error:
        receipt.update(status="failed", error=f"{type(error).__name__}: {error}")
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
