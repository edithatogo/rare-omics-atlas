#!/usr/bin/env Rscript
# Successor oracle: native GCT over an independently R-decoded raw SigDF.
# The parent run_qc_reference.R supplies the unchanged 65-field native panel.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 4L) {
    stop("usage: run_native_gct_reference.R R_SOURCE RAW_REFERENCE PROBE_INFO OUTPUT")
}
r_source <- normalizePath(args[1], mustWork=TRUE)
reference <- normalizePath(args[2], mustWork=TRUE)
probe_info_path <- normalizePath(args[3], mustWork=TRUE)
output <- args[4]
stopifnot(getRversion() == "4.5.2", !file.exists(output))
if (!dir.create(output, recursive=TRUE)) stop("cannot create output")
source(file.path(r_source, "sesame.R"), local=.GlobalEnv, encoding="UTF-8")
source(file.path(r_source, "SigDFMethods.R"), local=.GlobalEnv, encoding="UTF-8")
env <- new.env(parent=baseenv())
stopifnot(identical(load(probe_info_path, envir=env), "HM450.probeInfo"))
probe_info <- get("HM450.probeInfo", envir=env)
for (name in c("typeI.extC", "typeI.extT")) {
    stopifnot(is.character(probe_info[[name]]), !anyNA(probe_info[[name]]),
        !anyDuplicated(probe_info[[name]]))
}
sesameDataGet <- function(name) {
    stopifnot(identical(name, "HM450.probeInfo"))
    probe_info
}
sdf <- readRDS(file.path(reference, "raw-sdf.rds"))
ids <- readLines(file.path(reference, "probe-ids.txt"))
stopifnot(identical(sdfPlatform(sdf), "HM450"), identical(sdf$Probe_ID, ids),
    length(ids) == 486427L, !anyNA(ids), !anyDuplicated(ids))
curated_C <- intersect(InfIR(sdf)$Probe_ID, probe_info$typeI.extC)
curated_T <- intersect(InfIR(sdf)$Probe_ID, probe_info$typeI.extT)
stopifnot(length(curated_C) == 45427L, length(curated_T) == 15148L,
    !length(intersect(curated_C, curated_T)))
gct <- bisConversionControl(sdf)
stopifnot(length(gct) == 1L, is.finite(gct))
qc <- read.delim(file.path(reference, "native-r-qc.tsv"), colClasses="character",
    check.names=FALSE, stringsAsFactors=FALSE)
stopifnot(identical(names(qc), c("metric", "value")), nrow(qc) == 65L,
    !anyDuplicated(qc$metric), !"GCT" %in% qc$metric)
write.table(rbind(qc, data.frame(metric="GCT", value=sprintf("%.17g", gct))),
    file.path(output, "qc-reference.tsv"), sep="\t", quote=FALSE,
    row.names=FALSE, fileEncoding="UTF-8")
ext <- rep(".", length(ids))
ext[match(curated_C, ids)] <- "C"
ext[match(curated_T, ids)] <- "T"
writeLines(c("ext", ext), file.path(output, "native-typeI-ext.tsv"), useBytes=TRUE)
writeLines(curated_C, file.path(output, "native-curated-C.ids.txt"), useBytes=TRUE)
writeLines(curated_T, file.path(output, "native-curated-T.ids.txt"), useBytes=TRUE)
stopifnot(file.copy(file.path(reference, "pvalues-reference.tsv.gz"), output))
capture.output(sessionInfo(), file=file.path(output, "session-info.txt"))
cat(sprintf("native_GCT=%.17g; C=%d; T=%d; probes=%d\n",
    gct, length(curated_C), length(curated_T), length(ids)))
