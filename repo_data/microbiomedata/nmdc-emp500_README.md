# nmdc-emp500
A consolidation of EMP500 data IDs/links and metadata, as required by NMDC

## Requirements
- Python 3.9+
- NCBI E-utilities, specifically the [Entrez Direct](https://www.ncbi.nlm.nih.gov/books/NBK179288/) CLI tools
- sqlite3 command line tool
- Python packages, specified in `requirements.txt`. See below.

## Usage
- clone this, `git@github.com:microbiomedata/nmdc-emp500.git`
- `cd nmdc-emp500`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `make all`
  - Be patient. Downlaods some large files, decompresses, runs e-searches against NCBI...
- enjoy `target/emp500_biosample_sra_no_empty_cols.tsv`

**Note:** This dataset includes EMP500 data from whole-genome analyses, not amplicon analyses. It is also filtered for soil biosamples only.

---

- ~~Python [poetry](https://python-poetry.org/docs/#installation) might be helpful but is not in use yet.~~
