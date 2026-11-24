use rare_omics_catalogue::{
    normalise_geo, parse_search, parse_soft, select_summary, validate_accessions,
};
use serde_json::json;

#[test]
fn invalid_or_duplicate_seed_fails() {
    assert!(validate_accessions(&["GSE1".into(), "GSE1".into()]).is_err());
    assert!(validate_accessions(&["GSE1/../../x".into()]).is_err());
}
#[test]
fn search_errors_or_truncation_are_not_zero_results() {
    assert!(parse_search(&json!({"error":"API rate limit exceeded"})).is_err());
    assert!(parse_search(&json!({"esearchresult":{"count":"2","idlist":["2001"]}})).is_err());
}
#[test]
fn wrong_summary_accession_fails() {
    assert!(
        select_summary(
            &json!({"result":{"uids":["x"],"x":{"accession":"GSE2","entrytype":"GSE"}}}),
            "GSE1"
        )
        .is_err()
    );
}
#[test]
fn html_is_not_soft() {
    assert!(parse_soft("<html>Checking your browser</html>", "SAMPLE").is_err());
}
#[test]
fn duplicated_sample_is_not_silently_counted_twice() {
    assert!(parse_soft("^SAMPLE = GSM1\n^SAMPLE = GSM1\n", "SAMPLE").is_err());
}
#[test]
fn published_metadata_excludes_contacts_and_personal_traits() {
    let series = parse_soft("^SERIES = GSE1\n!Series_sample_id = GSM1\n!Series_platform_id = GPL1\n!Series_relation = SubSeries of: GSE2\n", "SERIES").unwrap();
    let samples = parse_soft("^SAMPLE = GSM1\n!Sample_platform_id = GPL1\n!Sample_characteristics_ch1 = tissue: blood\n!Sample_characteristics_ch1 = age: 7\n!Sample_contact_email = secret@example.org\n!Sample_title = named phenotype\n!Sample_organism_ch1 = Homo sapiens\n", "SAMPLE").unwrap();
    let result = normalise_geo("GSE1", &json!({"accession":"GSE1","entrytype":"GSE","n_samples":1,"samples":[{"accession":"GSM1"}]}), &series, &samples).unwrap();
    let encoded = serde_json::to_string(&result).unwrap();
    assert!(!encoded.contains("secret@example.org"));
    assert!(!encoded.contains("named phenotype"));
    assert!(!encoded.contains("age"));
    assert!(encoded.contains("blood"));
    assert!(result.0["independent_participant_count"].is_null());
    assert_eq!(result.0["series_relations"][0], "SubSeries of: GSE2");
}
#[test]
fn mismatched_assay_inventories_fail() {
    let series = parse_soft("^SERIES = GSE1\n!Series_sample_id = GSM1\n", "SERIES").unwrap();
    let samples = parse_soft("^SAMPLE = GSM2\n", "SAMPLE").unwrap();
    assert!(normalise_geo("GSE1", &json!({"accession":"GSE1","entrytype":"GSE","n_samples":1,"samples":[{"accession":"GSM1"}]}), &series, &samples).is_err());
}

#[test]
fn source_count_disagreement_fails() {
    let series = parse_soft("^SERIES = GSE1\n!Series_sample_id = GSM1\n", "SERIES").unwrap();
    let samples = parse_soft("^SAMPLE = GSM1\n", "SAMPLE").unwrap();
    assert!(normalise_geo("GSE1", &json!({"accession":"GSE1","entrytype":"GSE","n_samples":2,"samples":[{"accession":"GSM1"}]}), &series, &samples).is_err());
}

#[test]
fn truncated_summary_keeps_complete_soft_membership() {
    let series = parse_soft(
        "^SERIES = GSE1\n!Series_sample_id = GSM1\n!Series_sample_id = GSM2\n",
        "SERIES",
    )
    .unwrap();
    let samples = parse_soft("^SAMPLE = GSM1\n^SAMPLE = GSM2\n", "SAMPLE").unwrap();
    let result = normalise_geo("GSE1", &json!({"accession":"GSE1","entrytype":"GSE","n_samples":2,"samples":[{"accession":"GSM1"}]}), &series, &samples).unwrap();
    assert_eq!(result.0["catalogued_assay_count"], 2);
    assert_eq!(result.0["esummary_assay_inventory_complete"], false);
}

