# SynBio schema

This needs a rewrite.

## What is this?

Previously followed the [LinkML](https://github.com/biolink/biolinkml/) template. Now using gen-project.

## Previous content

To run the Makefile you will need Python (>=3.7), and biolinkml. You can type:

```bash
make install
```

But that claims it can't find `environment.sh` on Mark's Ubuntu 20 workstation. One could directly enter:

```bash
. environment.sh
pip install -r requirements.txt
```

But even the `environment.sh` and `pip install...` steps complained on Mark's  workstation. The solution appears to be

```bash
python3  -m venv venv 
source venv/bin/activate 
export PYTHONPATH=.:$PYTHONPATH 
pip install wheel 
pip install -r requirements.txt
```

You can make specific targets, e.g

```bash
make stage-jsonschema
```

Use the `all` target to make everything

Note to redeploy documentation all you need to do is:

```bash
make gh-deploy
```

That's it!

The Makefile takes care of dependencies. Downstream files are only rebuilt if source files change.

## Documentation framework

You can change the theme by editing [mkdocs.yml](mkdocs.yml)

Do not edit docs in place. They are placed in the `docs` dir by `make stage-docs`.

You can add your own docs to `src/docs/

Note that docs are actually deployed on the gh-pages branch, but you don't need to worry about this. Just type:

```bash
make gh-deploy
```

DO NOT DO THIS YET - repo stull private

The template site is deployed on

http://cmungall.github.io/synbio-schema

