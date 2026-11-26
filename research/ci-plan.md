# Strict development and CI contract

Updated 23 November 2026. This is the repository's implementation of the applicable central standards, not a second policy authority. Code verification, hosted provider acceptance, official owner-device qualification and scientific admission remain separate outcomes.

## One command from the outset

Prerequisites are Git, the official rustup installation and uv **0.13.9**. From a complete checkout:

```sh
uv sync --project tools/hf-release --frozen --python 3.15.2
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/bootstrap.py
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

Run verification before new implementation to expose the baseline, and after the bounded change. Missing tools, mismatched versions, unavailable advisory services, failed commands and absent generated coverage are failures. The default command is strict; there is no permissive profile. `--deep` adds a full reachable-history secret scan, including changes introduced by merge commits, and rejects a shallow checkout. It does not replace the central privacy guard.

The bootstrap pins Rust **1.95.0**, cargo-llvm-cov **0.8.7**, cargo-audit **0.23.0**, Gitleaks **8.30.1** and actionlint **1.7.12**. Native release checksum manifests are themselves SHA-256 pinned; only the verified expected binary is extracted. Development-only Python dependencies are locked in the existing publisher project: Ruff **0.15.13**, Pyright **1.1.409**, coverage **7.17.4** and pip-audit **2.10.1**. These are verification tools; the Rust catalogue gains no runtime dependencies.

The template's 90% changed-line coverage gate also runs locally through pinned `diff-cover` **11.0.4**, using real Python and Rust Cobertura reports, `--branch-coverage`, and untracked source files. A touched line with an untested branch counts as uncovered even if another branch executed. This uses the existing tool's support and preserves the original reports for Codecov. It compares with `origin/main` by default; `--base REF` or `VERIFY_BASE` selects and records the exact review base. Hosted pull requests use their base SHA, pushes use their previous SHA, and trusted main/manual runs use `HEAD^`. A missing base or report fails; no unknown baseline is converted to a pass. Project-wide regression comparison remains a separate Codecov provider result.

The single command checks:

- Rust formatting, all-target/all-feature Clippy with warnings denied, locked debug and release tests, doctests and rustdoc with warnings denied.
- Python formatting and linting; strict Pyright on production code and verification scripts; real publisher and harness regression tests. Python syntax targets the existing 3.11 minimum, while the executed development runtime is pinned to 3.15.2.
- Workflow syntax, local documentation links, JSON parsing and the Conductor dependency graph.
- The actual pinned limma synthetic exporter and atlas receiving contract, including named axes, complete families, uncertainty, missingness and independent R reference comparisons. See [repository integration](repository-integration.md).
- Full claimed production-source Rust/Python coverage. Tests are excluded from the coverage denominator; untested production paths remain included.
- RustSec advisories, Python advisories, a Python CycloneDX SBOM and a locked Rust dependency inventory. A Cargo metadata inventory is not itself an SBOM; the hosted lane additionally generates SPDX with the established SBOM action.
- Current-source Gitleaks scanning, including untracked nonignored changes; `--deep` additionally scans reachable Git history. Upstream default rules are explicit; inherited configuration, local ignore files and inline allow comments cannot waive this gate. Symlinks are identified in source hashes and are not followed by the snapshot scanner.

Receipts and individual safe command logs are written under ignored `artifacts/verification/`. A receipt records the source commit, dirty paths, current source-content digest, platform, tool versions, exact commands, exit codes and durations. Source changes during verification invalidate the result. Missing resource measurements are null. Reusing an output directory clears generated results before the new run; an interrupted/initialising receipt is not success.

## Hosted and official-device lanes

`Strict CI` runs on public pull requests, main pushes, merge groups, weekly schedules and manual dispatch. Its Ubuntu job uses the same strict command. It has bounded concurrency/timeouts, disabled persisted checkout credentials and immutable action pins. Coverage upload uses Codecov OIDC and fails on upload error. The template coverage policy is unchanged: project target `auto` with **1%** threshold, patch target **90%**. A generated report does not prove upload or provider acceptance; preserve those separate statuses in the receiving receipt.

**Canonical Codecov repository (26 November 2026):** [edithatogo/rare-venomics](https://app.codecov.io/gh/edithatogo/rare-venomics), GitHub repository ID 1467227964 (unchanged by rename). GitHub Actions OIDC already uses the current repository identity; do not use the dashboard URL as the upload endpoint or substitute the former slug. If Codecov returns `Repository not found`, synchronise the GitHub account/repository and enable the renamed repository in Codecov, verifying the GitHub App has access. Rerun the failed strict job after registration; require real provider acceptance on the current base and candidate, preserving the local measurement, native-hook and prior failure receipts. No coverage waiver, upload-error suppression, new token or change to the thresholds is authorised by this documentation.

A separate read-only PR dependency-review job uses the official action pinned at `bbc44d14a204704ccc493733616cd1e93a0321ec` and blocks low-or-higher known vulnerabilities across runtime, development and unknown scopes. It posts no PR comments and makes no invented licence-policy choice. The local Cargo.lock audit and audit of the installed, frozen Python developer environment remain active alongside this diff review. The Python result applies to the qualified platform/environment; it does not claim to audit every alternate platform or extra recorded in the multi-platform lockfile.

The separate `privacy-and-secrets` job calls the reviewed central Presidio/Gitleaks action at `2efdbd988064f6857795b9fa9ed4e1d08d18791d`. It preserves the standard's commit-range/full-history semantics, value-free findings and reported coverage gaps. Current-source Gitleaks is an additional local check, not a replacement for Presidio. The native pre-commit hook below additionally runs that central guard on the actual staged candidate. The 24 November hosted replay uses the existing full strict hook in an ephemeral checkout on pull requests, stages the exact current-base merge tree and creates a local Git commit with the hook installed, then proves the replay tree equals the candidate tree and restores the candidate revision. No GitHub write token or remote push is used. The ordinary non-PR strict command and separate central hosted privacy/dependency/provider checks remain; the native-hook replay receipt and logs must actually pass for the exact tree before merge. This is not official owner-device acceptance.

## Install the native pre-commit hook

Prepare the central scanner checkout and isolated environment using its [pinned local guidance](https://github.com/edithatogo/repository-standards/blob/2efdbd988064f6857795b9fa9ed4e1d08d18791d/privacy/local-hooks.md). Set `PRIVACY_CHECKOUT`, `PRIVACY_PYTHON` and `GITLEAKS_BIN` to their absolute paths outside this repository, then install:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/hooks.py install \
  --privacy-root "$PRIVACY_CHECKOUT" \
  --privacy-python "$PRIVACY_PYTHON" \
  --gitleaks "$GITLEAKS_BIN"
git config --local --get core.hooksPath
```

