# Minimal cross-language interoperability contract

**Ponytail decision: approve** file-based Arrow/Parquet interchange for tabular metadata, provenance and results. Follow **Rust > Julia or Mojo > Python > R** among suitable implementations; no language permanently owns a scientific stage. Julia/Bioconductor can remain reference or fallback methods while an existing Rust candidate is qualified. See [selection policy](language-dependency-triage.md).

1. When an admitted source is downloaded, preserve original GEO data files without conversion in local Bronze, with SHA256 and licence/access state. Public Bronze can contain source links/checksum manifests; it does not require mirroring participant files. Apply the separate [hosting and redistribution decision](resources-hosting-reuse.md) before any Hugging Face release.
2. Store sample, assay, ontology and feature annotations as typed Parquet. Use the chosen Polars/DataFusion/DuckDB route for local joins; do not maintain duplicate engines for the same stage. Record exact `study_id`, `sample_id`, `feature_id` and reference genome.
3. Keep methylation beta/M matrices as labelled dense or chunked matrices when appropriate; do not melt all CpGs to a gigantic long table simply to use Parquet.
4. Emit analytical effects and uncertainty as small stable Parquet outputs, with units and finite/missing semantics documented. Distinguish beta differences, M-value contrasts, ordinary coefficient SEs, moderated SEs and unscaled design factors. A field called `lfcSE` is not sufficient evidence of its meaning; see the [source audit](methylation-backend-audit.md).
5. Before using new language backends, **later** run one cross-language synthetic round trip, asserting same identifiers, order mapping, nulls, types, numbers and hashes. A file's read success alone is not numerical equivalence.
6. Prefer file-based process boundaries. Defer custom `extendr`/`jlrs`/`PyO3` bindings, in-process embedding and service APIs until profiling or failure isolation justify them.

**Practical metadata contract (proposal, not implemented):** study/accession, participant identity confidence, sample/assay IDs, tissue, batch, disease OMIM/MONDO ID, HPO evidence source, raw rights, provenance pointer, array version, reference genome, feature ID, M-value vs beta-value flag, adjusted effect estimates, uncertainty, originating model version.

**Lakehouse decision:** local Bronze / Silver / Gold logical folders and typed outputs are enough. No Delta, Iceberg, Fabric, Spark, Databricks, catalog service or streaming until actual collaboration, scale or lineage demands them.

**Precision decision:** qualify the actual production export and import path, not only an internal float64 test helper. SeSAMe2's compact beta and text exports have different precision from its R-comparison helper. Beta values near 0/1 can magnify rounding on conversion to M values; record clipping/offset rules and test effects, SEs and inferential tails after the full round trip. Arrow preserves a declared number type; it cannot restore information already rounded upstream.

## Replaceable backend decision

See [language-agnostic scientific backend qualification](backend-replacement-policy.md). Portability requires a **scientific contract** (estimand, controls, QC, numeric semantics, FDR, provenance), not a generic runtime plugin interface. The default orchestration is a small number of isolated command-line stages writing typed artifacts. Replacement from R or Julia by Rust is permitted only after exact-input numerical comparison, public cohort and simulation-based statistical qualification, and acceptable measured resource/deployment/maintenance costs. A speed advantage is not the only valid reason to select Rust. No such benchmark has yet been run.

