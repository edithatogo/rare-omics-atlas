# Local development and hardware

**Updated 22 November 2026.** The owner requires the **official GitHub Actions runner** for local development qualification. This means the runner distributed from [actions/runner](https://github.com/actions/runner), registered as a self-hosted runner; an Actions emulator such as act is not acceptance evidence for this requirement.

## Hardware record

Purchase/configuration correspondence was privately inspected on 22 November 2026. Only relevant machine specifications are recorded here; no invoices, email identifiers, personal addresses, order identifiers or payment details are published. These are historical configuration records, not live hardware detection or benchmark results.

| Machine | Evidence-supported configuration | Proposed role |
|---|---|---|
| 14-inch MacBook Pro | Apple M1 Max; 10-core CPU, 24-core GPU; 32 GB unified memory; 512 GB SSD | Interactive work, small/cohort-level CPU analyses, Apple ARM64 compatibility and numerical checks |
| Desktop workstation | Intel Core i9-14900K, 24 cores / 32 threads; 128 GB DDR5; NVIDIA GeForce RTX 4060 with 8 GB VRAM; 4 TB Samsung 990 PRO NVMe; additional 500 GB NVMe for Linux; Windows 11 Pro and configured Linux dual boot | Main CPU/memory-intensive matrix processing and resampling; Windows x64 and separately Linux x64 qualification; CUDA only for a justified supported workload |

The invoice identifies **RTX 4060**, resolving the earlier ambiguous “4600”. Do not copy every vendor description as a verified hardware specification; the live GPU/driver, OS, installed RAM, free disk and effective memory settings must be recorded when an actual run begins. The desktop's two boot environments are not two independent machines.

For scale, an illustrative 850,000-probe × 200-sample float64 matrix contains **1.36 GB of numeric values** (850,000 × 200 × 8 bytes), before IDs, masks, copies, intensities and model workspace. One 850,000 × 62 matrix is about 422 MB. These arithmetic examples are not measured peak memory. Use cohort-wise processing and record actual peak RSS and disk use. The 128 GB workstation offers useful headroom; the M1's 32 GB is sufficient to investigate modest cohorts with a measured memory plan. Its 512 GB disk makes unnecessary duplicate raw archives particularly unattractive.

Keep CPU float64 as the numerical reference. GPU memory is not extra CPU RAM, Apple Metal does not provide double precision in the same way as CPU code, and GPU hardware alone does not justify a GPU implementation. No job has been benchmarked on either device in this review.

## Official local runner policy

Use the official [self-hosted runner reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners), [installation guidance](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners) and [security guidance](https://docs.github.com/en/actions/reference/security/secure-use). The proposed lanes are:

| Lane | Required host identity / intended labels | Acceptance |
|---|---|---|
| Mac CPU | official runner, macOS ARM64; standard labels self-hosted/macOS/ARM64 plus a project-specific local label | Pinned-source build and relevant float64 numerical/consumer checks |
| Windows CPU | official runner, Windows x64; self-hosted/Windows/X64 plus project label | Native toolchain and scientific contract checks; WSL/Linux results do not prove Windows acceptance |
| Linux CPU | official runner on a supported Linux x64 environment; self-hosted/Linux/X64 plus project label | Linux-specific CLI/build qualification, especially C or compiler-dependent components |
| NVIDIA | Same qualified desktop environment plus a verified custom GPU label | Only after driver/device/runtime capability and the exact CPU-versus-GPU numerical comparison pass |

These are intended labels, not claims of existing registrations. GitHub's documented supported OS/version matrix must be checked against the installed system; the Linux dual-boot record alone does not prove a supported distribution/version.

For this public repository, **do not automatically run untrusted pull-request code on either personal workstation**. Use maintained/trusted revisions and an explicitly invoked local qualification workflow, a dedicated account or isolated environment, least-privilege tokens, time/resource limits and a clean working directory. Do not expose patient files, credentials, home directories or private evidence in workspaces, caches or uploaded logs. GitHub specifically warns that untrusted jobs can persistently compromise self-hosted runners; labels and ephemeral registration alone do not sandbox arbitrary code.

Use separate caches keyed by OS/architecture/toolchain and relevant dependency/source state. A runner receipt records exact source and workflow SHA, runner release/OS/architecture, toolchain/dependencies, input hashes, commands, run URL/job, outcome, timing, peak memory and unavailable measurements. A source review, shell invocation in this cloud workspace, configured YAML or queued job is not a local-runner success.

The existing central [Rust reusable workflow](https://github.com/edithatogo/repository-standards/blob/main/.github/workflows/rust-ci.yml) currently selects a hosted Ubuntu runner. It cannot be described as the requested local lane without an explicit supported runner selection or a small repository-specific workflow when there are actual checks to run. Retain any applicable hosted release/security gates; local development qualification and hosted release attestation have different purposes.

**Current status:** the actual limma-rust fork now has a [manual official self-hosted workflow](https://github.com/edithatogo/limma-rust/blob/main/.github/workflows/local-qualification.yml) for existing formatting, clippy and corpus checks. Its [setup receipt](https://github.com/edithatogo/limma-rust/blob/main/conductor/evidence/local-workflow-setup-2026-11-22.md) names labels and prerequisites. No owner device, runner registration, service activation or local job was observed. The 104-test cloud Linux replay is separately recorded and does not close this gate. No empty analysis workflow was added to the atlas.
