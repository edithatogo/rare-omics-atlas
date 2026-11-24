#!/usr/bin/env Rscript
# Installed native package qualification, unrelated technical/synthetic inputs only.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4L)
stage <- match.arg(args[3],c("install","technical","limma","enrichment"))
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
    writeLines(c("stage=technical","status=passed","scope=unrelated_HM450_fixture",
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
    writeLines(c("stage=limma","status=passed","scope=synthetic_named_M_matrix",
        "clinical_inference=false"),file.path(output,"limma-disposition.txt"))

}

if (stage=="enrichment") {
    suppressPackageStartupMessages(library(missMethyl))
    universe <- readLines(file.path(scratch,"synthetic-probe-universe.txt"))
    stopifnot(length(universe)==4000L,!anyDuplicated(universe))
    selected <- universe[seq(1,length(universe),by=20L)]
    stopifnot(length(universe)==4000L,length(selected)==200L,all(selected %in% universe))
    # The native mapping function filters to all.cpg after flattening. Supply
    # the exact tested annotation rows before flattening to bound memory.
    anno <- minfi::getAnnotation(IlluminaHumanMethylation450kanno.ilmn12.hg19::IlluminaHumanMethylation450kanno.ilmn12.hg19)
    stopifnot(!anyDuplicated(rownames(anno)),all(universe %in% rownames(anno)))
    anno <- anno[match(universe,rownames(anno)),,drop=FALSE]
    stopifnot(identical(rownames(anno),universe))
    invisible(gc(full=TRUE))
    go <- gometh(sig.cpg=selected,all.cpg=universe,collection="GO",array.type="450K",
        anno=anno,plot.bias=FALSE,prior.prob=TRUE,equiv.cpg=TRUE,fract.counts=TRUE)
    stopifnot(nrow(go)>0L,!anyDuplicated(rownames(go)),
        all(c("P.DE","FDR") %in% colnames(go)),any(is.finite(go$P.DE)),
        all(is.na(go$P.DE)|(go$P.DE>=0&go$P.DE<=1)),
        all(is.na(go$FDR)|(go$FDR>=0&go$FDR<=1)))
    cat("Synthetic missMethyl: ",length(universe)," tested, ",length(selected),
        " selected, ",nrow(go)," GO rows.\n",sep="")
    stopifnot(isTRUE(all.equal(go$FDR,p.adjust(go$P.DE,"BH"),tolerance=1e-12,check.attributes=FALSE)))
    write.table(data.frame(metric=c("tested","selected","GO_rows","finite_p","max_BH_error"),
        value=c(length(universe),length(selected),nrow(go),sum(is.finite(go$P.DE)),
        max(abs(go$FDR-p.adjust(go$P.DE,"BH")),na.rm=TRUE))),
        file.path(output,"enrichment-summary.tsv"),sep="\t",quote=FALSE,row.names=FALSE)
    capture.output(sessionInfo(),file=file.path(output,"enrichment-session-info.txt"))
    stopifnot(file.exists(file.path(output,"technical-disposition.txt")),file.exists(file.path(output,"limma-disposition.txt")))
    writeLines(c("scope=native_release_technical_and_synthetic","limma_synthetic_pass=true",
        "missMethyl_synthetic_pass=true","full_cross_version_preprocessing_parity_claimed=false",
        "clinical_cohort_qc=false","owner_device_qualified=false",
        "institutional_determination=false","scientific_admitted=false"),
        file.path(output,"disposition.txt"))

}
