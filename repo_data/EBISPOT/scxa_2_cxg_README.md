# Single Cell Expression Atlas Knowledge Graph

## Installing Dependencies

This project uses [Poetry](https://python-poetry.org/) to manage dependencies. If you haven't installed Poetry yet, you can do so by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

Once you have Poetry installed, you can install the project dependencies by navigating to the project directory in your terminal and running the following command:

```bash
poetry install
```

This command will read the pyproject.toml file and install all the dependencies listed there.

## Running the bulk experiments script with Poetry

You can run the `bulk_experiments.py` script from the command line. Here's an example of how to do it:

```bash
poetry run python src/bulk_experiments.py --study_filter <study_filter> --chunk_size <chunk_size> --download
```

Replace <study_filter>, <chunk_size>, and <download> with the appropriate values.

- study_filter: A string to filter specific studies.
- chunk_size: An integer indicating the number of studies to process at a time.
- download: (Optional) A boolean flag indicating whether to download files. Pass it to download files and omit it otherwise.
  
For example, to process studies that contain the word "E-CURD" in chunks of 10 and download the files, you would run:

```bash
poetry run python src/bulk_experiments.py --study_filter E-CURD --chunk_size 10 --download
```