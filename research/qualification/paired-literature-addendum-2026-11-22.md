# Paired-array literature addendum — 22 November 2026

**Completed:** the known paired-array findings have been reconciled with the central literature ledger. It now contains **13 studies, 17 verified study–dataset edges and two unresolved relationships**. This is an exact-seed literature update, not a scientific analysis or an exhaustive novelty review.

## Changes

| Record | Update and evidence boundary |
|---|---|
| Kandaswamy, PMID 33371772 | Added citation metadata and the explicit GSE154566 study-deposition edge, confirmed in the published article's Methods |
| Sugden, PMID 32885222 | Added citation metadata and a `benchmark-used` edge to GSE105018, explicitly identified as the 450K data layer; complete public access to its matched EPIC raw files is not inferred |
| Cheung, PMID 31833794 | Reconfirmed the existing GSE86833/GSE92580 reuse edges from primary text; neither was duplicated or replaced |
| E-Risk overlap | Added a separate unresolved relationship between the two E-Risk reports/dataset subsets. Shared cohort, tissue and age motivate specimen/person/family reconciliation; they do not establish the overlap count or an independent holdout |

All previous study and edge records were preserved. The original dated discovery/search receipts were not rewritten. The current JSON and TSV contain the same 17 verified edges; the unresolved relationships are deliberately kept outside that verified-edge TSV.

The paired subset of GSE154566 was already qualified separately in [the earlier paired-calibration receipt](paired-calibration-review-2026-11-22.md). This addendum does not repeat its biological-data intake or expand its rights assessment. The two E-Risk sample counts must not be added into an independent calibration total. Cheung's existing multi-cohort comparison and Sugden's reliability work remain prior art when selecting the narrower clinical transfer question.

## APIs actually used

The [machine-readable API receipts](../literature/2026-11-22-paired-addendum-api-receipts.json) retain exact request URLs, timestamps, response status, byte counts, SHA-256, returned metadata and failure details.

| Interface | Observed result |
|---|---|
| NCBI PubMed EFetch | Exact three-PMID request; HTTP 200; all three identities returned |
| OpenAlex Works | Exact three-DOI filter; HTTP 200; count 3 and three results on one page |
| Europe PMC search | Exact three-PMID query; HTTP 200; hit count 3 and three results on one page |
| Europe PMC fullTextXML | Three attempts: two HTTP 500 responses and one timeout, all retained |
| Legacy PMC `oa.fcgi` | HTTP 404; [official documentation](https://pmc.ncbi.nlm.nih.gov/tools/oa-service/) confirms retirement on 25 August 2026 |
| Current PMC Article Datasets AWS API | Eleven successful HTTP requests: three version listings, four metadata objects and four XML objects |

There were **18 direct API requests: 14 HTTP 200 responses and four failed attempts**. The interval from the first request to the final request's completion was **253.249018 seconds**, including intervening inspection and fallback selection. Individual request durations are retained; this elapsed span is not a throughput benchmark or a human-time estimate.

The replacement retrieval followed [PMC's current documentation](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/) and [official bucket README](https://pmc-oa-opendata.s3.amazonaws.com/README.txt), using anonymous ListObjectsV2 followed by the returned article metadata/XML locations. The legacy service's 404 was not treated as evidence of closed access. No API key, application or paid service was needed for these public requests.

## Source checks

The PMID/DOI identities agree across PubMed, OpenAlex, Europe PMC and the retrieved PMC metadata. Electronic and issue dates remain separate. Published article versions were selected using the metadata's `is_manuscript=false`: PMC8813077.1, PMC7467214.2 and PMC7574380.1. The additionally retrieved PMC7467214.1 is an author manuscript, not a fourth study.

All four XML downloads matched their metadata-supplied MD5, and each has an independently computed SHA-256 in the receipt. The selected XML article IDs match their metadata. Accession context was read in the actual Methods/Data Availability passages; it was not inferred from citation counts or a reference-list mention.

The [qualification JSON](paired-literature-addendum-2026-11-22.json) records the output hashes, identity checks, before/after counts, execution batches and limits. JSON parsing, JSON/TSV equivalence, unique study/edge keys and study-reference resolution passed. The one-off local check's initial syntax correction is disclosed there; it produced no source-file change or hidden retrieval result.

## Ponytail and retained limits

This extends the existing ledger and receipt formats. Standard public APIs and standard-library JSON/XML/CSV processing were sufficient; no crawler framework, database or new dependency was introduced. Only citation metadata, factual relationships and retrieval receipts are committed. Full articles, abstracts, raw API bodies and participant records remain outside Git.

No dataset-rights register, catalogue export, release manifest or frozen publication input was edited by this lane. No commit, push or Hub upload was performed. Independent E-Risk specimen linkage remains unresolved; no disease effect was estimated, no complete citation census was conducted and no N1 scientific protocol was frozen. Refresh the relevant literature again at the prescribed analysis/submission gates.
