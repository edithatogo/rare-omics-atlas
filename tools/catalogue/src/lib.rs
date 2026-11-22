//! Metadata-only adapters for official GEO/PRIDE responses.
//! No expressions, personal characteristics, contact data or patient counts are inferred.
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

mod sample_contract;
pub use sample_contract::{review_sample_json, review_sample_manifest};

pub type Result<T> = std::result::Result<T, String>;
pub type Soft = BTreeMap<String, BTreeMap<String, Vec<String>>>;
pub type CatalogueRows = (Value, Vec<Value>, Vec<Value>);

pub fn validate_accessions(accessions: &[String]) -> Result<()> {
    let mut seen = BTreeSet::new();
    for accession in accessions {
        let digits = accession
            .strip_prefix("GSE")
            .or_else(|| accession.strip_prefix("PXD"));
        if !digits.is_some_and(|s| !s.is_empty() && s.bytes().all(|c| c.is_ascii_digit())) {
            return Err(format!("unsupported accession: {accession}"));
        }
        if !seen.insert(accession) {
            return Err(format!("duplicate accession: {accession}"));
        }
    }
    Ok(())
}

pub fn parse_search(response: &Value) -> Result<Vec<String>> {
    let result = response
        .get("esearchresult")
        .ok_or("missing esearchresult")?;
    if response.get("error").is_some() || result.get("errorlist").is_some() {
        return Err("EUtils reported an error".into());
    }
    let ids = result["idlist"]
        .as_array()
        .ok_or("missing idlist")?
        .iter()
        .map(|x| x.as_str().map(str::to_owned).ok_or("non-string UID".into()))
        .collect::<Result<Vec<_>>>()?;
    let count = result["count"]
        .as_str()
        .ok_or("missing search count")?
        .parse::<usize>()
        .map_err(|e| e.to_string())?;
    if count != ids.len() {
        return Err(format!(
            "truncated search: count={count}, returned={}",
            ids.len()
        ));
    }
    if ids.is_empty() {
        return Err("accession not indexed by EUtils".into());
    }
    Ok(ids)
}

pub fn select_summary(response: &Value, accession: &str) -> Result<Value> {
    let result = response.get("result").ok_or("missing summary result")?;
    let uids = result["uids"].as_array().ok_or("missing summary UIDs")?;
    let matches: Vec<_> = uids
        .iter()
        .filter_map(|uid| uid.as_str().and_then(|uid| result.get(uid)))
        .filter(|record| record["accession"] == accession && record["entrytype"] == "GSE")
        .collect();
    if matches.len() != 1 {
        return Err(format!(
            "expected one exact GSE summary for {accession}, found {}",
            matches.len()
        ));
    }
    Ok(matches[0].clone())
}

/// Parse only named SOFT metadata sections; table records are never interpreted.
pub fn parse_soft(text: &str, entity: &str) -> Result<Soft> {
    let mut sections = Soft::new();
    let mut current: Option<String> = None;
    for line in text.lines() {
        if let Some(section) = line.strip_prefix('^') {
            let (kind, id) = section.split_once(" = ").ok_or("invalid SOFT entity")?;
            current = None;
            if kind == entity {
                if sections.insert(id.to_string(), BTreeMap::new()).is_some() {
                    return Err(format!("duplicate SOFT {entity} {id}"));
                }
                current = Some(id.to_string());
            }
        } else if let (Some(id), Some(field)) = (current.as_ref(), line.strip_prefix('!'))
            && let Some((key, value)) = field.split_once(" = ")
        {
            sections
                .get_mut(id)
                .unwrap()
                .entry(key.to_string())
                .or_default()
                .push(value.to_string());
        }
    }
    if sections.is_empty() {
        return Err(format!("response has no SOFT {entity} sections"));
    }
    Ok(sections)
}

fn values(fields: &BTreeMap<String, Vec<String>>, key: &str) -> Vec<String> {
    fields.get(key).cloned().unwrap_or_default()
}
fn id_set(ids: impl IntoIterator<Item = String>) -> Result<BTreeSet<String>> {
    let mut set = BTreeSet::new();
    for id in ids {
        if !id.starts_with("GSM") || !id[3..].bytes().all(|x| x.is_ascii_digit()) || id.len() == 3 {
            return Err(format!("invalid sample accession {id}"));
        }
        if !set.insert(id.clone()) {
            return Err(format!("duplicate sample accession {id}"));
        }
    }
    Ok(set)
}

