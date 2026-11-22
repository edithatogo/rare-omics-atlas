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

No analytical pipeline, Parquet implementation or automatic layer promotion has been created. Written contracts alone do not verify cross-language interoperability.

## A versioned result

Each promoted artifact needs its input hashes, source/annotation revisions, assay/sample axes, preprocessing or model version/flags, exclusion reasons, units, feature universe, rights classification and the current experiment freeze. Preserve derivation links rather than copying inputs indiscriminately. Cohort-wide moderation/FDR must not change merely because files are split into partitions.

Disease effects should first be estimated with each study's own controls. A later joint model consumes qualified estimates and their uncertainty; it does not concatenate all unrelated controls into an assumed universal healthy group. Adding diseases should trigger joint refitting of the defined model, with order-invariance checks where appropriate.

## Hugging Face is a release destination, not an automatic lakehouse

A public source catalogue and eligible aggregate outputs are the initial release candidates. Bronze raw and Silver participant-level files require their own distribution/disclosure/hosting decision. Source policy may support redistribution without obliging this project to mirror the files. Private HF storage also requires applicable permission.

Use one atlas metadata/results dataset if a release is made and register it in the existing account catalogue. Repository visibility is not a folder-level permission system. Do not create three public HF repositories merely to match the three layer names. [Rights register](dataset-rights.md) and [hosting/resource policy](resources-hosting-reuse.md) govern individual objects.
