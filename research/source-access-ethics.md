# Public-data accessibility, terms and ethics triage

Status: **22 November 2026 desktop verification of repository listing, not a file-transfer or sample-level audit**. Source pages listed below are public. No raw participant data were downloaded, no checksum has been computed, no participant-level consent reviewed, and no institutional ethics determination has been issued. The distinction is deliberate.

## Four separate questions

1. **Repository access:** Is the source publicly released and linked for download without an account, access committee or application?
2. **Download verification:** Has the proposed specific file actually been fetched and checksum/contents checked? **No**, for every row here.
3. **Lawful reuse:** Does the source study's applicable consent, data-use conditions, third-party rights, and any restrictions allow *this* secondary analysis? **Unresolved per study** until source methods/supplements and any study-specific notices are reconciled.
4. **Ethics/governance:** Has the responsible Australian institution decided whether the secondary analysis is eligible for exemption, another review pathway, or HREC approval? **Not yet**. Do not claim exemption on the basis of a public GEO page.

NCBI states that anybody can access public GEO without login and that files can be downloaded using its repository and FTP. NCBI generally imposes no restriction itself on GEO data use/distribution **but cannot waive source submitters' intellectual-property claims**. Sources: https://www.ncbi.nlm.nih.gov/geo/info/faq.html ; https://www.ncbi.nlm.nih.gov/geo/info/download.html ; https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html . These are repository-wide rules, not individual consent verification.

For Hugging Face hosting, source-specific ontology licences and existing account assets, use [resources, hosting and reuse](resources-hosting-reuse.md). The positive GEO distribution policy is evidence in favour of reuse; do not invent a universal submitter-permission requirement. Conversely, Silver transformation or Gold aggregation is not itself a new licence or a guarantee against disclosure. No dataset has been uploaded or mirrored by this planning review.

## Accession register: public source listings, **no application for GEO-listed files**

| Accession | Repository-listed public access | Concrete downloadable evidence | Limitation / qualified use |
|---|---|---|---|
| [GSE97362](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362) | **Yes** | 450K IDAT raw TAR 2.0 GB; series matrix | 235 assay records include CHARGE, Kabuki, and controls; KMT2D subset and sample overlap unverified |
| [GSE116300](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300) | **Yes** | IDAT raw TAR 539.1 MB; beta and M matrices | Kabuki *phenotype* cohort, not all KMT2D molecular diagnoses; original design describes synthetic controls and other relatives |
| [GSE218186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186) | **Yes** | EPIC IDAT raw TAR 1.0 GB; processed beta data | 62 records including seven affected individuals; assess overlap and molecular eligibility. The associated study also used an internal comparison cohort not publicly released for ethical reasons; it is not in this GEO series |
| [GSE74432](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE74432) | **Yes** | 450K IDAT raw TAR 1.1 GB | 122 records include controls, NSD1 variants and Weaver; not 122 independent patients |
| [GSE191276](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE191276) | **Yes** | EPIC IDAT raw TAR 99 MB; signal-intensity matrix | 3 Sotos, 3 individual controls, **one pooled parental DNA sample** (not an independent individual) |
| [GSE191274](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE191274) | **Yes** | RNA-seq raw-count matrix 4 MB; raw reads referenced in SRA | RNA and methylation share some labels; reconcile exact matched participants; SRA runs not independently fetched |
| [GSE167230](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE167230) | **Yes** | Mixed 450K/EPIC IDAT raw TAR 270.6 MB; beta matrix 13.7 MB | **Only seven deposited samples**: ICF1 (1), ICFX (2), SETD2 Sotos-like (2), TBRS (2). Earlier comparison study also reused other cohorts; no independent controls in this accession |
| [GSE66552](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE66552) | **Yes** | 450K IDAT raw TAR 548.8 MB | 45 samples: Williams deletion, reciprocal duplication and controls; dosage comparison is already published |
| [GSE125367](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE125367) | **Yes** | EPIC IDAT raw TAR 778.2 MB; signal-intensity matrix | SMARCA2 affected, controls and uncertain variant-test cases must be separated |
| [GSE152427](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE152427) | **Yes** | Public raw TAR 161.2 MB, signal intensities 232.9 MB | GEO lists raw TAR, but IDAT contents of archive not checked; 57 assay records and control/relative composition require review |
| [GSE152421](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE152421) | **Yes** | RNA-seq raw-count table 1.8 MB, processed table 3.5 MB; SRA raw reads referenced | 36 RNA assay records, not 36 affected persons; raw SRA run permissions / pairing not separately checked |
| [GSE221644](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE221644) | **Yes** | EPIC IDAT raw TAR 399.5 MB; processed matrix 116.3 MB | 17 PBMC samples; AGS RNASEH2B genotype-specific context; consent/reidentification risk requires review |
| [GSE269416](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE269416) | **Yes** | EPIC IDAT raw TAR 4.2 GB; normalised beta matrix 1.8 GB | **290 public records**, whereas the publication discusses a larger cohort (582). Includes replicates and a few saliva/fibroblast specimens; not a pure CHD2 cohort |
| [GSE261305](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE261305) | **Yes** | Open GEO xlsx/normalised text (~0.6 MB each) | **Targeted 770-gene NanoString kidney expression**, not a whole-transcriptome assay or confirmed inherited complement-genotype cohort |
| [PXD003403](https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD003403-1) | **Released public ProteomeXchange record** | PRIDE FTP dataset location explicitly listed; file transfer untested | King cobra **venom composition**, not human host-response proteomics; legacy FTP access requires further download check; dataset- and file-specific rights not cleared |

