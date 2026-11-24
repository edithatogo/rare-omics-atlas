# Official API catalogue

This small Rust CLI turns an explicit accession register into reproducible, public **metadata** tables. It uses NCBI's documented EUtils and GEO SOFT interfaces and the PRIDE Archive v3 REST API. It does not scrape search results or infer participant numbers from assay numbers.

## Run and replay

From the repository root, with Rust 1.95.0:

```sh
cargo +1.95.0 test --locked --manifest-path tools/catalogue/Cargo.toml
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml -- \
  --registry research/registries/dataset-rights.json \
  --out research/catalogue/2026-11-22 \
  --cache data/bronze/catalogue-responses
```

The canonical registry currently contains 29 accessions, including GSE154566. Use `--extra GSE...` only for accessions absent from the registry: duplicate seeds fail. Use a new output directory for a new dated snapshot. The CLI will not create clinical eligibility or infer distribution rights from metadata availability.

Default mode reuses an integrity-valid cache regardless of its age; there is no implicit time-to-live. Use `--refresh` for a new retrieval date, and retain the previous dated output snapshot. `--offline` replays only the cache; it checks every cached response's URL, byte count and SHA-256 before parsing. `--refresh` explicitly retrieves new source responses. Those flags are mutually exclusive. No API key or authentication is required. Requests are sequential, spaced at least 400 ms, with three bounded attempts for transient failures. Outputs checkpoint after each accession; exit 2 records one or more failed records instead of silently dropping them.

## Tables

| File | Unit and contents |
|---|---|
| `datasets.jsonl` | One accession, including failures; title, organism, platform, assay type, public/update dates, PubMed links, source relations, independently checked assay counts, source request references |
| `assays.jsonl` | One series–GSM membership, safe tissue/cell/platform/molecule/organism fields and public source accession links; no age, sex, diagnosis, variant, patient title or contact export |
| `files.jsonl` | Source-declared supplementary file URLs, and PRIDE file categories/sizes/checksums when provided; not a new transfer receipt |
| `requests.jsonl` | URL, resolved URL, timestamp in Unix milliseconds, HTTP outcome, bytes, local SHA-256, attempts and cache-object reference |
| `summary.json` | Input hash, requested/catalogued/failed counts, distinct assay IDs, elapsed execution time and limitations |

JSONL is deliberately sufficient for the small metadata catalogue and is directly readable by Arrow/Polars and Hugging Face. It avoids a dataframe dependency in the HTTP intake binary. The publication adapter can emit Parquet without changing source semantics. IDATs remain binary source files.

The **local raw response cache is not a public upload selection**. SOFT/API responses can contain contacts and richer sample information; only allowlisted fields enter these public tables. Clinical metadata curation is a later, analysis-specific step. The cache belongs in ignored Bronze storage. Raw matrices, platform manifests, sequences and IDAT archives are not downloaded by this tool.

A GEO SuperSeries and its subseries can share GSM accessions. The catalogue retains source relation strings and separate `series_assay_membership_rows` and `distinct_assay_accessions`; neither is a number of independent participants or cohorts. ESummary's sample listing can be truncated; its source count is checked against the complete series/sample SOFT membership, and the truncation status remains explicit.

## Source methods

1. Exact accession search in EUtils `db=gds` using `GSE...[ACCN] AND gse[ETYP]`; require a complete returned UID list.
2. ESummary resolves the UID; require exactly one matching accession and GSE entry type.
3. Documented GEO `acc.cgi` SOFT requests: `targ=self&form=text&view=quick` for the series and `targ=gsm&form=text&view=brief` for sample metadata. These avoid `targ=all`, which includes platform content. Require matching accession, unique samples and agreement between source inventories/counts. The parser interprets SOFT metadata lines only; it never interprets matrix cells.
4. PRIDE `/archive/v3/projects/{PXD}` plus its unpaginated `/files/all`; require exact project identity and file membership. Source checksum algorithms are left unknown when not stated by the API.
5. Retain source URLs and receipts. No assumption that FTP URLs listed by a source are currently downloadable; transfer verification remains separate.

Primary documentation:

