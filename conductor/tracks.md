# Dependency-ordered tracks

Updated 22 November 2026. **Initial executable work is recorded; complete scientific tracks are not claimed.** Stable track IDs are retained, but T07 selection/qualification moves ahead of every consuming analysis.

| Execution stage | Track / milestone | Requires | Current state |
|---|---|---|---|
| 1 | T00 context and source installation | Repository identity | Complete for project context and pinned source; host auto-activation unobserved |
| 2a | T00 strict code qualification | T00 context; pinned tools | Configure and run the same fail-closed command locally and on hosted PRs; official device acceptance remains separate |
| 2b | T01 source discovery, terms and initial transfers | T00 context | Initial three archive checks and 29-accession rights review complete; broader intake continues |
| 2c | T07 selected-method baseline | T00 context; named method; strict code checks for changes | Fork corpus, fresh synthetic R slice and fresh-fixture identity increments passed; production consumer and disease-method qualification pending |
| 2d | T00 official local runner / institutional route | Actual target device / institutional process | External prerequisites recorded; no operational or ethics approval claim |
| 2e | T07 technical preprocessing acceptance | Selected contract, required reference assets, independent technical fixtures and applicable device receipt | Pending; isolated fixture development can start before device acceptance |
| 3 | T01 analysis admission | Exact cohort, controls, overlap, covariates, accepted technical preprocessing and applicable institutional determination | Pending; no dataset accepted for inference yet |
| 4a | T07 protocol freeze | Data admission + selected method/independent reference contract | Pending; freeze N1 and protect clinical replication before numerical qualification |
| 4b | T07 selected-method acceptance | Frozen protocol, independent consumer-contract evidence and official target runner | Pending; qualify reference or Rust route using technical/discovery evidence |
| 5 | T02 Kabuki E2/E3 | T01 admission + T07 accepted route + confirmation of frozen N1 | Planned |
| 6 | T03 focused cross-disease comparison | T02 reference + separately admitted disease cohorts + selected method + N1 | Planned |
| 7 | T04 hierarchical model | Qualified independent disease effects/uncertainty from T03 + simplest baseline | Planned, conditional on adequate data |
| Parallel later | T05 multimodal validation | Admitted modalities and actual pairing; T02/T03 outputs when testing those modules | Conditional; does not need T04 if no shared model is used |
| Separate later | T06 genotype–toxin question | Quantitative disease/host/perturbation evidence and model identifiability | Conditional, not a prerequisite for the clinical paper |

See [dependencies.json](dependencies.json) for task-level prerequisites and [setup receipt](../research/qualification/setup-receipt.md) for what was actually performed. A partially complete parent track does not prevent work depending only on its completed context milestone.

## Active implementation increment

