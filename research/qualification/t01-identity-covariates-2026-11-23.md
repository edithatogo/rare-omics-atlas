# T01 identity and covariate curation — 23 November 2026

## Bounded result

Three fresh official GEO series records reconcile to the retained **341 assay records**. The GSE116300 design statement now explains the **27 versus 29** difference at group level: it describes 27 probands and two additional clinic recruits subsequently dropped as not having Kabuki syndrome. It does not name the two corresponding assay records. No sample identity, molecular eligibility, overlap or analysis partition was assigned.

The existing declaration disposition remains **257 held, 84 KMT2D-review-scope exclusions and zero ready/admitted**. This increment adds a source-specific covariate availability audit and inheritance evidence for ten previously established exact paper-to-GEO label joins. It creates no new donor–specimen–assay links. The [machine receipt](t01-identity-covariates-2026-11-23.json) contains exact source hashes, predicates and local derivation identities. The [T01 parent](../../conductor/tracks/t01-sources/plan.md) remains open.

Base: `aa2d24502cd0dffc070a5c9c09651d95c5b516e8`. All row-level source work remains under ignored `data/bronze/` and `data/silver/`; these two committed receipts contain aggregates only.

## GSE116300: resolved source explanation, unresolved named bridge

The [official series text](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=self&form=text&view=full) describes 48 study inputs: four synthetic methylation controls, six parental controls, nine age-matched controls, 27 probands with a Kabuki phenotype and two additional clinic recruits subsequently excluded as not having Kabuki syndrome. It also reports randomization across four 12-well chips.

The series accession list exactly matches the 44 retained GEO records: 29 case-labelled assays, nine controls and six case-parent assays. This is an inventory check. Neither agreement of totals nor the case labels identifies the two excluded recruits or supplies the paper's `KS` to GEO `PAT` crosswalk. No additional record was excluded by this review. The [previously recorded](t01-source-followup-2026-11-23.json) 36 described case/control arrays and 38 samples used for ancestry QC remain distinct source-reported sets.

The nine controls' reported age matching is useful study provenance, but individual ages remain absent from the GEO characteristics. Likewise, source randomization does not establish the rank or independence of a future analysis design. [Retained sample source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=gsm&form=text&view=brief)

## Covariates tied to the existing review roles

These counts were recomputed from the original SOFT characteristics and the unchanged local declarations. A `case` role denotes the current review candidate, not confirmed eligibility. Numeric, left-censored, explicitly missing and absent age fields remain separate.

| Series and existing review role | Assays | Numeric age | Left-censored age | Explicit age `NA` | Age not supplied | Sex supplied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GSE97362 candidate cases | 37 | 37 | 0 | 0 | 0 | 37 |
| GSE97362 source controls | 125 | 124 | 0 | 1 | 0 | 125 |
| GSE97362 scope exclusions | 73 | 71 | 2 | 0 | 0 | 73 |
| GSE116300 candidate cases | 24 | 0 | 0 | 0 | 24 | 24 |
| GSE116300 source controls | 9 | 0 | 0 | 0 | 9 | 9 |
| GSE116300 scope exclusions | 11 | 0 | 0 | 0 | 11 | 11 |
| GSE218186 candidate cases | 7 | 0 | 0 | 0 | 7 | 0 |
| GSE218186 source controls | 55 | 0 | 0 | 0 | 55 | 0 |

Across the 68 candidates, 37 have numeric age and 61 have recorded sex. Across the 189 source controls, 124 have numeric age, one has explicit `NA`, 64 have no age field and 134 have recorded sex. The two left-censored ages belong to the current scope-excluded source group; they were not converted to exact numbers. None of the 341 retained GEO characteristic sets supplies an explicit cell-fraction covariate. This last finding concerns those metadata fields, not the existence of clinical measurements elsewhere. [GSE97362](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362&targ=gsm&form=text&view=brief), [GSE116300](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=gsm&form=text&view=brief), [GSE218186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186&targ=gsm&form=text&view=brief)

