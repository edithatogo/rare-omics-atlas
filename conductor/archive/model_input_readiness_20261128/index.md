# T06 — model-input and source feasibility

**Status:** accepted and archived for the bounded public-source/documentation
increment in [PR #48](https://github.com/edithatogo/rare-venomics/pull/48), after
the exact candidate and receiving-main checks below. The T05/T06 scientific
parents remain open; quantitative genotype-by-venom execution is held.

## Completed scope

The [T06 Batch A assessment](../../tracks/t06-toxin/feasibility.md) reconciles
GSE261305's assay/clinical/genetic units, PXD003403's bottom-up identity and
related MSV000079351/PXD004160 deposit, measured versus missing quantities and
existing complement-model assumptions. The inspected pair does not establish
the linked genotype, active exposure, kinetics and independent response needed
for a quantitative model. The [model selection record](../../../research/model-selection-2026-11-28.md)
also receives the CpGPT audit: all three target cohorts have unknown checkpoint
split membership, not zero overlap.

The [receipt](../../../research/qualification/model-input-readiness-2026-11-28.json)
contains 23 public metadata/document response hashes, exact source/model
revisions, declared inventories, retrieval limits and extraction steps. The
integrator independently reproduced nine source-response hashes, three CpGPT
repository inventories and all seven PRIDE file/category/size entries. Metadata
hashes do not stand for molecular payload hashes; mutable endpoints are dated
snapshots. Molecular/clinical payloads, checkpoints and inference were not
acquired or executed. Requester-pays S3 was not contacted.

## Observed verification

The baseline was [Strict CI 46030138762](https://github.com/edithatogo/rare-venomics/actions/runs/46030138762)
on exact base `e3e83d95e46dec61dfae4f5057c1dd65eb33409f`. It passed. Independent
content review accepted all six changed files and a separate source sanity
review checked the human/venom attribution. [Review record](https://github.com/edithatogo/rare-venomics/pull/48#issuecomment-7229720719).
The source/audit work used Python standard-library HTTP retrieval, JSON,
SHA-256 and aggregate arithmetic; no new script/runtime was added. Local checks
confirmed all relative links, 23 unique source identifiers, aggregate totals,
null CpGPT membership fields and exact equality of all six reviewed Git blobs.

The hosted native commit invoked the installed full strict hook, using:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

| Boundary | Exact observed receipt |
|---|---|
| Staged implementation | Head `538a2e8750958c8ed0cbdd6fdda2114a1776a884`; base above; candidate `3574a6ef0cb8a8dbf6229a250456136adde28ddc`; tree `08370858a4c573eba3487d65ae322ac1a1567dc5`. API commit was staging only. |
| Native hook | Actual replay commit `899c3e4cee7cc99e0878520a32639366c1ab26d3`; hook passed and reproduced the exact candidate tree. |
| PR CI/provider | [Strict CI 46079421013](https://github.com/edithatogo/rare-venomics/actions/runs/46079421013): 34/34 strict checks passed in 249.152 seconds; privacy/secrets, dependency review and Codecov/patch passed. Inventory and coverage publication succeeded. |
| PR artifact | Artifact 15236851839, 250,688 bytes, SHA-256 `e11652c29a970b3377303003766a1dddd2f287753368e921571b2535972f67ff`. Download hash, byte length, ZIP CRC, actual hook log/JSON and all strict statuses verified. The receipt names the base plus exactly six staged paths; the hook binds these to the candidate tree. |
| Receiving main | Merged revision `77bf0a410356dd3cd739823d435d11aa252d1a38`, exact tested tree above. [Strict CI 46080722309](https://github.com/edithatogo/rare-venomics/actions/runs/46080722309) passed 34/34 strict checks in 186.911 seconds, plus privacy, inventory and coverage publication. PR-only steps were correctly skipped; the full strict verifier ran. Receipt is clean with zero dirty paths and completed 2026-11-27 23:15:48 UTC (28 November Australia/Brisbane). |
| Receiving artifact | Artifact 15237012647, 248,717 bytes, SHA-256 `2071fc4ff13c0db982fc17e7526eb948588c4463f71fcdcc49c425fef2705712`. Integrator verified received bytes, ZIP CRC and exact merged-revision receipt: all 34 checks passed with zero exit status and no failed checks. |
| Retained source receipt | SHA-256 `edcf68679e5e6511988b051283767a081d40122d7ffe726764e0250f9f5a59ef`. |
| PR #48 feasibility | SHA-256 `d1da2b417b533ee91e9b49bdf0ecc7e61ae2eb1261d38ed7df862d1a512a4355` at the accepted implementation revision. |

The independent artifact reviewer checked all 52 PR ZIP members and the actual
hook/strict logs, then independently compared the complete base/candidate Git
trees. Precisely four modified and two added files matched the six reviewed
blob hashes and byte lengths. [Premerge qualification](https://github.com/edithatogo/rare-venomics/pull/48#issuecomment-7229894524)
records the accepted review. Code coverage correctly reported no executable
patch lines for this documentation/metadata change.

The [receiving acknowledgement](https://github.com/edithatogo/rare-venomics/pull/48#issuecomment-7230028589)
records acceptance of the exact merged implementation.

## Reuse and limits

This completes the planned source/parameter mapping output, not the original
scientific tasks. Reuse the existing Conductor tracks, source-linked Bronze
and optional upstream methods. No solver, adapter, port, model framework or new
dependency is justified by these inputs. The small published Julia complement
model is a conditional reference; its runtime and scientific transfer remain
unqualified. CpGPT requires a versioned checkpoint-linked membership artifact
before a claim of independent evaluation.

This is N0/dependency input, not a complete scientific novelty assessment, N1
freeze, quantitative benchmark, clinical prediction or manuscript contribution.
Source-specific research/redistribution, institutional and actual-device gates
remain separate. No animal experimental programme or toxin optimisation was
introduced. T02/V01 priorities and the separate T01/T07 drafts #43/#44 were
preserved; scientific issues remain open.

The prior model-assessment increment was also linked from the archive README
and removed from the active increment list. This source assessment is now
removed from that list and linked from the same archive index. Archive-only
integration has its own exact-current-base checks and final receiving record
in PR #48's linked archive discussion; those receipts do not alter scientific
admission.
