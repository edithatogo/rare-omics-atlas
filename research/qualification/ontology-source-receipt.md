# Initial ontology source and disease identifier qualification

**Completed 22 November 2026: three reference files downloaded, SHA-256 verified against official release API digests, and five disease-level mappings checked against actual ontology assertions.** This is source/identifier qualification; it does not assign diagnoses or phenotypes to participants, qualify a Rust/Julia parser, execute a scientific model or approve data redistribution.

## Sources and exact bytes

Reuse the existing full MONDO OBO at Hugging Face repository **edithatogo/rareburden-commons-open-source-snapshots**, pinned revision **cf906c1f8b03179312c82137735976d642d337ed**, path **raw/mondo/v2026-07-06/mondo.obo**. This full OBO contains every required active term and its explicit OMIM/gene mapping. It is a deliberate source pin, not a claim to use the latest MONDO release. The newer rare-only OWL at **edithatogo/rareburden-open-sources@0dae8d3c4ac642cdee6b7ee34e46d9bd84919b66** was listed but not downloaded.

HPO assets came from the official [v2026-09-01 release](https://github.com/obophenotype/human-phenotype-ontology/releases/tag/v2026-09-01). Original references and source notices remain unchanged outside git at `/workspace/scratch/f247f15c065b/ontology_source_receipts`. Exact source URLs, API outcomes and notice hashes are in the [JSON receipt](ontology-source-receipt.json).

| Actual file | Bytes received | SHA-256 |
|---|---:|---|
| mondo-v2026-07-06.obo | 52,967,808 | `75c51066741e04c0ec4751210911d29e17e16431ed2ba5b8a46fc6a37ff5b00e` |
| hp-v2026-09-01.obo | 10,863,613 | `93dace952fcb3ec4728818857f6ba76bc2d5312f4d83266519b8694b8e798f22` |
| phenotype-v2026-09-01.hpoa | 35,816,037 | `e89aa39c8f97bf5a52c5d160f9250a603681d630ade8ec2679d84ac5aece1f72` |

The official MONDO [release API](https://api.github.com/repos/monarch-initiative/mondo/releases/tags/v2026-07-06) and HPO [release API](https://api.github.com/repos/obophenotype/human-phenotype-ontology/releases/tags/v2026-09-01) both returned HTTP 200. All three locally computed SHA-256 digests and sizes exactly match their official asset metadata. This independently corroborates the reused HF MONDO bytes. The MONDO OBO header identifies `releases/2026-07-06`; the HPO OBO header identifies `hp/releases/2026-09-01`.

**Preserve the annotation date separately:** `phenotype.hpoa` is an asset of tag v2026-09-01 but its internal annotation version is **2026-09-02**, referencing HPO **2026-09-01**. The HPO release was published 3 September 2026. These fields are distinct, not silently normalised to one date.

## Five verified disease mappings

The [crosswalk TSV](../registries/initial-disease-crosswalk.tsv) contains source version/hash, literal mapping evidence, HGNC IDs, HPOA identifier/coverage and qualifications. Every gene below is supported by the selected MONDO term's `has_material_basis_in_germline_mutation_in` relationship. OMIM mappings carry `MONDO:equivalentTo` provenance in the source xref. No OMIM prose was copied.

| Active disease label | Gene / HGNC | MONDO | OMIM | HPOA rows / unique positive terms |
|---|---|---|---|---:|
| Kabuki syndrome 1 | KMT2D / HGNC:7133 | MONDO:0007843 | OMIM:147920 | 186 / 183 |
| Kabuki syndrome 2 | KDM6A / HGNC:12637 | MONDO:0010465 | OMIM:300867 | 53 / 51 |
| Sotos syndrome | NSD1 / HGNC:14234 | MONDO:0019349 | OMIM:117550 | 133 / 128 |
| Tatton-Brown-Rahman overgrowth syndrome | DNMT3A / HGNC:2978 | MONDO:0014382 | OMIM:615879 | 39 / 39 |
| Weaver syndrome | EZH2 / HGNC:3527 | MONDO:0010193 | OMIM:277590 | 80 / 80 |

Two corrections matter for downstream work:

- **Sotos:** MONDO:0007299 is obsolete and explicitly replaced by **MONDO:0019349** in this release. Use the active term; retain replacement provenance when normalising old identifiers.
- **Kabuki:** KMT2D and KDM6A map to distinct subtypes. **ORPHA:2322** maps to the broader parent **MONDO:0016512**, not to either subtype as an exact equivalent. Do not duplicate parent annotations into subtype-specific observed evidence. TBRS, Weaver and Sotos have direct Orphanet xrefs in the selected source.

## HPO coverage and semantic preservation

Coverage is computed from the unmodified HPOA bytes for the five explicit OMIM identifiers, plus relevant Orphanet entries recorded separately. All selected HPO IDs exist and are active in the pinned HPO OBO. Counts describe annotation records and distinct phenotype terms, not patient numbers. Several diseases have more rows than unique terms because evidence records can repeat a term.

Original HPOA columns are retained outside git: disease identifier/name, qualifier, HPO ID, reference, evidence, onset, frequency, sex, modifier, aspect and biocuration. The JSON records aggregate evidence-code and populated-field counts. No phenotype rows or disease profiles were copied into this repository. The selected records contain no NOT annotations; this must not be interpreted as evidence that an unlisted feature is absent. Disease annotations do not become participant phenotypes merely because a participant has that diagnosis.

## Terms and attribution

[MONDO](https://mondo.monarchinitiative.org/pages/download/) and the pinned OBO/notice identify **CC BY 4.0**. Attribution: **MONDO, Monarch Initiative, release 2026-07-06**. Preserve embedded source notices; the dataset-level label does not settle every unrelated third-party asset's rights.

The pinned HPO `LICENSE.md` points to a website; that destination returned 404 in this web retrieval. The [official project licence page](https://human-phenotype-ontology.github.io/license.html) was successfully read and captured. Its acknowledgement, version-display and vocabulary-integrity requirements are retained; HPO is **not treated as CC0**. The initial incorrect `LICENSE` filename returned 404 and was resolved by fetching `LICENSE.md`; both events are recorded.

**Acknowledgement:** This project uses the Human Phenotype Ontology, release **2026-09-01**, and disease annotations internal version **2026-09-02**, provided by the **Human Phenotype Ontology Consortium**. Original files and logical relationships are preserved. Source-specific downstream redistribution review remains separate; no HPO/OMIM annotation mirror or Hugging Face release was created.

## Completion boundary

This completes a bounded initial MONDO/HPO byte check and the five-condition identifier crosswalk. Broader ontology expansion, Orphadata snapshot qualification, participant diagnosis assignment, library conformance and analysis-specific N1 remain separate tasks. The annotations are inputs for later explicitly defined consumers; their availability does not by itself establish a biological network or a clinical prediction.
