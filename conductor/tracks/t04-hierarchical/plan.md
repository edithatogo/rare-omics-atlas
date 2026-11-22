# T04 — task-level execution plan (future, not started)

- [ ] **T04.01:** Freeze region/module estimands and held-out diseases before fitting.
- [ ] **T04.02:** Compare separate-disease, complete-pooling and partial-pooling models with fixed priors and source information. Assess existing nuts-rs with a qualified density/gradient provider first; use Julia/Turing when it avoids substantial custom model infrastructure.
- [ ] **T04.03:** Run leave-one-disease-out and whole-study-out checks, calibrated uncertainty and negative-transfer analysis. Specify predictors available without the held-out disease's molecular outcomes; distinguish predicting an unseen disease effect from denoising an effect already observed in that disease.
- [ ] **T04.04:** Jointly refit and test invariance to ingestion order; avoid training with HPO features subsequently scored as ground truth.
- [ ] **T04.05:** Before selecting an inference backend, qualify density/gradients/transforms, analytic cases, simulation-based and posterior-predictive calibration against the fixed reference; compare distributions within Monte Carlo error. See `research/backend-replacement-policy.md` and `research/rust-candidate-audit.md`; no new sampler/PPL.

## Receiving record

- Assigned owner: **unassigned**
- Branch / pinned head: **none**
- Data rights and checksum receipts: **not run**
- Exact tests / numerical baselines: **not run**
- Publication / ethics gate: **not assessed**
- Conductor disposition: **planned**

Before marking complete, link exact evidence and obtain the integrator's receiving acknowledgement. Never infer completion from a document or synthetic fixture alone.

