# T07 — specification

## Objective
Qualify an existing backend for a named stage using Rust > Julia or Mojo > Python > R among suitable implementations. Preserve estimands, statistical decisions, provenance, rights and reproducibility. A justified C/C++ exception such as SeSAMe2 uses the same admission process.

## Scope and boundaries
Candidate-first, one method at a time, using fixed file-level data contracts. Compare against reference scientific implementations. Do not build a universal plugin framework, porting programme, GPU system or novel method simply to change language.

## Source gates
T01-qualified human molecular data with ethics/governance and terms status; synthetic edge cases; public cohort(s) such as GSE97362/GSE218186 or GSE74432 with valid sample splits.

## Acceptance
Demonstrate numerical and clinical-result equivalence as appropriate (effect sizes, SE, p/FDR tails, null and small-n calibration, errors), version-pinned software, measured runtime and peak memory, licensing compatibility and independent verification. For a scientifically different method, compare outcomes rather than falsely claiming exact numerical parity. Keep the Julia/R reference oracle.

## Stop
No real consumer, unclear terms, unacceptable migration cost or failed scientific/consumer checks: hold the candidate and retain the qualified backend. A performance bottleneck is not mandatory for native portability/maintenance work. No clinical efficacy claim follows from a faster implementation.

