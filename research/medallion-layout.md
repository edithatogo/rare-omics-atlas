# Minimal medallion storage

**Ponytail decision: use logical Bronze/Silver/Gold boundaries now; defer a service-backed lakehouse.** The useful feature is traceable promotion from originals to qualified data to analysis outputs. Current cohort scale and a single researcher do not justify Delta/Iceberg, a distributed catalogue or a new orchestration service.

| Layer | Contents | Promotion rule | Initial status |
|---|---|---|---|
| Bronze | Unmodified source archives; source URL/revision, local SHA-256, source notices and retrieval receipt | Complete transfer and format checks; preserve originals and restrictions | Three Kabuki raw archives and source metadata retrieved outside Git |
| Silver | Admitted assay/sample manifest, QC and labelled beta/M matrices; pinned disease/gene/ontology mappings | Qualified preprocessing, explicit inclusion/exclusion, identity/covariates, institutional analysis admission | No scientific Silver matrix produced |
| Gold | Prespecified contrasts, effects/SE, pathway/module results, validation and figures | Reproducible selected method, complete provenance, uncertainty and held-out evaluation | No scientific Gold result produced |

## Simple physical arrangement

Use one local data root with bronze, silver and gold directories when each layer first exists. A reference-cache directory holds pinned public annotations. These paths are ignored by Git. The current scratch intake is a Bronze cache; its durable evidence is the [source receipt](qualification/initial-source-receipt.md), not a claim that transient raw bytes are permanent storage.

Keep small factual registries and receipts in research/registries and research/qualification. Use Arrow/Parquet for tabular records, annotations and results when an actual consumer exists. Keep IDATs in their original format and dense methylation matrices in an appropriate labelled/chunked format. Do not turn every probe-by-sample value into a long Parquet row merely to use a preferred library.

The Rust API catalogue now produces normalized Silver **metadata**, with a reviewed source/identity contract. No biological Silver beta/M matrix, Gold result or cross-language Arrow/Parquet round-trip has yet been produced. Those require their own actual consumers.

## A versioned result

Each promoted artifact needs its input hashes, source/annotation revisions, assay/sample axes, preprocessing or model version/flags, exclusion reasons, units, feature universe, rights classification and the current experiment freeze. Preserve derivation links rather than copying inputs indiscriminately. Cohort-wide moderation/FDR must not change merely because files are split into partitions.

Disease effects should first be estimated with each study's own controls. A later joint model consumes qualified estimates and their uncertainty; it does not concatenate all unrelated controls into an assumed universal healthy group. Adding diseases should trigger joint refitting of the defined model, with order-invariance checks where appropriate.

## GitHub–Hugging Face integration

The [T09 release manifest](releases/2026-11-22/manifest.json) selects the reviewed API catalogue and three byte-identical GEO raw archives for one public Hugging Face dataset. Each object has its own source/reuse basis, byte count and SHA-256. One source-bound artifact decision is reused for identical bytes; there is no additional mandatory human sign-off. Other accessions remain source-linked Bronze until an actual transfer/release is recorded. Institutional admission to disease inference stays separate from this already-public source mirror.

Use one atlas metadata/results dataset if a release is made and register it in the existing account catalogue. Repository visibility is not a folder-level permission system. Do not create three public HF repositories merely to match the three layer names. [Rights register](dataset-rights.md) and [hosting/resource policy](resources-hosting-reuse.md) govern individual objects.

## Actual operational boundary

[The official Hub publisher](../tools/hf-release/README.md) verifies a fixed allowlist, then delegates authentication, uploads and commits to `huggingface_hub`. It binds publication to a clean reviewed GitHub revision and reads back exact Hub object hashes/sizes. GitHub stores code, source/rights manifests and receipts; Hugging Face stores the eligible large objects. Raw arrays do not pass through Git history. An authenticated cloud publication from a pinned GitHub checkout is recorded separately from an Actions job.

The [local qualification](../.github/workflows/local-qualification.yml) and [publication](../.github/workflows/publish-hf.yml) workflows use the official self-hosted runner, trusted main and manual dispatch. A single appropriately scoped HF credential is needed for the publication workflow; no environment approval, CODEOWNERS gate or service-backed lakehouse is introduced. Configuration is not evidence of a registered owner device or an executed Actions job.
