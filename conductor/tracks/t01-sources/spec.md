# T01 — specification

## Objective

Qualify a bounded dataset manifest for a defined scientific comparison, keeping access, use rights, redistribution, institutional classification and analytical eligibility separate.

## Current scope

The initial increment retrieves public source metadata and the three selected Kabuki archives, checks content identity and file headers, establishes a per-source rights register and maps known prior uses. It does not run disease inference, infer private participant identities or upload human data.

## Admission criteria

- Resolve official source URLs, exact file bytes/hash, assay type and original study provenance for every included input.
- Define affected molecular subsets, native controls, tissue, age/sex/batch availability and donor/assay units. A clinical label or series count is not a confirmed affected-patient count.
- Resolve participant/control reuse across development and validation cohorts using declared source evidence. Unknown overlap or perfect disease/platform confounding holds the affected claim.
- Preserve original diagnosis and causal mechanism; pin ontology/manifest releases and qualified mapping predicates. Disease-level HPO does not create participant phenotypes.
- Record a dated analysis-specific prior-art decision and the applicable institutional research classification before inference.
- Use [dataset rights](../../../research/dataset-rights.md) for research use, distribution and HF decisions. No additional author permission is required by default merely because a public repository does not expose private consent documents.

## Evidence and limits

[Initial source receipt](../../../research/qualification/initial-source-receipt.md) establishes successful transfers/header checks for three sources. The [29-accession rights register](../../../research/registries/dataset-rights.json) has a broader scope and does not assert all those files were downloaded.

A completed intake subtask is not full T01 admission. Newly selected diseases and file revisions repeat the relevant gates. The [medallion layout](../../../research/medallion-layout.md) preserves originals and derivation provenance without requiring a service-backed lakehouse or raw public mirror.
