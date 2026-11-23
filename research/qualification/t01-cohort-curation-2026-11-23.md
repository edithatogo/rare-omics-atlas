# T01 cohort-source curation — 23 November 2026

## Bounded result

Fresh original GEO metadata reconciles exactly to the existing **341 public assay records**. The local KMT2D review inventory now has **68 candidate case declarations, 189 source-control declarations and 84 scope exclusions**. The existing sample contract holds all 257 nonexcluded records. No participant count, analysis cohort, molecular admission or discovery/replication assignment is inferred.

This increment resolves source roles, several molecular source categories, native control groups, technical array links and an explicit historical study-reuse relationship. Participant/specimen identities, gene-specific eligibility, biological independence and required covariates still need curation before T01 admission. The source records, study pseudonyms and assay-level sidecars remain under ignored `data/bronze/` and `data/silver/`; this receipt contains cleared aggregates only.

Base: `4162111f38e63ca21d811d7df2e628239297bc8d`. The [machine receipt](t01-cohort-curation-2026-11-23.json) records source URLs, timestamps, byte hashes, transformation predicates and local artifact hashes. The [T01 parent](../../conductor/tracks/t01-sources/plan.md) remains open.

## Source reconciliation

The three NCBI sample SOFT responses were retrieved on **2026-11-23 UTC**. Their byte hashes match the earlier T01a source receipts, and their assay accession sets equal the checked-in [catalogue](../catalogue/2026-11-22/assays.jsonl), with no missing, added or duplicated assays.

| Original source | Public assay records | Source role/group facts | Fresh source SHA-256 |
| --- | ---: | --- | --- |
| [GSE97362](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362&targ=gsm&form=text&view=brief) | 235 | 37 KMT2D/Kabuki-labelled records, 73 CHD7/CHARGE/KDM6A-labelled records, 125 controls | `820228d67ecf030e9f6c5caef5ca0d7451c960c45eb8b770be5d7e68e12458cf` |
| [GSE116300](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=gsm&form=text&view=brief) | 44 | 29 source-labelled case assays, 9 controls, 6 case parents | `9a8722a365f07c83e6f663d0ab0bb8b7723bd736aad16696d099ee9d2b12c7e1` |
| [GSE218186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186&targ=gsm&form=text&view=brief) | 62 | 7 Kabuki-labelled assays, 55 controls | `0e72adc9bc6547023f23d5ba4743eb76dfd98a4cf7357ed8abe3dddcb11bcbde` |

Every assay has one red/green IDAT URL pair with a common array serial/position key. All 44 GSE116300 keys also agree with the explicit slide/array-position characteristics. There are no shared array keys across these three series. These checks reconcile **metadata links**; IDAT contents were not downloaded or quality-qualified in this lane. Different array keys do not establish different specimens or people.

## Molecular source categories and exact joins

### GSE97362

