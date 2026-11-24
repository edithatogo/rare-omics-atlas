# T06 — task-level execution plan (future, not started)

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

- Assigned owner: **unassigned**
- Branch / pinned head: **none**
- Data rights and checksum receipts: **not run**
- Exact tests / numerical baselines: **not run**
- Publication / ethics gate: **not assessed**
- Conductor disposition: **planned**

Before marking complete, link exact evidence and obtain the integrator's receiving acknowledgement. Never infer completion from a document or synthetic fixture alone.

