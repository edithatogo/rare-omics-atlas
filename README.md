# Rare-Venomics

One clinically oriented research repository, two scientific streams: **Rare Disease (Rare Omics Atlas)** and **Toxinology (including venomics and toxicogenomics)**. The GitHub repository was renamed to `edithatogo/rare-venomics` on 25 November 2026 (repository ID 1467227964 unchanged). The existing Hugging Face dataset identifier `edithatogo/rare-omics-atlas` is retained to preserve the published release history. See [stream ownership and scope](conductor/product.md) and [V01 Toxinology](conductor/tracks/v01-toxinology/index.md). T06 is the conditional cross-stream bridge. The status below applies to the existing rare-disease stream, not to an executed toxinology study.


**Status: official API catalogue published; source/sample validation and a pinned synthetic numerical exchange are implemented and locally verified with native commit hooks. Three raw archives remain locally verified, with their Hub transfer pending. Scientific analyses have not started.** Updated 23 November 2026.

An ontology-linked rare-disease epigenomics programme. The first proposed paper tests whether a prespecified Kabuki methylation result transfers across independent cohorts and platforms, with explicit clinical interpretation limits. A pooled network, extra ontology or change of programming language is not by itself a novel clinical finding.

## Start here

1. [Conductor context](conductor/index.md), [dependency-ordered tracks](conductor/tracks.md) and [initial completion receipt](research/qualification/setup-receipt.md).
2. [Dataset register](research/datasets.md), [actual initial source checks](research/qualification/initial-source-receipt.md) and [dataset-specific rights](research/dataset-rights.md).
3. [Experiments and paper bundles](research/experiment-publication-plan.md), [priorities](research/analyses.md), [platform comparison prior art](research/platform-comparison-review.md) and [clinical journals](research/journals.md).
4. [Literature map and scheduled watch](research/literature/README.md). PubMed, OpenAlex and Europe PMC receipts support the first review; pre-analysis and post-analysis novelty gates still apply.
5. [Backend contracts](research/backend-replacement-policy.md), [Rust candidates](research/rust-candidate-audit.md), [methylation backend audit](research/methylation-backend-audit.md) and [bounded Rust roadmap](research/rust-port-roadmap.md).
6. [Logical medallion storage](research/medallion-layout.md), [reference resources and hosting](research/resources-hosting-reuse.md), [official local runner policy](research/local-development.md) and [Ponytail decisions](research/ponytail-decisions.md).

## What is now evidenced

- The [new bounded source and receiving increments](research/qualification/contracts-hooks-2026-11-23.md) passed 34 strict local gates. T01a reconciles 341 public assay records and holds all actual declarations; T07a receives actual files from the pinned limma producer and passes 6,912 numerical comparisons. Both increments are reviewed and archived. Installed native hooks require exact staged privacy scanning and the full verifier for publishing commits; hosted outcomes remain separately recorded.

