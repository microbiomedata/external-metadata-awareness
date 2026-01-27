# humann_hpc

Based on the original version available from https://github.com/biobakery/humann, and the concise [docs for installation](https://huttenhower.sph.harvard.edu/humann). Also see [Alise Ponsero's version](https://github.com/aponsero/Humann_annotation_HPC).


## Pipeline summary

pipeline includes the following Steps

1) [bowtie2](https://github.com/BenLangmead/bowtie2) to remove human contamination

2) [TrimGalore](https://github.com/FelixKrueger/TrimGalore) to do quality control (e.g. removing low quality reads and trimming adaptors)

3) [humann](https://github.com/biobakery/humann) to get functional annotations using UNIREF90 which we used to get to KEGG annotations as well as and taxonomic annotations using metaphlan


## Steps to Install Humann

Done on the University of Arizona HPC running linux with SLURM.

```
conda create --name humann_kai python=3.7 // Can give it a different name just make sure to be consistent

# Activate Environment
conda activate humann_kai

#Set conda channel priority:
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --add channels biobakery

#install pip
conda install pip

# install humann
pip install humann --no-binary :all:

# install metaphlan
conda install -c bioconda metaphlan
# fix libtbb2 for bowtie2
conda install tbb=2020.2

# install bowtie2 #might not need this
conda install -c bioconda bowtie2

# install trim-galore
conda install -c bioconda trim-galore

```

## Install databases

```
# install databases done in new folder database
mkdir database
cd database/

#install humann databases: chocophlan uniref and human util
humann_databases --download chocophlan full .
humann_databases --download uniref uniref90_diamond .
humann_databases --download utility_mapping full .

#Download Human genome for bowtie2
wget https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.zip
unzip GRCh38_noalt_as.zip

```

## Run

Make sure to modify the list of samples in `config/list.txt`

From `/xdisk/bhurwitz/mig2020/rsgrps/bhurwitz/kai/humann_hpc`
```
Run main job:
./run_array_job.sh

Run for rarefaction curve:
./test_run_array_job.sh
```

### Get Functional results:

From the top directory run:
```
mkdir results_60_million

mv humann_results results_60_million

interactive # gives a node to work on

./norm_merge_results.sh
```

take file: `result_tables/humann_KOabundance_unstratified.tsv` with scp or similar.

e.g.: `scp kblumberg@sftp.hpc.arizona.edu:/xdisk/bhurwitz/mig2020/rsgrps/bhurwitz/kai/humann_hpc/results_60_million/humann_results/result_tables/humann_KOabundance_unstratified.tsv Heidi_KEGG_normalized_60M.tsv`

### Get Taxonomic results

To make the merged taxa table, from inside the `humann_results` folder, run the following:

```
mkdir bug_list
cp Karnes-10-1_UA-NGsp-fastq_Karnes-C11-U035_Karnes-C11_S285_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-10-2_UA-NGsp-fastq_Karnes-C12-U036_Karnes-C12_S286_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-1-1_UA-NGsp-fastq_Karnes-F01-U061_Karnes-F01_S267_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-1-2_UA-NGsp-fastq_Karnes-F02-U062_Karnes-F02_S268_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-2-1_UA-NGsp-fastq_Karnes-F03-U063_Karnes-F03_S269_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-2-2_UA-NGsp-fastq_Karnes-F04-U064_Karnes-F04_S270_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-3-1_UA-NGsp-fastq_Karnes-F05-U065_Karnes-F05_S271_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-3-2_UA-NGsp-fastq_Karnes-F06-U066_Karnes-F06_S272_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-4-1_UA-NGsp-fastq_Karnes-F07-U067_Karnes-F07_S273_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-4-2_UA-NGsp-fastq_Karnes-F08-U068_Karnes-F08_S274_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-5-1_UA-NGsp-fastq_Karnes-F09-U069_Karnes-F09_S275_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-5-2_UA-NGsp-fastq_Karnes-F10-U070_Karnes-F10_S276_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-6-1_UA-NGsp-fastq_Karnes-F11-U071_Karnes-F11_S277_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-6-2_UA-NGsp-fastq_Karnes-F12-U072_Karnes-F12_S278_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-7-1_UA-NGsp-fastq_Karnes-B09-U021_Karnes-B09_S279_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-7-2_UA-NGsp-fastq_Karnes-B10-U022_Karnes-B10_S280_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-8-1_UA-NGsp-fastq_Karnes-B11-U023_Karnes-B11_S281_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-8-2_UA-NGsp-fastq_Karnes-B12-U024_Karnes-B12_S282_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-9-1_UA-NGsp-fastq_Karnes-C09-U033_Karnes-C09_S283_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/
cp Karnes-9-2_UA-NGsp-fastq_Karnes-C10-U034_Karnes-C10_S284_R1_001_trimmed_humann_temp/*_bugs_list.tsv bug_list/

source activate humann_kai
merge_metaphlan_tables.py bug_list/*_bugs_list.tsv > merged_abundance_table.txt
```

Take file `merged_abundance_table.txt`

e.g.: `scp kblumberg@sftp.hpc.arizona.edu:/xdisk/bhurwitz/mig2020/rsgrps/bhurwitz/kai/humann_hpc/results_60_million/humann_results/merged_abundance_table.txt Heidi_metaphlan3_taxa_60M.tsv`
