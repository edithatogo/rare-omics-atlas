# Deeper methylation backend audit — 22 November 2026

## Scope and conclusion

Read-only source and documentation review under Ponytail full. No package was installed, compiled, executed, benchmarked or scientifically qualified. No patient arrays were downloaded. No upstream issue, PR, message or code change was made; this document records the source review. Source-derived failure mechanisms below are **audit findings to reproduce**, not results of executed tests.

Continue qualifying **existing limma-rust**, with a narrow contract and several concrete upstream corrections before cohort execution. Consider **SeSAMe2's existing C CLI** before any Rust IDAT/preprocessing rewrite. Its R comparisons already exist and should be reused; qualification still must cover public input bytes, annotation versions and the actual production export. Keep independent R references. Do not build a backend framework, a general statistical library or a new array pipeline.

This report extends the [candidate audit](rust-candidate-audit.md), particularly correcting any impression that SeSAMe2 has no R comparisons or that all its test samples are inherently private.

### Source snapshots

| Repository | Inspected source |
|---|---|
| sinmojito/limma-rust | `c569f87a1b5aa97f3499255bee7a1a8b45e200fa`; HEAD rechecked; Cargo 0.1.0; GPL-3.0-or-later |
| zhou-lab/sesame | `f6713747181764e0b7a97b64c3c0d52ab9d82703`; HEAD rechecked; academic/nonprofit research terms plus BSD-2 conditions; commercial use/transfers by inquiry |
| statrs-dev/statrs | tagged `v0.18.0` sources, matching limma-rust dependency |
| faer | official docs for **0.24.0**, matching checked-in limma-rust Cargo.lock; do not silently substitute latest 0.24.4 |
| vigna/CDFLIB-rs | `98476cddbd07ed33a61f5471678f2938674ee167`; Cargo 0.4.4, MIT |
| tla-org/rmathlib | `aa3152b3324e57fc95850289e23af8841145155f`; Cargo 1.1.0, GPL-2.0-or-later; excluded below |

## 1. limma-rust: specific issues before scientific use

### A. Input matching and numeric parsing

The shared [I/O module](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/io.rs) implements two unsafe defaults:

- `align_design` and `align_contrasts` use label matching when all requested labels exist, but silently accept positional matching if names do not match and dimensions happen to match. A sample typo plus a reordered design could therefore attach the wrong case/control covariates. A HashMap also overwrites duplicate source row IDs.
- `parse_cell` maps any unparseable numeric token to NaN, as well as intentional missing tokens. Invalid UTF-8 IDs are converted lossily. Corrupted input may therefore become missing data or altered identifiers rather than an error.

Smallest correction: validate uniqueness and exact required ID membership using the Rust standard library; fail clearly on mismatches; make any positional mode explicit. Reuse the existing `csv` and `anyhow` dependencies for row/column errors. Accept only declared missing tokens and reject malformed numeric text/nonfinite designs. No new validation framework.

Reference fixtures should include reordered correct labels, mismatched equal-length labels, duplicates, missing/unexpected names and malformed values. The current project may enforce the contract before invocation, but shared upstream fixes protect all callers.

### B. Effect standard errors and NaN-aware inference

In [top-table source](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/toptable.rs), `lfc_se` is assigned `stdev_unscaled`. The CSV writer labels this `lfcSE`. An unscaled design SE is not an effect's sampling or moderated SE:

- ordinary coefficient SE = unscaled SE × residual sigma;
- moderated coefficient SE = unscaled SE × sqrt(posterior residual variance).

This is especially consequential for T04 inverse-variance/hierarchical analysis. The downstream schema must explicitly name the desired uncertainty definition and effect units; an M-value contrast is a difference in log methylation odds, not transcript expression fold change. Do not use the advertised `lfcSE` blindly. The existing full fit dump supplies enough ingredients to compute the required quantity in a narrowly specified conversion, or upstream can correct/rename the field.

