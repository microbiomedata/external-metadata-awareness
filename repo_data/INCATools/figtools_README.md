
[![Build](https://travis-ci.org/INCATools/figtools.svg?branch=master)](https://travis-ci.org/INCATools/figtools?branch=master)

# figtools

Scala toolkit for analyzing [FigShare](https://figshare.com/) figures.

`figtools` allows you to programmatically download, search, list, and analyze
publication figure images from the `FigShare` database. The `analyze` feature
uses image processing techniques to separate publication figures into
separate subpanels, and attempts to assign the correct caption label from the
figure description text to each subpanel.

## Installation Instructions

Make sure you have the Java JDK 8 and [sbt](https://www.scala-sbt.org/) installed.

You will also need [tesseract](https://github.com/tesseract-ocr/tesseract) 
OCR installed.

On macOS, you can install all the dependencies using the following:

If you have not installed [Homebrew](https://brew.sh/), do:

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Next, install dependencies using `Homebrew`:

```
brew cask install java8
brew install sbt tesseract
```

Next, in the top-level `figtools` directory, run:

```
sbt package
```

Now in the `figtools/bin`, directory, run the `figtools` script.

NOTE: `figtools` needs to know how to find the tesseract `tessdata` directory.
It will look in `/usr/share/tessdata`, in the current directory, or
in the directory pointed to by the `TESSDATA_PREFIX` environment variable.
If you installed tesseract with homebrew, you can set `TESSDATA_PREFIX` to
`/usr/local/opt/tesseract/share/tessdata`.

The first time you run the script, it will download all of its dependencies to
your `~/.ivy2` directory. Then it will display the help message:

```
FigTools 0.1.0
Usage: figtools [options] [command] [command-options]

Available commands: analyze, download, download-all, get, list, search

Recursively analyze and segment a directory full of publication images.
-----------------------------------------------------------------------
Command: analyze
Usage: figtools analyze <List of FigShare IDs to analyze (optional)>
  --dir  <DIR>
        Directory in which to analyze image files
  --pdf-export-resolution  <DPI>
        Resolution to use when exporting PDFs to images
  --edge-detector  <MODULE>
        Edge detector to use. Possible values: susan imagej

Download figures from figtools into the current directory
---------------------------------------------------------
Command: download
Usage: figtools download <List of FigShare IDs>
  --url  <URL>
        URL of FigShare API
  --out-dir  <DIRECTORY>
        Output directory

Download *ALL* figures from figtools into the current directory.
----------------------------------------------------------------
Command: download-all
Usage: figtools download-all
  --url  <URL>
        URL of FigShare API
  --out-dir  <DIRECTORY>
        Output directory

Get metadata for FigShare IDs
-----------------------------
Command: get
Usage: figtools get <List of FigShare IDs>
  --url  <URL>
        URL of FigShare API

List FigShare IDs
-----------------
Command: list
Usage: figtools list
  --url  <URL>
        URL of FigShare API

Search for FigShare IDs
-----------------------
Command: search
Usage: figtools search <List of search terms>
  --url  <URL>
        URL of FigShare API
```
