#!/usr/bin/env Rscript
# Compare native R curation with published extension-list arithmetic explicitly.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 5L) stop("usage: compare_gct_lineage.R R_SOURCE RAW_SDF PROBE_INFO EXT_TABLE OUTPUT")
r_source <- normalizePath(args[1], mustWork=TRUE)
output <- args[5]
stopifnot(!file.exists(output))
if (!dir.create(output, recursive=TRUE)) stop("cannot create output")
for (name in c("sesame.R", "SigDFMethods.R")) {
    source(file.path(r_source, name), local=.GlobalEnv, encoding="UTF-8")
}
env <- new.env(parent=baseenv())
loaded <- load(args[3], envir=env)
stopifnot(identical(loaded, "HM450.probeInfo"))
probe_info <- get("HM450.probeInfo", envir=env)
stopifnot(is.list(probe_info), is.character(probe_info$typeI.extC),
    is.character(probe_info$typeI.extT), !anyDuplicated(probe_info$typeI.extC),
    !anyDuplicated(probe_info$typeI.extT))
sesameDataGet <- function(name) {
    stopifnot(identical(name, "HM450.probeInfo"))
    probe_info
}
sdf <- readRDS(args[2])
stopifnot(identical(attr(sdf, "platform"), "HM450"), nrow(sdf) == 486427L,
    !anyDuplicated(sdf$Probe_ID))
ext <- read.delim(gzfile(args[4]), colClasses="character", check.names=FALSE)
stopifnot(ncol(ext) == 1L, nrow(ext) == nrow(sdf), all(ext[[1]] %in% c("C", "T", ".")))
native <- bisConversionControl(sdf)
codes <- ext[[1]]
published <- mean(c(sdf$MG[codes == "C"], sdf$UG[codes == "C"]), na.rm=TRUE) /
    mean(c(sdf$MG[codes == "T"], sdf$UG[codes == "T"]), na.rm=TRUE)
curated_C <- intersect(InfIR(sdf)$Probe_ID, probe_info$typeI.extC)
curated_T <- intersect(InfIR(sdf)$Probe_ID, probe_info$typeI.extT)
sets <- list(curated_C=curated_C, curated_T=curated_T,
    published_C=sdf$Probe_ID[codes == "C"], published_T=sdf$Probe_ID[codes == "T"])
for (name in names(sets)) writeLines(sets[[name]], file.path(output, paste0(name, "-ids.txt")), useBytes=TRUE)
comparison <- data.frame(metric=c("native_bisConversionControl", "published_extension_arithmetic"),
    value=sprintf("%.17g", c(native, published)))
write.table(comparison, file.path(output, "gct-references.tsv"), sep="\t", quote=FALSE,
    row.names=FALSE, fileEncoding="UTF-8")
counts <- data.frame(extension=c("C", "T"),
    original_curated=c(length(probe_info$typeI.extC), length(probe_info$typeI.extT)),
    curated_present_InfIR=c(length(curated_C), length(curated_T)),
    published=c(length(sets$published_C), length(sets$published_T)),
    published_only=c(length(setdiff(sets$published_C, curated_C)), length(setdiff(sets$published_T, curated_T))),
    curated_only=c(length(setdiff(curated_C, sets$published_C)), length(setdiff(curated_T, sets$published_T))))
write.table(counts, file.path(output, "curation-comparison.tsv"), sep="\t", quote=FALSE,
    row.names=FALSE, fileEncoding="UTF-8")
capture.output(sessionInfo(), file=file.path(output, "session-info.txt"))
print(comparison)
print(counts)
