# Agent instructions

Read `conductor/index.md` and the current track **before** any work. Follow central `edithatogo/repository-standards` and the repo-local `conductor/workflow.md`. One owner/writer per track and path; do not overwrite competing work. No mandatory human approval where existing single-maintainer automated gates suffice.

**Current authorisation:** the owner's 22 November 2026 follow-up authorises continued implementation, review and archiving of completed tracks; API-backed dataset metadata; minimal Bronze/Silver/Gold storage integrated with GitHub and Hugging Face; bounded limma and SeSAMe Rust work after existing alternatives are checked; and reproducible local decision support. The earlier setup-only restriction is superseded. Complete ready work without repeated permission requests. Actual scientific use and distribution still follow the applicable source-specific conditions; a code test is not scientific or device acceptance. Do not start experimental perturbations, journal submissions, paid services of material cost or communications to third parties without their own authorisation.

Future local development qualification must use the **official GitHub Actions self-hosted runner**, with actual run evidence on the relevant device/OS; see `research/local-development.md`. An emulator, cloud shell or configured-but-unrun workflow is not equivalent. Do not route untrusted public PR code onto personal machines. No runner registration/activation has been verified here.

Ponytail full: prefer existing suitable tools, the simplest correct approach and the smallest justified change. Avoid speculative frameworks, ports, GPU kernels, lakehouse services and language embedding. Any custom implementation requires a concrete scientific, deployment, maintenance or resource need; claims of performance benefit require benchmarks. Preserve data rights, provenance, sample-level independence and explicit 'unknown' statuses.

Code verification starts strict: use `uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep` before and after code changes. Read `research/ci-plan.md` for pinned setup, coverage and separate privacy/provider/device outcomes. Missing tools or a failed gate must not become success. This is not the still-unobserved official owner-device acceptance.

Install the native pre-commit hook at the outset of each working clone using `scripts/hooks.py install` and the pinned external scanner paths in `research/ci-plan.md`. Commit through the installed hook with all intended changes staged; do not bypass or weaken it. Read `research/repository-integration.md` for ownership: limma owns its numerical contract, atlas pins and validates the actual exchange, and central standards remain the policy authority.

For **every analysis**, perform the dated N0/N1 novelty, journal-fit and dependency checks before execution, N2 after results, and N3 before journal submission; see `research/novelty-priority-protocol.md`. Do not claim a missed publication was absent or change frozen N1 outcomes after a competing article.

**Language preference: Rust > Julia > Python > R**, among scientifically suitable implementations. Use `research/language-dependency-triage.md` and `research/rust-candidate-audit.md`; distinguish a native engine from its wrapper and a runtime dependency from a test oracle. Existing C/C++/Fortran or specialist-language exceptions require an actual capability/deployment benefit. No unvalidated statistical substitution, preemptive port, or mandatory collection of candidate packages. Apply Orphanet/JIMD/JIMD Reports routing from `research/journals.md` to the actual clinical question.

Use `research/methylation-backend-audit.md` before selecting limma-rust or SeSAMe2. Resolve identity, uncertainty, missingness/rank and actual-export contracts before scientific admission. Python remains an optional specialist dependency. Bundle experiments under `research/experiment-publication-plan.md`; a capability or port does not require its own paper. Apply `research/resources-hosting-reuse.md` before any new annotation source or Hugging Face release.

Before marking a track completed: record exact source identifiers and checksums/commits when available; tests *actually run* and failures; retained limitations; manuscript implication and any publication/ethics/rights gate. A plan is not an implementation receipt.

## Incremental execution

Implement one ready, bounded track; review its actual outputs; archive it when its stated acceptance criteria pass, then start the next dependent track. The owner has already selected archiving, so do not ask again. Keep incomplete parent scientific tracks open. Independent source/literature review may run in parallel under separate path ownership. Estimate work in agent execution batches with input/exit criteria; record observed wall-clock duration when available. Do not use person-weeks/months or invent agent delivery times.
