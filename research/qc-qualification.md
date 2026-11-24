# HM450 QC and detection qualification

Updated 23 November 2026. The explicit [native v2 successor](native-qc-qualification.md)
now passes the bounded complete-universe technical contract; see its
[executed evidence](qualification/t07-native-qc-2026-11-23.md). This page retains
the v1 reproduction and original failed result.

The bounded T07c receiver is implemented. Its actual
full-panel comparison **fails and holds the method**: four of the 65 native R QC
fields differ at minimum beads zero. All complete ordered p-value exports match
their declared serialization reference. The extra GCT field qualifies published
extension-list arithmetic only; native R GCT uses different probe sets.
See the [dated evidence](qualification/t07-qc-2026-11-23.md) and
[machine-readable contract](contracts/sesame-hm450-qc-v1.json).

## What this command checks

The existing C producer owns numerical implementation; Atlas owns this receiving
boundary. The command reuses the raw/Q qualifier's source, input, annotation and
command helpers and Python's standard library. No production package, Rust port,
R embedding or new service is added. R remains an independent test oracle.

| Boundary | Required comparison |
|---|---|
| Source and data | Exact clean C/YAME revisions and all existing raw/Q input hashes; exact QC references, R revision, recipe path/scope and recipe bytes |
| Annotation | All 486,427 ordered HM450 probe IDs and the previously pinned annotation contract; no intersection or discarded mismatch |
| Native QC | All 65 independently calculated R fields, joined by name to the exact C header; 26 integer counts remain integers, including values beyond binary64's exact range |
| Floating QC | Exact missingness and ten-significant-digit serialization of independent R values; no fitted tolerance or exempted field |
| GCT | One additional field calculated independently from the pinned published extension lists; distinct from native `bisConversionControl` |
| Detection | Full raw and QCD-stage reference vectors against actual raw/QCDPB production p-value exports; exact NA and binary32-to-six-digit serialization |
| Detection decisions | No changed decision at the predeclared upstream 0.05 boundary; this does not select a study rejection threshold |
| Repeatability | Raw/QCDPB exports at one and two threads; identical raw QC across all four, and identical binary/text p-values within each stage |
| End integrity | Recheck source, assets, references, contract, R recipe, checker/helpers and built binaries after consumption |
| Failure | New output directory only; nonzero exit and failed receipt for a malformed/missing input, command error, integrity drift or comparison mismatch |

QC is calculated from the raw signals; its beta summaries use **D→B→P**. The
QCDPB production p-value output captures pOOBAH after **Q→C→D**, before P/B change
the downstream signals. It is not a p-value recomputed from a final beta export.
The production contract explicitly uses minimum beads **zero**. A separate
minimum-three diagnostic checks native bead handling without changing that
contract or selecting a scientific sample/probe exclusion policy.

## Reproduce the independent reference

First follow the existing [source/runtime reproduction recipe](qualification/t07-reference-2026-11-23/REFERENCE_REPRODUCTION.md).
It pins the original technical IDAT pair, annotation, unchanged R source files,
R 4.5.2 runtime, packages and serial preprocessCore 1.72.0 build. Reuse its
`PREPROCESS_DATA`, `PREPROCESS_SCRIPTS`, `PREPROCESS_R_SOURCE`, `PREPROCESS_SOURCE`,
`PREPROCESS_R_ENV`, `PREPROCESS_R_LIBRARY` and `PREPROCESS_MAMBA` variables.
Each output directory below must be new. No native R package installation is
claimed: the exact source functions are loaded with explicit local cache getters.

The source-level driver uses unchanged `readIDAT` and `chipAddressToSignal` with
the explicit HM450 address object. This avoids `readIDATpair`'s unrelated platform
autodetection cache requirement. `sesameQC_calcStats`, `pOOBAH` and `prepSesame`
remain unchanged. The GCT arithmetic is separately labelled in every receipt.

```sh
export R_LIBS_USER="$PREPROCESS_R_LIBRARY"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export QC_REFERENCE_ZERO="$PREPROCESS_DATA/qc-reference/r-beads0"
export QC_REFERENCE_THREE="$PREPROCESS_DATA/qc-reference/r-beads3"

"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  "$PREPROCESS_SCRIPTS/run_qc_reference.R" "$PREPROCESS_DATA" \
  "$PREPROCESS_R_SOURCE" "$QC_REFERENCE_ZERO" 0

"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  "$PREPROCESS_SCRIPTS/run_qc_reference.R" "$PREPROCESS_DATA" \
  "$PREPROCESS_R_SOURCE" "$QC_REFERENCE_THREE" 3
```

Create the deterministic gzip reference with the same streaming compressor used
for the retained receipt, then validate both exact contract pins. Run from Atlas:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import gzip
import hashlib
import json
import os
import shutil
from pathlib import Path

root = Path(os.environ["QC_REFERENCE_ZERO"])
target = root / "pvalues-reference.tsv.gz"
with (root / "pvalues-reference.tsv").open("rb") as source, target.open("xb") as raw:
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
        shutil.copyfileobj(source, compressed)
