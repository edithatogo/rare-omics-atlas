# Final Hub metadata publication — independent Ponytail review

Reviewed 22 November 2026 by a separate agent from the publication/helper authors.

**Decision: accept the completed metadata publication, canonical estate addition and corrected verification helper. Full T09 remains open.** No material finding remains in this bounded scope. This is not acceptance of the pending raw mirror, a GitHub Actions execution, owner-device qualification or a scientific analysis.

## Accepted publication and source bindings

The final [official API receipt](hf-metadata-publication-2026-11-22.json) verifies **14 selected objects, totalling 2,304,170 bytes**, at the public immutable Hub revision [`3f1cb8e64d8e31e7e40773441ba6266714569d05`](https://huggingface.co/datasets/edithatogo/rare-omics-atlas/tree/3f1cb8e64d8e31e7e40773441ba6266714569d05). These are the 13 objects in the [staging manifest](../releases/2026-11-22/hub-staging/staging-publication-manifest.json), plus that manifest itself. The prospective full release instead selects 13 metadata objects, three raw archives and two generated records: **18 selected objects**. It has not been published or verified as a complete release.

I independently compared the local sizes, SHA-256 values and Git blob identities for every staging object and its manifest with the final remote-object receipt. All 14 match. The server observations are Git blob SHA-1 identities; the receipt separately records locally calculated SHA-256 values. This review does not misrepresent those observations as remote SHA-256 downloads.

Ten selected metadata files are byte-identical to their recorded Git blobs at source commit `8cfc85110911a2991301b358e4510e28026d13b8`; I checked them against `git show`. The dataset card, Bronze notice and licence notice are three separately hashed staging notices, with no false claim that their revised bytes came from that earlier commit. The staging manifest's own hash and its link to the corrected prospective full manifest also match.

The [card-validation correction](../releases/2026-11-22/hub-staging/card-validation-fix-receipt.json) accurately distinguishes the live UI rejection from the successful publication. Against the immutable baseline, the canonical full-release card changes only the two stated frontmatter values: the custom licence slug and its HTTPS notice link. All four recorded post-correction card/manifest hashes match. The recorded prospective 18-object dry-run asserts no source revision and makes no remote upload claim.

The [publication account](hf-metadata-publication-2026-11-22.md), staging notices and current Conductor state consistently distinguish public metadata, source-linked Bronze and local archive integrity from biological preprocessing or inference. They retain source-specific conditions and attribution, without inventing universal redistribution rights or an institutional HREC/IRB determination. Accessions, GSM memberships and IDAT pairs are not presented as independent participants or affected cases.

## Independent estate check

Using the official Hub API in read-only mode, I checked `catalog.json` at both immutable estate revisions:

| Revision | Bytes | Local SHA-256 matched to the remote Git blob |
|---|---:|---|
| `f82a1b706e7c55845ffef5dad0a1d4571b2892dd` | 42,328 | `75f9d8576fb84afa35d488187a195e4e323ef01ff415c70bbdbf4428d5f1ffab` |
| `bc551011281caabca9cc2d6e37a72459d8367242` | 43,072 | `54a72ce6185f861eceeca0a2d5d6a9de44fc202363488a79d0b99c8795357c64` |

Comparing those content-bound local JSON objects confirms **all 78 previous entries are unchanged**, there are 79 unique repository entries, and the only new row is `edithatogo/rare-omics-atlas`. Outside the dataset array, only `generated_at` changes. The existing policy is unchanged. The new Atlas status is `metadata_catalogue_published_raw_pending`. This agrees with the [candidate review](hf-estate-candidate-review-2026-11-22.json) and [publication read-back](hf-estate-publication-2026-11-22.json); it is not an estate-wide audit.

## Findings reproduced and resolved

### 1. Receipt output could overwrite an input

The original helper, SHA-256 `702df9b4ce76d24b6d03a58f342adfbab5a24407fab1747dfab830fc6c50ef73`, wrote its receipt unconditionally after validation failed. In an isolated temporary root I put `{"source_sentinel":true}` in the staging-manifest path, supplied an invalid Hub revision and selected that same path as `--receipt`. The command exited 1 but replaced the manifest sentinel with `verification_failed` JSON. No actual repository input was modified and no network request was needed.

The accepted correction reuses the reviewed publisher's path validation and receipt writer. `receipt_safe` remains false until the staging/full manifests, helper, publisher/tooling and every selected input have been enumerated and excluded from the output path. Lexical symlinks are rejected. An unsafe or unenumerable input set cannot cause a receipt write. An ordinary safe receipt path outside the checkout remains supported.

### 2. Initial correction imported the publisher before verifying it

The first guard correction moved the publisher import ahead of its immutable-source comparison. In a second isolated temporary root, I supplied a modified publisher containing only a top-level marker write. Its marker was created before the helper exited 1. This reproduced an execution-order regression; no real repository input or Hub state changed.

The final helper rejects a publisher whose SHA-256 differs from the already reviewed `1641709238710f6496b3fed1d8983aa9fa3f867cc50cd68753df69a85a447aea` **before importing it**, and retains the subsequent Git-baseline byte comparison. The publisher itself is unchanged. Both negative controls and the author's final checks are preserved in the [guard receipt](hf-verifier-receipt-guard-2026-11-22.json) and [test log](hf-verifier-receipt-guard-2026-11-22.log).

## Verification actually performed

The implementation author ran the focused regression and then the existing complete suite: **16 tests passed**. I inspected the retained log and its file hashes rather than repeating the full suite. The new single regression contains 14 isolated variants, covering protected input/tooling paths, receipt/source/publisher symlinks, the modified publisher, the malformed manifest and safe output.

I independently ran that focused regression: one test with all 14 variants passed, with observed process elapsed time **0.276289 seconds**. I also repeated three actual CLI controls using temporary roots:

| Independent CLI control | Observed result | Process elapsed seconds |
|---|---|---:|
| Original manifest collision | Exit 1; input sentinel preserved | 0.186881 |
| Invalid revision with safe output | Exit 1; failure receipt written | 0.177652 |
| Modified publisher | Exit 1; no marker execution and no receipt | 0.245721 |

These controls made no Hub calls. The final corrected helper was then executed once against the live pinned Atlas revision by the publication owner. Its receipt records **12:23:52 UTC**, **8.444116 seconds**, Python **3.15.2**, `huggingface_hub` **2.4.0**, 14 verified objects and no observed raw archive paths. I checked that receipt against the final helper hash and rechecked every recorded object identity. `full_release_verified`, `automated_publisher_upload_executed` and `official_github_actions_run_observed` all remain false. I did not repeat that final live replay or a bulk archive download.

A one-off reviewer binding check initially referenced a nonexistent receipt field named `sha256`; it stopped with `KeyError` without changing files. The corrected check used the actual `local_sha256` and `observed_hash` fields and passed. This was a reviewer command error, not a failed publication or an altered receipt contract.

The separate full gzip/archive checks and UI transport observations are retained evidence from the publication work, not newly repeated claims by this reviewer. This review uses source/API evidence and does not claim a new browser inspection or owner-device execution. The observed process durations are execution receipts, not delivery estimates or a performance benchmark.

## Reviewed final snapshot

| File | SHA-256 |
|---|---|
| `research/releases/2026-11-22/hub-staging/verify-metadata.py` | `e7495ed243873706e2935e263c321d40364f18f5a76f1040d7618b2b6cae084b` |
| `tools/hf-release/tests/test_publisher.py` | `115bc1ecfe9c46d334020a1435f661273831354d4cd6196c2249a9ccd63fa0cd` |
| `tools/hf-release/publisher.py` | `1641709238710f6496b3fed1d8983aa9fa3f867cc50cd68753df69a85a447aea` |
| `research/releases/2026-11-22/hub-staging/staging-publication-manifest.json` | `3b5ab3a3dee81a48f42c10844d6b87f8ef75613e034f0d10b96e7026292f51c4` |
| `research/releases/2026-11-22/manifest.json` | `6954bacc70ec1adb19e2104def524b837c3abcb84bfceb24426cda9815744a52` |
| `research/qualification/hf-metadata-publication-2026-11-22.json` | `34bb8ef350b1078af79c0184d9966c0ea1a686fc6dc2738633e559fe21b58b3a` |
| `research/qualification/hf-estate-publication-2026-11-22.json` | `e5750ed8b8957dbdd12c95c813d7f48d45d719314a2a3752cf22deebb286b95c` |
| `research/releases/2026-11-22/hub-staging/card-validation-fix-receipt.json` | `abb4b0c6dd6e5eaccc59b293230e7e180d7ad904ba6bd4552685526c2402b5c5` |

## Ponytail assessment and retained boundary

**Lean already. Ship.** This applies to the reviewed metadata publication and its small verification correction. The implementation retains the official Hub client, shared publisher checks, existing tests and manual trusted-runner workflow. No second transfer framework, authentication stack, hosted lakehouse service or statistical implementation is warranted by this finding.

The configured workflow's parent-commit guard was not exercised by the browser-editor publication route. No official self-hosted Actions run has been observed. The three locally verified archives remain absent from this Hub release; the reported HTTP 402 and browser download timeouts remain external transfer limits. The current Conductor plan correctly leaves the full mirror, full-release notice/estate reconciliation and full T09 archival unchecked. Metadata/source-linked Bronze can support separately eligible local technical work without implying that those remaining criteria have passed.
