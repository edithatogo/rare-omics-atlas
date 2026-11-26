# V01 — bounded source metadata quality assessment (27 November 2026)

**Decision:** metadata is usable for source discovery and prior-art/overlap review. Actual human-event grain, independent cohort membership and eligible clinical estimands remain unverified. This is an N0 input, not an N1 freeze, completed event QC or a clinical analysis. No subject records were acquired.

## Executed metadata profile

Inputs: immutable GitHub revision `5b0f6e645b06ebc7b8a8f0103d2876da7772c574`, [12-record reconciliation](../literature/2026-11-26-v01-reconciliation.json) and [successful PubMed replay receipt](v01-public-source-successor-2026-11-26.json). The profile was calculated from those JSON objects, not from publication participants. Algorithm: count records and distinct numeric-string PMIDs; compare sorted ID arrays of publications, curated studies and replay; count nonempty title/date/journal/URL/PMID, nonnull normalized DOI and duplicates; count positive integer reported primary counts; count design/setting/period/unit completeness and relationships with both endpoints in the PMID set. No summation of heterogeneous sample counts. The exact source receipt reproduced the earlier PubMed response hash.

| Check | Observed | Implication |
|---|---:|---|
| Publication records / distinct PMIDs / valid PMIDs | 12/12/12 | No duplicate publication identifiers |
| PMID join to curated rows and exact source replay | 12/12 | Identity reconciliation at report grain only |
| Complete core bibliographic fields | 12/12 | Metadata coverage, not full text |
| Non-null DOI / duplicate normalized non-null DOI | 10 / 0 | PMID remains the key for missing DOI |
| Setting/period/design/unit description populated | 12/12 | A description may still contain unknown/approximate values |
| Explicit primary count present / absent | 9 / 3 | Different denominators; missing/uncertain counts not imputed |
| Study-level possible/candidate overlap relationships | 4 | Do not pool as independent cohorts |
| Dataset-release/projection relationships | 2 | Do not add releases or occurrence projections |
| Raw studies acquired / clinically admitted study rows | 0 / 0 | Independent eligible cohort count unknown |

Eleven records are clinically oriented and one concerns direct animal observations; the latter is contextual evidence only. The same hospital/period or surveillance network creates a possible dependence component, not an adjudicated duplicate. Retain unresolved trial-reuse and recruitment-period edges. Counts reported as lower bounds or for mixed populations are not common denominators. Do not estimate severity contrasts, prevalence, incidence or treatment effect from this seed.

## Confirmed source semantics and admission checks

The [original 2017 eAtlas catalogue](https://researchdata.edu.au/venomous-jellyfish-database-223-csiro/1356134) documents a 265-record mixed extract, predominantly assembled from media and other reports. The [expanded 2018 catalogue](https://eatlas.org.au/data/uuid/16904861-53e6-4123-a7bb-781f2429629f) describes 1,081 records and a broader scope, while still documenting mixed sting/specimen records, restricted portions of the parent database and incomplete ascertainment. Both pages direct users to the [same public archive landing page](https://nextcloud.eatlas.org.au/apps/sharealias/a/au-nesp-twq-2-2-3-venomous-jellyfish-db-20181130), now named `AU_NESP-TWQ-2-2-3_Venomous-Jellyfish-DB-20181130.zip`. The earlier release may not be independently obtainable from that link. The later metadata confirms CC BY 3.0 AU with specific attribution, supplied metadata and privacy requirements; inspect the actual archive and any embedded restrictions before reuse. The catalogue API previously returned 403; the ordinary archive page requires JavaScript. No original ZIP/CSV was obtained, and a public landing page is not permission for unapproved patient-text processing or public redistribution. Do not use WMS/OBIS to reconstruct restricted records.

| Observed dictionary fields / source | Prospective QC after approved acquisition | Scientific stop condition |
|---|---|---|
| `CSIRO_ID`, `EVENT_TYPE` | Versioned row keys; exact duplicates, sting vs specimen, cross-release membership and unresolved duplicate reports | Unique row ID is not unique human event; no event counts until reconciled |
| `REFERENCE` (2017), `PUBLIC_REFERENCE` (2018), `CURATOR`, `DATA_CODE` | Compare source literals, rights and evidence; distinguish reporting source from care pathway; preserve unknowns | No source-stratified comparison if source membership unresolvable |
| `PATROL`, `HOSPITAL`, `RETRIEVAL` (2018) | Separate beach context, hospital destination and transport; first contact requires explicit evidence | Never use patrol or hospital field alone as source or first-contact label |
| `YEAR`, `MONTH`, `DAY`, `EVENT_TIME`, `DATE_RANGE`, `EXACT_DATE`, `EXACT_TIME` (expanded additions) | Partial dates/time intervals; record precision and contradictions separately; do not fill missing components | No precise temporal comparisons from coarse or uncertain dates |
| `BLOOD_PRESSURE` vs expanded literal `BLOOD_PRESSUREL`; `NAUSEA_VOMITING` vs `NAUSEA` | Compare actual headers and observed values before canonical mapping; preserve literals/units, unknown vs explicit absence | No automatic equivalence of changed clinical semantics |
| `SPECIES_NAME`, `NEMATO_SAMPLES` | Evidence level and documented identification; samples taken does not mean species confirmed | No inferred individual exposure or causal attribution |
| Narrative fields (`EVENT_COMMENTS`, `PATIENT_COMMENTS`, other comments) | Local approved text only; completeness, structured baseline, independently adjudicated source-span checks if justified | No public text, model processing or clinical claims before approved conditions and qualification |

These checks are a preregistration-ready intake checklist, not measurements on absent event data. Apply only on the approved device, first report aggregate completeness and duplicate/unknown dispositions with privacy review; do not commit row-level identifiers, exact dates/coordinates or narrative examples. No new profiling framework needed; use the existing source receipt and simple tabular profiling when data become available.

AIHW [2024 marine animal report](https://www.aihw.gov.au/reports/injury/contact-with-animals/contents/types-of-animals/marine-animals) corroborates the earlier manual national count of 91 Irukandji-coded hospitalisations and crude rate 0.4 per 100,000 for 2021–22; not original workbook verification. [Technical notes, Table 17](https://www.aihw.gov.au/reports/injury/contact-with-animals/contents/technical-notes) distinguish ICD-10-AM `X26.01` (Irukandji) from parent `X26.0` (all jellyfish). The [2024 workbook listing](https://www.aihw.gov.au/reports/injury/contact-with-animals/data) and [later H16 source](https://www.aihw.gov.au/reports/injury/injury-in-australia/data) remain normal authorised download targets. The later [2026 report](https://www.aihw.gov.au/reports/injury/contact-with-living-things) flags a 2016–17/2017–18 collection break and excludes small causes from its ranked figure. Verify actual code levels, suppression, episode versus person counts, rate denominators, coding editions and break before any trend comparison. A parent code is not a syndrome-specific observation. The 121 all-jellyfish figure remains a prior manual benchmark, not independently workbook-verified. The historical AIHW 403 receipt remains unchanged; no alternate access-control bypass, new clinical raw-data transfer or publication has been performed.

## Next decision

V01.01 bibliographic increment has repeatable source evidence; receive its current-base workflow and record actual receiving-main result before acceptance. V01.02 clinical source QC remains pending the actual archive, approved processing and source/record reconciliation. Keep source-byte, redistribution, institutional, official-device, N0/N1, method and independent-unit gates separate. Prioritise authorised source acquisition and source-definition checks before NLP; keep Rare Disease and T06 direction unchanged.
