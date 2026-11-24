# T09 plan

- [x] Consume reviewed T08 catalogue and original three-archive receipts.
- [x] Prepare minimal medallion release manifest, exact source notices and official Hub publisher.
- [x] Test manifest/failure checks and trusted local workflow definitions; distinguish configuration from an actual owner-device run.
- [x] Independent Ponytail review and GitHub source publication (PR #7); subsequently correct the two card metadata fields rejected by the live Hub validator and rehash/recheck the prospective release.
- [x] Publish and verify the 13-object metadata subset plus its manifest through the Hub editor and official read-only API, at `3f1cb8e64d8e31e7e40773441ba6266714569d05`.
- [x] Register the canonical metadata-only estate entry at `bc551011281caabca9cc2d6e37a72459d8367242`, preserving all 78 existing entries.
- [ ] Transfer the three original archives and verify the complete release. Blocked: remote compute returned HTTP 402 and browser download transport timed out; an authenticated official owner runner has not been made available in this session. Use the existing manual workflow rather than add another upload system.
- [ ] Reconcile notices to the actual full release, verify immutable Hub paths/hashes and update the estate status.
- [ ] Archive full T09 only after its original full-publication acceptance passes. Metadata-only publication does not satisfy raw mirroring.

Evidence: [publication and remaining task](../../../research/qualification/hf-metadata-publication-2026-11-22.md), [14-object read-back](../../../research/qualification/hf-metadata-publication-2026-11-22.json), [estate read-back](../../../research/qualification/hf-estate-publication-2026-11-22.json). No scientific or official owner-device admission follows from this infrastructure work.

## Remaining executable batch

**Owner:** the trusted runner operator supplies the authenticated execution environment; the T09 implementer owns the manifest verification, read-back and estate receipt. Revisit when that environment is available. Do not buy remote compute or build an alternative uploader to clear this hold.

1. Pin reviewed main and run the strict verification command from [tracks.md](../../tracks.md#executing-one-ready-batch). Confirm `research/releases/2026-11-22/manifest.json`, source URLs, byte counts, SHA-256 and notices against the existing receipts; do not silently change the selected release. Preserve the existing published metadata subset.
2. In the selected trusted environment, run the existing `publisher.py` default dry-run using `--manifest research/releases/2026-11-22/manifest.json --root . --data-root <explicit-cache-root> --receipt <outside-inputs-dry-run.json>`, through `uv run --project tools/hf-release --frozen --python 3.15.2 python`. If originals are absent, use its existing `--fetch-sources` path. Pass only when all allowlisted inputs match; a download listing or partial transfer is insufficient.
3. Invoke the existing `publish-hf.yml` manual workflow on reviewed main and the actual registered target. Its publisher receives the exact source revision, uses the official Hub client and guards the parent commit. Retain the job's publication/failure artifact. A failed run with an observed Hub commit must be investigated by immutable read-back before any retry; do not claim that no mutation occurred.
4. Verify every allowlisted destination and both generated release records at the returned immutable Hub revision. Match sizes and LFS SHA-256 or Git blob IDs as implemented, and retain local SHA-256 provenance. Record the reviewed GitHub SHA, Hub SHA, full object count, source archive outcomes and check command in the new publication receipt. Pass only if all three raw archives and the complete release verify.
5. Update only the existing canonical estate entry from metadata-only to the observed complete release, preserving unrelated entries. Check the estate schema and read back the new commit. Reconcile notices to what was actually published; do not label biological Silver matrices or Gold analyses as present.
6. Review the complete release against `spec.md`; only then mark the remaining boxes complete and archive T09 using `conductor/workflow.md`. Leave T00 device/scientific milestones open unless their own evidence independently passes.

The values in angle brackets are environment-specific paths chosen by the operator, not literal runnable arguments. The exact full publisher command is already documented in `tools/hf-release/README.md`; this plan does not introduce a second publication interface.
