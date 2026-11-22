# T09 independent publisher review — 22 November 2026

**Decision: accept the bounded publisher, release selection and manual workflows for the source-commit/publication step. Two implementation findings were resolved during review. No remaining material finding was identified in this scope.** This is pre-publication acceptance: T09 archival still requires the actual GitHub source commit, successful Hub publication/read-back and the separately planned estate-registry update. This review did not upload files or execute an owner-device runner.

## Scope and Ponytail assessment

The reviewer read the T09 specification/plan, publisher and tests, frozen dependency declaration/lockfile, both manual workflows, release manifest/card/notices, T08 catalogue qualification/review, original intake receipt and later full gzip-check receipt. Only this review document was edited by the reviewer; the implementation agent/root owned fixes.

The official `huggingface_hub` client supplies authenticated Hub operations and large-file transport. The Python boundary is confined to publication; the catalogue remains Rust. Standard-library hashing, paths, JSON, Git subprocess calls and bounded HTTPS download are adequate here. There is no bespoke Hub protocol, generic connector hierarchy, database service or fabricated scientific Silver/Gold layer. The reviewed release manifest is the complete allowlist.

**Complexity-only Ponytail result: Lean already. Ship.** The separate correctness review below supplies the acceptance conditions; this sentence does not certify an unobserved remote publication.

## Findings resolved before acceptance

1. **A manual workflow could lose the only publication/failure receipt.** The original workflow wrote it only under `runner.temp`. Root added a pinned official `actions/upload-artifact` step with `if: always()`, selecting only that JSON receipt and retaining it for 14 days. This preserves evidence if a remote commit succeeds but its postcheck fails. A missing receipt after an earlier qualification failure is a warning, not a false publication success. Long-term qualification evidence still belongs in the planned GitHub receipt.
2. **Windows line-ending conversion could break exact-byte publication.** The repository initially had no text/EOL attributes. In a temporary Git repository using the real release README, `core.autocrlf=true` changed 3,518 LF bytes to 3,570 CRLF bytes while `git status --porcelain` stayed empty. The manifest hash consequently differed. Adding `* text=auto eol=lf` preserved exactly 3,518 bytes with clean Git status. Root added that policy plus explicit binary exclusions for TAR/GZIP/ZIP/PNG/PDF. The reviewer reread the final policy and workflow. This was a Linux Git simulation of the setting, not native Windows execution evidence.

## Independently executed checks

| Check | Observed result |
|---|---|
| Frozen publisher tests | `uv run --project tools/hf-release --frozen python -m unittest discover -s tools/hf-release/tests -v`: **15 passed, 0 failed**, 0.218 seconds reported by unittest |
| Runtime | CPython 3.15.2; `huggingface-hub` 2.4.0; `httpx2` 2.16.2; `hf-xet` 1.8.0; `socksio` 1.0.0 |
| Metadata allowlist | Independently recomputed sizes and SHA-256 for all **13** metadata objects; all match the release manifest |
| T08 continuity | All five catalogue output hashes/byte counts match the reviewed T08 qualification receipt; the selected rights-register and summary hashes match the T08 review |
| Bronze continuity | The three archive URLs, sizes and hashes match the earlier full-download intake receipt |
| Actual default dry-run | Ran the publisher without `--upload` or `--fetch-sources`, against the existing qualified archive cache; **18 verified local objects**, **0 remote objects**, `dry_run_verified` |
| Full archive rehash | The dry-run reread and verified all **3,828,981,760 bytes** in GSE97362, GSE116300 and GSE218186; no new network transfer was required |
| Dry-run timing | **3.1255408199976955 seconds** measured internally, 11:09:43–11:09:46 UTC; this is one observed cache-resident execution, not a throughput benchmark |
| EOL negative/control experiment | Clean Git checkout with CRLF conversion failed byte identity; the LF attributes policy preserved the exact source bytes |
| Patch whitespace | `git diff --check` returned success |

The dry-run receipt had `source_revision=null`, as expected before committing the reviewed source; it is not upload-mode acceptance. Its SHA-256 was `519cd4458dee2c787f0f6d41b0275e31c3b286326d89e27b6ab142a5d0d4734e`. The later upload receipt must name the real source revision and include observed remote results.

The later full-decompression receipt reports **691 gzip members** passing CRC across the same three archives. The reviewer checked its accession coverage and relation to the manifest, but did not rerun decompression. The earlier intake's `gzip_full_crc_checked=false` remains an honest historical record; the later receipt records the additional check. Neither constitutes scientific methylation QC.

## Publication contract reviewed

Upload mode requires the supplied full Git SHA to equal actual `HEAD`, with the selected manifest, metadata, publisher, dependency declaration and lockfile tracked and clean. All selected bytes must match the manifest. Unsupported repository/source URLs, noncanonical/traversing paths, symlinks, wrong sizes/hashes, unsupported object kinds and duplicate/reserved destinations fail. The tests include actual temporary-Git clean/dirty/revision behavior, rather than merely mocking Git.

