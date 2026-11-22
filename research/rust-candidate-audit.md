# Rust replacement audit — 22 November 2026

## Decision and evidence status

Apply the owner's **Rust > Julia or Mojo > Python > R** preference using the [selection policy](language-dependency-triage.md). The best next step is to qualify existing implementations, not start an R/Julia porting programme. Rust can cover more of this project than the previous shortlist suggested. Its strongest immediate opportunities are typed data, ontology similarity, interval operations and the existing limma port. Some advertised substitutes implement materially different methods.

**Evidence level:** primary documentation and selected source/CI/benchmark-file inspection. No candidate was installed, compiled, run, benchmarked or scientifically qualified here. Upstream performance and test results remain upstream reports. Exact source snapshots below identify the inspected bytes, not necessarily the published release commits. No source data were downloaded, no ethics determination made and no analysis novelty search completed by this dependency review.

### Search coverage

Two web search engines, docs.rs, official project documentation, GitHub repositories and source files were used. Query families included Rust IDAT/noob/SWAN/minfi/SeSAMe; differential methylation/limma/empirical Bayes; DMRcate/bumphunter/missMethyl/GOmeth; HPO/MONDO/Obographs; Polars/Arrow/DataFusion; genomic intervals; RNA DESeq2; MOFA/single-cell statistics; Bayesian NUTS/PPL; ODE/DAE/SDE/SBML/reaction networks; community detection/multiplex graphs; GPU/Metal/CUDA/Mojo/automatic differentiation. Strong substitution claims triggered source-level inspection. Absence from this search means **not identified in this review**, not proof no implementation exists anywhere.

## 1. Near-term candidates

| Candidate | What it could replace | What is needed | Disposition |
|---|---|---|---|
| **Polars (Rust)** | Hand-written tabular transformations; many pandas/dplyr-style steps | Stable schema/IDs, null and numeric semantics, streaming-plan checks and whole-stage memory/time comparison on representative tables | Preferred when an actual tabular stage exists |
| **DataFusion CLI / Rust API** | A SQL-based query step, including a possible DuckDB alternative | Query and file-format compatibility, resource/build cost; use CLI before writing an embedding | Alternative to Polars/DuckDB for a named consumer, not an additional required engine |
| **hpo** | PyHPO-style phenotype similarity and association traversal | Same ontology/IC corpus, obsolete/alternate IDs and grouping metric; preserve full source annotations outside simplified term sets | Preferred phenotype candidate |
| **ontolius** | General ontology loading/traversal in Python or custom code | Actual MONDO JSON/xref/relation qualification; licence and data-use review | Conditional; do not add just to duplicate hpo |
| **bedrs / gia** | Custom interval overlaps and some GenomicRanges/bedtools operations | Coordinate, strand, build, ties, duplicates and operation-specific reference fixtures | Try existing gia CLI first; use bedrs for a real native consumer |
| **limma-rust** | The supported linear-model/empirical-Bayes stage of R limma | Independent public-array replay, edge cases and target-platform checks | **First numerical qualification candidate** |
| **rsdeseq2** | Supported DESeq2 count-model workflow in later T05 | Actual count-matrix/design parity and downstream scientific checks | Later RNA candidate; never apply to array beta values |

