# T01a — public source reconciliation and sample declaration contract

Updated 23 November 2026 Australia/Brisbane; executed 22 November 2026 UTC. The filename preserves the UTC source-retrieval date. Source and code identities are in the [machine-readable receipt](t01-sample-contract-2026-11-22.json). This increment supplies a local structural review command in the existing Rust catalogue. It grants no scientific admission and establishes no independent-participant count.

## Actual source result

The official GEO sample SOFT inventories were retrieved directly and matched against `research/catalogue/2026-11-22/assays.jsonl` by exact GSM accession. Each source returned HTTP 200. Original response bytes, contact fields and unrestricted clinical annotations remain in ignored local Bronze storage.

| Official series | Source assay records | Catalogue assay records | Duplicate / missing / additional assay records | Available characteristic fields |
|---|---:|---:|---|---|
| [GSE97362](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362&targ=gsm&form=text&view=brief) | 235 | 235 | 0 / 0 / 0 | Age, disease state, gender, sample type and tissue on 235 records |
| [GSE116300](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300&targ=gsm&form=text&view=brief) | 44 | 44 | 0 / 0 / 0 | Array position, case status, mutation, phenotype, sex and slide ID on 44 records; variant classification on 14 |
| [GSE218186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186&targ=gsm&form=text&view=brief) | 62 | 62 | 0 / 0 / 0 | Disease state and tissue on 62 records |

The three sources share zero GSM accessions. This assay-level comparison does not establish participant independence or resolve reused controls. The bounded review has not established participant–specimen links, molecular eligibility or an analysis-specific discovery/replication assignment. `unknown` denotes an unresolved analysis declaration; the original sources do contain clinical and study annotations.

The actual local input therefore retains null participant/specimen identifiers and unknown role, partition, molecular eligibility and independence for all **341 assays**. The command returns exit **2**, with **341 held, zero ready for review and zero excluded**. Each held row records all six unresolved reasons. `independent_participant_count` remains null and `analysis_admitted` remains false. Source hashes and both local input/output hashes are retained in the JSON receipt.

## Implemented boundary

`sample-contract` accepts a local JSON file of at most 16 MiB, performs no network calls, leaves its input unchanged and writes its report to stdout. The existing catalogue remains the package's default executable. Strict Serde deserialization reuses packages already present in the lockfile; no package version or service was added.

The top-level fields are exactly `schema_version` (integer 1) and a nonempty `samples` array. Every sample requires these fields:

| Field | Required declaration |
|---|---|
| `dataset_accession`, `assay_accession` | Public `GSE`/`GSM` accession plus ASCII digits; every assay appears once in the input |
| `participant_id`, `specimen_id` | Locally curated opaque identifier, or JSON null for unknown; identifiers share one consistent namespace across the entire manifest |
| `role` | `case`, `control`, `excluded` or `unknown` |
| `partition` | `discovery`, `replication` or `unknown` |
| `molecular_eligibility` | `eligible`, `ineligible`, `unknown`, or `not_applicable` for an explicitly declared control/exclusion |
| `independence` | `verified`, `overlap` or `unknown`, supplied as a declaration requiring source review |
| `source` | Exactly `url` and `sha256`: HTTPS without embedded credentials and a 64-character lowercase hexadecimal digest |

Missing, extra, repeated, incorrectly typed or unsupported fields fail, including escaped-equivalent repeated JSON keys. Empty, padded, overlong and sentinel identifiers such as `unknown`/`NA` fail; unknown identity must use null. The URL and digest are checked for syntax. They are declared provenance references and are not dereferenced or accepted as proof of the claims.

Repeated participant or specimen identifiers hold every affected nonexcluded assay. Participant declarations that cross partitions or roles add explicit conflict reasons. A row explicitly excluded by role or molecular ineligibility stays excluded and does not cause another selected assay to be counted twice. An unknown or overlapping nonexcluded declaration stays held.

The report is deterministic under input reordering. Per-row output contains only public series/assay accessions, structural status, reason codes and `analysis_admitted: false`. It exports no participant/specimen identifier, source URL/hash or unrestricted source annotation. Its statuses have a deliberately limited meaning:

| Exit | Result |
|---:|---|
| 0 | At least one declaration is `ready_for_review`, with no held rows. Source claims and all scientific gates still require review. |
| 2 | One or more rows are held, or every row is excluded. A well-formed input has not supplied a usable review set. |
| 1 | Malformed, ambiguous, unreadable or oversized input. No report is emitted. |

All reports retain `source_claims_verified: false`, `analysis_admitted: false` and an unknown independent-participant count. Source rights/disclosure, covariates/design, qualified preprocessing/QC, institutional classification, the selected backend/device and analysis-specific N1 remain outstanding gates.

## Executable replay

Use the pinned setup in [the CI plan](../ci-plan.md). The actual review invocation is:

```sh
cargo +1.95.0 run --locked --manifest-path tools/catalogue/Cargo.toml \
  --bin sample-contract -- \
  --input data/silver/t01-sample-contract-2026-11-22/declared-samples.json
```

