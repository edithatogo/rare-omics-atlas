# HM450 preprocessing and annotation qualification

The bounded contract is [sesame-hm450-raw-q-v1](contracts/sesame-hm450-raw-q-v1.json).
It qualifies the existing SeSAMe2 production CLI's raw and quality-mask (`Q`)
outputs on one public author technical pair. Atlas owns the receiving checks;
SeSAMe2 owns its numerical implementation. No C code is copied into Atlas.

The checker uses the existing Python development environment and standard
library. Its [independent reference generator](../scripts/tests/preprocessing_reference.py)
is a test oracle, not a replacement production IDAT reader. The oracle reads
the input mean signals independently and follows the pinned R source's channel
rules and `max(M, 1) / max(M + U, 2)` beta definition. Exact R source bytes are
required before generation. YAME decodes the named annotation tracks; the
reference independently selects/unions them and never reads C pipeline values.

## Exact boundary

| Item | Contract |
|---|---|
| C engine | SeSAMe2 2.3.2 at `f6713747181764e0b7a97b64c3c0d52ab9d82703` |
| Decoder/library | Its YAME gitlink `e1e7b38e9f3b67981a78b1116e7312864677d69d` |
| Array assets | InfiniumAnnotation v8.5 at `678acbeddfb746c1ddfa24c5c1ca9f5197a61ee2`, HM450, hg38 |
| Public technical input | One author HM450 pair at immutable InfiniumAnnotationData revision; exact URLs, lengths and hashes are in the contract |
| Full universe | 486,427 ordered probe identities, including controls and unavailable coordinates |
| Stages | Raw and Q; explicit `--platform HM450`, pinned `--mask`, `--min-beads 0`, beta output only |
| Serialization | Production `.cg` binary32, then `describe-probe` six-significant-digit text |
| Acceptance | Every received value equals that declared serialization of the independent reference; every NA, identity, order and sample index agrees |
| Repeatability | The same pair at one and two threads; this does not benchmark concurrent processing of multiple samples |
| Annotation | Actual named coordinate export equals every pinned ordering/coordinate row; type-I extension row-space is complete |

The Q union selects exactly `M_1baseSwitchSNPcommon_5pt`,
`M_2extBase_SNPcommon_5pt`, `M_mapping`, `M_nonuniq` and
`M_SNPcommon_5pt`. It does not substitute the broader `M_general` track.
The explicit zero bead threshold differs from R `openSesame()`'s default and
must also be explicit in the reference. Coordinate `CpG_beg` is zero-based;
this contract preserves it and does not invoke the separate genome-neighbour
command, which can drop unaddressable contigs.

## Reproduce the technical increment

Use the pinned Atlas developer tools from [the strict CI contract](ci-plan.md).
The native fixture build additionally needs Git, Make, a C compiler, zlib and
libcurl development libraries. The existing upstream build targets POSIX
systems; this recipe does not claim native Windows or actual owner-device
support. Choose new checkout/output directories if the named paths already exist.

```sh
git clone --recursive https://github.com/zhou-lab/sesame.git artifacts/integration/sesame-raw-q
git -C artifacts/integration/sesame-raw-q checkout --detach f6713747181764e0b7a97b64c3c0d52ab9d82703
git -C artifacts/integration/sesame-raw-q submodule update --init --recursive
make -C artifacts/integration/sesame-raw-q -j2 sesame
```

Retrieve the seven exact public inputs and four small reference-source files.
Files remain local under ignored `data/reference-cache/`; the receipt and
downloaded bytes are separate from redistribution or scientific admission.
This recipe refuses changed bytes rather than replacing the contract.

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, 'scripts/tests')
from preprocessing_reference import R_REVISION, R_SOURCE_PINS

contract = json.loads(Path('research/contracts/sesame-hm450-raw-q-v1.json').read_text())
root = Path('data/reference-cache/sesame-hm450')
requests = [(root / name, pin['url'], pin['sha256'], pin['bytes'])
            for name, pin in contract['inputs'].items()]
