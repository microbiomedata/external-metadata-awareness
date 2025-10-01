# The Metatranscriptome Assembly Pipeline

## Summary
This workflow was developed by Brian Foster at JGI. Original repo can be found [here](https://code.jgi.doe.gov/BFoster/jgi_meta/-/tree/main/jgi_meta_wdl_sets/metatranscriptome_assembly_and_alignment). This workflow uses BBTools and SPAdes to assemble QC'ed transcriptomic reads. 


## Running Workflow in Cromwell

Description of the files:
 - `.wdl` file: the WDL file for workflow definition
 - `.json` file: the example input for the workflow
 - `.conf` file: the conf file for running Cromwell.
 - `.sh` file: the shell script for running the example workflow


## The Docker image and Dockerfile can be found here

- [microbiomedata/bbtools:38.96](https://hub.docker.com/r/microbiomedata/bbtools)
- [bryce911/spades:3.15.2](https://hub.docker.com/r/bryce911/spades)
- [microbiomedata/workflowmeta:1.1.1](https://hub.docker.com/r/microbiomedata/workflowmeta)


## Input files

The inputs for this workflow are as follows:

1. project name / contig prefix
2. Input fastq


```
{
  "metatranscriptome_assy.input_files":["https://portal.nersc.gov/cfs/m3408/test_data/metaT/SRR11678315/readsqc_output/SRR11678315-int-0.1_filtered.fastq.gz"],
  "metatranscriptome_assy.proj_id":"nmdc:xxxxxxx"
}
```

## Output files

The output will have one directory named by prefix project name and a bunch of output files, including statistical numbers, status log, and run information. 

The main read count table output is named by `prefix.pairedMapped_sorted.bam`. 

```
|-- nmdc_xxxxxxx_bamfiles.tar
|-- nmdc_xxxxxxx_contigs.fna
|-- nmdc_xxxxxxx_pairedMapped.sam.gz
|-- nmdc_xxxxxxx_pairedMapped_sorted.bam
|-- nmdc_xxxxxxx_readlen.txt
|-- nmdc_xxxxxxx_scaffolds.fna
|-- nmdc_xxxxxxx_spades.log
|-- scaffold_stats.json
```