The same module's BH and result sorting call `partial_cmp(...).unwrap()`. A NaN p-value/statistic can therefore panic. Preserve missing rows and the intended testing family exactly as the chosen R reference; replacing sorting with `total_cmp` alone would hide the scientific missingness decision. No extra statistics crate is needed for this bounded correction.

### C. Missing observations can change design rank

[fit.rs](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/fit.rs) rejects a rank-deficient **full** design, but the per-probe missing/weighted path checks retained observation count rather than retained design rank. With an intercept and case indicator, dropping every case for a probe can leave enough control observations but a non-estimable disease coefficient. The unpivoted solve still proceeds and df is based on the original column count.

A narrow first contract may reject/mask such probes with an explicit reason; complete R partial-estimability support is a larger separate feature. Test zero-weight/missing patterns as well as all-missing probes.

The complete-data fast path also estimates RSS by subtracting two large sums of squares and clamps negative results to zero. Cancellation on almost-perfect fits is a numerical risk to check against explicit residuals and R. The fast path transposes/copies the entire feature matrix. Neither risk is an observed performance or cohort failure here.

### D. Existing comparison scripts are not sufficient acceptance gates

The [upstream dump comparator](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/reference/compare_dumps.R):

- warns, rather than fails, when result row sets differ, then compares their intersection;
- excludes p-value and F-p-value columns from pass/fail;
- can ignore one-sided NaN/NA differences because its final comparisons use `na.rm=TRUE`.

Reuse its reference generation/dump interface but strengthen the existing comparator: exact key sets, duplicate detection, exact missingness/status, distribution-tail checks and downstream BH decisions. A reported upstream PASS is not our qualification.

The [CLI test](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/tests/cli.rs) checks the CLI against the same library, useful for wiring but not an independent statistical oracle; it does not check lfcSE. [CI](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/.github/workflows/ci.yml) runs Windows and stored reference values for default/no-default features. Add only the required Apple ARM64/x86 platform evidence and fresh independent R fixture regeneration, not a new test framework.

### E. CLI capability is narrower than library capability

[CLI source](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/bin/limma.rs) invokes unweighted lmFit and exposes contrasts, robust/trend and TREAT. It does not expose all weighted/block-correlation library functionality. With multiple coefficients and no explicit coefficient, the default can be an overall F test. Freeze a named disease contrast; do not let defaults choose the scientific question.

Start with this CLI only if the frozen design fits its supported contract. Add a small upstream flag for a specifically required library function before writing another executable. Its timing excludes input/output and some surrounding stages; do not present it as whole-workflow speed.

## 2. Exact reuse opportunities, and where simplification would alter behavior

[Cargofile](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/Cargo.toml) already uses ndarray, statrs, anyhow, optional csv/clap/rayon and optional faer. Default faer is enabled only for per-probe solves, without faer's own rayon. Preserve that deliberate avoidance of nested thread pools.

| Existing code | Reusable capability already available | Conditions |
|---|---|---|
| Handwritten economy QR | faer 0.24 `Mat::qr()`, `Qr::compute_thin_Q()`, `thin_R()`, `SolveLstsq::solve_lstsq()` | Full-rank fits preserve OLS method; compare covariance, residuals and rounding, retain feature-gated minimal build |
| Gram-matrix eigen-based rank/SVD | faer `singular_values()` / `thin_svd()`, or column-pivoted QR | Preserve chosen tolerance/rank/estimability policy; mathematical factorization alone does not define R behavior |
| Handwritten symmetric eigensolver | faer `self_adjoint_eigen()` | Account for eigenvalue ordering, eigenvector signs and repeated eigenspaces; judge reconstructed quantities, not raw sign equality |
| Cholesky and triangular-solve plumbing | faer `llt()` and existing solver operations | Return clear non-positive-definite failures; do not silently change the correlation model |
| Ordinary incomplete beta and log beta | statrs `checked_beta_reg(a,b,x)`, `checked_ln_beta(a,b)` | Argument order differs from local `betai(x,a,b)`; preserve boundary/error semantics and tail accuracy |
| Ordinary F survival | statrs `FisherSnedecor::sf()` | Uses direct complementary-beta expression, not `1-cdf`; independent tail grid before replacement |
| Central Student-t survival | statrs `StudentsT::sf()` (already equivalent by symmetry) | Existing `cdf(-x)` is also direct stable tail; replacing is mainly clarity |
| Inverse Student-t survival wrapper | Existing central-t symmetry: negative lower-tail inverse at p | Local `inverse_cdf(1-p)` loses small p by subtraction; qualify boundary/large-df behavior; not necessarily relevant to every initial stage |
| Short sort/median/quantile/BH functions | Standard library and existing ndarray | Preserve R type-7 quantiles, ties, NA handling and family semantics; generic defaults may differ |

