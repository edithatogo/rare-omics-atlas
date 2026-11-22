# T07 — specification

## Objective

Qualify an existing backend for a named stage using Rust > Julia or Mojo > Python > R among suitable implementations. Preserve estimands, statistical decisions, provenance, rights and reproducibility. A justified C/C++ exception such as SeSAMe2 uses the same admission process.

## Scope and boundaries

Candidate-first, one method at a time, using fixed file-level data contracts. Compare against reference scientific implementations. Do not build a universal plugin framework, porting programme, GPU system or novel method simply to change language.

Current authorisation is documentation/planning only. This specification does not implement a backend, install dependencies or establish passed tests. Qualification is limited to the selected stage; every possible replacement is not a prerequisite for T02 or publication.

## Source gates

T01-qualified human molecular data with ethics/governance and terms status; synthetic edge cases; eligible public cohorts such as GSE97362/GSE116300/GSE218186 with valid sample splits. For preprocessing, the [focused audit](../../../research/methylation-backend-audit.md) maps author test prefixes to public GSM2995280, GSE228820 and GSE264438 records and a documented HM450 fixture. Verify exact bytes and de-identification before treating these as a replay of the external lab corpus. Software comparison on shared inputs is distinct from independent biological replication.

## Initial candidate requirements

- **limma-rust:** first resolve strict sample/coefficient/probe matching and malformed values, actual ordinary/moderated SE rather than the inspected unscaled `lfcSE`, NaN-safe BH/output and per-probe retained-design rank. A narrow explicit rejection contract is acceptable. Reuse reference generation/dumps with an independent comparator that fails on key/missingness differences and gates p-value tails/FDR; preserve global eBayes and the intended testing family.
- **Numerical reuse:** prefer standard-library and already declared faer/statrs capabilities before new dependencies or handwritten numerics. Compare newer versions only for documented needed fixes, including toolchain implications; do not auto-upgrade or discard cancellation-resistant log-tail/R-specific routines. No installed dependency or qualified numerical route is claimed.
- **SeSAMe2, only if selected:** reuse existing author R comparisons, matching annotation/mask versions and admitted public raw fixtures. Compare raw signals, per-step QC/betas and the actual production interface: `.cg` float32 plus `describe-probe` `%.6g` versus the internal float64 test oracle. Validate export and beta-to-M effects before using the C CLI, with a narrow precision improvement only if required. Ordinary C DML is not limma moderation; minfi functional normalization is a different preprocessing method. Respect the academic/nonprofit research licence conditions.

## Acceptance

Demonstrate numerical and clinical-result equivalence as appropriate (effect sizes, SE, p/FDR tails, null and small-n calibration, errors), version-pinned software, measured runtime and peak memory, licensing compatibility and independent verification. For a scientifically different method, compare outcomes rather than falsely claiming exact numerical parity. Keep the Julia/R reference oracle.

The [official local GitHub Actions runner policy](../../../research/local-development.md) applies to the relevant Mac/Windows/Linux lane. Record the observed run/job, source/workflow/toolchain versions, input hashes, machine details and measured results. An emulator, cloud-shell command, hosted-only check or unexecuted workflow does not satisfy that local qualification requirement.

## Stop

No real consumer, unclear terms, unacceptable migration cost or failed scientific/consumer checks: hold the candidate and retain the qualified backend. A performance bottleneck is not mandatory for native portability/maintenance work. No clinical efficacy claim follows from a faster implementation.