The [original Butcher paper](https://doi.org/10.1016/j.ajhg.2017.04.004) was retrieved as complete [NCBI article XML](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=5420353), including the body and main tables. It distinguishes 11 KMT2D loss-of-function discovery cases, 10 recruited KMT2D variants of uncertain significance, and 8 pathogenic/likely pathogenic KMT2D cases in the validation cohort. **All ten Table 2 sample labels join exactly to ten GEO descriptions** in the KMT2D sequence-variant group; no numerical label translation was used.

The paper's methylation-signature classifications of those uncertain variants cannot establish independent molecular eligibility for a methylation analysis. Supplemental Tables S2/S5 are still needed for the intended case-level variant/classification joins. The 37 KMT2D/Kabuki-labelled assay records therefore remain molecularly held in the local declaration inventory. [NCBI source](https://pmc.ncbi.nlm.nih.gov/articles/PMC5420353/)

### GSE116300

The GEO source itself reports the following gene/classification combinations among its 29 case-labelled assays:

| Source molecular label | Assays |
| --- | ---: |
| KMT2D, pathogenic | 9 |
| KMT2D, VUS | 2 |
| KMT2D and KMT2B, VUS | 1 |
| KMT2A, pathogenic or likely pathogenic | 2 |
| DNMT3B, HCFC1 or ZBTB24; classification unstated | 3 |
| Mutation recorded as `None`; classification unstated | 12 |

These are source declarations, without fresh pathogenicity adjudication. The [paper](https://doi.org/10.1038/s41431-017-0023-0) reports 27 probands, whereas GEO contains 29 case-labelled assays. The paper's `KS` labels and GEO's `PAT` labels require an explicit crosswalk; equal numbers do not prove a join. This unresolved inventory difference also prevents interpreting assay counts as independent people. Six parent-labelled assays remain separately identified and excluded from this KMT2D review inventory; they are not assigned as unrelated controls. [Original abstract](https://pubmed.ncbi.nlm.nih.gov/29255178/)

### GSE218186

The [Hildonen paper](https://doi.org/10.1111/cge.14304) describes seven IC1 cases with pathogenic or likely pathogenic KMT2D variants. The deposited GEO records identify seven Kabuki-labelled assays but do not provide the case-level variant table. That supplementary mapping was not retrieved, so this increment makes no eligible molecular declaration for those assays. [Original publication record](https://pubmed.ncbi.nlm.nih.gov/36705342/)

Public retrieval of the requested supplements did not produce usable supplement bytes. The access log distinguishes HTTP failures and HTML responses from retrieved PDF/XLSX content. PMC browser challenge pages were not treated as full papers. No source-table mapping is claimed from those failed retrievals.

## Controls, covariates and technical batches

Source control roles are retained independently of future analysis selection. GSE97362 has **11 KMT2D discovery controls, 29 CHD7 discovery controls and 85 validation controls**; these are not interchangeable analysis sets by default. GSE116300 has 9 source controls, and the GSE218186 IC1 deposit has 55. All 189 remain held until the intended native comparison and identity/covariate requirements are frozen. [GSE97362 source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362&targ=gsm&form=text&view=brief), [GSE116300 source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=gsm&form=text&view=brief), [GSE218186 source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186&targ=gsm&form=text&view=brief)

| Source | Per-assay age in GEO characteristics | Per-assay sex in GEO characteristics | Technical array evidence |
| --- | --- | --- | --- |
| GSE97362 | 232 numeric values, 2 left-censored `<0.1`, 1 missing `NA` | 235 present | 38 chips; native KMT2D discovery cases occupy 3 chips and their controls 4, sharing 2 chips |
| GSE116300 | Not supplied | 44 present | 4 chips; each mixes source cases and controls; metadata slide/position matches all 44 raw URL keys |
| GSE218186 | Not supplied | Not supplied | 14 chips; all 7 case-containing chips also contain controls |

Age missingness and censoring are preserved. No age, sex or cell-mixture covariate is imputed. A chip serial is a candidate technical covariate, and does not replace a specimen identifier. The GSE97362 native comparison has one case-only chip and two control-only chips, which must be considered when the eventual design is qualified. Tissue/source fields consistently indicate blood; this does not qualify cell composition or batch adjustment.

## Historical reuse and independence

All 62 GSE218186 sample records carry the same processing description. It explicitly names these historical classifier inputs:

| Historical dataset | Source-described role | Source-described records |
| --- | --- | --- |
| PC, from GSE97362 | Training | 19 Kabuki plus 57 controls |
| IC2, not publicly deposited according to the source | Training | 12 Kabuki plus 13 controls |
| IC1, deposited as GSE218186 | Classifier testing | 7 Kabuki plus 55 controls |

The source says the datasets were combined to 450K content and quantile-normalized together before classifier construction. This proves a **study-data reuse relationship** and identifies the provenance of the published processing. It does not prove person-level overlap between the two public deposits, or establish prospective preprocessing independence. Historical training/test labels are preserved in the source sidecar and do not populate this project's new discovery/replication partition. [Original GEO processing records](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186&targ=gsm&form=text&view=brief)

## Existing-contract replay

The local review scope follows the KMT2D-specific [T02 specification](../../conductor/tracks/t02-kabuki/spec.md). This scope decision retains all public records in the catalogue and makes no molecular pathogenicity judgment:

| Series | Candidate `case` | Source `control` | `excluded` by current review scope |
| --- | ---: | ---: | ---: |
| GSE97362 | 37 | 125 | 73 CHD7/CHARGE/KDM6A records |
| GSE116300 | 24 | 9 | 5 other-gene case records and 6 case parents |
| GSE218186 | 7 | 55 | 0 |
| **Total** | **68** | **189** | **84** |

The 24 GSE116300 candidates comprise 12 KMT2D-containing source labels and 12 clinical cases recorded as `None` for mutation. Both uncertain variants and unresolved clinical cases stay held. Controls/exclusions use `molecular_eligibility: not_applicable`; all 68 candidates use `unknown`. All 341 participant/specimen IDs remain `null`, and all partition/independence values remain `unknown`.

The unchanged `sample-contract` program consumes the local declaration file:

```sh
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml \
  --bin sample-contract -- \
  --input data/silver/cohort-admission/source-curation-2026-11-23/declared-samples.json
```

Executed at `2026-11-23T01:40:35Z` with Rust 1.95.0. **Exit 2 was the expected held result:** 257 held, 84 excluded by declaration, 0 ready for review. The 257 held records each retain participant, specimen, partition and independence holds; the 68 candidate cases also retain molecular-eligibility holds. The report SHA-256 is `986d36ae5b10f71ab1378fbeda17838b77907e087dc3160c4212373e0c07d185`.

The source reference on a declaration binds it to retrieved GEO bytes; the validator does not independently verify the clinical truth of a source claim. Its output remains allowlisted and reports `analysis_admitted: false`.

### Reproduce the declaration input

Run from the repository root after the pinned tools are bootstrapped. This recipe reads the durable source hashes, retrieves missing original GEO files, fails on changed source bytes, and writes only ignored local records. Unrecognized source role/gene labels fail instead of silently receiving a declaration. It neither infers identities nor assigns analysis partitions.

```sh
uv run --project tools/hf-release --frozen --python 3.15.2 python - <<'PY'
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

receipt = json.loads(Path(
    'research/qualification/t01-cohort-curation-2026-11-23.json'
).read_text())
bronze = Path('data/bronze/t01-cohort-curation-2026-11-23')
silver = Path('data/silver/cohort-admission/source-curation-2026-11-23')
bronze.mkdir(parents=True, exist_ok=True)
silver.mkdir(parents=True, exist_ok=True)
samples = []
for source in receipt['public_sources']:
    series = source['accession']
    path = bronze / (series + '.soft')
    if not path.exists():
        with urlopen(source['url'], timeout=30) as response:
            path.write_bytes(response.read())
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('source bytes changed; new curation is required')
    rows = []
    for line in raw.decode().splitlines():
        if line.startswith('^SAMPLE = '):
            rows.append({'assay': line.split(' = ', 1)[1], 'traits': {}})
        elif line.startswith('!Sample_characteristics_ch1 = '):
            key, value = line.split(' = ', 1)[1].split(': ', 1)
            rows[-1]['traits'][key.lower()] = value
    if len(rows) != source['assay_records']:
        raise ValueError('source assay count changed')
    for row in rows:
        c = row['traits']
        if series == 'GSE97362':
            role = {
                'Control': 'control', 'Kabuki': 'case',
                'KMT2D variant': 'case', 'CHARGE': 'excluded',
                'CHD7 variant': 'excluded', 'KDM6A variant': 'excluded',
            }[c['disease state']]
        elif series == 'GSE116300':
            role = {'control': 'control', 'case parent': 'excluded',
                    'case': 'case'}[c['case status']]
            if role == 'case':
                role = {
                    'KMT2D': 'case', 'KMT2D_and_KMT2B': 'case',
                    'None': 'case', 'DNMT3B': 'excluded',
                    'HCFC1': 'excluded', 'KMT2A': 'excluded',
                    'ZBTB24': 'excluded',
                }[c['mutation']]
        elif series == 'GSE218186':
            role = {'Control': 'control',
                    'Kabuki syndrome': 'case'}[c['disease state']]
        else:
            raise ValueError('unrecognized source series')
        samples.append({
            'dataset_accession': series, 'assay_accession': row['assay'],
            'participant_id': None, 'specimen_id': None, 'role': role,
            'partition': 'unknown', 'independence': 'unknown',
            'molecular_eligibility': (
                'unknown' if role == 'case' else 'not_applicable'
            ),
            'source': {'url': source['url'], 'sha256': source['sha256']},
        })
if len(samples) != 341 or len({r['assay_accession'] for r in samples}) != 341:
    raise ValueError('missing or duplicated assay declarations')
payload = (json.dumps({'schema_version': 1, 'samples': samples},
                      indent=2, sort_keys=True) + '\n').encode()
if hashlib.sha256(payload).hexdigest() != (
    'e597ac2fd42ce0bf172cb67dc041df59c930a4ad048cae912335fba14916052b'
):
    raise ValueError('declaration reconstruction differs from the receipt')
(silver / 'declared-samples.json').write_bytes(payload)
print('341 source-bound assay declarations reconstructed locally')
PY
```

## Remaining work and order

The T01 curator can pursue **original variant/sample crosswalks, identity/overlap evidence and missing covariates in parallel**. Source mapping must resolve the GSE116300 paper/assay inventory difference and the intended case-level molecular classifications before eligibility is frozen. Molecular predictions derived from methylation remain separate from independent eligibility evidence.

Once those inputs are available, freeze the native control set, gene-specific eligible subset, repeated-specimen handling and new analysis partition together. Replay the existing validator on that source-bound manifest; structural readiness still requires explicit scientific admission. The T07 owner then applies the technical preprocessing/annotation and applicable official-device evidence gates before analysis. This receipt does not close those gates or trigger patient-data analysis.

## Strict baseline and validation boundary

The native hook path was configured as `.githooks` before this increment. The initial strict baseline retained two failures (`actionlint-version` and `workflow-lint`, exit 127) while Actionlint installation was still completing; its receipt remains at `artifacts/verification/preprocessing-baseline/receipt.json`. The corrected **strict `--deep` baseline passed 34/34 checks** at `artifacts/verification/preprocessing-baseline-corrected/receipt.json` before these tracked receipts were written. Both runs identify the same clean source tree (`974e2b89cdcff23ce07b35899bb902124c231f981c6c20e6204e846d5035a337`), and the strict policy was unchanged. Receipt hashes are retained in the machine record.

The source-curation lane changed no production code and reused the existing sample contract. The declaration reconstruction and actual CLI replay are its direct validation. The integration owner records full verification of the combined candidate separately; the clean baseline is not represented as testing later changes. Official-device acceptance and scientific admission remain separate, open conditions.
