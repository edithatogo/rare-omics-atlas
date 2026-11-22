# Ponytail full: architectural decision and approval register

This register applies the already-qualified-first / smallest-correct-solution approach. It is a **planning sign-off**, not a claim that dependencies, code or scientific results have been tested.

| Decision | Disposition | Reason / activation gate |
|---|---|---|
| Multiple languages under Rust > Julia/Mojo > Python > R | **Approve** | Existing scientific libraries avoid redundant ports; file boundaries keep isolation |
| Arrow/Parquet for tabular interchange | **Approve** | Open typed formats at actual producer/consumer boundaries; future semantic round-trip gate |
| Dense labelled matrix format for 450K/EPIC arrays | **Approve** | Parquet long form is an unnecessary storage/compute penalty |
| Conductor Git submodule at existing path | **Approve** | Reuses exact existing `.agents/plugins/conductor` convention; pinned commit; activation unverified |
| Central `repository-standards` and shared GitHub defaults | **Approve** | Single source of policy; only apply applicable research profiles |
| Starter template `template-solo-data` | **Defer** | Python code starter not needed for a docs-only project |
| Starter template `template-solo-rust` | **Defer** | No Rust crate yet |
| Full distributed lakehouse (Fabric/Databricks/Delta/Iceberg) | **Reject initially** | No measured operational need |
| Minimal Bronze/Silver/Gold conceptual boundaries | **Approve** | Provenance separation at trivial initial cost |
| Preemptive Rust reimplementation of limma, minfi, SciML | **Reject** | High validation burden; existing libraries already available |
| CPU-first processing, GPU acceleration on demand | **Approve** | Workloads small; benchmark first |
| Clinical-journal-first submission planning | **Approve** | Better audience and achievable scope, but acceptance not promised |
| Optional genotype×toxin stage | **Conditional** | Requires quantitative matched / functionally testable interactions |
| Automated model selection or regulatory digital twin | **Reject initially** | Data and causal identification insufficient |

Any new dependency must answer: (a) which validated requirement cannot be met by current tools? (b) what exact acceptance test qualifies it? (c) which package/dependency can it replace or avoid? If no measurable answer, do not add it.

## 22 November 2026 addendum

| Question | Disposition | Evidence needed before activation |
|---|---|---|
| Language-agnostic result contracts for later Rust replacements | **Approve as documentation only** | [backend qualification policy](backend-replacement-policy.md); actual cross-language round trip not run |
| Build in-process universal backend/plugin framework now | **Reject** | File-level isolated command stages cover current needs |
| Qualify existing `limma-rust` | **Conditional, prioritise first numerical backend candidate** | Canonical `limma` comparison on same qualified M matrices + null/small-n simulations + actual speed/RAM benchmarks |
| Rewrite raw IDAT normalisation in Rust now | **Reject** | Need significant benchmarked gap and per-platform statistical correctness |
| Rust interval joins and accession data checks | **Approve when analysis exists** | Reference output, checksum and CPU/RAM evidence |
| Write custom ODE/Bayesian code in Rust now | **Reject** | Julia SciML/Turing already solve relevant numerical tasks |
| Dataset is publicly listed; ethics therefore unnecessary | **Reject** | Download/access, source rights/consent and institutional review are independent gates |
| Metadata-only source qualification and ethics dossier | **Approve** | Public sources checked; no implied data transfer or approval |

Source: [public access and ethics triage](source-access-ethics.md). Ponytail is an engineering decision discipline, not an autonomous external signatory or a legal/HREC approval body.

## 22 November 2026: scientific priority and dependency refinement

- **Approve** a targeted N0/N1 pre-analysis and N2 post-analysis publication/preprint/dataset novelty check, plus N3 journal submission refresh, recorded in existing Conductor tracks; no always-on search service or extra layer. See [protocol](novelty-priority-protocol.md).
- **Approve** dynamic study prioritisation by data rights/ethics, molecular confirmation, controls, independence, power, clinical outcome, publication competition, effect on other tracks and journal fit; do not optimise N/I/F alone.
- **Approve conditionally** Python only for nonduplicative qualified specialist software and Rust Polars for a real large tabular consumer; Rust petgraph for an actual graph algorithm, not an ontology edge table.
- **Mojo updated below:** same preference tier as Julia; activation remains conditional on an existing suitable capability and a real consumer, with platform/precision qualification.
- **Prefer** lower-profile clinically appropriate journals (Molecular Syndromology, European Journal of Medical Genetics) over prior higher-profile outlets; reassess at N2/N3, never infer acceptance odds from impact factor.
- **No estate-wide modifications**: existing `repository-standards` scientific-native profile already requires a minimal core and numerical/resource qualification, and references Ponytail. Propose a central *advisory* update only after reusable evidence appears.

## 22 November 2026: deeper replacement review

These decisions supersede earlier blanket Julia-first or performance-only language selection. They are planning judgments, not independent software certification.

