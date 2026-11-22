# T07 — specification

## Objective
Qualify an existing Rust library to replace a specified R/Julia/Python scientific stage without changing estimands, statistical decisions, provenance, rights or reproducibility.

## Scope and boundaries
Candidate-first, one method at a time, using fixed file-level data contracts. Compare against reference scientific implementations. Do not build a universal plugin framework, porting programme, GPU system or novel method simply to change language.

## Source gates
T01-qualified human molecular data with ethics/governance and terms status; synthetic edge cases; public cohort(s) such as GSE97362/GSE218186 or GSE74432 with valid sample splits.

## Acceptance
Demonstrate numerical and clinical-result equivalence as appropriate (effect sizes, SE, p/FDR tails, null and small-n calibration, errors), version-pinned software, measured runtime and peak memory, licensing compatibility and independent verification. For a scientifically different method, compare outcomes rather than falsely claiming exact numerical parity. Keep the Julia/R reference oracle.

## Stop
No measured bottleneck, unclear terms, no benefit or failed parity: retain the existing backend. No clinical efficacy claim follows from a faster implementation.
