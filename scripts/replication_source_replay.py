"""Receive the selected GSE116300 source classifications; never admit a cohort."""

from __future__ import annotations

import csv
import hashlib
import io
import math
import re

GEO = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=gsm&form=text&view=brief"
GEO_SHA256 = "9a8722a365f07c83e6f663d0ab0bb8b7723bd736aad16696d099ee9d2b12c7e1"
CURATED_BLOB = "c696ef1982eb70591e451832eeee4aa3518e0897"
CURATED_URL = (
    "https://raw.githubusercontent.com/demh/epigenetic_ageing_clock/"
    "6fd592a4672a0281818a2a4c45ddf239b892097d/"
    "paper/syndromes_screen/metadata_files/GSE116300/metadata_GSE116300_curated.csv"
)
RULE = "GSE116300-source-pathogenic-KMT2D-v1"
Record = dict[str, object]
REQUIRED = ("case status", "mutation", "sex", "slide id", "array position")
CURATED_FIELDS = (
    "GEO_sample",
    "Sample_name",
    "Slide_ID",
    "Array_ID",
    "Gender",
    "Gene",
    "Pathogenic",
    "Age_years",
)


def label(value: str) -> str:
    return re.sub(r"[\s_-]", "", value).lower()


def sex(value: str) -> str:
    normalized = {"m": "m", "male": "m", "f": "f", "female": "f"}.get(value.strip().lower())
    if normalized is None:
        raise ValueError("invalid source sex field")
    return normalized


def review(
    geo: bytes,
    curated: bytes,
    *,
    geo_sha: str = GEO_SHA256,
    curated_blob: str = CURATED_BLOB,
    expected_cases: int = 9,
    expected_source: int = 44,
    expected_curated: int = 29,
) -> tuple[Record, dict[str, list[Record] | int], list[Record]]:
    if (
        hashlib.sha256(geo).hexdigest() != geo_sha
        or hashlib.sha1(
            f"blob {len(curated)}\0".encode() + curated, usedforsecurity=False
        ).hexdigest()
        != curated_blob
    ):
        raise ValueError("pinned source identity differs")
    samples: dict[str, dict[str, str]] = {}
    text = "\n".join(geo.decode().splitlines())
    for record in re.split(r"(?=^\^SAMPLE = )", text, flags=re.MULTILINE)[1:]:
        assay = record.splitlines()[0].removeprefix("^SAMPLE = ").strip()
        if re.fullmatch(r"GSM[0-9]+", assay) is None or assay in samples:
            raise ValueError("invalid or duplicate GEO assay")
        title = re.findall(r"^!Sample_title = (.+)$", record, re.M)
        fields: dict[str, str] = {}
        for key, value in re.findall(
            r"^!Sample_characteristics_ch1 = ([^:\n]+): *(.*)$", record, re.M
        ):
            key = key.lower()
            if key in (*REQUIRED, "variant classification"):
                if key in fields:
                    raise ValueError("ambiguous source field")
                fields[key] = value.strip()
        if len(title) != 1 or any(not fields.get(key) for key in REQUIRED):
            raise ValueError("missing required source field")
        if fields["case status"] not in ("case", "control", "case parent"):
            raise ValueError("unrecognized source role")
        fields["title"] = title[0]
        samples[assay] = fields
    if len(samples) != expected_source:
        raise ValueError("source assay count differs")

    reader = csv.reader(io.StringIO(curated.decode()))
    header = next(reader, [])
    if len(set(header)) != len(header) or not set(CURATED_FIELDS).issubset(header):
        raise ValueError("invalid curated fields")
    cases: set[str] = set()
    seen: set[str] = set()
    decisions: list[Record] = []
    for values in reader:
        if len(values) != len(header):
            raise ValueError("invalid curated fields")
        row = dict(zip(header, values, strict=True))
        assay = row["GEO_sample"]
        source = samples.get(assay)
        if assay in seen or source is None or source["case status"] != "case":
            raise ValueError("curated case join differs")
        seen.add(assay)
        gene = "NA" if source["mutation"] == "None" else source["mutation"]
        if (
            label(row["Sample_name"]) != label(source["title"])
            or row["Slide_ID"] != source["slide id"]
            or row["Array_ID"] != source["array position"]
            or sex(row["Gender"]) != sex(source["sex"])
            or row["Gene"] != gene
        ):
            raise ValueError("curated/source concordance differs")
        selected = gene == "KMT2D" and source.get("variant classification") == "pathogenic"
        if selected != (row["Gene"] == "KMT2D" and row["Pathogenic"] == "YES"):
            raise ValueError("source molecular classification differs")
        if not selected:
            continue
        try:
            diagnosis_age = float(row["Age_years"])
        except ValueError as exc:
            raise ValueError("invalid curated diagnosis age") from exc
        if not math.isfinite(diagnosis_age) or diagnosis_age < 0:
            raise ValueError("invalid curated diagnosis age")
        cases.add(assay)
        decisions.append(
            {
                "rule": RULE,
                "assay_accession": assay,
                "source_reported_classification": "pathogenic",
                "atlas_acmg_classification": None,
                "age_semantics": "diagnosis_age_not_sampling_age",
                "curated_diagnosis_age_years": diagnosis_age,
                "source_url": GEO,
                "source_sha256": geo_sha,
                "curated_url": CURATED_URL,
                "curated_blob": curated_blob,
            }
        )
    if len(seen) != expected_curated or seen != {
        assay for assay, fields in samples.items() if fields["case status"] == "case"
    }:
        raise ValueError("curated case count differs")
    controls = {assay for assay, fields in samples.items() if fields["case status"] == "control"}
    if len(cases) != expected_cases or len(controls) != expected_cases:
        raise ValueError("selected source count differs")
    declarations: list[Record] = [
        {
            "dataset_accession": "GSE116300",
            "assay_accession": assay,
            "participant_id": None,
            "specimen_id": None,
            "role": "case" if assay in cases else "control",
            "partition": "replication",
            "molecular_eligibility": "eligible" if assay in cases else "not_applicable",
            "independence": "unknown",
            "source": {"url": GEO, "sha256": geo_sha},
        }
        for assay in sorted(cases | controls)
    ]
    report: Record = {
        "rule": RULE,
        "source_geo_sha256": geo_sha,
        "source_curated_blob": curated_blob,
        "source_curated_sha256": hashlib.sha256(curated).hexdigest(),
        "source_assays": len(samples),
        "curated_case_joins": len(seen),
        "molecular_source_eligible": len(cases),
        "selected_control_assays": len(controls),
        "curated_selected_diagnosis_ages": len(decisions),
        "sampling_age_verified": False,
        "atlas_acmg_reclassifications": 0,
        "analysis_admitted": False,
        "independent_participant_count": None,
    }
    return report, {"schema_version": 1, "samples": declarations}, decisions