The expected hook path is `.githooks`. Installation verifies the exact central commit, clean source, isolated Python 3.15.2 environment, Gitleaks 8.30.1 and executable wrapper; it preserves conflicting existing hooks. Stage every intended source change before committing. The hook rejects a candidate that differs from the working tree, runs central staged privacy scanning and the full strict verifier, then checks that the source/index/HEAD have not changed. Missing tooling, scanner failure or verification failure blocks the commit. No cached success or permissive profile is used.

Actual installation is clone-local; another clone must run this command. The [integration document](repository-integration.md#native-pre-commit-enforcement) explains alternate-index handling and the separate server-side enforcement boundary.

## Other execution lanes

`Official local qualification` remains manual and accepts only this repository's reviewed main revision. It invokes the same harness on the selected macOS ARM64, Windows x64 or Linux x64 official runner and preserves the actual outcome. Each native command has its return code checked by Python, so a later PowerShell command cannot hide an earlier failure. No runner has been registered or activated by this increment, and no cloud result closes `T00.local_runner`.

The publication workflow stays separately authorised and source-bound. Verification has no Hub write token and never runs a real upload. The publisher's malformed-manifest failure handling is tested to preserve source files. Its historical metadata verifier separately pins the original reviewed publisher and the current reviewed implementation, without relabelling historical release bytes.

The [HM450 raw/Q qualification](preprocessing-qualification.md) adds mandatory
checker/oracle regression coverage to this same strict code command. Its actual
public-fixture production run is a separate explicit acceptance command requiring
the pinned C checkout, compiler and array assets. Re-run it before accepting a
change to that contract, checker, reference or selected upstream source; missing
inputs or upstream skips never count as method acceptance. Keeping this POSIX
candidate build separate preserves the existing cross-platform Atlas code gates
and avoids claiming an unsupported native Windows preprocessing route.

The [HM450 QC/p-value qualifier](qc-qualification.md) follows that same split.
Its preserved v1 comparison fails on documented semantic mismatches. The
[explicit native v2 successor](native-qc-qualification.md) passes its complete
technical boundary and additionally runs the focused real-C regression and
actual raw/Q preservation checks. Ordinary CI tests both versioned receiving
paths, exact source/annotation binding and failure preservation. A technical
pass does not accept the broader scientific or owner-device route.

## Central standards and template reconciliation

| Source | Inspected revision | Applied decision |
|---|---|---|
| [repository-standards](https://github.com/edithatogo/repository-standards/tree/2efdbd988064f6857795b9fa9ed4e1d08d18791d) | `2efdbd988064f6857795b9fa9ed4e1d08d18791d` | Rechecked 23 November: registry maintenance since `a3cc8dcc` changes one entry and its evidence; the other 167 entries and applicable templates/coverage policy are unchanged. The separate older scanner gap is corrected below. |
| [template-solo-rust](https://github.com/edithatogo/template-solo-rust/tree/1c96169526b3ae5845c22d1fae19aeec5c5f35f9) | `1c96169526b3ae5845c22d1fae19aeec5c5f35f9` | Rechecked 23 November: the only change since inspected `d592464` advances its reusable central workflow pin to `e642522`; Rust quality/coverage and the single-maintainer model remain unchanged |
| [template-solo-data](https://github.com/edithatogo/template-solo-data/tree/a4b2b2aa06cba3bc875ca34f806074d2f4f7ebb3) | `a4b2b2aa06cba3bc875ca34f806074d2f4f7ebb3` | Data boundary, Python coverage and published-artifact provenance |

The central reusable Rust job assumes a root Cargo manifest and floating stable Rust. This repository instead has a catalogue subproject and a previously qualified 1.95.0 toolchain; a thin local caller is therefore justified. The strict Python choice is a local implementation decision, not a claim that central policy mandates a particular type checker. Existing account community defaults should be inherited where GitHub supports inheritance. Preserve existing Renovate onboarding PR #1 rather than introduce another dependency bot.

### Merge-history secret-scan reconciliation

The native v2 increment also reviewed central main
`0be4668d17ac3b6d902d4354bd01f420c7c29272` and the same relevant Rust/data templates.
Its later central delta is Limma-specific nonidentifier review and a registry
size-cap adjustment. Atlas needs no new exception or policy change and retains
its already qualified `2efdbd` hook/action pin. The carried C licence contact is
an advisory under the existing repository profile, not a suppressed identifier.

T07c also corrects a pre-existing coverage gap between Atlas's former central
scanner pin `b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4` and the currently reviewed
central scanner. The native history scan now explicitly passes
`--all --full-history --diff-merges=first-parent --no-ext-diff --no-textconv`.
The hosted privacy action and installed native hook share the new exact central
pin. The action/runtime/install/lock/licence blobs inspected at the old and new
pins are unchanged; the scanner has the relevant merge-history correction.
This is separate from the latest registry-maintenance change.

A real Git/Gitleaks regression creates a disposable merge-only fictional canary,
removes it in the next commit and verifies that a clean final snapshot cannot
hide it. The old selector misses the canary; the production strict verifier now
fails `history-secrets` with exactly one redacted finding. The test checks that no
canary value is logged. It preserves all existing secret rules and waiver
prohibitions. The [dated receipt](qualification/t07-qc-2026-11-23.md) records the
actual red/green regression, native installation and full candidate checks.

## Outstanding dispositions

| Item | Disposition and receiving owner |
|---|---|
| Atlas code licence | **Unresolved.** The maintainer must choose or identify applicable terms. Do not copy a template licence or infer rights from public visibility. This prevents a claim of complete Community Standards/licence conformance. Existing source-specific dataset rights remain separate. |
| Hosted execution/provider receipt | Received at `412cc2720072bbf91b7c35e1e1256e3decd7d389`: strict, privacy, dependency-review, SPDX/upload and Codecov patch 95.30% succeeded. [Acceptance](qualification/strict-ci-2026-11-22.md#accepted-hosted-increment). Every subsequent candidate still needs its actual checks. A first project-regression baseline/result is not inferred from patch success. |
| Stable required-check enforcement | GitHub's repository/branch APIs were read on 22 November 2026: no rulesets were returned, `main` was unprotected, and required status contexts were empty. After observed successful jobs, the repository administrator can require the exact names. No branch protection or ruleset change is claimed here; preserve zero mandatory human approvals and existing protections. |
| Official device qualification | Trusted device operator must run the configured official workflow and retain its revision-bound receipt. |
| Published scientific releases | Remain behind existing source/data/method/N1/device gates; add release provenance/checksums for a real release, not speculative packaging. |

Keep T00/T01/T07 scientific parents open. Ready source-contract and synthetic method work can continue while external prerequisites remain unavailable. No blanket coverage waivers, statistical tolerance changes, package ports, GPU framework, managed lakehouse or alternative orchestrator is introduced by this CI increment.
