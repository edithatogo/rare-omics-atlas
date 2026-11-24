# Independent HM450 R reference and beta-export diagnostic

This is a reference recipe for one public technical HM450 pair. It adds no
production package or workflow dependency. All downloads, runtime files and
per-probe results must stay outside Git. The source-only drivers, comparison
scripts, immutable source/data pins and Linux runtime lock can be retained.

## Exact scope and adapters

The R source revision is `8b1fcfaed89b28e0def8b031a81611a0a770053c`
(sesame source version 1.31.12). Ten source files are downloaded unchanged and
verified using `reference-sources.json` and `reference-source.sha256`.
The runtime is R 4.5.2, MASS 7.3.66 and preprocessCore 1.72.0, with native
stringr/dplyr imports. `runtime-linux64-explicit.txt` fixes all 111 resolved
packages by URL/build/MD5; `environment-qcdpb-packages.json` also fixes SHA-256.
This lock is for Linux x86_64, not evidence for another operating system.

There are three explicit reference adapters or limitations:

1. `run_raw_q.R` calls unmodified `readIDAT()` on each channel and constructs the
   same named G/R/GN/RN matrix as `readIDAT1()`. It sets the contract's known
   HM450 platform directly, bypassing `idatSignature` autodetection/cache lookup.
   Unmodified `chipAddressToSignal(..., min_beads=NULL)` then maps the complete
   published R ordering. This matches the CLI's explicit `--min-beads 0`.
2. The raw/Q driver calls unmodified `qualityMask(mask=...)` with the five
   recommended tracks from the actual published R object. Before any beta
   comparison it requires exact identity of all 486,427 addresses/channels and
   all 24 mask tracks against the pinned C annotation assets. The full QCDPB
   driver additionally checks that native `qualityMask()` selects the same set.
3. `run_qcdpb.R` supplies local `sesameDataList`, `sesameDataGet` and
   `sesameDataHas` getters restricted to the exact HM450 address and mask objects.
   It leaves `prepSesame`, `qualityMask`, `backgroundMask`, channel inference,
   dye correction, pOOBAH, noob and `getBetas` unchanged. It uses the real
   stringr/dplyr/preprocessCore/MASS functions, not mathematical replacements.

This is execution of pinned source functions, not installation/qualification of
the full sesame package, its namespace lifecycle, automatic annotation discovery,
or its full package dependency graph. The R `hg38` GRanges member is not used:
the raw/Q driver reads only the complete ordering data frame. GenomicRanges was
not installed. Atlas separately checks named annotation against the pinned hg38
coordinate table. No QC-metric, scientific M-error-budget, EPIC, disease or
actual-owner-device admission follows from these results.

## Prepare exact local inputs

Use absolute paths; the scripts contain no workspace-specific path defaults.
`PREPROCESS_CONTRACT` points to Atlas's reviewed
`research/contracts/sesame-hm450-raw-q-v1.json`.

```sh
set -eu
export PREPROCESS_DATA=/absolute/path/to/ignored/preprocessing-data
export PREPROCESS_SCRIPTS=/absolute/path/to/atlas/scripts/tests
export PREPROCESS_PINS=/absolute/path/to/atlas/research/qualification/t07-reference-2026-11-23
export PREPROCESS_CONTRACT=/absolute/path/to/atlas/research/contracts/sesame-hm450-raw-q-v1.json
export PREPROCESS_R_SOURCE="$PREPROCESS_DATA/oracle/r-source"
export PREPROCESS_SOURCE=/absolute/path/to/pinned/sesame-checkout
export PREPROCESS_R_ENV="$PREPROCESS_DATA/tooling/r-4.5.2"
export PREPROCESS_R_LIBRARY="$PREPROCESS_DATA/tooling/r-library-serial"
```

The following download step reads only the reviewed pin manifests. It
refuses a pre-existing file whose bytes differ, and verifies length and SHA-256
before writing a missing file.

```sh
python - <<'PY'
import hashlib, json, os, pathlib, urllib.parse, urllib.request
data = pathlib.Path(os.environ["PREPROCESS_DATA"])
pins = pathlib.Path(os.environ["PREPROCESS_PINS"])
r_source = pathlib.Path(os.environ["PREPROCESS_R_SOURCE"])
contract = json.loads(pathlib.Path(os.environ["PREPROCESS_CONTRACT"]).read_text())
entries = [(data / name, pin["url"], pin["bytes"], pin["sha256"])
           for name, pin in contract["inputs"].items()]
for pin in json.loads((pins / "reference-r-assets.json").read_text()):
    entries.append((data / "r-assets" / pin["name"], pin["url"], pin["size"], pin["sha256"]))
for pin in json.loads((pins / "reference-sources.json").read_text())["sources"]:
    entries.append((r_source / pin["name"], pin["url"], pin["bytes"], pin["sha256"]))
for name in ["micromamba-download.json", "preprocesscore-source.json"]:
    pin = json.loads((pins / name).read_text())
    filename = pathlib.Path(urllib.parse.urlparse(pin["url"]).path).name
    entries.append((data / "tooling" / filename, pin["url"], pin["bytes"], pin["sha256"]))
for path, url, size, expected in entries:
    payload = path.read_bytes() if path.exists() else urllib.request.urlopen(url, timeout=60).read()
    if len(payload) != size or hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"pinned input differs: {path.name}")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
PY
(cd "$PREPROCESS_DATA" && sha256sum --check "$PREPROCESS_PINS/reference-data.sha256")
(cd "$PREPROCESS_R_SOURCE" && sha256sum --check "$PREPROCESS_PINS/reference-source.sha256")
```

