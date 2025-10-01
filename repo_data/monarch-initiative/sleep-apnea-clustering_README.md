# sleep-apnea-clustering

This repository aims to be a pipeline for processing the Sleep Heart Health Study (SHHS) dataset for cluster analysis. SHHS is available for download through the National Sleep Research Repository (NSRR). The R scripts and library functions here work with the CSV files downloaded from the NSRR listed in shhs-process.R. (Users will have to apply to download those files through the NSRR).

Currently, these scripts are intended to be run in a certain order. We are working on combining everything into one package, but to replicate the analysis done in my thesis, it is best to run the scripts.

### 1. shhs-process
  Loads data into R workspace. The key files are a data csv and a datadict csv (the dictionary of all the variables). 
  Note: You need to adjust file pointers to point to the directories where the files are located.

### 2. workingSHHS1
  * Subsets the data from shhs1-data.csv, cleans the data (recoding binary vars as factors, fixing data entry errors, etc.) and builds a data frame of relevant columns.
  * workingcvd, workinginterim, workingSHHS2 all do the same thing for those respective datasets.
  
### 3. factoranal
  * Input: data frame from workingSHHS1 (df)
  * Calculates a heterochoric correlation (hc) for df, plots correlation heatmap
  * Finds ideal number of factors through parallel analysis and VSS.
  * Find factor loadings for n factors.
  * Plots factor plot and factor diagram.
  
At this point, one would go back and select only the columns they want in df (that is, the important factors).
  
#### 3a. parallelpretty
  Function for plotting scree plot/parallel analysis in a nice, publication-worthy way.
  
  Code taken from https://sakaluk.wordpress.com/2016/05/26/11-make-it-pretty-scree-plots-and-parallel-analysis-using-psych-and-ggplot2/
  
  Sakaluk, J. K., & Short, S. D. (2016). [A Methodological Review of Exploratory Factor Analysis in Sexuality Research: Used Practices,  Best Practices, and Data Analysis Resources. Journal of Sex Research.](http://www.tandfonline.com/doi/abs/10.1080/00224499.2015.1137538)
  
### 4. calcGowerMat
  Calculates Gower distance matrix for hc.
  
### 5. plotinternalmetric
  * Calculates clusterings for hclust (many linkage method options), diana, and pam.
  * Calculates connectivity, Dunn index, silhouette width for each of those clusterings, with cuts from 2-10.
  * Plots a line graph for connectivity, Dunn, silhouette vs. number of clusters (for different clusterings)
  
Ideas and concepts of comparing clustering solutions came from: [A consensus framework for clustering microarray data. Ted Laderas and Shannon McWeeney. OMICS: A Journal of Integrative Biology. 2007. 116-128.](https://doi-org/10.1089/omi.2006.0008)

At this point, pick a particular clustering method and number of clusters
  

  

