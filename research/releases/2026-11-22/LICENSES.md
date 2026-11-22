# Source-specific reuse and attribution

This repository does not assign one new licence to all source artifacts. The release manifest records a reuse basis for each object. Original sources remain authoritative.

## GEO raw archives

The public archives GSE97362, GSE116300 and GSE218186 are redistributed byte-for-byte under GEO's stated public-data use/distribution policy, with source-owner rights retained. Official policy: https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html and https://www.ncbi.nlm.nih.gov/geo/info/faq.html (checked 22 November 2026). No source-specific distribution prohibition was found in the inspected metadata/archive scope. This is not a claim of an exclusive licence, public-domain status, or unrestricted permission from every possible rights holder.

- GSE97362: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE97362 ; Butcher et al., DOI https://doi.org/10.1016/j.ajhg.2017.04.004 .
- GSE116300: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116300 ; DOI https://doi.org/10.1038/s41431-017-0023-0 .
- GSE218186: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218186 ; publication identifiers are preserved in the catalogue and rights register.

The original TAR files include Illumina platform/manifest files. Their supplied names, headers and attribution are preserved without modification. They are not relicensed under the code licence. Separate journal-article licences do not automatically describe the GEO files; no article full text is included.

## Metadata

The Silver catalogue is a factual, allowlisted transformation of official NCBI and PRIDE metadata. Cite the original repositories, accessions and linked studies. Source API URLs, retrieval dates, byte counts and SHA-256 identifiers are in `silver/catalogue/2026-11-22/requests.jsonl`. Full raw API response bodies, contacts, unrestricted clinical text and individual twin phenotypes are not included.

PRIDE PXD003403 currently declares **EBI terms of use** in its API. Only its factual catalogue entry is included; no proteomics file is mirrored and no retrospective CC0 licence is asserted. Controlled EGA companion files are not included. Source-specific evidence and unresolved questions remain in `metadata/dataset-rights.json`.

Original project documentation and source manifests may be reused with attribution to Rare Omics Atlas and their cited sources. This permission does not expand the terms of third-party datasets. No clinical-use or diagnostic-performance claim is made.
