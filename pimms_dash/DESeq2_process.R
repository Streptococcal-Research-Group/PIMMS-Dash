library(DESeq2)

run_deseq <- function(countsdata, metadata, filtering=TRUE) {
  # Perform DESeq
  pimms2 <- DESeqDataSetFromMatrix(countData = countsdata, colData = metadata, design =~dex, tidy = TRUE)
  
  # https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html#why-are-some-p-values-set-to-na
  if (filtering) {
    pimms2 <- DESeq(pimms2)
    res <- results(pimms2)
  } else {
    pimms2 <- DESeq(pimms2, minReplicatesForReplace=Inf)
    res <- results(pimms2, cooksCutoff = FALSE, independentFiltering=FALSE)
  }

  # Get PCA plot dataframe
  if (any(lapply(countsdata, function(x){ length(which(x!=0))<1000}))) {
    vsdata <- varianceStabilizingTransformation(pimms2, blind = FALSE)
  } else {
    vsdata <- vst(pimms2, blind = FALSE)
  }
  pca <- plotPCA(vsdata, intgroup="dex")
  
  # Create output dataframes
  deseq_data <- data.frame(res)
  
  output_list <- list("deseq"=deseq_data, "pca"=pca)
  return(output_list)
}