**Public access** here means the *repository landing page lists public downloadable material*. It does not mean successful local file transfer, rights clearance, cohort independence, participant-level phenotyping, or unrestricted redistribution. Source pages were checked 22 November 2026; GEO records may change.

## Human research ethics and reuse in Australia

The [NHMRC National Statement (2025)](https://www.nhmrc.gov.au/research-policy/ethics/national-statement-ethical-conduct-human-research) is effective from **23 June 2026**. Section 3.1 addresses secondary use of information, scope of consent, reasonable participant expectations, privacy and identifiability. Exemption is an **institutional or appropriate review-body determination**, not a declaration the dataset downloader can make. This is particularly important for small, rare-disease molecular cohorts with variant/phenotype metadata and reidentification risk. The NHMRC has an ongoing 2026 consultation proposing changes to definitions and exemption criteria; check the final operative guidance before the research protocol is lodged: https://consultations.nhmrc.gov.au/ethics-integrity/2025-national-statement-update-public-consultation/consult_view/ .

Queensland Health [research ethics and governance HSD QH-HSD-035](https://www.health.qld.gov.au/system-governance/policies-standards/health-service-directives/research%2C-ethics-and-governance) applies when an HHS collaborates or research is undertaken at an HHS. [Metro North's guidance](https://metronorth.health.qld.gov.au/research/ethics/exempt) includes public-domain data as an example potentially eligible for exemption and describes **submitting for formal exemption determination**. A CHHHS/HHS-affiliated project should document its institutional review pathway and governance even when source data are entirely public. Do **not** infer that reuse of existing GEO matrices requires a fresh HREC application in every circumstance either: request the appropriate exemption/low-risk/HREC determination based on the actual protocol and material.

If future work uses Queensland Health clinical records, consented local biospecimens, identifiable data, linked case information or controlled-access datasets, reassess research ethics and site authorisation separately. Existing public-data status does not carry over to new clinical source material. Avoid public Git commits of patient-level matrices, combinations of rare variant + age + phenotype, or participant-linked redistributable datasets until permission and privacy decisions are documented.

### Suggested institutional determination packet (not a submitted application)

A protocol limited to public open-access, previously deposited data; source accession and sponsor/publication; anticipated reuse purpose; exactly which files and metadata are needed; whether personal information is present or reasonably re-identifiable; consent/use-notice audit; download/storage/retention plan; public output disclosure limits; source terms; intended collaborator institutions; and a request for **written determination** of ethics review requirements and any relevant HHS governance pathway.

## Ontology and software licensing are separate

- **MONDO:** open CC BY 4.0; cite and pin release: https://mondo.monarchinitiative.org/pages/download/ .
- **HPO:** freely usable, subject to the HPO project's actual licence requirements for acknowledgement, version and integrity of source ontology files: https://human-phenotype-ontology.github.io/license.html . Do not assume HPO itself is CC0 or that modifications may be redistributed as an official HPO release.
- **OMIM:** research usage is encouraged; identifiers and certain tables are accessible openly, but bulk gene–phenotype downloads may require registration and public redistribution/integration may require licensing. Avoid copying OMIM proprietary prose into the repository: https://pmc.ncbi.nlm.nih.gov/articles/PMC6323937/ .
- **GEO** and **ProteomeXchange:** public file availability is not a blanket copyright, consent, privacy or commercial use determination; record conditions at each accession.

## Admission rule for T01

A dataset can be **discovered_public** on source evidence above. Promote to **download_verified** only after successful retrieval, checksum and file-content inspection. Promote to **research_reuse_eligible** only after source-specific rights/consent and institutional ethics/governance pathway are documented, with any qualifications. Promote to **model_eligible** only after diagnosis, controls, sample independence and relevant QC are established. A missing datum means *unknown*, not approved.

