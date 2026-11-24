//! Exact, curated metadata joins; no ontology traversal or patient inference.
use crate::{Result, validate_accessions};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

const DISEASE_HEADER: &str = "disease_label\tgene_symbol\thgnc_id\tmondo_id\tomim_id\tomim_mapping_evidence\torpha_exact\torpha_parent\tgene_relation\tmondo_release\tmondo_sha256\tmondo_source_url\thpo_release\thpoa_internal_version\thpoa_database_id\thpoa_rows\thpoa_unique_positive_terms\thpoa_negative_rows\tmapping_status\tchecked_on\tnotes";

#[derive(Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Source {
    id: String,
    version: String,
    url: String,
    sha256: String,
    license: String,
    license_url: String,
}

#[derive(Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Mapping {
    source_label: String,
    source_id: String,
    term_id: String,
    term_label: String,
    predicate: String,
    evidence: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Registry {
    schema_version: u64,
    sources: Vec<Source>,
    mappings: Vec<Mapping>,
}

// Read only the catalogue's public metadata fields, never copy arbitrary input keys.
#[derive(Deserialize)]
struct Assay {
    dataset_accession: String,
    assay_accession: String,
    organisms: Vec<String>,
    tissue_or_cell_annotations: Vec<String>,
}

fn text(value: &str) -> Result<()> {
    if value.is_empty() || value.trim() != value || value.chars().any(char::is_control) {
        return Err("expected nonempty, unpadded text without control characters".into());
    }
    Ok(())
}

fn numeric_id(value: &str, prefix: &str, width: Option<usize>) -> Result<()> {
    let digits = value
        .strip_prefix(prefix)
        .ok_or("identifier namespace mismatch")?;
    if digits.is_empty()
        || !digits.bytes().all(|byte| byte.is_ascii_digit())
        || width.is_some_and(|width| digits.len() != width)
    {
        return Err("invalid numeric identifier".into());
    }
    Ok(())
}

fn https(value: &str) -> Result<()> {
    text(value)?;
    let url = reqwest::Url::parse(value).map_err(|_| "invalid reference URL")?;
    if url.scheme() != "https" || !url.username().is_empty() || url.password().is_some() {
        return Err("reference URL must be HTTPS without embedded credentials".into());
    }
    Ok(())
}

fn digest(value: &str) -> Result<()> {
    if value.len() != 64
        || !value
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
    {
        return Err("reference SHA-256 must be lowercase hexadecimal".into());
    }
    Ok(())
}

