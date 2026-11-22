# T04 — specification

## Objective

Determine whether mechanism-informed partial pooling improves small-cohort effect estimates or independently held-out predictions over separate-disease and complete-pooling baselines. This is **optional experiment E5**, normally part of the conditional **P2 combined transfer study**, in the [experiment/publication plan](../../../research/experiment-publication-plan.md). T04 is not a prerequisite for the initial clinical paper.

## Scientific / governance boundary

No execution, downloads or code generation is authorised by this planning track. Any source-dependent assertion requires independently verifiable evidence. Follow `conductor/workflow.md` and Ponytail decisions.

## Inputs and dependencies

Use only admitted E2/E4 disease-effect tables. See the [candidate dataset register](../../../research/datasets.md), [analysis matrix](../../../research/analyses.md) and [focused backend audit](../../../research/methylation-backend-audit.md). An accession or a significant-feature list alone is not sufficient input.

The receiving contract must preserve:

- Exact study, participant-dependence, disease/mechanism, feature and named-contrast identity; tissue, platform, genome build, assay coverage and provenance.
- A disease-minus-native-control effect on a declared scale, its **correctly scaled standard error**, uncertainty definition and applicable degrees of freedom. An M-value contrast is a difference in log methylation odds, not an expression fold change. Prespecify ordinary versus moderated uncertainty and the likelihood that uses it; do not silently mix them or assume estimated SEs are known without justification.
- Case/control counts, design/covariates/weights, missingness and non-estimability statuses, and the complete prespecified feature universe. Shared controls, repeated participants and related samples require a covariance/dependence treatment or a defensible independent subset.
- For region/module summaries, fixed definitions, contributing probes and an uncertainty calculation that respects their dependence. A shared region name does not guarantee the same measured sites across platforms.

**Do not ingest the inspected limma-rust `lfcSE` field as an effect SE:** it exports unscaled design uncertainty. Ordinary SE requires multiplication by residual sigma; moderated SE requires multiplication by the square root of posterior residual variance. Obtain a qualified, explicitly named quantity from the fit outputs or a corrected upstream export, and check the actual consumer table against the reference. Hold rows with unresolved IDs, scale, uncertainty or estimability. See [backend replacement contracts](../../../research/backend-replacement-policy.md).

## Evaluation and model boundary

Freeze the estimand, feature construction, priors, baselines and splits at N1. Whole-study holdouts must also exclude overlapping participants/families and reused controls from training. Whole-disease cold-start prediction must mask that disease's molecular outcomes across all its studies and use only predictors available independently of those outcomes, such as frozen gene/mechanism or ontology annotations. Molecularly derived modules, embeddings, feature selection and fitted preprocessing belong inside training folds. Prediction with already observed disease effects is a separately labelled denoising task.

Evaluate predictive loss, uncertainty, negative transfer and prespecified abstention. When scoring a held-out observed effect, include its sampling uncertainty in the predictive target; latent-effect calibration needs known-truth simulations or an appropriate independent reference. Do not use an HPO-derived predictor as its own validation outcome. Joint refitting should remove ingestion-order dependence within numerical/Monte Carlo tolerance; it is a reproducibility check, not a new scientific method.

Use an existing qualified density/gradient route with nuts-rs, or Julia/Turing when it avoids substantial custom infrastructure. Analytic derivatives, num-dual or ad_trait should be considered before experimental Enzyme when they meet the model's needs. An Enzyme comparison is optional supporting work, not an activation gate or standalone novelty claim; no new sampler, PPL or generic backend framework. Follow the [candidate audit](../../../research/rust-candidate-audit.md) and [official local-runner policy](../../../research/local-development.md).

## Publication target

Combine E5 with coherent E4/E6 results in P2 only if they establish a distinct, independently useful transfer claim. Orphanet Journal of Rare Diseases is conditional on clinical interpretation and independent validation; BMC Medical Genomics is an alternative. Use the [journal strategy](../../../research/journals.md) for a primarily methodological or genuinely metabolic question. Backend comparisons ordinarily remain supporting material. No separate paper is owed to this track, a Rust port or Enzyme.

## Exit criteria

- Independent predictive improvement, calibration, or a clear negative result; no uncontrolled false discoveries.
- Received effect/SE contracts and independent evaluation boundaries are satisfied; no conclusion rests on unscaled uncertainty or leaked outcomes.
- Permutation of ingestion order yields materially same joint-fit scientific estimands within tolerance.
- Any over-complex model retired if it does not outperform simpler baselines.
- Exact-source numerical/consumer evidence includes actual runs on the applicable official self-hosted runner; a source review or cloud-shell run is not local acceptance.

## Stop conditions

Apply N0/N1 before execution, N2 after results and N3 before submission/transfer. Continue only with a documented distinct contribution or justified replication. Stop or narrow the task if no worthwhile contribution remains, source rights or uncertainty are unresolved, validation samples are not independent, there are too few disease/study contrasts for the claimed evaluation, the proposed inference is not identifiable, or simpler methods make extra complexity unnecessary. An unsupported Rust/AD route does not block a suitable existing reference model or the earlier clinical study. Record an honest hold rather than invent evidence.

