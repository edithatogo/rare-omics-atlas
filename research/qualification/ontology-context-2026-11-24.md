# Ontology context and Reactome qualification — 24 November 2026

## Scope and current disposition

This owner-directed increment extends the existing catalogue and native reference route. It implements the ontology recommendations in the existing T01/T03/T04/T05 plans and resource table. No new runtime package, ontology parser framework or knowledge-graph service is required.

**Source bytes and the catalogue consumer have been exercised.** Rust formatting, five grouped ontology tests, all-target/all-feature Clippy and the actual catalogue replay pass. Independent Rust and Reactome source/code reviews found no blocker; branch-aware changed-line coverage is 100% (263 production lines, none missing). The prior candidate passed local strict verification and an actual installed-hook commit, but its hosted strict and native attempts failed as recorded below. Those successes do not qualify the changed combined candidate.

The current candidate is replayed onto actual merged main `9480311be20d51962ed9ce41684bf0bb56440f95`, retaining both PR #22's native hg38 QC repair and this ontology/Reactome extension. Fresh current-tree strict, hook, hosted and native checks remain pending. **No native Reactome result has been received.**

The [machine-readable receipt](ontology-context-2026-11-24.json) records the source pins and actual replay hashes. The original [MONDO/HPO/HPOA receipt](ontology-source-receipt.md) remains the authority for the five disease references. Neither receipt establishes patient diagnoses, observed patient HPO features, cell proportions, independent participant counts or scientific admission.

## New qualified source bytes

