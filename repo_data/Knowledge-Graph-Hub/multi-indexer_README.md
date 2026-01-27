# multi-indexer
A utility for creating sets of templated indexes for local or remote directories.

## What does this do? 

The `multi-indexer` creates an Apache HTTPd index-like page dictated by a mustache template. Such a template is provided here in `directory-index-template.html`.

If provided with a remote location on an AWS S3 bucket, it will create an index of remote directories/files.
(It *does not* upload any index files.)

Local indexing is *recursive* - it will index subfolders relative to the provided path.

Remote indexing is *not recursive* - it will create a single index for the provided path only.

## Installation

Install with `pip`:

`pip install multi-indexer`

## Usage

Run from the command line as `python -m multi_indexer`.

### Arguments

| Argument            | Long Argument                             | Description                                                               |
|---------------------|-------------------------------------------|---------------------------------------------------------------------------|
| -i INJECT           | --inject INJECT                           | Mustache template file to inject into                                     |
| -d DIRECTORY        | --directory DIRECTORY                     | The directory to copy from                                                |
| -p PREFIX           | --prefix PREFIX                           | The prefix to add to all files and links                                  |
| -x                  | --execute                                 | Actually run--not the default dry run                                     |
| -u                  | --up                                      | Release version, where pages have a link pointing up one level            |
| -v                  | --verbose                                 | More verbose output                                                       |
| -b BUCKET           | --bucket BUCKET                           | Name of S3 bucket if creating index for remote directory                  |
| -r REMOTE_DIRECTORY | --remote_directory REMOTE_DIRECTORY       | Name of S3 remote directory (without leading / ) if creating index for it |

The package may be imported as `multi_indexer`, though the `main()` function provides most of the functionality.

By default, no files will be written or uploaded unless `multi-indexer` is passed the `-x`/`--execute` flag.

You can find an example HTML template at the project repository:

https://github.com/Knowledge-Graph-Hub/multi-indexer/blob/main/directory-index-template.html

This is also the template the multi-indexer will use if no template is provided.

### Example usage for local indexing, just for local testing

This assumes that `directory-index-template.html` is present in your current working directory.

```
mkdir -p /tmp/foo/bar/bib/bab && mkdir -p /tmp/foo/bar/fish && mkdir -p /tmp/foo/bar/foul
touch /tmp/foo/top.md && touch /tmp/foo/bar/bib/bab/bottom.txt && touch /tmp/foo/bar/fish/trout.f && touch /tmp/foo/bar/fish/bass.f
multi_indexer -v --inject ./directory-index-template.html --directory /tmp/foo --prefix file:///tmp/foo -x
```

### Example usage for local indexing, assuming indexes will be uploaded:
```
multi_indexer -v --inject ./directory-index-template.html --directory $WORKSPACE/mnt --prefix https://soyouhave.afancy.website/$PROJECTDIR/ -x'
```

### Example usage for remote indexing:
```
multi_indexer -v --inject ./directory-index-template.html --prefix https://soyouhave.afancy.website/$PROJECTDIR/ -b a-bucket-name -r $PROJECTDIR -x'
```

## Credits

Adapted from `directory_indexer.py` by Eric Douglass, Seth Carbon, and Justin Reese, originally at
https://github.com/Knowledge-Graph-Hub/go-site/blob/master/scripts/multi_indexer.py
