# Planned technology and data contracts

Status: source-reviewed candidates; no application dependencies installed or qualified. **Preference: Rust > Julia or Mojo > Python > R**, after scientific suitability. See [selection policy](../research/language-dependency-triage.md) and [candidate audit](../research/rust-candidate-audit.md).

| Function | Preferred candidate to assess | Reference / fallback and gate |
|---|---|---|
| Typed metadata / results | Rust Polars, Arrow/Parquet | DataFusion CLI if SQL suffices; retain a simpler existing DuckDB query. One engine per stage |
| HPO / ontology / intervals | `hpo`, `ontolius`, `bedrs`/`gia`, each only when needed | Preserve full HPOA provenance and evidence; qualify MONDO and coordinate semantics |
| Raw Illumina array QC | No complete Rust replacement qualified | R minfi/SeSAMe reference; SeSAMe2 C CLI candidate with licence, mask and platform conformance gates |
| Differential CpG models | `limma-rust`, first numerical Rust qualification | R limma oracle; same matrix, design, global moderation and FDR family |
| DMR / probe-aware enrichment | Exact validated DMR / missMethyl workflow until suitable replacement | Generic Rust enrichment or interval grouping does not reproduce the method |
| Networks | `petgraph` with only required algorithm crates | `rustworkx-core`, `leiden-rs`, or alternative `graphrs`; signed/multilayer objective and holdout checks |
| Hierarchical inference | Assess `nuts-rs` with a qualified model/gradient route | Julia Turing fallback/reference; a sampler alone is not a full probabilistic model language |
| Biochemical kinetics | `diffsol`; `rebop` or `differential-equations` for their specific stochastic processes | Julia Catalyst/SciML where reaction construction or semantics require it; quantitative data first |
| Frontier kernels | Rust Burn/CubeCL; Mojo at Julia's preference tier | No installation until an actual kernel is needed; CPU float64 reference and device-specific comparison |

**File boundaries:** Parquet for typed columnar tables of metadata/results; Arrow IPC for selected interchange; original IDAT retained; HDF5 or another labelled chunked matrix format if required, with explicit sample/probe axes. Do not melt an entire methylation matrix to billions of rows just to use Parquet. Files avoid language embedding and do not promise zero-copy reads across separate processes.

**Schema rules:** stable `study_id`, `assay_id`, `sample_id`, documented `participant_id`, `disease_id`, `mechanism_id`, `ontology_release`, `platform`, `tissue`, `coordinate_build`, `feature_id`, `model_version`, `source_provenance`; null is not false. Record beta/M units, transformations, masks, tested feature universe and multiple-testing method separately.

**Cross-language gate:** when implementation is authorised, round-trip one synthetic Arrow/Parquet table through the actual producer and consumers. Check IDs, null/NaN, numeric precision, list/categorical types, schema and provenance; semantic equality is separate from byte-identical file hashes. Pin independently versioned Arrow/Polars/runtime implementations. Add no unused runtime just to test every possible language.

