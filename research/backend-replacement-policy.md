# Language-agnostic scientific results and Rust replacement policy

**Ponytail decision: approve a file-level scientific contract, reject a speculative plugin framework.** At N0/N1 **before** and N2/N3 **after each analysis**, explicitly consider retaining, removing or replacing dependencies; see [language and dependency triage](language-dependency-triage.md) and [novelty gates](novelty-priority-protocol.md). Apply **Rust > Julia or Mojo > Python > R** among scientifically suitable candidates, with the [source-reviewed audit](rust-candidate-audit.md). For new stages prefer a suitable existing Rust tool without requiring a speed claim. For replacements, numerical/consumer qualification and total cost still matter. Keep routine execution separate from an isolated R/Julia reference oracle. The project must be able to substitute a qualified Rust command-line backend for an R or Julia stage without rewriting the science or silently changing estimands. This policy is a **design and admission rule only**, not implemented software.

The [focused methylation audit](methylation-backend-audit.md) records the exact source findings and qualification priorities for limma-rust and SeSAMe2. Apply only the checks required by the named scientific stage; qualifying every candidate or porting every fallback is not a prerequisite for a clinical analysis.

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
| `differential-site` | qualified M matrix + design/contrasts + sample/covariates + missingness policy | unique CpG/contrast IDs, coefficient and effect scale, actual SE and its ordinary/moderated definition, test statistic, raw and FDR p-value, sign and estimation flag | R `limma`; `limma-rust` **candidate only**; its inspected `lfcSE` field is unscaled and cannot be accepted as an effect SE |
| `differential-region` | qualified site-level measures and genomic positions; predefined DMR settings | genomic intervals, effect, significance, CpG coverage, uncertainty | R DMR reference; Rust candidate deferred |
| `enrich-pathway` | qualified CpG/region results; platform/gene/probe mapping and ontology release | pathway ID, tested background, adjusted association score, supporting genes/regions | R `missMethyl`; Rust candidate deferred |
| `network-module` | disease effects + regulatory prior graph + provenance | module membership, edges, uncertainty, evidence types | Rust `petgraph` plus required algorithm (`rustworkx-core`/`leiden-rs`), or alternative `graphrs`; qualify against fixed reference |
| `cross-disease-model` | qualified effect estimates + uncertainty + fixed disease/mechanism covariates + split | posterior summaries, uncertainty, held-out predictions and calibration | Rust `nuts-rs` plus qualified model/gradient route; Julia/Turing reference/fallback |
| `reaction-simulate` | curated biological reactions, identified parameters, perturbation and initial conditions | time series, conserved quantities, uncertainty, errors | Rust `diffsol`, or the appropriate stochastic solver; Julia Catalyst/SciML reference/fallback |

## Compatibility gates for a proposed backend replacement

1. **Same scientific task:** approve estimand, normalisation, covariates, contrasts, QC, FDR method and control policy; version the contract before comparisons.
2. **Same evidence:** fixed synthetic cases **and** a rights-cleared public dataset for the named stage, with exact matched input files and sample exclusions. For the first CpG-model comparison, select an eligible cohort from GSE97362/GSE116300/GSE218186 after T01 admission. Public raw-array software fixtures can establish preprocessing fidelity but do not replace independent disease-cohort validation. If methods are not identical, call it a *different method* and evaluate separately rather than claim numerical parity.
3. **Numerical parity:** compare effect estimates, SEs, p-values/FDR near decision cutoffs, missing-data handling, rank/concordance, null simulations, tiny/imbalanced cohorts and deterministic behaviour. Predeclare justified tolerances per statistic before running; `p < 0.05` agreement alone is not sufficient.
4. **Clinical biological parity:** compare signed DMP/DMR results and pathway findings, control sensitivity, study hold-outs and false-positive calibration; inspect material discrepancies even when average errors are small.
5. **Resource and local-runner evidence:** use the [official GitHub Actions self-hosted runner lanes](local-development.md) on the relevant actual Mac/Windows/Linux target, with identical inputs/versions, peak memory, cold/warm runtime, bytes read, optional GPU, compile-time and maintenance/dependency costs. Record the observed job/run and hardware receipt. A hosted job, cloud shell check or emulator does not satisfy the owner's local-runner requirement. No presumed Rust speed advantage.
6. **Security and rights:** check software licence compatibility, provenance, dataset data-use conditions, platform architecture and genuine maintainership.
7. **Decision:** `candidate` -> `scientific_contract_passed` -> `consumer_and_total_cost_accepted` -> `selected`; unresolved required checks remain `hold`. Compare resource/deployment/maintenance costs without presuming speed advantage. Keep the authoritative reference oracle and last-known-qualified revision.

**Selection threshold:** correctness, required method coverage, platform, licence and consumer checks are mandatory. For otherwise suitable implementations at comparable cost, the owner's Rust preference decides. An existing qualified stage also needs a migration assessment; portability/deployment/maintainability can justify replacement even without a speed gain. Do not undertake major custom development merely to change languages. A different statistically valid algorithm is a method comparison, not exact implementation parity.

