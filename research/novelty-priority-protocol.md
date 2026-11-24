# Analysis lifecycle: evidence, novelty, priority and publication gates

**Status:** required protocol for every analysis, including reanalysis and later manuscripts. A bounded initial literature review has been executed and an authorised weekly watch is scheduled; see [queries, receipts and study–dataset edges](literature/README.md). Those source checks are not a completed analysis-specific N1 freeze. No custom crawler or monitoring service is built.

| Gate | When | Required dated receipt |
|---|---|---|
| **N0 — decide** | At study selection, before major work | Precise question and clinical endpoint; qualified public sources; patient/control independence; ethics/rights status; closest already published/preprint work; novelty/impact/feasibility and clinical journal fit; proceed / narrow / combine / benchmark-only / hold / stop |
| **N1 — freeze** | **Immediately before analysis** | Rerun targeted searches and document queries, dates, PMIDs/DOIs/preprints, methods/dataset overlap and decision. Freeze estimand, outcome, covariates, sample splits, primary null comparisons, simplest baseline and planned journal |
| **N2 — reappraise** | **After each completed analysis**, before manuscript/follow-on prioritisation | Rerun literature, preprint, repository and method searches. Check for intervening publications; classify independent replication versus incremental or redundant findings; reconsider effect size/precision, clinical interpretability, effort, journal, and whether to stop or refocus. Do not revise the historical N1 |
| **N3 — submit** | Immediately before journal submission or journal transfer | Refresh competing papers, aims/article type, fees, indexing, ethics and AI/data policies, prior-publication declarations and backup journal |

Sources: PubMed, Europe PMC, Crossref/OpenAlex; targeted bioRxiv/medRxiv and early-online journal sites; GEO/PRIDE/BioStudies for new datasets. Query the disease/gene synonyms, accession IDs, methylation/episignature, pathway/network/multiomics, prediction and precise method. Save exact date, queries/filters, hits and rationale; *not found* only means not found in the documented search. Include Goel/Goh/Stuart, 2026, DOI 10.1002/mgg3.70319 in the next background review, without presuming it answers a particular analysis.

**One receipt per gate** in its existing Conductor track, not a new ticketing system: source/search/date; overlap in participants, question, method and outcomes; unresolved uncertainty; selected option; manuscript target; owning commit/reviewer. If a competing study appears, retain results and distinguish an independent replication from a novel mechanism. N2 can legitimately turn a proposed paper into an open benchmark.

## Conditional prioritisation

No scientific score overrides a **hard hold**: uncertain use rights or required institutional review; unusable case/control comparison, unresolvable sample duplication, inadequate molecular confirmation, major confounding or no answerable estimand. Mark these unknown/hold rather than silently approving data.

Existing N/I/F (novelty/impact/feasibility, each 1–5) are subjective *opportunity* scores. Evaluate also clinical usefulness, quality of original controls, sample/power, independent replication, tissue/batch/age matching, provenance and consent, expected effort, novelty decay, journal fit/fees and negative transfer. Do not collapse all inputs to a false numerical probability of publication. Actual gating overrides score.

**Default sequence:** T00 context, T01 source/admission and T07 selected-method acceptance before any consuming analysis; T02 Kabuki as a reproducibility reference even if not worth its own publication; T03 or T05 next depending on data pairing and incremental clinical value; T04 only with sufficient independent disease effects and comparisons to simpler models; T06 separately gated by quantitative functional evidence. The selected method must be qualified before consumption; optional T07 replacements remain conditional. Alter this order at N0/N2 when new work or data changes value.

## Ponytail dependency review at each gate

Before analysis, examine the real consumer and existing qualified language/library. Apply Rust > Julia > Python > R among suitable implementations; a new Rust stage does not require a prior speed bottleneck. For a replacement, identify the capability, portability, maintenance or resource benefit. After analysis, examine correctness, elapsed time/RSS, licensing, maintainability and whether a simpler tool could replace what was used. Record **retain / replace / remove / defer** with real evidence in the track. Use [dependency triage](language-dependency-triage.md) and [scientific backend contract](backend-replacement-policy.md). No preemptive Rust ports, data framework or GPU driver. Reuse the scheduled watch and source APIs rather than building a new crawler.


## Durable experiment-to-literature map

Keep exact queries, query translations, pagination/results, API failures, source dates and PMIDs/DOIs/OpenAlex IDs with the dated review. An edge records whether the paper explicitly reuses an accession, references a source study, uses the same participants or merely cites a related method. These are different assertions. Verify full-text availability statements and GEO relations where abstracts omit accession IDs. A zero-hit search cannot establish that data were never reused.

The weekly watch checks a rolling overlap window for delayed indexing and early-online/preprint revisions, then records only material changes to novelty, dataset use, dependencies or journal fit. N1/N2/N3 are still event-triggered checks even when the weekly watch found no change. Preserve the original N1 if new literature appears later.

### Contribution and expanded-cohort check (24 November)

At every N0/N1/N2, record original measured/deposited data, original derived analyses, Atlas secondary analyses and additional external data/annotations separately in the existing receipt. Specify whether later data are identical measurements, new assay of same specimen, new modality/visit on same person, relatives, expanded partly overlapping cohort, truly distinct participants, or unresolved. New measurements of existing people can answer a new paired, technical, longitudinal or cross-modal question and must not be excluded just because they are not independent biological replicates. Deduplicate within each biological unit; use family/participant grouped splits across all modalities and studies. If shared controls or participant reuse are material, model dependence or restrict and label the claim; unknown pairing cannot support individual-level correlation or independent validation. At N1 predeclare an incremental comparison against the closest original analysis and simpler baseline, the new estimand/uncertainty criterion, data overlap and the smallest necessary additional data. At N2 classify what was actually achieved, including negative/benchmark-only results, rather than equating new workflow execution or source ingestion with a new biological finding. See the [dated gap review](experiment-publication-plan.md#24-november-2026--analytical-gap-and-contribution-review-pre-n1). This update is not the actual N1 freeze.
