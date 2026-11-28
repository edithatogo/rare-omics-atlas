# T05 — aggregate multimodal pairing readiness

**Status:** bounded source-readiness assessment accepted in [PR #50](https://github.com/edithatogo/rare-venomics/pull/50), with receiving-main qualification. This archive does not complete T05.01–.05 or admit any cohort.

## Completed evidence

The [immutable implementation receipt](../../tracks/t05-multiomics/pairing-readiness-2026-11-28.json) (Git blob `640927bf9f07103ed91dda4f16eb2357f2e2792c`) reconciles 125 distinct catalogue assay memberships across GSE191276 (7), GSE191274 (25), GSE152427 (57) and GSE152421 (36), with 16 historical request receipts. Pinned catalogue assay, dataset and request blob identifiers are preserved in that receipt. Historical hashes were inspected, not recomputed from original source payloads. Distinct GSM sets do not establish person independence or paired specimens.

The [subsequent file-listing replay](https://github.com/edithatogo/rare-venomics/pull/50#issuecomment-7231331348) retrieved pinned files.jsonl blob `d9bf7de5f603dd88357e0a2011c7f6337daf223c` by Git blob after the raw/range routes failed: 4,514 JSONL rows, 21 distinct target URL listings (7 series and 14 assay-level), zero marked download-verified. This supersedes the original catalogue retrieval limitation only; no source molecular payloads were fetched. The ADNP [additional source check](https://github.com/edithatogo/rare-venomics/pull/50#issuecomment-7231435405) records the 36 SRA experiments and 36 BioSample links without claiming paired individuals. The original study counts, anonymous Sotos control/pooled-parent limits, family dependence, diagnosis/sampling context and unresolved ADNP supplemental access are retained. Verified person/specimen/time pairing remains unknown; do not infer from order, labels or demographics. The historical receipt is unchanged.

## Observed verification

| Boundary | Exact receipt |
|---|---|
| Baseline | Base `f856b18c5376f960c41144fdc29c2d158e40f82c`; [receiving Strict CI 46082798313](https://github.com/edithatogo/rare-venomics/actions/runs/46082798313) passed. |
| Candidate | Head `636980b92af587f1f3cef080d6f72b9fcfd5dfbd`; merge candidate `7aa0fa153291111f691f46a5944034e4f5d465d3`; tree `bf3b6f4ee3b31b1b358f7cad343e14783c445099`. |
| Native hook | Actual replay commit `1e9cb21fed311ef1c09d926d2b8d3cedf74d0ec6`; [Strict CI 46090204662](https://github.com/edithatogo/rare-venomics/actions/runs/46090204662) succeeded, 34 strict checks, privacy/secrets, dependency and Codecov/patch passed. |
| Candidate artifact | 15241590855, 250,634 bytes, SHA-256 `3c29c6d1ab6f8b7886a65c0fa69dcd0bd1ba463ad82e0a3b7161d909d35f0a25`; actual hook receipt, 52 ZIP CRCs and all strict logs verified; 238.475 seconds. [Qualification record](https://github.com/edithatogo/rare-venomics/pull/50#issuecomment-7231410578). |
| Independent review | [Codex review](https://github.com/edithatogo/rare-venomics/pull/50#issuecomment-7231434513), completed on the exact head, no findings or unresolved threads. |
| Merged implementation | `b874d8cca79d8196d26ad1a515070048c2afedb8`; live tree exactly matches candidate above. |
| Receiving main | [Strict CI 46120039622](https://github.com/edithatogo/rare-venomics/actions/runs/46120039622) passed 34/34 checks in 175.318 seconds; privacy/secrets, inventory, coverage passed, PR-only steps skipped. Full verifier ran. |
| Receiving artifact | 15252969785, 248,693 bytes, SHA-256 `9bfc39c2480bdcaaa3f57e6e04aea9a555518900f163f13b75d85625dddbbbef`; all 50 ZIP CRCs, exact source revision, all 34 zero-exit checks/logs, no dirty paths or failed checks verified; completed 2026-11-28 07:18:53 UTC. [Final receiving record](https://github.com/edithatogo/rare-venomics/pull/50#issuecomment-7236222181). |

The full native strict command was `uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep`. Source work reused the existing JSONL catalogue, exact accession joins, aggregate arithmetic and source references; no new code or dependency. Archive-only integration requires its own actual native-hook/current-base checks, independent review and receiving-main receipt.

## Disposition

This is evidence for source-readiness and future N0, not a new disease finding, pairing/rights approval, model benchmark or N1 freeze. The existing T01 and T07 owners receive biological provenance and selected-method evidence; applicable institutional and actual approved-device gates remain. T05 stays conditional on a justified distinct contribution and admitted modalities; no automatic individual-level analysis. Preserve T02 as the first clinical priority, #43/#44 ownership and the separate V01 stream. No new model adapter, framework, acquisition service or independent scientific milestone. No branch deletion claimed.
