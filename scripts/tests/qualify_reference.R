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
    qcd3 <- prepSesame(raw3,"QCD")
    p3 <- pOOBAH(qcd3,return.pval=TRUE)
    processed3 <- noob(pOOBAH(qcd3,pval.threshold=0.05))
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
    control_signals <- sesame::controls(raw3)
    stopifnot(is.data.frame(control_signals),nrow(control_signals)>0L,
        all(c("UG","UR","Type") %in% colnames(control_signals)))
    write.table(control_signals,file.path(output,"technical-cohort-qc-controls.tsv"),
        sep="\t",quote=FALSE,row.names=FALSE)
    writeLines(c(paste0("native_control_records=",nrow(control_signals)),
        "candidate_sample_threshold=0.95","candidate_threshold_validated_for_clinical_use=false",
        "control_acceptance_ranges_validated=false","clinical_cohort_qc=false",
        "scope=unrelated_technical_fixture_only"),file.path(output,"technical-cohort-qc-disposition.txt"))
    cat("Technical fixed-denominator QC: ",count,"/",n," valid (",
        sprintf("%.6f",count/n),"); candidate threshold only.\n",sep="")

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
