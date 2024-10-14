# Introduction 
The PIMMS (Pragmatic Insertional Mutation Mapping System) pipeline has been developed for simple conditionally essential genome discovery experiments in bacteria.
This Dashboards aims to provide interactive visualisation of the PIMMs pipeline results.

---

### Prerequisites

To run the PIMMS Dashboard, ensure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Web browser (for accessing the dashboard)
  
### Local Development

You can build and run the application locally using Docker. Follow these steps:

1. **Build the Docker image**:
   ```sh
   docker build -t pimmsdash .
   ```

2. **Run the Docker container**:
   ```sh
   docker run --rm -p 8050:8050 pimmsdash
   ```

3. **Access the dashboard**:
   Open your browser and go to:
   ```
   http://127.0.0.1:8050/
   ```

### Deployment

This project is also deployed on Azure App Service. You can access the live version here:

- [PIMMS Dashboard on Azure](https://pimms-dashboard-uon.azurewebsites.net/)


### Citation 

https://doi.org/10.1101/2024.04.10.588854

# Usage

## Test Data
There are two sets of example data provided on the web app. The respective “control” and “test” files can be selected in the left control panel alongside their “coordinate-gff files” and run through the dashboard. The PIMMS-Dashboard pre-loaded datasets are from a high-throughput insertional mutagenesis sequencing experiment comparing Streptococcus suis (P1/7) following growth in laboratory medium (Todd Hewitt broth) and pig serum (Accession number PRJNA1169786). 

You can also upload your own csv and gff files which can be generated using PIMMS2 (https://github.com/Streptococcal-Research-Group/PIMMS2). The new data can be easily uploaded using the drag and drop option on the home screen. This will accept files from the PIMMS data analysis pipeline where a directory is created containing the files which are needed for the dashboard. The data can be generated from any high-throughput mutagenesis experiment including, but not limited to, TraDIS, Tn-Seq and HITS.

Any uploaded data is only available to the current browser session and does not become publicly available. The general dashboard options can be found in the options tab on the left control panel. These include plot configurations for the visualisation tabs and the ability to toggle DESeq2 processing on or off. We recommend that the default outlier removal in DESeq2 is left enabled. You can also download a parametres test file to document settings used during your analysis session.

After loading data and selecting the analysis options, you can work through the tabs to see different results. The six available tabs which allow for the user to visualise the uploaded data table to check its integrity. 

### Data Table
The data table tab is a replication of the uploaded csv file, showing the information of the annotated genome, including the NRMs for each sample. There are also additional columns produced from the DESeq2 module should it have been activated in the options. The output of these data provides an indication of the log2 fold change of the number of insertions for each coding sequence between the two conditions, determining the relative fitness. This is important as some mutations could be lost but not become essential due to compensation within a metabolic pathway. A base mean is also produced along with a raw p-value and multiple comparison corrected p-value using Benjamin-Hochberg correction. Each column can be sorted and searched using the column headers. A radio button is next to each row and can be toggled to select a gene of interest which will actiuvate the Gene Viewer tab.

### NIM Comparison
The NIM Comparison tab allows users to visualise the saturation of insertions across the genomes, between each phenotype. NIM is Normalized Insertions Mapped (total unique insertions mapped/Length of gene in Kb)/(total insertions mapped/106) or the additional NRM option which are Normalized Reads Mapped (total number of reads/length of gene in Kb)/(total mapped read count/106). These provide an indication of the disruption of a given gene in comparison to others within the population and also takes into account the variability of the number of mapped sequence reads for each experiment. The function of this tab is to allow you to quickly assess if there are any regions of the genome which have acquired a disproportionate number of mutations, or “hot spots”. This is a useful quality control step to ensure the mutations are random and has no negative impact on the analysis from poor mutation saturation, PCR or sequence library bias. 

### Venn Diagram
The Venn tab enables users to identify essential of fitness associated genes which are shared or unique to the conditions tested and export this subset list of genes from a chosen intersect. There are additional options to allow further filtering of the results. The sliders can be moved to increase the NIM score to include rare insertional events, or the percentile slider can ignore insertions which appear in the first or final percent of a gene. This can be important to remove insertions which would not disrupt a N or C terminus amino acid and change the function of the gene.

### Genome Scatter and Gene Viewer
The Genome Scatter tab produces an interactive figure where the user can zoom in on regions of the genome to investigate larger areas of essential genes and see if they are represented in both conditions. The Replicates tab produces a PCA which offers the user a method of quality control to see if the replicates cluster as would be expected for the two conditions. Finally, the GeneViewer tab enables finer scale assessment of the insertions detected in a specific gene. A specific gene of interest can be selected in the data table tab which will show each unique insertion point and number of insertions in the GeneViewer tab. This is helpful if used in conjunction with the Venn percentile sliders. 

## Issues

If you encounter any bugs or have feature requests, please submit them via the [GitHub Issues](https://github.com/your-repository-link/issues) page.

## License

This project is licensed under the [MIT License](LICENSE).

---


# Contribute
To contribute to this repository, please use separate branches for 
development of each feature, and use the Pull Request system rather
than merging directly into `main`.
