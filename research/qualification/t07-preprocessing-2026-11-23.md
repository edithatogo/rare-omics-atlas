# HM450 preprocessing/annotation increment — 23 November 2026

## Outcome and scope

The bounded SeSAMe2 **HM450 raw/Q production-export and annotation contract
passed** on the pinned public author technical pair. A fresh independent R
reference exactly matches the independent mathematical raw/Q oracle. Separate
full-QCDPB numerical and production beta-only diagnostics also passed on that
same pair. These results do not admit a disease cohort, establish sample QC
thresholds or accept an actual owner device.

The [machine receipt](t07-preprocessing-2026-11-23.json) preserves exact sources,
input/output hashes, commands, failures and limits. The [contract and executable
recipe](../preprocessing-qualification.md) explain how to reproduce the bounded
raw/Q gate. Base Atlas source: `4162111f38e63ca21d811d7df2e628239297bc8d`.
The [independent R reproduction recipe](t07-reference-2026-11-23/REFERENCE_REPRODUCTION.md)
supplies the exact source/data pins, isolated runtime lock, local adapter details
and separate raw/Q, internal QCDPB and production-export commands.

## Existing implementations and exact inputs

| Component | Inspected and executed source |
|---|---|
| SeSAMe2 C CLI | 2.3.2, `f6713747181764e0b7a97b64c3c0d52ab9d82703` |
| YAME | Gitlink `e1e7b38e9f3b67981a78b1116e7312864677d69d` |
| InfiniumAnnotation | v8.5, `678acbeddfb746c1ddfa24c5c1ca9f5197a61ee2` |
| Author public HM450 pair | InfiniumAnnotationData `6d176d6e7e56465403d4478a09fe11b983eeb721` |
| Fresh R numerical source | sesame 1.31.12, `8b1fcfaed89b28e0def8b031a81611a0a770053c` |
| R runtime | 4.5.2, isolated Linux environment; exact package lock retained with the reference recipe |
| R annotation objects | Zenodo record 23263026; source MD5 and independently computed SHA-256 checked |

The [immutable input manifest](../contracts/sesame-hm450-raw-q-v1.json) pins the
two IDAT files and five selected assets: ordering, hg38 coordinates, type-I
extension codes, mask and mask index. Each IDAT is 8,095,289 bytes and contains
622,399 addresses; the two address vectors agree exactly. Every required source
and input remains unchanged after execution.

The actual C build used GCC 14.2.0 and GNU Make 4.4.1 on Linux x86_64. It succeeded
with existing upstream compiler warnings, including format truncation,
indentation and unused-parameter warnings. This is not a warning-free upstream
build or an audit of all bundled native dependencies. The upstream offline
HM27 synthetic checks, 21 error-surface cases and documentation-consistency
checks also passed. Missing prerequisites in other upstream drivers can return
successful `SKIP`; those unexecuted suites are not counted as passing.

## Complete annotation qualification

The actual `sesame describe-probe` coordinate export matches **all 486,427
ordered rows** of the pinned ordering and coordinate files, with no intersection
filter or dropped rows. The universe contains 482,421 cg probes, 3,091 ch probes,
65 rs probes and 850 controls. Channels are 350,926 type-II, 89,206 red type-I and
46,295 green type-I. Coordinate metadata retains 858 unavailable chromosome
entries and every alternate/unplaced contig; zero-based `CpG_beg` is unchanged.
The extension-code file has the same complete row space. These checks do not
qualify GCT or other QC metric values.

The fresh R address object independently matches every probe ID, M/U address,
channel and initial mask value. **All 24 published R mask tracks** match the
decoded pinned annotation bits, with no absent IDs or differing bits. The
selected five recommended Q tracks union to **29,504 masked probes**; the
broader `M_general` track is not substituted. This validates the specific
checksum-bound companion-file alignment, not arbitrary positional annotation.

## Independent references and actual raw/Q exports

The portable mathematical oracle directly reads IDAT uint16 means and follows
the pinned R address/channel and beta-floor rules. It does not use C pipeline
values. Its complete deterministic reference table has SHA-256
`af498b8ffb757dea34d93f661f49165a6a45d7dfa677bc38a684286ac96b86e3`.
The separately executed unchanged R functions produce exactly the same M/U
signals, raw/Q binary64 values, NA patterns and Q mask over the entire universe.

The production checker cleans and rebuilds the pinned C source, requests beta
output with explicit platform/mask/bead settings, and reads the actual named
`.cg` text export. Every value must equal the declared binary32 followed by
six-significant-digit serialization of the independent reference. This checks
the composed production export; individual stored binary32 words are not
separately decoded and audited.

| Stage | Threads | Rows checked | Finite | NA | Result |
|---|---:|---:|---:|---:|---|
| Raw | 1 | 486,427 | 486,425 | 2 | Exact serialized agreement |
| Raw | 2 | 486,427 | 486,425 | 2 | Exact serialized agreement |
| Q | 1 | 486,427 | 456,921 | 29,506 | Exact serialized agreement |
| Q | 2 | 486,427 | 456,921 | 29,506 | Exact serialized agreement |

That is **1,945,708 probe values checked**, including 59,016 missing values.
The binary and text file hashes are identical between thread settings for each
stage. Repeating one pair does not test concurrent processing of a multi-sample
cohort or establish a performance benefit.

