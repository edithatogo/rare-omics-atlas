# Rare Omics Atlas

**Status: official API catalogue implemented and independently reviewed; minimal GitHub–Hugging Face publication in progress. Scientific analyses have not started.** Updated 22 November 2026.

An ontology-linked rare-disease epigenomics programme. The first proposed paper tests whether a prespecified Kabuki methylation result transfers across independent cohorts and platforms, with explicit clinical interpretation limits. A pooled network, extra ontology or change of programming language is not by itself a novel clinical finding.

## Start here

1. [Conductor context](conductor/index.md), [dependency-ordered tracks](conductor/tracks.md) and [initial completion receipt](research/qualification/setup-receipt.md).
2. [Dataset register](research/datasets.md), [actual initial source checks](research/qualification/initial-source-receipt.md) and [dataset-specific rights](research/dataset-rights.md).
3. [Experiments and paper bundles](research/experiment-publication-plan.md), [priorities](research/analyses.md), [platform comparison prior art](research/platform-comparison-review.md) and [clinical journals](research/journals.md).
4. [Literature map and scheduled watch](research/literature/README.md). PubMed, OpenAlex and Europe PMC receipts support the first review; pre-analysis and post-analysis novelty gates still apply.
5. [Backend contracts](research/backend-replacement-policy.md), [Rust candidates](research/rust-candidate-audit.md), [methylation backend audit](research/methylation-backend-audit.md) and [bounded Rust roadmap](research/rust-port-roadmap.md).
6. [Logical medallion storage](research/medallion-layout.md), [reference resources and hosting](research/resources-hosting-reuse.md), [official local runner policy](research/local-development.md) and [Ponytail decisions](research/ponytail-decisions.md).

## What is now evidenced

- The pinned Conductor submodule was fetched and its project context completed in a real clone. Automatic activation by a particular host application was not observed.
- The three initial public Kabuki archives were downloaded without an application or login. Their exact bytes, SHA-256 identifiers, TAR structure and IDAT headers were checked; see the receipt for counts and limitations. Raw files are outside Git.
- The [Rust API catalogue](tools/catalogue/README.md) resolves all 29 sources through official NCBI/GEO and PRIDE interfaces, retaining 114 source-response receipts. Its 2,532 series–assay memberships represent 2,465 unique GEO assays; these are not independent participant/cohort counts. [T08 is reviewed and archived](conductor/archive/t08_catalogue_20261122/index.md).
- The owner's [limma-rust fork](https://github.com/edithatogo/limma-rust) is derived from **MassDynamics**, a different implementation from the previously inspected sinmojito project. Its original 104-test corpus passed; the subsequent public synthetic R reference adds six tests, with 110 passing in debug/release and 30,840 fresh numerical comparisons. The independently reviewed LM01a increment is archived. Consumer, actual local-runner and methylation acceptance remain pending.
- A weekly literature watch is scheduled, alongside mandatory N0–N3 analysis gates.

## Execution and governance

Use **Rust > Julia > Python > R** among scientifically suitable implementations; a qualified existing C engine can avoid a rewrite. Keep independent numerical references. [Selected-backend qualification T07](conductor/tracks/t07-backend-qualification/index.md) precedes any clinical analysis that consumes it. Optional ports do not block a qualified reference route.

Central policy remains [repository-standards](https://github.com/edithatogo/repository-standards). Conductor is a pinned Git submodule at .agents/plugins/conductor; clone with submodules or initialise them explicitly. Applicable shared GitHub defaults are reused without importing an unrelated template/runtime.

The owner requires official GitHub Actions self-hosted runners for local development acceptance. The fork now has a manual trusted-revision workflow with real checks; registration and observed runs on the owner's machines remain external prerequisites. A cloud command is not that evidence.

## Limits

T00/T01 are **partly complete**, with remaining milestones visible rather than marked passed. Participant independence, final molecular subsets/covariates, reference annotations, institutional research classification and selected-method acceptance must be resolved before disease analysis. Public source permission is not a decision from an institution's ethics office.

Patient files are never committed to Git. The selected three-archive HF mirror is governed by the [exact release manifest](research/releases/2026-11-22/manifest.json); actual upload status is recorded in the publication receipt. No clinical association, diagnostic performance, causal mechanism or perturbation efficacy has been estimated. Disease-level HPO annotations are not participant observations, and two accessions are not automatically independent cohorts.
