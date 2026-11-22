# Source-bound Hugging Face publisher

This operational Python boundary uses the **official `huggingface_hub` client** for publication, including its supported large-file transport. It does not implement an upload protocol or introduce Python into the scientific analysis path. The source manifest is the complete release allowlist.

## Install and verify

Python **3.11 or newer** is required because the selected `httpx2[socks]` transport version requires it. The initial local qualification uses CPython 3.15.2. A different runtime must run the tests and dry-run before publication; supported syntax alone is not execution evidence.

From the repository root:

```sh
uv sync --frozen --project tools/hf-release --python 3.15.2
uv run --frozen --project tools/hf-release python -m unittest discover -s tools/hf-release/tests -v
uv run --frozen --project tools/hf-release python tools/hf-release/publisher.py \
  --manifest research/releases/2026-11-22/manifest.json \
  --root . \
  --data-root /path/to/atlas-source-cache \
  --receipt /path/to/hf-release-dry-run.json
```

The default is **dry-run**: verify every allowlisted local object and prepare the exact generated metadata, without calling the Hub. `--fetch-sources` additionally retrieves missing allowlisted public GEO archives over HTTPS. It preserves original bytes, bounds downloads by the declared size, verifies SHA-256, and promotes a verified `.part` file. Existing mismatched files or pre-existing partials are rejected instead of replaced. A partial created by a failed invocation is cleaned up. Source redirects are rejected because exact URLs are part of this bounded release contract.

The cache can be any explicitly selected data root. Raw bytes remain outside Git. The generated receipt must be distinct from the manifest, publisher and selected inputs; symlink paths are rejected.

## Publish the reviewed checkout

Once the manifest, metadata, publisher and lockfile have been committed, use a real Git checkout at that reviewed revision. Supply its full 40-character lowercase SHA:

```sh
uv run --frozen --project tools/hf-release python tools/hf-release/publisher.py \
  --manifest research/releases/2026-11-22/manifest.json \
  --root . \
  --data-root /path/to/atlas-source-cache \
  --source-revision FULL_REVIEWED_GITHUB_COMMIT_SHA \
  --receipt /path/to/hf-release-upload.json \
  --fetch-sources \
  --upload
```

The official client reads existing Hugging Face authentication from its supported environment/cache. This script accepts no token argument and never prints credentials or data contents. Use the repository's trusted manual workflow or a qualified authenticated execution environment. The script does not register GitHub runners or configure credentials.

Before a Hub mutation, upload mode requires matching Git `HEAD`, tracked and clean selected metadata/manifest/publisher/lockfile, and verified local sizes/hashes. The target is the explicitly named public dataset `edithatogo/rare-omics-atlas`. An existing private target is refused; the script does not change its visibility. A missing target is created publicly only in upload mode.

One official `create_commit` call receives exactly the allowlisted additions plus two generated release records. The observed Hub parent commit is supplied as `parent_commit`, so a concurrent change makes the operation fail. No folder glob, deletion, or unrelated account/repository update is performed.

After commit, the script queries the returned immutable Hub revision. Every selected object's size must match, along with its LFS SHA-256 or, for small ordinary Git files, the Git blob SHA-1 computed with the standard blob header. SHA-1 is used solely for matching Git object identifiers; local content integrity and the release manifest use SHA-256. A verification failure retains the observed Hub commit in the failure receipt so publication cannot be mistaken for an operation that never occurred.

## Manifest contract

Version 1 records `repo_id`, `release_id`, and `objects`. Each object has `path_in_repo`, `kind`, `size_bytes`, `sha256` and a nonempty `redistribution_basis`.

- `metadata`: `source_path` is a canonical relative path under `--root`.
- `source_archive`: `cache_path` is under `--data-root`, with a matching GEO `accession` and exact HTTPS source URL on `ftp.ncbi.nlm.nih.gov`.

Absolute/traversing/aliased paths, symlinks, duplicate destinations, unsupported kinds/sources and hash/size mismatches fail. The implementation does not infer permission from a URL; the reviewed manifest records the source-specific release basis.

The script adds the exact original manifest bytes at `releases/{release_id}/manifest.json`, and deterministic provenance at `releases/{release_id}/provenance.json`. Those reserved paths cannot occur in the input object's destinations. Provenance contains the reviewed GitHub revision, manifest and publisher hashes, and selected object hashes; its own hash is recorded in the external receipt, avoiding a circular checksum.

The existing account estate registry is updated separately after publication/read-back. This publisher neither republishes every source in the catalogue nor treats medallion promotion as scientific qualification or expanded distribution rights.

## Dependencies and checks

`huggingface-hub==2.4.0` provides the Hub API and upload transport. `httpx2[socks]==2.16.2` enables the observed SOCKS proxy configuration through the transport's supported extra. Both and their transitive packages are pinned by `uv.lock` against public PyPI. The native `hf-xet` package remains an official client dependency; no replacement upload engine is written here.

Tests cover malformed/duplicate paths, unsupported URLs, wrong hashes/sizes, symlink rejection, generated-file collisions, deterministic provenance, actual clean/mismatched/dirty Git checkout behavior, private-target refusal, exact parent-guarded commit selection, immutable-revision read-back, Git/LFS hash mismatches, retention of an observed commit after postcheck failure, partial cleanup and preservation of existing mismatched inputs. Fake Hub calls test the contract without publishing test files. Actual upload acceptance additionally requires its observed remote receipt.

Official references: [upload guide](https://huggingface.co/docs/huggingface_hub/guides/upload), [HfApi reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api), and [GEO download documentation](https://www.ncbi.nlm.nih.gov/geo/info/download.html).
