# Native QC successor decision — 23 November 2026

## Selected behavior, before the successor run

`sesame-hm450-qc-v2` selects equivalence to the pinned native R functions at
`8b1fcfaed89b28e0def8b031a81611a0a770053c`. The bounded producer change is the
absent-signal assignment used by QC aggregation. The existing detection export
already uses the selected behavior. This is a technical HM450 fixture decision;
it does not choose a clinical rejection rule or admit a cohort.

| Boundary | Selected semantics |
|---|---|
| No usable signal in either channel | Detection p-value is `1`, as in native `pOOBAH`; the probe is a detection failure, not a missing p-value. |
| One channel or allele absent | Use the available signal through the existing channel/allele calculation. |
| `num_dtna`, `frac_dtna` | Count missing **p-values** after native absent-signal handling, not missing raw addresses. They are zero for this fixture. Raw intensity missingness remains reported in its separate QC fields. |
| Overall detection fraction | Include absent-signal probes in the nonmissing p-value denominator. Success remains `p <= 0.05`. |
| Masked detection fraction | Include absent-signal probes only when their existing mask is false. Do not infer or change the raw mask from this QC calculation. |
| `cg`, `ch`, `rs` fractions | Include every corresponding nonmissing p-value, including absent-signal failures. |
| Empty denominator | Preserve the existing missing/NA result; do not coerce it to zero or one. |
| GCT | Call native `bisConversionControl` independently in R. Use the pinned `HM450.probeInfo$typeI.extC` and `typeI.extT`, each intersected with raw `InfIR(sdf)`, as a separate positional producer input. Ignore the mask and omit missing green values within each mean as native R does. |
| Precision and universe | Preserve all 486,427 ordered probes, exact counts/NA, ten-significant-digit QC serialization, and binary32/six-digit p-value serialization. No tolerance increase or exempted metric. |

The native QC panel contains 65 fields. Native `bisConversionControl` is an
independently called 66th field, not a member added retrospectively to that panel.
The curated C/T sets contain 45,427/15,148 named probes in this raw fixture. Their
complete identities, ordering, annotation source and derived asset bytes must be
bound in the successor evidence. This fixture-specific intersection must not be
reused for another platform, source revision or sample without qualification.

## Minimal multi-repository implementation

Atlas carries an immutable patch against upstream C source
`f6713747181764e0b7a97b64c3c0d52ab9d82703`, with YAME
`e1e7b38e9f3b67981a78b1116e7312864677d69d`. Apply it only to a fresh isolated
build checkout. Bind the base revisions, patch bytes and resulting Git tree;
reject other tracked changes, hidden index entries or untracked source files.
The original upstream checkout remains available for the negative regression.
Preserve the upstream academic/non-profit research terms and notices with the
patch. This does not establish permission for a new commercial distribution.

The producer's existing extension-file input can carry the curated GCT codes.
Copy the pinned original asset store to a new qualification output directory and
replace only that copy's extension table. Keep the original published table and
raw/Q annotation contract unchanged. Reuse the existing complete-universe
receiver with an explicit `v2` selection; retain `v1` as the default historical
replay. No new repository, producer API, GCT formula, numerical engine or full
language port is required.

## Required evidence and retained limits

Run the same real-C absent-signal/count/denominator regressions against the old
and patched source; retain the old failure. Run the successor receiver for raw
and QCDPB exports with one and two threads, preserving all comparisons and end
integrity checks. Recheck the unaffected raw/Q boundary on the patched source.
Run the repository's complete strict local suite and the installed native hook,
then independent review and hosted checks for the published tree.

The original [v1 contract](contracts/sesame-hm450-qc-v1.json),
[failed receiving result](qualification/t07-qc-2026-11-23.json) and original
reference recipe remain unchanged. A successor pass does not erase that failure.
Full QCDPB beta/M precision, other arrays, scientific admission, study rejection
rules and official owner-device acceptance remain separate open criteria.

Sources: pinned native `R/detection.R` (`pOOBAH`), `R/QC.R`
(`sesameQC_calcStats_detection`) and `R/sesame.R` (`bisConversionControl`);
[retained GCT and missing-signal investigation](qualification/t07-qc-2026-11-23.md).
