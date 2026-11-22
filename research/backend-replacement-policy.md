# Language-agnostic scientific results and Rust replacement policy

**Ponytail decision: approve a file-level scientific contract, reject a speculative plugin framework.** At N0/N1 **before** and N2/N3 **after each analysis**, explicitly consider retaining, removing or replacing dependencies; see [language and dependency triage](language-dependency-triage.md) and [novelty gates](novelty-priority-protocol.md). Apply **Rust > Julia or Mojo > Python > R** among scientifically suitable candidates, with the [source-reviewed audit](rust-candidate-audit.md). For new stages prefer a suitable existing Rust tool without requiring a speed claim. For replacements, numerical/consumer qualification and total cost still matter. Keep routine execution separate from an isolated R/Julia reference oracle. The project must be able to substitute a qualified Rust command-line backend for an R or Julia stage without rewriting the science or silently changing estimands. This policy is a **design and admission rule only**, not implemented software.

## Approach

Define each analysis stage by **documented inputs, scientific estimand and validated outputs**. A backend is a version-pinned executable or command, not an in-process plugin interface. Stage configuration may later name the executable, version and runtime; this does not warrant building a generic orchestrator now.

- **Freeze a reference, then select a backend:** R/Bioconductor provides array/statistical oracles and Julia Turing/SciML provides model/solver references. Existing Rust implementations are preferred candidates when they meet the actual method contract; lower-ranked references do not dictate the routine execution language. A qualified C/C++ engine may avoid a rewrite.
- **Exchange only at stage boundaries:** original IDATs remain native; dense beta/M assay matrices retain sample/probe axes in a suitable chunked/labelled representation (HDF5 is a candidate); metadata, model inputs/outputs and annotations use Arrow IPC/Parquet; use one appropriate Polars/DataFusion/DuckDB route for catalogue joins.
- **Do not replace a procedure merely by giving another library the same stage name.** Sign, coefficient scaling, missing-value conventions, reference genome, filtering, covariate model and multiple-testing method form part of the scientific contract.
- **Provenance:** dataset accession, source checksum, original array platform, mapping and ontology releases, exact backend/flags/version, runtime/OS/CPU/GPU, file hash, seed, data rights and cohort-split ID must accompany every result.

## Proposed stage contracts (to implement only when analysis begins)

| Stage ID | Input contract | Output contract | Reference and alternative |
|---|---|---|---|
| `assay-normalise` | IDAT pair manifest; platform, sample/batch labels; predefined QC | labelled beta and/or M matrix, detection/QC statistics, rejection reasons | R `minfi`/`sesame` oracle; no complete Rust replacement qualified; SeSAMe2 C CLI is a conditional exception |
| `differential-site` | qualified M matrix + design/contrasts + sample/covariates + missingness policy | CpG ID, contrast, coefficient, SE, test statistic, raw and FDR p-value, sign and estimation flag | R `limma`; `limma-rust` **candidate only** |
| `differential-region` | qualified site-level measures and genomic positions; predefined DMR settings | genomic intervals, effect, significance, CpG coverage, uncertainty | R DMR reference; Rust candidate deferred |
| `enrich-pathway` | qualified CpG/region results; platform/gene/probe mapping and ontology release | pathway ID, tested background, adjusted association score, supporting genes/regions | R `missMethyl`; Rust candidate deferred |
| `network-module` | disease effects + regulatory prior graph + provenance | module membership, edges, uncertainty, evidence types | Rust `petgraph` plus required algorithm (`rustworkx-core`/`leiden-rs`), or alternative `graphrs`; qualify against fixed reference |
| `cross-disease-model` | qualified effect estimates + uncertainty + fixed disease/mechanism covariates + split | posterior summaries, uncertainty, held-out predictions and calibration | Rust `nuts-rs` plus qualified model/gradient route; Julia/Turing reference/fallback |
| `reaction-simulate` | curated biological reactions, identified parameters, perturbation and initial conditions | time series, conserved quantities, uncertainty, errors | Rust `diffsol`, or the appropriate stochastic solver; Julia Catalyst/SciML reference/fallback |

## Compatibility gates for a proposed backend replacement

