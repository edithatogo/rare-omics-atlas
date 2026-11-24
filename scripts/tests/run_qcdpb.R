#!/usr/bin/env Rscript
# Unchanged upstream prepSesame("QCDPB") and numerical functions.
# The only adapter supplies the two exact downloaded annotation objects locally.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 4L) stop("usage: run_qcdpb.R DATA_ROOT R_SOURCE RAW_REFERENCE OUTPUT")
data_root <- normalizePath(args[1], mustWork=TRUE)
r_source <- normalizePath(args[2], mustWork=TRUE)
raw_reference <- normalizePath(args[3], mustWork=TRUE)
output <- args[4]
stopifnot(getRversion() == "4.5.2", !file.exists(output))
if (!dir.create(output, recursive=TRUE)) stop("cannot create output")
options(warn=1)
suppressPackageStartupMessages(library(methods))
suppressPackageStartupMessages(library(preprocessCore))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(stringr))
for (name in c("readIDAT.R", "sesame.R", "SigDFMethods.R", "mask.R", "QC.R",
    "channel_inference.R", "dye_bias.R", "detection.R", "background.R", "open.R")) {
    source(file.path(r_source, name), local=.GlobalEnv)
}

env <- new.env(parent=baseenv())
loaded <- load(file.path(data_root, "r-assets", "HM450.address.rda"), envir=env)
stopifnot(identical(loaded, "HM450.address"))
address <- get("HM450.address", envir=env)
mask_db <- readRDS(file.path(data_root, "r-assets", "KYCG.HM450.Mask.20261008.rds"))
assets <- list(HM450.address=address, KYCG.HM450.Mask.20261008=mask_db)
metadata <- data.frame(Title=names(assets), Description=c(
    "HM450 array probe addresses, ordering and hg38",
    "KYCG categorical database holding HM450 probe masking"), stringsAsFactors=FALSE)
# These getters replace sesameData's cache/network access only; mask selection,
# native qualityMask, backgroundMask and all numerical functions stay unchanged.
sesameDataList <- function(keyword=NULL, full=FALSE) {
    stopifnot(is.null(keyword) || identical(keyword, "KYCG"), is.logical(full))
    if (is.null(keyword)) metadata else metadata[grepl(keyword, metadata$Title), , drop=FALSE]
}
sesameDataGet <- function(name) {
    stopifnot(is.character(name), length(name) == 1L, name %in% names(assets))
    assets[[name]]
}
sesameDataHas <- function(name) {
    stopifnot(is.character(name))
    name %in% names(assets)
}

sdf <- readRDS(file.path(raw_reference, "raw-sdf.rds"))
sq <- readRDS(file.path(raw_reference, "q-sdf.rds"))
ids <- readLines(file.path(raw_reference, "probe-ids.txt"))
stopifnot(length(ids) == 486427L, !anyDuplicated(ids),
    identical(sdf$Probe_ID, ids), identical(sq$Probe_ID, ids),
    identical(qualityMask(sdf)$mask, sq$mask))
bg <- unique(backgroundMask("HM450"))
stopifnot(all(bg %in% ids))
writeLines(bg, file.path(output, "background-mask-ids.txt"), useBytes=TRUE)

processed <- prepSesame(sdf, "QCDPB")
beta <- getBetas(processed)
stopifnot(identical(processed$Probe_ID, ids), identical(names(beta), ids),
    length(beta) == length(ids), all(is.na(beta) | is.finite(beta)))
mu <- signalMU(processed, mask=FALSE)
stopifnot(identical(mu$Probe_ID, ids))
writeBin(as.double(beta), file.path(output, "qcdpb-beta.f64"), size=8L, endian="little")
writeBin(as.double(mu$M), file.path(output, "M-signal.f64"), size=8L, endian="little")
writeBin(as.double(mu$U), file.path(output, "U-signal.f64"), size=8L, endian="little")
writeBin(as.raw(processed$mask), file.path(output, "final-mask.u8"))
writeLines(ids, file.path(output, "probe-ids.txt"), useBytes=TRUE)
writeLines(as.character(processed$col), file.path(output, "channels.txt"))
saveRDS(processed, file.path(output, "qcdpb-sdf.rds"), version=3)
capture.output(sessionInfo(), file=file.path(output, "session-info.txt"))
writeLines(c("Source-level reference; not full sesame package installation.",
    "Input raw SigDF already qualified over every address, signal and raw/Q beta.",
    "Only sesameDataList/Get/Has are local exact-object cache adapters.",
    "Native mask discovery, qualityMask, backgroundMask and prepSesame are unchanged.",
    "prepSesame(sdf, QCDPB) uses all upstream default numerical arguments.",
    "Single selected public HM450 technical fixture; no EPIC/device/disease admission."),
    file.path(output, "adapter-scope.txt"))
summary <- data.frame(probes=length(beta), missing=sum(is.na(beta)),
    finite=sum(is.finite(beta)), final_masked=sum(processed$mask),
    background_masked=length(bg), q_masked=sum(sq$mask))
write.table(summary, file.path(output, "summary.tsv"), sep="\t", quote=FALSE, row.names=FALSE)
print(summary)
