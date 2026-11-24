# Paired-array calibration and local decision analysis — bounded update

Reviewed 22 November 2026. Read-only lane: no repository mutations, statistical disease analysis, complete array download, software numerical qualification, or new approvals/contact. Source/query receipts are in the companion JSON; raw downloaded manifests remain outside Git. Ponytail recommendation: reuse existing methods and the owner's suitable numerical library; keep calibration optional and answer a defined downstream uncertainty before building another framework.

## Decisions

1. **Yes, a local decision model is useful for choosing research and pipeline work.** Start with a transparent eligibility/priority table and sensitivity analysis. Reserve formal value-of-information for a clearly specified decision, uncertainty model and prospective observation process.
2. **Pooling additional paired cohorts has conditional value, but ordinary 450K–EPIC concordance is mature.** One substantial additional genuinely downloadable cohort was found: **GSE154566**, with a verifiable **233-pair blood subset**. This makes a useful technical resource, not an inherently new scientific study.
3. First qualify the actual analysis pipeline; then test whether a simple calibration/filtering policy improves a prespecified held-out rare-disease result. Bundle that evidence into the clinical paper when it materially changes interpretation. Do not require all technical cohorts or a new Rust preprocessing library before progressing the disease study.

## Newly verified public pairing

**GSE154566 — Kandaswamy et al., DNA methylation signatures of adolescent victimization.** PMID33371772; DOI [10.1080/15592294.2020.1853317](https://doi.org/10.1080/15592294.2020.1853317). The official [GEO series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154566) and API-style quick-SOFT describe 233 age-18 blood specimens assayed using both arrays.

Checks actually performed:

- Downloaded quick-SOFT and the official FTP file listing, with HTTP200.
- Downloaded all three small paired phenotype files and the pre-QC manifest, with HTTP200 and SHA256 records.
- The combined paired manifest contains **466 rows, 233 unique TwinIDs, exactly one 450K and one EPIC record per TwinID**, 466 distinct array basenames.
- Those paired specimens belong to **117 families: 116 pairs of twins plus one singleton**. The wider study recruited118 twin pairs; that is not the paired subset's denominator.
- All466 paired array basenames map to exactly two red/green IDAT members in the official raw manifest: **932 files**, with a combined listed member size of **5,454,457,454 bytes**.
- The full series has1177 assays/2354 IDAT files. Its raw TAR is **16,026,480,640 bytes**. A public unauthenticated range GET returned **HTTP206, bytes0–1023/16026480640**. Only1024 bytes were transferred; the raw archive was **not** downloaded or quality-controlled.
- The separate processed450K andEPIC matrices are listed at roughly572MiB and574MiB compressed; the jointly normalised matrix is about1.5GiB. Use raw files for pipeline qualification; use processed matrices only with their original processing provenance.
- Join on explicit specimen/person/array keys, not row order: the separate files have different ordering and different column spellings.

Official source URLs:

- [Quick SOFT](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154566&targ=self&form=text&view=full)
- [FTP files](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE154nnn/GSE154566/suppl/)
- [File manifest](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE154nnn/GSE154566/suppl/filelist.txt)

**Access is verified; secondary redistribution permission is not established by these technical checks.** Keep source access, analysis admission, local institutional classification and Hugging Face hosting rights as distinct fields. Do not upload the phenotype files or raw DNA data merely because the FTP server is open. A catalogue can expose the accession, technical counts and source links without copying individual phenotypes.

## Important prior art and independence

| Evidence | Implication |
|---|---|
| Cheung2019/2020, [PMID31833794](https://pubmed.ncbi.nlm.nih.gov/31833794/), DOI10.1080/15592294.2019.1700003 | Already combined GSE86833 infant blood andGSE92580 paediatric brain tumours with21 paired cartilage specimens; explored variance, cross-tissue reliability, absolute platform bias and six-CpG pyrosequencing. No public raw accession for the21 cartilage pairs was located in the inspected main text. |
| Sugden2020, [PMID32885222](https://pubmed.ncbi.nlm.nih.gov/32885222/), [PMC7467214](https://pmc.ncbi.nlm.nih.gov/articles/PMC7467214/), DOI10.1016/j.patter.2020.100014 | Studied350 E-Risk age18 blood pairs; quantified reliability and consequences for heritability, expression, cross-tissue concordance, smoking associations and clocks. It names public450K GSE105018 and provides reliability summaries. **Potential participant overlap with GSE154566 must be resolved; these are not automatically two independent cohorts.** |
| Lussier2024, [PMID39578866](https://pubmed.ncbi.nlm.nih.gov/39578866/), DOI10.1186/s13148-024-01761-4 | CACTI already provides ICC, IQR, correlation and array-bias annotations across450K/EPICv1/v2 in30children. Participant data require Drakenstein approval. Do not classify them as no-application open. |
| Zhang2024, [PMID38564759](https://pubmed.ncbi.nlm.nih.gov/38564759/), DOI10.1080/15592294.2024.2333660 | EPIC replicate reliability has already been linked to consistency of EWAS effects, DMRs, mQTLs, expression and blood-brain concordance. Generic “reliability improves downstream interpretation” is not a new claim. |
| Nazarenko2024, [PMID39289706](https://pubmed.ncbi.nlm.nih.gov/39289706/), DOI10.1186/s13148-024-01739-2 | Existing probe-intensity/background-noise modelling and dynamic thresholds are a relevant comparator before designing custom measurement-error scores. |
| Olstad2022, [PMID35765087](https://pubmed.ncbi.nlm.nih.gov/35765087/), DOI10.1186/s13148-022-01299-3 |17paired cord-blood specimens show how platform effects can impair exposure replication. Treat as prior art; no no-application raw admission established here. |
| Netherlands Twin Register2023 study, [PMID37834090](https://pubmed.ncbi.nlm.nih.gov/37834090/), DOI10.3390/ijms241914640 |83paired blood specimens from the Netherlands Twin Register; explicit data statement says participant consent prevents public data release. BIOS450K data are EGA EGAD00010000887 and NTR data require request. Not public intake. |

The public shortlist for a bounded implementation is consequently **GSE154566** as the larger blood calibration set, **GSE86833**'s five paired infant blood specimens as a small age/material sensitivity set, and **GSE92580**'s12cross-platform specimen pairs as an optional tumour/preservation stress set. The latter are12specimen pairs, not a verified12independent people. Never sum publications, series, tissues, repeated assays and donors into a single independent sample count.

This is targeted discovery, not a complete inventory. PubMed queries missed some known relevant papers; full-text accession checks and citation tracing remain necessary.

## A sharper experiment with potential value

**Question:** Does a frozen, tissue-aware technical qualification policy preserve clinically meaningful rare-disease methylation effects better than the ordinary common-probe baseline, when applied to an entirely held-out study?

Compare only a few defensible policies: (A) common probes plus the selected reference QC; (B) published reliability/noise annotations compatible with the exact platform/tissue; (C) a simple calibration or reliability weighting trained solely on eligible paired reference data. A new hierarchical method is contingent on a demonstrated limitation ofB.

1. Reconcile specimen/family IDs and array versions; reserve calibration/test cohorts before seeing outcomes. Hold all twins/repeated materials together.
2. Estimate **paired absolute differences, platform bias and uncertainty**, alongside correlation and an explicitly defined single-measure agreement ICC. Use bootstrap clusters at the person/family level. The relevant reliability unit is generally one future array, not the average of two arrays.
3. Report within-cohort variability separately from measurement disagreement. Low Pearson correlation/ICC at a biologically invariant CpG can coexist with small absolute error. Pooling tissues raises between-person variance and can inflate correlations without improving measurements.
4. With one measurement on each platform per specimen, observed disagreement conflates both arrays' errors, batch and processing. It does not identify each platform's independent error variance without extra replication or explicit assumptions; neither platform is automatic ground truth.
5. Test held-out platform residuals first; then test the **prespecified disease-effect estimand**, region stability or module-score transfer using each disease study's own controls. Do not claim that better CpG correlation proves better disease prediction. Use region/pathway aggregation only with a fixed probe universe, a prespecified mapping and appropriate coverage/probe-density handling.
6. Split calibration by families and studies; perform any selection only on training data. GSE154566 versusGSE86833 supplies only two very different blood cohorts, one with n=5. General blood-age heterogeneity and age-specific calibration are not well identified; tumour data cannot fix that. Leave-tissue-out work is a stress test, not evidence that tumour-derived weights are valid for children with rare disorders.
7. Stop expanding if calibration does not materially improve the frozen downstream outcome or uncertainty. Report the limit and retain the simpler pipeline.

**Provisional scientific ranking:** ordinary pooled correlation has low incremental novelty; reproducible execution qualification has high operational value but usually belongs in methods/supplements; a carefully controlled, genuinely held-out rare-disease transfer result has the stronger clinical contribution. This is a reasoned priority judgment, not a quantified acceptance probability. Prefer one bundled clinical study over a standalone “we combined public paired arrays” paper.

## Minimal reproducible local decision method

Maintain a small versioned table of candidate analyses or pipeline alternatives, not a patient treatment decision engine:

- **Non-compensatory eligibility:** source access/reuse, adequate specimen identity, required contrast/covariates, independent holdout, qualified method, actual resources. A high novelty score cannot compensate for a failed scientific requirement.
- **Outcomes:** expected clinical usefulness, exact novelty relative to dated literature, additional inferential precision, reproducibility/reuse, and measured resource cost. Identify subjective ordinal judgments and unknowns explicitly; missing cost is not zero.
- **Decision:** report Pareto-dominated alternatives, then a transparent weighted utility over admissible alternatives. Use fixed published weights plus a small sensitivity grid. Report where the recommendation changes and its reasons.
- **Replay:** fixed inputs, source hashes, equation/units, weight-grid file, seed only if sampling, output table and timestamp. A built-in table expression or small standard-library calculation is sufficient. Avoid adding a decision platform for five alternatives.
- Grid “fraction of weights where optionA wins” is a robustness description, **not** a calibrated probability thatA is optimal. Novelty/impact scores are not money or health utility unless a defensible conversion is specified.

Later, genuine VOI can ask “is another paired calibration cohort, targeted bisulphite validation, or a held-out expression assay worth obtaining?” EVPI is the difference between expected utility under perfect information and the best current expected utility. EVSI additionally requires a sampling/observation model and updating rule; a larger sample count or a weighted score alone cannot supply it. Report the unit as explicit research utility if that is what was elicited, rather than implying monetary or QALY benefits.

### Existing owner libraries

| Candidate, exact inspected main commit | Verified current source scope | Recommendation |
|---|---|---|
| [voiage](https://github.com/edithatogo/voiage/tree/1ac249333d4fb4817f487189dd41b5c86ebc2cc8), `1ac249333d4fb4817f487189dd41b5c86ebc2cc8` | README documents Rust domain/numerical/serialization crates, Python orchestration and a Julia EVPI C-ABI route. Pinned source exports `voiage_numerics::evpi` using validated `SampleMatrix`; broader EVSI kernels exist, but README distinguishes method-specific stable/experimental contracts. | Appropriate existing numerical dependency once genuine VOI inputs exist. Rust core satisfies preferred language; JuliaEVPI is a possible existing interface. Do not infer full Julia/Python parity, or install every optional backend. No numerical test run was performed in this lane. |
| [kairos](https://github.com/edithatogo/kairos/tree/5e5e507616f63aa709ae5fc0684413b3fd7ba4c6), `5e5e507616f63aa709ae5fc0684413b3fd7ba4c6` | Rust DES/ABM scheduler, queues, state and deterministic random streams; alpha scope explicitly limits qualification. | Useful only for a later specified laboratory/workflow/resource simulation; unnecessary for present table ranking or methylation inference. |
| [innovate](https://github.com/edithatogo/innovate/tree/a9360c1ea3414eaf0e712dbb131d3e923e958571), `a9360c1ea3414eaf0e712dbb131d3e923e958571` | Rust innovation/technology diffusion models; README describes migration and incomplete qualification. | Consider only for a later uptake/implementation question with adoption data; not a generic research prioritisation engine or biological disease model. |

**Execution sequencing:** one agent batch for catalogue/pair-map and N0 freeze; a next batch for bounded pipeline replay and observed runtime/memory receipts; only then a conditional larger calibration batch. Archive each batch's defined completed scope. Do not label full scientific calibration completed from the manifest/range checks above. No agent-duration forecast or human-person-time estimate is inferred from these read-only checks.

