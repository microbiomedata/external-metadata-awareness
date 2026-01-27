========
PhenoImp
========

|DocumentationStatus|_
|JavaCIWithMaven|_
|GithubReleases|_

A tool for distorting phenopackets in disease/gene prioritizer benchmarks.

*PhenoImp* is designed to add noise and simulate imperfections in clinical data stored as phenopackets,
as defined by `Phenopacket schema <https://phenopacket-schema.readthedocs.io/en/master/>`_.
The noisy phenopackets can be used in performance benchmarks of phenotype-driven clinical decision support tools to
estimate tool performance on real-world data.

*PhenoImp* is implemented as a standalone Java command-line application.

Tutorial
########

This section describes how to setup *PhenoImp* application and how to use it to add noise to an example phenopacket representing a patient with
*Retinoblastoma* (`OMIM:180200 <https://www.omim.org/entry/180200>`_).

Setup Java
~~~~~~~~~~

*PhenoImp* is written using Java 17 and you need Java Runtime Environment (JRE) 17 or better to run the app. Ensure that
you have an appropriate Java version on your ``$PATH``::

  $ java -version

The command above should produce an output similar to::

  openjdk version "17" 2021-09-14
  OpenJDK Runtime Environment (build 17+35-2724)
  OpenJDK 64-Bit Server VM (build 17+35-2724, mixed mode, sharing)


Download distribution archive or build from sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, let's get ahold of the executable JAR file download the distribution ZIP from `Releases section <https://github.com/monarch-initiative/PhenoImp/releases>`_.
The archive contains executable JAR file ``phenoimp-cli-${version}.jar``.

Alternatively, we can build the JAR file from source by running::

  $ git clone git@github.com:monarch-initiative/PhenoImp.git
  $ cd PhenoImp
  $ ./mvnw clean package

.. note::
  A JDK 17 or better is required to build and run *PhenoImp*.

After the successful build, the JAR file is located at ``phenoimp-cli/target/phenoimp-cli-${version}.jar``.
Ensure that the build went well by running::

  $ java -jar phenoimp-cli/target/phenoimp-cli-*.jar --help

From now on, we will use ``phenoimp`` instead of the rather lengthy ``java -jar phenoimp-cli/target/phenoimp-cli-*.jar``::

  $ alias phenoimp='java -jar phenoimp-cli/target/phenoimp-cli-*.jar'


Download data files
~~~~~~~~~~~~~~~~~~~

*PhenoImp* requires several external files to run and the files need to be downloaded into a dedicated data directory.
Use the ``download`` command for setting up the data directory::

  $ phenoimp download -d path/to/data

The command downloads the external files into ``path/to/data`` folder. Any missing parent directories are created,
if necessary.

Distort a phenopacket
~~~~~~~~~~~~~~~~~~~~~

*PhenoImp* allows to introduce one or more of the several types of noise into a phenopacket:

- Replacing phenotype terms with parent or grandparent terms.
- Adding a certain number of phenotype terms sampled randomly.
- Dropping one of two variants that lead to a disease that segregates with autosomal recessive mode of inheritance.

The noise is added using the ``distort`` command::

  $ phenoimp distort -d path/to/data -i path/to/phenopacket.json \
      -o path/to/phenopacket.distorted.json \
      --add-n-random-terms 2 \
      --drop-ar-variant \
      --approximate PARENT

where:

- ``-i | --input``: path to v1 or v2 phenopacket in JSON format.
- ``-o | --output``: where to write the distorted phenopacket JSON.
- ``--add-n-random-terms``: number of random HPO terms to add.
- ``--drop-ar-variant``: drop one of two variant interpretations if associated with disease segregating with autosomal recessive mode of inheritance.
- ``--approximate``: replace each phenotype term with its parent (choose one from ``{OFF, PARENT, GRANDPARENT}``).

Now, assuming the data directory has been set up correctly, the following command will replace all phenotype terms
with their grandparents, add 2 random terms, and drop one of the two heterozygous variants in a real-life case
of retinoblastoma::

  $ phenoimp distort -d path/to/data -i examples/retinoblastoma.v2.json \
      -o retinoblastoma.v2.distorted.json \
      --add-n-random-terms 2 \
      --approximate GRANDPARENT \
      --drop-ar-variant

The resulting JSON is stored as `retinoblastoma.v2.distorted.json`.

Build container
###############

Build *PhenoImp* Docker container by running the following steps::

  $ CONTAINER=<your_organization>/phenoimp:<version>
  $ BUILD_CONTEXT=docker
  $ cd PhenoImp
  $ ./mvnw clean package -Prelease
  $ cp phenoimp-cli/target/phenoimp-cli-*distribution.zip docker
  $ docker build -t ${CONTAINER} ${BUILD_CONTEXT}
  $ rm ${BUILD_CONTEXT}/*.zip

.. note::
  Ensure ``your_organization`` and ``version`` are set to meaningful values.

Check that the build worked by running::

  $ docker run -it --rm ${CONTAINER} phenoimp --help

.. |JavaCIWithMaven| image:: https://github.com/monarch-initiative/PhenoImp/workflows/Java%20CI%20with%20Maven/badge.svg
.. _JavaCIWithMaven: https://github.com/monarch-initiative/PhenoImp/actions/workflows/maven.yml

.. |GithubReleases| image:: https://img.shields.io/github/release/monarch-initiative/PhenoImp.svg
.. _GithubReleases: https://github.com/monarch-initiative/PhenoImp/releases

.. |DocumentationStatus| image:: https://readthedocs.org/projects/phenoimp/badge/?version=main
.. _DocumentationStatus: https://phenoimp.readthedocs.io/en/latest/?badge=main
