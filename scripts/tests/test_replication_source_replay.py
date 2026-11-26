"""Fictional public-source replay cases; no patient records."""

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from replication_source_replay import review

HEADER = "GEO_sample,Sample_name,Slide_ID,Array_ID,Gender,Gene,Pathogenic,Age_years\n"
CURATED = (
    HEADER
    + "GSM1,Case1,123,R01C01,Female,KMT2D,YES,4.5\n"
    "GSM3,Other,123,R02C01,Male,KMT2D,NA,NA\n"
)


def soft(assay, title, role, gene, classification, sex, position):
    fields = {
        "case status": role,
        "mutation": gene,
        "variant classification": classification,
        "Sex": sex,
        "slide id": "123",
        "array position": position,
    }
    return f"^SAMPLE = {assay}\n!Sample_title = {title}\n" + "".join(
        f"!Sample_characteristics_ch1 = {key}: {value}\n" for key, value in fields.items()
    )


GEO = (
    soft("GSM1", "Case1", "case", "KMT2D", "pathogenic", "female", "R01C01")
    + soft("GSM2", "Control", "control", "None", "NA", "male", "R01C02")
    + soft("GSM3", "Other", "case", "KMT2D", "VUS", "male", "R02C01")
    + soft("GSM4", "Parent", "case parent", "None", "NA", "female", "R02C02")
)


def call(geo=GEO, curated=CURATED, **kwargs):
    raw, table = geo.encode(), curated.encode()
    options = {
        "geo_sha": hashlib.sha256(raw).hexdigest(),
        "curated_blob": hashlib.sha1(
            f"blob {len(table)}\0".encode() + table, usedforsecurity=False
        ).hexdigest(),
        "expected_cases": 1,
        "expected_source": 4,
        "expected_curated": 2,
    }
    options.update(kwargs)
    return review(raw, table, **options)


class ReplicationSource(unittest.TestCase):
    def test_selected_source_roles_remain_held(self):
        report, manifest, decisions = call()
        self.assertEqual(report["molecular_source_eligible"], 1)
        self.assertEqual(report["selected_control_assays"], 1)
        self.assertEqual(report["source_assays"], 4)
        self.assertEqual(report["curated_selected_diagnosis_ages"], 1)
        self.assertFalse(report["sampling_age_verified"])
        self.assertFalse(report["analysis_admitted"])
        self.assertIsNone(report["independent_participant_count"])
        self.assertNotIn("GSM1", str(report))
        self.assertEqual([s["assay_accession"] for s in manifest["samples"]], ["GSM1", "GSM2"])
        self.assertTrue(all(s["partition"] == "replication" for s in manifest["samples"]))
        self.assertTrue(
            all(
                s["participant_id"] is None
                and s["specimen_id"] is None
                and s["independence"] == "unknown"
                for s in manifest["samples"]
            )
        )
        self.assertEqual(decisions[0]["age_semantics"], "diagnosis_age_not_sampling_age")
        self.assertEqual(decisions[0]["source_reported_classification"], "pathogenic")
        self.assertIsNone(decisions[0]["atlas_acmg_classification"])

    def test_pinned_bytes_fail_closed(self):
        for opts in ({"geo_sha": "0" * 64}, {"curated_blob": "0" * 40}):
            with self.subTest(opts=opts), self.assertRaisesRegex(ValueError, "identity"):
                call(**opts)

    def test_duplicate_and_invalid_assays(self):
        for data in (
            GEO.replace("^SAMPLE = GSM4", "^SAMPLE = GSM1"),
            GEO.replace("^SAMPLE = GSM4", "^SAMPLE = INVALID"),
        ):
            with self.subTest(data=data[-100:]), self.assertRaisesRegex(ValueError, "assay"):
                call(geo=data)

    def test_count_and_role_failures(self):
        for opts in ({"expected_source": 5}, {"expected_curated": 3}, {"expected_cases": 2}):
            with self.subTest(opts=opts), self.assertRaisesRegex(ValueError, "count"):
                call(**opts)
        with self.assertRaisesRegex(ValueError, "role"):
            call(geo=GEO.replace("case status: case parent", "case status: unrelated"))

    def test_ambiguous_characteristics_and_missing_field(self):
        for data in (
            GEO.replace(
                "case status: case\n",
                "case status: case\n!Sample_characteristics_ch1 = case status: control\n",
                1,
            ),
            GEO.replace("!Sample_characteristics_ch1 = Sex: female\n", "", 1),
        ):
            with self.subTest(data=data[:120]), self.assertRaisesRegex(ValueError, "field"):
                call(geo=data)

    def test_discordant_curated_inputs(self):
        for change in (
            CURATED.replace("GSM3,Other", "GSM1,Other"),
            CURATED.replace("GSM3,Other", "GSM4,Other"),
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "join"):
                call(curated=change)
        for change in (
            CURATED.replace("Case1,123", "Wrong,123"),
            CURATED.replace("Case1,123", "Case1,456"),
            CURATED.replace("R01C01,Female", "R06C02,Female"),
            CURATED.replace("Female,KMT2D", "Male,KMT2D"),
            CURATED.replace("Female,KMT2D", "Female,OTHER"),
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "concordance"):
                call(curated=change)

    def test_no_outcome_based_promotion_or_invalid_age(self):
        for change in (
            CURATED.replace("KMT2D,YES,4.5", "KMT2D,YES_predicted,4.5"),
            CURATED.replace("KMT2D,NA,NA", "KMT2D,YES,NA"),
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "classification"):
                call(curated=change)
        for change in (
            CURATED.replace("YES,4.5", "YES,NaN"),
            CURATED.replace("YES,4.5", "YES,-1"),
            CURATED.replace("YES,4.5", "YES,NA"),
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "age"):
                call(curated=change)

    def test_source_fields_and_curated_shape(self):
        for change in (
            CURATED.replace("GEO_sample,Sample_name", "GEO_sample,GEO_sample"),
            CURATED.replace("YES,4.5", "YES"),
            CURATED.replace("YES,4.5", "YES,4.5,extra"),
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "fields"):
                call(curated=change)
        with self.assertRaisesRegex(ValueError, "sex field"):
            call(curated=CURATED.replace("Female", "unknown"))
        report, _, _ = call(
            geo=GEO.replace("Sex: female", "sex: F").replace(
                "variant classification: VUS\n", "phenotype: clinical\n"
            )
        )
        self.assertEqual(report["molecular_source_eligible"], 1)
