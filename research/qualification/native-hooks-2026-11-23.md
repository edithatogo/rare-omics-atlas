# Native pre-commit hook: installation and canary evidence

Date: 23 November 2026. Scope: the working clone used for this implementation,
plus disposable local Git repositories. Other clones and owner devices have not
been qualified by this receipt.

## Implemented and installed

The [native wrapper](../../.githooks/pre-commit) invokes the
[installer/runner](../../scripts/hooks.py) through the existing pinned uv/Python
environment. Installation was actually executed in this clone and read back:
`core.hooksPath = .githooks`, with three absolute local configuration values for
the external scanner checkout, isolated Python and Gitleaks binary. These paths
are local configuration, not portable committed settings.

The scanner checkout is pinned to
[`b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4`](https://github.com/edithatogo/repository-standards/tree/b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4),
matching the hosted privacy workflow. Its actual Git root, clean source and
normal index flags are verified. The isolated runtime is Python **3.15.2** with
Gitleaks **8.30.1**. Tool paths must remain outside the candidate repository,
including their resolved targets. Existing conflicting hooks or hook-path
configuration are refused rather than replaced.

The runner requires the tracked working tree to equal the candidate index and
rejects untracked nonignored candidate files, assume-unchanged, skip-worktree and
unresolved entries. It captures the actual index tree, including Git's temporary
index for `commit -a` or `--only`. A disposable shared-object Git snapshot makes
that exact tree available to the central `--staged` guard, whose own environment
sanitizer removes alternate-index variables. The runner then invokes the existing
full strict verifier with `--deep`, and checks the candidate tree, HEAD and
working tree again. Foreign Git commands and the verifier's disposable test
repositories are isolated from the committing process's Git-local environment.

## Executed checks

The [13 hook regression tests](../../scripts/tests/test_hooks.py) passed. They
exercise actual disposable Git commits, installation conflicts, temporary
indexes, hidden edits, scanner and verifier failures, candidate mutation and
missing tooling/configuration. Ruff and strict Pyright passed. The hook helper's
measured line/branch coverage was **97%**: 142 statements, two missed statements,
50 branches and three partially covered branches. This is a measurement from
the hook tests, not the repository's complete strict-gate result.

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python -m unittest discover -s scripts/tests -p test_hooks.py -v
```

The actual tracked wrapper was also tested with the real pinned central scanner
in disposable repositories, using its established synthetic regression canary:

| Case | Observed outcome |
|---|---|
| Valid candidate committed with `git commit -a` | Real staged privacy scan and synthetic verifier ran; commit succeeded |
| Synthetic PAT staged only in an alternate index; normal index remained clean | Gitleaks blocked the commit; verifier did not run; HEAD was unchanged |
| Clean privacy scan followed by verifier exit 7 | Commit failed; HEAD was unchanged |

The disposable verifier deliberately used a small success/failure fixture. This
proves native Git invocation, exact staged scanning and failure propagation;
**the real repository's full verification during its actual hook-driven commit
remained pending at this receipt's creation**. The later strict receipt and
commit outcome must establish that separate result. No canary was pushed or
retained in repository history, and matched values were not logged.

## Retained boundaries

Installation must be repeated and tested in every clone using the
[CI instructions](../ci-plan.md) and the pinned
[central hook policy](https://github.com/edithatogo/repository-standards/blob/b30b07bcdaa6aebad2c6a57a4d0adc3616dabfe4/privacy/local-hooks.md).
Git permits local hook bypass; server-side required checks remain separate.
The scanner's stated coverage limitations still apply. These checks do not
establish actual owner-device acceptance, source rights, clinical de-identification
or scientific admission.
