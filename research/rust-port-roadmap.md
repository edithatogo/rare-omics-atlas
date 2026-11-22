# Rust port and small-extension roadmap

**Decision date: 22 November 2026.** Prefer **Rust > Julia > Python > R** among implementations that meet the scientific contract. First qualify existing code and make bounded additions that remove an actual obstacle. A full SeSAMe-rust implementation is feasible in principle, but it is a separate, conditional project and **is not a dependency of P1**, the initial Kabuki clinical replication/transfer paper.

This document refines [the candidate audit](rust-candidate-audit.md) and [the preprocessing audit](methylation-backend-audit.md). Their earlier `sinmojito/limma-rust` findings concern a different implementation from the user's **MassDynamics-derived fork**. For that fork, the [current source audit](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/source-audit-2026-11-22.md) and LM tracks are authoritative. Track links refer to the prepared publication paths; this document alone is not evidence of a completed remote publication.

Evidence here is source inspection and the separately recorded limma cloud reference replay. No IDAT parser, SeSAMe2 or new Rust preprocessing pipeline was built, run or benchmarked for this roadmap. The agent-batch sequence below is a plan, not a measured completion-time forecast.

## 1. Ordered work and its effect on the first paper

The dependencies are scientific and operational: source eligibility, reference outputs, a defined consumer and then implementation changes. Optional ports do not become prerequisites merely because they appear earlier in a numbered list.

| Stage / candidate | Bounded work needed | Acceptance before use | Dependency of P1? |
|---|---|---|---|
| **A. Source and method identity** | Pin actual repositories, software/annotation versions, supported methods, input rights and the reference procedure. Separate historical upstream evidence from this project's results | Source-bound records; full input/probe/sample identity; eligible intended use; unresolved conditions remain explicit | **Yes**, for the methods and data actually used; no new software required |
| **B. Existing limma-core reference and consumer boundary** | Reuse its tests; make a small R generator independently runnable; share strict fixture-name checks; specify numerical input/output and add only missing validation/export | Existing and fresh independent references, moderated SE/CI consistency, rank/missingness/errors, full feature/FDR universe and consumer round trip | **No Rust dependency.** These gates apply if Rust supplies P1 estimates; the qualified R route can proceed |
| **C. Existing SeSAMe2 CLI qualification** | Reuse its R drivers, exact public fixtures and versioned masks; assess the actual production export. Add a supported precision option only if the consumer needs it | Full intended probe universe and per-step results, missingness/QC, export→M-value→fixed-model checks and relevant device receipt | **No.** Conditional preprocessing alternative; retain the specified reference method |
| **D. Existing data/ontology interfaces** | Preserve complete annotations; use existing Parquet/Arrow writers and, if selected, methylprep's documented Parquet export. Avoid a duplicate wrapper/exporter | IDs, types, nulls, units and provenance round-trip; negation/frequency retained even if a similarity library cannot use them | The **data contract** is required where used; a new library or wrapper is not |
| **E. Small Rust IDAT reader** | Resolve provenance and reproduce parser findings first; then bounded length/offset checks, errors, channel handling and reference fixtures | Decoded address/mean/SD/bead-count agreement, malformed-input behaviour, exact supported platforms and licence decision | **No**; activate only for a real native consumer not served by a qualified reader/CLI |
| **F. Narrow SeSAMe-rust core** | Implement only a selected, fixed preprocessing procedure and platforms after a feasibility decision | Independent per-step and end-to-end references, actual output interface, public-cohort replay and target-device qualification | **No**; conditional later work |
| **G. DMR or probe-aware enrichment implementation** | First demonstrate a required method gap that an existing qualified package cannot reasonably fill | A complete method-specific oracle, bias/null checks, annotation/background semantics and downstream agreement | **No Rust dependency.** Retain the selected specialist reference; no generic substitute |

**Recommended next engineering work:** build the defined production consumer on the completed limma fresh-reference and fixture-hygiene increments; qualify SeSAMe2 only if it solves the selected preprocessing need; preserve annotations and reuse existing interchange. Do not repeat completed LM01a/LM02a work or start several numerical replacements at once. [E0 → E2 → E3 remains the clinical sequence](experiment-publication-plan.md), with backend/platform comparisons normally supporting that paper.

## 2. limma-rust: extend the actual fork, not an assumed implementation

The user's [fork](https://github.com/edithatogo/limma-rust) is based on [MassDynamics source at ba41fb6](https://github.com/edithatogo/limma-rust/tree/ba41fb6bbf6e3f2524bd44f5be017c827d5c4aaa), package `limma-core`, GPL-3.0-or-later. It has no production CSV parser, no field called `lfcSE`, and no existing faer/statrs dependency. Its rank-aware missingness path, nonfinite comparator, p/F-p/BH/CI checks and R-compatible numerical routines already exist. Old defects or dependency suggestions from the other implementation must not be imported as this fork's work list.

