# Rust replacement audit — 22 November 2026

## Decision and evidence status

Apply the owner's **Rust > Julia > Python > R** preference using the [selection policy](language-dependency-triage.md). The best next step is to qualify existing implementations, not start an R/Julia porting programme. Rust can cover more of this project than the previous shortlist suggested. Its strongest immediate opportunities are typed data, ontology similarity, interval operations and the existing limma port. Some advertised substitutes implement materially different methods.

**Current candidate and evidence:** the owner's [edithatogo/limma-rust](https://github.com/edithatogo/limma-rust) is the **MassDynamics-derived `limma-core`** at audited base `ba41fb6bbf6e3f2524bd44f5be017c827d5c4aaa`. It is a different implementation from the earlier sinmojito audit. Its cloud Linux debug replay with Rust 1.95.0 passed **104 tests** against committed mixed synthetic/proteomics references ([receipt](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/cloud-corpus-replay-2026-11-22.json)); fresh independent R generation, the methylation consumer and actual official local-runner acceptance remain pending. See [the current fork source audit](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/source-audit-2026-11-22.md).

**Evidence boundary:** the broader candidate search was primary-documentation and selected source/CI inspection; those packages were not executed by that review. Upstream results remain upstream reports unless an exact local receipt is identified. The current fork replay is the explicit initial executable exception, not a benchmark, a disease analysis or scientific admission. Source access/rights and literature novelty have their own records.

**Execution order:** [T07](../conductor/tracks/t07-backend-qualification/spec.md) qualifies whichever method is selected before the consuming analysis. Its committed/synthetic baseline can proceed alongside T01; human methylation qualification requires T01 admission. Optional replacements and the broader [Rust port roadmap](rust-port-roadmap.md) do not block a qualified reference route.

### Search coverage

Two web search engines, docs.rs, official project documentation, GitHub repositories and source files were used. Query families included Rust IDAT/noob/SWAN/minfi/SeSAMe; differential methylation/limma/empirical Bayes; DMRcate/bumphunter/missMethyl/GOmeth; HPO/MONDO/Obographs; Polars/Arrow/DataFusion; genomic intervals; RNA DESeq2; MOFA/single-cell statistics; Bayesian NUTS/PPL; ODE/DAE/SDE/SBML/reaction networks; community detection/multiplex graphs; GPU/Metal/CUDA/automatic differentiation. Strong substitution claims triggered source-level inspection. Absence from this search means **not identified in this review**, not proof no implementation exists anywhere.

## 1. Near-term candidates

| Candidate | What it could replace | What is needed | Disposition |
|---|---|---|---|
| **Polars (Rust)** | Hand-written tabular transformations; many pandas/dplyr-style steps | Stable schema/IDs, null and numeric semantics, streaming-plan checks and whole-stage memory/time comparison on representative tables | Preferred when an actual tabular stage exists |
| **DataFusion CLI / Rust API** | A SQL-based query step, including a possible DuckDB alternative | Query and file-format compatibility, resource/build cost; use CLI before writing an embedding | Alternative to Polars/DuckDB for a named consumer, not an additional required engine |
| **hpo** | PyHPO-style phenotype similarity and association traversal | Same ontology/IC corpus, obsolete/alternate IDs and grouping metric; preserve full source annotations outside simplified term sets | Preferred phenotype candidate |
| **ontolius** | General ontology loading/traversal in Python or custom code | Actual MONDO JSON/xref/relation qualification; licence and data-use review | Conditional; do not add just to duplicate hpo |
| **bedrs / gia** | Custom interval overlaps and some GenomicRanges/bedtools operations | Coordinate, strand, build, ties, duplicates and operation-specific reference fixtures | Try existing gia CLI first; use bedrs for a real native consumer |
| **Owner's MassDynamics-derived limma-core** | The supported linear-model/empirical-Bayes stage of R limma | Build on the passed corpus replay; independent R, public-array consumer and target-device gates | **First numerical candidate; not yet admitted for methylation** |
| **rsdeseq2** | Supported DESeq2 count-model workflow in later T05 | Actual count-matrix/design parity and downstream scientific checks | Later RNA candidate; never apply to array beta values |

