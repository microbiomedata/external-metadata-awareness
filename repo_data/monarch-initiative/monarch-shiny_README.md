# monarch-shiny
Experiments with interfaces over Monarch data using Shiny (R)

##Overview
Here, we are experimenting using [Shiny](http://shiny.rstudio.com/) to create
little interfaces over some of the monarch-derived data sets.

The workflow at the moment is to perform 1+ cypher queries over the data
in a monarch-built SciGraph instance, and then load them up in the server 
for each app here.  These
datafiles will be hardcoded at the moment while in early development, 
but then will be
moved to querying over an instance of a SciGraph db directly.

If you want to develop new apps, the easiest is to do this within the 
[Rstudio](http://rstudio.com/) framework.

##Required packages
shiny, ggplot2, VennDiagram, dplyr, d3heatmap, RColorBrewer  

These can be installed using the command ```install.packages(<name of package>)```

##App descriptions
###cross_species_coverage_app
The purpose of this is to enable viewing the available knowledge of the phenotypic
consequences of mutant phenotypes, either based on disease, or inferred 
through model organisms.  

We dump human-gene to phenotype relationships derived either directly to the 
human gene or inferred via human diseases associated with a gene, and 
also inferred to the human gene across orthology with a model organism.

###pheno_explorer_app
Similar to our Phenogrid, this presently uses dummy data to generate random 
matched profiles, and displays the information in a heatmap grid.