Check out SeSAMe2 at `f6713747181764e0b7a97b64c3c0d52ab9d82703` with its
YAME submodule at `e1e7b38e9f3b67981a78b1116e7312864677d69d`. Verify a clean
source tree and ordinary index flags, then build `sesame`, `pipeline_dump` and
`YAME/yame` using the repository's build instructions. Preserve command logs,
compiler/runtime identity and binary hashes. The Atlas raw/Q qualifier performs
its own clean rebuild and source checks; this recipe does not replace them.

## Isolated R runtime and documented serial reference build

Use the micromamba 2.10.0 archive URL and SHA-256 in
`micromamba-download.json`; verify the archive before extracting `bin/micromamba`.
Do not initialize a shell profile or change an existing R installation.

```sh
tar -xjf "$PREPROCESS_DATA/tooling/micromamba-2.10.0-0.tar.bz2" \
  -C "$PREPROCESS_DATA/tooling" bin/micromamba
export PREPROCESS_MAMBA="$PREPROCESS_DATA/tooling/bin/micromamba"
"$PREPROCESS_MAMBA" --no-rc --root-prefix "$PREPROCESS_DATA/tooling/mamba-root" \
  create --prefix "$PREPROCESS_R_ENV" --file "$PREPROCESS_PINS/runtime-linux64-explicit.txt" --yes
```

The initial precompiled preprocessCore run failed with
`pthread_create() ... 22`. This is retained as a failed attempt, not a numerical
comparison or SKIP pass. The official Bioconductor container maintainers
document building preprocessCore with `--disable-threading` for this error:
https://github.com/Bioconductor/bioconductor_docker/issues/22

Download the unchanged 1.72.0 source tarball from the URL in
`preprocesscore-source.json`. Its SHA-256 must be
`4472052371147cfbf91d223eb15f3b030d236de9b4bba6b58a205c368d53884d`;
the release PACKAGES metadata MD5 is `c288c12d10a9a8b02904140e08aa97bd`.
The source itself supports the build option. Install only into a separate
reference library, leaving the resolved conda package tree untouched.

```sh
mkdir -p "$PREPROCESS_R_LIBRARY"
MAKEFLAGS=-j2 "$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" \
  R CMD INSTALL --library="$PREPROCESS_R_LIBRARY" --configure-args=--disable-threading \
  "$PREPROCESS_DATA/tooling/preprocessCore_1.72.0.tar.gz"
export R_LIBS_USER="$PREPROCESS_R_LIBRARY"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  -e 'stopifnot(getRversion() == "4.5.2", packageVersion("preprocessCore") == "1.72.0"); cat(find.package("preprocessCore"), "\n")'
```

Verify that the printed package path is the separate reference library. Preserve
its shared-library SHA-256 and the complete build log. The successful run used
the unchanged tarball, GCC 16.2.0, and this serial option; it did not patch
numerical code or relax acceptance. The dplyr binary emitted a nonfatal warning
that it was built under R 4.5.3; that warning remains recorded in the run logs.

## Complete raw/Q reference

Decode all published mask tracks, retaining full rows and exact header order:

```sh
python - <<'PY'
import gzip, os, pathlib, subprocess
data = pathlib.Path(os.environ["PREPROCESS_DATA"])
mask = data / "assets/HM450/HM450.hg38.mask.cm"
tracks = [line.split("\t")[0] for line in mask.with_name(mask.name + ".idx").read_text().splitlines()]
result = subprocess.run([os.environ["PREPROCESS_SOURCE"] + "/YAME/yame", "unpack", "-C", str(mask), *tracks], check=True, capture_output=True)
if result.stdout.splitlines()[0].decode().split("\t") != tracks or len(result.stdout.splitlines()) != 486428:
    raise ValueError("complete mask decode differs")
(data / "oracle").mkdir(exist_ok=True)
(data / "oracle/decoded-all-masks.tsv.gz").write_bytes(gzip.compress(result.stdout, mtime=0))
PY
python "$PREPROCESS_SCRIPTS/preprocessing_reference.py" \
  --data-root "$PREPROCESS_DATA" --r-source "$PREPROCESS_R_SOURCE" \
  --yame "$PREPROCESS_SOURCE/YAME/yame" --output "$PREPROCESS_DATA/oracle/python-raw-q"
"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  "$PREPROCESS_SCRIPTS/run_raw_q.R" "$PREPROCESS_DATA" "$PREPROCESS_R_SOURCE" \
  "$PREPROCESS_DATA/oracle/decoded-all-masks.tsv.gz" "$PREPROCESS_DATA/oracle/r-raw-q"
python "$PREPROCESS_SCRIPTS/compare_raw_q.py" \
  --reference "$PREPROCESS_DATA/oracle/python-raw-q/expected-raw-q.tsv.gz" \
  --r-output "$PREPROCESS_DATA/oracle/r-raw-q" \
  --receipt "$PREPROCESS_DATA/oracle/r-raw-q/comparison-receipt.json"
```

