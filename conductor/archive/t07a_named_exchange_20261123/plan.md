# T07a — executable batches

- [x] Review repository roles and retain the existing two-project/central-policy arrangement.
- [x] Specify the bounded synthetic contract and producer-first update order.
- [x] Implement the receiver and failure/corruption regressions; preserve the observed first-red import failure.
- [x] Review the receiver independently; fix JSON boolean/numeric type substitution and receipt/input aliasing before execution.
- [x] Receive the actual published producer commit and commit the immutable pin.
- [x] Run `uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep --output artifacts/verification/contracts-hooks-corrected`, including the actual exporter/receiver.
- [x] Record the exact producer/reference/output hashes, commands, comparison counts, strict outcomes and retained limitations.
- [x] Independently review and archive this bounded receiving increment after the actual 34-check pass.
- Final integration requirement: commit the complete candidate through the installed native hook and observe its hosted checks; the PR records those later source-bound outcomes.

The [integration document](../../../research/repository-integration.md) gives the full commands and upgrade order. Preprocessing qualification, actual independent participants, governance, official devices and N1 remain with the parent tracks.

[Observed execution and retained failed attempts](../../../research/qualification/contracts-hooks-2026-11-23.md). Final evidence/status/archive edits followed the runtime receipt; the actual commit hook must revalidate the complete final tree.
