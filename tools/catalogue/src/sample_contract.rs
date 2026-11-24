//! Structural review of locally curated declarations, never scientific admission.
use crate::Result;
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

fn choice(value: &str, key: &str, options: &[&str]) -> Result<()> {
    if !options.contains(&value) {
        return Err(format!("unsupported {key}"));
    }
    Ok(())
}

fn identifier(value: &Value, key: &str) -> Result<()> {
    if value.is_null() {
        return Ok(());
    }
    let value = value
        .as_str()
        .ok_or_else(|| format!("{key} must be text or null"))?;
    if value.is_empty()
        || value.trim() != value
        || value.len() > 128
        || ["unknown", "na", "n/a", "none", "null", "?"].contains(&value.to_lowercase().as_str())
    {
        return Err(format!("{key} must be a declared identifier or null"));
    }
    Ok(())
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Manifest {
    schema_version: u64,
    samples: Vec<Sample>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Source {
    url: String,
    sha256: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Sample {
    #[serde(rename = "dataset_accession")]
    dataset: String,
    #[serde(rename = "assay_accession")]
    assay: String,
    #[serde(rename = "participant_id")]
    participant: Value,
    #[serde(rename = "specimen_id")]
    specimen: Value,
    role: String,
    partition: String,
    #[serde(rename = "molecular_eligibility")]
    molecular: String,
    independence: String,
    source: Source,
}

impl Sample {
    fn validate(&self) -> Result<()> {
        for (accession, prefix) in [(&self.dataset, "GSE"), (&self.assay, "GSM")] {
            if !accession.strip_prefix(prefix).is_some_and(|digits| {
                !digits.is_empty() && digits.bytes().all(|byte| byte.is_ascii_digit())
            }) {
                return Err("expected public GEO series and assay accessions".into());
            }
        }
        let url = reqwest::Url::parse(&self.source.url).map_err(|_| "invalid source URL")?;
        if url.scheme() != "https"
            || url.host_str().is_none()
            || !url.username().is_empty()
            || url.password().is_some()
        {
            return Err("source URL must be HTTPS without embedded credentials".into());
        }
        let digest = &self.source.sha256;
        if digest.len() != 64
            || !digest
                .bytes()
                .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
        {
            return Err("source SHA-256 must be 64 lowercase hexadecimal characters".into());
        }
        choice(
            &self.role,
            "role",
            &["case", "control", "excluded", "unknown"],
        )?;
        choice(
            &self.molecular,
            "molecular_eligibility",
            &["eligible", "ineligible", "unknown", "not_applicable"],
        )?;
        if self.molecular == "not_applicable"
            && !["control", "excluded"].contains(&self.role.as_str())
        {
            return Err("molecular not_applicable requires a control or excluded role".into());
        }
        identifier(&self.participant, "participant_id")?;
        identifier(&self.specimen, "specimen_id")?;
        choice(
            &self.partition,
            "partition",
            &["discovery", "replication", "unknown"],
        )?;
        choice(
            &self.independence,
            "independence",
            &["verified", "overlap", "unknown"],
        )
    }

    fn excluded(&self) -> bool {
        self.role == "excluded" || self.molecular == "ineligible"
    }
}

/// Check declarations and identity consistency. Source references are not dereferenced,
/// participant IDs are never inferred, and no result permits scientific analysis.
pub fn review_sample_manifest(manifest: &Value) -> Result<Value> {
    review(
        serde_json::from_value(manifest.clone())
            .map_err(|_| "invalid sample manifest fields or types")?,
    )
}

/// Parse a local manifest with duplicate-key rejection before reviewing declarations.
pub fn review_sample_json(bytes: &[u8]) -> Result<Value> {
    review(
        serde_json::from_slice(bytes)
            .map_err(|_| "invalid sample manifest JSON, fields or types")?,
    )
}

fn review(manifest: Manifest) -> Result<Value> {
    if manifest.schema_version != 1 {
        return Err("unsupported sample manifest schema".into());
    }
    let mut samples = manifest.samples;
    if samples.is_empty() {
        return Err("samples must be a nonempty array".into());
    }
    for sample in &samples {
        sample.validate()?;
    }
    samples.sort_by(|a, b| (&a.dataset, &a.assay).cmp(&(&b.dataset, &b.assay)));
    let mut assays = BTreeSet::new();
    let mut participants: BTreeMap<&str, Vec<usize>> = BTreeMap::new();
    let mut specimens: BTreeMap<&str, Vec<usize>> = BTreeMap::new();
    let mut reasons: Vec<BTreeSet<&str>> = vec![BTreeSet::new(); samples.len()];
    for (index, sample) in samples.iter().enumerate() {
        if !assays.insert(sample.assay.as_str()) {
            return Err("duplicate assay assignment in sample manifest".into());
        }
        if sample.excluded() {
            reasons[index].insert("excluded_by_declaration");
            continue;
        }
        for (unknown, reason) in [
            (sample.participant.is_null(), "participant_unknown"),
            (sample.specimen.is_null(), "specimen_unknown"),
            (sample.role == "unknown", "role_unknown"),
            (sample.partition == "unknown", "partition_unknown"),
            (
                sample.molecular == "unknown",
                "molecular_eligibility_unknown",
            ),
            (sample.independence == "unknown", "independence_unknown"),
            (sample.independence == "overlap", "declared_overlap"),
        ] {
            if unknown {
                reasons[index].insert(reason);
            }
        }
        if let Some(id) = sample.participant.as_str() {
            participants.entry(id).or_default().push(index);
        }
        if let Some(id) = sample.specimen.as_str() {
            specimens.entry(id).or_default().push(index);
        }
    }
    for indices in participants.values().filter(|indices| indices.len() > 1) {
        let partitions: BTreeSet<_> = indices
            .iter()
            .map(|&index| samples[index].partition.as_str())
            .filter(|&value| value != "unknown")
            .collect();
        let roles: BTreeSet<_> = indices
            .iter()
            .map(|&index| samples[index].role.as_str())
            .filter(|&value| value != "unknown")
            .collect();
        for &index in indices {
            reasons[index].insert("repeated_participant_requires_selection_or_model");
            if partitions.len() > 1 {
                reasons[index].insert("participant_crosses_partitions");
            }
            if roles.len() > 1 {
                reasons[index].insert("participant_role_conflict");
            }
        }
    }
    for indices in specimens.values().filter(|indices| indices.len() > 1) {
        for &index in indices {
            reasons[index].insert("repeated_specimen_requires_selection_or_model");
        }
    }
    let mut counts = BTreeMap::from([("ready_for_review", 0), ("held", 0), ("excluded", 0)]);
    let reports: Vec<_> = samples
        .iter()
        .zip(reasons)
        .map(|(sample, reasons)| {
            let status = if sample.excluded() {
                "excluded"
            } else if reasons.is_empty() {
                "ready_for_review"
            } else {
                "held"
            };
            *counts.get_mut(status).unwrap() += 1;
            json!({"dataset_accession":sample.dataset,"assay_accession":sample.assay,
            "status":status,"reasons":reasons,"analysis_admitted":false})
        })
        .collect();
    Ok(
        json!({"schema_version":1,"scope":"declared_sample_contract_only",
        "analysis_admitted":false,"independent_participant_count":Value::Null,
        "source_claims_verified":false,"summary":counts,"samples":reports,
        "pending_gates":["source_claim_review","source_rights_and_disclosure","covariates_and_design","technical_preprocessing_and_qc",
            "institutional_classification","selected_backend_and_device","analysis_specific_n1"]}),
    )
}
