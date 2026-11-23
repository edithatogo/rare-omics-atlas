# Selected synthetic inference contract

Updated 23 November 2026. **Selection is bounded to synthetic numerical/file qualification.** The scientific preprocessing/inference route remains unaccepted.

The selected contract is `limma-named-contrasts-v1` from the existing MassDynamics-derived owner fork. Its authoritative specification is `docs/named-consumer-v1.md` at the exact commit recorded in [the atlas pin](../../../research/contracts/limma-named-v1.json). [Repository integration](../../../research/repository-integration.md) defines ownership, update order, actual commands and receiving evidence.

## Selected operation and reference

Select the existing unweighted least-squares, contrast and default nonrobust/nontrend eBayes operations through the new named boundary. Preserve the whole feature universe for moderation and each complete contrast family for BH. The producer supplies ordinary and moderated uncertainty, total/residual df, raw/adjusted p-values, 95% intervals and explicit non-estimability.

The committed public synthetic `complete` and `missing` references come from the previously independently reproduced R 4.5.0 / limma 3.68.5 / statmod 1.5.2 recipe. Receiving qualification reads those unchanged outputs. This increment does not regenerate them or count agreement between Rust implementations as independent reference evidence.

The producer's canonical document freezes axes, column-major float64 inputs, supported missingness, rejection of unsupported rank/df/shape domains, output ordering and unchanged field-specific tolerances. The atlas receiver validates actual CSV/JSON bytes. A second scale declaration exercises transport only.

## Executable receiver

Run from the atlas root with the pinned development tools:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/qualify_limma.py \
  --output artifacts/verification/limma-receiving
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

The first command obtains the exact pinned producer and runs `cargo +1.95.0 run --locked --example export_named -- FIXTURE NEW_OUTPUT SCALE` for each declared synthetic case. Its receipt records actual paths, file hashes, commands and outcomes. The second makes that receiving operation a mandatory gate alongside the rest of the local/hosted checks. Nonzero commands, unavailable source or malformed/incorrect output fail.

## Remaining selection work

The [HM450 raw/Q contract](../../../research/preprocessing-qualification.md)
now specifies one bounded SeSAMe2 technical fixture, exact array assets,
independent reference and actual export checks. T07.02 still needs the complete
selected preprocessing/QC route, scientific precision budget and any additional
platform/annotation consumers. The numerical core does not supply preprocessing.
Production matrix ingestion is outside the synthetic example's contract.

T01 participant independence, molecular eligibility and applicable institutional determination remain unresolved. No disease-conditioned comparison has run. T07.02b N1 must freeze the scientific estimand, features, covariates, missingness, discovery/replication roles and acceptance bounds before such work. The official actual-device receipt remains external.

The bounded synthetic path can complete without those independent prerequisites; it must not be renamed scientific backend acceptance. Parent T07.02–.06 retain their unmet criteria.