Primary sources: [Polars](https://github.com/pola-rs/polars), [DataFusion](https://datafusion.apache.org/user-guide/introduction.html), [hpo](https://docs.rs/hpo/0.12.0/hpo/), [ontolius](https://docs.rs/ontolius/0.8.2/ontolius/), [bedrs](https://github.com/noamteyssier/bedrs), [gia](https://github.com/noamteyssier/gia), [limma-rust](https://github.com/sinmojito/limma-rust), [rsdeseq2](https://github.com/deminden/rsdeseq2).

### limma-rust: qualify the existing implementation

The inspected v0.1.0 project is an unofficial GPL-3.0-or-later port with reference fixtures for linear models, contrasts, empirical Bayes including robust/trend options, weights and related methods. Its [benchmark report](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/benchmarks/REPORT.md) reports agreement on public RNA/protein/metabolite datasets; it does not establish this project's rare-disease array performance. [CI](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/.github/workflows/ci.yml) is Windows-based and checks stored reference values rather than independently regenerating them with R. [The fit implementation](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/fit.rs) rejects a rank-deficient design. Do not promise all R partial-estimability semantics.

**Planned qualification, not executed:**

1. After T01 admission, select eligible molecularly confirmed cases and appropriate controls separately from GSE97362, GSE116300 and GSE218186. Participant independence is a scientific replication requirement; a shared-input software comparison is not an independent biological cohort.
2. Freeze one normalized M-value matrix, sample exclusions, design, contrasts, covariates and full tested feature universe per study. Keep preprocessing fixed while comparing differential-model engines; otherwise differences cannot be attributed to the Rust stage.
3. Compare coefficients, residual/prior/posterior variances, standard errors, degrees of freedom, moderated t/F statistics, log p-value tails, adjusted p-values and threshold-adjacent decisions. High correlation and the same top genes are insufficient.
4. Add synthetic null and known-effect data, small/imbalanced groups, constant probes, missingness, covariate confounding, near-singular/full-rank designs and required robust/trend options. Specify supported inputs and error behavior. If rank-deficient models are outside the chosen contract, reject them explicitly in both routes; do not conceal a narrower contract as full equivalence.
5. **Preserve global moderation and the intended multiple-testing family.** Independently fitting eBayes priors or BH adjustment per Parquet chunk changes the statistical procedure. Chunked I/O is allowed; arbitrary chunk-specific inference is not.
6. Assess the complete stage on Apple ARM64 and the actual x86 OS/CPU, including input/output, single versus matched thread counts, startup/compile costs, peak memory and failures. Review scientific conclusions after replacing only this stage.

Likely work is reference-fixture replay, a narrow input/output adapter only if existing interfaces are inadequate, platform evidence and bounded upstream fixes. A new implementation of limma is not justified. Keep canonical R limma as an isolated oracle even after any routine-execution replacement.

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

## 5. GPU, Mojo and other languages

[Burn](https://github.com/tracel-ai/burn) offers higher-level tensors/autodiff; [CubeCL](https://github.com/tracel-ai/cubecl) targets portable compute kernels and describes its API as alpha. Prefer existing operations before custom kernels. [Candle](https://github.com/huggingface/candle) is an alternative for a specifically better-supported model. Choose one relevant stack; GPU availability does not justify neural modelling on tiny cohorts.

CPU float64 is the reference on both machines. [Apple Metal](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf) does not provide general double-precision arithmetic. The exact NVIDIA model, VRAM, OS and driver are unresolved; do not reinterpret '4600' as a confirmed RTX 4060. Measure compile, transfer and full runtime, numerical tails and backend-specific behavior. Polars' [documented GPU engine](https://docs.pola.rs/user-guide/gpu-support/) currently targets Python Lazy API users on NVIDIA via cuDF; that does not imply a Rust Polars Metal engine.

Mojo's official [1.2.0 release](https://mojolang.org/releases/v1.2.0/) is dated 22 October 2026. Its [requirements](https://mojolang.org/docs/requirements/) and [MAX hardware documentation](https://max.modular.com/gpu/hardware-compatibility/) include Apple silicon, with the specific caveat that some kernels supported on later Apple chips fail on M1. [GPU use requires MAX](https://mojolang.org/docs/faq/), whose [licence is separate](https://www.modular.com/blog/max-license) from the open Mojo SDK. This removes outdated blanket objections about absent Apple support or pre-1.0 status; it does not establish a validated methylation ecosystem. Mojo sits beside Julia in preference, with a conditional role in a specific qualified kernel.

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
2. **T02 with T07 qualification:** first limma-rust comparison using fixed processed arrays. If it passes, select it for supported routine CpG modelling. In a separate experiment, assess SeSAMe2 against R SeSAMe. Never change preprocessing and inference simultaneously while attributing differences.
3. **T03/T05:** add a community method or RNA-count backend only for the frozen analysis. Missing supported inputs may justify a bounded upstream extension. Array DMR/probe-aware enrichment stay narrow R fallbacks until a scientifically complete substitute is ready.
4. **T04/T06:** qualify nuts-rs or diffsol only when the model exists. An existing solver plus a small model definition is plausible; recreating Turing/Catalyst is not.
5. **GPU/experimental AD/Mojo:** deferred until a specified workload warrants them. Native language preference by itself does not require GPU execution.

Every promotion needs exact source/licence, build/security, scientific numerical, consumer and resource evidence. A package's upstream tests are evidence to inspect, not this project's passed tests. Version pinning and explicit error behavior matter more than marketing speed multipliers. Prefer reproducible test cases and small upstream fixes over a private fork. No upstream issue/PR or message was sent during this review.

### Source snapshots inspected

These are read-at-source observations, not a dependency lockfile or installation approval. Confirm the exact version/revision pairing before execution.

| Repository | Source snapshot |
|---|---|
| sinmojito/limma-rust | `c569f87a1b5aa97f3499255bee7a1a8b45e200fa` |
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
