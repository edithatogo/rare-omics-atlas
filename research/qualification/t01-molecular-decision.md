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

### Control provenance receiving increment

The original source workflow now also inspects the hash-verified S6 workbook with a pinned read-only XLSX reader. It emits only worksheet-level exact whole-label match counts, recognised explicit source-category counts, and the presence of family/specimen headers. No source labels or rows are published. This is a diagnostic for locating the original source crosswalk, not automatic control-origin or participant-independence admission. An unresolved match remains held. The earlier source replay and failed formatting gate are preserved in their original run receipts.

### Targeted control and design receiving follow-up

The prior source-only run established all 11 exact control-label matches in column 1 of worksheet 3. The next run inspects only recognised generic headers, aggregates explicit recruitment-source categories and counts the coverage of actual identity fields, with no patient-level release. It also calculates the pre-QC metadata-only rank, residual degrees of freedom, case-coefficient variance factor and leave-one-assay-out/mixed-chip sensitivity using a pinned NumPy release. None of these outputs establishes biological independence, post-QC rank or scientific admission. An unrecognised source code or missing identity evidence remains unknown.


### Actual 24 November source and design receiving receipt

[Run 45384060198](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45384060198) on `dd3a16621406b5812bcfcde56607399c87f89ff2` passed the original-source replay after the [failed run 45383531427](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45383531427) exposed unnormalised SOFT line endings. All 11 selected controls matched S6 worksheet 3; 11/11 recorded sex and 11/11 comparable numeric age values agreed with GEO. No explicit control recruitment category, participant, specimen or family fields were found; all 11 control origins are unresolved, and no workbook age unit is inferred. All 11 case molecular joins retained their source diagnoses; no Atlas ACMG reclassification. The structural validator returned expected exit 2: 22 held, 0 excluded, 0 ready, no admission.

Metadata-only design (NumPy 2.2.6, Python 3.12.12, rank tolerance 1e-10): age/sex/group/intercept rank 4/4, n=22, residual df=18; chip-adjusted rank 8/8, residual df=14, case variance factor 0.3915115395397416. Mixed-chip restriction rank 5/5, n=15, 10 cases, df=10. All 22 leave-one-assay-out runs retained full rank and case estimability (minimum residual df=13; maximum case variance factor 0.5022605634795271). These checks are not post-QC rank, biological independence or scientific admission. The strict PR replay [45384060122](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45384060122) passed actual staged hook, privacy, dependency and Codecov patch on the prior base; fresh checks on the current base are required before integration. See [issue #15 receipt](https://github.com/edithatogo/rare-omics-atlas/issues/15#issuecomment-7130570095). Institutional, device, scientific QC, overlap and N1 gates remain held. No human array processing.

### Integration receipt — 24 November 2026

PR [#16](https://github.com/edithatogo/rare-omics-atlas/pull/16) received current-base native hook, strict, privacy, dependency, provider and source replay passes at 7282dc56daed3f0e47057b531bdd61d703cb785d (strict [45387805943](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45387805943), source [45387806006](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45387806006)); merge `73f082b7b9cf6128d33f36edb9d24d4f0838cd8f` has exact tested tree 87e21cc551fa6eb2e0489c62b05b6c845e3c9355. [Merged-main strict CI 45396711579](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45396711579) passed. The earlier pending integration wording is historical. T01 source replay is received, not cohort admission: 22 held, zero admitted, origin and independence unresolved. See [issue #15](https://github.com/edithatogo/rare-omics-atlas/issues/15#issuecomment-7131952531).
