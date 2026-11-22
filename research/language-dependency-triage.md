# Language preference and dependency selection

**Owner preference, 22 November 2026: Rust > Julia or Mojo > Python > R.** Apply this order among implementations that meet the actual scientific, reproducibility, platform and licence requirements. Julia and Mojo share a preference tier; they do not have interchangeable domain ecosystems. No installation or analytical code is authorised by this document.

The [dated candidate audit](rust-candidate-audit.md) records primary sources, observed limitations and the work needed for promising replacements. All candidates remain unqualified for this project until their named acceptance case has actually passed.

## How the hierarchy changes decisions

1. **A new stage:** choose an existing suitable Rust implementation first. A Rust choice does not require a speed claim or a pre-existing bottleneck. Reuse a CLI or narrow library; do not create an engine to satisfy a language preference.
2. **An existing qualified stage:** compare its replacement on identical inputs and scientific contracts. Correctness is mandatory; portability, simpler deployment, maintainability or reduced runtime/memory can justify the move. With otherwise suitable choices and comparable cost, prefer Rust. Do not require a performance win as the only legitimate reason, and do not accept a material regression without a reason.
3. **A missing Rust capability:** first consider a small upstream contribution or existing supported interface. If that becomes a new statistical-method development programme, use the next suitable language. No new code is authorised at present.
4. **The reference is separate from routine execution:** R/Bioconductor can remain an isolated scientific oracle after a Rust stage is selected. Retaining an oracle does not make R the preferred production language. Replace and remove obsolete routine dependencies only after consumer acceptance.
5. **Record interface and engine separately:** Python Polars uses a Rust engine; BridgeStan uses Stan/C++; SeSAMe2 is C. A wrapper does not change the numerical implementation's language. Established C/C++/Fortran engines and a justified specialist language are permitted exceptions when they reduce work or provide needed science.

## Proposed choices, conditional on a real consumer

| Stage | Preferred candidate / route | Fallback and unresolved work |
|---|---|---|
| Typed tables and joins | Rust Polars with Arrow/Parquet | DataFusion CLI for a SQL-only consumer; retain a simple existing DuckDB query when replacement adds needless work. Choose one engine for a stage |
| HPO similarity and disease associations | Rust `hpo`; Semsimian only for a needed richer score | Preserve source annotations. Semsimian supports weighted/negated terms, but its current nonoptional PyO3 needs native-build qualification |
| General ontology graph loading | Rust `ontolius` if needed | Qualify the exact MONDO release; its documented tested list does not establish MONDO support. Do not add alongside `hpo` without a separate need |
| Genomic interval operations | Rust `bedrs` or existing `gia` CLI | Coordinate/build/strand tests; `grangers` only if broader annotation functions repay extra dependency and conversion cost |
| Differential CpG models | **First numerical qualification: `limma-rust`** | Pinned R limma remains oracle and fallback. No raw IDAT preprocessing, DMR or missMethyl substitution is implied |
| Raw Illumina arrays | No qualified complete Rust pipeline found in this review | R minfi/SeSAMe reference; **SeSAMe2 C CLI** is a targeted exception candidate with numerical and licence gates |
| Array DMR inference and probe-aware pathway testing | Keep exact validated method until a suitable replacement is qualified | No verified complete Rust equivalent to the chosen DMR workflow or missMethyl found; a t-test, interval merge or generic enrichment is insufficient |
| Bulk RNA counts, later T05 | Assess Rust `rsdeseq2` for a DESeq2 estimand, or qualified `limma-rust` voom for its own estimand | These are different statistical methods; choose scientifically, not as interchangeable function names. Canonical DESeq2/limma reference |
| Networks | `petgraph`; add `rustworkx-core` only for a missing algorithm | `leiden-rs` for a qualified community objective; `graphrs` is an alternative integrated stack, not an extra mandatory graph representation |
| Hierarchical inference | Assess `nuts-rs` with an existing density/gradient route | Julia Turing is the practical fallback when Rust would require substantial model infrastructure. BridgeStan is a C++-backed option; no new sampler |
| Deterministic kinetics | Assess Rust `diffsol` for an identified ODE/DAE | Julia Catalyst/SciML for reaction construction, inference and unsupported semantics. A solver does not discover kinetics from methylation |
| Stochastic models | `rebop` for well-mixed reaction jumps; `differential-equations` for a specified SDE | Match the mathematical process and validate distributions/convergence against Julia/analytic references |
| GPU/tensors | Existing Burn operators first; CubeCL only for a missing kernel | CPU float64 reference. Candle is an alternative if it fits an existing model better. No GPU work solely because hardware is available |
| Specialist multi-omics | Prefer a qualified Rust/Julia method if it implements the required model | Python `mofapy2` is a legitimate direct interface to MOFA's Python core when that model is needed; generic Rust PCA/NMF is not a MOFA replacement |
| Ranked gene expression GSEA | Native `rsfgsea` CPU classic mode, if required | Qualify against fgsea; decor is a different scoring/null choice. Neither replaces array probe-bias correction |
| Mojo | **Removed from active initial stack**; retain future preference tier beside Julia | No selected early experiment requires a unique Mojo capability. Reconsider only for a supported, needed kernel with whole-stage evidence |

Primary sources and version-specific limitations are in the [audit](rust-candidate-audit.md). Arrow IPC/Parquet [file contracts](interoperability.md) and [backend qualification](backend-replacement-policy.md) remain the integration mechanism. Do not add all candidates or a universal plugin framework.

Read the [focused methylation audit](methylation-backend-audit.md) before accepting limma-rust/SeSAMe2: interface correctness and actual exported values matter as much as numerical kernels. Prefer already present faer/statrs functions; evaluate newer releases only against relevant contracts and MSRV/feature costs. Keep specialised stable log tails and R-specific algorithms where no equivalent is demonstrated.

**No mandatory Python runtime:** retain an isolated optional route for mofapy2, a genuinely needed PyMC/nutpie model, or methylprep/methylcheck capabilities. Methylprep already provides Parquet output; don't recreate its exporter. Existing native CLIs take precedence when scientifically equivalent. R remains an isolated oracle and narrow fallback for missing validated domain methods, not an all-purpose orchestrator. Data/Python policy tooling from other repositories is not a reason to embed those runtimes into the atlas core.

## Review and upstream work

At N0/N1 and N2/N3, record retain / replace / remove / defer against the current method, source revision, required capability and total cost. Distinguish **integration/validation**, **a bounded missing feature**, and **a new method or major rewrite**. Prefer submitting a reproducible fixture or narrow fix upstream when later authorised; do not silently maintain a fork. Document provenance and licence obligations before copying or translating source.

The [central scientific-native standard](https://github.com/edithatogo/repository-standards/blob/main/docs/scientific-native.md) already requires exact-source, security, numerical, consumer and resource evidence. Its [FAIR guidance](https://github.com/edithatogo/repository-standards/blob/main/docs/fair-research-software-standard.md) already supports Ponytail reuse. No estate-wide plugin installation, template replacement or compulsory language migration is warranted. Research-specific candidate decisions belong here; reusable evidence may later justify an opt-in central proposal.