The native GSE97362 KMT2D discovery comparison has numeric age and recorded sex for all 11 source cases and 11 source controls. This identifies a usable source of declared covariates when that comparison is eventually specified; it does not qualify its molecular subset, identities, batch design or independent subjects. No covariate was imputed or inferred from methylation.

## Existing exact joins: additional inheritance provenance

All ten sample labels in the original paper's Table 2 uniquely match the complete GEO description field in the KMT2D sequence-variant group. The predicate flattens XML inline text and collapses whitespace; it performs no number extraction, fuzzy matching or label translation. Those joins were already established in the [prior curation](t01-cohort-curation-2026-11-23.md). This increment attaches the table's source-reported inheritance: **two de novo and eight inherited**. The local join sidecar is hashed in the machine receipt; no study pseudonyms or variants are reproduced here. [Original article and Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC5420353/)

Inheritance does not identify a parent or establish biological independence. The paper describes these ten as the uncertain-variant group; its methylation-signature classifications remain separate from independent molecular eligibility. All ten declarations stay held.

The same article identifies three sources for controls, with further information in supplementary Table S6. These origins have not been assigned to individual assays. Its cohort-level ancestry statements and separate cell-type robustness assessment also do not supply per-assay ancestry or cell-fraction vectors. Original supplementary variant, phenotype and control-provenance tables remain relevant unresolved inputs. [Original article XML](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=5420353)

## Provenance, access and executed checks

The new plain-text series responses were retrieved on 23 November 2026 UTC:

| Series | Bytes | SHA-256 |
| --- | ---: | --- |
| GSE97362 | 10,344 | `5159bb5379cca45f702d49dcf65b2d1eeba94bc72936df3c28ed0b3bbce3e342` |
| GSE116300 | 5,094 | `d452f5c96e400ee27759307b593901675ab13d2919f02fbd12eccdfbf91fb5d5` |
| GSE218186 | 4,955 | `7be3fdb9903d099eaab10d84ed4585c7ed65c528af47d3533099acfd349248d3` |

Their retained paths are `data/silver/qc-semantics-curation-20261123/<accession>.series.soft`. The existing sample SOFT files and complete Butcher article XML were checked against their prior hashes before parsing. The series/sample/catalogue accession sets agree exactly for all three series. The declaration and existing contract-report hashes also remain unchanged.

The actual aggregation command was:

```sh
python data/silver/qc-semantics-curation-20261123/curate.py
```

It completed with Python **3.12.14**, exit **0**. Two initial diagnostic-script assumptions were corrected to the existing report schema and the explicitly selected three-series catalogue scope; their failed outcomes are retained locally. No source discrepancy was waived. The command did not run the sample-contract CLI again or perform a scientific analysis. Combined strict verification and the actual commit hook are recorded by the integration owner separately.

Public lookup of the publisher article encountered a non-retryable identity-provider redirect, and the GEO HTML viewer returned a browser challenge. The documented GEO text endpoints independently returned `geo/text` responses without credentials or challenge handling. No original supplement was obtained, and no new supplement download was attempted. The [six earlier failed retrievals](t01-source-followup-2026-11-23.json), including their access boundaries and original hashes, are preserved; the previously blocked endpoints were not retried.

## Next curation boundary

The highest-value remaining input is an explicit original sample/variant bridge identifying the GSE116300 paper records and the two excluded clinic recruits. Original case-variant and control-provenance tables for GSE97362 and GSE218186 remain necessary for the affected claims. An array key, equal count, source inheritance label or methylation-derived classification cannot replace these links.

Use the recorded covariate availability when selecting the eventual comparison and its requirements. Keep native controls explicit, declare handling of missing/censored covariates, and verify identities, independence and the selected technical QC before admission. Source curation and independent technical implementation can continue in parallel; this receipt does not close T01 or authorize disease inference.
