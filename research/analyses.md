# Prioritisation: analyses rather than library ratings

**Reassessed 22 November 2026.** All scores are **provisional subjective design judgements** on scales of 1–5: N novelty potential, I scientific/clinical impact potential, F feasibility with currently identified public evidence. Ranges express unresolved question-specific novelty and data readiness; they are not confidence intervals, publication odds or performed power calculations. Impact is conditional on establishing the result, not demonstrated clinical benefit. Hard gates may reverse the order. Score analyses and coherent study bundles, not libraries.

| ID | Scientific analysis | Input data | Methods / outcome | N | I | F | Target track |
|---|---|---|---|---:|---:|---:|---|
| A | Kabuki cross-study pathway replication | GSE97362, GSE116300, GSE218186 | independent adjusted DMP/DMR and pathway transfer; effect concordance | 2–3 | 3 | 3 | T02 / E2–E3 |
| B | Sotos–Weaver regulatory contrast | GSE74432, GSE191276 | regional methylation, gene mapping, pathway specificity | 1–2 | 3 | 2–3 | T03 / E4 |
| C | Kabuki–Sotos–Weaver regulatory convergence | GSE97362, GSE74432 (+ qualified replication) | shared/unique modules and genomic-context nulls | 1–2 | 3 | 2–3 | T03 / E4 |
| D | Reciprocal dosage | GSE66552 | deletion/duplication effect direction and module symmetry | 2 | 3 | 3 | T03 / E4 |
| E | Sotos methylation vs expression | GSE191276, GSE191274 | pairing audit; narrow external confirmation rather than unconstrained individual network learning | 1–2 | 3 | 2 | T05 / E6 |
| F | ADNP mutation-stratified cross-modal modelling | GSE152427, GSE152421 | qualified paired or disease-level effects; independent validation | 2–3 | 3–4 | 2 | T05 / E6 |
| G | Regional hierarchical model | qualified Kabuki/Sotos/Weaver/TBRS/SMARCA2 cohorts | compare per-disease, pooling, selective pooling, calibrated uncertainty | 3–4 | 4 | 2 | T04 / E5 |
| H | Genotype-aware clinical convergence | G+MONDO/OMIM/HPO | disease-level molecular vs phenotype similarity, leakage guards | 2–3 | 3–4 | 2 | T04 / E5 |
| I | Leave-one-disease-out transfer | G, independently qualified test cohorts | masked predictions from externally available predictors; negative transfer/abstention | 3–4 | 4 | 2 | T04 / E5 |
| J | Out-of-family generalisation | GSE221644, GSE269416 | out-of-distribution diagnostics with tissue/cell and mixed-diagnosis qualifications | 2–3 | 3 | 2 | T04 / E5 |
| K | Complement × cobra venom factor | GSE261305, PXD003403, curated kinetic model | quantitative scenario / identifiability; no genotype-interaction claim from unpaired inputs | 2–3 | 3 | 1–2 | T06 |
| L | Genotype×toxin interaction framework | qualified experimental variant-toxin pairs TBD | held-out functional perturbation predictions | 3–4 | 4–5 | 1 | T06 |

A's feasibility is reduced from 5 to 3 because participant independence, molecular subsets, usable metadata and actual file/rights qualification remain unresolved. Three Sotos cases and a pooled parental array do not supply an adequately sized independent network-learning cohort. B/C/E novelty is lower because comparative pathways and Sotos methylation–expression mechanisms already have substantial prior art. G–J remain conditional opportunities: meaningful holdouts, clinical interpretation and calibrated improvement have not been demonstrated.

## Coherent publication opportunities

Follow the [experiment/publication plan](experiment-publication-plan.md). These bundles share prerequisite work and are not additive publication counts.

| Bundle | Experiments and contribution | N | I | F | Disposition |
|---|---|---:|---:|---:|---|
| **P1: default clinical study** | E0 + E2 + E3: cohort qualification, platform robustness and independently useful KMT2D biological replication; E1/backend parity as supporting material | 2–3 | 3 | 3 | First decision point; one coherent manuscript only if clinically interpretable findings or useful limits justify it |
| **P1 extended** | P1 plus one focused E4 comparison that strengthens the same clinical question | 2–3 | 3–4 | 2–3 | Prefer combining a small useful comparison over creating a separate paper |
| **P2: conditional combined transfer study** | E4 + E5, with E6 only when expression adds independent information; calibrated transfer and negative-transfer limits | 3–4 | 4 | 2 | Later opportunity after adequate qualified contrasts and holdouts; cross-disease and multiomics work can form one study |
| Focused metabolic/functional study | Adequate E6/E7 evidence for a distinct inherited-metabolic or diagnostic question | 3–4 | 4–5 | 1 | Separate only if the actual evidence supports a distinct question; no new metabolic cohort or wet-lab study authorised |
| Implementation parity/port alone | A reproducible backend comparison without a new method or clinical finding | 1–2 | 2 | 3 | Supporting artefact by default; a software-methods paper requires a further generalisable contribution |

Generic Kabuki pathway lists or broad NSD1–DNMT3A overlap have novelty potential around 1–2, even when easy to compute. A higher bundle score depends on its distinct, falsifiable question and independent evidence, not the number of languages, ontologies, assays or diseases. If a bundle fails its scientific gate, keep the benchmark, combine coherent findings or stop; do not force a paper per track.

**Sequencing policy:** these N/I/F scores do not rank acceptance likelihood. At N0 and N2, apply [novelty/priority gates](novelty-priority-protocol.md): rights/ethics, independence, case/control quality, sample/power, clinical interpretability, external replication, study cost, publication recency, journal audience/APCs and negative transfer. A hard hold overrides an attractive score. T02 is a low-cost reference exercise, not guaranteed publication; T03 and T05 can swap based on matched data and clinical findings. T04 is contingent on validated disease-level estimates and meaningful improvement over simpler models. T06 is independently gated. Do not force a single fixed disease order.

**Main publication priorities:** A/E2–E3 supports the single default P1 clinical reproducibility study. B/C/E4 is an optional focused extension or part of later P2. G+I/E5 and E/F/E6 can be combined when expression supplies independent evidence for transfer; they do not imply separate manuscripts. K/L remain separately gated. [Journal routing](journals.md) follows the contribution actually established.

**No novelty claim without prior art:** the [dated overlap review](experiment-publication-plan.md#prior-art-already-narrowing-the-opportunity) includes Velasco 2021, Levy 2022, Giuili 2023, Cuvertino 2025, Brennan 2022, Wheeler 2026, Wang 2026 and Hansknecht 2026. Their comparisons, Kabuki networks/classifiers, NSD1–DNMT3A convergence and Sotos expression/cell-model work narrow generic novelty. Verify the precise analysis at N0–N3; this score revision does not establish that any proposed claim is first.

