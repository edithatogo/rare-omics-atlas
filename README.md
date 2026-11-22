# Rare Omics Atlas

**Status: research-planning scaffold only. No analytical source code, executable pipeline, data download or scientific result is included.**

An ontology-linked, public-data rare-disease epigenomics programme, designed to test cross-cohort reproducibility, cross-disease regulatory inference and (only later) independently testable molecular responses to toxins.

**Repository:** https://github.com/edithatogo/rare-omics-atlas . Local planning snapshot, 22 November 2026; no analysis or data download has been performed.

## Start here

1. [Conductor index](conductor/index.md) and [tracks](conductor/tracks.md).
2. [Proposed public datasets](research/datasets.md); every record is **candidate**, not independently qualified.
3. [Public access, ethics and rights triage](research/source-access-ethics.md), [backend replacement protocol](research/backend-replacement-policy.md), [Analysis priorities and scoring](research/analyses.md), [clinical journal strategy](research/journals.md), [language/data contracts](research/interoperability.md) and [Ponytail decisions](research/ponytail-decisions.md).
4. Rust replacements are managed under [conditional T07](conductor/tracks/t07-backend-qualification/index.md), not a universal plugin framework.
5. Follow the [scientific workflow](conductor/workflow.md) before any data is processed or code is written.

## Repository governance

- Central standard: https://github.com/edithatogo/repository-standards (scientific/native and research/data controls); consumer context remains locally authoritative.
- Gemini Conductor source is recorded as a **pinned Git submodule** at `.agents/plugins/conductor` in the repository's Git tree. Run `git submodule update --init --recursive` from a GitHub-connected working clone. Its bytes were not fetched in this offline planning environment.
- Use shared GitHub community defaults and relevant existing starter files rather than copy competing sets of templates. The `template-solo-data` starter is Python-oriented and is not required for this documentation-first project. Only adopt `template-solo-rust` if a Rust crate is later justified.
- No mandatory second human reviewer or CODEOWNERS dependency; maintain one writer per path and evidence-based merge gates.
- Never commit human participant files, restricted data, credentials or large raw assay files. A public GEO page does not establish unrestricted redistributability of derived individual-level material.

## Scope boundaries

Metadata discovery is not patient-level availability. A disease-level HPO association is **not** an observed phenotype in a study participant. Two GEO accessions are not necessarily independent cohorts. Toxin proteomics does not measure the host response. Literature overlap does not establish causal mechanisms. New model complexity must outperform prespecified simple baselines.

**Not yet done in this planning snapshot:** Conductor plugin activation, data-file transfer and checksum verification, participant-level rights/ethics determination, dependency installation, statistical analysis, numerical qualification, hosted checks or any scientific result. GitHub publication and initial submodule check are separate deployment/verification steps, not evidence of activated tooling.
