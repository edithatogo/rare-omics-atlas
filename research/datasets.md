# Candidate datasets (NOT yet qualified)

Repository-level public status and raw/processed download listings were checked in the [source-access and ethics audit](source-access-ethics.md) on 22 November 2026. Every accession listed in the register is public, but actual file transfer and data-specific permission remain **unverified**. Sample-level evidence and rights review are still required in T01. GEO series counts contain controls, other diagnoses and multiple assays; they are **not** automatically number of affected individuals.

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

Data register must later include `open_raw`, `open_processed`, `controlled`, `request_only`, `unknown` access classes; third-party reuse permissions; each sample's `role` and provenance; exact archive checksums; and flags for train/test contamination.

## Current data/ethics decision

Use the [source-access and ethics register](source-access-ethics.md) as the source of truth for public landing status, concrete archive types, original sizes, no-login rules, separate downstream rights, and institutional ethics/exemption decision gates. **No source has been promoted beyond public repository listing.** The ProteomeXchange record is released but legacy FTP retrieval remains untested. Avoid unqualified republication of rare-disease participant-level molecular data.
