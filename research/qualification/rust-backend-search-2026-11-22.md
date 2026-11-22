# Rust methylation backend refresh — 22 November 2026

## Decision for the current implementation

Apply Ponytail full: **use the owner's MassDynamics-derived core as the first Rust numerical candidate; retain sinmojito as an optional, separately qualified comparator and capability source. Keep the selected R implementation as the independent reference.** Do not install both Rust implementations into every production analysis or merge them wholesale. No complete native Rust SeSAMe-equivalent preprocessing pipeline was identified in the bounded searches below, but multiple partial Rust IDAT projects exist.

This lane performed read-only source/API research. It did not execute numerical tests, benchmark libraries, implement a parser, contact maintainers or modify either repository. The owner's previously recorded 104 passing debug/release tests remain prior evidence, not a fresh run by this lane.

## 1. Which limma implementation is better for this project?

| Aspect | MassDynamics / owner fork | sinmojito |
|---|---|---|
| Exact source | Upstream [ba41fb6](https://github.com/MassDynamics/limma-rust/tree/ba41fb6bbf6e3f2524bd44f5be017c827d5c4aaa), 14 Nov 2026; owner [843d868](https://github.com/edithatogo/limma-rust/tree/843d8685affb3833fbaf5f3e66ade6cbea6dc8f6), 22 Nov | [c569f87](https://github.com/sinmojito/limma-rust/tree/c569f87a1b5aa97f3499255bee7a1a8b45e200fa), 31 May 2026 |
| Package / publication | `limma-core` 0.1.0; exact crates.io endpoint returned 404 | `limma-rust` 0.1.0 published; imported as `limma`; CLI also named `limma` |
| Existing scope | Least-squares/missingness, contrasts, robust/trended eBayes, block correlation/GLS, topTable/BH/F/CI. No production input parser or CLI | Substantially broader source surface: weighted fits, TREAT, voom/vooma/array weights, normalization, camera/fry/rotation gene-set methods, differential splicing, library plus CLI |
| Runtime dependencies | thiserror only; R-tail and LINPACK routines retained intentionally | ndarray, statrs, anyhow; optional CSV/clap/rayon/faer, enabled by default features as specified |
| Relevant numerical semantics | Per-feature missingness uses retained rank/pivots; CI uses posterior variance scale; explicit nonfinite comparison; current tests gate p, F-p, BH and CIs | Full design rejects rank deficiency; per-feature missingness/weights path assumes retained full rank. The comparator below omits p/F-p from failure gates |
| Consumer gaps | Numeric API is positional; needs an identity-checked consumer contract and reproducible independent R regeneration | Present CLI is convenient but strict identity/error/uncertainty contracts need repairs before our scientific consumer |
| Validation interpretation | Existing cloud replay passed 104 tests against mixed synthetic/proteomics references. Not fresh R generation, methylation qualification or official personal-device evidence | Existing upstream validation/benchmark report and stored-reference CI; no fresh execution in this lane. Broader claimed parity does not waive method-specific checks |
| Licence | GPL-3.0-or-later; preserve R-derived attribution | GPL-3.0-or-later; preserve R-derived attribution |
| Initial role | Primary candidate for the supported methylation linear-model stage | Optional cross-check or named missing method; never a second mandatory runtime |

Public metadata/API refresh found all six previously audited main revisions unchanged. Local `git diff ba41fb6...843d868 -- src tests Cargo.lock` produced no differences; the owner's new work is context/configuration, not a new numerical algorithm. The fork's existing [source audit](https://github.com/edithatogo/limma-rust/blob/843d8685affb3833fbaf5f3e66ade6cbea6dc8f6/conductor/evidence/source-audit-2026-11-22.md) remains applicable.

### Current sinmojito source findings, rechecked

- [io.rs](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/io.rs): malformed nonempty numeric cells become NaN; failed name matching with equal-sized matrices falls back to position; duplicate names are not rejected before the HashMap alignment. Repairing CSV quoting in its latest commit did not resolve these different issues.
- [toptable.rs](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/toptable.rs): `lfc_se` is assigned `stdev_unscaled` and exported as `lfcSE`. That quantity is not a fitted/moderated standard error until multiplied by its appropriate residual/posterior variance scale.
- [fit.rs](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/src/fit.rs): complete design rank checks exist; reduced per-feature designs still need rank-sensitive qualification.
- [compare_dumps.R](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/reference/compare_dumps.R): different row sets merely warn and are intersected; p/F-p are explicitly excluded from failure gating; `na.rm=TRUE` can hide one-sided missing comparisons. This describes this particular comparator, not a claim that no other tests exist.
- [CI](https://github.com/sinmojito/limma-rust/blob/c569f87a1b5aa97f3499255bee7a1a8b45e200fa/.github/workflows/ci.yml) runs stored references on Windows for default/minimal feature sets and an MSRV build. It does not freshly generate R expectations.

These are source observations, not newly demonstrated failing executions. They are not defects in the owner's different implementation.

### A useful new upstream branch to reuse

MassDynamics `benchmark` at [df2c50b](https://github.com/MassDynamics/limma-rust/tree/df2c50b5473de823dcfcc70c0ce851d3585559fc) is one commit ahead of main and changes only the benchmark example, scripts and reports. `block-correlation` and `tests-validation` are behind main. The [benchmark report](https://github.com/MassDynamics/limma-rust/blob/df2c50b5473de823dcfcc70c0ce851d3585559fc/tests-validation/report/benchmark.md) describes an M5 Pro, synthetic 24-sample data, in-memory single-thread stages and separate whole-process/added RSS. Reuse that harness if a performance decision becomes necessary; do not invent a new benchmark framework or transfer its numbers to an M1 Max, Windows/NVIDIA or 450K/EPIC workloads.

### Using both without losing independence

For one frozen matrix/design/contrast, obtain reference outputs directly from pinned R limma and compare each candidate independently. Require exact IDs/order, support/domain agreement, matching missingness, coefficients, rank/df, ordinary and moderated uncertainty, p/F-p/BH/CI, and downstream decision stability. Two derivative ports agreeing is useful triangulation, not an independent scientific oracle or a majority vote. Evaluate sinmojito only when a named gap (for example TREAT or a particular weighting method) is required. Array probe-bias enrichment remains a separate scientific contract; generic camera/fgsea capability does not establish missMethyl equivalence.

## 2. Existing Rust array/IDAT work: expanded search

| Project and pinned revision | Actual useful scope | Why it is not presently a SeSAMe replacement |
|---|---|---|
| [a-xavier/illumina_array_reader, c6a19f8](https://github.com/a-xavier/illumina_array_reader/tree/c6a19f8062a66790e48add1f3197e91edd0edc91), Oct 2023 | Paired IDAT/gzip reader; address, mean, SD, bead count; Polars 0.33.2 | Existing source concerns remain: XOR in translated variable-length decoding, narrow accumulator, unchecked/unwrap paths. MIT declaration conflicts with copied-routine attribution to GPL-2 illuminaio and needs provenance clarification; not a finding of infringement |
| [snalty/idat-rs, 42af9c5](https://github.com/snalty/idat-rs/tree/42af9c598311010eec5dbb0fa0079200fd14b8d1), June 2024 | IDAT field-directory/iterator prototype | No LICENSE file or Cargo licence declaration found; only integer iterator arm implemented, other types `todo!`; iterator increments twice; field access private; test depends on an author's absolute local file. Not ready to adopt |
| [xo-cally GPU genotyping, eac96fa](https://github.com/xo-cally/GPU-ACCELERATED-CLUSTERING-FOR-HIGH-DENSITY-GENOTYPING-DATA/tree/eac96fa8afecbf0706ec48a833e4b6bcbc702a0f), Nov 2025 | IDAT/gzip address and mean reader feeding SNP genotyping | No declared licence found; no SD/bead-count extraction or methylation manifest/channel/QCDPB implementation. GPU genotyping is a different task |
| [michael092749/SNP-genotyping, c1dcce7](https://github.com/michael092749/SNP-genotyping/tree/c1dcce7e1aa8763963acce273904617395412d70), Sept 2024 | IDAT address/mean extraction within MPI/SNP normalization code | No declared licence found; project-specific shared state and sample parsing; required-field HashMap indexing can panic; barcode is read as u32. No SeSAMe preprocessing |
| [Cyanea Labs, 5d39b14](https://github.com/cyanea-bio/labs/tree/5d39b14357064efcfb918b1192e2f26d28b81ece), Nov 2026 | Apache-2.0 IDAT parser with addresses/means/beads/SD and metadata, separately accessible in `cyanea-io` | Best newly clarified **bounded reuse/fix candidate**, still unqualified. Source parser depends on count field preceding arrays, decodes only one string-length byte, reads two RunInfo strings rather than five, silently skips invalid offsets, and does not require equal lengths of all needed arrays |
| [selkamand/probepicker, f7a1e62](https://github.com/selkamand/probepicker/tree/f7a1e6214fb3d4cf2caa1ad7d33625b762fb4033), July 2024 | Streaming selection of variable probes from existing beta TSV/gzip | No explicit licence found; no IDAT preprocessing. Existing Polars/table operations may already cover the actual consumer |

The relevant Cyanea parser is [cyanea-io/src/microarray.rs](https://github.com/cyanea-bio/labs/blob/5d39b14357064efcfb918b1192e2f26d28b81ece/cyanea-io/src/microarray.rs). Its [Cargo features](https://github.com/cyanea-bio/labs/blob/5d39b14357064efcfb918b1192e2f26d28b81ece/cyanea-io/Cargo.toml) allow default CSV features to be disabled; the parser is exposed independently of optional omics/statistics modules. Thus it is inappropriate to dismiss all of Cyanea because its statistical routines differ. Conversely, the existing `limma_diff_expr` prior-df heuristic and beta-quantile `swan_normalize` in [cyanea-omics](https://github.com/cyanea-bio/labs/blob/5d39b14357064efcfb918b1192e2f26d28b81ece/cyanea-omics/src/microarray.rs) remain substantive differences, not small packaging gaps.

For parser conformance, [illuminaio's pinned reader](https://github.com/HenrikBengtsson/illuminaio/blob/ee4950a9d30d6687f394eae61c3c552554678404/R/readIDAT_nonenc.R) documents variable-length 7-bit string lengths, 5-field RunInfo and byte-sized bead counts. It is GPL-2, so distinguish behavioral reference tests from copying GPL source into a differently licensed project. No candidate was executed in this lane.

Additional sequencing-specific Rust candidates found include [rsomics-methyl, 4a937bc](https://github.com/omics-rust/rsomics-methyl/tree/4a937bc57994a8497238bfba38a74c73c97e80dc) (MethylDackel-compatible extraction/QC), Bismark's current Rust suite, Metheor, bsxplorer2 and fast_dss. These are candidates for later sequencing inputs, not IDAT/array-method substitutions.

## 3. SeSAMe-rust versus existing SeSAMe2

[SeSAMe2 C, f671374](https://github.com/zhou-lab/sesame/tree/f6713747181764e0b7a97b64c3c0d52ab9d82703) remains the lowest-custom-code non-R full workflow candidate, subject to existing source-specific qualifications. Its NUMERICS, DIVERGENCES and comparison scripts already compare with R. A new claim that this comparison has never been performed would be wrong. Production exports, masks/manifests and the exact intended analysis must still be tested; its unmoderated differential model is not the same as limma.

Its only listed public fork, [njspix/sesame, 70486b7](https://github.com/njspix/sesame/tree/70486b7ab34c5113c2e602d6125cc84da16371f7), has a C source tree and no Rust source in the returned complete recursive tree. That does not prove absence of private or unindexed development elsewhere.

Licences must be assessed by implementation: current [R SeSAMe DESCRIPTION, 8b1fcfa](https://github.com/zwdzwd/sesame/blob/8b1fcfaed89b28e0def8b031a81611a0a770053c/DESCRIPTION) declares MIT + file LICENSE; the [C implementation licence](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/LICENSE) explicitly limits its stated availability to academic/nonprofit research and directs commercial use/transfers to inquiry. Neither label settles licences of incorporated dependency code, annotations or human datasets. A future port needs source-by-source attribution; translating or wrapping code does not erase terms.

### Smallest implementable next increment

1. **Current priority: limma reference/consumer admission.** Fix shared fixture identity validation, define the supported numeric consumer and complete the reproducible R-reference recipe. This benefits the first disease analysis immediately. Do not replace custom kernels before a demonstrated need.
2. **Optional native reader round:** build a small conformance fixture set against Cyanea's existing parser: directory permutations, 127/128/255/256-byte strings, five-field RunInfo, missing/duplicate mandatory fields, truncation/overflow, pair/address consistency. First reproduce source concerns; then make bounded changes in the existing parser if the resulting dependency and licence are suitable. No reason yet for a separate all-purpose Rust reader.
3. **Public-data round:** independently compare integer fields and metadata from permitted 450K and EPIC IDATs against pinned readers, retaining exact probe/address/channel identity and source hashes. Qualify real gzip handling. This is reader acceptance only, not a claim of methylation-method parity.
4. **SeSAMe core only after that consumer requires it:** pin one supported platform pair, exact masks and QCDPB settings; add manifest mapping/channel handling, detection, background and dye correction one independently testable step at a time. Preserve a qualified C/R route while this optional work proceeds. Avoid reimplementing visualization, annotations, CNV, clocks or every SeSAMe helper.
5. **Official local-runner round:** record actual Mac/Windows builds and conformance receipts using the official GitHub Actions runner. Configuration or cloud success cannot substitute for execution on these devices.

Use agent execution rounds with a fixed first-pass wall-clock budget (for example 30 agent-minutes to reproduce and classify parser failures), then revise estimates using observed compile/test/download times. Record start/end/resource use, outcome and the exact remaining blocker. No person-week/month estimate or unsupported promise is needed. Reader/native-port work is infrastructure that can be bundled into the clinical/array-transfer paper; it does not need a standalone software paper.

## 4. Search coverage and limitations

The machine-readable report contains exact queries and returned repository/file names. Supplementary receipts retain current repository heads, crates registry results and Europe PMC requests.

- Ten GitHub repository queries included `idat language:Rust`, `methylation language:Rust`, `methylation array language:Rust`, `illumina language:Rust`, `sesame-rust`, `sesame-rs methylation`, and `sesame methylation fork:true`. All requested page 1 / 100 results; the connector does not report total/pagination links.
- GitHub code queries included `IlluminaID language:Rust`, `read_idat language:Rust`, `Infinium language:Rust`, `pOOBAH language:Rust`, `InfiniumI language:Rust` and `noob methylation language:Rust`. Indexed/default-branch scope matters. The broad IDAT query returned millions of irrelevant files and is explicitly excluded as absence evidence.
- Main branches, branch lists and public forks of the prior main candidates were checked. Newly identified small readers each reported zero forks and only main. MassDynamics has the useful benchmark-only branch noted above.
- crates.io searches: idat, illumina, methylation, sesame, minfi (100 results maximum; idat was truncated at 100 of 732 mostly image-related fuzzy matches). Exact idat-rs / illumina_array_reader / limma-core endpoints returned 404; limma-rust 0.1.0 and cyanea-io 0.1.1 returned published packages.
- Europe PMC API queries `TITLE_ABS:(sesame AND rust AND methylation)` and `TITLE_ABS:(IDAT AND rust)` returned zero. `TITLE_ABS:(limma-rust)` returned one irrelevant wheat stem-rust article because of tokenization. These are bounded negatives, not a novelty certificate.
- Two web search systems were used; the second was necessary because routine search produced substantial plant/rust-author noise. Relevant primary sources included the official SeSAMe/R/C repositories, Cyanea docs, library source and the Metheor article.
- Public metadata may change. No assertion covers private projects, unindexed branches, unpublished work, every registry match or every paper. Rerun the specific discovery queries immediately before launching a full port.

**Ponytail verdict:** approve the existing owner-fork route, strict interface/oracle work and a conditional Cyanea parser-conformance experiment. Approve sinmojito as optional evidence, not a dependency for every run. Defer a full SeSAMe-rust project until its deployment/scientific need is concrete, and reuse upstream tests/benchmarks before creating new infrastructure.