- [~] [T09 — Minimal GitHub–Hugging Face medallion](tracks/t09_hf_medallion_20261122/index.md): reviewed publisher/workflows and 14-object metadata publication complete; estate registered; raw transfer externally blocked. Full T09 remains open.
- Completed: [T08 API catalogue](archive/t08_catalogue_20261122/index.md), independently reviewed and archived before T09.
- Next: complete [T00 strict verification](tracks/t00-governance/plan.md#strict-verification-increment), then the [T01 source/admission tasks](tracks/t01-sources/plan.md#next-executable-batches) and [T07 selected contract](tracks/t07-backend-qualification/plan.md#next-executable-batches). Source-only decision support can use existing admission statuses; a native preprocessing change needs an observed blocker and reference case first. Parent scientific tracks retain their acceptance criteria.

The published metadata and source-linked Bronze are usable independently of the optional mirror. A raw-upload transport failure does not block eligible local technical work; it also does not close the mirror's acceptance criterion. The configured official-runner workflow is the concrete remaining route. [Observed publication and blocker](../research/qualification/hf-metadata-publication-2026-11-22.md).

## Executing one ready batch

1. Read the selected specification and plan; claim only its named paths. Record the starting commit and unresolved prerequisites. The tables below refine existing tasks; they do not add parallel copies of the same milestone.
2. Before changing code, run `uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py` and retain the baseline receipt. Run the same strict command after the change. The default includes debug/release tests, docs, lint, dependency audit and coverage; `--deep` additionally scans reachable Git history and requires a complete clone. Missing tools, skipped required checks and failed checks are unresolved gates, never passes.
3. Use each plan's inputs, outputs and pass/fail criteria. A future output path below is an acceptance target, not a claim that the file or command already exists. For an unselected scientific backend, first freeze its real command in T07.02; do not fabricate a runnable analysis CLI in a plan.
4. Keep participant-level manifests and scientific results in ignored `data/silver/` or `data/gold/`. Commit only cleared metadata, synthetic fixtures, code, aggregate decisions and receipts. Record the exact data hashes separately from Git source identity.
5. Review the smallest completed increment, record actual commands/outcomes, then start its dependent. Code checks, hosted PR checks, official owner-device acceptance, source publication and scientific admission require distinct evidence. Mark a parent complete only when all of its original exit criteria pass.

### Readiness and blocking owners

| Next task | Can proceed on current evidence? | Owner and resolution of the remaining dependency |
|---|---|---|
| T00 strict command and hosted PR workflow | Yes, implementation and cloud verification | Current CI integrator; preserve failed checks and tool/version receipts |
| T01 public source reconciliation / synthetic cohort contract | Yes, bounded metadata work | T01 implementation owner; source evidence resolves identity, unknowns remain excluded from inference |
| T07 selected method contract / synthetic consumer checks | Yes, independent of patient inference | T07 owner plus the existing limma-rust LM02 owner; use exact fork commits |
| T01 analysis admission / T07 protocol freeze | Only after cohort and applicable governance requirements pass | T01 owner records the institutional determination; T07 owner freezes the selected method and N1 |
| T00 actual-device acceptance / T09 original raw mirror | External runner and authenticated transport remain unavailable | Owner's trusted runner operator; revisit when registered-device access and a source-bound job are available |
| T02, then a justified T03 or T05 | Blocked until their named data, method, device and N1 receipts pass | Receiving scientific track owner; do not substitute a code test or metadata publication |
| T04 / T06 / optional ports | Conditional, outside the initial clinical critical path | Selected track owner; activate only for the adequate data or concrete capability need in its specification |

## Linked plans

- [T00 governance and operating prerequisites](tracks/t00-governance/index.md)
- [T01 sources, rights and cohort admission](tracks/t01-sources/index.md)
- [T07 selected backend qualification](tracks/t07-backend-qualification/index.md)
- [T02 Kabuki replication](tracks/t02-kabuki/index.md)
- [T03 cross-disease comparison](tracks/t03-comparison/index.md)
- [T04 hierarchical inference](tracks/t04-hierarchical/index.md)
- [T05 multi-omics](tracks/t05-multiomics/index.md)
- [T06 toxin feasibility](tracks/t06-toxin/index.md)

## Fork dependency and fallback

The [MassDynamics-derived fork](https://github.com/edithatogo/limma-rust/blob/main/conductor/tracks.md) follows LM00 → LM01 → LM02 → LM03 for Rust methylation admission. Conditional LM04 dependency substitutions and LM05 method additions are selected only for a demonstrated need. A required extension can be scheduled before an LM03 retry; LM03 success is not its prerequisite.

The atlas can select a qualified R/Bioconductor reference route while Rust admission continues. That route still needs method, data and local-runner evidence; a named fallback is not automatically accepted. Neither a full SeSAMe-rust port nor every candidate library is on the initial critical path.

## Reprioritisation

Every analysis requires N0/N1 before, N2 after and N3 at submission. The scheduled weekly literature watch supplements those gates. Reorder at explicit decision points when a dataset is unusable, a new paper changes novelty or a simpler dependency removes work. Preserve frozen analyses and historical results.

Tracks are work packages, not paper allocations. The default clinical bundle is E0 + E2 + E3, with E1 and backend checks in support. E4–E6 extend that paper or form one later coherent study only when the evidence warrants it.
