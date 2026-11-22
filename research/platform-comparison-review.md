# Paired-array evidence and implications for the first study

**Source review: 22 November 2026.** The completed search receipts and verified study–dataset relationships are in [literature/](literature/README.md). This was targeted literature and source inspection: no statistical disease analysis, numerical software validation or patient-array download was performed by this review. It does not establish a complete census of all paired datasets.

## Decision

Keep **E1 as optional qualification supporting the E0/E2/E3 clinical paper**. Ordinary 450K–EPIC concordance and integration are established, and the exact candidate references **GSE86833 and GSE92580 have already been reanalysed together**. The first paper needs a clinically useful transfer result or a carefully established limit of interpretation. A generic pooled Kabuki network also overlaps published work.

The more promising later contribution is a prespecified test of whether sharing information improves masked study/disease effects, with calibrated uncertainty and negative-transfer checks against simple baselines. This remains a provisional opportunity, dependent on qualified cohorts and a question-specific novelty review.

## 1. Paired cohorts and their access status

| Study | Pairing established by the primary source | Access evidence as checked | Appropriate role |
|---|---|---|---|
| [Pidsley et al. 2016, PMID 27717381](https://doi.org/10.1186/s13059-016-1066-1) | Matched 450K/EPIC material includes cell models, fibroblasts and five infant Guthrie blood specimens; GSE86829 is 450K and GSE86831 is EPIC | Article data availability explicitly names public SuperSeries [GSE86833](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE86833). Indexed official listing reports a 677.4 MB IDAT archive | Small same-specimen reference, with limited precision for population reliability |
| [Kling et al. 2017, PMID 28392843](https://doi.org/10.1186/s13148-017-0333-7) | Nine fresh-frozen paediatric brain tumour specimens T01–T09 and three FFPE specimens T10–T12 profiled on both platforms: 12 cross-platform specimen pairs. A further nine FFPE records paired to the fresh-frozen specimens supply a separate preservation comparison | Article explicitly deposits study data to public [GSE92580](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92580). Indexed official GEO lists GSE92577 450K raw 279.9 MB and GSE92579 EPIC raw 509.6 MB; SuperSeries 789.5 MB | Optional tumour/low-quality-DNA stress test; preserve person/specimen dependence |
| [Logue et al. 2017, PMID 28809127](https://doi.org/10.2217/epi-2017-0078) | 145 adult TRACTS blood DNA specimens on both platforms; 11 samples with additional EPIC technical repeats | Pairing confirmed in full text. An openly downloadable raw accession was not verified | Prior art; raw-data intake held pending source verification |
| [Solomon et al. 2018, PMID 30044683](https://doi.org/10.1080/15592294.2018.1497386) | CHAMACOS: 109 newborn cord specimens and 86 age-14 blood specimens each profiled on both platforms | Pairing confirmed in full text; public raw accession not verified. The 195 age-specific specimens must not be counted as 195 unique people without a donor table | Direct paediatric prior art; raw intake not admitted |
| [Fernandez-Jimenez et al. 2019, PMID 31250700](https://doi.org/10.1080/15592294.2019.1634975) | 108 paired placental specimens across the platforms | Primary publication establishes pairing; raw-access status not verified. Connector full-text retrieval failed | Tissue-specific prior art |
| [Cheung et al., online 2019/issue 2020, PMID 31833794](https://doi.org/10.1080/15592294.2019.1700003) | 21 new cartilage pairs plus reused GSE86833 blood and GSE92580 tumour pairs | Explicit reuse of both public references verified. Own cartilage raw accession not established in this bounded review | Direct prior overlap with a generic reanalysis of the proposed references |
| [Lussier et al. 2024, PMID 39578866](https://doi.org/10.1186/s13148-024-01761-4) | 30 children, 15 female and 15 male, around age five; same blood profiled on 450K, EPICv1 and EPICv2, with additional technical repeats | Publisher data availability requires appropriate Drakenstein Child Health Study approval. Code and [CACTI](https://cacti.geddes.rcac.purdue.edu/) annotations are separately available | Prior art and annotation lead; excluded from the no-application raw intake path |

The listed raw sizes describe repository archives, not measured memory requirements or successful transfers. Direct GEO page opens encountered a recaptcha in this review; article availability statements and indexed official listings support the limited access conclusions above. Source-specific [reuse/ethics](source-access-ethics.md) and [hosting](resources-hosting-reuse.md) decisions still apply.

### Three distinct kinds of comparison

- **Same DNA/specimen, different arrays:** estimates technical platform/processing disagreement. Repeated arrays do not add independent people.
- **Same person, different collection/tissue/preservation:** mixes technical and biological or storage effects. Participant grouping must be retained.
- **Different people, same disease:** tests biological replication when cohorts contain informative native controls. It does not isolate platform effects from recruitment, laboratory and other study differences.

For GSE92580 there are 12 cross-platform specimen pairs; the independent participant count remains to be established. The three paired-platform FFPE specimens T10–T12 are distinct from the additional FFPE records matched to the nine fresh-frozen specimens. Its methylation variance, tissue and DNA quality also differ from blood. Use it only if a specific remaining qualification question warrants that additional matrix.

The five candidate GSE86833 blood pairs are listed in the [experiment plan](experiment-publication-plan.md#concrete-optional-technical-subset). The [official RnBeads cross-platform tutorial](https://www.rnbeads.org/materials/data/tutorial/cross_platform/tutorial.html) supports the same-sample relationship; the final admission record must still reconcile GSM, donor, specimen and array identities.

## 2. Prior work that narrows novelty

### Platform agreement and integration

[Fortin et al., minfi, PMID 28035024](https://doi.org/10.1093/bioinformatics/btw691) already describes EPIC preprocessing/integration, common-probe representations and single-sample noob. Subsequent studies above examine locus reliability, differential methylation agreement, tissue differences and epigenetic-clock consistency.

Most directly, [Cheung et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC7574380/) explicitly retrieved **GSE92580 and GSE86833**. Reusing these series can qualify a current implementation, matched annotation/mask release or exact production export, but does not create a newly assembled platform-comparison cohort.

Possible incremental questions include whether a qualified backend substitution preserves **prespecified rare-disease effects and uncertainty**, whether reliability-aware filtering improves held-out disease-effect accuracy, or where array coverage changes clinically relevant interpretation. These are candidates for an N0 review, not established gaps. Include E1 in the clinical bundle only when it resolves an actual uncertainty.

### Kabuki networks and expression overlays

[Cuvertino et al., PMID 39701600, DOI 10.1093/bib/bbae667](https://pmc.ncbi.nlm.nih.gov/articles/PMC11658816/) explicitly reuses **GSE97362 and GSE116300**, combines those 450K data with a Cuvertino EPIC cohort and studies higher-order epigenomic coordination. It also examines **GSE126167/GSE126166** expression data from human/mouse Kabuki cell models. Generic pooled methylation-network construction or a cell-model RNA overlay therefore overlaps existing work.

The retrieved main-body text identifies the EPIC study by reference 34 rather than an explicit GSE218186 string. The [edge register](literature/2026-11-22-study-dataset-edges.json) leaves that linkage unresolved pending confirmation against the original study/series metadata. Article citation, dataset reuse and participant overlap are separate facts.

Preserve the date discrepancy: PubMed/OpenAlex return 22 November 2024, while the publisher electronic publication date is 19 December 2024 and the issue is 2025. The evidence record keeps source-specific values rather than silently replacing the publisher date.

### An additional modelling use of GSE97362

[The Multi-State Epigenetic Pacemaker, PMID 39549198, DOI 10.1007/s11357-024-01414-7](https://pmc.ncbi.nlm.nih.gov/articles/PMC11979089/) explicitly lists **GSE97362** among supporting GEO series. It models several contributors to methylation in pooled blood data, including age and cell composition.

This is verified accession-level reuse. It does **not** show which Kabuki cases or controls were retained, or that the disease effect itself was modelled. Check the authors' sample manifest before making those claims. Methods describes 17 datasets while availability lists 18 accessions; reconcile study/series units before interpreting that difference.

### Implication for the bundled paper

E2/E3 should test a **precise transfer/replication question**, with clinically useful limits and uncertainty, using each test cohort's own controls. Public cohorts may have appeared in previous analyses; a holdout within this study is not evidence that the data have never been analysed before.

E5 should compare independent models, full pooling and simple partial pooling before adding a network prior. Entire study/disease holdouts, training-only selection, uncertainty coverage, negative transfer and abstention are more informative than another descriptive graph. If performance matches simpler models, retain the simpler model and report the boundary honestly.

A useful reproducibility limitation may contribute to P1. Routine software parity belongs in supporting material unless a separate generalisable software contribution emerges. None of these judgments establishes acceptance odds or guarantees a manuscript.

## 3. Literature evidence and ongoing monitoring

The [dated literature baseline](literature/README.md) retains exact PubMed queries, translations/warnings and pagination; ten OpenAlex DOI resolutions; compact Europe PMC statuses; and explicit study–dataset edges. All citation pages were retrieved for the three particular PubMed queries. Selected relevant full texts were inspected; this was a targeted review with known false positives and omissions.

The exact-accession PubMed query dropped GSE86829, GSE86831 and GSE116300 from its translated query and warned about them. **No accession hit is not proof of no prior use.** Combine accession/parent-series searches, study title/DOI and disease/method synonyms with full-text/supplement inspection and citation tracing. A citation alone is not a verified reuse edge.

An enabled weekly literature watch has been created for approximately **Monday 08:00 Australia/Brisbane**, with the first scheduled run on **23 November 2026**. This supplements the mandatory **N0/N1 before each analysis, N2 after results, and N3 before submission/transfer** checks. Scheduling is completed; future searches and conclusions are not claimed to have occurred. See the [novelty protocol](novelty-priority-protocol.md).

Keep provider-specific publication dates and exact retrieval dates. New evidence can change priorities, journal fit or whether to combine/reframe/stop, but must not silently change frozen N1 outcomes.

## 4. Implementation boundary

The [backend audit](methylation-backend-audit.md) and [Rust candidate audit](rust-candidate-audit.md) own preprocessing and dependency qualification. Existing C SeSAMe2 already has R comparison machinery; reuse it before considering a new preprocessing ecosystem. A source-level Rust IDAT candidate and a complete SeSAMe-compatible pipeline have very different scopes.

Clinical E0→E2→E3 should retain a qualified existing reference route while a Rust candidate is assessed separately. Hardware, compiler choice and language migration do not supply biological novelty. A backend comparison should preserve exact inputs, annotations, masks, scientific methods and exported precision so that any difference has an interpretable cause.
