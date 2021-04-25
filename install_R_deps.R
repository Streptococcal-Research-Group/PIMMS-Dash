install.packages("BiocManager", repos="http://cran.us.r-project.org")
BiocManager::install("DESeq2")
stopifnot("DESeq2" %in% installed.packages()[,'Package'])