Evidence: [faer 0.24 overview](https://docs.rs/faer/0.24.0/faer/), [Qr methods](https://docs.rs/faer/0.24.0/faer/linalg/solvers/struct.Qr.html), [statrs beta v0.18.0](https://github.com/statrs-dev/statrs/blob/v0.18.0/src/function/beta.rs), [F distribution](https://github.com/statrs-dev/statrs/blob/v0.18.0/src/distribution/fisher_snedecor.rs), [Student-t](https://github.com/statrs-dev/statrs/blob/v0.18.0/src/distribution/students_t.rs).

The inspected [custom linalg](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/linalg.rs) economy QR actually constructs full n×n Q before taking its first p columns. Its rank/SVD form AᵀA, squaring the condition number; its Jacobi eigensolver has a fixed sweep cap without explicit convergence failure. These justify examining existing faer reuse, but typical cohorts have small n, so speed benefit still needs measurement. Full Q in the [natural-spline basis](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/splines.rs) has a real purpose and must not simply become thin Q. [GLS](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/glsseries.rs) uses the Cholesky/triangular helpers, so changing them requires those caller checks too.

### Keep method-specific code unless a demonstrated equivalent replaces it

[Special functions](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/special.rs) contain cancellation-resistant log incomplete beta/gamma and normal-tail calculations. statrs 0.18 has ordinary incomplete functions, but the inspected gamma module lacks trigamma/tetragamma and log-regularized-gamma APIs. Substituting `ln(cdf)` loses deep tails; `ln(x)-digamma(x)` loses the stable logmdigamma difference. Do not remove these solely to shorten code.

The [Nelder–Mead port](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/optim.rs) intentionally mirrors R initialization, control constants and failure codes for genas. Generic argmin is not a proven drop-in; genas is not required for the first array analysis. The same caution applies to eBayes' robust winsorization, unequal-df fitting, LOESS, Brent routines and RNG-dependent methods. Replacing all numerical code would expand the scientific task.

### Additional Rust numerical candidates

**CDFLIB-rs/cdflib 0.4.4 (MIT)** is worth an optional focused comparison if existing special functions fail a relevant boundary. It supplies paired lower/upper tails, incomplete gamma/beta and distribution APIs, with committed Fortran-generated reference fixtures and an Apple-silicon regeneration CI lane. Its ordinary CDF interface is not a universal log-probability interface; inverse/search tolerances differ from exact R conventions. Do not auto-add it or replace all statrs. Primary [README](https://github.com/vigna/CDFLIB-rs/blob/98476cddbd07ed33a61f5471678f2938674ee167/README.md), [traits](https://github.com/vigna/CDFLIB-rs/blob/98476cddbd07ed33a61f5471678f2938674ee167/src/traits.rs), [CI](https://github.com/vigna/CDFLIB-rs/blob/98476cddbd07ed33a61f5471678f2938674ee167/.github/workflows/ci.yml). Upstream reported accuracy, not independently rerun.

**Do not adopt rmathlib 1.1.0.** Although it exposes R-style tail/log-probability functions, [issue 38](https://github.com/tla-org/rmathlib/issues/38) reports materially invalid pgamma probabilities and the maintainer says the project was abandoned. Closed issue is not evidence of a numerical fix: inspected HEAD remains 1.1.0. This is different from `r_mathlib`, a C-backed interface. We did not reproduce the report.

## 3. SeSAMe2: existing comparisons, public corpus and remaining issues

### Naming matters

Welsh et al. (2023), [doi:10.1186/s13148-023-01459-z](https://doi.org/10.1186/s13148-023-01459-z), called an R SeSAMe workflow with additional QC/pOOBAH masking **SeSAMe 2**. That is not the current standalone C SeSAMe2 binary. The paper compares normalization strategies, not C-versus-R implementation fidelity. Its individual-level data are available on request; the linked Dryad distributions are not a substitute for an openly downloadable raw replicate corpus.

### Existing R validation should be credited and reused

The native C project already has per-step R comparisons, binary float64 raw-beta checks, QCDPB checks, QC, DML and other numerical drivers. [run_golden.sh](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/run_golden.sh) compares decoded IDAT address/mean/SD/bead-count output to R and additionally scans sesameData extdata and an external lab directory. The complete contents/checksums of that directory are not enumerated in this repository.

[run_qcdpb.sh](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/run_qcdpb.sh) names one HM450, EPIC, EPICv2 and MSA sample. [compare_qcdpb.R](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/compare_qcdpb.R) records older annotation-specific mismatches: HM450 28 one-sided NAs, EPIC 92, EPICv2 0, MSA 20, plus exact named large-difference probe sets. Its newer-mask branch records an upstream private-install measurement around 1e-15 with a 1e-12 ceiling and no NA mismatches. This is version-conditional evidence, not universal equality. It compares intersecting probe IDs; independent admission must also require the intended full universe.

[NUMERICS](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/NUMERICS.md) describes arithmetic boundary changes, zero-MAD fallback/status, channel/address/mask lineage and tiny quantile rounding differences. [DIVERGENCES](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/DIVERGENCES.md) explains probe-specific annotation differences and records that the R negative-control bug was fixed in sesame 1.31.5. Do not perpetuate an old resolved failure as current.

The checked-in [truth provenance](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/truth/PROVENANCE.tsv) records R4.6.0, sesame1.31.5, sesameData1.29.10, BiocVersion3.23.1, annotationv8.5, CLI2.3.1, YAME1.61. The tree has a frozen EPICv2 VCF truth file, not a complete frozen QCDPB corpus. [Truth rules](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/truth/README.md) distinguish R-sourced rows from explicitly justified C-sourced divergences.

### Publicly traceable samples

| Driver sample | Public primary-source mapping | What is still unknown |
|---|---|---|
| HM450 `3999492009_R01C01` | Original sesame [official vignette](https://zhou-lab.github.io/sesame-docs/v1.18/inferences.html) documents both files through `sesameAnno_download` Test keys | Current direct endpoint/byte success and lab-input hash not tested |
| EPIC `GSM2995280_201868590258_R01C01` | [GSM2995280](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2995280), public blood sample in GSE110530/GSE110555; both ~7MB compressed IDATs listed | No download or hash comparison here |
| EPICv2 `206909630040_R03C01` | [GSE228820](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE228820), GSM7139627 GM12878 replicate2, raw IDAT archive listed | Exact lab versus released bytes and release de-identification need checking |
| EPICv2 VCF `206909630042_R08C01` | Same GSE228820, GSM7139626 GM12878 replicate1 | Same limitation; VCF particularly sensitive to de-identification |
| MSA `207760740030_R01C03` | [GSM8265587](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM8265587), GSE264438, NA12878 DNA, paired IDATs listed | GEO explicitly says IDATs de-identified to mask SNP readings; cannot assume identical lab bytes |

Public-index evidence establishes available candidate inputs, not a completed access/rights/ethics check or permission to infer identity. Public downloads require no access application in those records; no files were fetched here. Some direct sample-page opens hit temporary NCBI access errors, while primary indexed sample/series records supplied the mappings. Use exact downloaded checksums when execution is authorized.

[Public CI](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/.github/workflows/conda-build.yml) explicitly lacks the external IDAT directory, populated store and R oracle, so real-IDAT comparisons skip. That does **not** mean all sample identities are private or that CI performs zero numerical checks. [Synthetic HM27 integration](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/run_hm27.py) runs offline from generated IDATs and a small store and is included in make test. It explicitly is not an R numerical comparison.

### Production export is a separate precision gate

[Raw-beta oracle](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/compare_betas.R) reads a test helper's binary float64 output. Production [cgwrite.c](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/src/cgwrite.c) casts format-4 beta/p-value/total-intensity output to float32. [describe.c](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/src/describe.c) prints these values with six significant digits; that is not a general float32 round-trip representation despite the nearby full-precision comment. M/U storage also rounds corrected signals to integers.

Therefore an internal raw-beta agreement claim does not prove IDAT→production export→M-value→limma equivalence. Quantify both float32 and textual rounding, especially near beta0/1 where logit amplifies changes. The inspected production CLI did not expose the test helper's f64 mode. If necessary, the smallest improvement is an upstream supported high-precision export/precision flag and round-trip fixture. Do not build a second IDAT processor or new binary storage format. The YAME ordering and .idx files remain mandatory provenance, or convert to the existing agreed labelled interchange at the boundary.

### Licence and route decision

[Licence](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/LICENSE) allows academic/nonprofit institutional research under stated BSD-2 conditions and directs commercial uses/transfers to inquiry. It is not an unrestricted BSD permission. Confirm the actual project's institutional/use context; this source audit is not a legal or HREC/IRB determination.

Use the existing C CLI as a process stage after qualification. It already covers manifest-dependent IDAT processing, QCDPB, masks and QC. Its ordinary DML regression is not limma empirical-Bayes moderation. If the study specifies minfi functional normalization, SeSAMe is a methodological change requiring separate evaluation rather than implementation substitution.

Extending Cyanea's Rust IDAT reader would still leave manifest/channel semantics, masks, control probes, noob, dye correction, QC, numerical edge cases and export qualification. Prior audit already found non-equivalent Cyanea limma/SWAN routines. A standalone reader fix is only justified by a real Rust-only consumer; no such requirement exists for the planned file-stage workflow.

## 4. Bounded qualification sequence

### Bounded Python alternative check

[FoxoTech/methylprep](https://github.com/FoxoTech/methylprep/blob/eb1d2dab0681734dff09cdc8aa63ca0a097a54e1/README.md), current HEAD `eb1d2dab0681734dff09cdc8aa63ca0a097a54e1`, is a real MIT Python CLI/API for IDAT, noob, pOOBAH, dye correction, masking and beta/M outputs. [methylcheck](https://github.com/FoxoTech/methylcheck) supplies processed-data QC, reports and plots. These can remove custom work when a needed capability is absent elsewhere. However, methylprep's documented R benchmark versions are old (sesame1.10.4/minfi1.38), and its [release history](https://github.com/FoxoTech/methylprep/blob/eb1d2dab0681734dff09cdc8aa63ca0a097a54e1/docs/release-history.md) records historical intermediate-step disagreement and only within-1% beta agreement in v1.5.0/1.5.1. That history is not a measurement of current parity. It also contradicts the README's 27K claim: support was removed in v1.5.6. v1.7.0 adds Parquet output, useful for the agreed interchange without a custom exporter. For a current same-method QCDPB route, first qualify SeSAMe2/R SeSAMe with pinned current annotations; retain methylprep as a named alternative if licences, platform support or output needs make it preferable. No case for mandatory Python orchestration, Mojo kernels or rewriting these packages. This was documentation inspection, not a Python numerical audit.

### Qualification steps

1. **Interface first:** strict IDs/missing tokens; effect units and correct uncertainty; named contrast; finite/rank contract; safe missingness in BH and output. Reproduce tiny failure fixtures and contribute minimal shared upstream fixes if subsequently authorized.
2. **Independent comparator:** extend existing scripts to fail on key/status/missingness differences, gate p tails and FDR, preserve complete tested universe. Separate input/export rounding from compute differences.
3. **Numerical internals:** try already included faer only where it removes handwritten work and improves a demonstrated hazard. Benchmark only afterward. Keep method-specific robust/log-tail behavior unless a proven equivalent replaces it.
4. **Public assay replay:** admit suitable public 450K/EPIC fixtures and cohorts through T01, freeze files/manifests/masks/reference versions. Compare raw decoding, per-step QC and betas, actual production exports, then a fixed M-value differential model. Reuse exact public core SeSAMe samples where bytes can be matched; do not treat the whole lab directory as reproduced.
5. **Cohort/consumer checks:** T02 eligible Kabuki datasets such as GSE97362/GSE116300/GSE218186 only after cohort/rights admission. Compare coefficients, ordinary/moderated SE as chosen, variance components, df, t/F, log-tail probabilities, BH and threshold-adjacent decisions. Independent participants are biological replication; same-input engine comparisons answer a different question.
6. **Hardware and promotion:** actual M1 Max and specified x86 OS/hardware, float64 CPU reference, matched threads, whole-stage memory/time and failure behavior. No speed claim from source size or upstream microbenchmarks.
7. **Stop at the needed subset:** no entire limma/Cyanea rewrite, no compulsory CDFLIB dependency, no blanket log-tail simplification. If a bounded candidate fails scientific qualification, retain the known reference stage and proceed with the clinical study.

Preserve **global** eBayes moderation and the intended multiple-testing family across storage chunks. Neither dataset expansion nor Parquet partitions justify independent per-chunk priors/FDR. Separate software-validation claims from biological novelty, and retain existing N0–N3 publication checks.

## Addendum: focused statrs/faer version check

The reuse table intentionally describes the dependencies locked by the inspected limma-rust revision. Newer releases warrant a **controlled comparison**, not automatic version selection merely because another candidate such as rsfgsea uses them.

- **statrs 0.19.0/0.19.1:** the tagged [changelog](https://github.com/statrs-dev/statrs/blob/v0.19.1/CHANGELOG.md) adds non-panicking inverse-CDF access, safeguards Gamma inverse quantiles for shape below one, and records later distribution-boundary, tiny-x Beta survival and NaN order-statistic fixes. The [Gamma source](https://github.com/statrs-dev/statrs/blob/v0.19.1/src/distribution/gamma.rs) uses bracketed Newton/bisection; [ChiSquared](https://github.com/statrs-dev/statrs/blob/v0.19.1/src/distribution/chi_squared.rs) delegates inverse CDF to Gamma, so this is relevant to low-df quantile fixtures. However, [Cargo](https://github.com/statrs-dev/statrs/blob/v0.19.1/Cargo.toml) requires Rust1.89, above limma-rust's declared1.85, and changes edition/dependency versions. The inspected [gamma API](https://github.com/statrs-dev/statrs/blob/v0.19.1/src/function/gamma.rs) still does not supply trigamma/tetragamma or log-regularized incomplete gamma. Its fixes do not repair limma's own NaN/BH sorting, input matching or SE field. Qualify only used functions and feature sets, preserve tail/NA contracts, and document toolchain changes before any future upgrade.
- **faer 0.24.0 to 0.24.4:** [release-source Cargo](https://github.com/sarah-quinones/faer-rs/blob/0539947ffb757a739d7e703a7d2fa0c792a909c1/faer/Cargo.toml) identifies0.24.4. Intervening [commit645768f](https://github.com/sarah-quinones/faer-rs/commit/645768f3f2b62f3c822ff8151aaa8900b07ff197) changes unpivoted QR rank-revealing behavior and Jacobi transpose/adjoint conventions. This is a concrete reason to compare supported full-rank, nearly singular and degenerate fixtures before choosing the execution pin. It does not establish improved cohort outcomes, speed or automatic R rank equivalence; the commit also relaxes rank-test expectations. The repository's main-branch changelog additionally contains later strided-view/iterative-solver fixes; do not claim those are in0.24.4. The current upstream source location is [Codeberg](https://codeberg.org/sarah-quinones/faer), with the inspected GitHub mirror providing commit evidence.

No numerical comparison or dependency update was performed for this addendum.

