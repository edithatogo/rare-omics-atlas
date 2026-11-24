#!/usr/bin/env python3
"""Reconstruct GSE97362 source molecular eligibility, not clinical pathogenicity."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

CASE = "KMT2D LOF discovery cohort"
CONTROL = "Control for KMT2D LOF discovery cohort"
GEO = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362&targ=gsm&form=text&view=brief"
SUPPLEMENT = "https://pmc-oa-opendata.s3.amazonaws.com/PMC5420353.1/mmc1.pdf"
RULE = "GSE97362-S2a-source-lof-v1"
GEO_SHA256 = "820228d67ecf030e9f6c5caef5ca0d7451c960c45eb8b770be5d7e68e12458cf"
SUPPLEMENT_MD5 = "c837df430d84e9881adbcb6709cc0cb3"
SUPPLEMENT_BYTES = 602011
Record = dict[str, object]


def table_s2a(text: str) -> dict[str, tuple[str, str]]:
    section = re.search(
        r"Table\s+S2\..*?a\)\s*KMT2D\s+Loss\s+of\s+Function\s+Mutations(.*?)"
        r"b\)\s*KMT2D\s+Sequence\s+Variants",
        text,
        re.DOTALL,
    )
    if section is None:
        raise ValueError("S2a section not found")
    rows = re.findall(
        r"^[ \t]*(KMT2D-\d+)[ \t]+([^\n]+?)[ \t]+(nonsense|frameshift)[ \t]*$",
        section.group(1),
        re.MULTILINE,
    )
    result = {label: (variant.strip(), consequence) for label, variant, consequence in rows}
    if len(rows) != len(result):
        raise ValueError("duplicate S2a study label")
    return result


def review(
    text: str,
    source_cases: dict[str, tuple[str, str]],
    geo_sha: str,
    supplement_sha: str,
    *,
    expected: int = 11,
) -> tuple[Record, dict[str, list[Record] | int], list[Record]]:
    samples: list[Record] = []
    decisions: list[Record] = []
    assays: set[str] = set()
    case_labels: list[str] = []
    controls = 0
    text = "\n".join(text.splitlines())
    for record in re.split(r"(?=^\^SAMPLE = )", text, flags=re.MULTILINE)[1:]:
        assay = record.splitlines()[0].removeprefix("^SAMPLE = ").strip()
        if assay in assays:
            raise ValueError("duplicate GEO assay")
        assays.add(assay)
        groups = re.findall(r"^!Sample_characteristics_ch1 = sample type: (.+)$", record, re.M)
        if CASE not in groups and CONTROL not in groups:
            continue
        if len(groups) != 1:
            raise ValueError("ambiguous selected source group")
        labels = re.findall(r"^!Sample_description = (.+)$", record, re.M)
        if len(labels) != 1:
            raise ValueError("missing or ambiguous source study label")
        label = labels[0].strip()
        case = groups == [CASE]
        if case:
            case_labels.append(label)
            if label not in source_cases:
                raise ValueError("no exact S2a source join")
            variant, consequence = source_cases[label]
            decisions.append(
                {
                    "rule": RULE,
                    "assay_accession": assay,
                    "study_label": label,
                    "gene": "KMT2D",
                    "transcript_reported": "NM_003482.3",
                    "source_reported_basis": "loss_of_function:" + consequence,
                    "source_variant_text": variant,
                    "source_reported_acmg_classification": None,
                    "source_url": SUPPLEMENT,
                    "source_locator": "Table S2a and Methods: Discovery Cohort",
                    "supplement_sha256": supplement_sha,
                    "geo_sha256": geo_sha,
                    "atlas_acmg_classification": None,
                    "molecular_eligibility": "eligible",
                    "reason": (
                        "Exact source label; independently ascertained source LOF discovery diagnosis"
                    ),
                }
            )
        else:
            controls += 1
        samples.append(
            {
                "dataset_accession": "GSE97362",
                "assay_accession": assay,
                "participant_id": None,
                "specimen_id": None,
                "role": "case" if case else "control",
                "partition": "discovery",
                "molecular_eligibility": "eligible" if case else "not_applicable",
                "independence": "unknown",
                "source": {"url": GEO, "sha256": geo_sha},
            }
        )
    if len(case_labels) != expected or controls != expected:
        raise ValueError("selected source group count differs")
    if set(case_labels) != set(source_cases) or len(set(case_labels)) != expected:
        raise ValueError("S2a exact one-to-one source join differs")
    report: Record = {
        "rule": RULE,
        "source_geo_sha256": geo_sha,
        "source_supplement_sha256": supplement_sha,
        "source_assays": len(assays),
        "molecular_source_eligible": len(case_labels),
        "selected_control_assays": controls,
        "atlas_acmg_reclassifications": 0,
        "analysis_admitted": False,
        "independent_participant_count": None,
    }
    return report, {"schema_version": 1, "samples": samples}, decisions


def write_review(out: Path, report: Record, manifest: object, decisions: object) -> None:
    out.mkdir(parents=True, exist_ok=False)
    for filename, value, key in (
        ("declared-samples.json", manifest, "manifest_sha256"),
        ("molecular-decisions.local.json", decisions, "decision_ledger_sha256"),
    ):
        payload = (json.dumps(value, indent=2) + "\n").encode()
        (out / filename).write_bytes(payload)
        report[key] = hashlib.sha256(payload).hexdigest()
    (out / "aggregate.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


class Arguments(argparse.Namespace):
    geo: Path
    supplement: Path
    out: Path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geo", type=Path, required=True)
    parser.add_argument("--supplement", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv, namespace=Arguments())
    raw = args.geo.read_bytes()
    supplement = args.supplement.read_bytes()
    geo_sha = hashlib.sha256(raw).hexdigest()
    if geo_sha != GEO_SHA256:
        raise ValueError("pinned GEO source differs")
    if (
        len(supplement) != SUPPLEMENT_BYTES
        or hashlib.md5(supplement, usedforsecurity=False).hexdigest() != SUPPLEMENT_MD5
    ):
        raise ValueError("published supplement bytes differ")
    text = subprocess.check_output(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(args.supplement), "-"],
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    report, manifest, decisions = review(
        raw.decode(), table_s2a(text), geo_sha, hashlib.sha256(supplement).hexdigest()
    )
    report["code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    write_review(args.out, report, manifest, decisions)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