- The pinned Conductor submodule was fetched and its project context completed in a real clone. Automatic activation by a particular host application was not observed.
- The three initial public Kabuki archives were downloaded without an application or login. Their exact bytes, SHA-256 identifiers, TAR structure and IDAT headers were checked; see the receipt for counts and limitations. Raw files are outside Git.
- The [Rust API catalogue](tools/catalogue/README.md) resolves all 29 sources through official NCBI/GEO and PRIDE interfaces, retaining 114 source-response receipts. Its 2,532 series–assay memberships represent 2,465 unique GEO assays; these are not independent participant/cohort counts. [T08 is reviewed and archived](conductor/archive/t08_catalogue_20261122/index.md).
- The [Hugging Face dataset](https://huggingface.co/datasets/edithatogo/rare-omics-atlas) contains 14 verified metadata/notice/manifest objects, totalling 2,304,170 bytes, at revision `3f1cb8e64d8e31e7e40773441ba6266714569d05`. The existing estate registry now has one additional canonical entry, preserving its 78 prior entries. The first metadata publication used the Hub editor and official API read-back; the configured GitHub workflow has not run. [Publication evidence and remaining transfer task](research/qualification/hf-metadata-publication-2026-11-22.md).
- The owner's [limma-rust fork](https://github.com/edithatogo/limma-rust) is derived from **MassDynamics**, a different implementation from the previously inspected sinmojito project. The historical baseline passed 104 tests; LM01a added a fresh public R reference with 30,840 comparisons and 110-test debug/release suites. Merged [LM02a](https://github.com/edithatogo/limma-rust/pull/4) adds shared identifier hygiene and strict identity checks for the four fresh cases, with 113 tests passing in each suite. Both bounded increments are reviewed and archived. Seven historical positional cases retain a sample-identity limitation; production consumer, actual local-runner and methylation acceptance remain pending.
- The [literature addendum](research/qualification/paired-literature-addendum-2026-11-22.md) reconciles 13 studies and 17 verified study–dataset edges, including GSE154566. Possible overlap between the two E-Risk paired-array reports remains unresolved.
- A weekly literature watch is scheduled, alongside mandatory N0–N3 analysis gates.

## Execution and governance

Use **Rust > Julia > Python > R** among scientifically suitable implementations; a qualified existing C engine can avoid a rewrite. Keep independent numerical references. [Selected-backend qualification T07](conductor/tracks/t07-backend-qualification/index.md) precedes any clinical analysis that consumes it. Optional ports do not block a qualified reference route.

Central policy remains [repository-standards](https://github.com/edithatogo/repository-standards). Conductor is a pinned Git submodule at .agents/plugins/conductor; clone with submodules or initialise them explicitly. Applicable shared GitHub defaults are reused without importing an unrelated template/runtime.

The owner requires official GitHub Actions self-hosted runners for local development acceptance. The fork now has a manual trusted-revision workflow with real checks; registration and observed runs on the owner's machines remain external prerequisites. A cloud command is not that evidence.

## Limits

T00/T01 are **partly complete**, with remaining milestones visible rather than marked passed. Participant independence, final molecular subsets/covariates, reference annotations, institutional research classification and selected-method acceptance must be resolved before disease analysis. Public source permission is not a decision from an institution's ethics office.

Patient files are never committed to Git. The current Hub publication is the [metadata subset](research/releases/2026-11-22/hub-staging/staging-publication-manifest.json); the [full release manifest](research/releases/2026-11-22/manifest.json) still describes a pending three-archive mirror. Bronze presently links upstream originals and local integrity receipts. No clinical association, diagnostic performance, causal mechanism or perturbation efficacy has been estimated. Disease-level HPO annotations are not participant observations, and two accessions are not automatically independent cohorts.

## Strict development verification

[![Codecov](https://codecov.io/gh/edithatogo/rare-venomics/graph/badge.svg)](https://app.codecov.io/gh/edithatogo/rare-venomics) — [coverage dashboard](https://app.codecov.io/gh/edithatogo/rare-venomics).

The [repository integration contract](research/repository-integration.md) assigns numerical ownership to limma and source/receiving ownership to atlas. Atlas's strict command runs an actual synthetic file exchange against an immutable limma commit and its independent R references. It also tests the local source/sample boundary; neither code contract admits a dataset for inference.

Install and run the pinned checks from the repository root before new code changes and after each increment:

```sh
uv sync --project tools/hf-release --frozen --python 3.15.2
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/bootstrap.py
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

See the [CI contract](research/ci-plan.md) for prerequisites, exact scope, receipts and template alignment. Hosted CI and the trusted manual official-device workflow reuse this command. The atlas code licence is unresolved; code checks do not establish Community Standards, scientific or actual-device acceptance.

Install the [native pre-commit hook](research/ci-plan.md#install-the-native-pre-commit-hook) in each clone before committing. It runs the pinned central privacy scanner on the actual staged candidate and the same strict verifier, refusing incomplete staging, missing tools or failed checks.
