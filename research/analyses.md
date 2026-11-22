# Prioritisation: analyses rather than library ratings

All scores are **provisional subjective design judgements** on scales of 1–5: N novelty potential, I scientific/clinical impact, F feasibility with currently identified public evidence. Not publication odds. Hard gates may reverse the order.

| ID | Scientific analysis | Input data | Methods / outcome | N | I | F | Target track |
|---|---|---|---|---:|---:|---:|---|
| A | Kabuki cross-study pathway replication | GSE97362, GSE116300, GSE218186 | independent adjusted DMP/DMR and pathway transfer; effect concordance | 2 | 3 | 5 | T02 |
| B | Sotos–Weaver regulatory contrast | GSE74432, GSE191276 | regional methylation, gene mapping, pathway specificity | 3 | 3 | 4 | T03 |
| C | Kabuki–Sotos–Weaver regulatory convergence | GSE97362, GSE74432 (+ qualified replication) | shared/unique modules and genomic-context nulls | 3 | 4 | 4 | T03 |
| D | Reciprocal dosage | GSE66552 | deletion/duplication effect direction and module symmetry | 2 | 3 | 4 | T03 |
| E | Sotos methylation vs expression | GSE191276, GSE191274 | test association/prediction with pairing gate | 3 | 4 | 3 | T05 |
| F | ADNP mutation-stratified cross-modal modelling | GSE152427, GSE152421 | methylation/expression modules; held-out responses | 3 | 4 | 3 | T05 |
| G | Regional hierarchical model | qualified Kabuki/Sotos/Weaver/TBRS/SMARCA2 cohorts | compare per-disease, pooling, selective pooling, calibrated uncertainty | 4 | 5 | 3 | T04 |
| H | Genotype-aware clinical convergence | G+MONDO/OMIM/HPO | disease-level molecular vs phenotype similarity, leakage guards | 4 | 4 | 3 | T04 |
| I | Leave-one-disease-out transfer | G, independently qualified test cohorts | masked predictions + negative transfer/abstention | 4 | 5 | 3 | T04 |
| J | Out-of-family generalisation | GSE221644, GSE269416 | out-of-distribution diagnostics | 4 | 4 | 3 | T04 |
| K | Complement × cobra venom factor | GSE261305, PXD003403, curated kinetic model | quantitative scenario / identifiability; do not claim genotype interaction yet | 3 | 4 | 2 | T06 |
| L | Genotype×toxin interaction framework | qualified experimental variant-toxin pairs TBD | held-out functional perturbation predictions | 5 | 5 | 1 | T06 |

**Sequencing policy:** these N/I/F scores do not rank acceptance likelihood. At N0 and N2, apply [novelty/priority gates](novelty-priority-protocol.md): rights/ethics, independence, case/control quality, sample/power, clinical interpretability, external replication, study cost, publication recency, journal audience/APCs and negative transfer. A hard hold overrides an attractive score. T02 is a low-cost reference exercise, not guaranteed publication; T03 and T05 can swap based on matched data and clinical findings. T04 is contingent on validated disease-level estimates and meaningful improvement over simpler models. T06 is independently gated. Do not force a single fixed disease order.

**Main publication priorities:** A is a feasibility/clinical reproducibility test; G+I is the principal potential methods contribution; B/C and E/F require biological insights or predictive validation beyond already published pathway overlap; K/L separately gated.

**No novelty claim without prior art:** Velasco et al. (2021) compared chromatin disorders; Kabuki hypergraph work already used public cohorts; cross-syndrome methylation function and epi-age comparisons exist. Verify against the specific analysis rather than saying 'first'.