## First methylation qualifications

These priorities are based on [pinned source inspection](methylation-backend-audit.md), not executed failure tests. Resolve or explicitly exclude each unsupported case before accepting that candidate for its named stage.

1. **Strict matching:** require unique sample/probe/coefficient IDs and the intended exact sets; reject label mismatches, unintended positional fallback and malformed numeric tokens. Preserve declared missing tokens separately from parse errors. Reuse existing standard-library, CSV and error handling rather than build a schema framework.
2. **Actual uncertainty:** the inspected limma-rust top table labels `stdev_unscaled` as `lfcSE`. Ordinary SE is `stdev_unscaled × sigma`; moderated SE is `stdev_unscaled × sqrt(s2_post)`. Declare which the consumer needs, and preserve effect units. An M-value contrast is not transcript expression fold change. Correct/rename the upstream field or use the existing full fit dump with a narrowly specified conversion; do not silently feed unscaled values into T04.
3. **Missingness and rank:** test NaN-aware BH/result ordering and retained-design rank after per-probe missing values or zero weights. A supported complete-case/rejection contract is acceptable; it must not be described as complete R partial-estimability support. Preserve the global moderation and testing family.
4. **Independent comparison:** reuse upstream reference generators/dumps, but fail on unequal key sets, duplicate IDs and one-sided missingness; gate tail probabilities and FDR as well as coefficients/variance/df. The inspected comparator's row warnings and excluded p-value gates are insufficient for admission. A CLI-versus-itself check does not establish scientific parity.

For numerical cleanup, first consider **faer/statrs already declared by the candidate**; they are not installed in this project. Reuse faer QR/SVD/eigen/Cholesky operations or statrs ordinary special functions only where the needed method and error behavior are preserved. Keep stable log-tail routines, R-specific robust estimation and necessary full-Q spline semantics until an equivalent is demonstrated. The audit documents concrete reasons to compare statrs 0.19.1 and faer 0.24.4 against the inspected locks; choose versions through controlled regression and toolchain checks, not an automatic bump. In particular, statrs 0.19.1 raises the minimum Rust version to 1.89. No broad numerical-library rewrite or additional dependency is required by this policy.

For **SeSAMe2**, reuse the author's existing R comparison scripts and publicly traceable fixtures, including GSM2995280 and GSE228820/GSE264438 samples identified in the audit. Admit exact input bytes, licences and annotation/mask versions; public sample identity does not prove equality to the external lab files, especially after de-identification. Test the **production export**: internal raw-beta comparisons use float64, but the inspected `.cg` output is float32 and `describe-probe` prints `%.6g`. Quantify both rounding steps through beta-to-M conversion and downstream inference. If precision is inadequate, prefer an existing supported route or a small upstream export option over a Rust preprocessing rewrite. The synthetic CI checks and existing author comparisons are useful evidence, not our independent public-cohort/local-runner receipt. SeSAMe2's academic/nonprofit research terms also require the intended use to qualify.

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
| `limma-rust` for CpG models | Strict IDs, actual SE, missingness/rank and independent-comparator cases first; then frozen M matrices from admitted GSE97362/GSE116300/GSE218186 | Existing Rust implementation may reduce runtime/deployment costs without a new port | **Early evaluation**, not presumptive switch |
| Rust probe-to-gene enrichment | `missMethyl` parity, source-matched backgrounds and annotation | Repeated large-scale pathway scoring may be costly | **Later**, only a concrete portability or resource need justifies method-development cost |
| Rust DMR inference | validated regional effects and FDR under original paper settings | Potential speed-up in repeated multi-disease analyses | **Defer**; complex method-specific behaviour |
| SeSAMe2 C preprocessing exception | Reuse author comparisons on admitted public raw fixtures; pinned matching manifests/masks, per-step QC and actual float32/text export into M values | Existing CLI may reduce routine R dependency | **Qualify separately**; licence, export and numerical differences first, no Rust rewrite |
| Rust NUTS | Analytic/simulated hierarchical posteriors, gradient checks, Julia reference, admitted disease effect/SE tables | Native inference with a qualified density route | **T04 conditional**; no new PPL |
| Rust ODE/SDE/reaction jumps | Analytic systems, public model/test suites and relevant perturbation data | Reuse diffsol/rebop/differential-equations | **T06 conditional** on a specified identifiable biological model |
| Metal/CUDA GPU | same workload CPU vs GPU with numerical error bounds | Large, dense or ensemble simulations | **Defer** until profiling |

**Current scope remains documentation and planning only. No custom code, packages or CI workflows should be added until an accepted Conductor track names a concrete numerical acceptance case and implementation is authorised.** No runner installation, dependency installation or passed numerical check is implied by this policy.

