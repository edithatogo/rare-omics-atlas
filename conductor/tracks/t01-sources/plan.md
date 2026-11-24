# T01 — initial intake and remaining admission work

- [x] **T01.01a:** Build an initial accession register, including paired platform references and explicit prior-use edges. This is a seed inventory, not an exhaustive count of rare-disease cohorts.
- [ ] **T01.01b:** Extend and qualify the inventory as each additional disease is selected.
- [x] **T01.02a:** Qualify five initial gene-defined MONDO/OMIM disease mappings and pinned HPO/HPOA coverage from actual source bytes; see [ontology receipt](../../../research/qualification/ontology-source-receipt.md).
- [ ] **T01.02b:** Apply those mappings to eligible participant/assay records and validate the actual selected library/consumer semantics; disease-level HPO remains separate from participant observations.
- [x] **T01.03a:** Retrieve initial three series/sample metadata and record aggregate diagnostic/control/assay categories.
- [x] **T01.03c:** Curate source roles, molecular categories/crosswalk limits, native controls, technical array links, missing covariates and explicit study-data reuse; replay the 341-record KMT2D review inventory through the existing contract. [Actual source receipt](../../../research/qualification/t01-cohort-curation-2026-11-23.md): 257 held, 84 review-scope exclusions, zero admitted. This does not close T01.03b.
- [ ] **T01.03b:** Freeze the actual molecular subset, participant/control independence and covariate-complete analysis manifest. No blanket acceptance of all clinically labelled Kabuki cases.
- [x] **T01.04:** Map verified prior studies to datasets and revise the platform/network novelty claims; retain unverified edges explicitly.
- [x] **T01.05a:** Download GSE97362, GSE116300 and GSE218186 raw archives; record exact byte counts/SHA-256, TAR structure, paired channels and IDAT headers.
- [ ] **T01.05b:** Perform scientific sample/probe QC with the selected qualified preprocessing route; qualify new sources when selected.
- [x] **T01.06a:** Review source use/distribution notices and document the institutional exemption/review route.
- [ ] **T01.06b:** Record the institution's applicable research classification/determination before disease inference. This is not a requirement to obtain new consent from every public-data author.
- [x] **T01.07a:** Execute a bounded PubMed/OpenAlex/Europe PMC prior-art review and create the weekly literature watch.
- [ ] **T01.07b:** Execute and freeze analysis-specific N1 immediately before E2/E3. The current source review is not a frozen scientific protocol.
- [x] **T01.08a:** Reuse the existing HF full MONDO snapshot and official HPO/HPOA release; actual bytes and hashes match official release metadata.
- [ ] **T01.08b:** Qualify Orphadata or other source products only when a selected consumer needs them; do not make every optional reference a prerequisite.
- [ ] **T01.09:** Add only resources required by the selected analysis, initially disease identifiers/manifests, then Reactome/GO for a pathway consumer.
- [x] **T01.10a:** Assess per-source and per-artifact HF eligibility in the rights register.
- [ ] **T01.10b:** When an actual release is selected, complete file-specific notices/disclosure/hosting review. No human-data release has been made.

## Next executable batches

