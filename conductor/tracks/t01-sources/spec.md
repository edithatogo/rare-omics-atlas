# T01 — specification

## Objective

Qualify a bounded dataset manifest for a defined scientific comparison, keeping access, use rights, redistribution, institutional classification and analytical eligibility separate.

## Current scope

The initial increment retrieves public source metadata and the three selected Kabuki archives, checks content identity and file headers, establishes a per-source rights register and maps known prior uses. It does not run disease inference, infer private participant identities or upload human data.

The [completed T01a increment](../../archive/t01a_sample_contract_20261123/index.md) reconciles 341 public GEO assay records against the catalogue and implements `sample-contract` in the existing Rust crate. Synthetic tests, independent review and all 34 combined strict checks passed before archive. Its initial replay held all 341 declarations. The subsequent [T01b curation receipt](../../../research/qualification/t01-cohort-curation-2026-11-23.md) records 257 held, 84 review-scope exclusions and zero ready or admitted; the original T01a result remains historical. The structural statuses `ready_for_review`, `held` and `excluded` never grant scientific admission, verify source claims or produce an independent-participant count.

The 24 November ontology extension adds a source-bound context consumer to the existing Rust catalogue. Its immediate inputs are the initial disease crosswalk and public tissue/cell literals, with curated Uberon/CL mappings. The disease dictionary remains reference context rather than assigning diagnoses to assays. The consumer must preserve source text, input hashes, explicit mapping predicates, ambiguous/unmapped/unreported values and unknown biological independence. See the [resource priorities](../../../research/resources-hosting-reuse.md#ontology-and-annotation-priorities) for subsequent gene, sequence-feature, pathway, regulatory, evidence, protein and metabolic consumers. Their activation depends on an actual analytical need.

## Admission criteria

- Resolve official source URLs, exact file bytes/hash, assay type and original study provenance for every included input.
- Define affected molecular subsets, native controls, tissue, age/sex/batch availability and donor/assay units. A clinical label or series count is not a confirmed affected-patient count.
- Resolve participant/control reuse across development and validation cohorts using declared source evidence. Unknown overlap or perfect disease/platform confounding holds the affected claim.
- Preserve original diagnosis and causal mechanism; pin ontology/manifest releases and qualified mapping predicates. Disease-level HPO does not create participant phenotypes.
- Qualify each consumed reference product, release/revision, actual hash, rights/attribution and identifier lifecycle. Report exact/broader/ambiguous/unmapped context separately; do not equate Kabuki parent/subtypes, tissue/cell mixtures, cultured cell lines or nearest-gene/regulatory-target annotations. A successful catalogue join does not establish clinical meaning, cell composition or analytical benefit.
- Record a dated analysis-specific prior-art decision and the applicable institutional research classification before inference.
- Use [dataset rights](../../../research/dataset-rights.md) for research use, distribution and HF decisions. No additional author permission is required by default merely because a public repository does not expose private consent documents.

## Evidence and limits

[Initial source receipt](../../../research/qualification/initial-source-receipt.md) establishes successful transfers/header checks for three sources. The [29-accession rights register](../../../research/registries/dataset-rights.json) has a broader scope and does not assert all those files were downloaded.

The [T01a source/contract receipt](../../../research/qualification/t01-sample-contract-2026-11-22.md) records exact source hashes, zero assay-set discrepancies, held reasons, the executable JSON interface and its peer-reviewed limits. Case/control and clinical annotations require analysis-specific curation; their existence does not resolve molecular eligibility or cross-study participant overlap.

A completed intake subtask is not full T01 admission. Newly selected diseases and file revisions repeat the relevant gates. The [medallion layout](../../../research/medallion-layout.md) preserves originals and derivation provenance without requiring a service-backed lakehouse or raw public mirror.