Use new output directories on subsequent runs. The raw/Q comparison requires
the complete ordered universe, exact M/U values, exact finite binary64 betas,
exact NA positions and exact Q bits. The selected run passed with zero numerical
differences, raw NA 2, Q masked 29,504 and Q NA 29,506.

## Full source-level QCDPB comparison

```sh
"$PREPROCESS_MAMBA" --no-rc run --prefix "$PREPROCESS_R_ENV" Rscript --vanilla \
  "$PREPROCESS_SCRIPTS/run_qcdpb.R" "$PREPROCESS_DATA" "$PREPROCESS_R_SOURCE" \
  "$PREPROCESS_DATA/oracle/r-raw-q" "$PREPROCESS_DATA/oracle/r-qcdpb"
YAME_DATA_HOME="$PREPROCESS_DATA/assets" "$PREPROCESS_SOURCE/pipeline_dump" \
  --platform HM450 --prep QCDPB --what beta \
  "$PREPROCESS_DATA/idats/HM450/3999492009_R01C01" \
  > "$PREPROCESS_DATA/oracle/c-qcdpb-f64.tsv" \
  2> "$PREPROCESS_DATA/oracle/c-qcdpb-f64.stderr"
python "$PREPROCESS_SCRIPTS/compare_qcdpb.py" \
  --r-output "$PREPROCESS_DATA/oracle/r-qcdpb" \
  --c-values "$PREPROCESS_DATA/oracle/c-qcdpb-f64.tsv" \
  --receipt "$PREPROCESS_DATA/oracle/r-qcdpb/internal-comparison.json"
```

The C helper prints 17 significant digits, preserving binary64 values. Its
complete ordered IDs and NA positions must match R. Every finite absolute
difference must be at most `1e-12`, the existing matched-annotation criterion in
https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/tests/compare_qcdpb.R
This recipe strengthens upstream's intersection comparison to the entire
universe. The observed maximum `1.1102230246251565e-15` is a result, not a new
acceptance threshold. All 486,427 rows matched, including 79,947 NA positions
and 406,480 finite betas.

## Separate actual production beta-only diagnostic

This step compares the actual product export directly to R; it does not use the
C internal helper as its truth. It retains the raw/Q production gate separately.

```sh
mkdir "$PREPROCESS_DATA/production-qcdpb-r"
YAME_DATA_HOME="$PREPROCESS_DATA/assets" "$PREPROCESS_SOURCE/sesame" preprocess \
  --platform HM450 --prep QCDPB \
  --mask "$PREPROCESS_DATA/assets/HM450/HM450.hg38.mask.cm" \
  --min-beads 0 --threads 1 --output beta \
  --out "$PREPROCESS_DATA/production-qcdpb-r/beta-only" \
  --tmp "$PREPROCESS_DATA/production-qcdpb-r" \
  "$PREPROCESS_DATA/idats/HM450/3999492009_R01C01"
YAME_DATA_HOME="$PREPROCESS_DATA/assets" "$PREPROCESS_SOURCE/sesame" describe-probe \
  --platform HM450 --all "$PREPROCESS_DATA/production-qcdpb-r/beta-only/beta.cg" \
  > "$PREPROCESS_DATA/production-qcdpb-r/export.tsv"
python "$PREPROCESS_SCRIPTS/compare_qcdpb_export.py" \
  --r-output "$PREPROCESS_DATA/oracle/r-qcdpb" \
  --text-export "$PREPROCESS_DATA/production-qcdpb-r/export.tsv" \
  --sample-index "$PREPROCESS_DATA/production-qcdpb-r/beta-only/beta.cg.idx" \
  --binary-output "$PREPROCESS_DATA/production-qcdpb-r/beta-only/beta.cg" \
  --receipt "$PREPROCESS_DATA/production-qcdpb-r/comparison-receipt.json"
(cd "$PREPROCESS_DATA" && sha256sum --check "$PREPROCESS_PINS/reference-data.sha256")
(cd "$PREPROCESS_R_SOURCE" && sha256sum --check "$PREPROCESS_PINS/reference-source.sha256")
```

Require successful command exits; preserve stdout, stderr, exact arguments and
before/after input, source and binary hashes. Text values must equal R values
after the declared binary32 then six-significant-digit conversion. This tests
that composed text interface; it does not inspect every stored binary word.
Identity, length, sample index and missingness are exact. The successful selected
run had no endpoint collapses. Measured maximum beta serialization error was
`5.294165927871575e-7`; maximum finite M serialization error was
`8.747193203184622e-5`. These measurements are not scientific error budgets.

`reference-evidence.json` records the separate successful comparisons, failed
attempts, runtime/adapter limits and artifact hashes. It contains no raw IDATs,
per-probe output rows or disease analysis.
