# Research operating procedure — Ponytail full

1. Read active track `spec.md` and `plan.md`; check repository state, issue/PR ownership and source truth. **No work outside approved track.**
2. Independently record **public landing/download listings**, **actual download/checksum**, **source-specific consent/rights**, and **institutional ethics/governance determination** as four separate statuses. Verify sample-level independence, tissue/platform, molecular diagnosis and assay controls; unknown means hold. Refer to `research/source-access-ethics.md`.
3. For **each analysis**, run and record N0/N1 *before execution* per [novelty/priority protocol](../research/novelty-priority-protocol.md): current published/early-online/preprint studies and new datasets, exact dataset or method overlap, clinical journal fit and justified priority. Freeze the scientific contrast, estimand, covariates, outcomes, negative controls, splits and provisional journal. A search not executed is a hold, not a negative finding.
4. Start with published validated methods and simplest baselines. Among suitable implementations use **Rust > Julia or Mojo > Python > R**. Read the [candidate audit](../research/rust-candidate-audit.md); prefer existing CLIs/libraries and distinguish the runtime engine from its interface and test oracle.
5. Preserve stage-level scientific contracts (`research/backend-replacement-policy.md`). Compare exact inputs and algorithmic outputs, validate numerically, note resampling and leakage boundaries. A replacement must pass its scientific/consumer contract and have acceptable resource/deployment/maintenance cost. Rust is preferred for suitable new stages without a mandatory speed win. File-level Arrow/Parquet interchange is sufficient. Data QC failure blocks analyses, not merely triggers warnings.
6. **After each analysis** perform N2, rechecking intervening publications, datasets, methods and journal relevance; record replicate/reframe/combine/stop decision without revising the frozen protocol. Perform N3 immediately before submission or transfer. At both pre- and post-analysis gates assess retaining, removing or replacing dependencies using [Ponytail language triage](../research/language-dependency-triage.md); do not introduce a package without an identified consumer, scientific oracle and evidence. Record actual commands/checks when later authorised.
7. Use one source of policy: `edithatogo/repository-standards`. Adopt GitHub shared defaults and templates only when applicable. No second competing Conductor installation.
8. Future local development qualification uses the official GitHub Actions self-hosted runner on the relevant target OS/architecture, with a revision-bound observed run. Follow [local development](../research/local-development.md); no untrusted PR execution on personal machines, emulator substitution or unobserved success claim.

### Medallion decision

**Approved:** logical Bronze (raw originals/rights/hash), Silver (qualified observations and ontology maps), Gold (published analysis tables/results). **Deferred:** a service-backed lakehouse, managed catalogues, orchestration, Fabric/Databricks/Delta/Iceberg, platinum layer, data warehouse schemas until materially needed.

Follow [hosting and resource decisions](../research/resources-hosting-reuse.md). Reuse the existing Hugging Face estate registry and eligible MONDO/Orphadata snapshots. Medallion promotion does not expand rights. Begin public distribution with source manifests and eligible aggregate outputs; any actual human-data upload needs the applicable rights, disclosure and hosting determination. No upload is authorised merely by this plan.

### Publication boundaries

Check each journal's live aims, article categories, APC, indexing and policies at submission; scope fit is not acceptance likelihood. Avoid splitting one modest study into redundant publications.

Use the [experiment/publication plan](../research/experiment-publication-plan.md). E0/E2/E3 form the initial clinical bundle; E1 and backend comparisons ordinarily support it. E4–E6 are conditional extensions or a combined later study, not an automatic paper per track. If novelty overlaps, combine, reframe as justified replication, retain as infrastructure or stop. Added ontologies, Rust ports and Enzyme alone do not constitute clinical novelty.

