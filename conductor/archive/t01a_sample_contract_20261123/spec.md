# T01a — public source reconciliation and local sample declarations

## Bounded objective

Reconcile the three selected GEO assay inventories against the committed catalogue, retain unavailable analysis declarations explicitly, and implement a small local structural review command in the existing Rust crate. This is an infrastructure increment of T01; no cohort is scientifically admitted.

## Acceptance

- Original source URLs, retrieval times, response hashes and exact assay-set comparisons are recorded without exporting contact or unrestricted clinical annotations.
- The actual 341-assay input remains held where participant/specimen identity, molecular eligibility, analysis role/partition or independence has not been established. Independent-participant count stays unknown.
- A strict local JSON boundary rejects malformed, duplicate, unsupported and ambiguous declarations; repeated participant/specimen or role/partition conflict holds every affected assay.
- Deterministic reports contain only public assay identifiers, status/reasons and explicit non-admission. Source declarations are not scientific truth verification.
- Meaningful synthetic and actual CLI regressions, independent review and the combined strict after-change gate pass before archive.
- T01 source truth, analysis-specific admission, institutional determination, selected T07 stages and official owner-device acceptance remain open.

## Minimal implementation

Use `tools/catalogue` and its existing test harness. Reuse the already-locked Serde packages for strict deserialization. No new service, database, clinical model, raw-data publication or statistical engine is required.
