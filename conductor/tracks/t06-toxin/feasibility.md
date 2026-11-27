# T06 — source and model feasibility

Assessed **28 November 2026 (Australia/Brisbane)** against repository main
`e3e83d95e46dec61dfae4f5057c1dd65eb33409f`. This is the public-source assessment
specified in [plan Batch A](plan.md#feasibility-first-batches), an N0/dependency
input. It is not a completed scientific N0/N1 review, model run or admission.

## Decision

**Retain a descriptive complement-pathway consumer; hold quantitative
genotype-by-venom prediction.** The named human and venom sources establish
disease context and component evidence, but no qualified joint genotype,
exposure and response reference. Their combination does not supply an
identifiable model. Missing measurements remain unknown, not zero.

The [source receipt](../../../research/qualification/model-input-readiness-2026-11-28.json)
records metadata response hashes, actual inventories, retrieval limits and the
separate CpGPT checkpoint-membership assessment. No patient-level table,
molecular payload, model weight or inference output was acquired for this work.
Source-linked Bronze is sufficient; no new runtime, solver, adapter or schema
package is needed. The existing [model assessment](../../../research/model-selection-2026-11-28.md)
continues to govern conditional AG2 and consequence-specific annotations.

## Human source: distinguish clinical people from expression assays

The [GEO record for GSE261305](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE261305)
lists **108 biopsy assays** on GPL25507. It describes bulk FFPE kidney RNA using
the 770-gene NanoString PanCancer Immune Profiling Panel, not single-cell UMI
sequencing. Its two expression cohorts are:

| Expression cohort | C3 glomerulopathy biopsies | Other glomerular-disease controls | Assays |
|---|---:|---:|---:|
| Native-biopsy discovery | 18: 11 C3GN, 7 DDD | 36 | 54 |
| Allograft-biopsy testing | 13 recurrent C3G | 41 | 54 |

The [original clinical study](https://doi.org/10.2215/CJN.0000000000000474)
has a separate **18-person transplant cohort**. Ten of the 13 recurrent-C3G
expression biopsies came from that cohort, with three additional cases. Genetic
testing was available for 12 clinical participants; six had reported variants,
only one interpreted as potentially disease-causing, without an available ACMG
classification. These aggregate counts do not qualify an assay–person–genotype
crosswalk or establish 108 independent, genetically confirmed people.

The actual supplementary listing contains `GSE261305_RCC_files_Final.xlsx`
(576,086 bytes) and `GSE261305_normalized.xls.gz` (650,942 bytes). HEAD requests
confirmed availability and length; neither body was read. The workbook name
does not establish validated raw-count semantics. Matrix, MINiML and SOFT
payloads were listed but not fetched. Source hashes cover the metadata responses,
not these molecular objects.

The paper conditions clinical-data sharing on appropriate IRB approvals and
separately points to GEO for transcriptomics. Public listing, research-use
permission, redistribution and institutional classification remain separate.
No clinical-data request or institutional determination was made here.

## Venom source: related deposits are not accession aliases

[PRIDE PXD003403](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD003403)
describes pooled venom from two reported *Ophiophagus hannah* individuals
(taxon 8665), originating from Malaysia and obtained from Kentucky Reptile Zoo.
Brazil is submitter-country metadata. Exact locality, individual contributions
and a modern taxonomic reassignment were not established.

The [original paper](https://doi.org/10.1074/mcp.M115.056523) assigns PXD003403
to **bottom-up** data. Its related [MassIVE deposit MSV000079351](https://massive.ucsd.edu/ProteoSAFe/dataset.jsp?accession=MSV000079351)
identifies **PXD004160**. Preserve that relationship instead of merging the
accessions. Three raw filenames and declared sizes overlap; payload identity
has not been checked.

| Deposit | Inspected file metadata | Declared bytes | Payloads read |
|---|---|---:|---:|
| PXD003403 | 3 RAW, 3 SEARCH, 1 OTHER | 2,988,039,396 | 0 |
| MSV000079351 / PXD004160 | 129 raw, 106 peak, 1 result | 39,011,223,423 | 0 |

The paper identifies CVF accession **I2C090 in native analysis of this pooled
material**. This is paper-level evidence, not a claim that the seven PXD003403
objects reproduce the native result. The paper describes relative ion-abundance
and NSAF methods; bulk BCA protein concentration and intact molecular mass do
not supply CVF-specific absolute concentration. A CVF-specific relative fraction
was not verified because molecular supplements were not inspected. Its bottom-up
triplicates are technical measurements of one digestion, not biological replicates.
No study-specific CVF kinetics or host exposure/response time course was found
in the inspected paper. A cited functional study is not a measurement of this pool.

## Source-to-parameter map

This is an input-compatibility map, not a fitted parameter table. No numerical
value is imported into a biological model.

| Needed quantity | Species / compartment / unit | Evidence inspected | Disposition |
|---|---|---|---|
| Targeted expression | Human, bulk kidney biopsy; assay counts or normalized expression | GSE261305 design and file metadata | Descriptive pathway context; numeric matrix and participant independence unqualified. Not plasma protein concentration. |
| Exact genotype and functional consequence | Human allele/transcript and linked person; activity change with defined units | Aggregate clinical genetics only | No eligible allele–assay linkage or quantified functional effect established. An AG2/AlphaMissense score cannot supply it. |
| CVF identity | Reported *O. hannah*, pooled venom; protein accession | Native result in the original paper | Presence supported at paper level; exact sequence/proteoform and activity not qualified as executable inputs. |
| Active CVF exposure | Relevant host compartment; concentration over time | Relative proteomic methods and bulk protein measurement | CVF-specific magnitude unverified; absolute concentration, exposure and bioavailability not established. |
| Complement state / response | Human plasma or relevant tissue; concentrations and time courses, defined terminal endpoint | Published models and external experiments | Source pair contains no matched genotype-by-exposure response. Kidney RNA is not C3a/C5a, MAC or haemolysis measurement. |
| Reaction and regulatory parameters | Defined species/compartment; rate/activity units | Existing model assumptions and published parameters | No measured transfer from these deposits. Identifiability and species/context validity unresolved. |
| Independent functional validation | Separate biological units and study; frozen endpoint | No qualified paired reference | Hold N1/model execution; correlated prediction scores are not replication. |

## Existing models before choosing a solver

| Reference | Useful scope | Validation and implementation limits | Decision |
|---|---|---|---|
| [Sagar et al., 2017](https://doi.org/10.1371/journal.pone.0187373) | Reduced lectin/alternative complement model; 18 ODEs, 28 parameters; C3a/C5a | Fits and held-out conditions come from the same experimental study. Authors explicitly report underdetermined parameter estimation and imperfect kinetics. Factor B/D assumed non-limiting; no MAC. [Original Julia repository](https://github.com/varnerlab/Complement_model_repository/tree/0b05998085bb19b3cf5633b5cb169b2e4be4c622) is MIT licensed; runtime/reproduction not tested here. | Smallest inspectable reference for a later justified reproducibility task; no parameter transfer from the candidate sources. |
| [Bansal et al., 2022](https://doi.org/10.3389/fphar.2022.855743) | Alternative/terminal pathways in plasma and erythrocyte surface; 311 states, 139 kinetic parameters | MATLAB/SimBiology. Comparisons include human complement and guinea-pig erythrocyte lysis; some rates were adjusted to comparison data. Patient variability deferred. Article is CC BY; downloadable executable contents/licence not verified. | Observable/compartment reference, not a justified present runtime or CVF/kidney model. |
| [Caruso et al., 2020](https://doi.org/10.1371/journal.pcbi.1008139) | Fluid/surface complement, haemolysis and PNH; 226 reactions, 121 parameters | MATLAB/SimBiology, distinct estimation/verification evidence with remaining mismatches. Local sensitivity is not proof of identifiability. Article CC BY; indexed [BioModels record](https://www.ebi.ac.uk/biomodels/MODEL2206230002) and executable licence/content were not successfully retrieved. | Revisit only for an actual haemolysis consumer. Do not mislabel reaction count as ODE count. |

[Hew et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32526239/) describe CVF's
distinct convertase behaviour; normal-complement parameters cannot simply be
relabeled as CVF parameters. [Morser et al., 2018](https://doi.org/10.1111/jth.13964)
report context-dependent effects of CPN/CPB2 deficiency in mice across CVF and
HUS models. That is independent mechanistic evidence, not validation of human
rare alleles, this venom pool or envenomation severity. No experimental protocol
or toxin-response optimisation is introduced here.

## Receiving scope and next decision

The source/metadata assessment is [received and archived](../../archive/model_input_readiness_20261128/index.md)
after independent content/artifact review, exact-current-base native-hook/strict,
privacy, dependency/provider checks and passing receiving-main verification.
The original scientific tasks and parent T06 remain open.

Proceed with an annotated evidence map only if it serves a named question.
Quantitative work needs a linked eligible genotype and measured functional
change, defined exposure, relevant response measurements, an independent
validation reference and source-specific rights. Freeze the actual estimand,
units, conventional comparator, uncertainty and rejection rules at N1 before
execution. A source search is not evidence that no suitable dataset exists
elsewhere; this hold applies to the inspected pair and proposed consumer.

This is research planning, with no clinical susceptibility or treatment claim,
new wet-lab work or journal submission. It does not complete the institutional
or official-device requirements, delay T02/V01, or take ownership of T01/T07's
active source and backend branches. Source verification and suitable existing
methods are reused; a solver, port or model API is deferred until a real
quantitative consumer warrants it.
