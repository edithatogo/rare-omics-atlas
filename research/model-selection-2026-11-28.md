# Genomic and cell-response model selection

Review date: **28 November 2026 (Australia/Brisbane)**. Protocol revision 1 is
versioned by Git. This is an implemented provider assessment and conditional
evaluation specification: **N0/dependency input, not an N1 freeze, an executed
model benchmark, scientific admission or clinical validation**.

The owner requested incorporation of the AlphaGenome 2 assessment and comparison
with potentially more useful models. Repository context inspected at
`098a330517210d90a88512de12490a9f193764d4`; central standards inspected at
`8f17a91d8aa66a600ed93a605f341f3d310da66d`. Existing T01/T07 owners retain their
source and numerical work. This assessment belongs to the optional interpretation
consumer in [T05](../conductor/tracks/t05-multiomics/plan.md) and conditional human
host-variation consumer in [T06](../conductor/tracks/t06-toxin/plan.md).

## Decision and first consumer

Retain **AlphaGenome 2 (AG2) for controlled evaluation of human regulatory
predictions**. Choose alternatives by the scientific question; a newer or larger
model is not a universal improvement. Preserve measured methylation replication
in T02 and V01's independently scheduled clinical-source work. No model below is
a new universal dependency, a replacement for source admission, or a reason to
delay either stream. Reuse the [capability crosswalk](../conductor/capability-crosswalk.md).

For the arrays already catalogued, a methylation-profile model is more directly
input-compatible than AG2, but compatibility does not prove incremental benefit
or external independence. For a future admissible human missense or splice
variant, a narrow predictor can be cheaper and more relevant than a regulatory
foundation model. For future measured single-cell perturbation data, a response
model answers a different question from sequence-to-regulation prediction.

The first model-specific adapter is deferred until a named consumer, eligible
inputs, exact model artifact/terms and an independent evaluation reference are
qualified. The present increment adds no model package, model download, model API call,
patient upload, live inference or workflow. It does not change clinical
eligibility based on a predicted score.

## Alternatives and relative priority

These are conditional choices by task, not a ranking from a common benchmark.
No head-to-head performance or device claim has been established here. Terms are
a dated source assessment; pin and qualify the selected code, checkpoint, data
and output rights separately before execution or distribution.

