# collapse_fastas

  * [Description](#description)
  * [Usage](#usage)
  * [Example Output](#example-output)
  * [License](#license)

## Description
A small bash script that uses `awk` and `sed` to combine multiple (multi-)FASTA files into a single FASTA file with a single header. 
Coordinates of the original FASTA entries in the new file are are recorded in a `.coords` and a `.bed` file. 

Tested on Ubuntu 14.04 with GNU `bash` 4.3.11(1)-release, GNU `awk` 4.0.1, GNU `sed` 4.2.2

## Usage
```
Usage: 
collapse_fasta.sh <output_name> /<path_to/<output_dir>/ /<path_to>/<fasta_1>.fa /<path_to>/<fasta_2>.fa [...]

Description:
  Takes as input: a name, an output directory and a list of FASTA files. 
  It combines all separate files into a single file with a single header 
  (specified by the name argument), and makes a-tab separated coordinates 
  file with start/end coordinates of each FASTA entry (i.e. reference 
  genome, chromosomes and/or contigs) in the new collapsed fasta.

Notes: 
  * FASTAs can be a mixture of uncompressed or gzipped (.gz).
  * Output columns are: 
    1) input_file 
    2) fasta_entry_header 
    3) fasta_entry_length 
    4) start_coordinate 
    5) end_coordinate


    Options:
    --help / -h     show this help text

```

## Example Output 
Can be seen under `test_data/collapsed_Test1.fa` and `collapsed_Test1.coords`

## License
MIT
