# T06 — task-level execution plan (source feasibility assessed; modelling held)

- [ ] **T06.01:** Start with GSE261305 for complement disease and PXD003403 venom proteins; verify genetic subsets and whether CVF identification is quantitative.
- [ ] **T06.02:** Inventory pre-existing complement models, species-specific validity, venom concentration/kinetics and published experimental observations.
- [ ] **T06.03:** Check identifiability and specify a simple model against existing quantitative evidence. Assess diffsol for ODE/DAE, rebop for reaction jumps, or differential-equations for a required SDE, with Julia Catalyst/SciML reference/fallback. Public solver/SBML tests and biological perturbation validation are separate requirements.
- [ ] **T06.04:** If data permit, freeze a genotype-by-toxin prediction and compare with independent functional observations; otherwise retain feasibility hold.

## Feasibility-first batches

| Order / tasks | Input and action | Output / acceptance |
|---|---|---|
| A: .01 / .02 | Read the source API records, original study methods and actual file inventories for GSE261305/PXD003403. Record species, host genotype/subset, venom identity, measured quantities/units, exposure conditions and available kinetic observations. Check existing models before selecting a solver. | `feasibility.md` in this track with exact references/hashes and a source-to-parameter table. Missing quantitative exposure or independent functional observations stays explicitly unknown; a protein identification is not a reaction rate. |
| B: .03 | If A permits an identifiable question, freeze `n1.md` with parameter bounds, equations, units, independent observations and rejection criteria. Select an existing solver and a reference; record its actual command. Run its applicable small analytic/conservation cases before any biological comparison. | A bounded synthetic model/fixture and exact numerical receipt, through the shared strict code gate. Hold non-identifiable parameters or unverifiable species assumptions; no new solver or general modelling framework. |
| C: .04 | Only after applicable T01/T07/device and institutional requirements pass, execute the frozen prediction against independently held-out functional observations. Execute N2 afterwards. | Local `data/gold/t06-toxin/` prediction/residual/uncertainty outputs and `n2.md` with proceed / narrow / hold / stop. Numerical accuracy alone cannot support susceptibility, therapy or biological validation. |

The future T06 owner resolves public quantitative/model evidence; the applicable institutional and trusted-device operators own their decisions/runs. This branch never blocks the initial Kabuki study. No new wet-lab work is authorised by a feasibility plan.

## Receiving record

### 28 November public-source feasibility assessment

[Batch A feasibility](feasibility.md) now records the original GSE261305/PXD003403
methods, metadata inventories, source hashes and existing complement-model
comparison. The [safe source receipt](../../../research/qualification/model-input-readiness-2026-11-28.json)
keeps metadata retrieval separate from molecular payloads and model execution.
The bounded authored assessment requires independent review and exact-current-base
integration checks; its final receiving evidence belongs in the PR/archive.

GSE261305's 108 assays are not an established genetically confirmed cohort.
PXD003403 is the bottom-up deposit; MSV000079351 identifies related PXD004160.
CVF identification and relative proteomic methods do not supply active exposure
or kinetics. Keep .01/.02's scientific qualification and .03/.04 open: the
inspected pair does not support an identifiable genotype-by-venom prediction.
No N1 freeze, solver selection, model inference or parent-track completion.

### 28 November conditional model reuse

Receive the [T05-owned model assessment and evaluation contract](../../../research/model-selection-2026-11-28.md)
only when T06.01/.02 identifies eligible human inputs and a testable exposure
question. AlphaMissense or a splice predictor may supply consequence-specific
annotations; AG2 or one Borzoi-family model may supply regulatory predictions.
None supplies toxin binding, reaction rates, dose-response parameters or the
direction of genotype-dependent clinical susceptibility.

Measured single-cell response work would have a separate consumer: scVI for
observed-count integration; State for a supported perturbation/context transfer;
PIE as an unqualified newer candidate for unseen perturbations. State's published
training-exposure limits do not support arbitrary new venom predictions. Require
actual independent functional observations, frozen conventional baselines and
calibrated response metrics before interpreting any transfer. Preserve the
feasibility hold where inputs or identifiability are missing; do not create an
animal-genomics programme or delay V01 source reconciliation. No model was run
and no new model dependency or T06 scientific milestone was completed.

- Scientific execution owner: **unassigned**; bounded source assessment: current integrator
- Quantitative branch / pinned head: **none**; source-assessment head bound in its PR/archive
- Data rights and checksum receipts: public metadata/document hashes recorded in [feasibility](feasibility.md); molecular rights, clinical linkage and scientific admission **unqualified**
- Biological/numerical baselines: **not run**; metadata/code integration receipts belong in the PR/archive
- Publication / institutional gate: **unqualified**; source-specific conditions described in feasibility
- Conductor disposition: bounded source assessment recorded; quantitative/scientific work **held**

Before marking complete, link exact evidence and obtain the integrator's receiving acknowledgement. Never infer completion from a document or synthetic fixture alone.


