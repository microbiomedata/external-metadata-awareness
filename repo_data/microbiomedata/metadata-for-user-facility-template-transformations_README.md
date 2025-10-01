# Metadata for User facility Template Transformations (MUTTs)

## Introduction

The programs bundled in this repository intend to solve the problem of automatically retrieving Biosample metadata records for a given study submitted to NMDC through the [NMDC Submission Portal](https://data.microbiomedata.org/submission/home), and converting the metadata into Excel spreadsheets that are accepted by [DOE user facilities](https://www.energy.gov/science/office-science-user-facilities).

There are two components (of MUTTs) to keep in mind when trying to use this application -

1. JSON header (sometimes also called *mapper*) configuration file
  * The headers that go into the user facility spreadsheet outputs is controlled by JSON files
  * The keys at the top level are used to indicate the main headers in the output. These values have mappings in the mapping configuration files described in the next point
  * You can use numbered keys to add more header information to clarify what a particular column contains
  * The *header* keyword is reserved in case you want to use some other column names as the main header
  * The *sub_port_mapping* keyword can be used to specify mappings between columns in the Submission Portal template and columns in the user facility spreadsheet outputs
  * Follow the examples that have already been specified in [input-files](input-files/). There are two user facility header customizations that have already been created as examples for the NMDC. They are:
    * EMSL header configuration: [emsl_header.json](input-files/emsl_header.json)
    * JGI MG and MT header configuration
      * [jgi_mg_header.json](input-files/jgi_mg_header.json)
      * [jgi_mt_header.json](input-files/jgi_mt_header.json)

2. [etl.py](etl.py)
   The command line application that can facilitate the conversion of metadata from the Submission Portal into user facility formats by consuming the above two files as inputs.

## Software Requirements
1. [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. [Python](https://www.python.org/downloads/release/python-390/) > 3.9

## Setup

1.  Clone this repo

```
git clone https://github.com/microbiomedata/metadata-for-user-facility-template-transformations.git
```

2. Install dependencies with poetry

```
poetry install
```

3. You need to obtain your NMDC Data and Submission Portal API Access Token and copy it over into your `.env` file, and associate it with the `DATA_PORTAL_REFRESH_TOKEN` environment variable. 
   1. You can retrieve your Access Token by following this link: https://data.microbiomedata.org/user
   2. Go over to the `.env` file and copy the Refresh Token like `DATA_PORTAL_REFRESH_TOKEN={refresh_token_value}`

4. Run `etl.py` with options as follows:

```bash
metadata-for-user-facility-template-transformations git:(main) ✗ poetry run python etl.py --help
Usage: etl.py [OPTIONS]

  Command-line interface for creating a spreadsheet based on metadata records.

  :param submission: The ID of the metadata submission. 
  :param user_facility: The user facility to retrieve data from. 
  :param header: True if the headers should be included, False otherwise. 
  :param mapper: Path to the JSON mapper specifying column mappings.
  :param unique_field: Unique field to identify the metadata records. 
  :param output: Path to the output XLSX file.

Options:
  -s, --submission TEXT       Metadata submission id.  [required]
  -u, --user-facility TEXT    User facility to send data to.  [required]
  -h, --header / --no-header  [default: no-header]
  -m, --mapper PATH           Path to user facility specific JSON file.
                              [required]
  -uf, --unique-field TEXT    Unique field to identify the metadata records.
                              [required]
  -o, --output TEXT           Path to result output XLSX file.  [required]
  --help                      Show this message and exit.
```


- Example - JGI/JGI_MG
```
poetry run python etl.py --submission {UUID of the target submission} --unique-field samp_name --user-facility jgi_mg --mapper input-files/jgi_mg_header.json --output file-name_jgi.xlsx
```

- Example - EMSL
```
poetry run python etl.py --submission {UUID of the target submission} --user-facility emsl --mapper input-files/emsl_header.json --header --unique-field samp_name --output file-name_emsl.xlsx
```
