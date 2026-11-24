use clap::Parser;
use rare_omics_catalogue::review_sample_json;
use serde_json::Value;
use std::{
    fs::File,
    io::Read,
    path::{Path, PathBuf},
    process::ExitCode,
};

#[derive(Parser)]
#[command(about = "Review a local declared sample manifest; never admits scientific analysis")]
struct Args {
    #[arg(long)]
    input: PathBuf,
}

fn review(input: &Path) -> Result<Value, Box<dyn std::error::Error>> {
    const LIMIT: u64 = 16 * 1024 * 1024;
    let mut bytes = Vec::new();
    File::open(input)?.take(LIMIT + 1).read_to_end(&mut bytes)?;
    if bytes.len() as u64 > LIMIT {
        return Err("sample manifest exceeds 16 MiB".into());
    }
    Ok(review_sample_json(&bytes).map_err(std::io::Error::other)?)
}

fn main() -> ExitCode {
    match review(&Args::parse().input) {
        Ok(report) => {
            println!("{}", serde_json::to_string_pretty(&report).unwrap());
            if report["summary"]["held"] == 0
                && report["summary"]["ready_for_review"].as_u64().unwrap() > 0
            {
                ExitCode::SUCCESS
            } else {
                ExitCode::from(2)
            }
        }
        Err(error) => {
            eprintln!("sample contract review failed: {error}");
            ExitCode::FAILURE
        }
    }
}
