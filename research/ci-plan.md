# Strict development and CI contract

Updated 22 November 2026. This is the repository's implementation of the applicable central standards, not a second policy authority. Code verification, hosted provider acceptance, official owner-device qualification and scientific admission remain separate outcomes.

## One command from the outset

Prerequisites are Git, the official rustup installation and uv **0.13.9**. From a complete checkout:

```sh
uv sync --project tools/hf-release --frozen --python 3.15.2
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/bootstrap.py
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

Run verification before new implementation to expose the baseline, and after the bounded change. Missing tools, mismatched versions, unavailable advisory services, failed commands and absent generated coverage are failures. The default command is strict; there is no permissive profile. `--deep` adds a full reachable-history secret scan and rejects a shallow checkout. It does not replace the central privacy guard.

The bootstrap pins Rust **1.95.0**, cargo-llvm-cov **0.8.7**, cargo-audit **0.23.0**, Gitleaks **8.30.1** and actionlint **1.7.12**. Native release checksum manifests are themselves SHA-256 pinned; only the verified expected binary is extracted. Development-only Python dependencies are locked in the existing publisher project: Ruff **0.15.13**, Pyright **1.1.409**, coverage **7.17.4** and pip-audit **2.10.1**. These are verification tools; the Rust catalogue gains no runtime dependencies.

The template's 90% changed-line coverage gate also runs locally through pinned `diff-cover` **11.0.4**, using real Python and Rust Cobertura reports, `--branch-coverage`, and untracked source files. A touched line with an untested branch counts as uncovered even if another branch executed. This uses the existing tool's support and preserves the original reports for Codecov. It compares with `origin/main` by default; `--base REF` or `VERIFY_BASE` selects and records the exact review base. Hosted pull requests use their base SHA, pushes use their previous SHA, and trusted main/manual runs use `HEAD^`. A missing base or report fails; no unknown baseline is converted to a pass. Project-wide regression comparison remains a separate Codecov provider result.

The single command checks:

- Rust formatting, all-target/all-feature Clippy with warnings denied, locked debug and release tests, doctests and rustdoc with warnings denied.
- Python formatting and linting; strict Pyright on production code and verification scripts; real publisher and harness regression tests. Python syntax targets the existing 3.11 minimum, while the executed development runtime is pinned to 3.15.2.
- Workflow syntax, local documentation links, JSON parsing and the Conductor dependency graph.
- Full claimed production-source Rust/Python coverage. Tests are excluded from the coverage denominator; untested production paths remain included.
- RustSec advisories, Python advisories, a Python CycloneDX SBOM and a locked Rust dependency inventory. A Cargo metadata inventory is not itself an SBOM; the hosted lane additionally generates SPDX with the established SBOM action.
- Current-source Gitleaks scanning, including untracked nonignored changes; `--deep` additionally scans reachable Git history. Upstream default rules are explicit; inherited configuration, local ignore files and inline allow comments cannot waive this gate. Symlinks are identified in source hashes and are not followed by the snapshot scanner.

Receipts and individual safe command logs are written under ignored `artifacts/verification/`. A receipt records the source commit, dirty paths, current source-content digest, platform, tool versions, exact commands, exit codes and durations. Source changes during verification invalidate the result. Missing resource measurements are null. Reusing an output directory clears generated results before the new run; an interrupted/initialising receipt is not success.

## Hosted and official-device lanes

`Strict CI` runs on public pull requests, main pushes, merge groups, weekly schedules and manual dispatch. Its Ubuntu job uses the same strict command. It has bounded concurrency/timeouts, disabled persisted checkout credentials and immutable action pins. Coverage upload uses Codecov OIDC and fails on upload error. The template coverage policy is unchanged: project target `auto` with **1%** threshold, patch target **90%**. A generated report does not prove upload or provider acceptance; preserve those separate statuses in the receiving receipt.

A separate read-only PR dependency-review job uses the official action pinned at `bbc44d14a204704ccc493733616cd1e93a0321ec` and blocks low-or-higher known vulnerabilities across runtime, development and unknown scopes. It posts no PR comments and makes no invented licence-policy choice. The local Cargo.lock audit and audit of the installed, frozen Python developer environment remain active alongside this diff review. The Python result applies to the qualified platform/environment; it does not claim to audit every alternate platform or extra recorded in the multi-platform lockfile.

The separate `privacy-and-secrets` job calls the reviewed central Presidio/Gitleaks action at `b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4`. It preserves the standard's commit-range/full-history semantics, value-free findings and reported coverage gaps. Current-source Gitleaks is an additional local check, not a replacement for Presidio. For pre-push use, install and invoke the pinned central guard as documented in its [local hook guidance](https://github.com/edithatogo/repository-standards/blob/b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4/privacy/local-hooks.md); no hook installation is implied by these committed files.

`Official local qualification` remains manual and accepts only this repository's reviewed main revision. It invokes the same harness on the selected macOS ARM64, Windows x64 or Linux x64 official runner and preserves the actual outcome. Each native command has its return code checked by Python, so a later PowerShell command cannot hide an earlier failure. No runner has been registered or activated by this increment, and no cloud result closes `T00.local_runner`.

The publication workflow stays separately authorised and source-bound. Verification has no Hub write token and never runs a real upload. The publisher's malformed-manifest failure handling is tested to preserve source files. Its historical metadata verifier separately pins the original reviewed publisher and the current reviewed implementation, without relabelling historical release bytes.

## Central standards and template reconciliation

| Source | Inspected revision | Applied decision |
|---|---|---|
| [repository-standards](https://github.com/edithatogo/repository-standards/tree/e6425228dea09637eb0a45a3787421e7bce42b3b) | `e6425228dea09637eb0a45a3787421e7bce42b3b` | Single policy authority; proportionate executable gates, privacy, dependency evidence, immutable actions and truthful receipts |
| [template-solo-rust](https://github.com/edithatogo/template-solo-rust/tree/d59246472351fc72a82a6ba535a4255af3a2fa45) | `d59246472351fc72a82a6ba535a4255af3a2fa45` | Rust quality/coverage policy and single-maintainer model |
| [template-solo-data](https://github.com/edithatogo/template-solo-data/tree/a4b2b2aa06cba3bc875ca34f806074d2f4f7ebb3) | `a4b2b2aa06cba3bc875ca34f806074d2f4f7ebb3` | Data boundary, Python coverage and published-artifact provenance |

The central reusable Rust job assumes a root Cargo manifest and floating stable Rust. This repository instead has a catalogue subproject and a previously qualified 1.95.0 toolchain; a thin local caller is therefore justified. The strict Python choice is a local implementation decision, not a claim that central policy mandates a particular type checker. Existing account community defaults should be inherited where GitHub supports inheritance. Preserve existing Renovate onboarding PR #1 rather than introduce another dependency bot.

## Outstanding dispositions

| Item | Disposition and receiving owner |
|---|---|
| Atlas code licence | **Unresolved.** The maintainer must choose or identify applicable terms. Do not copy a template licence or infer rights from public visibility. This prevents a claim of complete Community Standards/licence conformance. Existing source-specific dataset rights remain separate. |
| Hosted execution/provider receipt | Requires observed runs at the PR commit and actual Codecov result; workflow configuration alone is insufficient. CI integrator owns reconciliation. |
| Stable required-check enforcement | GitHub's repository/branch APIs were read on 22 November 2026: no rulesets were returned, `main` was unprotected, and required status contexts were empty. After observed successful jobs, the repository administrator can require the exact names. No branch protection or ruleset change is claimed here; preserve zero mandatory human approvals and existing protections. |
| Official device qualification | Trusted device operator must run the configured official workflow and retain its revision-bound receipt. |
| Published scientific releases | Remain behind existing source/data/method/N1/device gates; add release provenance/checksums for a real release, not speculative packaging. |

Keep T00/T01/T07 scientific parents open. Ready source-contract and synthetic method work can continue while external prerequisites remain unavailable. No blanket coverage waivers, statistical tolerance changes, package ports, GPU framework, managed lakehouse or alternative orchestrator is introduced by this CI increment.
