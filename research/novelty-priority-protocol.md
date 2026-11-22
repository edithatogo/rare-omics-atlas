# Analysis lifecycle: evidence, novelty, priority and publication gates

**Status:** required protocol for future analyses, not evidence of executed searches or analyses. Minimal manual checks at track transitions; no new automation or monitoring service. Every analysis A–L follows these gates, including reanalysis and subsequent manuscripts.

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

**Default sequence:** T00/T01 before any analysis; T02 Kabuki as a reproducibility reference even if not worth its own publication; T03 or T05 next depending on data pairing and incremental clinical value; T04 only with sufficient independent disease effects and comparisons to simpler models; T06 separately gated by quantitative functional evidence. T07 dependency qualification is conditional on real needs. Alter this order at N0/N2 when new work or data changes value.

## Ponytail dependency review at each gate

Before analysis, examine existing qualified language/library and its dependencies; specify what it fails to do. After analysis, examine correctness, elapsed time/RSS, licensing, maintainability and whether a simpler tool could replace what was used. Record **retain / replace / remove / defer** with real evidence in the track. Use [dependency triage](language-dependency-triage.md) and [scientific backend contract](backend-replacement-policy.md). No preemptive Rust ports, data framework, GPU driver or recurring literature crawler.
