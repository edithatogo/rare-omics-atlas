use clap::Parser;
use rare_omics_catalogue::{
    CatalogueRows, normalise_geo, normalise_pride, parse_search, parse_soft, select_summary,
    validate_accessions,
};
use reqwest::blocking::Client;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeSet,
    fs,
    io::{Read, Write},
    path::{Path, PathBuf},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

const MAX_RESPONSE: u64 = 32 * 1024 * 1024;
const EU: &str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";
const TOOL: &str = "rare_omics_atlas_catalogue";

#[derive(Parser)]
#[command(
    version,
    about = "Catalogue explicit public GEO/PRIDE accessions through official metadata APIs; never downloads assay matrices"
)]
struct Args {
    #[arg(long)]
    registry: PathBuf,
    #[arg(long)]
    out: PathBuf,
    #[arg(long)]
    cache: PathBuf,
    #[arg(long)]
    extra: Vec<String>,
    #[arg(long, conflicts_with = "offline")]
    refresh: bool,
    #[arg(long)]
    offline: bool,
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}
fn hash(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect()
}
fn error(message: impl Into<String>) -> std::io::Error {
    std::io::Error::other(message.into())
}
fn json_write(path: &Path, value: &Value) -> Result<(), std::io::Error> {
    let mut file = fs::File::create(path)?;
    serde_json::to_writer_pretty(&mut file, value)?;
    writeln!(file)
}
fn lines_write(path: &Path, values: &[Value]) -> Result<(), std::io::Error> {
    let mut file = fs::File::create(path)?;
    for value in values {
        serde_json::to_writer(&mut file, value)?;
        writeln!(file)?;
    }
    Ok(())
}