- [GEO programmatic access](https://www.ncbi.nlm.nih.gov/geo/info/geo_paccess.html)
- [GEO downloads and metadata formats](https://www.ncbi.nlm.nih.gov/geo/info/download.html)
- [SOFT format](https://www.ncbi.nlm.nih.gov/geo/info/soft.html)
- [EUtils usage and rate limits](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
- [NCBI disclaimer and copyright notice](https://www.ncbi.nlm.nih.gov/About/disclaimer.html)
- [PRIDE API documentation](https://www.ebi.ac.uk/pride/ws/archive/v3/docs/api-guide.html)
- [PRIDE's maintained client](https://github.com/PRIDE-Archive/pridepy)

## Ponytail dependency decision

This is an operational metadata adapter, not a new bioinformatics algorithm. Reqwest supplies TLS/HTTP and URL encoding; Serde JSON supplies the API format; SHA-2 supplies content hashes; Clap supplies the CLI. The bounded SOFT adapter covers only the fields consumed here. No Polars, SQL engine, graph layer, lakehouse service, custom HTTP implementation or retry framework is necessary. The lockfile and exact enabled features are part of the qualification record. A published metadata API is the source oracle, while negative tests protect accession identity, duplicate/sample membership, API errors and disclosure boundaries.

Cloud tests qualify this implementation in the observed environment. The repository's official local-runner requirement remains a separate target-device acceptance step.

## Curated ontology context

The existing catalogue can now receive the selected disease reference crosswalk and
explicit tissue/cell mappings without changing the original source snapshot:

```sh
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml \
  --bin ontology-context -- \
  --assays research/catalogue/2026-11-22/assays.jsonl \
  --diseases research/registries/initial-disease-crosswalk.tsv \
  --mappings research/registries/ontology-context-mappings.json
```

The command writes JSON to stdout only. Exit 0 means the inputs are structurally
valid and a report was produced; unmapped or ambiguous annotations remain in that
report. Exit 1 rejects malformed inputs, duplicate series–assay memberships,
duplicate/conflicting reference mappings, incompatible identifier namespaces,
unbound sources, or inputs larger than 16 MiB each. It never writes the input
files, retrieves references, assigns disease diagnoses, or admits an analysis.

The mapping JSON has `schema_version: 1`, `sources` and `mappings`. Each source
declares `id` (`UBERON` or `CL`), `version`, `url`, `sha256`, `license` and
`license_url`. Each mapping declares the entire literal `source_label`,
`source_id`, `term_id`, `term_label`, `predicate` and `evidence`. Matching uses the
complete source string, including its characteristic key and case; there is no
fuzzy match or silent synonym expansion. The permitted predicates have explicit
direction from the source label to the ontology term:

| Predicate / report status | Meaning |
|---|---|
| `skos:exactMatch` / `exact` | Curator-declared equivalent context |
| `skos:broadMatch` / `broader` | Target ontology concept is broader than the source label; source detail is retained |
| `skos:relatedMatch` / `related` | Context is related, without an equivalence or subsumption claim |
| Multiple candidates / `ambiguous` | Every candidate is retained; none is selected automatically |
| No candidate / `unmapped` | A source label exists but has no curated mapping |
| No source annotations / `unreported` | The catalogue supplied no tissue/cell annotation for that membership |

Namespaces determine the target's meaning. For example, a source characteristic
named `cell type: Peripheral blood` may map to an Uberon anatomical concept; this
does not declare a blood cell type or measured cellular composition. Organism
metadata and the complete original labels are retained. Repeated GSM accessions
in different series remain separate memberships and never become independent
participants.

The disease TSV is consumed as a separate reference dictionary: MONDO concepts,
HGNC gene relations, OMIM equivalence assertions, exact versus parent Orphanet
links, and the versioned disease-level HPOA coverage counts remain distinct. The
consumer does not join a disease label or causal gene onto assays, copy HPOA
terms into participant observations, resolve obsolete identifiers, or traverse
cross-reference chains. The five existing mappings are not a full HGNC or
Orphadata ingest.

Every report records SHA-256 hashes of all three exact input files, source
declarations, annotation-status counts and sorted assay context. It explicitly
keeps `analysis_admitted: false`, `source_claims_verified: false` and
`independent_participant_count: null`. The separate
[source qualification receipt](../../research/qualification/ontology-context-2026-11-24.md)
supplies the actual byte/term checks; syntactically valid URLs, version labels,
licences and digests alone do not verify those claims or provide distribution
clearance. The original [MONDO/HPO receipt](../../research/qualification/ontology-source-receipt.md)
continues to own disease-reference qualification.

This bounded metadata join uses the crate's existing Serde, SHA-2, Reqwest URL
validation and Clap dependencies. It adds no graph engine, OBO/OWL parser,
clinical phenotyping algorithm or new runtime package. Its regression tests
exercise mapping direction, ambiguity, missing labels, raw-input provenance,
duplicate/conflicting inputs, parent-versus-exact disease links and disclosure
boundaries.

### Optional HGNC gene-reference binding

The same command can also bind the disease dictionary's gene identifiers and
symbols to the five selected records from the HGNC quarterly archive of
6 October 2026:

```sh
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml \
  --bin ontology-context -- \
  --assays research/catalogue/2026-11-22/assays.jsonl \
  --diseases research/registries/initial-disease-crosswalk.tsv \
  --mappings research/registries/ontology-context-mappings.json \
  --hgnc research/registries/hgnc-gene-references.json
```

The optional registry has `schema_version: 1`, two `sources` named
`HGNC-complete` and `HGNC-withdrawn`, and `records`. Both sources use the same
release and the source fields documented above. Each record supplies `hgnc_id`,
`symbol`, `name`, `status`, `alias_symbol` and `prev_symbol` arrays, `entrez_id`,
`ensembl_gene_id` and `in_withdrawn_source`. The registry records the exact
generation-bound archive URLs, downloaded-byte hashes and HGNC's declared
CC0-1.0 licence.

Every disease-reference gene must match one selected HGNC ID and its exact
current approved symbol. Records must declare `status: "Approved"` and
`in_withdrawn_source: false`. An unknown ID, a conflicting or duplicated ID or
approved symbol, an alias or previous symbol substituted for the approved symbol,
a withdrawn record, or an unconsumed extra gene rejects the enriched report.
Multiple diseases may share a gene. Source alias and previous-symbol strings are
retained and sorted, but never become lookup keys or automatic replacements.
Unknown means absent from this selected registry; this is not a full HGNC
identifier resolver.

With `--hgnc`, the report adds `reference_genes`, `gene_reference_sources`,
`gene_reference_scope` and `input_sha256.hgnc_reference`. NCBI Gene and Ensembl
identifiers are HGNC-supplied cross-references; their presence does not qualify
NCBI/Ensembl release contents, transcript choices, genome builds or array
annotation joins. The [HGNC qualification receipt](../../research/qualification/hgnc-context-2026-11-25.md)
owns the independent archive and extraction checks, including the selected IDs'
absence from the withdrawn file. The runtime validates supplied declarations and
exact joins; `source_claims_verified` and `analysis_admitted` remain false,
participant counts remain unknown, and the assay contexts remain unchanged.
Without `--hgnc`, the existing three-input report is unchanged.
