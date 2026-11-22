# Living literature map

**Baseline completed 22 November 2026.** These files record executed, targeted metadata/full-text checks for the [platform and prior-use review](../platform-comparison-review.md). They contain citation metadata, accession relationships and retrieval receipts; article abstracts and full-text extracts are not committed.

## Files

| File | Contents and evidence boundary |
|---|---|
| [PubMed searches](2026-11-22-pubmed-searches.json) | Three exact queries, query translations, warning lists, pagination receipts and citation metadata: 64 platform-comparison results, 3 accession-query results, 65 broad Kabuki/modelling results. All pages for these queries were retrieved; selected relevant studies received full-text checks. Counts are not counts of eligible datasets or a systematic-review result |
| [OpenAlex seeds](2026-11-22-openalex-seeds.json) | Exact request URL, timestamp, HTTP 200 and ten DOI-resolved works. IDs support later citation tracing; this request did not execute a forward-citation census or establish dataset reuse |
| [Study–dataset edges](2026-11-22-study-dataset-edges.json) | Ten study metadata records, fifteen explicit generated/reused edges, four parent/subseries relationships, one unresolved EPIC linkage and a source-date conflict |
| [Edge table](2026-11-22-study-dataset-edges.tsv) | The same fifteen verified edges in a simple tabular interchange format |
| [Europe PMC receipts](2026-11-22-europepmc-receipts.json) | Eight actual XML request outcomes: two HTTP 200, five HTTP 500, one timeout. Successful accession mentions are retained; full-text passages are omitted |

## How to extend the record

For each search event retain the retrieval date/time, provider, exact query or request URL, translated query if supplied, pagination, returned counts, warnings and failures. Date provider outputs separately from the publication's electronic and issue dates. Link a changed conclusion to the exact evidence record.

For each study–dataset relationship retain the PMID/DOI, accession, relationship type, analysis type, primary source, evidence location, review date and unresolved sample restrictions. Separate **generated**, **reused**, **benchmark-used** and **cited-only** relationships. Citation counts, a reference-list mention and an exact-accession search hit are leads until context establishes use. Parent/subseries relationships do not create independent cohorts.

The current edge table is deliberately bounded. GSE218186's relation to the Cuvertino higher-order analysis remains unresolved in this retrieval slice; methods name the study by bibliographic reference. GSE97362's use in the Pacemaker publication is explicit, but affected-case inclusion is not established. Neither relationship establishes independence or analysis eligibility.

## Important search limits

PubMed omitted GSE86829, GSE86831 and GSE116300 from the translated exact-accession query and returned warnings. Thus absent results cannot prove unused data. Search parent/subseries, titles/DOIs, disease synonyms and methods; inspect full text and supplements; trace citing/cited papers. Broad KMT2D and EPIC searches include unrelated cancer and cohort-name hits.

For Cuvertino DOI 10.1093/bib/bbae667, PubMed/OpenAlex return 22 November 2024; the publisher electronic date is 19 December 2024 and the issue is 2025. Preserve provider values and the publisher source. Different date fields should not silently overwrite one another.

Public article access, public raw-data access, source-specific reuse/redistribution rights and participant inclusion are separate facts. These metadata records do not authorise human-data analysis or Hugging Face release.

## Enabled recurring watch and per-analysis gates

The weekly literature watch was **created and enabled on 22 November 2026**, scheduled for approximately **Monday 08:00 Australia/Brisbane**; its first scheduled run is **23 November 2026**. Creation was confirmed by the coordinating task. This records scheduling, not a completed future search or an automatic repository update.

The recurring watch supplements [N0–N3](../novelty-priority-protocol.md):

- **N0:** choose a distinct claim and assess current overlapping data, methods and clinical value.
- **N1:** refresh before execution; freeze the estimand, input/split, outcomes, methods and intended journal.
- **N2:** search after results; decide retain, combine, reframe, hold or stop without revising frozen outcomes to fit new literature.
- **N3:** refresh before journal submission or transfer, including journal scope/policies and dependency suitability.

Record each future run as a new dated event. Do not infer a negative finding from an unsuccessful API request or describe a scheduled run as completed.


The later source-rights pass added six explicit Wheeler study–dataset edges (three reused patient series and three generated model/reference series), bringing this seed edge register to 15. These additions come from the primary Methods/Data Availability and GEO source checks; they were not part of the original ten-DOI OpenAlex request. The original API receipts remain unchanged.

The [schedule receipt](watch-schedule.json) records creation-time status and timezone. Its last-run field was empty at creation; a scheduled future run is not a completed search.
