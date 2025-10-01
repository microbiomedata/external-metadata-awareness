metadata_converter
==================

This repo contains code and target outputs for a metadata converter with a
focus on environmental sample metadata.

Source schemas/templates/variable lists are in a variety of different formats.
We choose the biolinkml schema language as our base representation (see below).
We convert all source schemas to biolinkml. From here we convert to other representations
such as json-schema.

Currently the sources we have include:

* neon
    * `code <metadata_converter/neon.py>`__
    * `input <tests/neon/>`__ (CSV dump of schema)
    * `schema products <target/neon/>`__
        * `yaml <target/neon/neon.yaml>`__ (source biolinkml)
        * `json-schema <target/neon/neon.schema.json>`__ (derived)
    * `docs <docs/neon/>`__
* kbase
    * `code <metadata_converter/kbase.py>`__ (incomplete)
    * `input <tests/kbase/>`__ (YAML)
    * `schema products <target/kbase/>`__
        * `yaml <target/kbase/kbase.yaml>`__ (source biolinkml)
        * `json-schema <target/kbase/kbase.schema.json>`__ (derived)
    * `docs <docs/kbase/>`__
* EMP
    * `schema products <target/emp/>`__
        * `yaml <target/emp/emp.yaml>`__ (source biolinkml)
        * `json-schema <target/emp/emp.schema.json>`__ (derived)
    * `docs <docs/emp/>`__
* mixs
    * `code <metadata_converter/mixs7.py>`__ (incomplete)
    * `input <tests/mixs6/>`__ (YAML)
    * `schema products <target/mixs6/>`__
        * `yaml <target/kbase/kbase.yaml>`__ (source biolinkml)
        * `json-schema <target/kbase/kbase.schema.json>`__ (derived)
    * `docs <docs/kbase/>`__
 * mixs
    * INCOMPLETE
    * code is currently external
    * `schema products <target/mixs/>`__
        * `yaml <target/neon/mixs.yaml>`__ (source biolinkml)
        * `json-schema <target/mixs/mixs.schema.json>`__ (derived)
    * `docs <docs/mixs/>`__
* gold
    * `code <metadata_converter/ddl_tsv.py>`__
    * `input <tests/gold/>`__ (SQL DDL dump)
    * `schema products <target/gold/>`__
        * `yaml <target/gold/gold.yaml>`__ (source biolinkml)
        * `json-schema <target/gold/gold.schema.json>`__ (derived)
    * `docs <docs/gold/>`__
* DarwinCore
    * `code <metadata_converter/darwincore.py>`__
    * `input <tests/dwc/>`__ (DWC reference csv)
    * `schema products <target/dwc/>`__
        * `yaml <target/dwc/dwc.yaml>`__ (source biolinkml)
        * `json-schema <target/dwc/dwc.schema.json>`__ (derived)
    * `docs <docs/dwc/>`__


Mappings
========

See `mappings/ <mappings/>`__

We convert all the above yamls to OWL and perform mappings, als throwing select
ontologies and ontology-like artefacts into the mix, both OBO (ENVO, BCO, OBI, UO, PATO) and non-OBO (DataCite, Dublincore)

Building Targets
================

Help:

.. code-block:: sh

    make test
    make all

