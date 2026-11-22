# Agent instructions

Read `conductor/index.md` and the current track **before** any work. Follow central `edithatogo/repository-standards` and the repo-local `conductor/workflow.md`. One owner/writer per track and path; do not overwrite competing work. No mandatory human approval where existing single-maintainer automated gates suffice.

**Current authorisation: documentation and planning only.** Do not implement pipelines, install analytical dependencies, fetch datasets, run analyses, make publication claims, create releases or deploy services without a subsequent scoped request.

Ponytail full: prefer already-qualified tools, simplest correct approach, smallest justified change. Refuse speculative frameworks, custom statistical ports, GPU kernels, live lakehouse services or Python/R/Julia embedding unless a benchmark demonstrates need. Preserve data rights, provenance, sample-level independence and explicit 'unknown' statuses.

For **every analysis**, perform the dated N0/N1 novelty, journal-fit and dependency checks before execution, N2 after results, and N3 before journal submission; see `research/novelty-priority-protocol.md`. Do not claim a missed publication was absent or change frozen N1 outcomes after a competing article. Python may be used only when justified; Mojo is held. Polars/petgraph are conditional preferred Rust libraries, never mandatory upfront.

Before marking a track completed: record exact source identifiers and checksums/commits when available; tests *actually run* and failures; retained limitations; manuscript implication and any publication/ethics/rights gate. A plan is not an implementation receipt.
