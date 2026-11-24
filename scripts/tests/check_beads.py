#!/usr/bin/env python3
"""Independently compare original IDAT field-107 beads and the pinned HM450 masks."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import struct
import sys
import time
import zlib
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_beads(path: Path) -> tuple[tuple[int, ...], bytes]:
    """Preserve the original independent v3 directory/address/uint8 decoder."""
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != b"IDAT":
        raise ValueError("invalid IDAT header")
    version, count = struct.unpack_from("<qi", data, 4)
    if version != 3 or not 1 <= count <= 1000 or 16 + 10 * count > len(data):
        raise ValueError("invalid directory")
    fields: dict[int, int] = {}
    for index in range(count):
        code, offset = struct.unpack_from("<Hq", data, 16 + 10 * index)
        if code in fields or not 16 + 10 * count <= offset < len(data):
            raise ValueError("invalid field")
        fields[code] = offset

    def field(code: int, size: int) -> int:
        offset = fields.get(code)
        if offset is None or offset + size > len(data):
            raise ValueError("missing or truncated field")
        return offset

    n = struct.unpack_from("<i", data, field(1000, 4))[0]
    if n != 622399:
        raise ValueError("wrong complete IDAT address universe")
    addresses = struct.unpack_from(f"<{n}I", data, field(102, 4 * n))
    if len(set(addresses)) != n or any(address == 0 for address in addresses):
        raise ValueError("duplicate or invalid address")
    offset = field(107, n)
    return addresses, data[offset : offset + n]


def verify(
    data_root: Path, reference_zero: Path, reference_three: Path, output: Path
) -> dict[str, object]:
    sources = [
        data_root / f"idats/HM450/3999492009_R01C01_{color}.idat" for color in ("Grn", "Red")
    ]
    green_ids, green = read_beads(sources[0])
    red_ids, red = read_beads(sources[1])
    require(green_ids == red_ids, "paired original address vectors differ")
    paired = dict(zip(green_ids, zip(green, red, strict=True), strict=True))
    require(
        (reference_three / "original-address-ids.txt").read_text(encoding="utf-8").splitlines()
        == list(map(str, green_ids)),
        "original address reference differs",
    )
    require(
        (reference_three / "original-green-beads.u8").read_bytes() == green,
        "original green bead vector differs",
    )
    require(
        (reference_three / "original-red-beads.u8").read_bytes() == red,
        "original red bead vector differs",
    )
    ids = []
    mask = bytearray()
    missing_address_rows = low_present_rows = 0
    ordering = data_root / "assets/HM450/HM450.ordering.tsv.gz"
    with gzip.open(ordering, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t", strict=True)
        require(next(reader, None) == ["Probe_ID", "M", "U", "col"], "ordering schema differs")
        for row in reader:
            require(len(row) == 4 and row[3] in {"G", "R", "2"}, "invalid ordering row")
            ids.append(row[0])
            addresses = [row[2]] if row[3] == "2" else row[1:3]
            counts = [paired.get(int(value)) if value != "NA" else None for value in addresses]
            missing = any(value is None for value in counts)
            low = any(value is not None and min(value) < 3 for value in counts)
            mask.append(missing or low)
            missing_address_rows += missing
            low_present_rows += low
    require(len(ids) == len(set(ids)) == 486427, "wrong or duplicate complete probe universe")
    require(
        ids == (reference_three / "probe-ids.txt").read_text(encoding="utf-8").splitlines(),
        "ordered probe reference differs",
    )
    require(
        bytes(mask) == (reference_three / "initial-bead-mask.u8").read_bytes(),
        "minimum-three bead mask differs",
    )
    require(
        (reference_zero / "initial-bead-mask.u8").read_bytes() == bytes(len(ids)),
        "minimum-zero bead mask is not the complete zero mask",
    )
    (output / "independent-bead3-mask.u8").write_bytes(mask)
    return {
        "original_addresses": len(green_ids),
        "probes": len(ids),
        "original_bead_vector_mismatches": 0,
        "derived_mask_mismatches": 0,
        "min_beads3_masked": sum(mask),
        "missing_address_rows": missing_address_rows,
        "low_present_bead_rows": low_present_rows,
        "green_bead_histogram": dict(sorted(Counter(green).items())),
        "red_bead_histogram": dict(sorted(Counter(red).items())),
        "source_sha256": {str(source): sha256(source) for source in sources},
        "ordering_sha256": sha256(ordering),
        "bead_mask_sha256": hashlib.sha256(mask).hexdigest(),
        "minimum_zero_mask_sha256": sha256(reference_zero / "initial-bead-mask.u8"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("data-root", "reference-zero", "reference-three", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    receipt: dict[str, object] = {
        "schema_version": 1,
        "status": "running",
        "started_at": datetime.now(UTC).isoformat(),
        "scope": "Original HM450 IDAT bead vectors and initial minimum-zero/three masks only",
        "data_root": str(args.data_root.absolute()),
        "reference_zero": str(args.reference_zero.absolute()),
        "reference_three": str(args.reference_three.absolute()),
        "scientific_admitted": False,
        "native_qc_parity_accepted": False,
    }
    path = output / "bead-verification.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    started = time.monotonic()
    try:
        receipt["script_sha256"] = sha256(Path(__file__))
        receipt.update(
            verify(
                args.data_root.absolute(),
                args.reference_zero.absolute(),
                args.reference_three.absolute(),
                output,
            )
        )
        receipt["status"] = "passed"
    except (OSError, ValueError, EOFError, csv.Error, struct.error, zlib.error) as exc:
        receipt.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
    receipt["completed_at"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    keys = (
        "status",
        "original_addresses",
        "probes",
        "min_beads3_masked",
        "missing_address_rows",
        "low_present_bead_rows",
        "error",
    )
    print(json.dumps({key: receipt[key] for key in keys if key in receipt}, indent=2))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
