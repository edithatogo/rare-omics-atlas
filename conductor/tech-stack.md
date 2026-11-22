# Planned technology / data contracts

Status: candidates; no application dependencies installed.

| Function | First tool | Fallback / qualification |
|---|---|---|
| Study and ontology metadata | DuckDB; Parquet | Rust/Polars only for measured throughput or type-validation needs |
| Raw Illumina array QC | R/Bioconductor minfi/sesame | Rust replacement only after numerical parity |
| Differential methylation / enrichment | limma, missMethyl, qualified DMR workflow | Evaluate limma-rust on identical synthetic and public data |
| Scientific graphs / Bayesian inference | Julia Graphs.jl, Turing.jl | Simpler pathway effects before network and hierarchy |
| Biochemical models | Julia Catalyst/ModelingToolkit/DifferentialEquations | Rust diffsol/pathwaykit only for demonstrated advantages |
| GPU | none initially | Metal/CUDA only following profiler and numerical conformance |

**File boundaries:** Parquet for typed, row-oriented analytical tables and metadata; Arrow IPC for selected short-lived tabular interchange; original IDAT retained; HDF5 for big matrix arrays if required, with explicit sample/probe axes. Avoid long-form Parquet for billion-cell methylation matrices unless benchmarking warrants it.

**Schema rules:** stable `study_id`, `assay_id`, `sample_id`, `participant_id` (only when documented), `disease_id`, `mechanism_id`, `ontology_release`, `platform`, `tissue`, `coordinate_build`, `feature_id`, `model_version` and `source_provenance`; null is not false. Track log2 fold, beta and M-value units/interpretation separately, and record multiple-testing methodology. Pin source versions and calculation environment.

**Cross-language gate:** produce, read and round-trip one synthetic Parquet/Arrow table through intended R, Julia and Rust implementations before adopting additional data contracts. Validate type, null, numeric tolerance, ordering keys, metadata and file checksums.
