# Experiments and publication bundles

**Planning revision, 22 November 2026. No experiments executed.** Use the existing T01–T07 tracks; these experiment identifiers describe scientific work within them, not new projects. The [analysis scores](analyses.md), [journal routing](journals.md) and [N0–N3 review protocol](novelty-priority-protocol.md) apply.

## Default recommendation

Start with **one clinically focused study of the reproducibility and limits of biological interpretation in Kabuki blood methylation data**. Combine cohort qualification, platform robustness, differential effects, pathway/region replication and any backend qualification in one coherent paper and its supporting material. A separate paper is not owed to each capability.

This first study is a decision point: publish only if it establishes a worthwhile new or independently valuable conclusion. If it is merely a repeat of known findings, retain the qualified reference workflow and benchmark artefacts and move on. A distinct cross-disease comparison can be added to the same paper if it sharpens the same clinical question.

The more ambitious later opportunity is **calibrated transfer of molecular effects across rare diseases**, possibly strengthened by independently informative expression data. It requires enough qualified disease/study contrasts and real held-out validation. Neither adding ontology labels nor drawing a multilayer graph establishes a novel biological result.

## Concrete experiment sequence

| ID / track | Question and proposed data | Analysis and output | Decision gate |
|---|---|---|---|
| **E0 — T01** | Are comparisons possible? Begin GSE97362, GSE116300 and GSE218186; then GSE74432/GSE191276 and qualified additional diseases | Resolve participant–specimen–assay identities, molecular diagnosis, native controls, age/sex/tissue, platform, batch, cell covariates, reuse, files/checksums and rights. Produce an eligibility and exclusion table | Count people separately from arrays, pooled DNA and synthetic samples. Hold unresolvable diagnosis, dependence or complete case/batch confounding. No raw download is implied by this plan |
| **E1 — optional T07/T02** | How much do the same specimens disagree across 450K and EPIC? Candidate paired reference GSE86829/GSE86831, SuperSeries GSE86833 | Freeze a small matched subset and preprocessing comparison. Measure bias, absolute beta differences, locus/region agreement and uncertainty; compare same-platform repeats if available | A technical stress test only. Do not add it if it answers no remaining question, or treat these specimens as rare-disease controls |
| **E2 — T02** | What is the disease-minus-control effect within each Kabuki study? 450K GSE97362/GSE116300; EPIC GSE218186 | Qualified raw processing/QC, estimable within-study covariates, consistent masks/builds and labelled beta/M matrices. Estimate CpG and prespecified regional effects with uncertainty. Compare Rust and reference implementations on the same fixed processed input | Keep reference method usable if a candidate backend fails. Mixed historical diagnosis subsets and seven EPIC cases limit inference. Separate preprocessing-method changes from differential-backend changes |
| **E3 — T02** | Which discovery findings transfer to an independent cohort? Same admitted Kabuki cohorts | Select the discovery cohort/development set in advance, reserve EPIC replication, freeze regions/pathways, signs and primary metrics before inspecting test effects. Test against the held-out cohort's own controls. Report effect direction/magnitude, interval uncertainty, actual gene/region drivers and bias-aware enrichment | Useful reproducibility or failure-boundary finding required for P1. Nonsignificance in a small cohort is not absence. EPIC-only features remain exploratory without an independent EPIC test |
| **E4 — T03** | Does a focused comparison explain reproducible differences? Add Sotos/Weaver GSE74432, Sotos EPIC GSE191276, and DNMT3A only after sufficient cohort qualification | Compare within-study effects, separate hyper/hypomethylation, use regulatory-context/probe-density matched nulls, account for shared controls. Contrast allelic mechanisms, not just gene names | Already crowded prior art. The three Sotos cases and three individual controls are corroborative; the pooled parental array is one assay. GSE167230's two TBRS samples without new native controls do not establish an adequate TBRS comparison |
| **E5 — T04** | Does sharing information improve held-out effects? Use admitted disease effect/SE tables from E2/E4 | Compare independent models, full pooling and simple partial pooling before a network prior. Train-only feature selection, normalization parameters and modules. Whole-study and whole-disease holdouts; evaluate predictive loss, uncertainty coverage, negative transfer and abstention; test ontology ablations | An unseen disease prediction may use only predictors available without its masked molecular outcomes. Otherwise describe the task as denoising or within-disease prediction. If simple models match, retain them |
| **E6 — T05** | Does expression add independent information? Sotos GSE191276 + GSE191274; ADNP GSE152427 + GSE152421 after eligibility/pairing checks. Later Kabuki neural-model RNA/ChIP lead GSE289159/GSE289158, with source-specific verification limits below | Verified paired participants: methylation-only, expression-only and combined models with participant/family holdouts. Unpaired cohorts: disease-level directional confirmation, not patient correlation. Neural-model overlays are cross-tissue/cross-assay interpretation. Preserve mapping and missing-view assumptions | Tiny paired sets do not support unconstrained network learning. Existing Sotos/ADNP/Kabuki integrations must be exceeded by a distinct question, replication or predictive result. Do not make this extension a prerequisite for P1 |
| **E7 — later T05/T06** | Can one molecular prediction be falsified? Assay/model chosen from E3–E6 | Specify perturbation direction, relevant cell model, controls, blinded analysis, outcome and adequate replication before the experiment. An independent public perturbation dataset may supply supportive evidence where truly independent | New experimental scope and applicable governance required. Association does not identify causal direction, drug benefit or reaction rates. Toxin work remains separately gated |

