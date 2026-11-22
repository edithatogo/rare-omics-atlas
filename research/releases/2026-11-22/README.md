---
pretty_name: Rare Omics Atlas
license: other
license_name: Source-specific rights with retained attribution
license_link: LICENSES.md
tags:
- methylation
- rare-disease
- genomics
- metadata
- provenance
- medical
language:
- en
viewer: false
---

# Rare Omics Atlas

A source-bound research catalogue and a minimal Bronze/Silver/Gold store for rare-disease epigenomics. Code, source selection and Conductor work are maintained in [GitHub](https://github.com/edithatogo/rare-omics-atlas). Exact release inputs and the source Git commit are recorded under `releases/2026-11-22/`. This dataset is registered in the account's [dataset estate registry](https://huggingface.co/datasets/edithatogo/dataset-estate-registry).

## Included in this release

- **Bronze:** byte-identical GEO raw archives for GSE97362, GSE116300 and GSE218186; total 3,828,981,760 bytes. They contain 341 red/green IDAT pairs, including cases, controls and other diagnoses, plus source-supplied platform annotations. These are not 341 independent affected participants.
- **Silver metadata:** a catalogue of 29 accessions resolved using official NCBI E-utilities/GEO SOFT and PRIDE REST. It contains 2,532 series–GSM memberships, 2,465 unique GEO assay accessions and 4,514 source-declared file records. SuperSeries/subseries can repeat assays. No independent cohort total is asserted.
- **Gold:** no scientific result yet. No differential-methylation matrix, clinical classifier or perturbation recommendation is included.

The remaining catalogue file URLs point to upstream material; their presence is not proof that the files are mirrored here. `download_verified=false` in source catalogue records denotes that the catalogue client did not transfer those files; separate Bronze release and intake receipts record the three archives actually checked and mirrored.

## Reuse and interpretation

See [LICENSES.md](LICENSES.md) and `metadata/dataset-rights.json`. GEO supports public-data use and distribution while retaining any source-owner claims; mirroring does not relicense original data or source-supplied vendor annotations. Article licences are not automatically applied to separate GEO files. Preserve original author/source attribution and cite the source studies as well as this pinned Hub revision.

These already public source objects were retrieved without login or an application. This release makes no institutional HREC/IRB determination about a later research project. Clinical analysis still needs the specified cohort, independence, method and institutional-admission checks. Disease-level annotations are not patient observations. Do not attempt to identify study participants.

The catalogue exports accession, assay, platform, organism and selected tissue/cell metadata. Original API responses containing contacts/free-text clinical characteristics are not republished. Controlled companion EGA data are excluded.

## Reproducible download

Use the official Hugging Face Hub client and pin the commit reported by the release receipt:

```python
from huggingface_hub import hf_hub_download
path = hf_hub_download(
    repo_id="edithatogo/rare-omics-atlas",
    repo_type="dataset",
    filename="bronze/geo/GSE218186/GSE218186_RAW.tar",
    revision="PIN_THE_RELEASE_COMMIT",
)
```

Verify the file against the SHA-256 and byte count in the release manifest. Original IDATs remain in their native format; future table outputs can use Arrow/Parquet without forcing dense probe-by-sample matrices into long-form rows.
