library(DESeq2)

run_deseq <- function(countsdata, metadata) {
  # Perform DESeq
  pimms2 <- DESeqDataSetFromMatrix(countData = countsdata, colData = metadata, design =~dex, tidy = TRUE)
  pimms2 <- DESeq(pimms2)
  res <- results(pimms2)
  
  # Get PCA plot dataframe
  vsdata <- vst(pimms2, blind = FALSE)
  pca <- plotPCA(vsdata, intgroup="dex")
  
  # Create output dataframes
  deseq_data <- data.frame(res)
  
  output_list <- list("deseq"=deseq_data, "pca"=pca)
  return(output_list)
}
