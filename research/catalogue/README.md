# Official-source metadata catalogue

The [22 November 2026 snapshot](2026-11-22/summary.json) catalogues **29 accession records** from the current rights register: 28 GEO series and one PRIDE project. This seed set includes rare-disease material, companion modalities and technical references. It is not an exhaustive count of rare-disease datasets or independent cohorts.

The runnable [Rust intake CLI](../../tools/catalogue/README.md) uses official EUtils, documented GEO SOFT requests and PRIDE v3 APIs. All 29 source identities were checked, and all 114 successful response objects were independently verified by URL, size and SHA-256 during review. Raw API responses remain in ignored/local Bronze storage; these checked-in JSONL tables contain the approved metadata subset.

| Observed unit | Count | Interpretation |
|---|---:|---|
| Accession records | 29 | 28 GEO series plus PXD003403 |
| Series–GSM memberships | 2,532 | Same assay can occur in a SuperSeries and subseries |
| Distinct GSM accessions | 2,465 | Assay records; not unique donors |
| Repeated series memberships | 67 | 30 in the GSE86833 family and 37 in GSE92580 |
| Source file metadata rows | 4,514 | Declared source URLs; includes repeats through series membership |
| Successful API/SOFT responses | 114 | 4 per GEO series, 2 for PRIDE |
| Independent participants/cohorts | Unknown | Requires study-specific curation and family/specimen linkage |

GSE154566 contributes 1,177 assay records to this catalogue. The separately reviewed 233 paired age-18 specimens are a subset/design fact, not the catalogue's assay count. The full source series also contains other ages/platforms. PRIDE reports seven files, an `EBI terms of use` licence label and no assay count used by this catalogue.

## Snapshot files

- [Dataset metadata](2026-11-22/datasets.jsonl): source titles, organism, platforms, assay types, dates, PubMed/BioProject/series relations and source counts.
- [Assay metadata](2026-11-22/assays.jsonl): source series–GSM memberships, platform, organism, molecule, tissue/cell annotations and accession links. Contact details, personal traits, diagnoses and variant values are not exported.
- [File metadata](2026-11-22/files.jsonl): source-declared supplementary URLs and available PRIDE file sizes/checksums/categories.
- [Request receipts](2026-11-22/requests.jsonl): source URL, retrieval timestamp, outcome, bytes, SHA-256 and cache object reference.
- [Execution summary](2026-11-22/summary.json) and [qualification receipt](../qualification/api-catalogue-2026-11-22.md).

Source-declared file URLs are **not new download receipts**. The existing three-archive download evidence remains in [initial-source-receipt.json](../qualification/initial-source-receipt.json). This catalogue does not relabel every listed file as transferred, clinically admitted, paired or eligible for redistribution.

The CLI does not decide a file's rights from repository availability. Keep [dataset rights](../registries/dataset-rights.json), metadata source identity and analysis admission as separate facts. Hugging Face publication uses the allowlisted catalogue outputs through the repository's publication adapter. It does not upload the raw response cache automatically.
