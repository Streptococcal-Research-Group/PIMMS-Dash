library(DESeq2)

run_deseq <- function(countsdata, metadata) {
  pimms2 <- DESeqDataSetFromMatrix(countData = countsdata, colData = metadata, design =~dex, tidy = TRUE)
  pimms2 <- DESeq(pimms2)
  res <- results(pimms2)
  df = data.frame(res)
  return(df)
}
