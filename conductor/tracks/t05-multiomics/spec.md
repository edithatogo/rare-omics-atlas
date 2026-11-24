# T05 — specification

## Objective

Test whether expression adds independently supported information to methylation effects or frozen modules, without false sample pairing or unsupported patient-level prediction.

## Scientific / governance boundary

This scientific experiment has not started. Initial public-source intake elsewhere is authorised and separately recorded; this track does not authorise disease inference or a new scientific implementation. Any source-dependent assertion requires independently verifiable evidence. Follow `conductor/workflow.md` and Ponytail decisions.

## Inputs and dependencies

See [candidate dataset register](../../../research/datasets.md), [analysis matrix](../../../research/analyses.md), and [journal routing](../../../research/journals.md). This track's relevant studies and exact eligibility must be qualified before use.

## Publication target

This is **E6**, normally an extension or validation component of the combined E4/E5 **P2** study when it answers the same primary question. Follow the [experiment/publication plan](../../../research/experiment-publication-plan.md); T05 does not require a separate paper. A distinct focused metabolic/functional study is considered only if the actual E6/E7 evidence justifies it.

European Journal of Medical Genetics or Molecular Syndromology are candidates for a focused clinical result; use the central [journal strategy](../../../research/journals.md) for P2 or a substantive SSIEM-relevant question. Journal fit does not justify inventing pairing or adding an unsuitable cohort.

## Exit criteria

- Pairing is evidenced through participant/specimen records, or analysis is explicitly disease-level only. Shared disease labels or related accessions do not establish matched participants.
- Verified paired sets with adequate information use participant/family holdouts and compare methylation-only, expression-only and combined baselines. Three Sotos methylation cases are inadequate for unconstrained individual-level network learning; narrow prespecified corroboration may still be useful.
- Unpaired cohorts support disease-level directional/biological confirmation, not sample-wise correlation or an assumed patient-level joint model. Freeze genomic mapping/module choices before independent confirmation.
- Incremental information or a justified validation result beyond already published Sotos/ADNP integration is required for promotion; small real cohorts do not establish general predictive performance.
- No causal claims without perturbation data.

## Stop conditions

Reassess overlapping publications through N0/N2; continue only with a documented distinct contribution or justified replication. Stop if no worthwhile contribution remains, source rights are unclear, validation samples are not independent, the proposed inference is not identifiable, or simpler methods make the extra complexity unnecessary. Record an honest hold rather than invent evidence.


## Execution prerequisites

Use the task-level [dependency registry](../../dependencies.json) and [tracks order](../../tracks.md). Admit this experiment's specific datasets and selected method before execution, with actual local-runner acceptance and a current N1 freeze. Optional ports do not block a qualified reference route. The molecular, pairing and identifiability requirements in this specification remain independent gates.
