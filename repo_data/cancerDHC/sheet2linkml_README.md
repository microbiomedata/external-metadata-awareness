# sheet2linkml

[![PyPI version](https://badge.fury.io/py/sheet2linkml.svg)](https://badge.fury.io/py/sheet2linkml)

A python package for converting the CRDC-H data model, which is currently stored in a 
[Google Sheet](https://docs.google.com/spreadsheets/d/1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4/). The command line utility built into the package can be used 
to generate a [LinkML](https://github.com/linkml/linkml) representation of the CRDC-H data model.

## Installation Requirements and Pre-requisites

- Python 3.7 or higher
- [pyenv](https://github.com/pyenv/pyenv)
    - If you do not have a version of Python greater than 3.9, it is recommended to use `pyenv` to be able to easily use and 
switch between multiple Python versions.
    - If you’re experiencing issues with pyenv on macOS, you can consider using [miniconda](https://docs.conda.io/en/latest/miniconda.html).
- [poetry](https://github.com/python-poetry/poetry)
    - One-time installation commands are available for [osx/linux/bash on windows](https://github.com/python-poetry/poetry#osx--linux--bashonwindows-install-instructions) and for [windows powershell](https://github.com/python-poetry/poetry#windows-powershell-install-instructions).

If you are using a Windows machine, typical bash programs will not work on `cmd` in the same way as they work in the Linux/MacOS terminals. To circumvent this, it is recommended that you use one of the following Bash on Windows strategies:
- [WSL](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/)
- [Cygwin](https://cygwin.com/index.html)
- [Git Bash](https://gitforwindows.org/) 

so you can easily execute the command line utilities that are described later in these docs.



## Installing

Create and activate a Python 3.9+ virtual environment within which you can install the package:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install sheet2linkml
```

## Authorization

sheet2linkml uses the [`pygsheets` library](https://github.com/nithinmurali/pygsheets) in order to access sheets in
Google Drive. To authorize it to access your Google Sheets, you will need to create and download Google Drive client credentials. First,
[enable the Google Drive API](https://developers.google.com/drive/api/v3/enable-drive-api). After the API is enabled, 
[create and download the client credentials](https://www.iperiusbackup.net/en/how-to-enable-google-drive-api-and-get-client-credentials/)
from the [Google API Console](https://console.developers.google.com/). Save the file as `google_api_credentials.json` in
the root directory of this project. [Detailed instructions and screenshots](https://pygsheets.readthedocs.io/en/stable/authorization.html)
are also available from the [`pygsheets` documentation](https://pygsheets.readthedocs.io/).

## Command Line Client Usage

Identify the Google Sheet that you want to convert to LinkML. Note that sheet2linkml is not currently a general-purpose Google Sheet to LinkML converter. It will only work with Google Sheets that have been written in a particular, currently undefined format.

Contact your CCDH colleagues to obtain the correct sheet ID and assert it either in a `.env` file or in the shell, like this:

```shell
export CDM_GOOGLE_SHEET_ID=1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4
```

A `google_api_credentials.json` file is also required in the root of this repo as detailed in the Authorization section above.

And the user is responsible for defining 
- `~/path/to/crdch_model.yaml`
- `~/path/to/logging.ini`
    - `./logging.ini` may be adaquate for many users

### Then perform the conversion:

```shell
sheet2linkml --output ~/path/to/crdch_model.yaml --logging-config ~/path/to/logging.ini
```