#[test]
fn pride_wrong_file_membership_fails() {
    assert!(
        rare_omics_catalogue::normalise_pride(
            "PXD1",
            &json!({"accession":"PXD1"}),
            &json!([{"projectAccessions":["PXD2"],"fileName":"x"}])
        )
        .is_err()
    );
}

fn declared_samples() -> serde_json::Value {
    json!({"schema_version":1,"samples":[{
        "dataset_accession":"GSE1","assay_accession":"GSM1",
        "participant_id":"SYNTHETIC-PARTICIPANT-A","specimen_id":"SYNTHETIC-SPECIMEN-A",
        "role":"case","partition":"discovery","molecular_eligibility":"eligible",
        "independence":"verified",
        "source":{"url":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE1","sha256":"a".repeat(64)}
    }]})
}

#[test]
fn complete_declarations_do_not_admit_science_or_export_private_identifiers() {
    let report = rare_omics_catalogue::review_sample_manifest(&declared_samples()).unwrap();
    assert_eq!(report["summary"]["ready_for_review"], 1);
    assert_eq!(report["samples"][0]["status"], "ready_for_review");
    assert_eq!(report["analysis_admitted"], false);
    assert_eq!(report["source_claims_verified"], false);
    assert!(report["independent_participant_count"].is_null());
    assert!(!report["pending_gates"].as_array().unwrap().is_empty());
    let encoded = report.to_string();
    for private in [
        "SYNTHETIC-PARTICIPANT-A",
        "SYNTHETIC-SPECIMEN-A",
        "https://",
        "sha256",
    ] {
        assert!(!encoded.contains(private));
    }
}

#[test]
fn unknown_identity_diagnosis_roles_and_overlap_remain_held() {
    let mut manifest = declared_samples();
    let row = &mut manifest["samples"][0];
    row["participant_id"] = serde_json::Value::Null;
    row["specimen_id"] = serde_json::Value::Null;
    for key in ["role", "partition", "molecular_eligibility", "independence"] {
        row[key] = json!("unknown");
    }
    let report = rare_omics_catalogue::review_sample_manifest(&manifest).unwrap();
    assert_eq!(report["summary"]["held"], 1);
    assert_eq!(report["samples"][0]["reasons"].as_array().unwrap().len(), 6);
    assert_eq!(report["samples"][0]["analysis_admitted"], false);
    manifest["samples"][0]["independence"] = json!("overlap");
    let report = rare_omics_catalogue::review_sample_manifest(&manifest).unwrap();
    assert!(
        report["samples"][0]["reasons"]
            .as_array()
            .unwrap()
            .contains(&json!("declared_overlap"))
    );
}

#[test]
fn malformed_or_ambiguous_sample_contracts_fail_closed() {
    let mut invalid = vec![
        serde_json::Value::Null,
        json!({}),
        json!({"schema_version":2,"samples":[]}),
        json!({"schema_version":1,"samples":null}),
        json!({"schema_version":1,"samples":[]}),
        json!({"schema_version":1,"samples":[null]}),
    ];
    for (field, value) in [
        ("dataset_accession", json!("PXD1")),
        ("assay_accession", json!("GSM")),
        ("dataset_accession", json!(false)),
        ("assay_accession", json!("GSM1x")),
        ("participant_id", json!(false)),
        ("participant_id", json!("unknown")),
        ("participant_id", json!("")),
        ("participant_id", json!(" padded ")),
        ("participant_id", json!("x".repeat(129))),
        ("specimen_id", json!("NA")),
        ("role", json!("patient")),
        ("role", json!(null)),
        ("partition", json!("test")),
        ("molecular_eligibility", json!("not_applicable")),
        ("molecular_eligibility", json!(true)),
        ("independence", json!("probably")),
        ("source", json!({"url":"https://example.org"})),
    ] {
        let mut manifest = declared_samples();
        manifest["samples"][0][field] = value;
        invalid.push(manifest);
    }
    for (field, value) in [
        ("url", json!("not a URL")),
        ("url", json!("http://example.org/source")),
        ("url", json!("https://name:password@example.org/source")),
        ("url", json!("https://:password@example.org/source")),
        ("sha256", json!("f".repeat(63))),
        ("sha256", json!("A".repeat(64))),
        ("sha256", json!(false)),
    ] {
        let mut manifest = declared_samples();
        manifest["samples"][0]["source"][field] = value;
        invalid.push(manifest);
    }
    let mut extra = declared_samples();
    extra["samples"][0]["unexpected_contact"] = json!("must not be exported");
    invalid.push(extra);
    for field in declared_samples()["samples"][0].as_object().unwrap().keys() {
        let mut missing = declared_samples();
        missing["samples"][0].as_object_mut().unwrap().remove(field);
        invalid.push(missing);
    }
    for manifest in invalid {
        assert!(rare_omics_catalogue::review_sample_manifest(&manifest).is_err());
    }
}

#[test]
fn duplicate_assay_memberships_cannot_count_as_independent_samples() {
    let mut manifest = declared_samples();
    let mut second = manifest["samples"][0].clone();
    second["dataset_accession"] = json!("GSE2");
    manifest["samples"].as_array_mut().unwrap().push(second);
    assert!(
        rare_omics_catalogue::review_sample_manifest(&manifest)
            .unwrap_err()
            .contains("duplicate assay")
    );
}

#[test]
fn repeated_participants_hold_every_affected_assay_and_expose_split_conflicts() {
    for (role, partition) in [
        ("case", "discovery"),
        ("control", "replication"),
        ("unknown", "unknown"),
    ] {
        let mut manifest = declared_samples();
        let mut second = manifest["samples"][0].clone();
        second["assay_accession"] = json!("GSM2");
        second["specimen_id"] = json!("SYNTHETIC-SPECIMEN-B");
        second["role"] = json!(role);
        second["partition"] = json!(partition);
        manifest["samples"].as_array_mut().unwrap().push(second);
        let report = rare_omics_catalogue::review_sample_manifest(&manifest).unwrap();
        assert_eq!(report["summary"]["held"], 2);
        for row in report["samples"].as_array().unwrap() {
            let reasons = row["reasons"].as_array().unwrap();
            assert!(reasons.contains(&json!("repeated_participant_requires_selection_or_model")));
            assert_eq!(
                reasons.contains(&json!("participant_crosses_partitions")),
                partition == "replication"
            );
            assert_eq!(
                reasons.contains(&json!("participant_role_conflict")),
                role == "control"
            );
        }
    }
}

#[test]
fn repeated_specimens_hold_all_rows_even_with_different_declared_participants() {
    let mut manifest = declared_samples();
    let mut second = manifest["samples"][0].clone();
    second["assay_accession"] = json!("GSM2");
    second["participant_id"] = json!("SYNTHETIC-PARTICIPANT-B");
    second["partition"] = json!("replication");
    manifest["samples"].as_array_mut().unwrap().push(second);
    let report = rare_omics_catalogue::review_sample_manifest(&manifest).unwrap();
    assert_eq!(report["summary"]["held"], 2);
    for row in report["samples"].as_array().unwrap() {
        assert!(
            row["reasons"]
                .as_array()
                .unwrap()
                .contains(&json!("repeated_specimen_requires_selection_or_model"))
        );
    }
}

#[test]
fn explicit_exclusions_do_not_block_the_remaining_selected_assay() {
    for (role, molecular) in [("excluded", "unknown"), ("case", "ineligible")] {
        let mut manifest = declared_samples();
        let mut excluded = manifest["samples"][0].clone();
        excluded["assay_accession"] = json!("GSM2");
        excluded["role"] = json!(role);
        excluded["molecular_eligibility"] = json!(molecular);
        manifest["samples"].as_array_mut().unwrap().push(excluded);
        let report = rare_omics_catalogue::review_sample_manifest(&manifest).unwrap();
        assert_eq!(report["summary"]["ready_for_review"], 1);
        assert_eq!(report["summary"]["excluded"], 1);
        assert_eq!(report["analysis_admitted"], false);
    }
}

#[test]
fn source_declared_controls_and_order_are_explicit() {
    let mut manifest = declared_samples();
    let mut control = manifest["samples"][0].clone();
    control["assay_accession"] = json!("GSM2");
    control["participant_id"] = json!("SYNTHETIC-PARTICIPANT-B");
    control["specimen_id"] = json!("SYNTHETIC-SPECIMEN-B");
    control["role"] = json!("control");
    control["molecular_eligibility"] = json!("not_applicable");
    manifest["samples"].as_array_mut().unwrap().push(control);
    let expected = rare_omics_catalogue::review_sample_manifest(&manifest).unwrap();
    assert_eq!(expected["summary"]["ready_for_review"], 2);
    manifest["samples"].as_array_mut().unwrap().reverse();
    assert_eq!(
        rare_omics_catalogue::review_sample_manifest(&manifest).unwrap(),
        expected
    );
}

#[test]
fn local_sample_review_cli_distinguishes_ready_held_and_invalid_without_writing_inputs() {
    use std::{
        fs,
        process::Command,
        time::{SystemTime, UNIX_EPOCH},
    };
    let root = std::env::temp_dir().join(format!(
        "sample-contract-{}-{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir_all(&root).unwrap();
    let path = root.join("manifest.json");
    let mut held = declared_samples();
    held["samples"][0]["participant_id"] = serde_json::Value::Null;
    let mut excluded = declared_samples();
    excluded["samples"][0]["role"] = json!("excluded");
    for (manifest, expected_code) in [
        (declared_samples(), 0),
        (held, 2),
        (excluded, 2),
        (json!({}), 1),
    ] {
        let bytes = serde_json::to_vec(&manifest).unwrap();
        fs::write(&path, &bytes).unwrap();
        let result = Command::new(env!("CARGO_BIN_EXE_sample-contract"))
            .args(["--input"])
            .arg(&path)
            .output()
            .unwrap();
        assert_eq!(result.status.code(), Some(expected_code));
        assert_eq!(fs::read(&path).unwrap(), bytes);
        if expected_code != 1 {
            let report: serde_json::Value = serde_json::from_slice(&result.stdout).unwrap();
            assert_eq!(report["analysis_admitted"], false);
            assert!(
                !String::from_utf8(result.stdout)
                    .unwrap()
                    .contains("SYNTHETIC-PARTICIPANT")
            );
        } else {
            assert!(result.stdout.is_empty());
        }
    }
    let valid_json = declared_samples().to_string();
    for bytes in [
        b"not JSON".to_vec(),
        vec![b' '; 16 * 1024 * 1024 + 1],
        valid_json
            .replace(
                "\"participant_id\":",
                "\"participant_id\":null,\"participant_id\":",
            )
            .into_bytes(),
        valid_json
            .replace(
                "\"participant_id\":",
                "\"participant_\\u0069d\":null,\"participant_id\":",
            )
            .into_bytes(),
        valid_json
            .replace(
                "\"schema_version\":1",
                "\"schema_version\":1,\"schema_version\":1",
            )
            .into_bytes(),
        valid_json
            .replace("\"sha256\":", "\"sha256\":\"unreviewed\",\"sha256\":")
            .into_bytes(),
    ] {
        fs::write(&path, bytes).unwrap();
        let result = Command::new(env!("CARGO_BIN_EXE_sample-contract"))
            .arg("--input")
            .arg(&path)
            .output()
            .unwrap();
        assert_eq!(result.status.code(), Some(1));
        assert!(result.stdout.is_empty());
    }
    fs::remove_file(&path).unwrap();
    let result = Command::new(env!("CARGO_BIN_EXE_sample-contract"))
        .arg("--input")
        .arg(&path)
        .output()
        .unwrap();
    assert_eq!(result.status.code(), Some(1));
    fs::remove_dir_all(root).unwrap();
}
