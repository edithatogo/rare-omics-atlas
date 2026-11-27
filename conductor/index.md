# Conductor project context

The owner authorises continued bounded implementation, API catalogue and GitHub–Hugging Face integration, following implement → review → archive for each completed track. Source, numerical, scientific and actual-device acceptance remain distinct. See [AGENTS.md](../AGENTS.md) for the current scope.

- [Product](product.md)
- [Product guidelines](product-guidelines.md)
- [Technology and data contracts](tech-stack.md)
- [General style guide](code_styleguides/general.md)
- [Workflow](workflow.md)
- [Tracks and execution dependencies](tracks.md)
- [Cross-stream capability crosswalk and just-in-time reuse](capability-crosswalk.md)
- [Machine-readable milestones](dependencies.json)
- [Setup receipt](../research/qualification/setup-receipt.md)
- [Source intake receipt](../research/qualification/initial-source-receipt.md)
- [Ponytail decisions](../research/ponytail-decisions.md)
- [Dataset rights](../research/dataset-rights.md)
- [Literature map](../research/literature/README.md)
- [Experiments and publication bundles](../research/experiment-publication-plan.md)
- [Backend audit](../research/methylation-backend-audit.md)
- [Rust additions and SeSAMe-rust assessment](../research/rust-port-roadmap.md)
- [Medallion layout](../research/medallion-layout.md)
- [Resources and hosting](../research/resources-hosting-reuse.md)
- [Ontology context implementation and source receipt](../research/qualification/ontology-context-2026-11-24.md)
- [Ontology and annotation priorities](../research/resources-hosting-reuse.md#ontology-and-annotation-priorities)
- [Official local runners](../research/local-development.md)
- [Strict development and CI contract](../research/ci-plan.md)
- [Repository ownership, native hooks and pinned receiving integration](../research/repository-integration.md)
- [Accepted source/receiving increment and actual strict evidence](../research/qualification/contracts-hooks-2026-11-23.md)
- [HM450 preprocessing/annotation contract and executable recipe](../research/preprocessing-qualification.md)
- [HM450 QC/p-value v1 history and executable recipe](../research/qc-qualification.md)
- [Native QC v2 semantics, curated GCT and executable qualification](../research/native-qc-qualification.md)
- [Cohort-source curation and actual held declarations](../research/qualification/t01-cohort-curation-2026-11-23.md)
- [Current identity and covariate source evidence](../research/qualification/t01-identity-covariates-2026-11-23.md)
- [Clinical journal routing](../research/journals.md)
- [Actual Hub metadata publication and remaining raw transfer](../research/qualification/hf-metadata-publication-2026-11-22.md)

## Scientific streams

- **Rare Disease (Rare Omics Atlas):** existing T01–T05 and applicable T07 milestones; unchanged scientific priority and identifiers.
- **Toxinology:** [V01 source reconciliation, clinical information extraction and research opportunities](tracks/v01-toxinology/index.md), tracked by [issue #30](https://github.com/edithatogo/rare-omics-atlas/issues/30). Venomics, human host-response omics and clinically motivated animal biology are components of this stream, not separate repositories.
- **Cross-stream:** existing [T06](tracks/t06-toxin/index.md), conditional on separately admissible data and a defensible host variation/exposure question.
- **Shared:** T00 governance, T08 catalogue, T09 data releases, existing ontology, literature, method and publication controls. Shared infrastructure is not shared biological replication. No new Conductor installation or separate ticketing system.

The [machine-readable V01 milestones](dependencies.json) are independent of methylation-specific prerequisites. PRs #28, #36 and #37 are now received; the rare-disease scientific scope is unchanged. V01's initial source metadata release is integrated, not published to the Hub. The [publication implementation/preflight correction](archive/v01_publication_preflight_20261127/index.md) is accepted and archived; the actual upload is externally blocked because HF_TOKEN was unavailable to the reviewed job. Original clinical data access and inference are held. See the [acquisition and release record](tracks/v01-toxinology/acquisition.md).

## Execution rule

Schedule ready milestones, not numeric track labels. T00 context enables T01 discovery and a synthetic/committed-corpus backend baseline. Patient-data inference requires T01 analysis admission, the selected T07 backend, actual target-device qualification and an analysis-specific N1 freeze. Optional Rust ports and unneeded model layers remain separate branches.

A source manifest, completed code test, statistical acceptance and an institutional decision are different receipts. Never satisfy a missing criterion by renaming it. When an external prerequisite is unavailable, record its owner, resolution and affected downstream milestones; continue independent authorised work.

The owner's 24 November ontology extension is implemented within existing T01/T03/T04/T05 responsibilities. T01 qualifies selected source bytes and catalogue context; the consuming scientific track evaluates any predictive or interpretive benefit. Optional ontologies and knowledgebases do not become universal prerequisites, and disease annotations do not become observed participant phenotypes.
