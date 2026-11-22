# T08 independent Ponytail review — 22 November 2026

**Decision: accept the bounded metadata capability for T08 completion and archival. No material finding remains open in the reviewed source and final catalogue snapshot.** The dependent metadata-publication track can begin after T08 is archived. This review does not admit a scientific disease analysis, verify raw-data transfers, authorize patient-data redistribution or satisfy the owner's official local-device runner milestone.

## What was reviewed

The reviewer read the T08 specification, Cargo manifest and lockfile, both Rust source files, contract tests, CLI documentation, the actual final JSONL/summary outputs and the recorded implementation checks. The final replay uses the current 29-entry rights register, with **no extra accessions**, and its registry hash matches that input.

The implementation uses the existing HTTP/TLS, JSON, SHA-256 and CLI libraries for their appropriate tasks. Its small SOFT parser reads the required metadata sections. An additional dataframe engine, generic connector framework or new retry dependency is unnecessary for this bounded operation.

## Findings resolved before acceptance

1. **Cache failures previously lost provenance.** A corrupt cache or malformed receipt could return an error before adding a request record, leaving an accession with no source-request reference. The revised code emits an explicit rejected/missing-cache receipt, including the URL, check time and failure details; integrity mismatches retain observed/expected digest and byte-count information. The implementation agent extended the cache contract test to require a failure receipt.
2. **An interrupted rerun could retain an old complete summary.** The revised code writes a `running` summary before harvesting, then writes `complete` or `complete_with_failures` only at the end. This prevents an earlier complete summary from certifying partially rewritten outputs.

The reviewer questioned whether GEO SOFT supplied `Series_platform_organism`; direct inspection of the cached responses confirmed that all 28 series responses include that field. The current normalization is therefore supported by the actual source bytes, and no speculative fallback was requested.

## Independently executed metadata checks

These were read-only consistency checks executed by the reviewer, separate from the implementation agent's Rust tests:

| Check | Observed result |
|---|---|
| Registry and final status | Exact 29-accession set; current registry SHA-256 matches final summary; status `complete`; zero failed accessions |
| Source inventory | 28 GEO accessions and 1 PRIDE project; this is a seed inventory that includes technical references and other omics, not 29 distinct rare diseases or 29 independent methylation cohorts |
| GEO membership counts | Every source-reported assay count matches the normalized series membership rows |
| Membership versus unique assays | 2,532 series–assay membership rows; 2,465 distinct GSM accessions |
| Expected repeated memberships | All 67 repeats arise from the technical SuperSeries/subseries: 15 + 15 in GSE86833, 12 + 25 in GSE92580 |
| Platform consistency | No contradictory platform mappings for a GSM appearing in multiple series; no empty platform field in the observed assay records |
| Large technical cohort | GSE154566 has 1,177 assay records: 233 GPL13534 and 944 GPL23976; this does not establish paired participants |
| File inventory | 4,514 source-declared file records, including 7 PRIDE records; all retain `download_verified=false` |
| Request provenance | All dataset request references resolve to the 114 retained request receipts |
| Cache integrity | Independently recomputed SHA-256, byte counts and URL-derived request IDs for all 114 raw cached response objects; no mismatch |
| Observed request pacing | Minimum original request-start spacing was 400 ms; all observed requests returned HTTP 200 |
| Replay provenance | Final request records indicate cache reuse while retaining original retrieval timestamps |
| Public schema | Organisms, assay types and PubMed IDs are string arrays across GEO/PRIDE; contact/age/sex/phenotype free-text fields are not selected into the public schema |
| Inference boundaries | Every dataset remains `analysis_admitted=false`; independent participant counts remain null; source relations and SuperSeries duplication are retained |

Raw response objects were inspected at the separate local cache path, outside the Git repository. They are not the public upload selection.

## Execution evidence observed, not rerun by this reviewer

The implementation agent's committed-format [checks log](api-catalogue-2026-11-22.checks.log) records:

- Rust 1.95.0 locked test run: **11 passed, 0 failed** (one binary cache test and ten contract tests).
- Formatting check passed.
- Clippy with `--all-targets -- -D warnings` passed.
- The duplicate-dependency inspection reported no entries for the current target.

The reviewer read that log and the tested source, but did **not** independently rerun Cargo or claim a second Rust execution. The live harvest and final offline replay are distinct receipts in the catalogue's qualification record. Cloud execution establishes this increment's metadata behavior only.

## Remaining limits, preserved rather than waived

The CLI's requests are sequential with bounded retries. It does not currently inspect a server `Retry-After` header; no 429 response was encountered in the observed run. This is not a blocker for the completed, rate-spaced intake. Revisit the existing bounded delay only if a real service response requires it.

An integrity-valid cache is a reproducible snapshot, not a freshness guarantee. A new source retrieval requires `--refresh`; offline replay must retain the original retrieval dates. This distinction must remain clear when the catalogue is refreshed before an analysis.

GEO/PRIDE file URLs are metadata assertions. This track has not downloaded full matrices/IDAT archives, verified listed payload accessibility or resolved every dataset's reuse/distribution terms. The HF publisher must select only the reviewed public metadata and separately admitted products. Scientific admission, participant-level curation and actual official GitHub Actions runner evidence on the owner's devices remain separate open milestones.

## Snapshot identity

| Reviewed item | SHA-256 |
|---|---|
| Current rights register | `d07604c04b5f027c1be78642b13cf15c444166828410815972a0b6e7226d0aff` |
| Final catalogue summary | `7d7f9c68fb3c70d7d9ab2be592fd6d7cd00d9dda61cb1f68f8b3fdbb7bb9e222` |
| `tools/catalogue/src/lib.rs` | `855b8c227e318d8437def6ba88b9c0a7a1816b7bd874ef7d0da6eaba1cb4f08b` |
| `tools/catalogue/src/main.rs` | `72b6cc13f0de0f2a1e2bc6ccb7f191c116e2e36ce2622f28eec2120d3412c19d` |
| `tools/catalogue/tests/contracts.rs` | `c7c5c32517883cb468188550be520c7d5bd8409f777bcd4adc10bf52166d2084` |
| `tools/catalogue/Cargo.lock` | `5a557f33934ebcb4ec2730f7f4d195ccd91d40bbad18945277cb91d5307272cb` |

**Sequencing decision:** archive the completed T08 metadata increment, then implement/review the minimal GitHub-to-HF metadata publication increment. Do not relabel remaining T01 scientific admission or target-device gates as completed merely because the catalogue now exists.

