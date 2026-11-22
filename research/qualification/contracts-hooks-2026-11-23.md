# Pinned numerical exchange and strict local integration

Reviewed **23 November 2026, Australia/Brisbane**. Instrument timestamps below are UTC on 22 November. **The bounded local code and synthetic receiving increment passed.** Scientific admission, production preprocessing and actual owner-device qualification remain separate.

The [machine-readable record](contracts-hooks-2026-11-23.json) retains every strict command/status, safe log hashes, selected code hashes, actual input/reference/output hashes, the producer source mapping and preserved failed attempts. [Repository integration](../repository-integration.md) defines responsibilities and upgrade order; [the pin](../contracts/limma-named-v1.json) selects the source.

## Exact source and execution

| Evidence | Observed identity or outcome |
|---|---|
| Atlas starting commit and coverage base | `6bd452abde7aff9fbf2969814dca39a0f182d18a` |
| Tested atlas source snapshot SHA-256 | `0577334a5275ac1ca5e2da8f44b9f0935424ba996f58bf2231d93d4b4cfb2230` |
| Limma immutable receiving pin | [`c08c53943a7acb9c6a1152df8d79e27cffe7199b`](https://github.com/edithatogo/limma-rust/commit/c08c53943a7acb9c6a1152df8d79e27cffe7199b) |
| Limma actual hook-checked local commit | `23caa34226f3671f452562bfbfde0393be50e845` |
| Verified identical local/published limma Git tree | `5b6804e446a037ffdcd18efbd816c74f3b1accde` |
| Corrected full run | 14:56:27–14:56:55 UTC; 28.318 seconds; **34/34 checks passed** |
| Debug, release and instrumented Rust tests | **20 passed in each profile; zero failed or ignored** |
| Python tests | **38 harness + 41 publisher = 79 passed** |
| Local branch-aware changed-code coverage | **499/513 lines, 97.27%; unchanged requirement 90%** |
| Original complete runtime receipt SHA-256 | `e2fd84d913862ffdb9b309409fa7b0d8f1eed0b2024c6878668deacfb8475651` |
| Original receiving receipt SHA-256 | `710cf1eb0201a6262100b55fe135ff3005ec40682782099d951d1303784ad8f5` |

The observed full command was:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py \
  --deep --output artifacts/verification/contracts-hooks-corrected
```

It ran pinned tool/version checks, Rust debug/release/docs/Clippy, strict Python types/lint/tests, actual receiving execution under coverage, native coverage and the unchanged patch threshold, advisory audits/inventories, current-source and reachable-history secret scans, workflow/document/JSON/dependency checks. The machine-readable record gives exact arguments and exit codes. Missing services, tools, source or outputs cannot become success.

The full suite tested the source snapshot above. Final evidence/status/archive edits followed it; the actual publishing commit must additionally pass the installed hook for the complete staged tree. Its local/remote commit mapping and hosted outcome belong to the final PR. A local strict run does not assert a hosted provider result.

## Actual producer-to-receiver exchange

Atlas obtained a clean checkout at the real published pin and ran the actual Rust `export_named` example. It received files, rather than calling an in-process numerical object or replacing the oracle.

| Synthetic case / scale declaration | Rows received | Numerical comparisons | Nonfinite fields preserved |
|---|---:|---:|---:|
| Complete / log2 expression | 192 | 2,304 | 0 |
| Missing / log2 expression | 192 | 2,304 | 27 |
| Missing / log2 methylation odds, transport check only | 192 | 2,304 | 27 |
| **Total executed exchanges** | **576** | **6,912** | **54** |

Each case retains all 96 features and both contrasts, in the prescribed order. The receiver verifies all four named axes, complete family size, exact typed schema/method/scale, warning expectations, both SE definitions, raw/BH p-values, df, intervals and non-estimability. Every expected NaN/infinity is checked rather than omitted. All comparisons meet the unchanged field-specific reference tolerances. The repeated missing case checks scale transport and is not a third independent dataset.

The references are the previously independently generated R 4.5.0 / limma 3.68.5 / statmod 1.5.2 outputs. **R was not rerun in this increment.** The missing default eBayes scalar file alone has the generator's exact one-based row IDs. Inspection of the unchanged writer proves original input order, so the receiver explicitly maps that one pinned file. Other reference tables and all received results stay strictly named. No reference or tolerance was rewritten.

The canonical [numerical contract](https://github.com/edithatogo/limma-rust/blob/c08c53943a7acb9c6a1152df8d79e27cffe7199b/docs/named-consumer-v1.md) remains in limma. Atlas owns receiving/provenance; central standards remain the policy authority. The catalogue does not link the GPL core, and this design does not resolve atlas's outstanding licence selection.

## Failure handling and review

The receiver's first test failed before implementation because the module did not exist. Its first actual development exchange stopped on the R scalar row convention described above; verification of the original generator justified the narrow mapping.

Independent review found JSON's boolean/numeric equality ambiguity and a possible receipt/input overwrite. Exact typed metadata comparison and pre-write path/symlink/hardlink checks now reject those cases. Eleven receiver regressions cover these failures alongside bad pins, dirty/hidden sources, malformed metadata/CSV, reordered/missing rows, altered uncertainty and replaced nonfinite values.

The first combined run failed only because an existing coverage-isolation test fixture did not emit the newly mandatory `limma-contract.json` artifact. It correctly prevented success. The fixture was updated with that one generated-artifact entry; no production gate changed. The failed receipt and logs remain in `artifacts/verification/contracts-hooks/`, and their identities are recorded in the durable JSON. The corrected full run used a new output directory.

Native hooks are installed in both working clones, and [their real scanner canary proof](native-hooks-2026-11-23.md) is separate from the full project commit. The producer's actual local commit passed staged privacy and every strict gate: zero Gitleaks findings, zero blocking Presidio findings and two advisory detections on recorded durations. No scanner exception was added.

The named producer API is covered by native Rust reports. cargo-llvm-cov 0.8.7 excludes example files by default; the exporter's two executable tests are mandatory in all producer profiles, but no example source-line coverage claim is made. Native reports and thresholds are preserved.

## Bounded closure and next executable work

This evidence supports archival of T01a's structural code increment and T07a's pinned synthetic exchange, with their own source/review records. Parent T01/T07 remain open. The [source receipt](t01-sample-contract-2026-11-22.md) reconciles **341 public assay records** and the actual declaration run holds every one; independent participant count and scientific admission remain unresolved.

Next qualify the selected preprocessing/QC route and required manifest/mask/build/annotation assets on unrelated technical fixtures; resolve participant independence, molecular eligibility and applicable institutional classification; then freeze analysis-specific N1 before disease-conditioned qualification or inference. Actual owner-device runs require the configured official runner on those devices. Optional raw mirroring, ports or model extensions are not added to this critical path.
