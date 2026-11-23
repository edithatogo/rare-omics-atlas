#!/usr/bin/env Rscript
# Executes unchanged pinned R numerical functions with only local asset loading.
# This is a source-level reference adapter, not a full sesame package install.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 4L) stop("usage: run_raw_q.R DATA_ROOT R_SOURCE DECODED_MASKS OUTPUT")
data_root <- normalizePath(args[1], mustWork=TRUE)
r_source <- normalizePath(args[2], mustWork=TRUE)
decoded_path <- normalizePath(args[3], mustWork=TRUE)
output <- args[4]
stopifnot(getRversion() == "4.5.2", !file.exists(output))
if (!dir.create(output, recursive=TRUE)) stop("cannot create output")
options(warn=1)
for (name in c("readIDAT.R", "sesame.R", "SigDFMethods.R", "mask.R")) {
    source(file.path(r_source, name), local=.GlobalEnv)
}

env <- new.env(parent=baseenv())
loaded <- load(file.path(data_root, "r-assets", "HM450.address.rda"), envir=env)
stopifnot(identical(loaded, "HM450.address"))
address <- get("HM450.address", envir=env)
manifest <- address$ordering
ordering <- read.delim(gzfile(file.path(data_root,
    "assets/HM450/HM450.ordering.tsv.gz")),
    colClasses=c("character", "integer", "integer", "character"),
    check.names=FALSE, stringsAsFactors=FALSE)
stopifnot(nrow(ordering) == 486427L, nrow(manifest) == 486427L,
    !anyDuplicated(ordering$Probe_ID), !anyDuplicated(manifest$Probe_ID),
    identical(names(ordering), c("Probe_ID", "M", "U", "col")))
r_col <- as.character(manifest$col)
r_col[is.na(r_col)] <- "2"
identity_checks <- c(
    Probe_ID=identical(manifest$Probe_ID, ordering$Probe_ID),
    M=identical(manifest$M, ordering$M),
    U=identical(manifest$U, ordering$U),
    col=identical(r_col, ordering$col),
    no_initial_mask=identical(manifest$mask, rep(FALSE, nrow(manifest))))
write.table(data.frame(field=names(identity_checks), identical=identity_checks),
    file.path(output, "address-comparison.tsv"), sep="\t", quote=FALSE, row.names=FALSE)
stopifnot(all(identity_checks))

mask_db <- readRDS(file.path(data_root, "r-assets", "KYCG.HM450.Mask.20261008.rds"))
decoded <- read.delim(gzfile(decoded_path), colClasses="integer", check.names=FALSE)
stopifnot(nrow(decoded) == nrow(ordering), identical(names(mask_db), names(decoded)))
mask_checks <- lapply(names(mask_db), function(name) {
    members <- mask_db[[name]]
    stopifnot(is.character(members), !anyDuplicated(members),
        all(decoded[[name]] %in% c(0L, 1L)))
    data.frame(track=name, r_count=length(members),
        decoded_count=sum(decoded[[name]]),
        absent_from_complete_order=length(setdiff(members, ordering$Probe_ID)),
        mismatched_bits=sum((ordering$Probe_ID %in% members) != as.logical(decoded[[name]])))
})
mask_checks <- do.call(rbind, mask_checks)
write.table(mask_checks, file.path(output, "mask-comparison.tsv"),
    sep="\t", quote=FALSE, row.names=FALSE)
stopifnot(all(mask_checks$absent_from_complete_order == 0L),
    all(mask_checks$mismatched_bits == 0L),
    all(mask_checks$r_count == mask_checks$decoded_count))

# The explicit HM450 contract replaces only platform autodetection/cache access.
# readIDAT and chipAddressToSignal below are unchanged upstream functions.
green <- readIDAT(file.path(data_root, "idats/HM450/3999492009_R01C01_Grn.idat"))
red <- readIDAT(file.path(data_root, "idats/HM450/3999492009_R01C01_Red.idat"))
stopifnot(identical(rownames(green$Quants), rownames(red$Quants)),
    nrow(green$Quants) == 622399L, nrow(red$Quants) == 622399L)
dm <- cbind(G=green$Quants[,"Mean"], R=red$Quants[,"Mean"],
    GN=green$Quants[,"NBeads"], RN=red$Quants[,"NBeads"])
attr(dm, "platform") <- "HM450"
sdf <- chipAddressToSignal(dm, manifest, min_beads=NULL)
attr(sdf, "platform") <- "HM450"
stopifnot(identical(sdf$Probe_ID, ordering$Probe_ID), !any(sdf$mask))
raw_beta <- getBetas(sdf)
tracks <- recommendedMaskNames("HM450")
stopifnot(identical(tracks, c("M_1baseSwitchSNPcommon_5pt", "M_2extBase_SNPcommon_5pt",
    "M_mapping", "M_nonuniq", "M_SNPcommon_5pt")))
q_ids <- unique(unlist(mask_db[tracks], use.names=FALSE))
sq <- qualityMask(sdf, mask=q_ids)
q_beta <- getBetas(sq)
stopifnot(identical(names(raw_beta), ordering$Probe_ID),
    identical(names(q_beta), ordering$Probe_ID),
    identical(sq$mask, ordering$Probe_ID %in% q_ids))

write_f64 <- function(value, name) {
    writeBin(as.double(value), file.path(output, name), size=8L, endian="little")
}
writeLines(ordering$Probe_ID, file.path(output, "probe-ids.txt"), useBytes=TRUE)
mu <- signalMU(sdf, mask=FALSE)
stopifnot(identical(mu$Probe_ID, ordering$Probe_ID))
write_f64(mu$M, "M-signal.f64")
write_f64(mu$U, "U-signal.f64")
write_f64(raw_beta, "raw-beta.f64")
write_f64(q_beta, "q-beta.f64")
writeBin(as.raw(sq$mask), file.path(output, "q-mask.u8"))
saveRDS(sdf, file.path(output, "raw-sdf.rds"), version=3)
saveRDS(sq, file.path(output, "q-sdf.rds"), version=3)
writeLines(c("Source-level adapter; no full sesame package installation.",
    "Unmodified readIDAT -> explicit paired matrix -> unmodified chipAddressToSignal.",
    "Platform is explicitly HM450; min_beads=NULL; no automatic platform/cache lookup.",
    "Unmodified getBetas and qualityMask(mask=the published R five-track union).",
    "All complete ordered address rows and all 24 published mask tracks compared exactly."),
    file.path(output, "adapter-scope.txt"))
capture.output(sessionInfo(), file=file.path(output, "session-info.txt"))
summary <- data.frame(probes=length(raw_beta), raw_na=sum(is.na(raw_beta)),
    q_masked=sum(sq$mask), q_na=sum(is.na(q_beta)),
    annotation_tracks=nrow(mask_checks), annotation_bit_mismatches=sum(mask_checks$mismatched_bits))
write.table(summary, file.path(output, "summary.tsv"),
    sep="\t", quote=FALSE, row.names=FALSE)
print(summary)