**Order:** E0 → E2 → E3. E1 is an optional supporting experiment. E4 follows only if its contrast remains worthwhile; E5 and E6 are ordered by data readiness and scientific value. E7 is not a prerequisite for a modest clinically useful replication paper.

At every step, N0 selects the claim, N1 freezes analysis and evaluation, N2 checks intervening publications after results, and N3 refreshes before submission/transfer. The current review is a targeted desk update, not a completed systematic search or an executed N1 protocol.

## Integrating raw 450K and EPIC arrays

### Same person, same specimen, or different people?

| Situation | Correct use | What it cannot establish |
|---|---|---|
| Same DNA/specimen on both platforms | Paired technical comparison; quantify bias and unreliable loci/regions; choose one biological observation or model repeated assays explicitly | Two independent patients or biological replication |
| Same person, different collection time/tissue | Repeated-measures or longitudinal design, with time/tissue effects and participant grouping | Pure technical equivalence; independent train/test observations |
| Different patients with cases and native controls in each cohort/platform | Estimate disease effects separately, then compare or meta-analyse common-feature effects with uncertainty and heterogeneity | A uniquely isolated platform effect, because laboratory, recruitment and other study factors also differ |
| Disease only on one platform and controls only on another | Seek a genuinely informative design/reference; otherwise hold or restrict the claim | Batch correction cannot identify an absent disease-versus-platform contrast |

