# T07c — exact HM450 QC and detection boundary

## Scope and sources

Base Atlas source is `55341f42359ba69e95570ec0064ee5a7197f59eb`. Reuse T07b's
immutable public HM450 technical pair, C/YAME revisions, annotation and isolated
independent R runtime. Atlas owns the consumer; upstream owns numerical code.
The native hook was reinstalled and the full strict baseline passed 34/34 before
tracked changes. Source/reference curation may run in separate owned paths.

## Predeclared checks

The actual C QC TSV has 66 ordered metrics: 26 counts and 40 floating values.
Unchanged R `sesameQC_calcStats` supplies 65; GCT needs a separately evidenced
independent reference. Require every name and the exact sample, without metric
intersection. Counts and missingness must match exactly; floating QC values must
equal ten-significant-digit serialization of the fresh reference. Preserve
semantic differences as failed comparisons, including detection denominators.

QC is computed from the raw signals, with its beta summaries using D→B→P.
The production p-value export is separately checked at raw and QCDPB settings;
the latter captures pOOBAH after QCD and before B. Require the full ordered probe
universe, sample index, NA and binary32→six-significant-digit serialization, plus
no changed detection decisions at the upstream 0.05 boundary. Minimum beads is
explicitly zero. One/two-thread outputs must agree; a repeated pair does not
qualify concurrent multi-sample execution.

## Exit and held boundaries

Implement the smallest receiving command using existing helpers and the Python
standard library; run meaningful corruption/failure regressions and the actual
pinned fixture. Record every metric/p-value result, exact commands/hashes,
independent review, strict/hook/hosted outcomes and an accepted or held method
disposition. Missing references, skipped upstream tests and observed mismatches
must never become passes. Archive the completed receiving increment only after
its implementation/review gates pass; keep failed method and parent criteria open.

No sample rejection threshold, scientific beta/M precision budget, clinical
analysis, new platform, official owner-device acceptance or licence is inferred.
Actual-device access, institutional decisions and unavailable original source
crosswalks remain distinct environmental or evidence limits.
