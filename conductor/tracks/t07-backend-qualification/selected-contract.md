# Selected method contracts and receiving limits

Updated 25 November 2026 Australia/Brisbane. **Native R/Bioconductor is the first-science candidate; cohort use remains unaccepted.** This document consolidates its implemented qualification boundary and retains the separately accepted synthetic Rust contract. The [N1 draft](n1.md) is not frozen.

## Native reference candidate

The executable authority is [qualify_reference.R](../../../scripts/tests/qualify_reference.R), run by the existing [native-reference workflow](../../../.github/workflows/native-reference.yml). The [receiving receipt](../../../research/qualification/t07-native-reference-candidate.md) records exact revisions, artifacts, failures and accepted operations; acceptance never transfers automatically to changed code or assets.

| Component | Existing selected qualification |
|---|---|
| Runtime | Bioconductor 3.22 Linux AMD64 image `bioconductor/bioconductor_docker@sha256:67ab741591c5cd068f8993ca5f0371794c300da9cc5e0b3b2c1c90c9058e4c6f`; observed R 4.5.2, script permits R 4.5.x. Release repositories resolve dependencies; installed versions and resource hashes are recorded, not a complete transitive lock. |
| Core packages | SeSAMe 1.28.1, sesameData 1.28.0, limma 3.66.0, missMethyl 1.44.0. Enrichment additionally checks BiasedUrn 2.0.12, GO.db/org.Hs.eg.db 3.22.0, minfi 1.56.0 and HM450 hg19 annotation 0.6.1. |
| Input identity | Unrelated author HM450 pair `3999492009_R01C01` and previous `HM450.ordering.tsv.gz`; exact original URLs, byte counts and SHA-256 in the [existing input contract](../../../research/contracts/sesame-hm450-raw-q-v1.json). Its historical minimum-beads-zero raw/Q contract is unchanged. Native release probe inventory is checked separately; the observed 850 IDs unique to each release prohibit an assumed identical universe. |
| Preprocessing | Historical legacy route: native `readIDATpair`, `prepSesame(...,"QCDPB")`, `pOOBAH`, `getBetas` and signal extraction; its intended negative-control backgrounds remain unqualified pending corrected-route replay. The successor scientific-QC exercise uses `min_beads=3`, native recommended masks and native hg38 probe ranges for a fixed autosomal CpG denominator, independently of each sample's detection, beads or beta. Detection must be finite and within [0,0.05]; only finite interior beta yields `M=log2(beta/(1-beta))`. No clipping or denominator shrinkage after sample failure. |
| QC receiving limit | Retain eligible IDs, coordinate/source-object identities and hashes, disaggregated rejection reasons and correctly labelled control measurements. [PR #23's historical run](../../../research/qualification/ontology-context-2026-11-24.md) records legacy-route execution and a fixed-denominator audit: 366,308/408,966 observations labelled valid (89.5693%), with the exclusion partition retained. All 848 exported control `Type` values are malformed and numeric; they do not validate control identities or intended pOOBAH/noob negative-control backgrounds. The artifacts do not separately export the `negControls(raw3)` row count. Receive the exact-source corrected-route replay proposed in [PR #24](https://github.com/edithatogo/rare-omics-atlas/pull/24) before qualifying those backgrounds. The prospective >=0.95 criterion was not met; that clinical threshold and control ranges remain unvalidated. The predecessor minfi-lookup failure remains historical. |
| Inference | Synthetic named 128-feature/12-sample M matrix, rank-four design and one missing observation. Native `lmFit` and `eBayes(trend=FALSE,robust=FALSE)` are checked against OLS, scaled moderated SE, two-sided p-values, 95% intervals and complete-family BH. This does not qualify arbitrary missingness, rank deficiency, weights, blocks or cohort ingestion. |
| Enrichment | Native `gometh(collection="GO")` and `gsameth` with the pinned [Reactome v98 collection](../../../research/contracts/reactome-v98.json), using `array.type="450K"`, `prior.prob=TRUE`, `equiv.cpg=TRUE`, `fract.counts=TRUE` and the same 4,000 tested/200 selected synthetic CpGs. Actual accepted families contain 13,817 GO terms and 2,178 eligible Reactome pathways. [Independent receiving checks](../../../research/qualification/ontology-context-2026-11-24.md) retain raw/received values, native integer versus fractional counts, coverage and full-family BH. Both raw native probability-domain results remain false; only the bounded corrected receivers pass. These are technical consumer qualifications, not a selected clinical pathway family or pathway activity. The installed annotation is restricted to intended tested rows before native flattening to bound memory; original `all.cpg` and selected inputs remain unchanged. Annotation presence and native gene mapping are reported separately. The hg19 gene annotation is used by CpG ID, separately from native hg38 QC coordinates; no cross-build region join is qualified. |

The workflow invokes `Rscript --vanilla /qualification.R /input /output STAGE /tmp/atlas-reference` for `install`, `technical`, `limma`, then `enrichment`, each in a fresh R process in the same container. Those paths are the workflow's real mounts; this is a technical/synthetic recipe, **not an implemented production cohort CLI**. Preserve source revision, input hashes, installed-package/session records, selected resource identities, numerical tables, resource measurements and container outcome. Hosted execution remains limited to authorised public-source, unrelated technical and synthetic inputs; HF supplies eligible storage only.

[PR #17](https://github.com/edithatogo/rare-omics-atlas/pull/17) received the bounded installed native operation. Its raw missMethyl probability-domain failure remains recorded: receive exactly one only for the proven integer-zero count boundary after native membership/fractional-count/odds checks; preserve raw and corrected tables, every GO ID/count, unchanged positive-count values and full-family BH. Invalid positive-count, missing/nonfinite or materially wrong zero-tail values still reject. This is not a general genome-wide enrichment acceptance or a replacement statistical method.

PR #23 records the historical legacy-route execution and fixed-denominator audit. Its later control-label defect means intended negative-control backgrounds remain unqualified; PR #24's proposed correction requires its own exact-source native replay and review. The independently accepted ontology and unchanged synthetic limma/enrichment operations retain their bounded scope. Before cohort QC, justify sample/probe/control rejection policies without disease outcomes, qualify exact production QC ingestion/output commands and receive applicable institution/environment and official-device evidence. T01 then receives source eligibility, actual cohort QC and post-QC design for analysis admission. Freeze N1 before disease-conditioned qualification or inference, with real production design/output commands and supported cases. A generic local strict run does not by itself exercise this installed native route. Exact region construction, region effects/uncertainty and EPIC consumers remain unselected; add no dependency without the chosen consumer and reference. The following synthetic contract stays independently available.

## Existing synthetic Rust inference contract

The selected contract is `limma-named-contrasts-v1` from the existing MassDynamics-derived owner fork. Its authoritative specification is `docs/named-consumer-v1.md` at the exact commit recorded in [the atlas pin](../../../research/contracts/limma-named-v1.json). [Repository integration](../../../research/repository-integration.md) defines ownership, update order, actual commands and receiving evidence.

### Selected operation and reference

Select the existing unweighted least-squares, contrast and default nonrobust/nontrend eBayes operations through the new named boundary. Preserve the whole feature universe for moderation and each complete contrast family for BH. The producer supplies ordinary and moderated uncertainty, total/residual df, raw/adjusted p-values, 95% intervals and explicit non-estimability.

The committed public synthetic `complete` and `missing` references come from the previously independently reproduced R 4.5.0 / limma 3.68.5 / statmod 1.5.2 recipe. Receiving qualification reads those unchanged outputs. This increment does not regenerate them or count agreement between Rust implementations as independent reference evidence.

The producer's canonical document freezes axes, column-major float64 inputs, supported missingness, rejection of unsupported rank/df/shape domains, output ordering and unchanged field-specific tolerances. The atlas receiver validates actual CSV/JSON bytes. A second scale declaration exercises transport only.

### Executable receiver

Run from the atlas root with the pinned development tools:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/qualify_limma.py \
  --output artifacts/verification/limma-receiving
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

The first command obtains the exact pinned producer and runs `cargo +1.95.0 run --locked --example export_named -- FIXTURE NEW_OUTPUT SCALE` for each declared synthetic case. Its receipt records actual paths, file hashes, commands and outcomes. The second makes that receiving operation a mandatory gate alongside the rest of the local/hosted checks. Nonzero commands, unavailable source or malformed/incorrect output fail.

### Remaining selection work

The [HM450 raw/Q contract](../../../research/preprocessing-qualification.md)
now specifies one bounded SeSAMe2 technical fixture, exact array assets,
independent reference and actual export checks. T07.02 still needs the complete
selected preprocessing/QC route, scientific precision budget and any additional
platform/annotation consumers. The numerical core does not supply preprocessing.
Production matrix ingestion is outside the synthetic example's contract.

T01's exact 11-case discovery source-molecular joins are received; participant independence, control provenance, post-QC estimability and applicable institutional determination remain unresolved. No disease-conditioned comparison has run. T07.02b [N1](n1.md) must freeze the scientific estimand, features, covariates, missingness, discovery/replication roles and acceptance bounds before such work. The official actual-device receipt remains external.

The bounded synthetic path can complete without those independent prerequisites; it must not be renamed scientific backend acceptance. Parent T07.02–.06 retain their unmet criteria.
