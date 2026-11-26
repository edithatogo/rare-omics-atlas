#!/usr/bin/env Rscript
# Installed native package qualification, unrelated technical/synthetic inputs only.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4L)
stage <- match.arg(args[3],c("install","technical","limma","enrichment","annotation"))
scratch <- normalizePath(args[4],mustWork=TRUE)
input <- normalizePath(args[1],mustWork=TRUE)
output <- normalizePath(args[2],mustWork=TRUE)
options(timeout=600,Ncpus=2,warn=1)
stopifnot(getRversion()>="4.5.0",getRversion()<"4.6.0",
    as.character(BiocManager::version())=="3.22")
expected <- c(sesame="1.28.1",sesameData="1.28.0",
    limma="3.66.0",missMethyl="1.44.0")
repos <- BiocManager::repositories(version="3.22")
options(repos=repos)
if (stage=="install") write.table(data.frame(repository=names(repos),url=unname(repos)),
    file.path(output,"repositories.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
if (stage=="install") BiocManager::install(names(expected),version="3.22",ask=FALSE,update=FALSE,Ncpus=2L)
versions <- vapply(names(expected),function(p) as.character(packageVersion(p)),character(1))
stopifnot(identical(versions,expected))
if (stage=="install") write.table(installed.packages()[,c("Package","Version","Built"),drop=FALSE],
    file.path(output,"installed-packages.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
if (stage=="install") quit(save="no",status=0L)

if (stage=="technical") {
    suppressPackageStartupMessages(library(sesame))
    suppressPackageStartupMessages(library(sesameData))

    catalogue <- sesameDataList(full=TRUE)
    mask_titles <- grep("^KYCG\\.HM450\\.Mask",catalogue$Title,value=TRUE,ignore.case=TRUE)
    required <- unique(c("idatSignature","HM450.address","HM450.probeInfo",mask_titles))
    stopifnot(length(mask_titles)>0L,all(required %in% catalogue$Title))
    stopifnot(isTRUE(sesameDataCache(required)))
    sha256 <- function(path) {
        answer <- system2("sha256sum",shQuote(path),stdout=TRUE,stderr=TRUE)
        stopifnot(length(answer)==1L,grepl("^[0-9a-f]{64} ",answer))
        substr(answer,1L,64L)
    }
    asset_hashes <- vapply(required,function(title) {
        tmp <- tempfile(fileext=".rds")
        on.exit(unlink(tmp))
        saveRDS(sesameDataGet(title),tmp,version=3)
        sha256(tmp)
    },character(1))
    asset_rows <- catalogue[match(required,catalogue$Title),c("EHID","Title"),drop=FALSE]
    asset_rows$serialized_rds_sha256 <- unname(asset_hashes)
    write.table(asset_rows,file.path(output,"reference-objects.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    capture.output(sessionInfo(),file=file.path(output,"technical-session-info.txt"))
    mask_names <- recommendedMaskNames()[["HM450"]]
    stopifnot(length(mask_names)>0L,all(mask_names %in% listAvailableMasks("HM450")))
    prefix <- file.path(input,"3999492009_R01C01")
    raw <- readIDATpair(prefix,platform="HM450",min_beads=NULL)
    stopifnot(length(raw$Probe_ID)>100000L,!anyDuplicated(raw$Probe_ID))
    qcd <- prepSesame(raw,"QCD")
    pval <- pOOBAH(qcd,return.pval=TRUE)
    stopifnot(identical(names(pval),raw$Probe_ID),
        all(is.na(pval)|(is.finite(pval)&pval>=0&pval<=1)))
    processed <- prepSesame(raw,"QCDPB")
    beta <- getBetas(processed)
    staged <- getBetas(noob(pOOBAH(qcd)))
    stopifnot(identical(raw$Probe_ID,processed$Probe_ID),
        identical(names(beta),raw$Probe_ID),identical(names(beta),names(staged)),
        identical(is.na(beta),is.na(staged)),
        all(is.na(beta)|(is.finite(beta)&beta>=0&beta<=1)),
        all(is.na(beta[processed$mask])),max(abs(beta-staged),na.rm=TRUE)<=1e-12)
    mu <- signalMU(processed,mask=FALSE)
    stopifnot(!anyDuplicated(mu$Probe_ID))
    ix <- match(names(beta),mu$Probe_ID)
    finite <- is.finite(beta)
    stopifnot(sum(finite)>100000L,all(!is.na(ix[finite])))
    formula <- pmax(mu$M[ix[finite]],1)/pmax(mu$M[ix[finite]]+mu$U[ix[finite]],2)
    beta_error <- max(abs(beta[finite]-formula))
    stopifnot(is.finite(beta_error),beta_error<=1e-12)
    prior <- read.delim(gzfile(file.path(input,"HM450.ordering.tsv.gz")),
        stringsAsFactors=FALSE,check.names=FALSE)$Probe_ID
    stopifnot(length(prior)==486427L,!anyDuplicated(prior))
    qc <- sesameQC_calcStats(raw,"detection")
    stopifnot(inherits(qc,"sesameQC"))
    interior <- finite & beta>0 & beta<1
    m <- rep(NA_real_,length(beta))
    names(m) <- names(beta)
    m[interior] <- log2(beta[interior]/(1-beta[interior]))
    stopifnot(all(is.finite(m[interior])),all(is.na(m[!interior])))
    summary <- data.frame(metric=c("raw_probe_count","finite_beta","missing_beta",
        "finite_endpoints","finite_M","max_beta_formula_error","prior_order_exact",
        "prior_only_probes","selected_release_only_probes","qc_stats_computed"),
        value=c(length(beta),sum(finite),sum(is.na(beta)),sum(finite & !interior),
        sum(is.finite(m)),beta_error,as.integer(identical(raw$Probe_ID,prior)),
        length(setdiff(prior,raw$Probe_ID)),length(setdiff(raw$Probe_ID,prior)),1L))
    write.table(summary,file.path(output,"technical-summary.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    print(summary)

    universe <- sort(names(beta)[interior & grepl("^cg[0-9]+$",names(beta))])
    stopifnot(length(universe)>=4000L)
    universe <- universe[unique(round(seq(1,length(universe),length.out=4000L)))]
    stopifnot(length(universe)==4000L)
    writeLines(universe,file.path(scratch,"synthetic-probe-universe.txt"))

    # Outcome-blind scientific-QC policy exercise on this unrelated fixture.
    # Fixed universe is independent of detection, bead count and observed beta.
    manifest_ids <- sesameDataGet("HM450.address")$ordering$Probe_ID
    # Reuse native hg38 coordinates with the native hg38 recommended masks.
    # The separate missMethyl gene mapping below retains its native hg19 annotation.
    annotation <- sesameData::sesameData_getManifestGRanges("HM450",genome="hg38")
    stopifnot(identical(manifest_ids,raw$Probe_ID),!anyDuplicated(manifest_ids),
        inherits(annotation,"GRanges"),length(annotation)>0L,
        length(names(annotation))==length(annotation),!anyNA(names(annotation)),
        all(nzchar(names(annotation))),!anyDuplicated(names(annotation)),
        all(c("mapping","sub30_copy") %in% mask_names))
    chr <- as.character(GenomicRanges::seqnames(annotation))
    position <- GenomicRanges::start(annotation)
    end <- GenomicRanges::end(annotation)
    autosomal <- chr %in% paste0("chr",1:22)&is.finite(position)&position>0&
        is.finite(end)&end>=position
    recommended <- getMask("HM450",mask_names="recommended")
    stopifnot(length(recommended)>0L,!anyNA(recommended))
    fixed_cpg <- manifest_ids[grepl("^cg[0-9]+$",manifest_ids)]
    fixed_annotated <- fixed_cpg[fixed_cpg %in% names(annotation)]
    fixed_autosomal <- fixed_annotated[fixed_annotated %in% names(annotation)[autosomal]]
    eligible <- sort(setdiff(fixed_autosomal,recommended),method="radix")
    stopifnot(length(eligible)>0L,!anyDuplicated(eligible))
    denominator_path <- file.path(output,"technical-cohort-qc-denominator.txt")
    writeLines(eligible,denominator_path)
    denominator_sha <- sha256(denominator_path)
    writeLines(mask_names,file.path(output,"technical-cohort-qc-mask-names.txt"))
    tmp <- tempfile(fileext=".rds")
    saveRDS(annotation,tmp,version=3)
    annotation_sha <- sha256(tmp)
    unlink(tmp)
    rm(annotation)
    invisible(gc(full=TRUE))
    # Candidate validity rule: missing detection, failed bead or any
    # processing mask invalidates an observation; endpoint beta remains NA.
    valid_measurement <- function(beta,p,mask,bead_mask) {
        stopifnot(length(beta)==length(p),length(beta)==length(mask),
            length(beta)==length(bead_mask))
        is.finite(beta)&beta>0&beta<1&is.finite(p)&p>=0&p<=0.05&
            !is.na(mask)&!mask&!is.na(bead_mask)&!bead_mask
    }
    stopifnot(identical(valid_measurement(
        c(.5,.5,.5,NA_real_,0,1,.5,.5,.5,.5,.5),
        c(.05,.050001,NA_real_,.01,.01,.01,.01,.01,-.01,Inf,.01),
        c(FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,NA,FALSE,FALSE,FALSE),
        c(rep(FALSE,10),TRUE)),c(TRUE,rep(FALSE,10))))
    raw3 <- readIDATpair(prefix,platform="HM450",min_beads=3L)
    stopifnot(identical(raw3$Probe_ID,manifest_ids),!anyNA(raw3$mask),
        all(raw3$mask[raw$mask]))
    # The preceding independently received T07b/T07d evidence qualifies
    # address-level counts. Exercise native min-beads here, without a
    # second production IDAT parser or custom masking implementation.
    # Reproduce the actual pinned SeSAMe 1.28.1 legacy-control defect before
    # correcting anything: old positional names place red bead count in Type.
    # Both pOOBAH and noob then omit their intended negative-control input.
    legacy_controls <- sesame::controls(raw3)
    negative_controls <- getFromNamespace("negControls","sesame")
    stopifnot(nrow(legacy_controls)>0L,
        all(grepl("^[0-9]+$",as.character(legacy_controls$Type))),
        nrow(negative_controls(raw3))==0L)
    write.table(legacy_controls,file.path(output,"technical-cohort-qc-legacy-controls.tsv"),
        sep="\t",quote=FALSE,row.names=FALSE)
    legacy_qcd3 <- prepSesame(raw3,"QCD")
    legacy_p3 <- pOOBAH(legacy_qcd3,return.pval=TRUE)
    legacy_processed3 <- noob(pOOBAH(legacy_qcd3,pval.threshold=0.05))
    legacy_b3 <- getBetas(legacy_processed3)
    legacy_mask3 <- legacy_processed3$mask
    stopifnot(identical(names(legacy_p3),manifest_ids),
        identical(names(legacy_b3),manifest_ids),!anyNA(legacy_mask3))
    rm(legacy_qcd3,legacy_processed3)
    invisible(gc(full=TRUE))

    # Use the existing native manifest-based controls() branch, rather than
    # invent a new parser, relabel the old bead-count column, or port pOOBAH.
    # Verify identity, source signals, legacy bead count and exact join on
    # the unrelated author fixture independently of the malformed attribute.
    canonical <- sesameDataGet("HM450.address")$controls
    stopifnot(is.data.frame(canonical),all(c("Address","Type") %in% names(canonical)),
        nrow(canonical)>0L,!anyNA(canonical$Address),
        !anyDuplicated(as.character(canonical$Address)),
        !anyNA(canonical$Type),all(nzchar(as.character(canonical$Type))))
    address <- as.character(canonical$Address)
    raw_reader <- getFromNamespace("readIDAT","sesame")
    green <- raw_reader(paste0(prefix,"_Grn.idat"))$Quants
    red <- raw_reader(paste0(prefix,"_Red.idat"))$Quants
    stopifnot(!anyDuplicated(rownames(green)),!anyDuplicated(rownames(red)),
        identical(rownames(green),rownames(red)),
        all(c("Mean","NBeads") %in% colnames(green)),
        all(c("Mean","NBeads") %in% colnames(red)))
    g <- as.numeric(green[match(address,rownames(green)),"Mean"])
    r <- as.numeric(red[match(address,rownames(red)),"Mean"])
    rn <- as.numeric(red[match(address,rownames(red)),"NBeads"])
    available <- is.finite(g)&is.finite(r)
    stopifnot(nrow(legacy_controls)==sum(available),
        identical(as.numeric(legacy_controls$UG),g[available]),
        identical(as.numeric(legacy_controls$UR),r[available]),
        identical(as.numeric(as.character(legacy_controls$Type)),rn[available]))
    rm(green,red,rn)
    # Remove only the deprecated attribute; keep the native signal columns,
    # masks, platform, order, and all fixed denominator identities unchanged.
    original <- raw3
    attr(raw3,"controls") <- NULL
    stopifnot(is.null(attr(raw3,"controls")),identical(sdfPlatform(raw3),"HM450"),
        identical(names(raw3),names(original)),
        all(vapply(names(raw3),function(k) identical(raw3[[k]],original[[k]]),logical(1))))
    rm(original)
    control_signals <- sesame::controls(raw3)
    stopifnot(is.data.frame(control_signals),
        all(c("Address","Type","UG","UR") %in% names(control_signals)),
        identical(as.character(control_signals$Address),address),
        identical(as.character(control_signals$Type),as.character(canonical$Type)),
        !anyNA(control_signals$Type),
        !any(grepl("^[0-9]+$",as.character(control_signals$Type))),
        all(paste0("ctl_",address[available]) %in% raw3$Probe_ID),
        identical(as.numeric(control_signals$UG[available]),g[available]),
        identical(as.numeric(control_signals$UR[available]),r[available]),
        identical(is.finite(control_signals$UG)&is.finite(control_signals$UR),available))
    neg_rows <- grepl("negative",tolower(as.character(canonical$Type)))
    stopifnot(any(neg_rows&available),
        identical(as.numeric(negative_controls(raw3)$G),as.numeric(control_signals$UG[neg_rows])),
        identical(as.numeric(negative_controls(raw3)$R),as.numeric(control_signals$UR[neg_rows])))
    write.table(data.frame(Address=address,Type=as.character(canonical$Type),
        expected_control_probe=paste0("ctl_",address),available_both=available,
        raw_green=g,raw_red=r,native_green=control_signals$UG,native_red=control_signals$UR),
        file.path(output,"technical-control-join.tsv"),sep="\t",quote=FALSE,row.names=FALSE)

    qcd3 <- prepSesame(raw3,"QCD")
    stopifnot(is.null(attr(qcd3,"controls")))
    # Negative-control input must survive QCD and reach both native stages.
    after_qcd <- sesame::controls(qcd3)
    neg <- negative_controls(qcd3)
    stopifnot(identical(as.character(after_qcd$Address),address),
        identical(as.character(after_qcd$Type),as.character(canonical$Type)),
        nrow(neg)==sum(neg_rows),
        identical(as.numeric(neg$G),as.numeric(after_qcd$UG[neg_rows])),
        identical(as.numeric(neg$R),as.numeric(after_qcd$UR[neg_rows])),
        any(is.finite(neg$G)&is.finite(neg$R)))
    p3 <- pOOBAH(qcd3,return.pval=TRUE,combine.neg=TRUE)
    # Independent empirical-CDF calculation with exactly the native
    # out-of-band and restored negative-control inputs. No fallback prior
    # should be needed on this fixture.
    nonuniq <- getFromNamespace("nonuniqMask","sesame")
    nmk <- qcd3[!(qcd3$Probe_ID %in% nonuniq("HM450")),]
    bgG <- c(getFromNamespace("oobG","sesame")(nmk),neg$G)
    bgR <- c(getFromNamespace("oobR","sesame")(nmk),neg$R)
    stopifnot(sum(!is.na(bgG))>100L,sum(!is.na(bgR))>100L)
    reference_p3 <- setNames(pmin(
        1-ecdf(bgR)(pmax(qcd3$MR,qcd3$UR,na.rm=TRUE)),
        1-ecdf(bgG)(pmax(qcd3$MG,qcd3$UG,na.rm=TRUE))),qcd3$Probe_ID)
    stopifnot(identical(names(p3),names(reference_p3)),
        identical(is.na(p3),is.na(reference_p3)),
        max(abs(p3-reference_p3),na.rm=TRUE)<=1e-12)
    reference_p_error <- max(abs(p3-reference_p3),na.rm=TRUE)
    p3_oob <- pOOBAH(qcd3,return.pval=TRUE,combine.neg=FALSE)
    detected3 <- pOOBAH(qcd3,pval.threshold=0.05,combine.neg=TRUE)
    stopifnot(identical(negative_controls(detected3),neg))
    processed3 <- noob(detected3,combine.neg=TRUE)
    # Same detected input with only the native noob negative switch
    # disabled isolates the background-stage difference from detection.
    b3_noob_oob <- getBetas(noob(detected3,combine.neg=FALSE))
    stopifnot(identical(names(b3_noob_oob),manifest_ids))
    rm(nmk,bgG,bgR,reference_p3,detected3)
    invisible(gc(full=TRUE))
    b3 <- getBetas(processed3)
    unmasked3 <- getBetas(processed3,mask=FALSE)
    direct3 <- getBetas(prepSesame(raw3,"QCDPB"))
    stopifnot(identical(names(b3),manifest_ids),identical(names(p3),manifest_ids),
        identical(names(unmasked3),manifest_ids),
        all(is.na(p3)|(is.finite(p3)&p3>=0&p3<=1)),
        all(is.na(unmasked3)|(is.finite(unmasked3)&unmasked3>=0&unmasked3<=1)),
        identical(b3[!processed3$mask],unmasked3[!processed3$mask]),
        identical(names(b3),names(direct3)),identical(is.na(b3),is.na(direct3)),
        max(abs(b3-direct3),na.rm=TRUE)<=1e-12,
        !anyNA(processed3$mask),all(processed3$mask[raw3$mask]),
        all(is.na(b3[raw3$mask])),all(is.na(b3[processed3$mask])))
    at <- match(eligible,manifest_ids)
    stopifnot(!anyNA(at))
    v <- valid_measurement(b3[at],p3[at],processed3$mask[at],raw3$mask[at])
    # Marginal reasons can overlap. The first true reason assigns each rejected
    # probe once; inspect underlying beta, not the NA imposed by a mask.
    bead_bad <- raw3$mask[at]
    reasons <- cbind(bead_or_missing_address=bead_bad,
        detection_missing=!is.finite(p3[at]),
        detection_above_threshold=is.finite(p3[at])&p3[at]>0.05,
        processing_mask=processed3$mask[at],
        beta_missing_or_nonfinite=!is.finite(unmasked3[at]),
        beta_endpoint=is.finite(unmasked3[at])&(unmasked3[at]==0|unmasked3[at]==1))
    stopifnot(!anyNA(reasons),!anyNA(v),
        identical(unname(v),unname(rowSums(reasons)==0L)))
    remaining <- rep(TRUE,length(at))
    exclusive <- integer(ncol(reasons))
    for (i in seq_len(ncol(reasons))) {
        exclusive[i] <- sum(remaining&reasons[,i])
        remaining <- remaining&!reasons[,i]
    }
    n <- length(eligible)
    count <- sum(v)
    m3 <- setNames(rep(NA_real_,n),eligible)
    m3[v] <- log2(b3[at][v]/(1-b3[at][v]))
    stopifnot(count+sum(exclusive)==n,identical(unname(remaining),unname(v)),
        all(is.finite(m3[v])),all(is.na(m3[!v])))
    # Exact legacy/corrected paired results on the same fixed denominator.
    legacy_valid <- valid_measurement(legacy_b3[at],legacy_p3[at],
        legacy_mask3[at],raw3$mask[at])
    stopifnot(!anyNA(legacy_valid),sum(legacy_valid)==366308L,
        n==408966L)
    changed <- function(a,b) {
        stopifnot(length(a)==length(b),identical(names(a),names(b)))
        sum(xor(is.na(a),is.na(b)) | (!is.na(a)&!is.na(b)&a!=b),na.rm=TRUE)
    }
    max_delta <- function(a,b) {
        at <- is.finite(a)&is.finite(b)
        stopifnot(any(at))
        max(abs(a[at]-b[at]))
    }
    compare <- data.frame(metric=c("manifest_controls","available_control_pairs",
        "unavailable_control_pairs","legacy_negative_controls","restored_negative_controls",
        "restored_finite_negative_pairs","legacy_valid","corrected_valid",
        "fixed_denominator","pOOBAH_reference_max_error",
        "pOOBAH_changed_vs_legacy","pOOBAH_max_delta_vs_legacy",
        "pOOBAH_changed_vs_oob_only","pOOBAH_max_delta_vs_oob_only",
        "mask_changed_vs_legacy","beta_changed_vs_legacy","beta_max_delta_vs_legacy",
        "noob_beta_changed_vs_oob_only","noob_beta_max_delta_vs_oob_only",
        "eligible_gained","eligible_lost"),
        value=c(length(address),sum(available),sum(!available),0L,sum(neg_rows),
        sum(is.finite(neg$G)&is.finite(neg$R)),sum(legacy_valid),count,n,
        reference_p_error,changed(legacy_p3,p3),max_delta(legacy_p3,p3),
        changed(p3,p3_oob),max_delta(p3,p3_oob),sum(legacy_mask3!=processed3$mask),
        changed(legacy_b3,b3),max_delta(legacy_b3,b3),
        changed(b3,b3_noob_oob),max_delta(b3,b3_noob_oob),
        sum(v&!legacy_valid),sum(!v&legacy_valid)))
    stopifnot(count-sum(legacy_valid)==sum(v&!legacy_valid)-sum(!v&legacy_valid),
        identical(names(legacy_b3),names(b3)),identical(names(legacy_p3),names(p3)))
    write.table(compare,file.path(output,"technical-control-correction-summary.tsv"),
        sep="\t",quote=FALSE,row.names=FALSE)
    print(compare)
    fmt17 <- function(x) ifelse(is.na(x),NA_character_,sprintf("%.17g",x))
    con <- gzfile(file.path(output,"technical-control-correction-probes.tsv.gz"),"wt")
    write.table(data.frame(Probe_ID=manifest_ids,legacy_p=fmt17(legacy_p3),
        corrected_p=fmt17(p3),legacy_beta=fmt17(legacy_b3),corrected_beta=fmt17(b3),
        legacy_mask=legacy_mask3,corrected_mask=processed3$mask),con,
        sep="\t",quote=FALSE,row.names=FALSE)
    close(con)
    writeLines(c("scope=unrelated_HM450_fixture_only",
        "legacy_numeric_control_type_reproduced=true",
        "legacy_negative_controls_missing=true",
        "native_manifest_controls_received=true",
        "native_pOOBAH_ecdf_comparison_passed=true",
        "native_noob_direct_staged_passed=true",
        "clinical_cohort_qc=false","owner_device_qualified=false"),
        file.path(output,"technical-control-correction-disposition.txt"))
    write.table(data.frame(reason=c(colnames(reasons),"valid"),
        marginal=c(colSums(reasons),count),exclusive=c(exclusive,count)),
        file.path(output,"technical-cohort-qc-exclusions.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    write.table(data.frame(metric=c("manifest_probes","cg_probes","cg_without_annotation",
        "nonautosomal_or_missing_coordinate","static_recommended_exclusions",
        "fixed_denominator","valid","finite_M","valid_fraction","candidate_95pct_met",
        "coordinate_build","denominator_sha256","annotation_rds_sha256"),
        value=c(length(manifest_ids),length(fixed_cpg),length(fixed_cpg)-length(fixed_annotated),
        length(fixed_annotated)-length(fixed_autosomal),length(fixed_autosomal)-n,
        n,count,sum(is.finite(m3)),sprintf("%.17g",count/n),
        as.integer(count>=ceiling(0.95*n)),"hg38",denominator_sha,annotation_sha)),
        file.path(output,"technical-cohort-qc-denominator.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    native_qc <- sesameQC_getStats(sesameQC_calcStats(raw3,
        c("detection","intensity","numProbes","channel","dyeBias","betas")))
    stopifnot(length(native_qc)>0L,all(vapply(native_qc,length,integer(1))==1L))
    gct <- bisConversionControl(raw3)
    stopifnot(length(gct)==1L,is.finite(gct),gct>=0)
    native_qc <- c(native_qc,list(native_gct=gct))
    write.table(data.frame(metric=names(native_qc),value=unlist(native_qc,use.names=FALSE)),
        file.path(output,"technical-cohort-qc-native-panel.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    stopifnot(identical(control_signals,sesame::controls(raw3)))
    write.table(control_signals,file.path(output,"technical-cohort-qc-controls.tsv"),
        sep="\t",quote=FALSE,row.names=FALSE)
    writeLines(c(paste0("native_control_records=",nrow(control_signals)),
        "candidate_sample_threshold=0.95","candidate_threshold_validated_for_clinical_use=false",
        "control_acceptance_ranges_validated=false","clinical_cohort_qc=false",
        "scope=unrelated_technical_fixture_only"),file.path(output,"technical-cohort-qc-disposition.txt"))
    cat("Technical fixed-denominator QC: ",count,"/",n," valid (",
        sprintf("%.6f",count/n),"); candidate threshold only.\n",sep="")

    writeLines(c("stage=technical","status=passed","scope=unrelated_HM450_fixture",
        "legacy_no_bead_benchmark_preserved=true",
        "selected_min_beads3_manifest_controls_received=true",
        "clinical_cohort_qc=false","cross_version_parity_claimed=false"),
        file.path(output,"technical-disposition.txt"))

}

if (stage=="limma") {
    suppressPackageStartupMessages(library(limma))
    # Synthetic named M matrix: independent OLS, uncertainty, complete BH family.
    set.seed(20261124)
    n <- 12L
    p <- 128L
    case <- rep(c(0,1),each=6L)
    sex <- rep(c(0,1),6L)
    age <- c(-2,1,4,-3,0,2,3,-1,0,4,-4,2)
    design <- cbind(intercept=1,case=case,age=age,sex=sex)
    rownames(design) <- paste0("synthetic-",seq_len(n))
    stopifnot(qr(design)$rank==ncol(design))
    M <- matrix(rnorm(p*n),nrow=p)+outer(seq(-1,1,length.out=p),case)
    dimnames(M) <- list(paste0("feature-",seq_len(p)),rownames(design))
    M[1,2] <- NA_real_
    fit <- lmFit(M,design)
    ols <- t(vapply(seq_len(p),function(i) {
        keep <- is.finite(M[i,])
        lm.fit(design[keep,,drop=FALSE],M[i,keep])$coefficients
    },numeric(ncol(design))))
    stopifnot(max(abs(fit$coefficients-ols))<=1e-10)
    moderated <- eBayes(fit,trend=FALSE,robust=FALSE)
    tt <- topTable(moderated,coef="case",number=Inf,sort.by="none",confint=TRUE)
    se <- moderated$stdev.unscaled[,"case"]*sqrt(moderated$s2.post)
    pvalue <- 2*pt(-abs(moderated$coefficients[,"case"]/se),df=moderated$df.total)
    half <- qt(.975,df=moderated$df.total)*se
    stopifnot(identical(rownames(tt),rownames(M)),all(is.finite(se)),
        max(abs(tt$logFC-moderated$coefficients[,"case"]))<=1e-10,
        max(abs(tt$P.Value-pvalue))<=1e-10,
        max(abs(tt$adj.P.Val-p.adjust(pvalue,"BH")))<=1e-10,
        max(abs(tt$CI.L-(tt$logFC-half)))<=1e-10,
        max(abs(tt$CI.R-(tt$logFC+half)))<=1e-10)
    cat("Synthetic limma: ",p," complete named rows; OLS, moderated SE/p/CI and BH checks passed.\n",sep="")
    write.table(data.frame(metric=c("features","samples","missing_values","design_rank",
        "max_OLS_error","max_p_error","max_BH_error","max_CI_lower_error","max_CI_upper_error"),
        value=c(p,n,sum(is.na(M)),qr(design)$rank,max(abs(fit$coefficients-ols)),
        max(abs(tt$P.Value-pvalue)),max(abs(tt$adj.P.Val-p.adjust(pvalue,"BH"))),
        max(abs(tt$CI.L-(tt$logFC-half))),max(abs(tt$CI.R-(tt$logFC+half))))),
        file.path(output,"limma-summary.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    capture.output(sessionInfo(),file=file.path(output,"limma-session-info.txt"))
    # Independent synthetic fixture for prospective N1 v0.2; no cohort inputs.
    local({
        case <- rep(0:1, each=6L)
        age <- c(-2,1,4,-3,0,2,3,-1,0,4,-4,2)
        age <- age-mean(age)
        sex <- rep(0:1,6L)
        chip <- rep(c(1L,1L,1L,2L,2L,3L),2L)
        design <- cbind(intercept=1,case=case,age=age,sex=sex,
            chip2=as.integer(chip==2L),chip3=as.integer(chip==3L))
        rownames(design) <- sprintf("synthetic-sample-%02d",seq_len(nrow(design)))
        probe <- sprintf("synthetic-probe-%02d",seq_len(19L))
        chr <- c(rep("chr1",6L),rep("chr2",3L),rep("chr1",9L),"chrX")
        start <- c(0L,500L,999L,1000L,1500L,1999L,0L,500L,999L,
            2000L,2999L,3000L,3500L,3999L,4000L,4500L,4999L,5000L,0L)
        M <- outer(seq_along(probe),seq_along(case),function(i,j)
            sin(i*j*0.37)+0.3*cos((i+2)*j*0.23))+
            outer((seq_along(probe)-10)/10,case)+
            outer(rep(0.02,length(probe)),age)
        dimnames(M) <- list(probe,rownames(design))
        M[cbind(c(14L,15L,15L,16L,16L,17L,17L,18L),
            c(2L,2L,8L,6L,12L,1L,2L,9L))] <- NA_real_
        stopifnot(qr(design)$rank==6L,identical(colnames(M),rownames(design)),
            !anyDuplicated(probe),all(start>=0L))

        valid <- is.finite(M)
        n0 <- rowSums(valid[,case==0L,drop=FALSE])
        n1 <- rowSums(valid[,case==1L,drop=FALSE])
        rank <- vapply(seq_len(nrow(M)),function(i)
            qr(design[valid[i,],,drop=FALSE])$rank,integer(1))
        df <- rowSums(valid)-rank
        eligible <- chr %in% paste0("chr",1:22)
        estimable <- rank==ncol(design)&df>=5L
        primary <- eligible&estimable&rowSums(valid)==ncol(M)
        sensitivity <- eligible&estimable&n0>=ceiling(0.8*sum(case==0L))&
            n1>=ceiling(0.8*sum(case==1L))
        # Predeclared identities, including balanced-but-low-df, rank and coverage failures.
        stopifnot(identical(unname(which(primary)),seq_len(13L)),
            identical(unname(which(sensitivity)),c(seq_len(14L),18L)),
            n0[15L]==5L,n1[15L]==5L,rank[15L]==6L,df[15L]==4L,
            n0[16L]==5L,n1[16L]==5L,rank[16L]==5L,df[16L]==5L,
            n0[17L]==4L,n1[17L]==6L,!eligible[19L])

        bin_start <- (start%/%1000L)*1000L
        bin <- paste(chr,bin_start,bin_start+1000L,sep=":")
        members <- split(which(primary),bin[primary])
        retained <- members[lengths(members)>=3L]
        expected <- list("chr1:0:1000"=1:3,"chr1:1000:2000"=4:6,"chr2:0:1000"=7:9)
        stopifnot(identical(unname(lapply(retained,as.integer)),unname(expected)),
            identical(names(retained),names(expected)),length(members)==5L)
        regional <- t(vapply(retained,function(ids)
            colMeans(M[ids,,drop=FALSE]),numeric(ncol(M))))
        colnames(regional) <- colnames(M)
        stopifnot(all(is.finite(regional)),identical(rownames(regional),names(expected)))

        # A separate complete moderation and BH family per operation; no chunking.
        fit_family <- function(Y) {
            fit <- lmFit(Y,design)
            reference <- t(vapply(seq_len(nrow(Y)),function(i) {
                keep <- is.finite(Y[i,])
                X <- design[keep,,drop=FALSE]
                y <- Y[i,keep]
                b <- setNames(qr.solve(X,y),colnames(X))
                residual_df <- nrow(X)-ncol(X)
                variance <- sum((y-X%*%b)^2)/residual_df
                c(effect=unname(b["case"]),ordinary_se=sqrt(variance*solve(crossprod(X))["case","case"]),
                    df=residual_df)
            },c(effect=0,ordinary_se=0,df=0)))
            ordinary_se <- fit$stdev.unscaled[,"case"]*fit$sigma
            stopifnot(all(is.finite(reference)),
                max(abs(fit$coefficients[,"case"]-reference[,"effect"]))<=1e-10,
                max(abs(ordinary_se-reference[,"ordinary_se"]))<=1e-10,
                identical(as.numeric(fit$df.residual),as.numeric(reference[,"df"])))
            mod <- eBayes(fit,trend=FALSE,robust=FALSE)
            tt <- topTable(mod,coef="case",number=Inf,sort.by="none",confint=TRUE)
            se <- mod$stdev.unscaled[,"case"]*sqrt(mod$s2.post)
            p <- 2*pt(-abs(mod$coefficients[,"case"]/se),df=mod$df.total)
            half <- qt(.975,df=mod$df.total)*se
            stopifnot(identical(rownames(tt),rownames(Y)),all(is.finite(se)&se>0),
                all(is.finite(p)&p>=0&p<=1),
                max(abs(tt$logFC-reference[,"effect"]))<=1e-10,
                max(abs(tt$P.Value-p))<=1e-10,
                max(abs(tt$adj.P.Val-p.adjust(p,"BH")))<=1e-10,
                max(abs(tt$CI.L-(tt$logFC-half)))<=1e-10,
                max(abs(tt$CI.R-(tt$logFC+half)))<=1e-10)
            data.frame(id=rownames(Y),effect=tt$logFC,ordinary_se=ordinary_se,
                reference_effect=reference[,"effect"],reference_ordinary_se=reference[,"ordinary_se"],
                residual_df=fit$df.residual,residual_variance=fit$sigma^2,
                unscaled_se=fit$stdev.unscaled[,"case"],prior_df=mod$df.prior,
                prior_variance=mod$s2.prior,posterior_variance=mod$s2.post,
                moderated_se=se,moderated_df=mod$df.total,
                p=tt$P.Value,bh=tt$adj.P.Val,ci_lower=tt$CI.L,ci_upper=tt$CI.R)
        }
        fits <- list(primary=fit_family(M[primary,,drop=FALSE]),
            sensitivity=fit_family(M[sensitivity,,drop=FALSE]),regions=fit_family(regional))
        stopifnot(max(abs(fits$regions$effect-c(-1.057399924280879,-0.545695195289085,
            -0.256220308312924)))<=1e-10,
            max(abs(fits$regions$ordinary_se-c(0.156837028300713,0.288598056479679,
            0.221273175751039)))<=1e-10,
            max(abs(fits$regions$effect-vapply(retained,function(ids)
                mean(fits$primary$effect[match(probe[ids],fits$primary$id)]),numeric(1))))<=1e-10)
        emit <- function(x,name) write.table(x,file.path(output,paste0("synthetic-n1-",name,".tsv")),
            sep="\t",quote=FALSE,row.names=FALSE)
        emit(data.frame(sample=rownames(design),design),"design")
        emit(data.frame(probe=probe,chr=chr,start=start,bin=bin,eligible=eligible,
            control_valid=n0,case_valid=n1,rank=rank,residual_df=df,primary=primary,
            sensitivity=sensitivity,M,check.names=FALSE),"probe-audit")
        emit(data.frame(region=rep(names(members),lengths(members)),
            probe=probe[unlist(members,use.names=FALSE)],
            retained=rep(lengths(members)>=3L,lengths(members))),"region-membership")
        emit(data.frame(region=rownames(regional),regional,check.names=FALSE),"region-scores")
        for (family in names(fits)) emit(fits[[family]],family)
        writeLines(c("scope=synthetic_n1_v0.2_only","status=passed","clinical_inference=false",
            "n1_frozen=false"),file.path(output,"synthetic-n1-disposition.txt"))
        cat("Synthetic N1: 13 primary, 15 sensitivity, 3 fixed regional scores; rank/df and separate BH families passed.\n")
    })
    writeLines(c("stage=limma","status=passed","scope=synthetic_named_M_matrix",
        "clinical_inference=false"),file.path(output,"limma-disposition.txt"))

}

if (stage=="enrichment") {
    suppressPackageStartupMessages(library(missMethyl))
    stopifnot(as.character(packageVersion("BiasedUrn"))=="2.0.12",
        as.character(packageVersion("GO.db"))=="3.22.0",
        as.character(packageVersion("org.Hs.eg.db"))=="3.22.0",
        as.character(packageVersion("IlluminaHumanMethylation450kanno.ilmn12.hg19"))=="0.6.1",
        as.character(packageVersion("minfi"))=="1.56.0")
    universe <- readLines(file.path(scratch,"synthetic-probe-universe.txt"))
    stopifnot(length(universe)==4000L,!anyDuplicated(universe))
    selected <- universe[seq(1,length(universe),by=20L)]
    stopifnot(length(universe)==4000L,length(selected)==200L,all(selected %in% universe))
    # The native mapping function filters to all.cpg after flattening. Supply
    # the exact tested annotation rows before flattening to bound memory.
    anno <- minfi::getAnnotation(IlluminaHumanMethylation450kanno.ilmn12.hg19::IlluminaHumanMethylation450kanno.ilmn12.hg19)
    stopifnot(!anyDuplicated(rownames(anno)))
    annotation_index <- match(universe,rownames(anno))
    annotated <- universe[!is.na(annotation_index)]
    anno <- anno[annotation_index[!is.na(annotation_index)],,drop=FALSE]
    stopifnot(length(annotated)>0L,identical(rownames(anno),annotated))
    # Original all.cpg and selected inputs are retained even if a CpG is
    # absent from annotation or unmapped to an Entrez gene by native code.
    flat <- getFromNamespace(".getFlatAnnotation","missMethyl")("450K",anno)
    mapped_cpg <- unique(flat$cpg)
    stopifnot(all(mapped_cpg %in% annotated))
    write.table(data.frame(metric=c("tested","selected","annotation_present_tested",
        "annotation_absent_tested","annotation_present_selected","annotation_absent_selected",
        "gene_mapped_tested","gene_unmapped_tested","gene_mapped_selected","gene_unmapped_selected"),
        value=c(length(universe),length(selected),length(annotated),
        length(setdiff(universe,annotated)),sum(selected %in% annotated),
        sum(!selected %in% annotated),length(mapped_cpg),length(setdiff(universe,mapped_cpg)),
        sum(selected %in% mapped_cpg),sum(!selected %in% mapped_cpg))),
        file.path(output,"enrichment-mapping.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    rm(flat)
    invisible(gc(full=TRUE))
    go <- gometh(sig.cpg=selected,all.cpg=universe,collection="GO",array.type="450K",
        anno=anno,plot.bias=FALSE,prior.prob=TRUE,equiv.cpg=TRUE,fract.counts=TRUE)
    # Preserve unmodified synthetic results *before* the strict probability gate.
    # This makes a numerical failure inspectable without changing the method,
    # deleting terms, clipping probabilities or changing the BH family.
    stopifnot(nrow(go)>0L,!anyDuplicated(rownames(go)),
        all(c("N","DE","P.DE","FDR") %in% colnames(go)))
    raw_go <- data.frame(GOID=rownames(go),N=go$N,DE=go$DE,
        P.DE=sprintf("%.17g",go$P.DE),FDR=sprintf("%.17g",go$FDR))
    write.table(raw_go,file.path(output,"enrichment-raw.tsv"),sep="\t",
        quote=FALSE,row.names=FALSE)
    bad_p <- which(!is.na(go$P.DE)&(!is.finite(go$P.DE)|go$P.DE<0|go$P.DE>1))
    bad_fdr <- which(!is.na(go$FDR)&(!is.finite(go$FDR)|go$FDR<0|go$FDR>1))
    fmt <- function(x) sprintf("%.17g",x)
    write.table(data.frame(metric=c("tested","selected","GO_rows","finite_p",
        "missing_p","p_below_zero","p_above_one","nonfinite_p_excluding_NA",
        "invalid_FDR","minimum_finite_p","maximum_finite_p"),
        value=c(length(universe),length(selected),nrow(go),sum(is.finite(go$P.DE)),
        sum(is.na(go$P.DE)),sum(go$P.DE<0,na.rm=TRUE),
        sum(go$P.DE>1,na.rm=TRUE),sum(!is.na(go$P.DE)&!is.finite(go$P.DE)),
        length(bad_fdr),fmt(min(go$P.DE[is.finite(go$P.DE)])),
        fmt(max(go$P.DE[is.finite(go$P.DE)])))),
        file.path(output,"enrichment-diagnostics.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    if(length(bad_p)>0L) {
        # Diagnosis only. The pinned release computes P(X>x)+P(X=x).
        # Compare that calculation with the inclusive upper tail and a
        # separate small exact urn recurrence. Never substitute these results.
        mapped <- getMappedEntrezIDs(sig.cpg=selected,all.cpg=universe,
            array.type="450K",anno=anno,genomic.features="ALL")
        stopifnot(abs(sum(mapped$equiv)-length(mapped_cpg))<=1e-8)
        pwf <- getFromNamespace(".estimatePWF","missMethyl")(
            D=mapped$de,bias=as.vector(mapped$equiv))
        go_sets <- getFromNamespace(".getGO","missMethyl")()$idList
        num_genes <- length(mapped$universe)
        draws <- length(mapped$sig.eg)
        # Bounded independent sequential weighted sampling without replacement.
        # The recurrence is a diagnostic, not a production backend.
        inclusive <- function(q,m1,m2,n,odds) {
            if(!is.finite(odds)||odds<=0||n>m1+m2||n<0) return(NA_real_)
            if(q<=max(0,n-m2)) return(1)
            if(q>min(n,m1)) return(0)
            if(n>1000L) return(NA_real_)
            d <- numeric(min(n,m1)+1L)
            d[1L] <- 1
            for(t in seq_len(n)) {
                k <- seq.int(max(0L,t-1L-m2),min(t-1L,m1))
                red <- m1-k
                white <- m2-(t-1L-k)
                pr <- odds*red/(odds*red+white)
                next_d <- numeric(length(d))
                ix <- k+1L
                next_d[ix] <- d[ix]*(1-pr)
                can_red <- k<m1
                next_d[ix[can_red]+1L] <- next_d[ix[can_red]+1L]+
                    d[ix[can_red]]*pr[can_red]
                d <- next_d
            }
            stopifnot(abs(sum(d)-1)<=1e-10)
            sum(d[seq.int(q+1L,length(d))])
        }
        # At most 20 failing terms, deterministically prioritised by magnitude.
        distance <- abs(go$P.DE[bad_p]-pmin(1,pmax(0,go$P.DE[bad_p])))
        selected_bad <- head(bad_p[order(distance,decreasing=TRUE,na.last=TRUE)],20L)
        diag_rows <- lapply(selected_bad,function(i) {
            term <- rownames(go)[i]
            genes <- go_sets[[term]]
            in_set <- mapped$universe %in% genes
            m1 <- sum(in_set)
            m2 <- num_genes-m1
            frac <- sum(mapped$fract.counts$frac[mapped$sig.eg %in% genes])
            q <- as.integer(frac)
            stopifnot(m1==go$N[i],floor(frac)==go$DE[i])
            odds <- if(m1>0L&&m2>0L) mean(pwf[in_set])/mean(pwf[!in_set]) else NA_real_
            safe <- function(expr) tryCatch(expr,error=function(e) NA_real_)
            legacy <- if(is.finite(odds)&&odds>0) safe(
                BiasedUrn::pWNCHypergeo(q,m1,m2,draws,odds,lower.tail=FALSE)+
                BiasedUrn::dWNCHypergeo(q,m1,m2,draws,odds)) else NA_real_
            direct <- if(is.finite(odds)&&odds>0) safe(
                BiasedUrn::pWNCHypergeo(q-1L,m1,m2,draws,odds,
                    precision=1e-12,lower.tail=FALSE)) else NA_real_
            data.frame(GOID=term,raw_p=fmt(go$P.DE[i]),fractional_DE=fmt(frac),
                integer_q=q,m1=m1,m2=m2,draws=draws,odds=fmt(odds),
                native_sum=fmt(legacy),direct_upper_tail=fmt(direct),
                independent_urn_tail=fmt(safe(inclusive(q,m1,m2,draws,odds))))
        })
        write.table(do.call(rbind,diag_rows),file.path(output,"enrichment-invalid-terms.tsv"),
            sep="\t",quote=FALSE,row.names=FALSE)
    }
    capture.output(sessionInfo(),file=file.path(output,"enrichment-session-info.txt"))
    # P(X >= 0) is exactly one for any valid nonnegative count distribution.
    # missMethyl 1.44.0 passes fractional DE through BiasedUrn's integer
    # coercion and reports floor(DE). Correct only that proven boundary.
    # The pre-existing 1e-12 numerical comparison bound guards against
    # materially wrong native results; the received domain stays exactly [0,1].
    receive_zero_count_tails <- function(native) {
        stopifnot(nrow(native)>0L,!anyDuplicated(rownames(native)),
            all(c("N","DE","P.DE","FDR") %in% colnames(native)),
            all(is.finite(native$N)),all(native$N>0),
            all(native$N==floor(native$N)),
            all(is.finite(native$DE)),all(native$DE>=0),
            all(native$DE==floor(native$DE)),all(native$DE<=native$N),
            all(is.finite(native$P.DE)),all(is.finite(native$FDR)),
            all(native$FDR>=0 & native$FDR<=1))
        zero <- native$DE==0
        stopifnot(all(abs(native$P.DE[zero]-1)<=1e-12),
            all(native$P.DE[!zero]>=0 & native$P.DE[!zero]<=1),
            isTRUE(all.equal(native$FDR,p.adjust(native$P.DE,"BH"),
                tolerance=1e-12,check.attributes=FALSE)))
        received <- native
        received$P.DE[zero] <- 1
        received$FDR <- p.adjust(received$P.DE,"BH")
        stopifnot(identical(rownames(received),rownames(native)),
            identical(received$N,native$N),identical(received$DE,native$DE),
            identical(received$P.DE[!zero],native$P.DE[!zero]),
            all(received$P.DE>=0 & received$P.DE<=1),
            all(received$FDR>=0 & received$FDR<=1))
        received
    }
    # Observed red fixture plus explicit negative tests: do not blanket clip.
    regression <- data.frame(N=c(14L,24L,8L),DE=c(0L,0L,2L),
        P.DE=c(1.0000000000000113,0.9999999999999897,0.025))
    regression$FDR <- p.adjust(regression$P.DE,"BH")
    fixed <- receive_zero_count_tails(regression)
    stopifnot(identical(fixed$P.DE,c(1,1,0.025)),
        identical(fixed$FDR,p.adjust(c(1,1,0.025),"BH")))
    reject <- function(native) inherits(try(receive_zero_count_tails(native),
        silent=TRUE),"try-error")
    wrong <- regression
    wrong$P.DE[3L] <- 1.0000000000000113
    wrong$FDR <- p.adjust(wrong$P.DE,"BH")
    stopifnot(reject(wrong))
    wrong <- regression
    wrong$P.DE[1L] <- 0.99
    wrong$FDR <- p.adjust(wrong$P.DE,"BH")
    stopifnot(reject(wrong))
    wrong <- regression
    wrong$P.DE[3L] <- NA_real_
    stopifnot(reject(wrong))
    wrong <- regression
    wrong$FDR[3L] <- 0.9
    stopifnot(reject(wrong))

    # Require the actual failing terms to be reproduced and corroborated.
    # The diagnostic code above must preserve the native raw table and
    # independently evaluate the largest invalid values before receipt.
    stopifnot(length(bad_p)>0L,length(bad_fdr)==0L,
        all(go$DE[bad_p]==0),all(go$P.DE[bad_p]>1))
    diagnostic <- do.call(rbind,diag_rows)
    stopifnot(nrow(diagnostic)==min(length(bad_p),20L),
        all(diagnostic$integer_q==0L),
        all(as.numeric(diagnostic$direct_upper_tail)==1),
        all(as.numeric(diagnostic$independent_urn_tail)==1),
        all(abs(as.numeric(diagnostic$raw_p)-
            as.numeric(diagnostic$native_sum))<=1e-12))

    # Verify every received zero integer count against the original
    # missMethyl gene mapping and fractional counts, without changing them.
    zero <- go$DE==0
    stopifnot(length(mapped$sig.eg)==nrow(mapped$fract.counts),
        all(is.finite(mapped$fract.counts$frac)),
        all(mapped$fract.counts$frac>=0),all(is.finite(pwf)))
    boundary <- vapply(which(zero),function(i) {
        genes <- go_sets[[rownames(go)[i]]]
        in_set <- mapped$universe %in% genes
        m1 <- sum(in_set)
        frac <- sum(mapped$fract.counts$frac[mapped$sig.eg %in% genes])
        odds <- if(m1>0L && m1<num_genes) mean(pwf[in_set])/mean(pwf[!in_set]) else NA_real_
        c(m1,frac,odds)
    },numeric(3))
    stopifnot(all(is.finite(boundary)),all(boundary[1L,]==go$N[zero]),
        all(boundary[2L,]>=0 & boundary[2L,]<1),
        all(boundary[3L,]>0))
    received <- receive_zero_count_tails(go)
    # This observed synthetic family must retain its complete BH results.
    stopifnot(max(abs(received$FDR-go$FDR))<=1e-12,
        identical(received$FDR<=0.05,go$FDR<=0.05))
    write.table(data.frame(GOID=rownames(received),N=received$N,
        DE=received$DE,P.DE=fmt(received$P.DE),FDR=fmt(received$FDR)),
        file.path(output,"enrichment-received.tsv"),sep="\t",
        quote=FALSE,row.names=FALSE)
    write.table(data.frame(metric=c("tested","selected","GO_rows","finite_p",
        "raw_invalid_p","zero_count_rows","corrected_p","max_absolute_correction",
        "max_BH_error","max_BH_change","changed_significance"),
        value=c(length(universe),length(selected),nrow(received),
        sum(is.finite(received$P.DE)),length(bad_p),sum(zero),
        sum(received$P.DE!=go$P.DE),fmt(max(abs(received$P.DE-go$P.DE))),
        fmt(max(abs(received$FDR-p.adjust(received$P.DE,"BH")))),
        fmt(max(abs(received$FDR-go$FDR))),
        sum((received$FDR<=0.05)!=(go$FDR<=0.05)))),
        file.path(output,"enrichment-summary.tsv"),sep="\t",
        quote=FALSE,row.names=FALSE)
    # Reactome v98 uses the same synthetic CpGs and native Entrez mapping.
    # The workflow verifies the exact source bytes against reactome-v98.json.
    # Keep evidence and exclusion counts; deduplicate gene-pathway pairs so
    # repeated TAS/IEA assertions cannot increase pathway sizes or evidence.
    pathway_source <- read.delim(file.path(input,"NCBI2Reactome_All_Levels.txt"),
        header=FALSE,quote="",comment.char="",colClasses="character",
        check.names=FALSE)
    stopifnot(ncol(pathway_source)==6L,nrow(pathway_source)==781553L,
        !anyNA(pathway_source),length(unique(pathway_source[[6L]]))==16L)
    names(pathway_source) <- c("gene","pathway","url","name","evidence","species")
    human <- pathway_source[pathway_source$species=="Homo sapiens",]
    stopifnot(nrow(human)==157638L,all(grepl("^R-HSA-[0-9]+$",human$pathway)),
        setequal(human$evidence,c("IEA","TAS")))
    numeric_id <- grepl("^[1-9][0-9]*$",human$gene)
    stopifnot(sum(!numeric_id)==224L,length(unique(human$gene[!numeric_id]))==22L)
    human_numeric <- human[numeric_id,]
    pairs <- unique(human_numeric[,c("gene","pathway")])
    stopifnot(nrow(pairs)==140535L,length(unique(pairs$gene))==11470L,
        length(unique(pairs$pathway))==2861L)
    evidence_counts <- as.data.frame(table(human_numeric$evidence))
    names(evidence_counts) <- c("evidence","source_rows")
    write.table(evidence_counts,file.path(output,"reactome-evidence.tsv"),
        sep="\t",quote=FALSE,row.names=FALSE)
    reactome_sets <- split(pairs$gene,pairs$pathway)
    eligible_sets <- lapply(reactome_sets,intersect,mapped$universe)
    eligible_counts <- lengths(eligible_sets)
    expected_ids <- names(eligible_sets)[eligible_counts>0L]
    stopifnot(length(expected_ids)>0L,all(eligible_counts<length(mapped$universe)))
    write.table(data.frame(pathway=names(reactome_sets),
        source_genes=lengths(reactome_sets),eligible_genes=eligible_counts,
        disposition=ifelse(eligible_counts>0L,"tested","no_gene_in_tested_universe")),
        file.path(output,"reactome-family.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    reactome <- gsameth(sig.cpg=selected,all.cpg=universe,collection=reactome_sets,
        array.type="450K",anno=anno,plot.bias=FALSE,prior.prob=TRUE,
        equiv.cpg=TRUE,fract.counts=TRUE,genomic.features="ALL")
    stopifnot(identical(rownames(reactome),expected_ids))
    write.table(data.frame(pathway=rownames(reactome),N=reactome$N,DE=reactome$DE,
        P.DE=fmt(reactome$P.DE),FDR=fmt(reactome$FDR)),
        file.path(output,"reactome-raw.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    fractional <- vapply(eligible_sets[expected_ids],function(genes)
        sum(mapped$fract.counts$frac[mapped$sig.eg %in% genes]),numeric(1))
    stopifnot(all(reactome$N==eligible_counts[expected_ids]),
        all(reactome$DE==floor(fractional)))
    zero_ids <- expected_ids[reactome$DE==0]
    zero_odds <- vapply(eligible_sets[zero_ids],function(genes) {
        in_set <- mapped$universe %in% genes
        mean(pwf[in_set])/mean(pwf[!in_set])
    },numeric(1))
    stopifnot(length(zero_ids)>0L,all(is.finite(zero_odds)),all(zero_odds>0),
        all(fractional[zero_ids]>=0 & fractional[zero_ids]<1))
    zero_tail <- vapply(seq_along(zero_ids),function(i)
        BiasedUrn::pWNCHypergeo(-1L,eligible_counts[zero_ids[i]],
            length(mapped$universe)-eligible_counts[zero_ids[i]],
            length(mapped$sig.eg),zero_odds[i],precision=1e-12,lower.tail=FALSE),numeric(1))
    stopifnot(all(zero_tail==1))
    write.table(data.frame(pathway=zero_ids,fractional_DE=fmt(fractional[zero_ids]),
        native_integer_DE=0L,odds=fmt(zero_odds),inclusive_upper_tail=fmt(zero_tail)),
        file.path(output,"reactome-zero-boundary.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    # Reuse the qualified mathematical zero-count boundary, never a blanket
    # probability clip or a filter based on observed significance.
    reactome_received <- receive_zero_count_tails(reactome)
    stopifnot(max(abs(reactome_received$FDR-reactome$FDR))<=1e-12,
        identical(reactome_received$FDR<=0.05,reactome$FDR<=0.05))
    write.table(data.frame(pathway=rownames(reactome_received),N=reactome_received$N,
        DE=reactome_received$DE,P.DE=fmt(reactome_received$P.DE),
        FDR=fmt(reactome_received$FDR)),file.path(output,"reactome-received.tsv"),
        sep="\t",quote=FALSE,row.names=FALSE)
    write.table(data.frame(metric=c("tested_CpGs","selected_CpGs","source_human_rows",
        "excluded_nonnumeric_rows","unique_numeric_gene_pathway_pairs","source_pathways",
        "empty_universe_pathways","tested_pathways","native_universe_genes",
        "native_genes_in_reactome","native_selected_genes_in_reactome",
        "raw_invalid_p","zero_count_rows","corrected_p","max_absolute_correction",
        "max_BH_error","changed_significance"),value=c(length(universe),length(selected),
        nrow(human),sum(!numeric_id),nrow(pairs),length(reactome_sets),sum(eligible_counts==0L),
        nrow(reactome),length(mapped$universe),sum(mapped$universe %in% pairs$gene),
        sum(mapped$sig.eg %in% pairs$gene),sum(reactome$P.DE<0|reactome$P.DE>1),
        sum(reactome$DE==0),sum(reactome_received$P.DE!=reactome$P.DE),
        fmt(max(abs(reactome_received$P.DE-reactome$P.DE))),
        fmt(max(abs(reactome_received$FDR-p.adjust(reactome_received$P.DE,"BH")))),
        sum((reactome_received$FDR<=0.05)!=(reactome$FDR<=0.05)))),
        file.path(output,"reactome-summary.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    cat("Synthetic missMethyl: GO and Reactome receivers passed; raw probabilities retained.\n")
    capture.output(sessionInfo(),file=file.path(output,"enrichment-session-info.txt"))
    stopifnot(file.exists(file.path(output,"technical-disposition.txt")),file.exists(file.path(output,"limma-disposition.txt")))
    writeLines(c("scope=native_release_technical_and_synthetic","limma_synthetic_pass=true",
        "missMethyl_synthetic_zero_count_receiver_pass=true",
        "missMethyl_native_probability_domain_pass=false",
        "reactome_synthetic_zero_count_receiver_pass=true",
        paste0("reactome_native_probability_domain_pass=",
            tolower(as.character(all(reactome$P.DE>=0 & reactome$P.DE<=1)))),
        "full_cross_version_preprocessing_parity_claimed=false",
        "clinical_cohort_qc=false","owner_device_qualified=false",
        "institutional_determination=false","scientific_admitted=false"),
        file.path(output,"disposition.txt"))

}


# Outcome-blind reference-only audit after the unchanged historical stages.
# No human sample/phenotype values, alternate preprocessing or disease fit.
if (stage=="annotation") {
    suppressPackageStartupMessages(library(sesameData))
    suppressPackageStartupMessages(library(missMethyl))
    stopifnot(as.character(packageVersion("org.Hs.eg.db"))=="3.22.0",
        as.character(packageVersion("IlluminaHumanMethylation450kanno.ilmn12.hg19"))=="0.6.1",
        as.character(packageVersion("minfi"))=="1.56.0")
    sha256 <- function(path) {
        result <- system2("sha256sum",shQuote(path),stdout=TRUE,stderr=TRUE)
        stopifnot(length(result)==1L,grepl("^[0-9a-f]{64} ",result))
        substr(result,1L,64L)
    }
    emit <- function(x,name) write.table(x,file.path(output,name),sep="\t",
        quote=FALSE,row.names=FALSE)
    emit_summary <- function(values,name) emit(data.frame(metric=names(values),
        value=unname(values)),name)
    ids_path <- file.path(output,"technical-cohort-qc-denominator.txt")
    ids <- readLines(ids_path)
    stopifnot(length(ids)==408966L,identical(ids,sort(unique(ids),method="radix")),
        all(grepl("^cg[0-9]{8}$",ids)),
        sha256(ids_path)=="1d413041ee2bee0666b42ccb0a50c5180a305a4684f1327559796ec67e5f2366")
    # Native builder uses CpG_beg+1 and CpG_end in its inclusive GRanges.
    # Use the leftmost CpG coordinate, not the strand-specific probe end.
    region_start <- function(start1,end1) {
        stopifnot(length(start1)==length(end1),all(is.finite(start1)),
            all(is.finite(end1)),all(start1==floor(start1)),all(end1==floor(end1)),
            all(start1>=1),all(end1>=start1),all(end1-start1+1<=2))
        ((start1-1L)%/%1000L)*1000L
    }
    # Independently predeclared boundary, width and malformed-range cases.
    stopifnot(identical(as.integer(region_start(c(1L,1000L,1001L,2000L,2001L),
        c(2L,1001L,1002L,2000L,2002L))),c(0L,0L,1000L,1000L,2000L)),
        inherits(try(region_start(0L,1L),silent=TRUE),"try-error"),
        inherits(try(region_start(NA_real_,2L),silent=TRUE),"try-error"),
        inherits(try(region_start(1.5,2),silent=TRUE),"try-error"),
        inherits(try(region_start(2L,1L),silent=TRUE),"try-error"),
        inherits(try(region_start(1L,3L),silent=TRUE),"try-error"))
    stopifnot(isTRUE(sesameDataCache("HM450.address")))
    gr <- sesameData_getManifestGRanges("HM450",genome="hg38")
    stopifnot(inherits(gr,"GRanges"),!anyDuplicated(names(gr)))
    tmp <- tempfile(fileext=".rds")
    saveRDS(gr,tmp,version=3)
    native_sha <- sha256(tmp)
    unlink(tmp)
    stopifnot(native_sha=="1f0cfe59556ebc3b3bce92be7c55256fe61cf4048a8182086b34d1ff5b898779")
    index <- match(ids,names(gr))
    stopifnot(!anyNA(index),identical(names(gr)[index],ids))
    gr <- gr[index]
    chr <- as.character(GenomicRanges::seqnames(gr))
    s <- GenomicRanges::start(gr)
    e <- GenomicRanges::end(gr)
    strand <- as.character(GenomicRanges::strand(gr))
    stopifnot(all(chr %in% paste0("chr",1:22)),all(strand %in% c("+","-","*")))
    # Retain the actual width distribution even if the range guard fails.
    emit(as.data.frame(table(width=e-s+1L)),"annotation-native-widths.tsv")
    bin <- region_start(s,e)
    stopifnot(all(s-1L>=bin),all(s-1L<bin+1000L),
        all(e>s-1L),all(e-(s-1L)==GenomicRanges::width(gr)))
    region <- paste(chr,bin,bin+1000L,sep=":")
    locus <- paste(chr,s-1L,sep=":")
    duplicate_anchor <- duplicated(locus)|duplicated(locus,fromLast=TRUE)
    # The old ordering and coordinate file are exact checksum-pinned companion
    # files. Positional joining is allowed only inside that historical release.
    old_order <- read.delim(gzfile(file.path(input,"HM450.ordering.tsv.gz")),
        check.names=FALSE,stringsAsFactors=FALSE)
    old_coord <- read.delim(gzfile(file.path(input,"HM450.hg38.coord.tsv.gz")),
        check.names=FALSE,colClasses="character",quote="",comment.char="")
    stopifnot(identical(names(old_order),c("Probe_ID","M","U","col")),
        identical(names(old_coord),c("CpG_chrm","CpG_beg","strand","mapQ")),
        nrow(old_order)==486427L,nrow(old_coord)==nrow(old_order),
        !anyNA(old_order$Probe_ID),!anyDuplicated(old_order$Probe_ID))
    old_ix <- match(ids,old_order$Probe_ID)
    old_chr <- old_coord$CpG_chrm[old_ix]
    old_start <- suppressWarnings(as.numeric(old_coord$CpG_beg[old_ix]))
    old_valid <- !is.na(old_ix)&old_chr %in% paste0("chr",1:22)&
        is.finite(old_start)&old_start>=0&old_start==floor(old_start)
    # A release difference is a reported finding, not an instruction to
    # replace native coordinates or silently redefine the eligible universe.
    comparison <- rep("absent_from_historical_order",length(ids))
    comparison[!is.na(old_ix)] <- "historical_coordinate_unavailable"
    comparison[old_valid] <- ifelse(chr[old_valid]==old_chr[old_valid]&
        s[old_valid]-1L==old_start[old_valid],"same_anchor","different_anchor")
    coordinates <- data.frame(probe=ids,build="hg38",chr=chr,
        native_start1=s,native_end1=e,strand=strand,start0=s-1L,end0=e,
        region=region,duplicate_anchor=duplicate_anchor,historical_comparison=comparison)
    stopifnot(identical(coordinates$probe,ids),!anyDuplicated(coordinates$probe))
    emit(coordinates,"annotation-native-coordinates.tsv")
    regions <- table(region)
    region_counts <- data.frame(region=names(regions),eligible_probes=as.integer(regions),
        at_least_three=as.integer(regions)>=3L)
    stopifnot(sum(region_counts$eligible_probes)==length(ids))
    emit(region_counts,"annotation-region-census.tsv")
    emit_summary(c(eligible_probes=length(ids),native_annotation_rds_sha256=native_sha,
        denominator_sha256=sha256(ids_path),region_count=length(regions),
        regions_with_at_least_three=sum(regions>=3L),regions_with_fewer_than_three=sum(regions<3L),
        probes_in_regions_with_fewer_than_three=sum(regions[regions<3L]),
        interval_crosses_bin=sum(e>bin+1000L),
        duplicate_anchor_probes=sum(duplicate_anchor),
        distinct_anchors=length(unique(locus)),unknown_strand=sum(strand=="*"),
        as.list(table(factor(comparison,levels=c("absent_from_historical_order",
            "historical_coordinate_unavailable","same_anchor","different_anchor")))),
        coordinates_sha256=sha256(file.path(output,"annotation-native-coordinates.tsv"))),
        "annotation-coordinate-summary.tsv")
    rm(gr,coordinates,old_order,old_coord,old_ix,old_chr,old_start,old_valid,
        comparison,index,chr,s,e,strand,bin,region,locus,duplicate_anchor,regions,region_counts)
    invisible(gc(full=TRUE))

    # Native hg19 gene annotation remains a separate ID-based relationship.
    # Use the package's own mapper in bounded disjoint CpG chunks; only
    # mapping is chunked, never limma moderation or enrichment testing.
    anno <- minfi::getAnnotation(
        IlluminaHumanMethylation450kanno.ilmn12.hg19::IlluminaHumanMethylation450kanno.ilmn12.hg19)
    stopifnot(!anyDuplicated(rownames(anno)),
        all(c("Name","UCSC_RefGene_Name","UCSC_RefGene_Group") %in% names(anno)))
    annotation_index <- match(ids,rownames(anno))
    present <- !is.na(annotation_index)
    a <- anno[annotation_index[present],c("Name","UCSC_RefGene_Name","UCSC_RefGene_Group"),drop=FALSE]
    stopifnot(identical(rownames(a),ids[present]),identical(as.character(a$Name),ids[present]))
    rm(anno)
    invisible(gc(full=TRUE))
    flat <- getFromNamespace(".getFlatAnnotation","missMethyl")
    canonical <- function(x) {
        x <- x[,c("cpg","entrezid","symbol","alias","group"),drop=FALSE]
        x[] <- lapply(x,as.character)
        x <- x[order(x$cpg,x$entrezid,method="radix"),,drop=FALSE]
        rownames(x) <- NULL
        stopifnot(!anyNA(x$cpg),all(grepl("^cg[0-9]{8}$",x$cpg)),
            !anyNA(x$entrezid),all(grepl("^[0-9]+$",x$entrezid)),
            !anyDuplicated(x[,c("cpg","entrezid")]))
        x
    }
    chunks <- split(seq_len(nrow(a)),(seq_len(nrow(a))-1L)%/%20000L)
    native_pairs <- canonical(do.call(rbind,lapply(chunks,function(i) {
        x <- flat("450K",a[i,,drop=FALSE])
        stopifnot(all(x$cpg %in% rownames(a)[i]))
        x
    })))
    # Exact full-row comparison on the previous unrelated technical 4000
    # probe universe intersected with the fixed eligible set.
    audit_ids <- intersect(readLines(file.path(scratch,"synthetic-probe-universe.txt")),rownames(a))
    stopifnot(length(audit_ids)>0L)
    whole <- canonical(flat("450K",a[match(audit_ids,rownames(a)),,drop=FALSE]))
    chunked <- canonical(native_pairs[native_pairs$cpg %in% audit_ids,,drop=FALSE])
    stopifnot(identical(whole,chunked),all(native_pairs$cpg %in% ids[present]))
    counts <- tabulate(match(native_pairs$cpg,ids),nbins=length(ids))
    stopifnot(sum(counts)==nrow(native_pairs),all(counts[!present]==0L))
    status <- ifelse(!present,"absent_from_hg19_annotation",
        ifelse(counts==0L,"present_no_native_gene_mapping",
            ifelse(counts==1L,"one_native_gene","multiple_native_genes")))
    # Native alias2SymbolTable chooses a first mapping for ambiguous aliases.
    # Preserve source symbol and native-selected alias; this is NOT a new
    # authoritative HGNC/transcript mapping or demonstration of regulation.
    emit(native_pairs,"annotation-native-gene-pairs.tsv")
    emit(data.frame(probe=ids,annotation_build="hg19",annotation_present=present,
        native_gene_count=counts,disposition=status),"annotation-gene-coverage.tsv")
    emit_summary(c(eligible_probes=length(ids),annotation_present=sum(present),
        annotation_absent=sum(!present),gene_mapped=sum(counts>0L),
        gene_unmapped=sum(counts==0L),mapped_to_multiple_genes=sum(counts>1L),
        unique_native_pairs=nrow(native_pairs),native_entrez_genes=length(unique(native_pairs$entrezid)),
        whole_vs_chunked_audit_probes=length(audit_ids),whole_vs_chunked_audit_pairs=nrow(whole),
        native_pairs_sha256=sha256(file.path(output,"annotation-native-gene-pairs.tsv")),
        coverage_sha256=sha256(file.path(output,"annotation-gene-coverage.tsv"))),
        "annotation-gene-summary.tsv")
    capture.output(sessionInfo(),file=file.path(output,"annotation-session-info.txt"))
    emit(data.frame(package=c("sesameData","IlluminaHumanMethylation450kanno.ilmn12.hg19","org.Hs.eg.db"),
        version=c("1.28.0","0.6.1","3.22.0"),
        license=vapply(c("sesameData","IlluminaHumanMethylation450kanno.ilmn12.hg19","org.Hs.eg.db"),
            function(p) as.character(packageDescription(p,fields="License")),character(1))),
        "annotation-source-notices.tsv")
    writeLines(c("scope=public_reference_only","status=passed",
        "scientific_cohort_qc=false","scientific_admission=false","n1_frozen=false",
        "transcript_mapping_qualified=false","cohort_scale_enrichment_qualified=false"),
        file.path(output,"annotation-disposition.txt"))
    cat("HM450 reference-only annotation: ",length(ids)," eligible IDs; ",
        sum(counts>0L)," native gene-mapped; ",nrow(native_pairs)," unique pairs.\n",sep="")
}
