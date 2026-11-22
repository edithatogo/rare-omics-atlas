# Candidate datasets (NOT yet qualified)

Repository-level public status and raw/processed download listings for the initial candidates were checked in the [source-access and ethics audit](source-access-ethics.md) on 22 November 2026. Actual file transfer and data-specific permission remain **unverified**. Newly added discovery leads below retain their own source-verification limits. Sample-level evidence and rights review are still required in T01. GEO series counts contain controls, other diagnoses and multiple assays; they are **not** automatically number of affected individuals.

| Disease / material | Public identifier | Source | Planned analysis | Critical gate |
|---|---|---|---|---|
| Kabuki and CHARGE | GSE97362 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362 | Kabuki DMP/DMR/pathway discovery | Identify KMT2D molecular subset, source controls, overlap |
| Kabuki phenotypic cohort | GSE116300 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300 | Kabuki replication | KMT2D status, case eligibility, sample reuse |
| Kabuki EPIC | GSE218186 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186 | Independent platform replication | Seven reported affected cases, verify raw files and cases |
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

Data register must later include `open_raw`, `open_processed`, `controlled`, `request_only`, `unknown` access classes; third-party reuse permissions; each sample's `role` and provenance; exact archive checksums; and flags for train/test contamination.

The optional technical reference lists a 677.4 MB SuperSeries raw archive. The five paired labels and exact GSM candidates are in the [experiment plan](experiment-publication-plan.md); the supporting primary source is the [official RnBeads cross-platform tutorial](https://www.rnbeads.org/materials/data/tutorial/cross_platform/tutorial.html). This is repository/tutorial evidence, not a completed download or technical validation. Public SeSAMe platform fixtures are separately recorded in the [backend audit](methylation-backend-audit.md); a software fixture is not a clinically independent replication cohort.

Later NSD1/DNMT3A engineered-cell studies (GSE299394 and GSE309381) are **discovery leads only**, not admitted cohorts. Their main contribution and relationship to patient datasets must first be assessed against the prior art in the experiment plan. Do not add them automatically merely because they increase modality count.

### Later Kabuki neural-model layer: RNA and histone ChIP, not DNA arrays

[Cuvertino et al., PLOS Genetics 2025](https://doi.org/10.1371/journal.pgen.1011608) provides a useful E6 discovery lead. The official indexed [GSE289159](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE289159) record identifies 23 RNA-seq assay records across iPSC, neuronal-progenitor and cortical-neuron stages, a 5.5 MB processed gene-count file and raw SRA reads. These are not 23 independent participants. The article also lists [GSE289158](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE289158) for its data; its companion epigenomic work is H3K4me1 ChIP-seq, but this accession's direct GEO modality/file inventory was not retrieved successfully. Do not mark it download-verified or count it as an additional methylation array study.

The paper already tests histone–expression/enhancer relationships and differentiation effects. Its main ChIP comparison has one affected line and one control line in triplicate. A possible later use is testing frozen blood-derived modules against an independently qualified cell-model layer, with explicit donor, tissue and assay limitations. It is neither matched blood methylation–expression validation nor a perturbation-rescue dataset. No files were downloaded, and neither lead is a P1 prerequisite.

## Current data/ethics decision

Use the [source-access and ethics register](source-access-ethics.md) as the source of truth for public landing status, concrete archive types, original sizes, no-login rules, separate downstream rights, and institutional ethics/exemption decision gates. **No source has been promoted beyond public repository listing.** The ProteomeXchange record is released but legacy FTP retrieval remains untested. Avoid unqualified republication of rare-disease participant-level molecular data.

