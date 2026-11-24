# API catalogue qualification — 22 November 2026

**Implemented, reviewed and qualified in the observed cloud environment.** The catalogue covers all 29 currently registered source accessions: 28 GEO series and PXD003403. It is ready for the metadata publication adapter. This receipt does not certify a scientific cohort, an owner-device runner or a new raw-data transfer.

## What ran

The [Rust CLI](../../tools/catalogue/README.md) queried official NCBI EUtils GDS ESearch/ESummary, documented GEO SOFT series/sample endpoints, and PRIDE Archive v3 project/file APIs. Exact source identities and complete sample inventories were checked. Every accession succeeded; none was silently omitted.

The live harvest took **168.224 seconds of observed execution**. The final implementation replayed the 114 cached source responses, validating URL, bytes and SHA-256, against the canonical 29-record rights register in **3.009 seconds**. These are execution receipts, not throughput or device-performance benchmarks. Source metadata retrieval timestamps remain those of the live HTTP requests; cache replay does not relabel them as newly fetched.

| Output | Observed result |
|---|---:|
| Dataset records | 29/29 successful |
| Series–GSM memberships | 2,532 |
| Unique GSM accessions | 2,465 |
| Repeated memberships | 67 |
| Source file metadata rows | 4,514 |
| API/SOFT response objects | 114, all HTTP 200 and independently hash checked |
| Public catalogue bytes | 2,191,092 across the five snapshot files |

The repeated memberships are fully explained by the technical series: 15 each from GSE86829 and GSE86831 repeated in GSE86833, and 12 from GSE92577 plus 25 from GSE92579 repeated in GSE92580. They are retained as source memberships, not counted as additional participants. GSE154566 has 1,177 deposited assays, which must not be confused with its 233 paired age-18 specimens. PRIDE reports seven file records; its current API licence label is **EBI terms of use**, not a new CC0 finding.

## Verification

The final source passed `cargo +1.95.0 fmt -- --check`, **11 contract tests**, `clippy --all-targets -- -D warnings`, and the locked dependency-tree check. Tests exercise wrong or duplicate accession IDs, API errors/truncation, HTML masquerading as SOFT, duplicate/mismatched assay inventories, disagreeing source counts, safe handling of truncated ESummary listings, incorrect PRIDE file membership, the metadata disclosure allowlist, and corrupted cached bytes. Full commands and observed exit codes are in [the machine-readable receipt](api-catalogue-2026-11-22.json) and [captured check output](api-catalogue-2026-11-22.checks.log).

The initial negative contract run failed before implementation existed. Development also caught a SHA-2 0.11 formatting API difference and a Clippy conditional-style warning; both were corrected before final checks. No failed source accession is hidden in the final snapshot.

An independent Ponytail review checked all 114 raw source-response hashes/sizes/URL-derived IDs, every dataset's request links, source sample counts, platform/organism coverage, common array field types, SuperSeries duplication and the public export's exclusions. Review led to explicit cache-failure receipts, a `running` status that prevents reuse of a stale completion summary, and documentation that a valid cache has **no implicit expiry**. Use `--refresh` for a new retrieval date. The reviewer reported no remaining implementation finding within this scope.

## Dependency decision

Only four direct runtime dependencies were added: Reqwest 0.13.5, Serde JSON 1.0.154, SHA-2 0.11.1 and Clap 4.6.9. Each declares `MIT OR Apache-2.0`. HTTP/TLS, URL encoding, JSON, hashing and CLI parsing are delegated to those libraries. The application contains a bounded SOFT metadata adapter, not a general GEO parser or numerical method. A dataframe, graph engine, database, service-backed lakehouse or custom downloader is not needed at this boundary.

The lockfile resolves 180 registry packages across target/platform selections. `cargo tree -d` found no duplicate versions in the active target graph. An OSV batch query returned 180 results and no vulnerability findings for those exact locked versions; this is a dated advisory query, not proof of absence of vulnerabilities. Exact response details, direct dependency licences and source hashes are in the JSON receipt.

The source-manifest SHA-256 is `0e373583b83febca88df0942c53439b50a79bbbada3242321bf574795116db40`. The canonical registry hash used by the final replay is `d07604c04b5f027c1be78642b13cf15c444166828410815972a0b6e7226d0aff`.

## Scope retained

The [public tables](../catalogue/README.md) contain source metadata and accession links. They do not export contacts, patient titles, age/sex, diagnoses or variant values. Raw API responses are a local/ignored Bronze cache and are not automatically included in a Hugging Face release. The existing three-archive receipt remains the authority for actual array downloads; a listed supplementary URL is not a new transfer.

Independent donor counts, relatedness, clinical cohort eligibility, disease effects and platform harmonisation remain separate analytical tasks. The catalogue does not assert that every source is a rare-disease methylation cohort. No owner-device official GitHub runner was executed in this environment. There is no new scientific manuscript claim; this completed capability supports the planned bundled clinical analyses.