| Source | Frozen product | Actual bytes | SHA-256 verification |
|---|---|---:|---|
| Uberon | [v2026-11-05 OBO release asset](https://github.com/obophenotype/uberon/releases/download/v2026-11-05/uberon.obo) | 22,534,892 | Actual SHA-256 and size match the official release API asset metadata |
| Cell Ontology | [v2026-11-13 OBO release asset](https://github.com/obophenotype/cell-ontology/releases/download/v2026-11-13/cl.obo) | 19,846,560 | Actual SHA-256 and size match the official release API asset metadata |
| Reactome | [v98 NCBI mapping file](https://download.reactome.org/98/NCBI2Reactome_All_Levels.txt) | 97,248,132 | SHA-256 computed from downloaded bytes and pinned; no independent upstream SHA-256 was found |

The JSON receipt includes exact hashes, release/asset IDs, official URLs, ontology headers and license-file hashes. The tag's repository OBO and the release asset are not assumed identical. Uberon was published on 5 November; CL's release header is 13 November and its release was published on 16 November. Reactome's [v98 archive record](https://doi.org/10.5281/zenodo.24067822) identifies the October 2026 release; the full 4.7 GB archive was not downloaded.

Attribution: **Uberon contributors**, selected asset CC BY 3.0; **Cell Ontology contributors**, selected asset CC BY 4.0. Source labels and short synonym assertions are preserved with source/version and license URLs. The mappings are Atlas curation and are not presented as upstream mapping assertions. Reactome data are CC0 under [section 1c of its agreement](https://reactome.org/license); its illustrations and software have distinct terms. The full source files remain in ignored `data/reference-cache/`; this increment commits source receipts and a small mapping table, not a new public bulk mirror.

## Actual catalogue consumption

The new `ontology-context` binary uses the existing Rust catalogue crate, its existing dependencies and the [curated registry](../registries/ontology-context-mappings.json). It consumes these exact three inputs:

```sh
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml \
  --bin ontology-context -- \
  --assays research/catalogue/2026-11-22/assays.jsonl \
  --diseases research/registries/initial-disease-crosswalk.tsv \
  --mappings research/registries/ontology-context-mappings.json
```

Standard output is a deterministic JSON sidecar; redirect it to an ignored local output when desired. Input files are not modified. The report contains all three input hashes, original source labels, organisms, mapping predicates/evidence and ontology source declarations. It does not fetch or verify source claims by itself; that separate actual source verification is recorded above.

| Replay measure | Result | Unit |
|---|---:|---|
| Catalogue memberships processed | 2,532 | Series–assay membership records |
| Records with at least one mapped context | 1,404 | Membership records |
| Records with no annotation | 321 | Membership records |
| Exact mappings | 489 | Source annotation entries |
| Broader mappings | 458 | Source annotation entries |
| Related mappings | 457 | Source annotation entries |
| Unmapped entries | 895 | Source annotation entries |
| Ambiguous entries | 0 | Source annotation entries |
| Disease references retained | 5 | Disease concepts, not assigned patients |

A record can carry multiple annotations, so annotation and membership totals must not be added together. There are 17 explicit source-label mappings to eight active terms. The replay output is 1,471,158 bytes with SHA-256 `485088ea41ff6b5c987e8606c4e8d8a6102891b599b550fd58a42a86f74fdc79`; input hashes are in the JSON receipt.

### Semantic decisions tested

- Exact literal joins preserve the original metadata; the executable performs no fuzzy matching, ontology traversal or transitive cross-reference inference.
- “Peripheral blood” maps to broader Uberon blood even when the original field is called “cell type.” It does not create a specific blood-cell identity.
- Uberon's “whole blood” synonym is **RELATED**. The report preserves `skos:relatedMatch` rather than promoting it to exact equivalence.
- iPSC maps to broader pluripotent stem cell; induced origin and culture context remain in the original label. Neuronal progenitor maps only to the broader neural progenitor concept. Cortical neuron is an exact CL synonym, without implying a brain-tissue specimen.
- Bare “Buccal,” named cell lines and unspecified brain tumour remain unmapped in this bounded table. Cultured, cancer-associated, developmental and source-field qualifiers are retained.
- Multiple candidates are reported as ambiguous; malformed inputs, conflicting labels/duplicate mappings, duplicate series–assay memberships and unsupported predicates are rejected. Repeated assay IDs across different series remain memberships, not independent donors.
- MONDO/HGNC causal-gene relations, OMIM equivalence, exact versus parent Orphanet IDs and disease-level HPOA coverage are exported as a **separate reference dictionary**. The input catalogue has no qualifying diagnostic fields; the consumer assigns no disease to an assay and no disease phenotype to a person.

## Reactome native synthetic consumer

The [v98 contract](../contracts/reactome-v98.json) pins the exact file, selection rule and source counts. The existing [native reference workflow](../../.github/workflows/native-reference.yml) downloads and checks these bytes before the existing R enrichment stage. The source contains 781,553 rows across 16 species. Its [official six-column format](https://reactome.org/download-data?id=60&ml=1) includes identifier, pathway, URL, name, evidence and species.

The Homo sapiens subset has 157,638 rows. Excluding 224 rows with 22 nonnumeric sequence identifiers leaves 157,414 rows, 11,470 numeric identifiers, 2,861 pathways and 140,535 distinct gene–pathway pairs. TAS and IEA source rows are retained in explicit evidence counts; repeated pairs are deduplicated. A human pathway label alone does not establish that every member is human; the native human annotation universe remains authoritative.

The implemented call to `missMethyl::gsameth` uses exactly the existing 4,000 tested and 200 selected synthetic CpGs, native Entrez mappings, annotation, equivalent-CpG weighting and fractional counting. It reports mapping/family coverage, pathways absent from the tested universe, unmodified native probabilities and complete-family BH results. No pathway is filtered by its p-value or apparent effect.

The existing receiver permits only the already qualified numerical boundary: a tiny deviation from one at native **integer** count zero. Fractional overlaps are independently reconstructed, their floors checked against native DE, and the direct inclusive upper tail is checked at that integer boundary. Positive fractional overlap below one is not described as zero biological overlap. Native raw results and any native probability-domain failure remain visible; positive-count probabilities are unchanged. This is bounded technical qualification of the selected native route, not an independent proof of the entire enrichment model.

**Native execution remains pending for the combined candidate.** The initial hosted attempt failed at the predecessor's technical annotation load before limma or enrichment; it produced no Reactome result. Required output includes `reactome-family.tsv`, `reactome-evidence.tsv`, `reactome-raw.tsv`, `reactome-zero-boundary.tsv`, `reactome-received.tsv`, `reactome-summary.tsv` and the actual workflow disposition. Source verification is not substituted for that run.

The combined candidate is bound to these actual code/contract bytes:

| File | SHA-256 |
|---|---|
| `scripts/tests/qualify_reference.R` | `e961009556ee083de013e041dc7ab57fb844ab968768d9e18b57cbccc0f52c23` |
| `.github/workflows/native-reference.yml` | `d08b8ed6284e39fbcc2cce36c334c1d7bfdccf06560dbb25b09ae2136ae77746` |
| `research/contracts/reactome-v98.json` | `407b395d5fd5e491ee34b1d5dc4afbc82f1915baf77f9bbe2d31a6eb5f0abff3` |

## Verification and remaining scientific work

The unchanged-base strict command was attempted before implementation and failed because Rust and native verification tools were absent. That failure is retained in the local baseline receipt. The pinned toolchain, scanners and native pre-commit hook were then installed.

### Historical candidate and receiving reconciliation

The prior ontology candidate `f7adf0d514c5c7bf1eb0bc42790313b17fdc1299` was based on `dc2433ddb9d5778ce2a1df37b1d001068209d19a`. Its Git tree was `8fffcdf4bb99a55ccc2e1b752f849bab7c07c843` and the verifier's source-content SHA-256 was `bec654f083bcc4a6ec0ffeb76c60b13f4f8aef6d0e09e1c2d3c483f0ea134244`. Actual local strict verification passed **34/34** in **149.851 seconds**; the actual installed-hook commit then passed **34/34** in **32.710 seconds**. These are bounded historical code receipts, not native R or owner-device acceptance.

| Observed attempt | Result and retained limitation |
|---|---|
| [Initial hosted strict 45409996763](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45409996763) | Failed with one history finding. A subsequent scan of currently fetched refs returned zero findings with no scanner waiver. Association with an outdated PR #22 prose head then present in fetched history is an **inference**, not an established causal result. Preserve the failed attempt and require the current hosted history gate to pass. |
| [Initial native 45409996742](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45409996742) | Failed in the technical stage at minfi annotation loading, before limma and enrichment. Downloaded artifact `14926959908` has SHA-256 `5e51e7cfe118bf14268b19a7bb1d39fa8271fb8cc4caecb2eea0720daa0dfd25`. No Reactome operation was exercised. |
| [PR #22](https://github.com/edithatogo/rare-omics-atlas/pull/22) receiving | Merged as `9480311be20d51962ed9ce41684bf0bb56440f95` at **24 November 2026 14:18:54 UTC / 25 November 00:18:54 Australia/Brisbane**, while [its native run 45410579769](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45410579769) remained in progress. This is another premerge native-evidence gap; merge does not grant technical qualification. |
| Current combined ontology candidate | Ontology changes replayed onto that actual main without textual conflict, preserving the native hg38 coordinates/masks, disjoint QC/control evidence and Reactome enrichment addition. Fresh current-tree strict, installed hook, hosted and native qualification are pending. |

The existing [native receipt](t07-native-reference-candidate.md#receiving-history-reconciliation) preserves earlier ordering gaps and the original fixed-denominator annotation failure. The hg38 QC denominator and native hg19 CpG-ID gene annotation remain distinct; no cross-build region mapping or clinical threshold acceptance follows from this integration. A later pass must be recorded against its actual changed source and must not rewrite earlier failures.

Targeted Rust tests exercise mapping direction, related/ambiguous/unmapped/unreported states, original-label preservation, input hashes, separate disease semantics, malformed/duplicate/conflicting input, disclosure boundaries, file-size limits and read-only CLI behavior. Actual formatting, five grouped tests and Clippy pass. See the PR's final exact-tree check receipts before treating this candidate as integrated.

The [resource priorities](../resources-hosting-reuse.md#ontology-and-annotation-priorities) and existing Conductor tracks now cover HGNC/Ensembl/SO, regulatory resources, ECO/PROV-O, protein, reaction, metabolite and cross-species resources as named consumers require them. They do not imply that every resource has been downloaded or analytically validated. Frozen molecular-only, ontology-only and combined comparisons, source-removal ablations and outcome-leakage controls apply to selected scientific uses.

Clinical cohort admission, material participant/family and cross-study independence, any required per-control provenance, actual-device qualification, the applicable institutional determination and analysis-specific N1 remain open. The [separate primary-Methods receipt](t01-molecular-decision.md#primary-methods-bytes-and-scoped-source-disposition--25-november-2026) supports the pooled native-control recruitment context without resolving individual recruitment site or biological independence. No disease analysis, patient phenotyping, new independent observation or demonstrated clinical benefit results from this increment.
