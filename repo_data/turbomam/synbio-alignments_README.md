## Usage

First, make sure you have [`sshpass`](https://gist.github.com/arunoda/7790979) installed.

Next, set the following environment variables, which are used to log into the LBL server.
* `LBL_USER`
* `LBL_PASSWORD`

Optionally, set up a Python virtual environment and install the requirements (or just install the requirements):
```
python3 -m venv _venv
source _venv/bin/activate
python3 -m pip install -r requirements.txt
```

Before running, you will need to mirror some of the files from the LBL server to your local machine. This includes selecting the "best" reference genome from the available genomes in the master sample's `reference_genome` directory. This is done based on the ANI score compared to the Unicycler assembly. While there are other assembly FASTAs to use, the Unicycler assembly is always used in this process.
```
make prepare
```

Now you're ready to go! Running the following will create `build/alignments.csv`:
```
make align
```

This output contains the following:
* `sample`: master sample ID
* `ref_genome`: reference genome used (selected from `data/iarpa/TE/[sample]/reference_genome`)
* `seq_id`: element sequence ID
* `ref_start`: start of alignment in reference genome
* `ref_end`: end of alignment in reference genome
* `assembly_start`: start of alignment in Unicycler assembly
* `assembly_end`: end of alignment in Unicycler assembly