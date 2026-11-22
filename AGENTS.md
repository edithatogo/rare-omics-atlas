# Agent instructions

Read `conductor/index.md` and the current track **before** any work. Follow central `edithatogo/repository-standards` and the repo-local `conductor/workflow.md`. One owner/writer per track and path; do not overwrite competing work. No mandatory human approval where existing single-maintainer automated gates suffice.

**Current authorisation: documentation and planning only.** Do not implement pipelines, install analytical dependencies, fetch datasets, run analyses, make publication claims, create releases or deploy services without a subsequent scoped request.

Future local development qualification must use the **official GitHub Actions self-hosted runner**, with actual run evidence on the relevant device/OS; see `research/local-development.md`. An emulator, cloud shell or configured-but-unrun workflow is not equivalent. Do not route untrusted public PR code onto personal machines. No runner registration/activation has been verified here.

Ponytail full: prefer existing suitable tools, the simplest correct approach and the smallest justified change. Avoid speculative frameworks, ports, GPU kernels, lakehouse services and language embedding. Any future custom implementation requires a concrete scientific, deployment, maintenance or resource need; claims of performance benefit require benchmarks. Preserve data rights, provenance, sample-level independence and explicit 'unknown' statuses.

For **every analysis**, perform the dated N0/N1 novelty, journal-fit and dependency checks before execution, N2 after results, and N3 before journal submission; see `research/novelty-priority-protocol.md`. Do not claim a missed publication was absent or change frozen N1 outcomes after a competing article.

**Language preference: Rust > Julia or Mojo > Python > R**, among scientifically suitable implementations. Use `research/language-dependency-triage.md` and `research/rust-candidate-audit.md`; distinguish a native engine from its wrapper and a runtime dependency from a test oracle. Existing C/C++/Fortran or specialist-language exceptions require an actual capability/deployment benefit. No unvalidated statistical substitution, preemptive port, or mandatory collection of candidate packages. Apply Orphanet/JIMD/JIMD Reports routing from `research/journals.md` to the actual clinical question.

Use `research/methylation-backend-audit.md` before selecting limma-rust or SeSAMe2. Resolve identity, uncertainty, missingness/rank and actual-export contracts before scientific admission. Mojo is outside the active initial stack; Python remains an optional specialist dependency. Bundle experiments under `research/experiment-publication-plan.md`; a capability or port does not require its own paper. Apply `research/resources-hosting-reuse.md` before any new annotation source or Hugging Face release.

Before marking a track completed: record exact source identifiers and checksums/commits when available; tests *actually run* and failures; retained limitations; manuscript implication and any publication/ethics/rights gate. A plan is not an implementation receipt.