pub fn normalise_geo(
    accession: &str,
    summary: &Value,
    series: &Soft,
    samples: &Soft,
) -> Result<CatalogueRows> {
    if summary["accession"] != accession {
        return Err("summary accession mismatch".into());
    }
    let fields = series
        .get(accession)
        .ok_or("SOFT series accession mismatch")?;
    if series.len() != 1 {
        return Err("multiple SOFT series returned".into());
    }
    let expected = id_set(values(fields, "Series_sample_id"))?;
    let observed = id_set(samples.keys().cloned())?;
    if expected != observed {
        return Err(format!(
            "SOFT series/sample membership mismatch: expected {}, returned {}",
            expected.len(),
            observed.len()
        ));
    }
    let summary_samples = summary["samples"]
        .as_array()
        .ok_or("summary sample inventory missing")?;
    let summary_ids = id_set(
        summary_samples
            .iter()
            .map(|s| s["accession"].as_str().unwrap_or("").to_owned()),
    )?;
    // ESummary can truncate sample listings. It remains useful as an independent count,
    // but full SOFT membership is the authority and truncation stays explicit.
    if !summary_ids.is_subset(&expected) {
        return Err("ESummary lists samples absent from SOFT".into());
    }
    let n_samples = summary["n_samples"].as_u64().ok_or("missing n_samples")?;
    if n_samples as usize != expected.len() {
        return Err(format!(
            "source assay counts disagree: ESummary={n_samples}, SOFT={}",
            expected.len()
        ));
    }
    let mut assays = Vec::new();
    let mut files = Vec::new();
    for (gsm, metadata) in samples {
        let tissue: Vec<String> = values(metadata, "Sample_characteristics_ch1")
            .into_iter()
            .filter_map(|s| {
                s.split_once(':')
                    .filter(|(key, _)| {
                        ["tissue", "tissue type", "cell type", "cell line"]
                            .contains(&key.trim().to_lowercase().as_str())
                    })
                    .map(|(key, val)| format!("{}: {}", key.trim(), val.trim()))
            })
            .collect();
        assays.push(json!({"dataset_accession":accession,"assay_accession":gsm,
            "platform_accessions":values(metadata,"Sample_platform_id"),
            "organisms":values(metadata,"Sample_organism_ch1"),
            "molecules":values(metadata,"Sample_molecule_ch1"),"tissue_or_cell_annotations":tissue,
            "source_series_memberships":values(metadata,"Sample_series_id"),
            "source_relations":values(metadata,"Sample_relation"),
            "independent_participant_id":Value::Null,"clinical_metadata_status":"not exported; requires analysis-specific curation"}));
        for url in values(metadata, "Sample_supplementary_file") {
            if url != "NONE" {
                files.push(json!({"dataset_accession":accession,"assay_accession":gsm,"source_url":url,"metadata_scope":"sample","download_verified":false}));
            }
        }
    }
    for url in values(fields, "Series_supplementary_file") {
        if url != "NONE" {
            files.push(json!({"dataset_accession":accession,"assay_accession":Value::Null,"source_url":url,"metadata_scope":"series","download_verified":false}));
        }
    }
    let row = json!({"schema_version":1,"accession":accession,"repository":"GEO","status":"catalogued",
        "title":summary["title"],"assay_types":values(fields,"Series_type"),"platform_accessions":values(fields,"Series_platform_id"),
        "organisms":values(fields,"Series_platform_organism"),"public_date":summary["pdat"],"source_status":values(fields,"Series_status"),
        "submission_date":values(fields,"Series_submission_date"),"last_update_date":values(fields,"Series_last_update_date"),
        "pubmed_ids":summary["pubmedids"],"bioproject":summary["bioproject"],
        "series_relations":values(fields,"Series_relation"),"source_assay_count":n_samples,
        "catalogued_assay_count":observed.len(),"esummary_assay_inventory_complete":summary_ids==expected,
        "independent_participant_count":Value::Null,"analysis_admitted":false,
        "file_inventory_scope":"source-declared series and sample supplementary URLs; no directory scraping, HEAD or raw download",
        "rights_record":"research/registries/dataset-rights.json"});
    Ok((row, assays, files))
}

pub fn normalise_pride(
    accession: &str,
    project: &Value,
    source_files: &Value,
) -> Result<CatalogueRows> {
    if project["accession"] != accession {
        return Err("PRIDE accession mismatch".into());
    }
    let file_array = source_files
        .as_array()
        .ok_or("PRIDE file list must be an unpaginated array")?;
    let mut names = BTreeSet::new();
    let mut files = Vec::new();
    for f in file_array {
        let memberships = f["projectAccessions"]
            .as_array()
            .ok_or("PRIDE file project membership missing")?;
        if !memberships.iter().any(|a| a == accession) {
            return Err("PRIDE file project membership mismatch".into());
        }
        let name = f["fileName"].as_str().ok_or("PRIDE file name missing")?;
        if !names.insert(name) {
            return Err(format!("duplicate PRIDE filename {name}"));
        }
        let urls: Vec<_> = f["publicFileLocations"]
            .as_array()
            .ok_or("PRIDE file locations missing")?
            .iter()
            .map(|x| x["value"].clone())
            .collect();
        files.push(json!({"dataset_accession":accession,"file_name":name,"source_urls":urls,
            "source_size_bytes":f["fileSizeBytes"],"source_checksum":f["checksum"],"source_checksum_algorithm":Value::Null,
            "checksum_note":"API provides checksum without an explicit algorithm in this response; not inferred from string length",
            "source_file_category":f["fileCategory"]["value"],"download_verified":false}));
    }
    let pubmed_ids: Vec<String> = project["references"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|r| {
                    r["pubmedID"]
                        .as_u64()
                        .map(|id| id.to_string())
                        .or_else(|| r["pubmedID"].as_str().map(str::to_owned))
                })
                .collect()
        })
        .unwrap_or_default();
    let names = |key: &str| -> Vec<String> {
        project[key]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|r| r["name"].as_str().map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default()
    };
    Ok((
        json!({"schema_version":1,"accession":accession,"repository":"PRIDE","status":"catalogued",
        "title":project["title"],"public_date":project["publicationDate"],"submission_date":project["submissionDate"],
        "source_license_label":project["license"],"source_submission_type":project["submissionType"],
        "organisms":names("organisms"),"organism_parts":names("organismParts"),"assay_types":names("experimentTypes"),
        "instruments":project["instruments"],"pubmed_ids":pubmed_ids,"source_file_count":files.len(),
        "source_assay_count":Value::Null,"independent_participant_count":Value::Null,"analysis_admitted":false,
        "rights_record":"research/registries/dataset-rights.json"}),
        Vec::new(),
        files,
    ))
}