Raw and Q each retain seven existing beta endpoints and have zero new
finite-to-endpoint collapses on this pair. The maximum observed beta
serialization difference is **5.29411764649268 × 10⁻⁷**; the maximum finite
M-value difference is **0.00036133936109372655**. These are measured losses,
not chosen scientific acceptance limits. No clipping or imputation is added.

## Separate fresh QCDPB diagnostics

The unchanged R `prepSesame(sdf, "QCDPB")` functions run with an explicitly
qualified raw SigDF, exact local R annotation objects and upstream default
numerical arguments. Three small `sesameDataList/Get/Has` adapters supply the
local cache objects; mask selection, background-mask selection and numerical
functions are unchanged. This is a disclosed source-level reference adapter,
not a full sesame/sesameData package installation.

The initial precompiled `preprocessCore` run failed with `pthread_create` error
22. The failure is retained. The successful run used **the same preprocessCore
1.72.0 source**, compiled with the documented `--disable-threading` option in a
separate local R library. No numerical function or comparison tolerance changed.

| Comparison | Complete-universe result | Acceptance basis |
|---|---|---|
| R QCDPB versus C internal binary64 helper output | 486,427 identical ordered IDs; 79,947 matching NAs; 406,480 finite values; maximum absolute difference **1.1102230246251565 × 10⁻¹⁵** | Upstream predeclared maximum absolute bound **10⁻¹²**, plus strict full-universe and NA checks |
| Actual production beta-only QCDPB export versus fresh R | Same complete universe and NA pattern; exact composed binary32/six-digit agreement; zero endpoints or new endpoint collapses | Exact declared serialization of R values, including named sample index |

The production beta-only diagnostic explicitly sets HM450, the pinned mask,
zero bead threshold and one thread. Its maximum measured beta serialization
error is **5.294165927871575 × 10⁻⁷**, and finite M error is
**8.747193203184622 × 10⁻⁵**. The internal helper comparison is independent
numerical evidence only because its comparator is fresh R; it cannot substitute
for the separate actual production-export check.

These are one-fixture beta diagnostics. Full QC metrics, additional platforms,
multiple-sample ingestion and scientific error budgets remain unqualified.
The stable executable Atlas contract remains the bounded raw/Q gate; a broader
scientific preprocessing route is not admitted by these additional results.

## Review, strict code checks and failed attempts

The native hook was installed before implementation. The first baseline caught
Actionlint before its installation completed; its failed receipt is preserved.
With the complete pinned toolchain, the unchanged-source strict `--deep`
baseline passed all 34 checks. No gate or tool requirement was weakened.

Independent code review identified two integrity gaps before acceptance: the
YAME binary needed an end-of-run hash check, and the declared Q-mask track list
needed exact validation. Both were fixed and covered by regressions; checker
and shared-helper hashes are also checked before/after. Initial targeted
Pyright checks found nine optional-value narrowing errors; explicit casts after
validated row-presence checks resolved them. The reviewed production command
then passed again on the exact pinned inputs.

The 21 checker tests use a complete synthetic universe and literal serialized
outputs, with external processes mocked. They exercise corruption, dropped or
duplicated identities, missingness, endpoints, sample/schema drift, source/input
pins and symlinks, timeouts/failures, fresh output handling, and after-run changes
to inputs, binaries, contract and checker files. Four independent-oracle tests
separately check channel/address rules, zero-signal floors and IDAT field parsing.
Four additional reference-comparator tests preserve failed receipts, complete
schema/universe checks and input/receipt separation. The formatted committed
comparators were replayed against all actual reference rows and exports, with
the same passing results; both R driver hashes match the scripts actually run.
The first combined strict candidate run passed **34/34**, with **99% changed-code
coverage** under the unchanged branch-aware 90% minimum. The complete final candidate, including reference recipes and archived bounded
tracks, also passed **34/34** in **32.303 seconds**: 67 harness/reference tests,
41 publisher tests and 20 Rust tests in each profile, with 99% changed-code
coverage. Final evidence-only receipt updates are rechecked by the native commit
hook; the PR records that exact published tree and its hosted checks.

The current central standards and both relevant templates were rechecked. The
central delta only removes a retired registry source; the Rust template delta
only advances its central workflow pin. The [CI plan](../ci-plan.md) records the
current immutable revisions and unchanged policy. No new runtime dependency,
preprocessing port, service, repository or workflow framework was introduced.

## Next implementation order

1. Use this technical evidence to specify the **complete selected preprocessing
   and QC contract**: QC metrics, sample/probe rejection rules, supported platforms
   and a predeclared scientific precision budget. A higher-precision export is a
   bounded candidate only if the actual consumer requires it.
2. Continue **molecular/sample crosswalks, identity/overlap and missing covariates
   in parallel**, using the [new cohort-source receipt](t01-cohort-curation-2026-11-23.md).
   Freeze native controls, eligible cases and analysis partitions together after
   those inputs are available; array keys and methylation predictions do not
   resolve independent participant or molecular eligibility.
3. Receive the applicable institutional determination and official actual-device
   run. Apply the accepted technical QC route and record T01 admission; then
   freeze N1 before disease-conditioned T07/T02 comparisons.

Limma's status reconciliation is a separate documentation-only change and does
not alter Atlas's existing numerical producer pin. No clinical effect analysis,
raw Hub mirror, licence assignment, runner activation or branch-rule change is
claimed by this increment. Source-linked local work and further source curation
can continue while their independent external prerequisites remain open.
