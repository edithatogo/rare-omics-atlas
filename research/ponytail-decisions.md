# Ponytail review and decision register

Updated 22 November 2026. Ponytail was applied to source selection, dependency reduction, sequencing, implementation scope and publication bundling. These are engineering/research planning decisions, not an independent scientific certification, institutional approval or journal acceptance prediction.

This current register supersedes earlier ambiguous references to two different limma-rust projects. Historical source findings remain explicitly scoped in the [backend audit](methylation-backend-audit.md).

| Aspect | Decision | Reason and evidence |
|---|---|---|
| Dependency-ordered execution | Adopt | Complete prerequisites before their consumers; T07 selected-method acceptance precedes T02, with task-level dependencies in Conductor |
| Initial track completion | Record actual bounded results | All 29 registered accessions catalogued through source APIs; fork LM01a/LM02a complete and archived; scientific, historical-identity and device gates remain visible |
| Multiple languages | Rust > Julia > Python > R among suitable choices | Prefer established capabilities and preserve independent oracles; no mandatory multi-language runtime bundle |
| Arrow/Parquet | Adopt for actual tabular boundaries | Existing engines avoid custom transport; cross-language semantic equality still requires a consumer test |
| Dense assay storage | Preserve labelled/chunked matrix representation | Avoid a huge long-form table solely for Parquet |
| Medallion | Adopt logical Bronze/Silver/Gold | Low-cost provenance and admission boundaries; no automatic release permissions |
| Service-backed lakehouse | Defer | No demonstrated need for Delta/Iceberg, distributed catalogue or orchestration |
| Conductor | Reuse pinned source and project context in both repos | Source actually installed; host auto-activation remains unobserved |
| Central standards/templates | Reuse applicable policy, no estate-wide changes | Existing scientific-native and Rust standards cover this work; no unrelated starter/runtime |
| Actual limma fork | Continue qualifying the MassDynamics-derived owner fork | Historical 104-test baseline; LM01a added 30,840 fresh R comparisons with 110-test suites; merged LM02a has 113-test suites. These are successive evidence snapshots, not methylation admission |
| Fork improvements | Retain completed reference/harness work; qualify the production consumer next | Shared ambiguous-ID rejection and exact fresh named alignment are implemented; seven historical positional cases, production consumption and actual-device qualification remain open |
| faer/statrs | Conditional new-dependency experiment in the actual fork | Neither is installed there; preserve rank/pivot/tail semantics and qualify affected callers |
| SeSAMe2 | Qualify existing C CLI before a rewrite | Author R comparisons already exist; resolve source terms, annotation and real export precision |
| SeSAMe-rust | Optional bounded roadmap, not initial prerequisite | Reader/adapter work has bounded conformance batches; a full preprocessing ecosystem has multiple separately validated stages |
| IDAT reader candidate | Hold adoption pending parser/provenance qualification | Source findings and copied-routine attribution require reproduction/clarification, not assumed equivalence |
| HPO/ontology/interval libraries | Use needed existing functions | Preserve complete source annotations; do not replace missing metadata by inventing phenotypes |
| Polars/petgraph | Use for actual table/graph consumers | One representation per stage; avoid a new framework or package collection |
| DMR/probe-aware enrichment | Retain exact validated method until equivalent replacement passes | Generic intervals/GSEA do not reproduce regional inference or probe-opportunity correction |
| Python | Optional specialist role | MOFA or a needed existing exporter may avoid custom science; no general orchestration requirement |
| Experimental Rust AD/GPU | Defer to a specific model need | Enzyme or a GPU alone is not a publication claim; compare model-level accuracy and total cost |
| 450K/EPIC comparisons | Supporting qualification by default | Exact proposed cohorts have prior joint reuse; test a specific transfer/uncertainty issue |
| Clinical paper bundle | E0 + E2 + E3 first, technical work in support | Stronger than one manuscript per capability; change scope when novelty or data changes |
| Cross-disease/multi-omics | Conditional later extension or one coherent study | Native controls, molecular mechanisms, pairing, independence and held-out outcomes first |
| Journals | Clinical fit and achievable scope | Molecular Syndromology/EJMG first where appropriate; OJRD, paediatric, JIMD Reports/JIMD or bioinformatics routes depend on the actual claim |
| Continual literature mapping | Existing weekly automation plus N0–N3 | PubMed/OpenAlex/Europe PMC/Crossref and repository evidence; no custom crawler/service |
| GEO rights | Positive source evidence, not blanket unknown | Separate research use, distribution, article licence and institutional/hosting decision per artifact |
| Hugging Face | Reviewed metadata subset published; raw mirroring pending | Publication used the Hub UI, not an observed GitHub workflow run; the three archives, 3,828,981,760 bytes, remain local. See the [publication receipt](qualification/hf-metadata-publication-2026-11-22.json) |
| Official local runners | Actual owner-device evidence required | Fork has a real manually invoked workflow; cloud test does not meet this gate |

## Review procedure