fn hash(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

fn diseases(bytes: &[u8]) -> Result<Vec<Value>> {
    let content = std::str::from_utf8(bytes).map_err(|_| "disease crosswalk must be UTF-8")?;
    let mut lines = content.lines();
    if lines.next() != Some(DISEASE_HEADER) {
        return Err("unsupported disease crosswalk header".into());
    }
    let mut ids = BTreeSet::new();
    let mut omim_ids = BTreeSet::new();
    let mut rows = Vec::new();
    for line in lines {
        let fields: Vec<_> = line.split('\t').collect();
        if fields.len() != 21 {
            return Err("invalid disease crosswalk field count".into());
        }
        for (i, field) in fields.iter().enumerate() {
            if i != 6 && i != 7 {
                text(field)?;
            }
        }
        for (field, prefix, width) in [
            (2, "HGNC:", None),
            (3, "MONDO:", Some(7)),
            (4, "OMIM:", Some(6)),
        ] {
            numeric_id(fields[field], prefix, width)?;
        }
        for field in [6, 7] {
            if !fields[field].is_empty() {
                numeric_id(fields[field], "ORPHA:", None)?;
            }
        }
        if fields[5] != "MONDO:equivalentTo"
            || fields[8] != "has_material_basis_in_germline_mutation_in"
            || fields[14] != fields[4]
            || fields[18] != "verified_from_pinned_ontology"
            || (!fields[6].is_empty() && fields[6] == fields[7])
        {
            return Err("unsupported or conflicting disease mapping semantics".into());
        }
        digest(fields[10])?;
        https(fields[11])?;
        if !ids.insert(fields[3]) || !omim_ids.insert(fields[4]) {
            return Err("duplicate or conflicting disease identifier".into());
        }
        let counts = fields[15..18]
            .iter()
            .map(|s| {
                s.parse::<u64>()
                    .map_err(|_| "invalid HPOA coverage count".into())
            })
            .collect::<Result<Vec<_>>>()?;
        if counts[1] > counts[0] || counts[2] > counts[0] - counts[1] {
            return Err("inconsistent HPOA coverage counts".into());
        }
        let mut row: BTreeMap<_, Value> = DISEASE_HEADER
            .split('\t')
            .zip(fields)
            .map(|(key, value)| (key, json!(value)))
            .collect();
        for (key, count) in [
            "hpoa_rows",
            "hpoa_unique_positive_terms",
            "hpoa_negative_rows",
        ]
        .into_iter()
        .zip(counts)
        {
            row.insert(key, json!(count));
        }
        rows.push(json!(row));
    }
    if rows.is_empty() {
        return Err("disease crosswalk is empty".into());
    }
    rows.sort_by(|a, b| a["mondo_id"].as_str().cmp(&b["mondo_id"].as_str()));
    Ok(rows)
}

/// Join literal source annotations to explicitly curated, versioned references.
/// Source claims and term validity require the separate source receipt; this does
/// not fetch references, infer patient observations, or permit scientific analysis.
pub fn ontology_context(assays: &[u8], crosswalk: &[u8], mappings: &[u8]) -> Result<Value> {
    let mut registry: Registry = serde_json::from_slice(mappings)
        .map_err(|_| "invalid ontology mapping JSON, fields or types")?;
    if registry.schema_version != 1 || registry.sources.is_empty() || registry.mappings.is_empty() {
        return Err("unsupported or empty ontology mapping registry".into());
    }
    let mut sources = BTreeSet::new();
    for source in &registry.sources {
        if !["UBERON", "CL"].contains(&source.id.as_str()) || !sources.insert(&source.id) {
            return Err("unsupported or duplicate ontology source".into());
        }
        text(&source.version)?;
        text(&source.license)?;
        https(&source.url)?;
        https(&source.license_url)?;
        digest(&source.sha256)?;
    }
    let mut seen = BTreeSet::new();
    let mut term_labels = BTreeMap::new();
    for mapping in &registry.mappings {
        for field in [
            &mapping.source_label,
            &mapping.term_label,
            &mapping.evidence,
        ] {
            text(field)?;
        }
        if !sources.contains(&mapping.source_id)
            || !["skos:exactMatch", "skos:broadMatch", "skos:relatedMatch"]
                .contains(&mapping.predicate.as_str())
        {
            return Err("unbound source or unsupported mapping predicate".into());
        }
        numeric_id(
            &mapping.term_id,
            &format!("{}:", mapping.source_id),
            Some(7),
        )?;
        if !seen.insert((&mapping.source_label, &mapping.term_id)) {
            return Err("duplicate or conflicting context mapping".into());
        }
        if term_labels
            .insert(&mapping.term_id, &mapping.term_label)
            .is_some_and(|prior| prior != &mapping.term_label)
        {
            return Err("conflicting labels for one ontology term".into());
        }
    }
    registry.sources.sort_by(|a, b| a.id.cmp(&b.id));
    registry
        .mappings
        .sort_by(|a, b| (&a.source_label, &a.term_id).cmp(&(&b.source_label, &b.term_id)));
    let reference_diseases = diseases(crosswalk)?;
    let content = std::str::from_utf8(assays).map_err(|_| "assay JSONL must be UTF-8")?;
    let mut memberships = BTreeSet::new();
    let mut summary = BTreeMap::from([
        ("exact", 0),
        ("broader", 0),
        ("related", 0),
        ("ambiguous", 0),
        ("unmapped", 0),
    ]);
    let mut unreported_memberships = 0;
    let mut rows = Vec::new();
    for line in content.lines() {
        let assay: Assay =
            serde_json::from_str(line).map_err(|_| "invalid assay metadata JSONL")?;
        validate_accessions(std::slice::from_ref(&assay.dataset_accession))?;
        numeric_id(&assay.dataset_accession, "GSE", None)?;
        numeric_id(&assay.assay_accession, "GSM", None)?;
        if !memberships.insert((
            assay.dataset_accession.clone(),
            assay.assay_accession.clone(),
        )) {
            return Err("duplicate series-assay membership".into());
        }
        let mut labels = BTreeSet::new();
        for label in &assay.tissue_or_cell_annotations {
            text(label)?;
            if !labels.insert(label) {
                return Err("duplicate source annotation".into());
            }
        }
        for organism in &assay.organisms {
            text(organism)?;
        }
        let mut annotations = Vec::new();
        for label in labels {
            let candidates: Vec<_> = registry
                .mappings
                .iter()
                .filter(|m| &m.source_label == label)
                .collect();
            let status = match candidates.as_slice() {
                [] => "unmapped",
                [one] if one.predicate == "skos:exactMatch" => "exact",
                [one] if one.predicate == "skos:relatedMatch" => "related",
                [_] => "broader",
                _ => "ambiguous",
            };
            *summary.get_mut(status).unwrap() += 1;
            annotations.push(json!({"source_label":label,"status":status,"candidates":candidates}));
        }
        if annotations.is_empty() {
            unreported_memberships += 1;
        }
        rows.push(json!({"dataset_accession":assay.dataset_accession,"assay_accession":assay.assay_accession,
            "organisms":assay.organisms,"context_status":if annotations.is_empty(){"unreported"}else{"reported"},
            "annotations":annotations}));
    }
    if rows.is_empty() {
        return Err("assay catalogue is empty".into());
    }
    rows.sort_by(|a, b| {
        (
            a["dataset_accession"].as_str(),
            a["assay_accession"].as_str(),
        )
            .cmp(&(
                b["dataset_accession"].as_str(),
                b["assay_accession"].as_str(),
            ))
    });
    Ok(
        json!({"schema_version":1,"scope":"curated_reference_and_source_metadata_context",
        "analysis_admitted":false,"source_claims_verified":false,"independent_participant_count":Value::Null,
        "input_sha256":{"assays":hash(assays),
            "disease_crosswalk":hash(crosswalk),
            "context_mappings":hash(mappings)},
        "sources":registry.sources,"reference_diseases":reference_diseases,
        "disease_reference_scope":"reference concepts only; no assay diagnosis or observed participant phenotype",
        "mapping_direction":"source label to ontology term; broadMatch target is broader than source",
        "summary":{"series_assay_memberships":rows.len(),"unreported_memberships":unreported_memberships,
            "annotation_status_counts":summary},
        "assays":rows}),
    )
}