| Aspect | Ponytail disposition | Concrete reason / gate |
|---|---|---|
| Rust > Julia/Mojo > Python > R | **Adopt** | Among scientifically suitable candidates; a new Rust stage needs no speed claim. Keep runtime and oracle separate |
| Broader candidate register | **Adopt as source review** | [Audit](rust-candidate-audit.md) identifies existing libraries and inspected source revisions; no installation or qualification implied |
| limma-rust | **First numerical qualification** | Existing port avoids a new one; exact array/design/moderation/FDR/platform checks before use |
| hpo, ontolius, bedrs/gia | **Use when needed** | Existing ontology/interval operations avoid custom code; annotation and coordinate semantics still matter |
| petgraph + required algorithm | **Conditional** | rustworkx-core/leiden-rs or alternative graphrs reduce algorithm code; no mandatory bundle or duplicate graphs |
| SeSAMe2 C exception | **Qualify, do not port** | Existing IDAT CLI; licence, mask/manifest and numerical discrepancies need explicit checks |
| Cyanea array replacement | **Hold inspected methods** | Source implements materially different moderation/SWAN procedures; use focused candidates |
| nuts-rs/diffsol/rebop/SDE candidates | **Conditional on actual model** | Reuse numerical components; validate the complete scientific contract, not only a solver call |
| Array DMR/missMethyl native port | **Defer** | Specific methodological gaps remain; narrow R fallback is smaller than an unvalidated rewrite |
| Mojo/Enzyme/GPU/new language | **Conditional, no installation** | Mature language features do not supply domain-method equivalence; preserve CPU float64 and pin experimental components |
| OJRD and SSIEM titles | **Add by manuscript fit** | OJRD for substantive rare-disease work; JIMD Reports for focused metabolic studies; JIMD for stronger relevant contributions. No acceptance odds inferred |
| New tracks/frameworks/estate-wide rollout | **Unnecessary** | Existing T01–T07, file boundaries and central standards accommodate these refinements |

No upstream messages or PRs, scientific code, dependency installs, assay downloads or numerical tests were performed by this review. Targeted planning searches inform the documents; complete analysis-specific N0–N3 receipts remain future gates.

## 22 November 2026: source-level audit and bundled study decisions

Apply the following to the current plan. This is Ponytail's engineering review discipline, not independent scientific certification, journal acceptance, permission to host data or ethics approval.

| Aspect | Disposition | Smallest justified action |
|---|---|---|
| First paper | **One clinical bundle by default** | E0 qualification + E2 cohort estimates + E3 frozen external replication; E1 technical and backend checks support the paper. Additional capabilities do not imply more manuscripts |
| Cross-disease, expression and model papers | **Combine conditionally** | E4–E6 extend the first paper or form one coherent later study only when independence, sample size and a distinct question support it; see [experiment plan](experiment-publication-plan.md) |
| limma-rust source defects | **Hold scientific use pending bounded fixes/qualification** | Strict IDs/unique labels, correctly defined uncertainty, explicit NA/rank policy and a comparison that fails on identifier/NA/p-value discrepancies; use [focused audit](methylation-backend-audit.md) |
| limma-rust custom numerical routines | **Prefer existing dependencies first** | Evaluate faer thin QR/SVD/eigensolvers and statrs checked functions. Separately qualify newer versions/MSRV; preserve stable tail math and R-specific moderation semantics. Do not assume shorter code is equivalent |
| SeSAMe2 versus R | **Reuse existing upstream comparison** | Author comparison already exists. Extend only missing public-fixture, platform, mask and actual-export coverage. Qualify C production precision/licence; do not port the pipeline to Rust or claim the first comparison |
| New Rust candidates | **Conditional** | rsfgsea CPU classic for an actual ranked-expression GSEA stage; Semsimian for needed weighted/negative phenotype evidence; num-dual/ad_trait for a defined gradient. No mandatory package collection |
| Remaining array-method gaps | **Retain narrow oracle/fallback** | Exact DMR, probe-opportunity enrichment and specialised variance procedures still need method-specific equivalence. A change of language is not justification for an unvalidated substitute |
| Python / Mojo | **Python optional; Mojo inactive initially** | Preserve real specialist options such as MOFA, PyMC/nutpie and methylprep/methylcheck. No Python orchestrator just for file exchange. Mojo has no necessary initial consumer; keep its preference tier as a watchlist, not an installed runtime |
| Enzyme through Rust | **Defer to a specified model; not novel alone** | Existing Rust/LLVM AD is prior art. Compare gradient providers under the same model/sampler, with gradient, calibration, posterior and total-cost checks. Usually supporting methods, not a separate paper |
| 450K + EPIC | **Integrate with explicit estimand** | Same-specimen pairs test platform agreement; independent cohorts test disease-effect transfer. Platform-confounded disease/control designs cannot be repaired by batch correction. Preserve common and platform-specific analyses separately |
| Hugging Face medallion hosting | **Eligible objects only** | Reuse account registry and qualified reference snapshots. Initially publish source manifests and disclosure-reviewed aggregate outputs; source rights and institutional hosting permission remain object-specific |
| Additional reference resources | **Incremental** | MONDO/HPO/OMIM IDs + manifests/gene identity initially, Reactome/GO with pathways; other resources need a named consumer and appropriate terms. No universal knowledge-graph build |
| Hardware and local runners | **Official runner required; activation unverified** | Sanitised mail-confirmed hardware recorded in [local development](local-development.md). Register and observe trusted local jobs when implementation starts; no emulator or hosted-only receipt |
| Journals | **Clinical question first, realistic scope** | Add paediatric and disease-specific options; BMC Bioinformatics/Bioinformatics Advances for substantive methods. OJRD and SSIEM titles remain fit-dependent, not automatic targets or acceptance claims |
| Existing account/repo infrastructure | **Reuse selectively** | Preserve Conductor gitlink, central standards and public source provenance. No estate-wide edits, duplicated registries, new templates, extra services or patient-data uploads are needed now |

The source and URL review is dated and bounded. Recheck releases, prior art, journal policies and terms at N0/N1 and N2/N3; do not represent this register as a standing automatic approval for future code or public data release.

