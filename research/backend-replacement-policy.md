# Language-agnostic scientific results and Rust replacement policy

**Ponytail decision: approve a file-level scientific contract, reject a speculative plugin framework.** At N0/N1 **before** and N2/N3 **after each analysis**, explicitly consider retaining, removing or replacing dependencies; see [language and dependency triage](language-dependency-triage.md) and [novelty gates](novelty-priority-protocol.md). Apply **Rust > Julia > Python > R** among scientifically suitable candidates, with the [source-reviewed audit](rust-candidate-audit.md). For new stages prefer a suitable existing Rust tool without requiring a speed claim. For replacements, numerical/consumer qualification and total cost still matter. Keep routine execution separate from an isolated R/Julia reference oracle. The project must be able to substitute a qualified Rust command-line backend for an R or Julia stage without rewriting the science or silently changing estimands. This policy defines admission; it is not a scientific implementation or a passed consumer qualification.

## Current candidate and evidence

The active Rust differential-model candidate is the owner's **MassDynamics-derived [edithatogo/limma-rust](https://github.com/edithatogo/limma-rust)**, package `limma-core`, audited base `ba41fb6bbf6e3f2524bd44f5be017c827d5c4aaa`. The earlier `sinmojito/limma-rust` audit concerns a different implementation. Its parser, `lfcSE`, rank/comparator findings and existing faer/statrs dependencies must not be assigned to this fork. See [the actual fork source audit](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/source-audit-2026-11-22.md).

**Observed baseline:** `cargo +1.95.0 test --locked` passed **104 tests** in the cloud Linux workspace against committed mixed synthetic/proteomics references; see [the exact receipt](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/cloud-corpus-replay-2026-11-22.json). Fresh independently generated R output, the named methylation consumer and official user-device runner acceptance remain separate, unpassed gates. An existing test replay does not qualify the backend for patient-data inference.

The [focused methylation audit](methylation-backend-audit.md) separates current-fork work from historical findings and SeSAMe2 qualification. [T07](../conductor/tracks/t07-backend-qualification/spec.md) must qualify the **selected method before its consuming scientific analysis**; its baseline can proceed alongside T01 on committed/synthetic fixtures. Optional ports and unneeded replacements are not prerequisites: a qualified reference route can supply the analysis. The [Rust port roadmap](rust-port-roadmap.md) defines the small additions and conditional larger work.

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
| `differential-site` | qualified M matrix + design/contrasts + sample/covariates + missingness policy | unique CpG/contrast IDs, coefficient and effect scale, actual SE and its ordinary/moderated definition, test statistic, raw and FDR p-value, sign and estimation flag | R `limma`; owner's MassDynamics-derived `limma-core` is a candidate with a passed initial corpus replay; no `lfcSE` field exists in this fork |
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

Follow the actual fork's [LM01 baseline](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm01_baseline_20261122/spec.md), [LM02 consumer contract](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm02_consumer_20261122/spec.md) and [LM03 methylation admission](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm03_methylation_20261122/spec.md). These are remaining qualification tasks, not an assertion that this implementation has the other repository's defects.

1. **Strict boundary identity:** the core accepts positional numeric matrices, not production CSV. Validate unique sample/probe/design/contrast identifiers and exact ordering in the consumer. Strengthen the existing fixture loaders' name checks where absent, reusing CSV/Serde and standard-library machinery. Reject malformed numeric text in the chosen adapter rather than treating it as an intentional missing value.
2. **Actual uncertainty:** the fork has no `lfcSE` field and already scales its confidence intervals correctly. Ordinary SE is `stdev_unscaled × sigma`; moderated SE is `stdev_unscaled × sqrt(s2_post)`. Declare which quantity the consumer needs and export it from existing components if required. Preserve M-value units as differences in log methylation odds.
3. **Supported input and estimability:** rank-aware per-feature missingness and NaN-aware ordering already exist. Verify their supported-domain contract and all-missing/zero-df/non-estimable cases against the oracle; define invalid public input behaviour. Do not assume weighted fitting or every limma method is supported. Preserve global moderation and the testing family.
4. **Independent reproducibility:** the current harness already gates p/F p-values, BH, CIs and mismatched nonfinite values. Reuse it. Make a bounded independent R generator self-contained, identify its exact versions/inputs and compare the named consumer. The historical upstream report and this cloud replay are distinct from fresh R execution.

The current fork has **neither faer nor statrs**; its runtime dependency is thiserror, with CSV/Serde test machinery. Introducing a numerical library is a new, conditional decision under [LM04](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm04_dependencies_20261122/spec.md), justified by an observed maintenance or resource need. Retain R LINPACK's rank/pivot/non-estimable semantics and specialised tail/robust behaviour until a proposed replacement passes all affected callers. Version comparisons retained in the historical sinmojito audit are not upgrade instructions for this fork. No new numerical dependency is required by this policy.

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

## Qualification work and its evidence boundary

| Candidate replacement | First safe comparison | Reason to attempt | Likely decision |
|---|---|---|---|
| Rust native accession/checksum and genomic interval joins | Round-trip manifest + genomic intervals against reference outputs | Large metadata and interval operations often benefit from typed native tooling | **Earliest**, when there is an actual data consumer |
| Owner's MassDynamics-derived `limma-core` for CpG models | Build on the 104-test cloud replay; fresh independent R generator and consumer contract, then frozen M matrices from admitted GSE97362/GSE116300/GSE218186 | Existing Rust implementation may reduce deployment/maintenance cost without a new port | **Initial baseline passed; scientific admission pending** |
| Rust probe-to-gene enrichment | `missMethyl` parity, source-matched backgrounds and annotation | Repeated large-scale pathway scoring may be costly | **Later**, only a concrete portability or resource need justifies method-development cost |
| Rust DMR inference | validated regional effects and FDR under original paper settings | Potential speed-up in repeated multi-disease analyses | **Defer**; complex method-specific behaviour |
| SeSAMe2 C preprocessing exception | Reuse author comparisons on admitted public raw fixtures; pinned matching manifests/masks, per-step QC and actual float32/text export into M values | Existing CLI may reduce routine R dependency | **Qualify separately**; licence, export and numerical differences first, no Rust rewrite |
| Rust NUTS | Analytic/simulated hierarchical posteriors, gradient checks, Julia reference, admitted disease effect/SE tables | Native inference with a qualified density route | **T04 conditional**; no new PPL |
| Rust ODE/SDE/reaction jumps | Analytic systems, public model/test suites and relevant perturbation data | Reuse diffsol/rebop/differential-equations | **T06 conditional** on a specified identifiable biological model |
| Metal/CUDA GPU | same workload CPU vs GPU with numerical error bounds | Large, dense or ensemble simulations | **Defer** until profiling |

**Current increment:** repository setup and the existing fork corpus replay have real receipts. This policy does not initiate a new scientific implementation or disease analysis. New numerical code needs the relevant track and acceptance case; configured workflows are not executed user-device runner evidence. Qualify the selected backend before analysis while keeping optional ports off the critical path.