A preliminary [cloud debug replay](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/cloud-corpus-replay-2026-11-22.json) passed **104 tests** with Rust 1.95.0 against the committed mixed synthetic/proteomics references. It is not fresh R execution, a user-device official-runner result or methylation validation.

Subsequent bounded increments are completed: [LM01a / PR #3](https://github.com/edithatogo/limma-rust/pull/3) generated an independent public synthetic R reference, with 30,840 comparisons and 110 passing tests per full suite; [LM02a / PR #4](https://github.com/edithatogo/limma-rust/pull/4) adds shared identifier hygiene and strict named alignment in the four fresh cases, with 113 passing tests per suite. Both are reviewed and archived. Seven historical positional cases remain unqualified for named sample identity. Production consumer, official-device and methylation acceptance remain open.

| Fork work | What to do | Why this is smaller than a port |
|---|---|---|
| [LM01: reproducible baseline](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm01_baseline_20261122/spec.md) | LM01a's public pinned R generator, synthetic references and supported error cases are complete. Remaining actual-device evidence and any separately required broader reference domain stay open | Reuse the completed generator and corpus; do not create a second reference framework |
| [LM02: consumer contract](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm02_consumer_20261122/spec.md) | LM02a's shared reader hygiene/fresh named checks are complete. Next define the production caller's ordered sample/feature/design/contrast contract, input/error domains and required existing quantities; keep the historical positional gap explicit | No new dataframe engine, generic backend abstraction or statistical algorithm is required |
| [LM03: methylation admission](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm03_methylation_20261122/spec.md) | Hold the processed M matrix, design, contrasts and feature universe fixed; compare effects, actual SE, df, variances, tails/FDR and missingness with an independent reference | Isolates the inference backend from preprocessing changes |
| [LM04: conditional dependencies](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm04_dependencies_20261122/spec.md) | Consider one replacement only for an observed maintenance problem or measured resource need; qualify all callers | Custom R-compatible code is not automatically redundant |
| [LM05: conditional extensions](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks/lm05_extensions_20261122/spec.md) | Reuse or add one capability demanded by a named consumer | Weighted fitting, TREAT and camera require distinct method work; they are not routine interface additions |

Moderated standard error is already obtainable from `sqrt(s2_post) * stdev_unscaled`. Preserve the distinction from unscaled design uncertainty, and label M-value effects as differences in log methylation odds. Keep empirical-Bayes moderation and BH families global to the prespecified contrast; independently fitting them per Parquet chunk changes the method.

A generic QR library may use different pivot/rank rules from R's limited-pivot LINPACK path. Passing fitted-value tests alone does not establish equivalent non-estimable coefficients. Retain the existing algorithms until a bounded alternative passes the actual caller contract.

## 3. SeSAMe-rust: potential benefits, existing alternatives and realistic scope

### Use the existing C implementation first where suitable

The [native C SeSAMe2](https://github.com/zhou-lab/sesame/tree/f6713747181764e0b7a97b64c3c0d52ab9d82703) already supplies IDAT processing and method-specific comparison machinery. [Its golden driver](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/run_golden.sh), [QCDPB comparison](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/compare_qcdpb.R), NUMERICS and DIVERGENCES should be reused. That is existing upstream R comparison evidence, not proof this project's complete production route has passed.

There is a specific, bounded question before any rewrite. The inspected [production writer](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/src/cgwrite.c) uses float32 for the relevant .cg outputs, and [text output](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/src/describe.c) uses six significant digits. The test helper's float64 result does not prove that production export preserves the downstream measurement. Evaluate the real export and beta-to-M conversion, particularly near beta 0/1, with named clipping/missingness rules. If it fails the prespecified consumer contract, a supported high-precision export or precision option plus a round-trip fixture is a smaller upstream task than a second preprocessing pipeline. Do not invent another binary storage format.

A CLI process stage is sufficient for integration. A Rust wrapper around it would retain the C engine and its licence; it would not establish a native Rust implementation or create a new scientific method. Likewise, replacing a specified minfi functional-normalisation procedure with SeSAMe is a method change, not implementation parity. C SeSAMe2's ordinary DML regression does not replace limma's empirical-Bayes moderation.

### What a Rust implementation could improve

A well-maintained Rust implementation could provide checked input boundaries, typed results/errors and a convenient native library interface for other Rust consumers. It could reduce dependence on a particular external executable or R installation. These are candidate deployment and maintenance benefits to demonstrate.

There is **no assumed speed advantage over native C SeSAMe2**. A wrapper can add maintenance without removing the original implementation. Translating syntax does not validate manifest mappings, channel inference, masks, detection probabilities, background/dye correction, QC, beta/M semantics or boundary cases.

### Agent execution batches

The owner prefers agent effort and observed execution time. These are dependency-bounded batches, not human person-time conversions or promises of elapsed duration. A batch ends with an executable check, a review and either an archived result or a named blocker. Download/build/service queues vary; record actual wall-clock durations when run.

| Scope | Agent work sequence | Completion boundary |
|---|---|---|
| Existing IDAT reader conformance | Source/licence review → synthetic counterexamples → smallest fix → independent real-file replay → review/archive | Exact address/mean/SD/bead counts and defined failure behaviour; no preprocessing claim |
| One-platform preprocessing prototype | Freeze reference and manifests → one preprocessing stage per reviewed batch → full chain/export comparison | A restricted prototype; no disease inference until accepted |
| Research-qualified 450K + EPICv1 core | Reuse the one-platform stages → additional platform fixtures → missingness/QC/export checks → fixed downstream replay → official-device run | Independent per-stage and end-to-end evidence, including masks, axes, precision and failures |
| Broader ecosystem | One demonstrated capability gap per separately specified batch | EPICv2/MSA, CNV, cell composition and specialised functions have separate oracles; no assumed complete parity |

The duration and number of correction batches are **unmeasured** until performed. Prefer an existing suitable implementation when it removes a batch. Keep the full native SeSAMe programme outside the initial clinical paper's critical path.

## 4. Existing Rust IDAT implementations before a new reader

The [expanded source/API search](qualification/rust-backend-search-2026-11-22.md) found multiple partial readers, including Cyanea, snalty/idat-rs and two SNP-genotyping projects. No complete native SeSAMe-equivalent route was identified within the documented scope; this does not rule out private or unindexed work.

**Preferred next candidate:** Cyanea's Apache-2.0 `cyanea-io::parse_idat`, with unneeded default features disabled. First reproduce its apparent directory-order, variable-length string, RunInfo and invalid-offset problems using synthetic conformance cases, then make the smallest compatible fixes. Qualify address, mean, SD and bead counts against independent R reader outputs on eligible 450K/EPIC files. Do not adopt Cyanea's non-equivalent limma/SWAN routines as part of this reader choice.

**SeSAMe Rust sequence:** reader conformance → fixed manifest/channel mapping → detection/masking → background/dye correction → beta/M export → fixed downstream comparison. Give each stage its own reference and acceptance, preserving the existing R/C route. The current R SeSAMe source declares MIT + LICENSE, while C SeSAMe2 has a different institutional-use licence; inspect incorporated dependencies and annotations separately. A language translation is infrastructure, not an automatic new paper.

### Earlier a-xavier candidate and retained findings

The inspected [a-xavier/illumina_array_reader at c6a19f8](https://github.com/a-xavier/illumina_array_reader/tree/c6a19f8062a66790e48add1f3197e91edd0edc91) is an existing small IDAT/gzip reader that exposes address, intensity mean, standard deviation and bead count through Polars. [Cargo](https://github.com/a-xavier/illumina_array_reader/blob/c6a19f8062a66790e48add1f3197e91edd0edc91/Cargo.toml) uses Polars 0.33.2 and flate2. It is not a SeSAMe preprocessing implementation.

Independent source reinspection of [reading_function.rs](https://github.com/a-xavier/illumina_array_reader/blob/c6a19f8062a66790e48add1f3197e91edd0edc91/src/reading_function.rs) confirms the expression `(m % 128) * 2^shift` in variable-length decoding, with a narrow accumulator. Rust's `^` means XOR, so this is a concrete suspected decoding defect requiring a failing conformance case. Unchecked slices, offsets, UTF-8 and required-field unwraps also need defined outcomes. **These are source findings; no failing execution is claimed here.**

The first bounded tasks would be:

1. Resolve the source/licence question below before basing a reusable package on this code.
2. Add independent byte-level cases for single/multibyte lengths, truncation, overflow, invalid offsets, missing/unknown fields and compressed/plain equivalence; reproduce each claimed defect before fixing it.
3. Use checked lengths/offsets and typed failures, then verify red/green pairing and address identity without silent reorder.
4. Compare decoded address/mean/SD/bead-count vectors against an independent reader on a small, eligible 450K/EPIC fixture set. Require exact decoded integer values and explicit supported-version behaviour.
5. Only then assess Polars compatibility, optional export separation and build cost for the actual consumer. Do not combine parser fixes, a dataframe migration and statistical preprocessing into one change.

The [paired-array review](platform-comparison-review.md) supplies potential small fixtures such as GSE86833. The preprocessing audit also maps author test prefixes to public records including GSM2995280 and GSE228820. Public accession identity does not establish byte identity with a laboratory fixture; check hashes, masks/de-identification and permitted reuse. These technical specimens are not independent rare-disease controls.

### Licence/provenance gate

The reader's [LICENSE](https://github.com/a-xavier/illumina_array_reader/blob/c6a19f8062a66790e48add1f3197e91edd0edc91/LICENSE) says MIT, while source comments attribute routines to illuminaio and describe the string routine as copied. The inspected [illuminaio DESCRIPTION](https://github.com/HenrikBengtsson/illuminaio/blob/develop/DESCRIPTION) declares GPL-2. This discrepancy requires exact upstream revision/copyright provenance and a compatible reuse decision. It is **not a finding of infringement**, and a declared MIT file alone does not settle the provenance question.

A broader port must separately inspect the exact R SeSAMe, dependency and annotation licences, retain applicable attribution and avoid assuming a translation or process wrapper changes permissions. The MassDynamics limma-core fork remains GPL-3.0-or-later.

The inspected [C SeSAMe2 licence](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/LICENSE) limits the stated research availability to academic/nonprofit institutions and directs commercial use/transfers to inquiry. Confirm the intended institutional use and distribution against that exact licence. Unresolved copying, commercial-use or redistribution questions need maintainer/institutional clarification before adoption. Software permission does not determine human-data reuse, annotation redistribution or HREC/IRB status; those remain [source-specific decisions](source-access-ethics.md).

## 5. Other small additions that avoid new custom systems

**HPO:** the inspected `hpo` parser skips negated annotations and reduces disease annotations to term membership; see [the pinned source](https://github.com/anergictcell/hpo/tree/c56fc31398a1a332876bbdcc17bee4ab45e3e750). Preserve original negation, frequency, onset, evidence and provenance in the Silver annotation tables even when the selected similarity operation only accepts positive term sets. Omission is not a negative phenotype, and disease-level frequency is not an observed participant characteristic. Test alternate/obsolete IDs and the exact information-content corpus. If an analysis truly needs weighted/negative similarity, assess an existing implementation such as Semsimian before extending a parser; its metric and binding/dependency contract still need qualification. Do not reimplement an ontology engine merely to retain fields.

**Interchange:** use the chosen existing Rust/Julia writer and established Arrow/Parquet format. If methylprep is selected for a specific preprocessing/QC gap, its [documented Parquet output](https://github.com/FoxoTech/methylprep/blob/eb1d2dab0681734dff09cdc8aa63ca0a097a54e1/docs/release-history.md) already provides an export route. Qualify its actual schema and missingness; do not create a duplicate exporter or mandatory Python orchestration. File exchange is enough; cross-language in-process bindings are optional only for a real need.

**Regions and pathways:** existing interval tools can remove custom overlap code, but interval merging is not a DMR method. Generic enrichment/GSEA does not reproduce [missMethyl's probe-aware procedure](https://bioconductor.org/packages/release/bioc/vignettes/missMethyl/inst/doc/missMethyl.html). Keep the named specialist reference until there is a specific method case, correct probe universe and multi-gene/region mapping, unequal-opportunity null checks and an independent oracle. No custom DMR or missMethyl implementation is selected now.

## 6. Promotion, stopping and publication

For any selected addition, record source/versions/licences, the minimal missing capability, frozen inputs and reference, explicit output/error tolerances, consumer behaviour, resource/deployment cost and rollback. Run relevant local acceptance with the [official GitHub Actions runner policy](local-development.md); a cloud test or configured-but-unrun workflow does not substitute for the intended device receipt. Existing reference methods remain available when a candidate is held or rejected.

Apply [N0/N1 before and N2/N3 after analysis/before submission](novelty-priority-protocol.md). Recheck both literature and current dependencies: a newly suitable library may eliminate the proposed custom work. Do not change frozen outcomes after a competing publication. Stop a port when an existing route meets the need, unresolved provenance prevents responsible reuse, or implementation cost threatens the worthwhile clinical study.

Backend conformance, parser fixes, export precision and ontology preservation normally belong in P1's reproducibility material or shared infrastructure. A separate methods/software paper requires a substantive reusable advance and demonstrated scientific value beyond language choice. [Publication bundles and clinical/bioinformatics journal options](experiment-publication-plan.md) remain tied to the analysis contribution, not to the number of capabilities created.
