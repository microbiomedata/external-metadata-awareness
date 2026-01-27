###########################
Annotation Sufficiency Tool
###########################

The Annotation Sufficiency Tool (AST) is designed to provide feedback as to whether a collection of
`Human Phenotype Ontology (HPO) <https://hpo.jax.org/app/>`_ terms used to annotate a patient are
sufficient with respect to quantity and specificity. The current version of AST uses a heuristic to
provide feedback on a one to five star scale. Future versions will implement a more sophisticated algorithm.

Building AST
############

To build AST from source, clone it from GitHub and use the maven package command. Check the result
by running the tool without arguments.

.. code-block:: bash

    git clone https://github.com/monarch-initiative/AST.git
    cd AST
    mvn package
    java -jar target/AnnotationSufficiencyTool.jar
    Usage: java -jar AnnotationSufficiencyTool.jar [-hV] [COMMAND]
    Annotation Sufficiency Tool
        -h, --help      Show this help message and exit.
        -V, --version   Print version information and exit.
    Commands:
        download, D  Download files for AnnotationSufficiencyTool
        assess, A    Assess Annotation Sufficiency

Setting up AST
##############

The AST tool uses several downloaded files for annotation sufficiency assessment.
To download these files, run the following command

.. code-block:: bash

    java -jar target/AnnotationSufficiencyTool.jar

This will download four files to a newly created directory called ``data``. Tp update these files, delete this
directory and rerun the command or run the command with the ``--overwrite`` flag.

Running AST
###########

To run AST, you need to supply a `GA4GH Phenopacket <https://github.com/phenopackets/phenopacket-schema>`_. See
`here <https://www.ga4gh.org/news/phenopackets-standardizing-and-exchanging-patient-phenotypic-data/>`_ for a general
introduction. Example phenopackets can be downloaded from this `zenodo repository <https://zenodo.org/record/3905420#.YGxNExIpBH4>`_.

Run the tool as follows

.. code-block:: bash

    java -jar target/AnnotationSufficiencyTool.jar assess -p <path>

Here, ``<path>`` can be the path to either a single phenopacket or to a directory that contains phenopackets.

Examples
########

We have provided some example phenopackets to make it easier to try out the tool. For convenience,
we leave the application in the target directory that is created by maven.

.. code-block:: bash

    java -jar target/AnnotationSufficiencyTool.jar assess -p examplePhenopackets/Dorboz-2017-NKX6-2-Patient_3_II-3.json
    Dorboz-2017-NKX6-2-Patient_3_II-3.json  103.1%

This creates an output file ``AST.tsv`` (change the outfile name with the ``-o`` flag).

.. code-block:: bash

    cat AST.tsv
    Dorboz-2017-NKX6-2-Patient_3_II-3.json  103.1%

We can run the tool across the entire directory

.. code-block:: bash

    java -jar target/AnnotationSufficiencyTool.jar assess -p examplePhenopackets/
    Dorboz-2017-NKX6-2-Patient_4_II-1.json  0.9
    Dougherty-2016-NPC1-The_proband.json    1.4
    Ekvall-2015-NRAS-case_1.json    0.9
    Dorboz-2017-NKX6-2-Patient_3_II-3.json  10.0
    Du-2018-TINF2-proband.json      4.2

Again, these results are also written to the output file.


Interpretation
##############

An annotation score of 1.0 means that the query terms have the same breadth and depth as (on average) the terms used to annotated
diseases in the HPO database do. A score of 0.9 means the query terms are 90% as good, and a score of 4.2 means that the query terms
are better.

This is a first approximation to a tool that will provide feedback on query terms.
