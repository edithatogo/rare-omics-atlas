# T08 — API-backed accession catalogue

## Scope

Create and run a small Rust CLI that resolves the existing 28-accession source register plus GSE154566 through official NCBI E-utilities/GEO machine-readable metadata and PRIDE REST as applicable. Emit explicit dataset, assay and downloadable-file records, separate from actual transfer, independent people and scientific admission. No full matrices or raw archives are downloaded by this catalogue step.

## Acceptance

- Exact accession match; every requested source has a result or explicit error, with API URL, retrieval date and response hash.
- API-reported counts, series/subseries relations, assay/platform mappings and supplementary file URLs remain source assertions. Missing counts/identity remain unknown.
- Contact and unrestricted phenotype free text stay out of the public export; cache originals outside Git.
- Failures, malformed identity, duplicates and stale/corrupt cached bytes have defined behaviour.
- Locked build, targeted contract tests and one actual complete source-catalogue run are recorded. Independent Ponytail review resolves material findings.
- This track completes the cloud-verified metadata capability, not scientific inference, raw transfer or acceptance on the owner's local runner. Those milestones remain open explicitly.

## Execution budget

One implementation batch, one live API qualification batch, then review/correction as needed. Record observed command durations; no unmeasured elapsed promise.
