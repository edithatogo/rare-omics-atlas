# V01 — publication implementation and preflight correction

**Status:** accepted and archived for the bounded implementation/preflight scope of [PR #42](https://github.com/edithatogo/rare-venomics/pull/42). Actual metadata publication is **blocked externally**. The [V01 parent](../../tracks/v01-toxinology/index.md), its source-intake and publication milestones, and [issue #30](https://github.com/edithatogo/rare-venomics/issues/30) remain open.

## Scope and acceptance

The original automatic publication [45892080466](https://github.com/edithatogo/rare-venomics/actions/runs/45892080466) failed 17 of 47 publisher tests because its shallow checkout omitted the historical publisher object. PR #42 changed the automatic and manual publication checkouts to full history and added an explicit historical-object preflight in the automatic lane. Its declared exit required exact-base qualification, receiving-main CI and observation of the corrected publication attempt; it did not assert successful credentials or upload.

The release manifest, four reviewed metadata/aggregate objects, publisher code and pins, test/coverage/privacy gates, activation predicate and no-overwrite policy were preserved. The exact manifest remains SHA-256 `4e0fcc255351e5b557d731916413d55e8dd5bb61789733c1c1cb99ecb97db7b6`.

## Observed evidence

| Boundary | Actual receipt |
|---|---|
| Exact-base PR qualification | [Strict CI 45897063620](https://github.com/edithatogo/rare-venomics/actions/runs/45897063620) passed strict verification, native hook, privacy, dependency review and Codecov. ZIP artifact 15155086152 SHA-256 `68561cc05651dbfbb087de15675e2d51d357f2852604ee5eaad7bac98762a557` was independently downloaded and checked. |
| Native hook and receiving tree | Base `b178fc753d5ff1f662662ba6541ff88fad88d2a7`; candidate `e9996941d372f1346bdca6476b259f7c3d3cb250`; replay commit `9d7a1b9f59193e79ae03349a2a59549d6ea4f284`; hook passed. Tested tree `2a09917c443c8e31f9eb113e5026b47ce935ca24` equals merged tree at `e32e8917aed52e72828cb6cb1fa505da67aef516`. |
| Receiving main | [Strict CI 45913236312](https://github.com/edithatogo/rare-venomics/actions/runs/45913236312) completed successfully on that exact merged revision at 2026-11-26 23:57:59 UTC (27 November in Australia/Brisbane). Strict verification, inventory, coverage publication and privacy passed; PR-only steps were correctly skipped. |
| Corrected publication preflight | [Activated run 45913968090](https://github.com/edithatogo/rare-venomics/actions/runs/45913968090), job 140228652175: pinned manifest and full-history checks passed; all 47 publisher tests passed in 1.002 seconds; dry-run returned `dry_run_verified` with six locally verified objects and zero remote objects. |
| Credential boundary | The upload shell found `HF_TOKEN` unavailable or empty and exited before invoking the publisher upload command. No authentication attempt, upload receipt or immutable Hub publication revision exists from this run. This is distinct from an invalid-token rejection. |
| Artifact integrity | Artifact 15160944809 is 881 bytes; independently computed ZIP SHA-256 `a2c6c7497c1e3bcad0f8f2604626e7e8097930c8cbbabe2e7f9d7a1c984a489c` matches GitHub, and ZIP CRC passed. Its sole member is `v01-public-dry-run.json`, 1,905 bytes, SHA-256 `df2584d7d4c677cf378b46dc0bcb5111bcd0f229a22cd0c46a3c9b7408909170`. The [unaltered receipt](../../../research/qualification/v01-publication-preflight-2026-11-27.json) is preserved beyond artifact retention. |
| Independent remote observation | Read-only Hub inspection on 27 November still reported `silver/toxinology/2026-11-25` absent in `edithatogo/rare-omics-atlas`. No publication is claimed. |

The six dry-run payloads are the four metadata/aggregate objects plus the generated release manifest and provenance. Their exact paths, byte counts and hashes are in the preserved receipt. The provenance is bound to source revision `e32e8917aed52e72828cb6cb1fa505da67aef516`; the historical GitHub alias in the frozen release remains intentional.

## Review and reuse decision

Independent read-only review on 27 November checked the declared PR scope, source-bound publication policy, archive criteria and milestone separation. The verified preflight resolves the checkout defect; the observed missing credential does not complete publication. Reuse the existing T09 publisher and source/hash conventions for this V01 consumer. No new publisher, runtime dependency, credential workaround or shared framework is required. All 33 non-V01 milestone objects remain unchanged.

The original shallow-checkout failure remains failed. The intervening [run 45898336751](https://github.com/edithatogo/rare-venomics/actions/runs/45898336751) was an intentional activation no-op, not a transfer receipt. The corrected activated run also remains failed at its credential boundary. A later documentation-only merge may produce another no-op; it cannot resolve this hold.

## Concrete remaining action

The repository credential operator must securely configure or make available a fine-grained Hugging Face token with write permission limited to the existing dataset `edithatogo/rare-omics-atlas`, as the repository Actions secret named `HF_TOKEN`. Use the provider settings directly; do not place the token in chat, logs or repository files. See [GitHub repository-secret instructions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) and [Hugging Face token scopes](https://huggingface.co/docs/hub/security-tokens).

Then retry the failed job in [publication run 45913968090](https://github.com/edithatogo/rare-venomics/actions/runs/45913968090), retaining its original activated source revision. Require an actual upload receipt, immutable Hub commit and matching byte counts/SHA-256 for all six objects, including provenance. Preserve the parent-commit concurrency and no-overwrite checks. An existing partial or differing release is a conflict to investigate, not permission to overwrite.

This archived increment supplies technical preflight evidence only. Original eAtlas clinical records, AIHW workbook acquisition, clinical source QC, institution, official owner device and N1 admission remain at their existing holds. No clinical analysis or new scientific finding resulted; the metadata receipt supports reproducibility, not a manuscript claim of patient-level evidence or independent cohorts. The separate T09 raw-mirror task and independent PRs #43/#44 are outside this increment.