Primary sources: [Polars](https://github.com/pola-rs/polars), [DataFusion](https://datafusion.apache.org/user-guide/introduction.html), [hpo](https://docs.rs/hpo/0.12.0/hpo/), [ontolius](https://docs.rs/ontolius/0.8.2/ontolius/), [bedrs](https://github.com/noamteyssier/bedrs), [gia](https://github.com/noamteyssier/gia), [owner's limma-rust](https://github.com/edithatogo/limma-rust), [rsdeseq2](https://github.com/deminden/rsdeseq2).

### Current owner's fork: qualify the existing implementation

The active `limma-core` fork is GPL-3.0-or-later, with `thiserror` as its runtime dependency and CSV/Serde test machinery. It already implements rank-aware per-feature missingness, NaN-aware ordering, confidence-interval scaling and numerical gates for p/F p-values, BH and nonfinite mismatches. There is no production file parser or field called `lfcSE`, and neither faer nor statrs is a dependency. Those facts change the work needed before use; they do not remove scientific qualification.

Follow fork [LM01 baseline](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm01_baseline_20261122/spec.md) → [LM02 consumer](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm02_consumer_20261122/spec.md) → [LM03 methylation admission](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm03_methylation_20261122/spec.md):

1. Reuse the passed committed-corpus replay and existing harness. Make a bounded synthetic R fit/contrast/eBayes generator independently runnable with exact versions, input/reference hashes and expected errors; the external full corpus and locally named R image are not self-contained prerequisites yet.
2. Define the named consumer's unique sample/feature/design/contrast IDs, exact ordering, numeric/missingness policy, supported public inputs and output units. Reuse a shared strict fixture loader instead of creating a schema framework or assuming a production-parser defect.
3. Export actual ordinary/moderated SE from existing fit quantities if required. The fork already computes CI margins using `sqrt(s2_post) * stdev_unscaled`; no `lfcSE` field requires renaming. Preserve non-estimable outputs and compare supported rank/missingness/error cases, without assuming weighted fitting or full limma API coverage.
4. After T01 admission, select eligible cases and appropriate within-study controls from GSE97362/GSE116300/GSE218186. Freeze a processed M-value matrix, design, contrasts, covariates and full tested feature universe. Compare coefficients, variance components, df, actual SE, t/F, p/FDR tails and threshold-adjacent decisions. Software comparison on shared inputs is not independent biological replication.
5. **Preserve global moderation and the intended testing family.** Parquet chunks may support I/O but must not acquire separate eBayes priors or BH families. Include null/known-effect and small/imbalanced cases; high correlations or the same top hits are insufficient.
6. Obtain the actual official local-runner evidence for the required devices and measure the accepted end-to-end consumer. The 104-test cloud result does not establish Mac/Windows acceptance or a speed advantage.

A new numerical dependency is conditional on a demonstrated need under LM04. Preserve R LINPACK's limited-pivot/rank/non-estimable semantics and specialised tails; a generic QR can reproduce fitted values while changing coefficient estimability. The current core need not acquire dataframe, GPU or language-binding dependencies merely to integrate with the atlas.

### Historical comparison: sinmojito/limma-rust

The previously inspected [sinmojito implementation at c569f87](https://github.com/sinmojito/limma-rust/tree/c569f87a1b5aa97f3499255bee7a1a8b45e200fa) is also an unofficial GPL-3.0-or-later limma port, but has a different package/source architecture and dependencies. Its [benchmark report](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/benchmarks/REPORT.md) reports public RNA/protein/metabolite agreement; [its CI](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/.github/workflows/ci.yml) uses stored references on Windows. Neither report establishes this project's methylation acceptance.

The parser/`lfcSE`/missingness-rank/comparator findings and faer/statrs reuse opportunities remain preserved with pinned source links in [the historical sections of the focused audit](methylation-backend-audit.md). They are not defects or installed dependencies of the owner's MassDynamics-derived fork. Reconsider this alternative only for a named capability or demonstrated benefit, with its own acceptance.

### Ontology and interval details that affect science

`hpo` already provides term/set similarity and OMIM/ORPHA associations. The inspected parser skips `NOT` annotations and retains term membership rather than all HPOA frequency/evidence fields. Keep original negation, frequency, onset, evidence and provenance in the catalog; distinguish disease-level annotations from observed participant phenotypes. Check the exact same information-content corpus and group similarity definition in reference comparisons. Its enrichment calculations are not a substitute for array probe-bias correction.

`ontolius` is a GPLv3 general Obographs JSON library. Its documented tested ontologies include HPO, GO, MAxO, UO and MP; MONDO is not explicitly included. Test the actual frozen MONDO release, relation types, alternate/obsolete identifiers and mapping provenance. Neither library grants rights to underlying OMIM content or supplies unrestricted OMIM text.

`grangers` (BSD-3) is a broader Polars/noodles-based annotation option. Its [README](https://github.com/COMBINE-lab/grangers) explicitly describes coercing `.`/`?` strand to `+`; that behavior cannot silently enter general CpG/region work. Preserve unknown strand or use another route. Public dependency types also require compatible Polars/noodles versions. Prefer the smaller interval tool when transcript extraction and GTF/GFF functions are not needed. Rust-Bio/noodles remain useful format/sequence building blocks, not array-analysis replacements.

## 2. Raw arrays, DMRs and enrichment: real gaps and alternatives

### SeSAMe2 is a useful C exception candidate

[SeSAMe2](https://zhou-lab.github.io/sesame/) offers a native C IDAT preprocessing CLI from the sesame lab. It could remove R from routine preprocessing after qualification. Use the CLI and files; a new Rust binding or translation is unnecessary.

Its [licence](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/LICENSE) specifies academic/nonprofit research and directs commercial use or transfers to inquiry. Do not label the whole distribution unrestricted BSD. The [README](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/README.md) says numerical gates require R and test IDATs outside public CI. [NUMERICS](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/NUMERICS.md) and [DIVERGENCES](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/DIVERGENCES.md) document annotation/mask and boundary differences. Its ordinary OLS `dml` is not limma moderation.

Qualification must compare public 450K and EPIC arrays with pinned matching manifests, probe identity/order, channel assignments, masks and processing settings. Inspect raw signals, detection/QC, missingness and beta values at each step; explain legitimate differences individually rather than widening a blanket tolerance. Test supported OS targets and resulting differential/pathway findings. Keep R SeSAMe as oracle/fallback. If the planned method is minfi functional normalization, SeSAMe preprocessing is a **different method**, not an implementation-equivalent substitution.

### Cyanea array modules are held for substantive method differences

The inspected [microarray source](https://github.com/cyanea-bio/labs/blob/5d39b14357064efcfb918b1192e2f26d28b81ece/cyanea-omics/src/microarray.rs) uses heuristic variance moderation with prior degrees of freedom proportional to feature count and approximate normal-tail tests. Its SWAN-labelled routine maps beta-value quantiles between probe types, rather than the CpG-count-stratified intensity procedure described in the [SWAN paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC3446316/). These are method differences, not simply missing packaging. The [bisulfite DMR source](https://github.com/cyanea-bio/labs/blob/5d39b14357064efcfb918b1192e2f26d28b81ece/cyanea-omics/src/methylation.rs) concatenates correlated site/sample observations, raising pseudoreplication concerns. An IDAT reader alone does not establish preprocessing fidelity.

Hold these particular analysis modules as replacements; this is not a judgment on every Cyanea module. Making them equivalent would require statistical-method development and validation. Existing limma-rust is the more focused candidate.

### Narrow R fallback remains justified

No inspected Rust candidate established complete equivalence to the chosen array DMR method or [missMethyl GOmeth/GOregion](https://bioconductor.org/packages/release/bioc/vignettes/missMethyl/inst/doc/missMethyl.html). Generic t-tests, interval merging, hypergeometric enrichment and GSEA do not account for all the same array sampling biases.

A future probe-aware enrichment implementation would need the correct probe universe, multi-gene mappings, unequal probe opportunity correction, statistical tail calculation and region-to-probe handling. Qualify against exact annotations/backgrounds with synthetic unequal-probe null cases and real 450K/EPIC cohorts. A small self-contained stage could eventually be worth contributing; it is not an immediate quick translation. Do not rewrite an entire R package to obtain one required function.

## 3. Networks and shared modules

| Candidate | Useful scope | Remaining work |
|---|---|---|
| **petgraph** | Native graph storage and common algorithms | Stable external IDs; direction, duplicate, self-loop and layer semantics |
| **rustworkx-core** | Additional native algorithms built on petgraph | Select only missing algorithms; use its compatible re-exported petgraph to avoid incompatible graph types |
| **leiden-rs** | Community detection with a petgraph adapter and multiplex support | Freeze objective/resolution; qualify signed layers, shared node set, quality and partition stability |
| **graphrs** | Integrated graph analysis including Louvain/Leiden | Alternative stack where it removes more adapter work; do not install multiple representations without need |

Sources: [petgraph](https://docs.rs/petgraph/latest/petgraph/), [rustworkx-core](https://docs.rs/rustworkx-core/latest/rustworkx_core/), [leiden-rs](https://github.com/atopx/leiden-rs), [graphrs](https://docs.rs/graphrs/latest/graphrs/).

Leiden-rs rejects negative **edge** weights but supports negative **layer** weights. Splitting positive/negative evidence into layers may express a desired objective, but this must be demonstrated; do not drop negative methylation/expression associations or equate multiplex shared-node graphs with arbitrary heterogeneous CpG–gene networks.

Qualification separates graph construction from community detection. Freeze residualisation, association estimator, feature selection, sparsification and inter-layer coupling within training data. Compare planted partitions and the exact cohort-derived networks with a chosen reference. Test objective values, connectedness, seed and node-order stability, label-invariant partition metrics and held-out biological prediction. Matching arbitrary numeric module labels is not meaningful. Upstream a small interface or correctness fix if needed; there is no reason to implement Leiden anew.

## 4. Bayesian and mechanistic modelling

| Candidate | What exists | What it still needs here |
|---|---|---|
| **nuts-rs** | Native NUTS sampler used through nutpie/PyMC | A correct density/gradient, transforms/Jacobians, diagnostics and predictive layer for the frozen disease model |
| **BridgeStan Rust API** | Stan density, derivatives and parameter transformations | Supported connection to the sampler and qualification; retains Stan/C++ toolchain, not pure Rust |
| **diffsol** | Stiff/non-stiff ODE and mass-matrix DAE integration and sensitivities | Identified biological equations, units, events and parameters; comparison to SciML/SUNDIALS |
| **rebop** | Well-mixed stochastic reaction simulation, including a mass-action macro DSL | Supported rates and reaction semantics; distributional checks, not identical random trajectories |
| **differential-equations** | Published Rust ODE/DAE/DDE/SDE interfaces | Exact solver/noise interpretation, convergence and failure behavior for the required problem |
| **sbmlsim-core** | SBML-to-WASM with CVODE/IDA/KLU numerical components and reported semantic tests | Independent replay of supported SBML cases and model behavior; disclose C/transitive components and unsupported constructs |
| **pathwaykit** | Pathway formats, graph/stoichiometric operations and FBA/FVA | Model/format/LP semantics and reference comparison if those functions are needed; not a kinetic solver or methylation enrichment method |

Sources: [nuts-rs](https://github.com/pymc-devs/nuts-rs), [BridgeStan](https://github.com/roualdes/bridgestan), [diffsol](https://github.com/martinjrobins/diffsol), [rebop](https://docs.rs/rebop/latest/rebop/), [differential-equations](https://docs.rs/differential-equations/latest/differential_equations/), [sbmlsim-core](https://matthiaskoenig.github.io/sbmlsim-core/), [its semantic tests](https://matthiaskoenig.github.io/sbmlsim-core/testsuite/), [pathwaykit](https://docs.rs/pathwaykit/latest/pathwaykit/).

**Bayesian qualification:** begin with analytically solvable normal-normal cases with fixed hyperparameters, followed by simulated small disease hierarchies. Match priors, likelihood, transforms and data; check gradients, simulation-based calibration, divergences, effective sample size, uncertainty and whole-study/disease holdouts. Compare posterior distributions within Monte Carlo error, not identical draws. Define which predictors are available for an unseen disease without its molecular outcomes; denoising an observed effect is a different task. The admitted disease effect/SE tables are a useful consumer test; small real datasets alone cannot prove calibration. Julia Turing remains the practical reference/fallback when assembling a Rust model would require substantial infrastructure.

**Dynamics qualification:** public SBML semantic tests, curated kinetic models and analytically checkable systems validate solvers. Stiff ODE/DAE tests need conservation, positivity, events, sensitivities and tolerance convergence. Reaction jumps need distributional/moment checks; SDEs need specified Itô/Stratonovich interpretation and strong/weak convergence. Cross-sectional methylation does not supply missing rate constants or validate predicted time courses. T06 stays conditional on quantitative perturbation evidence.

`ode_solvers` is a smaller [explicit ODE option](https://docs.rs/ode_solvers/latest/ode_solvers/) for non-stiff problems. [mini-mcmc](https://docs.rs/crate/mini-mcmc/latest) is an alternative sampler/autodiff candidate, with compatible versions required. [fugue-ppl](https://github.com/alexnodeland/fugue) explicitly describes research-grade maturity; [Ferric](https://github.com/Ferric-AI/ferric) explicitly limits its present hierarchical inference. Improving a general PPL is a separate research programme. Reuse `faer`/`argmin` when already required; a linear-algebra library does not supply a disease model.

## 5. GPU and other languages

[Burn](https://github.com/tracel-ai/burn) offers higher-level tensors/autodiff; [CubeCL](https://github.com/tracel-ai/cubecl) targets portable compute kernels and describes its API as alpha. Prefer existing operations before custom kernels. [Candle](https://github.com/huggingface/candle) is an alternative for a specifically better-supported model. Choose one relevant stack; GPU availability does not justify neural modelling on tiny cohorts.

CPU float64 is the reference on both machines. [Apple Metal](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf) does not provide general double-precision arithmetic. The later [hardware review](local-development.md) verifies purchase records for M1 Max/32 GB and i9-14900K/128 GB/RTX 4060 8 GB; live OS/driver state and performance remain unmeasured. Measure compile, transfer and full runtime, numerical tails and backend-specific behavior. Polars' [documented GPU engine](https://docs.pola.rs/user-guide/gpu-support/) currently targets Python Lazy API users on NVIDIA via cuDF; that does not imply a Rust Polars Metal engine.


Rust's experimental [Enzyme/std::autodiff route](https://rustc-dev-guide.rust-lang.org/autodiff/installation.html) is a more direct frontier candidate for gradients than adding a new modelling language. It needs a pinned nightly, operation coverage, analytic/finite-difference checks and a fallback. [Futhark](https://futhark-lang.org/) is a specialised array-kernel option, but its advertised GPU backends do not establish a Metal route. No additional language/toolchain is selected now. Mature C/C++ components are useful when they avoid reimplementation; SeSAMe2 and BridgeStan are concrete examples.

## 6. Broader candidates screened out of the immediate stack

| Candidate family | Why it does not displace the selected scientific procedure |
|---|---|
| [single-statistics](https://docs.rs/single-statistics/latest/single_statistics/), SingleRust | Sparse single-cell tests and workflows do not establish limma moderation, Illumina preprocessing or probe-aware enrichment |
| [anndata-rs](https://scverse.org/anndata-rs/) | Useful H5AD/out-of-core format support if a future assay requires it; no need to convert dense blood-array matrices just to adopt a single-cell ecosystem |
| [SciRS2](https://github.com/cool-japan/scirs), linfa/smartcore/statrs-style general statistics | Broad capabilities and author-reported test counts are not evidence for the required domain method. Evaluate one missing numerical function, not a wholesale scientific-stack replacement |
| [GSEApy](https://github.com/zqfang/GSEApy) | Rust computation with a Python interface may be useful for genuine GSEA; not a verified native Rust public API or replacement for missMethyl biases |
| [MOFA/mofapy2](https://biofam.github.io/MOFA2/installation.html) | The core is Python; a direct Python route can avoid an R front end if MOFA is scientifically appropriate. Generic PCA/NMF is a different model; no qualified Rust MOFA replacement identified |
| [rsomics-methyl](https://github.com/omics-rust/rsomics-methyl), modkit and other sequencing methylation tools | Bisulfite/read-count/nanopore methods are different assay pipelines from IDAT arrays |
| Generic Rust SBML readers / pathway graphs | Reading a reaction file does not prove event, kinetic, unit, parameter-estimation or enrichment semantics |

## 7. Minimal development and validation sequence

1. **T01 data/ontology work:** use existing Rust data/ontology/interval tools for the concrete need, and existing CLIs where sufficient. Qualification effort is mainly contracts and fixtures; no new engine.
2. **T07 before T02 consumption:** build on the owner's fork baseline, independent R generator and consumer contract. Qualify the selected inference method on fixed processed arrays after T01 admission, then let T02 consume accepted outputs. SeSAMe2 is a separate conditional preprocessing comparison. A qualified reference route can proceed while an optional Rust replacement remains held; do not change preprocessing and inference simultaneously while attributing differences.
3. **T03/T05:** add a community method or RNA-count backend only for the frozen analysis. Missing supported inputs may justify a bounded upstream extension. Array DMR/probe-aware enrichment stay narrow R fallbacks until a scientifically complete substitute is ready.
4. **T04/T06:** qualify nuts-rs or diffsol only when the model exists. An existing solver plus a small model definition is plausible; recreating Turing/Catalyst is not.
5. **GPU/experimental AD:** deferred until a specified workload warrants them. Native language preference by itself does not require GPU execution.

Every promotion needs exact source/licence, build/security, scientific numerical, consumer and resource evidence. Upstream tests are evidence to inspect; the separately receipted 104-test fork replay is this project's bounded cloud result, not broader admission. Version pinning and explicit error behavior matter more than marketing speed multipliers. Prefer reproducible test cases and small upstream fixes over a private fork. No upstream issue/PR or message was sent during this review.

### Source snapshots inspected

These identify the source reviewed, not a project-wide dependency lockfile. The owner's fork also has the explicit initial cloud test receipt; other entries remain source-only observations. Confirm exact version/revision pairing before use.

| Repository | Source snapshot |
|---|---|
| edithatogo/limma-rust, parent MassDynamics/limma-rust — current candidate | `ba41fb6bbf6e3f2524bd44f5be017c827d5c4aaa`; initial cloud replay recorded |
| sinmojito/limma-rust — historical alternative | `c569f87a1b5aa97f3499255bee7a1a8b45e200fa`; source findings are separate |
| cyanea-bio/labs | `5d39b14357064efcfb918b1192e2f26d28b81ece` |
| zhou-lab/sesame | `f6713747181764e0b7a97b64c3c0d52ab9d82703` |
| anergictcell/hpo | `c56fc31398a1a332876bbdcc17bee4ab45e3e750` |
| ielis/ontolius | `fe10ac2e3a22e6e3c5482a19c91825ba8045b0dc` |
| noamteyssier/bedrs | `f71d798d5a7dc21a7b731a1de6f0858fc37ee667` |
| COMBINE-lab/grangers | `2bb35149893618d0a63a5105977b8391287625ba` |
| deminden/rsdeseq2 | `ede9157049363bb3bb151c01fd235a94d2de4b98` |
| pymc-devs/nuts-rs | `67fe05abea520ae77531da11625297c5b1cdeed0` |
| martinjrobins/diffsol | `8b9f70c755a3deab19fcbf45c8e7d9abbe78bb2c` |
| atopx/leiden-rs | `fad950eea78feab2c9a839c93986edc3ac8d716f` |
| Qiskit/rustworkx | `d730373a544200df944c99a4bb0cf344d3681453` |

Journal routing, including Orphanet and the SSIEM journals, is maintained in [journals.md](journals.md). A language migration does not increase the novelty of a clinical claim; retain the separate N0–N3 publication checks.

## 8. Focused follow-up: concrete improvements before use

The [deeper methylation source audit](methylation-backend-audit.md) supersedes any impression that the first candidate is ready without interface checks. It records exact code paths and bounded upstream changes rather than recommending a new library.

**Current fork:** complete the independently reproducible R reference and narrow consumer contract, then qualify methylation inputs and actual local devices. Strict fixture identity and supported public misuse cases are concrete small additions. Existing rank-aware fitting, CI scaling, NaN ordering and numerical comparison gates should be retained and tested, not reimplemented to repair defects from another repository. The [new roadmap](rust-port-roadmap.md) separates these additions from optional larger ports.

**Reuse first:** the current core has only thiserror at runtime. No faer/statrs upgrade is pending. A new dependency needs a named need, exact source/licence/features, all affected caller tests and acceptable cost. The historical sinmojito audit retains its valid existing-library suggestions; they are scoped to that implementation. CDFLIB-rs remains an optional focused candidate and rmathlib 1.1.0 remains held on the separately documented unresolved upstream report; neither is compulsory.

**SeSAMe2 already has R comparisons.** Its per-step and QCDPB drivers, NUMERICS and DIVERGENCES should be reused. The full external lab corpus is not enumerated, but core test specimens are traceable to public material, including GSM2995280 and GSE228820; released/de-identified bytes must be checked against the original fixtures. Public CI skips real-IDAT/R gates, while synthetic tests still run. Production float32 .cg and six-significant-digit text output are distinct from the float64 oracle helper: qualify the actual export and beta-to-M tails. A supported precision/export option, if needed, is a small upstream task. The 2023 paper's R workflow called “SeSAMe 2” is not a validation of today's standalone C SeSAMe2.

### Additional candidates that can remove real custom work

| Candidate | Concrete consumer / possible replacement | Qualification and disposition |
|---|---|---|
| [rsfgsea](https://github.com/deminden/rsfgsea), 0.4.0 | Existing native Rust CLI/core for genuine preranked GSEA, particularly T05 expression; preferable to adding GSEApy solely for that function | CPU classic mode first. Freeze ranks, universe, ties, gene-set size, scoring, RNG/permutation settings, p-tail/FDR and leading edges. Core default features are empty and Python bindings are separate; no build was run. **Does not replace missMethyl** |
| [Semsimian](https://github.com/monarch-initiative/semsimian), 0.3.0 | Existing Rust API for weighted and explicitly negated phenotype term-set similarity; may avoid custom hpo extensions | Preserve source predicates, IC corpus and weight/negation semantics. Current Cargo includes nonoptional PyO3/build dependencies, so Python-free compilation is unverified. Make bindings optional upstream only if a real native consumer needs it; simpler hpo remains adequate for positive term sets |
| [num-dual](https://docs.rs/num-dual/latest/num_dual/), 0.16.0 | Existing forward/hyperdual gradients and Hessians for a small smooth later model | Verify operation/type coverage and transformed-parameter Jacobians. A simpler first derivative route than experimental compiler work when parameter count permits |
| [ad_trait](https://github.com/djrakita/ad_trait) | Existing forward/reverse alternative when its supported operations fit the model | Qualification against independent gradients/posteriors; not a new project-wide abstraction |
| [CDFLIB-rs](https://github.com/vigna/CDFLIB-rs), 0.4.4 | Paired probability tails/inverse distributions if an identified numerical gap remains | Existing Fortran oracle fixtures are useful upstream evidence, not our test results. Not a universal log-probability replacement |
| [OxO2/SSSOM](https://ceur-ws.org/Vol-4111/Demo_Paper_1.pdf) with Nemo | Existing predicate/provenance-aware crosswalk reasoning | Use frozen mappings initially; no local ontology reasoning service or custom mapping engine without a real need |

rsfgsea's decor mode changes its scoring/null using expression correlations and is not a universally calibrated array correction or cameraPR replacement. Its GPU route also needs its own parity evidence. Use a named method rather than evolving defaults. Semsimian's weighted/negated score is a defined algorithm, not an automatic interpretation of HPO frequency as a weight; omissions are not negative observations.

Source snapshots added: rsfgsea c422ddb205585bd88c23c5ee82644c5572aac2d4; Semsimian 3ee1beb8f841f56db82aa7a575d76729c5effba3; CDFLIB-rs 98476cddbd07ed33a61f5471678f2938674ee167. These are source observations, not installed dependencies.

### Python: use only for a required specialist capability

No Python runtime is required by the initial plan. Retain optional specialist methods only when they avoid substantive custom scientific code.

Python remains an optional, isolated route for an actual specialist consumer: MOFA's mofapy2 core; PyMC/nutpie if a specified model would otherwise require substantial new Rust inference infrastructure; or [methylprep/methylcheck](https://github.com/FoxoTech/methylprep) if their processing/QC functions resolve a specific gap. Methylprep already documents Parquet output, so do not write a duplicate exporter. Historical benchmark claims are not current exact QCDPB parity. SeSAMe2/R SeSAMe is the first same-method preprocessing qualification, subject to its licence, precision and platform gates. Avoid mandatory pandas orchestration and do not install Python just to expose a native Rust CLI.

### Enzyme: useful later, not a novelty claim

[Enzyme's NeurIPS 2020 paper](https://proceedings.neurips.cc/paper_files/paper/2020/hash/9332c513ef44b682e9347822c2e457ac-Abstract.html) already includes Rust among LLVM-targeting languages; [Rust compiler integration was proposed in 2023](https://github.com/rust-lang/compiler-team/issues/611). Using experimental std::autodiff is not itself a new scientific method.

The current [Rust guide](https://rustc-dev-guide.rust-lang.org/autodiff/installation.html) supports an Enzyme nightly component for named Linux, Apple/Intel macOS and Windows llvm-mingw targets. [Current source documentation](https://github.com/rust-lang/rust/blob/main/library/core/src/autodiff.md) describes forward/reverse and higher derivatives, with limitations including dyn Trait inputs, fat LTO and more fragile debug builds. Do not repeat outdated blanket feature limitations from older pages. Apple CPU support is not evidence for Metal GPU differentiation.

If T04 later needs an AD comparison, hold model, parameterisation, sampler, data and splits fixed. Compare analytic/existing-library/Stan or Turing derivatives against Enzyme; test analytic and directional gradients, transformations/log-Jacobians, simulated calibration, interval coverage, divergences, posterior agreement and effective samples per second. Include compile/startup and full-stage memory/time on the actual [hardware](local-development.md). Two engines sharing an incorrect density do not independently validate the model.

Stop if the simpler route meets the need or compiler infrastructure would delay the clinical work. AD cannot infer causal direction, fix batch confounding, differentiate an arbitrary hard clustering decision, or supply kinetics from methylation. Default publication role is supporting material in a useful clinical/transfer paper. A separate methods/software paper requires a distinct reusable advance with demonstrated scientific value; no such result is claimed.
