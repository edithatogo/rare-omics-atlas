# T07c — HM450 QC and detection receiving contract

- [Specification](spec.md)
- [Executable plan](plan.md)
- [Parent T07](../../tracks/t07-backend-qualification/index.md)

This bounded increment implements and executes the next technical receiving
boundary. A completed checker can return a held upstream method; it cannot
convert a failed QC comparison into scientific acceptance.

Implementation and independent review are complete, with all 34 strict candidate
gates passed. The actual committing hook rechecks the final archive/evidence
bytes; immutable hosted integration evidence is recorded in the associated PR.
The production QC qualification remains failed and the selected method held.
