# Conductor project context

This project is **documentation-only** until the owner authorises a named track for implementation. No computational scientific claim is accepted by merely writing this plan.

- [Product and scientific purpose](product.md)
- [Technology and interoperability decisions](tech-stack.md)
- [Scientific workflow and evidence gates](workflow.md)
- [Tracks registry](tracks.md)
- [Local Ponytail decisions](../research/ponytail-decisions.md)
- [Rust candidate audit and qualification gaps](../research/rust-candidate-audit.md)
- [Clinical journal routing, including Orphanet and SSIEM](../research/journals.md)

## Planned project phases

T00 governance and first-principles scoping → T01 dataset/provenance qualification → T02 Kabuki replication → T03 cross-disease comparison → T04 hierarchical methods → T05 matched multi-omics → T06 genotype–toxin analysis.

T05 may be pursued before T04 only if matched assays are qualified and no shared model implementation is needed. T06 is separately gated and is not required for publication of T02–T04.

## Rules

- Exact accessions, versions, participant reuse and permissions first.
- Freeze hypotheses before testing external data.
- Distinguish methylation association, expression prediction and causal perturbation evidence.
- Every numerical method requires a published baseline and explicit stop criteria.
- Prefer **clinical-genetics journal fit**, rather than aiming first for high-profile methods journals.

**Current cross-cutting gates:** [Source public-access, rights and ethics](../research/source-access-ethics.md) and [Rust scientific backend qualification](../research/backend-replacement-policy.md). Both are planning/source checks, not analysis execution receipts.

