# T02 — task-level execution plan (future, not started)

- [ ] **T02.01:** After T01/E0, select molecularly appropriate KMT2D cases and same-study controls initially from native GSE97362 (11+11). GSE116300 and GSE218186 are separately conditional replication cohorts. Use the original source diagnoses; no variant reclassification or genotype–phenotype analysis. See [24 November first-science receipt](../../../research/qualification/t01-first-science-2026-11-24.md). Resolve participant reuse, specimen/platform identity and estimable covariates; count biological participants separately from assays.
- [ ] **T02.02:** Confirm the N1 protocol already frozen during selected-method qualification: E2/E3 discovery/replication groups, features, region effects, bias-aware pathways, multiplicity and covariates. Refresh novelty without changing frozen outcomes. Changes to method or scientific choices require an explicitly new protocol and requalification before execution. Keep reserved replication effects concealed and fit feature/module choices within training only.
- [ ] **T02.03:** Consume the already accepted named T07 assay/QC/inference/enrichment contract, exact backend version and evidence. Do not select or qualify a backend after starting this analysis. Rust comparison is required only for a selected Rust route; a separately qualified reference route remains valid. Unsupported DMR/enrichment stages retain their chosen validated method.
- [ ] **T02.04:** Execute E2 within-study case-control estimates, then E3 frozen replication against each cohort's native controls. Evaluate effect-direction/magnitude, actual genomic-region/gene drivers, pathway transfer and uncertainty; label EPIC-only discoveries exploratory without another independent EPIC test.
- [ ] **T02.05:** After any analysis, perform N2: repeat novelty/publication/preprint/dataset queries, reassess clinical contribution and journal fit, decide one P1 manuscript versus benchmark/combine/hold, and inspect dependency removals or swaps. Add T03/E4 only if it strengthens the same primary question; execute N3 if submitting.
- [ ] **T02.06 — conditional:** Assess whether E1 is needed to resolve a specific platform-measurement uncertainty. If so, qualify the GSE86829/GSE86831 same-specimen reference and compare paired measurements with the limits in the experiment plan. It is supporting evidence, not a routine blocker or a rare-disease control pool.

## Execution batches after admission

These are future outputs; no disease-analysis command exists in the catalogue/publisher tools. Use only the real backend commands frozen by T07.02 and N1. The receiving T02 owner records them verbatim in each receipt, with source and input hashes.

| Order / tasks | Input and executable action | Output / pass criterion |
|---|---|---|
| A: .01–.03, receive | Read T01's local participant/assay/exclusion manifests, selected T07 contract and acceptance, and official-device receipt. Match the source revisions, molecular subset, roles and covariates to frozen N1. Run the existing strict code gate before any code change. | `admission.md` in this track plus a hash-bound local analysis manifest. Pass only if every required receipt and selected row is accepted; a mismatch or unknown required field holds execution. |
| B: .04, E2 | Run the selected within-study command on discovery data with each study's native controls; preserve the full feature universe, M-value units and scaled uncertainty. Fit any feature/module choices on discovery only. | Local `data/gold/t02-kabuki/e2/` effect, uncertainty, feature-coverage and QC tables; cleared execution receipt naming command, hashes and counts. Pass the frozen numerical/consumer checks; do not inspect replication effects to tune choices. |
| C: .04, E3 | Freeze and hash the discovery definitions, then run the independent replication command with its own controls. Calculate the prespecified direction/magnitude/coverage metrics and uncertainty using the same feature/build semantics. | Local `data/gold/t02-kabuki/e3/` transfer tables and a cleared receipt, including negative results and EPIC-only exploratory labels. Independence and protocol compliance are required; significance is not a completion criterion. |
| D: .05 / optional .06, decision | Execute N2 searches and compare the observed contribution to the frozen question. Add E1 or T03 only for a documented remaining uncertainty/contribution. | `n2.md` records publish / combine / benchmark / hold / stop, sources and rationale; N3 only when submission is actually selected. No paper, clinical validity or publication acceptance is presumed. |

T01 owns missing cohort evidence; T07 owns missing method evidence; the trusted runner operator owns actual-device execution. T02 remains planned while any mandatory receiving gate is open. Optional raw mirroring, full Rust ports and hierarchical modelling are not prerequisites.

## Receiving record

- Assigned owner: **unassigned**
- Branch / pinned head: **none**
- Data rights and checksum receipts: **not run**
- Exact tests / numerical baselines: **not run**
- Publication / ethics gate: **not assessed**
- Conductor disposition: **planned**

Before marking complete, link exact evidence and obtain the integrator's receiving acknowledgement. Never infer completion from a document or synthetic fixture alone.
