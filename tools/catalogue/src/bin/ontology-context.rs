use clap::Parser;
use rare_omics_catalogue::{ontology_context, ontology_context_with_hgnc};
use serde_json::Value;
use std::{
    fs::File,
    io::Read,
    path::{Path, PathBuf},
    process::ExitCode,
};

#[derive(Parser)]
#[command(
    about = "Join curated ontology references to public catalogue metadata; never admits scientific analysis"
)]
struct Args {
    #[arg(long)]
    assays: PathBuf,
    #[arg(long)]
    diseases: PathBuf,
    #[arg(long)]
    mappings: PathBuf,
    /// Bind disease-reference genes to selected approved HGNC source records.
    #[arg(long)]
    hgnc: Option<PathBuf>,
}

fn read(path: &Path) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    const LIMIT: u64 = 16 * 1024 * 1024;
    let mut bytes = Vec::new();
    File::open(path)?.take(LIMIT + 1).read_to_end(&mut bytes)?;
    if bytes.len() as u64 > LIMIT {
        return Err("ontology context input exceeds 16 MiB".into());
    }
    Ok(bytes)
}

fn review(args: Args) -> Result<Value, Box<dyn std::error::Error>> {
    let assays = read(&args.assays)?;
    let diseases = read(&args.diseases)?;
    let mappings = read(&args.mappings)?;
    Ok(match args.hgnc {
        Some(path) => ontology_context_with_hgnc(&assays, &diseases, &mappings, &read(&path)?),
        None => ontology_context(&assays, &diseases, &mappings),
    }
    .map_err(std::io::Error::other)?)
}

fn main() -> ExitCode {
    match review(Args::parse()) {
        Ok(report) => {
            println!("{}", serde_json::to_string_pretty(&report).unwrap());
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("ontology context failed: {error}");
            ExitCode::FAILURE
        }
    }
}
