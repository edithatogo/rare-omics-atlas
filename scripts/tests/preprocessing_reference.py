#!/usr/bin/env python3
"""Independent raw/Q expectations for the pinned public HM450 technical pair.

Reads IDAT means directly, following the published R address/channel contract.
Uses YAME only to decode the published annotation mask, never pipeline values.
This is a bounded mathematical oracle, not execution of R or a QCDPB oracle.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import struct
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

R_REVISION = "8b1fcfaed89b28e0def8b031a81611a0a770053c"
YAME_REVISION = "e1e7b38e9f3b67981a78b1116e7312864677d69d"
PROBE_COUNT = 486427
R_SOURCE_PINS = {
    "sesame.R": "aded5603c661b804468f4d6be4ec0e37d9f0bdeaa1da054d7ad3978e9cac6f5f",
    "SigDFMethods.R": "3625dc4d804c15fa257fadc25877ef70e970e8bc5353a1d85ead90913adce0bc",
    "mask.R": "23eae3dfda6fd5ea4cdcfc885ec16c86d15d8d10720b7e8571e60548a7534527",
    "readIDAT.R": "534986132b27a5c002e3e1842d9cb05428c7040ae03bc7230b8694eddd16f302",
}
Q_TRACKS = (
    "M_1baseSwitchSNPcommon_5pt",
    "M_2extBase_SNPcommon_5pt",
    "M_mapping",
    "M_nonuniq",
    "M_SNPcommon_5pt",
)
INPUT_PINS = {
    "assets/HM450/HM450.ordering.tsv.gz": "e659fe9983df66a20eacff97b98dd08e225963cead5d512d11d6c38a7e9136f6",
    "assets/HM450/HM450.hg38.mask.cm": "adebc62a6e6c1a783a5cd00bf61b441ee2b72c017d7be978fbf2ee6334d04360",
    "assets/HM450/HM450.hg38.mask.cm.idx": "27dff6eb30329c3fc974226a8da3e2b8d5d66f4205abde8eebb78fb07e28b959",
    "idats/HM450/3999492009_R01C01_Grn.idat": "80ebef9ba5dcacdd1d0c70da9e06ee3d4c914552240858811704638fcfdfe6bd",
    "idats/HM450/3999492009_R01C01_Red.idat": "0c12f9867f6e8c22056192185a810d2d1436362a67a607e395c66357844612be",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_means(path: Path) -> tuple[tuple[int, ...], dict[int, int]]:
    """Decode only the public v3 field directory, addresses and uint16 means."""
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != b"IDAT":
        raise ValueError("invalid IDAT header")
    version, count = struct.unpack_from("<qi", data, 4)
    if version != 3 or not 1 <= count <= 1000 or 16 + 10 * count > len(data):
        raise ValueError("unsupported IDAT version or field count")
    fields: dict[int, int] = {}
    for i in range(count):
        code, offset = struct.unpack_from("<Hq", data, 16 + 10 * i)
        if code in fields or not 16 + 10 * count <= offset < len(data):
            raise ValueError("duplicate field or invalid field offset")
        fields[code] = offset

    def field(code: int, size: int) -> int:
        offset = fields.get(code)
        if offset is None or offset + size > len(data):
            raise ValueError("missing or truncated required IDAT field")
        return offset

    n = struct.unpack_from("<i", data, field(1000, 4))[0]
    if not 1 <= n <= 2000000:
        raise ValueError("invalid bead count")
    addresses = struct.unpack_from(f"<{n}I", data, field(102, 4 * n))
    means = struct.unpack_from(f"<{n}H", data, field(104, 2 * n))
    if any(a == 0 for a in addresses) or len(set(addresses)) != n:
        raise ValueError("invalid or duplicate bead address")
    return addresses, dict(zip(addresses, means, strict=True))


def beta(m: int | None, u: int | None) -> float | None:
    if m is None or u is None:
        return None
    return max(m, 1) / max(m + u, 2)


def signals(
    channel: str,
    m_address: int | None,
    u_address: int | None,
    green: dict[int, int],
    red: dict[int, int],
) -> tuple[int | None, int | None]:
    if channel == "2":
        return green.get(u_address or 0), red.get(u_address or 0)
    if channel not in ("G", "R"):
        raise ValueError("invalid channel")
    source = green if channel == "G" else red
    return source.get(m_address or 0), source.get(u_address or 0)


def read_ordering(path: Path) -> list[tuple[str, int | None, int | None, str]]:
    rows: list[tuple[str, int | None, int | None, str]] = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        if next(reader) != ["Probe_ID", "M", "U", "col"]:
            raise ValueError("unexpected ordering schema")
        for fields in reader:
            if len(fields) != 4:
                raise ValueError("malformed ordering row")
            probe, m, u, channel = fields
            if not probe.strip() or channel not in ("G", "R", "2"):
                raise ValueError("invalid ordering identity or channel")
            rows.append(
                (
                    probe,
                    None if m == "NA" else int(m),
                    None if u == "NA" else int(u),
                    channel,
                )
            )
    if len(rows) != PROBE_COUNT or len({row[0] for row in rows}) != len(rows):
        raise ValueError("wrong or duplicate complete probe universe")
    return rows


def decode_q(yame: Path, mask: Path) -> tuple[list[bool], dict[str, int], list[str]]:
    command = [str(yame), "unpack", "-C", str(mask), *Q_TRACKS]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    reader = csv.reader(io.StringIO(result.stdout), delimiter="\t")
    if next(reader) != list(Q_TRACKS):
        raise ValueError("decoded mask track identities/order differ")
    masked: list[bool] = []
    counts: dict[str, int] = dict.fromkeys(Q_TRACKS, 0)
    for row in reader:
        if len(row) != len(Q_TRACKS) or any(value not in ("0", "1") for value in row):
            raise ValueError("invalid decoded mask bits")
        masked.append("1" in row)
        for track, value in zip(Q_TRACKS, row, strict=True):
            counts[track] += int(value)
    if len(masked) != PROBE_COUNT:
        raise ValueError("mask and complete ordering lengths differ")
    return masked, counts, command


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--r-source", type=Path, required=True)
    parser.add_argument("--yame", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data_root = args.data_root.resolve(strict=True)
    r_source = args.r_source.resolve(strict=True)
    yame = args.yame.resolve(strict=True)
    revision = subprocess.check_output(
        ["git", "-C", str(yame.parent), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != YAME_REVISION:
        raise ValueError("YAME source revision differs from the selected decoder")
    subprocess.run(["git", "-C", str(yame.parent), "diff", "--quiet", "HEAD"], check=True)
    sources: list[dict[str, str | int]] = []
    for name, expected in R_SOURCE_PINS.items():
        path = r_source / name
        if sha256(path) != expected:
            raise ValueError("reference source changed")
        sources.append(
            {
                "name": name,
                "sha256": expected,
                "bytes": path.stat().st_size,
                "source_url": f"https://raw.githubusercontent.com/zwdzwd/sesame/{R_REVISION}/R/{name}",
            }
        )
    inputs = {}
    for name, expected in INPUT_PINS.items():
        actual = sha256(data_root / name)
        if actual != expected:
            raise ValueError(f"input hash mismatch: {name}")
        inputs[name] = {"sha256": actual, "bytes": (data_root / name).stat().st_size}
    green_ids, green = read_means(data_root / "idats/HM450/3999492009_R01C01_Grn.idat")
    red_ids, red = read_means(data_root / "idats/HM450/3999492009_R01C01_Red.idat")
    if green_ids != red_ids or len(green_ids) != 622399:
        raise ValueError("paired address vectors or fixture bead count differ")
    ordering = read_ordering(data_root / "assets/HM450/HM450.ordering.tsv.gz")
    qmask, track_counts, command = decode_q(yame, data_root / "assets/HM450/HM450.hg38.mask.cm")
    output: Path = args.output
    output.mkdir(parents=True, exist_ok=False)
    table = output / "expected-raw-q.tsv.gz"
    raw_na = q_na = 0
    probe_digest = hashlib.sha256()
    with (
        table.open("wb") as compressed,
        gzip.GzipFile(filename="", mode="wb", fileobj=compressed, mtime=0) as gz,
        io.TextIOWrapper(gz, encoding="utf-8", newline="") as text,
    ):
        writer = csv.writer(text, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "Probe_ID",
                "channel",
                "M_signal",
                "U_signal",
                "raw_beta",
                "q_mask",
                "q_beta",
            ]
        )
        for (probe, m_address, u_address, channel), masked in zip(ordering, qmask, strict=True):
            m, u = signals(channel, m_address, u_address, green, red)
            raw = beta(m, u)
            quality = None if masked else raw
            raw_na += raw is None
            q_na += quality is None
            probe_digest.update(probe.encode("utf-8") + b"\n")
            writer.writerow(
                [
                    probe,
                    channel,
                    "NA" if m is None else m,
                    "NA" if u is None else u,
                    "NA" if raw is None else repr(raw),
                    int(masked),
                    "NA" if quality is None else repr(quality),
                ]
            )
    receipt = {
        "status": "generated",
        "created_utc": datetime.now(UTC).isoformat(),
        "scope": "independent raw/Q mathematical oracle, not executed R or QCDPB acceptance",
        "sample": "3999492009_R01C01",
        "platform": "HM450",
        "minimum_beads": 0,
        "data_root": str(data_root),
        "r_source_directory": str(r_source),
        "r_source_revision": R_REVISION,
        "reference_sources": sources,
        "formula": "getBetas: max(M,1)/max(M+U,2); missing either allele gives NA",
        "yame_source_revision": revision,
        "yame_binary_sha256": sha256(yame),
        "mask_decode_command": command,
        "mask_decode_exit_code": 0,
        "inputs": inputs,
        "beads_per_channel": len(green_ids),
        "probes": len(ordering),
        "channels": dict(Counter(row[3] for row in ordering)),
        "q_track_counts": track_counts,
        "q_masked": sum(qmask),
        "raw_na": raw_na,
        "q_na": q_na,
        "ordered_probe_ids_sha256": probe_digest.hexdigest(),
        "generator_sha256": sha256(Path(__file__)),
        "outputs": {table.name: {"sha256": sha256(table), "bytes": table.stat().st_size}},
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: receipt[key]
                for key in [
                    "status",
                    "scope",
                    "probes",
                    "raw_na",
                    "q_masked",
                    "q_na",
                    "outputs",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
