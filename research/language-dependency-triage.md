# Ponytail language and dependency choices

**No installation is authorised by this planning document.** Reuse already-qualified tools first, and compare scientific results before claiming a replacement. The minimal file-based Arrow/Parquet contracts in [interoperability](interoperability.md) remain authoritative.

| Candidate | Initial decision | Admit when / remove when |
|---|---|---|
| **Julia** | Preferred modelling language | Use Turing, SciML/Catalyst and Graphs.jl for concrete hierarchical, regulatory and kinetic models; do not write new mechanistic solvers without identified data |
| **Rust** | Preferred native processing where needed | Typed provenance, genomic intervals, parsing, sparse graph work, resource-constrained throughput. Do not equate Rust with automatic scientific or speed advantage |
| **R/Bioconductor** | Qualified scientific reference | IDAT QC, normalisation, limma, DMR and missMethyl. A Rust replacement requires numerical/statistical parity and value |
| **Python** | **Optional**, not prohibited | Use specific mature ontology/repository SDK, algorithm, comparison oracle or visualisation if Julia/Rust/R implementation would entail more work. No duplicate Python data pipeline merely for convenience |
| **Mojo** | **Defer** | Mojo 1.0 was announced Aug 2026, but maturity of *this scientific workflow* and target hardware is unproven. Consider only an isolated benchmarked numerical kernel with an actual bottleneck and scientific oracle |
| **DuckDB** | Initial local metadata engine | SQL joins/provenance/catalogue, no managed lakehouse. Reuse until its query model or throughput is insufficient |
| **Polars (Rust)** | **Preferred conditional** | Add LazyFrame/streaming for real large ingestion/joins/transforms beyond a simple DuckDB query. Require stable IDs, null/schema/row-count parity, identical data, time+peak RSS and reduced custom code. Do not duplicate Python and Rust Polars without an existing consumer |
| **petgraph (Rust)** | **Preferred conditional** | Add when there is an actual Rust graph algorithm; SQL/Parquet relationships suffice for metadata and Julia Graphs.jl for Julia network modelling. Validate graph direction, node IDs, multi-edges, duplicate handling and algorithm output before adoption |
| **limma-rust** | First numerical Rust candidate, **not selected** | Compare exact M matrices, design, empirical Bayes, SE/p/FDR tails, null and small-n simulations, public cohort effects, resource evidence |
| **Rust-Bio, diffsol, pathwaykit, nuts-rs** | Defer | Add only when one qualified native method or bottleneck requires it, benchmarking against existing genomics/Julia references |
| **Burn/CubeCL/GPU** | Defer | Only a large real workload and CPU vs Metal/CUDA numerical/resource comparison justify installation |

## Required dependency swap decision

At N0/N1 and N2/N3: (1) understand the scientific estimand and actual consumers; (2) use repository-owned helpers, stdlib or existing SQL/Julia/R libraries; (3) identify one missing feature; (4) qualify a candidate on exact-source synthetic and admissible public inputs, including licensing and security; (5) demonstrate a material scientific, cost or maintainability advantage; (6) replace *and remove* obsolete dependency only after consumer tests pass. Merely being faster or newer does not imply identical methods.

References: https://docs.pola.rs/user-guide/concepts/lazy-api/ ; https://docs.rs/petgraph/latest/petgraph/ ; https://www.modular.com/blog/modular-26-5-mojo-1-0-is-here .

## Cross-repository assessment

The [central scientific-native standard](https://github.com/edithatogo/repository-standards/blob/main/docs/scientific-native.md) already requires exact-version, security, numerical and consumer qualification and a minimal native core. Its [FAIR standard](https://github.com/edithatogo/repository-standards/blob/main/docs/fair-research-software-standard.md) already documents Ponytail's reuse-first approach. **No mandatory estate-wide Ponytail installation, workflow, duplicate policy, or package addition is justified.** Keep research-specific publication/source gates here. If this project demonstrates a broadly useful algorithm contract or resource benefit, propose one *opt-in advisory* central change with reproducible receipts, not a rollout to unrelated repos. Do not overwrite existing repo templates, Conductor ownership or shared controls.
