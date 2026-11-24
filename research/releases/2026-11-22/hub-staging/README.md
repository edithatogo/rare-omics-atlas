---
pretty_name: Rare Omics Atlas — public-source catalogue
license: other
license_name: rare-omics-source-specific
license_link: https://huggingface.co/datasets/edithatogo/rare-omics-atlas/blob/main/LICENSES.md
tags:
- methylation
- rare-disease
- genomics
- metadata
- provenance
language:
- en
viewer: false
---

# Rare Omics Atlas

## Publication status: metadata available; raw archive transfer pending

This public dataset provides a **29-accession catalogue assembled through official APIs**, source and rights receipts, and minimal Bronze/Silver/Gold layer notices. The five catalogue files are under `silver/catalogue/2026-11-22/`: `datasets.jsonl`, `assays.jsonl`, `files.jsonl`, `requests.jsonl` and `summary.json`.

**The three raw methylation archives are not stored on this Hugging Face dataset.** Earlier execution downloaded and verified 3,828,981,760 bytes (3.83 GB) in local working storage. Those original files remain available from GEO at the links below. Publication of their bytes to this Hub repository remains unfinished.

| Layer | Current contents |
|---|---|
| Bronze | Source links and local download/integrity receipts; no raw archive bytes on the Hub |
| Silver metadata | Five API catalogue files, plus source and rights metadata |
| Scientific Silver | No processed biological beta/M matrix |
| Gold | No scientific analysis results, classifier or perturbation recommendations |

The catalogue includes **28 GEO series and one PRIDE project**, spanning rare-disease material, companion modalities and technical references. It is a seed inventory, not a count of all rare-disease methylation datasets. It records 2,532 series–GSM memberships, 2,465 unique GEO assay accessions and 4,514 source-declared file records. SuperSeries/subseries can repeat assays; neither count establishes independent participants or cohorts.

## Source archives

These are upstream downloads, not Hub download paths:

| Source | Original GEO archive | Locally verified bytes |
|---|---|---:|
| [GSE97362](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362) | [GEO RAW archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE97nnn/GSE97362/suppl/GSE97362_RAW.tar) | 2,181,539,840 |
| [GSE116300](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300) | [GEO RAW archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE116nnn/GSE116300/suppl/GSE116300_RAW.tar) | 565,248,000 |
| [GSE218186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186) | [GEO RAW archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE218nnn/GSE218186/suppl/GSE218186_RAW.tar) | 1,082,193,920 |

Those archives contain 341 red/green IDAT pairs, including controls and other diagnoses, plus source-supplied annotations. They do not represent 341 independent affected participants. `metadata/initial-source-receipt.json` and `metadata/full-gzip-check.json` describe local checks; their presence here does not mean the raw archives were uploaded. Likewise, catalogue file URLs and `download_verified=false` fields describe the metadata client's scope rather than a Hub mirror.

## GitHub source and publication route

Code, the dataset register and Conductor tracks are maintained in [GitHub](https://github.com/edithatogo/rare-omics-atlas). The catalogue, original receipts and unchanged layer notices are bound to [source commit 8cfc851](https://github.com/edithatogo/rare-omics-atlas/commit/8cfc85110911a2991301b358e4510e28026d13b8).

This metadata subset uses the **Hugging Face browser editor**. Exact byte verification against the named GitHub sources and the three revised staging notices is recorded separately. The new dataset card, Bronze notice and licence notice do not claim to originate from commit 8cfc851. An automated publication workflow is configured in GitHub; it has not transferred this release to the Hub, and no owner-device runner execution is claimed. The full archival publication track remains open while the raw transfer is pending.

## Reuse and interpretation

See [LICENSES.md](LICENSES.md) and `metadata/dataset-rights.json`. Source-specific rights and attribution remain in force. The catalogue exports accession, assay, platform, organism and selected tissue/cell metadata; original API response bodies containing contacts and unrestricted clinical text are not included. Controlled companion EGA data and PRIDE proteomics files are not mirrored.

These metadata and source links do not establish cohort eligibility, a clinical-use claim or an institutional HREC/IRB determination for a later study. Disease-level annotations are not patient observations.

## Retrieve the metadata

Use the official Hub client, pin the actual Hub commit, and verify against the staging publication receipt:

```python
from huggingface_hub import hf_hub_download
path = hf_hub_download(
    repo_id="edithatogo/rare-omics-atlas",
    repo_type="dataset",
    filename="silver/catalogue/2026-11-22/datasets.jsonl",
    revision="PIN_THE_ACTUAL_METADATA_COMMIT",
)
```