requests += [(root / 'r-source' / name,
              f'https://raw.githubusercontent.com/zwdzwd/sesame/{R_REVISION}/R/{name}',
              expected, None) for name, expected in R_SOURCE_PINS.items()]
for path, url, expected, size in requests:
    if path.exists():
        data = path.read_bytes()
    else:
        with urlopen(url, timeout=60) as response:
            data = response.read()
    if hashlib.sha256(data).hexdigest() != expected or (size is not None and len(data) != size):
        raise ValueError(f'pinned source bytes differ: {path.name}')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
print('All pinned inputs verified')
PY

uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/tests/preprocessing_reference.py \
  --data-root data/reference-cache/sesame-hm450 \
  --r-source data/reference-cache/sesame-hm450/r-source \
  --yame artifacts/integration/sesame-raw-q/YAME/yame \
  --output data/reference-cache/sesame-hm450/reference

uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/qualify_preprocessing.py \
  --checkout artifacts/integration/sesame-raw-q \
  --data-root data/reference-cache/sesame-hm450 \
  --reference data/reference-cache/sesame-hm450/reference/expected-raw-q.tsv.gz \
  --output artifacts/verification/preprocessing-raw-q

uv run --project tools/hf-release --frozen --python 3.15.2 python scripts/verify.py --deep
```

The qualifier checks the immutable clean source, submodule and all input bytes,
cleans and builds the C tools, runs the actual named annotation export and all
four raw/Q exchanges, then rechecks sources, input bytes, binaries, contract and
checker implementation. Output directories must be new and inside ignored
`artifacts/verification/`. Missing assets, malformed/incomplete output, command
failure or detected drift produces a failed receipt and nonzero exit. It never
inherits an upstream missing-prerequisite `SKIP` as a pass.

The ordinary strict command always runs the checker/oracle regression tests,
typing, lint and branch-aware patch coverage. This explicit technical fixture
run is also required before accepting changes to this qualification contract,
checker, reference or selected upstream source. It is separate from the
cross-platform Atlas code gates because the candidate C build and public
technical inputs are additional prerequisites. No missing fixture run is called
method acceptance, and no default strict gate is disabled.

## Interpretation and retained limits

The production serializer loses precision relative to the binary64 reference.
Acceptance above specifies the actual representation; it is not a scientific
beta- or M-error budget. Receipts report observed beta/M differences, existing
endpoints and any new finite-to-endpoint collapses. No clipping, imputation or
tolerance selected from the observed errors is introduced.

This one HM450 fixture does not qualify EPIC, EPICv2, multi-sample behavior,
full QCDPB, p-values/QC metrics, gene mapping, disease cohorts or a scientific
inference route. Fresh R source-level execution and any full-pipeline diagnostic
are separately identified in the dated evidence, including adapters and failures.
An upstream internal pipeline dump measures serialization loss; it is never the
independent production oracle.

The pinned [SeSAMe2 licence](https://github.com/zhou-lab/sesame/blob/f6713747181764e0b7a97b64c3c0d52ab9d82703/LICENSE)
and [YAME licence](https://github.com/zhou-lab/YAME/blob/e1e7b38e9f3b67981a78b1116e7312864677d69d/LICENSE)
include academic/nonprofit research terms and a separate commercial-use condition.
This increment downloads and builds them locally, without redistributing their
source/binaries or representing them as unrestricted BSD. Atlas's unresolved
code-licence decision remains separate. The upstream build's observed warnings
and dependency/device limits are retained in the evidence.

The [dated qualification receipt](qualification/t07-preprocessing-2026-11-23.md)
records the actual raw/Q acceptance and separate full-QCDPB beta diagnostics.
The [independent R recipe](qualification/t07-reference-2026-11-23/REFERENCE_REPRODUCTION.md)
includes source-level adapters, exact environment/data pins and retained failures.
