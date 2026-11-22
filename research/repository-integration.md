# Repository boundaries and executable integration

Updated 23 November 2026. Ponytail full review retains the two existing project repositories and the central standards repository. Their responsibilities differ, and the immediate integration need is a small, versioned file exchange. The numerical implementation has an existing independent oracle and its own downstream users; atlas has separate source rights, cohort, preprocessing and publication responsibilities.

## Ownership and documentation

| Repository | Owns | Authoritative entry point |
|---|---|---|
| `edithatogo/repository-standards` | Shared policy and the pinned privacy scanner | The inspected central revisions in [CI reconciliation](ci-plan.md#central-standards-and-template-reconciliation) |
| `edithatogo/limma-rust` | Numerical core, named numerical API, synthetic exporter, independent numerical references and supported-method limits | `docs/named-consumer-v1.md` at the exact revision in [the integration pin](contracts/limma-named-v1.json) |
| `edithatogo/rare-omics-atlas` | Source catalogue, sample declarations, eligibility, preprocessing qualification, received-file checks, provenance, downstream analysis and publication | This boundary document, [T01](../conductor/tracks/t01-sources/index.md) and [T07](../conductor/tracks/t07-backend-qualification/index.md) |

Keep the numerical specification in limma and link it from atlas. Keep the receiving evidence and source-admission decisions in atlas. The integration pin supplies the source identity; the generated receipt supplies the actual execution outcome. Neither README should maintain a competing numerical contract or a mutable count of “current” tests.

No new repository, submodule, shared hook package, workflow service or general plugin framework is needed for this increment. Atlas invokes a separately checked-out executable. Its catalogue does not gain a dependency on the GPL numerical crate or a copy of its numerical routines. This boundary does not itself settle distribution licensing: limma retains its existing licence and the atlas code licence remains unresolved.

## Bounded numerical exchange

The selected synthetic contract is `limma-named-contrasts-v1`: named float64 matrices, unweighted least squares, default nonrobust/nontrend eBayes, complete per-contrast BH families, ordinary and moderated SE and 95% intervals. Per-feature non-estimability is preserved. Unsupported domains must reject. The canonical limma document specifies the exact fields, ordering and tolerances.

Atlas's [receiver](../scripts/qualify_limma.py) uses the existing Python development environment and standard library. It does not fit a model, implement empirical Bayes or recompute BH. It runs the actual Rust example, reads its CSV and JSON files, and compares against the committed independent R tables. A small Python receiver avoids a new catalogue CSV/runtime dependency for a qualification-only operation.

The mandatory gate:

1. Reads a full immutable limma commit SHA and the fixed repository URL from the committed pin.
2. Obtains or checks a clean checkout at that commit. A different origin, floating revision, changed source, untracked source or hidden index entry fails.
3. Runs the exporter on the independent `complete` and `missing` fixtures. A second missing-fixture exchange checks transport of the methylation-scale declaration; it does not turn that fixture into methylation evidence.
4. Verifies exact schema, all four ordered axes, complete contrast-major rows, declared units/method, warnings and non-estimability. Duplicate JSON keys and malformed CSV fail.
5. Compares every received numerical field, including NaNs/infinities, against the existing independent reference with unchanged field-specific tolerances.
6. Records source and file hashes, actual commands, exit status, comparison counts and retained limits under `artifacts/verification/`. A failed or interrupted invocation cannot reuse a prior success.

The R generator's missing-case eBayes scalar table uses exact one-based row numbers because those vectors lack row names. The receiving adapter maps only that pinned reference file to original input feature order, as proved by the unchanged generator's direct vector binding. All other relevant reference tables and every received result retain strict named alignment. The receipt records this convention and the reference-generator hash; there is no generic positional fallback.

The gate is part of the ordinary strict command:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

For an isolated diagnosis of the same receiver:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/qualify_limma.py \
  --output artifacts/verification/limma-receiving
```

An existing checkout can be supplied with `--checkout /absolute/path/to/limma-rust`; it must match the pin exactly and be clean. Otherwise a revision-specific checkout is created in ignored `artifacts/integration/`. Export directories are new for each invocation, while previous evidence remains available. The strict CI runner needs normal public GitHub/Cargo registry access, with no write token or patient data.

## Change and integration order

| Batch | Inputs and executable work | Exit and next consumer |
|---|---|---|
| 1. Local enforcement | Install the pinned tools and native hooks in each clone; run the current strict baseline. | Failures are repaired before publishing new source. Hooks scan the actual staged candidate and run the same verifier. |
| 2a. Source/sample boundary | Review official source metadata, reconcile public assay accessions, validate synthetic declarations and run the real held manifest. | T01 records structural results and unresolved evidence. This may run alongside 2b. |
| 2b. Numerical boundary | Implement the smallest named API/exporter in limma; compare against the existing independent R oracle; review rejection paths. | Local strict checks and the actual pre-commit hook pass before a local commit is published. |
| 3. Producer publication and CI | Publish the locally verified Git tree to a limma PR and start its applicable hosted checks. | The real immutable commit unblocks receiving tests while producer CI runs. Producer integration still waits for its checks. Do not invent the future SHA or track `main`. |
| 4. Receiving integration | Update the atlas pin, run the actual exporter/receiver and every strict local gate, then commit through the hook. | Atlas publishes its own tested tree and receives its own hosted checks. Final integration requires both the accepted producer and receiver; a producer pass alone cannot satisfy this gate. |
| 5. Bounded closure | Link exact local/provider receipts, review the declared scope and archive only the completed bounded increments. | Parent scientific, historical identity, licence, raw-mirror and actual-device gates retain their own status. |
| 6. Next scientific dependency | Qualify the selected preprocessing/QC stage and required annotation assets; resolve actual participant independence and applicable governance. | Only the resulting admission and frozen N1 protocol permit disease-conditioned inference. |

When updating limma later, repeat producer qualification first, then update the atlas pin in a separate receiving change. A failed receiving check leaves the previously qualified pin in use. Changes to field meaning, scale, ordering, missingness or method require an explicitly versioned contract and new acceptance evidence. Storage chunking cannot split global moderation or a complete BH family.

## Native pre-commit enforcement

The installed `.githooks/pre-commit` calls the repo's own small helper and strict verifier. The helper checks the central scanner checkout at `b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4` and isolated Python/Gitleaks tooling. It refuses an existing conflicting hook path or executable legacy hook instead of overwriting it.

The guard captures the actual Git candidate tree, including the alternate index used by `git commit -a` and `git commit --only`. Because the central scanner removes inherited Git environment variables, the helper gives it a disposable Git index containing that exact candidate. It rejects unstaged tracked changes, untracked candidate files and hidden source changes, then runs strict verification with Git-local variables isolated. It checks the candidate, HEAD and working tree again before allowing the commit.

Follow the installation command in [the CI contract](ci-plan.md#install-the-native-pre-commit-hook). The three machine-specific paths are local Git configuration, never committed. Native hooks enforce this clone's normal commit path; hosted checks remain necessary for API/web changes and other clones. Required server-side checks are a separate administrator setting and are not implied by installing a local hook.

## Evidence boundary

Synthetic receiving success establishes this file/API contract at the pinned source. It does not establish production ingestion, array preprocessing, molecular diagnosis, independent participants, scientific findings, raw-data mirroring or official owner-device execution. Source/sample validation always reports `analysis_admitted: false`; a complete declaration can be ready for review without being accepted for inference.