Exit 2 is the required result for this held real-source inventory. To reconstruct that input from the public snapshot and verify the pinned original source bytes, run from the repository root:

```sh
python - <<'PY'
import hashlib
import json
import urllib.request
from pathlib import Path

receipt = json.loads(Path('research/qualification/t01-sample-contract-2026-11-22.json').read_text())
catalogue = [json.loads(line) for line in Path(receipt['catalogue_path']).read_text().splitlines()]
bronze = Path('data/bronze/t01-source-reconciliation-2026-11-22')
silver = Path('data/silver/t01-sample-contract-2026-11-22')
bronze.mkdir(parents=True, exist_ok=True)
silver.mkdir(parents=True, exist_ok=True)
samples = []
for source in receipt['public_sources']:
    with urllib.request.urlopen(source['url'], timeout=60) as response:
        raw = response.read()
    assert hashlib.sha256(raw).hexdigest() == source['sha256'], 'source revision changed'
    accession = source['accession']
    ids = [line.split(' = ', 1)[1] for line in raw.decode().splitlines() if line.startswith('^SAMPLE = ')]
    expected = [row['assay_accession'] for row in catalogue if row['dataset_accession'] == accession]
    assert len(ids) == len(set(ids)) == len(expected) == source['assay_records']
    assert set(ids) == set(expected), 'source/catalogue assay disagreement'
    (bronze / f'{accession}.soft').write_bytes(raw)
    for assay in sorted(ids):
        samples.append(dict(dataset_accession=accession, assay_accession=assay,
            participant_id=None, specimen_id=None, role='unknown', partition='unknown',
            molecular_eligibility='unknown', independence='unknown',
            source=dict(url=source['url'], sha256=source['sha256'])))
target = silver / 'declared-samples.json'
target.write_text(json.dumps(dict(schema_version=1, samples=samples), indent=2) + '\n')
assert hashlib.sha256(target.read_bytes()).hexdigest() == receipt['reconciliation_and_review']['input_sha256']
print(f'Reconstructed {len(samples)} held declarations at {target}')
PY
```

A changed remote response stops this replay. Review a new source revision in a new receipt rather than weakening the hash comparison or replacing the old evidence.

## Verification and peer review

The clean predecessor `9b06b16` passed all 33 strict checks before changes after its pinned tool environment was selected; elapsed time was 26.355 seconds. The earlier missing-tool environment failure remains separately recorded. The accepted predecessor PR subsequently merged as `6bd452abde7aff9fbf2969814dca39a0f182d18a`, which is the comparison base for this increment.

After the parser correction, `cargo +1.95.0 test --locked --manifest-path tools/catalogue/Cargo.toml` passed **20 tests**: 19 integration contracts and the existing cache-integrity unit test. Formatting and Clippy with warnings denied passed. Native llvm-cov plus `diff-cover --branch-coverage --compare-branch origin/main --include-untracked --fail-under 90` measured **190/191 changed Rust lines, 99.48%**, without transforming the coverage report or excluding production paths.

Independent peer review reproduced a real duplicate-key ambiguity in the initial Value parser. Strict typed deserialization corrected it; actual CLI tests now reject repeated participant, escaped-equivalent participant, schema and source keys. The reviewer reran the original reproduction and observed exit 1, empty stdout and a fixed diagnostic without private values. The corrected declaration boundary was accepted, with scientific truth and device acceptance explicitly outside that review.

The [combined strict receipt](contracts-hooks-2026-11-23.json) subsequently passed **34/34 checks** in 28.318 seconds: 20 Rust tests per debug/release/instrumented run, 38 harness tests and 41 publisher tests. Combined changed-code coverage was **499/513 lines, 97.27%**. The runtime receipt SHA-256 is `e2fd84d913862ffdb9b309409fa7b0d8f1eed0b2024c6878668deacfb8475651`, for source-tree hash `0577334a5275ac1ca5e2da8f44b9f0935424ba996f58bf2231d93d4b4cfb2230`. The initial combined run's failure is preserved: an isolated harness fixture lacked the newly mandatory consumer artifact. The fixture was corrected without weakening the production gate.

[T01a is completed and archived](../../conductor/archive/t01a_sample_contract_20261123/index.md) on that bounded implementation, peer review and strict evidence. The candidate pass preceded final evidence/archive edits; the coordinating owner's native commit hook revalidates the final tree, and hosted outcomes are recorded against their own published revisions. Official owner-device acceptance remains unobserved.

## Receiving work and publication implication

The T01 owner next reviews the original study supplements and metadata for defensible participant/specimen links, eligibility, native controls and covariates. Use declared local identifiers only when the source evidence supports them. The institution owns its applicable research determination; T07 owns the selected preprocessing and numerical contract. Unresolved source claims remain held even when a synthetic declaration passes the structural command.

This is E0 infrastructure evidence supporting the bundled P1 study. It provides no new disease result, confirmed molecular cohort or participant denominator, and creates no separate manuscript claim. The parent T01 scientific-admission track remains open.