At N0/N1 and N2/N3 ask which existing tool or dependency removes a real requirement, what source revision and licence apply, and which small test accepts the change. Record retain / replace / remove / defer. A new Rust stage does not require a speed claim, but an asserted speed benefit needs a comparison.

Prefer a bounded upstream-compatible addition over a private reimplementation when the method is already available. Do not send upstream messages or PRs without authorisation. Owned-repository context changes and the existing-corpus check are recorded in [setup evidence](qualification/setup-receipt.md).

A failed or redundant experiment can remain useful supporting validation. Preserve frozen analyses, report negative transfer and uncertainty, and do not manufacture a paper from every library, ontology, model or port.

## Continued implementation — 22 November 2026

- API catalogue: the small Rust client completed metadata retrieval for all **29 registered accessions** through official E-utilities/GEO and PRIDE interfaces, with JSONL boundaries and response receipts. These are source metadata records, not 29 independent rare-disease cohorts or 29 raw-data transfers; see the [qualification receipt](qualification/api-catalogue-2026-11-22.md). No dataframe engine is needed for source JSON.
- Minimal medallion: one Hugging Face dataset, GitHub-owned code/manifests and source-specific object records. A reviewed metadata subset is published through the Hub UI; the three locally verified archives remain unmirrored. The publisher's source-bound checks pass, but neither those checks nor this UI publication establishes an executed GitHub publication workflow or owner-device runner. The official Hub client remains a justified Python operational boundary; do not reimplement authentication, chunking, resumable upload or Hub commits in Rust.
- Numerical backend: retain the MassDynamics-derived owner core first. [LM01a](https://github.com/edithatogo/limma-rust/blob/bc167f3bc25c4a927e468b0c0f6b24d68bdc156a/conductor/archive/lm01a_reference_20261122/index.md) completed independent public synthetic R generation: 117 byte-identical reference files, 30,840 comparisons and full 110-test debug/release suites. [LM02a](https://github.com/edithatogo/limma-rust/blob/bc167f3bc25c4a927e468b0c0f6b24d68bdc156a/conductor/archive/lm02a_fixture_identity_20261122/index.md), merged in [PR #4](https://github.com/edithatogo/limma-rust/pull/4), adds shared identifier hygiene and strict fresh named alignment, with 113-test debug/release suites and all 563 input/reference files unchanged. The seven historical positional cases are not fully sample-identity qualified; the production consumer, owner-device and methylation gates remain open. Evaluate sinmojito only for a concrete extra method; agreement between two ports is not an independent reference.
- SeSAMe Rust: use the expanded existing-reader search; prefer a bounded Cyanea conformance/fix experiment over a second generic parser. Native QCDPB stages follow independent references, not a complete ecosystem rewrite.
- Decision support: eligibility precedes subjective score/rank sensitivity. Reuse Voiage's Rust EVPI only when coherent uncertainty draws and utilities exist. Do not add a decision framework for a small options table.
- Paired cohorts: GSE154566 adds 233 verifiable paired blood specimens, with family clustering and possible prior-publication overlap. Ordinary pooled concordance is mature; assess whether a frozen policy improves held-out disease effects.
- Execution: implement, review and archive each completed bounded track. Preserve incomplete parent scientific/device milestones. Use agent batches and measured durations; no human-effort estimates or fabricated delivery times.

See the [new Rust search](qualification/rust-backend-search-2026-11-22.md) and [paired/decision review](qualification/paired-calibration-review-2026-11-22.md). These are source reviews; implementation-specific receipts govern what actually ran.

## Repository and integration refinement — 23 November 2026

Retain the two projects and the central policy source. Limma owns the numerical API, independent oracle and canonical contract; atlas owns source/admission, preprocessing and the receiving adapter. The [repository integration contract](repository-integration.md) records the exact ownership and producer-first update sequence. Independent source work and producer CI can run alongside the receiving work once a real immutable producer commit exists.

Use native Git hooks and the existing strict verifiers, with the exact central privacy scanner. No hook framework or shared package is justified for these two small wrappers. The actual committing index must be scanned, including alternate indexes, and the tested working tree must match it. Clone-local installation and server-side required checks remain distinct.

Use the existing Rust numerical operations through one thin named boundary. Reuse the already-present development CSV/Serde support for a synthetic exporter and the existing atlas Python environment's standard library for its receiver. This avoids a new numerical dependency, a language bridge and a second implementation of inference. The numerical contract does not include production raw-data parsing.

Keep real exporter round-trip tests in Cargo's ordinary target selection. The pinned cargo-llvm-cov native defaults exclude example files from coverage reporting; its unsupported all-default override would require duplicating toolchain/vendor/test filtering. Preserve those defaults and disclose that scope while requiring the executable tests, rather than transform reports or claim coverage that was not measured.

The source/sample boundary validates declarations and keeps unresolved evidence held. Reusing already-locked Serde for strict duplicate-field rejection is justified by an independently reproduced parser ambiguity. No new scientific admission rule or identity inference is introduced.
