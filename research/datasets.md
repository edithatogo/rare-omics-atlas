# Dataset inventory and qualification status

Updated 22 November 2026. Three initial Kabuki archives have now been **downloaded and header checked**; see the [exact source receipt](qualification/initial-source-receipt.md). That is a completed access/format check, not admission to disease inference. The [rights register](dataset-rights.md) distinguishes research reuse, distribution, hosting and institutional status for each reviewed source. Sample/assay counts remain distinct from independent affected participants.

| Disease / material | Public identifier | Source | Planned analysis | Critical gate |
|---|---|---|---|---|
| Kabuki and CHARGE | GSE97362 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362 | Kabuki DMP/DMR/pathway discovery | Identify KMT2D molecular subset, source controls, overlap |
| Kabuki phenotypic cohort | GSE116300 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300 | Kabuki replication | KMT2D status, case eligibility, sample reuse |
| Kabuki EPIC | GSE218186 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186 | Candidate independent platform replication | 62 IDAT pairs transferred; seven source-labelled cases  and 55 controls, with independence/covariates still required |
| Sotos / Weaver | GSE74432 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE74432 | NSD1/EZH2 cross-disease regions | Verify variant/phenotype labels and controls |
| Sotos EPIC | GSE191276 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE191276 | Sotos external effect estimates | Three cases, three individual controls, pooled DNA sample not individual |
| Sotos RNA | GSE191274 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE191274 | Expression validation | Sample pairing to GSE191276 not assumed |
| TBRS/SETD2/ICF targeted | GSE167230 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE167230 | Prior-art cross-disorder comparator | Only seven newly deposited records; locate reused external cohorts |
| 7q11.23 deletion/duplication | GSE66552 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE66552 | Dosage asymmetry comparison | Molecular diagnoses and matching |
| SMARCA2-related Nicolaides–Baraitser | GSE125367 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE125367 | Out-of-family validation | Access and independent controls |
| ADNP methylation | GSE152427 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE152427 | Mutation-class epigenomics | Qualified affected sample IDs |
| ADNP RNA | GSE152421 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE152421 | Cross-modal test | Reconcile participant pairing with GSE152427 |
| AGS methylation | GSE221644 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE221644 | Negative transfer test | Interferon, tissue and cell composition |
| CHD2 / epilepsy | GSE269416 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE269416 | Generalisation test | Mixed diagnoses; stratification mandatory |
| C3 glomerulopathy RNA panel | GSE261305 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE261305 | Complement disease mapping | Not all individuals genetically confirmed |
| King cobra venom proteomics | PXD003403 | https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD003403 | Toxin-side complement model | Venom source, not host response or quantitative exposure |
| Same-specimen technical array reference | GSE86829 / GSE86831, SuperSeries GSE86833 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE86833 | Optional E1 450K–EPIC paired stress test | Official RnBeads tutorial identifies same specimens; qualify five Guthrie-card pairs, individual GSM/file mapping and rights; not disease controls |

The machine-readable rights/intake registers now record bounded source evidence. The eventual admitted assay manifest must additionally include `open_raw`, `open_processed`, `controlled`, `request_only`, `unknown` access classes; third-party reuse permissions; each sample's `role` and provenance; exact archive checksums; and flags for train/test contamination.

