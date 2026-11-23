#!/usr/bin/env python3
"""Qualify pinned HM450 raw/Q production exports; never admit a scientific cohort."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from itertools import zip_longest
from pathlib import Path
from typing import cast

from qualify_limma import digest, git, read_object, require

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/contracts/sesame-hm450-raw-q-v1.json"
REPOSITORY = "https://github.com/zhou-lab/sesame.git"
REFERENCE_COLUMNS = ["Probe_ID", "channel", "M_signal", "U_signal", "raw_beta", "q_mask", "q_beta"]
ASSETS = (
    "HM450.ordering.tsv.gz",
    "HM450.hg38.coord.tsv.gz",
    "HM450.typeI_ext.tsv.gz",
    "HM450.hg38.mask.cm",
    "HM450.hg38.mask.cm.idx",
)
SAMPLE = "3999492009_R01C01"
Q_TRACKS = [
    "M_1baseSwitchSNPcommon_5pt",
    "M_2extBase_SNPcommon_5pt",
    "M_mapping",
    "M_nonuniq",
    "M_SNPcommon_5pt",
]
INPUT_NAMES = {f"assets/HM450/{name}" for name in ASSETS} | {
    f"idats/HM450/{SAMPLE}_{colour}.idat" for colour in ("Grn", "Red")
}


def object_field(value: dict[str, object], key: str) -> dict[str, object]:
    item = value.get(key)
    require(isinstance(item, dict), f"missing object: {key}")
    return cast(dict[str, object], item)


def revision(value: dict[str, object], key: str) -> str:
    item = value.get(key)
    require(
        isinstance(item, str) and re.fullmatch(r"[0-9a-f]{40}", item) is not None,
        f"invalid immutable revision: {key}",
    )
    return cast(str, item)


def checked_file(path: Path, pin: dict[str, object]) -> str:
    require(not any(p.is_symlink() for p in [path, *path.parents]), "input path contains a symlink")
    actual = digest(path)
    require(
        type(pin.get("bytes")) is int and path.stat().st_size == pin["bytes"],
        f"input length differs: {path.name}",
    )
    require(actual == pin.get("sha256"), f"input hash differs: {path.name}")
    return actual


def check_inputs(data: Path, reference: Path, contract: dict[str, object]) -> dict[str, str]:
    require(
        type(contract.get("schema_version")) is int and contract["schema_version"] == 1,
        "unsupported contract schema",
    )
    require(
        contract.get("contract_id") == "sesame-hm450-raw-q-v1"
        and contract.get("source_repository") == REPOSITORY
        and contract.get("sample") == SAMPLE
        and contract.get("platform") == "HM450"
        and contract.get("genome_build") == "hg38"
        and type(contract.get("minimum_beads")) is int
        and contract["minimum_beads"] == 0
        and contract.get("stages") == ["raw", "Q"]
        and json.dumps(contract.get("threads")) == "[1, 2]"
        and contract.get("q_tracks") == Q_TRACKS
        and contract.get("scientific_admitted") is False
        and contract.get("official_owner_device_accepted") is False
        and contract.get("full_qcdpb_accepted") is False,
        "unsupported technical contract",
    )
    inputs = object_field(contract, "inputs")
    require(set(inputs) == INPUT_NAMES, "required input set differs")
    hashes = {
        name: checked_file(data / name, object_field(inputs, name)) for name in sorted(INPUT_NAMES)
    }
    hashes["independent_reference"] = checked_file(reference, object_field(contract, "reference"))
    return hashes


def check_source(checkout: Path, contract: dict[str, object]) -> None:
    require(
        not any(path.is_symlink() for path in [checkout / "YAME", checkout, *checkout.parents]),
        "source path contains a symlink",
    )
    require(
        Path(git(checkout, "rev-parse", "--show-toplevel")).resolve() == checkout.resolve(),
        "checkout must be a repository root",
    )
    require(git(checkout, "remote", "get-url", "origin") == REPOSITORY, "wrong source origin")
    for path, key in ((checkout, "source_revision"), (checkout / "YAME", "yame_revision")):
        require(git(path, "rev-parse", "HEAD") == revision(contract, key), "source revision drift")
        require(
            not git(path, "status", "--porcelain", "--untracked-files=all"),
            "source checkout is dirty",
        )
        require(
            all(line.startswith("H ") for line in git(path, "ls-files", "-v").splitlines()),
            "source has hidden index entries",
        )


def annotation_rows(assets: Path, exported: Path) -> tuple[list[str], dict[str, object]]:
    """Validate the actual named annotation export against the entire pinned row space."""
    ids: list[str] = []
    chromosomes: Counter[str] = Counter()
    channels: Counter[str] = Counter()
    extensions: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    with (
        gzip.open(assets / ASSETS[0], "rt", encoding="utf-8", newline="") as ordering,
        gzip.open(assets / ASSETS[1], "rt", encoding="utf-8", newline="") as coordinates,
        gzip.open(assets / ASSETS[2], "rt", encoding="utf-8", newline="") as extension,
        exported.open(encoding="utf-8", newline="") as received,
    ):
        readers = [
            csv.reader(stream, delimiter="\t")
            for stream in (ordering, coordinates, extension, received)
        ]
        expected = [
            ["Probe_ID", "M", "U", "col"],
            ["CpG_chrm", "CpG_beg", "strand", "mapQ"],
            ["ext"],
            ["Probe_ID", "CpG_chrm", "CpG_beg", "strand", "mapQ"],
        ]
        require([next(reader, None) for reader in readers] == expected, "annotation schema differs")
        for rows in zip_longest(*readers):
            require(all(row is not None for row in rows), "annotation row counts differ")
            order, coord, ext, actual = cast(tuple[list[str], ...], rows)
            require(
                [len(row) for row in (order, coord, ext, actual)] == [4, 4, 1, 5],
                "malformed annotation row",
            )
            probe, m, u, channel = order
            require(
                bool(probe.strip()) and channel in ("2", "G", "R"),
                "invalid annotation identity/channel",
            )
            require(
                u.isdecimal()
                and int(u) > 0
                and (
                    (channel == "2" and m == "NA")
                    or (channel != "2" and m.isdecimal() and int(m) > 0)
                ),
                "invalid annotation address semantics",
            )
            require(actual == [probe, *coord], "named coordinate alignment differs")
            ids.append(probe)
            chromosomes[coord[0]] += 1
            channels[channel] += 1
            extensions[ext[0]] += 1
            kinds[probe[:2] if probe[:2] in ("cg", "ch", "rs") else "control"] += 1
    require(bool(ids) and len(set(ids)) == len(ids), "empty or duplicated probe universe")
    return ids, {
        "rows": len(ids),
        "channels": dict(channels),
        "probe_kinds": dict(kinds),
        "coordinate_contigs": dict(chromosomes),
        "extension_codes": dict(extensions),
        "ordered_probe_ids_sha256": hashlib.sha256(
            "".join(p + "\n" for p in ids).encode()
        ).hexdigest(),
        "coordinate_convention": "pinned hg38 CpG_beg is zero-based; no rows filtered",
        "positional_join_basis": "only these checksum-pinned companion files share this ordering",
    }


def beta_value(text: str) -> float | None:
    if text == "NA":
        return None
    value = float(text)
    require(math.isfinite(value) and 0 <= value <= 1, "invalid beta or missing-value token")
    return value


def serialized_beta(value: float) -> float:
    binary32 = struct.unpack("<f", struct.pack("<f", value))[0]
    return float(format(binary32, ".6g"))


def validate_export(
    reference: Path, actual: Path, index: Path, ids: list[str], stage: str, sample: str
) -> dict[str, object]:
    require(stage in ("raw", "Q"), "unsupported preprocessing stage")
    require(index.read_text(encoding="utf-8") == f"{sample}\t0\n", "sample index differs")
    missing = count = endpoints = endpoint_collapses = 0
    max_beta_error = max_m_error = 0.0
    with (
        gzip.open(reference, "rt", encoding="utf-8", newline="") as oracle,
        actual.open(encoding="utf-8", newline="") as received,
    ):
        expected_rows = csv.reader(oracle, delimiter="\t")
        actual_rows = csv.reader(received, delimiter="\t")
        require(
            next(expected_rows, None) == REFERENCE_COLUMNS
            and next(actual_rows, None) == ["Probe_ID", sample],
            "beta schema differs",
        )
        for values in zip_longest(ids, expected_rows, actual_rows):
            probe, expected, row = values
            require(
                probe is not None and expected is not None and row is not None,
                "complete probe universe differs",
            )
            expected = cast(list[str], expected)
            row = cast(list[str], row)
            require(len(expected) == 7 and len(row) == 2, "malformed beta row")
            require(expected[0] == row[0] == probe, "probe identity/order differs")
            target = beta_value(expected[4 if stage == "raw" else 6])
            value = beta_value(row[1])
            count += 1
            if target is None:
                require(value is None, "reference NA was replaced")
                missing += 1
                continue
            require(
                value is not None and value == serialized_beta(target),
                "production beta differs from independent serialized reference",
            )
            value = cast(float, value)
            max_beta_error = max(max_beta_error, abs(value - target))
            if target in (0.0, 1.0):
                endpoints += 1
            elif value in (0.0, 1.0):
                endpoint_collapses += 1
            else:
                max_m_error = max(
                    max_m_error,
                    abs(math.log2(value / (1 - value)) - math.log2(target / (1 - target))),
                )
    return {
        "rows": count,
        "missing": missing,
        "finite": count - missing,
        "reference_endpoints": endpoints,
        "finite_to_endpoint_collapses": endpoint_collapses,
        "maximum_absolute_beta_serialization_error": max_beta_error,
        "maximum_finite_absolute_m_serialization_error": max_m_error,
        "acceptance": "exact binary32 then six-significant-digit serialization",
        "scientific_m_error_budget_accepted": False,
        "text_sha256": digest(actual),
        "sample_index_sha256": digest(index),
    }


def run(
    command: list[str],
    checkout: Path,
    environment: dict[str, str],
    output: Path,
    name: str,
    commands: list[dict[str, object]],
) -> None:
    started = time.monotonic()
    record: dict[str, object] = {
        "command": command,
        "stdout": name + ".stdout",
        "stderr": name + ".stderr",
        "status": "running",
    }
    commands.append(record)
    with (
        (output / (name + ".stdout")).open("w") as stdout,
        (output / (name + ".stderr")).open("w") as stderr,
    ):
        try:
            result = subprocess.run(
                command,
                cwd=checkout,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                check=False,
                timeout=1200,
            )
            record.update(
                exit_code=result.returncode, status="passed" if result.returncode == 0 else "failed"
            )
            require(result.returncode == 0, f"command failed: {name}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            record.update(status="failed", error=type(exc).__name__)
            raise
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 3)


def qualify(
    checkout: Path, data: Path, reference: Path, output: Path, receipt: dict[str, object]
) -> None:
    driver = Path(__file__)
    helpers = driver.with_name("qualify_limma.py")
    implementation = {path.name: digest(path) for path in (driver, helpers)}
    contract = read_object(CONTRACT)
    before = check_inputs(data, reference, contract)
    check_source(checkout, contract)
    receipt.update(
        implementation_sha256=implementation,
        contract_sha256=digest(CONTRACT),
        input_sha256=before,
        source_revision=contract["source_revision"],
        yame_revision=contract["yame_revision"],
    )
    commands: list[dict[str, object]] = []
    receipt["commands"] = commands
    environment = dict(os.environ)
    environment["YAME_DATA_HOME"] = str(data / "assets")
    for name, command in (
        ("clean-sesame", ["make", "clean"]),
        ("clean-yame", ["make", "-C", "YAME", "clean"]),
        ("build", ["make", "-j2", "sesame"]),
        ("version", [str(checkout / "sesame"), "version"]),
    ):
        run(command, checkout, environment, output, name, commands)
    binary = checkout / "sesame"
    receipt["binary_sha256"] = digest(binary)
    receipt["yame_binary_sha256"] = digest(checkout / "YAME/yame")
    assets = data / "assets/HM450"
    run(
        [str(binary), "describe-probe", "--platform", "HM450", str(assets / ASSETS[1])],
        checkout,
        environment,
        output,
        "annotation",
        commands,
    )
    ids, annotation = annotation_rows(assets, output / "annotation.stdout")
    require(
        type(contract.get("probe_count")) is int
        and len(ids) == contract["probe_count"]
        and annotation["ordered_probe_ids_sha256"] == contract.get("ordered_probe_ids_sha256"),
        "pinned probe universe differs",
    )
    receipt["annotation"] = annotation
    results: list[dict[str, object]] = []
    receipt["exports"] = results
    for stage in ("raw", "Q"):
        for threads in (1, 2):
            name = f"{stage}-{threads}"
            target = output / name
            run(
                [
                    str(binary),
                    "preprocess",
                    "--platform",
                    "HM450",
                    "--prep",
                    "" if stage == "raw" else stage,
                    "--mask",
                    str(assets / ASSETS[3]),
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
                    str(data / f"idats/HM450/{SAMPLE}"),
                ],
                checkout,
                environment,
                output,
                name,
                commands,
            )
            run(
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
            result = validate_export(
                reference,
                output / f"{name}-export.stdout",
                target / "beta.cg.idx",
                ids,
                stage,
                SAMPLE,
            )
            result.update(
                stage=stage, threads=threads, binary_output_sha256=digest(target / "beta.cg")
            )
            results.append(result)
    require(
        check_inputs(data, reference, contract) == before, "inputs changed during qualification"
    )
    require(digest(CONTRACT) == receipt["contract_sha256"], "contract changed during qualification")
    require(digest(binary) == receipt["binary_sha256"], "binary changed during qualification")
    require(
        digest(checkout / "YAME/yame") == receipt["yame_binary_sha256"],
        "YAME binary changed during qualification",
    )
    require(
        {path.name: digest(path) for path in (driver, helpers)} == implementation,
        "qualification implementation changed during execution",
    )
    check_source(checkout, contract)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output: Path = args.output.absolute()
    require(
        output.resolve().is_relative_to(ROOT / "artifacts/verification")
        and not any(path.is_symlink() for path in [output, *output.parents]),
        "output must be under artifacts/verification without symlinks",
    )
    output.mkdir(parents=True, exist_ok=False)
    receipt: dict[str, object] = {
        "schema_version": 1,
        "contract_id": "sesame-hm450-raw-q-v1",
        "status": "running",
        "started_at": datetime.now(UTC).isoformat(),
        "scientific_admitted": False,
        "official_owner_device_accepted": False,
        "full_qcdpb_accepted": False,
        "limitations": [
            "One unrelated public HM450 technical pair; raw/Q stages only.",
            "No disease-conditioned analysis, full QCDPB or scientific M-error acceptance.",
            "R execution, software licensing and device outcomes have separate receipts.",
        ],
    }
    path = output / "preprocessing-contract.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    started = time.monotonic()
    try:
        qualify(
            args.checkout.absolute(),
            args.data_root.absolute(),
            args.reference.absolute(),
            output,
            receipt,
        )
        receipt["status"] = "passed"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        receipt.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
    path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(f"Preprocessing qualification {receipt['status']}: {path}")
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
