# V01 — acquisition, reuse and release record (2026-11-25)

## Observed intake

- Repository identity 1467227964 confirmed under `edithatogo/rare-venomics`; PR #31 received on main. PR #28 remains draft; its scientific scope unchanged. PR #29 remains open with security changes overlapping the workflow paths; reconcile it separately rather than overwrite that branch.
- PubMed structured provider returned exact records for PMIDs 12492390 and 23508658, no missing IDs; targeted search identified PMID 9887916. Bibliographic fields only, not abstract or full text, staged as three JSONL records. Original API response byte hash unavailable through the connector; do not substitute the projection hash for it.
- Original eAtlas public catalogue (265 mixed records, CC BY 3.0 AU with specific acknowledgement and metadata conditions) inspected. Expanded release direct catalogue returned HTTP 403. The local environment's DNS could not resolve GitHub, eAtlas, OBIS or the Hub. No event CSV, source ZIP, AIHW workbook or original raw data transfer verified. Do not bypass source access restrictions. The OBIS projection is not independent clinical evidence.
- AIHW public report, hospitalisations 2021–22: 91 Irukandji hospitalisations, rate 0.4/100,000, 121 total jellyfish hospitalisations. Three aggregate benchmark rows are manual source transcription, not automated workbook extraction. Website copyright policy CC BY 4.0 subject to exceptions; source and attribution recorded. These are hospitalisation episodes, not distinct people or all stings.

The [four-object release manifest](../../../research/releases/2026-11-25-v01/manifest.json) includes source-linked metadata, the bibliographic projection, existing aggregate benchmark and a readme. Retain SHA-256/byte counts of the exact reviewed objects. Hub read-only listing showed existing Rare Omics Atlas metadata; no V01 objects and no original methylation archives verified on the Hub. Hugging Face storage only, no compute. The connector cannot commit files to an existing dataset; use the existing reviewed official publisher with the owner runner and existing authentication. No new repo or duplicate data lake.

## Programmatic acquisition first

1. Existing Searchright source-backed PubMed/Europe PMC/Crossref review/export capability (technical preview, pin and verify actual consumer before adoption). Until admitted use official EUtils exact-identifier metadata and source receipt, no custom literature crawler. The following bounded replay uses native curl on a trusted, authorised environment, in a new ignored Bronze cache directory. Check the response is the expected PubMed JSON and that the three IDs resolve; preserve source bytes and hash locally. Do not store contacts, abstract or patient narratives in the public projection.

```bash
umask 077
mkdir -p data/bronze/v01
curl --fail --silent --show-error --max-time 60 --max-filesize 10485760 \
  'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=9887916,12492390,23508658&retmode=json' \
  -o data/bronze/v01/pubmed-esummary.json.part
python -m json.tool data/bronze/v01/pubmed-esummary.json.part >/dev/null
# inspect expected identity and hash; promote only after verification, never overwrite a prior receipt
```

2. For eAtlas use source catalogue/API and archive routes disclosed by the custodian. Current 403 is a hold; retry only ordinary authorised access on the trusted device, not alternative access-control bypass. Inspect metadata and source-specific terms before retrieving event-level records. The existing catalogue client already uses reqwest, serde, sha2, bounded request receipts and cache replay. Do not introduce a second crawler or alter rare-disease catalogue seeds; reuse the pattern when an actual source response is available. Source-linked Bronze is sufficient until privacy and release checks permit mirroring.
3. Prioritise official AIHW supplement file and published aggregate series; prefer native HTTP/download with the existing openpyxl route only for a real workbook (already used in molecular-source CI). Record time-period/coding breaks, source table, aggregation level, nulls and exact hashes. No inference from the three benchmark rows.
4. Existing data catalogue supports GEO metadata where a clinical or host-response question and its rights/admission justify a new seed; use separate dated stream-specific output, not a modified rare-disease registry. Use existing source retrieval and reviewed publication manifests; release the metadata and eligible data only after source-specific rights, privacy, research governance and exact content verification.

## Dependency and synergy decisions

| Consumer | Reuse first | Conditional alternative / gate |
|---|---|---|
| Source acquisition | Native curl/official APIs; existing Rust catalogue reqwest/serde/sha2/clap | Extend only for a verified response and named consumer, no new dependency now |
| Study metadata and literature | Searchright, Sourceright, CiteWeft where actual tested contracts suffice | EUtils/Europe PMC/Crossref receipts; no duplicate literature framework |
| Typed tables | JSONL for small tables; existing Polars/Arrow/Parquet when a consumer requires it | Native CSV and stdlib for bounded profiles; one engine per stage |
| Phenotype/context | Existing HPO/MONDO, Uberon/CL, provenance and mappings | Add ExO, ENVO, ECO/OBI, taxonomy/clinical terminology only for observed gaps; no graph service |
| Narrative extraction | Structured fields, deterministic dictionaries and source spans; test existing NLP packages only after text availability | Independent double annotation and held-out precision/recall, abstention and error; no new model or training prerequisite |
| Statistical inference | Existing selected methods and references | Qualify on the exact design, missingness, dependence and estimand; no blanket transfer of methylation qualification |
| Reporting | StandardFlow; CINEX, STROBE, RECORD as applicable | Reuse N0–N3 and complete analysis-family evidence |
| Release | Current official locked huggingface_hub publisher, SHA-256 manifest, trusted self-hosted workflow | No separate publication engine or Hub compute; no patient data or raw clinical narratives in public storage |
| Cross-stream synergy | Shared study/assay identity, clinical phenotype mapping, source receipts, reproducibility, reference-method qualification | T06 only when independent quantitative and clinical evidence makes a defensible question; no change to T01/T07/T02 |

Do not make new NLP, graph or omics libraries universal dependencies. Apply Rust > Julia > Python > R after scientific suitability; prefer existing native tools, original validated methods, and file interchange. Reuse rather than reimplement.

## Publication handoff

Once the exact reviewed candidate passes current-base hook, strict/privacy/provider checks and is on trusted main, use the existing [publication workflow](../../../.github/workflows/publish-hf.yml), release choice `2026-11-25-v01`, on the authorised registered device with existing Hub credentials. The original release remains the default and its content hashes are unchanged. The publisher still accepts the exact historical GitHub alias, which resolves to the same repository; no new repository or rights expansion. Read back immutable Hub revision and every manifest-selected file hash before recording publication. Current candidate is not uploaded. The three older methylation archive transfers remain separate T09 work. Do not mark scientific admission or device qualification complete.
