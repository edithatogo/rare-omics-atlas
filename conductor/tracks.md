# Tracks registry

Status: **all tracks planned**. Files here are scoped specifications, not delivered code, executed tests or accepted scientific evidence.

| Track | Name | Dependency | Status |
|---|---|---|---|
| [T00](tracks/t00-governance/index.md) | Repository governance and Conductor activation | None | planned |
| [T01](tracks/t01-sources/index.md) | Public source, ontology and prior-art qualification | T00 | planned |
| [T02](tracks/t02-kabuki/index.md) | Kabuki cohort/pathway reproducibility | T01 | planned |
| [T03](tracks/t03-comparison/index.md) | Cross-disease methylation comparisons | T01 | planned |
| [T04](tracks/t04-hierarchical/index.md) | Julia hierarchical cross-disease inference | T01 + T03 | planned |
| [T05](tracks/t05-multiomics/index.md) | Matched and disease-matched multimodal validation | T01 (+ T02/T03 for model linkage) | planned |
| [T06](tracks/t06-toxin/index.md) | Genetic mechanism × toxin perturbation feasibility | T01, separate experiment gate | planned |

Recommended work: T00 → T01 → T02; then T03 and separately T05; T04 after disease-qualified effects; T06 only after quantitative independent data. Avoid parallel write ownership collisions.
