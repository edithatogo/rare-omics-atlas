# Ontology context and Reactome qualification — 24 November 2026

## Scope and current disposition

This owner-directed increment extends the existing catalogue and native reference route. It implements the ontology recommendations in the existing T01/T03/T04/T05 plans and resource table. No new runtime package, ontology parser framework or knowledge-graph service is required.

**Bounded source, catalogue and native synthetic consumers are accepted.** [PR #23](https://github.com/edithatogo/rare-omics-atlas/pull/23) merged as `92639afe9b219e2814bbedf4faffa9e2b3bb882f` after exact-current-base strict, installed-hook, privacy, dependency, Codecov and native checks plus independent artifact review. Rust formatting, five grouped ontology tests, all-target/all-feature Clippy and the actual catalogue replay pass; branch-aware changed-line coverage is 100% (263 production lines, none missing). This closes T01.09a / T01.ontology_context and bounded T07.03e, with parent scientific admission and N1 still open.

The accepted head `be9aaaac189a21c87b8ec646b1b308c558b9f2da` was based on `9480311be20d51962ed9ce41684bf0bb56440f95`, retaining PR #22's native hg38 denominator change and this ontology/Reactome extension. The later control-label audit limits that technical run to historical legacy-route execution and a fixed-denominator audit; intended negative-control backgrounds remain unqualified as detailed below. Tested merge `adc790ecb6d7451140f3e494314ead7d4f2b56dc`, actual local commit `b37eaf54d81632552460624bc375428a850fdacf`, API candidate and actual merged main share tree `8c9feacf04c3277338dea7835a6f6d70dfd76f27`. **Merged-main strict run [45417852753](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45417852753) subsequently passed on `92639afe9b219e2814bbedf4faffa9e2b3bb882f`; the observed API run was updated at 24 November 14:53:50 UTC / 25 November 00:53:50 Australia/Brisbane.**

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

**Actual native run [45413616413](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45413616413), job `138513757775`, passed.** Downloaded artifact `14933475463` is 1,491,415 bytes with SHA-256 `25d363ddf2f4dac17bf306d5d0d46f1fc8bb5d7f044d13b8179e4ae63a08638a`; the API digest and ZIP CRC matched. Its source-revision file names the exact tested merge above. The container exited zero with `OOMKilled=false`. The initial failed native attempt remains recorded below.

| Actual Reactome result | Value |
|---|---:|
| Numeric human source pathways | 2,861 |
| Pathways with no gene in the tested universe | 683 |
| Complete eligible tested family | 2,178 |
| Native universe genes / genes represented in Reactome | 2,906 / 1,705 |
| Native selected genes represented in Reactome | 118 |
| Raw probabilities outside [0,1] | 692, all above one |
| Native integer-zero DE rows | 1,541 |
| Integer-zero rows with positive fractional overlap below one | 72, maximum 0.5 |
| Probabilities changed by the bounded receiver | 1,394 |
| Positive-count probabilities changed | 0 |
| Maximum absolute probability correction | 4.218847493575595e-15 |
| Independent raw / received full-family BH discrepancy | 0 / 0 |
| Exported FDR values or 0.05 decisions changed | 0 |

Source-set cardinalities were independently recomputed. All raw/received pathway IDs and N/DE fields match exactly, and result N agrees with the family audit's eligible count. The 683 pathways without a measured-universe gene are retained in the family audit rather than removed according to significance. The zero-boundary export has 1,469 rows with zero fractional overlap and 72 with positive fractional overlap below one; all have native integer DE zero and a direct inclusive tail of exactly one. **Raw native probability-domain acceptance is false for both GO and Reactome.** The bounded corrected receivers pass; this is not permission for a general probability clip, nor a claim that every native zero-integer row has no biological overlap.

Reactome raw table SHA-256 is `402befe6afdf44a4d52218434f888c83aa53ec8f2584f1909e28516e343e8d9c`; received table SHA-256 is `3c99410fb208c08cc3eeb85fbd37b1385042518cfbf1b399121ab35fe5e88dd5`. The full 13,817-term GO raw and received tables are byte-identical to the earlier accepted outputs, preserving 4,253 raw invalid probabilities, 8,704 tiny zero-count corrections and no BH changes. Independent review covers source cardinalities, exported family/IDs/N/DE, boundary values, raw/received domains and full-family BH. Native per-gene mapping vectors and all positive fractional weights are checked by the pinned R runtime assertions; they are not separately exported for an independent reconstruction of the complete model.

### Historical legacy-route execution and fixed-denominator audit

The historical legacy route used a native hg38 fixed denominator of **408,966** eligible CpGs and labelled **366,308** finite-M observations valid (**89.5693%**). The disjoint partition is 292 bead/missing-address exclusions, 42,366 subsequent detection-threshold exclusions and 366,308 valid observations; the other exclusive reasons are zero. Marginal processing-mask failures overlap those reasons and are not added again. The sorted denominator SHA-256 is `1d413041ee2bee0666b42ccb0a50c5180a305a4684f1327559796ec67e5f2366`. All seven QC exports match PR #22's completed successor byte-for-byte, including the native panel, masks, exclusion table and the 848-row control export. Those rows have malformed numeric labels; they are not validated control identities.

The fixture **does not meet** the prospective 95% valid-fraction criterion. That clinical threshold and clinical control acceptance ranges remain unvalidated. The recorded run and denominator/count audit do not qualify intended negative-control backgrounds, sample suitability or cohort QC. Native hg38 QC coordinates and hg19 gene annotation joined by CpG ID stay separate. The synthetic limma stage retains 128 features, 12 samples, one missing value and rank four; OLS/CI errors are zero, maximum p error is 3.33066907387547e-16 and BH error 4.44089209850063e-16. Its 5.55e-17 BH-error difference from PR #22 is rounding-scale; all other summary metrics agree.

#### Control-label defect and corrected-route hold

Independent review of the actual #22/#23 `technical-cohort-qc-controls.tsv` found **all 848 exported `Type` values numeric (3–58)**, rather than canonical control labels. The shared table SHA-256 is `86b22d86cfc0adb5f660c0034d1ae28374b1d43f21819b3a6e99555aa6d7c33a`. This is a directly observed artifact defect. The historical artifacts do **not** separately export the runtime row count returned by `negControls(raw3)`.

The diagnosis follows pinned SeSAMe 1.28.1 source at `3fa12279a56279c9edf3a82fa9b646fb0e3abaef`: [`readIDAT1` emits G/R/GN/RN, while legacy `readControls` applies obsolete positional names](https://github.com/bioc/sesame/blob/3fa12279a56279c9edf3a82fa9b646fb0e3abaef/R/sesame.R), placing red bead count `RN` in `type`. [`controls()` prioritises this legacy attribute](https://github.com/bioc/sesame/blob/3fa12279a56279c9edf3a82fa9b646fb0e3abaef/R/SigDFMethods.R); [`negControls()` searches probe ID and then control type, and pOOBAH uses negative controls by default](https://github.com/bioc/sesame/blob/3fa12279a56279c9edf3a82fa9b646fb0e3abaef/R/detection.R). [`noob` also defaults to combining negative controls with out-of-band signals](https://github.com/bioc/sesame/blob/3fa12279a56279c9edf3a82fa9b646fb0e3abaef/R/background.R). This source diagnosis is distinct from a separately exported historical runtime assertion. **The intended negative-control backgrounds remain unqualified pending an exact-source corrected-route replay and review.** [PR #24](https://github.com/edithatogo/rare-omics-atlas/pull/24) proposes that correction; its fix and proposed N1 revision are not accepted by this receipt.

The defect concerns the technical preprocessing stage. At reviewed PR #24 head `3d4cceaf2b8e4f0c5ca4a1a96f50532efd3e5c8c`, the complete limma/enrichment suffix beginning `if (stage=="limma")` remains byte-identical to #23: 21,651 UTF-8 bytes, SHA-256 `74ad323568c82f4469b342c69f53ea4b86d61b2029c57802ead8792c12c8adc0`. The earlier generation of the historical 4,000 tested/200 selected synthetic CpGs is unchanged. T01.09a and the bounded T07.03e synthetic receiver therefore retain their separately evidenced acceptance; no corrected technical QC or clinical use is inferred.

The historical combined candidate is bound to these actual code/contract bytes:

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
| [Initial hosted strict 45409996763](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45409996763) | Failed with one history finding. A subsequent scan of currently fetched refs returned zero findings with no scanner waiver. Association with an outdated PR #22 prose head then present in fetched history is an **inference**, not an established causal result. The failed attempt remains failed; the later combined hosted history scan passed over 59 commits with zero findings and no waiver. |
| [Initial native 45409996742](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45409996742) | Failed in the technical stage at minfi annotation loading, before limma and enrichment. Downloaded artifact `14926959908` has SHA-256 `5e51e7cfe118bf14268b19a7bb1d39fa8271fb8cc4caecb2eea0720daa0dfd25`. No Reactome operation was exercised. |
| [PR #22](https://github.com/edithatogo/rare-omics-atlas/pull/22) receiving | Merged as `9480311be20d51962ed9ce41684bf0bb56440f95` at **24 November 2026 14:18:54 UTC / 25 November 00:18:54 Australia/Brisbane**, while [native run 45410579769](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45410579769) remained in progress. It subsequently passed, finishing at 14:25:37.738 UTC; artifact `14931035812`, 1,420,961 bytes, SHA-256 `8aff87ff3565a2f65ccee07599f12f9b47708a87e023a32d8ba284757f6c9c9b`. The premerge native-evidence gap remains historical; the later pass does not erase it. |
| Accepted combined ontology implementation | Replayed onto actual main without textual conflict. Local committing hook passed 34/34 in **54.331 seconds**. [Hosted strict 45413616626](https://github.com/edithatogo/rare-omics-atlas/actions/runs/45413616626), job `138513759659`, replayed the installed hook and passed 34/34 in **258.744 seconds**. The source-content SHA-256 is `e4619c9083d63e5e1bfd95411a5f30ba3561c001d62a2b5437c5c770139701de` in both receipts. Privacy, dependency review and Codecov patch passed; native run and independent artifact review passed before PR #23 merged. |

Hosted strict artifact `14932621724` is 247,897 bytes with SHA-256 `fcc1b4c6bb489aa72bfd682fb0ea0c401bfec8a42241a5e9f5ac50b5065ca987`; download digest and ZIP CRC passed. The history scan covered 59 commits with zero findings and no waiver. The accepted code's patch coverage was 100% over 263 changed production lines. The subsequent receiving-main strict run also passed, as recorded above.

The existing [native receipt](t07-native-reference-candidate.md#receiving-history-reconciliation) preserves earlier ordering gaps and the original fixed-denominator annotation failure. This receipt records the later exact-source qualification while preserving those failures. No cross-build region mapping or clinical threshold acceptance follows from integration.

Targeted Rust tests exercise mapping direction, related/ambiguous/unmapped/unreported states, original-label preservation, input hashes, separate disease semantics, malformed/duplicate/conflicting input, disclosure boundaries, file-size limits and read-only CLI behavior. The bounded implementation is now merged with the exact-tree qualification above. This follow-up records evidence and Conductor completion only; executable code, workflow and Reactome contract bytes remain unchanged. Its own applicable strict/hook/hosted checks are still required before merging these receipt edits; it does not relabel historical native output as a new execution.

The [resource priorities](../resources-hosting-reuse.md#ontology-and-annotation-priorities) and existing Conductor tracks now cover HGNC/Ensembl/SO, regulatory resources, ECO/PROV-O, protein, reaction, metabolite and cross-species resources as named consumers require them. They do not imply that every resource has been downloaded or analytically validated. Frozen molecular-only, ontology-only and combined comparisons, source-removal ablations and outcome-leakage controls apply to selected scientific uses.

Clinical cohort admission, material participant/family and cross-study independence, any required per-control provenance, actual-device qualification, the applicable institutional determination and analysis-specific N1 remain open. The [separate primary-Methods receipt](t01-molecular-decision.md#primary-methods-bytes-and-scoped-source-disposition--25-november-2026) supports the pooled native-control recruitment context without resolving individual recruitment site or biological independence. No disease analysis, patient phenotyping, new independent observation or demonstrated clinical benefit results from this increment.

### Subsequent negative-control correction candidate

Prior-base PR #24 native run 45418562201 and strict/hook run 45418562021 passed for the exact candidate tested against 92639afe9b219e2814bbedf4faffa9e2b3bb882f. The later PR #25 receipt-only merge at bcccd781fea89895c0ca1e4af1ea43f8d45e1073 passed main strict run 45424094141. This candidate retains those receipt changes and the unchanged tested R blob. Fresh exact-current-base native, strict/hook, privacy, dependency, coverage and review are still required before integration; the prior pass is not a current-base pass.

The prior-base native correction reproduced zero legacy negative controls and restored 614 finite negative-control pairs from 850 manifest controls (848 available pairs, two explicitly unavailable). The fixed hg38 denominator remains 408,966; 366,397 valid (89.59106625%), versus 366,308 legacy, 89 gained and zero lost. Disjoint exclusions: 292 bead/address and 42,277 subsequent detection failures. Across all 486,427 probes, 436,288 detection p-values, 94 masks and 376,178 beta values changed; maximum p-value and beta differences 0.00288613970205076 and 0.00284753124099446; independent ECDF error zero and direct/staged native noob comparison passed. The same fixture still fails the prospective 95% rule. The technical exercise is not clinical cohort QC. GO and Reactome raw/received table digests are unchanged on the original synthetic universe; no ontology data or scientific admission change. See the [native correction receipt](t07-native-reference-candidate.md).
