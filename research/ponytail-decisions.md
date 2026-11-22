# Ponytail review and decision register

Updated 22 November 2026. Ponytail was applied to source selection, dependency reduction, sequencing, implementation scope and publication bundling. These are engineering/research planning decisions, not an independent scientific certification, institutional approval or journal acceptance prediction.

This current register supersedes earlier ambiguous references to two different limma-rust projects. Historical source findings remain explicitly scoped in the [backend audit](methylation-backend-audit.md).

| Aspect | Decision | Reason and evidence |
|---|---|---|
| Dependency-ordered execution | Adopt | Complete prerequisites before their consumers; T07 selected-method acceptance precedes T02, with task-level dependencies in Conductor |
| Initial track completion | Record actual subtask results | Context, source transfer/headers, rights/prior-art and fork corpus replay completed; external gates remain visible |
| Multiple languages | Rust > Julia > Python > R among suitable choices | Prefer established capabilities and preserve independent oracles; no mandatory multi-language runtime bundle |
| Arrow/Parquet | Adopt for actual tabular boundaries | Existing engines avoid custom transport; cross-language semantic equality still requires a consumer test |
| Dense assay storage | Preserve labelled/chunked matrix representation | Avoid a huge long-form table solely for Parquet |
| Medallion | Adopt logical Bronze/Silver/Gold | Low-cost provenance and admission boundaries; no automatic release permissions |
| Service-backed lakehouse | Defer | No demonstrated need for Delta/Iceberg, distributed catalogue or orchestration |
| Conductor | Reuse pinned source and project context in both repos | Source actually installed; host auto-activation remains unobserved |
| Central standards/templates | Reuse applicable policy, no estate-wide changes | Existing scientific-native and Rust standards cover this work; no unrelated starter/runtime |
| Actual limma fork | Qualify MassDynamics-derived owner fork | Existing 104-test corpus passed; other implementation's defects are not this fork's roadmap |
| Fork improvements | Independent R recipe, fixture identity and narrow consumer contract first | These address actual reproducibility/integration gaps before numerical rewriting |
| faer/statrs | Conditional new-dependency experiment in the actual fork | Neither is installed there; preserve rank/pivot/tail semantics and qualify affected callers |
| SeSAMe2 | Qualify existing C CLI before a rewrite | Author R comparisons already exist; resolve source terms, annotation and real export precision |
| SeSAMe-rust | Optional bounded roadmap, not initial prerequisite | Reader/adapter work can be modest; a validated preprocessing ecosystem is months of work |
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
| Hugging Face | Eligible objects only, no upload yet | Public metadata and later reviewed aggregate results first; raw/Silver conditional |
| Official local runners | Actual owner-device evidence required | Fork has a real manually invoked workflow; cloud test does not meet this gate |

## Review procedure

At N0/N1 and N2/N3 ask which existing tool or dependency removes a real requirement, what source revision and licence apply, and which small test accepts the change. Record retain / replace / remove / defer. A new Rust stage does not require a speed claim, but an asserted speed benefit needs a comparison.

Prefer a bounded upstream-compatible addition over a private reimplementation when the method is already available. Do not send upstream messages or PRs without authorisation. Owned-repository context changes and the existing-corpus check are recorded in [setup evidence](qualification/setup-receipt.md).

A failed or redundant experiment can remain useful supporting validation. Preserve frozen analyses, report negative transfer and uncertainty, and do not manufacture a paper from every library, ontology, model or port.
