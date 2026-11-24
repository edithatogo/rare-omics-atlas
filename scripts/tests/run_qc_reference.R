#!/usr/bin/env Rscript
# Source-level independent reference. No producer output is consumed here.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 4L) stop("usage: run_qc_reference.R DATA_ROOT R_SOURCE OUTPUT MIN_BEADS")
data_root <- normalizePath(args[1], mustWork=TRUE)
r_source <- normalizePath(args[2], mustWork=TRUE)
output <- args[3]
min_beads <- as.integer(args[4])
stopifnot(getRversion() == "4.5.2", min_beads %in% c(0L, 3L), !file.exists(output))
if (!dir.create(output, recursive=TRUE)) stop("cannot create output")
options(warn=1)
suppressPackageStartupMessages(library(methods))
suppressPackageStartupMessages(library(preprocessCore))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(stringr))
for (name in c("readIDAT.R", "sesame.R", "SigDFMethods.R", "mask.R", "QC.R",
    "channel_inference.R", "dye_bias.R", "detection.R", "background.R", "open.R")) {
    source(file.path(r_source, name), local=.GlobalEnv, encoding="UTF-8")
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
# Only exact-object cache access is adapted. Numerical/mask functions unchanged.
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

prefix <- file.path(data_root, "idats/HM450/3999492009_R01C01")
# Same explicit-platform adapter used by the already-qualified raw/Q reference.
# readIDATpair's readIDAT1 always calls platform inference before its explicit
# override, requiring an unrelated idatSignature cache object. Avoid that cache
# call; execute unchanged readIDAT and chipAddressToSignal on paired originals.
green <- readIDAT(paste0(prefix, "_Grn.idat"))
red <- readIDAT(paste0(prefix, "_Red.idat"))
stopifnot(identical(rownames(green$Quants), rownames(red$Quants)),
    nrow(green$Quants) == 622399L, nrow(red$Quants) == 622399L)
dm <- cbind(G=green$Quants[,"Mean"], R=red$Quants[,"Mean"],
    GN=green$Quants[,"NBeads"], RN=red$Quants[,"NBeads"])
attr(dm, "platform") <- "HM450"
sdf <- chipAddressToSignal(dm, address$ordering,
    min_beads=if (min_beads == 0L) NULL else min_beads)
attr(sdf, "platform") <- "HM450"
writeLines(rownames(green$Quants), file.path(output, "original-address-ids.txt"), useBytes=TRUE)
writeBin(as.raw(green$Quants[,"NBeads"]), file.path(output, "original-green-beads.u8"))
writeBin(as.raw(red$Quants[,"NBeads"]), file.path(output, "original-red-beads.u8"))
ids <- sdf$Probe_ID
stopifnot(length(ids) == 486427L, !anyDuplicated(ids),
    identical(ids, address$ordering$Probe_ID))
writeLines(ids, file.path(output, "probe-ids.txt"), useBytes=TRUE)
saveRDS(sdf, file.path(output, "raw-sdf.rds"), version=3)
writeBin(as.raw(sdf$mask), file.path(output, "initial-bead-mask.u8"))

qc <- unlist(sesameQC_calcStats(sdf)@stat)
stopifnot(length(qc) == 65L, !anyDuplicated(names(qc)), !"GCT" %in% names(qc))
qc_rows <- data.frame(metric=names(qc), value=sprintf("%.17g", unname(qc)))
write.table(qc_rows, file.path(output, "native-r-qc.tsv"),
    sep="\t", quote=FALSE, row.names=FALSE, fileEncoding="UTF-8")

# Independent arithmetic oracle for the C producer's published extension lists.
# This is NOT native bisConversionControl's older probeInfo curation.
ext <- read.delim(gzfile(file.path(data_root, "assets/HM450/HM450.typeI_ext.tsv.gz")),
    colClasses="character", check.names=FALSE, stringsAsFactors=FALSE)
stopifnot(ncol(ext) == 1L, nrow(ext) == length(ids), all(ext[[1]] %in% c("C", "T", ".")))
ext_code <- ext[[1]]
gct <- mean(c(sdf$MG[ext_code == "C"], sdf$UG[ext_code == "C"]), na.rm=TRUE) /
    mean(c(sdf$MG[ext_code == "T"], sdf$UG[ext_code == "T"]), na.rm=TRUE)
stopifnot(is.finite(gct))
write.table(rbind(qc_rows, data.frame(metric="GCT", value=sprintf("%.17g", gct))),
    file.path(output, "qc-reference.tsv"), sep="\t", quote=FALSE,
    row.names=FALSE, fileEncoding="UTF-8")
gct_lineage <- do.call(rbind, lapply(c("C", "T", "."), function(code) {
    do.call(rbind, lapply(c("R", "G", "2"), function(channel) {
        data.frame(extension=code, channel=channel,
            count=sum(ext_code == code & as.character(sdf$col) == channel))
    }))
}))
write.table(gct_lineage, file.path(output, "gct-extension-lineage.tsv"),
    sep="\t", quote=FALSE, row.names=FALSE, fileEncoding="UTF-8")
writeLines(c("GCT is independently computed in R from raw R-decoded signals and the pinned published positional extension table.",
    "It does not call native bisConversionControl; native HM450.probeInfo curation is a distinct reference.",
    "C/R native QC parity covers 65 metrics; the extra GCT value qualifies only the published-list arithmetic."),
    file.path(output, "gct-scope.txt"), useBytes=TRUE)

raw_pval <- pOOBAH(sdf, return.pval=TRUE)
qcd <- prepSesame(sdf, "QCD")
qcd_pval <- pOOBAH(qcd, return.pval=TRUE)
stopifnot(identical(names(raw_pval), ids), identical(names(qcd_pval), ids),
    all(is.finite(raw_pval)), all(is.finite(qcd_pval)),
    all(raw_pval >= 0 & raw_pval <= 1), all(qcd_pval >= 0 & qcd_pval <= 1))
writeBin(as.double(raw_pval), file.path(output, "raw-pval.f64"), size=8L, endian="little")
writeBin(as.double(qcd_pval), file.path(output, "qcd-pval.f64"), size=8L, endian="little")
writeBin(as.raw(qcd$mask), file.path(output, "qcd-mask.u8"))
writeBin(as.raw(pOOBAH(qcd)$mask), file.path(output, "qcdp-mask.u8"))
write.table(data.frame(Probe_ID=ids, raw_pval=sprintf("%.17g", raw_pval),
    qcd_pval=sprintf("%.17g", qcd_pval)), file.path(output, "pvalues-reference.tsv"),
    sep="\t", quote=FALSE, row.names=FALSE, fileEncoding="UTF-8")

missing_signal <- is.na(sdf$MG) & is.na(sdf$UG) & is.na(sdf$MR) & is.na(sdf$UR)
summary <- data.frame(probes=length(ids), min_beads=min_beads,
    initial_bead_masked=sum(sdf$mask), no_signal=sum(missing_signal),
    raw_detection_failed=sum(raw_pval > 0.05), qcd_masked_before_P=sum(qcd$mask),
    qcd_detection_failed=sum(qcd_pval > 0.05), qcdp_masked=sum(pOOBAH(qcd)$mask),
    native_qc_metrics=length(qc), gct_published_lists=gct)
write.table(summary, file.path(output, "summary.tsv"), sep="\t", quote=FALSE,
    row.names=FALSE, fileEncoding="UTF-8")
capture.output(sessionInfo(), file=file.path(output, "session-info.txt"))
print(summary)