1. **Same scientific task:** approve estimand, normalisation, covariates, contrasts, QC, FDR method and control policy; version the contract before comparisons.
2. **Same evidence:** fixed synthetic cases **and** a right-cleared public dataset (first: GSE97362/GSE218186 or GSE74432), with exact matched input files and sample exclusions. If methods are not identical, call it a *different method* and evaluate separately rather than claim numerical parity.
3. **Numerical parity:** compare effect estimates, SEs, p-values/FDR near decision cutoffs, missing-data handling, rank/concordance, null simulations, tiny/imbalanced cohorts and deterministic behaviour. Predeclare justified tolerances per statistic before running; `p < 0.05` agreement alone is not sufficient.
4. **Clinical biological parity:** compare signed DMP/DMR results and pathway findings, control sensitivity, study hold-outs and false-positive calibration; inspect material discrepancies even when average errors are small.
5. **Resource evidence:** benchmark on **same hardware** and identical inputs/versions, peak memory, cold/warm runtime, bytes read, optional GPU, compile-time and maintenance/dependency costs. No presumed Rust speed advantage.
6. **Security and rights:** check software licence compatibility, provenance, dataset data-use conditions, platform architecture and genuine maintainership.
7. **Decision:** `candidate` -> `scientific_contract_passed` -> `consumer_and_total_cost_accepted` -> `selected`; unresolved required checks remain `hold`. Compare resource/deployment/maintenance costs without presuming speed advantage. Keep the authoritative reference oracle and last-known-qualified revision.

**Selection threshold:** correctness, required method coverage, platform, licence and consumer checks are mandatory. For otherwise suitable implementations at comparable cost, the owner's Rust preference decides. An existing qualified stage also needs a migration assessment; portability/deployment/maintainability can justify replacement even without a speed gain. Do not undertake major custom development merely to change languages. A different statistically valid algorithm is a method comparison, not exact implementation parity.

## Avoid these common interoperability errors

- Missing (`null`) versus `NaN`, infinity, zero and detection-failed probes.
- Probe and sample row/column order silently changing across Parquet queries; join by stable IDs.
- `float32` versus `float64`; beta and M values have different units and stability near 0/1.
- Different genome builds / EPIC vs 450K probe sets, annotation version drift.
- Hidden reuse of a patient, control, sample or super-series component in both train/test.
- Different treatment of covariates, moderated variance priors, and multiple testing. Chunked files must not silently produce chunk-specific empirical-Bayes priors or FDR families.
- Numeric module labels and stochastic sample paths are not comparable identities: use label-invariant graph metrics and posterior/distributional checks where appropriate.
- Licensing: porting GPL code can convey obligations, even when rewritten in Rust. A clean-room implementation needs careful legal and scientific provenance, not a blanket exemption.

## Test and benchmark plan (no code yet)

| Candidate replacement | First safe comparison | Reason to attempt | Likely decision |
|---|---|---|---|
| Rust native accession/checksum and genomic interval joins | Round-trip manifest + genomic intervals against reference outputs | Large metadata and interval operations often benefit from typed native tooling | **Earliest**, when there is an actual data consumer |
| `limma-rust` for CpG models | Frozen processed M matrices from admitted GSE97362/GSE116300/GSE218186; synthetic small-n and explicit rank/error cases | Millions of model fits could benefit in larger atlases | **Early evaluation**, not presumptive switch |
| Rust probe-to-gene enrichment | `missMethyl` parity, source-matched backgrounds and annotation | Repeated large-scale pathway scoring may be costly | **Later**, only a concrete portability or resource need justifies method-development cost |
| Rust DMR inference | validated regional effects and FDR under original paper settings | Potential speed-up in repeated multi-disease analyses | **Defer**; complex method-specific behaviour |
| SeSAMe2 C preprocessing exception | Pinned R SeSAMe, same raw arrays, manifests/masks and QC; per-step outputs | Existing CLI may reduce routine R dependency | **Qualify separately**; licence and numerical differences first, no Rust rewrite |
| Rust NUTS | Analytic/simulated hierarchical posteriors, gradient checks, Julia reference, admitted disease effect/SE tables | Native inference with a qualified density route | **T04 conditional**; no new PPL |
| Rust ODE/SDE/reaction jumps | Analytic systems, public model/test suites and relevant perturbation data | Reuse diffsol/rebop/differential-equations | **T06 conditional** on a specified identifiable biological model |
| Metal/CUDA GPU | same workload CPU vs GPU with numerical error bounds | Large, dense or ensemble simulations | **Defer** until profiling |

**No custom code, packages or CI workflows should be added until an accepted Conductor track names a concrete numerical acceptance case.**