struct Intake {
    client: Client,
    cache: PathBuf,
    refresh: bool,
    offline: bool,
    last_request: Option<Instant>,
    receipts: Vec<Value>,
}
impl Intake {
    fn get(&mut self, url: &str) -> Result<Vec<u8>, String> {
        let key = hash(url.as_bytes());
        let body_path = self.cache.join(format!("{key}.body"));
        let receipt_path = self.cache.join(format!("{key}.json"));
        if !self.refresh && body_path.is_file() && receipt_path.is_file() {
            let cached = (|| -> Result<(Vec<u8>, Value), String> {
                let bytes = fs::read(&body_path).map_err(|e| e.to_string())?;
                let mut receipt: Value =
                    serde_json::from_slice(&fs::read(&receipt_path).map_err(|e| e.to_string())?)
                        .map_err(|e| e.to_string())?;
                if receipt["url"] != url
                    || receipt["sha256"] != hash(&bytes)
                    || receipt["bytes"].as_u64() != Some(bytes.len() as u64)
                {
                    return Err(format!(
                        "cache integrity/identity mismatch; observed SHA256={}, bytes={}; expected SHA256={}, bytes={}",
                        hash(&bytes),
                        bytes.len(),
                        receipt["sha256"],
                        receipt["bytes"]
                    ));
                }
                receipt["cache_reused"] = json!(true);
                Ok((bytes, receipt))
            })();
            return match cached {
                Ok((bytes, receipt)) => {
                    self.receipts.push(receipt);
                    Ok(bytes)
                }
                Err(message) => {
                    self.receipts.push(json!({"request_id":key,"url":url,"checked_at_unix_ms":now_ms(),"retrieved_at_unix_ms":Value::Null,"http_status":Value::Null,"cache_reused":false,"cache_status":"rejected","error":message}));
                    Err(format!("{message} for {url}"))
                }
            };
        }
        if self.offline {
            let message = format!("offline cache miss: {url}");
            self.receipts.push(json!({"request_id":key,"url":url,"checked_at_unix_ms":now_ms(),"retrieved_at_unix_ms":Value::Null,"http_status":Value::Null,"cache_reused":false,"cache_status":"missing","error":message}));
            return Err(message);
        }
        for attempt in 1..=3 {
            if let Some(last) = self.last_request {
                // All requests are sequential and spaced >=400ms, below NCBI's 3/s no-key limit.
                if let Some(wait) = Duration::from_millis(400).checked_sub(last.elapsed()) {
                    thread::sleep(wait);
                }
            }
            self.last_request = Some(Instant::now());
            let retrieved = now_ms();
            let result = self.client.get(url).send();
            match result {
                Ok(response) => {
                    let status = response.status().as_u16();
                    let final_url = response.url().to_string();
                    let mut bytes = Vec::new();
                    let read = response.take(MAX_RESPONSE + 1).read_to_end(&mut bytes);
                    let failure = read.err().map(|e|e.to_string()).or_else(||(bytes.len() as u64>MAX_RESPONSE).then(||"metadata response exceeds 32 MiB limit".into()));
                    let mut receipt = json!({"request_id":key,"url":url,"final_url":final_url,"retrieved_at_unix_ms":retrieved,
                        "http_status":status,"attempt":attempt,"bytes":bytes.len(),"sha256":hash(&bytes),"cache_reused":false,
                        "cache_object":Value::Null,"error":failure});
                    if status==200 && receipt["error"].is_null() {
                        receipt["cache_object"] = json!(format!("{key}.body"));
                        fs::write(&body_path,&bytes).map_err(|e|e.to_string())?;
                        json_write(&receipt_path,&receipt).map_err(|e|e.to_string())?;
                        self.receipts.push(receipt); return Ok(bytes);
                    }
                    receipt["error"] = json!(format!("HTTP {status}; {}", failure.unwrap_or_default()));
                    self.receipts.push(receipt);
                    if status!=429 && status<500 { return Err(format!("HTTP {status} or invalid metadata body from {url}")); }
                },
                Err(e) => self.receipts.push(json!({"request_id":key,"url":url,"retrieved_at_unix_ms":retrieved,"http_status":Value::Null,
                    "attempt":attempt,"error":e.to_string(),"cache_reused":false})),
            }
            if attempt < 3 {
                thread::sleep(Duration::from_secs(attempt));
            }
        }
        Err(format!("metadata request failed after 3 attempts: {url}"))
    }
    fn json(&mut self, url: &str) -> Result<Value, String> {
        serde_json::from_slice(&self.get(url)?).map_err(|e| format!("invalid API JSON: {e}"))
    }
    fn text(&mut self, url: &str) -> Result<String, String> {
        String::from_utf8(self.get(url)?).map_err(|e| e.to_string())
    }
    fn geo(&mut self, accession: &str) -> Result<CatalogueRows, String> {
        let mut search =
            reqwest::Url::parse(&format!("{EU}/esearch.fcgi")).map_err(|e| e.to_string())?;
        search.query_pairs_mut().extend_pairs([
            ("db", "gds"),
            ("term", &format!("{accession}[ACCN] AND gse[ETYP]")),
            ("retmode", "json"),
            ("retmax", "100"),
            ("tool", TOOL),
        ]);
        let ids = parse_search(&self.json(search.as_str())?)?;
        let summary_url = format!(
            "{EU}/esummary.fcgi?db=gds&retmode=json&id={}&tool={TOOL}",
            ids.join(",")
        );
        let summary = select_summary(&self.json(&summary_url)?, accession)?;
        let series = parse_soft(&self.text(&format!("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}&targ=self&form=text&view=quick"))?,"SERIES")?;
        let samples = parse_soft(&self.text(&format!("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}&targ=gsm&form=text&view=brief"))?,"SAMPLE")?;
        normalise_geo(accession, &summary, &series, &samples)
    }
    fn pride(&mut self, accession: &str) -> Result<CatalogueRows, String> {
        let base = format!("https://www.ebi.ac.uk/pride/ws/archive/v3/projects/{accession}");
        normalise_pride(
            accession,
            &self.json(&base)?,
            &self.json(&format!("{base}/files/all"))?,
        )
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let started = now_ms();
    let elapsed = Instant::now();
    let registry_bytes = fs::read(&args.registry)?;
    let registry: Value = serde_json::from_slice(&registry_bytes)?;
    let seeds = registry["datasets"]
        .as_array()
        .ok_or_else(|| error("registry.datasets must be an array"))?;
    let mut accessions = seeds
        .iter()
        .map(|d| {
            d["accession"]
                .as_str()
                .map(str::to_owned)
                .ok_or_else(|| error("missing accession"))
        })
        .collect::<Result<Vec<_>, _>>()?;
    accessions.extend(args.extra.clone());
    validate_accessions(&accessions).map_err(error)?;
    accessions.sort();
    fs::create_dir_all(&args.cache)?;
    fs::create_dir_all(&args.out)?;
    json_write(
        &args.out.join("summary.json"),
        &json!({"schema_version":1,"status":"running","started_at_unix_ms":started,"registry_sha256":hash(&registry_bytes),"requested_accession_count":accessions.len(),"catalogued_accession_count":0,"failed_accession_count":0}),
    )?;
    let mut intake = Intake {
        client: Client::builder()
            .user_agent("rare-omics-atlas/0.1 (https://github.com/edithatogo/rare-omics-atlas)")
            .timeout(Duration::from_secs(50))
            .connect_timeout(Duration::from_secs(10))
            .build()?,
        cache: args.cache,
        refresh: args.refresh,
        offline: args.offline,
        last_request: None,
        receipts: Vec::new(),
    };
    let (mut datasets, mut assays, mut files) = (Vec::new(), Vec::new(), Vec::new());
    let mut failures = 0;
    for accession in &accessions {
        eprintln!("cataloguing {accession}");
        let before = intake.receipts.len();
        let result = if accession.starts_with("GSE") {
            intake.geo(accession)
        } else {
            intake.pride(accession)
        };
        let mut row = match result {
            Ok((dataset, mut sample_rows, mut file_rows)) => {
                assays.append(&mut sample_rows);
                files.append(&mut file_rows);
                dataset
            }
            Err(message) => {
                failures += 1;
                eprintln!("{accession}: {message}");
                json!({"schema_version":1,"accession":accession,"status":"failed","error":message,"analysis_admitted":false})
            }
        };
        let requests: BTreeSet<_> = intake.receipts[before..]
            .iter()
            .filter_map(|r| r["request_id"].as_str())
            .collect();
        row["source_request_ids"] = json!(requests);
        row["seed_condition_label"] = seeds
            .iter()
            .find(|s| s["accession"] == *accession)
            .map(|s| s["condition"].clone())
            .unwrap_or(json!("additional paired-array technical reference"));
        datasets.push(row);
        // Checkpoints preserve successful records and failures after each accession.
        lines_write(&args.out.join("datasets.jsonl"), &datasets)?;
        lines_write(&args.out.join("assays.jsonl"), &assays)?;
        lines_write(&args.out.join("files.jsonl"), &files)?;
        lines_write(&args.out.join("requests.jsonl"), &intake.receipts)?;
    }
    let summary = json!({"schema_version":1,"status":if failures==0 {"complete"} else {"complete_with_failures"},"tool_version":env!("CARGO_PKG_VERSION"),"started_at_unix_ms":started,"completed_at_unix_ms":now_ms(),
        "elapsed_seconds":elapsed.elapsed().as_secs_f64(),"registry_sha256":hash(&registry_bytes),"extra_accessions":args.extra,
        "requested_accession_count":accessions.len(),"catalogued_accession_count":accessions.len()-failures,"failed_accession_count":failures,
        "series_assay_membership_rows":assays.len(),"distinct_assay_accessions":assays.iter().filter_map(|r|r["assay_accession"].as_str()).collect::<BTreeSet<_>>().len(),
        "file_metadata_rows":files.len(),"request_receipts":intake.receipts.len(),"independent_cohort_count":Value::Null,
        "limitations":["Seed inventory, not an exhaustive rare-disease survey","GEO assay identifiers are not independent participants","SuperSeries/subseries memberships can repeat assays","File URLs are source-declared listings, not fresh download checks","Scientific admission and sample phenotypes require separate curation","Raw API/SOFT cache is excluded from public catalogue; contacts and personal traits are not exported"]});
    json_write(&args.out.join("summary.json"), &summary)?;
    println!("{}", serde_json::to_string_pretty(&summary)?);
    if failures > 0 {
        std::process::exit(2);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn corrupted_offline_cache_fails_before_parsing() {
        let dir = std::env::temp_dir().join(format!(
            "atlas-cache-test-{}-{}",
            std::process::id(),
            now_ms()
        ));
        fs::create_dir_all(&dir).unwrap();
        let url = "https://example.org/metadata";
        let key = hash(url.as_bytes());
        fs::write(dir.join(format!("{key}.body")), b"tampered").unwrap();
        json_write(
            &dir.join(format!("{key}.json")),
            &json!({"url":url,"sha256":hash(b"original"),"bytes":8}),
        )
        .unwrap();
        let mut intake = Intake {
            client: Client::new(),
            cache: dir.clone(),
            refresh: false,
            offline: true,
            last_request: None,
            receipts: Vec::new(),
        };
        assert!(
            intake
                .get(url)
                .unwrap_err()
                .contains("cache integrity/identity mismatch")
        );
        assert_eq!(intake.receipts.len(), 1);
        assert_eq!(intake.receipts[0]["cache_status"], "rejected");
        fs::remove_dir_all(dir).unwrap();
    }
}
