scoped-mapping
==============

When mapping input strings from column/field ``X`` in some datasource to terms from OBO foundry ontologies, use the values in column/field ``Y`` to determine which ontology to map to.

Note that GitHub uses a hyphen and PyPI uses an underscore

Currently tested on a 32GB MacBook Pro running Catalina. Requires the riot library from Apache Jena. ``make all`` uses homebrew for installing Jena, but does not install homebrew. This will probably run on other 'nix systems but will require a system dependent installation of Jena.



Installation
------------
::

  python3.9 -m venv sm_venv
  source sm_venv/bin/activate
  pip install -r requirements.txt
  pip install -i https://test.pypi.org/simple/ scoped-mapping
  


Sample code
-----------

See Jupyter Notebooks

  


Scoping mappings based on subsets of NCBItaxon
----------------------------------------------

First download `semantic-sql` and some of its dependencies. Build an SQLite database with the NCBItaxon content. Building requires lots of disk space, RAM and patience. Well worth it when it comes to query time::

    make all

If a dataset has taxon values, one can use them to subset or scope how other values in the dataset should be mapped. For example, the NCBI Biosample metadata collection has MIxS triads (broad, narrow and medium) that could me mapped to ENVO terms in many cases. But ENVO might not be appropriate for cultured samples or samples that were taken from a multicellular organism. One way to check for those cases is looking for transitive subclasses in NCBItaxon. There are numerous ways to do that, but they are all generally computationally expensive.

Here, we use rdftab and relation-graph (via semantic-sql) to infer those transitive subClassOf relationships and load them into an SQLite database. Building this database requires lots of RAM and roughly 10 GB of disk space, but after that the querying is fast and convenient.

Building
---------

Once::

  pip install build twine

Every time::

  git add ...
  git commit -m ...
  git push 
  git tag ...
  pip install --use-feature=in-tree-build .
  
Ready to deploy?::

  python -m build --sdist --wheel .
  ls -l dist/
  
remove all artifacts from all builds in ``dist/`` except for the latest

::

  twine upload --repository pypitest dist/*