| Actual question | Most useful candidate to assess | Decision for this repository |
|---|---|---|
| Missing probes or a fixed representation of measured Illumina methylation profiles | [MethylGPT v1.1.2](https://github.com/albert-ying/MethylGPT/releases/tag/v1.1.2); [CpGPT](https://github.com/lucascamillomd/CpGPT) as a possible second comparator | Closer input fit to T02/T05 arrays than AG2. Start with observed-probe and simple reconstruction baselines. MethylGPT's target-cohort overlap below prevents calling those cohorts fresh external validation. Neither model replaces measured episignatures. |
| Functional interpretation of an admissible human missense allele | [AlphaMissense](https://github.com/google-deepmind/alphamissense) precomputed lookup | A small optional annotation is more directly relevant than AG2 for this consequence class. Predictions are CC BY 4.0, code Apache-2.0 and trained weights are not released. The current reference repository is archived. Unsupported alleles are unknown, not benign. It is not a nonsense/frameshift predictor or a required new gate for already molecularly confirmed Kabuki cases. |
| A plausible splice-disrupting human variant | [Pangolin](https://github.com/tkzeng/Pangolin), with [SpliceAI](https://github.com/Illumina/SpliceAI) as a conditional comparator | Select the exact allele, transcript, reference and independent RNA/functional reference first. Pangolin offers local inference and GPL-3.0 code; separately qualify the selected bundled weights. The current SpliceAI repository declares PolyForm Strict code and CC BY-NC 4.0 weights; older descriptions of its licence must not be reused. Scores do not establish host-response direction. |
| A human noncoding regulatory effect or variant-to-gene hypothesis | AG2; one member of the [Borzoi family](https://github.com/calico/borzoi) if local inference is actually needed | AG2 remains the broad optional regulatory arm. Borzoi is a narrower RNA-coverage comparator with a local implementation. Choose a model using its actual tissue/output catalogue and the consumer's endpoint. Neither establishes clinical pathogenicity or downstream toxin response by itself. |
| Integration or representation of observed single-cell RNA counts | [scVI](https://docs.scvi-tools.org/en/stable/user_guide/models/scvi.html) | More directly aligned with measured cell-state integration than a DNA regulatory predictor. Use only when single-cell data and independent biological units justify it; current bulk RNA companions do not become single-cell inputs. Compare with donor-aware conventional analysis and avoid removing disease effects as batch effects. |
| A measured perturbation transferred to another supported human cell context | [State](https://github.com/ArcInstitute/state) | Relevant to a future T06 host-response consumer if the perturbation and inputs are supported. The published model's perturbations need training exposure; it is not an arbitrary unseen-venom simulator. Code, model-use and output redistribution terms are separate; qualify the selected artifact and use. |
| An unseen perturbation described through biological knowledge | [PIE](https://arcinstitute.org/news/pie) | Watch and assess only against a concrete independent reference. Its October 2026 developer results address unseen perturbations more directly than State, but do not establish venom-specific validity. Source-derived knowledge and perturbation data require overlap control; pretrained weight terms are non-commercial. |

For local regulatory inference, the [author-maintained PyTorch port and Flashzoi implementation](https://github.com/johahi/borzoi-pytorch)
offers base Borzoi, Flashzoi and Borzoi Prime. The corresponding published model
cards identify [base weights as CC BY 4.0](https://huggingface.co/johahi/borzoi-replicate-0),
[Flashzoi weights as MIT](https://huggingface.co/johahi/flashzoi-replicate-0) and
[Prime weights as Apache-2.0](https://huggingface.co/johahi/borzoi-prime-replicate-0).
Those labels are not interchangeable with the implementation's Apache-2.0 code
licence. Flashzoi's speed is an upstream claim; its documented modern NVIDIA GPU,
FlashAttention-2 and mixed-precision requirements must match an actual qualified
device. Prime's cell-type RNA coverage is useful only if its catalogue fits the
question. Select one comparator rather than adopting all three. Models trained
on the same genomic folds do not supply independent validation cohorts.

[CpGPT's licence](https://github.com/lucascamillomd/CpGPT/blob/main/LICENSE) is a
modified MIT licence with restrictions on compensated aging-biomarker/longevity
competitions; do not label it unrestricted MIT. Its exact pretraining overlap
with the selected cohorts has not been audited here. A smaller checkpoint can
be a feasibility advantage, but only a matched evaluation can establish utility.
The [scvi-tools code](https://github.com/scverse/scvi-tools) uses BSD-3-Clause;
any reused checkpoint and dataset retains its own provenance and terms. State's
[model licence](https://github.com/ArcInstitute/state/blob/main/MODEL_LICENSE.md)
must be read separately from its CC BY-NC-SA code licence. Genetic knockdown is
not automatically equivalent to heterozygous disease, drug exposure or venom.

[Evo 2](https://github.com/ArcInstitute/evo2) is a lower-priority sequence-model
lead, not a qualified human regulatory or venom-binding replacement. Broad
multi-species pretraining does not validate a new species/task. [Scooby](https://github.com/gagneurlab/scooby)
and its newer cell-conditioned work remain a watch item pending exact inherited
model/output terms and a suitable reference. Enformer, Sei, scGPT and Geneformer
do not justify additional runtimes without a specific advantage over the chosen
baseline and shortlisted consumer. This assessment starts no standalone animal
genomics, toxin-design or new perturbation programme.

Protein-structure prediction is a possible later T06 interpretation task, once
PXD003403 protein identities, sequence mappings and a specific structural question
are qualified. [AlphaFold 3](https://github.com/google-deepmind/alphafold3) or
[Boltz-2](https://github.com/jwohlwend/boltz) could supply structural hypotheses
for specified proteins or complexes. Structures and interface-confidence scores
do not establish toxin activity, clinical severity or antivenom neutralisation.
The [Boltz affinity module](https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md)
supports small-molecule–protein binding; do not describe it as a toxin–antibody
affinity predictor. A selected consumer needs exact inputs, artifact-specific
terms and an independent structural or functional reference. Current source
reconciliation remains the priority; no structure-model dependency or protein
design work is introduced.

## MethylGPT release and executed public metadata overlap audit

The reviewed [v1.1.2 release](https://github.com/albert-ying/MethylGPT/releases/tag/v1.1.2)
resolves to `7b137f593caa941ee5b12b803ff98759c1d5c90c` and uses the `methylgpt-1.1`
weight bundle. Its [versioned package documentation](https://github.com/albert-ying/MethylGPT/blob/7b137f593caa941ee5b12b803ff98759c1d5c90c/methylgpt/package/README.md)
accepts sample-by-CpG beta values in [0, 1] and covers **49,156 CpGs**, not all
probes on a 450K or EPIC array. Default imputation uses a factor reconstruction;
the optional neural correction is not documented as an accuracy improvement.
`impute()` retains observed values, `reconstruct()` estimates all vocabulary
positions and `residuals()` keeps missing values missing. These operations must
not be substituted for one another.

The documented disease-analysis checkpoint is `weights_age_stage.pt`; a default
clock-distilled embedding answers a different question. The public PyPI
`methylgpt` 0.1.x package is the older 2024 implementation, not this rebuilt
release. Any later evaluation must pin the source and selected artifact rather
than assuming a bare package install selects this version. The reviewed package
declares Apache-2.0; the exact downloaded checkpoint's rights and hash still need
artifact-level qualification. No checkpoint was downloaded in this assessment.

We executed a public **metadata-only exact-ID join**, not a molecular analysis:
the full versioned upstream split table was decompressed and parsed, then joined
to the repository's pinned assay catalogue. The [aggregate receipt](qualification/model-source-overlap-2026-11-28.json)
records immutable source URLs, SHA-256 and Git-blob hashes where available, byte
counts, row totals, split totals and the reproduction method. It exports no
profile identifiers, individual rows, molecular values or model outputs.

| Catalogued series | Distinct catalogued assay IDs | Exact IDs in upstream train / development | Exact IDs in upstream test | IDs absent from this split table |
|---|---:|---:|---:|---:|
| GSE97362 | 235 | 0 / 0 | 235 | 0 |
| GSE116300 | 44 | 0 / 0 | 44 | 0 |
| GSE218186 | 62 | 0 / 0 | 0 | 62 |

The split table contains 169,120 distinct profile IDs: 145,700 train, 3,922
development, 14,185 test, 5,203 excluded-downstream and 110 excluded-QC. All 279
exact matches above are in its **test** partition. This does **not** establish
training contamination. It establishes that those cohorts were included in the
upstream evaluation corpus and cannot be presented as previously unseen external
validation of that release. Neither exact-ID absence for GSE218186 nor zero
train/development matches proves biological independence: sample aliases,
reused controls, earlier checkpoints and vocabulary/model-selection exposure
remain unresolved. The local catalogue itself does not confer scientific or
source-rights admission.

Consequently MethylGPT is a conditional sensitivity-analysis candidate. Before
making an independent replication claim, identify a suitable external reference
and qualify overlap at the biological-unit level. Do not change the original
T02 estimand or reserve a known upstream test cohort as if this audit had made it
new. The audit is complete as a source-overlap receipt; model performance,
Kabuki-effect preservation and device qualification are **not run**.

## Follow-up: qualify inputs before selecting an adapter

The [28 November source-readiness receipt](qualification/model-input-readiness-2026-11-28.json)
adds a bounded CpGPT availability audit. At the pinned code/model/dependency
revisions, inspected repository inventories and small/large configurations do
not provide a checkpoint-linked study/profile split manifest. **Train,
validation, test and excluded membership remain unknown for GSE97362,
GSE116300 and GSE218186; none is recorded as zero overlap.** This does not prove
that a manifest is absent elsewhere. Configured local split directories and
probe/genome annotation databases do not establish cohort membership.

The documented CpGCorpus metadata route uses requester-pays S3; no request was
made. Corpus presence would still not establish checkpoint-specific membership.
Before an independent benchmark, obtain an accessible, versioned membership
table linked to the selected checkpoint. The pinned code licence adds a
restriction on compensated aging-biomarker/longevity competitions; preserve the
full terms instead of relying on the model-card MIT label. No model/dependency
binaries were downloaded and no CpGPT inference was run.

For the conditional T06 consumer, the [source-to-parameter assessment](../conductor/tracks/t06-toxin/feasibility.md)
finds no qualified genotype–exposure–response linkage in GSE261305 and the
related venom deposits. It records existing complement models as narrower
mechanistic references. Quantitative execution remains held; a regulatory or
missense score cannot replace the missing biochemical observations.

## AlphaGenome 2: retained scope and constraints

The [official API documentation](https://www.alphagenomedocs.com/getting_started.html)
supports DNA sequence/interval/variant queries with a selected reference condition
or human single-cell expression conditioning. The [official release](https://deepmind.google/blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease/)
and [preprint record](https://api.biorxiv.org/details/biorxiv/10.64898/2026.11.11.765857)
support a recent regulatory-model advance; their benchmarks do not validate
Kabuki episignatures, envenomation severity or antivenom response. Full-paper
evaluation and training-overlap qualification remain necessary for a selected use.

- The [own-cell interface](https://www.alphagenomedocs.com/colabs/v2/conditioning_on_single_cell_data.html)
  requires human raw integer UMI counts with Ensembl gene IDs, at most 256 cells
  per call. A venom name, bulk sample profile or disease label is not a measured
  cellular state. Multiple cells are not independent donors. The encoder does
  not itself resolve donor/batch confounding.
- The [imputation guide](https://www.alphagenomedocs.com/user_guides/imputation.html)
  distinguishes `observed` training supervision, `imputed_supported` and
  `imputed_exploratory`. Every query output remains a prediction. Expression-only
  conditioning does not support methylation/histone imputation on its own;
  unmeasured splice, TF-binding and contact outputs remain exploratory. Retain
  per-track support labels and exclude unsupported modalities from primary claims.
- The [FAQ](https://www.alphagenomedocs.com/faqs.html) documents human hg38 and
  mouse mm10 reference support, unbenchmarked predictions in other species and
  raw rather than calibrated clinical-risk scores. Its allele substitution can
  accept a reference mismatch: any future adapter must independently validate
  assembly, normalized alleles, coordinates and REF against the pinned FASTA.
- The [official client terms summary](https://github.com/google-deepmind/alphagenome)
  restricts direct API/Atlas outputs to non-commercial research and prohibits
  their use to train other ML models or make clinical decisions. The Apache-2.0
  client licence is distinct from output rights. Any expressly permissive
  downloadable-artifact exception must be verified for the selected artifact.
  Do not put restricted predictions into T05's learned feature matrix, distil
  them, or silently convert them into fitted model priors. Use a fixed external
  interpretation/benchmark arm while those terms apply. Public redistribution
  requires its own artifact-specific determination.
- A predicted local sequence effect does not simulate the genome-wide trans
  consequences of a chromatin-regulator defect. AG2 methylation output is not a
  replacement for the measured KMT2D-associated T02 phenotype, preprocessing or
  QC. This is a scope inference, not a claimed negative Kabuki benchmark.
- Human regulation, animal genomic context, toxin structure/binding and clinical
  response remain separate evidence types. Other-species sequence acceptance is
  not validated snake or cubozoan regulatory prediction. No shortlisted model
  supplies toxin dose, reaction kinetics, neutralisation or a genotype-by-exposure
  causal effect merely by producing a score.
- [AlphaGenome Atlas](https://www.alphagenomedocs.com/) and AG2 are separately
  identified products; an Atlas lookup is not automatically AG2 inference.
  Current non-commercial live API rates suit bounded cached analyses, not a
  promised unrestricted whole-genome service. AG2 self-hosting has not been
  qualified in this assessment.

## Proposed evaluation contract

Select **one** actual consumer and model family before implementation. The owning
scientific track completes its [N0/N1 requirements](novelty-priority-protocol.md),
including current literature and dataset overlap, source rights and the actual
estimand. This document does not create an additional admission system.

### A. Measured methylation: optional profile-model sensitivity

Keep qualified measured beta/M values and the existing inference as the primary
analysis. Predefine whether the optional task is missing-probe reconstruction,
fixed representation or independent biological corroboration; these are
different estimands. Do not convert an age/tissue predictor into a diagnostic
classifier by relabelling its output.

Before execution, reconcile the selected checkpoint's training, development and
upstream test membership with target studies, reused controls and sample aliases.
Record known overlap and unknowns. A model's published test cohort is not fresh
independent validation for this project; an accession missing from one group
column is not proof of absence under other identifiers. Keep subject/family,
study and platform partitions together as appropriate.

Freeze observed-probe-only/no-imputation and simple training-derived reconstruction
baselines before using a model. Test multiple prespecified missingness patterns,
including platform-specific coverage and patterns supported by the actual QC
process; random masking alone is insufficient. Preserve the original observed
matrix and missingness mask. Report reconstruction on genuinely held-out observed
values, probe coverage, error by platform and preservation or attenuation of
prespecified disease effects. Freeze effect-preservation endpoints before
evaluating them. Imputed values must never silently become measurements or alter
molecular eligibility. No outcome-driven selection of imputation or embedding
methods is permitted on the reserved replication cohort.

### B. Human regulatory loci or variants

Use independently specified functional references for variant-to-gene and
cell-context questions. Public reference intervals can support a non-patient
technical/regulatory benchmark; patient-specific claims require actual variants
and separately qualified linkage. Compare frozen proximity and empirical
regulatory annotations with AG2 and, only if justified, one local regulatory
comparator. Hold out linked variants/loci and account for LD, gene-family and
training-corpus overlap. Multiple model replicates or predictors trained on
related sources do not create independent biological evidence.

Select conditions, modalities, mapping rules and score direction before seeing
results. Measure coverage, unsupported/failed calls, precision and recall of
supported links, direction where independently measured, and recovery at a fixed
review budget, with uncertainty at the independent locus/study level. Retain
negative controls and clinically relevant counterexamples. Do not transform
arbitrary raw scores into pathogenicity probabilities. Independent source
agreement is stronger than agreement between correlated predictors.

### C. Coding or splice interpretation

Use an exact human allele/transcript/protein match for missense lookup; keep
unsupported consequence types and missing records distinct from benign calls.
For splicing, freeze the FASTA, annotation, masking, window and aggregation rules;
retain reference mismatches and unsupported variant types. Compare to independent
RNA/functional evidence where available. A predicted damaging variant does not
specify the direction of susceptibility to venom or revise the source-defined
Kabuki inclusion rules.

### D. Measured single-cell response

Start only with a justified cell-state or perturbation consumer, admissible raw
counts, observed treatments/controls and adequate independent biological units.
Genetic perturbation, drug exposure and crude venom exposure are separate
transfer settings. Hold out donors, biological replicates, studies and the
specified perturbation or combination as the actual question requires. Cells
conditioned on a measurement cannot independently validate recovery of that same
measurement.

Require no-change/control, mean and appropriate linear baselines; add an additive
baseline for combinations. Evaluate both full-profile and prespecified
perturbation-sensitive outcomes. Calibrate metrics with positive and negative
controls on development data and freeze metrics/weights/feature selection before
test evaluation. A technical-duplicate positive control is an evaluation
diagnostic, not an observation available to a deployed predictor. Keep direction,
strong/weak-response strata, uncertainty and negative transfer visible. The
[2026 calibration study](https://www.nature.com/articles/s41587-026-03307-w) shows
why neither one aggregate correlation nor a blanket claim that all deep models
lose to simple baselines is adequate.

## Prediction evidence and storage

Reuse the existing [medallion layout](medallion-layout.md), registry conventions
and file interchange. No new schema package, database, orchestration service or
mandatory GPU/runtime is needed for this decision record.

| Layer | Required content |
|---|---|
| Bronze | Source/request manifest, unmodified response or versioned lookup reference, input and artifact hashes, code/checkpoint/table versions, retrieval/inference date, source and applicable terms. |
| Silver | Explicit predicted-annotation records with species, build/coordinates/alleles, gene/transcript, condition and its source, modality/scorer/units/direction, support status, unsupported reason and provenance. Methylation reconstructions retain original observed values/mask and their derivation. |
| Gold | Prespecified comparison, uncertainty, coverage, errors, cost/runtime and negative results, with exact input/model versions and scientific scope. |

Code and safe aggregate receipts belong in GitHub. Existing HF storage may hold
only artifacts whose specific source/model/output rights and disclosure decision
permit it; source-linked storage remains sufficient. No automatic publication of
new predictions and no patient/model upload follows from this assessment.

Any future adapter remains optional and uses the upstream maintained client or
CLI where suitable. Mock/cache paths serve ordinary CI; live inference needs an
explicit eligible run. Record all failures, version changes and response hashes;
never silently fall back to another model. Qualify numerical port/precision and
actual device compatibility only when the selected implementation requires them.

## Acceptance and next decision

This increment is complete as a documented selection/evaluation decision only
after independent content review and the existing current-base hook/strict,
privacy, dependency and applicable provider checks pass. The PR retains exact
review/check receipts; parent T05/T06 scientific milestones stay planned.

The next scientific decision is the first eligible consumer/reference pair,
with training/evaluation overlap resolved and source-specific use permitted.
Only then choose one adapter and freeze N1. Continue or narrow the model addition
if it produces prespecified incremental information at acceptable error and cost;
retain a null benchmark or stop if simpler evidence suffices. Do not select the
winning metric or publish a new clinical claim after looking at reserved results.
