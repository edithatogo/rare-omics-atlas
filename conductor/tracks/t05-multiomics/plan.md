# T05 — task-level execution plan (future, not started)

- [ ] **T05.01:** For E6, reconcile Sotos GSE191276 ↔ GSE191274 and ADNP GSE152427 ↔ GSE152421 through participant/specimen records and source tables. Complete N0/N1 with original-study and recent integration overlap, an answerable estimand and a frozen validation plan.
- [ ] **T05.02:** Separate genuinely paired participants from independent disease-matched RNA cohorts. Three Sotos methylation cases cannot support unconstrained individual-level network learning; use prespecified corroboration if justified. Without pairing, restrict to disease-level confirmation and do not calculate invented sample-wise correlations.
- [ ] **T05.03:** Select minimal interpretable cross-modal/regulatory baselines under the language policy. For adequately sized verified paired data, compare methylation-only, expression-only and combined models with participant/family holdouts and training-only mapping/module selection. For selected ontology/regulatory features, also compare molecular-only, ontology-only and combined inputs on the same holdouts, including a source-removal ablation. Freeze species/build/transcripts, MONDO/mechanism, Uberon/CL context, GO/Reactome families and SO/regulatory link semantics before scoring. Assess rsdeseq2 only for the chosen RNA-count estimand; use qualified specialist Python such as mofapy2 only when its model is needed and avoids reimplementation. Generic factorisation is not an equivalent substitution.
- [ ] **T05.04:** Only escalate to ATAC, proteomics or higher-order networks when an independently testable prediction requires them. Any E7 functional experiment has a separate feasible assay/governance plan; an observed methylation-expression association alone supplies no causal perturbation claim.
- [ ] **T05.05:** At N2 assess whether E6 adds independent information to E4/E5 and should join the same P2 paper, remain supporting evidence or stop. Propose a separate metabolic/functional manuscript only for a distinct adequate contribution; review dependencies and complete N3 for any submission.

## Executable batches when this extension is selected

| Order / tasks | Input and action | Output / acceptance |
|---|---|---|
| A: .01 / .02 | Resolve the named GEO/source participant–specimen relations and selected assay-specific rights through T01. Count biological people separately from technical/differentiation records. Freeze the clinical question, pairing class, mapping rules and held-out information in `n1.md`. | Local `data/silver/t05-multiomics/pairing.tsv` plus a cleared aggregate receipt with source IDs and hashes. Verified pairs support paired analysis; unresolved/unpaired records permit only the separately justified disease-level design. |
| B: .03 | Receive the selected T07 assay/inference contracts and actual-device evidence. Name real backend commands before execution. For adequate pairing, run the three frozen baselines under participant/family holdouts; otherwise run the prespecified disease-level confirmation with frozen maps/modules. | Local `data/gold/t05-multiomics/` estimates/uncertainty/evaluation tables and exact execution receipt. Pass the pairing, mapping, leakage and numerical contracts; no sample-wise correlation from invented pairs and no outcome-driven remapping. |
| C: .04 / .05 | Execute N2, test whether the additional modality supplies independent information, and decide combine / supporting evidence / stop. | `n2.md` with evidence and publication role. Any new perturbation experiment or additional modality starts only after its separate scientific/governance decision; associations remain associations. |

T05 need not wait for T04 unless it actually consumes that model. It waits for its own cohort/pairing and selected-method gates; existing T01/T07 owners resolve those missing receipts. Use the shared strict entry point for any bounded code addition.

### Annotation consumers within T05.03/.04

Receive exact product/release/hash and mapping/coverage receipts under the [shared resource priorities](../../../research/resources-hosting-reuse.md#ontology-and-annotation-priorities). HGNC/Ensembl establish gene/transcript identity; SO types sequence features; Uberon/CL describe reported source or model context. Retain cell-line identity, differentiation stage, tissue and original labels separately. An iPSC-derived neuron is not an independent patient's brain measurement, and a broader term does not resolve an unknown subtype.

Use EpiFactors for sourced regulator/complex classes and selected ENCODE/Ensembl regulatory assets for the actual build/tissue/assay question. Preserve proximity, overlap and supported target relations separately; test whether regulatory information improves over the frozen proximity baseline. Where justified by measured modalities, PR/UniProt add protein-form identity and Rhea/ChEBI/HMDB add reaction/metabolite context. Open Targets, Monarch/MP and KEGG remain conditional; no extra source or modality is a prerequisite without a selected consumer. Keep evidence types and derivations in existing records, using ECO/PROV-O where they answer an interchange need.

Group every modality of a participant/family in the same split. Freeze source releases and outcome-derived edge exclusions; fit learned maps/modules only within training folds. Retain primary evidence so repeated aggregator assertions count once. Report coverage, calibration/uncertainty and negative transfer along with incremental performance. For small/unpaired cohorts, use the prospectively specified descriptive or disease-level corroboration; do not manufacture a predictive claim or paired observations from ontology annotations.

## Receiving record

**Additional E6 lead:** qualify the later Kabuki neural-model RNA/ChIP accessions GSE289159/GSE289158 only if a frozen blood-module question needs them; see [dataset limitations](../../../research/datasets.md#later-kabuki-neural-model-layer-rna-and-histone-chip-not-dna-arrays). Histone ChIP is not a DNA methylation array, differentiation/technical replicates are not independent donors, and GSE289158's direct file inventory remains unverified. Existing histone–expression integration is prior art, not a new result of this project.

- Assigned owner: **unassigned**
- Branch / pinned head: **none**
- Data rights and checksum receipts: **not run**
- Exact tests / numerical baselines: **not run**
- Publication / ethics gate: **not assessed**
- Conductor disposition: **planned**

Before marking complete, link exact evidence and obtain the integrator's receiving acknowledgement. Never infer completion from a document or synthetic fixture alone.

### 24 November source-record audit and incremental question

[Actual aggregate metadata review](../../../research/experiment-publication-plan.md#executed-public-metadata-pairing-audit-aggregate-only): Sotos companion RNA series contains six exact array/RNA titles (three cases and three individual controls); pooled-parent array excluded from individual matching. Confirm donor/specimen/timing/family and file/rights before claiming pairs. Only a small prospectively defined directional/module or agreement analysis is plausible at that paired size. ADNP SuperSeries contains 36 RNA and 57 DNA assay titles with differing naming conventions; obtain the author-provided crosswalk, never align by order. No new individual-level output produced. The source studies already integrate methylation and expression; select a narrow incremental benefit against existing results and methylation-only/expression-only baselines, or stop. Additional measurements on the same participants are specifically desirable, but split/resample by participant/family across every modality and source; model repeat/visit/tissue where relevant. For unpaired cohorts/cell models use only prespecified disease-level or cross-tissue corroboration, not invented paired correlations or independent patient validation. The [additional source leads](../../../research/datasets.md#additional-measurements-and-cohort-reuse--24-november-review) include request-only human PBMC measurements, published organoid multiome and public processed-only organoid lead; no data requests, new infrastructure or mandatory extra layer. Existing T05.01–.05 and N1/N2 govern all work.