contract = json.loads(Path("research/contracts/sesame-hm450-qc-v1.json").read_text())
for name, expected in contract["reference_files"].items():
    data = (root / name).read_bytes()
    if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
        raise SystemExit(f"reference bytes differ: {name}")
print("Both exact QC reference pins match")
PY
```

Do not replace differing bytes by editing the contract. Diagnose source/runtime,
input, compression or method differences and retain the failed attempt.

## Run the production receiving boundary

Use the independent raw/Q reference from the preceding recipe. The C checkout
must be at the existing exact source/YAME pins with no tracked changes. The
command performs a clean build and executes all four real exports:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/qualify_qc.py \
  --checkout "$PREPROCESS_SOURCE" \
  --data-root "$PREPROCESS_DATA" \
  --raw-reference "$PREPROCESS_DATA/oracle/python-raw-q/expected-raw-q.tsv.gz" \
  --reference-root "$QC_REFERENCE_ZERO" \
  --output artifacts/verification/hm450-qc-replay
```

At the documented source/reference pins this command returns **1**, with
`status: failed` in `qc-contract.json`, because native QC parity is not satisfied.
The receipt retains all field comparisons, all four complete p-value outcomes,
commands, hashes and the error. Do not ignore the exit or relabel the receiving
gate as passed. The repository's regression tests separately pass when they
correctly detect and preserve this held-method result.

Rerun this explicit qualification when the selected source, contract, checker,
recipe or reference changes. Ordinary cross-platform Atlas CI includes checker
regressions and coverage; this POSIX C build and its external reference assets
remain an explicit technical acceptance lane.

## Replay bead and GCT diagnostics

The independent bead script reads original IDAT field 107 and compares every
address count and derived initial mask against the R reference. It uses explicit
failure checks, so Python `-O` cannot disable acceptance:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python -O scripts/tests/check_beads.py \
  --data-root "$PREPROCESS_DATA" \
  --reference-zero "$QC_REFERENCE_ZERO" \
  --reference-three "$QC_REFERENCE_THREE" \
  --output artifacts/verification/hm450-bead-replay
```

The native GCT diagnosis uses the separately retrieved `HM450.probeInfo` object.
The exact official URL, content hash, metadata revision and retrieval outcome are
recorded in [probeInfo provenance](qualification/t07-qc-reference-2026-11-23/probeinfo-source.json)
and its [transfer receipt](qualification/t07-qc-reference-2026-11-23/probeinfo-path-download.json).
The earlier raw/Q asset downloader does not fetch this extra object. The command
below reads its exact URL/size/hash from the committed transfer receipt, validates
the bytes before writing and reuses an existing file only when it matches:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import hashlib
import json
import os
import urllib.request
from pathlib import Path

pin = json.loads(Path(
    "research/qualification/t07-qc-reference-2026-11-23/probeinfo-path-download.json"
).read_text())
target = Path(os.environ["PREPROCESS_DATA"]) / "r-assets/HM450.probeInfo.rda"
existing = target.exists()
if existing:
    data = target.read_bytes()
else:
    with urllib.request.urlopen(pin["url"], timeout=60) as response:
        data = response.read(pin["size_bytes"] + 1)
if len(data) != pin["size_bytes"] or hashlib.sha256(data).hexdigest() != pin["sha256"]:
    raise SystemExit("HM450.probeInfo bytes differ; no new object written")
if not existing:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(data)
print("Exact HM450.probeInfo size and SHA-256 verified")
PY
```

Then invoke the diagnostic using that verified object:

```sh
"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  "$PREPROCESS_SCRIPTS/compare_gct_lineage.R" "$PREPROCESS_R_SOURCE" \
  "$QC_REFERENCE_ZERO/raw-sdf.rds" "$PREPROCESS_DATA/r-assets/HM450.probeInfo.rda" \
  "$PREPROCESS_DATA/assets/HM450/HM450.typeI_ext.tsv.gz" \
  "$PREPROCESS_DATA/qc-reference/gct-lineage"
```

This produces both GCT values, the complete named curated/published sets and
set-difference counts. Different curations remain different references even when
each calculation is reproducible.

## Successor decision and next boundary

T07 selected [native R missing-signal semantics and curated GCT](native-qc-semantics.md)
and implemented the [explicit v2 successor](native-qc-qualification.md). Its
complete technical run passes while this v1 result stays failed. Study
sample/probe rejection rules and full QCDPB beta/M precision budgets remain unselected.
Keep T01 identity, overlap, molecular-subset and covariate curation in parallel.

This is technical qualification on an unrelated public author fixture. No
disease contrast, participant admission, clinical replication result, frozen
scientific N1 or publication claim follows from it. Actual official owner-device
execution and applicable institutional determinations remain required by the
existing parent tracks. Access to some original cohort supplements is currently
blocked; available local technical work is not generally exhausted.
