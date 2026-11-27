# T05 — genomic model assessment and source-overlap audit

**Status:** accepted and archived for the bounded documentation/public-metadata
scope of [PR #46](https://github.com/edithatogo/rare-venomics/pull/46), after the
exact candidate and receiving-main evidence below. The [T05 parent](../../tracks/t05-multiomics/index.md)
and [T06 parent](../../tracks/t06-toxin/index.md) remain planned.

## Scope and result

The owner requested incorporation of the AlphaGenome 2 recommendation and
consideration of more useful alternatives. The [selection/evaluation record](../../../research/model-selection-2026-11-28.md)
is the reusable decision: retain AG2 as a conditional human regulatory arm;
prefer task-matched methylation, coding/splice or measured-cell methods when
their input, source and validation requirements are met. Defer every model
adapter until a real consumer and independent reference are qualified.
No model runtime, workflow, weights, molecular values or scientific inference
was added. Existing T01/T07 work and T02/V01 priorities are preserved.

The [aggregate audit](../../../research/qualification/model-source-overlap-2026-11-28.json)
processed public metadata from MethylGPT v1.1.2 at
`7b137f593caa941ee5b12b803ff98759c1d5c90c` and the catalogue at
`098a330517210d90a88512de12490a9f193764d4`. All 235 GSE97362 and 44 GSE116300
catalogued assay IDs match the declared upstream test split; zero exact IDs
match train/development. The 62 GSE218186 catalogue IDs are absent from that
table. These are assay/profile counts, not independent admitted participants.
Upstream test exposure is not proof of training contamination; absence is not
proof of biological independence.

## Observed acceptance evidence

| Boundary | Actual receipt |
|---|---|
| Independent content/source review | [Exact-file review and hashes](https://github.com/edithatogo/rare-venomics/pull/46#issuecomment-7222019496); no remaining content/scope blocker. Separate source and artifact reviews were completed. |
| PR qualification | [Strict CI 46024443964](https://github.com/edithatogo/rare-venomics/actions/runs/46024443964) passed all 34 strict checks in 181.632 seconds, privacy/secrets, dependency review and Codecov/patch; coverage upload succeeded. [Qualification record](https://github.com/edithatogo/rare-venomics/pull/46#issuecomment-7222242655). |
| Native hook | Base `098a330517210d90a88512de12490a9f193764d4`; implementation head `5b11a3ed89b59589cf23814300e887b8fd2739f2`; merge candidate `22c2e37757caf19681ee3798ebb6100932e0dee4`; replay commit `30796d0483cae53c07829b8d0525f4f4c532774a`; hook passed on tree `4d92cbf75c3e4ea899e05cb847608e5d9667759d`. |
| PR artifact integrity | Artifact 15211952184, 250,595 bytes, SHA-256 `86f5057b5e42e5df8e44db7e9acc188147c2927fccaad6d245207cc20b582d94`. Downloaded ZIP hash, CRC, actual hook JSON/log and strict receipt independently checked. The strict receipt's base revision plus exactly five staged paths is bound to the candidate tree by the hook receipt. |
| Receiving main | Merged revision `bd62bf656fa43822c26183cdd278370a3f3a2fd9` has exactly the tested tree above. [Strict CI 46026284535](https://github.com/edithatogo/rare-venomics/actions/runs/46026284535) succeeded: all 34 strict checks, privacy, inventory and coverage publication passed; PR-only steps were correctly skipped. The clean receipt names the merged revision, has zero dirty paths and completed at 2026-11-27 15:45:44 UTC (28 November in Australia/Brisbane), after 260.662 seconds of strict verification. |
| Receiving artifact integrity | Artifact 15213140602, 248,699 bytes, SHA-256 `331fc2a16942e6503a9c02cc07e8f1bf343075a318ddd18bbf849e0f2a66d9dd`. The integrator downloaded it and verified byte count, hash, ZIP CRC and the clean exact-revision receipt with 34 successful zero-exit checks. |
| Retained aggregate audit | SHA-256 `d3d2c2cec89cca42da04003d299d5752ebaac8525c2030b9f3ca0b8805f64130` for the committed metadata receipt; source-level digests and reproduction method are inside it. |

The review compared the existing files with the pinned base, checked model
claims against primary sources, and independently reproduced both input
hashes, byte counts, the corpus Git blob ID, the full 169,120-row split census
and every cohort join. Original compressed split SHA-256:
`07581393c2dbe3870c4dc77d580fd1a3ec939393678c7198c82d0e7a6106670b`;
catalogue SHA-256:
`6e7680a5a66fd35380b3cf7a976e8aefb365fd69102779fb5ddf07b4289152fb`.
The receipt retains the successful reproduction method and original connector
gzip-format limitation. No profile IDs or source rows were exported.

## Reuse, completion and remaining limits

Reuse existing T05/T06 ownership, source/hash conventions, optional specialist
clients and the existing Bronze/Silver/Gold layout. Extend only the decision
record and track receiving notes. Defer speculative adapters, model frameworks,
GPU installations and new scientific milestones.

This completed increment is N0/dependency input, not a frozen N1, executed
benchmark, clinical result or manuscript-level scientific contribution.
MethylGPT needs a qualified independent evaluation and biological-overlap review;
other candidates need exact artifact/terms, eligible data and an actual question.
AG2 output restrictions remain relevant to learned features and redistribution.
Every selected model still requires its applicable numerical, scientific,
institutional and official-device evidence. None supplies toxin reaction rates,
clinical susceptibility or antivenom efficacy merely from a prediction.

One implementation batch produced the assessment and metadata audit; an
independent review/verification batch qualified those exact bytes. This archive
reconciles the completed bounded scope without completing either parent track
or closing scientific issues #15/#30. The archive reconciliation requires its
own current-base checks; its receiving record is linked from the discussion
of PR #46.

