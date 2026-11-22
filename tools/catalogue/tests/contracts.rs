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
