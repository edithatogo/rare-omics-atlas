#!/usr/bin/env python3
"""Receive a pinned limma synthetic export and compare it with independent R references."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from bootstrap import RUST

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/edithatogo/limma-rust.git"
CONTRACT = "limma-named-contrasts-v1"
PREFIX = "ebayes_robFALSE_trendFALSE"
COLUMNS = [
    "feature_id",
    "contrast_id",
    "estimate",
    "stdev_unscaled",
    "s2_post",
    "ordinary_se",
    "moderated_se",
    "df_residual",
    "df_total",
    "t",
    "p_value",
    "adj_p_value",
    "ci_lower",
    "ci_upper",
    "non_estimable",
    "input_scale",
]
METHOD: dict[str, object] = {
    "fit": "unweighted_least_squares",
    "moderation": "ebayes_default",
    "robust": False,
    "trend": False,
    "adjustment": "BH_per_contrast",
    "confidence_level": 0.95,
    "numeric_type": "float64",
    "missing_value": "NaN",
}
CASES = [
    ("complete", "log2_expression"),
    ("missing", "log2_expression"),
    ("missing", "log2_methylation_odds"),
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_object(path: Path) -> dict[str, object]:
    value: object = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(isinstance(value, dict), "JSON document must be an object")
    return cast(dict[str, object], value)


def read_manifest(path: Path) -> str:
    manifest = read_object(path)
    require(
        type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1,
        "unsupported integration manifest version",
    )
    require(manifest.get("contract_id") == CONTRACT, "unsupported numerical contract")
    require(manifest.get("source_repository") == REPOSITORY, "unexpected source repository")
    revision = manifest.get("source_revision")
    require(
        isinstance(revision, str) and re.fullmatch("[0-9a-f]{40}", revision) is not None,
        "source revision must be an immutable full commit SHA",
    )
    return cast(str, revision)


def check_source(checkout: Path, revision: str) -> None:
    require(
        Path(git(checkout, "rev-parse", "--show-toplevel")).resolve() == checkout.resolve(),
        "checkout must be a repository root",
    )
    require(
        git(checkout, "remote", "get-url", "origin") == REPOSITORY,
        "checkout origin does not match the pinned repository",
    )
    require(git(checkout, "rev-parse", "HEAD") == revision, "checkout revision differs from pin")
    require(
        not git(checkout, "status", "--porcelain", "--untracked-files=all"),
        "checkout contains uncommitted source changes",
    )
    # Git status alone does not reveal assume-unchanged or skip-worktree entries.
    flags = git(checkout, "ls-files", "-v").splitlines()
    require(all(line.startswith("H ") for line in flags), "checkout has hidden source changes")


def prepare_source(checkout: Path, revision: str) -> None:
    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--no-checkout", REPOSITORY, str(checkout)], check=True)
        subprocess.run(["git", "-C", str(checkout), "checkout", "--detach", revision], check=True)
    check_source(checkout, revision)


def matrix(path: Path) -> tuple[list[str], list[str], list[dict[str, float]]]:
    with path.open(encoding="utf-8", newline="") as stream:
        records = list(csv.reader(stream))
    require(
        bool(records) and len(records[0]) > 1 and records[0][0] == "row",
        f"invalid reference header: {path.name}",
    )
    columns = records[0][1:]
    ids = [row[0] for row in records[1:] if row]
    require(
        bool(ids) and len(ids) == len(records) - 1 and len(set(ids)) == len(ids),
        f"invalid reference identities: {path.name}",
    )
    require(len(set(columns)) == len(columns), f"duplicate reference columns: {path.name}")
    require(
        all(len(row) == len(columns) + 1 for row in records[1:]),
        f"invalid reference shape: {path.name}",
    )
    values = [
        {
            column: float("nan") if value == "NA" else float(value)
            for column, value in zip(columns, row[1:], strict=True)
        }
        for row in records[1:]
    ]
    return ids, columns, values


def matches(actual: float, expected: float, field: str) -> bool:
    if not math.isfinite(actual) or not math.isfinite(expected):
        return (math.isnan(actual) and math.isnan(expected)) or actual == expected
    if field in ("estimate", "ci_lower", "ci_upper"):
        tolerance = 1e-10
    elif field in ("p_value", "adj_p_value"):
        tolerance = max(1e-12, 1e-8 * abs(expected))
    else:
        tolerance = (1e-6 if field == "df_total" else 1e-8) * abs(expected)
    return abs(actual - expected) <= tolerance


def validate_exchange(fixture: Path, output: Path, scale: str) -> dict[str, object]:
    """Validate actual received bytes; no fitting, moderation or BH is reimplemented."""
    require(scale in ("log2_expression", "log2_methylation_odds"), "unsupported input scale")
    features, samples, _ = matrix(fixture / "input_log2.csv")
    design_samples, design, _ = matrix(fixture / "design.csv")
    contrast_design, contrasts, _ = matrix(fixture / "contrasts.csv")
    require(design_samples == samples and contrast_design == design, "reference axes disagree")
    metadata = read_object(output / "metadata.json")
    expected_metadata: dict[str, object] = {
        "schema_version": 1,
        "contract_id": CONTRACT,
        "crate_version": "0.1.0",
        "purpose": "synthetic_qualification",
        "input_scale": scale,
        "feature_ids": features,
        "sample_ids": samples,
        "design_ids": design,
        "contrast_ids": contrasts,
        "layout": "contrast_major_then_feature",
        "columns": COLUMNS,
        "method": METHOD,
        "warnings": [],
    }
    # Python's ordinary equality equates True/1 and False/0. Preserve JSON types.
    require(
        json.dumps(metadata, sort_keys=True, allow_nan=False)
        == json.dumps(expected_metadata, sort_keys=True, allow_nan=False),
        "received metadata differs from qualified contract",
    )
    with (output / "estimates.csv").open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == COLUMNS, "received CSV columns differ from contract")
        rows = list(reader)
    require(len(rows) == len(features) * len(contrasts), "received feature universe is incomplete")

    def aligned(name: str, *, ordinal: bool = False) -> list[dict[str, float]]:
        ids, _, values = matrix(fixture / name)
        expected_ids = [str(index + 1) for index in range(len(features))] if ordinal else features
        require(ids == expected_ids, f"reference feature order differs: {name}")
        return values

    unscaled = aligned("contrasts_stdev_unscaled.csv")
    moderated = aligned(f"{PREFIX}_moderated_se.csv")
    # The pinned R recipe's write_mat uses 1..n only when row names are absent.
    # Its missing-case cbind of eBayes scalar vectors retains original input order.
    # This explicit convention applies to that one oracle file, never received rows.
    scalar_ordinals = fixture.name == "missing"
    ebayes = aligned(f"{PREFIX}_scalars.csv", ordinal=scalar_ordinals)
    fitted = aligned("lmfit_scalars.csv")
    comparisons = nonfinite = 0
    worst_relative = 0.0
    for c, contrast in enumerate(contrasts):
        table = aligned(f"{PREFIX}_toptable_{c + 1}.csv")
        for g, feature in enumerate(features):
            row = rows[c * len(features) + g]
            require(
                None not in row and all(isinstance(value, str) for value in row.values()),
                "received CSV row has the wrong number of fields",
            )
            require(
                row["feature_id"] == feature and row["contrast_id"] == contrast,
                "received identities or row order differ",
            )
            require(row["input_scale"] == scale, "received row has the wrong input scale")
            expected = {
                "estimate": table[g]["logFC"],
                "stdev_unscaled": unscaled[g][contrast],
                "s2_post": ebayes[g]["s2_post"],
                "ordinary_se": fitted[g]["sigma"] * unscaled[g][contrast],
                "moderated_se": moderated[g][contrast],
                "df_residual": fitted[g]["df_residual"],
                "df_total": ebayes[g]["df_total"],
                "t": table[g]["t"],
                "p_value": table[g]["P.Value"],
                "adj_p_value": table[g]["adj.P.Val"],
                "ci_lower": table[g]["CI.L"],
                "ci_upper": table[g]["CI.R"],
            }
            non_estimable = math.isnan(expected["estimate"]) or math.isnan(
                expected["stdev_unscaled"]
            )
            require(
                row["non_estimable"] == str(non_estimable).lower(),
                "received non-estimability flag differs",
            )
            for field, reference in expected.items():
                value = float(row[field])
                require(
                    matches(value, reference, field),
                    f"independent R mismatch: {feature}/{contrast}/{field}",
                )
                comparisons += 1
                if not math.isfinite(reference):
                    nonfinite += 1
                elif reference != 0:
                    worst_relative = max(worst_relative, abs(value - reference) / abs(reference))
    return {
        "rows": len(rows),
        "numeric_comparisons": comparisons,
        "nonfinite_values_preserved": nonfinite,
        "worst_finite_relative_error": worst_relative,
        "input_scale": scale,
        "reference_scalar_rows": "one_based_input_order" if scalar_ordinals else "feature_ids",
        "warnings": metadata["warnings"],
        "input_and_reference_sha256": {
            path.name: digest(path) for path in sorted(fixture.glob("*.csv"))
        },
        "output_sha256": {
            name: digest(output / name) for name in ("estimates.csv", "metadata.json")
        },
    }


def qualify(checkout: Path, revision: str, output: Path) -> list[dict[str, object]]:
    prepare_source(checkout, revision)
    exchange = Path(tempfile.mkdtemp(prefix="limma-exchange-", dir=output))
    environment = dict(os.environ)
    for key in ("MD_GOLDEN_CORPUS_DIR", "LIMMA_FRESH_REFERENCE_DIR"):
        environment.pop(key, None)
    results: list[dict[str, object]] = []
    for case, scale in CASES:
        fixture = checkout / "tests-validation/fresh-reference" / case
        received = exchange / f"{case}-{scale}"
        command = [
            "cargo",
            f"+{RUST}",
            "run",
            "--locked",
            "--example",
            "export_named",
            "--",
            str(fixture),
            str(received),
            scale,
        ]
        log = exchange / f"{received.name}.log"
        with log.open("w", encoding="utf-8") as stream:
            subprocess.run(
                command,
                cwd=checkout,
                env=environment,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=1200,
            )
        result = validate_exchange(fixture, received, scale)
        result.update(
            {
                "case": case,
                "command": command,
                "exit_code": 0,
                "output": str(received.relative_to(output)),
            }
        )
        results.append(result)
    check_source(checkout, revision)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "research/contracts/limma-named-v1.json"
    )
    parser.add_argument(
        "--checkout", type=Path, help="existing clean checkout at the manifest revision"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="verification directory for evidence"
    )
    args = parser.parse_args()
    selected_output: Path = args.output.absolute()
    output = selected_output.resolve()
    require(
        output.is_relative_to(ROOT / "artifacts/verification"),
        "output must be under artifacts/verification",
    )
    require(
        not any(path.is_symlink() for path in [selected_output, *selected_output.parents]),
        "output path must not contain a symlink",
    )
    receipt_path = output / "limma-contract.json"
    require(
        not receipt_path.is_symlink() and receipt_path.resolve() != args.manifest.resolve(),
        "receipt must not overwrite an input or follow a symlink",
    )
    require(
        not receipt_path.exists() or receipt_path.stat().st_nlink == 1,
        "receipt must not overwrite a hard-linked file",
    )
    output.mkdir(parents=True, exist_ok=True)
    receipt: dict[str, object] = {
        "schema_version": 1,
        "contract_id": CONTRACT,
        "status": "running",
        "started_at": datetime.now(UTC).isoformat(),
        "scientific_admitted": False,
        "official_owner_device_accepted": False,
        "reference_regenerated": False,
        "rust_toolchain": RUST,
        "limitations": [
            "Only committed synthetic complete/missing fixtures and the named v1 method are qualified.",
            "Transporting a methylation scale declaration does not validate methylation preprocessing.",
            "Production ingestion, actual-device execution and scientific admission remain separate gates.",
        ],
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    try:
        revision = read_manifest(args.manifest)
        checkout = args.checkout or ROOT / "artifacts/integration" / f"limma-{revision}"
        receipt.update(
            {
                "source_repository": REPOSITORY,
                "source_revision": revision,
                "manifest_sha256": digest(args.manifest),
            }
        )
        receipt["cases"] = qualify(checkout.resolve(), revision, output)
        receipt["reference_generator_sha256"] = digest(
            checkout / "tests-validation/scripts/fresh_reference.R"
        )
        receipt["status"] = "passed"
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        receipt.update({"status": "failed", "error": str(exc), "error_type": type(exc).__name__})
        if isinstance(exc, subprocess.CalledProcessError):
            receipt.update({"failed_command": exc.cmd, "exit_code": exc.returncode})
        elif isinstance(exc, subprocess.TimeoutExpired):
            receipt.update({"failed_command": exc.cmd, "exit_code": 124})
    receipt["completed_at"] = datetime.now(UTC).isoformat()
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Limma receiving contract {receipt['status']}: {receipt_path}", flush=True)
    return int(receipt["status"] != "passed")


if __name__ == "__main__":
    raise SystemExit(main())