The default mode performs local validation and prepares deterministic generated records without instantiating a Hub client. Source fetching is explicit, bounded by expected size, restricted to exact public GEO HTTPS archive paths and checked before promotion. Existing mismatched files are preserved; failed invocation-owned partial files are removed.

In upload mode, an existing private target is refused and its visibility is not changed. A missing target may be created publicly under the explicitly selected owner/repository. The publisher passes only the 16 manifest objects plus the exact manifest and generated provenance to one official `create_commit` call. It sends the observed parent commit, with no deletion or folder-wide upload. [The official API documents](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api) that `parent_commit` causes a concurrent-change mismatch to fail; the installed 2.4.0 signatures accept the used arguments.

Read-back is pinned to the returned commit OID. Every selected remote path and size must match, along with LFS SHA-256 or the small-file Git blob identifier computed from the local bytes. A bad LFS digest cannot fall back to a matching Git identifier. If a postcheck fails after a commit, the failure receipt retains the observed Hub commit. Generic SDK exception details are withheld from the public receipt; the publisher does not take or print a credential argument. Tests use fake Hub operations and therefore establish the control contract, not actual upload success.

## Release meaning and source rights

The selected Bronze objects are the previously inspected public GEO archives, copied without changing their original bytes. The card/notices preserve source and Illumina annotation attribution, use source-specific rights rather than relicensing all material, and distinguish article licences from deposited array files. The manifest records the affirmative GEO public use/distribution basis and the reviewed absence of a contrary source notice in the inspected scope. This review does not introduce a new blanket author-permission or HREC/IRB requirement for this bounded public mirror.

The Silver objects are the exact reviewed factual catalogue and provenance selection. They do not republish cached API response bodies, contacts or unrestricted clinical free text. They do not claim that every listed URL was transferred. The 29 accessions include technical references/other omics; 2,532 series–assay memberships and 2,465 distinct GSM accessions are not independent participant or disease counts. There is no scientific Gold result. Later scientific inference, participant linkage and institutional classification remain separate recorded tasks.

## Workflow and remaining acceptance limits

Both workflows are manual-only, require the owner repository and `refs/heads/main`, use a pinned checkout of `github.sha`, disable persisted Git credentials and target explicit official self-hosted labels. No public-PR trigger executes code on the owner's workstations. Publication credentials are scoped to the upload step; the retained artifact is only the sanitized receipt. The checkout and artifact action release-tag checks were supplied by root; this reviewer inspected the pinned final YAML.

The source was still uncommitted at review time, on base `89b268fe1d1d457f03bf75320ae82e027fbd43d9`. Before real publication, commit the reviewed inputs, use that actual checkout/SHA and retain the resulting immutable Hub receipt. Do not archive T09 on this dry-run alone. The planned estate-registry update must preserve unrelated entries and be independently read back after publication.

Neither configured labels, these tests, the EOL simulation nor this cloud shell establishes Mac/Windows/Linux owner-device runner acceptance. The documented local-runner milestone remains open. No patient-model validity, disease-analysis completion, benchmark speedup or novel scientific result is claimed.

## Reviewed snapshot

| Item | SHA-256 |
|---|---|
| `tools/hf-release/publisher.py` | `1641709238710f6496b3fed1d8983aa9fa3f867cc50cd68753df69a85a447aea` |
| `tools/hf-release/tests/test_publisher.py` | `c1aeb885c246def49fca6402eaf5167053dc94ec851c56b1578c725bd4dd086f` |
| `tools/hf-release/pyproject.toml` | `94a564885f79b3d3fd6a406cb24e31dd59f470bba8fee3797543969f6599ba6a` |
| `tools/hf-release/uv.lock` | `6dbe5c00650daf62a89e3256ec1cad540b1705036269b41fdcd68ab9d993735f` |
| `.github/workflows/publish-hf.yml` | `a5db4d2fd9ed91a93508051bfba812744b5ff1e5d038b21948e36d3ad77ba497` |
| `.github/workflows/local-qualification.yml` | `a75b0410a32360c7c550fe9fa85524e896b7f50eb4f2057b85af59ae5e0757bd` |
| `.gitattributes` | `52c02cde3e456f9e0899c00bddaffa91ce779b90763087280b91707dd3399732` |
| `research/releases/2026-11-22/manifest.json` | `8d68e803c1f01aa52e382f31b709893e6e52758df10ac0160b8d75656008f6f2` |

The manifest binds all 16 selected input objects. The generated provenance becomes source-commit-specific when upload mode receives the real reviewed Git SHA; its pre-commit dry-run hash is not the eventual publication hash.
