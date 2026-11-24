# Living literature map

**Baseline completed 22 November 2026.** These files record executed, targeted metadata/full-text checks for the [platform and prior-use review](../platform-comparison-review.md). They contain citation metadata, accession relationships and retrieval receipts; article abstracts and full-text extracts are not committed.

## Files

| File | Contents and evidence boundary |
|---|---|
| [PubMed searches](2026-11-22-pubmed-searches.json) | Three exact queries, query translations, warning lists, pagination receipts and citation metadata: 64 platform-comparison results, 3 accession-query results, 65 broad Kabuki/modelling results. All pages for these queries were retrieved; selected relevant studies received full-text checks. Counts are not counts of eligible datasets or a systematic-review result |
| [OpenAlex seeds](2026-11-22-openalex-seeds.json) | Exact request URL, timestamp, HTTP 200 and ten DOI-resolved works. IDs support later citation tracing; this request did not execute a forward-citation census or establish dataset reuse |
| [Study–dataset edges](2026-11-22-study-dataset-edges.json) | Living verified edge ledger: sixteen studies, twenty-one explicit prior-use/generated/comparator/reanalysis edges through 23 November, with the original parent/subseries, unresolved EPIC/E-Risk and date-conflict restrictions retained |
| [Edge table](2026-11-22-study-dataset-edges.tsv) | The same twenty-one verified edges in a tabular interchange; the original 17-row baseline remains reconstructible using checked_on, and unresolved overlap remains separate |
| [Europe PMC receipts](2026-11-22-europepmc-receipts.json) | Eight actual XML request outcomes: two HTTP 200, five HTTP 500, one timeout. Successful accession mentions are retained; full-text passages are omitted |
| [23 November watch receipt](2026-11-23-watch.json) | Overlapping entry-date queries and exact accession checks, BioStudies and GEO metadata source responses, three new primary publications with four verified historical reuse edges, OpenAlex identifier crosswalk, limitations, and E0–E7 disposition |
| [Paired-array addendum API receipts](2026-11-22-paired-addendum-api-receipts.json) | Fresh exact-ID/DOI lookups for Kandaswamy, Sugden and Cheung through PubMed, OpenAlex and Europe PMC; failed full-text calls and successful documented PMC AWS retrievals, with hashes, version metadata and limits |

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

## Paired-array addendum — 22 November 2026

The [focused qualification receipt](../qualification/paired-literature-addendum-2026-11-22.md) reconciles the additional paired-array evidence with this central ledger. It adds Kandaswamy (PMID 33371772) and Sugden (PMID 32885222), bringing the current register to **13 studies and 17 verified study–dataset edges**. Cheung's two existing GSE86833/GSE92580 reuse edges were reconfirmed from primary text and retained without duplication. Original search receipts remain unchanged.

Kandaswamy's article explicitly deposits its study at **GSE154566**. The separately qualified GEO pairing metadata identifies 233 blood specimens measured on both arrays. Sugden reports a 350-specimen E-Risk comparison and identifies **GSE105018** for the 450K layer; this does not establish public access to all paired EPIC raw files. Because both concern age-18 E-Risk blood, **participant overlap remains unresolved**. The ledger does not treat them as two independent calibration cohorts, add their sample counts, or assert that Sugden used GSE154566. Explicit specimen/person/family linkage is required before a joint calibration or independent holdout claim.

Cheung already compared multiple tissues and public paired cohorts. Sugden already examined downstream implications of probe reliability. These are specific prior-art constraints on a simple pooled-concordance or generic reliability paper. They do not establish that every clinically focused transfer question is exhausted. This exact-seed reconciliation is not a new systematic review, a completed N1 protocol or an assessment that a proposed disease analysis is novel.

### Current full-text API route

All three metadata lookups succeeded. The new Europe PMC fullTextXML attempts returned two HTTP 500s and one timeout; those failures are recorded. An attempted legacy `oa.fcgi` request returned 404. [NCBI documents that this service retired on 25 August 2026](https://pmc.ncbi.nlm.nih.gov/tools/oa-service/); that response must not be interpreted as lack of open access.

The [current PMC Article Datasets documentation](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/) and its [bucket README](https://pmc-oa-opendata.s3.amazonaws.com/README.txt) describe anonymous HTTPS/S3 access. The addendum used ListObjectsV2 to enumerate each PMCID's versions, read their metadata and retrieve the XML. Published versions were selected using `is_manuscript`, not by assuming the largest version suffix is newest. All four retrieved XML objects matched the metadata-supplied MD5, and each received a separate SHA-256. Only citation metadata, relationship assertions and receipts are committed; article text and participant records are not republished.

## Literature watch — 23 November 2026

[The dated review receipt](2026-11-23-watch.json) preserves four complete PubMed entry-date query result sets (6/6, 17/17, 2/2, 13/13), exact accession/DOI checks, all seven paged BioStudies accession searches, OpenAlex DOI/PMID/PMCID matches and the source API caveats. In particular, PubMed excluded GSE116300 and GSE154566 from its translated exact-accession query; the independent BioStudies and publisher/PMC checks supplied leads that abstract searching had missed. Zero BioStudies hits for GSE218186 is **not** evidence that GEO lacks that series or that it has not been reused.

The cumulative maintained register now has **16 study identities and 21 explicit verified study–dataset edges** (the 22 November frozen-as-dated baseline was 13 and 17). Four additional **historical** edges were verified from the published source passages, rather than inferred from citation counts: [Heiss/Just 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6346546/) reanalysed GSE97362 for cross-study detection-p QC; [Ruiz-Arenas et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10327521/) used three GSE97362 cases in an epimutacionsData demonstration/comparator; and the published [Kreger et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11599844/) separately identifies GSE154566 and GSE105018 for twin methylation analyses. Kreger's [2024 preprint](https://doi.org/10.1101/2024.03.02.583106) is a version of the same work, not another independent use. Neither the GSE97362 examples nor use of two E-Risk series establishes new independent participants. The existing E-Risk overlap and per-person/sample identity hold stays open.

An additional methodological paper, [Rangani et al., published online 29 October 2026](https://doi.org/10.1080/15592294.2026.2753261), reports CpG- and methylation-level-dependent differences in absolute EPIC/targeted sequencing/pyrosequencing measures; PubMed lists a **December 2026 issue**, which is not the online date. It uses a limited engineered-cell BACH2 experiment with 33 EPIC samples drawn from 90 TMS/pyrosequencing samples and only two CpGs shared across all three methods. This reinforces E1's existing bias and uncertainty checks; it is **not** an independent 450K/EPIC rare-disease validation. A [24 October Kabuki narrative review](https://www.mdpi.com/1422-0067/27/21/9490) expressly reports no new data created or analysed, so it adds no dataset-reuse edge; the [Goel/Goh/Stuart review](https://doi.org/10.1002/mgg3.70319) remains background.

**Disposition:** E0/T01 independence/source qualification remains the earliest scientific gate; E1/T07 is optional and methods-limited; E2/E3/T02, later E4–E7, and N1/N2/N3 decisions retain their dependency order. No rights, provisional journal, manuscript split, direct dependency, limma-core numerical acceptance or frozen scientific protocol changed. The linked receipt is a bounded evidence event, not a systematic literature review.
