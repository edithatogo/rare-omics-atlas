# T01 molecular decisions: source assertion, study eligibility, and audit replay

**Scope:** GSE97362 P1 discovery. See [issue #15](https://github.com/edithatogo/rare-omics-atlas/issues/15) and the [first-science receipt](t01-first-science-2026-11-24.md). This is not a clinical variant classifier, not an ACMG reclassification and not scientific admission.

## Decision policy (before methylation outcomes)

| Original evidence | Molecular eligibility for P1 | Audit requirement |
|---|---|---|
| Source-confirmed KMT2D LOF discovery diagnosis in Butcher 2017, exact S2a study-label join to the explicitly labelled GEO discovery group | Eligible for the source-molecular component only | Cite Methods and S2a, original transcript and reported variant text/consequence; preserve original and derived classifications separately. |
| Explicit pathogenic or likely pathogenic source laboratory classification for the selected disease, supported independently of methylation | Candidate eligible after source/assay linkage and disease-mechanism review | Preserve the source's exact classification, evidence and date/version; do not claim the Atlas assigned ACMG criteria. Applies to candidate GSE116300/IC1 replication only after appropriate source/overlap review. |
| VUS, benign/likely benign, another gene, unresolved diagnosis, conflict or methylation-dependent classification | Hold unresolved/discordant evidence, exclude known out-of-scope cases from the contrast | Document reason; never use methylation-derived signature scores to establish the primary case labels. |
| Source-labelled native control | Not applicable | Verify source control role and material provenance/independence separately. Do not infer that controls were genetically screened. |

The source paper [Butcher et al. 2017](https://doi.org/10.1016/j.ajhg.2017.04.004) reports clinical and sequence-variant ascertainment before methylation analysis, KMT2D LOF as the discovery case definition, and transcript NM_003482.3. Table S2a contains the reported nonsense/frameshift changes. The rule is **exact source membership plus source-reported LOF evidence**, not an inference of pathogenicity from a truncating string. Do not infer PVS1 or an ACMG P/LP class from consequence alone. The [ACMG/AMP consensus](https://doi.org/10.1038/gim.2015.30) and [ClinGen PVS1 guidance](https://doi.org/10.1002/humu.23626) require the gene/disease mechanism, transcript and predicted null effect to be evaluated in context and evidence combined appropriately. If a material conflict ever necessitates new classification, document the gene/disease/inheritance, normalized variant/transcript/build, exact guideline/version, dated independent evidence for each applied or rejected criterion and strength, conflict resolution, final class, reviewer and decision date. No classifier using the methylation outcome and no independent re-adjudication by default.

## Reproduce the exact source decision

Use the original [GEO SOFT](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362&targ=gsm&form=text&view=brief) and [published supplementary PDF](https://pmc-oa-opendata.s3.amazonaws.com/PMC5420353.1/mmc1.pdf), whose size/MD5 are recorded in the [PMC version manifest](https://pmc-oa-opendata.s3.amazonaws.com/PMC5420353.1/PMC5420353.1.json). The existing GEO source SHA-256 and exact supplement size/MD5 are checked before parsing; the actual supplement SHA-256, code hash, decision-ledger hash and sample declaration hash are recorded. The original source decision is separately reviewable. Record the actual source revision, run and extraction-tool version. A changed source or failed exact join holds the comparison; do not relax the checks.

In an appropriate working directory, retain original files under ignored data/bronze and outputs in a new ignored data/silver directory (or ephemeral read-only metadata review directory). No file containing row-level variants, source pseudonyms, clinical text or patient/specimen mapping belongs in Git or public CI artifacts.

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/molecular_replay.py \
  --geo data/bronze/GSE97362.soft --supplement data/bronze/mmc1.pdf \
  --out data/silver/t01-molecular-replay
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml \
  --bin sample-contract -- --input data/silver/t01-molecular-replay/declared-samples.json
```

The second command is expected to return exit 2 (22 held, no scientific admission): molecular eligibility does not establish biological identity or independence. The first command writes a local decision ledger and the unchanged v1 structural manifest; only its aggregate receipt may be shared. The [read-only hosted source workflow](../../.github/workflows/molecular-source.yml) downloads the exact original public sources in an ephemeral directory, runs the same replay, checks the expected structural hold and verifies the control workbook binary without claiming that Table S6 resolves individual control provenance. No clinical assay matrix, patient-level output, or disease effects are uploaded. Hugging Face is storage only. Synthetic unit tests cover exact joins, VUS non-promotion, duplicate/ambiguous evidence, source-pin mismatch and deterministic aggregate boundaries; real source and strict hosted outcomes remain separate.

## Remaining decisions

Receive source-supported biological sample and family independence or a scientifically defensible restriction/dependence-aware plan; inspect S6 control provenance rather than invent identifiers; repeat design checks after selected QC. Preserve the historical 341-assay inventory and declarations; a 22-assay replay is a separate selected-subset review, not an update to the global counts. Qualify the actual selected R/Bioconductor route on independent technical/synthetic inputs, then obtain institutional and applicable official-device evidence, complete cohort QC, and freeze N1 before disease inference. No variant reclassification, raw participant data upload or optional numerical port is a prerequisite.
