# T01b — bounded cohort-source curation

Reconcile the three original public GEO sample sources to the existing
341-assay catalogue. Preserve original roles, molecular source categories,
variant/sample crosswalk limits, array links, native controls, available
covariates and explicit historical study reuse. Write a source-bound KMT2D
review inventory with unknown participant/specimen/partition/independence fields.

Reuse the existing Rust sample-contract CLI. Do not infer participants from
array keys, new molecular eligibility from methylation predictions, or new
discovery/replication roles from historical paper labels. Preserve every public
assay in the catalogue, including review-scope exclusions.

Acceptance requires exact source hashes and assay sets, a reproducible local
manifest, an actual validator result, cleared aggregate evidence, independent
review and the combined strict candidate checks. Failed source retrievals and
all remaining admission conditions must stay visible. Full T01 remains open.
