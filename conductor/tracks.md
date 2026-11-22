# Tracks registry

Status: **all tracks planned**. Files here are scoped specifications, not delivered code, executed tests or accepted scientific evidence.

| Track | Name | Dependency | Status |
|---|---|---|---|
| [T00](tracks/t00-governance/index.md) | Repository governance and Conductor activation | None | planned |
| [T01](tracks/t01-sources/index.md) | Public source, ontology and prior-art qualification | T00 | planned |
| [T02](tracks/t02-kabuki/index.md) | Kabuki cohort/pathway reproducibility | T01 | planned |
| [T03](tracks/t03-comparison/index.md) | Cross-disease methylation comparisons | T01 | planned |
| [T04](tracks/t04-hierarchical/index.md) | Hierarchical cross-disease inference | T01 + T03 | planned |
| [T05](tracks/t05-multiomics/index.md) | Matched and disease-matched multimodal validation | T01 (+ T02/T03 for model linkage) | planned |
| [T06](tracks/t06-toxin/index.md) | Genetic mechanism × toxin perturbation feasibility | T01, separate experiment gate | planned |
| [T07](tracks/t07-backend-qualification/index.md) | Conditional backend qualification (Rust preferred) | T01 + named scientific stage/portability/resource requirement | deferred |

Every analysis is subject to the shared [N0/N1 before, N2 after and N3 submission review](../research/novelty-priority-protocol.md), including literature novelty, new datasets, journal fit, source independence and dependency retain/swap/remove. These gates can reorder, narrow, combine or stop a track without rewriting already frozen analyses.

Recommended **default, not fixed**: T00 → T01 → T02 as reference; T03 or T05 next according to paired data and clinical relevance; T04 after disease-qualified effects; T06 only after quantitative independent data. Avoid parallel write ownership collisions.

T07 is conditional: no automatic ports or monitoring process. Prefer existing Rust tools under the language hierarchy, retain independent numerical oracles, and use the dated audit to distinguish validation work from missing methods. Qualified C exceptions such as SeSAMe2 can share the same admission process.

