# Ponytail full: architectural decision and approval register

This register applies the already-qualified-first / smallest-correct-solution approach. It is a **planning sign-off**, not a claim that dependencies, code or scientific results have been tested.

| Decision | Disposition | Reason / activation gate |
|---|---|---|
| Multiple languages (Julia modelling, R reference assays, selective Rust) | **Approve** | Existing scientific libraries avoid redundant ports; file boundaries keep isolation |
| Arrow/Parquet for tabular interchange | **Approve** | Open typed formats across all three; future synthetic round trip gate |
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
