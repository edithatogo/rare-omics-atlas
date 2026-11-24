# HGNC binding for the existing disease references

**25 November 2026, Australia/Brisbane — T01.09b / batch C2.**

Source qualification, focused consumer checks and independent source/code/output review passed. This bounded increment independently checks the five existing MONDO disease-reference genes against archived HGNC authority records. Exact current-candidate strict/hook/hosted integration evidence is recorded separately in the receiving PR and [issue #15](https://github.com/edithatogo/rare-omics-atlas/issues/15). T01.09b remains open for the selected platform, genome build, transcript and annotation consumers. The [machine-readable receipt](hgnc-context-2026-11-25.json) preserves the source and replay evidence.

## Source and rights

The [official archive documentation](https://www.genenames.org/download/archive/) distinguishes approved symbols, previous symbols, aliases and withdrawn records. Its quarterly products are retained beyond the rolling monthly archive. We selected the **6 October 2026 quarterly release**, with exact Google Cloud Storage object generations, rather than a mutable current download. HGNC publishes its data under [CC0](https://www.genenames.org/about/license/); attribution to HGNC, HUGO Gene Nomenclature Committee at the University of Cambridge, [RRID:SCR_002827](https://scicrunch.org/resolver/SCR_002827), is retained.

| Actual downloaded source | Object generation | Bytes | Computed SHA-256 |
|---|---|---:|---|
| [Approved complete set](https://storage.googleapis.com/public-download-files/hgnc/archive/archive/quarterly/tsv/hgnc_complete_set_2026-10-06.tsv?generation=1791293906485185) | `1791293906485185` | 16,973,125 | `8bf6f686e640dbc864a346484626953621b0500d900d26cd085a35c2782d725d` |
| [Withdrawn records](https://storage.googleapis.com/public-download-files/hgnc/archive/archive/quarterly/tsv/withdrawn_2026-10-06.tsv?generation=1791293905928029) | `1791293905928029` | 258,994 | `9328a7361ed5149bf7901cae52c6c30b832b8ec55af22146ea296081278a3140` |

Both downloaded byte lengths and computed MD5 values match the official object metadata. SHA-256 values above were computed locally; they are not described as upstream-published checksums. The complete set has **45,233 Approved records** with unique HGNC IDs and current symbols. The withdrawn product has **5,291 records**: 1,802 Entry Withdrawn and 3,489 Merged/Split. Each selected ID has one exact approved-symbol match and is absent from the withdrawn product. Independent source and root reviews reproduced these observations.

## Selected references and historical-name conflicts

The [selected registry](../registries/hgnc-gene-references.json) is a projection of these source rows. It retains current ID/symbol/name/status, alias and previous-symbol lists, the withdrawn-source check and HGNC's Entrez/Ensembl cross-references.

| Current symbol | HGNC ID | HGNC-declared Entrez Gene | HGNC-declared Ensembl gene |
|---|---|---|---|
| KMT2D | HGNC:7133 | 8085 | ENSG00000167548 |
| KDM6A | HGNC:12637 | 7403 | ENSG00000147050 |
| NSD1 | HGNC:14234 | 64324 | ENSG00000165671 |
| DNMT3A | HGNC:2978 | 1788 | ENSG00000119772 |
| EZH2 | HGNC:3527 | 2146 | ENSG00000106462 |

The full source provides concrete reasons to avoid symbol-only substitution:

- `MLL2` is an alias of KMT2B (HGNC:15840) and a previous symbol of KMT2D (HGNC:7133). `MLL4` is an alias of both genes.
- `ALR` occurs as an alias of AKR1A1, GFER and KMT2D.
- `EZH1` is both the approved symbol for HGNC:3526 and an alias recorded for EZH2 (HGNC:3527).
- Withdrawn HGNC:11418 (`STO`) points to HGNC:14234 (`NSD1`); withdrawn HGNC:11964 (`TNRC21`) points to HGNC:7133 (`KMT2D`). Both have source status Merged/Split. These lifecycle assertions do not authorize an automatic identifier replacement.

The selected registry contains only the five required genes. It is not a complete alias resolver, and absence from that projection does not establish absence from HGNC.

## Consumer contract

The existing `ontology-context` command accepts optional `--hgnc research/registries/hgnc-gene-references.json`. Without that option, its historical three-input output remains unchanged. Supplied mode requires every disease-reference HGNC ID to bind to exactly one Approved record with the exact current symbol and a declared negative withdrawn-source check. IDs absent from the selected registry, withdrawn, duplicate, conflicting or unconsumed records and alias/previous-symbol substitution reject. Multiple disease concepts may share one exact gene reference. Original MONDO disease, gene-relation and HPOA context remain intact.

The command validates the selected registry and joins; it does not download or requalify upstream sources. It retains `source_claims_verified: false`, `analysis_admitted: false` and an unknown independent-participant count. Its separate gene-reference fields preserve provenance and the registry input hash. Entrez/Ensembl identifiers remain HGNC-sourced assertions: no independent NCBI/Ensembl, transcript, genomic coordinate, mechanism, protein or regulatory relationship is qualified here. No gene or disease is assigned to an assay.

## Reproduce source-to-registry equality

Retrieve the two generation-qualified URLs above into ignored `data/reference-cache/hgnc-2026-10-06/` with their original filenames. From the repository root, the following standard-library check verifies their bytes and the complete selected projection:

```python
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

cache = Path("data/reference-cache/hgnc-2026-10-06")
registry = json.loads(Path("research/registries/hgnc-gene-references.json").read_text())
for source in registry["sources"]:
    raw = (cache / Path(urlsplit(source["url"]).path).name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source["sha256"]
with (cache / "hgnc_complete_set_2026-10-06.tsv").open(newline="") as stream:
    complete = list(csv.DictReader(stream, delimiter="\t"))
with (cache / "withdrawn_2026-10-06.tsv").open(newline="") as stream:
    retired = {row["HGNC_ID"] for row in csv.DictReader(stream, delimiter="\t")}
with Path("research/registries/initial-disease-crosswalk.tsv").open(newline="") as stream:
    required = {row["hgnc_id"]: row["gene_symbol"] for row in csv.DictReader(stream, delimiter="\t")}
assert len({row["hgnc_id"] for row in complete}) == len(complete)
by_id = {row["hgnc_id"]: row for row in complete}
assert len(registry["records"]) == len(required)
assert {gene["hgnc_id"] for gene in registry["records"]} == set(required)
for gene in registry["records"]:
    source = by_id[gene["hgnc_id"]]
    assert source["symbol"] == required[gene["hgnc_id"]]
    assert source["status"] == "Approved"
    assert gene["hgnc_id"] not in retired and gene["in_withdrawn_source"] is False
    for key in ("hgnc_id", "symbol", "name", "status", "entrez_id", "ensembl_gene_id"):
        assert gene[key] == source[key]
    for key in ("alias_symbol", "prev_symbol"):
        assert gene[key] == (source[key].split("|") if source[key] else [])
print("Five exact HGNC references match the pinned approved and withdrawn sources.")
```

## Execution and receiving evidence

The initial installed-hook setup was revalidated. Before changes, full strict verification passed all 34 checks in 55.933 seconds on main `bcccd781fea89895c0ca1e4af1ea43f8d45e1073`. The baseline source digest was `f2325bf0a4b0365dd94788179e6205819c570f2dea9fa5fa782a4a983072f2ca`.

The focused Rust ontology suite passed **8/8 tests** (0.07 seconds test execution; 3.50 seconds build), followed by all-target Clippy with warnings denied, formatting and whitespace checks. The tests cover exact source records, inert ambiguous aliases, current-symbol conflicts, missing/withdrawn/duplicate/unconsumed records, malformed input/provenance, deterministic ordering, multiple disease concepts per gene, optional CLI failure and read-only behavior. No runtime dependency was added.

The actual full-catalogue command documented in the [catalogue README](../../tools/catalogue/README.md#optional-hgnc-gene-reference-binding) passed with five Approved gene bindings, five disease references and 2,532 series-assay memberships. An independent output review compared every original report field and the complete selected gene projection:

| Actual artifact | Bytes | SHA-256 / disposition |
|---|---:|---|
| Selected HGNC registry | 2,692 | `541d0d5c34e74287b86b96243011329502efa729ac53746c49de120b4eac8b86` |
| Historical three-input report | 1,471,158 | `485088ea41ff6b5c987e8606c4e8d8a6102891b599b550fd58a42a86f74fdc79`; regenerated output is byte-identical |
| Optional HGNC report | 1,474,172 | `97a117b191f5548fe21ea735c9e8ff744550fe2061fc14aa5ada7093fd0c9f70`; only the three gene-reference fields and additional input hash are added |

All existing assay contexts, disease references and counts remain unchanged: 489 exact, 458 broader, 457 related, 895 unmapped and zero ambiguous annotation entries; 321 memberships have no reported annotation. Annotation and membership units remain separate. The output preserves all three scientific/source/participant limits described above.

The documented source-to-registry recipe was executed against the actual downloaded files and passed. Independent source/code review found no remaining blocker. Full installed-hook and hosted checks must pass for the exact current-base candidate before merge; their actual revisions, trees, durations and outcomes are preserved with the receiving PR and issue #15. The baseline and focused checks above do not replace those gates. The R qualification script, native-reference workflow and numerical contracts are unchanged, so this increment does not trigger or claim a new native R qualification.

## Conductor and scientific disposition

This is the bounded gene-reference component of existing T01.09b/C2. The parent remains open for selected platform/build/transcript joins and any subsequently consumed annotations. T01's specification now distinguishes the historical initial 341 held declarations from the later 257 held / 84 review-scope exclusions / zero admitted result; neither historical receipt was rewritten.

The separately owned SeSAMe control/N1 increment in [PR #24](https://github.com/edithatogo/rare-omics-atlas/pull/24) is unchanged. Source-derived identifiers establish reference context, not new participant observations or independent evidence. Cohort QC, biological independence, applicable institutional determination, official owner-device qualification and N1 remain open. No clinical effect, scientific ontology benefit or new publication claim follows from this reference increment.