The optional technical reference lists a 677.4 MB SuperSeries raw archive. The five paired labels and exact GSM candidates are in the [experiment plan](experiment-publication-plan.md); the supporting primary source is the [official RnBeads cross-platform tutorial](https://www.rnbeads.org/materials/data/tutorial/cross_platform/tutorial.html). This is repository/tutorial evidence, not a completed download or technical validation. Public SeSAMe platform fixtures are separately recorded in the [backend audit](methylation-backend-audit.md); a software fixture is not a clinically independent replication cohort.

Wheeler DOI [10.1186/s13072-025-00650-1](https://doi.org/10.1186/s13072-025-00650-1) explicitly reuses Sotos GSE191276, TBRS GSE128801 and HESJAS GSE120428, and introduces GSE299394 arrays and GSE301386 CUT&RUN. These relationships materially constrain a generic NSD1/DNMT3A novelty claim. They are future source leads, not admitted independent validation cohorts. Wheeler identifies GSE309381 as RNA-seq; its direct file inventory remains unverified. Do not add a modality merely to increase a dataset count.

### Later Kabuki neural-model layer: RNA and histone ChIP, not DNA arrays

[Cuvertino et al., PLOS Genetics 2025](https://doi.org/10.1371/journal.pgen.1011608) provides a useful E6 discovery lead. The official indexed [GSE289159](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE289159) record identifies 23 RNA-seq assay records across iPSC, neuronal-progenitor and cortical-neuron stages, a 5.5 MB processed gene-count file and raw SRA reads. These are not 23 independent participants. The article also lists [GSE289158](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE289158) for its data; its companion epigenomic work is H3K4me1 ChIP-seq, but this accession's direct GEO modality/file inventory was not retrieved successfully. Do not mark it download-verified or count it as an additional methylation array study.

The paper already tests histone–expression/enhancer relationships and differentiation effects. Its main ChIP comparison has one affected line and one control line in triplicate. A possible later use is testing frozen blood-derived modules against an independently qualified cell-model layer, with explicit donor, tissue and assay limitations. It is neither matched blood methylation–expression validation nor a perturbation-rescue dataset. No files from these two neural-model leads were downloaded, and neither is a P1 prerequisite.

## Current data/ethics decision

Use the [source-access and ethics register](source-access-ethics.md) as the source of truth for public landing status, concrete archive types, original sizes, no-login rules, separate downstream rights, and institutional ethics/exemption decision gates. **GSE97362, GSE116300 and GSE218186 have passed the explicitly bounded transfer/header checks.** No source has yet been accepted for statistical disease inference. The ProteomeXchange record is released but legacy FTP retrieval remains untested. Avoid unqualified republication of rare-disease participant-level molecular data.


## Additional paired array reference and prior use

[GSE92580](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92580), with 450K subseries GSE92577 and EPIC subseries GSE92579, supplies nine fresh-frozen and three FFPE cross-platform specimen pairs. Additional FFPE records paired with the first nine tumours address a different preservation comparison. The independent participant count has not been established here. It is technical evidence, not a whole-blood control cohort. The listed SuperSeries raw size is 789.5 MB; no transfer is claimed.

Cheung already jointly reanalysed GSE86833 and GSE92580. The [platform review](platform-comparison-review.md) documents this and the approval-required Drakenstein three-platform study. Prior work also reused GSE97362 in the Multi-State Epigenetic Pacemaker; inclusion of its affected Kabuki subset is unresolved. See the [explicit literature edges](literature/README.md), not an assumption that an accession has never been modelled.

## Initial ontology crosswalk

The [five-condition crosswalk](registries/initial-disease-crosswalk.tsv) and [reference receipt](qualification/ontology-source-receipt.md) now bind active MONDO/OMIM/gene assertions to actual verified reference bytes. Sotos uses active MONDO:0019349; MONDO:0007299 is obsolete. Kabuki KMT2D and KDM6A are distinct subtypes, and the broad ORPHA:2322 identifier is not an exact subtype mapping. Disease annotation coverage does not create observed HPO phenotypes for a sample.

## Newly checked DNMT3A and chromatin leads

| Source | Public material checked | Eligibility limit |
|---|---|---|
| GSE128801 | 12 blood 450K records; listed IDAT 282.1 MB, beta 27.3 MB and intensities 29.7 MB | Related TBRS pedigree, including four affected children and a mosaic father; not 12 independent affected people. The paper's 15 unrelated EPIC cases are not in this 12-record series |
| GSE120428 | 13 EPIC assays; listed IDAT 342.5 MB | Mixed blood/fibroblasts, repeats, HESJAS/DNMT3A-overgrowth/PCNT comparators and controls. The same paper's human exome/RNA/RRBS/ChIP data are controlled EGA sources, excluded from no-application intake |
| GSE301386 | 15 WT H1/WA01 CUT&RUN assays; archive listed 1.0G, sample bigWig tracks and SRA links | Three labelled replicates per IgG/H3K4me1/H3K4me3/H3K27me3/H2AK119ub condition. Wild-type chromatin reference, not mutant rescue or patient methylation |

No raw archives/sequences from these three additional leads were transferred. Exact sources and per-artifact rights are recorded in the [29-accession register](dataset-rights.md). GEO archive names alone do not establish that a RAW.tar contains sequencing reads.
