# Planned technology and data contracts

Status: source-reviewed candidates; the owner fork's existing corpus was replayed in an isolated workspace, but no scientific backend is accepted for the atlas. **Preference: Rust > Julia > Python > R**, after scientific suitability. See [selection policy](../research/language-dependency-triage.md) and [candidate audit](../research/rust-candidate-audit.md).

| Function | Preferred candidate to assess | Reference / fallback and gate |
|---|---|---|
| Typed metadata / results | Rust Polars, Arrow/Parquet | DataFusion CLI if SQL suffices; retain a simpler existing DuckDB query. One engine per stage |
| HPO / ontology / intervals | `hpo`, `ontolius`, `bedrs`/`gia`, each only when needed | Semsimian only for a real weighted/negated phenotype need; its Python-free build is unverified. Preserve full HPOA evidence; qualify MONDO and coordinates |
| Raw Illumina array QC | No complete Rust replacement qualified | R minfi/SeSAMe reference; SeSAMe2 C CLI candidate with licence, mask and platform conformance gates |
| Differential CpG models | Owner MassDynamics-derived `limma-rust` (`limma-core`) | Existing 104-test corpus passed; independent R recipe, supported API/label/consumer contract, target-device and fixed M-matrix acceptance still required; global moderation/FDR |
| DMR / probe-aware enrichment | Exact validated DMR / missMethyl workflow until suitable replacement | Generic Rust enrichment or interval grouping does not reproduce the method |
| Networks | `petgraph` with only required algorithm crates | `rustworkx-core`, `leiden-rs`, or alternative `graphrs`; signed/multilayer objective and holdout checks |
| Hierarchical inference | Assess `nuts-rs` with a qualified model/gradient route | Julia Turing fallback/reference; a sampler alone is not a full probabilistic model language |
| Biochemical kinetics | `diffsol`; `rebop` or `differential-equations` for their specific stochastic processes | Julia Catalyst/SciML where reaction construction or semantics require it; quantitative data first |
| Ranked expression enrichment, later | Native `rsfgsea` CPU classic mode if required | Exact fgsea comparison; not a substitute for missMethyl's array correction |
| Frontier kernels / derivatives | Existing Rust facilities; num-dual before experimental Enzyme where sufficient | No initial GPU/AD stage; CPU float64 reference. Python only for a required specialist method |

**File boundaries:** Parquet for typed columnar tables of metadata/results; Arrow IPC for selected interchange; original IDAT retained; HDF5 or another labelled chunked matrix format if required, with explicit sample/probe axes. Do not melt an entire methylation matrix to billions of rows just to use Parquet. Files avoid language embedding and do not promise zero-copy reads across separate processes.

**Schema rules:** stable `study_id`, `assay_id`, `sample_id`, documented `participant_id`, `disease_id`, `mechanism_id`, `ontology_release`, `platform`, `tissue`, `coordinate_build`, `feature_id`, `model_version`, `source_provenance`; null is not false. Record beta/M units, transformations, masks, tested feature universe and multiple-testing method separately.

**Cross-language gate:** when implementation is authorised, round-trip one synthetic Arrow/Parquet table through the actual producer and consumers. Check IDs, null/NaN, numeric precision, list/categorical types, schema and provenance; semantic equality is separate from byte-identical file hashes. Pin independently versioned Arrow/Polars/runtime implementations. Add no unused runtime just to test every possible language.

The [focused backend audit](../research/methylation-backend-audit.md) distinguishes the actual owner fork from the historical sinmojito review. Neither faer nor statrs is installed in the owner fork; additions are conditional. It also records SeSAMe2's float64-test versus production-export distinction. The [local development policy](../research/local-development.md) requires official Actions runners and records the purchase-verified M1 Max/32 GB and i9/128 GB/RTX 4060 8 GB hardware. [Reference/hosting decisions](../research/resources-hosting-reuse.md) stage additional ontologies and reuse existing account assets. The isolated Rust baseline is not a runner installation or an accepted atlas backend. See the [initial setup receipt](../research/qualification/setup-receipt.md).
