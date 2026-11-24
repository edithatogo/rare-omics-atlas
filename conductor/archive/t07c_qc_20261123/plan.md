# T07c — executable batches

- [x] Confirm exact current main, install the native hook and pass strict `--deep`
  baseline at `artifacts/verification/qc-baseline-20261123/receipt.json`.
- [x] Trace the actual QC/p-value CLI and independent R stages; predeclare exact
  full-schema and serialization checks before observing comparison values.
- [x] Produce the independent pinned QC/GCT and raw/QCD p-value references,
  retaining source-level adapters, semantic differences and failed attempts.
- [x] Implement `scripts/qualify_qc.py`, its immutable contract and corruption /
  failure tests; preserve before/after source, input, binary and checker identity.
- [x] Execute the complete production fixture and record accepted / held for
  each boundary. A method mismatch is an observed hold, not a passing test.
- [x] Independently review and pass the complete strict candidate suite: 34/34
  gates, 96 harness tests, 41 publisher tests and 20 Rust tests per profile.
  Final committing-hook and applicable hosted results are recorded in the
  integration PR; a failed integration gate blocks publication/merge.
- [x] Record environmental/source limits and next dependency order; archive only
  this completed implementation/receiving increment.

Batch one consumes existing source/assets and exits with exact reference bytes
and a narrow executable boundary. Batch two consumes those bytes and exits with
the full observed production comparison. Batch three reviews and integrates the
candidate. Record observed durations; no invented delivery estimate.

## Observed execution

The final production receiver ran 13 commands in 36.346 seconds and returned 1:
all 1,945,708 p-value comparisons passed while four native QC fields failed.
Both runs and all partial outputs remain retained. The final portable original
bead replay passed with Python assertions disabled in 2.202 seconds. Full sources,
commands, reference adapters, retained failures and scope are in the
[dated receipt](../../../research/qualification/t07-qc-2026-11-23.md).

Independent review closed unbound R-lineage declarations and incomplete
compressed/CSV failure receipts; 22 QC and six bead regressions pass. A separate
real merge-history secret-scanning regression closes the pre-existing scanner
coverage gap without waivers. This implementation can be completed while the
explicit native QC comparison and parent scientific/device criteria remain held.

Archived the completed receiver implementation after independent review and
strict verification. Final source publication remains bound to the installed
native hook and applicable PR checks; those immutable outcomes are reported in
the integration PR without relabelling this failed method comparison.
