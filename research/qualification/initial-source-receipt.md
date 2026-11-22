# Initial public-source qualification receipt

Checked 22 November 2026. All three raw archives were actually transferred over public HTTPS without a login, application, permission request or contact with an author. The total is **3,828,981,760 bytes (3.83 GB decimal; about 3.57 GiB)**, containing **341 complete red/green IDAT pairs**.

| Source | Archive bytes | Red/green pairs | Valid IDAT headers | Local SHA-256 |
|---|---:|---:|---:|---|
| GSE97362 | 2,181,539,840 | 235 | 470/470 | 521fb68f049c69d3911bc8b91f010e81cb76caa7092436a823632c11249da7c7 |
| GSE116300 | 565,248,000 | 44 | 88/88 | 82742b84a4e9b7f352afad1e54524673517e14031e972df7d0facfe59757f326 |
| GSE218186 | 1,082,193,920 | 62 | 124/124 | 9c6014691c6bc0838efaca1ea697533ac68c85a86f600c1d69cbe69fa5143ab0 |

All returned HTTP 200 and matched the observed Content-Length. TAR traversal completed, no unsafe member paths were found, and every inspected IDAT had the IDAT magic and version 3 header. No archive members were extracted to arbitrary paths. The [machine-readable receipt](initial-source-receipt.json) records exact URLs, timestamps, bytes, hashes, member/channel counts and check scope.

These checks read only the first 16 decompressed bytes of each IDAT. They do **not** establish full gzip CRC integrity, valid intensities, detection performance, sample/probe QC or biological correctness. The local SHA-256 identifies the bytes received; no publisher-provided expected checksum was compared.

## Metadata intake and candidate subsets

The official series SOFT and quick sample SOFT were also downloaded and hashed. Detailed source metadata remains outside Git; the receipt retains field coverage and selected aggregate categories. A quick SOFT view can include assay-value previews and must not be described as a complete analysed matrix or as containing only bibliographic metadata.

| Source | Observed metadata | Consequence for analysis |
|---|---|---|
| GSE97362 | 235 whole-blood assay records; disease labels include 11 Kabuki, 19 CHARGE, 53 CHD7-variant, 26 KMT2D-variant, 1 KDM6A-variant and 125 controls. Sample-type fields identify 11 KMT2D-LOF discovery records and 11 native KMT2D-discovery controls | Candidate first contrast is the declared LOF discovery group versus its native controls, pending full manifest/covariate/independence review. Do not classify every variant record as affected |
| GSE116300 | 44 assay records: 29 cases, 9 controls and 6 case parents; phenotype field has 29 KS, 9 normal and 6 unknown. Mutation and sex fields exist, and a subset has variant-classification fields | Clinical KS labels alone do not define the molecularly confirmed KMT2D subset. Parents are not automatically eligible unrelated controls |
| GSE218186 | 62 whole-blood assay records: 7 Kabuki and 55 controls | Candidate EPIC replication cohort; public GEO characteristics do not by themselves resolve all age/sex/covariate and participant-overlap questions |

Assay counts and source clinical labels are not confirmed independent-patient counts. No attempt was made to reidentify individuals. Use declared overlap/participant evidence and permitted study records for later train/test independence decisions.

## Status and next steps

**Passed:** public transfer, local content identity, archive traversal, channel-pair inventory and bounded IDAT header checks for these three exact archives.

**Pending:** scientific QC, molecular subset, valid native controls, sample independence/covariates, reference annotations, selected-method acceptance and the applicable institutional classification before disease inference. The current checks do not produce a Silver matrix or a clinical result.

See [dataset rights](../dataset-rights.md) for research-use/distribution evidence and separate HF eligibility. Raw source files, detailed participant metadata and previews are not committed. No Hugging Face upload was performed. The 28-accession rights register is broader than this three-archive download receipt.