The T01 owner takes these in order, using the [shared execution rule](../../tracks.md#executing-one-ready-batch). Public source reconciliation and synthetic contract implementation can proceed while an institution's analysis determination is outstanding. None of these rows admits a patient cohort by implication.

**Completed bounded increment, 23 November 2026 Australia/Brisbane:** [T01a](../../archive/t01a_sample_contract_20261123/index.md) reconciles all 341 public assay IDs and provides the strict local declaration command. Its synthetic and CLI tests, independent review and all 34 combined strict checks passed before archive. The actual input is entirely held. T01.03b and T01.02b retain their scientific/consumer scope and remain open.

| Batch / existing tasks | Inputs and action | Output and acceptance |
|---|---|---|
| A: T01.01b / .03b, resolve the selected analysis declarations | Receive the [T01a source receipt](../../../research/qualification/t01-sample-contract-2026-11-22.md), the committed catalogue, rights register and original study supplements. Start with GSE97362 11+11 native discovery; published Table S2a independently establishes all 11 source molecular diagnoses by exact study-label joins. Use the [versioned source molecular decision replay](../../../research/qualification/t01-molecular-decision.md), including source classification, exact evidence locator, original input and decision hashes. No new variant adjudication is needed. Use published recruitment/provenance when adequate, without seeking extra private identifiers; resolve material specimen/family/overlap and control-origin uncertainty or specify a defensible restriction/sensitivity. Review GSE116300 and GSE218186 separately only as candidate replication. See [24 November first-science receipt](../../../research/qualification/t01-first-science-2026-11-24.md). Review evidence for donor–specimen–assay links, molecular subset, native controls and available covariates. Preserve exact source references and unknowns; do not derive participants from assay counts or infer private identities. | Local `data/silver/cohort-admission/<analysis-id>/declared-samples.json` using the implemented contract, with source-bound covariate/exclusion evidence as required by the chosen analysis. Unknown identities remain null and unresolved declarations remain held. Every curated value must have an actual source; assay-set agreement alone cannot resolve participant reuse. |
| B: T01.02b / .03b, run the implemented structural review | Run `cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml --bin sample-contract -- --input data/silver/cohort-admission/<analysis-id>/declared-samples.json`. Preserve stdout and exit status locally. Inspect repeated participant/specimen and cross-partition/role reasons; source URL/hash syntax is a declaration, not verification. The T01a tests already exercise negative and synthetic boundaries; extend only for a concrete new supported case. | Deterministic `ready_for_review` / `held` / `excluded` report with public assay identifiers and reasons. Exit 1 rejects invalid input; exit 2 holds unresolved or entirely excluded inputs; exit 0 means structural readiness for source review. Every result keeps scientific admission false and participant count unknown. Code changes require the existing Rust tests and full strict entry point. Clinical/source review continues independently of structural success. |
| C: T01.02b / .08b / .09, selected reference assets | Use `research/registries/initial-disease-crosswalk.tsv` and the ontology receipt. Select only the platform/build masks and annotation versions required by T07.02, then retrieve/check their actual bytes and licence. Test ID joins against those versions; keep disease-level HPO separate from observed participant phenotypes. | Source-bound local annotation files under `data/reference-cache/`, hashes and mapping/coverage counts in the admission receipt. Pass on exact selected joins, understood missingness and compatible genome/platform semantics. Optional resources with no consumer stay deferred. |
| D: T01.05b / .06b, admission | Receive the exact preprocessing/QC contract from T07.02 and the applicable institutional determination. Execute that qualified technical QC on the admitted local inputs, recording command, feature/sample exclusion reasons and input/output hashes. Reserve clinical replication effects as specified at N1. | Local sample/probe QC tables and a cleared admission decision: selected / held / excluded per cohort, with exact remaining reasons. Pass only when molecular subset, independence, estimability, rights, QC and the applicable determination all satisfy the specification. A missing institutional receipt holds disease inference, not metadata work. |
| E: T01.07b, hand off to T07.02b | Repeat the analysis-specific sources/queries required by `research/novelty-priority-protocol.md`; combine batch A–D evidence with the chosen method contract. | One immutable versioned N1 receipt in the consuming track, naming discovery/replication roles, contrasts, features, covariates, negative controls and decision. This prepares T07 qualification; it does not run T02. |

The validator's exact fields, exit codes, tests and actual held source replay are in the [T01a receipt](../../../research/qualification/t01-sample-contract-2026-11-22.md). Reuse that boundary; no new database, orchestration service, scoring framework or generic model API is needed.

### Catalogue replay or refresh, only when the batch requires it

Run the existing catalogue command from `tools/catalogue/README.md` with `--offline` and an integrity-valid local cache for a replay. For a new source snapshot, choose a **new dated output directory** and use `--refresh`; never overwrite the 2026-11-22 snapshot. Require zero failed records and inspect the summary's series memberships versus distinct assay accessions. Neither value is an independent-participant count. A missing cache is not an offline pass, and catalogue success does not satisfy batch D.

### Blocker ownership

The T01 owner resolves source/identity/annotation questions through the cited records; the institution owns its actual determination; the T07 owner owns the selected numerical/QC contract. Record a hold against only the affected accession or analysis. The optional T09 raw mirror and any unneeded ontology/port are not admission prerequisites.

### Source follow-up — 23 November 2026

The [aggregate follow-up receipt](../../../research/qualification/t01-source-followup-2026-11-23.json) records six bounded public retrieval attempts for the original GSE97362/GSE116300/GSE218186 publication material: **zero usable new supplement/PDF files and zero new named assay-to-paper joins**. API/server errors, two browser-challenge HTML responses and a publisher HTTP 403 were retained locally. One candidate publisher download URL remains unverified; its HTTP 503 does not establish file existence or access policy. The aggregate projection retains the original receipt SHA-256 and primary URLs without publishing response files or ephemeral tool citation IDs.

The GSE116300 article distinguishes **27 sequenced probands, 36 described case/control arrays and 38 QC-passing samples used for ancestry principal components**; not all 38 belong to the analytical set. GEO contains 29 case-labelled assays, 9 controls and 6 case-parent assays. Agreement between the 38 nonparent assay count and the paper's QC count does not establish a named join or identify the two additional case-labelled assays. The `KS`/`PAT` crosswalk remains unresolved.

The prior declaration and structural-review files were rechecked against their recorded hashes: **257 held, 84 KMT2D-review-scope exclusions and 0 ready for review remain unchanged**. No participant count, molecular eligibility, biological independence or scientific admission was inferred. T01.03b stays open. The T01 curator resumes the affected joins when valid original source material supplies an explicit sample/variant bridge; participant/specimen, overlap and required-covariate holds remain until their own evidence is available. Independent preprocessing/QC qualification may continue.

## Receiving record

### Identity and covariate increment — 23 November 2026

The [new aggregate source receipt](../../../research/qualification/t01-identity-covariates-2026-11-23.md)
retains three fresh official series texts and exactly reconciles all 341 assay
IDs. GSE116300 explicitly describes 27 probands plus two clinic recruits later
dropped as non-KS; the two are still not named in an assay crosswalk. Ten existing
exact GSE97362 Table 2/GEO description joins gained inheritance provenance (two
de novo, eight inherited), with no new participant/parent/specimen link.

Covariate availability is now recorded by existing review role: 68 candidate
cases have 37 numeric ages and 61 recorded sexes; 189 source controls have 124
numeric ages, one explicit missing age and 134 recorded sexes. The native
GSE97362 11-case/11-control discovery comparison has age and sex supplied for all
22 assays, while molecular eligibility, identity, independence and design remain
held. No values were imputed or inferred from methylation.

The declarations remain 257 held, 84 review-scope exclusions and zero
ready/admitted. First receive the selected GSE97362 discovery comparison using the
source molecular and design evidence; resolve material control provenance and
independence, then apply batch A/B's existing structural review. No contemporary
variant reclassification is an analysis requirement. See [receiving issue #15](https://github.com/edithatogo/rare-omics-atlas/issues/15). The separate native QC v2 technical pass does not
clear those identity, covariate or institutional requirements.

Owner/integrator: ChatGPT with parallel source and literature review under Ponytail. **In progress; initial public intake complete, scientific admission pending.**

Evidence: [initial source checks](../../../research/qualification/initial-source-receipt.md), [T01a source/contract checks](../../../research/qualification/t01-sample-contract-2026-11-22.md), [rights](../../../research/dataset-rights.md), [literature receipts](../../../research/literature/README.md), [platform review](../../../research/platform-comparison-review.md). All source/header and structural declaration checks are distinct from statistical QC, cohort independence and institutional approval.

### 24 November contribution and cohort-extension receiving rule

Apply the [dated analytical gap review](../../../research/experiment-publication-plan.md#24-november-2026--analytical-gap-and-contribution-review-pre-n1) under existing T01.01b/.03b/.04/.07b, not a new track. Search for later assays/phenotypes on existing cohorts as actively as genuinely new cohorts. Maintain source-established identity and pairing evidence, specimen/time/tissue, family/reuse, original assay/processing level and original analytical role in the existing local manifest/source receipt. Separate actual measured/deposited inputs, source estimates/results, Atlas operations and additional external data; count participants, specimens and assays separately. Same-person new data may support paired/longitudinal/cross-modal inference after admission; use grouped dependence-aware designs, not independent replication. Hold unresolved pairings only for the claim requiring them. The Sotos 6 exact-title candidates and ADNP 36+57 assay-label mismatch are actual aggregate metadata findings, not admission. Candidate GSE199836 and additional model/request-only sources are in [dataset inventory](../../../research/datasets.md#additional-measurements-and-cohort-reuse--24-november-review); reconcile the existing rights/edge registers only when source-specific conditions and roles are evidenced. No new mandatory modality or human-data cloud access. Current T01 source/control/family/overlap, institutional and post-QC holds remain; N1 stays draft until required gates are received.
