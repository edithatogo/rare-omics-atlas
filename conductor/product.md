# Product / research definition

**Working name:** Rare-Venomics (current GitHub slug `rare-omics-atlas`; proposed rename `rare-venomics` is not yet executed).

**Overarching aim:** learn from public and appropriately governed molecular, experimental and clinical data about the causes and heterogeneity of human disease, including envenomation. One repository with separate scientific protocols, common source/rights/ontology/qualification tooling, and a single Conductor. Preserve existing history, dataset IDs, publication bundles and acceptance receipts.

## Stream A — Rare Disease (Rare Omics Atlas)

**Objective:** establish whether publicly accessible rare-disease methylation arrays support reproducible biology, and whether a mechanism-informed hierarchical model provides incremental, externally validated benefit over conventional per-disease analysis.

**Primary users:** clinical geneticists, translational researchers, computational biologists and clinicians working with rare developmental disorders. Later target-based toxinology studies are separate applications.

**Scientific outputs (conditional):** (1) independent Kabuki cohort reproducibility; (2) curated ontology-linked dataset catalogue; (3) cross-disease methylation/pathway comparisons; (4) disease-conditioned hierarchical model; (5) selected regulatory and genotype–toxin perturbation hypotheses.

These are capabilities and findings, not five manuscripts. Default to the [bundled clinical experiment plan](../research/experiment-publication-plan.md); metadata, backend parity and platform checks support the main clinical claim unless independently substantial evidence justifies another paper.

**Out of scope until evidence:** new methylation normalisation algorithm, bespoke R-to-Rust or Julia-to-Rust ports, universal biomedical knowledge graph, patient-specific digital twin, distributed cloud lakehouse, clinical diagnostic deployment.

**Not yet demonstrated:** literature priority, publication acceptance, cohort independence, real-world prediction, numerical equivalence of any cross-language replacement.


## Stream B — Toxinology

Study human envenomation and toxic responses through clinical epidemiology, existing venom and host-response omics, exposure ecology and evidence-graded comparative biology. Initial application: Irukandji syndrome; broader envenomations are conditional on useful public data and novel questions. Animal species, life stage, geography and documented molecular diversity are upstream explanatory context, analogous to an exposure-side genotype–phenotype relationship, not proof of patient-level causality. Do not undertake unrelated animal genomics, toxin engineering/optimisation or clinical deployment. See [V01](tracks/v01-toxinology/index.md).

## Shared and cross-stream

The existing conditional T06 is the bridge for host molecular susceptibility, not a second parallel track. Share catalogue, manifests, ontology references, rights, evidence extraction, method contracts, reproducible files, N0–N3 and CI. Maintain independent scientific admission and ownership. The broader Cairns envenomation research programme can reuse code and approved aggregate outputs; prospective registry, biobank, clinical linkage, wet lab and institutional data stay separately governed. No new data service, graph database, or duplicate statistical engine unless an actual consumer justifies it.