Normalize raw intensities using a specified, qualified method and matched annotation/mask versions. A single-sample method such as minfi ssNoob or the qualified SeSAMe workflow is a sensible candidate for incremental intake. It does not make every platform artefact disappear. Minfi supports common-probe virtual arrays, but its original EPIC integration evaluation was small and described as preliminary: [Fortin et al. 2017](https://doi.org/10.1093/bioinformatics/btw691), [minfi guide](https://bioconductor.org/packages/release/bioc/vignettes/minfi/inst/doc/minfi.html).

For the main cross-platform comparison, intersect **valid, consistently identified probes after QC**, using the same genome build and annotation semantics. A nominal shared CpG ID does not prove identical assay behavior. Retain platform-specific features for separately labelled within-platform analyses. Do not fill unmeasured 450K sites with zeros or treat an imputed value as measured. Preserve the CpGs and coverage contributing to each region; matching a region name alone does not equalize measurement.

Keep empirical-Bayes moderation and FDR families global to their prespecified contrast, even if data are stored in chunks. A cohort/meta-analysis approach is usually easier to interpret than pooling all beta values and trying to remove study effects afterwards. Shared controls induce covariance and cannot be reused as independent evidence. Residualization, batch estimates, feature selection and module construction learned from held-out data can invalidate a claimed prospective transfer test; explicitly distinguish transductive analysis from new-cohort prediction.

Whole-methylome sample correlation is insufficient: high correlation can coexist with poor agreement at individual low-variance loci. Include per-feature bias/absolute differences and region-level agreement with uncertainty; use ICC only with an appropriate formulation and enough replication. Sources: [Logue et al. 2017](https://pubmed.ncbi.nlm.nih.gov/28809127/), [Solomon et al. 2018](https://pubmed.ncbi.nlm.nih.gov/30044683/).

### Concrete optional technical subset

The [official RnBeads vignette](https://www.rnbeads.org/materials/data/tutorial/cross_platform/tutorial.html) describes GSE86831 EPIC profiles as the same samples represented by GSE86829 450K, including infant blood from archival Guthrie cards. The [GSE86833 record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE86833) lists a 677.4 MB IDAT archive and the following candidate pairs:

| Label | 450K assay | EPIC assay |
|---|---|---|
| Guthrie T-73 | GSM2309164 | GSM2309180 |
| Guthrie T-75 | GSM2309165 | GSM2309181 |
| Guthrie T-76 | GSM2309166 | GSM2309182 |
| Guthrie T-80 | GSM2309167 | GSM2309183 |
| Guthrie T-82 | GSM2309168 | GSM2309184 |

Before use, inspect each GSM, actual files and original study to confirm pair identity, raw chemistry, repeats and source rights. These five archived dried-blood specimens supply a small technical stress test, with storage/tissue limitations and imprecise locus reliability estimates. They are **not controls for the rare-disease contrasts**. No archive was downloaded here.

Useful outputs from E1–E3 are a feature-coverage table, agreement/instability estimates, a reproducible shared-feature reference, independent disease-effect transfer results, and clearly labelled EPIC-only hypotheses. More measured sites do not automatically create more independent evidence or a better disease classifier.

## Paper decisions and alternatives

| Bundle | Content | Required central contribution | Initial journal route |
|---|---|---|---|
| **P1: default clinical bundle** | E0 + E2 + E3; E1/backend qualification as supporting material | Reproducibility and clinically meaningful limits of interpretation in Kabuki blood methylation. No new episignature or diagnostic-utility claim without appropriate validation | Molecular Syndromology; backup European Journal of Medical Genetics. BMC Pediatrics if a substantive paediatric clinical question drives the paper; AJMG Part A if genotype/phenotype interpretation warrants it |
| **P1 extended** | P1 + one focused E4 contrast | One coherent comparative clinical question with stronger evidence than separate small analyses | EJMG or Molecular Syndromology; OJRD if relevance extends substantially beyond the initial disease |
| **P2: conditional combined transfer study** | E4 + E5, plus E6 when expression provides independent information | Reliable borrowing of information, uncertainty/negative-transfer boundaries and independently tested predictions beyond existing convergence studies | OJRD for a clinically interpretable result; BMC Medical Genomics as an alternative. BMC Bioinformatics or Bioinformatics Advances when the principal contribution is methodological |
| **Focused metabolic/functional study, only if justified** | Adequate E6/E7 and a real inherited-metabolic or diagnostic question | Mechanism or diagnostic interpretation supported by appropriate data; not merely an enriched metabolic term | JIMD Reports for focused sound work; JIMD for stronger evidence likely to influence metabolic practice/research |
| **Optional software/methods paper** | Broad, reusable validation or a genuinely new method from T07/E5 | Demonstrated research value, independent comparisons and maintainable software; more than a port, wrapper or compiler feature | BMC Bioinformatics or Bioinformatics Advances; JOSS only if its actual substantial-software/research-use criteria are met |

There is **no target number of papers**. If E4–E6 are too small to support a distinct contribution, combine them with the initial study where scientifically coherent or retain them as exploratory supporting work. Do not delay a sound completed study indefinitely for speculative additions. Do not publish overlapping primary claims twice.

**Keep as supporting artefacts by default:** metadata catalogue, ontology crosswalk, Arrow round trip, IDAT backend comparison, Rust-versus-R parity, library fixes, compiler/GPU benchmarks and failure cases. Such work can be valuable without a standalone manuscript.

Scores in [analyses.md](analyses.md) rate the study/bundle, not the libraries. Feasibility depends on participant-level eligibility and independence, not simply the number of GEO records. Manuscript scope, article type, fees and current editorial policies are rechecked at N3; no acceptance probability is inferred from journal impact factor.

## Prior art already narrowing the opportunity

A targeted update reconfirmed the following overlaps; it does not establish that a proposed precise analysis is the first:

- [Velasco et al. 2021](https://doi.org/10.3390/ijms22073735) already compared methylation across chromatin disorders including relevant NSD1/DNMT3A mechanisms.
- [Levy et al. 2022](https://doi.org/10.1002/humu.24446) compared functional methylation patterns across 65 syndromes.
- [Giuili et al. 2023](https://doi.org/10.1007/s00439-023-02609-2) assessed Kabuki/Sotos normalization, classifiers and missing-feature effects.
- [Cuvertino et al., 2025 issue](https://doi.org/10.1093/bib/bbae667) already analysed Kabuki higher-order/hypergraph structure using published cohorts.
- [Cuvertino et al., PLOS Genetics, September 2025](https://doi.org/10.1371/journal.pgen.1011608) integrated H3K4me1 ChIP-seq and RNA-seq across Kabuki iPSC, neuronal-progenitor and cortical-neuron stages. These are **histone-mark data, not DNA methylation arrays**. The article lists GSE289158/GSE289159; the official indexed GSE289159 record identifies 23 RNA assay records and a 5.5 MB gene-count file, whereas GSE289158's specific file inventory could not be directly verified. The principal ChIP comparison uses one affected line and one control line in triplicate, limiting donor-level generalisation. This is a later E6 model-layer lead and substantial prior art, not paired blood multiomics or evidence of rescue.
- [Brennan et al. 2022](https://doi.org/10.1093/hmg/ddac026) already integrated Sotos/NSD1 methylation and expression.
- [Wheeler et al., online 27 December 2025 / 2026 volume](https://link.springer.com/article/10.1186/s13072-025-00650-1) studied NSD1–DNMT3A enhancer/bivalent-promoter convergence in engineered models and patient data. Merely adding DNMT3A does not restore novelty. GSE299394/GSE309381 are later cell-model candidates, subject to access, design and prior-use review.
- [Wang et al. 2026](https://doi.org/10.1016/j.ajhg.2026.04.010) reported expanded Kabuki episignature/variant mapping with 110 KMT2D carriers and 854 controls. A new small classifier is a weak default.
- [Hansknecht et al. 2026](https://link.springer.com/article/10.1186/s13148-026-02162-5), with Puri as co-senior author, studied NSD1-KO iPSC methylation/RNA/differentiation and compared Sotos GSE191276. Blood-to-cell-model comparison is also not an untouched idea.

Order-invariant batch fitting, ordinary platform integration and generic pathway overlap are established approaches. The prospective contribution must be a particular, falsifiable clinical or methodological claim with an honest independent test and useful uncertainty.

