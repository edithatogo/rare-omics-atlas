# Reproduce native HM450 QC v2

This is the executable successor to the preserved
[v1 receiver](qc-qualification.md). Read the
[predeclared semantics](native-qc-semantics.md) and
[v2 contract](contracts/sesame-hm450-qc-v2.json). V1 remains the default selection
and retains its original failed result. V2 is an explicit, bounded native R
compatibility contract on the same 486,427-probe technical fixture.

## Prerequisites and source preparation

Install the [native hook and strict tools](ci-plan.md) and pass the complete
strict baseline. Reuse the existing [source/runtime recipe](qualification/t07-reference-2026-11-23/REFERENCE_REPRODUCTION.md)
and the [QC reference recipe](qc-qualification.md#reproduce-the-independent-reference).
They define `PREPROCESS_SOURCE`, `PREPROCESS_DATA`, `PREPROCESS_R_SOURCE`,
`PREPROCESS_SCRIPTS`, `PREPROCESS_R_ENV`, `PREPROCESS_R_LIBRARY`,
`PREPROCESS_MAMBA` and `QC_REFERENCE_ZERO`.

Set `QC_RAW_REFERENCE` to the actual existing raw/Q reference produced by that
recipe. The documented fresh recipe writes `oracle/python-raw-q/expected-raw-q.tsv.gz`;
the retained execution used `oracle/generated-raw-q-portable-final/expected-raw-q.tsv.gz`.
Both must match the unchanged raw/Q contract's exact bytes. A missing path is a
failed attempt, not permission to regenerate or relabel a different reference.

From the Atlas root, create a **new** producer checkout using the already pinned
clean source. These local clones preserve the original source and failed outputs:

```sh
export QC_NATIVE_SOURCE="$PWD/artifacts/integration/sesame-native-qc-v2-replay"
export QC_RAW_REFERENCE="$PREPROCESS_DATA/oracle/python-raw-q/expected-raw-q.tsv.gz"
export QC_NATIVE_REFERENCE="$PREPROCESS_DATA/qc-reference/native-v2-replay"
export QC_PROBE_INFO="$PREPROCESS_DATA/r-assets/HM450.probeInfo.rda"

uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import os
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
import qualify_preprocessing as prep
from qualify_limma import read_object
prep.check_source(Path(os.environ["PREPROCESS_SOURCE"]), read_object(prep.CONTRACT))
PY

git clone --no-hardlinks --no-checkout "$PREPROCESS_SOURCE" "$QC_NATIVE_SOURCE"
git -C "$QC_NATIVE_SOURCE" remote set-url origin https://github.com/zhou-lab/sesame.git
git -C "$QC_NATIVE_SOURCE" checkout --detach f6713747181764e0b7a97b64c3c0d52ab9d82703
git clone --no-hardlinks "$PREPROCESS_SOURCE/YAME" "$QC_NATIVE_SOURCE/YAME"
git -C "$QC_NATIVE_SOURCE/YAME" remote set-url origin https://github.com/zhou-lab/YAME.git
git -C "$QC_NATIVE_SOURCE/YAME" checkout --detach e1e7b38e9f3b67981a78b1116e7312864677d69d
git -C "$QC_NATIVE_SOURCE" apply --index "$PWD/research/patches/sesame/native-qc-missing-signal.patch"
```

The resulting staged tree must be
`067d6fa93c34f326122a7c84bcad2ee3c3dc9112`. The canonical patch is 4,086 bytes,
SHA-256 `1566367d82b345cad6c6cd75fea9dc1a9384691999557b6b517b5ec7013e866b`.
The receiver checks the original HEADs and origins, complete canonical diff,
staged tree, clean worktree/YAME and visible index entries. It ignores caller Git
environment overrides and disables replacement objects. Do not commit a new
producer HEAD or apply unrelated changes in this qualification checkout.

The patch changes one functional assignment and its associated comments. Its
[upstream licence](patches/sesame/UPSTREAM-LICENSE.txt) remains applicable.

## Independent reference and native GCT input

Obtain `HM450.probeInfo.rda` using the existing
[pinned retrieval recipe](qc-qualification.md#replay-bead-and-gct-diagnostics).
The retained run read the same bytes from `qc-reference-20261123/HM450.probeInfo.rda`;
set `QC_PROBE_INFO` accordingly when reusing that object. Validate it and both
recipe files before execution:

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import os
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
import qualify_qc as qc
from qualify_limma import read_object
contract = read_object(qc.NATIVE_CONTRACT)
qc.prep.checked_file(Path(os.environ["QC_PROBE_INFO"]),
    qc.prep.object_field(qc.prep.object_field(contract, "gct_annotation"), "source_object_pin"))
qc.prep.checked_file(qc.ROOT / qc.REFERENCE_RECIPE,
    qc.prep.object_field(contract, "parent_reference_recipe_pin"))
qc.prep.checked_file(qc.ROOT / qc.NATIVE_RECIPE,
    qc.prep.object_field(contract, "reference_recipe_pin"))
PY

export R_LIBS_USER="$PREPROCESS_R_LIBRARY"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  "$PREPROCESS_SCRIPTS/run_native_gct_reference.R" "$PREPROCESS_R_SOURCE" \
  "$QC_REFERENCE_ZERO" "$QC_PROBE_INFO" "$QC_NATIVE_REFERENCE"

uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import gzip
import os
import shutil
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
import qualify_qc as qc
from qualify_limma import read_object
reference = Path(os.environ["QC_NATIVE_REFERENCE"])
with (reference / "native-typeI-ext.tsv").open("rb") as source, \
        (reference / "native-typeI-ext.tsv.gz").open("xb") as target:
    with gzip.GzipFile(filename="", fileobj=target, mode="wb", mtime=0, compresslevel=9) as zipped:
        shutil.copyfileobj(source, zipped)
qc.check_contract(read_object(qc.NATIVE_CONTRACT), reference)
print("All five native QC reference pins match")
PY
```

The parent reference independently decodes the original IDAT pair and calls the
unchanged native 65-field QC functions. The successor reads that R-decoded raw
SigDF, calls unchanged native `bisConversionControl`, and emits the complete
curated C/T identities and positional extension projection. It consumes no C
output. The p-value reference remains byte-identical to v1. Native GCT's selected
C/T groups contain 45,427/15,148 unique raw red-channel probes; no mask is applied
and individual missing green values are omitted within each mean. The current
finite-fixture contract does not accept infinite GCT or coerce an empty/zero
denominator into a value.

## Execute the complete successor

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/qualify_qc.py \
  --contract v2 \
  --checkout "$QC_NATIVE_SOURCE" \
  --data-root "$PREPROCESS_DATA" \
  --raw-reference "$QC_RAW_REFERENCE" \
  --reference-root "$QC_NATIVE_REFERENCE" \
  --output artifacts/verification/hm450-native-qc-v2-replay
```

The command runs 24 external commands, including a compiler identity check,
strict `-Werror` compilation of the seven-case real C regression and its actual
execution. It then clean-builds the pinned producer and validates the unchanged
complete annotation universe. It copies the five original asset files into the
new output directory and substitutes only the pinned curated extension table in
that copy. No original file is overwritten and no missing-asset fallback is
accepted.

All 66 QC fields and all raw/QCD-stage p-values are received at one and two
threads. Four additional raw/Q beta exports from the **same patched binary and
asset store** must match the unchanged mathematical reference, including exact
NA/order and declared binary32/six-digit serialization. The final checks rebind
the source, annotation, patch, references, recipes, harness, original and copied
inputs, contract and executable bytes. Reusing an output directory fails.

Expected success is exit zero with `status: passed` in `qc-contract.json`.
Preserve any failed or incomplete run and its logs. Success qualifies only this
technical boundary. It does not select a study rejection threshold, full QCDPB
beta/M precision budget, scientific cohort or official owner device.

## Code and integration gates

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python -m unittest discover \
  -s scripts/tests -p 'test_qc*.py'
uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

The native commit hook reruns the complete strict command and central staged
privacy guard. Ordinary CI executes receiver/schema/source-integrity regressions;
the external C/array-assets lane above remains explicit. Its build on this Linux
host does not establish a supported native Windows route. Actual address/undefined
sanitizer checks are retained separately; LeakSanitizer was unavailable under the
current host's tracing setup and is not claimed to pass.
