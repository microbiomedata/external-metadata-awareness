# Algorithm overview
- This is an algorithm designed to prioritize disease or genes based on an input set of patient phenotypes
- Leverages the following data and formalities
  - phenio.db + semsimian algorithm for patient disease or gene prioritization based on phenotypes
  - monarch-kg nodes file and sssom mapping file to get hgnc, mondo, and hpo 'metadata'
  - diseases and genes are reported in MONDO and HGNC namespaces respectively
  - input phenotypes currently must be encoded as HPO terms and must start with "HP:"... For example HP:3000043
  - input to the algorithm can be one of the following
    - filepath to directory of phenopackets (with HPO encoded phenotypes) where each file ends with the .json extenstion
    - filepath to single phenopacket (again ending with .json file extension)
    - comma separated list of HPO encoded phenotype terms... for example HP:3000043,HP:0500017 (single term can also be used as input)
  - output is a single .tsv file per sample, with the top hits appearing first and the worst hits appearing last (higher 'score' == better match)
- Note, the download_data.py script provided defaults to the latest version of phenio, monarch-kg, and sssom mappings. However, these files can be manually downloaded for different versions if so desired.
  
# Installation and setup
```bash
   git clone git@github.com:monarch-initiative/semphen.git
   cd semphen
   python python/download_data.py -d path/to/data/download/directory
```
- TO DO: Add poetry install instructions and .toml file... pip install might be nice as well (pypi)

# Running the algorithm example commands
- Running on multiple phenopackets (-m can be gene or disease)
  ```bash
     python python/semphen.py -i path/to/json/phenopackets \
                              -o path/to/output/directory \
                              -d path/to/data/download/directory \
                              -m gene
  ```
  
- Additionally, the -c argument can be used to parallel process multiple phenopackets at once. To use 10 cores, use -c 10
  ```bash
     python python/semphen.py -i path/to/json/phenopackets \
                              -o path/to/output/directory \
                              -d path/to/data/download/directory \
                              -m disease \
                              -c 10
  ```
- Running on a single input phenopacket
  ```bash
     python python/semphen.py -i path/to/input/phenopacket.json \
                              -o path/to/output/file.tsv \
                              -d path/to/data/download/directory \
                              -m gene
  ```
- Running with HPO terms directly instead of pulling from phenopacket(s)
  ```bash
     python python/semphen.py -i HP:3000043,HP:0500017 \
                              -o path/to/output/file.tsv \
                              -d path/to/data/download/directory \
                              -m disease
  ```
